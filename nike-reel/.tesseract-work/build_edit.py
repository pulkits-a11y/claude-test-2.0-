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

clip_frames = {k: round((v[3] - v[2]) * FPS) for k, v in CLIPS.items()}
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
for k, name in (("CLIP_OLEARY", "oleary"), ("CLIP_DONAHOE", "donahoe")):
    CLIPINFO[k] = json.loads(run("project", "import-video", "--project", P, "--file", os.path.join(W, "clips", f"{name}.mov"), "--asset-id", name))
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
CAP_Y, CAP_SIZE, CAP_W = 556, 50, 640
SPLITS = {8: [(0, 2), (2, 4), (4, 6), (6, 8)], 11: [(0, 2), (2, 5)],
          12: [(0, 3), (3, 6), (6, 9), (9, 11), (11, 13), (13, 16)], 13: [(0, 4), (4, 7), (7, 11)],
          15: [(0, 2), (2, 5), (5, 9)], 19: [(0, 3), (3, 5), (5, 8)], 20: [(0, 2), (2, 5)], 21: [(0, 2), (2, 4), (4, 7)],
          22: [(0, 2), (2, 5)], 26: [(0, 3), (3, 6)], 27: [(0, 3), (3, 5), (5, 7), (7, 10)], 28: [(0, 3)]}
KEY = {8: [4, 5], 11: [4], 12: [8, 9, 10], 13: [8, 9, 10], 15: [2], 19: [6, 7], 20: [4], 21: [2, 3], 22: [4], 26: [4, 5], 27: [9], 28: [0, 1, 2]}
HIGHLIGHT = {(11, 4), (19, 7), (22, 4)}          # Highlight-box wipe on these key words


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


phrases = []
for line, parts in SPLITS.items():
    for (i0, i1) in parts:
        phrases.append(dict(line=line, i0=i0, i1=i1, start=wf(line, i0, floor=seg_start_of(line))))
phrases.sort(key=lambda p: p["start"])
for k, p in enumerate(phrases):
    nxt = phrases[k + 1]["start"] if k + 1 < len(phrases) else endcard_in
    p["end"] = min(nxt, seg_end_of(p["line"]))

cap = D.group("CAPTIONS (word-by-word, Caption line lockup)", 0, endcard_in)
D.effect(cap, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.85], "offset": [0, 3], "blurRadius": 10,
               "spreadRadius": 2, "blendMode": "normal"})
D.effect(cap, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 0], "blurRadius": 42,
               "spreadRadius": 8, "blendMode": "normal"})
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
            # dark letters revealed by the wiping box (alpha matte), over green letters, over the visible green box
            dark = D.text(f"cap L{p['line']}w{i} '{word}' inverted (matte)", word, x, CAP_Y, "archivo", CAP_SIZE, BG, f0, p["end"], cap, wght=CAP_W)
            matte = D.rect(f"cap L{p['line']}w{i} wipe matte", x - 5, CAP_Y - 40, w + 15, 54, GREEN, f0, p["end"], cap)
            green = D.text(f"cap L{p['line']}w{i} '{word}'", word, x, CAP_Y, "archivo", CAP_SIZE, GREEN, f0, p["end"], cap, wght=CAP_W)
            box = D.rect(f"cap L{p['line']}w{i} highlight box", x - 5, CAP_Y - 40, w + 15, 54, GREEN, f0, p["end"], cap)
            D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": dark, "matteLayerId": matte, "mode": "alpha"})
            for lid in (matte, box):     # box wipes left -> right after a 3-frame ghost (stepped)
                D.keys(lid, "scaleX", [(0, 0, "hold"), (STEP, 50, "hold"), (2 * STEP, 100, "hold")])
            D.keys(green, "opacity", [(0, 40, "hold"), (STEP, 100, "hold")])
            cap_rows.append((p["line"], i, word, f0, "Highlight-box wipe"))
        else:
            lid = D.text(f"cap L{p['line']}w{i} '{word}'", word, x, CAP_Y, "archivo", CAP_SIZE, GREEN if key else TEXT, f0, p["end"], cap, wght=CAP_W)
            D.keys(lid, "opacity", [(0, 0, "linear"), (5, 100, "linear")])        # fade up: fade in while rising 16 px
            D.keys(lid, "positionY", [(0, CAP_Y + 16, "linear"), (5, CAP_Y, "linear")])
            cap_rows.append((p["line"], i, word, f0, "Fade up"))


