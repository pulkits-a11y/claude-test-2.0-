#!/usr/bin/env python3
"""Build the AUDIO half of the RC_GTA-Origin Tesseract project, deterministically.

Golden rule: 00_Brief/GTA_VI_Edit_Plan.pdf (Music plan p.32-35, SFX plan p.35-38, Audio mix and export settings
p.38), with the client's notes (REVISION_v02.md ... REVISION_v05.md) where they override it. v05: the client's
instruction doc (REVISION_v05.md G9 + S, doc section 2.7) wins where it conflicts (X8: a sound on every caption word).
Inputs (all established earlier, read-only here):

  timing/beat_map.json             beat clock (B1-B18 start frames, vo_end_s, edit_end_s) and `vo_file`: every
                                   duration, and the voiceover, come from it
  <vo_file>                        locked voiceover (v05: 01_VO/VO_processed_v05.wav, mono, 48 kHz, 115%, both doc
                                   cuts), with VO_words_<tag>.json (word timings -> ducking spans, the 'fun' anchor)
                                   and VO_processing_<tag>.json beside it
  timing/beat_map_v04.json +       v04 -> v05 frame map (the doc cuts A/B): cues written before v05 ("legacy", see
  timing/v04_to_v05.json           below) are moved to v05 beat frames; an event inside a cut is dropped
  02_Music/music_plan.json         Black Vertigo analysis (drop downbeat 183.38 s, sections), cut points, levels
  03_SFX/sfx_plan.json             S01-S19 cue rules (event, align, offsets, trims, fades, peaks); the v02
                                   change to S10 (note 5) is CUE_OVERRIDES below
  03_SFX/sfx_analysis.json         measured file data
  03_SFX/v05/library.json          v05 SFX library (tools/build_tesseract_sfx_v05.py): canonical names -> files,
                                   align (start|peak|end), default peak level, group, class
  hyperframes/<comp>/cues.json     per beat (beat frames, f0 = beat start):
                                   * v05 schema (any of word_pops/key_words/hook_cuts/sfx/dropouts/archival, or
                                     "timing": "v05"): frames are v05 beat frames as written. `events` = the legacy
                                     S01-S19 events the lane still wants (an event it leaves out = no sound; no
                                     STORYBOARD fallback). word_pops -> tick (3 variants, rotating), key_words ->
                                     whoosh_in ending on the frame + thump_low on it, hook_cuts -> swipe (peak on the
                                     cut), sfx [{f, name, gain_db?, dur_f?, note?}] -> the library sound (gain_db = its
                                     sample-peak level in dBFS), dropouts [{f, frames}] -> music bed AND riser/ambience
                                     SFX silent for `frames` frames ending at f, archival -> picture only
                                   * legacy (only `events`): v02/v04 beat frames, moved to v05 by the cut map; a file
                                     whose events still equal the v01 snapshot (.tesseract-work/cues_v01_snapshot.json)
                                     is v01-timed and scaled to the v04 beat first; an event it lacks comes from the
                                     STORYBOARD.md "Cues" lines (v01 frames, scaled and mapped the same way; cached in
                                     .tesseract-work/cue_defaults.json, --refresh-cue-defaults)

Every run (deterministic; one Tesseract export at a time):
  1. prepares the FFmpeg derivatives the plan needs (MU6 low-pass 800 Hz excerpt in .tesseract-work/derived,
     S02/S14 300 Hz high-pass in 03_SFX/derived), recipes beside them, and measures the MP3
     decoder offset of Tesseract vs FFmpeg (cached in .tesseract-work/decoder_offsets.json);
  2. deletes and recreates .tesseract-work/audio.tsrct: one composition (1920x1080, edit_end_s from the
     beat map, #0A0A0A), five groups "A1 Voiceover", "A2 Music", "A3 SFX hits & impacts", "A4 Risers,
     whooshes & textures" (CONFLICTS.md C6), "A5 Caption pops & key words" (v05), layer ids >= 9000, asset ids
     "aud-*", volume envelopes as keyframe animators on propertyType "volume";
  3. pass 1 (pre-master): exports the group stems, corrects each S-cue's gain so its rendered sample peak sits
     at the plan's level (the 48 kHz v05 library layers render exactly as modelled and keep their level), then
     solves the master: one static make-up gain on every layer to reach -14 LUFS plus limiter-like gain dips
     only where the true peak would pass MASTER_CEILING_DBTP (Tesseract has no limiter; CONFLICTS C20);
  4. pass 2: commits the final document, exports .tesseract-work/checks/mix.wav (+ final stems unless
     --no-stems), measures everything, draws waveform views and writes
     .tesseract-work/checks/audio_report.json and .tesseract-work/AUDIO_NOTES.md.

Usage:  python3 tools/build_tesseract_audio.py [--no-stems] [--no-waveforms] [--refresh-cue-defaults]
Test:   --cues-dir DIR reads DIR/<composition>/cues.json before hyperframes/<composition>/cues.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import lfilter, resample_poly

# --------------------------------------------------------------------------------------------
# Paths and tools
# --------------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".tesseract-work"
CHECKS = WORK / "checks"
PROJECT = WORK / "audio.tsrct"
TSRCT = Path("/root/.local/share/Tesseract/bin/tsrct")
SKILL = ROOT.parent / ".claude/skills/tesseract-video"
SOUND_HELPER = SKILL / "scripts/tesseract_sound.py"

BEAT_MAP = ROOT / "timing/beat_map.json"
BEAT_MAP_V04 = ROOT / "timing/beat_map_v04.json"         # v05: the v04 beat clock (cues written before v05)
CUTS_V04_V05 = ROOT / "timing/v04_to_v05.json"           # v05: the doc cuts A/B (v04 seconds removed, shifts)


def vo_paths(beat_map_path: Path = BEAT_MAP):
    """v05: the voiceover is the beat map's `vo_file` (not a hard-coded name); its word timings and processing
    report sit beside it (VO_processed_<tag>.wav -> VO_words_<tag>.json, VO_processing_<tag>.json; a `words_file`
    key in the beat map wins). Falls back to the v02 115% files if the beat map has no `vo_file`."""
    try:
        bm = json.loads(Path(beat_map_path).read_text())
    except (OSError, ValueError):
        bm = {}
    vo = ROOT / (bm.get("vo_file") or "01_VO/VO_processed_115.wav")
    tag = vo.stem[len("VO_processed_"):] if vo.stem.startswith("VO_processed_") else vo.stem
    words = ROOT / bm["words_file"] if bm.get("words_file") else vo.with_name("VO_words_%s.json" % tag)
    return vo, words, vo.with_name("VO_processing_%s.json" % tag), tag


VO_FILE, WORDS_JSON, VO_REPORT, VO_TAG = vo_paths()
CUE_DEFAULTS = WORK / "cue_defaults.json"               # STORYBOARD.md cues (v01 frames), scaled at load
CUES_V01 = WORK / "cues_v01_snapshot.json"              # the v01 cues.json events (to spot v01-timed files)
STORYBOARD = ROOT / "STORYBOARD.md"
MUSIC_PLAN = ROOT / "02_Music/music_plan.json"
SFX_PLAN = ROOT / "03_SFX/sfx_plan.json"
SFX_ANALYSIS = ROOT / "03_SFX/sfx_analysis.json"
SFX_DIR = ROOT / "03_SFX"
MUSIC_DERIVED = WORK / "derived"                        # v02: the MU6 excerpt moves with the new offset
SFX_DERIVED = ROOT / "03_SFX/derived"
SFX_LIB_DIR = ROOT / "03_SFX/v05"                       # v05 library (tools/build_tesseract_sfx_v05.py)
SFX_LIB = SFX_LIB_DIR / "library.json"
CUES_DIR_TEST = None                                    # --cues-dir (test only)

SR = 48000          # Tesseract mixes and exports at 48 kHz (measured)
FPS = 30

# --------------------------------------------------------------------------------------------
# Mix decisions (plan p.35 and p.38; see AUDIO_NOTES.md for the reasoning and measurements)
# --------------------------------------------------------------------------------------------
# A1: unity. The processed VO meets the plan's voice spec as a (mono) track: -16.3 LUFS, -3.4 dBTP.
# Tesseract plays a mono source at full level on BOTH channels (no pan law, measured), so on a stereo
# meter the voice reads +3 dB (-13.3 LUFS) before the master gain; unity keeps the plan's peak
# relationships (voice peaks about -3.8 dBFS > every SFX peak level of -6 dBFS or lower, except S19).
VO_GAIN_DB = 0.0
# v04 (REVISION_v04.md note 1, "remove Bg music we can change that"): no music bed in the mix. Everything music-related
# (anchor, MU marks, bar edit, envelopes, MU6 excerpt) is still computed and reported, so a new track is dropped in by
# setting MUSIC = True (and 02_Music/music_plan.json for that track); with MUSIC = False the A2 group stays empty, no
# music asset is imported, and the master gain is solved on voice + SFX alone (every SFX keeps its level vs the voice).
MUSIC = False
# A2 bed: music_plan.json proposed -8 dB; measured Black Vertigo short-term loudness after the
# drop is about -9 LUFS, so -7 dB puts the un-ducked bed at about -16 LUFS (plan: no-voice level)
# and the ducked bed at about -22/-23 LUFS (plan: under the voice). See the report.
MUSIC_BASE_DB = -7.0
DUCK_DB = -7.0               # plan: 6-8 dB of reduction
ATTACK_S = 0.050             # plan: 50 ms attack (look-ahead: full depth when the phrase starts)
RELEASE_S = 0.300            # plan: 300 ms release
MERGE_GAP_S = 0.25           # word gaps shorter than this stay ducked (one phrase)
MU5_LIFT_DB = 3.0            # plan: lift the music 3 dB for 2 s after "fun"
MU5_HOLD_S = 2.0
MU5_RETURN_S = 0.300         # ramp back after the 2 s (same as the duck release)
MU6_DB = -6.0                # plan: -6 dB with the 800 Hz low-pass
MU6_LOWPASS_HZ = 800
MU7_DB = -6.0                # plan: resume 6 dB lower under the glow line (B16)
MU7_RETURN_S = 0.030         # back to the normal bed at the B17 cut
MU4_FRAMES = 15              # plan: hard-mute 15f
EDGE_S = 0.010               # de-click ramp for hard cuts/mutes/crossfades (engine evaluates
                             # gain every 10 ms and interpolates linearly, measured)
# Master stage (plan p.38: "limiter ceiling -1.0 dBTP; integrated loudness -14 LUFS +-1").
# Tesseract has no native limiter, so the master is a gain applied equally to EVERY layer: one
# static make-up gain (solved so the mix reads MASTER_TARGET_LUFS) plus, only where the true peak
# would cross the ceiling, a smooth limiter-like dip (look-ahead attack, slow release) computed from
# the pre-master stems. MASTER_CEILING_DBTP keeps 0.5 dB of the plan's -1.0 dBTP for AAC encoding.
MASTER_TARGET_LUFS = -14.0
MASTER_CEILING_DBTP = -1.5
MASTER_ATTACK_S = 0.050
MASTER_RELEASE_S = 0.300

# v02 (REVISION_v02.md note 5): B11's flip became the X4 glitch used in B8, so S10's sound changes from the
# S10 Flip whoosh to B8's glitch impact (the S08a file) at S08's level (same pre-master gain as S08, which also
# follows S08's calibration), on B11's new `glitch` event. While B11's cues.json is still v01 it has no
# `glitch`, so the cue falls back to `flip_start`. It stays in S10's plan group A4: in A3 it would overlap S09's
# sustained sub drop, and the isolation of each cue's rendered peak (stem minus the model of the others) is not
# reliable for a sharp transient over a sustained cue (measured: the resampler residual of the glitch, -19 dBFS,
# moved S09's isolated peak by +1.9 dB and its calibration by -2 dB).
# MU2 whole-bar edit (plan p.34: 'remove or repeat a whole bar inside the breakdown (2:28.5-2:46.0)'), applied in v02
# on the coordinator's instruction: with the drop anchored on the faster VO's 'fun', the breakdown arrived 1.53 s
# before 'broke'. The track now starts one bar earlier (so the breakdown arrives inside 'broke') and one whole bar
# inside the breakdown is removed on a bar line, so everything after the seam (MU3, the MU5 drop on 'fun', MU6-MU8)
# stays exactly where the anchor puts it. Kept only if MU2 gets closer to 'broke', MU3 stays within 1 s of 'dull'
# and the seam lies between MU2 and MU3 (MU5 is after it by construction; the stem check measures it).
MU2_BAR_EDIT = True
BAR_EDIT_BAR = None            # 1-based breakdown bar to remove; None = the best-matching seam among bars 2..n-1
BAR_EDIT_XFADE_S = 0.030       # equal-power crossfade (3 steps of the engine's 10 ms gain clock) ...
BAR_EDIT_LEAD_S = 0.025        # ... ending this long before the bar line, so the next bar's downbeat comes through
                               # whole and the removed bar's downbeat (up to ~20 ms early on this track) is not heard
CUE_OVERRIDES = {
    "S10": {"group": "A4", "files": ["S08a_Glitch, Impact.wav"], "event": "B11.glitch",
            "fallback_event": "B11.flip_start", "align": "start", "offset_f": 0, "peak_dbfs": None,
            "gain_link": "S08",
            "plan": "v02 note 5: the B11 flip is replaced by the X4 glitch of B8, and the glitch sound replaces "
                    "the flip whoosh: B8's glitch impact (S08a) at S08's level, starting on the glitch frame."},
}

# v05 (REVISION_v05.md G9 + S, doc 2.7): the cues.json v05 schema and the 03_SFX/v05 library. Overrides the plan's
# "never a pop on every caption / a whoosh on every cut" (REVISION_v05 X8).
V05_KEYS = ("word_pops", "key_words", "hook_cuts", "sfx", "dropouts", "archival")
V05_LAYER_BASE = 20000         # v05 library layers: 20000 + n (edit order); S-cues stay 10000 + cue x 100 + n
V05_GAIN_CAP_DBFS = -4.0       # a cue's gain_db is the sound's sample-peak level; never above S19's -4 (voice on top)
V05_KEY_WORD_PAIR = ("whoosh_in", "thump_low")     # key_words: whoosh ending on the frame + thump on it
V05_WORD_POP = "tick"                              # word_pops: 3 variants rotating in edit order
V05_HOOK_CUT = "swipe"                             # hook_cuts: peak on the cut
V05_DROPOUT_MAX_F = 15                             # doc: 2-6 frames; anything longer is clamped (plan MU4 = 15 f)
# classes silenced inside cues.json `dropouts` (with the bed off "risers/ambience obey the same dropouts", G9):
# the library's riser/ambience sounds and the plan's sustained S-cues
DROPOUT_CLASSES = ("riser", "ambience")
LEGACY_CLASS = {"S05": "ambience", "S07": "riser", "S18": "riser"}

# Layer / group ids (>= 9000, picture script uses lower ids)
GID = {"A1": 9001, "A2": 9002, "A3": 9003, "A4": 9004, "A5": 9005}
GNAME = {"A1": "A1 Voiceover", "A2": "A2 Music", "A3": "A3 SFX hits & impacts",
         "A4": "A4 Risers, whooshes & textures", "A5": "A5 Caption pops & key words"}
SFX_GROUPS = ("A3", "A4", "A5")
VO_LAYER_ID = 9101
MUSIC_LAYER_ID = 9201
MUSIC_B_LAYER_ID = 9203        # the main bed after the MU2 bar edit's seam
MUSIC_LP_LAYER_ID = 9202


def sfx_layer_id(cue: str, sub_index: int) -> int:
    return 10000 + int(cue[1:]) * 100 + sub_index


# --------------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------------
def log(*a):
    print(*a, flush=True)


def run(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError("command failed (%d): %s\n%s\n%s" % (r.returncode, " ".join(map(str, cmd)),
                                                               r.stdout[-3000:], r.stderr[-3000:]))
    return r


def tsrct(*args):
    return run([TSRCT, *args])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def db(x: float) -> float:
    return 20 * math.log10(max(x, 1e-12))


def lin(d: float) -> float:
    return 10 ** (d / 20)


def frames_to_s(f) -> float:
    return f / FPS


def ms(t_s: float) -> int:
    return int(round(t_s * 1000))


_PROBE_CACHE: dict = {}


def probe(path: Path) -> dict:
    key = str(path)
    if key not in _PROBE_CACHE:
        _PROBE_CACHE[key] = _probe(path)
    return dict(_PROBE_CACHE[key])


def _probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
             "stream=channels,sample_rate,codec_name:format=duration", "-of", "json", path])
    j = json.loads(r.stdout)
    st = j["streams"][0]
    return {"channels": int(st["channels"]), "sample_rate": int(st["sample_rate"]),
            "codec": st["codec_name"], "duration": float(j["format"]["duration"])}


_DECODE_CACHE: dict = {}


def decode(path: Path) -> np.ndarray:
    """ffmpeg decode at 48 kHz, float, native channels; mono is duplicated at FULL level on both
    channels, which is what Tesseract does (measured), so peaks match the mix."""
    key = str(path)
    if key not in _DECODE_CACHE:
        ch = probe(path)["channels"]
        out = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-f", "f32le",
                              "-ar", str(SR), "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(out, np.float32).reshape(-1, ch).astype(np.float64)
        if ch == 1:
            x = np.repeat(x, 2, axis=1)
        elif ch > 2:
            x = x[:, :2]
        _DECODE_CACHE[key] = x
    return _DECODE_CACHE[key]


def read_wav(path: Path) -> np.ndarray:
    x, sr = sf.read(str(path), always_2d=True)
    assert sr == SR, (path, sr)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x


# --------------------------------------------------------------------------------------------
# Loudness (ITU-R BS.1770-4 / EBU R128) for stems; the official mix numbers also come from
# ffmpeg ebur128 and the skill's measure helper.
# --------------------------------------------------------------------------------------------
_KB1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_KA1 = [1.0, -1.69065929318241, 0.73248077421585]
_KB2 = [1.0, -2.0, 1.0]
_KA2 = [1.0, -1.99004745483398, 0.99007225036621]


def _kpower(x):
    y = lfilter(_KB2, _KA2, lfilter(_KB1, _KA1, x, axis=0), axis=0)
    return np.sum(y * y, axis=1)


def _blocks(power, win_s, hop_s):
    c = np.concatenate([[0.0], np.cumsum(power)])
    w, h = int(round(win_s * SR)), int(round(hop_s * SR))
    starts = np.arange(0, len(power) - w + 1, h)
    return starts, (c[starts + w] - c[starts]) / w


def lufs_of(msq):
    return -0.691 + 10 * np.log10(np.maximum(msq, 1e-20))


def integrated_lufs(x):
    _, m = _blocks(_kpower(x), 0.4, 0.1)
    l = lufs_of(m)
    g = l > -70
    if not np.any(g):
        return None
    rel = lufs_of(np.mean(m[g])) - 10
    g2 = g & (l > rel)
    return float(lufs_of(np.mean(m[g2])))


def windowed_lufs(x, win_s):
    """(window centre times, LUFS) with 100 ms hop."""
    s, m = _blocks(_kpower(x), win_s, 0.1)
    return (s + win_s * SR / 2) / SR, lufs_of(m)


def true_peak_dbtp(x):
    return db(float(np.max(np.abs(resample_poly(x, 4, 1, axis=0)))))


def xcorr_lag(y, ref, maxlag):
    """Lag (samples) by which y is delayed relative to ref, searched within +-maxlag."""
    n = min(len(y), len(ref))
    y, ref = y[:n] - np.mean(y[:n]), ref[:n] - np.mean(ref[:n])
    nfft = 1 << int(math.ceil(math.log2(2 * n)))
    cc = np.fft.irfft(np.fft.rfft(y, nfft) * np.conj(np.fft.rfft(ref, nfft)), nfft)
    lags = np.concatenate([np.arange(0, maxlag + 1), np.arange(-maxlag, 0)])
    vals = np.concatenate([cc[: maxlag + 1], cc[-maxlag:]])
    return int(lags[int(np.argmax(vals))])


# --------------------------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------------------------
def load_json(p: Path):
    with open(p) as f:
        return json.load(f)


def parse_storyboard_cues(text: str) -> dict:
    """{beat: {event: frame}} from the '**Cues**' line of each '## Bn ...' section.
    `name` = 58 / ~48 / 'first digit move (~29)' -> first integer; `name` = a..b -> name=a, name_end=b."""
    out = {}
    beat = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(B\d+)\b", line)
        if m:
            beat = m.group(1)
            out.setdefault(beat, {})
            continue
        if beat and line.startswith("**Cues**"):
            for m in re.finditer(r"`([A-Za-z0-9_]+)`\s*=\s*([^`]*)", line):
                name, rest = m.group(1), m.group(2)
                rng = re.match(r"\s*(\d+)\s*\.\.\s*(\d+)", rest)
                if rng:
                    out[beat][name] = int(rng.group(1))
                    out[beat][name + "_end"] = int(rng.group(2))
                    continue
                num = re.search(r"~?(\d+)", rest)
                if num:
                    out[beat][name] = int(num.group(1))
    return out


def parse_storyboard_durations(text: str) -> dict:
    """{beat: frames} from the '## Bn Name (143f)' headings (the beat lengths the storyboard frames refer to)."""
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"^##\s+(B\d+)\b[^\n(]*\((\d+)f\)", text, re.M)}


class CutMap:
    """v04 -> v05 beat frames (REVISION_v05.md section 0). A beat that is shorter in v05 (v04_dur_frames - dur_frames
    = n > 0) lost one block of n frames: where a `removed` span of timing/v04_to_v05.json overlaps its v04 window
    (clamped to the beat), else at its end. With the client override: B3 loses its first 20 f (v04 local 0-19, "Here's
    how."; B3 now starts at "It's"), B13 39 f at local 161-199 (the title-hold silence), B17 its last 18 f (logo tail);
    every other beat keeps its local frames. map() -> the v05 frame, or None for a frame that was cut (or now lies past
    the beat). Identity for a beat without v04 timing (B18) or when the map files are missing."""

    def __init__(self, beat_map: dict):
        self.blocks = {}                                  # beat -> (v04 local start, n frames, v05 dur)
        try:
            removed = [tuple(map(float, r)) for r in load_json(CUTS_V04_V05).get("removed", [])]
        except (OSError, ValueError):
            removed = []
        for bt in beat_map["beats"]:
            s4, d4 = bt.get("v04_start_frame"), bt.get("v04_dur_frames")
            if s4 is None or d4 is None:
                continue
            d5 = int(bt["dur_frames"])
            n = int(d4) - d5
            if n <= 0:
                continue
            st = None
            for ra, rz in removed:
                fa, fz = ra * FPS - int(s4), rz * FPS - int(s4)
                if fz > 0 and fa < int(d4):
                    st = max(0, int(round(fa)))
                    break
            self.blocks[bt["id"]] = (min(d5, d5 if st is None else st), n, d5)

    def identity(self, bid) -> bool:
        return bid not in self.blocks

    def map(self, bid: str, f: int):
        if bid not in self.blocks:
            return f
        st, n, d5 = self.blocks[bid]
        if st <= f < st + n:
            return None
        f5 = f if f < st else f - n
        return None if not 0 <= f5 <= d5 else f5


def parse_v05_lists(doc: dict, bid: str, notes: list) -> dict:
    """The v05 lists of a cues.json (REVISION_v05.md S), validated. A frame list item is an int or {"f": n, ...}
    (gain_db / name / note pass through); sfx items need f and name; dropouts [{f, frames}] (or [f, frames]);
    archival [[f0, f1], ...]. Missing keys = nothing."""
    out = {k: [] for k in V05_KEYS}

    def frame_items(key):
        res = []
        for it in doc.get(key) or []:
            if isinstance(it, bool):
                notes.append("%s %s: ignored item %r" % (bid, key, it))
            elif isinstance(it, (int, float)):
                res.append({"f": int(round(it))})
            elif isinstance(it, dict) and isinstance(it.get("f"), (int, float)):
                res.append(dict(it, f=int(round(it["f"]))))
            else:
                notes.append("%s %s: ignored item %r (needs a frame number or {\"f\": n})" % (bid, key, it))
        return res
    for key in ("word_pops", "key_words", "hook_cuts"):
        out[key] = frame_items(key)
    for it in frame_items("sfx"):
        if it.get("name"):
            out["sfx"].append(it)
        else:
            notes.append("%s sfx: ignored %r (no name)" % (bid, it))
    for it in doc.get("dropouts") or []:
        if isinstance(it, dict) and isinstance(it.get("f"), (int, float)):
            f, n = int(round(it["f"])), int(round(it.get("frames", 4)))
        elif isinstance(it, (list, tuple)) and len(it) == 2:
            f, n = int(round(it[0])), int(round(it[1]))
        else:
            notes.append("%s dropouts: ignored %r (needs {\"f\": n, \"frames\": k})" % (bid, it))
            continue
        if n > V05_DROPOUT_MAX_F:
            notes.append("%s dropout at f%d: %d frames clamped to %d" % (bid, f, n, V05_DROPOUT_MAX_F))
        out["dropouts"].append({"f": f, "frames": max(1, min(n, V05_DROPOUT_MAX_F))})
    for it in doc.get("archival") or []:
        if isinstance(it, (list, tuple)) and len(it) == 2:
            out["archival"].append([int(round(it[0])), int(round(it[1]))])
        else:
            notes.append("%s archival: ignored %r (needs [f0, f1])" % (bid, it))
    return out


def is_v05_cues(doc: dict) -> bool:
    return any(k in doc for k in V05_KEYS) or str(doc.get("timing", "")).lower() == "v05"


def cues_path(comp: str) -> Path:
    if CUES_DIR_TEST and (Path(CUES_DIR_TEST) / comp / "cues.json").exists():
        return Path(CUES_DIR_TEST) / comp / "cues.json"
    return ROOT / "hyperframes" / comp / "cues.json"


class Events:
    """Event frames per beat (beat-relative, f0 = the beat's first frame), in v05 beat lengths.

    * v05 cues.json (REVISION_v05 S): `events` exactly as written (v05 frames), no STORYBOARD fallback (a legacy
      event a lane leaves out has no sound), plus the v05 lists (self.v05[beat]).
    * legacy cues.json (only `events`; v02/v04 frames): moved to v05 by the cut map (CutMap: B3 -20 f, its first 20 f
      cut; B13 -39 f after local 161; B17's tail; an event inside a cut is dropped and not refilled from the
      STORYBOARD). One that still equals the v01
      snapshot is scaled from the v01 to the v04 beat length first. Events it lacks come from the STORYBOARD.md cues
      (v01 frames, scaled to the v04 beat, then mapped).
    * no cues.json: the STORYBOARD.md cues (scaled + mapped).
    The music marks read `music_table` (always with the STORYBOARD/legacy fallback), so a v05 file that drops a
    legacy event never breaks the music automation."""

    def __init__(self, beat_map: dict, refresh_defaults: bool):
        self.beats = {b["id"]: b for b in beat_map["beats"]}
        text = STORYBOARD.read_text()
        sb = parse_storyboard_cues(text)
        sb_dur = parse_storyboard_durations(text)
        if refresh_defaults or not CUE_DEFAULTS.exists():
            doc = {"_source": "STORYBOARD.md '**Cues**' lines (beat-relative frames in the storyboard's v01 beat "
                              "lengths, `_durations`). Fallback used by tools/build_tesseract_audio.py for every "
                              "event that the beat's hyperframes/<composition>/cues.json does not list (or when that "
                              "file does not exist yet), scaled to the v04 beat length and moved to v05 by the cut "
                              "map. '~29'/'~48' are taken as 29/48; a range a..b is stored as name=a, name_end=b.",
                   "_durations": sb_dur, **{b: sb.get(b, {}) for b in self.beats if b in sb_dur}}
            CUE_DEFAULTS.write_text(json.dumps(doc, indent=1) + "\n")
            log("wrote", CUE_DEFAULTS.relative_to(ROOT))
        self.defaults = load_json(CUE_DEFAULTS)
        drift = {b: (sb.get(b, {}), self.defaults.get(b, {})) for b in self.beats
                 if sb.get(b, {}) != self.defaults.get(b, {})}
        if drift:
            log("WARNING: .tesseract-work/cue_defaults.json differs from STORYBOARD.md (use --refresh-cue-defaults):", drift)
        dflt_dur = self.defaults.get("_durations") or sb_dur
        v01 = load_json(CUES_V01)["beats"] if CUES_V01.exists() else {}
        self.cut = CutMap(beat_map)
        self.source = {}          # beat -> where its events came from
        self.event_source = {}    # "B16.rewind_end" -> file
        self.scaled = {}          # beat -> note on v01 frames scaled to the v04 beat
        self.remapped = {}        # beat -> note on v04 frames moved to v05
        self.dropped = {}         # beat -> {event: v04 frame} cut by the v05 trims
        self.schema = {}          # beat -> "v05" | "legacy" | "none"
        self.v05 = {}             # beat -> parsed v05 lists
        self.notes = []           # parse notes
        self.table = {}           # SFX events
        self.music_table = {}     # music marks (always with fallback)
        for bid, b in self.beats.items():
            comp = b["composition"]["id"]
            dur = int(b["dur_frames"])
            dur4 = int(b.get("v04_dur_frames") or dur)
            cj = cues_path(comp)
            # STORYBOARD defaults: v01 frames -> v04 beat length -> v05 frames
            k_sb = dur4 / float(dflt_dur.get(bid) or dur4)
            sb_map, sb_cut = {}, {}
            for k, v in self.defaults.get(bid, {}).items():
                f4 = int(round(int(v) * k_sb))
                f5 = self.cut.map(bid, f4)
                if f5 is None:
                    sb_cut[k] = f4
                else:
                    sb_map[k] = f5
                    self.event_source["%s.%s" % (bid, k)] = "STORYBOARD.md cues (x%.4f to the v04 beat%s)" % (
                        k_sb, "" if self.cut.identity(bid) else ", moved to v05")
            raw_doc = load_json(cj) if cj.exists() else None
            if raw_doc is not None and is_v05_cues(raw_doc):
                self.schema[bid] = "v05"
                ev_cj = {k: int(v) for k, v in (raw_doc.get("events") or {}).items()}
                self.v05[bid] = parse_v05_lists(raw_doc, bid, self.notes)
                self.table[bid] = dict(ev_cj)
                self.music_table[bid] = dict(sb_map, **ev_cj)
                for k in ev_cj:
                    self.event_source["%s.%s" % (bid, k)] = str(cj.relative_to(ROOT) if cj.is_relative_to(ROOT) else cj) + " (v05)"
                self.source[bid] = "%s (v05 schema: events as written, no STORYBOARD fallback)" % (
                    cj.relative_to(ROOT) if cj.is_relative_to(ROOT) else cj)
                if sb_cut:
                    self.dropped[bid] = {"STORYBOARD:" + k: v for k, v in sb_cut.items()}
                continue
            merged = dict(sb_map)
            if raw_doc is not None:
                self.schema[bid] = "legacy"
                raw = {k: int(v) for k, v in (raw_doc.get("events") or {}).items()}
                snap = (v01.get(bid) or {})
                stale = bool(raw) and snap.get("events") == raw and int(snap.get("v01_dur_frames") or dur4) != dur4
                k_cj = dur4 / float(snap["v01_dur_frames"]) if stale else 1.0
                ev4 = {k: int(round(v * k_cj)) for k, v in raw.items()}
                if stale:
                    self.scaled[bid] = "%s is still v01-timed (= the v01 snapshot): %s scaled x%.4f (%d -> %d f) to %s" % (
                        cj.relative_to(ROOT), raw, k_cj, int(snap["v01_dur_frames"]), dur4, ev4)
                    log("note: " + self.scaled[bid])
                ev_cj, cut_ev = {}, {}
                for k, f4 in ev4.items():
                    f5 = self.cut.map(bid, f4)
                    if f5 is None:
                        cut_ev[k] = f4
                    else:
                        ev_cj[k] = f5
                for k in set(cut_ev) | set(sb_cut):           # cut away: not refilled from the STORYBOARD
                    merged.pop(k, None)
                if cut_ev or sb_cut:
                    self.dropped[bid] = dict(cut_ev, **{"STORYBOARD:" + k: v for k, v in sb_cut.items()})
                if ev4 != ev_cj:
                    self.remapped[bid] = "%s: legacy (v04) frames %s -> v05 %s%s" % (
                        cj.relative_to(ROOT) if cj.is_relative_to(ROOT) else cj, ev4, ev_cj,
                        "; cut by the v05 trims (no sound): %s" % cut_ev if cut_ev else "")
                    log("note: " + self.remapped[bid])
                for k, v in ev_cj.items():
                    merged[k] = v
                    self.event_source["%s.%s" % (bid, k)] = str(cj.relative_to(ROOT) if cj.is_relative_to(ROOT) else cj) + (
                        " (v01, scaled)" if stale else "") + ("" if self.cut.identity(bid) else " (v04, moved to v05)")
                missing = sorted(set(sb_map) - set(ev_cj) - set(cut_ev))
                self.source[bid] = str(cj.relative_to(ROOT) if cj.is_relative_to(ROOT) else cj) + (
                    " (v01-timed, scaled)" if stale else "") + ("" if self.cut.identity(bid) else " (legacy, moved to v05)") + (
                    " (+ STORYBOARD cues for %s)" % ", ".join(missing) if missing else "")
            else:
                self.schema[bid] = "none"
                self.source[bid] = "STORYBOARD.md cues (scaled)" if sb_map else "no cues"
                if sb_cut:
                    self.dropped[bid] = {"STORYBOARD:" + k: v for k, v in sb_cut.items()}
            self.table[bid] = merged
            self.music_table[bid] = dict(merged)

    def beat_start_frame(self, beat: str) -> int:
        return int(self.beats[beat]["start_frame"])

    def has(self, ref: str) -> bool:
        beat, name = ref.split(".", 1)
        return name == "start" or name in self.table.get(beat, {})

    def frame(self, ref: str, table=None) -> int:
        """'B8.first_black' -> edit frame; 'B15.start' -> beat start frame."""
        beat, name = ref.split(".", 1)
        tab = self.table if table is None else table
        if name == "start":
            return self.beat_start_frame(beat)
        if name not in tab.get(beat, {}):
            raise KeyError("event %s not found (source %s)" % (ref, self.source.get(beat)))
        return self.beat_start_frame(beat) + tab[beat][name]

    def t(self, ref: str) -> float:
        return frames_to_s(self.frame(ref))

    def tm(self, ref: str) -> float:
        """Music marks: the event with the STORYBOARD/legacy fallback even for v05 files; a mark that exists nowhere
        falls back to its beat's start (recorded in self.notes)."""
        try:
            return frames_to_s(self.frame(ref, self.music_table))
        except KeyError:
            note = "music mark %s: no such event anywhere; its beat's start is used" % ref
            if note not in self.notes:
                self.notes.append(note)
                log("WARNING: " + note)
            return frames_to_s(self.beat_start_frame(ref.split(".", 1)[0]))

    def beat_frame(self, ref: str) -> int:
        beat, name = ref.split(".", 1)
        if name == "start":
            return 0
        if name in self.table.get(beat, {}):
            return self.table[beat][name]
        return self.music_table[beat][name]


# --------------------------------------------------------------------------------------------
# FFmpeg derivatives (originals are never touched; recipe JSON beside every derivative)
# --------------------------------------------------------------------------------------------
def make_derivative(src: Path, out: Path, afilter: str, codec="pcm_f32le", note=""):
    out.parent.mkdir(parents=True, exist_ok=True)
    recipe = {"source": str(src.relative_to(ROOT)), "source_sha256": sha256(src), "ffmpeg_filter": afilter,
              "codec": codec, "ffmpeg": run(["ffmpeg", "-version"]).stdout.splitlines()[0], "note": note,
              "made_by": "tools/build_tesseract_audio.py"}
    rpath = out.with_suffix(".json")
    if out.exists() and rpath.exists():
        old = load_json(rpath)
        if {k: old.get(k) for k in ("source_sha256", "ffmpeg_filter", "codec")} == \
                {k: recipe[k] for k in ("source_sha256", "ffmpeg_filter", "codec")}:
            return out
    tmp = out.with_name(out.stem + ".tmp.wav")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-af", afilter, "-map_metadata", "-1",
         "-flags:a", "+bitexact", "-c:a", codec, "-fflags", "+bitexact", tmp])
    tmp.replace(out)
    recipe["output"] = str(out.relative_to(ROOT))
    recipe["output_sha256"] = sha256(out)
    rpath.write_text(json.dumps(recipe, indent=1) + "\n")
    log("derivative:", out.relative_to(ROOT), "<-", afilter)
    return out


