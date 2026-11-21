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
for name, f in (("m_oleary", "oleary_fast_matte.mp4"), ("m_B19", "B19_matte.mp4"), ("m_B60", "B60_matte.mp4")):
    MATTES[name] = json.loads(run("project", "import-video", "--project", P, "--file", os.path.join(W, "clips", f), "--asset-id", name))
run("project", "import-asset", "--project", P, "--file", os.path.join(W, "clips", "hill.wav"), "--asset-id", "hill_audio", "--kind", "audio")
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

# ================= 2. film grain over the whole frame (Stepped look texture) =================
gid = D.nid()
D.add({"type": "createFxAdjustmentLayer", "compositionId": C, "layerId": gid, "name": "LOOK: film grain (stepped 10 fps)",
       "activeRange": {"start": 0, "duration": ms(endcard_in)}, "transform": xf()})
ge = D.effect(gid, {"type": "grain", "amount": 0.09, "size": 1.5, "softness": 0.55, "aspectRatio": 1.0, "seed": 1})
D.effect_script(gid, ge, "seed", "return Math.floor(input.time.seconds * 10);")

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
SPLITS = {8: [(0, 2), (2, 4), (4, 6), (6, 8)], 11: [(0, 2), (2, 5)],
          12: [(0, 3), (3, 6), (6, 9), (9, 11), (11, 13), (13, 16)], 13: [(0, 4), (4, 7), (7, 11)],
          15: [(0, 2), (2, 5), (5, 9)], 19: [(0, 3), (3, 5), (5, 8)], 20: [(0, 2), (2, 5)], 21: [(0, 2), (2, 4), (4, 7)],
          22: [(0, 2), (2, 5)], 26: [(0, 3), (3, 6)]}
KEY = {8: [4, 5], 11: [4], 12: [8, 9, 10], 13: [8, 9, 10], 15: [2], 19: [6, 7], 20: [4], 21: [2, 3], 22: [4], 26: [4, 5]}
HIGHLIGHT = {(11, 4), (19, 7), (22, 4)}


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

cap = caption_group("CAPTIONS (regular: word-by-word, Blur-to-sharp)")
spec = ("archivo", CAP_SIZE, {"wght": CAP_W, "wdth": 100}, 0)
cap_rows = []
for p in phrases:
    ws = [WORDS[p["line"]][i]["w"] for i in range(p["i0"], p["i1"])]
    xs, Wd = layout_line(ws, [spec] * len(ws))
    x0 = 960 - Wd / 2
    for j, i in enumerate(range(p["i0"], p["i1"])):
        f0 = max(p["start"], wf(p["line"], i))
        if f0 >= p["end"]:
            f0 = p["end"] - 1
        x = x0 + xs[j]
        key = i in KEY.get(p["line"], [])
        word = ws[j]
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

