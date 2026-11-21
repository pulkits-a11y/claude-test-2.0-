"""Full build of the Nike reel in Tesseract (horizontal 1920x1080, 30 fps).

Footage + placeholders + VO (as the rough cut) plus: captions (own group), Text Centerpieces,
the '2021' overlay, the shelf/hype/athlete Half Cover, Stepped look (Posterize Time 10 fps),
film grain, the typography guide's 'BTW' shader on display type, static-shot edge blurs,
the freeze-and-drain Special B-roll, end card and a mastering chain.

Usage: python3 build_edit.py [oleary_frames donahoe_frames hill_frames]
"""
import json, os, subprocess, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from edit_plan import *
from design import Doc, ms, grid, BG, TEXT, GREEN, STEP
from textkit import advance, layout_line

R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W = os.path.join(R, ".tesseract-work")
TS = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
P = os.path.join(R, "NikeReel.tsrct")
MEZZ = os.path.join(W, "mezz")
os.makedirs(MEZZ, exist_ok=True)
random.seed(7)

clip_frames = {k: round((v[3] - v[2]) / v[5] * FPS) for k, v in CLIPS.items()}
if len(sys.argv) == 4:
    clip_frames = dict(zip(["CLIP_OLEARY", "CLIP_DONAHOE", "CLIP_HILL"], map(int, sys.argv[1:])))
tl, endcard_in = timeline(clip_frames)
TOTAL = endcard_in + ENDCARD_FRAMES
off = {i: tl[i][0] - LINE[i][3] * FPS for i in tl if isinstance(i, int)}
WORDS = {int(k): v for k, v in json.load(open(os.path.join(W, "vo_words_aligned.json"))).items()}


def wf(line, i, floor=None):
    """Edit frame a word appears on: its spoken frame snapped down to the 10 fps grid (0-2 frames early),
    never before `floor` (the cut that opens its scene)."""
    f = grid(round(WORDS[line][i]["s"] * FPS + off[line]))
    return f if floor is None else max(floor, f)


def run(*args):
    r = subprocess.run([TS, *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"tsrct {' '.join(args[:2])} failed: {r.stderr[-2500:]}")
    return r.stdout


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


# ================= segments & shots =================
seg_start = [tl[s[2]][0] for s in SEGMENTS]
seg_end = seg_start[1:] + [endcard_in]
SEG = {s[0]: (s, a, b) for s, a, b in zip(SEGMENTS, seg_start, seg_end)}
GRID_CUT_SEGS = {"H_L27"}           # cuts that overlays sync to land on the 10 fps grid

shots = []
for name, plan in SHOTS.items():
    _, a, b = SEG[name]
    starts = []
    for line, cut, clip, src, note in plan:
        f = tl[line][0] if cut is None else round(cut * FPS + off[line])
        starts.append(grid(f) if (name in GRID_CUT_SEGS and cut is not None) else f)
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
CUT = {(sh["seg"], sh["clip"], sh["src"]): sh["start"] for sh in shots}

STATIC = {("B44", 5.0), ("B19", 13.4), ("B21", 10.3), ("B18", 34.2), ("B32", 16.7), ("B31", 15.0), ("B37", 36.0),
          ("B39", 3.3), ("B39", 8.7), ("B35", 20.85), ("B43", 11.3), ("B41", 3.4), ("B19", 4.80), ("B59", 20.7),
          ("B62", 2.0), ("B62", 21.0), ("B74", 12.9), ("B51", 28.0), ("B78", 2.0)}


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
    elif sh["seg"] in FREEZE and sh["clip"] == FREEZE[sh["seg"]]["clip"] and sh["src"] == FREEZE[sh["seg"]]["src"]:
        fr = round(FREEZE[sh["seg"]]["freeze_vo"] * FPS + off[19])
        sh["freeze_frame"] = fr
        a, b = sh["src"], sh["src"] + n / FPS
    else:
        a, b = sh["src"], sh["src"] + n / FPS
    sh["mezz"], sh["mezz_start"] = mezz_for(sh["clip"], a, b)

# ================= project & assets =================
if os.path.exists(P):
    os.remove(P)
run("project", "create", "--project", P, "--width", "1920", "--height", "1080")
assets = {}
for sh in shots:
    if sh["clip"] == "MISSING":
        continue
    aid = os.path.basename(sh["mezz"])[:-4].replace(".", "_")
    if aid not in assets:
        assets[aid] = json.loads(run("project", "import-video", "--project", P, "--file", sh["mezz"], "--asset-id", aid))
    sh["asset"] = aid
vo_path = os.path.join(R, "Sources", "voiceover", "VO_1.07x.wav")
run("project", "import-asset", "--project", P, "--file", vo_path, "--asset-id", "vo_107", "--kind", "audio")
endcard = json.loads(run("project", "import-video", "--project", P, "--file",
                         os.path.join(R, "Sources", "endcard", "EndCard_CTA.mp4"), "--asset-id", "endcard"))
run("project", "import-asset", "--project", P, "--file", os.path.join(R, "Sources", "logo", "RawCanvas_R_white_alpha.png"),
    "--asset-id", "logo_r_white", "--kind", "image")
run("project", "import-asset", "--project", P, "--file", os.path.join(R, "Sources", "caption_scrim.png"), "--asset-id", "caption_scrim", "--kind", "image")
CLIPINFO = {}
for k, name in (("CLIP_OLEARY", "oleary_fast"), ("CLIP_DONAHOE", "donahoe_fast")):
    CLIPINFO[k] = json.loads(run("project", "import-video", "--project", P, "--file", os.path.join(W, "clips", f"{name}.mov"), "--asset-id", name))
MATTES = {}
for name, f in (("m_oleary", "oleary_fast_matte.mp4"), ("m_B19", "B19_matte.mp4"), ("m_B60", "B60_matte.mp4"), ("m_B21", "B21_17_matte.mp4")):
    MATTES[name] = json.loads(run("project", "import-video", "--project", P, "--file", os.path.join(W, "clips", f), "--asset-id", name))
run("project", "import-asset", "--project", P, "--file", os.path.join(W, "clips", "hill.wav"), "--asset-id", "hill_audio", "--kind", "audio")
MGINFO = json.loads(run("project", "import-video", "--project", P, "--file", os.path.join(R, "Sources", "mg", "retail-popup-mg_preview-1.mp4"), "--asset-id", "mg_retail"))
for aid, f in (("tv_frame", "tv/tv_frame_alpha.png"), ("tv_mask", "tv/tv_screen_mask.png"), ("st_footlocker", "stills/retail_footlocker_WN212.png"),
               ("st_nikestore", "stills/retail_nikestore_WN170.png"), ("st_aisle", "stills/retail_aisle_WN250.png"), ("logo_alo", "logos/alo_logo.png"), ("hotspot", "hotspot.png"), ("logo_vuori", "logos/vuori_logo.png")):
    run("project", "import-asset", "--project", P, "--file", os.path.join(R, "Sources", f), "--asset-id", aid, "--kind", "image")
TV_POS, TV_SCALE = (1198, 594), 70      # frames the Donahoe picture-in-picture (fit x 284-836, y 136-700) on the screen
run("project", "import-asset", "--project", P, "--file", os.path.join(R, "Sources", "hill_photo_B60_16s.png"), "--asset-id", "hill_photo", "--kind", "image")
for f in ["Archivo[wdth,wght].ttf", "InstrumentSerif-Regular.ttf", "InstrumentSerif-Italic.ttf"]:
    run("project", "import-font", "--project", P, "--file", os.path.join(R, "Sources", "fonts", f))

D = Doc()
C = D.C


def xf(pos=(960, 540), scale=100, anchor=(960, 540), opacity=100):
    return {"anchorPoint": list(anchor), "position": list(pos), "scale": [scale, scale], "rotation": 0, "opacity": opacity}


CROP = {"B51": ((960, 705), 132), "B52": ((960, 500), 110), "B44": ((1104, 600), 115)}    # B51: ABC7 logo x1530-1720/y835-985 -> crop bottom; B52: "LilJohn504" channel mark top-left -> crop top


def punch(clip):
    if clip in CROP:
        return CROP[clip]
    bug = BUG.get(clip)
    if bug == "tr":
        return (1046, 460), 115
    if bug == "br":
        return (1040, 636), 120
    return (960, 540), 100


# ================= 1. watermark (top) =================
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "RawCanvas watermark (R, 65%, no animation)",
       "activeRange": {"start": 0, "duration": ms(endcard_in)},
       "transform": {"anchorPoint": [0, 0], "position": [104, 74], "scale": [34, 34], "rotation": 0, "opacity": 80},
       "source": {"assetId": "logo_r_white", "fit": "contain"}})

# ================= 2. LOOK adjustment layer (top): grade -> orange push -> glow -> grain -> screen mesh -> vignette =================
gid = D.nid()
D.add({"type": "createFxAdjustmentLayer", "compositionId": C, "layerId": gid, "name": "LOOK: glow > grain > mesh > vignette (grade is on the footage layers)",
       "activeRange": {"start": 0, "duration": ms(endcard_in)}, "transform": xf()})