# --------------------------------------------------------------------------------------------
# MP3 decoder offset (Tesseract vs FFmpeg), measured once per file and Tesseract version
# --------------------------------------------------------------------------------------------
def tsrct_version() -> str:
    return run([TSRCT, "--version"]).stdout.strip()


def calibrate_decoder_offsets(files: list) -> dict:
    """Tesseract's MP3 decoder does not apply the LAME/Xing encoder-delay skip that FFmpeg applies,
    so the same source time can play later in Tesseract. Measure the lag per file by exporting it
    from a scratch project and cross-correlating with FFmpeg's decode. Returns {path: lag_seconds}."""
    cache_p = WORK / "decoder_offsets.json"
    cache = load_json(cache_p) if cache_p.exists() else {}
    ver = tsrct_version()
    out = {}
    calib_dir = WORK / "calib"
    for f in files:
        key = sha256(f)
        c = cache.get(key)
        if c and c.get("tsrct") == ver:
            out[str(f)] = c["lag_s"]
            continue
        calib_dir.mkdir(parents=True, exist_ok=True)
        proj = calib_dir / "calib.tsrct"
        if proj.exists():
            proj.unlink()
        tsrct("project", "create", "--project", proj)
        tsrct("project", "import-asset", "--project", proj, "--file", f, "--asset-id", "aud-calib", "--kind", "audio")
        info = probe(f)
        dur_ms = int(info["duration"] * 1000)
        s0 = 140000 if dur_ms > 150000 else 0           # music: a busy section; SFX: the start
        d = min(6000, dur_ms - s0 - 50)
        jpath = calib_dir / "calib.json"
        tsrct("project", "checkout", "--project", proj, "--output", jpath)
        doc = load_json(jpath)
        doc["duration"] = d / 1000 + 0.2
        doc["composition"]["layers"] = [audio_layer_json(1, "calib", "aud-calib", 0, d, s0, dur_ms, 1.0,
                                                         "soundEffect", f.name, "")]
        jpath.write_text(json.dumps(doc))
        tsrct("project", "commit", "--project", proj, "--file", jpath)
        wav = calib_dir / "calib.wav"
        tsrct("export-audio", "--project", proj, "--output", wav)
        y = read_wav(wav)[: int(d / 1000 * SR)].mean(axis=1)
        ref = decode(f)[int(s0 / 1000 * SR): int(s0 / 1000 * SR) + len(y)].mean(axis=1)
        best_lag = xcorr_lag(y, ref, int(0.1 * SR))          # FFT cross-correlation, +-100 ms
        lag_s = best_lag / SR
        cache[key] = {"file": str(f.relative_to(ROOT)), "lag_samples_48k": best_lag, "lag_s": lag_s, "tsrct": ver}
        out[str(f)] = lag_s
        log("decoder offset: %s plays %+.2f ms vs FFmpeg" % (f.name, lag_s * 1000))
    cache_p.write_text(json.dumps(cache, indent=1) + "\n")
    if calib_dir.exists():
        shutil.rmtree(calib_dir)
    return out


# --------------------------------------------------------------------------------------------
# Document JSON builders
# --------------------------------------------------------------------------------------------
def audio_layer_json(lid, name, asset, E, D, S0, intrinsic, volume, modality, source_name, description):
    return {
        "type": "Audio", "id": lid, "name": name,
        "playback": {"type": "windowed", "inputRange": {"start": E, "duration": D},
                     "mapping": {"type": "linear", "input": {"start": 0, "duration": D},
                                 "output": {"start": 0, "duration": D}},
                     "inputOffsetMs": S0 - E},
        "sourceRange": {"start": S0, "duration": D},
        "sourceIntrinsicDuration": intrinsic,
        "source": {"assetId": asset},
        "volume": round(float(volume), 6),
        "captionsEnabled": False,
        "metadata": {"modality": modality, "source": "uploaded", "sourceName": source_name},
        "description": description,
    }


def group_json(gid, name, layers, dur_ms, description):
    return {
        "type": "Group", "id": gid, "name": name, "blendMode": "normal",
        "playback": {"type": "windowed", "inputRange": {"start": 0, "duration": dur_ms},
                     "mapping": {"type": "linear", "input": {"start": 0, "duration": dur_ms},
                                 "output": {"start": 0, "duration": dur_ms}},
                     "inputOffsetMs": 0},
        "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100},
        "layers": layers,
        "description": description,
    }


def keyframes_entry(layer_id, points, key_prefix):
    """points: [(layerTime_ms, linear gain)] on the layer's CONTENT clock (= source time for the
    documented offset-style mapping: parent time + inputOffsetMs). Measured: a keyframe's easing
    governs the segment ARRIVING at it, so every keyframe is 'linear' (a final 'hold' would turn the
    last ramp, e.g. a fade-out, into a step at its end)."""
    kfs = []
    for i, (t, g) in enumerate(points):
        kfs.append({"id": "%s-%04d" % (key_prefix, i), "layerTime": int(t),
                    "value": {"type": "float", "value": round(float(g), 7)},
                    "easing": {"type": "linear"}})
    return {"target": {"kind": "layer", "layerId": layer_id, "propertyType": "volume"},
            "animator": {"type": "keyframes", "enabled": True, "keyframes": kfs}}


def simplify(t, g, tol_rel=0.003, tol_abs=2e-5):
    """Keep the fewest breakpoints of a sampled piecewise-linear gain curve (iterative RDP on the
    vertical error, relative to the local level)."""
    n = len(t)
    keep = np.zeros(n, bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        seg_t = t[a + 1:b]
        interp = g[a] + (g[b] - g[a]) * (seg_t - t[a]) / (t[b] - t[a])
        err = np.abs(g[a + 1:b] - interp)
        lim = np.maximum(tol_abs, tol_rel * np.maximum(np.abs(g[a + 1:b]), 1e-9))
        k = int(np.argmax(err - lim))
        if err[k] > lim[k]:
            m = a + 1 + k
            keep[m] = True
            stack.append((a, m))
            stack.append((m, b))
    idx = np.nonzero(keep)[0]
    return t[idx], g[idx]


# --------------------------------------------------------------------------------------------
# Music: ducking + MU1-MU8 envelope
# --------------------------------------------------------------------------------------------
def phrase_spans(words: list, merge_gap: float):
    spans = []
    for w in words:
        s, e = float(w["start"]), float(w["end"])
        if spans and s - spans[-1][1] < merge_gap - 1e-9:
            spans[-1][1] = max(spans[-1][1], e)
            spans[-1][2].append(w["text"])
        else:
            spans.append([s, e, [w["text"]]])
    return [(a, b, " ".join(t)) for a, b, t in spans]


def duck_curve(tt, spans):
    """Amplitude-linear timed ducking: each phrase is a trapezoid (ramp down over ATTACK_S ending
    at the phrase start, hold, ramp up over RELEASE_S from the phrase end); the curve is the
    minimum over phrases, which is what a 50/300 ms ducker does in gaps shorter than 350 ms."""
    d = lin(DUCK_DB)
    out = np.ones_like(tt)
    for i, (s, e, _) in enumerate(spans):
        a0 = s - ATTACK_S
        g = np.ones_like(tt)
        if i == 0 and a0 <= 0:          # voice starts in the first frame: start the bed already ducked
            g[tt < s] = d
        else:
            m = (tt >= a0) & (tt < s)
            g[m] = 1 + (d - 1) * (tt[m] - a0) / ATTACK_S
        m = (tt >= s) & (tt <= e)
        g[m] = d
        m = (tt > e) & (tt < e + RELEASE_S)
        g[m] = d + (1 - d) * (tt[m] - e) / RELEASE_S
        out = np.minimum(out, g)
    return out


def ramp(tt, t0, t1, v0, v1):
    """piecewise: v0 before t0, linear to v1 at t1, v1 after."""
    if t1 <= t0:
        return np.where(tt < t0, v0, v1)
    return np.where(tt <= t0, v0, np.where(tt >= t1, v1, v0 + (v1 - v0) * (tt - t0) / (t1 - t0)))


def music_anchor(words: list, music_plan: dict) -> dict:
    """v02 re-anchor (plan p.34: 'anchor MU5 on fun first'): the measured drop downbeat (track s, FFmpeg clock)
    on the onset of 'fun' (B10) -> offset = drop - onset. MU2/MU3 are where the track's own measured sections then
    land; they are checked against 'broke'/'dull' with the plan's rules (a whole-bar edit inside the breakdown is
    the only allowed fix, and only when MU3 misses 'dull' by more than 1 s)."""
    sec = music_plan["analysis"]["sections_track_s"]
    drop = float(sec["drop_downbeat"])
    word = lambda beat, stem: next(w for w in words if w["beat"] == beat and w["text"].lower().strip(".,?!:").startswith(stem))
    fun, broke, dull = word("B10", "fun"), word("B2", "broke"), word("B6", "dull")
    off = round(drop - float(fun["start"]), 4)
    planned = music_plan.get("offset_s")
    if planned is None or abs(float(planned) - off) > 0.0005:
        log("WARNING: 02_Music/music_plan.json offset_s %s != drop %.2f - 'fun' %.3f = %.4f s; using %.4f s" % (
            planned, drop, float(fun["start"]), off, off))
    mu2, mu3 = float(sec["breakdown"][0]) - off, float(sec["near_silence"][0]) - off
    return {"offset_s": off, "drop_track_s": drop, "fun_onset_s": float(fun["start"]),
            "music_plan_offset_s": planned,
            "MU2": {"edit_s": round(mu2, 3), "track_s": float(sec["breakdown"][0]), "broke_s": [broke["start"], broke["end"]],
                    "delta_from_onset_s": round(mu2 - float(broke["start"]), 3),
                    "within_half_second": abs(mu2 - float(broke["start"])) <= 0.5,
                    "inside_word": float(broke["start"]) <= mu2 <= float(broke["end"])},
            "MU3": {"edit_s": round(mu3, 3), "track_s": float(sec["near_silence"][0]), "dull_s": [dull["start"], dull["end"]],
                    "delta_from_onset_s": round(mu3 - float(dull["start"]), 3),
                    "within_1s": abs(mu3 - float(dull["start"])) <= 1.0, "on_or_after": mu3 >= float(dull["start"]) - 1e-6},
            "bar_s": float(music_plan["analysis"]["bar_s"])}


def bar_edit_plan(music_file: Path, music_plan: dict, anchor: dict) -> dict:
    """The MU2 whole-bar edit (see MU2_BAR_EDIT). Candidate bars 2..n-1 of the breakdown (not the arrival, not the
    bar into MU3); each is scored by how alike the two seam sides are: 10 octave-band levels (40 Hz-20 kHz) of the
    0.5 s before the removed bar vs the 0.5 s before the bar after it (what the crossfade mixes) plus the 0.5 s
    after both bar lines (what follows the seam vs what would have followed); the lowest sum wins."""
    sec = music_plan["analysis"]["sections_track_s"]
    bar = float(music_plan["analysis"]["bar_s"])
    bd0, bd1 = (float(v) for v in sec["breakdown"])
    n = int(round((bd1 - bd0) / bar))
    off = anchor["offset_s"]
    pre = off - bar
    x = decode(music_file).mean(axis=1)

    def bands(seg):
        S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        f = np.fft.rfftfreq(len(seg), 1 / SR)
        e = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240, 20000]
        return 10 * np.log10(np.array([S[(f >= a) & (f < b)].sum() + 1e-12 for a, b in zip(e, e[1:])]))

    seg = lambda a, b: x[int(round(a * SR)): int(round(b * SR))]
    cands = []
    for k in range(2, n):
        T = bd0 + (k - 1) * bar                        # track time of the removed bar's first bar line
        d_before = float(np.mean(np.abs(bands(seg(T - 0.5, T)) - bands(seg(T + bar - 0.5, T + bar)))))
        d_after = float(np.mean(np.abs(bands(seg(T, T + 0.5)) - bands(seg(T + bar, T + bar + 0.5)))))
        cands.append({"bar": k, "track_s": [round(T, 4), round(T + bar, 4)], "seam_edit_s": round(T - pre, 4),
                      "d_before_db": round(d_before, 2), "d_after_db": round(d_after, 2),
                      "score": round(d_before + d_after, 2)})
    pick = next((c for c in cands if c["bar"] == BAR_EDIT_BAR), None) if BAR_EDIT_BAR else min(cands, key=lambda c: c["score"])
    mu2_old, mu2_new = anchor["MU2"]["edit_s"], bd0 - pre
    b0, b1 = anchor["MU2"]["broke_s"]
    closer = abs(mu2_new - b0) < abs(mu2_old - b0) or b0 <= mu2_new <= b1
    seam = pick["seam_edit_s"]
    keep = bool(MU2_BAR_EDIT and closer and anchor["MU3"]["within_1s"] and mu2_new < seam < anchor["MU3"]["edit_s"])
    return {"applied": keep, "bar_s": bar, "offset_before_seam_s": round(pre, 4), "offset_after_seam_s": off,
            "removed_bar": pick["bar"], "removed_track_s": pick["track_s"], "seam_bar_line_edit_s": seam,
            "xfade_s": [round(seam - BAR_EDIT_LEAD_S - BAR_EDIT_XFADE_S, 4), round(seam - BAR_EDIT_LEAD_S, 4)],
            "xfade": "equal power (cos/sin), %d ms, ending %d ms before the bar line" % (
                BAR_EDIT_XFADE_S * 1000, BAR_EDIT_LEAD_S * 1000),
            "MU2_edit_s": round(mu2_new, 4), "MU2_without_edit_s": round(mu2_old, 4), "broke_s": [b0, b1],
            "MU2_inside_broke": bool(b0 <= mu2_new <= b1), "MU2_after_onset_s": round(mu2_new - b0, 3),
            "candidates": cands,
            "conditions": {"MU2_closer_to_broke": bool(closer), "MU3_within_1s": anchor["MU3"]["within_1s"],
                           "seam_between_MU2_and_MU3": bool(mu2_new < seam < anchor["MU3"]["edit_s"]),
                           "MU5_after_seam": bool(seam < anchor["fun_onset_s"])}}


