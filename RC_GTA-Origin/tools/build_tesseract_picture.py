#!/usr/bin/env python3
"""Build the PICTURE half of the RC_GTA-Origin Tesseract project, deterministically.

Golden rule: 00_Brief/GTA_VI_Edit_Plan.pdf (Style kit > Grade and texture p.10, Screen types L1/L2/L10
p.13-15, Transitions X1/X2/X8 p.15-16, Toolchain + Handoff rules p.3-4). How each item is built, the
measurements behind the numbers and the deviations: .tesseract-work/PICTURE_NOTES.md.

Inputs (read at run time, whatever exists then):
  timing/beat_map.json                          beat clock (start/end frames, composition ids, edit_end_s)
  05_GFX/renders/<composition>.mov              HyperFrames beat renders (ProRes 4444 + alpha, beat + 12f)
  hyperframes/<composition>/tesseract_shots.json Tesseract-owned footage shots (PRODUCTION_SPEC.md schema)
  04_Broll/_originals/*/<RID>__*, 04_Broll/_placeholders/<RID>.mp4   footage (fallback chain for old entries)

Every run deletes and recreates .tesseract-work/picture.tsrct: one composition `main`, 1920x1080, duration
= beat_map edit_end_s, background #0A0A0A, layer ids 1..8999, asset ids "pic-*". Top to bottom:
  1. "Grain (whole edit)"        Adjustment, Grain effect (seed animated per frame), whole edit
  2. "HyperFrames beat renders"  Group, one Video per existing MOV: MOV local frame 6 on the beat's start
                                 frame, visible over [beat start, beat end) only
  3. "Bxx footage"               one Group per beat with Tesseract shots; per shot a Group holding the L2 bars,
                                 the shot's look/whip Adjustments and a framing Group (push-in, X2 drift)
                                 around the Video (+ the L1 mask guide)
Footage is never imported raw: each shot's window (+ margins) is cut with FFmpeg from the original to an
H.264 1080p-fit 30 fps CFR working copy in .tesseract-work/media/ (crop applied, pixel aspect corrected,
never stretched, speed/reverse baked in, no B-frames so the decode clock is exact). Copies are cached by
a hash of their recipe and re-used; unused copies are deleted.

Usage:  python3 tools/build_tesseract_picture.py [--no-cache]
Writes: .tesseract-work/picture.tsrct, picture.editable.json, checks/picture_report.json
Test only: --shots-dir DIR reads DIR/<composition>/tesseract_shots.json first (falls back to hyperframes/),
           --output X.tsrct writes the document (and X.editable.json, X.report.json) there instead.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".tesseract-work"
MEDIA = WORK / "media"
CHECKS = WORK / "checks"
PROJECT = WORK / "picture.tsrct"
JSON_OUT = WORK / "picture.editable.json"
REPORT = CHECKS / "picture_report.json"
TSRCT = Path("/root/.local/share/Tesseract/bin/tsrct")
BEAT_MAP = ROOT / "timing/beat_map.json"
RENDERS = ROOT / "05_GFX/renders"
HF_DIR = ROOT / "hyperframes"
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")

FPS = 30
W, H = 1920, 1080
HANDLE_F = 6                       # HF compositions start 6f before the beat (PRODUCTION_SPEC handoff)
INK = [10 / 255, 10 / 255, 10 / 255, 1.0]   # #0A0A0A ink black (bars, background)

# ---- look constants (PICTURE_NOTES.md has the measurements behind each value) --------------------------
GRAIN_EDIT = {"amount": 1.0, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0}   # p1-p99 spread 3.7% of full scale at any level
GRAIN_ARCHIVAL = {"amount": 0.6, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0}  # extra on archival shots: ~4.3% combined
VIGNETTE_LIGHT = {"amount": 0.25, "radius": 1.0, "feather": 0.8}   # corners about -17%, edge centres -7%
L1_SCALE = 105.0                   # plan: footage at 105%
L1_BLUR_PX = 12                    # plan: edges blurred 12 px
L1_SHARP_FRAC = 0.70               # plan: centre 70% stays sharp
L1_FEATHER = (192, 108)            # mask feather (x, y) px: the sharp->blurred ramp outside the 70% box
PUSH_DEFAULT = (100.0, 104.0)      # plan rule 7: every held shot pushes in 100% -> 104%
HELD_MIN_F = 12                    # shots shorter than this get no default push-in (burst clips)
EASE_OUT = {"type": "cubicBezier", "x1": 0.2, "y1": 0.0, "x2": 0.0, "y2": 1.0}   # plan "ease out"
EASE_IN = {"type": "cubicBezier", "x1": 0.55, "y1": 0.0, "x2": 1.0, "y2": 0.45}
LINEAR = {"type": "linear"}
HOLD = {"type": "hold"}
X2_FRAMES = 20                     # plan X2: slides 40-80 px sideways over 20f, ease out
X2_DEFAULT_PX = 60
X8_DEFAULT = {"frames": 6, "blur_px": 80, "dir": "left"}
X8_TRAVEL = 0.25                   # whip travel per half, fraction of frame width (motion tile offset)
BARS_DEFAULT = {"bars_px": 138, "slide_in_f": 8}
MARGIN_F = 15                      # working-copy handle on each side of a shot (trim room)
WC_RECIPE = "wc-v3 libx264 crf14 bf0 g30 bt709 lanczos"

PG0 = {"temperature": 0.0, "tint": 0.0, "exposure": 0.0, "contrast": 0.0, "highlights": 0.0, "shadows": 0.0,
       "whites": 0.0, "blacks": 0.0, "saturation": 0.0, "vibrance": 0.0}
GRADES = {   # primaryGrade deltas per shot grade (plan p.10)
    "archival": {"temperature": 0.08, "blacks": 0.12, "saturation": -0.20},   # + vignette + grain (look adj)
    "game": {"contrast": 0.18},
    "b9-sat60": {"contrast": 0.18, "saturation": -0.40},
    "b10-pop": {"contrast": 0.18, "saturation": 0.10},                          # +10% for 1 s, then 0
    "none": None,
}
B10_POP_MS = 1000


def log(*a):
    print(*a, flush=True)


def run(cmd, check=True):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit("command failed (%d): %s\n%s\n%s" % (r.returncode, " ".join(map(str, cmd)), r.stdout[-2000:],
                                                             r.stderr[-4000:]))
    return r


def tsrct(*args):
    return run([TSRCT] + list(args))


def ms_floor(frame: int) -> int:
    """Composition frame -> integer ms at or before the frame's exact time (n*1000/30)."""
    return (int(frame) * 1000) // FPS


