"""v3: the reference-video caption system and the reference-style hook (0:00-0:07.5).

Captions: one style for every word in the film - Archivo SemiBold-ish (wght 600) at 47 px, the reference's
32 px cap height - warm white with a two-layer glow, on the centre line of the frame, each phrase split into a left
block (right-aligned to the subject's left edge) and a right block (left-aligned to its right edge). Words drop in
stretched (scaleY 520% -> 100%) on the frame they are spoken, like the reference.

Hook (frames 0-227): tracking-box montage of 2-3 frame hits -> CRT on black with the line either side -> red flash ->
GTA III wordmark with tracking boxes -> logos built from tiles with thumbnails around -> full-frame footage.
"""
import json, os, random
import cv2, numpy as np
from lib import *
import textfit as tf

CAP_SIZE = 47
CAP_AX = {"wdth": 100, "wght": 600}
CAP_FILL = hexc("#FFF6EA")
GLOW_TIGHT = hexc("#FFE6C2")
GLOW_WIDE = hexc("#FFC98A")
CAP_MID = 540                       # caption cap-height centre: the frame's centre line
PAD = 34                            # gap between a caption block and the subject's edge
DISPLAY = {5: "9/11", 6: None, 22: "III", 39: "9/11", 40: None, 107: "IV,", 108: "V,", 111: "VI,"}
HUD_WHITE = [1, 1, 1, 0.78]
HUD_DOT = hexc("#7CFF8A")


def ctx(reel):
    """Bind the generator's shared objects (Doc, asset registry, helpers)."""
    global D, R, WF, prep, rl
    rl = reel; D = reel.D; R = reel.R; WF = reel.WF; prep = reel.prep


# =================================================================== captions
def word_text(i):
    return DISPLAY.get(i, rl.WORDS[i]["w"])


def baseline():
    return CAP_MID + tf.cap_height("AR", CAP_SIZE) / 2


def caption_word(txt, f0, f1, x, strike=False):
    """One word: a group (text + tight glow + wide glow [+ slash]) that drops in stretched, pivoting on its centre."""
    d = f1 - f0; w = tf.advance("AR", txt, CAP_SIZE, CAP_AX); base = baseline()
    def t(name, color, blend="normal", o=100, fx=None):
        return D.text(name, 0, d, txt, rl.AR, CAP_SIZE, color, x, base, axes=CAP_AX, shadow=False, blend=blend, o=o, effects=fx)
    lay = [t(txt, CAP_FILL),
           t(txt + " (glow, tight)", GLOW_TIGHT, "screen", 100, [D.gauss(4)]),
           t(txt + " (glow, mid)", GLOW_TIGHT, "screen", 100, [D.gauss(10)]),
           t(txt + " (glow, wide)", GLOW_WIDE, "screen", 85, [D.gauss(24)])]
    if strike:
        lay[0:0] = slash("slash: " + txt.strip(",."), d, x, tf.advance("AR", txt.rstrip(",."), CAP_SIZE, CAP_AX))
    cx, cy = x + w / 2, CAP_MID
    g = D.group(f"Caption: {txt}", f0, f1, lay, tr=T(cx, cy, ax=cx, ay=cy))
    D.kf(g, "scaleY", [(0, 520, HOLD), (5, 100, E_OX)])
    D.kf(g, "scaleX", [(0, 85, HOLD), (5, 100, E_OX)])
    return g


def phrase(L=(), R_=(), gap=(700, 1220), end=None, center=False, strike=(), start=None):
    """L / R_: word indices for the left and right blocks. The phrase holds until `end`."""
    out = []
    blocks = [(list(L), "right", gap[0] - PAD), (list(R_), "left", gap[1] + PAD)] if not center else [(list(L) + list(R_), "center", 960)]
    for idxs, align, x in blocks:
        idxs = [i for i in idxs if word_text(i) is not None]
        if not idxs: continue
        texts = [word_text(i) for i in idxs]
        xs, ws, _ = tf.line_layout("AR", texts, CAP_SIZE, CAP_AX, 0, x, align)
        for i, txt, xx in zip(idxs, texts, xs):
            if WF[i] >= end: continue          # spoken after the phrase is cleared (e.g. "since." under the floating covers)
            out.append(caption_word(txt, WF[i] if start is None else max(start, WF[i]), end, xx, strike=i in strike))
    return out