def music_envelopes(ev: Events, beat_map: dict, spans, dropouts=()):
    """The bed's pre-master gain on a 1 ms grid. v05 (doc 2.7, G9): duck DUCK_DB under the voice, silent inside every
    cues.json dropout window (2-6 f ending on the big word, 10 ms ramps), full level again from 'fun.' (MU5: the
    drop, +3 dB for 2 s); the v02 marks MU4-MU8 as before. Marks read ev.tm (fallbacks, never a KeyError)."""
    t_end = float(beat_map["vo_end_s"])                       # MU8: hard stop at the end of "now?"
    tt = np.arange(0, ms(t_end) + 1) / 1000.0                  # 1 ms grid on the edit clock
    marks = {
        "MU1": 0.0,
        "MU4_start": ev.tm("B8.first_black"),
        "MU4_end": ev.tm("B8.first_black") + frames_to_s(MU4_FRAMES),
        "MU5": ev.tm("B10.fun"),
        "MU6_start": ev.tm("B15.start"),
        "MU6_end": ev.tm("B15.label"),
        "MU7_start": ev.tm("B16.rewind"),
        "MU7_end": ev.tm("B16.rewind_end"),
        "MU7_return": ev.tm("B17.start"),
        "MU8": t_end,
    }
    duck = duck_curve(tt, spans)
    # MU5 lift: +3 dB from the drop for 2 s, then back over MU5_RETURN_S
    l5 = ramp(tt, marks["MU5"] - EDGE_S, marks["MU5"], 1.0, lin(MU5_LIFT_DB)) * \
        ramp(tt, marks["MU5"] + MU5_HOLD_S, marks["MU5"] + MU5_HOLD_S + MU5_RETURN_S, 1.0, lin(-MU5_LIFT_DB))
    # MU7: -6 dB from the end of the rewind cut to the B17 cut
    l7 = ramp(tt, marks["MU7_end"], marks["MU7_end"] + EDGE_S, 1.0, lin(MU7_DB)) * \
        ramp(tt, marks["MU7_return"], marks["MU7_return"] + MU7_RETURN_S, 1.0, lin(-MU7_DB))
    # mutes: start de-click ramp (MU1), MU4 15f, MU7 rewind cut, MU8 stop
    mute = ramp(tt, 0.0, EDGE_S, 0.0, 1.0)
    for a, b in ((marks["MU4_start"], marks["MU4_end"]), (marks["MU7_start"], marks["MU7_end"])):
        mute = mute * np.maximum(ramp(tt, a - EDGE_S, a, 1.0, 0.0), ramp(tt, b, b + EDGE_S, 0.0, 1.0))
    mute = mute * ramp(tt, marks["MU8"] - EDGE_S, marks["MU8"], 1.0, 0.0)
    if dropouts:                                                # v05: cues.json dropouts (doc 2.7 micro-silences)
        mute = mute * mute_env(tt, [(a, b) for a, b, *_ in dropouts])
        marks["dropouts"] = [[round(a, 3), round(b, 3)] for a, b, *_ in dropouts]
    # MU6: crossfade main -> low-passed copy (-6 dB) and back, EDGE_S each way
    x6 = ramp(tt, marks["MU6_start"] - EDGE_S, marks["MU6_start"], 0.0, 1.0) * \
        ramp(tt, marks["MU6_end"], marks["MU6_end"] + EDGE_S, 1.0, 0.0)
    base = lin(MUSIC_BASE_DB)                                   # pre-master
    bed = base * duck * l5 * l7 * mute
    main = bed * (1 - x6)
    lp = bed * x6 * lin(MU6_DB)
    return tt, main, lp, marks, duck


# --------------------------------------------------------------------------------------------
# SFX clips from sfx_plan.json
# --------------------------------------------------------------------------------------------
class Clip:
    def __init__(self, **kw):
        self.fade_in = 0.0
        self.fade_out = 0.0
        self.rel_gain_db = 0.0
        self.gain_link = None
        self.notes = []
        self.__dict__.update(kw)

    @property
    def end(self):
        return self.edit_start + self.dur


def file_stem_label(fname: str) -> str:
    stem = Path(fname).stem
    return re.sub(r"^S\d+[a-z]?_", "", stem)


def s13_keystrokes(path: Path):
    """Onsets of the single keystrokes in the S13 typing file (1 ms peak envelope)."""
    x = decode(path)
    m = np.max(np.abs(x), axis=1)
    w = SR // 1000
    n = len(m) // w
    env = m[: n * w].reshape(n, w).max(axis=1)
    d = 20 * np.log10(env + 1e-12)
    pk = d.max()
    thr, low = pk - 20, pk - 32
    onsets, armed = [], True
    for i in range(n):
        if armed and d[i] > thr:
            j = i
            while j > 0 and d[j - 1] > low:
                j -= 1
            onsets.append(j / 1000)
            armed = False
        elif not armed and d[i] < low and np.all(d[i:i + 20] < low):
            armed = True
    strokes = []
    for k, o in enumerate(onsets):
        nxt = onsets[k + 1] if k + 1 < len(onsets) else n / 1000
        a = round(o - 0.006, 3)
        b = round(min(o + 0.080, nxt - 0.006), 3)
        seg = x[int(a * SR): int(b * SR)]
        strokes.append({"onset": o, "start": a, "end": b, "peak_dbfs": db(float(np.max(np.abs(seg))))})
    return strokes


def build_sfx_clips(ev: Events, sfx_plan: dict, analysis: dict, edit_end: float):
    clips = []
    decisions = {}
    for cue in sfx_plan["cues"]:
        cid = cue["cue"]
        if cid in CUE_OVERRIDES:                      # v02 client notes (CUE_OVERRIDES)
            cue = {k: v for k, v in dict(cue, **CUE_OVERRIDES[cid]).items() if v is not None}
            decisions["%s_v02_override" % cid] = {k: v for k, v in CUE_OVERRIDES[cid].items() if v is not None}
        group = cue["group"]
        if cid == "S13":
            if not ev.has(cue["event"]):
                decisions.setdefault("skipped", []).append("S13 (%s `%s`, %s cues)" % (
                    cue["event"].split(".")[0], cue["event"].split(".", 1)[1], ev.schema.get(cue["event"].split(".")[0])))
                continue
            clips_s13, dec = build_s13(ev, cue)
            clips += clips_s13
            decisions["S13"] = dec
            continue
        layer_specs = []
        if "layers" in cue:
            for i, L in enumerate(cue["layers"]):
                layer_specs.append(dict(L, sub=chr(ord("a") + i)))
        else:
            for i, f in enumerate(cue["files"]):
                layer_specs.append({"file": f, "sub": chr(ord("a") + i) if len(cue["files"]) > 1 else ""})
        for i, L in enumerate(layer_specs):
            fname = L["file"]
            orig = SFX_DIR / fname
            fdur = probe(orig)["duration"]
            event = L.get("event") or cue["event"]
            fallback_note = None
            if not ev.has(event) and cue.get("fallback_event"):
                fallback_note = "%s has no `%s` event yet (source %s): placed on %s instead" % (
                    event.split(".")[0], event.split(".", 1)[1], ev.source[event.split(".")[0]], cue["fallback_event"])
                log("note: %s %s" % (cid, fallback_note))
                event = cue["fallback_event"]
            if not ev.has(event):        # v05: a lane that leaves a legacy event out wants no sound there
                decisions.setdefault("skipped", []).append("%s%s (%s `%s`, %s cues)" % (
                    cid, L["sub"], event.split(".")[0], event.split(".", 1)[1], ev.schema.get(event.split(".")[0])))
                continue
            t_ev = ev.t(event)
            align = L.get("align", cue.get("align", "start"))
            off = frames_to_s(L.get("offset_f", cue.get("offset_f", 0)))
            src_start = 0.0
            dur = fdur
            if "slice_s" in cue:
                src_start, src_end = cue["slice_s"]
                dur = src_end - src_start
            if "trim_to_s" in cue:
                dur = min(dur, cue["trim_to_s"])
            if align == "start":
                start = t_ev + off
                rule = "start on %s%s" % (event, " %+df" % L.get("offset_f", cue.get("offset_f", 0))
                                          if (L.get("offset_f", cue.get("offset_f", 0))) else "")
            elif align == "peak":
                start = t_ev - cue["peak_at_s"] + off
                rule = "peak at %.2f s on %s" % (cue["peak_at_s"], event)
            elif align == "sound_start":
                start = t_ev + off - L["sound_starts_s"]
                rule = "sound (%.2f s into file) starts %+df from %s" % (L["sound_starts_s"], L["offset_f"], event)
            elif align == "end":
                start = t_ev + off - dur
                rule = "file end on %s" % event
                if cue.get("from_event") and ev.has(cue["from_event"]):
                    span = t_ev - ev.t(cue["from_event"])
                    if dur > span:          # head trim so it starts on from_event
                        src_start += dur - span
                        dur = span
                        start = t_ev - dur
                        rule += " (head trimmed to start on %s)" % cue["from_event"]
                    else:
                        rule += " (file %.3f s < %.3f s span from %s: starts %df after it)" % (
                            dur, span, cue["from_event"], round((start - ev.t(cue["from_event"])) * FPS))
            else:
                raise ValueError(align)
            c = Clip(cue=cid, sub=L["sub"], group=group, file=fname, orig=orig, asset_file=orig,
                     src_start=src_start, dur=dur, edit_start=start, event=event, event_t=t_ev, rule=rule,
                     plan=cue.get("plan", ""), file_dur=fdur,
                     target_dbfs=L.get("peak_dbfs", cue.get("peak_dbfs", cue.get("peak_dbfs_combined"))),
                     combined=("peak_dbfs_combined" in cue) and len(layer_specs) > 1,
                     rel_gain_db=float(L.get("extra_gain_db", 0.0)), gain_link=cue.get("gain_link"))
            if fallback_note:
                c.notes.append(fallback_note)
                c.rule += " (fallback)"
            if c.gain_link:
                c.notes.append("v02: plays at %s's pre-master gain (client note 5: the glitch sound of B8)" % c.gain_link)
            if cue.get("fade_out_f"):
                c.fade_out = frames_to_s(cue["fade_out_f"])
            if cue.get("highpass_hz"):
                hp = cue["highpass_hz"]
                der = SFX_DERIVED / ("%s_hp%d.wav" % (Path(fname).stem, hp))
                make_derivative(orig, der, "highpass=f=%d" % hp, note="%s: plan 'high-pass at %d Hz' (p.35)" % (cid, hp))
                c.asset_file = der
                c.derived = "highpass=f=%d (FFmpeg, 2-pole)" % hp
            if src_start > 0.0005 and cid in ("S02", "S14"):
                c.fade_in = EDGE_S
                c.notes.append("10 ms de-click fade-in (the slice starts inside the siren)")
            # never run past the edit: trim the tail with a short fade (S19's PowerDown)
            if c.end > edit_end + 1e-6:
                c.dur = edit_end - c.edit_start
                c.fade_out = max(c.fade_out, frames_to_s(4))
                c.notes.append("tail trimmed at the edit end (%.3f s) with a 4f fade" % edit_end)
            clips.append(c)
    for c in clips:                  # a gain link to a cue that is not in this edit: its level becomes a target
        if c.gain_link and not any(x.cue == c.gain_link for x in clips):
            ref = next((q for q in sfx_plan["cues"] if q["cue"] == c.gain_link), {})
            lvl = ref.get("peak_dbfs", ref.get("peak_dbfs_combined"))
            c.target_dbfs = float(lvl if lvl is not None else (c.target_dbfs if c.target_dbfs is not None else -12.0))
            c.notes.append("%s is not in this edit (its event was left out), so this cue is calibrated on its own at %s's "
                           "plan level, %.1f dBFS" % (c.gain_link, c.gain_link, c.target_dbfs))
            c.gain_link = None
    if decisions.get("skipped"):
        log("legacy S-cues without their event (no sound): " + ", ".join(decisions["skipped"]))
    return clips, decisions


def build_s13(ev: Events, cue: dict):
    fname = cue["files"][0]
    orig = SFX_DIR / fname
    t0 = ev.t(cue["event"])
    letters = [t0 + frames_to_s(2 * k) for k in range(14)]       # T6: 14 letters, one every 2f
    strokes = s13_keystrokes(orig)
    # how the whole file would sit if started on the first letter
    offs = []
    for s in strokes:
        tt = t0 + s["onset"]
        k = int(np.argmin([abs(tt - L) for L in letters]))
        offs.append(round((tt - letters[k]) * 1000))
    gaps = [round((b["onset"] - a["onset"]) * 1000) for a, b in zip(strokes, strokes[1:])]
    first_late_ms = round(strokes[0]["onset"] * 1000)
    last_after_ms = round((t0 + strokes[-1]["onset"] - letters[-1]) * 1000)
    sits = (first_late_ms <= 34 and max(abs(o) for o in offs) <= 34 and max(gaps) <= 100)
    dec = {"letters_f": [ev.beat_frame(cue["event"]) + 2 * k for k in range(14)],
           "file_keystroke_onsets_s": [s["onset"] for s in strokes],
           "keystroke_gaps_ms": gaps,
           "if_file_started_on_first_letter": {
               "first_keystroke_after_first_letter_ms": first_late_ms,
               "keystroke_offsets_from_nearest_letter_ms": offs,
               "last_keystroke_after_last_letter_ms": last_after_ms},
           "criterion": "sits if the first keystroke is within 1f of the first letter, every keystroke within "
                        "1f of a letter and no gap longer than 3f (a run of silent letters)",
           "sits": bool(sits)}
    clips = []
    if sits:
        clips.append(Clip(cue="S13", sub="", group=cue["group"], file=fname, orig=orig, asset_file=orig,
                          src_start=0.0, dur=probe(orig)["duration"], edit_start=t0, event=cue["event"],
                          event_t=t0, rule="start with the first letter", plan=cue.get("plan", ""),
                          file_dur=probe(orig)["duration"], target_dbfs=cue["peak_dbfs"], combined=False))
        dec["decision"] = "whole file from the first letter"
        return clips, dec
    # slice single keystrokes: one every 2 letters (letters 1,3,...,13 = every 4f), file order
    slots = letters[0::2]
    use = strokes[: len(slots)]
    for k, (slot, s) in enumerate(zip(slots, use)):
        c = Clip(cue="S13", sub="k%d" % (k + 1), group=cue["group"], file=fname, orig=orig, asset_file=orig,
                 src_start=s["start"], dur=round(s["end"] - s["start"], 3),
                 edit_start=slot - (s["onset"] - s["start"]), event=cue["event"], event_t=t0,
                 rule="keystroke %d (file %.3f s) on letter %d (%s %+df)" % (
                     k + 1, s["onset"], 2 * k + 1, cue["event"], 4 * k),
                 plan=cue.get("plan", ""), file_dur=probe(orig)["duration"], target_dbfs=cue["peak_dbfs"],
                 combined=True)
        clips.append(c)
    dec["decision"] = ("sliced: %d single keystrokes, one every 2 letters (every 4f from the type-on), "
                       "keystroke onset on the letter frame; one shared gain (loudest keystroke at the "
                       "plan's -18 dBFS)" % len(clips))
    return clips, dec


# --------------------------------------------------------------------------------------------
# v05: the SFX library layers (cues.json word_pops / key_words / hook_cuts / sfx) and the dropouts
# --------------------------------------------------------------------------------------------
def load_library():
    """03_SFX/v05/library.json -> {name: entry} (None when the library has not been built)."""
    if not SFX_LIB.exists():
        return None
    return load_json(SFX_LIB)["sounds"]


def library_not_used() -> set:
    """Library names the v05 client override retired (REVISION_v05.md S: stamp_thud, whoosh_flip, type_on): kept in the
    library, never placed (a lane file that still lists one gets a warning)."""
    return set(load_json(SFX_LIB).get("not_used_v05", [])) if SFX_LIB.exists() else set()


def library_pick(lib: dict, name: str, counters: dict):
    """'tick' / 'hit' rotate their variants in call order (edit order); 'tick_2' / 'hit_3' pick one.
    -> (canonical name, entry, file) or (None, None, None)."""
    if name in lib:
        e = lib[name]
        k = counters.get(name, 0)
        counters[name] = k + 1
        return name, e, e["files"][k % len(e["files"])]
    m = re.fullmatch(r"(.+?)_(\d+)", name)
    if m and m.group(1) in lib and 1 <= int(m.group(2)) <= len(lib[m.group(1)]["files"]):
        e = lib[m.group(1)]
        return m.group(1), e, e["files"][int(m.group(2)) - 1]
    return None, None, None


def build_v05_clips(ev: Events, lib, edit_end: float):
    """One Clip per v05 sound request, in edit order. Placement by the library's align on the edit frame (beat start
    + f): start = the sound's first sample on the frame, peak = its sample peak on the frame, end = its last sample
    at the frame's start. Level = the library default (the file is written at it, so gain 0 dB), or the cue's gain_db
    (sample-peak dBFS, capped at V05_GAIN_CAP_DBFS). A head before 0 s is cut (10 ms fade-in), a tail past the edit
    end too (4f fade); `dur_f` on an sfx item shortens it (3f fade). Rules: one tick per frame (duplicates merged), no
    tick on a frame that has a key word (the key word wins), word_pops/key_words/hook_cuts may carry {"f", "gain_db"}."""
    info = {"requests": 0, "by_kind": {}, "by_beat": {}, "skipped": [], "merged_ticks": 0, "cap_hits": []}
    if not any(ev.v05.values()):
        return [], info
    if lib is None:
        info["skipped"].append("03_SFX/v05/library.json missing: run tools/build_tesseract_sfx_v05.py; no v05 sounds")
        log("WARNING: " + info["skipped"][-1])
        return [], info
    reqs = []                                    # (edit_f, order, kind, name, beat, f, item)
    for bid, L in ev.v05.items():
        b0 = ev.beat_start_frame(bid)
        keys = {it["f"] for it in L["key_words"]}
        seen = set()
        for it in L["word_pops"]:
            if it["f"] in keys or it["f"] in seen:
                info["merged_ticks"] += 1
                continue
            seen.add(it["f"])
            reqs.append((b0 + it["f"], 2, "word_pop", it.get("name") or V05_WORD_POP, bid, it["f"], it))
        for it in L["key_words"]:
            reqs.append((b0 + it["f"], 0, "key_word", V05_KEY_WORD_PAIR[0], bid, it["f"], it))
            reqs.append((b0 + it["f"], 1, "key_word", V05_KEY_WORD_PAIR[1], bid, it["f"], it))
        for it in L["hook_cuts"]:
            reqs.append((b0 + it["f"], 3, "hook_cut", it.get("name") or V05_HOOK_CUT, bid, it["f"], it))
            if bid not in ("B1", "B2"):
                ev.notes.append("%s hook_cuts f%d: outside the hook (B1-B2); placed anyway" % (bid, it["f"]))
        for it in L["sfx"]:
            reqs.append((b0 + it["f"], 4, "sfx", str(it["name"]).strip(), bid, it["f"], it))
    reqs.sort(key=lambda r: (r[0], r[1]))
    # QA: caption frames vs the beat's VO word onsets (beat map words): a lane's file written for another timing
    # shows up as frames that sit on no word (G4/U2: a word appears on its spoken frame, 0-2 f late is fine)
    info["caption_alignment"] = {}
    for bid, L in ev.v05.items():
        b0 = ev.beat_start_frame(bid)
        ons = [int(w_["start_frame"]) - b0 for w_ in ev.beats[bid].get("words", [])]
        fr = [it["f"] for it in L["word_pops"] + L["key_words"]]
        if not fr or not ons:
            continue
        off = [min((f_ - o for o in ons), key=abs) for f_ in fr]
        ok = sum(1 for d_ in off if -1 <= d_ <= 3)
        info["caption_alignment"][bid] = {"caption_frames": len(fr), "on_a_word_onset": ok,
                                          "median_offset_f": float(np.median(off)), "stale_timing_suspected": ok < 0.8 * len(fr)}
        if ok < 0.8 * len(fr):
            msg = ("%s cues.json: only %d of %d word_pops/key_words frames sit on a VO word onset (-1..+3 f; median offset "
                   "%+.0f f): written for another timing? re-time it to the beat map's words" % (bid, ok, len(fr), np.median(off)))
            ev.notes.append(msg)
            log("WARNING: " + msg)
    counters, clips = {}, []
    retired = library_not_used()
    for n_, (ef, _, kind, name, bid, f, it) in enumerate(reqs):
        canon, e, fname = library_pick(lib, name, counters)
        if e is None:
            info["skipped"].append("%s f%d %s: no library sound named %r" % (bid, f, kind, name))
            log("WARNING: " + info["skipped"][-1])
            continue
        if canon in retired:
            why = (e.get("notes") or "").split("NOT USED in v05 ")[-1].strip(" .()")
            info["skipped"].append("%s f%d %s: %r is retired by the client override (%s): not placed, remove it from "
                                   "the cue file" % (bid, f, kind, name, why))
            log("WARNING: " + info["skipped"][-1])
            continue
        path = SFX_LIB_DIR / fname
        fi = next((x for x in e.get("file_info", []) if x["file"] == fname), {})
        fdur = probe(path)["duration"]
        t_ev = frames_to_s(ef)
        align = e.get("align", "start")
        if align == "peak":
            start = t_ev - float(fi.get("peak_s", 0.0))
        elif align == "end":
            start = t_ev - fdur
        else:
            start = t_ev
        src_start, dur, fade_in, fade_out, notes = 0.0, fdur, 0.0, 0.0, []
        if kind == "sfx" and it.get("dur_f"):
            want = frames_to_s(int(it["dur_f"]))
            if want < dur - 1e-6:
                dur, fade_out = want, min(frames_to_s(3), want / 3)
                notes.append("shortened to %df (dur_f) with a %.0f ms fade" % (int(it["dur_f"]), fade_out * 1000))
        if start < 0:
            src_start, dur, start = -start, dur + start, 0.0
            fade_in = EDGE_S
            notes.append("head before 0 s cut (10 ms fade-in)")
        if start + dur > edit_end + 1e-6:
            dur = edit_end - start
            fade_out = max(fade_out, min(frames_to_s(4), dur / 2))
            notes.append("tail trimmed at the edit end (%.3f s) with a 4f fade" % edit_end)
        if dur <= 0.002:
            info["skipped"].append("%s f%d %s %s: nothing left inside the edit" % (bid, f, kind, name))
            continue
        dflt = float(e["default_peak_dbfs"])               # the sound's level (a variant set: its loudest variant)
        level = dflt
        if it.get("gain_db") is not None and (kind == "sfx" or (kind == "key_word" and canon == V05_KEY_WORD_PAIR[1])
                                              or kind in ("word_pop", "hook_cut")):
            level = float(it["gain_db"])
        elif it.get("gain_db") is not None and kind == "key_word":      # the whoosh follows the thump's override
            level = dflt + float(it["gain_db"]) - float(lib[V05_KEY_WORD_PAIR[1]]["default_peak_dbfs"])
        if level > V05_GAIN_CAP_DBFS:
            info["cap_hits"].append("%s f%d %s gain_db %.1f -> %.1f" % (bid, f, name, level, V05_GAIN_CAP_DBFS))
            level = V05_GAIN_CAP_DBFS
        file_peak = float(fi.get("sample_peak_dbfs", dflt))
        offset = level - dflt                               # layer gain: variants keep their loudness match
        rule = {"start": "start on the frame", "peak": "peak (%.3f s in) on the frame" % float(fi.get("peak_s", 0)),
                "end": "end on the frame"}[align]
        c = Clip(cue="v%04d" % n_, sub="", group=e.get("group", "A3"), file=fname, orig=path, asset_file=path,
                 src_start=src_start, dur=dur, edit_start=start, event="%s.f%d" % (bid, f), event_t=t_ev,
                 beat_f=f, rule="%s: %s" % (kind.replace("_", " "), rule), plan=(it.get("note") or e.get("notes", ""))[:200],
                 file_dur=fdur, target_dbfs=round(file_peak + offset, 2), combined=False, v05=True, kind=kind,
                 sound=canon, cls=e.get("class", "hit"), fade_in=fade_in, fade_out=fade_out, file_peak_dbfs=file_peak,
                 level_offset_db=offset, level_dbfs=round(level, 2))
        c.notes += notes
        if it.get("gain_db") is not None:
            c.notes.append("gain_db %+.1f dBFS (default %.1f)" % (float(it["gain_db"]), float(e["default_peak_dbfs"])))
        clips.append(c)
        info["by_kind"][kind] = info["by_kind"].get(kind, 0) + 1
        info["by_beat"].setdefault(bid, {}).setdefault(kind, 0)
        info["by_beat"][bid][kind] += 1
    info["requests"] = len(reqs)
    for k, c in enumerate(sorted(clips, key=lambda c: (c.edit_start, c.cue))):
        c.layer_id = V05_LAYER_BASE + k
    return clips, info