def frames_ms(n: float) -> int:
    return int(round(n * 1000 / FPS))


def rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s).strip("-")


# --------------------------------------------------------------------------------------------
# Ids
# --------------------------------------------------------------------------------------------
class Ids:
    def __init__(self):
        self.layer = 0
        self.item = 50000            # effects and masks (composition-unique, away from all layer ids)

    def L(self):
        self.layer += 1
        if self.layer >= 9000:
            raise SystemExit("picture layer ids exhausted (must stay below 9000)")
        return self.layer

    def E(self):
        self.item += 1
        return self.item


# --------------------------------------------------------------------------------------------
# Layer JSON (document schema: JBFXLayer*Model; layers[0] is topmost)
# --------------------------------------------------------------------------------------------
def tr(x=0.0, y=0.0, s=100.0, ax=0.0, ay=0.0, o=100.0, sx=None, sy=None):
    return {"anchorPoint": [ax, ay], "position": [x, y], "scale": [sx if sx is not None else s, sy if sy is not None else s],
            "rotation": 0, "opacity": o}


def playback(start, dur, offset=0):
    return {"type": "windowed", "inputRange": {"start": int(start), "duration": int(dur)},
            "mapping": {"type": "linear", "input": {"start": 0, "duration": int(dur)},
                        "output": {"start": 0, "duration": int(dur)}},
            "inputOffsetMs": int(offset)}


def group_json(gid, name, start, dur, layers, transform=None, effects=None, desc=None):
    """Identity clock (inputOffsetMs 0): children windows and the group's own keyframes use composition ms."""
    g = {"type": "Group", "id": gid, "name": name, "blendMode": "normal", "playback": playback(start, dur),
         "transform": transform or tr(), "layers": layers}
    if effects:
        g["effects"] = effects
    if desc:
        g["description"] = desc
    return g


def video_json(lid, name, asset, intrinsic, start, dur, offset, rect, fit, transform, effects=None, masks=None,
               desc=None):
    """Video window [start, start+dur) on the parent clock; content time = parent time + offset."""
    v = {"type": "Video", "id": lid, "name": name, "blendMode": "normal",
         "playback": playback(start, dur, offset),
         "sourceRange": {"start": int(start + offset), "duration": int(dur)},
         "sourceIntrinsicDuration": int(intrinsic), "transform": transform,
         "source": {"assetId": asset, "fit": fit,
                    "sourceRect": {"x": rect[0], "y": rect[1], "width": rect[2], "height": rect[3]}}}
    if effects:
        v["effects"] = effects
    if masks:
        v["masks"] = masks
    if desc:
        v["description"] = desc
    return v


def rect_json(lid, name, start, dur, size, pos, color, desc=None):
    r = {"type": "Rect", "id": lid, "name": name, "blendMode": "normal", "activeRange": {"start": int(start), "duration": int(dur)},
         "transform": tr(pos[0], pos[1]), "rect": {"size": [size[0], size[1]], "fillColor": color}}
    if desc:
        r["description"] = desc
    return r


def adjustment_json(lid, name, start, dur, effects, desc=None):
    a = {"type": "Adjustment", "id": lid, "name": name, "blendMode": "normal",
         "activeRange": {"start": int(start), "duration": int(dur)}, "transform": tr(), "effects": effects}
    if desc:
        a["description"] = desc
    return a


def fx(eid, effect, mask_refs=None):
    e = {"id": eid, "effect": effect}
    if mask_refs is not None:
        e["compositingOptions"] = {"effectOpacity": 1.0, "maskReferences": list(mask_refs)}
    return e


def primary_grade(delta):
    d = dict(PG0)
    d.update(delta)
    return dict({"type": "primaryGrade", "semanticVersion": 1}, **d)


