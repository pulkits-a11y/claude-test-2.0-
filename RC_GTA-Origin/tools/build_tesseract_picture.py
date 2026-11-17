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
  1. "Finish ..."                the whole-edit finish (REVISION_v02.md rule F; v03 notes 14-15), over everything:
                                 static CRT scanlines (multiply), a static monochrome grain plate (linear light),
                                 a dark hard vignette and an animated chromatic aberration (easeInOutSine keys).
                                 v03 removed the dust overlay and stopped the grain from changing per frame
  2. "HyperFrames beat renders"  Group, one Video per existing MOV: MOV local frame 6 on the beat's start
                                 frame, visible over [beat start, beat end) only
  3. "Bxx footage"               one Group per beat with Tesseract shots; per shot a Group holding the L2 bars,
                                 the shot's look/whip Adjustments and a framing Group (zoom keys, X2 drift)
                                 around the Video (+ the L1 mask guide)
Nothing is linear (client note 14, rule C): every keyframe carries an easings.net curve as a cubic-bezier
(EASINGS below); shots may give zoom/drift keys as `framing.keys` (framing v2, rule D).
Footage is never imported raw: each shot's window (+ margins) is cut with FFmpeg from the original to an
H.264 1080p-fit 30 fps CFR working copy in .tesseract-work/media/ (crop applied, pixel aspect corrected,
never stretched, speed/reverse baked in, no B-frames so the decode clock is exact). Copies are cached by
a hash of their recipe and re-used; unused copies are deleted.

Usage:  python3 tools/build_tesseract_picture.py [--no-cache]
Writes: .tesseract-work/picture.tsrct, picture.editable.json, checks/picture_report.json
Test only: --shots-dir DIR reads DIR/<composition>/tesseract_shots.json first (falls back to hyperframes/),
           --output X.tsrct writes the document (and X.editable.json, X.report.json) there instead,
           --no-renders leaves the HyperFrames renders out (footage, grades and the finish only).
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
GRAIN_ARCHIVAL = {"amount": 0.6, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0}  # extra on archival shots: ~4.3% combined
VIGNETTE_LIGHT = {"amount": 0.25, "radius": 1.0, "feather": 0.8}   # corners about -17%, edge centres -7%
L1_SCALE = 105.0                   # plan: footage at 105%
L1_BLUR_PX = 12                    # plan: edges blurred 12 px
L1_SHARP_FRAC = 0.70               # plan: centre 70% stays sharp
L1_FEATHER = (192, 108)            # mask feather (x, y) px: the sharp->blurred ramp outside the 70% box
PUSH_DEFAULT = (100.0, 104.0)      # v03 note 13 (zooms reverted): a held shot without framing pushes 100 -> 104%
PUSH_ALTERNATE = False             # ... eased (sine.inOut); no auto-alternated zoom-outs (v02 rule D's are removed)
HELD_MIN_F = 12                    # shots shorter than this get no default push-in (burst clips)

# ---- easings.net curves as CSS cubic-bezier (client note 14, REVISION_v02.md rule C: nothing linear) ----------
# Tesseract: a keyframe's easing shapes the segment ARRIVING at it (the first key's easing is never used; it gets
# the next segment's curve so no key in the document is linear). Elastic/bounce are not cubic-bezier curves.
EASINGS = {
    "easeInSine": (0.12, 0, 0.39, 0), "easeOutSine": (0.61, 1, 0.88, 1), "easeInOutSine": (0.37, 0, 0.63, 1),
    "easeInQuad": (0.11, 0, 0.5, 0), "easeOutQuad": (0.5, 1, 0.89, 1), "easeInOutQuad": (0.45, 0, 0.55, 1),
    "easeInCubic": (0.32, 0, 0.67, 0), "easeOutCubic": (0.33, 1, 0.68, 1), "easeInOutCubic": (0.65, 0, 0.35, 1),
    "easeInQuart": (0.5, 0, 0.75, 0), "easeOutQuart": (0.25, 1, 0.5, 1), "easeInOutQuart": (0.76, 0, 0.24, 1),
    "easeInQuint": (0.64, 0, 0.78, 0), "easeOutQuint": (0.22, 1, 0.36, 1), "easeInOutQuint": (0.83, 0, 0.17, 1),
    "easeInExpo": (0.7, 0, 0.84, 0), "easeOutExpo": (0.16, 1, 0.3, 1), "easeInOutExpo": (0.87, 0, 0.13, 1),
    "easeInCirc": (0.55, 0, 1, 0.45), "easeOutCirc": (0, 0.55, 0.45, 1), "easeInOutCirc": (0.85, 0, 0.15, 1),
    "easeInBack": (0.36, 0, 0.66, -0.56), "easeOutBack": (0.34, 1.56, 0.64, 1), "easeInOutBack": (0.68, -0.6, 0.32, 1.6),
}
GSAP_FAMILY = {"sine": "Sine", "quad": "Quad", "power1": "Quad", "cubic": "Cubic", "power2": "Cubic", "quart": "Quart",
               "power3": "Quart", "quint": "Quint", "power4": "Quint", "strong": "Quint", "expo": "Expo", "circ": "Circ",
               "back": "Back"}