def v05_gains(clips):
    """v05 library layers play the FILE at its level: the files are written at their default level, so the layer gain
    is 0 dB, or the cue's gain_db minus the default (a variant set moves together, keeping its loudness match). Not
    re-normalised when a cue cuts its head or tail, so a cue never comes out louder than its sound's level. target_dbfs
    = the file's own sample peak + that gain."""
    for c in clips:
        if not getattr(c, "v05", False):
            continue
        c.gain_db = float(c.level_offset_db)
        sig = clip_signal(c, muted=False)
        amp = np.max(np.abs(sig), axis=1)
        c.raw_peak_dbfs = db(float(np.max(amp)))
        c.peak_time = c.edit_start + int(np.argmax(amp)) / SR
        c.gain_group = c.cue


def dropout_windows(ev: Events):
    """cues.json dropouts -> [(t0, t1, beat, f, frames)] edit seconds: silence for `frames` frames ENDING at f."""
    out = []
    for bid, L in ev.v05.items():
        for d in L["dropouts"]:
            f1 = ev.beat_start_frame(bid) + d["f"]
            out.append((frames_to_s(f1 - d["frames"]), frames_to_s(f1), bid, d["f"], d["frames"]))
    return sorted(out)


def apply_dropouts(clips, windows):
    """With the bed off (G9) the risers/ambience obey the dropouts: every clip of a DROPOUT_CLASSES class (library
    class, or LEGACY_CLASS for the plan's S-cues) is silent inside each window it overlaps (10 ms ramps; the gain
    is computed on the unmuted sound)."""
    hits = []
    for c in clips:
        cls = getattr(c, "cls", None) or LEGACY_CLASS.get(c.cue)
        c.mutes = []
        if cls not in DROPOUT_CLASSES:
            continue
        for a, b, bid, f, n in windows:
            if a < c.end - 1e-6 and b > c.edit_start + 1e-6:
                c.mutes.append((max(a, c.edit_start), min(b, c.end)))
                c.notes.append("silent %.3f-%.3f s (dropout %s f%d, %df)" % (a, b, bid, f, n))
                label = ("%s (%s %s)" % (c.sound, c.event.replace(".f", " f"), c.kind.replace("_", " "))
                         if getattr(c, "v05", False) else "%s%s %s" % (c.cue, c.sub, Path(c.file).stem))
                hits.append({"clip": label, "cue": c.cue, "sound": getattr(c, "sound", c.cue),
                             "window_s": [round(a, 3), round(b, 3)], "dropout": "%s f%d (%df)" % (bid, f, n)})
    return hits


def mute_env(tt, mutes):
    g = np.ones_like(np.asarray(tt, float))
    for a, b in mutes or []:
        g = np.minimum(g, np.maximum(ramp(tt, a - EDGE_S, a, 1.0, 0.0), ramp(tt, b, b + EDGE_S, 0.0, 1.0)))
    return g


def clip_signal(c: Clip, lag_s: float = 0.0, muted: bool = True):
    """Gainless signal of a clip as Tesseract will play it (fades amplitude-linear; dropout mutes unless muted=False)."""
    x = decode(c.asset_file)
    a = int(round(c.src_start * SR))
    n = int(round(c.dur * SR))
    seg = np.zeros((n, 2))
    part = x[a: a + n]
    seg[: len(part)] = part
    env = np.ones(n)
    if c.fade_in > 0:
        k = int(round(c.fade_in * SR))
        env[:k] *= np.linspace(0, 1, k, endpoint=False)
    if c.fade_out > 0:
        k = int(round(c.fade_out * SR))
        env[n - k:] *= np.linspace(1, 0, k)
    if muted and getattr(c, "mutes", None):
        env *= mute_env(c.edit_start + np.arange(n) / SR, c.mutes)
    return seg * env[:, None]


def quantize_clips(clips):
    """Tesseract places layers in whole milliseconds; use exactly those times everywhere (gains,
    model, report) so the model lines up with the render sample-for-sample."""
    for c in clips:
        intr_ms = int(probe(c.asset_file)["duration"] * 1000)
        c.E = ms(c.edit_start)
        c.S0t = ms(c.src_start)                     # source start on the FFmpeg decode clock
        c.D = min(ms(c.dur), intr_ms - c.S0t)
        c.edit_start, c.src_start, c.dur = c.E / 1000.0, c.S0t / 1000.0, c.D / 1000.0
        c.intr_ms = intr_ms


def gain_groups(clips):
    groups = {}
    for c in clips:
        groups.setdefault(c.cue if c.combined else c.cue + c.sub, []).append(c)
    return groups


def sfx_model(clips, n_samples, master=None):
    """Per-group sum of every clip at its gain (x master), and each clip's own placed signal."""
    model = {g: np.zeros((n_samples, 2)) for g in SFX_GROUPS}
    own = {}
    for c in clips:
        sig = clip_signal(c) * lin(c.gain_db)
        if master is not None:
            sig = sig * master(c.edit_start + np.arange(len(sig)) / SR)[:, None]
        i = int(round(c.edit_start * SR))
        L = max(0, min(len(sig), n_samples - i))
        model[c.group][i: i + L] += sig[:L]
        own[id(c)] = (i, sig[:L])
    return model, own


def isolated_peaks(clips, stems_g, model, own):
    """Each gain group's rendered sample peak, isolated from overlapping cues of the same group by
    subtracting their model (placements are sample-exact; only resampler detail differs)."""
    out = {}
    for key, cs in gain_groups(clips).items():
        g = cs[0].group
        i0 = min(own[id(c)][0] for c in cs)
        i1 = max(own[id(c)][0] + len(own[id(c)][1]) for c in cs)
        others = model[g][i0:i1].copy()
        for c in cs:
            i, sig = own[id(c)]
            others[i - i0: i - i0 + len(sig)] -= sig
        iso = stems_g[g][i0:i1] - others
        k = int(np.argmax(np.max(np.abs(iso), axis=1)))
        out[key] = {"peak_dbfs": db(float(np.max(np.abs(iso)))), "peak_s": (i0 + k) / SR,
                    "window_s": (i0 / SR, i1 / SR), "group": g, "clips": cs}
    return out


def compute_sfx_gains(clips):
    """Linear volume per clip so the cue's sample peak hits the plan's peak level
    (combined peak for layered cues, mixed here at their real offsets and relative gains)."""
    groups = {}
    for c in clips:
        key = c.cue if c.combined else (c.cue, c.sub)
        groups.setdefault(key, []).append(c)
    for key, cs in groups.items():
        if cs[0].gain_link or getattr(cs[0], "v05", False):
            continue
        t0 = min(c.edit_start for c in cs)
        t1 = max(c.end for c in cs)
        buf = np.zeros((int(math.ceil((t1 - t0) * SR)) + 2, 2))
        for c in cs:
            s = clip_signal(c, muted=False) * lin(c.rel_gain_db)
            i = int(round((c.edit_start - t0) * SR))
            buf[i: i + len(s)] += s
        pk = float(np.max(np.abs(buf)))
        target = cs[0].target_dbfs
        g = target - db(pk)
        tp_idx = int(np.argmax(np.max(np.abs(buf), axis=1)))
        for c in cs:
            c.raw_peak_dbfs = db(pk)
            c.gain_db = g + c.rel_gain_db             # pre-master gain of this layer
            c.peak_time = t0 + tp_idx / SR
            c.gain_group = key if isinstance(key, str) else key[0] + key[1]
    link_gains(clips)
    v05_gains(clips)
    return groups


def link_gains(clips):
    """v02: a cue with `gain_link` plays at the linked cue's pre-master gain (S10 = B8's glitch impact at S08's
    level). Its reported plan peak is the level the file reaches at that gain. Re-run after every calibration
    pass so the link follows the linked cue's correction."""
    for c in clips:
        if not c.gain_link:
            continue
        ref = next(x for x in clips if x.cue == c.gain_link)
        sig = clip_signal(c, muted=False)
        amp = np.max(np.abs(sig), axis=1)
        c.raw_peak_dbfs = db(float(np.max(amp)))
        c.gain_db = ref.gain_db - ref.rel_gain_db + c.rel_gain_db
        c.target_dbfs = round(c.raw_peak_dbfs + c.gain_db, 2)
        c.peak_time = c.edit_start + int(np.argmax(amp)) / SR
        c.gain_group = c.cue + c.sub


# --------------------------------------------------------------------------------------------
# Measurement
# --------------------------------------------------------------------------------------------
def ffmpeg_ebur128(path: Path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(path), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    s = r.stderr[r.stderr.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1))
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", s).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", s).group(1))
    return {"integrated_lufs": I, "lra_lu": lra, "true_peak_dbtp": tp}


def region_peak(x, t0, t1):
    a, b = max(0, int(t0 * SR)), min(len(x), int(t1 * SR))
    if b <= a:
        return -200.0
    return db(float(np.max(np.abs(x[a:b]))))


def voice_activity(tt, spans):
    act = np.zeros_like(tt, dtype=bool)
    for s, e, _ in spans:
        act |= (tt >= s) & (tt <= e)
    return act


# --------------------------------------------------------------------------------------------
# Layer specs: every layer's PRE-MASTER gain on a 1 ms edit-clock grid over its window
# --------------------------------------------------------------------------------------------
class Spec:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def clip_pre_curve(c, E, D):
    """Pre-master gain curve of an SFX clip on its window (1 ms grid): gain x fades."""
    tt = (E + np.arange(D + 1)) / 1000.0
    g = np.full(len(tt), lin(c.gain_db))
    rel = tt - E / 1000.0
    if c.fade_in > 0:
        g *= np.clip(rel / c.fade_in, 0, 1)
    if c.fade_out > 0:
        g *= np.clip((D / 1000.0 - rel) / c.fade_out, 0, 1)
    if getattr(c, "mutes", None):
        g *= mute_env(tt, c.mutes)
    return tt, g


def to_layers(specs, master):
    """specs -> (group layers, dynamics entries). master: callable(edit seconds array) -> linear
    gain, applied to every layer. Constant results become a static volume, others keyframes."""
    groups = {k: [] for k in GID}
    entries = []
    for sp in specs:
        g = sp.pre * master(sp.tt)
        t_ms = np.round(sp.tt * 1000).astype(float)
        kt, kg = simplify(t_ms, g)
        static = len(kt) == 2 and abs(kg[0] - kg[1]) <= 1e-6 * max(1e-9, abs(kg[0]))
        vol = float(kg[0]) if static else float(np.max(g))
        sp.final_curve = (kt, kg)
        layer = audio_layer_json(sp.id, sp.name, sp.asset, sp.E, sp.D, sp.S0, sp.intr, vol, sp.modality,
                                 sp.source_name, sp.description)
        groups[sp.group].append(layer)
        if not static:
            off = sp.S0 - sp.E                                   # content clock = parent + offset
            entries.append(keyframes_entry(sp.id, [(int(t) + off, v) for t, v in zip(kt, kg)], sp.key))
    for k in SFX_GROUPS:
        groups[k].sort(key=lambda L: (L["playback"]["inputRange"]["start"], L["id"]))
    return groups, entries


def commit_document(doc_base, groups, entries, edit_end, out_project, json_path):
    doc = json.loads(json.dumps(doc_base))
    dur_ms = ms(edit_end)
    doc["composition"]["layers"] = [
        group_json(GID["A1"], GNAME["A1"], groups["A1"], dur_ms, "A1: voiceover (plan p.38 track layout)"),
        group_json(GID["A2"], GNAME["A2"], groups["A2"], dur_ms, "A2: music MU1-MU8 (plan p.34-35)" if MUSIC else
                   "A2: music, empty since v04 (client note 1: no background music; set MUSIC = True in "
                   "tools/build_tesseract_audio.py to bring a track back)"),
        group_json(GID["A3"], GNAME["A3"], groups["A3"], dur_ms, "A3: SFX hits and impacts (plan p.35-38)"),
        group_json(GID["A4"], GNAME["A4"], groups["A4"], dur_ms, "A4: risers, whooshes and textures (plan p.35-38)"),
        group_json(GID["A5"], GNAME["A5"], groups["A5"], dur_ms, "A5 (v05, doc 2.7): a tick on every caption word "
                   "(cues.json word_pops, 3 samples rotating, -24 dBFS) and a whoosh into + a low thump on every key/hero "
                   "word (key_words, -16/-14 dBFS); 03_SFX/v05 library"),
    ]
    doc["composition"]["dynamics"] = {"entries": entries}
    json_path.write_text(json.dumps(doc, indent=1) + "\n")
    args = ["project", "commit", "--project", PROJECT, "--file", json_path]
    if out_project != PROJECT:
        if out_project.exists():
            out_project.unlink()
        args += ["--output", out_project]
    r = tsrct(*args)
    return doc, json.loads(r.stdout).get("warnings", [])


STEMS = (("voice", "A1"), ("music", "A2"), ("sfx_a3", "A3"), ("sfx_a4", "A4"), ("sfx_a5", "A5"))


def export_stems(doc, prefix, only=None):
    """Copies of the document with the other groups hidden (isHidden mutes their audio)."""
    out = {}
    for name, keep in STEMS:
        if only and name not in only:
            continue
        d = json.loads(json.dumps(doc))
        if not next((g.get("layers") for g in d["composition"]["layers"] if g["id"] == GID[keep]), None):
            out[name] = None                               # an empty group (A2 with MUSIC off): silence
            continue
        for g in d["composition"]["layers"]:
            g["isHidden"] = g["id"] != GID[keep]
        sj, sp = WORK / ("stem_%s.json" % name), WORK / ("stem_%s.tsrct" % name)
        sj.write_text(json.dumps(d))
        if sp.exists():
            sp.unlink()
        tsrct("project", "commit", "--project", PROJECT, "--file", sj, "--output", sp)
        wav = CHECKS / ("%sstem_%s.wav" % (prefix, name))
        tsrct("export-audio", "--project", sp, "--output", wav)
        sp.unlink()
        sj.unlink()
        out[name] = read_wav(wav)
    n = min(len(v) for v in out.values() if v is not None)
    return {k: (v[:n] if v is not None else np.zeros((n, 2))) for k, v in out.items()}


