"""Build the rough cut: footage, placeholders, VO, end card and watermark. No design text.

Usage: python3 build_roughcut.py [oleary_frames donahoe_frames hill_frames]
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from edit_plan import *

R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W = os.path.join(R, ".tesseract-work")
T = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
P = os.path.join(R, "NikeReel.tsrct")
MEZZ = os.path.join(W, "mezz")
os.makedirs(MEZZ, exist_ok=True)

clip_frames = {"CLIP_OLEARY": 150, "CLIP_DONAHOE": 180, "CLIP_HILL": 90}
if len(sys.argv) == 4:
    clip_frames = dict(zip(["CLIP_OLEARY", "CLIP_DONAHOE", "CLIP_HILL"], map(int, sys.argv[1:])))
tl, endcard_in = timeline(clip_frames)
TOTAL = endcard_in + ENDCARD_FRAMES
ms = lambda f: round(f * 1000 / FPS)
off = {i: tl[i][0] - LINE[i][3] * FPS for i in tl if isinstance(i, int)}   # VO second -> edit frame offset per line


def run(*args):
    r = subprocess.run([T, *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"tsrct {' '.join(args[:2])} failed: {r.stderr[-1500:]}")
    return r.stdout


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


# ---------- segment windows ----------
seg_start = [tl[s[2]][0] for s in SEGMENTS]
seg_end = seg_start[1:] + [endcard_in]
SEG = {s[0]: (s, a, b) for s, a, b in zip(SEGMENTS, seg_start, seg_end)}

# ---------- shots ----------
shots = []   # dict(seg, clip, src, start, end, note)
for name, plan in SHOTS.items():
    (_, _, first, _), a, b = SEG[name]
    starts = []
    for line, cut, clip, src, note in plan:
        starts.append(tl[line][0] if cut is None else round(cut * FPS + off[line]))
    for k, (line, cut, clip, src, note) in enumerate(plan):
        s0 = a if k == 0 else starts[k]
        s1 = starts[k + 1] if k + 1 < len(plan) else b
        if clip == "BURST":
            t = s0
            for bc, bsrc, n in BURST:
                shots.append(dict(seg=name, clip=bc, src=bsrc, start=t, end=t + n, note="burst"))
                t += n
            assert t == s1, (name, t, s1)
            continue
        shots.append(dict(seg=name, clip=clip, src=src, start=s0, end=s1, note=note))

# ---------- mezzanines (trimmed, visually lossless, muted) ----------
def mezz_for(clip, a, b):
    srcf = os.path.join(R, "Sources", "broll", f"{clip}.mp4")
    d = dur(srcf)
    m0, m1 = max(0.0, a - 0.5), min(d, b + 0.5)
    out = os.path.join(MEZZ, f"{clip}_{a:07.2f}.mp4")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{m0:.3f}", "-i", srcf, "-t", f"{m1 - m0:.3f}", "-an",
                        "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], check=True)
    return out, m0

for sh in shots:
    if sh["clip"] == "MISSING":
        continue
    n = sh["end"] - sh["start"]
    if sh["clip"] in REVERSE:
        hi, lo = REVERSE[sh["clip"]]
        a, b = lo, hi
    elif sh["seg"] in FREEZE and sh["clip"] == "B51" and sh["src"] == 36.0:
        fr = round(FREEZE[sh["seg"]]["freeze_vo"] * FPS + off[19])
        sh["freeze_frame"] = fr
        a, b = sh["src"], sh["src"] + (fr - sh["start"]) / FPS
    else:
        a, b = sh["src"], sh["src"] + n / FPS
    sh["mezz"], sh["mezz_start"] = mezz_for(sh["clip"], a, b)

# ---------- project ----------
if os.path.exists(P):
    os.remove(P)
run("project", "create", "--project", P, "--width", "1920", "--height", "1080")
assets = {}
for sh in shots:
    if sh["clip"] == "MISSING":
        continue
    aid = os.path.basename(sh["mezz"])[:-4].replace(".", "_")
    if aid not in assets:
        info = json.loads(run("project", "import-video", "--project", P, "--file", sh["mezz"], "--asset-id", aid))
        assets[aid] = info
    sh["asset"] = aid
vo_path = os.path.join(R, "Sources", "voiceover", "VO_1.07x.wav")
run("project", "import-asset", "--project", P, "--file", vo_path, "--asset-id", "vo_107", "--kind", "audio")
endcard = json.loads(run("project", "import-video", "--project", P, "--file",
                         os.path.join(R, "Sources", "endcard", "EndCard_CTA.mp4"), "--asset-id", "endcard"))
run("project", "import-asset", "--project", P, "--file", os.path.join(R, "Sources", "logo", "RawCanvas_R_white_alpha.png"),
    "--asset-id", "logo_r_white", "--kind", "image")
font = json.loads(run("project", "import-font", "--project", P, "--file", os.path.join(R, "Sources", "fonts", "Archivo[wdth,wght].ttf")))
FONT_FAMILY = font.get("fontFamily") or font["faces"][0]["fontFamily"]
FONT_STYLE = font.get("fontStyle") or font["faces"][0]["fontStyle"]

# ---------- actions ----------
C = "main"
A = []
nid = [1]
def new_id():
    nid[0] += 1
    return nid[0]
def xf(pos=(960, 540), scale=100, anchor=(960, 540), opacity=100):
    return {"anchorPoint": list(anchor), "position": list(pos), "scale": [scale, scale], "rotation": 0, "opacity": opacity}
def punch(clip):
    bug = BUG.get(clip)
    if bug == "tr":
        return xf(pos=(1046, 460), scale=115)
    if bug == "br":
        return xf(pos=(1040, 636), scale=120)
    return xf()
DARK = [18 / 255, 18 / 255, 18 / 255, 1]

# watermark (top of stack): every frame except the end card
A.append({"type": "createFxImageLayer", "compositionId": C, "layerId": new_id(), "name": "RawCanvas watermark (R, 65%)",
          "activeRange": {"start": 0, "duration": ms(endcard_in)},
          "transform": {"anchorPoint": [0, 0], "position": [48, 48], "scale": [84.2, 84.2], "rotation": 0, "opacity": 65},
          "source": {"assetId": "logo_r_white", "fit": "contain"}})

# review slates for non-footage segments (rough cut only)
for (name, kind, first, label), a, b in zip(SEGMENTS, seg_start, seg_end):
    if label:
        A.append({"type": "createFxTextLayer", "compositionId": C, "layerId": new_id(), "name": f"ROUGH-CUT SLATE {name}",
                  "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
                  "transform": {"anchorPoint": [0, 0], "position": [96, 1000], "scale": [100, 100], "rotation": 0, "opacity": 55},
                  "sourceText": {"text": f"[{name}] {label}" + ("  (MISSING: clip not supplied)" if kind == "CLIP" else ""),
                                 "fontFamily": FONT_FAMILY, "fontStyle": FONT_STYLE, "fontSize": 26,
                                 "fillColor": [0.6, 0.6, 0.6, 1], "strokeWidth": 0, "justification": "left"}})
for sh in shots:
    if sh["clip"] == "MISSING":
        A.append({"type": "createFxTextLayer", "compositionId": C, "layerId": new_id(), "name": "ROUGH-CUT SLATE missing B80-B82",
                  "activeRange": {"start": ms(sh["start"]), "duration": ms(sh["end"]) - ms(sh["start"])},
                  "transform": {"anchorPoint": [0, 0], "position": [96, 1000], "scale": [100, 100], "rotation": 0, "opacity": 55},
                  "sourceText": {"text": "[B_L13] And at the gym, Alo and Vuori became the new flex.  (MISSING: B80-B82 not in Drive)",
                                 "fontFamily": FONT_FAMILY, "fontStyle": FONT_STYLE, "fontSize": 26,
                                 "fillColor": [0.6, 0.6, 0.6, 1], "strokeWidth": 0, "justification": "left"}})

# placeholder screens (each its own clean segment)
for (name, kind, first, label), a, b in zip(SEGMENTS, seg_start, seg_end):
    if kind in ("FC", "TC", "CLIP"):
        A.append({"type": "createFxRectLayer", "compositionId": C, "layerId": new_id(),
                  "name": {"FC": f"{name} Full Cover placeholder", "TC": f"{name} Text Centerpiece background",
                           "CLIP": f"{name} live clip slot"}[kind],
                  "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
                  "transform": xf(pos=(0, 0), anchor=(0, 0)), "rect": {"size": [1920, 1080], "fillColor": DARK}})

# B-roll
video_ids = {}
for sh in shots:
    if sh["clip"] == "MISSING":
        continue
    lid = new_id()
    video_ids[id(sh)] = lid
    info = assets[sh["asset"]]
    n_ms = ms(sh["end"]) - ms(sh["start"])
    src_ms = round((sh["src"] - sh["mezz_start"]) * 1000)
    if sh["clip"] in REVERSE:
        hi, lo = REVERSE[sh["clip"]]
        src_ms = round((lo - sh["mezz_start"]) * 1000)
        n_src = round((hi - lo) * 1000)
    else:
        n_src = n_ms
    A.append({"type": "createFxVideoLayer", "compositionId": C, "layerId": lid,
              "name": f"{sh['seg']} {sh['clip']} @{sh['src']:.2f}s - {sh['note']}",
              "activeRange": {"start": ms(sh["start"]), "duration": n_ms},
              "sourceRange": {"start": src_ms, "duration": min(n_src, info["durationMs"] - src_ms)},
              "sourceIntrinsicDuration": info["durationMs"],
              "transform": punch(sh["clip"]),
              "source": {"assetId": sh["asset"], "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
              "volume": 0.0})
    if sh["clip"] in REVERSE:
        hi, lo = REVERSE[sh["clip"]]
        A.append({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": lid, "timeRemap": {
            "keyframes": [{"id": "rev-a", "time": ms(sh["start"]), "value": round((hi - sh["mezz_start"]) * 1000), "easing": {"type": "linear"}},
                          {"id": "rev-b", "time": ms(sh["end"]), "value": round((lo - sh["mezz_start"]) * 1000), "easing": {"type": "linear"}}],
            "before": "inactive", "after": "inactive"}})
    if "freeze_frame" in sh:
        v0 = round((sh["src"] - sh["mezz_start"]) * 1000)
        fz = ms(sh["freeze_frame"])
        vf = v0 + (fz - ms(sh["start"]))
        A.append({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": lid, "timeRemap": {
            "keyframes": [{"id": "fz-a", "time": ms(sh["start"]), "value": v0, "easing": {"type": "linear"}},
                          {"id": "fz-b", "time": fz, "value": vf, "easing": {"type": "linear"}},
                          {"id": "fz-c", "time": ms(sh["end"]), "value": vf, "easing": {"type": "linear"}}],
            "before": "inactive", "after": "inactive"}})

# end card, as supplied, with its own audio
ec_ms = endcard["durationMs"]
A.append({"type": "createFxVideoLayer", "compositionId": C, "layerId": new_id(), "name": "END CARD (attached CTA, as-is)",
          "activeRange": {"start": ms(endcard_in), "duration": ms(TOTAL) - ms(endcard_in)},
          "sourceRange": {"start": 0, "duration": min(ec_ms, ms(TOTAL) - ms(endcard_in))}, "sourceIntrinsicDuration": ec_ms,
          "transform": xf(), "source": {"assetId": "endcard", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
          "volume": 1.0})

# VO, one Audio layer per line (40 ms pre-roll, 60 ms tail)
VO_MS = round(dur(vo_path) * 1000)
for i in [x for x in ORDER if isinstance(x, int)]:
    _, tag, text, s_in, s_out = LINE[i]
    a_ms = ms(tl[i][0]) - 40
    src = round(s_in * 1000) - 40
    if src < 0:
        a_ms, src = a_ms - src, 0
    n = round((s_out - s_in) * 1000) + 100
    A.append({"type": "createFxAudioLayer", "compositionId": C, "layerId": new_id(), "name": f"VO L{i:02d} {text[:40]}",
              "activeRange": {"start": a_ms, "duration": n}, "sourceRange": {"start": src, "duration": min(n, VO_MS - src)},
              "sourceIntrinsicDuration": VO_MS, "source": {"assetId": "vo_107"}, "volume": 1.0})

# base dark under everything
A.append({"type": "createFxRectLayer", "compositionId": C, "layerId": new_id(), "name": "Base dark #121212",
          "activeRange": {"start": 0, "duration": ms(TOTAL)}, "transform": xf(pos=(0, 0), anchor=(0, 0)),
          "rect": {"size": [1920, 1080], "fillColor": DARK}})
A.insert(0, {"type": "updateFxComposition", "compositionId": C, "startTimeMs": 0, "durationMs": ms(TOTAL)})
# root duration is fixed up after apply (apply leaves it at the last visual layer end)

json.dump(A, open(os.path.join(W, "roughcut_actions.json"), "w"), indent=1)
res = json.loads(run("project", "apply", "--project", P, "--actions", os.path.join(W, "roughcut_actions.json")))
print("apply warnings:", res.get("warnings"))
# apply leaves the root duration at the last visual layer's end; set it to the full program length
run("project", "checkout", "--project", P, "--output", os.path.join(W, "editable.json"))
_d = json.load(open(os.path.join(W, "editable.json"))); _d["duration"] = round(ms(TOTAL) / 1000, 3)
json.dump(_d, open(os.path.join(W, "editable.json"), "w"))
run("project", "commit", "--project", P, "--file", os.path.join(W, "editable.json"))

json.dump(dict(clip_frames=clip_frames, timeline={str(k): v for k, v in tl.items()}, endcard_in=endcard_in, total=TOTAL,
               segments=[dict(name=s[0], kind=s[1], label=s[3], start=a, end=b) for s, a, b in zip(SEGMENTS, seg_start, seg_end)],
               shots=[{k: v for k, v in sh.items() if k not in ("mezz",)} for sh in shots]),
          open(os.path.join(W, "roughcut_plan.json"), "w"), indent=1)
print(f"font {FONT_FAMILY}/{FONT_STYLE}; shots {len(shots)}; total {TOTAL} frames = {TOTAL / FPS:.2f} s")