D.effect(gid, {"type": "glow", "glowThreshold": 75, "glowRadius": 70, "glowIntensity": 0.35})
ge = D.effect(gid, {"type": "grain", "amount": 0.14, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0, "seed": 1})
D.effect_script(gid, ge, "seed", "return Math.floor(input.time.seconds * 24);")
me = D.effect(gid, {"type": "customShader", "name": "screenMesh", "description": "Two Venetian Blinds passes (0 and 90 deg), 3 px, multiplied.",
                    "wgsl": open(os.path.join(W, "shaders", "mesh.wgsl")).read(),
                    "params": [{"name": "periodPx", "description": "Blind width in px.", "min": 1, "max": 12, "default": 3},
                               {"name": "lineFrac", "description": "Dark part of each blind (0..1).", "min": 0, "max": 1, "default": 0.5},
                               {"name": "strength", "description": "Mesh opacity (multiply).", "min": 0, "max": 1, "default": 0.15}]})
TALK = [(tl["CLIP_OLEARY"][0], SEG["A1_OLEARY"][2])] + [(x["start"], x["end"]) for x in shots
        if (x["clip"], x["src"]) in {("B59", 25.6), ("B60", 10.5), ("B62", 21.0), ("B19", 13.4), ("B21", 10.3), ("B18", 34.2)}]
TALK += [(tl["CLIP_DONAHOE"][0], SEG["A2_DONAHOE"][2])]
conds = " || ".join(f"(t >= {a_ / FPS:.3f} && t < {b_ / FPS:.3f})" for a_, b_ in TALK)
D.effect_script(gid, me, "strength", f"var t = input.time.seconds; return ({conds}) ? 0.05 : 0.15;")
D.effect(gid, {"type": "vignette", "amount": 0.28, "feather": 0.7, "radius": 0.8})



def grade_fx(lid):
    """B-roll grade: warm, more contrast, slightly crushed blacks, oranges pushed (footage only, not the charcoal/MG)."""
    D.effect(lid, {"type": "primaryGrade", "semanticVersion": 1, "temperature": 0.22, "tint": 0, "exposure": 0, "contrast": 0.28,
                   "highlights": 0, "shadows": -0.06, "whites": 0.05, "blacks": -0.18, "saturation": 0.04, "vibrance": 0})
    eo = D.nid()
    D.add({"type": "addFxLayerEffect", "compositionId": C, "layerId": lid, "effectId": eo,
           "effect": {"type": "primaryGrade", "semanticVersion": 1, "temperature": 0, "tint": 0, "exposure": 0, "contrast": 0,
                      "highlights": 0, "shadows": 0, "whites": 0, "blacks": 0, "saturation": 0.28, "vibrance": 0},
           "compositingOptions": {"effectOpacity": 1, "maskReferences": [],
                                  "qualifier": {"semanticVersion": 1, "hue": {"center": 25, "width": 34, "softness": 12},
                                                "saturation": {"low": 0.2, "high": 1, "softness": 0.08}, "luminance": {"low": 0.08, "high": 1, "softness": 0.05},
                                                "refine": {"denoise": 2, "blurRadius": 2, "choke": 0}, "invert": False}}})
    D.effect(lid, {"type": "gaussianBlur", "blurriness": 0.75, "repeatEdgePixels": True})

# ================= 3. captions (own group) =================
EASE = {"type": "cubicBezier", "x1": 0.65, "y1": 0.0, "x2": 0.25, "y2": 1.0}     # ease in-out
EOUT = {"type": "cubicBezier", "x1": 0.15, "y1": 0.85, "x2": 0.3, "y2": 1.0}     # ease out
EIN = {"type": "cubicBezier", "x1": 0.6, "y1": 0.0, "x2": 0.9, "y2": 0.4}        # ease in


def kk(lid, prop, keys):
    """Keyframes with explicit easing dicts (frames are layer-local)."""
    D.add({"type": "setFxPropertyKeyframes", "compositionId": C, "property": {"layerId": lid, "propertyType": prop},
           "keyframes": [{"id": f"{prop}-{lid}-{i}", "layerTime": ms(fr), "value": {"type": "float", "value": v},
                          "easing": (e if isinstance(e, dict) else {"type": e})} for i, (fr, v, e) in enumerate(keys)]})


def ekk(lid, eid, param, keys):
    D.add({"type": "setFxLayerEffectParamAnimator", "compositionId": C, "layerId": lid, "effectId": eid, "paramName": param,
           "dependencies": [], "animator": {"type": "keyframes", "enabled": True, "keyframes": [
               {"id": f"{param}-{eid}-{i}", "layerTime": ms(fr), "value": {"type": "float", "value": v},
                "easing": (e if isinstance(e, dict) else {"type": e})} for i, (fr, v, e) in enumerate(keys)]}})


def mblur(lid):
    D.add({"type": "setFxLayerMotionBlur", "compositionId": C, "layerId": lid, "enabled": True})


def zoom_transition(lid, n, base=100.0, end=None, t_in=True, t_out=False, push_to=None):
    """Zoom-blur transition: in = scale x1.14 -> 1 with radial blur clearing (6 f, ease-out);
    out = scale x1.08 with radial blur over the last 4 f (ease-in). Frames are layer-local, n = layer length."""
    end = end if end is not None else (push_to if push_to is not None else base)
    ks, rb = [], []
    if t_in:
        ks += [(0, base * 1.14, "linear"), (6, base, EOUT)]
        rb += [(0, 30, "linear"), (6, 0, EOUT)]
    else:
        ks += [(0, base, "linear")]
        rb += [(0, 0, "linear")]
    if t_out and n >= 14:
        ks += [(n - 4, end, "linear"), (n, end * 1.08, EIN)]
        rb += [(n - 4, 0, "linear"), (n, 24, EIN)]
    elif end != base:
        ks += [(n, end, "linear")]
    kk(lid, "scaleX", ks)
    kk(lid, "scaleY", ks)
    eid = D.effect(lid, {"type": "radialBlur", "centerX": 0.5, "centerY": 0.5, "amount": 0})
    ekk(lid, eid, "amount", rb)
    mblur(lid)


CAP_Y, CAP_SIZE, CAP_W = 556, 50, 640
SPLITS = {8: [(0, 2), (2, 4), (5, 6)], 11: [(0, 2), (2, 5)],
          12: [(0, 3), (3, 6), (6, 9), (9, 11), (11, 13), (13, 16)], 13: [(0, 4), (4, 7), (7, 11)],
          15: [(0, 2), (2, 5), (5, 9)], 19: [(0, 3), (3, 5), (5, 8)], 20: [(0, 2), (2, 5)], 21: [(0, 2), (2, 4), (4, 7)],
          22: [(0, 2), (2, 5)], 26: [(0, 3), (3, 6)]}
KEY = {8: [5], 11: [4], 12: [8, 9, 10], 13: [8, 9, 10], 15: [2], 19: [6, 7], 20: [4], 21: [2, 3], 22: [4], 26: [4, 5]}
HIGHLIGHT = {(11, 4), (19, 7), (22, 4)}
LOGO_W = {"logo_alo": 900, "logo_vuori": __import__("PIL.Image").Image.open(os.path.join(R, "Sources", "logos", "vuori_logo.png")).size[0]}
LOGOS = {(13, 4): ("logo_alo", 76, 51, 8), (13, 6): ("logo_vuori", 150, 33, 2)}   # (asset, width, height, baseline drop)


def seg_start_of(line):
    f = tl[line][0]
    for (s_, a_, b_) in zip(SEGMENTS, seg_start, seg_end):
        if a_ <= f < b_:
            return a_
    return 0


def seg_end_of(line):
    f = tl[line][0]
    for (s, a, b) in zip(SEGMENTS, seg_start, seg_end):
        if a <= f < b:
            return b
    return endcard_in


def caption_group(name):
    g = D.group(name, 0, endcard_in)
    D.effect(g, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.85], "offset": [0, 3], "blurRadius": 10,
                 "spreadRadius": 2, "blendMode": "normal"})
    D.effect(g, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 0], "blurRadius": 42,
                 "spreadRadius": 8, "blendMode": "normal"})
    return g


phrases = []
for line, parts in SPLITS.items():
    for (i0, i1) in parts:
        phrases.append(dict(line=line, i0=i0, i1=i1, start=wf(line, i0, floor=seg_start_of(line))))
phrases.sort(key=lambda p: p["start"])
for k, p in enumerate(phrases):
    nxt = phrases[k + 1]["start"] if k + 1 < len(phrases) else endcard_in
    p["end"] = min(nxt, seg_end_of(p["line"]))
    if (p["line"], p["i0"]) == (8, 2):          # nothing on screen over the eBay shot
        ebay = [x for x in shots if x["clip"] == "B21" and x["src"] == 13.7][0]
        p["end"] = max(p["start"] + 1, min(p["end"], ebay["start"]))
    if (p["line"], p["i0"]) == (8, 5):          # 'ex-CEO,' clears when JOHN / DONAHOE takes over
        p["end"] = max(p["start"] + 1, min(p["end"], wf(8, 6)))

