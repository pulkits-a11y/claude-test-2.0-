"""v3: the reference-video caption system and the reference-style hook (0:00-0:07.5).

Captions: one style for every word in the film - Archivo SemiBold-ish (wght 600) at 47 px, the reference's
32 px cap height - warm white with a two-layer glow, on the centre line of the frame, each phrase split into a left
block (right-aligned to the subject's left edge) and a right block (left-aligned to its right edge). Words drop in
stretched (scaleY 520% -> 100%) on the frame they are spoken, like the reference.

Hook (frames 0-227): tracking-box montage of 2-3 frame hits -> CRT on black with the line either side -> red flash ->
GTA III wordmark with tracking boxes -> logos built from tiles with thumbnails around -> full-frame footage.
"""
import json, os, random, re
import cv2, numpy as np
from lib import *
import textfit as tf

CAP_SIZE = 47
CAP_AX = {"wdth": 100, "wght": 600}
CAP_FILL = [0.992, 0.957, 0.89, 1]  # #FDF4E3, the reference caption's warm white
CAP_MID = 540                       # caption cap-height centre: the frame's centre line
PAD = 34                            # gap between a caption block and the subject's edge
DISPLAY = {5: "9/11", 6: None, 22: "III", 39: "9/11", 40: None, 42: "6", 104: "City", 106: "Andreas", 107: "IV", 108: "V", 111: "VI,"}   # v5b: no commas on the box names
HUD_WHITE = [1, 1, 1, 0.78]
HUD_DOT = hexc("#7CFF8A")
# v5 glow, measured against the reference's "by definition," (light added around the letters, 1-60 px out): four blurred
# copies of the word added on top of the picture - (blur px, opacity %, colour). The text itself stays sharp on top.
GLOW_NEAR, GLOW_FAR = [1, 0.96, 0.88, 1], [1, 0.87, 0.66, 1]
GLOW_TIERS = [(20, 25, GLOW_NEAR), (40, 45, GLOW_NEAR), (80, 55, GLOW_NEAR), (160, 50, GLOW_FAR)]
# glow only where it matters: the hook's 9/11 and "this?", the list (guns, fire, burning buildings), the dates and
# deadlines, the names, the cut, the grid, the rush job, the template, VI and the closing lines
GLOW_WORDS = set(range(200))      # v5b: every caption glows (client: "make all captions bold" - the glow look)
CAP_SHADOW = {"enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 2], "blurRadius": 10, "spreadRadius": 0, "blendMode": "normal"}
HOOK_END = 227                      # the stretched drop-in entrance is kept for the hook only


def ctx(reel):
    """Bind the generator's shared objects (Doc, asset registry, helpers)."""
    global D, R, WF, prep, rl
    rl = reel; D = reel.D; R = reel.R; WF = reel.WF; prep = reel.prep


# =================================================================== captions
def word_text(i):
    """v8: no punctuation in any caption (commas, periods, question marks); apostrophes and the 9/11 slash stay."""
    t = DISPLAY.get(i, rl.WORDS[i]["w"])
    return None if t is None else re.sub(r"[.,?!;:]", "", t)


def baseline():
    return CAP_MID + tf.cap_height("AR", CAP_SIZE) / 2


def word_unit(name, txt, f0, f1, x, color, hook, shadow=None, extra=(), size=CAP_SIZE, mid=CAP_MID, blur=True, enter=True, fade=0, wipe=None):
    """One word as a group pivoting on its centre: drops in stretched (scaleY 520% -> 100%) in the hook, fades up with
    a 10 px rise after it (v5: the stretch is kept for the hook only)."""
    d = f1 - f0; w = tf.advance("AR", txt, size, CAP_AX); base = mid + tf.cap_height("AR", size) / 2
    t = D.text(txt, 0, d, txt, rl.AR, size, color, x, base, axes=CAP_AX, shadow=False)
    if shadow: t["dropShadow"] = shadow
    cx, cy = x + w / 2, mid
    lay = list(extra) + [t]
    if wipe:                           # v8: wiped on left to right and off again (the cover labels), through a matte
        n_in, n_out = wipe; ch = tf.cap_height("AR", size); mx, my, mw, mh = x - 14, mid - ch / 2 - 0.42 * size, w + 28, ch + 0.84 * size
        m = D.rect(f"{name} (wipe matte)", 0, d, mx, my, mw, mh, [1, 1, 1, 1], tr=T(mx, my, ax=mx, ay=my))
        D.kf(m, "scaleX", [(0, 0, HOLD), (n_in, 100, E_OX), (d - n_out, 100, HOLD), (d, 0, E_IOX)])
        lay = [D.group(f"{name} (text)", 0, d, lay, matte={"layer": m["id"], "mode": "alpha"}), m]
    g = D.group(name, f0, f1, lay, tr=T(cx, cy, ax=cx, ay=cy))
    if not blur: g["motionBlur"] = t["motionBlur"] = False
    if not enter or wipe: pass                 # v6: a word carried on to a new spot at a cut just appears there
    elif hook:
        D.kf(g, "scaleY", [(0, 520, HOLD), (5, 100, E_OX)]); D.kf(g, "scaleX", [(0, 85, HOLD), (5, 100, E_OX)])
    else:
        D.kf(g, "opacity", [(0, 0, HOLD), (3, 100, E_OX)]); D.kf(g, "positionY", [(0, cy + 10, HOLD), (4, cy, E_OX)])
    if fade: D.kf(g, "opacity", [(d - fade, 100, HOLD), (d, 0, E_IOC)])
    return g


def caption_word(txt, f0, f1, x, strike=False, glow=False, fade=0, size=CAP_SIZE):
    """A sharp caption word (+ slash). Words without glow carry a small soft shadow so they read on bright footage."""
    extra = slash("slash: " + txt.strip(",."), f1 - f0, x, tf.advance("AR", txt.rstrip(",."), CAP_SIZE, CAP_AX)) if strike else ()
    return word_unit(f"Caption: {txt}", txt, f0, f1, x, CAP_FILL, f0 < HOOK_END, shadow=None if glow else CAP_SHADOW, extra=extra, fade=fade, size=size)


def glow_stack(label, items, k=1.0):
    """The glow of a run of words: per tier one group of copies of the words (same timing and entrance), blurred and
    added on top of the picture. items: (text, f0, f1, x, size, mid, enter, fade)."""
    f0 = min(it[1] for it in items); f1 = max(it[2] for it in items); out = []
    for blur, o, col in GLOW_TIERS:
        units = [word_unit(f"Glow copy: {it[0]}", it[0], it[1] - f0, it[2] - f0, it[3], col, it[1] < HOOK_END, size=it[4], mid=it[5], blur=False,
                           enter=it[6], fade=it[7], wipe=it[8] if len(it) > 8 else None) for it in items]
        g = D.group(f"Glow {blur * k:.0f} px at {o}%: {label}", f0, f1, units, blend="add", o=o,
                    effects=[D.fx({"type": "gaussianBlur", "blurriness": blur * k, "repeatEdgePixels": False})])
        g["motionBlur"] = False
        out.append(g)
    return out


def phrase(L=(), R_=(), gap=(700, 1220), end=None, center=False, strike=(), start=None, fade=0, size=CAP_SIZE):
    """L / R_: word indices for the left and right blocks. The phrase holds until `end`. Returns the sharp words and
    the glowing ones (text, f0, f1, x, size, mid)."""
    sharp, glow = [], []
    blocks = [(list(L), "right", gap[0] - PAD), (list(R_), "left", gap[1] + PAD)] if not center else [(list(L) + list(R_), "center", 960)]
    for idxs, align, x in blocks:
        idxs = [i for i in idxs if word_text(i) is not None]
        if not idxs: continue
        texts = [word_text(i) for i in idxs]
        xs, ws, _ = tf.line_layout("AR", texts, size, CAP_AX, 0, x, align)
        for i, txt, xx in zip(idxs, texts, xs):
            if WF[i] >= end: continue          # spoken after the phrase is cleared (e.g. "since." under the floating covers)
            f0 = WF[i] if start is None else max(start, WF[i])
            sharp.append(caption_word(txt, f0, end, xx, strike=i in strike, glow=i in GLOW_WORDS, fade=fade, size=size))
            if i in GLOW_WORDS: glow.append((txt, f0, end, xx, size, CAP_MID, True, fade))
    return sharp, glow


def placed(idxs, segs, end, size=CAP_SIZE, align="left", tag="Caption", together=False, wipe=None):
    """v6: words set next to what they describe instead of on the centre line, moving to a new spot at a cut.
    segs: [(from_frame, x, mid)] - x is the line's left edge (align left) or centre (align center), mid its cap centre."""
    sharp, glow = [], []
    idxs = [i for i in idxs if word_text(i) is not None]; texts = [word_text(i) for i in idxs]
    for n, (fa, x, mid) in enumerate(segs):
        fb = segs[n + 1][0] if n + 1 < len(segs) else end
        xs, _, _ = tf.line_layout("AR", texts, size, CAP_AX, 0, x, align)
        for i, txt, xx in zip(idxs, texts, xs):
            if WF[i] >= fb: continue
            f0 = fa if together else max(WF[i], fa); enter = together or WF[i] >= fa
            sharp.append(word_unit(f"{tag}: {txt}", txt, f0, fb, xx, CAP_FILL, enter and f0 < HOOK_END, size=size, mid=mid, enter=enter, wipe=wipe))
            glow.append((txt, f0, fb, xx, size, mid, enter, 0, wipe))
    return sharp, glow


FLAG = (1250, 470)          # v8: the waving US flag at 0:14 (centre), where "in the US." used to sit


def six_weeks():
    """v8: "6 weeks before launch" centred on the frame like the client's sketch: a big numeral 6, "weeks" beside its
    top and "before launch" under that, the numeral as tall as the two lines together."""
    sw, sb, gap, gx = 96, 64, 22, 30
    cw, cb = tf.cap_height("AR", sw), tf.cap_height("AR", sb); th = cw + gap + cb
    s6 = round(th / (tf.cap_height("AR", 100) / 100))
    w6 = tf.advance("AR", "6", s6, CAP_AX); wt = max(tf.advance("AR", "weeks", sw, CAP_AX), tf.advance("AR", "before launch", sb, CAP_AX))
    x0 = 960 - (w6 + gx + wt) / 2; top = 540 - th / 2; xt = x0 + w6 + gx
    return [placed([42], [(362, x0, 540)], 403, size=s6), placed([43], [(362, xt, top + cw / 2)], 403, size=sw),
            placed([44, 45], [(362, xt, top + cw + gap + cb / 2)], 403, size=sb)]


def captions(END):
    TV = (700, 1220); COVER = (560, 1360); HEAD = (700, 1220); CENTRE = (900, 1020); BOX = (680, 1240)
    P = [
        dict(L=range(0, 5), R_=[5], gap=TV, end=44),                                  # What if I told you | 9/11
        dict(L=[7, 8, 9], R_=range(10, 15), gap=TV, end=124),                           # is the reason | GTA covers look like this?
        dict(L=[15, 16], R_=[17, 18, 19], gap=(660, 1260), end=145),                    # This was | meant to be
        dict(L=[20, 21, 22], R_=[23], gap=(600, 1320), end=189),                        # the GTA III | cover,
        dict(L=[24], R_=[25], gap=(600, 1060), end=207),                                # six | months  (either side of his face)
        dict(L=[26, 27], R_=[], gap=(880, 1600), end=230),                              # of painting.  (just left of him, clear of his body)
        dict(L=[28, 29], gap=(600, 1320), end=236),                                     # It had  (v8: off when "guns" lands alone)
        dict(L=[35, 36], R_=[37], gap=COVER, end=322),                                  # all over | it.
        dict(L=[38, 39], R_=[41], gap=(700, 1320), end=362),                            # Then 9/11 | hit,
        dict(L=[46], R_=[47, 48], gap=(560, 1370), end=426),                            # Rockstar | pulled it
        dict(L=[52, 53], R_=[54], gap=(790, 1130), end=462, size=56),                   # The new | cover  (v8: tucked in to him, bigger)
        dict(L=[55], R_=[56], gap=COVER, end=476),                                      # couldn't | show
        dict(L=[61], R_=[62, 63], gap=(620, 1300), end=558),                            # Artist | Stephen Bliss
        dict(L=[64, 65], R_=[66, 67], gap=(620, 1300), end=586),                        # had about | a week,
        dict(L=[68, 69], R_=[70], gap=HEAD, end=609),                                   # so he | chopped
        dict(L=[75, 76], R_=[77], gap=(500, 1420), end=657),                            # He only | kept  (v8: off once it's said)
        dict(L=[85, 86], R_=[87, 88, 89, 90], gap=(500, 1420), end=755),                # and boxed | them into a grid.
        dict(L=[91, 92], R_=[93], gap=(620, 1300), end=782),                            # That rush | job?  (v5: card centred)
        dict(L=[94, 95, 96], R_=[97], gap=(630, 1290), end=803),                        # It's been the | template
        dict(L=[98, 99], R_=[100, 101, 102], gap=(630, 1290), end=838),                 # for every | GTA cover  (off before the floating covers)
        dict(L=[], R_=[107], gap=BOX, end=920),                                         # IV,
        dict(L=[108], R_=[], gap=BOX, end=940),                                         # V,
        dict(L=[109, 110], R_=[111], gap=COVER, end=974),                               # even GTA | VI,
        dict(L=[112], R_=[113], gap=CENTRE, end=998),                                   # same | boxes,  (off before the match cut)
        dict(L=[114], R_=[115], gap=(500, 1420), end=1021),                             # same | grid,
        dict(L=[116, 117, 118], center=True, end=END - 28, fade=10),                     # 25 years later.  (v6: fades, the end holds on the covers)
    ]
    # v6: placed next to what they describe (frames and positions read off the shots)
    L62 = dict(size=62, align="center", tag="Caption (lower third)")
    G60 = dict(size=60, align="center")                                                # v8: one word at a time, centred, a little bigger
    Q = [placed([30], [(236, 960, 540)], 258, **G60),                                 # guns
         placed([31], [(258, 960, 470), (268, 760, 600), (275, 760, 470)], 295, align="center"),   # fire, - over the blast, the car, the street
         placed([32, 33, 34], [(271, 1100, 250)], 295, align="center"),                # and burning buildings - up by the skyline
         *six_weeks(),                                                                 # 6 | weeks / before launch  (v8: centred, like the sketch)
         placed([57], [(476, 960, 540)], 495, **G60), placed([58], [(495, 960, 540)], 505, **G60),   # guns / buildings / or fire:
         placed([59, 60], [(505, 960, 540)], 528, **G60),                              # one at a time, centred
         placed([50, 51], [(429, FLAG[0], FLAG[1] + 235)], 445, align="center"),        # the US  (under the waving flag)
         placed([103, 104], [(853, 960, 925)], 882, align="center", together=True, wipe=(6, 4)),   # Vice City   (under the cover, as in v7)
         placed([105, 106], [(883, 960, 925)], 911, align="center", together=True, wipe=(6, 4))]   # San Andreas
    sharp, glow = [], []
    for s, g in [phrase(**p) for p in P] + Q:
        sharp += s
        if g: glow += glow_stack(" ".join(x[0] for x in g), g)
    return (D.group("Captions (reference style)", 0, END, sharp),
            D.group("Caption glow (blurred copies, added)", 0, END, glow, blend="add",
                    desc="Glow on the words that matter: per word run, four blurred copies (20/40/80/160 px) added over the picture."))


# =================================================================== slashes (p5.brush, thin, solid)
SLASHES = []


def slash(name, d, x, w, n=14, at=5):
    """A thin solid hand-drawn slash through a caption word: rendered with p5.brush at 3x, scaled down and thresholded
    to a solid core; drawn on left to right with a wipe that starts fast and slows (ease-out expo)."""
    key = "slash_" + name.split(": ")[-1].lower()
    cw, ch = int(w + 36), 50
    if key not in R:
        bdir = os.path.join(ROOT, "build", "brush"); out = os.path.join(ROOT, "build", "assets", "strokes"); os.makedirs(out, exist_ok=True)
        spec = {"name": key + "_3x", "w": cw * 3, "h": ch * 3, "pad": 40, "color": "#ffffff", "brush": "charcoal", "weight": 2.4,
                "seed": 11 + len(SLASHES) * 7, "angle": -4, "passes": 1, "gap": 0, "scale": 3}
        import subprocess
        subprocess.run(["node", os.path.join(bdir, "render.js"), json.dumps([spec]), out], check=True, capture_output=True)
        g = cv2.imread(os.path.join(out, spec["name"] + ".png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        g = cv2.resize(g, (cw, ch), interpolation=cv2.INTER_AREA)
        a = (np.clip((g - 0.18) * 3.5, 0, 1) * 255).astype(np.uint8)
        col = np.array([0x2A, 0x32, 0xD8], np.uint8)
        prep.img(key, np.dstack([np.full_like(a, col[0]), np.full_like(a, col[1]), np.full_like(a, col[2]), a]))
    SLASHES.append(key)
    cx, cy = x + w / 2, CAP_MID + 2
    x0, y0 = cx - cw / 2, cy - ch / 2
    wipe = D.rect(name + " (wipe matte)", at, d, x0, y0, cw, ch, [1, 1, 1, 1], tr=T(x0, y0, ax=x0, ay=y0))
    D.kf(wipe, "scaleX", [(0, 0, HOLD), (n, 100, E_OX)])
    img = D.image(name, key, at, d, tr=T(cx, cy, ax=cw / 2, ay=ch / 2), fit="stretch", rect=(0, 0, cw, ch),
                  matte={"layer": wipe["id"], "mode": "alpha"})
    return [img, wipe]


# =================================================================== HUD (tracking boxes)
def cover_img(im):
    """An image as it lands on the 1920x1080 canvas with fit=cover."""
    h, w = im.shape[:2]; s = max(1920 / w, 1080 / h)
    r = cv2.resize(im, (int(round(w * s)), int(round(h * s))))
    y0 = (r.shape[0] - 1080) // 2; x0 = (r.shape[1] - 1920) // 2
    return r[y0:y0 + 1080, x0:x0 + 1920]


def hud_box(name, k, d, x, y, bw, bh, px, py, f0=0, label=True, size=13):
    """One tracking box: thin white outline, coordinate label on its top-left corner, green dot at the tracked point."""
    r = D.rect(f"{name}: box {k}", f0, d, x, y, bw, bh, HUD_WHITE)
    r["rect"].update({"fillEnabled": False, "strokeEnabled": True, "strokeColor": HUD_WHITE, "strokeWidth": 1.5})
    out = [r, D.rect(f"{name}: dot {k}", f0, d, px - 2, py - 2, 4, 4, HUD_DOT)]
    if label and not (x < 190 and y < 170):          # keep the logo corner clear
        out.insert(0, D.text(f"{name}: label {k}", f0, d, f"x: {int(px)} y: {int(py)}", rl.AR, size, HUD_WHITE, x, y - 5,
                             axes={"wdth": 100, "wght": 500}, shadow=False))
    for l in out: l["motionBlur"] = False
    return out


def hud_pts(name, gray, d, mapf=lambda p: p, n=7, seed=1, big=1, bounds=(150, 120, 1770, 960), min_dist=90, roi=None,
            big_size=((380, 620), (220, 380)), small=((50, 170), (40, 130)), f0=0):
    """Computer-vision tracking boxes on the strongest corners of an image (gray, in its own pixels; mapf maps them
    to the canvas): thin white boxes, a coordinate label at each box's corner, a green dot at its centre."""
    pts = cv2.goodFeaturesToTrack(gray, 120, 0.02, min_dist, mask=roi)
    rnd = random.Random(seed)
    pts = [mapf(tuple(map(float, p.ravel()))) for p in (pts if pts is not None else [])]
    pts = [p for p in pts if bounds[0] < p[0] < bounds[2] and bounds[1] < p[1] < bounds[3]] or [((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)]
    rnd.shuffle(pts); out = []
    for k, (px, py) in enumerate(pts[:n + big]):
        sz = big_size if k < big else small
        bw, bh = rnd.randint(*sz[0]), rnd.randint(*sz[1])
        out += hud_box(name, k + 1, d, px - bw / 2, py - bh / 2, bw, bh, px, py, f0=f0)
    return out


def hud(name, im, d, n=7, seed=1, big=1):
    """Tracking boxes on a full-frame still (fit=cover)."""
    return hud_pts(name, cv2.cvtColor(cover_img(im), cv2.COLOR_BGR2GRAY), d, n=n, seed=seed, big=big, min_dist=70)


def vmap(asset, scale=100, cx=960, cy=540):
    """Select pixels -> canvas for a video layer framed with fit=cover in the full frame, scaled about the centre."""
    a = R[asset]; s0 = max(W / a["w"], H / a["h"]) * scale / 100
    return lambda p: ((p[0] - a["w"] / 2) * s0 + cx, (p[1] - a["h"] / 2) * s0 + cy)


def tracked_hud(name, asset, d, mapf, roi, n=7, seed=1, big=(), min_dist=55, f0=0, labels=True):
    """Tracking boxes that follow the footage: corners found on the shot's first frame (inside roi, select pixels)
    and followed frame by frame with Lucas-Kanade optical flow; every box, label and dot is keyed on every frame.
    big: extra boxes (x, y, w, h in select pixels) that follow their centre."""
    a = R[asset]; start = int(round(a["lead"] * FPS)); cap = cv2.VideoCapture(a["path"]); frames, i = [], 0
    while len(frames) < d:
        ok, f = cap.read()
        if not ok: break
        if i >= start: frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
        i += 1
    m = np.zeros_like(frames[0]); x, y, w, h = map(int, roi); m[y:y + h, x:x + w] = 255
    pts = cv2.goodFeaturesToTrack(frames[0], 80, 0.02, min_dist, mask=m)
    pts = [] if pts is None else [tuple(map(float, p.ravel())) for p in pts]
    rnd = random.Random(seed); rnd.shuffle(pts); pts = pts[:n]
    anchors = [(bx + bw / 2, by + bh / 2) for bx, by, bw, bh in big] + pts
    P = np.float32(anchors).reshape(-1, 1, 2); track = [P.reshape(-1, 2).copy()]
    for k in range(1, len(frames)):
        Q, st, _ = cv2.calcOpticalFlowPyrLK(frames[k - 1], frames[k], P, None, winSize=(41, 41), maxLevel=3)
        lost = st.ravel() == 0; Q[lost] = P[lost]; P = Q; track.append(P.reshape(-1, 2).copy())
    while len(track) < d: track.append(track[-1])
    out = []
    for j, (sx, sy) in enumerate(anchors):
        px, py = mapf((sx, sy))
        if j < len(big):
            bx, by, bw, bh = big[j]; (x0, y0), (x1, y1) = mapf((bx, by)), mapf((bx + bw, by + bh)); bw, bh = x1 - x0, y1 - y0
        else:
            bw, bh = rnd.randint(46, 150), rnd.randint(36, 110)
        lay = hud_box(name, j + 1, d, px - bw / 2, py - bh / 2, bw, bh, px, py, f0=f0, label=labels)
        dx = [mapf(track[k][j])[0] - px for k in range(d)]; dy = [mapf(track[k][j])[1] - py for k in range(d)]
        for l in lay:
            ox, oy = l["transform"]["position"]
            D.kf(l, "positionX", [(k - f0, ox + dx[k], HOLD) for k in range(f0, d)])
            D.kf(l, "positionY", [(k - f0, oy + dy[k], HOLD) for k in range(f0, d)])
        out += lay
    return out


def hikey(invert=1, lo=0.25, hi=0.72):
    return [D.shader("hiKey", "hikey.wgsl", [("invert.toggle", invert, 0, 1, "1 = negative"), ("lo", lo, 0, 1, "Black point"),
                                             ("hi", hi, 0, 1, "White point")],
                     "High-key two-tone: luminance through a hard curve to cream #FFF4E6 / near black (optionally inverted).")]


def glitch(amount=0.04):
    return [D.shader("crtGlitch", "crtglitch.wgsl", [("animationTime", 0, 0, 3600, "Engine clock (s)."), ("amount", amount, 0, 0.3, "Row shift"),
                                                       ("bands", 46, 4, 200, "Glitch bands"), ("height", H, 1, 8000, "px")],
                     "CRT feed: black-and-white, contrast, scan lines and stepped horizontal row tears.")]


# =================================================================== hook
def stills():
    S = prep.still
    S("hud_b01", "B01", 300.0); S("hud_b04", "B04", 10.0, crop=(0, 0, 608, 342)); S("hud_b50", "B50", 10.0)
    S("hud_b49", "B49", 40.0); S("hud_b48", "B48", 60.0); S("hud_b25", "B25", 200.0); S("hud_b04b", "B04", 6.0, crop=(0, 380, 608, 342))
    for k in ("logo_gta3", "logo_vi", "b09_front", "b09_front_title_mask", "cov_III_title_mask_v2", "cov_VI_title_mask_v2", "C05_flash_mask"):
        prep.img(k, path=os.path.join(ROOT, "build", "assets", "img", k + ".png"))
    if "redleak" not in R:                       # red light leak (reference 0:01.4 / 0:04.4)
        y, x = np.mgrid[0:1080, 0:1920].astype(np.float32)
        base = np.zeros((1080, 1920, 3), np.float32); base[:] = (8, 10, 60)
        blob = np.exp(-(((x - 760) / 900) ** 2 + ((y - 460) / 520) ** 2))
        band = np.exp(-(((x - 0.55 * y - 1180) / 160) ** 2))
        img = base + blob[..., None] * np.array([30, 70, 255]) + band[..., None] * np.array([90, 150, 255]) * 0.8
        prep.img("redleak", cv2.GaussianBlur(np.clip(img, 0, 255).astype(np.uint8), (0, 0), 12))
    if "tilegrid" not in R:                      # the faint tile grid behind the logos
        g = np.zeros((1080, 1920, 3), np.uint8)
        for yy in range(0, 1080, 48):
            for xx in range(0, 1920, 48): cv2.rectangle(g, (xx + 3, yy + 3), (xx + 44, yy + 44), (14, 14, 14), -1)
        prep.img("tilegrid", g)


def hit(name, f0, f1, layers, look=None):
    return rl.shot(name, f0, f1, layers, look=look, dim=0, prism_on=False)


def still_layer(name, asset, d, effects=None, drift_on=False):
    return rl.iclip(name, asset, d, fit="cover", drift_on=drift_on, effects=effects)


def terminal(d, fg, bg):
    lines = ["> mount /archive/2001/rockstar_nyc", "> scanning covers ......... 48 found", "> cover_gta3_eu.tif   4800x6800   ok",
             "> cover_gta3_us.tif   4800x6800   ok", "> diff --frames eu us", "  match 0.000  [grid] [no-fire] [no-skyline]"]
    out = [D.text(f"Terminal line {i + 1}", 0, d, l, rl.AR, 26, fg, 120, 150 + i * 40, axes={"wdth": 100, "wght": 500}, shadow=False) for i, l in enumerate(lines)]
    return out + [D.rect("Terminal background", 0, d, 0, 0, W, H, bg)]


def H1():
    """0-25: the tracking-box montage under "What if I told you" - 2-3 frame hits."""
    sh = []
    def img(k): return cv2.imread(R[k]["path"])
    # v5: about twice the boxes per hit (the tracking-box look is the hook's style)
    spec = [(0, 3, "hud_b01", hikey(1), 15), (3, 6, "hud_b04", None, 14), (6, 8, "A01", hikey(1, .08, .45), 12), (8, 11, "hud_b50", None, 18),
            (15, 18, "hud_b49", None, 15), (18, 21, "hud_b48", hikey(0, .2, .8), 15), (21, 24, "hud_b25", None, 16), (24, 25, "hud_b04b", hikey(1), 10)]
    for k, (f0, f1, a, lk, n) in enumerate(spec):
        d = f1 - f0
        lay = hud(f"HUD {a}", img(a), d, n=n, seed=k + 3, big=2) + [still_layer(a, a, d)]
        if a == "hud_b49":     # the radar circle of the reference's top-down car shot
            c = D.rect("Tracking circle", 0, d, 760, 340, 400, 400, HUD_WHITE, roundness=200)
            c["rect"].update({"fillEnabled": False, "strokeEnabled": True, "strokeColor": HUD_WHITE, "strokeWidth": 1.5}); lay.insert(0, c)
        if a == "hud_b25":     # motion-smeared pan
            lay[-1]["effects"] = (lay[-1].get("effects") or []) + [D.dirblur(90, 90)]
            D.kf(lay[-1], "positionX", [(0, 1060, HOLD), (d, 860, E_IOX)])
        sh.append(hit(f"H1.{k + 1} {a}", f0, f1, lay, look=lk))
    sh.insert(4, hit("H1 terminal (orange on cream)", 11, 13, terminal(2, hexc("#E8572C"), hexc("#FFF4E6"))))
    sh.insert(5, hit("H1 terminal (cyan on black)", 13, 15, terminal(2, hexc("#46D8EE"), hexc("#05070A"))))
    return sh


TVBODY = (710, 220, 590, 609)          # A01 TV body on the 1920 canvas (cover fit): x, y, w, h


def tv(d, screens, s0=74, s1=84):
    """The A01 CRT cut out of its room and set on black: its body lifted to read as a grey set, footage pinned into the
    screen, scaled about the body's centre. v5: held, then hard jump cuts to a tighter zoom (reference 0:02.4) on
    "GTA" and on "this?" - never wider than the gap between the caption blocks. Tracking boxes on the set."""
    bx, by, bw, bh = TVBODY; cx, cy = bx + bw / 2, by + bh / 2
    m = D.rect("TV body (matte)", 0, d, bx, by, bw, bh, [1, 1, 1, 1], roundness=34)
    plate = D.image("A01 TV (lifted)", "A01", 0, d, effects=[D.fx({"type": "levels", "inputBlack": 2, "inputWhite": 62, "gamma": 1.35, "outputBlack": 6, "outputWhite": 225})],
                    matte={"layer": m["id"], "mode": "alpha"})
    scr = hud_box("TV screen", 1, d, 756, 280, 512, 424, 1012, 491)
    body = np.zeros((1080, 1920), np.uint8); body[by + 10:by + bh - 10, bx + 10:bx + bw - 10] = 255; body[270:715, 750:1275] = 0
    boxes = hud_pts("TV set", cv2.cvtColor(cover_img(cv2.imread(R["A01"]["path"])), cv2.COLOR_BGR2GRAY), d, n=6, seed=4, big=0,
                    roi=body, min_dist=60, small=((40, 110), (34, 90)))
    g = D.group("CRT", 0, d, scr + boxes + screens + [plate, m], tr=T(960, 540, s0, ax=cx, ay=cy))
    # v5b: back to the v4 move - a slow, subtle grow from its entry (the jump-cut zooms are gone)
    for p in ("scaleX", "scaleY"): D.kf(g, p, [(0, s0, HOLD), (d * 1.4, s1 + (s1 - s0) * .4, E_OX)])
    return g


def H2():
    """25-110: the CRT on black with the line either side; red light at the start and a red flash on "this?"."""
    s0 = 25; d = 85
    scr1 = rl.pinned("TV feed: B04 9/11 news", "B04", 10.0, 42, effects=glitch(0.035))
    scr2 = rl.pinned("TV feed: B07 the covers", "B07", 36.3, 40, effects=glitch(0.03))
    scr2["playback"]["inputRange"]["start"] = rl.ms(42); scr2["playback"]["mapping"]["input"]["start"] = rl.ms(42)
    scr3 = rl.pinned("TV feed: red flash", "B07", 37.7, 3, effects=rl.L_duo("red") + hikey(1, .2, .7))
    scr3["playback"]["inputRange"]["start"] = rl.ms(82); scr3["playback"]["mapping"]["input"]["start"] = rl.ms(82)
    set_ = tv(d, [scr3, scr2, scr1])
    red1 = D.image("Red light (arrival)", "redleak", 0, 3, fit="stretch")
    red2 = D.image("Red light (flash on 'this?')", "redleak", 82, 85, fit="stretch")
    return [hit("H2.1 CRT on black", 25, 110, [set_, red2, red1])]


def tile_logo(name, asset, d, cx, cy, width, appear=5, seed=1, label_frac=0.35):
    """A logo built from tiles (reference 0:04.7-0:05.7): the logo shows only through rounded tiles that pop on over
    `appear` frames in random order; a third of the tiles carry a coordinate label."""
    a = R[asset]; s = width / a["w"]; h = a["h"] * s; x0, y0 = cx - width / 2, cy - h / 2
    im = cv2.imread(a["path"], cv2.IMREAD_UNCHANGED); alpha = im[..., 3] if im.shape[2] == 4 else np.full(im.shape[:2], 255, np.uint8)
    pitch, size = 48, 42; rnd = random.Random(seed); tiles, labels = [], []
    gx0 = int(np.floor(x0 / pitch)) * pitch; gy0 = int(np.floor(y0 / pitch)) * pitch
    for ty in range(gy0, int(y0 + h) + pitch, pitch):
        for tx in range(gx0, int(x0 + width) + pitch, pitch):
            ax0, ay0 = int(max(0, (tx - x0) / s)), int(max(0, (ty - y0) / s)); ax1, ay1 = int(min(a["w"], (tx + size - x0) / s)), int(min(a["h"], (ty + size - y0) / s))
            if ax1 <= ax0 or ay1 <= ay0 or alpha[ay0:ay1, ax0:ax1].mean() < 0.3 * 255: continue
            f = rnd.randint(0, appear)
            tiles.append(D.rect(f"Tile {tx},{ty}", f, d, tx + 3, ty + 3, size, size, [1, 1, 1, 1], roundness=5))
            if rnd.random() < label_frac:
                labels.append(D.text(f"Tile label {tx},{ty}", f, d, f"x: {tx + 24} y: {ty + 24}", rl.AR, 11, HUD_WHITE, tx + 3, ty - 2, axes={"wdth": 100, "wght": 500}, shadow=False))
    m = D.group(f"{name}: tiles (matte)", 0, d, tiles)
    logo = D.image(name, asset, 0, d, tr=T(cx, cy, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]),
                   matte={"layer": m["id"], "mode": "alpha"})
    return labels + [logo, m]


THUMBS = [("B48", 60.0, 300, 760), ("B49", 26.0, 1530, 330), ("B26", 875.0, 1500, 800), ("B09", 50.0, 380, 300), ("B25", 200.0, 1660, 590)]


def thumbs(d, k=5, seed=1):
    out = []
    for i, (b, t, x, y) in enumerate(THUMBS[:k]):
        v = rl.vclip(f"Thumbnail {b}", b, t, d, fit="cover", rect=(0, 0, 150, 90), cx=x, cy=y, drift_on=False)
        r = D.rect(f"Thumbnail {b} frame", 0, d, x - 76, y - 46, 152, 92, HUD_WHITE)
        r["rect"].update({"fillEnabled": False, "strokeEnabled": True, "strokeColor": HUD_WHITE, "strokeWidth": 1})
        lab = D.text(f"Thumbnail {b} label", 0, d, f"x: {x} y: {y}", rl.AR, 11, HUD_WHITE, x - 76, y - 50, axes={"wdth": 100, "wght": 500}, shadow=False)
        out += [lab, r, v]
    return out


def wordmark(d):
    """The GTA III wordmark with a tracking box on every letter, thumbnails around it, the tile grid and a title flash
    (the hook's 0:03 screen until v4; v5 moves it to "It's been the template")."""
    a = R["logo_gta3"]; width = 520; s = width / a["w"]; x0, y0 = 960 - width / 2, 540 - a["h"] * s / 2
    letters = json.load(open(os.path.join(ROOT, "build", "assets", "logo_gta3_letters.json")))["letters"]
    lay = []
    for k, (lx, ly, lw, lh) in enumerate(letters):
        bx, by, bw, bh = x0 + lx * s - 6, y0 + ly * s - 6, lw * s + 12, lh * s + 12
        r = D.rect(f"Letter box {k + 1}", 0, d, bx, by, bw, bh, HUD_WHITE)
        r["rect"].update({"fillEnabled": False, "strokeEnabled": True, "strokeColor": HUD_WHITE, "strokeWidth": 1.2})
        lay.append(r)
        if k % 2 == 0: lay.append(D.text(f"Letter label {k + 1}", 0, d, f"x: {int(bx + bw / 2)} y: {int(by + bh / 2)}", rl.AR, 11, HUD_WHITE, bx, by - 4, axes={"wdth": 100, "wght": 500}, shadow=False))
    tr = lambda: T(960, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2)
    word = D.image("GTA III wordmark (from the US cover)", "logo_gta3", 0, d, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]), effects=glitch(0.02))
    flash = rl.glow_flash("logo_gta3", d, tr, a, 2, halo=14, scale=s)
    return lay + flash + [word] + thumbs(d, 5) + [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")]


HOOK_MATCH = ["cov_III", "cov_VC", "cov_SA", "cov_LCS", "cov_IV", "cov_V", "cov_VI"]


def hook_match(name, f0, f1, height=620):
    """The match cut (every cover at the same spot and size, a one-frame white flash on each switch) sized to sit
    between the "is the reason | GTA covers look like this?" caption blocks, tracking boxes on every cover."""
    d = f1 - f0; a = R["cov_III"]; s = height / a["h"]; w = a["w"] * s; x0, y0 = 960 - w / 2, 540 - height / 2
    n = len(HOOK_MATCH); durs = [d // n + (1 if i < d % n else 0) for i in range(n)]
    lay, flashes, t = [], [], 0
    for i, (k, dur) in enumerate(zip(HOOK_MATCH, durs)):
        im = D.image(f"{k[4:]} cover", k, 0, dur, tr=T(960, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]))
        g = cv2.cvtColor(cv2.imread(R[k]["path"]), cv2.COLOR_BGR2GRAY)
        boxes = hud_pts(f"HUD {k[4:]} cover", g, dur, lambda p: (x0 + p[0] * s, y0 + p[1] * s), n=7, seed=21 + i, big=1, min_dist=60,
                        bounds=(x0 + 12, y0 + 12, x0 + w - 12, y0 + height - 12), big_size=((150, 260), (120, 200)), small=((36, 110), (30, 90)))
        lay.append(D.group(f"{k[4:]} cover + tracking boxes", t, t + dur, boxes + [im]))
        if t: flashes.append(D.rect(f"White flash @{f0 + t}", t, t + 1, 0, 0, W, H, rl.FLASH, o=28))
        t += dur
    for r in flashes: r["motionBlur"] = False         # one crisp frame each
    return hit(name, f0, f1, flashes + lay + [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")])


def H3():
    """110-145: the match cut through the covers (v5), then logos built from tiles (VI, then the European cover)."""
    sh = [hook_match("H3.1 Match cut: every cover (tracking boxes)", 110, 124)]
    d = 9
    sh.append(hit("H3.2 VI built from tiles", 124, 133, tile_logo("GTA VI logo (B06)", "logo_vi", d, 960, 540, 560, 4, 5, .7) + thumbs(d, 5, 2) +
                  [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")]))
    d = 12; c = R["C02_euro"]
    sh.append(hit("H3.3 European cover built from tiles", 133, 145, tile_logo("European GTA III cover (C02)", "C02_euro", d, 960, 540, c["w"] * 720 / c["h"], 6, 9, .7) +
                  thumbs(d, 5, 3) + [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")]))
    return sh


def tracked_shot(name, b, t, d, roi, big=(), n=7, seed=1, scale=100, cx=960, cy=540):
    """Footage with tracking boxes locked to it: the clip and its boxes in one group, which carries the drift."""
    a = prep.sel(b, t, d / FPS + 0.2)
    v = rl.vclip(f"{b} at {t} s", b, t, d, scale=scale, cx=cx, cy=cy, drift_on=False)
    boxes = tracked_hud(f"Track {b}", a, d, vmap(a, scale, cx, cy), roi, n=n, seed=seed, big=big)
    for l in boxes: l["transform"]["opacity"] = 35          # v5b: barely there
    g = D.group(f"{b} + tracking boxes", 0, d, boxes + [v], tr=T(960, 540, ax=960, ay=540))
    rl.drift(g, d, 960, 540, 100)
    return g


def H4():
    """145-227: full-frame footage, captions either side of the subject; v5: tracking boxes locked to the box in his
    hands, the box front and Bliss's face."""
    sh = []
    v = R[prep.sel("B09", 48.5, 16 / FPS + 0.2)]; bw_, bh_ = v["w"], v["h"]
    sh.append(rl.shot("H4.1 European box in hands", 145, 161, [tracked_shot("B09 European box in hands", "B09", 48.5, 16,
                      roi=(0.08 * bw_, 0.02 * bh_, 0.8 * bw_, 0.9 * bh_), big=[(0.3 * bw_, 0.02 * bh_, 0.27 * bw_, 0.36 * bh_)], n=0, seed=5)], dim=10))
    a = R["b09_front"]; sc = W / a["w"]
    tr = lambda: T(960, 540, 100 * sc, ax=a["w"] / 2, ay=a["h"] / 2)
    front = D.image("B09 European box, front (still frame at 50 s)", "b09_front", 0, 28, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]))
    g = cv2.cvtColor(cv2.imread(a["path"]), cv2.COLOR_BGR2GRAY)
    boxes = hud_pts("HUD box front", g, 28, lambda p: ((p[0] - a["w"] / 2) * sc + 960, (p[1] - a["h"] / 2) * sc + 540), n=1, seed=8, big=0, min_dist=80,
                    big_size=((300, 460), (180, 280)), f0=3)
    for l in boxes: l["transform"]["opacity"] = 35          # v5b: one faint box only
    # v8: after a beat the background around the box dims, so the cover is the highlight
    if "b09_front_dim" not in R:
        q = np.int32([(236, 0), (936, 0), (944, 720), (262, 720)]); al = np.full((a["h"], a["w"]), 255, np.uint8); cv2.fillPoly(al, [q], 0, cv2.LINE_AA)
        al = cv2.GaussianBlur(al, (0, 0), 6); prep.img("b09_front_dim", np.dstack([np.zeros((a["h"], a["w"], 3), np.uint8), al]))
    dim = D.image("Dim around the cover", "b09_front_dim", 0, 28, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]), o=0)
    D.kf(dim, "opacity", [(0, 0, HOLD), (8, 0, HOLD), (16, 62, E_IOC)])
    sh.append(rl.shot("H4.2 European box, front + title flash", 161, 189, boxes + rl.glow_flash("b09_front_title_mask", 28, tr, a, 1, halo=16, scale=sc) + [dim, front], dim=10))
    # B26 at 875: Bliss alone in the call panel (x 228-1692, y 150-1020): panel scaled to fill; boxes on his face
    sh.append(rl.shot("H4.3 Stephen Bliss talking", 189, 207, [tracked_shot("B26 Bliss talking (call panel, filled)", "B26", 875.0, 18, roi=(640, 230, 420, 560),
                      big=[(690, 250, 290, 300)], n=0, seed=6, scale=131, cy=540 + (540 - 585) * 1.31)], dim=10))
    sh.append(rl.shot("H4.4 Bliss at his mural", 207, 227, [tracked_shot("B27 Bliss at his mural", "B27", 52.0, 20, roi=(560, 160, 1100, 780),
                      big=[], n=1, seed=7, scale=108)], dim=10))
    return sh


def flash_cover(name, asset, mask, d, height, cx, cy, at):
    """A cover held still at a given height, its title letters flicker-flashing at `at` (rotoscoped mask)."""
    a = R[asset]; w = a["w"] * height / a["h"]
    tr = lambda: T(w / 2, height / 2, 100 * height / a["h"], ax=a["w"] / 2, ay=a["h"] / 2)
    im = D.image(name, asset, 0, d, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]))
    return D.group(name + " + title flash", 0, d, rl.glow_flash(mask, d, tr, a, at, halo=14, scale=height / a["h"]) + [im],
                   tr=T(cx, cy, ax=w / 2, ay=height / 2), shadow=rl.SHADOW)


MATCH = ["cov_III", "cov_VC", "cov_SA", "cov_LCS", "cov_VCS", "cov_IV", "cov_TBOGT", "cov_CW", "cov_V", "cov_VI"]


def matchcut(name, f0, f1):
    """Every cover, one after another at the same spot and size (a match cut), with a one-frame white flash on each switch."""
    d = f1 - f0; a = R["cov_III"]; s = H / a["h"]; n = len(MATCH); lay, flashes, t = [], [], 0
    durs = [d // n + (1 if i < d % n else 0) for i in range(n)]
    for k, dur in zip(MATCH, durs):
        lay.append(D.image(f"{k[4:]} cover", k, t, t + dur, tr=T(960, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"])))
        if t: flashes.append(D.rect(f"White flash @{f0 + t}", t, t + 1, 0, 0, W, H, rl.FLASH, o=32))
        t += dur
    for r in flashes: r["motionBlur"] = False         # one crisp frame (motion blur smeared it over its neighbours)
    return rl.shot(name, f0, f1, flashes + lay, dim=8)