# ================= 4a. TC1 with camera moves (zoom to each word, eased, motion blur) =================
(_, a, b) = SEG["TC1"]
g = D.group("TC1 Text Centerpiece (camera follows each word)", 0, endcard_in)
L = WORDS[1]
focus = []    # (frame, centre x, centre y, zoom)
pos, _ = row([w["w"] for w in L[0:4]], [SMALL] * 4, 404)
for i, (x, y) in zip(range(0, 4), pos):
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(1, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
    focus.append((wf(1, i, a), x + advance(L[i]["w"], *SMALL) / 2, y - 21, 2.5))
big = ("serif", 230, None, 0)
pos, _ = row(["needed", "retail"], [big, big], 618)
for k, (i, (x, y)) in enumerate(zip((4, 5), pos)):
    lid, w = centred_text(f"TC1 KEY '{L[i]['w']}'", L[i]["w"], x, y, "serif", 230, GREEN, wf(1, i, a), b, g)
    D.vox(lid, 230); D.pop(lid)
    if k == 0:
        D.flicker_in(lid)
    focus.append((wf(1, i, a), x + w / 2, y - 78, 1.55))
pos, _ = row([w["w"] for w in L[6:9]], [SMALL] * 3, 714)
for i, (x, y) in zip(range(6, 9), pos):
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(1, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
    focus.append((wf(1, i, a), x + advance(L[i]["w"], *SMALL) / 2, y - 21, 2.1 if i < 8 else 1.0))
focus[-1] = (focus[-1][0], 960, 560, 1.0)       # pull back to the whole lockup on "anyone."
cam = {"positionX": [], "positionY": [], "scaleX": [], "scaleY": []}
prev = None
for (f, wx, wy, z) in focus:
    v = {"positionX": 960 - z * (wx - 960), "positionY": 540 - z * (wy - 540), "scaleX": z * 100, "scaleY": z * 100}
    arrive = f + 2
    if prev is None:
        for kname in cam: cam[kname].append((a, v[kname], "linear"))
    else:
        depart = max(prev[0] + 1, f - 5)
        if depart < arrive:
            for kname in cam:
                if depart > prev[0]: cam[kname].append((depart, prev[1][kname], "linear"))
                cam[kname].append((arrive, v[kname], EASE))
    prev = (arrive if prev is not None else a, v)
for kname, ks in cam.items():
    kk(g, kname, ks)
mblur(g)
plan_rows.append(("TC1", "Well, turns out, Nike NEEDED RETAIL more than anyone.", "Size-contrast build", "Blur-to-sharp",
                  "Flicker-in; camera zooms to each word (eased, motion blur)", "Cut out", "centered"))

# ================= 4b. TC2 =================
(_, a, b) = SEG["TC2"]
g = scene_group("TC2 Text Centerpiece: So WHAT HAPPENED?", a, b)
L = WORDS[7]
BIG2 = ("archivo", 196, {"wght": 880, "wdth": 80}, 0)
xs, Wd = layout_line(["WHAT", "HAPPENED?"], [BIG2, BIG2])
x0 = 960 - Wd / 2
y2 = 652
lid = D.text("TC2 connector 'So'", "So", x0 + 6, 452, "serif_italic", 120, TEXT, wf(7, 0, a), b, g); D.vox(lid, 120); D.ghost_to_solid(lid)
fw = wf(7, 1, a)
wW = advance("WHAT", *BIG2)
D.rect("TC2 Block-to-word block (WHAT)", x0, y2 - 142, wW, 146, GREEN, fw, fw + STEP, g)
lid = D.text("TC2 KEY 'WHAT'", "WHAT", x0, y2, "archivo", 196, TEXT, fw + STEP, b, g, wght=880, wdth=80); D.vox(lid, 196)
fh = wf(7, 2, a)
xh = x0 + xs[1]
letters = list("HAPPENED?")
order = list(range(len(letters))); random.shuffle(order)
for n_, li in enumerate(order):
    pre = "".join(letters[:li])
    lx = xh + advance(pre, *BIG2) if pre else xh
    batch = (n_ * 3) // len(letters)
    col = GREEN if letters[li] == "?" else TEXT
    lid = D.text(f"TC2 KEY letter '{letters[li]}'", letters[li], lx, y2, "archivo", 196, col, fh + batch * STEP, b, g, wght=880, wdth=80)
    D.vox(lid, 196)
plan_rows.append(("TC2", "So WHAT HAPPENED?", "Connector + keyword", "Ghost-to-solid (So)", "Block-to-word (WHAT), Random letter reveal (HAPPENED?)", "Cut out", "centered"))

# ================= 4c. TC3 =================
(_, a, b) = SEG["TC3"]
g = scene_group("TC3 Text Centerpiece: And that was only HALF the problem.", a, b)
L = WORDS[14]
ONLY = ("serif_italic", 80, None, 0)
pos, _ = row(["And", "that", "was", "only"], [SMALL, SMALL, SMALL, ONLY], 418)
for i, (x, y) in zip(range(0, 4), pos):
    if i < 3:
        lid = D.text(f"TC3 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(14, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
    else:
        lid = D.text("TC3 connector 'only'", "only", x, y, "serif_italic", 80, TEXT, wf(14, i, a), b, g); D.vox(lid, 80); D.ghost_to_solid(lid)
HALF = ("serif_italic", 330, None, 0)
(hx, hy), = row(["half"], [HALF], 704)[0]
fhf = wf(14, 4, a)
flash, _w = centred_text("TC3 KEY 'half' Flash-in frames", "half", hx, hy, "serif_italic", 330, TEXT, fhf, fhf + STEP, g)
D.effect(flash, {"type": "dropShadow", "enabled": True, "color": [GREEN[0], GREEN[1], GREEN[2], 0.95], "offset": [0, 0], "blurRadius": 46,
                 "spreadRadius": 6, "blendMode": "normal"})
lid, _w = centred_text("TC3 KEY 'half'", "half", hx, hy, "serif_italic", 330, GREEN, fhf + STEP, b, g); D.vox(lid, 330)
pos, _ = row(["the", "problem."], [SMALL, SMALL], 806)
for i, (x, y) in zip(range(5, 7), pos):
    lid = D.text(f"TC3 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(14, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
plan_rows.append(("TC3", "And that was only HALF the problem.", "Connector + keyword", "Blur-to-sharp; Ghost-to-solid (only)", "Flash-in", "Cut out", "centered"))

# ================= 4e. shelf / hype / athlete / all at once: centred block, no panel, no captions =================
(_, a, b) = SEG["H_L27"]
g = D.group("SHELF / HYPE / ATHLETE / ALL AT ONCE (centred block)", 0, endcard_in)
D.effect(g, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.6], "offset": [0, 0], "blurRadius": 46, "spreadRadius": 10, "blendMode": "normal"})
L = WORDS[27]
CONN = ("archivo", 50, {"wght": 520, "wdth": 100}, 0)
KW = ("serif", 262, None, 0)
c_hype = CUT[("H_L27", "B51", 28.0)]
c_ath = CUT[("H_L27", "B78", 2.0)]
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
    D.effect(fg, {"type": "dropShadow", "enabled": True, "color": [1.0, 0.96, 0.9, 0.85], "offset": [0, 0], "blurRadius": 38,
                  "spreadRadius": 3, "blendMode": "normal"})
    D.keys(fg, "opacity", [(t, v, "hold") for t, v in pattern if t < n])


# --- O'Leary ---
key = "CLIP_OLEARY"
a, b = tl[key][0], SEG["A1_OLEARY"][2]
info = CLIPINFO[key]
src0 = round((CLIPS[key][2] - CLIPS[key][1]) / CLIPS[key][5] * 1000)
gm = D.group("O'Leary year mark", 0, endcard_in)
year_mark(gm, "2021", a + STEP, b)
ow = clip_words(key)
ref_captions(key, ow, [(0, 3, {2}, False), (3, 7, {6}, False), (7, 10, {9}, False), (10, 13, {12}, False),
                       (13, 17, {15, 16}, False), (17, len(ow), {len(ow) - 2, len(ow) - 1}, False)], a, b)
gO = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gO, "name": "LIVE CLIP Kevin O'Leary (1.15x, full frame)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
OL_T = xf(pos=(1517, 853), scale=158)     # hides the CNBC chyron (y>770) and stock box (x>1230)
flicker(gO, "m_oleary", 0, b - a, src0, OL_T, FLICK_LONG, "O'Leary", dur_ms=ms(b) - ms(a))
vO = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vO, "name": "O'Leary video + own audio", "parentLayerId": gO,
       "activeRange": {"start": 0, "duration": ms(b) - ms(a)}, "sourceRange": {"start": src0, "duration": min(ms(b) - ms(a), info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
       "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": CLIPS[key][4]})
end_rel = tl[key][1] - a
D.keys(vO, "volume", [(0, 0, "linear"), (2, CLIPS[key][4], "linear"), (end_rel, CLIPS[key][4], "linear"), (end_rel + 3, 0, "linear")])
ng = D.effect(vO, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 5})
D.effect_script(vO, ng, "seed", "return Math.floor(input.time.seconds * 24);")
zoom_transition(gO, b - a, base=100, t_in=False, t_out=True, push_to=104)
plan_rows.append(("CLIP_OLEARY", "This is WHY / you should be WORRIED / about the FUTURE / of a WALMART / or a FOOT LOCKER / They don't NEED RETAIL",
                  "Connector + keyword (reference: italic serif + big serif)", "Blur-to-sharp", "Blur-to-sharp + texture", "Cut out", "centre"))

# --- Donahoe: card cropped clear of CNBC graphics over a blurred fill of the same shot ---
key = "CLIP_DONAHOE"
a, b = tl[key][0], SEG["A2_DONAHOE"][2]
info = CLIPINFO[key]
src0 = round((CLIPS[key][2] - CLIPS[key][1]) / CLIPS[key][5] * 1000)
gm = D.group("Donahoe year mark", 0, endcard_in)
year_mark(gm, "2024", a + STEP, b)
dw = clip_words(key)
ref_captions(key, dw, [(0, 3, {2}, False), (3, 6, {5}, False), (6, 10, {8}, False), (10, len(dw), {len(dw) - 1}, True)], a, b)
gD = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gD, "name": "LIVE CLIP John Donahoe (1.15x)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
card = D.nid()
D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": card, "name": "Donahoe card matte", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": ms(b) - ms(a)}, "transform": xf(pos=(380, 0), anchor=(0, 0)), "rect": {"size": [1160, 1080], "fillColor": [1, 1, 1, 1]}})
vD = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vD, "name": "Donahoe video + own audio (card)", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": ms(b) - ms(a)}, "sourceRange": {"start": src0, "duration": min(ms(b) - ms(a), info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": xf(pos=(2060, 820), scale=200),
       "source": {"assetId": "donahoe_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": CLIPS[key][4]})