def captions(END):
    TV = (700, 1220); COVER = (560, 1360); HEAD = (700, 1220); CENTRE = (900, 1020); BOX = (680, 1240)
    P = [
        dict(L=range(0, 5), R_=[5], gap=TV, end=44),                                  # What if I told you | 9/11
        dict(L=[7, 8, 9], R_=range(10, 15), gap=TV, end=124),                           # is the reason | GTA covers look like this?
        dict(L=[15, 16], R_=[17, 18, 19], gap=(660, 1260), end=145),                    # This was | meant to be
        dict(L=[20, 21, 22], R_=[23], gap=(600, 1320), end=189),                        # the GTA III | cover,
        dict(L=[24], R_=[25], gap=(600, 1060), end=207),                                # six | months  (either side of his face)
        dict(L=[26, 27], R_=[], gap=(880, 1600), end=230),                              # of painting.  (just left of him, clear of his body)
        dict(L=[28, 29], R_=[30], gap=(600, 1320), end=258),                            # It had | guns,
        dict(L=[31], R_=[32, 33, 34], gap=HEAD, end=295),                               # fire, | and burning buildings
        dict(L=[35, 36], R_=[37], gap=COVER, end=322),                                  # all over | it.
        dict(L=[38, 39], R_=[41], gap=(700, 1320), end=362),                            # Then 9/11 | hit,
        dict(L=[42, 43], R_=[44, 45], gap=(690, 1230), end=403),                        # six weeks | before launch.
        dict(L=[46], R_=[47, 48], gap=(560, 1370), end=426),                            # Rockstar | pulled it
        dict(L=[], R_=[49, 50, 51], gap=(560, 1040), end=448),                          # in the US.
        dict(L=[52, 53], R_=[54], gap=HEAD, end=462),                                   # The new | cover
        dict(L=[55], R_=[56], gap=COVER, end=476),                                      # couldn't | show
        dict(L=[57], R_=[58], gap=HEAD, end=505, strike=(57, 58)),                      # guns, | buildings,
        dict(L=[59], R_=[60], gap=HEAD, end=530, strike=(60,)),                         # or | fire.
        dict(L=[61], R_=[62, 63], gap=(620, 1300), end=558),                            # Artist | Stephen Bliss
        dict(L=[64, 65], R_=[66, 67], gap=(620, 1300), end=586),                        # had about | a week,
        dict(L=[68, 69], R_=[70], gap=HEAD, end=609),                                   # so he | chopped
        dict(L=[71, 72], R_=[73, 74], gap=HEAD, end=640),                               # up his | own painting.
        dict(L=[75, 76], R_=[77], gap=(500, 1420), end=710),                            # He only | kept (clear of the US cover)
        dict(L=[85, 86], R_=[87, 88, 89, 90], gap=(500, 1420), end=755),                # and boxed | them into a grid.
        dict(L=[91, 92], R_=[93], gap=(940, 1620), end=782),                            # That rush | job?
        dict(L=[94, 95, 96], R_=[97], gap=(630, 1290), end=803),                        # It's been the | template
        dict(L=[98, 99], R_=[100, 101, 102], gap=(630, 1290), end=838),                 # for every | GTA cover  (off before the floating covers)
        dict(L=[103], R_=[104], gap=BOX, end=883),                                      # Vice | City,   (either side of the box)
        dict(L=[105], R_=[106], gap=BOX, end=911),                                      # San | Andreas,
        dict(L=[], R_=[107], gap=BOX, end=920),                                         # IV,
        dict(L=[108], R_=[], gap=BOX, end=940),                                         # V,
        dict(L=[109, 110], R_=[111], gap=COVER, end=974),                               # even GTA | VI,
        dict(L=[112], R_=[113], gap=CENTRE, end=998),                                   # same | boxes,  (off before the match cut)
        dict(L=[114], R_=[115], gap=(500, 1420), end=1021),                             # same | grid,
        dict(L=[116, 117, 118], center=True, end=END),                                  # 25 years later.
    ]
    out = []
    for p in P:
        out += phrase(**p)
    return D.group("Captions (reference style)", 0, END, out)


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