class Dyn:
    """composition.dynamics entries (keyframes / jsScript), ids composition-unique ("pic-...")."""

    def __init__(self):
        self.entries = []

    def keys(self, target, points, tag):
        kfs = []
        for i, (t, v, easing) in enumerate(points):
            kfs.append({"id": "pic-%s-%02d" % (tag, i), "layerTime": int(t),
                        "value": {"type": "float", "value": round(float(v), 6)}, "easing": easing})
        self.entries.append({"target": target, "animator": {"type": "keyframes", "enabled": True, "keyframes": kfs}})

    def layer(self, lid, prop, points):
        self.keys({"kind": "layer", "layerId": lid, "propertyType": prop}, points, "%d-%s" % (lid, prop))

    def effect(self, eid, param, points):
        self.keys({"kind": "effectProperty", "effectId": eid, "paramName": param}, points, "fx%d-%s" % (eid, param))

    def script(self, eid, param, code):
        self.entries.append({"target": {"kind": "effectProperty", "effectId": eid, "paramName": param},
                             "animator": {"type": "jsScript", "layerTimeJsCode": code}})


# --------------------------------------------------------------------------------------------
# Media
# --------------------------------------------------------------------------------------------
def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,sample_aspect_ratio,r_frame_rate,nb_frames,color_space,duration:format=duration",
             "-of", "json", path])
    j = json.loads(r.stdout)
    s = j["streams"][0]
    sar = s.get("sample_aspect_ratio") or "1:1"
    try:
        n, d = (int(x) for x in sar.split(":"))
        sar_f = Fraction(n, d) if n > 0 and d > 0 else Fraction(1)
    except ValueError:
        sar_f = Fraction(1)
    dur = float(j.get("format", {}).get("duration") or s.get("duration") or 0)
    return {"w": int(s["width"]), "h": int(s["height"]), "sar": sar_f, "dur": dur,
            "fps": s.get("r_frame_rate"), "nb_frames": s.get("nb_frames"), "color_space": s.get("color_space")}


def resolve_source(shot: dict):
    """'source' (PRODUCTION_SPEC) -> original by R-ID -> labelled stand-in."""
    notes = []
    if shot.get("source"):
        p = ROOT / shot["source"]
        if p.exists():
            return p, "source", notes
        notes.append("source %s missing" % shot["source"])
    rid = shot.get("rid") or ""
    hits = sorted(h for h in glob.glob(str(ROOT / "04_Broll/_originals" / "*" / (glob.escape(rid) + "__*")))
                  if h.lower().endswith(VIDEO_EXT))
    if rid and hits:
        return Path(hits[0]), "original-by-rid", notes
    ph = ROOT / "04_Broll/_placeholders" / ("%s.mp4" % rid)
    if rid and ph.exists():
        return ph, "placeholder", notes
    return None, "missing", notes


def even(x: float) -> int:
    return max(2, int(round(x / 2.0)) * 2)


def parse_crop(crop):
    if not crop:
        return None
    try:
        w, h, x, y = (int(round(float(v))) for v in str(crop).split(":"))
        return w, h, x, y
    except ValueError:
        raise SystemExit("bad crop %r (expected w:h:x:y)" % crop)