cap = caption_group("CAPTIONS (regular: word-by-word, Blur-to-sharp)")
spec = ("archivo", CAP_SIZE, {"wght": CAP_W, "wdth": 100}, 0)
cap_rows = []
for p in phrases:
    ws = [WORDS[p["line"]][i]["w"] for i in range(p["i0"], p["i1"])]
    xs, Wd = layout_line(ws, [spec] * len(ws))
    lg = {j: LOGOS[(p["line"], i)] for j, i in enumerate(range(p["i0"], p["i1"])) if (p["line"], i) in LOGOS}
    if lg:      # words replaced by logos: lay out by actual widths
        sp_w = advance(" ", *spec)
        widths = [lg[j][1] if j in lg else advance(ws[j], *spec) for j in range(len(ws))]
        xs, acc = [], 0.0
        for wv in widths:
            xs.append(acc); acc += wv + sp_w * 1.3
        Wd = acc - sp_w * 1.3
    x0 = 960 - Wd / 2
    for j, i in enumerate(range(p["i0"], p["i1"])):
        f0 = max(p["start"], wf(p["line"], i))
        if f0 >= p["end"]:
            f0 = p["end"] - 1
        x = x0 + xs[j]
        key = i in KEY.get(p["line"], [])
        word = ws[j]
        if j in lg:
            asset, wl, hl, dy = lg[j]
            img = D.nid()
            D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": img, "name": f"cap L{p['line']}w{i} LOGO {asset}", "parentLayerId": cap,
                   "activeRange": {"start": ms(f0), "duration": ms(p["end"]) - ms(f0)},
                   "transform": {"anchorPoint": [0, 0], "position": [x, CAP_Y - hl + dy], "scale": [round(100 * wl / LOGO_W[asset], 3)] * 2, "rotation": 0, "opacity": 100},
                   "source": {"assetId": asset, "fit": "contain"}})
            D.blur_to_sharp(img)
            cap_rows.append((p["line"], i, word, f0, "Logo (Blur-to-sharp)"))
            continue
        if (p["line"], i) in HIGHLIGHT:
            w = advance(word, *spec)
            dark = D.text(f"cap L{p['line']}w{i} '{word}' inverted (matte)", word, x, CAP_Y, "archivo", CAP_SIZE, BG, f0, p["end"], cap, wght=CAP_W)
            matte = D.rect(f"cap L{p['line']}w{i} wipe matte", x - 5, CAP_Y - 40, w + 15, 54, GREEN, f0, p["end"], cap)
            green = D.text(f"cap L{p['line']}w{i} '{word}'", word, x, CAP_Y, "archivo", CAP_SIZE, GREEN, f0, p["end"], cap, wght=CAP_W)
            box = D.rect(f"cap L{p['line']}w{i} highlight box", x - 5, CAP_Y - 40, w + 15, 54, GREEN, f0, p["end"], cap)
            D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": dark, "matteLayerId": matte, "mode": "alpha"})
            for lid in (matte, box):
                D.keys(lid, "scaleX", [(0, 0, "hold"), (STEP, 50, "hold"), (2 * STEP, 100, "hold")])
            D.keys(green, "opacity", [(0, 40, "hold"), (STEP, 100, "hold")])
            cap_rows.append((p["line"], i, word, f0, "Highlight-box wipe"))
        else:
            lid = D.text(f"cap L{p['line']}w{i} '{word}'", word, x, CAP_Y, "archivo", CAP_SIZE, GREEN if key else TEXT, f0, p["end"], cap, wght=CAP_W)
            D.blur_to_sharp(lid)
            cap_rows.append((p["line"], i, word, f0, "Blur-to-sharp"))


# ================= helpers for centred display rows =================
def row(words, specs, y, cx=960, align="center", x_left=None):
    xs, Wd = layout_line(words, specs)
    x0 = (cx - Wd / 2) if align == "center" else (x_left if align == "left" else cx - Wd)
    return [(x0 + x, y) for x in xs], Wd


def centred_text(name, s, x, y, font, size, color, f0, f1, parent, wght=None, wdth=100):
    w = advance(s, font, size, {"wght": wght, "wdth": wdth} if font == "archivo" else None, 0)
    return D.text(name, s, x, y, font, size, color, f0, f1, parent, wght=wght, wdth=wdth, anchor=(w / 2, -0.34 * size)), w


def scene_group(name, a, b, push=True):
    """Scene group spanning the program; on its own window: zoom-blur in, eased slow push, zoom-blur out."""
    g = D.group(name, 0, endcard_in)
    if push:
        ks = [(a, 114, "linear"), (a + 6, 100, EOUT), (b - 4, 104, "linear"), (b, 112, EIN)]
        kk(g, "scaleX", ks); kk(g, "scaleY", ks)
        eid = D.effect(g, {"type": "radialBlur", "centerX": 0.5, "centerY": 0.5, "amount": 0})
        ekk(g, eid, "amount", [(a, 30, "linear"), (a + 6, 0, EOUT), (b - 4, 0, "linear"), (b, 22, EIN)])
        mblur(g)
    return g


SMALL = ("archivo", 58, {"wght": 520, "wdth": 100}, 0)
plan_rows = []


# ---------- v6 helpers: WHAT HAPPENED style (Archivo 880 / width 80 caps), soft shadow, camera ----------
def WH(size):
    return ("archivo", size, {"wght": 880, "wdth": 80}, 0)


def soft_shadow(g, alpha=0.45, blur=40, spread=4):
    """The light shadow used on the shelf/hype/athlete block (client reference: 'little to no shadow')."""
    D.effect(g, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, alpha], "offset": [0, 0], "blurRadius": blur,
                 "spreadRadius": spread, "blendMode": "normal"})


def fit_size(s, font, size, maxw, axes=None):
    while size > 20 and advance(s, font, size, axes, 0) > maxw:
        size -= 4
    return size


def wh_word(name, s, x, y, size, color, f0, f1, parent, block=False, anim="blur", vox=True):
    if f0 >= f1:
        f0 = f1 - 1
    if block:
        w = advance(s, *WH(size))
        D.rect(f"{name} block", x, y - 0.725 * size, w, 0.745 * size, GREEN, f0, min(f0 + STEP, f1), parent)
        f0 = min(f0 + STEP, f1 - 1)
    lid = D.text(name, s, x, y, "archivo", size, color, f0, f1, parent, wght=880, wdth=80)
    if anim == "blur" and not block:
        D.blur_to_sharp(lid)
    if vox:
        D.vox(lid, size)
    return lid


def wh_random(name, s, x, y, size, color_fn, f0, f1, parent):
    letters = list(s)
    order = [i for i in range(len(letters)) if letters[i] != " "]
    random.shuffle(order)
    for n_, li in enumerate(order):
        pre = "".join(letters[:li])
        lx = x + (advance(pre, *WH(size)) if pre else 0)
        batch = (n_ * 3) // max(1, len(order))
        lid = D.text(f"{name} '{letters[li]}'", letters[li], lx, y, "archivo", size, color_fn(letters[li]),
                     min(f0 + batch * STEP, f1 - 1), f1, parent, wght=880, wdth=80)
        D.vox(lid, size)


def cam_vals(cx, cy, z):
    return {"positionX": 960 - z * (cx - 960), "positionY": 540 - z * (cy - 540), "scaleX": z * 100, "scaleY": z * 100}


def cam_keys(g, keys):
    """keys: list of (frame, vals-dict, easing). Frames are program frames (group spans the program)."""
    clean = []
    for (f, v, e) in keys:
        if clean and f <= clean[-1][0]:
            continue
        clean.append((f, v, e))
    for prop in ("positionX", "positionY", "scaleX", "scaleY"):
        kk(g, prop, [(f, round(v[prop], 3), e) for (f, v, e) in clean])
    mblur(g)

# ================= 4a. TC1: camera follows each word (ease-out, motion blur); retail stores pop in; slide right, then a true cut wide =================
(_, a, b) = SEG["TC1"]
L = WORDS[1]
f_cut = wf(1, 6, a)
big = ("serif", 230, None, 0)
pos_s1, _ = row([w["w"] for w in L[0:4]], [SMALL] * 4, 404)
pos_b, _ = row(["needed", "retail"], [big, big], 618)
pos_s2, _ = row([w["w"] for w in L[6:9]], [SMALL] * 3, 714)