def hud(name, im, d, n=7, seed=1, big=1):
    """Computer-vision tracking boxes on the strongest features of a frame: thin white boxes, a coordinate label at
    each box's corner, a green dot at its centre."""
    g = cv2.cvtColor(cover_img(im), cv2.COLOR_BGR2GRAY)
    pts = cv2.goodFeaturesToTrack(g, 60, 0.03, 110)
    rnd = random.Random(seed)
    pts = [tuple(map(int, p.ravel())) for p in (pts if pts is not None else [])]
    pts = [p for p in pts if 150 < p[0] < 1770 and 120 < p[1] < 960] or [(960, 540)]
    rnd.shuffle(pts); out = []
    for k, (px, py) in enumerate(pts[:n + big]):
        if k < big: bw, bh = rnd.randint(380, 620), rnd.randint(220, 380)
        else: bw, bh = rnd.randint(50, 170), rnd.randint(40, 130)
        x, y = px - bw / 2, py - bh / 2
        r = D.rect(f"{name}: box {k + 1}", 0, d, x, y, bw, bh, HUD_WHITE)
        r["rect"].update({"fillEnabled": False, "strokeEnabled": True, "strokeColor": HUD_WHITE, "strokeWidth": 1.5})
        lab = D.text(f"{name}: label {k + 1}", 0, d, f"x: {px} y: {py}", rl.AR, 13, HUD_WHITE, x, y - 5, axes={"wdth": 100, "wght": 500}, shadow=False)
        dot = D.rect(f"{name}: dot {k + 1}", 0, d, px - 2, py - 2, 4, 4, HUD_DOT)
        out += [lab, r, dot]
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
    spec = [(0, 3, "hud_b01", hikey(1), 7), (3, 6, "hud_b04", None, 6), (6, 8, "A01", hikey(1, .08, .45), 5), (8, 11, "hud_b50", None, 9),
            (15, 18, "hud_b49", None, 7), (18, 21, "hud_b48", hikey(0, .2, .8), 7), (21, 24, "hud_b25", None, 8), (24, 25, "hud_b04b", hikey(1), 4)]
    for k, (f0, f1, a, lk, n) in enumerate(spec):
        d = f1 - f0
        lay = hud(f"HUD {a}", img(a), d, n=n, seed=k + 3) + [still_layer(a, a, d)]
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
    screen, scaled about the body's centre and growing slowly (reference 0:01.5-0:04.4)."""
    bx, by, bw, bh = TVBODY; cx, cy = bx + bw / 2, by + bh / 2
    m = D.rect("TV body (matte)", 0, d, bx, by, bw, bh, [1, 1, 1, 1], roundness=34)
    plate = D.image("A01 TV (lifted)", "A01", 0, d, effects=[D.fx({"type": "levels", "inputBlack": 2, "inputWhite": 62, "gamma": 1.35, "outputBlack": 6, "outputWhite": 225})],
                    matte={"layer": m["id"], "mode": "alpha"})
    g = D.group("CRT", 0, d, screens + [plate, m], tr=T(960, 540, s0, ax=cx, ay=cy))
    D.kf(g, "scaleX", [(0, s0, HOLD), (d * 1.4, s1 + (s1 - s0) * .4, E_OX)]); D.kf(g, "scaleY", [(0, s0, HOLD), (d * 1.4, s1 + (s1 - s0) * .4, E_OX)])
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


def H3():
    """110-145: the GTA III wordmark with tracking boxes, then logos built from tiles (VI, then the European cover)."""
    sh = []
    d = 14; a = R["logo_gta3"]; width = 520; s = width / a["w"]; x0, y0 = 960 - width / 2, 540 - a["h"] * s / 2
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
    sh.append(hit("H3.1 GTA III wordmark + tracking", 110, 124, lay + flash + [word] + thumbs(d, 3)[:9] + [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")]))
    d = 9
    sh.append(hit("H3.2 VI built from tiles", 124, 133, tile_logo("GTA VI logo (B06)", "logo_vi", d, 960, 540, 560, 4, 5) + thumbs(d, 5, 2) +
                  [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")]))
    d = 12; c = R["C02_euro"]
    sh.append(hit("H3.3 European cover built from tiles", 133, 145, tile_logo("European GTA III cover (C02)", "C02_euro", d, 960, 540, c["w"] * 720 / c["h"], 6, 9, .25) +
                  thumbs(d, 5, 3) + [D.image("Tile grid", "tilegrid", 0, d, fit="stretch")]))
    return sh


def H4():
    """145-227: full-frame footage, captions either side of the subject."""
    sh = []
    sh.append(rl.shot("H4.1 European box in hands", 145, 161, [rl.vclip("B09 European box in hands", "B09", 48.5, 16)], dim=10))
    a = R["b09_front"]; sc = W / a["w"]
    tr = lambda: T(960, 540, 100 * sc, ax=a["w"] / 2, ay=a["h"] / 2)
    front = D.image("B09 European box, front (still frame at 50 s)", "b09_front", 0, 28, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]))
    sh.append(rl.shot("H4.2 European box, front + title flash", 161, 189, rl.glow_flash("b09_front_title_mask", 28, tr, a, 1, halo=16, scale=sc) + [front], dim=10))
    # B26 at 875: Bliss alone in the call panel (x 228-1692, y 150-1020): panel scaled to fill
    sh.append(rl.shot("H4.3 Stephen Bliss talking", 189, 207, [rl.vclip("B26 Bliss talking (call panel, filled)", "B26", 875.0, 18, scale=131, cx=960, cy=540 + (540 - 585) * 1.31)], dim=10))
    sh.append(rl.shot("H4.4 Bliss at his mural", 207, 227, [rl.vclip("B27 Bliss at his mural", "B27", 52.0, 20, scale=108)], dim=10))
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
        if t: flashes.append(D.rect(f"White flash @{f0 + t}", t, t + 1, 0, 0, W, H, rl.FLASH, o=85))
        t += dur
    return rl.shot(name, f0, f1, flashes + lay, dim=8)