# --------------------------------------------------------------------------------------------
# Master curve (static make-up + limiter-like dips), from the pre-master stems
# --------------------------------------------------------------------------------------------
def solve_master(pre_mix):
    os4 = resample_poly(pre_mix, 4, 1, axis=0)
    blk = SR // 100 * 4                                          # 10 ms blocks at 4x
    nb = len(os4) // blk
    tp_db = 20 * np.log10(np.abs(os4[: nb * blk]).reshape(nb, blk, 2).max(axis=(1, 2)) + 1e-12)
    grid = np.arange(0, len(pre_mix) + 1, SR // 1000) / SR      # 1 ms grid
    ceil = MASTER_CEILING_DBTP - 0.1                             # 0.1 dB for envelope interpolation
    m0 = MASTER_TARGET_LUFS - integrated_lufs(pre_mix)
    for _ in range(12):
        need = tp_db + m0 - ceil
        R = np.zeros(len(grid))
        for j in np.nonzero(need > 0)[0]:
            r, a, b = need[j], j * 0.01, (j + 1) * 0.01
            lo, hi = int((a - MASTER_ATTACK_S) * 1000), int((b + MASTER_RELEASE_S) * 1000) + 1
            seg = grid[max(0, lo): min(len(grid), hi)]
            shape = np.minimum(np.clip((seg - (a - MASTER_ATTACK_S)) / MASTER_ATTACK_S, 0, 1),
                               np.clip(((b + MASTER_RELEASE_S) - seg) / MASTER_RELEASE_S, 0, 1))
            R[max(0, lo): min(len(grid), hi)] = np.maximum(R[max(0, lo): min(len(grid), hi)], r * shape)
        gain_db = m0 - R
        g_samples = lin_arr(np.interp(np.arange(len(pre_mix)) / SR, grid, gain_db))
        I = integrated_lufs(pre_mix * g_samples[:, None])
        if abs(MASTER_TARGET_LUFS - I) < 0.005:
            break
        m0 += MASTER_TARGET_LUFS - I
    final = pre_mix * g_samples[:, None]
    # dip regions for the notes
    dips = []
    on = R > 1e-4
    i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            dips.append({"start_s": round(float(grid[i]), 3), "end_s": round(float(grid[j - 1]), 3),
                         "max_db": round(float(R[i:j].max()), 2),
                         "at_s": round(float(grid[i + int(np.argmax(R[i:j]))]), 3)})
            i = j
        else:
            i += 1
    info = {"static_makeup_db": round(float(m0), 3), "dips": dips,
            "premaster_integrated_lufs": round(float(integrated_lufs(pre_mix)), 2),
            "premaster_true_peak_dbtp": round(float(tp_db.max()), 2),
            "predicted_integrated_lufs": round(float(integrated_lufs(final)), 2),
            "predicted_true_peak_dbtp": round(true_peak_dbtp(final), 2),
            "static_only_true_peak_dbtp": round(float(tp_db.max() + m0), 2),
            "static_gain_for_ceiling_only_db": round(float(MASTER_CEILING_DBTP - tp_db.max()), 2),
            "static_gain_for_ceiling_only_integrated_lufs": round(float(
                integrated_lufs(pre_mix * lin(MASTER_CEILING_DBTP - tp_db.max()))), 2)}
    def master(t):
        return lin_arr(np.interp(np.asarray(t, float), grid, gain_db))
    return master, info


def lin_arr(d):
    return np.power(10.0, np.asarray(d) / 20.0)


# --------------------------------------------------------------------------------------------
# Main build
# --------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-stems", action="store_true", help="skip the final stem exports and stem checks")
    ap.add_argument("--no-waveforms", action="store_true", help="skip the waveform PNGs")
    ap.add_argument("--refresh-cue-defaults", action="store_true",
                    help="rewrite timing/cue_defaults.json from STORYBOARD.md")
    ap.add_argument("--cues-dir", help="test only: read DIR/<composition>/cues.json before hyperframes/")
    args = ap.parse_args()
    global CUES_DIR_TEST
    CUES_DIR_TEST = args.cues_dir

    WORK.mkdir(exist_ok=True)
    CHECKS.mkdir(exist_ok=True)
    beat_map = load_json(BEAT_MAP)
    words = load_json(WORDS_JSON)["words"]
    music_plan = load_json(MUSIC_PLAN)
    sfx_plan = load_json(SFX_PLAN)
    analysis = load_json(SFX_ANALYSIS)
    ev = Events(beat_map, args.refresh_cue_defaults)
    edit_end = float(beat_map["edit_end_s"])
    vo_end = float(beat_map["vo_end_s"])

    # ---- SFX clips and their (pre-master) gains -------------------------------------------------
    clips, decisions = build_sfx_clips(ev, sfx_plan, analysis, edit_end)
    lib = load_library()
    clips_v05, v05_info = build_v05_clips(ev, lib, edit_end)          # v05: cues.json word_pops/key_words/...
    clips += clips_v05
    dropouts = dropout_windows(ev)
    v05_info["dropouts"] = [{"beat": d[2], "f": d[3], "frames": d[4], "window_s": [round(d[0], 3), round(d[1], 3)]}
                            for d in dropouts]
    v05_info["dropout_mutes"] = apply_dropouts(clips, dropouts)
    quantize_clips(clips)
    compute_sfx_gains(clips)
    if clips_v05:
        log("v05 library layers: %d (%s); ticks merged %d; dropouts %d (%d SFX mutes); skipped %s" % (
            len(clips_v05), v05_info["by_kind"], v05_info["merged_ticks"], len(dropouts),
            len(v05_info["dropout_mutes"]), v05_info["skipped"] or "none"))

    # ---- MP3 decoder offsets (FFmpeg-made WAVs need none) ---------------------------------------
    music_file = ROOT / music_plan["track"]
    anchor = music_anchor(words, music_plan)           # v02: drop downbeat on the new 'fun' (plan p.34: MU5 first)
    offset_s = anchor["offset_s"]                      # track (FFmpeg decode clock) = edit + offset_s (after the seam)
    bar_edit = bar_edit_plan(music_file, music_plan, anchor)
    anchor["bar_edit"] = bar_edit
    if bar_edit["applied"]:
        anchor["MU2_without_bar_edit"] = dict(anchor["MU2"])
        m2 = bar_edit["MU2_edit_s"]
        b0, b1 = anchor["MU2"]["broke_s"]
        anchor["MU2"].update({"edit_s": round(m2, 3), "delta_from_onset_s": round(m2 - b0, 3),
                              "within_half_second": abs(m2 - b0) <= 0.5, "inside_word": b0 <= m2 <= b1,
                              "track_s_at_edit_0": bar_edit["offset_before_seam_s"]})
    log("MU2 bar edit: %s; remove breakdown bar %d (track %.3f-%.3f s), seam on the bar line at edit %.3f s, MU2 "
        "%.3f -> %.3f s ('broke' %.3f-%.3f s); candidates %s" % (
            "APPLIED" if bar_edit["applied"] else "not applied", bar_edit["removed_bar"], *bar_edit["removed_track_s"],
            bar_edit["seam_bar_line_edit_s"], bar_edit["MU2_without_edit_s"], bar_edit["MU2_edit_s"],
            *bar_edit["broke_s"], [(c["bar"], c["score"]) for c in bar_edit["candidates"]]))
    mp3s = sorted({c.asset_file for c in clips if c.asset_file.suffix.lower() == ".mp3"} | {music_file}, key=str)
    lags = calibrate_decoder_offsets(mp3s)
    lag_mu = lags[str(music_file)]
    mu_s0 = ms(offset_s + lag_mu)                      # Tesseract source ms of the main bed at edit 0 (no edit)
    mu_s0_pre = ms(bar_edit["offset_before_seam_s"] + lag_mu)   # ... of the part before the bar edit's seam
    delta = mu_s0 / 1000 - lag_mu                      # FFmpeg-clock track time at edit 0 (offset_s +- 0.5 ms)

    # ---- MU6 low-passed excerpt, sample-aligned with the main bed --------------------------------
    mu6_a_ms = ms(ev.t("B15.start") - 1.5)
    mu6_b_ms = ms(ev.t("B15.label") + 1.0)
    n0 = int(round((delta + mu6_a_ms / 1000) * 44100))
    n1 = n0 + int(round((mu6_b_ms - mu6_a_ms) / 1000 * 44100))
    lp_file = MUSIC_DERIVED / ("BlackVertigo_MU6_lp%d_%d-%d.wav" % (MU6_LOWPASS_HZ, n0, n1))
    make_derivative(music_file, lp_file,
                    "lowpass=f=%d,atrim=start_sample=%d:end_sample=%d" % (MU6_LOWPASS_HZ, n0, n1),
                    note="MU6: 'Low-pass at about 800 Hz' (plan p.34). Excerpt = samples %d-%d at 44.1 kHz of "
                         "FFmpeg's decode (track %.5f-%.5f s = edit %.3f-%.3f s), filtered from the track "
                         "start so the filter is settled; float WAV (the track peaks above 0 dBFS)." % (
                             n0, n1, n0 / 44100, n1 / 44100, mu6_a_ms / 1000, mu6_b_ms / 1000))

    # ---- ducking phrases and music envelopes (pre-master) -----------------------------------------
    spans = phrase_spans(words, MERGE_GAP_S)
    tt, main_env, lp_env, marks, duck = music_envelopes(ev, beat_map, spans, dropouts)

    # ---- create the project and import every asset -------------------------------------------------
    for stale in [PROJECT] + list(WORK.glob("stem_*.tsrct")):
        if stale.exists():
            stale.unlink()
    tsrct("project", "create", "--project", PROJECT)
    assets = {}

    def import_asset(path: Path, asset_id: str):
        if asset_id not in assets:
            tsrct("project", "import-asset", "--project", PROJECT, "--file", path, "--asset-id", asset_id,
                  "--kind", "audio")
            assets[asset_id] = path
        return asset_id

    a_vo = import_asset(VO_FILE, "aud-vo-processed-" + re.sub(r"[^a-z0-9]+", "-", VO_TAG.lower()).strip("-"))
    a_mu = import_asset(music_file, "aud-mu-black-vertigo") if MUSIC else None
    a_lp = import_asset(lp_file, "aud-mu-black-vertigo-mu6-lp%d" % MU6_LOWPASS_HZ) if MUSIC else None
    for c in clips:
        c.asset_id = import_asset(c.asset_file, ("aud-v05-" if getattr(c, "v05", False) else "aud-") +
                                  re.sub(r"[^a-z0-9]+", "-", c.asset_file.stem.lower()).strip("-"))
    jpath = WORK / "audio.editable.json"
    tsrct("project", "checkout", "--project", PROJECT, "--output", jpath)
    doc_base = load_json(jpath)
    doc_base["dimensions"] = {"width": int(beat_map["canvas"][0]), "height": int(beat_map["canvas"][1])}
    doc_base["duration"] = edit_end
    doc_base["backgroundColor"] = [10 / 255, 10 / 255, 10 / 255, 1.0]

    # ---- layer specs ------------------------------------------------------------------------------
    specs = []
    vo_ms = int(probe(VO_FILE)["duration"] * 1000)
    vt = np.arange(vo_ms + 1) / 1000.0
    vo_fm = (load_json(VO_REPORT).get("final_metrics") or {}) if VO_REPORT.exists() else {}
    vo_rep = load_json(VO_REPORT) if VO_REPORT.exists() else {}
    vo_cuts = "; ".join("cut %s %d f ('%s')" % (c_["name"], c_["frames"], c_["removed"]) for c_ in vo_rep.get("v05_cuts", []))
    specs.append(Spec(group="A1", id=VO_LAYER_ID, name="VO processed %s (locked, beat map vo_file)" % VO_TAG, asset=a_vo,
                      E=0, D=vo_ms, S0=0, intr=vo_ms, modality="voiceover", source_name=VO_FILE.name, key="vo", tt=vt,
                      pre=np.full(len(vt), lin(VO_GAIN_DB)),
                      description="Locked voiceover %s (the beat map's vo_file; %s%% speed%s) at unity, edit 0 = file 0. "
                                  "Already through the plan's chain (HPF 80 Hz, de-esser, 3:1 compression; %s LUFS as a "
                                  "mono track, true peak %s dBFS; %s). Volume = the master gain only." % (
                                      VO_FILE.relative_to(ROOT), round(float(vo_rep.get("speed", 1.15)) * 100),
                                      ("; " + vo_cuts) if vo_cuts else "", vo_fm.get("integrated_lufs", "?"),
                                      vo_fm.get("true_peak_dbfs", "?"), VO_REPORT.relative_to(ROOT))))
    mu_D = ms(vo_end)
    mu_intr = int(probe(music_file)["duration"] * 1000)
    main_tt, main_pre, main_E, main_D, main_S0 = tt, main_env, 0, mu_D, mu_s0
    if bar_edit["applied"]:
        x0, x1 = bar_edit["xfade_s"]
        u = np.clip((tt - x0) / (x1 - x0), 0.0, 1.0)
        g_a, g_b = np.cos(0.5 * np.pi * u), np.sin(0.5 * np.pi * u)          # equal power
        sel_a = tt <= x1 + 1e-9
        sel_b = tt >= x0 - 1e-9
        main_tt, main_pre, main_D, main_S0 = tt[sel_a], (main_env * g_a)[sel_a], ms(x1), mu_s0_pre
        e_b = ms(x0)
        spec_b = (Spec(group="A2", id=MUSIC_B_LAYER_ID, name="MU2-MU8 Black Vertigo (main bed after the bar edit)",
                          asset=a_mu, E=e_b, D=mu_D - e_b, S0=e_b + mu_s0, intr=mu_intr, modality="music",
                          source_name=music_file.name, key="mu-main-b", tt=tt[sel_b], pre=(main_env * g_b)[sel_b],
                          description="Black Vertigo after the MU2 bar edit's seam: track = edit + %.2f s (the anchor: the "
                                      "drop, track %.2f s, on 'fun' %.3f s), from the equal-power crossfade %.3f-%.3f s "
                                      "(%d ms before the bar line at %.3f s; breakdown bar %d, track %.3f-%.3f s, is "
                                      "removed) to the hard stop at the end of 'now?' (MU8). Same envelope as the "
                                      "main bed (duck, MU4-MU8, x master)." % (
                                          offset_s, anchor["drop_track_s"], anchor["fun_onset_s"], x0, x1,
                                          BAR_EDIT_LEAD_S * 1000, bar_edit["seam_bar_line_edit_s"],
                                          bar_edit["removed_bar"], *bar_edit["removed_track_s"])))
    specs.append(Spec(group="A2", id=MUSIC_LAYER_ID, name="MU1-MU8 Black Vertigo (main bed)" if not bar_edit["applied"]
                      else "MU1-MU2 Black Vertigo (main bed up to the bar edit)", asset=a_mu, E=main_E,
                      D=main_D, S0=main_S0, intr=mu_intr, modality="music", source_name=music_file.name, key="mu-main",
                      tt=main_tt, pre=main_pre,
                      description=("Black Vertigo (Alexandre Brovelli) from track %.2f s at edit 0 (MU1, full energy, "
                                   "no fade-in), drop (track %.2f s) on the 'fun' onset %.3f s (MU5 marks from frame %.3f s), "
                                   "hard stop at the end of 'now?' %.3f s (MU8). Source start %d ms = %.2f s + %.1f ms MP3 "
                                   "decoder offset (Tesseract does not skip the LAME encoder delay). Keyframes: base %.1f "
                                   "dB, %.0f dB duck (50/300 ms) under every VO phrase, MU4 15f mute, MU5 +3 dB for 2 s, MU6 "
                                   "crossfade to the low-pass copy, MU7 rewind cut then -6 dB, MU8 stop, x master." % (
                                       offset_s, anchor["drop_track_s"], anchor["fun_onset_s"], marks["MU5"],
                                       marks["MU8"], mu_s0, offset_s, lag_mu * 1000, MUSIC_BASE_DB, DUCK_DB))
                      if not bar_edit["applied"] else
                      ("Black Vertigo (Alexandre Brovelli) from track %.2f s at edit 0 (MU1, full energy, no fade-in: one "
                       "bar earlier than the anchor, so the breakdown, track %.2f s, arrives at %.3f s inside 'broke' = "
                       "MU2) up to the MU2 bar edit's equal-power crossfade %.3f-%.3f s, where layer %d (the rest of the "
                       "track, breakdown bar %d removed) takes over. Source start %d ms = %.4f s + %.1f ms MP3 decoder "
                       "offset. Keyframes: base %.1f dB, %.0f dB duck (50/300 ms) under every VO phrase, the crossfade, "
                       "x master." % (bar_edit["offset_before_seam_s"], bar_edit["MU2_edit_s"] + bar_edit[
                           "offset_before_seam_s"], bar_edit["MU2_edit_s"], bar_edit["xfade_s"][0], bar_edit["xfade_s"][1],
                                      MUSIC_B_LAYER_ID, bar_edit["removed_bar"], mu_s0_pre,
                                      bar_edit["offset_before_seam_s"], lag_mu * 1000, MUSIC_BASE_DB, DUCK_DB))))
    if bar_edit["applied"]:
        specs.append(spec_b)
    lp_E, lp_end = ms(marks["MU6_start"] - 0.1), ms(marks["MU6_end"] + 0.1)
    sel = (tt >= lp_E / 1000 - 1e-9) & (tt <= lp_end / 1000 + 1e-9)
    lp_intr = int(probe(lp_file)["duration"] * 1000)
    lp_s0 = lp_E - mu6_a_ms                            # derivative clock: 0 = edit mu6_a
    assert 0 <= lp_s0 and lp_s0 + (lp_end - lp_E) <= lp_intr
    specs.append(Spec(group="A2", id=MUSIC_LP_LAYER_ID, name="MU6 Black Vertigo low-pass %d Hz (-6 dB)" % MU6_LOWPASS_HZ,
                      asset=a_lp, E=lp_E, D=lp_end - lp_E, S0=lp_s0, intr=lp_intr, modality="music",
                      source_name=lp_file.name, key="mu-lp", tt=tt[sel], pre=lp_env[sel],
                      description="MU6: the same excerpt pre-filtered with FFmpeg lowpass=f=%d (%s, recipe "
                                  "beside it), sample-aligned with the main bed. From 'Don't believe me?' (%.3f s) "
                                  "until B15's `label` moment, 'Race' (%.3f s; the v01 RACE AND CHASE label, removed in "
                                  "v02 by note 7) the main bed crossfades (%d ms) to this copy at -6 dB, then opens "
                                  "again." % (MU6_LOWPASS_HZ, lp_file.parent.relative_to(ROOT), marks["MU6_start"],
                                              marks["MU6_end"], EDGE_S * 1000)))
    if not MUSIC:                                      # v04 note 1: the A2 group stays empty
        specs = [sp for sp in specs if sp.group != "A2"]
    sub_index = {}
    for c in clips:
        c.lag_s = lags.get(str(c.asset_file), 0.0)
        if getattr(c, "v05", False):                     # v05 library layer: id set in edit order, 48 kHz WAV
            c.S0 = c.S0t
            c.name = "%s %s f%d %s (%s)" % (Path(c.file).stem, c.event.split(".")[0], c.beat_f,
                                            c.kind.replace("_", " "), c.cls)
            continue
        k = sub_index.get(c.cue, 0)
        sub_index[c.cue] = k + 1
        c.layer_id = sfx_layer_id(c.cue, k)
        c.S0 = c.S0t + ms(c.lag_s)                       # Tesseract source ms (decoder offset included)
        assert c.S0 + c.D <= c.intr_ms + ms(c.lag_s)
        label = file_stem_label(c.file)
        tag = c.cue + (c.sub if c.sub and not c.sub.startswith("k") else "")
        name = "%s %s" % (tag, label)
        if c.sub.startswith("k"):
            name += " (key %s/%d)" % (c.sub[1:], sum(1 for x in clips if x.cue == c.cue))
        if getattr(c, "derived", None):
            name += " (%.1f-%.1f s, HPF %s Hz)" % (c.src_start, c.src_start + c.dur, re.search(r"f=(\d+)", c.derived).group(1))
        c.name = name
    base_specs = list(specs)

    def sfx_specs():
        out = []
        for c in clips:
            ctt, cpre = clip_pre_curve(c, c.E, c.D)
            if getattr(c, "v05", False):
                desc = ("v05 %s | %s | %s beat f%d = edit %.3f s (f%d) | %s | %s dBFS sample peak (library %s%s)%s | %s" % (
                    c.sound, c.kind, c.event.split(".")[0], c.beat_f, c.event_t, round(c.event_t * FPS), c.rule,
                    c.target_dbfs, Path(c.file).name, ", cue gain_db" if any("gain_db" in n for n in c.notes) else "",
                    (" | " + "; ".join(c.notes)) if c.notes else "", c.plan))
            else:
                desc = ("%s | event %s = edit %.3f s (f%d) | %s | pre-master gain %.2f dB -> sample peak %.1f dBFS%s | "
                        "plan: %s%s" % (c.cue, c.event, c.event_t, round(c.event_t * FPS), c.rule, c.gain_db, c.target_dbfs,
                                        " (combined)" if c.combined else "", c.plan,
                                        (" | " + "; ".join(n for n in c.notes if "dropout" in n)) if getattr(c, "mutes", None) else ""))
            out.append(Spec(group=c.group, id=c.layer_id, name=c.name, asset=c.asset_id, E=c.E, D=c.D, S0=c.S0,
                            intr=c.intr_ms + ms(c.lag_s), modality="soundEffect", source_name=c.asset_file.name,
                            key="%s%s" % (c.cue.lower(), c.sub), tt=ctt, pre=cpre, clip=c, description=desc))
        return out

    # ---- pass 1: pre-master document -> pre-master stems --------------------------------------------
    unity = lambda t: np.ones(len(np.atleast_1d(t)))
    specs = base_specs + sfx_specs()
    groups, entries = to_layers(specs, unity)
    commit_document(doc_base, groups, entries, edit_end, PROJECT, jpath)
    pre = export_stems(load_json(jpath), "premaster_")
    # SFX gain calibration on Tesseract's own render: each cue's isolated sample peak -> plan level
    calib = {}
    for it in range(2):
        model, own = sfx_model(clips, len(pre["sfx_a3"]))
        iso = isolated_peaks(clips, {"A3": pre["sfx_a3"], "A4": pre["sfx_a4"], "A5": pre["sfx_a5"]}, model, own)
        fix = {k: d["clips"][0].target_dbfs - d["peak_dbfs"] for k, d in iso.items()
               if not d["clips"][0].gain_link and not getattr(d["clips"][0], "v05", False)
               and not any(getattr(c_, "mutes", None) for c_ in d["clips"])}
        for k, d in iso.items():
            if getattr(d["clips"][0], "v05", False):
                continue
            calib.setdefault(k, {"computed_gain_db": round(d["clips"][0].gain_db - d["clips"][0].rel_gain_db, 3),
                                 "first_render_peak_dbfs": round(d["peak_dbfs"], 3)})
        todo = {k: v for k, v in fix.items() if abs(v) > 0.02}
        if not todo:
            break
        for k, v in todo.items():
            for c in iso[k]["clips"]:
                c.gain_db += v
            calib[k]["correction_db"] = round(calib[k].get("correction_db", 0.0) + v, 3)
        link_gains(clips)                                # S10 follows S08's corrected gain
        log("SFX gain calibration pass %d: %s" % (it + 1, {k: round(v, 2) for k, v in todo.items()}))
        specs = base_specs + sfx_specs()
        groups, entries = to_layers(specs, unity)
        commit_document(doc_base, groups, entries, edit_end, PROJECT, jpath)
        pre.update(export_stems(load_json(jpath), "premaster_", only=("sfx_a3", "sfx_a4")))
    pre_mix = pre["voice"] + pre["music"] + pre["sfx_a3"] + pre["sfx_a4"] + pre["sfx_a5"]
    master, minfo = solve_master(pre_mix)
    minfo["sfx_gain_calibration"] = calib
    for f in CHECKS.glob("premaster_stem_*.wav"):
        f.unlink()
    log("master: static %+.2f dB; pre-master I %.2f LUFS / TP %.2f dBTP; static-only TP would be %.2f dBTP; "
        "dips %s" % (minfo["static_makeup_db"], minfo["premaster_integrated_lufs"], minfo["premaster_true_peak_dbtp"],
                     minfo["static_only_true_peak_dbtp"], minfo["dips"]))

    # ---- pass 2: final document ------------------------------------------------------------------
    groups, entries = to_layers(specs, master)
    doc, warn = commit_document(doc_base, groups, entries, edit_end, PROJECT, jpath)
    chk = json.loads(run([TSRCT, "project", "check", "--project", PROJECT]).stdout)
    n_layers = sum(len(v) for v in groups.values())
    log("committed %s: %d groups, %d audio layers, %d volume animators; warnings=%s; check valid=%s" % (
        PROJECT.relative_to(ROOT), len(GID), n_layers, len(entries), warn, chk.get("valid")))
    if not chk.get("valid"):
        raise SystemExit("project check failed: %s" % chk)
    m0 = minfo["static_makeup_db"]
    for c in clips:
        c.master_db_at_peak = db(float(master(np.array([c.peak_time]))[0]))

    # ---- cue table ----------------------------------------------------------------------------------
    log("\nCue table (edit clock, 30 fps). gain = pre-master; final = gain + master (static %+.2f dB, dips listed)" % m0)
    log("%-4s %-40s %-3s %-18s %5s %8s %7s %8s %6s %6s %6s %6s %7s %7s %6s" % (
        "cue", "layer", "grp", "event", "evf", "event s", "start f", "start s", "dur s", "fadeI", "fadeO", "srcIn",
        "gain dB", "final", "peak"))
    for c in sorted((c for c in clips if not getattr(c, "v05", False)), key=lambda c: (c.edit_start, c.layer_id)):
        log("%-4s %-40s %-3s %-18s %5d %8.3f %7.1f %8.3f %6.3f %6.3f %6.3f %6.3f %+7.2f %+7.2f %6.1f" % (
            c.cue, c.name[:40], c.group, c.event, round(c.event_t * FPS), c.event_t, c.edit_start * FPS, c.edit_start,
            c.dur, c.fade_in, c.fade_out, c.src_start, c.gain_db, c.gain_db + c.master_db_at_peak, c.target_dbfs))
    log("\nMusic marks: " + ", ".join("%s %.3f s (f%.1f)" % (k, v, v * FPS) for k, v in marks.items()
                                     if isinstance(v, float)) + ("; dropouts %s" % marks["dropouts"] if marks.get("dropouts") else ""))

    # ---- export and measure -------------------------------------------------------------------------
    mix = CHECKS / "mix.wav"
    tsrct("export-audio", "--project", PROJECT, "--output", mix)
    log("exported", mix.relative_to(ROOT))
    report = {
        "project": str(PROJECT.relative_to(ROOT)), "tsrct": tsrct_version(),
        "constants": {k: globals()[k] for k in (
            "VO_GAIN_DB", "MUSIC_BASE_DB", "DUCK_DB", "ATTACK_S", "RELEASE_S", "MERGE_GAP_S", "MU5_LIFT_DB",
            "MU5_HOLD_S", "MU5_RETURN_S", "MU6_DB", "MU6_LOWPASS_HZ", "MU7_DB", "MU7_RETURN_S", "MU4_FRAMES", "EDGE_S",
            "MASTER_TARGET_LUFS", "MASTER_CEILING_DBTP", "MASTER_ATTACK_S", "MASTER_RELEASE_S", "MUSIC",
            "V05_GAIN_CAP_DBFS", "V05_KEY_WORD_PAIR", "V05_WORD_POP", "V05_HOOK_CUT", "V05_DROPOUT_MAX_F",
            "DROPOUT_CLASSES", "LEGACY_CLASS")},
        "vo": {"file": str(VO_FILE.relative_to(ROOT)), "words": str(WORDS_JSON.relative_to(ROOT)),
               "report": str(VO_REPORT.relative_to(ROOT)), "from": "timing/beat_map.json vo_file"},
        "v05": dict(v05_info, library=str(SFX_LIB.relative_to(ROOT)) if lib else None,
                    cues_schema=ev.schema, legacy_remapped_v04_to_v05=ev.remapped, cut_by_v05_trims=ev.dropped,
                    cue_notes=ev.notes, legacy_s_cues_skipped=decisions.get("skipped", []),
                    levels_dbfs={k: v["default_peak_dbfs"] for k, v in (lib or {}).items()},
                    cues_dir_test=CUES_DIR_TEST),
        "master": minfo, "event_sources": ev.source, "music_marks_s": marks,
        "music_anchor": anchor, "cue_scaling_v01_to_v02": ev.scaled,
        "beat_start_s": {b: round(ev.beat_start_frame(b) / FPS, 4) for b in ev.beats},
        "music_source": {"file": music_plan["track"], "offset_s": offset_s, "tesseract_source_start_ms": mu_s0,
                         "bar_edit": bar_edit, "tesseract_source_start_ms_before_seam": mu_s0_pre if bar_edit["applied"] else None,
                         "decoder_offset_ms": round(lag_mu * 1000, 3), "mu6_derivative": str(lp_file.relative_to(ROOT)),
                         "mu6_layer": {"start_ms": lp_E, "end_ms": lp_end, "source_start_ms": lp_s0}},
        "decoder_offsets_ms": {Path(k).name: round(v * 1000, 3) for k, v in lags.items()},
        "phrases": [{"start": a, "end": b, "text": t} for a, b, t in spans],
        "s13_decision": decisions.get("S13"),
        "assets": {k: str(v.relative_to(ROOT)) for k, v in assets.items()},
        "layers": [{"id": sp.id, "group": sp.group, "name": sp.name, "keyframes": len(sp.final_curve[0])
                    if len(sp.final_curve[0]) > 2 else 0} for sp in specs],
    }
    report["cues"] = [{
        "cue": c.cue, "sub": c.sub, "layer_id": c.layer_id, "layer": c.name, "group": c.group, "file": c.file,
        "asset": c.asset_id, "asset_file": str(c.asset_file.relative_to(ROOT)), "event": c.event,
        "event_beat_frame": c.beat_f if getattr(c, "v05", False) else ev.beat_frame(c.event),
        "event_edit_frame": round(c.event_t * FPS), "v05": getattr(c, "v05", False) and {
            "kind": c.kind, "sound": c.sound, "class": c.cls} or None,
        "dropout_mutes_s": [[round(a, 3), round(b, 3)] for a, b in getattr(c, "mutes", [])] or None,
        "event_s": round(c.event_t, 4), "rule": c.rule, "edit_start_s": round(c.edit_start, 4),
        "edit_start_frame": round(c.edit_start * FPS, 2), "edit_end_s": round(c.end, 4),
        "source_in_s": round(c.src_start, 4), "duration_s": round(c.dur, 4), "fade_in_s": c.fade_in,
        "fade_out_s": round(c.fade_out, 4), "rel_gain_db": c.rel_gain_db, "gain_db_pre_master": round(c.gain_db, 3),
        "master_db_at_peak": round(c.master_db_at_peak, 3), "final_gain_db": round(c.gain_db + c.master_db_at_peak, 3),
        "target_peak_dbfs_pre_master": c.target_dbfs, "combined": c.combined,
        "computed_peak_time_s": round(c.peak_time, 4), "file_peak_before_gain_dbfs": round(c.raw_peak_dbfs, 2),
        "notes": c.notes, "placement_ms": {"start": c.E, "duration": c.D, "source_start": c.S0}}
        for c in sorted(clips, key=lambda c: (c.edit_start, c.layer_id))]
    measure(report, mix, clips, spans, marks, music_file, offset_s, master, args, edit_end, doc)
    (CHECKS / "audio_report.json").write_text(json.dumps(report, indent=1, default=float) + "\n")
    write_notes(report, clips, spans, marks, decisions, ev, beat_map, music_plan, lp_file, lag_mu, mu_s0)
    log("\nwrote", (CHECKS / "audio_report.json").relative_to(ROOT), "and", (WORK / "AUDIO_NOTES.md").relative_to(ROOT))


# --------------------------------------------------------------------------------------------
# Measurement of the final mix and stems
# --------------------------------------------------------------------------------------------
def gain_db_between(stem, ref, a, b, sos=None):
    i, j = int(a * SR), int(b * SR)
    x, y = stem[i:j, 0], ref[i:j, 0]
    if sos is not None:
        from scipy.signal import sosfilt
        x, y = sosfilt(sos, x), sosfilt(sos, y)
    return 10 * np.log10(np.mean(x ** 2) + 1e-20) - 10 * np.log10(np.mean(y ** 2) + 1e-20)


def measure(report, mix, clips, spans, marks, music_file, offset_s, master, args, edit_end, doc):
    from scipy.signal import butter
    m = {"ffmpeg_ebur128": ffmpeg_ebur128(mix)}
    x = read_wav(mix)
    m["own"] = {"integrated_lufs": integrated_lufs(x), "true_peak_dbtp": true_peak_dbtp(x),
                "sample_peak_dbfs": db(float(np.max(np.abs(x))))}
    helper = CHECKS / "loudness.json"
    r = subprocess.run([sys.executable, str(SOUND_HELPER), "measure", str(mix), "--report", str(helper), "--overwrite"],
                       capture_output=True, text=True)
    m["skill_measure"] = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip().startswith("{") else \
        {"error": (r.stdout + r.stderr)[-500:]}
    mono = np.repeat(x.mean(axis=1, keepdims=True), 2, axis=1)
    m["mono_folddown"] = {"integrated_lufs": integrated_lufs(mono), "delta_vs_stereo_lu": integrated_lufs(mono) -
                          m["own"]["integrated_lufs"]}
    mob = CHECKS / "mobile_preview.wav"
    rr = subprocess.run([sys.executable, str(SOUND_HELPER), "mobile-preview", str(mix), "--output", str(mob),
                         "--overwrite"], capture_output=True, text=True)
    m["mobile_preview"] = str(mob.relative_to(ROOT)) if rr.returncode == 0 else (rr.stdout + rr.stderr)[-300:]
    eb = m["ffmpeg_ebur128"]
    m["targets_met"] = {"integrated_-14_pm1": abs(eb["integrated_lufs"] + 14.0) <= 1.0,
                        "true_peak_le_-1": eb["true_peak_dbtp"] <= -1.0}
    log("\nMIX: ffmpeg I %.2f LUFS, LRA %.1f LU, TP %.2f dBTP | own I %.2f, TP %.2f, sample peak %.2f | targets %s" % (
        eb["integrated_lufs"], eb["lra_lu"], eb["true_peak_dbtp"], m["own"]["integrated_lufs"], m["own"]["true_peak_dbtp"],
        m["own"]["sample_peak_dbfs"], m["targets_met"]))
    log("skill measure:", json.dumps(m["skill_measure"]))
    report["mix"] = m
    if not args.no_waveforms:
        waves = []
        s08 = next((c for c in clips if c.cue == "S08"), None)
        s18 = next((c for c in clips if c.cue == "S18"), None)
        s19 = next((c for c in clips if c.cue == "S19"), None)
        b9 = next((s_[0] for s_ in spans if s_[0] >= marks["MU4_end"] - 0.05), marks["MU4_end"])
        report["waveform_markers_s"] = {"S08": s08 and s08.edit_start, "B9_voice": b9, "S18": s18 and s18.edit_start,
                                        "S19": s19 and s19.edit_start}
        an_ = report["music_anchor"]
        b8_0 = s08.edit_start if s08 else marks["MU4_start"] - 0.3
        end_0 = (s18 or s19).edit_start if (s18 or s19) else max(0.0, marks["MU8"] - 2.0)
        views = [("mu5-drop-s09-fun", marks["MU5"] - 1.3, marks["MU5"] + 2.7, [marks["MU5"], marks["MU5"] + MU5_HOLD_S]),
                 ("b8-break-mu4-mute", b8_0 - 0.55, b9 + 0.6, [b8_0, marks["MU4_start"], marks["MU4_end"], b9]),
                 ("b17-ending", end_0 - 0.8, edit_end, [end_0, marks["MU8"]] + ([s19.edit_start] if s19 else [])),
                 ("mu2-breakdown-on-broke", an_["MU2"]["edit_s"] - 1.5, an_["MU2"]["edit_s"] + 1.5,
                  [an_["MU2"]["broke_s"][0], an_["MU2"]["edit_s"]])]
        if not MUSIC:
            views = [v_ for v_ in views if not v_[0].startswith("mu2")]
        v05c = [c for c in clips if getattr(c, "v05", False)]
        if v05c:                                    # v05: the densest 4 s of auto layers, and every dropout
            ts = np.array(sorted(c.event_t for c in v05c))
            best = max(range(len(ts)), key=lambda i: int(np.sum((ts >= ts[i]) & (ts < ts[i] + 4.0))))
            a_ = max(0.0, float(ts[best]) - 0.3)
            views.append(("v05-densest-4s", a_, min(edit_end, a_ + 4.3),
                          [round(float(t_), 3) for t_ in ts[(ts >= a_) & (ts < a_ + 4.3)]][:24]))
            for d in report.get("v05", {}).get("dropouts", []):
                w0, w1 = d["window_s"]
                views.append(("v05-dropout-%s-f%d" % (d["beat"].lower(), d["f"]), max(0.0, w0 - 1.2),
                              min(edit_end, w1 + 0.8), [w0, w1]))
        if MUSIC and an_["bar_edit"]["applied"]:
            x0_, x1_ = an_["bar_edit"]["xfade_s"]
            views.append(("mu2-bar-edit-seam", x0_ - 1.0, x1_ + 1.0, [x0_, x1_, an_["bar_edit"]["seam_bar_line_edit_s"]]))
        for tag, a_, b_, mk in views:
            outp = CHECKS / ("wave_%s.png" % tag)
            rr = subprocess.run([sys.executable, str(SOUND_HELPER), "waveform", str(mix), "--mode", "music",
                                 "--clock", "edit", "--start-ms", str(ms(a_)), "--duration-ms", str(ms(b_ - a_)),
                                 "--markers-ms", ",".join(str(ms(t)) for t in mk), "--output", str(outp),
                                 "--overwrite"], capture_output=True, text=True)
            waves.append({"png": str(outp.relative_to(ROOT)), "window_s": [round(a_, 3), round(b_, 3)],
                          "markers_s": [round(t, 3) for t in mk], "ok": rr.returncode == 0,
                          "msg": (rr.stderr or "")[-300:]})
        report["waveforms"] = waves
    if args.no_stems:
        return
    st_ = export_stems(doc, "")
    v, mu, s3, s4, s5 = st_["voice"], st_["music"], st_["sfx_a3"], st_["sfx_a4"], st_["sfx_a5"]
    n = min(len(x), len(v))
    st = {"voice": {"integrated_lufs": integrated_lufs(v), "true_peak_dbtp": true_peak_dbtp(v),
                    "sample_peak_dbfs": db(float(np.max(np.abs(v))))},
          "stems_sum_vs_mix_max_abs_diff": float(np.max(np.abs(x[:n] - (v + mu + s3 + s4 + s5)[:n])))}
    if MUSIC:
        # ---- music bed loudness: under the voice vs without voice ------------------------------------
        tc3, l3 = windowed_lufs(mu, 3.0)
        _, v3 = windowed_lufs(v, 3.0)
        tc04, l04 = windowed_lufs(mu, 0.4)
        grid = np.arange(0, len(mu) / SR, 0.01)
        act = voice_activity(grid, spans)
        cs = np.concatenate([[0], np.cumsum(act)])
        cov3 = np.array([(cs[min(len(grid), int((t + 1.5) * 100))] - cs[max(0, int((t - 1.5) * 100))]) / 300.0 for t in tc3])
        ok = (tc3 - 1.5 >= 0.0) & (tc3 + 1.5 <= marks["MU8"])
        for a_, b_ in ((marks["MU4_start"], marks["MU4_end"]), (marks["MU6_start"], marks["MU6_end"]),
                       (marks["MU7_start"], marks["MU7_return"] + MU7_RETURN_S)):
            ok &= ~((tc3 + 1.5 > a_) & (tc3 - 1.5 < b_))       # normal bed only; MU4/MU6/MU7 checked apart
        under = ok & (cov3 >= 0.85)
        an = report["music_anchor"]
        m2, m3, m5, m8 = an["MU2"]["edit_s"], an["MU3"]["edit_s"], marks["MU5"], marks["MU8"]
        sections = {"MU1 full beat 0-%.1f s" % m2: (0.0, m2), "breakdown %.1f-%.1f s" % (m2, m3): (m2, m3),
                    "near-silence + build %.1f-%.1f s" % (m3, m5): (m3, m5),
                    "post-drop %.1f-%.1f s" % (m5, m8): (m5, m8)}
        bed = {"under_voice_short_term_median_lufs": float(np.median(l3[under])),
               "voice_short_term_median_lufs": float(np.median(v3[under])), "by_section": {}}
        for k, (a_, b_) in sections.items():
            s_ = under & (tc3 - 1.5 >= a_) & (tc3 + 1.5 <= b_)
            if np.any(s_):
                bed["by_section"][k] = {"bed_lufs": float(np.median(l3[s_])), "voice_lufs": float(np.median(v3[s_])),
                                       "windows": int(np.sum(s_))}
        gaps = [(spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1)]
        hold_a, hold_b = max(gaps, key=lambda g_: g_[1] - g_[0])     # the B13 title hold (longest VO gap)
        selh = (tc04 - 0.2 >= hold_a + RELEASE_S) & (tc04 + 0.2 <= hold_b - ATTACK_S)
        bed["title_hold_window_s"] = [hold_a, hold_b]
        bed["title_hold_momentary_median_lufs"] = float(np.median(l04[selh]))
        bed["title_hold_momentary_max_lufs"] = float(np.max(l04[selh]))
        trk = decode(music_file)
        be = report["music_anchor"].get("bar_edit") or {}
        off_pre = be["offset_before_seam_s"] if be.get("applied") else offset_s
        seam = be["seam_bar_line_edit_s"] if be.get("applied") else 0.0
        mref = np.zeros_like(mu)
        seg = trk[int(round(offset_s * SR)):][: len(mu)]
        mref[: len(seg)] = seg
        if be.get("applied"):                     # before the seam the track runs one bar earlier
            i_s = int(round(seam * SR))
            seg = trk[int(round(off_pre * SR)):][: i_s]
            mref[: len(seg)] = seg

        def undecked_st(a_, b_):
            o_ = off_pre if b_ <= seam else offset_s
            y = trk[int((o_ + a_) * SR): int((o_ + b_) * SR)]
            y = y * lin(MUSIC_BASE_DB) * master(a_ + np.arange(len(y)) / SR)[:, None]
            tcr, lr = windowed_lufs(y, 3.0)
            return tcr + a_, lr
        hc = (hold_a + hold_b) / 2
        tcr, lr = undecked_st(max(0.0, hc - 3.5), min(m8, hc + 3.5))
        bed["undecked_bed_short_term_title_hold_lufs"] = float(lr[np.argmin(np.abs(tcr - hc))])
        _, lr2 = undecked_st(m5 + MU5_HOLD_S + MU5_RETURN_S, m8 - 0.05)
        bed["undecked_bed_short_term_post_drop_median_lufs"] = float(np.median(lr2))
        _, lr3 = undecked_st(0.0, max(3.1, m2 - 0.1))
        bed["undecked_bed_short_term_mu1_median_lufs"] = float(np.median(lr3))
        st["music_bed"] = bed
        # ---- music envelope checks (stem vs the FFmpeg-clock track; includes the master) ---------------
        def mdb(t):
            return db(float(master(np.array([t]))[0]))
        p_ = max(spans, key=lambda s: s[1] - s[0])
        mid = (p_[0] + p_[1]) / 2

        def ducked(a_, b_, length=0.5, guard=0.05):
            """A window inside one VO phrase (bed at full duck depth) and inside [a_, b_]: the longest such stretch,
            centred, `length` s (shortened to fit, not under 0.2 s). Windows are derived, so they follow the timing."""
            best = None
            for s0_, e0_, _ in spans:
                lo, hi = max(s0_ + guard, a_), min(e0_ - guard, b_)
                if hi - lo >= 0.2 and (best is None or hi - lo > best[1] - best[0]):
                    best = (lo, hi)
            if best is None:
                raise SystemExit("no voice phrase of >= 0.2 s inside %.3f-%.3f s for a music check" % (a_, b_))
            c_, L_ = (best[0] + best[1]) / 2, min(length, best[1] - best[0])
            return c_ - L_ / 2, c_ + L_ / 2

        lp4, hp2 = butter(4, 400, "lowpass", fs=SR, output="sos"), butter(4, 2000, "highpass", fs=SR, output="sos")
        th = (hold_a + RELEASE_S + 0.05, hold_b - ATTACK_S - 0.05)
        th = ((th[0] + th[1]) / 2 - min(0.5, (th[1] - th[0]) / 2), (th[0] + th[1]) / 2 + min(0.5, (th[1] - th[0]) / 2))
        b12 = report["beat_start_s"].get("B12") or m8
        w5 = ducked(m5 + MU5_HOLD_S + MU5_RETURN_S + 0.1, b12)
        w6 = ducked(marks["MU6_start"] + 0.1, marks["MU6_end"] - 0.1)
        w6b = ducked(marks["MU6_end"] + 0.1, marks["MU7_start"] - 0.05, length=0.4)
        w7 = ducked(marks["MU7_end"] + 0.1, marks["MU7_return"] - 0.05)
        w17 = ducked(marks["MU7_return"] + MU7_RETURN_S + 0.1, m8 - 0.1)
        cen = lambda w_: (w_[0] + w_[1]) / 2
        chk = {
            "title_hold_gain_db": [gain_db_between(mu, mref, *th), MUSIC_BASE_DB + mdb(cen(th))],
            "mid_longest_phrase_gain_db": [gain_db_between(mu, mref, mid - 0.5, mid + 0.5), MUSIC_BASE_DB + DUCK_DB + mdb(mid)],
            "MU5_on_fun_gain_db": [gain_db_between(mu, mref, marks["MU5"] + 0.05, marks["MU5"] + 0.35),
                                   MUSIC_BASE_DB + DUCK_DB + MU5_LIFT_DB + mdb(marks["MU5"] + 0.2)],
            "after_MU5_ducked_gain_db": [gain_db_between(mu, mref, *w5), MUSIC_BASE_DB + DUCK_DB + mdb(cen(w5))],
            "MU6_lowband_gain_db": [gain_db_between(mu, mref, *w6, sos=lp4), MUSIC_BASE_DB + DUCK_DB + MU6_DB + mdb(cen(w6))],
            "MU6_highband_gain_db": [gain_db_between(mu, mref, *w6, sos=hp2), "low-passed: far below the low band"],
            "after_label_highband_gain_db": [gain_db_between(mu, mref, *w6b, sos=hp2), "open again: = full-band ducked gain"],
            "MU7_glow_line_gain_db": [gain_db_between(mu, mref, *w7), MUSIC_BASE_DB + DUCK_DB + MU7_DB + mdb(cen(w7))],
            "B17_back_to_normal_gain_db": [gain_db_between(mu, mref, *w17), MUSIC_BASE_DB + DUCK_DB + mdb(cen(w17))],
            "MU4_mute_peak_dbfs": region_peak(mu, marks["MU4_start"] + 0.01, marks["MU4_end"] - 0.01),
            "MU7_rewind_cut_peak_dbfs": region_peak(mu, marks["MU7_start"] + 0.01, marks["MU7_end"] - 0.01),
            "after_MU8_peak_dbfs": region_peak(mu, marks["MU8"] + 0.001, edit_end),
            "dropouts_max_peak_dbfs": max([region_peak(mu, a_ + 0.011, b_ - 0.001) for a_, b_ in marks.get("dropouts", [])
                                           if b_ - a_ > 0.03] or [-200.0]),
            "drop_offset_vs_track_clock_ms": xcorr_lag(mu[int((marks["MU5"] - 0.5) * SR): int((marks["MU5"] + 1.5) * SR), 0],
                                                       mref[int((marks["MU5"] - 0.5) * SR): int((marks["MU5"] + 1.5) * SR), 0],
                                                       int(0.05 * SR)) / SR * 1000,
        }
        if be.get("applied"):
            x0, x1 = be["xfade_s"]
            lag = lambda a_, b_: xcorr_lag(mu[int(a_ * SR): int(b_ * SR), 0], mref[int(a_ * SR): int(b_ * SR), 0],
                                           int(0.05 * SR)) / SR * 1000
            rms = lambda a_, b_: 10 * np.log10(np.mean(mu[int(a_ * SR): int(b_ * SR)] ** 2) + 1e-20)
            chk["bar_edit_track_lag_before_seam_ms"] = lag(max(0.0, x0 - 2.2), x0 - 0.05)
            chk["bar_edit_track_lag_after_seam_ms"] = lag(x1 + 0.05, x1 + 2.2)
            chk["bar_edit_seam_level_vs_neighbours_db"] = rms(x0 - 0.02, x1 + 0.02) - 0.5 * (
                rms(x0 - 0.42, x0 - 0.02) + rms(x1 + 0.02, x1 + 0.42))
            # the same windows at that bar line of the unedited track (the bed's own pre-downbeat dip, for reference)
            tb = be["removed_track_s"][1] - (be["seam_bar_line_edit_s"] - x0)
            tr_ = lambda a_, b_: 10 * np.log10(np.mean(trk[int(a_ * SR): int(b_ * SR)] ** 2) + 1e-20)
            w_ = x1 - x0
            chk["bar_edit_same_window_unedited_bar_line_db"] = tr_(tb - 0.02, tb + w_ + 0.02) - 0.5 * (
                tr_(tb - 0.42, tb - 0.02) + tr_(tb + w_ + 0.02, tb + w_ + 0.42))
        st["music_envelope_checks"] = chk
        st["music_check_windows_s"] = {k: [round(v[0], 3), round(v[1], 3)] for k, v in (
            ("title_hold", th), ("after_MU5", w5), ("MU6", w6), ("after_label", w6b), ("MU7_glow", w7), ("B17", w17))}
    else:                                              # v04: no bed; the voice reference numbers only
        tc3, v3 = windowed_lufs(v, 3.0)
        grid = np.arange(0, len(v) / SR, 0.01)
        cs = np.concatenate([[0], np.cumsum(voice_activity(grid, spans))])
        cov3 = np.array([(cs[min(len(grid), int((t + 1.5) * 100))] - cs[max(0, int((t - 1.5) * 100))]) / 300.0 for t in tc3])
        bed = {"voice_short_term_median_lufs": float(np.median(v3[cov3 >= 0.85]))}
        chk = {}
        st["music_bed"] = bed                          # the voice reference only (no bed)
        st["music_envelope_checks"] = {}
        st["music_stem_peak_dbfs"] = db(float(np.max(np.abs(mu))))
    # ---- SFX: each cue's rendered peak, isolated from overlapping cues of its group via the model ---
    stems_g = {"A3": s3, "A4": s4, "A5": s5}
    model, own = sfx_model(clips, len(s3), master)
    # sanity: residual energy of stem - model relative to the stem (placement is sample-exact; the rest
    # is the resampler of 44.1/96 kHz sources)
    st["sfx_model_vs_stem_residual_db"] = {
        g: round(10 * np.log10((np.sum((stems_g[g] - model[g]) ** 2) + 1e-20) / (np.sum(stems_g[g] ** 2) + 1e-20)), 1)
        for g in model}
    resid = st["sfx_model_vs_stem_residual_db"]
    vglob = db(float(np.max(np.abs(v))))
    per_cue = []
    for key, d in sorted(isolated_peaks(clips, stems_g, model, own).items()):
        cs_ = d["clips"]
        pk, tpk = d["peak_dbfs"], d["peak_s"]
        target = cs_[0].target_dbfs
        final_target = target + db(float(master(np.array([tpk]))[0]))
        exact = getattr(cs_[0], "v05", False) or any(getattr(c_, "mutes", None) for c_ in cs_)
        if exact:       # v05 layers (head/tail cuts, dropout mutes): the model's own peak is the expectation
            final_target = db(max(float(np.max(np.abs(own[id(c_)][1]))) for c_ in cs_))
        a_, b_ = d["window_s"]
        vloc = region_peak(v, a_, b_)
        per_cue.append({"cue": key, "group": d["group"], "window_s": [round(a_, 3), round(b_, 3)],
                        "layer": cs_[0].name if getattr(cs_[0], "v05", False) else None,
                        "expected_from": "model" if exact else "plan level + master",
                        "plan_peak_dbfs": target, "master_db_at_peak": round(final_target - target, 2),
                        "expected_final_peak_dbfs": round(final_target, 2), "measured_peak_dbfs": round(pk, 2),
                        "peak_at_s": round(tpk, 3), "error_db": round(pk - final_target, 2),
                        "group_stem_window_peak_dbfs": round(region_peak(stems_g[d["group"]], a_, b_), 2),
                        "mix_window_peak_dbfs": round(region_peak(x, a_, b_), 2),
                        "voice_peak_same_window_dbfs": round(vloc, 2), "voice_peak_global_dbfs": round(vglob, 2),
                        "above_voice_window": bool(pk > vloc + 0.05), "above_voice_global": bool(pk > vglob + 0.05)})
    st["sfx_cues"] = per_cue
    report["stems"] = st
    if MUSIC:
        log("voice stem: I %.2f LUFS (stereo meter), TP %.2f dBTP | bed under voice %.1f LUFS ST (voice %.1f); %s | "
            "title hold momentary %.1f, un-ducked bed ST %.1f (hold) / %.1f (post-drop) / %.1f (MU1)" % (
                st["voice"]["integrated_lufs"], st["voice"]["true_peak_dbtp"], bed["under_voice_short_term_median_lufs"],
                bed["voice_short_term_median_lufs"], {k: round(v_["bed_lufs"], 1) for k, v_ in bed["by_section"].items()},
                bed["title_hold_momentary_median_lufs"], bed["undecked_bed_short_term_title_hold_lufs"],
                bed["undecked_bed_short_term_post_drop_median_lufs"], bed["undecked_bed_short_term_mu1_median_lufs"]))
        log("music checks [measured, expected]:", json.dumps(chk, default=lambda o: round(o, 2)))
    else:
        log("voice stem: I %.2f LUFS (stereo meter), TP %.2f dBTP, short-term median %.1f LUFS | music OFF: A2 stem "
            "peak %.1f dBFS" % (st["voice"]["integrated_lufs"], st["voice"]["true_peak_dbtp"],
                                bed["voice_short_term_median_lufs"], st["music_stem_peak_dbfs"]))
    log("stems sum vs mix max diff %.1e; SFX stem-minus-model residual energy %s dB" % (
        st["stems_sum_vs_mix_max_abs_diff"], resid))
    log("\nSFX rendered peaks (isolated from overlapping cues) vs plan, and vs the voice:")
    for r_ in per_cue:
        if r_["layer"]:
            continue
        log("  %-5s plan %6.1f  master %+5.2f  expected %6.2f  measured %6.2f (err %+.2f)  voice(window) %6.2f  %s" % (
            r_["cue"], r_["plan_peak_dbfs"], r_["master_db_at_peak"], r_["expected_final_peak_dbfs"],
            r_["measured_peak_dbfs"], r_["error_db"], r_["voice_peak_same_window_dbfs"],
            "ABOVE VOICE" if r_["above_voice_window"] else ""))
    v5 = [r_ for r_ in per_cue if r_["layer"]]
    if v5:
        errs = np.array([r_["error_db"] for r_ in v5])
        muted_ = {c.cue for c in clips if getattr(c, "mutes", None)}
        errs_u = np.array([r_["error_db"] for r_ in v5 if r_["cue"] not in muted_] or [0.0])
        st["v05_layers_check"] = {"layers": len(v5), "max_abs_error_db": round(float(np.max(np.abs(errs))), 3),
                                  "max_abs_error_db_not_muted": round(float(np.max(np.abs(errs_u))), 3),
                                  "muted_layers": len(muted_ & {r_["cue"] for r_ in v5}),
                                  "median_error_db": round(float(np.median(errs)), 3),
                                  "above_voice_window": [r_["layer"] for r_ in v5 if r_["above_voice_window"]],
                                  "worst": sorted(v5, key=lambda r_: -abs(r_["error_db"]))[:3]}
        log("  v05 library layers: %d, rendered vs model peak error max %.3f dB (%.3f dB without the %d dropout-muted "
            "ones, whose remaining peak sits on a 10 ms mute ramp), median %+.3f; above the voice in their own window: %d" % (
                len(v5), st["v05_layers_check"]["max_abs_error_db"], st["v05_layers_check"]["max_abs_error_db_not_muted"],
                st["v05_layers_check"]["muted_layers"], st["v05_layers_check"]["median_error_db"],
                len(st["v05_layers_check"]["above_voice_window"])))


# --------------------------------------------------------------------------------------------
# AUDIO_NOTES.md (generated from this run's numbers)
# --------------------------------------------------------------------------------------------
def v05_notes(R, clips, ev, beat_map, marks):
    """The v05 section of AUDIO_NOTES.md (REVISION_v05.md G9 + S, doc 2.7)."""
    L = []
    w = L.append
    v5 = R.get("v05", {})
    lib = load_library() or {}
    vo_rep = load_json(VO_REPORT) if VO_REPORT.exists() else {}
    w("## v05 changes (REVISION_v05.md G9 + S, doc section 2.7)\n")
    w("* **Voice and timing**: `%s` is the beat map's `vo_file` (no hard-coded name; words `%s`, report `%s`): %s. "
      "Edit %d f = %.3f s, %d beats (%s), the voice ends %.3f s, the story at f%s; B18 is the CTA end card (no voice)." % (
          VO_FILE.relative_to(ROOT), WORDS_JSON.name, VO_REPORT.name, "; ".join(
              "cut %s %d f ('%s', %s)" % (c_["name"], c_["frames"], c_["removed"], c_["why"]) for c_ in vo_rep.get("v05_cuts", []))
          or "no cut list", int(beat_map["edit_end_frame"]), float(beat_map["edit_end_s"]), len(beat_map["beats"]),
          ", ".join("%s %d f" % (b["id"], b["dur_frames"]) for b in beat_map["beats"] if b.get("v04_dur_frames") not in (
              b["dur_frames"],)), float(beat_map["vo_end_s"]), beat_map.get("story_end_frame", "?")))
    sch = v5.get("cues_schema", {})
    blocks = "; ".join("%s loses v04 local %d-%d (%d f)" % (b, st, st + n - 1, n) for b, (st, n, _) in ev.cut.blocks.items())
    w("* **Cue files** (beat frames, f0 = beat start). v05 schema: %s. Legacy (only `events`, moved from v04 to v05 "
      "frames by `timing/v04_to_v05.json`: %s; every other beat keeps its local frames): %s. None: %s.%s%s" % (
          ", ".join(b for b, v in sch.items() if v == "v05") or "none", blocks or "no beat changed length",
          ", ".join(b for b, v in sch.items() if v == "legacy") or "none",
          ", ".join(b for b, v in sch.items() if v == "none") or "none",
          (" Moved: " + "; ".join(v5.get("legacy_remapped_v04_to_v05", {}).values()) + ".") if v5.get(
              "legacy_remapped_v04_to_v05") else "",
          (" Cut by the v05 trims (no sound, no STORYBOARD refill): " + "; ".join(
              "%s %s" % (b, d) for b, d in v5.get("cut_by_v05_trims", {}).items()) + ".") if v5.get("cut_by_v05_trims") else ""))
    if v5.get("legacy_s_cues_skipped"):
        w("* **Legacy S-cues left out** (their beat's cue file no longer lists the event, so no sound): " +
          ", ".join(v5["legacy_s_cues_skipped"]) + ".")
    w("* **Auto layers (as built)**: `word_pops` -> `tick` (tick_1/2/3 rotating in edit order; one tick per frame, none "
      "on a frame that is also a key word), sound start on the frame, %s dBFS; `key_words` -> `whoosh_in` ENDING on the "
      "frame (%s dBFS) + `thump_low` starting on it (%s dBFS); `hook_cuts` -> `swipe` with its peak on the cut (%s "
      "dBFS); `sfx` -> the named library sound, aligned by its library `align` (start / peak / end on the frame) at its "
      "default level or the item's `gain_db` (the sound's sample peak in dBFS, capped at %.0f), `dur_f` shortens it; "
      "`dropouts` [{f, frames}] -> silence over the `frames` frames ending at f for the music bed (when on) and every "
      "riser/ambience sound (whoosh_in, reverse_cymbal, riser, keyboard_clatter; S05, S07, S18); `archival` -> picture "
      "only. Missing keys = nothing. Levels are pre-master; the master gain (below) comes on top. Group A5 holds the "
      "ticks, whooshes-in and thumps; the rest go to A3 (hits) / A4 (sweeps, risers, textures)." % (
          lib.get("tick", {}).get("default_peak_dbfs", "?"), lib.get("whoosh_in", {}).get("default_peak_dbfs", "?"),
          lib.get("thump_low", {}).get("default_peak_dbfs", "?"), lib.get("swipe", {}).get("default_peak_dbfs", "?"),
          V05_GAIN_CAP_DBFS))
    bk = v5.get("by_kind", {})
    w("* **This run**: %d v05 layers (%s), %d duplicate/key-word ticks merged; %d dropouts%s.%s%s" % (
        sum(bk.values()), ", ".join("%s %d" % kv for kv in bk.items()) or "none", v5.get("merged_ticks", 0),
        len(v5.get("dropouts", [])), (" (" + "; ".join("%s f%d %df = %.3f-%.3f s" % (
            d["beat"], d["f"], d["frames"], d["window_s"][0], d["window_s"][1]) for d in v5["dropouts"]) + ")") if v5.get(
            "dropouts") else "", (" Silenced by them: " + "; ".join("%s %s-%s s" % (
                m_["clip"], m_["window_s"][0], m_["window_s"][1]) for m_ in v5.get("dropout_mutes", [])) + ".") if v5.get(
            "dropout_mutes") else "", (" Skipped: " + "; ".join(v5["skipped"]) + ".") if v5.get("skipped") else ""))
    if v5.get("by_beat"):
        w("\n| Beat | Cues | Ticks | Key words (whoosh + thump) | Hook swipes | Named sfx |\n|---|---|---|---|---|---|")
        for b in beat_map["beats"]:
            d = v5["by_beat"].get(b["id"], {})
            named = [c for c in clips if getattr(c, "v05", False) and c.kind == "sfx" and c.event.split(".")[0] == b["id"]]
            if sch.get(b["id"]) != "v05" and not d:
                continue
            w("| %s | %s | %d | %d | %d | %s |" % (b["id"], sch.get(b["id"], "?"), d.get("word_pop", 0),
                                                   d.get("key_word", 0) // 2, d.get("hook_cut", 0), ", ".join(
                "%s f%d %s%.0f" % (c.sound, c.beat_f, "" if c.target_dbfs < 0 else "+", c.target_dbfs) for c in
                sorted(named, key=lambda c: c.beat_f)) or "-"))
        w("")
    if lib:
        w("**03_SFX/v05 library** (`tools/build_tesseract_sfx_v05.py`; 48 kHz 24-bit WAV written AT the default level; "
          "recipes in library.json):\n")
        w("| Name | Files | Align | Default dBFS | Group | Class | Source |\n|---|---|---|---|---|---|---|")
        for k, e in lib.items():
            w("| `%s` | %s | %s | %.0f | %s | %s | %s |" % (k, ", ".join(e["files"]), e["align"], e["default_peak_dbfs"],
                                                         e["group"], e["class"], e["source"]))
        w("")
    w("* **Music automation** (built, bed off: MUSIC = False, client v04 note 1): duck %.0f dB under every VO phrase "
      "(50/300 ms), silent inside every dropout window (10 ms ramps), full level again from 'fun.' (MU5: the drop on "
      "its frame, +3 dB for 2 s), MU4/MU6/MU7/MU8 as in v02. `MUSIC = True` brings a bed back with all of it.\n" % DUCK_DB)
    ca = v5.get("caption_alignment") or {}
    if ca:
        w("* **Caption frames vs the VO** (word_pops + key_words within -1..+3 f of a word onset of the beat map): " +
          ", ".join("%s %d/%d%s" % (b, d["on_a_word_onset"], d["caption_frames"], " STALE?" if d["stale_timing_suspected"]
                                     else "") for b, d in ca.items()) + ".")
    if ev.notes or v5.get("cap_hits"):
        w("* Cue-file notes: " + "; ".join(ev.notes + v5.get("cap_hits", [])) + ".\n")
    return L