def tc1_build(g, lo, hi, tag):
    """Builds the lockup in group g, visible in [lo, hi). Words that started before lo skip their entrance."""
    out = {}
    for i, (x, y) in zip(range(0, 4), pos_s1):
        f0 = wf(1, i, a)
        if f0 >= hi:
            continue
        lid = D.text(f"TC1{tag} '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, max(f0, lo), hi, g, wght=520); D.vox(lid, 58)
        if f0 >= lo:
            D.blur_to_sharp(lid)
        out[i] = (f0, x + advance(L[i]["w"], *SMALL) / 2, y - 21)
    for k, (i, (x, y)) in enumerate(zip((4, 5), pos_b)):
        f0 = wf(1, i, a)
        if f0 >= hi:
            continue
        lid, w = centred_text(f"TC1{tag} KEY '{L[i]['w']}'", L[i]["w"], x, y, "serif", 230, GREEN, max(f0, lo), hi, g)
        D.vox(lid, 230)
        if f0 >= lo:
            D.pop(lid)
            if k == 0:
                D.flicker_in(lid)
        out[i] = (f0, x + w / 2, y - 78)
    for i, (x, y) in zip(range(6, 9), pos_s2):
        f0 = max(f_cut, wf(1, i, a))
        if f0 >= hi:
            continue
        lid = D.text(f"TC1{tag} '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, max(f0, lo), hi, g, wght=520); D.vox(lid, 58)
        if f0 >= lo:
            D.blur_to_sharp(lid)
    return out


gA = D.group("TC1 A: zoomed camera follows each word (retail stores pop in)", 0, f_cut)
fA = tc1_build(gA, 0, f_cut, "A")
ret_c = fA[5][1:]
f_ret = wf(1, 5, a)
for k, (asset, dx, dy, rot) in enumerate((("st_footlocker", 360, -300, -3), ("st_nikestore", -430, 250, 2.5), ("st_aisle", 520, 215, -2))):
    f0 = f_ret + 1 + 3 * k
    lid = D.nid()
    D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": lid, "name": f"TC1 retail pop-in {asset}", "parentLayerId": gA,
           "activeRange": {"start": ms(f0), "duration": ms(f_cut) - ms(f0)},
           "transform": {"anchorPoint": [540, 310], "position": [ret_c[0] + dx, ret_c[1] + dy], "scale": [40, 40], "rotation": rot, "opacity": 100},
           "source": {"assetId": asset, "fit": "contain"}})
    kk(lid, "scaleX", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    kk(lid, "scaleY", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    D.effect(lid, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 8], "blurRadius": 26, "spreadRadius": 0, "blendMode": "normal"})
keys, prev_arr, prev_v = [], None, None
for i in range(0, 6):
    f, cx, cy = fA[i]
    v = cam_vals(cx, cy, 2.5 if i < 4 else 1.55)
    if prev_v is None:
        keys.append((a, v, "linear")); prev_arr = a
    else:
        depart = max(prev_arr + 1, f - 4)
        if depart > prev_arr:
            keys.append((depart, prev_v, "linear"))
        keys.append((f + 2, v, EOUT)); prev_arr = f + 2
    prev_v = v
slide = dict(prev_v); slide["positionX"] -= 170
keys.append((f_cut, slide, EOUT))                       # zoomed in on 'retail', the camera slides right
cam_keys(gA, keys)
gB = D.group("TC1 B: hard cut to the wide lockup", 0, b)
tc1_build(gB, f_cut, b, "B")
cam_keys(gB, [(f_cut, cam_vals(960, 560, 1.0), "linear"), (b, cam_vals(960, 560, 1.04), EOUT)])
plan_rows.append(("TC1", "Well, turns out, Nike NEEDED RETAIL more than anyone.", "Size-contrast build", "Blur-to-sharp",
                  "Flicker-in; camera follows each word (ease-out, motion blur); 3 retail stills pop in; slide right, hard cut wide", "Cut out", "centered"))

# ================= 4b. TC2: camera follows So / WHAT / HAPPENED? (ease-out, motion blur), slides right, hard cut wide =================
(_, a, b) = SEG["TC2"]
L = WORDS[7]
BIG2 = ("archivo", 196, {"wght": 880, "wdth": 80}, 0)
xs, Wd = layout_line(["WHAT", "HAPPENED?"], [BIG2, BIG2])
x0 = 960 - Wd / 2
y2 = 652
fs, fw, fh = wf(7, 0, a), wf(7, 1, a), wf(7, 2, a)
wW = advance("WHAT", *BIG2)
xh = x0 + xs[1]
letters = list("HAPPENED?")
order = list(range(len(letters))); random.shuffle(order)
f_cut2 = min(b - 6, fh + 3 * STEP + 2)