EASE_PUSH = "easeInOutSine"        # slow push / zoom across a held shot (rule C table); legacy scale_from/to too
EASE_X2 = "easeOutQuart"           # X2 cut-then-drift settling into place (the plan's "ease out" = power3.out)
EASE_BARS = "easeOutQuart"         # L2 bars sliding in and landing
EASE_WHIP_OUT, EASE_WHIP_IN = "easeInQuart", "easeOutQuart"   # X8: accelerate into the cut / decelerate out of it
EASE_POP_RETURN = "easeInOutSine"  # b10-pop saturation back to 0 after its second
POP_RETURN_F = 8
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
    "b10-pop": {"contrast": 0.18, "saturation": 0.10},                          # +10% for 1 s, then back (eased)
    "neutralize": {"contrast": 0.18, "saturation": -0.20},                      # v02 B17 fan edit, after NEUTRALIZE
    "none": None,
}
B10_POP_MS = 1000
# v02 grade `neutralize` (REVISION_v02.md B17: the madebyajit fan edit's heavy pink/magenta grade must sit with the
# other GTA 6 footage). Per shot, from its own working copy: per luma decile, the median R/G/B are pulled
# `strength` of the way to (decile luma x target_rgb), a slightly warm neutral like the trailer footage
# (R17.2/R17.4 average R:G:B about 1.03:1:0.97); the three channel curves through those points are a colorCurves
# effect (a tone-dependent white balance: the cast differs between the magenta shadows and the pinkish
# highlights). Then hueCurves takes the purple/magenta that remains in the fence and shadows down (hue about
# 250-320 deg; skin at 10-40 deg is untouched), and the primaryGrade above adds the `game` contrast and -20%
# saturation. Measured on the clip @ 1-5 s: mean R-G 0.18-0.25 -> 0.01-0.05, chroma 0.19-0.25 -> 0.07-0.08 (the
# trailer footage: R-G 0.01-0.03, chroma 0.05-0.08). PICTURE_NOTES.md has the frames.
NEUTRALIZE = {"strength": 0.85, "target_rgb": (1.03, 1.0, 0.97), "bins": 10, "sample_fps": 5, "sample_w": 480,
              "hue_vs_saturation": [(0.0, 0.5), (0.6, 0.5), (0.7, 0.25), (0.79, 0.12), (0.88, 0.25), (0.96, 0.5),
                                    (1.0, 0.5)]}

# ---- whole-edit finish (REVISION_v02.md rule F; v03 notes 14-15), top layers over everything ------------------
# Calibrated on flat fields, test patterns and real frames in Tesseract 0.7.0 (PICTURE_NOTES.md "Whole-edit finish").
FINISH_GRAIN = {"amount": 3.0, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0,   # on a 50% grey Rect plate,
                "plate": 0.5, "blend": "linearLight", "opacity": 28.0,            # desaturated: monochrome film grain;
                "seed": 1.0}                                                      # linear light adds 2 x opacity x
                # (plate - 0.5). v03 note 15: STATIC (one seed, no per-frame script): the same grain on every frame.
                # v04 note 2 ("reduce opacity of textures"): opacity 55 -> 28%, about half as visible (p1-p99 on flat
                # grey about 6% of full scale, was 11.8%)
FINISH_VIGNETTE = {"amount": 0.70, "radius": 0.74, "feather": 0.50}   # v03 note 14 (darker/harder): flat field
                # corners -68%, edge centres -35% (v02: amount 0.57, radius 1.0, feather 0.8 = -38% / -17%)
FINISH_SCANLINES = {"enabled": False,      # v04 note 7: no whole-edit CRT lines (the kit draws them inside dark cards)
                    "period_px": 9, "depth": 0.30, "shape": 1.5, "blend": "multiply"}   # v03 note 15: static CRT
                # scanlines (they replace the dust overlay): a raised-cosine dark band every 9 px at 1080p, the line
                # centre 30% darker; 9 px = the line pitch of the client's references (2.77-2.79 px in the 576-586 px
                # wide screenshots) and coarse enough not to alias when the video is shown smaller (4 px lines turn
                # into moire beats or vanish at the references' scale, measured)
FINISH_CHROMA = {"direction": 90.0, "px": (0.6, 2.0), "half_period_s": 1.2,   # R and B each shifted 0.6 <-> 2.0 px
                 "px_per_amount": 19.1}                                       # (horizontal; 2.4 s period, sine)
                 # measured: amount 1.0 = R -19.06 px, B +19.06 px along `direction` (0 = vertical), uniform


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


EASE_WARNINGS = []


def ease_name(name, default=EASE_PUSH, where="") -> str:
    """An easings.net name ('easeOutExpo'), any spelling of it ('ease-out-expo') or a GSAP name ('expo.out',
    'power3.out', 'back.out(1.7)', 'sine.inOut') -> the easings.net name. 'linear'/'none'/unknown -> `default`
    with a warning (client note 14: nothing linear)."""
    if name is None or name == "":
        return default
    n = str(name).strip()
    if n in EASINGS:
        return n
    flat = re.sub(r"[^a-z]", "", n.lower())
    for k in EASINGS:
        if k.lower() == flat:
            return k
    m = re.fullmatch(r"([a-z]+[1-4]?)(?:\.(in|out|inout))?(?:\(.*\))?", re.sub(r"\s+", "", n.lower()))
    if m and m.group(1) in GSAP_FAMILY:
        d = {"in": "In", "out": "Out", "inout": "InOut", None: "Out"}[m.group(2)]
        return "ease%s%s" % (d, GSAP_FAMILY[m.group(1)])
    EASE_WARNINGS.append("%s: easing %r is %s; used %s" % (where or "?", name, "linear (not allowed, note 14)" if flat in (
        "linear", "none") else "unknown", default))
    return default


