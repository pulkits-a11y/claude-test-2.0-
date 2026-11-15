#!/usr/bin/env python3
"""Build the AUDIO half of the RC_GTA-Origin Tesseract project, deterministically.

Golden rule: 00_Brief/GTA_VI_Edit_Plan.pdf (Music plan p.32-35, SFX plan p.35-38, Audio mix
and export settings p.38). Inputs (all established earlier, read-only here):

  01_VO/VO_processed_108.wav      locked voiceover (mono, 48 kHz, already through the plan's chain)
  01_VO/VO_words_108.json          word timings -> ducking phrase spans
  timing/beat_map.json             beat clock (B1-B17 start frames, vo_end_s, edit_end_s)
  02_Music/music_plan.json         Black Vertigo cut points MU1-MU8, offset 139.68 s, levels
  03_SFX/sfx_plan.json             S01-S19 cue rules (event, align, offsets, trims, fades, peaks)
  03_SFX/sfx_analysis.json         measured file data
  hyperframes/<comp>/cues.json     event frames per beat when a beat builder has written them,
                                   else timing/cue_defaults.json (made from STORYBOARD.md "Cues")

Every run:
  1. deletes and recreates .tesseract-work/audio.tsrct (one composition, 1920x1080, 82.4 s, #0A0A0A)
     with four groups "A1 Voiceover", "A2 Music", "A3 SFX hits & impacts",
     "A4 Risers, whooshes & textures" (CONFLICTS.md C6); layer ids >= 9000, asset ids "aud-*";
  2. prepares the FFmpeg derivatives the plan needs (MU6 low-pass 800 Hz excerpt, S02/S14
     300 Hz high-pass) in 02_Music/derived and 03_SFX/derived, recipes beside them;
  3. exports the audio mix to .tesseract-work/checks/mix.wav (+ stems unless --no-stems),
     measures it and writes .tesseract-work/checks/audio_report.json and
     .tesseract-work/AUDIO_NOTES.md.

Usage:  python3 tools/build_tesseract_audio.py [--no-stems] [--no-waveforms] [--refresh-cue-defaults]
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

VO_FILE = ROOT / "01_VO/VO_processed_108.wav"
WORDS_JSON = ROOT / "01_VO/VO_words_108.json"
BEAT_MAP = ROOT / "timing/beat_map.json"
CUE_DEFAULTS = ROOT / "timing/cue_defaults.json"
STORYBOARD = ROOT / "STORYBOARD.md"
MUSIC_PLAN = ROOT / "02_Music/music_plan.json"
SFX_PLAN = ROOT / "03_SFX/sfx_plan.json"
SFX_ANALYSIS = ROOT / "03_SFX/sfx_analysis.json"
SFX_DIR = ROOT / "03_SFX"
MUSIC_DERIVED = ROOT / "02_Music/derived"
SFX_DERIVED = ROOT / "03_SFX/derived"

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

# Layer / group ids (>= 9000, picture script uses lower ids)
GID = {"A1": 9001, "A2": 9002, "A3": 9003, "A4": 9004}
GNAME = {"A1": "A1 Voiceover", "A2": "A2 Music", "A3": "A3 SFX hits & impacts",
         "A4": "A4 Risers, whooshes & textures"}
VO_LAYER_ID = 9101
MUSIC_LAYER_ID = 9201
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


def probe(path: Path) -> dict:
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


class Events:
    """Event frames per beat: hyperframes/<comp>/cues.json if present, else timing/cue_defaults.json."""

    def __init__(self, beat_map: dict, refresh_defaults: bool):
        self.beats = {b["id"]: b for b in beat_map["beats"]}
        sb = parse_storyboard_cues(STORYBOARD.read_text())
        if refresh_defaults or not CUE_DEFAULTS.exists():
            doc = {"_source": "STORYBOARD.md '**Cues**' lines (beat-relative frames, f0 = the beat's first "
                              "word). Fallback used by tools/build_tesseract_audio.py only for beats whose "
                              "hyperframes/<composition>/cues.json does not exist yet. '~29'/'~48' are taken "
                              "as 29/48; a range a..b is stored as name=a, name_end=b.",
                   **{b: sb.get(b, {}) for b in self.beats}}
            CUE_DEFAULTS.write_text(json.dumps(doc, indent=1) + "\n")
            log("wrote", CUE_DEFAULTS.relative_to(ROOT))
        self.defaults = load_json(CUE_DEFAULTS)
        drift = {b: (sb.get(b, {}), self.defaults.get(b, {})) for b in self.beats
                 if sb.get(b, {}) != self.defaults.get(b, {})}
        if drift:
            log("WARNING: timing/cue_defaults.json differs from STORYBOARD.md (use --refresh-cue-defaults):", drift)
        self.source = {}
        self.table = {}
        for bid, b in self.beats.items():
            comp = b["composition"]["id"]
            cj = ROOT / "hyperframes" / comp / "cues.json"
            if cj.exists():
                self.table[bid] = {k: int(v) for k, v in load_json(cj).get("events", {}).items()}
                self.source[bid] = str(cj.relative_to(ROOT))
            else:
                self.table[bid] = {k: int(v) for k, v in self.defaults.get(bid, {}).items()}
                self.source[bid] = "timing/cue_defaults.json"

    def beat_start_frame(self, beat: str) -> int:
        return int(self.beats[beat]["start_frame"])

    def frame(self, ref: str) -> int:
        """'B8.first_black' -> edit frame; 'B15.start' -> beat start frame."""
        beat, name = ref.split(".", 1)
        if name == "start":
            return self.beat_start_frame(beat)
        if name not in self.table[beat]:
            raise KeyError("event %s not found (source %s)" % (ref, self.source[beat]))
        return self.beat_start_frame(beat) + self.table[beat][name]

    def t(self, ref: str) -> float:
        return frames_to_s(self.frame(ref))

    def beat_frame(self, ref: str) -> int:
        beat, name = ref.split(".", 1)
        return 0 if name == "start" else self.table[beat][name]


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


def music_envelopes(ev: Events, beat_map: dict, spans):
    t_end = float(beat_map["vo_end_s"])                       # MU8: hard stop at the end of "now?"
    tt = np.arange(0, ms(t_end) + 1) / 1000.0                  # 1 ms grid on the edit clock
    marks = {
        "MU1": 0.0,
        "MU4_start": ev.t("B8.first_black"),
        "MU4_end": ev.t("B8.first_black") + frames_to_s(MU4_FRAMES),
        "MU5": ev.t("B10.fun"),
        "MU6_start": ev.t("B15.start"),
        "MU6_end": ev.t("B15.label"),
        "MU7_start": ev.t("B16.rewind"),
        "MU7_end": ev.t("B16.rewind_end"),
        "MU7_return": ev.t("B17.start"),
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
        group = cue["group"]
        if cid == "S13":
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
                if cue.get("from_event"):
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
                     rel_gain_db=float(L.get("extra_gain_db", 0.0)))
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


def clip_signal(c: Clip, lag_s: float = 0.0):
    """Gainless signal of a clip as Tesseract will play it (fades amplitude-linear)."""
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
    return seg * env[:, None]


def compute_sfx_gains(clips):
    """Linear volume per clip so the cue's sample peak hits the plan's peak level
    (combined peak for layered cues, mixed here at their real offsets and relative gains)."""
    groups = {}
    for c in clips:
        key = c.cue if c.combined else (c.cue, c.sub)
        groups.setdefault(key, []).append(c)
    for key, cs in groups.items():
        t0 = min(c.edit_start for c in cs)
        t1 = max(c.end for c in cs)
        buf = np.zeros((int(math.ceil((t1 - t0) * SR)) + 2, 2))
        for c in cs:
            s = clip_signal(c) * lin(c.rel_gain_db)
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
    return groups


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