def tc2_build(g, lo, hi, tag):
    if fs < hi:
        lid = D.text(f"TC2{tag} connector 'So'", "So", x0 + 6, 452, "serif_italic", 120, TEXT, max(fs, lo), hi, g); D.vox(lid, 120)
        if fs >= lo:
            D.ghost_to_solid(lid)
    if fw < hi:
        if fw >= lo:
            D.rect(f"TC2{tag} Block-to-word block (WHAT)", x0, y2 - 142, wW, 146, GREEN, fw, min(fw + STEP, hi), g)
        if fw + STEP < hi:
            lid = D.text(f"TC2{tag} KEY 'WHAT'", "WHAT", x0, y2, "archivo", 196, TEXT, max(fw + STEP, lo), hi, g, wght=880, wdth=80); D.vox(lid, 196)
    for n_, li in enumerate(order):
        f0 = fh + ((n_ * 3) // len(letters)) * STEP
        if f0 >= hi:
            continue
        pre = "".join(letters[:li])
        lx = xh + advance(pre, *BIG2) if pre else xh
        lid = D.text(f"TC2{tag} KEY letter '{letters[li]}'", letters[li], lx, y2, "archivo", 196, GREEN if letters[li] == "?" else TEXT,
                     max(f0, lo), hi, g, wght=880, wdth=80)
        D.vox(lid, 196)


gA = D.group("TC2 A: zoomed camera follows So / WHAT / HAPPENED?", 0, f_cut2)
tc2_build(gA, 0, f_cut2, "A")
v_so = cam_vals(x0 + 60, 410, 2.3)
v_what = cam_vals(x0 + wW / 2, y2 - 72, 1.7)
v_hap = cam_vals(xh + (Wd - xs[1]) / 2, y2 - 72, 1.45)
slide = dict(v_hap); slide["positionX"] -= 150
cam_keys(gA, [(a, v_so, "linear"), (max(a + 1, fw - 3), v_so, "linear"), (fw + 2, v_what, EOUT),
              (max(fw + 3, fh - 3), v_what, "linear"), (fh + 2, v_hap, EOUT), (f_cut2, slide, EOUT)])
gB = D.group("TC2 B: hard cut to the wide lockup", 0, b)
tc2_build(gB, f_cut2, b, "B")
cam_keys(gB, [(f_cut2, cam_vals(960, 560, 1.0), "linear"), (b, cam_vals(960, 560, 1.04), EOUT)])
plan_rows.append(("TC2", "So WHAT HAPPENED?", "Connector + keyword", "Ghost-to-solid (So)",
                  "Block-to-word (WHAT), Random letter reveal (HAPPENED?); camera follows each word, slides right, hard cut wide", "Cut out", "centered"))

# ================= 4c. TC3 in the WHAT HAPPENED style =================
(_, a, b) = SEG["TC3"]
g = scene_group("TC3 Text Centerpiece: and that was only HALF THE PROBLEM.", a, b)
L = WORDS[14]
S3 = fit_size("HALF THE PROBLEM.", "archivo", 190, 1640, {"wght": 880, "wdth": 80})
xs3, W3 = layout_line(["HALF", "THE", "PROBLEM."], [WH(S3)] * 3)
x0 = 960 - W3 / 2
y3 = 652
CONN3 = ("serif_italic", 104, None, 0)
pc, _ = row([L[i]["w"] for i in range(4)], [CONN3] * 4, 452, align="left", x_left=x0 + 6)
for i, (x, y) in zip(range(4), pc):
    lid = D.text(f"TC3 connector '{L[i]['w']}'", L[i]["w"], x, y, "serif_italic", 104, TEXT, wf(14, i, a), b, g); D.vox(lid, 104); D.ghost_to_solid(lid)
wh_word("TC3 KEY 'HALF'", "HALF", x0, y3, S3, GREEN, wf(14, 4, a), b, g, block=True)
wh_random("TC3 'THE'", "THE", x0 + xs3[1], y3, S3, lambda c: TEXT, wf(14, 5, a), b, g)
wh_random("TC3 'PROBLEM.'", "PROBLEM.", x0 + xs3[2], y3, S3, lambda c: GREEN if c == "." else TEXT, wf(14, 6, a), b, g)
plan_rows.append(("TC3", "and that was only HALF THE PROBLEM.", "Connector + keyword (TC2 style)", "Ghost-to-solid (connector)",
                  "Block-to-word (HALF), Random letter reveal (THE PROBLEM.)", "Cut out", "centered"))

# ================= 4e. shelf / hype / athlete / all at once: centred block, no panel, no captions =================
(_, a, b) = SEG["H_L27"]
g = D.group("SHELF / HYPE / ATHLETE / ALL AT ONCE (centred block)", 0, endcard_in)
D.effect(g, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.6], "offset": [0, 0], "blurRadius": 46, "spreadRadius": 10, "blendMode": "normal"})
L = WORDS[27]
CONN = ("archivo", 50, {"wght": 520, "wdth": 100}, 0)
KW = ("serif", 262, None, 0)
c_hype = CUT[("H_L27", "B51", 28.0)]
c_ath = CUT[("H_L27", "B78", 3.1)]
c_all = CUT[("H_L27", "B79", 13.6)]
YC, YK = 418, 642
for conn_idx, word, f_kw, f0, f1 in (((0, 1, 2, 3), "shelf", wf(27, 4, a), a, wf(27, 5, a)),
                                     ((5,), "hype", c_hype, wf(27, 5, a), wf(27, 7, a)),
                                     ((7, 8), "athlete", c_ath, wf(27, 7, a), c_all)):
    conn = [L[i]["w"] for i in conn_idx]
    cw_, kw_ = layout_line(conn, [CONN] * len(conn))[1], advance(word, *KW)
    xl = 960 - max(cw_, kw_) / 2
    pos, _ = row(conn, [CONN] * len(conn), YC, align="left", x_left=xl)
    for i, (x, y) in zip(conn_idx, pos):
        lid = D.text(f"HC connector '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 50, TEXT, max(f0, wf(27, i, a)), f1 if word != "athlete" else c_all, g, wght=520)
        D.blur_to_sharp(lid)
    k_end = c_hype if word == "shelf" else (c_ath if word == "hype" else c_all)
    D.rect(f"HC Block-to-word block ({word})", xl - 2, YK - 170, kw_ + 12, 176, GREEN, f_kw, f_kw + STEP, g)
    lid = D.text(f"HC KEY '{word}'", word, xl, YK, "serif", 262, GREEN, f_kw + STEP, k_end, g); D.vox(lid, 262)
wa = advance("all at once.", "serif_italic", 236, None, 0)
lid = D.text("HC KEY 'all at once.'", "all at once.", 960 - wa / 2, 600, "serif_italic", 236, GREEN, c_all, b, g); D.vox(lid, 236); D.blur_to_sharp(lid, 16)
plan_rows.append(("H_L27", "It gave up the SHELF, the HYPE and the ATHLETE. ALL AT ONCE.", "Connector + keyword (centred block)",
                  "Blur-to-sharp (connectors)", "Block-to-word (shelf/hype/athlete); Blur-to-sharp (all at once.)", "Cut out", "centre"))

# ================= 4f. live clips: full frame, reference-style captions, year mark, flicker; Hill quote =================
CW = json.load(open(os.path.join(W, "clip_words.json")))


def cframe(key, t):
    return tl[key][0] + round((t - CLIPS[key][2]) / CLIPS[key][5] * FPS)


def clip_words(key):
    src = ([w for w in CW["oleary_head"] if w["s"] < 254.95] + [w for w in CW["oleary"] if w["s"] >= 254.95]) if key == "CLIP_OLEARY" else CW["donahoe"]
    out = []
    for w in sorted(src, key=lambda w: w["s"]):
        if not (CLIPS[key][2] - 0.1 <= w["s"] < CLIPS[key][3]) or w["w"] == "-":
            continue
        if w["w"].startswith("-") and out:
            out[-1] = dict(out[-1], w=out[-1]["w"] + w["w"]); continue
        out.append(w)
    return out


REF_S = ("serif_italic", 66, None, 0)
REF_B = ("serif", 156, None, 0)
REF_BI = ("serif_italic", 156, None, 0)


def ref_captions(key, words, groups, slot_a, slot_b, y=690):
    """Reference-style captions: small italic serif connectors + big serif keyword in green, one centred line."""
    cg = caption_group(f"SPECIAL CAPTIONS {key} (reference style)")
    starts = [max(slot_a, grid(cframe(key, words[i0]["s"]))) for (i0, i1, ks, it) in groups]
    for gi, (i0, i1, keys, italic_key) in enumerate(groups):
        f1 = starts[gi + 1] if gi + 1 < len(groups) else slot_b
        ws = words[i0:i1]
        specs = [(REF_BI if italic_key else REF_B) if (i0 + j) in keys else REF_S for j in range(len(ws))]
        xs, Wd = layout_line([w["w"] for w in ws], specs)
        x0 = 960 - Wd / 2
        for j, w in enumerate(ws):
            sp = specs[j]
            fw = min(max(starts[gi], grid(cframe(key, w["s"]))), f1 - 1)
            col = GREEN if (i0 + j) in keys else TEXT
            lid = D.text(f"refcap {key} '{w['w']}'", w["w"], x0 + xs[j], y, sp[0], sp[1], col, fw, f1, cg)
            D.blur_to_sharp(lid, 14 if sp is REF_S else 18)
            if (i0 + j) in keys:
                D.vox(lid, sp[1])


def year_mark(g, text, f0, f1):
    YM = ("archivo", 118, {"wght": 880, "wdth": 80}, 0)
    w = advance(text, *YM)
    x = 1816 - w
    D.rect(f"year mark block ({text})", x, 182 - 86, w, 88, GREEN, f0, f0 + STEP, g)
    lid = D.text(f"year mark '{text}'", text, x, 182, "archivo", 118, TEXT, f0 + STEP, f1, g, wght=880, wdth=80); D.vox(lid, 118)


FLICK_LONG = [(0, 72), (3, 0), (4, 78), (10, 0), (13, 85), (19, 100), (25, 0), (27, 100), (28, 0), (30, 100), (35, 0), (37, 100), (44, 0)]
FLICK_SHORT = [(0, 85), (3, 0), (5, 100), (9, 0), (11, 100), (16, 0)]
FLICK_QUICK = [(0, 100), (2, 0), (3, 100), (5, 0)]      # two hard flashes in 5 frames


def flicker(parent, matte_asset, f0, n, src_ms, transform, pattern, name, dur_ms=None):
    """Glowing warm-white silhouette of the subject (person matte) blinking over the shot."""
    fg = D.nid()
    D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": fg, "name": f"FLICKER {name}", "parentLayerId": parent,
           "activeRange": {"start": ms(f0), "duration": dur_ms or (ms(f0 + n) - ms(f0))},
           "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
    dur_ms = dur_ms or (ms(f0 + n) - ms(f0))
    wr = D.nid()
    D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": wr, "name": f"flicker fill {name}", "parentLayerId": fg,
           "activeRange": {"start": 0, "duration": dur_ms}, "transform": xf(pos=(0, 0), anchor=(0, 0)),
           "rect": {"size": [1920, 1080], "fillColor": [0.96, 0.93, 0.89, 1]}})
    mi = MATTES[matte_asset]
    mv = D.nid()
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": mv, "name": f"flicker matte {name} (MODNet)", "parentLayerId": fg,
           "activeRange": {"start": 0, "duration": dur_ms}, "sourceRange": {"start": src_ms, "duration": min(dur_ms, mi["durationMs"] - src_ms)},
           "sourceIntrinsicDuration": mi["durationMs"], "transform": transform,
           "source": {"assetId": matte_asset, "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
    D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": wr, "matteLayerId": mv, "mode": "luma"})
    D.effect(fg, {"type": "dropShadow", "enabled": True, "color": [1.0, 0.96, 0.9, 0.35], "offset": [0, 0], "blurRadius": 10,
                  "spreadRadius": 0, "blendMode": "normal"})
    D.keys(fg, "opacity", [(t, v, "hold") for t, v in pattern if t < n])


# --- shared: year flash, alternating captions, TV captions ---
YR = 18     # frames the year owns the screen before any caption


def year_flash(text, f0, f1):
    """Hard on / hard off: a huge year over the dimmed shot (no entrance, no exit)."""
    gy = D.group(f"YEAR FLASH {text} (hard in / hard out)", 0, endcard_in)
    size = 470
    w = advance(text, *WH(size))
    D.text(f"year '{text}'", text, 960 - w / 2, 540 + 0.36 * size, "archivo", size, TEXT, f0, f1, gy, wght=880, wdth=80)
    D.rect(f"year flash dim ({text})", 0, 0, 1920, 1080, [BG[0], BG[1], BG[2], 0.80], f0, f1, gy)


def lr_captions(key, words, groups, slot_a, slot_b, maxw=520, xl=110, xr=1810, yc=520):
    """Reference-style captions placed beside the speaker: a left block, then a right block, then the next pair."""
    cg = D.group(f"SPECIAL CAPTIONS {key} (alternating left / right)", 0, endcard_in)
    soft_shadow(cg)
    starts = [max(slot_a, grid(cframe(key, words[g_[0]]["s"]))) for g_ in groups]
    for gi, (i0, i1, keys, side) in enumerate(groups):
        f1 = slot_b
        for gj in range(gi + 1, len(groups)):
            if groups[gj][3] == "L":
                f1 = starts[gj]; break
        ws = words[i0:i1]
        specs = []
        for j, w in enumerate(ws):
            if (i0 + j) in keys:
                specs.append(("serif", fit_size(w["w"], "serif", 156, maxw), None, 0))
            else:
                specs.append(REF_S)
        lines = [[]]
        for j in range(len(ws)):
            if lines[-1]:
                cand = layout_line([ws[k]["w"] for k in lines[-1]] + [ws[j]["w"]], [specs[k] for k in lines[-1]] + [specs[j]])[1]
                if cand > maxw:
                    lines.append([])
            lines[-1].append(j)
        hts = [max(specs[j][1] for j in ln) * 0.95 for ln in lines]
        top = yc - sum(hts) / 2
        for ln, h in zip(lines, hts):
            base = top + h * 0.78
            xs_, lw = layout_line([ws[j]["w"] for j in ln], [specs[j] for j in ln])
            x0 = xl if side == "L" else xr - lw
            for j, xo in zip(ln, xs_):
                sp, w = specs[j], ws[j]
                fw = min(max(starts[gi], grid(cframe(key, w["s"]))), f1 - 1)
                lid = D.text(f"lrcap {key} '{w['w']}'", w["w"], x0 + xo, base, sp[0], sp[1], GREEN if (i0 + j) in keys else TEXT, fw, f1, cg)
                D.blur_to_sharp(lid, 14 if sp is REF_S else 18)
                if (i0 + j) in keys:
                    D.vox(lid, sp[1])
            top += h


def tv_captions(key, words, groups, slot_a, slot_b, y=1012):
    """One centred line under the TV: hard start word by word, subtle glow, no drop shadow."""
    cg = D.group(f"SPECIAL CAPTIONS {key} (under the TV, hard start, subtle glow)", 0, endcard_in)
    D.effect(cg, {"type": "dropShadow", "enabled": True, "color": [0.93, 0.93, 0.93, 0.30], "offset": [0, 0], "blurRadius": 16,
                  "spreadRadius": 0, "blendMode": "normal"})
    SS, SB = ("serif_italic", 50, None, 0), ("serif", 100, None, 0)
    starts = [max(slot_a, grid(cframe(key, words[g_[0]]["s"]))) for g_ in groups]
    for gi, (i0, i1, keys) in enumerate(groups):
        f1 = starts[gi + 1] if gi + 1 < len(groups) else slot_b
        ws = words[i0:i1]
        specs = [SB if (i0 + j) in keys else SS for j in range(len(ws))]
        xs_, lw = layout_line([w["w"] for w in ws], specs)
        for j, w in enumerate(ws):
            fw = min(max(starts[gi], grid(cframe(key, w["s"]))), f1 - 1)
            D.text(f"tvcap {key} '{w['w']}'", w["w"], 960 - lw / 2 + xs_[j], y, specs[j][0], specs[j][1],
                   GREEN if (i0 + j) in keys else TEXT, fw, f1, cg)


# --- O'Leary: 2021 owns the screen, a quick flash on him, then captions beside him (left, right, ...) ---
key = "CLIP_OLEARY"
a, b = tl[key][0], SEG["A1_OLEARY"][2]
info = CLIPINFO[key]
src0 = round((CLIPS[key][2] - CLIPS[key][1]) / CLIPS[key][5] * 1000)
year_flash("2021", a, a + YR)
ow = clip_words(key)
lr_captions(key, ow, [(0, 3, {2}, "L"), (3, 7, {6}, "R"), (7, 10, {9}, "L"), (10, 13, {12}, "R"),
                      (13, 17, {15, 16}, "L"), (17, len(ow), {len(ow) - 2, len(ow) - 1}, "R")], a + YR, b)
gO = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gO, "name": "LIVE CLIP Kevin O'Leary (1.15x, full frame)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
OL_T = xf(pos=(1517, 853), scale=158)     # hides the CNBC chyron (y>770) and stock box (x>1230)
flicker(gO, "m_oleary", YR, 6, src0 + ms(YR), OL_T, FLICK_QUICK, "O'Leary", dur_ms=ms(YR + 6) - ms(YR))
vO = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vO, "name": "O'Leary video + own audio", "parentLayerId": gO,
       "activeRange": {"start": 0, "duration": ms(b) - ms(a)}, "sourceRange": {"start": src0, "duration": min(ms(b) - ms(a), info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
       "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": CLIPS[key][4]})
end_rel = tl[key][1] - a
D.keys(vO, "volume", [(0, 0, "linear"), (2, CLIPS[key][4], "linear"), (end_rel, CLIPS[key][4], "linear"), (end_rel + 3, 0, "linear")])
grade_fx(vO)
zoom_transition(gO, b - a, base=100, t_in=False, t_out=True, push_to=104)
plan_rows.append(("CLIP_OLEARY", "2021 (hard) / This is WHY | you should be WORRIED | about the FUTURE | of a WALMART | or a FOOT LOCKER | They don't NEED RETAIL",
                  "Connector + keyword (reference style), alternating left / right", "Blur-to-sharp", "Blur-to-sharp + texture", "Cut out", "left / right of speaker"))

# --- Donahoe: 2024 owns the screen, then the clip plays inside a vintage TV (CRT look), captions under the TV ---
key = "CLIP_DONAHOE"
a, b = tl[key][0], SEG["A2_DONAHOE"][2]
info = CLIPINFO[key]
src0 = round((CLIPS[key][2] - CLIPS[key][1]) / CLIPS[key][5] * 1000)
year_flash("2024", a, a + YR)
dw = clip_words(key)
tv_captions(key, dw, [(0, 3, {2}), (3, 6, {5}), (6, 10, {8}), (10, len(dw), {len(dw) - 1})], a + YR, b)
gD = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gD, "name": "LIVE CLIP John Donahoe inside the TV (1.15x)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [922, 468], "position": [922, 468], "scale": [100, 100], "rotation": 0, "opacity": 100}})
tvdur = ms(b) - ms(a)
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "TV frame (supplied green-screen still, screen keyed out)",
       "parentLayerId": gD, "activeRange": {"start": 0, "duration": tvdur}, "transform": xf(pos=(0, 0), anchor=(0, 0)),
       "source": {"assetId": "tv_frame", "fit": "contain"}})