def ease(name, default=EASE_PUSH, where="") -> dict:
    x1, y1, x2, y2 = EASINGS[ease_name(name, default, where)]
    return {"type": "cubicBezier", "x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2)}


def eased_points(points):
    """[(t, v, easing-name-or-None)] -> [(t, v, cubic-bezier)]: each key arrives with its own curve; the first key
    (whose easing is never used) gets the second key's curve, so no keyframe in the document is linear."""
    out = []
    for i, (t, v, e) in enumerate(points):
        if i == 0 and e is None and len(points) > 1:
            e = points[1][2]
        out.append((t, v, e if isinstance(e, dict) else ease(e)))
    return out


def osc_points(t0, t1, half, a, b, name="easeInOutSine", phase=0):
    """Keys alternating a, b, a, ... every `half` ms over [t0, t1] (a last key at t1 on the interpolated value),
    every segment easeInOutSine: a smooth back-and-forth, never linear."""
    pts, k, t = [], phase, float(t0)
    while t < t1 - 1e-6:
        pts.append((int(round(t)), a if k % 2 == 0 else b, name))
        t += half
        k += 1
    last_v = a if k % 2 == 0 else b
    prev_t, prev_v = pts[-1][0], pts[-1][1]
    u = (t1 - prev_t) / float(half)
    x1, y1, x2, y2 = EASINGS[name]
    pts.append((int(t1), prev_v + (last_v - prev_v) * bezier_y(u, x1, y1, x2, y2), name))
    return pts


def bezier_y(x, x1, y1, x2, y2):
    """CSS cubic-bezier: y for a given x (bisection on the parametric x)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        xt = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t ** 2 * x2 + t ** 3
        lo, hi = (t, hi) if xt < x else (lo, t)
    t = (lo + hi) / 2
    return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3


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
        """points: [(t, value, easing)] with easing an easings.net name, None (= the next key's curve for a first
        key, else the default) or a ready cubic-bezier dict."""
        points = eased_points(points)
        kfs = []
        for i, (t, v, easing) in enumerate(points):
            if not isinstance(easing, dict) or easing.get("type") != "cubicBezier":
                raise SystemExit("non-eased keyframe %s %s (client note 14)" % (tag, easing))
            kfs.append({"id": "pic-%s-%03d" % (tag, i), "layerTime": int(t),
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
        sp = str(shot["source"]).strip()
        for p in (ROOT / sp, Path(sp), ROOT.parent / sp):   # project-relative (spec), absolute, or repo-relative
            if p.is_file():
                return p.resolve(), "source", notes
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
        if ef > int(beat["dur_frames"]):
            warnings.append("%s %s: ends at beat f%d, %d f past the beat's %d frames (shot file still v01-timed?)" % (
                beat["id"], s["id"], ef, ef - int(beat["dur_frames"]), int(beat["dur_frames"])))
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


DEFAULT_PUSH_COUNT = [0]


def framing_keys(shot, screen, n, notes):
    """The shot's zoom/drift keys [(f, scale %, ease name, x px | None, y px | None)], f = frames from the shot's
    first frame (0..n). Framing v2 (REVISION_v02.md): framing.keys = [{f, scale, ease, x?, y?}], `ease` = the
    easings.net curve arriving at that key (default easeInOutSine). Legacy scale_from/scale_to: one move across the
    shot, easeInOutSine unless framing.ease says otherwise. No framing: a held shot (>= HELD_MIN_F, not L10) gets
    the rule D default 100 -> 108% push, alternating with 108 -> 100% zoom-outs; bursts/short shots stay at 100%."""
    fr = shot.get("framing") if isinstance(shot.get("framing"), dict) else {}
    anchor = fr.get("anchor", "center")
    where = shot["id"]
    if isinstance(fr.get("keys"), list) and fr["keys"]:
        keys, prev = [], float(fr.get("scale_from", 100.0))
        for k in fr["keys"]:
            if not isinstance(k, dict):
                notes.append("%s: framing key %r ignored (not an object)" % (where, k))
                continue
            f = int(round(float(k.get("f", 0))))
            if not 0 <= f <= n:
                notes.append("%s: framing key f%d outside the shot (0..%d); clamped" % (where, f, n))
                f = min(max(f, 0), n)
            prev = float(k.get("scale", prev))
            keys.append((f, prev, ease_name(k.get("ease"), EASE_PUSH, where) if k.get("ease") else None,
                         float(k["x"]) if k.get("x") is not None else None,
                         float(k["y"]) if k.get("y") is not None else None))
        keys.sort(key=lambda k: k[0])
        ded = []
        for k in keys:
            if ded and ded[-1][0] == k[0]:
                ded[-1] = k
            else:
                ded.append(k)
        keys = [(f, sc, (e or EASE_PUSH) if i else e, x, y) for i, (f, sc, e, x, y) in enumerate(ded)]
        return keys, "framing v2 keys", anchor
    if "scale_from" in fr or "scale_to" in fr:
        s0 = float(fr.get("scale_from", 100))
        s1 = float(fr.get("scale_to", s0))
        e = ease_name(fr.get("ease"), EASE_PUSH, where)
        return [(0, s0, None, None, None), (n, s1, e, None, None)], "legacy scale_from/to, %s" % e, anchor
    if screen == "L10" or n < HELD_MIN_F:
        return [(0, 100.0, None, None, None)], "static (burst or short shot)", anchor
    k = DEFAULT_PUSH_COUNT[0]
    DEFAULT_PUSH_COUNT[0] += 1
    a, b = PUSH_DEFAULT[::-1] if (PUSH_ALTERNATE and k % 2) else PUSH_DEFAULT
    return [(0, a, None, None, None), (n, b, EASE_PUSH, None, None)], "default %s, %s" % (
        "push-in" if b > a else "zoom-out", EASE_PUSH), anchor


def framing_desc(keys) -> str:
    parts = []
    for i, (f, sc, e, x, y) in enumerate(keys):
        xy = "" if x is None and y is None else " (x %s, y %s)" % (x, y)
        parts.append("f%d %.1f%%%s%s" % (f, sc, xy, "" if i == 0 else " " + (e or EASE_PUSH)))
    return " -> ".join(parts)


NEUTRALIZE_CACHE = {}


def render_proxy(mov: Path, height: int) -> Path:
    """Preview proxy of a beat render: ProRes 4444 (alpha kept, 10-bit) scaled to `height`, same frames and rate, so
    the render's placement is unchanged (fit: cover on the 1920x1080 canvas). Cached by the source's size/mtime."""
    out = WORK / "proxies" / ("%s_%dp.mov" % (mov.stem, height))
    st = mov.stat()
    tag = "%d %d %d" % (st.st_size, st.st_mtime_ns, height)
    meta = out.with_suffix(".src")
    if out.exists() and meta.exists() and meta.read_text() == tag:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp.mov")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", mov, "-an", "-vf", "scale=-2:%d:flags=bicubic" % height,
         "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-qscale:v", "9", "-vendor", "apl0",
         tmp])
    tmp.replace(out)
    meta.write_text(tag)
    return out


def neutralize_curves(src: Path, t0: float, t1: float):
    """colorCurves points for grade `neutralize` (see NEUTRALIZE), measured on the SOURCE clip over [t0, t1] s: the
    span every `neutralize` shot of that clip uses, so shots cut from the same clip share one grade (no jump at
    their cuts, and a 10-frame shot is not graded from 2 samples)."""
    key = (str(src), round(t0, 3), round(t1, 3))
    if key in NEUTRALIZE_CACHE:
        return NEUTRALIZE_CACHE[key]
    nz = NEUTRALIZE
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", "%.4f" % t0, "-t", "%.4f" % max(t1 - t0, 1.0 / FPS),
                          "-i", str(src), "-vf", "fps=%d,scale=%d:-2" % (nz["sample_fps"], nz["sample_w"]),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    px = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(float) / 255.0
    px = px[(px.max(axis=1) > 0.02)]                       # ignore the ink pillars of a contain-fit copy
    y = px @ np.array([0.2126, 0.7152, 0.0722])
    edges = np.quantile(y, np.linspace(0, 1, nz["bins"] + 1))
    pts = {c: [] for c in ("red", "green", "blue")}
    meds = []
    for k in range(nz["bins"]):
        m = (y >= edges[k]) & (y <= edges[k + 1])
        if not np.any(m):
            continue
        yk, med = float(np.median(y[m])), np.median(px[m], axis=0)
        meds.append((round(yk, 3), [round(float(v), 3) for v in med]))
        for i, c in enumerate(("red", "green", "blue")):
            tgt = min(1.0, yk * nz["target_rgb"][i])
            pts[c].append((float(med[i]), float(med[i] + nz["strength"] * (tgt - med[i]))))
    curves = {"master": [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 1.0}]}
    for c, p_ in pts.items():
        out = [(0.0, 0.0)]
        for x_, y_ in sorted(p_):
            if x_ <= out[-1][0] + 0.01 or x_ >= 0.99:
                continue
            out.append((round(x_, 4), round(max(y_, out[-1][1]), 4)))
        out.append((1.0, 1.0))
        curves[c] = [{"x": a, "y": b} for a, b in out]
    rg = float(np.mean(px[:, 0] - px[:, 1]))
    out = (curves, "from %s %.2f-%.2f s at %d fps (%d px): per-decile luma/median RGB %s; source mean R-G %.3f" % (
        rel(src), t0, t1, nz["sample_fps"], len(px), meds, rg))
    NEUTRALIZE_CACHE[key] = out
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
        if narrow:   # 4:3 archival: full height with ink pillars, never stretched; the bars slide in over it
            pic = (0, 0, W, H)   # (visibly, as L2 asks) and leave it inside the band (style kit: 4:3 in a band)
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
    # --- framing: zoom keys (v02 framing v2 / legacy scale_from-to / default push) --------------------
    fkeys, fmode, anchor = framing_keys(shot, screen, ef - sf, notes)
    s0, s1 = fkeys[0][1], fkeys[-1][1]
    ax, ay = (W / 2.0, H / 2.0) if not isinstance(anchor, (list, tuple)) else (float(anchor[0]), float(anchor[1]))
    # drift keys (x/y px) need overscan like X2, so the move never uncovers the frame edge
    if fit == "cover" or (pic[2] / pic[3]) <= wc["aspect"]:
        for f_, sc, _, kx, ky in fkeys:
            need = 100.0 * max(1 + 2 * abs(kx or 0) / W, 1 + 2 * abs(ky or 0) / H) / (max(sc, 1.0) / 100.0)
            if need > base + 1e-6:
                notes.append("%s: framing key f%d (scale %.1f, x %s, y %s) needs %.2f%% overscan; video scaled to it" % (
                    shot["id"], f_, sc, kx, ky, need))
                base = need
    if min(k[1] for k in fkeys) < 100.0 - 1e-6 and fit == "cover":
        notes.append("%s: framing scale below 100%% (%.1f) uncovers the frame edge" % (shot["id"], min(k[1] for k in fkeys)))

    # --- the Video (+ L1 mask guide) inside the framing group -----------------------------------------
    offset = -(((sf - wc["head_f"]) * 1000) // FPS)         # content ms = parent ms + offset (exact frame pick)
    vid_id = ids.L()
    effects, masks, inner = [], [], []
    g = GRADES[grade]
    pg_id = None
    if grade == "neutralize":
        src_ = ROOT / shot["_src_rel"] if not Path(shot["_src_rel"]).is_absolute() else Path(shot["_src_rel"])
        cv, stats = neutralize_curves(src_, *shot["_neutralize_span"])
        effects.append(fx(ids.E(), {"type": "colorCurves", "semanticVersion": 1, "curves": cv}))
        effects.append(fx(ids.E(), {"type": "hueCurves", "semanticVersion": 1, "hueVsSaturation": [
            {"x": x_, "y": y_} for x_, y_ in NEUTRALIZE["hue_vs_saturation"]]}))
        notes.append("%s: neutralize curves %s" % (shot["id"], stats))
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
        t0 = start + offset          # +10% for 1 s, then eased back to 0 (v01: a hold step; v02 note 14)
        sat = GRADES["b10-pop"]["saturation"]
        dyn.effect(pg_id, "saturation", [(t0, sat, EASE_POP_RETURN), (t0 + B10_POP_MS, sat, EASE_POP_RETURN),
                                         (t0 + B10_POP_MS + frames_ms(POP_RETURN_F), 0.0, EASE_POP_RETURN)])

    fid = ids.L()
    kx0 = next((k[3] for k in fkeys if k[3] is not None), None)
    ky0 = next((k[4] for k in fkeys if k[4] is not None), None)
    framing = group_json(fid, "%s framing" % label, start, dur, inner,
                         transform=tr(ax + (kx0 or 0.0), ay + (ky0 or 0.0), s0, ax, ay),
                         desc="%s: %s%s" % (fmode, framing_desc(fkeys), "; X2 drift %d px %s over %df (%s)" % (
                             drift, shot.get("x2_dir") or "left", X2_FRAMES, EASE_X2) if x2 else ""))
    key_ms = lambda f_: ms_floor(sf + f_)
    if len(fkeys) > 1 and any(abs(k[1] - s0) > 1e-9 for k in fkeys):
        for p in ("scaleX", "scaleY"):
            dyn.layer(fid, p, [(key_ms(f_), sc, e) for f_, sc, e, _, _ in fkeys])
    for p, idx, base_v in (("positionX", 3, ax), ("positionY", 4, ay)):
        if any(k[idx] is not None for k in fkeys):
            last, pts = 0.0, []
            for k in fkeys:
                last = float(k[idx]) if k[idx] is not None else last
                pts.append((key_ms(k[0]), base_v + last, k[2]))
            if len({round(v, 6) for _, v, _ in pts}) > 1:
                dyn.layer(fid, p, pts)
    outer = framing
    if x2:
        sign = 1 if (shot.get("x2_dir") or "left").lower() == "left" else -1   # 'left' = slides leftwards
        d_ms = min(frames_ms(X2_FRAMES), dur)
        x2_pts = [(start, ax + sign * drift, None), (start + d_ms, ax, EASE_X2)]
        if any(k[3] is not None for k in fkeys):          # drift keys own the framing group's positionX
            outer = group_json(ids.L(), "%s X2 drift" % label, start, dur, [framing], transform=tr(ax, ay, 100.0, ax, ay),
                               desc="X2 cut-then-drift %d px over %df, %s" % (drift, X2_FRAMES, EASE_X2))
            dyn.layer(outer["id"], "positionX", x2_pts)
        else:
            dyn.layer(fid, "positionX", x2_pts)

    # --- shot-level adjustments: whip (lowest), then the look (vignette/grain) -----------------------
    shot_layers = []
    look = []
    if screen == "L1" or grade == "archival":
        look.append(fx(ids.E(), dict({"type": "vignette"}, **VIGNETTE_LIGHT)))
    if grade == "archival":
        gid = ids.E()
        look.append(fx(gid, dict({"type": "grain", "seed": float(vid_id % 97 + 11)}, **GRAIN_ARCHIVAL)))
        # v03 note 15: static grain (one seed per shot, no per-frame script)
    whips = []
    for part, a, b, x8 in x8_parts(shot, beat["start_frame"]):
        wa, wb = ms_floor(a), ms_floor(b)
        wd = wb - wa
        aid, mt_id, db_id = ids.L(), ids.E(), ids.E()
        sgn = -1 if str(x8.get("dir", "left")).lower() == "left" else 1   # content moves this way
        blur = float(x8.get("blur_px", 80))
        if part == "out":
            mt_keys = [(0, 0.5, None), (wd, 0.5 + sgn * X8_TRAVEL, EASE_WHIP_OUT)]
            db_keys = [(0, 0.0, None), (wd, blur, EASE_WHIP_OUT)]
        else:
            mt_keys = [(0, 0.5 - sgn * X8_TRAVEL, None), (wd, 0.5, EASE_WHIP_IN)]
            db_keys = [(0, blur, None), (wd, 0.0, EASE_WHIP_IN)]
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
            dyn.layer(top_id, "positionY", [(0, -bars, None), (slide_ms, 0.0, EASE_BARS)])
            dyn.layer(bot_id, "positionY", [(0, H, None), (slide_ms, H - bars, EASE_BARS)])
    if look:
        shot_layers.append(adjustment_json(ids.L(), "%s look (%s%s)" % (label, "L1 vignette" if screen == "L1" else "",
                                                                       (" + " if screen == "L1" and grade == "archival" else "") +
                                                                       ("archival vignette + grain" if grade == "archival" else "")),
                                           start, dur, look))
    shot_layers += whips
    shot_layers.append(outer)
    sg = group_json(ids.L(), "%s · %s" % (label, shot["id"]), start, dur, shot_layers,
                    desc=(shot.get("notes") or "")[:600] or None)
    info = {"id": shot["id"], "beat": beat["id"], "rid": rid, "screen": screen, "grade": grade,
            "beat_frames": list(shot["_beat_f"]), "edit_frames": [sf, ef], "window_ms": [start, end],
            "source": shot["_src_rel"], "source_kind": shot["_src_kind"], "source_in_s": wc["t_in"],
            "speed": wc["speed"], "reverse": wc["reverse"], "crop": wc["crop"],
            "working_copy": rel(wc["path"]), "wc_size": [wc["w"], wc["h"]], "aspect": round(wc["aspect"], 4),
            "fit": fit, "picture_rect": [round(v, 2) for v in pic], "video_scale": round(base, 3), "push": [s0, s1],
            "framing_mode": fmode, "framing_keys": [{"f": k[0], "scale": k[1], "ease": k[2], "x": k[3], "y": k[4]}
                                                    for k in fkeys],
            "x2_drift_px": drift if x2 else None, "x8": [p[0] for p in x8_parts(shot, beat["start_frame"])],
            "bars": bars or None, "content_offset_ms": offset, "video_layer": vid_id, "group_layer": sg["id"]}
    return sg, info


# --------------------------------------------------------------------------------------------
# v02 whole-edit finish (REVISION_v02.md rule F, client note 13)
# --------------------------------------------------------------------------------------------
def scanline_image(path: Path):
    """The static CRT scanline plate (FINISH_SCANLINES) as a 1920x1080 PNG for a multiply layer: white between the
    lines, a raised-cosine dark band (to the power `shape`, so the lines are thinner than the gaps) every `period_px`
    rows, its centre `depth` darker. Written once per setting (deterministic)."""
    import numpy as np
    from PIL import Image
    sc = FINISH_SCANLINES
    if path.exists():
        return path
    y = np.arange(H, dtype=float)
    w = (0.5 - 0.5 * np.cos(2 * np.pi * (y + 0.5) / sc["period_px"])) ** sc["shape"]
    v = 1.0 - sc["depth"] * w / w.max()
    img = np.repeat(np.repeat(np.round(v * 255).astype(np.uint8)[:, None], W, 1)[:, :, None], 3, 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.png")
    Image.fromarray(img).save(tmp)
    tmp.replace(path)
    return path


def finish_layers(ids: Ids, dyn: Dyn, edit_ms: int, scan_asset: str):
    """Top-of-stack finishing layers over the whole edit (footage + HyperFrames renders), all editable in the
    .tsrct. Top to bottom: CRT scanlines (static, multiply), grain plate (static), vignette, chromatic aberration
    (eased keys; the CA works on the picture only, the scanlines and grain sit on top of everything)."""
    layers, info = [], {}
    pg = lambda **k: primary_grade(k)
    # CRT scanlines (v03 note 15): a static multiply plate; off since v04 (note 7)
    sc = FINISH_SCANLINES
    if sc.get("enabled") and scan_asset:
        sid = ids.L()
        layers.append({"type": "Image", "id": sid, "name": "Finish: CRT scanlines (whole edit)", "blendMode": sc["blend"],
                   "activeRange": {"start": 0, "duration": int(edit_ms)},
                   "transform": {"anchorPoint": [W / 2.0, H / 2.0], "position": [W / 2.0, H / 2.0], "scale": [100, 100],
                                 "rotation": 0, "opacity": 100},
                   "source": {"assetId": scan_asset, "fit": "contain",
                              "sourceRect": {"x": 0, "y": 0, "width": W, "height": H}},
                   "description": "v03 note 15: static CRT scanlines across the whole edit (multiply): a dark band every "
                                  "%d px at 1080p, its centre %.0f%% darker; static (no animation)." % (
                                      sc["period_px"], sc["depth"] * 100)})
        info["scanlines"] = {"layer": sid, **sc}
    else:
        info["scanlines"] = {"layer": None, **sc}
    # grain: a 50% grey plate with the engine's grain, desaturated (monochrome), linear light, ONE seed (static)
    gid, geff, gsat = ids.L(), ids.E(), ids.E()
    g = {k: v for k, v in FINISH_GRAIN.items() if k in ("amount", "size", "softness", "aspectRatio", "seed")}
    plate = FINISH_GRAIN["plate"]
    layers.append({"type": "Rect", "id": gid, "name": "Finish: grain (whole edit, static)", "blendMode": FINISH_GRAIN["blend"],
                   "activeRange": {"start": 0, "duration": int(edit_ms)},
                   "transform": tr(0, 0, 100.0, o=FINISH_GRAIN["opacity"]),
                   "rect": {"size": [W, H], "fillColor": [plate, plate, plate, 1.0]},
                   "effects": [fx(geff, dict({"type": "grain"}, **g)), fx(gsat, pg(saturation=-1.0))],
                   "description": "v02 note 13 'a pretty visible / obvious grain', v03 note 15 'keep the noise filter but "
                                  "it moves, remove it': monochrome film grain (grain on a 50%% grey plate, saturation -1) "
                                  "added in linear light at %.0f%% opacity, one fixed seed, so the same grain on every "
                                  "frame. Flat grey: p1-p99 about 12%% of full scale (PICTURE_NOTES.md)." %
                                  FINISH_GRAIN["opacity"]})
    info["grain"] = {"layer": gid, **FINISH_GRAIN}
    # vignette
    vid = ids.L()
    layers.append(adjustment_json(vid, "Finish: vignette (whole edit)", 0, edit_ms,
                                  [fx(ids.E(), dict({"type": "vignette"}, **FINISH_VIGNETTE))],
                                  desc="v03 note 14 'even darker / harder': on a flat field the corners are about 68% "
                                       "darker than the centre, the edge centres about 35%, and the darkening starts "
                                       "well inside the frame (about 12% at three quarters of the way to the edge)."))
    info["vignette"] = {"layer": vid, **FINISH_VIGNETTE}
    # chromatic aberration: R and B shifted opposite ways along `direction`, oscillating (eased) between px[0], px[1]
    cid, ceff = ids.L(), ids.E()
    a0, a1 = (v / FINISH_CHROMA["px_per_amount"] for v in FINISH_CHROMA["px"])
    layers.append(adjustment_json(cid, "Finish: chromatic aberration (whole edit)", 0, edit_ms,
                                  [fx(ceff, {"type": "chromaticAberration", "amount": round(a0, 5),
                                             "direction": FINISH_CHROMA["direction"]})],
                                  desc="v02 note 13 'a subtle chromatic animation': red and blue shifted %.1f <-> %.1f px "
                                       "(opposite ways, horizontal) and back every %.1f s, easeInOutSine." % (
                                           FINISH_CHROMA["px"][0], FINISH_CHROMA["px"][1],
                                           2 * FINISH_CHROMA["half_period_s"])))
    dyn.effect(ceff, "amount", [(t, round(v, 5), e) for t, v, e in osc_points(
        0, edit_ms, FINISH_CHROMA["half_period_s"] * 1000, a0, a1)])
    info["chroma"] = {"layer": cid, "amount": [round(a0, 5), round(a1, 5)], **FINISH_CHROMA}
    return layers, info


# --------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-cache", action="store_true", help="re-cut every footage working copy")
    ap.add_argument("--shots-dir", help="test only: read <dir>/<composition>/tesseract_shots.json first")
    ap.add_argument("--output", help="test only: write the project here instead of .tesseract-work/picture.tsrct")
    ap.add_argument("--no-renders", action="store_true", help="test only: leave the HyperFrames renders out")
    ap.add_argument("--render-proxy", type=int, default=0, metavar="HEIGHT",
                    help="preview only: import the beat renders as ProRes 4444 proxies of this height (e.g. 720), "
                         "cached in .tesseract-work/proxies (alpha, frame count and timing unchanged)")
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
        if mov.exists() and not args.no_renders:
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
    sc = FINISH_SCANLINES
    scan_asset = None
    if sc.get("enabled"):
        scan_png = scanline_image(WORK / "derived" / ("scanlines_p%d_d%02d_s%.1f.png" % (
            sc["period_px"], round(sc["depth"] * 100), sc["shape"])))
        scan_asset = "pic-tex-scanlines"
        tsrct("project", "import-asset", "--project", PROJECT, "--file", scan_png, "--asset-id", scan_asset, "--kind", "image")
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
    # every import rewrites the whole package (temp copy + rename, measured), so the small assets go in first and
    # the beat renders last, smallest first: far less rewriting, and the package is at most twice its size on disk
    hf_assets, hf_ok = {}, set()
    def size_or_0(path):
        try:
            return path.stat().st_size
        except OSError:
            return 0
    for b, mov in sorted(hf, key=lambda bm: size_or_0(bm[1])):
        aid = "pic-hf-%s" % b["composition"]["id"]   # a beat being re-rendered can be an incomplete file: skip it
        try:
            nf = int(probe(mov)["nb_frames"] or 0)
            src_mov = render_proxy(mov, args.render_proxy) if args.render_proxy else mov
            r = json.loads(tsrct("project", "import-video", "--project", PROJECT, "--file", src_mov, "--asset-id", aid).stdout)
        except (SystemExit, OSError, ValueError, KeyError, IndexError) as e:
            warnings.append("%s: unreadable or incomplete (being re-rendered?); beat render skipped: %s" % (
                rel(mov), str(e).strip().splitlines()[0][:200] if str(e).strip() else type(e).__name__))
            missing_renders.append(b["composition"]["id"] + " (unreadable)")
            continue
        hf_assets[b["id"]] = (aid, r, nf)
        hf_ok.add(b["id"])
    hf = [(b, mov) for b, mov in hf if b["id"] in hf_ok]
    # grade `neutralize`: one measurement span per source clip, the union of its neutralize shots' source time
    spans_nz = {}
    for b in beats:
        for s in shots_by_beat.get(b["id"], []):
            if s.get("grade") == "neutralize" and id(s) in shot_assets:
                wc_ = shot_assets[id(s)][2]
                a_ = wc_["t_in"]
                z_ = a_ + (s["_end_f"] - s["_start_f"]) / FPS * wc_["speed"]
                lo, hi = spans_nz.get(s["_src_rel"], (a_, z_))
                spans_nz[s["_src_rel"]] = (min(lo, a_, z_), max(hi, a_, z_))
    for b in beats:
        for s in shots_by_beat.get(b["id"], []):
            if s.get("grade") == "neutralize" and s.get("_src_rel") in spans_nz:
                s["_neutralize_span"] = spans_nz[s["_src_rel"]]
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

    finish, finish_info = finish_layers(ids, dyn, edit_ms, scan_asset)
    root += finish

    hf_group_id = ids.L()
    hf_layers, hf_info = [], []
    for b, mov in hf:
        aid, imp, nf = hf_assets[b["id"]]
        sf, ef = int(b["start_frame"]), int(b["end_frame"])
        start, end = ms_floor(sf), ms_floor(ef)
        # content(t) = t + offset must pick MOV local frame 6 + (n - sf) at edit frame n:
        # offset = ceil(200 - sf*1000/30) = 200 - floor(sf*1000/30) (6f = exactly 200 ms)
        offset = (HANDLE_F * 1000) // FPS - start
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
              "warnings": warnings + EASE_WARNINGS, "notes": notes, "finish": finish_info,
              "keyframes": {"total": sum(len(e["animator"].get("keyframes", [])) for e in dyn.entries),
                            "linear_or_hold": sum(1 for e in dyn.entries for k in e["animator"].get("keyframes", [])
                                                  if k["easing"].get("type") != "cubicBezier"),
                            "scripts": sum(1 for e in dyn.entries if e["animator"]["type"] == "jsScript")},
              "constants": {"FINISH_GRAIN": FINISH_GRAIN, "FINISH_VIGNETTE": FINISH_VIGNETTE, "FINISH_SCANLINES": FINISH_SCANLINES,
                            "FINISH_CHROMA": FINISH_CHROMA, "NEUTRALIZE": NEUTRALIZE, "PUSH_DEFAULT": PUSH_DEFAULT,
                            "EASES": {"push": EASE_PUSH, "x2": EASE_X2, "bars": EASE_BARS, "whip": [EASE_WHIP_OUT, EASE_WHIP_IN],
                                      "b10_pop_return": EASE_POP_RETURN},
                            "GRAIN_ARCHIVAL": GRAIN_ARCHIVAL, "VIGNETTE_LIGHT": VIGNETTE_LIGHT,
                            "L1": [L1_SCALE, L1_BLUR_PX, L1_SHARP_FRAC, L1_FEATHER], "GRADES": GRADES,
                            "X8_TRAVEL": X8_TRAVEL, "MARGIN_F": MARGIN_F, "WC_RECIPE": WC_RECIPE}}
    REPORT.write_text(json.dumps(report, indent=1) + "\n")
    log("picture: %s committed; %d HF renders, %d footage shots in %d beat groups, max layer id %d; check valid=%s" % (
        rel(PROJECT), len(hf_info), len(shot_info), len({i['beat'] for i in shot_info}), ids.layer, chk.get("valid")))
    log("  missing renders (skipped): %s" % (", ".join(missing_renders) or "none"))
    for w in r.get("warnings", []) + (chk.get("warnings") or []):
        log("  tesseract warning: %s" % (w if isinstance(w, str) else json.dumps(w)))
    for w in warnings + EASE_WARNINGS:
        log("  WARN %s" % w)
    log("  keyframes: %(total)d, all cubic-bezier (linear/hold: %(linear_or_hold)d), %(scripts)d seed scripts" % report["keyframes"])
    for n in notes:
        log("  note %s" % n)
    log("  report: %s" % rel(REPORT))
    if chk.get("valid") is False:
        raise SystemExit("project check failed: %s" % json.dumps(chk.get("diagnostics"))[:2000])


if __name__ == "__main__":
    main()