# ================= helpers for centred display rows =================
def row(words, specs, y, cx=960, align="center", x_left=None):
    xs, Wd = layout_line(words, specs)
    x0 = (cx - Wd / 2) if align == "center" else (x_left if align == "left" else cx - Wd)
    return [(x0 + x, y) for x in xs], Wd


def centred_text(name, s, x, y, font, size, color, f0, f1, parent, wght=None, wdth=100):
    w = advance(s, font, size, {"wght": wght, "wdth": wdth} if font == "archivo" else None, 0)
    return D.text(name, s, x, y, font, size, color, f0, f1, parent, wght=wght, wdth=wdth, anchor=(w / 2, -0.34 * size)), w


def scene_group(name, a, b, drift=True):
    g = D.group(name, 0, endcard_in)
    if drift:   # slow drift on held text, stepped every 3rd frame (Stepped look)
        D.stepped_drift(g, a, b)
    return g


SMALL = ("archivo", 58, {"wght": 520, "wdth": 100}, 0)
plan_rows = []    # typography plan for the report
CLIP_VIDEO_LAYERS = []

# ================= 4a. TC1 =================
(_, a, b) = SEG["TC1"]
g = scene_group("TC1 Text Centerpiece: Well, turns out, Nike NEEDED RETAIL more than anyone.", a, b)
L = WORDS[1]
pos, _ = row([w["w"] for w in L[0:4]], [SMALL] * 4, 404)
for i, (x, y) in zip(range(0, 4), pos):
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(1, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
big = ("serif", 230, None, 0)
pos, _ = row(["needed", "retail"], [big, big], 618)
for k, (i, (x, y)) in enumerate(zip((4, 5), pos)):
    lid, w = centred_text(f"TC1 KEY '{L[i]['w']}'", L[i]["w"], x, y, "serif", 230, GREEN, wf(1, i, a), b, g)
    D.vox(lid, 230); D.pop(lid)
    if k == 0:
        D.flicker_in(lid)
pos, _ = row([w["w"] for w in L[6:9]], [SMALL] * 3, 714)
for i, (x, y) in zip(range(6, 9), pos):
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(1, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
plan_rows.append(("TC1", "Well, turns out, Nike NEEDED RETAIL more than anyone.", "Size-contrast build", "Blur-to-sharp", "Flicker-in (+ MG scale/blur build)", "Cut out", "centered"))

# ================= 4b. TC2 =================
(_, a, b) = SEG["TC2"]
g = scene_group("TC2 Text Centerpiece: So WHAT HAPPENED?", a, b)
L = WORDS[7]
BIG2 = ("archivo", 196, {"wght": 880, "wdth": 80}, 0)
words2 = ["WHAT", "HAPPENED", "?"]
xs, Wd = layout_line(["WHAT", "HAPPENED?"], [BIG2, BIG2])
x0 = 960 - Wd / 2
y2 = 652
lid = D.text("TC2 connector 'So'", "So", x0 + 6, 452, "serif_italic", 120, TEXT, wf(7, 0, a), b, g); D.vox(lid, 120); D.ghost_to_solid(lid)
fw = wf(7, 1, a)
wW = advance("WHAT", *BIG2)
blk = D.rect("TC2 Block-to-word block (WHAT)", x0, y2 - 142, wW, 146, GREEN, fw, fw + STEP, g)
lid = D.text("TC2 KEY 'WHAT'", "WHAT", x0, y2, "archivo", 196, TEXT, fw + STEP, b, g, wght=880, wdth=80); D.vox(lid, 196)
fh = wf(7, 2, a)
xh = x0 + xs[1]
letters = list("HAPPENED?")
order = list(range(len(letters))); random.shuffle(order)
for n, li in enumerate(order):
    pre = "".join(letters[:li])
    lx = xh + advance(pre, *BIG2) if pre else xh
    batch = (n * 3) // len(letters)          # 3 stepped batches: +0, +3, +6 frames
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

# ================= 4e. Half Cover: shelf / hype / athlete / all at once =================
(_, a, b) = SEG["H_L27"]
g = scene_group("HALF COVER: It gave up the SHELF, the HYPE and the ATHLETE. ALL AT ONCE.", a, b, drift=False)
L = WORDS[27]
CONN = ("archivo", 50, {"wght": 520, "wdth": 100}, 0)
c_hype = CUT[("H_L27", "B51", 28.0)]
c_ath = CUT[("H_L27", "B78", 2.0)]
c_all = CUT[("H_L27", "B79", 13.6)]
# connector words (small sans), each on its spoken frame
pos, _ = row([w["w"] for w in L[0:4]], [CONN] * 4, 214, align="left", x_left=236)
for i, (x, y) in zip(range(0, 4), pos):
    lid = D.text(f"HC connector '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 50, TEXT, max(a, wf(27, i, a)), wf(27, 5, a), g, wght=520); D.ghost_to_solid(lid)
lid = D.text("HC connector 'the' (hype)", "the", 236, 214, "archivo", 50, TEXT, wf(27, 5, a), wf(27, 7, a), g, wght=520); D.ghost_to_solid(lid)
pos, _ = row(["and", "the"], [CONN] * 2, 214, align="left", x_left=236)
for i, (x, y) in zip((7, 8), pos):
    lid = D.text(f"HC connector '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 50, TEXT, wf(27, i, a), c_all, g, wght=520); D.ghost_to_solid(lid)
KW = ("serif", 262, None, 0)
for word, f0, f1 in (("shelf", wf(27, 4, a), c_hype), ("hype", c_hype, c_ath), ("athlete", c_ath, c_all)):
    w = advance(word, *KW)
    D.rect(f"HC Block-to-word block ({word})", 230, 440 - 170, w + 12, 176, GREEN, f0, f0 + STEP, g)
    lid = D.text(f"HC KEY '{word}'", word, 232, 440, "serif", 262, GREEN, f0 + STEP, f1, g); D.vox(lid, 262)
lid = D.text("HC KEY 'all at once.'", "all at once.", 232, 432, "serif_italic", 236, GREEN, c_all, b, g); D.vox(lid, 236); D.blur_to_sharp(lid, 16)
panel = D.rect("HC panel #121212 (top half)", 0, 0, 1920, 512, BG, a, b, g)
D.keys(panel, "positionY", [(0, -512, "hold"), (STEP, -256, "hold"), (2 * STEP, 0, "hold")])
plan_rows.append(("H_L27", "It gave up the SHELF, the HYPE and the ATHLETE. ALL AT ONCE.", "Connector + keyword",
                  "Ghost-to-solid (connectors)", "Panel wipe (loud, panel); Block-to-word (shelf/hype/athlete); Blur-to-sharp (all at once.)",
                  "Cut out", "top panel, left"))


# ================= 4f. live clips: Half Covers (speaker left, panel right), lower thirds, clip captions, Hill quote =================
CW = {k: v for k, v in json.load(open(os.path.join(W, "clip_words.json"))).items()}
def cw(name, lo, hi):
    return [w for w in CW[name] if lo - 0.05 <= w["s"] < hi]
def cframe(key, t):
    return tl[key][0] + round((t - CLIPS[key][2]) * FPS)
def clip_caption_phrases(key, words, groups, keyset=()):
    out = []
    for gi, (i0, i1) in enumerate(groups):
        ws = words[i0:i1]
        f0 = grid(cframe(key, ws[0]["s"]))
        f1 = grid(cframe(key, words[groups[gi + 1][0]]["s"])) if gi + 1 < len(groups) else None
        out.append((ws, max(tl[key][0], f0), f1))
    return out
def place_clip_captions(key, phrases, end, cx=480, y=960, keyset=()):
    for k, (ws, f0, f1) in enumerate(phrases):
        f1 = f1 or end
        words = [w["w"] for w in ws]
        xs, Wd = layout_line(words, [spec] * len(words))
        x0 = cx - Wd / 2
        for j, w in enumerate(ws):
            fw = max(f0, grid(cframe(key, w["s"])))
            lid = D.text(f"clipcap {key} '{w['w']}'", w["w"], x0 + xs[j], y, "archivo", CAP_SIZE,
                         GREEN if w["w"].strip('.,').lower() in keyset else TEXT, min(fw, f1 - 1), f1, cap, wght=CAP_W)
            D.keys(lid, "opacity", [(0, 0, "linear"), (5, 100, "linear")])
            D.keys(lid, "positionY", [(0, y + 16, "linear"), (5, y, "linear")])

def lower_third(g, name, role, f0, f1):
    D.rect(f"LT accent bar ({name})", 1040, 846, 6, 84, GREEN, f0, f1, g)
    l1 = D.text(f"LT name {name}", name, 1068, 884, "archivo", 44, TEXT, f0, f1, g, wght=600); D.blur_to_sharp(l1)
    l2 = D.text(f"LT role {name}", role, 1068, 926, "archivo", 30, [0.75, 0.75, 0.75, 1], f0 + STEP, f1, g, wght=500); D.blur_to_sharp(l2)

for key, nm, role, small, big, big_font, words_lo in (
        ("CLIP_OLEARY", "Kevin O'Leary", "CNBC, June 2021", ["They", "don't"], "need retail", "serif", 260.10),
        ("CLIP_DONAHOE", "John Donahoe", "Nike CEO, April 2024", ["a", "little", "more", "than"], "we intended", "serif_italic", 475.20)):
    a = tl[key][0]
    b = SEG["A1_OLEARY" if key == "CLIP_OLEARY" else "A2_DONAHOE"][2]
    g = scene_group(f"HALF COVER live clip {nm}", a, b, drift=False)
    srcname = "oleary" if key == "CLIP_OLEARY" else "donahoe"
    allw = CW["oleary_head"] + CW["oleary"] if key == "CLIP_OLEARY" else CW["donahoe"]
    seen, words = set(), []
    for w in sorted(allw, key=lambda w: w["s"]):
        if CLIPS[key][2] - 0.1 <= w["s"] < CLIPS[key][3] and round(w["s"], 1) not in seen and w["w"] not in ("-",):
            if w["w"].startswith("-") and words:
                words[-1] = dict(words[-1], w=words[-1]["w"] + w["w"]); continue
            seen.add(round(w["s"], 1)); words.append(w)
    # overlay words (in the panel) and caption words (before the overlay)
    ov = [w for w in words if w["s"] >= words_lo - 0.02]
    pre = [w for w in words if w["s"] < words_lo - 0.02]
    # keyword lockup in the panel
    SM = ("archivo", 58, {"wght": 520, "wdth": 100}, 0)
    pos, _ = row([w["w"] for w in ov[:len(small)]], [SM] * len(small), 430, align="left", x_left=1040)
    for w, (x, y) in zip(ov[:len(small)], pos):
        lid = D.text(f"HC {nm} '{w['w']}'", w["w"], x, y, "archivo", 58, TEXT, max(a, grid(cframe(key, w["s"]))), b, g, wght=520); D.ghost_to_solid(lid)
    bigw = ov[len(small)]
    size = 190
    while advance(big, big_font, size, None, 0) > 800: size -= 6
    fb = max(a, grid(cframe(key, bigw["s"])))
    lid = D.text(f"HC {nm} KEY '{big}'", big, 1036, 640, big_font, size, GREEN, fb, b, g); D.vox(lid, size); D.pop(lid) if False else None
    D.blur_to_sharp(lid, 16)
    lower_third(g, nm, role, a + STEP, b)
    D.rect(f"HC {nm} panel right half", 960, 0, 960, 1080, BG, a, b, g)
    # speaker video (left half, crops out CNBC chyron/stock box)
    info = CLIPINFO[key]
    f_start, s_in, s_out, gain = CLIPS[key][1], CLIPS[key][2], CLIPS[key][3], CLIPS[key][4]
    lidv = D.nid()
    pos_v, sc_v = ((801, 795), 150) if key == "CLIP_OLEARY" else ((1342, 840), 200)
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": lidv, "name": f"LIVE CLIP {nm} ({s_in:.2f}-{s_out:.2f}s, own audio)",
           "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
           "sourceRange": {"start": round((s_in - f_start) * 1000), "duration": min(ms(b) - ms(a), info["durationMs"] - round((s_in - f_start) * 1000))},
           "sourceIntrinsicDuration": info["durationMs"], "transform": xf(pos=pos_v, scale=sc_v),
           "source": {"assetId": srcname, "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": gain})
    n = b - a
    D.keys(lidv, "volume", [(0, 0, "linear"), (3, gain, "linear"), (tl[key][1] - a - 1, gain, "linear"), (tl[key][1] - a + 2, 0, "linear")])
    ng = D.effect(lidv, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 5})
    D.effect_script(lidv, ng, "seed", "return Math.floor(input.time.seconds * 24);")
    CLIP_VIDEO_LAYERS.append(None)
    # captions for the speech before the overlay, 2-4 words, centred on the speaker half
    if key == "CLIP_OLEARY":
        groups = [(0, 3), (3, 6), (6, 9), (9, 12), (12, 15), (15, 18)]
        keyset = {"walmart", "locker"}
    else:
        groups = [(0, 2), (2, 4), (4, 6)]
        keyset = {"over-rotated", "over-rotated,"}
    groups = [(i, min(j, len(pre))) for i, j in groups if i < len(pre)]
    ph = clip_caption_phrases(key, pre, groups)
    place_clip_captions(key, ph, fb, keyset=keyset)
    plan_rows.append((key, f"{' '.join(small)} {big.upper()}", "Connector + keyword", "Ghost-to-solid", "Blur-to-sharp", "Cut out", "right-half panel"))

# Hill: Text Centerpiece with live audio, quote marks and a small photo
key = "CLIP_HILL"
a = tl[key][0]; b = SEG["TC4_HILL"][2]
g = scene_group("TC4 Hill quote: We lost our OBSESSION with sport.", a, b)
hw = [w for w in CW["hill"] if CLIPS[key][2] - 0.1 <= w["s"] < CLIPS[key][3]]
ph = D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "Hill photo (B60 still)", "parentLayerId": g,
            "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
            "transform": {"anchorPoint": [0, 0], "position": [250, 392], "scale": [44, 44], "rotation": 0, "opacity": 100},
            "source": {"assetId": "hill_photo", "fit": "contain"}})