mask = D.nid()
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": mask, "name": "TV screen matte", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": tvdur}, "transform": xf(pos=(0, 0), anchor=(0, 0)), "source": {"assetId": "tv_mask", "fit": "contain"}})
gS = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gS, "name": "TV screen content (CRT)", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": tvdur},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": gS, "matteLayerId": mask, "mode": "alpha"})
vD = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vD, "name": "Donahoe video + own audio", "parentLayerId": gS,
       "activeRange": {"start": 0, "duration": tvdur}, "sourceRange": {"start": src0, "duration": min(tvdur, info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": xf(pos=TV_POS, scale=TV_SCALE),
       "source": {"assetId": "donahoe_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": CLIPS[key][4]})
D.rect("TV screen black", 0, 0, 1920, 1080, [0.02, 0.02, 0.02, 1], 0, b - a, gS)
end_rel = tl[key][1] - a
D.keys(vD, "volume", [(0, 0, "linear"), (2, CLIPS[key][4], "linear"), (end_rel, CLIPS[key][4], "linear"), (end_rel + 3, 0, "linear")])
grade_fx(gS)
D.effect(gS, {"type": "chromaticAberration", "amount": 0.15, "direction": 0})
D.effect(gS, {"type": "customShader", "name": "crtScanlines", "description": "CRT scanlines with a slow rolling band.",
              "wgsl": open(os.path.join(W, "shaders", "crt.wgsl")).read(),
              "params": [{"name": "animationTime", "description": "Engine clock (s).", "min": 0, "max": 3600, "default": 0},
                         {"name": "linePx", "description": "Scanline period in px.", "min": 1, "max": 20, "default": 3.0},
                         {"name": "strength", "description": "Scanline darkness 0..1.", "min": 0, "max": 1, "default": 0.38},
                         {"name": "roll", "description": "Rolling band speed (screens/s).", "min": 0, "max": 2, "default": 0.35}]})
ng = D.effect(gS, {"type": "grain", "amount": 0.30, "size": 1.4, "softness": 0.3, "aspectRatio": 1.0, "seed": 6})
D.effect_script(gS, ng, "seed", "return Math.floor(input.time.seconds * 24);")
D.effect(gS, {"type": "glow", "glowThreshold": 60, "glowRadius": 14, "glowIntensity": 0.5})
D.effect(gD, {"type": "vignette", "amount": 0.55, "feather": 0.6, "radius": 0.75})
ng2 = D.effect(gD, {"type": "grain", "amount": 0.12, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0, "seed": 9})
D.effect_script(gD, ng2, "seed", "return Math.floor(input.time.seconds * 24);")
zk = [(0, 100, "linear"), (b - a, 118, EASE)]
kk(gD, "scaleX", zk); kk(gD, "scaleY", zk)
plan_rows.append(("CLIP_DONAHOE", "2024 (hard) / we had OVER-ROTATED / away from WHOLESALE / a little MORE than / we INTENDED",
                  "Connector + keyword (reference style), one line under the TV", "Hard start", "Hard start + subtle glow", "Cut out", "under the TV"))

# --- Hill: WHAT HAPPENED style quote, big photo + title, camera follows each element (ease-out, motion blur) ---
key = "CLIP_HILL"
a = tl[key][0]; b = SEG["TC4_HILL"][2]
g = D.group("TC4 Hill quote (camera follows: photo, WE LOST OUR, OBSESSION, wide)", 0, endcard_in)
hw = [w for w in CW["hill"] if CLIPS[key][2] - 0.1 <= w["s"] < CLIPS[key][3]]
fr = [max(a, grid(cframe(key, w["s"]))) for w in hw]
ph = D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "Hill photo (B60 still, large)", "parentLayerId": g,
            "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
            "transform": {"anchorPoint": [0, 0], "position": [190, 190], "scale": [82, 82], "rotation": 0, "opacity": 100},
            "source": {"assetId": "hill_photo", "fit": "contain"}})
D.blur_to_sharp(ph["layerId"], 14)
D.effect(ph["layerId"], {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.5], "offset": [0, 10], "blurRadius": 30, "spreadRadius": 0, "blendMode": "normal"})
wh_word("Hill title 'ELLIOTT HILL'", "ELLIOTT HILL", 192, 812, 78, TEXT, a + STEP, b, g)
t2 = D.text("Hill title 'NIKE CEO'", "NIKE CEO", 196, 866, "archivo", 36, GREEN, a + 2 * STEP, b, g, wght=600, tracking=80); D.blur_to_sharp(t2)
q = D.text("Hill quote mark", "“", 812, 488, "serif", 240, GREEN, a, b, g); D.vox(q, 240); D.ghost_to_solid(q)
QX, Q1 = 900, 470
xsq, Wq1 = layout_line([w["w"].upper() for w in hw[0:3]], [WH(96)] * 3)
for j, w in enumerate(hw[0:3]):
    wh_word(f"Hill '{w['w'].upper()}'", w["w"].upper(), QX + xsq[j], Q1, 96, TEXT, fr[j], b, g)