def write_notes(report, clips, spans, marks, decisions, ev, beat_map, music_plan, lp_file, lag_mu, mu_s0):
    R = report
    mi = R["master"]
    mix = R.get("mix", {})
    eb = mix.get("ffmpeg_ebur128", {})
    st = R.get("stems", {})
    bed = st.get("music_bed", {})
    chk = st.get("music_envelope_checks", {})
    an = R["music_anchor"]
    off = an["offset_s"]
    vo_fm = (load_json(VO_REPORT).get("final_metrics") or {}) if VO_REPORT.exists() else {}
    L = []
    w = L.append
    w("# Audio half of the Tesseract project (A1-A5), v05\n")
    w("Generated by `tools/build_tesseract_audio.py` on every run (do not hand-edit; change the script's constants "
      "and re-run). Golden rule: the Master Edit Plan, Music plan p.32-35, SFX plan p.35-38, Audio mix and export "
      "settings p.38, overridden where the client's notes say so (REVISION_v02.md ... REVISION_v05.md; v05: the "
      "instruction doc's section 2.7 wins, X8). Inputs: `%s` and `%s` (the beat map's `vo_file`), "
      "`timing/beat_map.json` (%s), `02_Music/music_plan.json`, `03_SFX/sfx_plan.json`, `03_SFX/sfx_analysis.json`, "
      "`03_SFX/v05/library.json`, each beat's `hyperframes/<composition>/cues.json` (v05 schema, or legacy events "
      "moved to v05 frames, else the STORYBOARD.md cues).\n" % (
          VO_FILE.relative_to(ROOT), WORDS_JSON.relative_to(ROOT), beat_map.get("version", "?")))
    L += v05_notes(R, clips, ev, beat_map, marks)
    w("## v02 changes\n")
    w("* **Voiceover 115%%** (note 10): `%s` (%.2f s, %s LUFS as a mono track, true peak %s dBFS) and its word times. "
      "Every duration comes from the beat map: edit %.3f s = %d frames, voice ends %.3f s." % (
          VO_FILE.relative_to(ROOT), probe(VO_FILE)["duration"], vo_fm.get("integrated_lufs", "?"),
          vo_fm.get("true_peak_dbfs", "?"), float(beat_map["edit_end_s"]), int(beat_map["edit_end_frame"]),
          float(beat_map["vo_end_s"])))
    if not MUSIC:
        w("* **v04: no background music** (client note 1, 'remove Bg music we can change that'): the A2 group is empty, "
          "no music asset is packaged; voice and every SFX keep their pre-master levels and the master gain is solved on "
          "voice + SFX alone (table below). The music code stays: `MUSIC = True` in the script (and "
          "02_Music/music_plan.json for the new track) brings a bed back with the v02 rules (anchor on 'fun', MU1-MU8, "
          "the MU2 bar edit, ducking); the marks it would use are still in audio_report.json.")
    w("* **Music re-anchored on MU5 first** (plan p.34): the measured drop downbeat (track %.2f s) on the new 'fun' "
      "onset %.3f s: track = edit + %.2f s (v01: + 139.68 s). Every other mark is re-derived from the beat map and the "
      "events exactly as in v01 (table below)." % (an["drop_track_s"], an["fun_onset_s"], off))
    be = an.get("bar_edit") or {}
    if be.get("applied"):
        w("* **MU2 whole-bar edit** (plan p.34's allowed fix, applied on the coordinator's v02 instruction): the track "
          "starts one bar (%.4f s) earlier, at %.2f s, so the breakdown arrives at %.3f s inside 'broke' (%.3f-%.3f s; "
          "without the edit %.3f s, %.2f s before it), and breakdown bar %d (track %.3f-%.3f s) is removed on its bar "
          "line at edit %.3f s with a %d ms equal-power crossfade, so MU3, the MU5 drop and everything after the seam "
          "keep the anchor's timing (details under the MU table)." % (
              be["bar_s"], be["offset_before_seam_s"], be["MU2_edit_s"], be["broke_s"][0], be["broke_s"][1],
              be["MU2_without_edit_s"], be["broke_s"][0] - be["MU2_without_edit_s"], be["removed_bar"],
              be["removed_track_s"][0], be["removed_track_s"][1], be["seam_bar_line_edit_s"], BAR_EDIT_XFADE_S * 1000))
    s10 = next((c for c in clips if c.cue == "S10"), None)
    if s10 and any("not in this edit" in n for n in s10.notes):
        w("* **S10 = the glitch** (note 5): B8's glitch impact (`%s`) on `%s`; v05: S08 is no longer in the edit (B8's "
          "cue file dropped `breaks`), so S10 is calibrated on its own at S08's plan level (%.1f dBFS)." % (
              s10.file, s10.event, s10.target_dbfs))
    elif s10:
        w("* **S10 = the glitch** (note 5): B11's flip became the X4 glitch of B8, so its sound changed from S10 Flip "
          "to B8's glitch impact (`%s`) at S08's pre-master gain (%+.2f dB, following S08's calibration; not "
          "calibrated on its own, so its 'error' below is Tesseract's resampler on the bare transient), in S10's "
          "group A4, starting on `%s` (%s)." % (s10.file, s10.gain_db, s10.event,
                                      "; ".join(s10.notes) if s10.notes else "B11 cues.json"))
    if R.get("cue_scaling_v01_to_v02"):
        w("* **v01-timed cue files** (the beat builder has not rewritten them yet): their frames are scaled to the "
          "v02 beat length until it does: " + "; ".join("%s: %s" % (k, v) for k, v in R["cue_scaling_v01_to_v02"].items()) + ".")
    w("* Picture keyframes follow the client's 'nothing linear' rule (easings.net curves). The audio volume "
      "automation below stays piecewise linear on purpose: it is a sampled gain envelope (ducking, de-click ramps, "
      "limiter dips), not an animation, and the engine interpolates gain linearly every 10 ms anyway.\n")
    w("## What was built\n")
    w("* `.tesseract-work/audio.tsrct`, deleted and recreated on each run. One composition `main`, 1920x1080, "
      "%.1f s, background #0A0A0A. Five Group layers (CONFLICTS C6 + v05): `A1 Voiceover` (9001), `A2 Music` (9002), "
      "`A3 SFX hits & impacts` (9003), `A4 Risers, whooshes & textures` (9004), `A5 Caption pops & key words` (9005). "
      "Every layer id is >= 9000 (VO 9101, music 9201-9203, S-cues 10000 + cue x 100 + n, v05 library layers 20000 + "
      "n in edit order), every asset id starts with `aud-`, so the picture half can merge in with lower ids. %d audio "
      "layers, %d of them with volume keyframes." % (
          beat_map["edit_end_s"], len(R["layers"]), sum(1 for x in R["layers"] if x["keyframes"])))
    w("* Volume envelopes are native keyframe animators in `composition.dynamics`: propertyType `volume`, the "
      "value is the final linear gain, timed on the layer's content clock (source ms). Measured engine behaviour "
      "that shaped the build: (1) the volume is evaluated every 10 ms and interpolated linearly, so the shortest "
      "ramp is 10 ms (every hard cut, mute and crossfade here is a 10 ms ramp); (2) a keyframe's easing governs "
      "the segment *arriving* at it, so every keyframe is `linear`; (3) Tesseract plays a mono file at full level on "
      "both channels; (4) its MP3 decoder does not skip the LAME encoder delay (FFmpeg does), measured per file.")
    w("* FFmpeg derivatives (originals untouched; recipe JSON beside each): `%s` (MU6, lowpass=f=%d), "
      "`03_SFX/derived/S02_Siren_hp300.wav` and `03_SFX/derived/S14_Siren_hp300.wav` (highpass=f=300)." % (
          lp_file.relative_to(ROOT), MU6_LOWPASS_HZ))
    w("* Checks in `.tesseract-work/checks/`: `mix.wav` (`tsrct export-audio`, 48 kHz 16-bit stereo), stems "
      "`stem_voice/music/sfx_a3/sfx_a4.wav` (document copies with the other groups hidden), `audio_report.json` "
      "(every number below), `loudness.json` (skill `measure`), `wave_*.png` (+ JSON) waveform views.\n")
    w("## Gain structure\n")
    w("Per-track levels are the plan's track levels (pre-master); the master stage then sets the programme "
      "loudness, as in a DAW (track levels -> master limiter/gain).\n")
    w("| Stage | Setting | Why |\n|---|---|---|")
    w("| A1 voiceover | unity (0 dB) | The processed VO already meets the plan's voice spec as a track: %s LUFS "
      "(mono), true peak %s dBFS. Tesseract sends mono at full level to both channels, so the voice reads "
      "%.1f LUFS on a stereo meter before the master and %.1f LUFS after it (CONFLICTS C21). Unity keeps the plan's "
      "peak relationships: voice peaks about -3.8 dBFS before the master, every SFX at -6 dBFS or lower except S19. |" % (
          vo_fm.get("integrated_lufs", "?"), vo_fm.get("true_peak_dbfs", "?"),
          st.get("voice", {}).get("integrated_lufs", float("nan")) - mi["static_makeup_db"],
          st.get("voice", {}).get("integrated_lufs", float("nan"))))
    w("| A2 music bed | base %.1f dB, duck %.0f dB | Calibrated on the measured track: the un-ducked bed reads about "
      "-16 LUFS short-term and the ducked full-energy bed about -22 LUFS (plan p.35). music_plan.json proposed -8 dB "
      "(it measured about 1 dB under both targets). |" % (MUSIC_BASE_DB, DUCK_DB) if MUSIC else
      "| A2 music bed | off (v04 note 1) | No background music; the group stays in the project, empty. |")
    w("| A3/A4 SFX | per cue (table) | Each cue's sample peak at the cue sheet's level, combined peak for layered "
      "cues (mixed in Python at their real offsets and relative gains). |")
    w("| Master | static %+.2f dB on every layer, plus %d short automated dip(s) | Solved so the mix reads %.1f LUFS "
      "integrated. A static gain alone cannot also keep true peak <= -1 dBTP: the pre-master mix peaks at %.2f dBTP "
      "(%s), so a static-only master would peak at %.2f dBTP, and the "
      "static gain that would meet the ceiling (%.2f dB) leaves the mix at %.2f LUFS, outside -14 +-1. The plan's "
      "master is a limiter with a -1.0 dBTP ceiling; Tesseract has none, so its gain reduction is emulated by "
      "master gain automation (applied equally to every layer, %d ms look-ahead attack, %d ms release, ceiling "
      "%.1f dBTP to keep 0.5 dB for AAC encoding). Every relative level stays as planned (CONFLICTS C20). |" % (
          mi["static_makeup_db"], len(mi["dips"]), MASTER_TARGET_LUFS, mi["premaster_true_peak_dbtp"],
          "at the 'fun' drop: S09 sub drop + MU5 lift + voice" if MUSIC else "at its loudest transient",
          mi["static_only_true_peak_dbtp"], mi["static_gain_for_ceiling_only_db"],
          mi["static_gain_for_ceiling_only_integrated_lufs"], MASTER_ATTACK_S * 1000, MASTER_RELEASE_S * 1000,
          MASTER_CEILING_DBTP))
    if mi["dips"]:
        w("\nMaster dips (gain reduction on top of the static make-up): " + "; ".join(
            "%.3f-%.3f s, max %.2f dB at %.3f s" % (d["start_s"], d["end_s"], d["max_db"], d["at_s"]) for d in mi["dips"]) + ".\n")
    if MUSIC:
        w("## A2 music: MU1-MU8\n")
        w("Black Vertigo (`%s`, licensed per the user). Track time (FFmpeg decode clock) = edit + %.2f s, anchored on the "
          "measured drop downbeat %.2f s on the onset of 'fun' (%.3f s, `%s`; MU5's lift and S09 start on its frame, "
          "%.3f s). Tesseract plays this MP3 %.2f ms later than FFmpeg (measured, encoder delay not skipped), so the "
          "layer's source start is %d ms; the stem check below shows the drop at %+.2f ms from the track clock.\n" % (
              music_plan["track"], off, an["drop_track_s"], an["fun_onset_s"], WORDS_JSON.name, marks["MU5"],
              lag_mu * 1000, mu_s0, chk.get("drop_offset_vs_track_clock_ms", float("nan"))))
        w("| Code | Edit time | Frame | Track time | Implementation |\n|---|---|---|---|---|")
        m2, m3 = an["MU2"], an["MU3"]
        w("| MU1 | 0.000 s | 0 | %.2f s | Bed starts at full energy, no fade-in (10 ms de-click ramp only). The voice starts at %.3f s, so the bed enters already ducked. |" % (
            be["offset_before_seam_s"] if be.get("applied") else off, spans[0][0]))
        if be.get("applied"):
            w("| MU2 | %.3f s | %.1f | %.2f s | The breakdown arrives inside 'broke' (%.3f-%.3f s), %.3f s after its onset (%s the plan's half second; v01 was 0.636 s after it), through the whole-bar edit: the track starts one bar earlier and breakdown bar %d is removed at %.3f s (seam), so nothing after the seam moves. |" % (
                m2["edit_s"], m2["edit_s"] * FPS, m2["track_s"], m2["broke_s"][0], m2["broke_s"][1], m2["delta_from_onset_s"],
                "within" if m2["within_half_second"] else "just outside", be["removed_bar"], be["seam_bar_line_edit_s"]))
        else:
            w("| MU2 | %.3f s | %.1f | %.2f s | The breakdown arrives by itself, %.3f s %s the onset of 'broke' (%.3f-%.3f s): %s. No edit (MU2_BAR_EDIT off or its conditions failed, see audio_report.json). |" % (
                m2["edit_s"], m2["edit_s"] * FPS, m2["track_s"], abs(m2["delta_from_onset_s"]),
                "before" if m2["delta_from_onset_s"] < 0 else "after", m2["broke_s"][0], m2["broke_s"][1],
                "within half a second" if m2["within_half_second"] else "outside the plan's half second"))
        w("| MU3 | %.3f s | %.1f | %.2f s | Near-silent section starts %.3f s %s 'dull' (%.3f s): %s 1 s (the plan's test), %s. |" % (
            m3["edit_s"], m3["edit_s"] * FPS, m3["track_s"], abs(m3["delta_from_onset_s"]),
            "before" if m3["delta_from_onset_s"] < 0 else "after", m3["dull_s"][0],
            "within" if m3["within_1s"] else "NOT within",
            "on or after it as the table asks" if m3["on_or_after"] else
            "but before it, not 'on or just after' (a bar edit inside the breakdown cannot move MU3 with the drop "
            "anchored and the build uncut)"))
        w("| MU4 | %.3f-%.3f s | %d-%d | %.2f-%.2f s | Hard mute for 15f from B8's first black frame (10 ms ramp into it), then un-mute in place (the track keeps running). |" % (
            marks["MU4_start"], marks["MU4_end"], round(marks["MU4_start"] * FPS), round(marks["MU4_end"] * FPS),
            marks["MU4_start"] + off, marks["MU4_end"] + off))
        w("| MU5 | %.3f s | %d | %.2f s | The drop lands on 'fun' (onset %.3f s) with S09 and the X3 flash; +3 dB from the 'fun' frame for 2 s (to %.3f s), back over 0.3 s. |" % (
            marks["MU5"], round(marks["MU5"] * FPS), an["drop_track_s"], an["fun_onset_s"], marks["MU5"] + MU5_HOLD_S))
        w("| MU6 | %.3f-%.3f s | %d-%d | %.2f-%.2f s | From 'Don't believe me?' the main bed crossfades (10 ms) to layer 9202, the same excerpt low-passed at %d Hz, at -6 dB; it opens again (10 ms) on B15's `label` moment ('Race', where the v01 RACE AND CHASE label landed; the label itself is removed in v02, note 7). |" % (
            marks["MU6_start"], marks["MU6_end"], round(marks["MU6_start"] * FPS), round(marks["MU6_end"] * FPS),
            marks["MU6_start"] + off, marks["MU6_end"] + off, MU6_LOWPASS_HZ))
        w("| MU7 | %.3f-%.3f s | %d-%d | %.2f-%.2f s | Music cut under the 1 s rewind (S17 alone), resumes in place 6 dB lower under the glow line, back to the normal bed at the B17 cut %.3f s (30 ms). |" % (
            marks["MU7_start"], marks["MU7_end"], round(marks["MU7_start"] * FPS), round(marks["MU7_end"] * FPS),
            marks["MU7_start"] + off, marks["MU7_end"] + off, marks["MU7_return"]))
        w("| MU8 | %.3f s | %.1f | %.2f s | Hard stop at the end of 'now?' (beat_map vo_end_s), 10 ms ramp, the layer ends there. No music in the logo tail; S18 and S19 carry it. |\n" % (
            marks["MU8"], marks["MU8"] * FPS, marks["MU8"] + off))
        if be.get("applied"):
            w("**MU2 bar edit.** Candidates (breakdown bars 2-%d; the arrival bar and the bar into MU3 are excluded), scored "
              "by the octave-band level difference of the two sides of the seam (0.5 s before the removed bar vs before the "
              "bar after it, and 0.5 s after both bar lines): %s. Chosen: bar %d, seam on its bar line at %.3f s (under the "
              "voice, the bed ducked). Two layers: %d plays the track one bar early up to the crossfade, %d the rest at the "
              "anchor's offset; the equal-power crossfade runs %.3f-%.3f s, ending %d ms before the bar line, so the next "
              "bar's downbeat comes through whole and the removed bar's downbeat (up to ~20 ms early on this track) is not "
              "heard. Checks on the music stem: track lag %s ms before the seam and %s ms after it (vs the FFmpeg-decoded "
              "track at each offset), level across the crossfade %s dB vs the 0.4 s either side (the same windows at that bar "
              "line of the unedited track: %s dB, the bed's own dip before a downbeat); MU3 stays %.3f s from "
              "'dull' (within 1 s), the drop stays at %+.2f ms from the track clock (MU5 frame-exact, frame %d).\n" % (
                  len(be["candidates"]) + 1, ", ".join("bar %d %.2f dB" % (c["bar"], c["score"]) for c in be["candidates"]),
                  be["removed_bar"], be["seam_bar_line_edit_s"], MUSIC_LAYER_ID, MUSIC_B_LAYER_ID, be["xfade_s"][0],
                  be["xfade_s"][1], BAR_EDIT_LEAD_S * 1000,
                  ("%.2f" % chk["bar_edit_track_lag_before_seam_ms"]) if "bar_edit_track_lag_before_seam_ms" in chk else "?",
                  ("%.2f" % chk["bar_edit_track_lag_after_seam_ms"]) if "bar_edit_track_lag_after_seam_ms" in chk else "?",
                  ("%+.2f" % chk["bar_edit_seam_level_vs_neighbours_db"]) if "bar_edit_seam_level_vs_neighbours_db" in chk else "?",
                  ("%+.2f" % chk["bar_edit_same_window_unedited_bar_line_db"]) if "bar_edit_same_window_unedited_bar_line_db" in chk else "?",
                  m3["delta_from_onset_s"], chk.get("drop_offset_vs_track_clock_ms", float("nan")), round(marks["MU5"] * FPS)))
        gaps = [b_[0] - a_[1] for a_, b_ in zip(spans, spans[1:])]
        short = sum(1 for g_ in gaps if g_ < ATTACK_S + RELEASE_S)
        th_ = bed.get("title_hold_window_s", [0, 0])
        longer = ["%.3f s after '%s'" % (b_[0] - a_[1], a_[2].split()[-1]) for a_, b_ in zip(spans, spans[1:])
                  if b_[0] - a_[1] >= ATTACK_S + RELEASE_S and abs(a_[1] - th_[0]) > 1e-6]
        w("**Ducking.** %d phrase spans from `%s` (word gaps shorter than %.2f s merged). Each phrase ducks the "
          "bed by %.0f dB with a 50 ms look-ahead attack (full depth when the phrase starts) and a 300 ms release; the "
          "curve is the minimum of the per-phrase trapezoids (amplitude-linear ramps), i.e. what a 50/300 ms ducker "
          "does. %d of the %d pauses are shorter than attack + release (0.35 s), so the bed swells a few dB in those "
          "pauses without fully recovering. It comes fully up in the B13 title hold (%.3f-%.3f s)%s. To hold the duck "
          "through sentence pauses instead, set MERGE_GAP_S = 0.30 and re-run.\n" % (
              len(spans), WORDS_JSON.name, MERGE_GAP_S, DUCK_DB, short, len(gaps), th_[0], th_[1],
              (" and the other pauses of 0.35 s or more (" + ", ".join(longer) + ")") if longer else ""))
    else:
        w("## A2 music: off (v04)\n")
        w("No music bed (client note 1). The bed's v02 timing (offset %.2f s, MU1-MU8 marks, the MU2 bar edit) is still "
          "computed and recorded in `checks/audio_report.json` for a replacement track.\n" % off)
    w("## A3/A4 SFX cues\n")
    w("Edit frame = beat start frame + the event's beat frame. Gain = pre-master layer gain (dB); final = with the "
      "master at the cue's peak. Plan = the cue sheet's peak level; measured = the cue's rendered sample peak, "
      "isolated from overlapping cues of the same group (stem minus the model of the others).\n")
    w("| Cue | Layer (id) | Grp | Event: beat f -> edit f (s) | Placement rule | Start s (frame) | Dur s | Src in s | Fades | Gain dB | Final dB | Plan dBFS | Measured dBFS |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    meas = {r_["cue"]: r_ for r_ in st.get("sfx_cues", [])}
    for c in sorted((c for c in clips if not getattr(c, "v05", False)), key=lambda c: (c.edit_start, c.layer_id)):
        beat, en = c.event.split(".")
        fades = []
        if c.fade_in:
            fades.append("in %d ms" % round(c.fade_in * 1000))
        if c.fade_out:
            fades.append("out %.0ff" % (c.fade_out * FPS))
        mm = meas.get(c.cue if c.combined else c.cue + c.sub, {})
        w("| %s | %s (%d) | %s | %s.%s f%d -> %d (%.3f) | %s | %.3f (%.1f) | %.3f | %.3f | %s | %+.2f | %+.2f | %.1f%s | %s |" % (
            c.cue, c.name, c.layer_id, c.group, beat, en, ev.beat_frame(c.event), round(c.event_t * FPS), c.event_t,
            c.rule.replace("|", "/"), c.edit_start, c.edit_start * FPS, c.dur, c.src_start, ", ".join(fades) or "-",
            c.gain_db, c.gain_db + c.master_db_at_peak, c.target_dbfs, " comb." if c.combined else "",
            ("%.2f" % mm["measured_peak_dbfs"]) if mm else "-"))
    w("")
    s13 = decisions.get("S13")
    if s13:
        o = s13["if_file_started_on_first_letter"]
        w("**S13 decision.** T6 types 14 letters, one every 2f from B13 f%d (edit f%d). The 1.27 s file holds %d "
          "keystrokes at %s s (gaps %s ms). Started on the first letter, its first keystroke comes %d ms after the "
          "first letter, the keystrokes sit %s ms from the nearest letter and the last one lands %d ms after the last "
          "letter. Criterion: %s. Result: **%s**.\n" % (
              s13["letters_f"][0], s13["letters_f"][0] + ev.beat_start_frame("B13"),
              len(s13["file_keystroke_onsets_s"]), s13["file_keystroke_onsets_s"], s13["keystroke_gaps_ms"],
              o["first_keystroke_after_first_letter_ms"], o["keystroke_offsets_from_nearest_letter_ms"],
              o["last_keystroke_after_last_letter_ms"], s13["criterion"], s13["decision"]))
    w("## Measurements (this run)\n")
    if eb:
        w("* **Mix** (`checks/mix.wav`): integrated **%.1f LUFS**, true peak **%.1f dBTP**, LRA %.1f LU (FFmpeg "
          "ebur128). Own BS.1770 meter: %.2f LUFS, %.2f dBTP, sample peak %.2f dBFS. Skill `measure` "
          "(`checks/loudness.json`): %.2f LUFS, %.2f dBTP, LRA %.1f LU. Plan targets -14 +-1 LUFS and <= -1 dBTP: %s." % (
              eb["integrated_lufs"], eb["true_peak_dbtp"], eb["lra_lu"], mix["own"]["integrated_lufs"],
              mix["own"]["true_peak_dbtp"], mix["own"]["sample_peak_dbfs"],
              mix.get("skill_measure", {}).get("integrated_lufs", float("nan")),
              mix.get("skill_measure", {}).get("true_peak_dbtp", float("nan")),
              mix.get("skill_measure", {}).get("loudness_range_lu", float("nan")),
              "met" if all(mix["targets_met"].values()) else "NOT met %s" % mix["targets_met"]))
    if mix.get("mono_folddown"):
        w("* Mono fold-down ((L+R)/2): %.2f LUFS (%+.2f LU vs stereo), so nothing important cancels in mono. Phone "
          "check aid: `%s` (skill `mobile-preview`: mono, 150 Hz-7 kHz; not a substitute for a real phone)." % (
              mix["mono_folddown"]["integrated_lufs"], mix["mono_folddown"]["delta_vs_stereo_lu"], mix["mobile_preview"]))
    if st:
        v_ = st["voice"]
        w("* **Voice** (A1 stem, stereo meter): %.1f LUFS integrated, true peak %.1f dBTP, sample peak %.1f dBFS; "
          "short-term median %.1f LUFS where the voice covers >= 85%% of the 3 s window." % (
              v_["integrated_lufs"], v_["true_peak_dbtp"], v_["sample_peak_dbfs"], bed["voice_short_term_median_lufs"]))
        m0_ = mi["static_makeup_db"]
        full = [(k, v2) for k, v2 in (bed.get("by_section") or {}).items() if k.startswith(("MU1", "post"))]
    if st and MUSIC:
        w("* **Music bed under the voice** (A2 stem, same windows, normal bed only; final-mix values, the pre-master "
          "track level is %.2f dB higher): median %.1f LUFS short-term. By section: %s. The plan's ~-22 LUFS is the "
          "full-energy bed's track level: %s LUFS pre-master. The breakdown and the near-silent section are quieter by "
          "the track's own design (plan: 'the energy dips around broke, goes nearly silent on dull'). The bed sits "
          "%.1f dB under the voice as a median over the whole edit and %.1f-%.1f dB under it in the full-energy "
          "sections." % (
              -m0_, bed["under_voice_short_term_median_lufs"], "; ".join(
                  "%s bed %.1f / voice %.1f LUFS" % (k, v2["bed_lufs"], v2["voice_lufs"]) for k, v2 in bed["by_section"].items()),
              " and ".join("%.1f" % (v2["bed_lufs"] - m0_) for k, v2 in full),
              bed["voice_short_term_median_lufs"] - bed["under_voice_short_term_median_lufs"],
              min(v2["voice_lufs"] - v2["bed_lufs"] for k, v2 in full),
              max(v2["voice_lufs"] - v2["bed_lufs"] for k, v2 in full)))
        w("* **Music bed without voice** (final-mix values; pre-master +%.2f dB): B13 title hold (%.3f-%.3f s) "
          "momentary median %.1f LUFS (max %.1f); the un-ducked bed reads %.1f LUFS short-term there, %.1f LUFS median "
          "after the drop and %.1f LUFS in the MU1 section (plan: about -16)." % (-mi["static_makeup_db"],
              bed["title_hold_window_s"][0], bed["title_hold_window_s"][1], bed["title_hold_momentary_median_lufs"],
              bed["title_hold_momentary_max_lufs"], bed["undecked_bed_short_term_title_hold_lufs"],
              bed["undecked_bed_short_term_post_drop_median_lufs"], bed["undecked_bed_short_term_mu1_median_lufs"]))
        w("* **Music envelope checks** (A2 stem vs the FFmpeg-decoded track, dB, [measured, expected incl. master]):")
        for k, v2 in chk.items():
            if isinstance(v2, list):
                w("  * %s: %s" % (k, ", ".join(("%.2f" % x) if isinstance(x, float) else str(x) for x in v2)))
            else:
                w("  * %s: %.2f" % (k, v2))
    if st:
        w("* The four stems sum to the mix within %.1e (sample value). The SFX model (each cue at its gain and "
          "placement) leaves a residual of %s dB relative to the A3/A4 stems (resampling of the 44.1/96 kHz files)." % (
            st["stems_sum_vs_mix_max_abs_diff"], ", ".join("%s %.1f" % (k, v2) for k, v2 in st["sfx_model_vs_stem_residual_db"].items())))
        w("\n| Cue | Window s | Plan peak | Master at peak | Expected | Measured | Error | Voice peak, same window | Above the voice? |")
        w("|---|---|---|---|---|---|---|---|---|")
        for r_ in (r_ for r_ in st["sfx_cues"] if not r_.get("layer")):
            w("| %s | %.3f-%.3f | %.1f | %+.2f | %.2f | %.2f | %+.2f | %.2f | %s |" % (
                r_["cue"], r_["window_s"][0], r_["window_s"][1], r_["plan_peak_dbfs"], r_["master_db_at_peak"],
                r_["expected_final_peak_dbfs"], r_["measured_peak_dbfs"], r_["error_db"], r_["voice_peak_same_window_dbfs"],
                ("yes (allowed: the final logo hit, no voice)" if r_["cue"].startswith("S19") else "**yes**")
                if r_["above_voice_window"] else "no"))
        leg_ = [r_ for r_ in st["sfx_cues"] if not r_.get("layer")]
        vg_ = st["sfx_cues"][0]["voice_peak_global_dbfs"] if st["sfx_cues"] else float("nan")
        w("\nVoice sample peak over the whole mix: %.2f dBFS. %s" % (vg_, "No S-cue peak is above the voice in its "
          "window except S19 (plan p.38)." if not any(r_["above_voice_window"] for r_ in leg_ if not r_["cue"].startswith(
              "S19")) else "SEE ABOVE: an S-cue peak is above the voice in its window."))
        vc_ = st.get("v05_layers_check")
        if vc_:
            w("\nv05 library layers (%d): rendered sample peak vs the model's (isolated, master included) max error "
              "%.3f dB without the %d dropout-muted ones (%.3f dB with them: their remaining peak sits on a mute ramp, "
              "which the engine draws on its 10 ms gain clock), median %+.3f dB (48 kHz files: no resampling). Every one "
              "is below the voice's global peak (%.2f dBFS): %s. %d of them peak above the voice inside their own short "
              "window (whooshes before a word, ticks in pauses, the CTA's sounds: by design)." % (
                  vc_["layers"], vc_["max_abs_error_db_not_muted"], vc_["muted_layers"], vc_["max_abs_error_db"],
                  vc_["median_error_db"], vg_,
                  "yes" if not any(r_["above_voice_global"] for r_ in st["sfx_cues"] if r_.get("layer")) else "NO",
                  len(vc_["above_voice_window"])))
    if R.get("waveforms"):
        w("\n**Waveforms of the mix** (skill helper, edit clock): " + "; ".join(
            "`%s` (%.2f-%.2f s, markers %s)" % (x_["png"], x_["window_s"][0], x_["window_s"][1], x_["markers_s"])
            for x_ in R["waveforms"]) + ".\n")
        wm = {k: (v if v is not None else float("nan")) for k, v in R.get("waveform_markers_s", {}).items()}
        w("What to look for: (1) the drop: the bed and S09 together on the %.3f s marker ('fun'), the energy held "
          "through the +3 dB lift, easing after the %.3f s marker; (2) the break: S08 at %.3f s, its tail decaying "
          "through MU4's 15f mute (%.3f-%.3f s), the bed back at %.3f s and the B9 voice at %.3f s; (3) the ending: the "
          "bed stopping dead at %.3f s, S18 rising into the logo hit at %.3f s and S19's decay carrying the tail to "
          "the end of the edit (%.3f s).\n" % (
              marks["MU5"], marks["MU5"] + MU5_HOLD_S, wm.get("S08", float("nan")), marks["MU4_start"],
              marks["MU4_end"], marks["MU4_end"], wm.get("B9_voice", float("nan")), marks["MU8"],
              wm.get("S19", float("nan")), float(beat_map["edit_end_s"])))
    w("## Deviations and interpretations\n")
    for line in deviation_notes(clips, ev, marks, beat_map):
        w("* " + line)
    leg_ids = sorted({c.cue for c in clips if not getattr(c, "v05", False)}, key=lambda k: int(k[1:]))
    w("\nChecked by measurement and waveform views only: no listening was possible in this container, so the plan's "
      "'check on phone speakers and on earbuds' is left for a listening pass. S-cues in this edit (%d): %s%s.\n" % (
          len(leg_ids), ", ".join(leg_ids), ("; left out by the lanes' v05 cue files: " + "; ".join(
              decisions.get("skipped", []))) if decisions.get("skipped") else ""))
    w("## Re-run\n")
    w("`python3 tools/build_tesseract_audio.py` (about 1 minute; one export at a time). `--no-stems` skips the stem "
      "checks, `--no-waveforms` the PNGs, `--refresh-cue-defaults` rewrites `.tesseract-work/cue_defaults.json` from "
      "STORYBOARD.md. When a beat builder rewrites `hyperframes/<composition>/cues.json` for v02, the next run uses it "
      "as written (it no longer equals the v01 snapshot, so it is not scaled).")
    (WORK / "AUDIO_NOTES.md").write_text("\n".join(L) + "\n")


def deviation_notes(clips, ev, marks, beat_map):
    """The deviations/interpretations list, with this run's numbers (v01 wording kept where it still applies)."""
    cue = lambda cid: [c for c in clips if c.cue == cid]
    out = []
    s07 = cue("S07")
    if s07 and all(ev.has(k) for k in ("B7.stamp2", "B7.stamp3", "B8.first_black")):
        c = s07[0]
        span = ev.t("B8.first_black") - ev.t("B7.stamp2")
        out.append("C17 S07: it ends exactly on B8's first black frame (%.3f s), %s" % (
            ev.t("B8.first_black"),
            "but the file (%.3f s = %.0ff) is shorter than the %.0ff from the second stamp, so it starts %.0ff after "
            "stamp 2 (%.0ff after stamp 3). Not time-stretched." % (
                c.dur, c.dur * FPS, span * FPS, (c.edit_start - ev.t("B7.stamp2")) * FPS,
                (c.edit_start - ev.t("B7.stamp3")) * FPS) if c.dur < span - 1e-6 else
            "head-trimmed so it starts on the second stamp (%.3f s)." % ev.t("B7.stamp2")))
    if MUSIC:
        out += [
            "C18 music level wording: plan p.35 puts the bed at -22 LUFS 'roughly 14-18 dB below the voice', but -22 is "
            "6 dB below the -16 LUFS voice spec. The absolute levels and the 6-8 dB duck are used, and the measured gaps "
            "are reported above.",
            "C19 no-voice list: no music in the logo tail (MU8), the B14 burst is under the voice in the processed VO, "
            "and the B8 hold is MU4's mute. The bed comes fully up in the B13 title hold.",
            "Music base is -7 dB, not music_plan.json's -8 dB. Measured on the track, -7 dB puts the un-ducked bed at "
            "about -16 LUFS and the ducked full-energy bed at about -22 LUFS (pre-master), as plan p.35 asks."]
    else:
        out.append("v04 note 1: no background music (MU1-MU8 off). Without the bed the master make-up gain is higher; "
                   "every SFX keeps its pre-master level relative to the voice, as calibrated against the plan's peaks.")
    out += [
        "C20 master: there is no limiter. One static make-up gain on every layer, plus limiter-style master gain "
        "automation only where the true peak would pass the ceiling.",
        "C21 voice level: A1 is at unity. The VO is about -16.4 LUFS as a mono track, but Tesseract sends mono at full "
        "level to both channels, so it reads about 3 dB louder on the stereo meter. Track levels are set before the "
        "master stage, as in a DAW.",
    ]
    if cue("S19"):
        out.append("C22 S19 is kept at the cue sheet's -4 dBFS: it is the highest SFX level and the only SFX above the voice.")
    if cue("S03"):
        out.append("S03 keeps sfx_plan.json's reading: the error SOUND (0.11 s into the file) starts 3f before the tear, so "
                   "the file starts 0.21 s before it; the glitch starts on the tear at +12 dB. Plan p.35 can also be read as "
                   "'file 3f before the tear, sound on it' (0.11 s later). Changing that means one field in sfx_plan.json.")
    s01 = cue("S01")
    if s01:
        c = s01[0]
        out.append("S01, S11 and S16 put the plan's peak times (0.33/1.14/0.96 s, CONFLICTS C13) on their events. S01 "
                   "therefore starts %.3f s (%.1ff) before the slam, the plan's '10f' to within %.0f ms." % (
                       c.event_t - c.edit_start, (c.event_t - c.edit_start) * FPS,
                       abs((c.event_t - c.edit_start) - 10 / FPS) * 1000))
    if cue("S13"):
        out.append("S13 is sliced into single keystrokes, one every 2 letters (see the S13 decision above). The plan "
                   "allows this when the file does not sit with the letters.")
    trimmed = [c for c in clips if any("tail trimmed" in n for n in c.notes) and not getattr(c, "v05", False)]
    out.append(("S02/S14: the 0.5-1.3 s slice starts inside the siren, so a 10 ms de-click fade-in comes before the "
               "plan's 6f fade-out." if (cue("S02") or cue("S14")) else "") + ("".join(" %s%s runs %.0f ms past the end of the edit, so it is trimmed at "
                                                "%.3f s with a 4f fade." % (c.cue, c.sub, (c.edit_start + c.file_dur -
                                                                                     c.src_start - float(beat_map["edit_end_s"])) * 1000,
                                                                            float(beat_map["edit_end_s"]))
                                                for c in trimmed)))
    out += [
        "MU1 starts with a 10 ms de-click ramp, and MU4/MU6/MU7/MU8 use 10 ms ramps (the engine's gain resolution). "
        "MU5's +3 dB returns over 0.3 s after its 2 s; MU7's -6 dB returns at the B17 cut over 30 ms.",
        "SFX gains are closed-loop: computed from FFmpeg decodes, then corrected once against Tesseract's own render "
        "(its resampler shaves up to 0.17 dB off some 44.1/96 kHz transients) so every cue's rendered peak is at the "
        "plan's level. S10 (v02) is not calibrated on its own: it keeps S08's corrected gain (same file, same level), "
        "or its own plan level when S08 is not in the edit. The v05 library layers are 48 kHz WAVs: Tesseract plays "
        "them without resampling, exactly as modelled, so they keep their library level without a correction.",
        "The MP3s sit on Tesseract's decode clock. Black Vertigo's source start includes the measured decoder offset, "
        "so the drop lands on 'fun'. The SFX MP3s carry no encoder-delay tag and measured 0 ms.",
    ]
    used = {c.event for c in clips} | {"B8.first_black", "B10.fun", "B15.label", "B16.rewind", "B16.rewind_end"}
    fb = sorted(k for k in used if ev.event_source.get(k, "").startswith("STORYBOARD"))
    out.append("Events come from the beats' cues.json files. A v05 file is read as written (no fallback for the S-cues; "
               "the music marks still fall back); a legacy file is moved from v04 to v05 frames (v01-timed ones are "
               "scaled to the v04 beat first), and an event a legacy beat does not list falls back to the STORYBOARD.md "
               "cue scaled and moved the same way%s. MU7's end is B16's `rewind_end` (%s)." % (
                   (" (this run: " + ", ".join(fb) + ")") if fb else "", ev.event_source.get("B16.rewind_end", "?")))
    return out


if __name__ == "__main__":
    main()