def working_copy(shot: dict, src: Path, sp: dict, beat_id: str, use_cache: bool, warnings: list):
    """Cut [shot - margin, shot + margin] of the source to an H.264 30 fps CFR copy; returns metadata."""
    sf, ef = shot["_start_f"], shot["_end_f"]
    n_shot = ef - sf
    speed = float(shot.get("speed") or 1.0)
    if speed <= 0:
        raise SystemExit("%s: speed must be > 0" % shot["id"])
    rev = bool(shot.get("reverse"))
    t_in = float(shot.get("source_in_s") or 0.0)
    span = n_shot / FPS * speed                       # source seconds the shot consumes
    mh = mt = MARGIN_F
    dur = sp["dur"]
    if dur <= 0:
        raise SystemExit("cannot read the duration of %s" % src)
    # keep the shot itself inside the file (stand-ins are 12 s long)
    if not rev and t_in + span > dur - 0.05:
        new = max(0.0, dur - 0.05 - span)
        warnings.append("%s: source_in_s %.3f + %.3f s runs past the end of %s (%.3f s); moved to %.3f" % (
            shot["id"], t_in, span, src.name, dur, new))
        t_in = new
    if rev and t_in - span < 0:
        new = min(dur - 0.05, span)
        warnings.append("%s: reversed shot needs %.3f s before source_in_s %.3f; moved to %.3f" % (shot["id"], span, t_in, new))
        t_in = new
    # margins (frames of edit time), clipped to the file
    if not rev:
        mh = max(0, min(mh, int(math.floor(t_in / speed * FPS))))
        mt = max(0, min(mt, int(math.floor((dur - 0.05 - t_in - span) / speed * FPS))))
        ss = t_in - mh / FPS * speed
    else:
        mh = max(0, min(mh, int(math.floor((dur - 0.05 - t_in) / speed * FPS))))
        mt = max(0, min(mt, int(math.floor((t_in - span) / speed * FPS))))
        ss = t_in - (n_shot + mt) / FPS * speed
    n_total = mh + n_shot + mt
    t_len = (n_total + 2) / FPS * speed               # 2 spare frames, capped by -frames:v
    ss = max(0.0, ss)

    crop = parse_crop(shot.get("crop"))
    cw, ch = (crop[0], crop[1]) if crop else (sp["w"], sp["h"])
    disp_aspect = float(cw * sp["sar"]) / ch
    if abs(disp_aspect / (W / H) - 1) <= 0.01:
        ow, oh = W, H
    elif disp_aspect < W / H:
        ow, oh = even(H * disp_aspect), H
    else:
        ow, oh = W, even(W / disp_aspect)
    cs = (sp.get("color_space") or "").lower()
    in_matrix = {"bt709": "bt709", "smpte170m": "bt601", "bt470bg": "bt601", "bt2020nc": "bt2020"}.get(
        cs, "bt709" if sp["h"] >= 720 else "bt601")
    vf = []
    if crop:
        vf.append("crop=%d:%d:%d:%d" % crop)
    vf.append("scale=%d:%d:flags=lanczos:in_color_matrix=%s:out_color_matrix=bt709:out_range=tv" % (ow, oh, in_matrix))
    vf.append("setsar=1")
    if abs(speed - 1.0) > 1e-9:
        vf.append("setpts=(PTS-STARTPTS)/%.6f" % speed)
    vf.append("fps=%d" % FPS)
    if rev:
        vf.append("reverse")
    vf.append("format=yuv420p")
    st = src.stat()
    key = json.dumps({"src": rel(src), "size": st.st_size, "mtime": st.st_mtime_ns, "ss": round(ss, 4),
                      "len": round(t_len, 4), "n": n_total, "vf": vf, "recipe": WC_RECIPE}, sort_keys=True)
    h = hashlib.sha1(key.encode()).hexdigest()[:10]
    out = MEDIA / ("%s__%s__%s.mp4" % (beat_id, safe_id(shot["id"]), h))
    if not (use_cache and out.exists()):
        tmp = out.with_suffix(".tmp.mp4")
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", "%.4f" % ss, "-i", src, "-t", "%.4f" % t_len,
             "-an", "-sn", "-dn", "-vf", ",".join(vf), "-frames:v", str(n_total),
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-bf", "0", "-g", "30",
             "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
             "-color_range", "tv", "-movflags", "+faststart", tmp])
        tmp.replace(out)
    got = probe(out)
    n_got = int(got["nb_frames"] or round(got["dur"] * FPS))
    if n_got < mh + n_shot:
        raise SystemExit("%s: working copy has %d frames, the shot needs %d (source too short?)" % (shot["id"], n_got, mh + n_shot))
    if n_got < n_total:
        warnings.append("%s: working copy has %d of %d frames (tail margin shortened)" % (shot["id"], n_got, n_total))
    return {"path": out, "w": got["w"], "h": got["h"], "frames": n_got, "head_f": mh, "tail_f": max(0, n_got - mh - n_shot),
            "ss": ss, "t_in": t_in, "speed": speed, "reverse": rev, "crop": shot.get("crop"),
            "aspect": disp_aspect, "recipe": vf, "hash": h}


# --------------------------------------------------------------------------------------------
# Shots -> layers
# --------------------------------------------------------------------------------------------
def load_shots(beat: dict, warnings: list, shots_dir=None):
    comp = beat["composition"]["id"]
    p = HF_DIR / comp / "tesseract_shots.json"
    if shots_dir and (Path(shots_dir) / comp / "tesseract_shots.json").exists():
        p = Path(shots_dir) / comp / "tesseract_shots.json"
    if not p.exists():
        return [], None
    try:
        j = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        warnings.append("%s: unreadable (%s); beat skipped" % (rel(p), e))
        return [], p
    shots = []
    for i, s in enumerate(j.get("shots") or []):
        s = dict(s)
        s.setdefault("id", "%s-shot%02d" % (beat["id"], i + 1))
        try:
            sf, ef = int(s["start_f"]), int(s["end_f"])
        except (KeyError, TypeError, ValueError):
            warnings.append("%s %s: start_f/end_f missing; skipped" % (beat["id"], s["id"]))
            continue
        if ef <= sf:
            warnings.append("%s %s: end_f <= start_f; skipped" % (beat["id"], s["id"]))
            continue
        s["_beat_f"] = (sf, ef)
        s["_start_f"] = beat["start_frame"] + sf
        s["_end_f"] = beat["start_frame"] + ef
        s["screen"] = (s.get("screen") or "full").strip()
        s["grade"] = (s.get("grade") or "none").strip()
        shots.append(s)
    return shots, p


def bars_entering(shot, all_shots):
    """Bars slide in when entering the cinematic moment: not when an L2 shot ends exactly where this one starts."""
    for o in all_shots:
        if o is not shot and o["screen"] == "L2" and o["_end_f"] == shot["_start_f"]:
            return False
    return True


def x8_parts(shot, beat_start):
    """[(part, start_f, end_f, info)] of X8 whip halves on this shot (composition frames)."""
    out = []
    x8 = dict(X8_DEFAULT)
    x8.update(shot.get("x8") or {})
    sf, ef = shot["_start_f"], shot["_end_f"]
    half = int(x8.get("frames", 6)) // 2
    mid = beat_start + int(x8["mid_f"]) if "mid_f" in x8 else None
    if (shot.get("exit") or "").upper() == "X8":
        a = beat_start + int(x8["start_f"]) if "start_f" in x8 else (mid - half if mid is not None else ef - half)
        b = mid if mid is not None else ef
        a, b = max(a, sf), min(b, ef)
        if b > a:
            out.append(("out", a, b, x8))
    if (shot.get("enter") or "").upper() == "X8":
        a = mid if mid is not None else sf
        b = beat_start + int(x8["end_f"]) if "end_f" in x8 else (a + half)
        a, b = max(a, sf), min(b, ef)
        if b > a:
            out.append(("in", a, b, x8))
    return out