D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": vD, "matteLayerId": card, "mode": "alpha"})
end_rel = tl[key][1] - a
D.keys(vD, "volume", [(0, 0, "linear"), (2, CLIPS[key][4], "linear"), (end_rel, CLIPS[key][4], "linear"), (end_rel + 3, 0, "linear")])
ng = D.effect(vD, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 6})
D.effect_script(vD, ng, "seed", "return Math.floor(input.time.seconds * 24);")
vB = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vB, "name": "Donahoe blurred fill", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": ms(b) - ms(a)}, "sourceRange": {"start": src0, "duration": min(ms(b) - ms(a), info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": xf(pos=(1500, 760), scale=300),
       "source": {"assetId": "donahoe_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
D.effect(vB, {"type": "gaussianBlur", "blurriness": 60, "repeatEdgePixels": True})
D.effect(vB, {"type": "hueSaturation", "hue": 0, "saturation": -30, "lightness": -55, "colorize": False, "colorizeHue": 0,
              "colorizeSaturation": 0, "colorizeLightness": 0})
zoom_transition(gD, b - a, base=100, t_in=True, t_out=True, push_to=104)
plan_rows.append(("CLIP_DONAHOE", "we had OVER-ROTATED / away from WHOLESALE / a little MORE than / we INTENDED", "Connector + keyword (reference style)",
                  "Blur-to-sharp", "Blur-to-sharp + texture", "Cut out", "centre"))

# --- Hill: Text Centerpiece with live audio, quote marks and a small photo ---
key = "CLIP_HILL"
a = tl[key][0]; b = SEG["TC4_HILL"][2]
g = scene_group("TC4 Hill quote: We lost our OBSESSION with sport.", a, b)
hw = [w for w in CW["hill"] if CLIPS[key][2] - 0.1 <= w["s"] < CLIPS[key][3]]
ph = D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "Hill photo (B60 still)", "parentLayerId": g,
            "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
            "transform": {"anchorPoint": [0, 0], "position": [250, 392], "scale": [44, 44], "rotation": 0, "opacity": 100},
            "source": {"assetId": "hill_photo", "fit": "contain"}})