D.blur_to_sharp(ph["layerId"], 14)
cap1 = D.text("Hill photo caption", "Elliott Hill, Nike CEO", 252, 702, "archivo", 26, [0.75, 0.75, 0.75, 1], a + STEP, b, g, wght=500)
q = D.text("Hill quote mark", "“", 610, 560, "serif", 300, GREEN, a, b, g); D.vox(q, 300); D.ghost_to_solid(q)
SMQ = ("archivo", 58, {"wght": 520, "wdth": 100}, 0)
pos, _ = row([w["w"] for w in hw[0:3]], [SMQ] * 3, 448, align="left", x_left=760)
for w, (x, y) in zip(hw[0:3], pos):
    lid = D.text(f"Hill '{w['w']}'", w["w"], x, y, "archivo", 58, TEXT, max(a, grid(cframe(key, w["s"]))), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
fo = max(a, grid(cframe(key, hw[3]["s"])))
lid = D.text("Hill KEY 'obsession'", "obsession", 752, 650, "serif_italic", 210, GREEN, fo, b, g); D.vox(lid, 210); D.flicker_in(lid)
pos, _ = row([hw[4]["w"], hw[5]["w"].rstrip(".") + ".”"], [SMQ] * 2, 748, align="left", x_left=760)
for w, txt_, (x, y) in zip(hw[4:6], (hw[4]["w"], hw[5]["w"].rstrip(".") + ".”"), pos):
    lid = D.text(f"Hill '{txt_}'", txt_, x, y, "archivo", 58, TEXT, max(a, grid(cframe(key, w["s"]))), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
D.add({"type": "createFxAudioLayer", "compositionId": C, "layerId": D.nid(), "name": "LIVE AUDIO Elliott Hill (earnings call)",
       "activeRange": {"start": ms(a), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceRange": {"start": round((CLIPS[key][2] - CLIPS[key][1]) * 1000), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceIntrinsicDuration": 2800, "source": {"assetId": "hill_audio"}, "volume": CLIPS[key][4]})
plan_rows.append(("TC4", "We lost our OBSESSION with sport.", "Connector + keyword", "Blur-to-sharp", "Flicker-in", "Cut out", "centered with photo"))

# ================= 5. placeholder screens =================
for (name, kind, first, label), a, b in zip(SEGMENTS, seg_start, seg_end):
    if kind in ("FC", "TC", "CLIP"):
        nm = {"FC": f"{name} FULL COVER PLACEHOLDER (blank, VO + watermark)", "TC": f"{name} Text Centerpiece background",
              "CLIP": f"{name} live clip slot (clip not supplied)"}[kind]
        if kind == "FC":
            w_mg = advance("MG", "archivo", 140, {"wght": 800, "wdth": 100}, 0)
            D.text(f"{name} preview label MG", "MG", 960 - w_mg / 2, 590, "archivo", 140, TEXT, a, b, wght=800)
        D.rect(nm, 0, 0, 1920, 1080, BG, a, b)
for sh in shots:
    if sh["clip"] == "MISSING":
        D.rect("B_L13 slot: B80-B82 Alo/Vuori not supplied", 0, 0, 1920, 1080, BG, sh["start"], sh["end"])

# ================= 6. footage =================
for sh in shots:
    if sh["clip"] == "MISSING":
        continue
    lid = D.nid()
    info = assets[sh["asset"]]
    n_ms = ms(sh["end"]) - ms(sh["start"])
    src_ms = round((sh["src"] - sh["mezz_start"]) * 1000)
    n_src = n_ms
    if sh["clip"] in REVERSE:
        hi, lo = REVERSE[sh["clip"]]
        src_ms, n_src = round((lo - sh["mezz_start"]) * 1000), round((hi - lo) * 1000)
    pos, sc = punch(sh["clip"])
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": lid,
           "name": f"{sh['seg']} {sh['clip']} @{sh['src']:.2f}s - {sh['note']}",
           "activeRange": {"start": ms(sh["start"]), "duration": n_ms},
           "sourceRange": {"start": src_ms, "duration": min(n_src, info["durationMs"] - src_ms)},
           "sourceIntrinsicDuration": info["durationMs"], "transform": xf(pos=pos, scale=sc),
           "source": {"assetId": sh["asset"], "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
           "volume": 0.0})
    n = sh["end"] - sh["start"]
    ng = D.effect(lid, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 3})
    D.effect_script(lid, ng, "seed", "return Math.floor(input.time.seconds * 24);")
    ng = D.effect(lid, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 3})
    D.effect_script(lid, ng, "seed", "return Math.floor(input.time.seconds * 24);")
    if sh["clip"] in REVERSE:
        hi, lo = REVERSE[sh["clip"]]
        D.add({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": lid, "timeRemap": {
            "keyframes": [{"id": f"rev-{lid}-a", "time": ms(sh["start"]), "value": round((hi - sh["mezz_start"]) * 1000), "easing": {"type": "linear"}},
                          {"id": f"rev-{lid}-b", "time": ms(sh["end"]), "value": round((lo - sh["mezz_start"]) * 1000), "easing": {"type": "linear"}}],
            "before": "inactive", "after": "inactive"}})
    if "freeze_frame" in sh:   # no freeze (user): the shot keeps playing while it drains to B&W
        # drain to black and white over 9 frames, stepped (lands on 'hype')
        rel = sh["freeze_frame"] - sh["start"]
        hs = D.effect(lid, {"type": "hueSaturation", "hue": 0, "saturation": 0, "lightness": 0, "colorize": False,
                            "colorizeHue": 0, "colorizeSaturation": 0, "colorizeLightness": 0})
        D.effect_keys(lid, hs, "saturation", [(rel, 0, "hold"), (rel + 3, -34, "hold"), (rel + 6, -67, "hold"), (rel + 9, -100, "hold")])
    if (sh["clip"], sh["src"]) in STATIC and n >= 6:
        db = D.effect(lid, {"type": "directionalBlur", "direction": 90, "blurLength": 0})
        D.effect_keys(lid, db, "blurLength", [(0, 48, "linear"), (2, 0, "linear"), (n - 3, 0, "linear"), (n - 1, 48, "linear")])
        D.keys(lid, "scaleX", [(0, sc, "linear"), (n, round(sc * 1.05, 2), "linear")])
        D.keys(lid, "scaleY", [(0, sc, "linear"), (n, round(sc * 1.05, 2), "linear")])

ec_ms = endcard["durationMs"]
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": D.nid(), "name": "END CARD (attached CTA, as-is, own audio)",
       "activeRange": {"start": ms(endcard_in), "duration": ms(TOTAL) - ms(endcard_in)},
       "sourceRange": {"start": 0, "duration": min(ec_ms, ms(TOTAL) - ms(endcard_in))}, "sourceIntrinsicDuration": ec_ms,
       "transform": xf(), "source": {"assetId": "endcard", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
       "volume": 1.0})

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