def build_shot(shot, beat, wc, asset, intrinsic, ids: Ids, dyn: Dyn, all_shots, notes):
    bid = "B%02d" % int(beat["id"][1:])
    screen, grade = shot["screen"], shot["grade"]
    if grade not in GRADES:
        notes.append("%s: unknown grade %r -> none" % (shot["id"], grade))
        grade = "none"
    sf, ef = shot["_start_f"], shot["_end_f"]
    start, end = ms_floor(sf), ms_floor(ef)
    dur = end - start
    rid = shot.get("rid") or "?"
    label = "%s %s %s" % (bid, rid, screen)
    narrow = wc["aspect"] < (W / H) * 0.99
    wide = wc["aspect"] > (W / H) * 1.01

    # --- picture rectangle and fit (never stretch) ---------------------------------------------------
    if screen == "L2":
        lb = dict(BARS_DEFAULT)
        lb.update(shot.get("letterbox") or {})
        bars = int(lb["bars_px"])
        if narrow:   # 4:3 archival stays inside the band (fit the band height, ink pillars)
            pic = (0, bars, W, H - 2 * bars)
            fit = "contain"
        else:        # 16:9 (or wider) fills the band width; the bars cover the rest
            pic = (0, 0, W, H) if not wide else (0, bars, W, H - 2 * bars)
            fit = "cover"
    else:
        lb, bars = None, 0
        pic = (0, 0, W, H)
        fit = "contain" if narrow else "cover"
    base = L1_SCALE if screen == "L1" else 100.0

    # --- X2 drift: needs overscan so the slide never uncovers the frame edge --------------------------
    x2 = (shot.get("enter") or "").upper() == "X2"
    drift = 0
    if x2:
        drift = int(shot.get("x2_drift_px") or X2_DEFAULT_PX)
        if not 40 <= drift <= 80:
            notes.append("%s: x2_drift_px %d outside the plan's 40-80 px" % (shot["id"], drift))
        covers_width = fit == "cover" or (pic[2] / pic[3]) <= wc["aspect"]
        if covers_width:
            base = max(base, 100.0 * (1 + drift / (W / 2.0)))
    # --- framing (push-in) ----------------------------------------------------------------------------
    fr = shot.get("framing")
    if isinstance(fr, dict) and ("scale_from" in fr or "scale_to" in fr):
        s0, s1 = float(fr.get("scale_from", 100)), float(fr.get("scale_to", fr.get("scale_from", 100)))
        anchor = fr.get("anchor", "center")
    elif screen == "L10" or (ef - sf) < HELD_MIN_F:
        s0 = s1 = 100.0
        anchor = "center"
    else:
        s0, s1 = PUSH_DEFAULT
        anchor = "center"
    ax, ay = (W / 2.0, H / 2.0) if not isinstance(anchor, (list, tuple)) else (float(anchor[0]), float(anchor[1]))

    # --- the Video (+ L1 mask guide) inside the framing group -----------------------------------------
    offset = -(((sf - wc["head_f"]) * 1000) // FPS)         # content ms = parent ms + offset (exact frame pick)
    vid_id = ids.L()
    effects, masks, inner = [], [], []
    g = GRADES[grade]
    pg_id = None
    if g:
        pg_id = ids.E()
        effects.append(fx(pg_id, primary_grade(g)))
    if screen == "L1":
        guide_id, mask_id, blur_id = ids.L(), ids.E(), ids.E()
        px, py, pw, ph = pic
        if fit == "contain":     # guide follows the visible picture, not the canvas
            vw = min(pw, ph * wc["aspect"])
            vh = vw / wc["aspect"]
            px, py, pw, ph = px + (pw - vw) / 2, py + (ph - vh) / 2, vw, vh
        gw, gh = pw * L1_SHARP_FRAC + L1_FEATHER[0], ph * L1_SHARP_FRAC + L1_FEATHER[1]
        gx, gy = px + (pw - gw) / 2, py + (ph - gh) / 2
        inner.append(rect_json(guide_id, "%s soft-edge mask guide" % label, start, dur, (round(gw, 2), round(gh, 2)),
                               (round(gx, 2), round(gy, 2)), [1, 1, 1, 1],
                               desc="L1 mask geometry (consumed by the Video's mask, not drawn): centre 70% of the "
                                    "picture grown by half the feather"))
        masks.append({"id": mask_id, "layer": guide_id, "mode": "none", "inverted": True,
                      "feather": [float(L1_FEATHER[0]), float(L1_FEATHER[1])], "opacity": 1.0, "expansion": 0.0})
        effects.append(fx(blur_id, {"type": "gaussianBlur", "blurriness": float(L1_BLUR_PX), "repeatEdgePixels": True},
                          mask_refs=[mask_id]))
    vtr = tr(W / 2.0, H / 2.0, base, W / 2.0, H / 2.0)
    src_note = "%s @ %.3f s%s%s" % (shot["_src_rel"], wc["t_in"], " x%.2f" % wc["speed"] if wc["speed"] != 1 else "",
                                    " reversed" if wc["reverse"] else "")
    inner.append(video_json(vid_id, "%s video (%s)" % (label, shot["id"]), asset, intrinsic, start, dur, offset,
                            pic, fit, vtr, effects=effects, masks=masks or None,
                            desc="%s; working copy %s (%dx%d, head %df)" % (src_note, wc["path"].name, wc["w"], wc["h"],
                                                                            wc["head_f"])))
    if grade == "b10-pop" and pg_id:
        t0 = start + offset
        dyn.effect(pg_id, "saturation", [(t0, GRADES["b10-pop"]["saturation"], LINEAR), (t0 + B10_POP_MS, 0.0, HOLD)])

    fid = ids.L()
    framing = group_json(fid, "%s framing" % label, start, dur, inner, transform=tr(ax, ay, s0, ax, ay),
                         desc="push-in %.0f%% -> %.0f%% across the shot%s" % (s0, s1, "; X2 drift %d px %s over %df" % (
                             drift, shot.get("x2_dir") or "left", X2_FRAMES) if x2 else ""))
    if s1 != s0:
        for p in ("scaleX", "scaleY"):
            dyn.layer(fid, p, [(start, s0, LINEAR), (end, s1, LINEAR)])
    if x2:
        sign = 1 if (shot.get("x2_dir") or "left").lower() == "left" else -1   # 'left' = slides leftwards
        d_ms = min(frames_ms(X2_FRAMES), dur)
        dyn.layer(fid, "positionX", [(start, ax + sign * drift, LINEAR), (start + d_ms, ax, EASE_OUT)])

    # --- shot-level adjustments: whip (lowest), then the look (vignette/grain) -----------------------
    shot_layers = []
    look = []
    if screen == "L1" or grade == "archival":
        look.append(fx(ids.E(), dict({"type": "vignette"}, **VIGNETTE_LIGHT)))
    if grade == "archival":
        gid = ids.E()
        look.append(fx(gid, dict({"type": "grain", "seed": 7.0}, **GRAIN_ARCHIVAL)))
        dyn.script(gid, "seed", "return Math.round(input.time.seconds * 30) * 7 + %d;" % (vid_id % 97 + 11))
    whips = []
    for part, a, b, x8 in x8_parts(shot, beat["start_frame"]):
        wa, wb = ms_floor(a), ms_floor(b)
        wd = wb - wa
        aid, mt_id, db_id = ids.L(), ids.E(), ids.E()
        sgn = -1 if str(x8.get("dir", "left")).lower() == "left" else 1   # content moves this way
        blur = float(x8.get("blur_px", 80))
        if part == "out":
            mt_keys = [(0, 0.5, LINEAR), (wd, 0.5 + sgn * X8_TRAVEL, EASE_IN)]
            db_keys = [(0, 0.0, LINEAR), (wd, blur, EASE_IN)]
        else:
            mt_keys = [(0, 0.5 - sgn * X8_TRAVEL, LINEAR), (wd, 0.5, EASE_OUT)]
            db_keys = [(0, blur, LINEAR), (wd, 0.0, EASE_OUT)]
        whips.append(adjustment_json(aid, "%s X8 whip %s" % (label, part), wa, wd, [
            fx(mt_id, {"type": "motionTile", "tileCenterX": 0.5, "tileCenterY": 0.5, "tileWidth": 100.0,
                       "tileHeight": 100.0, "outputWidth": 100.0, "outputHeight": 100.0, "phase": 0.0,
                       "mirrorEdges": True}),
            fx(db_id, {"type": "directionalBlur", "direction": 90.0, "blurLength": 0.0})],
            desc="X8 whip %s half: horizontal move %.0f px (mirrored motion tile) with a %.0f px directional blur" % (
                part, X8_TRAVEL * W, blur)))
        dyn.effect(mt_id, "tileCenterX", mt_keys)
        dyn.effect(db_id, "blurLength", db_keys)
    if bars:
        enter = bars_entering(shot, all_shots)
        slide_ms = min(frames_ms(int(lb.get("slide_in_f", 8))), dur) if enter else 0
        top_id, bot_id = ids.L(), ids.L()
        shot_layers.append(rect_json(top_id, "%s L2 bar top" % label, start, dur, (W, bars), (0, 0), INK,
                                     desc="L2 bar %d px%s" % (bars, ", slides in over %df" % lb.get("slide_in_f", 8) if enter else "")))
        shot_layers.append(rect_json(bot_id, "%s L2 bar bottom" % label, start, dur, (W, bars), (0, H - bars), INK))
        if enter and slide_ms > 0:
            dyn.layer(top_id, "positionY", [(0, -bars, LINEAR), (slide_ms, 0.0, EASE_OUT)])
            dyn.layer(bot_id, "positionY", [(0, H, LINEAR), (slide_ms, H - bars, EASE_OUT)])
    if look:
        shot_layers.append(adjustment_json(ids.L(), "%s look (%s%s)" % (label, "L1 vignette" if screen == "L1" else "",
                                                                       (" + " if screen == "L1" and grade == "archival" else "") +
                                                                       ("archival vignette + grain" if grade == "archival" else "")),
                                           start, dur, look))
    shot_layers += whips
    shot_layers.append(framing)
    sg = group_json(ids.L(), "%s · %s" % (label, shot["id"]), start, dur, shot_layers,
                    desc=(shot.get("notes") or "")[:600] or None)
    info = {"id": shot["id"], "beat": beat["id"], "rid": rid, "screen": screen, "grade": grade,
            "beat_frames": list(shot["_beat_f"]), "edit_frames": [sf, ef], "window_ms": [start, end],
            "source": shot["_src_rel"], "source_kind": shot["_src_kind"], "source_in_s": wc["t_in"],
            "speed": wc["speed"], "reverse": wc["reverse"], "crop": wc["crop"],
            "working_copy": rel(wc["path"]), "wc_size": [wc["w"], wc["h"]], "aspect": round(wc["aspect"], 4),
            "fit": fit, "picture_rect": [round(v, 2) for v in pic], "video_scale": round(base, 3), "push": [s0, s1],
            "x2_drift_px": drift if x2 else None, "x8": [p[0] for p in x8_parts(shot, beat["start_frame"])],
            "bars": bars or None, "content_offset_ms": offset, "video_layer": vid_id, "group_layer": sg["id"]}
    return sg, info


# --------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-cache", action="store_true", help="re-cut every footage working copy")
    ap.add_argument("--shots-dir", help="test only: read <dir>/<composition>/tesseract_shots.json first")
    ap.add_argument("--output", help="test only: write the project here instead of .tesseract-work/picture.tsrct")
    args = ap.parse_args()
    global PROJECT, JSON_OUT, REPORT
    if args.output:
        PROJECT = Path(args.output).resolve()
        JSON_OUT = PROJECT.with_suffix(".editable.json")
        REPORT = PROJECT.with_suffix(".report.json")

    MEDIA.mkdir(parents=True, exist_ok=True)
    CHECKS.mkdir(parents=True, exist_ok=True)
    bm = json.loads(BEAT_MAP.read_text())
    if int(bm.get("fps", FPS)) != FPS or list(bm.get("canvas", [W, H])) != [W, H]:
        raise SystemExit("beat_map fps/canvas differ from 30 fps 1920x1080")
    edit_end_s = float(bm["edit_end_s"])
    edit_ms = int(round(edit_end_s * 1000))
    warnings, notes = [], []

    # ---- gather beats, renders and shots ---------------------------------------------------------
    beats = bm["beats"]
    hf, missing_renders = [], []
    for b in beats:
        comp = b["composition"]["id"]
        mov = RENDERS / ("%s.mov" % comp)
        if mov.exists():
            hf.append((b, mov))
        else:
            missing_renders.append(comp)
    shots_by_beat, shot_files = {}, {}
    for b in beats:
        sh, p = load_shots(b, warnings, args.shots_dir)
        shot_files[b["id"]] = rel(p) if p else None
        if sh:
            shots_by_beat[b["id"]] = sh
    all_shots = [s for b in beats for s in shots_by_beat.get(b["id"], [])]

    # ---- project + imports -----------------------------------------------------------------------
    if PROJECT.exists():
        PROJECT.unlink()
    tsrct("project", "create", "--project", PROJECT)
    hf_assets = {}
    for b, mov in hf:
        aid = "pic-hf-%s" % b["composition"]["id"]
        r = json.loads(tsrct("project", "import-video", "--project", PROJECT, "--file", mov, "--asset-id", aid).stdout)
        hf_assets[b["id"]] = (aid, r)
    wc_used = set()
    shot_assets, imported = {}, {}
    for b in beats:
        for s in shots_by_beat.get(b["id"], []):
            src, kind, n = resolve_source(s)
            warnings += ["%s %s: %s" % (b["id"], s["id"], x) for x in n]
            if src is None:
                warnings.append("%s %s: no footage for %s (no source, original or stand-in); shot skipped" % (
                    b["id"], s["id"], s.get("rid")))
                continue
            if kind == "placeholder":
                warnings.append("%s %s: %s is the labelled STAND-IN %s" % (b["id"], s["id"], s.get("rid"), rel(src)))
            elif kind == "original-by-rid":
                notes.append("%s %s: no 'source' field; resolved %s by R-ID to %s (source_in_s %.3f taken as seconds "
                             "in that file)" % (b["id"], s["id"], s.get("rid"), rel(src), float(s.get("source_in_s") or 0)))
            s["_src_rel"], s["_src_kind"] = rel(src), kind
            sp = probe(src)
            wc = working_copy(s, src, sp, "B%02d" % int(b["id"][1:]), not args.no_cache, warnings)
            wc_used.add(wc["path"].name)
            aid = "pic-ft-%s-%s" % (b["id"].lower(), wc["hash"])
            if aid not in imported:
                imported[aid] = json.loads(tsrct("project", "import-video", "--project", PROJECT, "--file", wc["path"],
                                                 "--asset-id", aid).stdout)
            shot_assets[id(s)] = (aid, imported[aid], wc)
    if not args.output:                     # a test build must not evict the real build's working copies
        for f in MEDIA.glob("*.mp4"):
            if f.name not in wc_used:
                f.unlink()

    # ---- document --------------------------------------------------------------------------------
    tsrct("project", "checkout", "--project", PROJECT, "--output", JSON_OUT)
    doc = json.loads(JSON_OUT.read_text())
    doc["dimensions"] = {"width": W, "height": H}
    doc["duration"] = edit_end_s
    doc["backgroundColor"] = INK
    ids, dyn = Ids(), Dyn()
    root = []

    grain_adj, grain_eff = ids.L(), ids.E()
    root.append(adjustment_json(grain_adj, "Grain (whole edit)", 0, edit_ms,
                                [fx(grain_eff, dict({"type": "grain", "seed": 1.0}, **GRAIN_EDIT))],
                                desc="Plan p.10: a very light grain layer (3-5%) over the whole edit to glue the sources "
                                     "together; seed advances every frame"))
    dyn.script(grain_eff, "seed", "return Math.round(input.time.seconds * 30) + 1;")

    hf_group_id = ids.L()
    hf_layers, hf_info = [], []
    for b, mov in hf:
        aid, imp = hf_assets[b["id"]]
        sf, ef = int(b["start_frame"]), int(b["end_frame"])
        start, end = ms_floor(sf), ms_floor(ef)
        # content(t) = t + offset must pick MOV local frame 6 + (n - sf) at edit frame n:
        # offset = ceil(200 - sf*1000/30) = 200 - floor(sf*1000/30) (6f = exactly 200 ms)
        offset = (HANDLE_F * 1000) // FPS - start
        nf = int(probe(mov)["nb_frames"] or 0)
        want = int(b["dur_frames"]) + 2 * HANDLE_F
        if nf and nf != want:
            warnings.append("%s: render has %d frames, beat + 12 = %d (stale render vs timing?)" % (rel(mov), nf, want))
        lid = ids.L()
        hf_layers.append(video_json(lid, "B%02d HF %s" % (int(b["id"][1:]), b["composition"]["id"]), aid,
                                    imp["durationMs"], start, end - start, offset, (0, 0, W, H), "cover", tr(),
                                    desc="%s: local frame %d on beat frame 0 (edit frame %d); visible [%d, %d) f" % (
                                        rel(mov), HANDLE_F, sf, sf, ef)))
        hf_info.append({"beat": b["id"], "render": rel(mov), "layer": lid, "edit_frames": [sf, ef], "window_ms": [start, end],
                        "content_offset_ms": offset, "mov_frames": nf, "expected_frames": want})
    root.append(group_json(hf_group_id, "HyperFrames beat renders", 0, edit_ms, hf_layers,
                           desc="One ProRes 4444 alpha render per beat (05_GFX/renders), each over its own beat only"))

    shot_info = []
    for b in beats:
        sh = [s for s in shots_by_beat.get(b["id"], []) if id(s) in shot_assets]
        if not sh:
            continue
        groups = []
        for s in sh:
            aid, imp, wc = shot_assets[id(s)]
            g, info = build_shot(s, b, wc, aid, imp["durationMs"], ids, dyn, all_shots, notes)
            groups.append(g)
            shot_info.append(info)
        a = min(ms_floor(s["_start_f"]) for s in sh)
        z = max(ms_floor(s["_end_f"]) for s in sh)
        a, z = max(0, a), min(edit_ms, z)
        root.append(group_json(ids.L(), "B%02d footage" % int(b["id"][1:]), a, z - a, groups,
                               desc="Tesseract-owned shots of %s (%s)" % (b["id"], shot_files[b["id"]])))

    doc["composition"]["layers"] = root
    doc["composition"]["dynamics"] = {"entries": dyn.entries}
    JSON_OUT.write_text(json.dumps(doc, indent=1) + "\n")
    r = json.loads(tsrct("project", "commit", "--project", PROJECT, "--file", JSON_OUT).stdout)
    chk = json.loads(run([TSRCT, "project", "check", "--project", PROJECT], check=False).stdout or "{}")
    report = {"project": rel(PROJECT), "tsrct": tsrct("--version").stdout.strip(), "edit_end_s": edit_end_s,
              "layers_max_id": ids.layer, "hf_renders": hf_info, "missing_renders": missing_renders,
              "shots": shot_info, "shot_files": shot_files, "commit_warnings": r.get("warnings", []),
              "check": {"valid": chk.get("valid"), "diagnostics": chk.get("diagnostics"), "warnings": chk.get("warnings")},
              "warnings": warnings, "notes": notes,
              "constants": {"GRAIN_EDIT": GRAIN_EDIT, "GRAIN_ARCHIVAL": GRAIN_ARCHIVAL, "VIGNETTE_LIGHT": VIGNETTE_LIGHT,
                            "L1": [L1_SCALE, L1_BLUR_PX, L1_SHARP_FRAC, L1_FEATHER], "GRADES": GRADES,
                            "X8_TRAVEL": X8_TRAVEL, "MARGIN_F": MARGIN_F, "WC_RECIPE": WC_RECIPE}}
    REPORT.write_text(json.dumps(report, indent=1) + "\n")
    log("picture: %s committed; %d HF renders, %d footage shots in %d beat groups, max layer id %d; check valid=%s" % (
        rel(PROJECT), len(hf_info), len(shot_info), len({i['beat'] for i in shot_info}), ids.layer, chk.get("valid")))
    log("  missing renders (skipped): %s" % (", ".join(missing_renders) or "none"))
    for w in r.get("warnings", []) + (chk.get("warnings") or []):
        log("  tesseract warning: %s" % (w if isinstance(w, str) else json.dumps(w)))
    for w in warnings:
        log("  WARN %s" % w)
    for n in notes:
        log("  note %s" % n)
    log("  report: %s" % rel(REPORT))
    if chk.get("valid") is False:
        raise SystemExit("project check failed: %s" % json.dumps(chk.get("diagnostics"))[:2000])


if __name__ == "__main__":
    main()