SO = fit_size("OBSESSION", "archivo", 210, 860, {"wght": 880, "wdth": 80})
Q2 = Q1 + round(0.725 * SO) + 22        # tight leading between the three lines
Q3 = Q2 + round(0.725 * 96) + 22
WO = advance("OBSESSION", *WH(SO))
wh_word("Hill KEY 'OBSESSION'", "OBSESSION", QX - 6, Q2, SO, GREEN, fr[3], b, g, block=True)
last = hw[5]["w"].upper().rstrip(".") + ".”"
xsq3, Wq3 = layout_line([hw[4]["w"].upper(), last], [WH(96)] * 2)
for j, (w, s_) in enumerate(zip(hw[4:6], (hw[4]["w"].upper(), last))):
    wh_word(f"Hill '{s_}'", s_, QX + xsq3[j], Q3, 96, TEXT, fr[4 + j], b, g)
cam_keys(g, [(a, cam_vals(452, 452, 1.55), "linear"),
             (a + 5, cam_vals(452, 452, 1.55), "linear"),
             (a + 11, cam_vals(QX + Wq1 / 2, Q1 - 35, 1.6), EOUT),
             (max(a + 12, fr[3] - 3), cam_vals(QX + Wq1 / 2, Q1 - 35, 1.6), "linear"),
             (max(a + 13, fr[3] + 3), cam_vals(QX + WO / 2, Q2 - 0.36 * SO, 1.3), EOUT),
             (max(a + 14, fr[4] - 2), cam_vals(QX + WO / 2, Q2 - 0.36 * SO, 1.3), "linear"),
             (max(a + 15, fr[4] + 5), cam_vals(960, 530, 1.0), EOUT),
             (b, cam_vals(960, 530, 1.03), EOUT)])
D.add({"type": "createFxAudioLayer", "compositionId": C, "layerId": D.nid(), "name": "LIVE AUDIO Elliott Hill (earnings call)",
       "activeRange": {"start": ms(a), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceRange": {"start": round((CLIPS[key][2] - CLIPS[key][1]) * 1000), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceIntrinsicDuration": 2800, "source": {"assetId": "hill_audio"}, "volume": CLIPS[key][4]})
plan_rows.append(("TC4", "“WE LOST OUR OBSESSION WITH SPORT.” + photo, ELLIOTT HILL / NIKE CEO", "Connector + keyword (TC2 style)",
                  "Blur-to-sharp", "Block-to-word (OBSESSION); camera follows each element", "Cut out", "photo left, quote right"))

# ================= 4g. FC2: the supplied MG (retail pop-up) + text placed in its empty space =================
(_, a, b) = SEG["FC2"]
mg_start = tl[10][0] - 27          # DSW lands on "DSW", Dillard's on "Dillard's", Foot Locker on "Foot Locker"
sg = D.group("FC2 MG TEXT (placed next to what the MG is showing)", 0, endcard_in)
soft_shadow(sg)
# (line, word indices, x, baseline y, size, key word indices, align, max width)
PH = [(9, [0, 1], 960, 600, 150, {1}, "center", 1400),
      (9, [2, 3], 1110, 470, 120, set(), "left", 720),
      (9, [4, 5], 1110, 610, 120, {5}, "left", 720),
      (10, [0, 1, 2], 90, 200, 104, set(), "left", 790),
      (10, [3, 4, 5], 90, 200, 104, set(), "left", 610),
      (10, [6], 450, 235, 140, {6}, "center", 500),
      (10, [7, 8], 1000, 108, 88, {8}, "center", 640),
      (10, [9, 10, 11], 1840, 285, 84, {11}, "right", 600),
      (10, [12, 13, 14], 1840, 285, 84, {13, 14}, "right", 620)]
ph_starts = [max(a, wf(ln, ix[0])) for (ln, ix, *_r) in PH]
for k, (ln, ix, x, y, size, keys, align, maxw) in enumerate(PH):
    f1 = b if k == len(PH) - 1 else (ph_starts[k + 2] if k == 1 else ph_starts[k + 1])
    ws = [WORDS[ln][i]["w"].upper() for i in ix]
    size = fit_size(" ".join(ws), "archivo", size, maxw, {"wght": 880, "wdth": 80})
    xs_, lw = layout_line(ws, [WH(size)] * len(ws))
    x0 = {"left": x, "center": x - lw / 2, "right": x - lw}[align]
    for j, i in enumerate(ix):
        fw = min(max(ph_starts[k], wf(ln, i)), f1 - 1)
        wh_word(f"FC2 '{ws[j]}'", ws[j], x0 + xs_[j], y, size, GREEN if i in keys else TEXT, fw, f1, sg, block=i in keys)
mgi = MGINFO
lid = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": lid, "name": "FC2 MG: retail pop-up (supplied); holds its empty first frame",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)}, "sourceRange": {"start": 0, "duration": mgi["durationMs"]},
       "sourceIntrinsicDuration": mgi["durationMs"], "transform": xf(),
       "source": {"assetId": "mg_retail", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
D.add({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": lid, "timeRemap": {
    "keyframes": [{"id": "mg-a", "time": ms(a), "value": 0, "easing": {"type": "linear"}},
                  {"id": "mg-b", "time": ms(mg_start), "value": 0, "easing": {"type": "linear"}},
                  {"id": "mg-c", "time": ms(b), "value": min(mgi["durationMs"] - 34, ms(b) - ms(mg_start)), "easing": {"type": "linear"}}],
    "before": "inactive", "after": "inactive"}})
plan_rows.append(("FC2", "HIS PLAN? / CUT OUT / THE MIDDLEMAN. / NIKE PULLED OUT / OF STORES LIKE / DSW / AND DILLARD'S, / AND SENT LESS / TO FOOT LOCKER.",
                  "Caption line (special, TC2 style), placed in the MG's empty space", "Blur-to-sharp", "Block-to-word", "Cut out", "context dependent"))

# ================= 4h. JOHN / DONAHOE (left, TC2 style) with a quick flash on him =================
shj = [x for x in shots if x["clip"] == "B21" and x["src"] == 17.0][0]
gj = D.group("SPECIAL TEXT: JOHN / DONAHOE", 0, endcard_in)
soft_shadow(gj)
SJ = fit_size("DONAHOE.", "archivo", 210, 640, {"wght": 880, "wdth": 80})
wh_word("JOHN", "JOHN", 130, 500, SJ, TEXT, max(shj["start"], wf(8, 6)), shj["end"], gj, block=True)
wh_random("DONAHOE.", "DONAHOE.", 130, 500 + 0.84 * SJ, SJ, lambda c: GREEN if c == "." else TEXT, max(shj["start"], wf(8, 7)), shj["end"], gj)

# ================= 5. placeholder screens =================
GRUNGE = []
for (name, kind, first, label), a, b in zip(SEGMENTS, seg_start, seg_end):
    if kind in ("FC", "TC", "CLIP"):
        nm = {"FC": f"{name} FULL COVER PLACEHOLDER (blank, VO + watermark)", "TC": f"{name} Text Centerpiece background",
              "CLIP": f"{name} live clip background"}[kind]
        if kind == "FC" and name != "FC2":
            w_mg = advance("MG", "archivo", 140, {"wght": 800, "wdth": 100}, 0)
            D.text(f"{name} preview label MG", "MG", 960 - w_mg / 2, 590, "archivo", 140, TEXT, a, b, wght=800)
        if kind in ("FC", "TC"):
            hs = D.nid()
            D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": hs, "name": f"{name} soft hotspot behind text",
                   "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)}, "transform": xf(pos=(0, 0), anchor=(0, 0), opacity=7),
                   "source": {"assetId": "hotspot", "fit": "contain"}})
            gr = D.nid()
            D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": gr, "name": f"{name} GRUNGE (procedural stand-in for Grunge 353), Soft Light 20%",
                   "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
                   "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 20},
                   "rect": {"size": [1920, 1080], "fillColor": [0.5, 0.5, 0.5, 1]}})
            D.effect(gr, {"type": "turbulentNoise", "fractalType": "rocky", "contrast": 180, "brightness": -5, "complexity": 7,
                          "scale": 260, "subInfluence": 75, "evolution": 0})
            kk(gr, "scaleX", [(0, 100, "linear"), (b - a, 105, "linear")])
            kk(gr, "scaleY", [(0, 100, "linear"), (b - a, 105, "linear")])
            GRUNGE.append(gr)
        D.rect(nm, 0, 0, 1920, 1080, BG, a, b)

# ================= 6. footage: one group per shot (punch-in, push, transitions, flicker, 3D chart) =================
FLICKER_SHOTS = {("B19", 4.80): ("m_B19", FLICK_QUICK), ("B60", 10.5): ("m_B60", FLICK_QUICK), ("B21", 17.0): ("m_B21", FLICK_QUICK)}
seg_shots = {}
for sh in shots:
    seg_shots.setdefault(sh["seg"], []).append(sh)