D.blur_to_sharp(ph["layerId"], 14)
D.text("Hill photo caption", "Elliott Hill, Nike CEO", 252, 702, "archivo", 26, [0.75, 0.75, 0.75, 1], a + STEP, b, g, wght=500)
q = D.text("Hill quote mark", "“", 610, 560, "serif", 300, GREEN, a, b, g); D.vox(q, 300); D.ghost_to_solid(q)
SMQ = ("archivo", 58, {"wght": 520, "wdth": 100}, 0)
pos, _ = row([w["w"] for w in hw[0:3]], [SMQ] * 3, 448, align="left", x_left=760)
for w, (x, y) in zip(hw[0:3], pos):
    lid = D.text(f"Hill '{w['w']}'", w["w"], x, y, "archivo", 58, TEXT, max(a, grid(cframe(key, w["s"]))), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
fo = max(a, grid(cframe(key, hw[3]["s"])))
lid = D.text("Hill KEY 'obsession'", "obsession", 752, 650, "serif_italic", 210, GREEN, fo, b, g); D.vox(lid, 210); D.flicker_in(lid)
last = hw[5]["w"].rstrip(".") + ".”"
pos, _ = row([hw[4]["w"], last], [SMQ] * 2, 748, align="left", x_left=760)
for w, txt_, (x, y) in zip(hw[4:6], (hw[4]["w"], last), pos):
    lid = D.text(f"Hill '{txt_}'", txt_, x, y, "archivo", 58, TEXT, max(a, grid(cframe(key, w["s"]))), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
D.add({"type": "createFxAudioLayer", "compositionId": C, "layerId": D.nid(), "name": "LIVE AUDIO Elliott Hill (earnings call)",
       "activeRange": {"start": ms(a), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceRange": {"start": round((CLIPS[key][2] - CLIPS[key][1]) * 1000), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceIntrinsicDuration": 2800, "source": {"assetId": "hill_audio"}, "volume": CLIPS[key][4]})
plan_rows.append(("TC4", "We lost our OBSESSION with sport.", "Connector + keyword", "Blur-to-sharp", "Flicker-in", "Cut out", "centered with photo"))

# ================= 4g. FC2 special captions (WHAT HAPPENED style) over the MG slot =================
(_, a, b) = SEG["FC2"]
sg = caption_group("FC2 SPECIAL CAPTIONS (Archivo Black condensed caps)")
SPC = ("archivo", 124, {"wght": 880, "wdth": 80}, 0)
SP_PHR = [(9, 0, 2, {1}), (9, 2, 4, set()), (9, 4, 6, {5}), (10, 0, 3, {1, 2}), (10, 3, 5, set()), (10, 5, 7, {6}),
          (10, 7, 9, {8}), (10, 9, 12, {11}), (10, 12, 15, {13, 14})]
sp_starts = [max(a, wf(ln, i0)) for (ln, i0, i1, ks) in SP_PHR]
for k, (ln, i0, i1, ks) in enumerate(SP_PHR):
    f1 = sp_starts[k + 1] if k + 1 < len(SP_PHR) else b
    ws = [WORDS[ln][i]["w"].upper() for i in range(i0, i1)]
    xs, Wd = layout_line(ws, [SPC] * len(ws))
    x0 = 960 - Wd / 2
    for j, i in enumerate(range(i0, i1)):
        fw = min(max(sp_starts[k], wf(ln, i)), f1 - 1)
        if i in ks:
            wdt = advance(ws[j], *SPC)
            D.rect(f"FC2 block '{ws[j]}'", x0 + xs[j], 610 - 90, wdt, 92, GREEN, fw, min(fw + STEP, f1), sg)
            lid = D.text(f"FC2 '{ws[j]}'", ws[j], x0 + xs[j], 610, "archivo", 124, GREEN, min(fw + STEP, f1 - 1), f1, sg, wght=880, wdth=80)
        else:
            lid = D.text(f"FC2 '{ws[j]}'", ws[j], x0 + xs[j], 610, "archivo", 124, TEXT, fw, f1, sg, wght=880, wdth=80)
            D.blur_to_sharp(lid)
        D.vox(lid, 124)
plan_rows.append(("FC2", "HIS PLAN? CUT OUT THE MIDDLEMAN. NIKE PULLED OUT OF STORES LIKE DSW AND DILLARD'S, AND SENT LESS TO FOOT LOCKER.",
                  "Caption line (special, TC2 style)", "Blur-to-sharp", "Block-to-word", "Cut out", "centre"))

# ================= 5. placeholder screens =================
for (name, kind, first, label), a, b in zip(SEGMENTS, seg_start, seg_end):
    if kind in ("FC", "TC", "CLIP"):
        nm = {"FC": f"{name} FULL COVER PLACEHOLDER (blank, VO + watermark)", "TC": f"{name} Text Centerpiece background",
              "CLIP": f"{name} live clip background"}[kind]
        if kind == "FC" and name != "FC2":
            w_mg = advance("MG", "archivo", 140, {"wght": 800, "wdth": 100}, 0)
            D.text(f"{name} preview label MG", "MG", 960 - w_mg / 2, 590, "archivo", 140, TEXT, a, b, wght=800)
        D.rect(nm, 0, 0, 1920, 1080, BG, a, b)

# ================= 6. footage: one group per shot (punch-in, push, transitions, flicker, 3D chart) =================
FLICKER_SHOTS = {("B19", 4.80): ("m_B19", FLICK_SHORT), ("B60", 10.5): ("m_B60", FLICK_SHORT)}
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
               "transform": {"anchorPoint": [960, 540], "position": list(pos) if not chart else [1150, 640], "scale": [sc, sc] if not chart else [140, 140],
                             "rotation": 0, "opacity": 100, **({"rotationX": 14, "rotationY": -18} if chart else {})}})
        if chart:   # 3D tilt + diagonal pan + highlighter on the "Nike" legend
            hl = D.nid()
            D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": hl, "name": "highlighter on 'Nike' legend", "parentLayerId": sgp,
                   "activeRange": {"start": 0, "duration": gdur}, "transform": xf(pos=(436, 292), anchor=(0, 0)),
                   "rect": {"size": [90, 40], "fillColor": [GREEN[0], GREEN[1], GREEN[2], 0.55]}})
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
        ng = D.effect(lid, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 3})
        D.effect_script(lid, ng, "seed", "return Math.floor(input.time.seconds * 24);")
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
            kk(sgp, "positionX", [(0, 1150, "linear"), (n, 1000, EASE)])
            kk(sgp, "positionY", [(0, 640, "linear"), (n, 560, EASE)])
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
json.dump(_d, open(os.path.join(W, "editable.json"), "w"))
run("project", "commit", "--project", P, "--file", os.path.join(W, "editable.json"))
json.dump(dict(clip_frames=clip_frames, timeline={str(k): v for k, v in tl.items()}, endcard_in=endcard_in, total=TOTAL,
               segments=[dict(name=s[0], kind=s[1], label=s[3], start=a, end=b) for s, a, b in zip(SEGMENTS, seg_start, seg_end)],
               shots=[{k: v for k, v in sh.items() if k != "mezz"} for sh in shots], captions=cap_rows, typography=plan_rows),
          open(os.path.join(W, "edit_plan_out.json"), "w"), indent=1)
print(f"actions {len(D.A)}; shots {len(shots)}; caption words {len(cap_rows)}; total {TOTAL} f = {TOTAL / FPS:.2f} s")