line_starts = {tl[i][0] for i in tl if isinstance(i, int)}
for segname, lst in seg_shots.items():
    for k, sh in enumerate(lst):
        n = sh["end"] - sh["start"]
        gdur = ms(sh["end"]) - ms(sh["start"])
        first, last = k == 0, k == len(lst) - 1
        new_line = any(sh["start"] <= f <= sh["start"] + 2 for f in line_starts)
        info = assets[sh["asset"]]
        src_ms = round((sh["src"] - sh["mezz_start"]) * 1000)
        n_src = ms(n)
        if sh["clip"] in REVERSE:
            hi, lo = REVERSE[sh["clip"]]
            src_ms, n_src = round((lo - sh["mezz_start"]) * 1000), round((hi - lo) * 1000)
        pos, sc = punch(sh["clip"])
        chart = (sh["clip"], sh["src"]) == ("B74", 12.9)
        sgp = D.nid()
        D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": sgp, "name": f"{segname} {sh['clip']} @{sh['src']:.2f}s - {sh['note']}",
               "activeRange": {"start": ms(sh["start"]), "duration": ms(sh["end"]) - ms(sh["start"])},
               "transform": {"anchorPoint": [960, 540], "position": list(pos) if not chart else [1180, 610], "scale": [sc, sc] if not chart else [178, 178],
                             "rotation": 0 if not chart else -6, "opacity": 100, **({"rotationX": 20, "rotationY": -6} if chart else {})}})
        if chart:   # 3D tilt + diagonal pan + highlighter on the "Nike" legend
            hl = D.nid()
            D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": hl, "name": "highlighter on 'Nike' legend", "parentLayerId": sgp,
                   "activeRange": {"start": 0, "duration": gdur}, "transform": xf(pos=(456, 293), anchor=(0, 0)),
                   "rect": {"size": [100, 44], "fillColor": [GREEN[0], GREEN[1], GREEN[2], 0.6], "roundness": 8}})
            kk(hl, "scaleX", [(0, 0, "linear"), (6, 0, "linear"), (13, 100, EOUT)])
        if (sh["clip"], sh["src"]) in FLICKER_SHOTS:
            m_asset, patt = FLICKER_SHOTS[(sh["clip"], sh["src"])]
            flicker(sgp, m_asset, 0, n, src_ms, xf(), patt, f"{sh['clip']}@{sh['src']}", dur_ms=gdur)
        lid = D.nid()
        D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": lid, "name": f"{sh['clip']} @{sh['src']:.2f}s", "parentLayerId": sgp,
               "activeRange": {"start": 0, "duration": gdur},
               "sourceRange": {"start": src_ms, "duration": min(n_src if sh["clip"] in REVERSE else gdur, info["durationMs"] - src_ms)},
               "sourceIntrinsicDuration": info["durationMs"], "transform": xf(),
               "source": {"assetId": sh["asset"], "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
               "volume": 0.0})
        grade_fx(lid)
        if sh["clip"] == "B79":   # darken the pale mint so 'all at once.' and the watermark read
            D.effect(lid, {"type": "hueSaturation", "hue": 0, "saturation": -10, "lightness": -45, "colorize": False,
                           "colorizeHue": 0, "colorizeSaturation": 0, "colorizeLightness": 0})
        if sh["clip"] in REVERSE:
            hi, lo = REVERSE[sh["clip"]]
            D.add({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": lid, "timeRemap": {
                "keyframes": [{"id": f"rev-{lid}-a", "time": 0, "value": round((hi - sh["mezz_start"]) * 1000), "easing": {"type": "linear"}},
                              {"id": f"rev-{lid}-b", "time": gdur, "value": round((lo - sh["mezz_start"]) * 1000), "easing": {"type": "linear"}}],
                "before": "inactive", "after": "inactive"}})
        if "freeze_frame" in sh:      # drain to B&W while the shot keeps playing (lands on 'hype')
            rel = sh["freeze_frame"] - sh["start"]
            hs = D.effect(lid, {"type": "hueSaturation", "hue": 0, "saturation": 0, "lightness": 0, "colorize": False,
                                "colorizeHue": 0, "colorizeSaturation": 0, "colorizeLightness": 0})
            D.effect_keys(lid, hs, "saturation", [(rel, 0, "hold"), (rel + 3, -34, "hold"), (rel + 6, -67, "hold"), (rel + 9, -100, "hold")])
        static = (sh["clip"], sh["src"]) in STATIC
        if chart:
            kk(sgp, "positionX", [(0, 1180, "linear"), (n, 1060, EOUT)])     # diagonal pan across the tilted plane
            kk(sgp, "positionY", [(0, 610, "linear"), (n, 520, EOUT)])
            mblur(sgp)
        else:
            zoom_transition(sgp, n, base=sc, t_in=(first or new_line), t_out=last and segname != "H_L27",
                            push_to=round(sc * 1.05, 2) if static else None)

ec_ms = endcard["durationMs"]
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": D.nid(), "name": "END CARD (attached CTA, muted)",
       "activeRange": {"start": ms(endcard_in), "duration": ms(TOTAL) - ms(endcard_in)},
       "sourceRange": {"start": 0, "duration": min(ec_ms, ms(TOTAL) - ms(endcard_in))}, "sourceIntrinsicDuration": ec_ms,
       "transform": xf(), "source": {"assetId": "endcard", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
       "volume": 0.0})
D.add({"type": "setFxCompositionMotionBlur", "compositionId": C, "settings": {"enabled": True, "shutterAngle": 180, "shutterPhase": -90,
                                                                              "samplesPerFrame": 8, "adaptiveSampleLimit": 48}})

# ================= 7. VO =================
VO_MS = round(dur(vo_path) * 1000)
for i in [x for x in ORDER if isinstance(x, int)]:
    _, tag, text, s_in, s_out = LINE[i]
    a_ms = ms(tl[i][0]) - 40
    src = round(s_in * 1000) - 40
    if src < 0:
        a_ms, src = a_ms - src, 0
    n = round((s_out - s_in) * 1000) + 100
    D.add({"type": "createFxAudioLayer", "compositionId": C, "layerId": D.nid(), "name": f"VO L{i:02d} {text[:40]}",
           "activeRange": {"start": a_ms, "duration": n}, "sourceRange": {"start": src, "duration": min(n, VO_MS - src)},
           "sourceIntrinsicDuration": VO_MS, "source": {"assetId": "vo_107"}, "volume": 1.0})

# ================= 8. base =================
D.rect("Base dark #121212", 0, 0, 1920, 1080, BG, 0, TOTAL)

# ================= 9. master: light VO cleanup + loudness =================
MASTER_GAIN_DB = float(os.environ.get("MASTER_GAIN_DB", "10.9"))
for eff in ({"type": "compressor", "thresholdDb": -26, "ratio": 2.2, "attackMs": 12, "releaseMs": 140, "kneeDb": 6, "makeupDb": 0, "mix": 1.0},
            {"type": "deEsser", "frequencyHz": 6200, "thresholdDb": 6, "reductionDb": 4},
            {"type": "limiter", "ceilingDb": -1.6, "inputDb": MASTER_GAIN_DB, "lookaheadMs": 5, "releaseMs": 80, "stereoLink": 1, "truePeak": True}):
    D.add({"type": "addFxMixerEffect", "compositionId": C, "layerId": None, "effect": {"id": D.nid(), "enabled": True, "effect": eff}})

D.A.insert(0, {"type": "updateFxComposition", "compositionId": C, "startTimeMs": 0, "durationMs": ms(TOTAL)})
json.dump(D.A, open(os.path.join(W, "edit_actions.json"), "w"), indent=1)
res = json.loads(run("project", "apply", "--project", P, "--actions", os.path.join(W, "edit_actions.json")))
print("apply warnings:", res.get("warnings"))
run("project", "checkout", "--project", P, "--output", os.path.join(W, "editable.json"))
_d = json.load(open(os.path.join(W, "editable.json"))); _d["duration"] = round(ms(TOTAL) / 1000, 3)
def _blend(o):
    if isinstance(o, dict):
        n = o.get("name", "")
        if "GRUNGE" in n: o["blendMode"] = "softLight"
        elif "soft hotspot" in n: o["blendMode"] = "screen"
        for v in o.values(): _blend(v)
    elif isinstance(o, list):
        for v in o: _blend(v)
_blend(_d)
json.dump(_d, open(os.path.join(W, "editable.json"), "w"))
run("project", "commit", "--project", P, "--file", os.path.join(W, "editable.json"))
json.dump(dict(clip_frames=clip_frames, timeline={str(k): v for k, v in tl.items()}, endcard_in=endcard_in, total=TOTAL,
               segments=[dict(name=s[0], kind=s[1], label=s[3], start=a, end=b) for s, a, b in zip(SEGMENTS, seg_start, seg_end)],
               shots=[{k: v for k, v in sh.items() if k != "mezz"} for sh in shots], captions=cap_rows, typography=plan_rows),
          open(os.path.join(W, "edit_plan_out.json"), "w"), indent=1)
print(f"actions {len(D.A)}; shots {len(shots)}; caption words {len(cap_rows)}; total {TOTAL} f = {TOTAL / FPS:.2f} s")
