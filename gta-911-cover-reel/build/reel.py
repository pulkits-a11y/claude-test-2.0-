"""GTA 9/11 Cover Reel - generator for the editable Tesseract project.

Run with the scratch venv python (needs opencv, uharfbuzz, fonttools):
    python build/reel.py            # prepare assets, write document + keyframes, commit
Outputs GTA911_CoverReel.tsrct at the project root. Everything visible in the reel is a
native Tesseract layer: scene groups > shot groups > look group > media, text layers per
word, film-wide overlays and the logo slot at the top.
"""
import json, math, os, random, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2, numpy as np
from lib import *
import textfit as tf
import prep

X = prep.X
D = Doc()
R = prep.reg
END = 1057                      # 35.233 s, the processed voiceover's length
WORDS = json.load(open(os.path.join(ROOT, "build", "words.json")))
WF = [int(round(w["s"] * FPS)) for w in WORDS]     # onset frame of each word
AR, IS = "Archivo SemiBold", "Instrument Serif"
CAP = {"wdth": 100, "wght": 500}; LAB = {"wdth": 100, "wght": 600}; HEAVY = {"wdth": 62, "wght": 900}; WIDE = {"wdth": 125, "wght": 300}
FULL = (0, 0, W, H)

# ============================================================== assets
def build_assets():
    prep.init_base()
    P = os.path.join(ROOT, "source")
    for n, f in [("tex_grunge", "textures/grunge.jpg"), ("tex_halftone", "textures/halftone.jpg"), ("tex_grain", "textures/grain.jpg"),
                 ("tex_paper", "textures/paper.jpg"), ("A01", "plates/A01.webp"), ("A02", "plates/A02.webp"), ("A03", "plates/A03.webp"),
                 ("A04", "plates/A04.webp")]:
        prep.img(n, path=os.path.join(P, f))
    # prism streak: the build18 .pz gradient (transparent ends, red > amber > green > cyan > violet)
    if "prism" not in R:
        w = 1024; g = np.zeros((128, w, 4), np.float32)
        stops = [(0, (255, 0, 80, 0)), (.14, (255, 40, 60, .85)), (.30, (255, 190, 30, .85)), (.48, (80, 255, 120, .8)),
                 (.66, (30, 200, 255, .85)), (.82, (110, 70, 255, .85)), (1, (220, 40, 255, 0))]
        for x in range(w):
            p = x / (w - 1)
            for (a, ca), (b, cb) in zip(stops, stops[1:]):
                if a <= p <= b:
                    t = (p - a) / (b - a); c = [ca[i] + (cb[i] - ca[i]) * t for i in range(4)]; break
            g[:, x] = [c[2], c[1], c[0], c[3] * 255]
        prep.img("prism", g.astype(np.uint8))
    if "tex_grain_a" not in R:
        g = cv2.imread(os.path.join(P, "textures", "grain.jpg"), cv2.IMREAD_GRAYSCALE).astype(np.float32)
        a = np.clip((g - 14) * 2.2, 0, 255).astype(np.uint8)
        prep.img("tex_grain_a", np.dstack([np.full_like(a, 255)] * 3 + [a]))
    prep.img("logo", path=os.path.join(P, "logo", "logo.png"))
    prep.audio("vo", os.path.join(P, "audio", "GTA911_VO_tight_118.wav"))
    # ---- front pages (B01, 638x480; page column x199-439) - top of each page, masthead to main photo
    pages = {"pg_disaster": (31.14, 300), "pg_actofwar": (324.76, 262), "pg_warathome": (404.84, 250), "pg_siege": (413.74, 268),
             "pg_savaged": (351.46, 160)}
    for n, (t, h) in pages.items(): prep.still(n, "B01", t, crop=(199, 0, 240, h))
    prep.still("C01_outrage", "B01", 360.35, crop=(199, 0, 240, 480))
    # ---- covers from B07 (flat, centred, ~840x1026) and the GTA VI cover from B06
    for n, t in [("III", 37), ("VC", 45), ("SA", 66), ("LCS", 76), ("VCS", 86.5), ("IV", 97), ("EFLC", 107), ("TBOGT", 117),
                 ("CW", 127), ("V", 138), ("VONLINE", 145), ("VI", 162.5)]:
        prep.still("cov_" + n, "B07", t, crop=(544, 30, 834, 1020))
    prep.still("B06_vi_logo", "B06", 9.8)
    # ---- European original cover (B09 at 20 s, flattened from the angled box) = C02 / #12 stand-in
    prep.still("C02_euro", "B09", 20.0, warp=[(372, 113), (872, 120), (940, 716), (318, 716)], size=(900, 1250))
    # ---- disc (C03): circle cut from B09 at 82 s
    if "C03_disc" not in R:
        im = prep.frame("B09", 82.0); cx, cy, r = 663, 356, 352
        sq = im[cy - r:cy + r, cx - r:cx + r].copy(); a = np.zeros(sq.shape[:2], np.uint8); cv2.circle(a, (r, r), r - 2, 255, -1, cv2.LINE_AA)
        prep.img("C03_disc", np.dstack([sq, a]))
    prep.still("C04_ps2box", "B21_0645-0710", 16.0, crop=(580, 270, 720, 810))
    # ---- Bliss stills: B26 solo panel (880 s), B27 close portrait (140.6 s), B28 right half (1720 s)
    prep.still("bliss26", "B26", 880.0, crop=(262, 142, 1416, 856))
    prep.still("bliss27", "B27", 140.6, crop=(0, 120, 1920, 840))
    prep.still("bliss27b", "B27", 32.2, crop=(0, 100, 1920, 880))
    prep.still("bliss28", "B28", 1720.0, crop=(960, 0, 960, 1080))
    for n, t in [("art1", 74.0), ("art2", 78.0), ("art3", 82.0), ("art4", 120.0), ("art5", 42.3)]: prep.still("b27_" + n, "B27", t)
    prep.still("bed_cal_2001", "B22", 103.0)
    for n, t in [("bed34a", 49.0), ("bed34b", 125.0), ("bed34c", 205.0)]: prep.still(n, "B34", t)
    # rotoscoped logo letters (white, alpha = letter mask) for the glow flashes; built from the stills in build/stills, see NOTES
    prep.img("C02_title_mask", path=os.path.join(ROOT, "build", "assets", "img", "C02_title_mask.png"))
    prep.img("cov_VI_vi_mask", path=os.path.join(ROOT, "build", "assets", "img", "cov_VI_vi_mask.png"))


def V(b, t, dur):
    """A video select; returns (asset, src_ms of the wanted moment, intrinsic)."""
    a = prep.sel(b, t, dur)
    return a, int(round(R[a]["lead"] * 1000)), R[a]["dur"]


# ============================================================== drift, prism, dim, shot
def _bez(x1, y1, x2, y2, x):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2; bx = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3
        lo, hi = (t, hi) if bx < x else (lo, t)
    t = (lo + hi) / 2
    return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3

STRETCH = 4.0                                  # drift keys run past the cut so the move is still going at the cut
Y_AT_CUT = _bez(.16, 1, .3, 1, 1 / STRETCH)
SHOT_N = [0]


def drift(layer, d, x0, y0, s_end, full=True):
    """46 px/s sideways (alternating) and 119%->116% (full-frame) or the same ratio on a sized still, ease-out expo."""
    SHOT_N[0] += 1
    sgn = 1 if SHOT_N[0] % 2 else -1
    tr = layer["transform"]
    if layer["type"] == "Group" and list(tr["anchorPoint"]) == [0, 0] and list(tr["position"]) == [0, 0]:
        tr["anchorPoint"], tr["position"] = [x0, y0], [x0, y0]   # a group otherwise scales about its top-left corner
    move = 46 * d / FPS
    s_start = s_end * 119 / 116
    tot_m, tot_s = move / Y_AT_CUT, (s_end - s_start) / Y_AT_CUT
    a = x0 - sgn * move / 2
    D.kf(layer, "positionX", [(0, a, HOLD), (d * STRETCH, a + sgn * tot_m, E_OX)])
    for p in ("scaleX", "scaleY"):
        D.kf(layer, p, [(0, s_start, HOLD), (d * STRETCH, s_start + tot_s, E_OX)])


PZ = {"A": (-90, 36, 780, 92, 5), "B": (1360, 14, 640, 112, -14), "C": (1610, 420, 640, 104, -74), "D": (-330, 560, 640, 104, 80)}
PAIRS = [("A", "C"), ("B", "D"), ("A", "B")]


def prism(d, k):
    out = []
    for j, key in enumerate(PAIRS[k % 3]):
        x, y, w, h, r = PZ[key]
        lay = D.image(f"Prism streak {key}", "prism", 0, d, tr=T(x + w / 2, y + h / 2, r=r, ax=w / 2, ay=h / 2), fit="stretch",
                      rect=(0, 0, w, h), blend="screen", effects=[D.gauss(18)])
        lo, hi = ((28, 46), (22, 38))[j]
        D.kf(lay, "opacity", [(0, lo, HOLD), (d / 2, hi, E_IOC), (d, lo, E_IOC)])
        out.append(lay)
    return out


def shot(name, f0, f1, media, look=None, dim=18, prism_on=True, top=(), bg=True):
    """A shot group: [top extras] > prism streaks > dim > look group(media) > black bed. Times local to the shot."""
    d = f1 - f0
    k = SHOT_N[0]
    lay = list(top)
    if prism_on: lay += prism(d, k)
    if dim: lay.append(D.rect("Dim", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=dim))
    # clip grade (grade_lite) on the framed picture, then the shot's Special B-roll look
    lay.append(D.group("Graded media + look" if look else "Graded media", 0, d, media, effects=GRADE_FX() + (look or [])))
    if bg: lay.append(D.rect("Black", 0, d, 0, 0, W, H, [0, 0, 0, 1]))
    return D.group(name, f0, f1, lay)


# grade_lite.json (the build18 look's light grade) recreated on every clip with native effects:
# adjust -> Primary Grade (same normalised scale), bloom -> Glow, chromaticAberration -> Chromatic Aberration,
# vignette/grain -> Vignette/Grain. filmArtifacts (dust) has no native effect: it comes from the grunge and clip-grain layers.
LITE = json.load(open(os.path.join(ROOT, "source", "reference", "grade_lite.json")))
GRADE = lambda: []        # the grade is applied once per shot, on the framed picture (see shot()), not per layer
def GRADE_FX():
    a, dt, ef = LITE["adjust"], LITE["details"], LITE["effects"]
    return [D.fx({"type": "primaryGrade", "semanticVersion": 1, "exposure": a["exposure"], "contrast": a["contrast"], "highlights": a["highlights"],
                  "shadows": a["shadows"], "whites": a["whites"], "blacks": a["blacks"], "temperature": a["temperature"], "tint": a["tint"],
                  "saturation": a["saturation"], "vibrance": a["vibrance"]}),
            D.fx({"type": "glow", "glowThreshold": 75, "glowRadius": ef["bloomRadius"], "glowIntensity": ef["bloom"]}),
            D.fx({"type": "chromaticAberration", "amount": ef["chromaticAberration"] * 0.5, "direction": ef["chromaticAngle"]}),
            # Tesseract's vignette at the file's 0.42 / midpoint 0.5 darkens the whole frame (and the brief adds a film-wide one),
            # so the radius is opened and the amount eased to keep the centre clear - the closest match to an edge-only vignette.
            D.fx({"type": "vignette", "amount": dt["vignette"] * 0.6, "radius": dt["vignetteMidpoint"] + 0.3, "feather": dt["vignetteFeather"]}),
            D.fx({"type": "grain", "amount": dt["grain"], "size": dt["grainSize"], "softness": 1 - dt["grainRoughness"], "seed": 7})]


def vclip(name, b, t, d, idx=None, fit="cover", rect=FULL, scale=100, cx=960, cy=540, drift_on=True, effects=None, full=True,
          matte=None, rate=1.0):
    a, sm, intr = V(b, t, d / FPS * rate + 0.2)
    ax, ay = rect[0] + rect[2] / 2, rect[1] + rect[3] / 2
    lay = D.video(name, a, 0, d, sm, intr, tr=T(cx, cy, scale, ax=ax, ay=ay), fit=fit, rect=rect,
                  effects=(GRADE() + (effects or [])), matte=matte, rate=rate)
    if drift_on: drift(lay, d, cx, cy, scale)
    return lay


def iclip(name, asset, d, fit="cover", rect=FULL, scale=100, cx=960, cy=540, rot=0, drift_on=True, effects=None, grade=True,
          shadow=None, matte=None, o=100):
    ax, ay = rect[0] + rect[2] / 2, rect[1] + rect[3] / 2
    lay = D.image(name, asset, 0, d, tr=T(cx, cy, scale, r=rot, ax=ax, ay=ay, o=o), fit=fit, rect=rect,
                  effects=((GRADE() if grade else []) + (effects or [])), shadow=shadow, matte=matte)
    if drift_on: drift(lay, d, cx, cy, scale)
    if rot: settle(lay, rot)
    return lay


def settle(lay, rot, n=10):
    """An overlay may come in at an angle but always settles straight."""
    D.kf(lay, "rotation", [(0, rot, HOLD), (n, 0, E_OX)])


def upright(name, asset, d, height=1080, cx=960, cy=540, blur_bed=True, rot=0):
    """Upright object at full height in the middle over a blurred, darkened copy of itself."""
    a = R[asset]; w = a["w"] * height / a["h"]
    out = [iclip(name, asset, d, fit="stretch", rect=(0, 0, w, height), cx=cx, cy=cy, rot=rot, shadow=SHADOW)]
    if blur_bed:
        out.append(D.rect("Bed darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=45))
        out.append(iclip(name + " (blurred bed)", asset, d, fit="cover", effects=[D.gauss(60)], drift_on=False, grade=False))
    return out


def card(name, asset, d, height, cx, cy, rot):
    """A still as a borderless card with a soft shadow, coming in tilted and settling straight."""
    a = R[asset]; w = a["w"] * height / a["h"]
    img = D.image(name + " photo", asset, 0, d, tr=T(w / 2, height / 2, ax=w / 2, ay=height / 2), fit="stretch",
                  rect=(0, 0, w, height), effects=GRADE())
    g = D.group(name, 0, d, [img], tr=T(cx, cy, r=rot, ax=w / 2, ay=height / 2), shadow=SHADOW)
    drift(g, d, cx, cy, 100); settle(g, rot, min(10, d))
    return g


# ============================================================== looks (applied to the look group)
def L_heat(): return [D.shader("heatMap", "heatmap.wgsl", [("amount", 1, 0, 1, "Mix of the thermal ramp over the source.")],
                               "Luminance mapped to #2B0A3D > #8E1A5C > #E8452C > #F7A43A > #FFF3C4 (thermal silhouettes).")]
def L_half(cell=8): return [D.shader("halftonePrint", "halftone.wgsl", [("cell", cell, 2, 64, "Dot pitch in px."), ("contrast", 1.7, .5, 4, "Contrast before screening."),
                                     ("width", W, 1, 8000, "Layer width px."), ("height", H, 1, 8000, "Layer height px.")],
                                     "Greyscale, high contrast, 8 px 45-degree dot screen, #EFE9DF dots on near black.")]
DUO = {"vice": ("#5A0B3C", "#FFB36B"), "red": ("#120606", "#D8322A"), "ember": ("#140B06", "#F08A24")}
def L_duo(k):
    s, h = hexc(DUO[k][0]), hexc(DUO[k][1])
    return [D.shader("duotone" + k.title(), "duotone.wgsl", [("shadow.colorR", s[0], 0, 1, "Shadow colour R"), ("shadow.colorG", s[1], 0, 1, "Shadow colour G"),
            ("shadow.colorB", s[2], 0, 1, "Shadow colour B"), ("high.colorR", h[0], 0, 1, "Highlight colour R"), ("high.colorG", h[1], 0, 1, "Highlight colour G"),
            ("high.colorB", h[2], 0, 1, "Highlight colour B"), ("contrast", 1.25, .5, 4, "Contrast before mapping.")],
            f"Duotone {k}: two flat colours from luminance, {DUO[k][0]} shadows, {DUO[k][1]} highlights.")]
def L_inv(g):
    e = D.shader("invertFlash", "invert.wgsl", [("amount", 0, 0, 1, "1 = negative.")], "Negative on the first 2 frames of the shot.")
    return [e], (lambda grp: D.kf_fx(grp, e, "amount", [(0, 1, HOLD), (2, 0, HOLD)]))
def L_static(d, n=3, base=0.0):
    e = D.shader("tvStatic", "static.wgsl", [("animationTime", 0, 0, 3600, "Engine clock (s)."), ("amount", base, 0, 1, "Static mix."),
                 ("width", W, 1, 8000, "px"), ("height", H, 1, 8000, "px")], "TV static with rolling bars; full on the last 3 frames.")
    return e, (lambda lay: D.kf_fx(lay, e, "amount", [(0, base, HOLD), (d - n, 1, HOLD)]))


def look_group_post(grp, fn):
    fn(grp)


# ============================================================== text
def shadowed(layer): return layer


def words_line(prefix, idxs, texts, key, font, axes, size, y_center, x, align, color, tracking, out_f, scene0, entrance="hard",
               baseline=None):
    """One layer per word, laid out as the finished line; each appears on its spoken frame (scene-local)."""
    if key == "IS":   # Instrument Serif dropped on review: same line in the Archivo caption face, at the old line's width
        size = is_size(" ".join(texts), size); key, font, axes, tracking = "AR", AR, CAP, 0
    xs, ws, tot = tf.line_layout(key, texts, size, axes, tracking, x, align)
    base = baseline if baseline is not None else y_center + tf.cap_height(key, size) / 2
    out = []
    for i, (wi, t) in enumerate(zip(idxs, texts)):
        f0 = WF[wi] - scene0
        lay = D.text(f"{prefix}: {t}", f0, out_f - scene0, t, font, size, color, xs[i], base, axes=axes, tracking=tracking)
        if entrance == "blur": blur_in(lay)
        out.append(lay)
    return out, xs, ws, base


def blur_in(lay, n=6):
    e = D.gauss(24); lay.setdefault("effects", []).append(e)
    D.kf_fx(lay, e, "blurriness", [(0, 24, HOLD), (n, 0, E_OX)])
    D.kf(lay, "opacity", [(0, 0, HOLD), (n, 100, E_OX)])
    return e


def blur_out(lay, dur_f, n=4, e=None):
    if e is None:
        e = D.gauss(0); lay.setdefault("effects", []).append(e)
        D.kf_fx(lay, e, "blurriness", [(dur_f - n, 0, HOLD), (dur_f, 24, E_OX)])
    D.kf(lay, "opacity", [(0, 100, HOLD), (dur_f - n, 100, HOLD), (dur_f, 0, E_OX)])


def pop_in(lay, w, capH, n=5):
    x, y = lay["transform"]["position"]
    lay["transform"]["anchorPoint"] = [w / 2, -capH / 2]; lay["transform"]["position"] = [x + w / 2, y - capH / 2]
    for p in ("scaleX", "scaleY"): D.kf(lay, p, [(0, 112, HOLD), (n, 100, E_OX)])
    D.kf(lay, "opacity", [(0, 0, HOLD), (n, 100, E_OX)])


def smear_in(lay, side=-1, n=6):
    x = lay["transform"]["position"][0]
    e = D.dirblur(0, 90); lay.setdefault("effects", []).append(e)
    D.kf(lay, "positionX", [(0, x + side * 300, HOLD), (n, x, E_OX)])
    D.kf_fx(lay, e, "blurLength", [(0, 140, HOLD), (n, 0, E_OX)])
    D.kf(lay, "opacity", [(0, 0, HOLD), (2, 100, E_OX)])
    return e


def smear_out(lay, dur_f, axis="x", sign=1, n=4, e=None):
    p = lay["transform"]["position"]
    if e is None:
        e = D.dirblur(0, 90 if axis == "x" else 0); lay.setdefault("effects", []).append(e)
    else:
        e["effect"]["direction"] = 90 if axis == "x" else 0
    D.kf_fx(lay, e, "blurLength", [(dur_f - n, 0, HOLD), (dur_f, 160, E_IOX)])
    prop, v = ("positionX", p[0]) if axis == "x" else ("positionY", p[1])
    D.kf(lay, prop, [(dur_f - n, v, HOLD), (dur_f, v + sign * 300, E_IOX)])


def track_in(lay, n=8, final=None):
    """(was a letter-spacing collapse - dropped on review) now the soft blur-in."""
    return blur_in(lay, n)


def big(name, f0, f1, txt, font, size, x, y, axes=None, color=WARM, just="left", tracking=-10, leading=None, shadow=True):
    return D.text(name, f0, f1, txt, font, size, color, x, y, axes=axes, just=just, tracking=tracking, leading=leading, shadow=shadow)


def is_size(txt, size):
    """Archivo size taking the width the old Instrument Serif line had (never larger than the size asked for)."""
    wi = max(tf.advance("IS", l, size, None, -10) for l in txt.split("\n"))
    wa = max(tf.advance("AR", l, size, CAP, 0) for l in txt.split("\n"))
    return round(size * min(1.0, wi / wa))


def IS_big(name, f0, f1, txt, size, x, y, just="center", color=WARM, shadow=True):
    """Big word, set in the Archivo caption face (Instrument Serif dropped on review)."""
    sz = is_size(txt, size)
    return big(name, f0, f1, txt, AR, sz, x, y, axes=CAP, color=color, just=just, tracking=0, leading=sz, shadow=shadow)


def HV_big(name, f0, f1, txt, size, x, y, just="left"):
    return big(name, f0, f1, txt, AR, size, x, y, axes=HEAVY, color=WHITE, just=just, tracking=0, leading=size * 0.9)


def label(name, f0, f1, txt, x, y, size=32, just="center"):
    base = y + tf.cap_height("AR", size) / 2
    return big(name, f0, f1, txt.upper(), AR, size, x, base, axes=LAB, color=WARM, just=just, tracking=500)


def caption(prefix, idxs, texts, y, out_f, s0, x=960, align="center", size=48, entrance="hard"):
    return words_line(prefix, idxs, texts, "AR", AR, CAP, size, y, x, align, WHITE, 0, out_f, s0, entrance)[0]


def wide(prefix, idxs, texts, y, out_f, s0, x=120, size=54):
    return words_line(prefix, idxs, texts, "AR", AR, WIDE, size, y, x, "left", WHITE, 40, out_f, s0, "blur")[0]


# ============================================================== CRT / screen wall helpers
TV = [(766, 287), (1257, 289), (764, 695), (1260, 695)]      # A01 screen glass on the 1920 canvas (cover fit)


def crt(d, screen_layers, zoom=1.0, cx=1011, cy=491):
    """A01 TV with footage pinned into its screen (curve via slight bulge, flicker, glass sheen). zoom about the screen centre."""
    sx, sy = (TV[0][0] + TV[3][0]) / 2, (TV[0][1] + TV[3][1]) / 2
    sheen = D.rect("Glass reflection", 0, d, TV[0][0], TV[0][1], TV[1][0] - TV[0][0], TV[2][1] - TV[0][1], [1, 1, 1, 1], blend="screen", o=7, roundness=40)
    screen = D.group("Screen", 0, d, screen_layers, effects=[D.fx({"type": "bulge", "horizontalRadius": 300, "verticalRadius": 220,
                     "bulgeHeight": 0.25, "centerX": sx, "centerY": sy})] if False else None)
    pl = D.image("A01 TV plate", "A01", 0, d, effects=GRADE())
    g = D.group("TV", 0, d, [sheen, screen, pl], tr=T(cx, cy, 100 * zoom, ax=sx, ay=sy))
    drift(g, d, cx, cy, 100 * zoom)
    # flicker: tiny opacity steps on the screen every 2 frames
    rnd = random.Random(int(d * 97 + cx))
    D.kf(screen, "opacity", [(f, 90 + rnd.random() * 10, HOLD) for f in range(0, d + 1, 2)])
    return g


def pinned(name, b, t, d, effects=None):
    a, sm, intr = V(b, t, d / FPS + 0.2)
    return D.video(name, a, 0, d, sm, intr, effects=(effects or []) + [D.pin(*TV)], fit="cover")


# ============================================================== scenes
SCENES = [(0, 67), (67, 120), (120, 185), (185, 227), (227, 320), (320, 400), (400, 445), (445, 528), (528, 585), (585, 637),
          (637, 710), (710, 752), (752, 853), (853, 936), (936, 969), (969, END)]
TEXT, FLASH_AT = {}, [67, 400, 528, 710, 936]


def S01():
    s0, s1 = SCENES[0]; sh = []; tx = []
    # 1 screen wall with the skyline keyed into every screen (luma matte from the wall's own screens)
    d = 8; base = vclip("B50 CRT wall", "B50", 3.0, d, drift_on=False)
    mt = vclip("B50 screens (matte)", "B50", 3.0, d, effects=[D.fx({"type": "levels", "inputBlack": 120, "inputWhite": 175, "gamma": 1, "outputBlack": 0, "outputWhite": 255})], drift_on=False)
    sky = vclip("B04 skyline in screens", "B04", 2.0, d, matte={"layer": mt["id"], "mode": "luma"}, drift_on=False)
    wall = D.group("Screen wall", 0, d, [sky, mt, base], tr=T(960, 540, ax=960, ay=540)); drift(wall, d, 960, 540, 116)
    sh.append(shot("S1.1 Screen wall", 0, 8, [wall]))
    # 2 CRT, screen ~45% of frame width
    sh.append(shot("S1.2 CRT screen", 8, 13, [crt(5, [pinned("B04 skyline", "B04", 3.5, 5)], zoom=1.75, cx=960, cy=560)]))
    # 3,4,6,7 photo cards + halftone; headline at y300 (match cut)
    for i, (f0, f1, pg, rot) in enumerate([(13, 19, "pg_disaster", -4), (19, 25, "pg_actofwar", 3), (44, 50, "pg_warathome", -2), (50, 57, "pg_siege", 4)]):
        a = R[pg]; hgt = 900 * a["h"] / 300; scale = hgt / a["h"]
        cy = 300 - 35 * scale + hgt / 2 + 14
        sh.append(shot(f"S1.{[3, 4, 6, 7][i]} Front page card", f0, f1, [card(pg, pg, f1 - f0, hgt, 960, cy, rot)], look=L_half(), dim=15))
    # 5 C01 cutout on collage; "9/11" behind the page's lower half
    d = 19; a = R["C01_outrage"]; w = 640; h = a["h"] * w / a["w"]
    cut = iclip("C01 Sept 12 front page (cutout)", "C01_outrage", d, fit="stretch", rect=(0, 0, w, h), cx=960, cy=430 + h / 2, rot=-1.5, shadow=SHADOW)
    nine = big("9/11", 0, d, "9/11", AR, 300, 960, 520, axes=CAP, color=WARM, just="center", tracking=0)   # top half above the page
    bed = [D.rect("Bed darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=60), vclip("B01 front pages (bed)", "B01", 200.0, d, effects=[D.gauss(70)])]
    sh.append(shot("S1.5 Cutout on collage", 25, 44, [cut, nine] + bed, dim=20))
    # 8 CRT, static on the last 3 frames
    st, setst = L_static(10)
    scr = pinned("B04 skyline", "B04", 6.0, 10, effects=[st]); setst(scr)
    sh.append(shot("S1.8 CRT screen + static", 57, 67, [crt(10, [scr], zoom=1.75, cx=960, cy=560)]))
    tx += caption("What if I told you", [0, 1, 2, 3, 4], ["What", "if", "I", "told", "you"], 660, 25, s0)
    tx += caption("is the reason", [7, 8, 9], ["is", "the", "reason"], 660, 67, s0)
    return sh, tx


def mosaic_tiles(d, start_pop, order, skip=((2, 1), (3, 1)), step=2, per=2):
    cw, ch = W / 6, H / 3; lay = []; k = 0
    cells = [(c, r) for r in range(3) for c in range(6) if (c, r) not in skip]
    rnd = random.Random(7); rnd.shuffle(cells)
    for i, (c, r) in enumerate(cells):
        f = start_pop + (i // per) * step
        cov = order[i % len(order)]
        a = R[cov]; gw, gh = cw - 8, ch - 8
        im = D.image(f"Tile {cov[4:]}", cov, f, d, tr=T(c * cw + cw / 2, r * ch + ch / 2, ax=gw / 2, ay=gh / 2), fit="cover", rect=(0, 0, gw, gh), effects=GRADE())
        lay.append(im)
    return lay


def whip_out(grp, d, n=3, dy=-160):
    e = D.dirblur(0, 0); grp.setdefault("effects", []).append(e)
    D.kf_fx(grp, e, "blurLength", [(d - n, 0, HOLD), (d, 40, E_IOX)])
    D.kf(grp, "positionY", [(d - n, 0, HOLD), (d, dy, E_IOX)])


def whip_in(grp, n=3, dy=160):
    e = D.dirblur(40, 0); grp.setdefault("effects", []).append(e)
    D.kf_fx(grp, e, "blurLength", [(0, 40, HOLD), (n, 0, E_OX)])
    D.kf(grp, "positionY", [(0, dy, HOLD), (n, 0, E_OX)])


BOX = {}   # per-clip framing so boxes land in the same spot: (b, t, scale, cx, cy)


def S02():
    s0, s1 = SCENES[1]; sh = []; tx = []
    sh.append(shot("S2.1 GTA VI cover", 67, 75, upright("GTA VI cover (B06 stand-in for #8)", "cov_VI", 8)))
    # VI letters in the B06 frame: x 576-1255, y 270-796 (centre 915.5, 533); scaled into the 632x352 centre hole of the mosaic
    d = 29; sl = 0.6
    hole = D.rect("VI window (matte)", 0, d, 644, 364, 632, 352, [1, 1, 1, 1])
    logo = iclip("GTA VI logo (B06), VI only", "B06_vi_logo", d, fit="cover", scale=100 * sl, cx=960 + 44.5 * sl, cy=540 + 7 * sl, drift_on=False,
                 matte={"layer": hole["id"], "mode": "alpha"})
    tiles = mosaic_tiles(d, 8, ["cov_III", "cov_VC", "cov_SA", "cov_LCS", "cov_IV", "cov_V", "cov_VCS", "cov_EFLC", "cov_TBOGT", "cov_CW", "cov_VONLINE", "cov_VI"])
    g = shot("S2.2 Mosaic build", 75, 104, [logo, hole] + tiles, dim=10)
    whip_out(g, d, 4)
    sh.append(g)
    for i, (f0, f1, b, t, look, sc, cx, cy) in enumerate([(104, 110, "B36", 106.5, None, 98, 1221, 435), (110, 115, "B38", 11.0, L_half(), 94, 704, 498),
                                                          (115, 120, "B39", 67.5, None, 76, 745, 540)]):
        bed = [D.rect("Bed darken", 0, f1 - f0, 0, 0, W, H, [0, 0, 0, 1], o=50), vclip(f"{b} (blurred bed)", b, t, f1 - f0, drift_on=False, effects=[D.gauss(50)], scale=115)]
        sh.append(shot(f"S2.{i + 3} Burst box", f0, f1, [vclip(f"{b} box in hands", b, t, f1 - f0, scale=sc, cx=cx, cy=cy)] + bed, look=look, dim=(12, 45, 12)[i]))
    tx_ = words_line("GTA covers look like", [10, 11, 12, 13], ["GTA", "covers", "look", "like"], "IS", IS, None, 100, 0, 960, "center", WARM, -10, 104, s0, "blur", baseline=920)[0]
    for l in tx_:
        dur = l["activeRange"]["duration"] * FPS // 1000
        smear_out(l, dur, axis="y", sign=-1, n=4)
    tx += tx_
    tx.append(IS_big("this?", WF[14] - s0, s1 - s0, "this?", 260, 1220, 640, just="left"))
    return sh, tx


def S03():
    s0, s1 = SCENES[2]; sh = []; tx = []
    sh.append(shot("S3.1 European box out", 120, 126, [vclip("B09 European box in hands", "B09", 48.5, 6, scale=125, cx=1320)], dim=20))
    disc = iclip("C03 disc", "C03_disc", 6, fit="stretch", rect=(0, 0, 600, 600), cx=1320, cy=540, shadow=GLOW_WHITE, drift_on=False)
    D.kf(disc, "rotation", [(0, 0, HOLD), (6, 90, E_IOX)])
    sh.append(shot("S3.2 Glowing disc", 126, 132, [disc], dim=0))
    sh.append(shot("S3.3 Polaroid flash", 132, 136, [vclip("B11 Polaroid flash", "B11", 120.1, 4)], dim=0))
    # polaroid developing (B10) with C02 comped into the print
    d = 9; pol = vclip("B10 Polaroid developing", "B10", 14.0, d, scale=100, cx=1255, cy=540, drift_on=False)
    photo = D.image("C02 as the photo", "C02_euro", 0, d, tr=T(1320, 565, 100 * 600 / 1250, r=-3, ax=450, ay=625), fit="stretch", rect=(0, 0, 900, 1250), blend="multiply")
    D.kf(photo, "opacity", [(0, 15, HOLD), (d, 85, E_IOC)])
    g = D.group("Polaroid", 0, d, [photo, pol]); drift(g, d, 960, 540, 100)
    sh.append(shot("S3.4 Polaroid", 136, 145, [g], dim=0))
    sh.append(shot("S3.5 Detail: title + logo flash", 145, 154, [detail("C02_euro", EURO["title"], 9, flash="C02_title_mask", flash_at=2)], dim=25))
    sh.append(shot("S3.6 Detail: car", 154, 163, [detail("C02_euro", EURO["car"], 9)], look=L_half(), dim=15))
    d = 22
    cut = flash_still("C02 original cover (cutout)", "C02_euro", "C02_title_mask", d, 860, 960, 540, rot=-3, flash_at=11)
    shelf = [D.rect("Shelf darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=50), iclip("A02 store shelf", "A02", d, effects=[D.gauss(14)])]
    sh.append(shot("S3.7 Cutout on collage + logo flash", 163, 185, [cut] + shelf, dim=10))
    tx += [label("THIS", WF[15] - s0, 145 - s0, "THIS", 120, 250, 32, "left")]
    wx = 120 + tf.advance("AR", "THIS ", 32, LAB, 500)
    tx += [label("WAS", WF[16] - s0, 145 - s0, "WAS", wx, 250, 32, "left")]
    for wi, (t, yb) in zip([17, 18, 19], [("MEANT", 480), ("TO", 660), ("BE", 840)]):
        l = HV_big(t, WF[wi] - s0, 145 - s0, t, 200, 116, yb); blur_out(l, 145 - WF[wi]); tx.append(l)
    return sh, tx


def detail(asset, box, d, name=None, flash=None, flash_at=2):
    """A separate shot framed on one region of a still (x, y, w, h in the still's pixels), with drift.
    flash: a letter-mask asset of the same still; its letters glow-flash for a split second at flash_at."""
    a = R[asset]; x, y, w, h = box
    s = max(W / w, H / h)
    cx, cy = 960 - (x + w / 2 - a["w"] / 2) * s, 540 - (y + h / 2 - a["h"] / 2) * s
    if not flash:
        return iclip(name or f"Detail of {asset}", asset, d, fit="stretch", rect=(0, 0, a["w"], a["h"]), scale=100 * s, cx=cx, cy=cy)
    tr = lambda: T(cx, cy, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2)
    im = D.image(name or f"Detail of {asset}", asset, 0, d, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]))
    g = D.group(f"Detail of {asset} + logo flash", 0, d, glow_flash(flash, d, tr, a, flash_at) + [im], tr=T(960, 540, ax=960, ay=540))
    drift(g, d, 960, 540, 100)
    return g


def glow_flash(mask, d, tr, a, at, peak=100, halo=30, scale=1.0):
    """Rotoscoped glow flash on the logo letters only: the letter mask (white) plus a soft halo of it, flashing up over
    2 frames and dropping away over 5 (screen blend), locked to the still's transform."""
    out = []
    for nm, fx, o in [("Logo flash halo (wide)", [D.gauss(halo * 2.2 / scale)], peak), ("Logo flash halo", [D.gauss(halo / scale)], peak), ("Logo flash", [], peak * 0.85)]:
        l = D.image(nm, mask, 0, d, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]), blend="screen", effects=fx or None, o=0)
        D.kf(l, "opacity", [(0, 0, HOLD), (at, 0, HOLD), (at + 2, o, E_OX), (at + 7, 0, E_OX)])   # a split second: up in 2, gone in 5
        out.append(l)
    return out


def flash_still(name, asset, mask, d, height, cx, cy, rot=0, flash_at=10, blur_bed=False):
    """A still at a given height (straight once settled) whose logo letters glow-flash at flash_at."""
    a = R[asset]; w = a["w"] * height / a["h"]
    tr = lambda: T(w / 2, height / 2, ax=a["w"] / 2, ay=a["h"] / 2, s=100 * height / a["h"])
    im = D.image(name, asset, 0, d, tr=tr(), fit="stretch", rect=(0, 0, a["w"], a["h"]))
    g = D.group(name + " + logo flash", 0, d, glow_flash(mask, d, tr, a, flash_at, halo=24, scale=height / a["h"]) + [im], tr=T(cx, cy, r=rot, ax=w / 2, ay=height / 2), shadow=SHADOW)
    drift(g, d, cx, cy, 100)
    if rot: settle(g, rot)
    return g


def S04():
    s0, s1 = SCENES[3]; sh = []; tx = []
    # one held shot for the whole line: the letters of "Six months" filled with the painting itself (the European cover art)
    d = 42
    m = big("Six months (matte)", 0, d, "Six months", AR, 300, 960, 640, axes={"wdth": 100, "wght": 700}, color=WHITE, just="center", tracking=0, shadow=False)
    m["sourceText"]["fontSize"] = round(1560 / tf.advance("AR", "Six months", 1, {"wdth": 100, "wght": 700}))
    blur_in(m, 8)
    a = R["C02_euro"]
    paint = iclip("C02 cover painting in the letters", "C02_euro", d, fit="stretch", rect=(0, 0, a["w"], a["h"]), scale=100 * 1920 / a["w"], cy=380,
                  matte={"layer": m["id"], "mode": "alpha"})
    sh.append(shot("S4.1 The painting in the type", 185, 227, [paint, m], dim=0))
    tx += wide("of painting.", [26, 27], ["of", "painting."], 940, 227, s0)
    return sh, tx


# crops kept to about 3x so the 720p-sourced cover still reads (they were up to 9x and turned to mush)
EURO = {"gun": (20, 250, 600, 338), "flames": (0, 640, 620, 349), "building": (0, 170, 900, 506),
        "face": (200, 400, 560, 315), "car": (100, 800, 700, 394), "title": (110, 20, 690, 388)}
SPLIT = {"gun": (250, 420), "flames": (220, 830), "building": (660, 420)}   # panel centres for the borderless split


def S05():
    s0, s1 = SCENES[4]; sh = []; tx = []
    sh.append(shot("S5.1 Original cover", 227, 236, upright("C02 original cover (#12 stand-in)", "C02_euro", 9), dim=30))
    sh.append(shot("S5.2 Detail: the gun", 236, 244, [detail("C02_euro", EURO["gun"], 8)]))
    sh.append(shot("S5.3 Gameplay: shooting", 244, 252, [vclip("B49 GTA III shooting", "B49", 28.5, 8)], look=L_heat(), dim=0))
    sh.append(shot("S5.4 Detail: the flames", 252, 260, [detail("C02_euro", EURO["flames"], 8)]))
    inv, setinv = L_inv(None)
    g = shot("S5.5 Gameplay: explosion", 260, 270, [vclip("B49 GTA III explosion", "B49", 99.4, 10)], look=inv, dim=12); setinv(g["layers"][-2])
    sh.append(g)
    sh.append(shot("S5.6 Burning buildings", 270, 294, [detail("C02_euro", EURO["building"], 24)]))
    sh.append(shot("S5.8 Split screen", 294, 309, split3(15)))
    sh.append(shot("S5.9 Original cover, wider", 309, 320, upright("C02 original cover", "C02_euro", 11, height=980), dim=25))
    tx += caption("It had", [28, 29], ["It", "had"], 660, 236, s0)
    capH = tf.cap_height("AR", 280)
    l = HV_big("GUNS", 236 - s0, 258 - s0, "GUNS", 280, 116, 400); pop_in(l, tf.advance("AR", "GUNS", 280, HEAVY), capH); tx.append(l)
    wF = tf.advance("AR", "FIRE", 300, HEAVY)
    l = HV_big("FIRE", 258 - s0, 275 - s0, "FIRE", 300, 1804 - wF, 980); pop_in(l, wF, tf.cap_height("AR", 300)); tx.append(l)
    xs, ws, _ = tf.line_layout("AR", ["BURNING", "BUILDINGS"], 200, HEAVY, 0, 960, "center")
    tx.append(HV_big("BURNING", WF[33] - s0, 299 - s0, "BURNING", 200, xs[0], 640))
    tx.append(HV_big("BUILDINGS", WF[34] - s0, 299 - s0, "BUILDINGS", 200, xs[1], 640))
    tx += caption("all over it.", [35, 36, 37], ["all", "over", "it."], 980, 320, s0)
    return sh, tx


def panel(name, d, x, y, w, h, content):
    """A panel: content clipped to a rectangle via an alpha track matte."""
    m = D.rect(name + " panel matte", 0, d, x, y, w, h, [1, 1, 1, 1])
    for c in content: c["trackMatte"] = {"layer": m["id"], "mode": "alpha"}
    return [D.group(name, 0, d, content + [m])] if len(content) > 1 else content + [m]


def split3(d):
    """Three 640 px panels edge to edge (no borders), each a ~1.8x crop of the cover."""
    out = []; s = 1.8
    for i, k in enumerate(["gun", "flames", "building"]):
        x0 = i * 640; a = R["C02_euro"]; px, py = SPLIT[k]
        im = D.image(f"Panel {k}", "C02_euro", 0, d, tr=T(x0 + 320, 540, 100 * s, ax=px, ay=py), fit="stretch",
                     rect=(0, 0, a["w"], a["h"]), effects=GRADE())
        drift(im, d, x0 + 320, 540, 100 * s)
        out += panel(f"Panel {k}", d, x0, 0, 640, H, [im])
    return out


def S06():
    s0, s1 = SCENES[5]; sh = []; tx = []
    sh.append(shot("S6.1 CRT: Sept 12 skyline", 320, 364, [crt(44, [pinned("B04 skyline (stand-in for #19 ITN)", "B04", 10.0, 44)], zoom=1.0, cy=491)], dim=12))
    # six weeks: the PS2 box on the right (comes in tilted, settles straight); one left-aligned text block on the left
    d = 36; a = R["C04_ps2box"]
    cut = iclip("C04 PS2 box (B21 still)", "C04_ps2box", d, fit="stretch", rect=(0, 0, a["w"] * 760 / a["h"], 760), cx=1390, cy=540, rot=3, shadow=SHADOW)
    bed = [D.rect("Bed darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=60), vclip("B20 GTA III boxes (blurred bed)", "B20", 9.5, d, effects=[D.gauss(55)], drift_on=False)]
    sh.append(shot("S6.2 PS2 box, six weeks", 364, 400, [cut] + bed, dim=10))
    tx += words_line("Then 9/11 hit.", [38, 39, 41], ["Then", "9/11", "hit."], "IS", IS, None, 90, 0, 960, "center", WARM, -10, 364, s0, "hard", baseline=920)[0]
    sz = 150; l = big("six weeks", 364 - s0, s1 - s0, "six weeks", AR, sz, 160, 560, axes=CAP, color=WARM, just="left", tracking=0); blur_in(l); tx.append(l)
    tx += caption("before launch", [44, 45], ["before", "launch"], 0, s1, s0, x=164, align="left", size=52)
    for l in tx[-2:]: l["transform"]["position"][1] = 650
    return sh, tx


def blur_in_layer(l): return l


def S07():
    s0, s1 = SCENES[6]; sh = []; tx = []
    sh.append(shot("S7.1 CRT: Rockstar logo", 400, 413, [crt(13, [pinned("Rockstar logo (B39 stand-in for #25 boot)", "B39", 537.6, 13)], zoom=1.45, cx=960, cy=560)], dim=12))
    d = 9
    base = vclip("B24 paper tear", "B24", 0.9, d, effects=[D.fx({"type": "levels", "inputBlack": 150, "inputWhite": 255, "gamma": 1, "outputBlack": 0, "outputWhite": 255})], drift_on=False, rate=0.5, scale=170, cy=40)
    mt = vclip("B24 paper (matte)", "B24", 0.9, d, effects=[D.fx({"type": "levels", "inputBlack": 185, "inputWhite": 215, "gamma": 1, "outputBlack": 0, "outputWhite": 255})], drift_on=False, rate=0.5, scale=170, cy=40)
    a = R["C02_euro"]
    cov = D.image("C02 on the paper", "C02_euro", 0, d, tr=T(960, 540, 100 * 1080 / a["h"], ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]),
                  blend="multiply", matte={"layer": mt["id"], "mode": "luma"}, effects=GRADE())
    sh.append(shot("S7.2 Paper comp: the cover tears", 413, 422, [cov, mt, base], dim=0))
    sh.append(shot("S7.3 Torn pieces", 422, 426, [vclip("B24 torn paper", "B24", 1.25, 4, scale=190, cy=0)], look=L_duo("red"), dim=0))
    d = 19; ca = R["C02_euro"]; h = 900; w = ca["w"] * h / ca["h"]
    left = iclip("C02 original cover (left panel)", "C02_euro", d, fit="stretch", rect=(0, 0, w, h), cx=480, cy=540)
    sh.append(shot("S7.4 Split: Europe | US", 426, 445, panel("Left panel", d, 0, 0, 960, H, [left]) + [D.rect("Right panel (black)", 0, d, 960, 0, 960, H, [0, 0, 0, 1])], dim=0))
    tx.append(label("ROCKSTAR", WF[46] - s0, 413 - s0, "ROCKSTAR", 960, 980, 32))
    l = HV_big("PULLED", 413 - s0, 422 - s0, "PULLED", 340, 960 - tf.advance("AR", "PULLED", 340, HEAVY) / 2, 680)
    e = smear_in(l, -1, 4); smear_out(l, 9, "x", 1, 3, e); tx.append(l)
    tx += caption("it", [48], ["it"], 660, 426, s0)
    tx.append(label("EUROPE", 426 - s0, s1 - s0, "EUROPE", 120, 980, 30, "left"))
    tx += words_line("in the US.", [49, 50, 51], ["in", "the", "US."], "IS", IS, None, 110, 0, 1440, "center", WARM, -10, s1, s0, "blur", baseline=600)[0]
    return sh, tx


STROKES = []


def brush_strike(name, f0, f1, x, w, base, size, n=6):
    """A hand-drawn charcoal slash (rendered with p5.brush, build/brush) drawn on left to right with a wipe matte."""
    key = "stroke_" + name.split(": ")[-1].strip(".")
    cw, ch = int(w + 120), 220
    STROKES.append({"name": key, "w": cw, "h": ch, "pad": 40, "color": "#ffffff", "brush": "charcoal", "weight": 7,
                    "seed": 11 + len(STROKES) * 7, "angle": -5, "passes": 2, "gap": 10, "scale": 3})
    make_strokes()
    cx, cy = x + w / 2, base - tf.cap_height("AR", size) * 0.42
    x0, y0 = cx - cw / 2, cy - ch / 2
    wipe = D.rect(name + " (wipe matte)", f0, f1, x0, y0, cw, ch, [1, 1, 1, 1], tr=T(x0, y0, ax=x0, ay=y0))
    D.kf(wipe, "scaleX", [(0, 0, HOLD), (n, 100, E_OX)])
    img = D.image(name, key, f0, f1, tr=T(cx, cy, ax=cw / 2, ay=ch / 2), fit="stretch", rect=(0, 0, cw, ch),
                  matte={"layer": wipe["id"], "mode": "alpha"})
    return [img, wipe]


def make_strokes():
    """Renders any stroke not yet imported: white-on-black from p5.brush, then coloured #D8322A with the brightness as alpha."""
    todo = [s for s in STROKES if s["name"] not in R]
    if not todo: return
    bdir = os.path.join(ROOT, "build", "brush"); out = os.path.join(ROOT, "build", "assets", "strokes"); os.makedirs(out, exist_ok=True)
    subprocess.run(["node", os.path.join(bdir, "render.js"), json.dumps(todo), out], check=True, capture_output=True)
    col = np.array([0x2A, 0x32, 0xD8], np.uint8)
    for s_ in todo:
        g = cv2.imread(os.path.join(out, s_["name"] + ".png"), cv2.IMREAD_GRAYSCALE)
        prep.img(s_["name"], np.dstack([np.full_like(g, col[0]), np.full_like(g, col[1]), np.full_like(g, col[2]), g]))


def strike(name, f0, f1, x, w, base, size):
    r = D.rect(name, f0, f1, 0, 0, w, 12, WARM, tr=T(x, base - size * 0.28, ax=0, ay=6))
    D.kf(r, "scaleX", [(0, 0, HOLD), (5, 100, E_OX)])
    return r


def S08():
    s0, s1 = SCENES[7]; sh = []; tx = []
    sh.append(shot("S8.1 Bliss in the studio", 445, 462, [vclip("B27 Bliss in the gallery (stand-in for #28)", "B27", 58.5, 17)], dim=20))
    d = 14
    paper = [iclip("paper.jpg", "tex_paper", d, grade=False), D.rect("#ECE7E0", 0, d, 0, 0, W, H, hexc("#ECE7E0"))]
    paper[0]["blendMode"] = "multiply"
    ink = words_line("couldn't show", [55, 56], ["couldn't", "show"], "IS", IS, None, 160, 0, 960, "center", INK, -10, 476, 462, "blur", baseline=600)[0]
    sh.append(shot("S8.2 Paper card", 462, 476, ink + paper, dim=0, prism_on=False))
    sh.append(shot("S8.3 Gameplay: shooting", 476, 495, [vclip("B49 GTA III shooting", "B49", 30.0, 19)], look=L_half(), dim=10))
    sh.append(shot("S8.4 Liberty City at night", 495, 505, [vclip("B25 Liberty City at night", "B25", 41.0, 10)], look=L_duo("vice"), dim=0))
    inv, setinv = L_inv(None)
    g = shot("S8.5 Explosion", 505, 521, [vclip("B49 explosion", "B49", 99.2, 16)], look=inv, dim=12); setinv(g["layers"][-2]); sh.append(g)
    d = 7; st, setst = L_static(d)
    base = vclip("B50 CRT wall", "B50", 20.0, d, drift_on=False)
    mats, clips = [], []
    for i, (b, t, lk) in enumerate([("B49", 30.6, L_half()), ("B25", 41.4, L_duo("vice")), ("B49", 99.8, None)]):
        mt = vclip(f"B50 screens third {i + 1} (matte)", "B50", 20.0, d, drift_on=False,
                   effects=[D.fx({"type": "levels", "inputBlack": 120, "inputWhite": 175, "gamma": 1, "outputBlack": 0, "outputWhite": 255})])
        m3 = D.rect(f"Third {i + 1}", 0, d, i * 640, 0, 640, H, [1, 1, 1, 1])
        c = vclip(f"Clip {i + 1} in screens", b, t, d, drift_on=False, effects=lk, matte={"layer": mt["id"], "mode": "luma"})
        clips.append(D.group(f"Screens third {i + 1}", 0, d, [c, mt], matte={"layer": m3["id"], "mode": "alpha"})); clips.append(m3)
    wall = D.group("Screen wall", 0, d, clips + [base], effects=[st]); setst(wall)
    sh.append(shot("S8.6 Screen wall + static", 521, 528, [wall], dim=10))
    tx += caption("The new cover", [52, 53, 54], ["The", "new", "cover"], 960, 462, s0, x=120, align="left")
    for wi, t, size, f1 in [(57, "guns", 280, 495), (58, "buildings", 260, 505)]:
        f0 = WF[wi]; sz = is_size(t, size); w = tf.advance("AR", t, sz, CAP)
        tx.append(IS_big(t, f0 - s0, f1 - s0, t, size, 960, 640)); tx[0:0] = brush_strike(f"strike: {t}", f0 + 2 - s0, f1 - s0, 960 - w / 2, w, 640, sz)
    sz = is_size("or fire.", 280); xs_, ws_, _ = tf.line_layout("AR", ["or", "fire."], sz, CAP, 0, 960, "center")
    tx.append(big("or", 505 - s0, 521 - s0, "or", AR, sz, xs_[0], 640, axes=CAP, color=WARM, tracking=0))
    tx.append(big("fire.", WF[60] - s0, 521 - s0, "fire.", AR, sz, xs_[1], 640, axes=CAP, color=WARM, tracking=0))
    tx[0:0] = brush_strike("strike: fire", WF[60] + 2 - s0, 521 - s0, xs_[1], ws_[1] - tf.advance("AR", ".", sz, CAP), 640, sz)
    return sh, tx


FACE = {}


def bliss_card(name, asset, d, rot, cx=960):
    """820 px card cut around the face (face 34% of the card height, centred at 45% down), so his face sits at
    (cx, 460) at the same size on every card."""
    k = "card_" + asset
    if k not in R:
        im = cv2.imread(R[asset]["path"]); fx, fy, fw = FACE[asset]
        ch = fw / 0.34; cw = ch * 0.78; x0, y0 = int(fx - cw / 2), int(fy - 0.45 * ch)
        pad = cv2.copyMakeBorder(im, 2000, 2000, 2000, 2000, cv2.BORDER_REPLICATE)
        prep.img(k, pad[y0 + 2000:y0 + 2000 + int(ch), x0 + 2000:x0 + 2000 + int(cw)])
    return card(name, k, d, 820, cx, 460 - 0.45 * 820 + 410, rot)


def S09():
    s0, s1 = SCENES[8]; sh = []; tx = []
    for i, (f0, f1, asset, rot) in enumerate([(528, 532, "bliss26", -4), (532, 536, "bliss27b", 3), (536, 540, "bliss28", -2)]):
        sh.append(shot(f"S9.{i + 1} Photo card", f0, f1, [bliss_card(f"Bliss photo #{asset[-2:]}", asset, f1 - f0, rot)], dim=10))
    # heat map + strip of the real eyes (same still, same framing)
    d = 10; a = R["bliss26"]; fx, fy, fw = FACE["bliss26"]; s = 520 / fw
    cx, cy = 960 + (a["w"] / 2 - fx) * s, 540 + (a["h"] / 2 - fy) * s
    heat = D.group("Heat map face", 0, d, [D.image("Bliss #26 (heat)", "bliss26", 0, d, tr=T(cx, cy, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]))], effects=L_heat())
    ey = 540 - 0.12 * 520
    strip_m = D.rect("Eye strip 1920x160", 0, d, 0, ey - 80, W, 160, [1, 1, 1, 1])
    eyes = D.image("C06 eyes strip (real)", "bliss26", 0, d, tr=T(cx, cy, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]),
                   matte={"layer": strip_m["id"], "mode": "alpha"}, effects=GRADE())
    g = D.group("Heat map + eye strip", 0, d, [eyes, strip_m, heat]); drift(g, d, 960, 540, 100)
    sh.append(shot("S9.4 Heat map + eye strip", 540, 550, [g], dim=0))
    # C05: person matte on the B26 still, over a dark blurred bed of his artwork; "Bliss" behind
    # head top (y~100 in the still) at y 140, shirt running off the bottom of the frame
    d = 22; a = R["bliss26"]; fx, fy, fw = FACE["bliss26"]; s = 960 / (a["h"] - 100)
    cx, cy = 960 + (a["w"] / 2 - fx) * s, 140 - 100 * s + a["h"] * s / 2
    prep.img("C05_bliss_cutout", path=os.path.join(ROOT, "build", "assets", "img", "C05_bliss_cutout.png"))
    d = 35
    arts = [iclip(f"Artwork {k}", f"b27_art{k}", d, fit="cover", rect=(i * 480, 0, 480, H), cx=i * 480 + 240, effects=[D.gauss(30)], drift_on=False) for i, k in enumerate([1, 2, 3, 4])]
    cut = iclip("C05 Bliss cutout (head and shoulders, B26 still)", "C05_bliss_cutout", d, fit="stretch", rect=(0, 0, a["w"], a["h"]), scale=100 * s, cx=cx, cy=cy,
                shadow=SHADOW)
    sh.append(shot("S9.5 Cutout on collage", 550, 585, [cut, D.rect("Bed darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=55)] + arts, dim=0))
    tx += caption("Artist", [61], ["Artist"], 500, 550, s0, x=700, align="right")
    tx += caption("Stephen", [62], ["Stephen"], 500, 550, s0, x=1220, align="left")
    tx.append(label("STEPHEN BLISS · GTA COVER ARTIST", 550 - s0, 585 - s0, "STEPHEN BLISS · GTA COVER ARTIST", 960, 96, 30))
    tx += caption("had about", [64, 65], ["had", "about"], 990, 572, s0)
    w = tf.advance("AR", "A WEEK", 320, HEAVY)
    l = HV_big("A WEEK", 572 - s0, s1 - s0, "A WEEK", 320, 960 - w / 2, 680); pop_in(l, w, tf.cap_height("AR", 320)); tx.append(l)
    return sh, tx


def S10():
    s0, s1 = SCENES[9]; sh = []; tx = []
    sh.append(shot("S10.1 Blade through paper", 585, 604, [vclip("B30 blade cutting paper", "B30", 0.6, 19, rate=0.6)], dim=12))
    d = 5; a = R["C02_euro"]
    base = vclip("B30 blade", "B30", 2.4, d, drift_on=False, rate=0.6)
    mt = vclip("B30 paper (matte)", "B30", 2.4, d, drift_on=False, rate=0.6, effects=[D.fx({"type": "levels", "inputBlack": 120, "inputWhite": 170, "gamma": 1, "outputBlack": 0, "outputWhite": 255})])
    cov = D.image("C02 on the paper", "C02_euro", 0, d, tr=T(960, 540, 100 * 1500 / a["w"], ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]),
                  blend="multiply", matte={"layer": mt["id"], "mode": "luma"})
    sh.append(shot("S10.2 Paper comp: blade and cover", 604, 609, [cov, mt, base], dim=0))
    sh.append(shot("S10.3 Hands working", 609, 619, [vclip("B31 Bliss working", "B31", 51.0, 10, scale=130)], look=L_half(), dim=10))
    sh.append(shot("S10.4 Detail: a face", 619, 627, [detail("C02_euro", EURO["face"], 8)]))
    d = 10; wt = D.rect("Whiteout", 0, d, 0, 0, W, H, FLASH)
    D.kf(wt, "opacity", [(0, 0, HOLD), (4, 0, HOLD), (10, 95, E_IOX)])
    sh.append(shot("S10.5 Detail: a car, whiteout", 627, 637, [detail("C02_euro", EURO["car"], 10)], top=[wt], dim=0))
    tx += caption("So he", [68, 69], ["So", "he"], 660, 602, s0)
    # CHOPPED splits along the blade's line at 606: two copies, each matted to one side of a tilted line
    w = tf.advance("AR", "CHOPPED", 340, HEAVY); x0 = 960 - w / 2; f0, f1 = 602 - s0, 609 - s0
    for half, (dx, dy, mx) in {"top": (-30, -30, 0), "bottom": (30, 30, 1)}.items():
        m = D.rect(f"CHOPPED {half} matte", f0, f1, -400, 0, 2720, 1400, [1, 1, 1, 1], tr=T(960, 560 + (-700 if half == "top" else 700), r=-18, ax=960, ay=700))
        l = HV_big(f"CHOPPED ({half} half)", f0, f1, "CHOPPED", 340, x0, 680); l["trackMatte"] = {"layer": m["id"], "mode": "alpha"}
        D.kf(l, "positionX", [(4, x0, HOLD), (10, x0 + dx, E_OX)]); D.kf(l, "positionY", [(4, 680, HOLD), (10, 680 + dy, E_OX)])
        tx += [l, m]
    ws = wide("up his own painting.", [71, 72, 73, 74], ["up", "his", "own", "painting."], 960, s1, s0)
    for l in ws:
        dur = l["activeRange"]["duration"] * FPS // 1000
        D.kf(l, "opacity", [(0, 0, HOLD), (6, 100, E_OX), (dur - 6, 100, HOLD), (dur, 0, E_IOX)])
    tx += ws
    return sh, tx


P3 = {"L1": (50, 42, 312, 247), "L2": (50, 264, 312, 490), "L3": (50, 505, 312, 742), "L4": (50, 765, 312, 978), "M1": (335, 50, 555, 201),
      "M2": (335, 209, 555, 432), "M3": (335, 440, 555, 537), "M4": (335, 544, 555, 746), "M5": (335, 763, 555, 978), "R1": (572, 50, 782, 235),
      "R2": (572, 248, 782, 487), "R3": (572, 506, 782, 735), "R4": (572, 766, 782, 985)}   # GTA III grid panels in cov_III pixels (+3,+3 offset)


def S11():
    s0, s1 = SCENES[10]; sh = []; tx = []
    wt = D.rect("Clearing from white", 0, 15, 0, 0, W, H, FLASH); D.kf(wt, "opacity", [(0, 95, HOLD), (6, 0, E_OX)])
    sh.append(shot("S11.1 The US grid cover", 637, 652, upright("US GTA III cover (B07 stand-in for #32)", "cov_III", 15), top=[wt]))
    def pbox(k): x0, y0, x1, y1 = P3[k]; return (x0 - 3, y0 - 3, x1 - x0, y1 - y0)
    sh.append(shot("S11.2 Detail: face panel", 652, 660, [detail("cov_III", pbox("M4"), 8)]))
    sh.append(shot("S11.3 Cutscene close-up", 660, 674, [vclip("B48 GTA III cutscene", "B48", 30.0, 14, scale=120)], look=L_duo("vice"), dim=0))
    sh.append(shot("S11.4 Detail: car panel", 674, 683, [detail("cov_III", pbox("L3"), 9)]))
    sh.append(shot("S11.5 Car chase", 683, 693, [vclip("B48 GTA III car chase", "B48", 102.0, 10)], look=L_heat(), dim=0))
    sh.append(shot("S11.6 Detail: helicopter panel", 693, 700, [detail("cov_III", pbox("L1"), 7)]))
    inv, setinv = L_inv(None)
    g = shot("S11.7 Police helicopter", 700, 710, [vclip("B49 helicopter in flight", "B49", 26.0, 10, scale=140, cy=640)], look=inv, dim=10); setinv(g["layers"][-2]); sh.append(g)
    tx += words_line("He only kept", [75, 76, 77], ["He", "only", "kept"], "IS", IS, None, 100, 0, 960, "center", WARM, -10, 652, s0, "blur", baseline=940)[0]
    return sh, tx


def grid_rects():
    a = R["cov_III"]; s = H / a["h"]; ox = (W - a["w"] * s) / 2
    return {k: (ox + (x0 - 3) * s, (y0 - 3) * s, (x1 - x0) * s, (y1 - y0) * s) for k, (x0, y0, x1, y1) in P3.items()}, s, ox


def S12():
    s0, s1 = SCENES[11]; sh = []; tx = []
    G, s, ox = grid_rects(); a = R["cov_III"]
    order = ["L1", "M1", "R1", "L2", "R2", "M2", "L3", "M3", "R3", "M4", "L4", "M5", "R4"]
    srcs = [("B48", 30), ("B49", 26), ("B48", 102), ("B48", 150), ("B49", 28.5), ("B48", 200), ("B48", 250), ("B48", 300), ("B49", 31), ("B48", 350),
            ("B48", 400), ("B48", 450), ("B48", 500)]
    d = 28; lay = []
    for i, k in enumerate(order):
        x, y, w, h = G[k]; f = i * 2
        c = vclip(f"Panel {k} gameplay", srcs[i][0], srcs[i][1], d - f, drift_on=False, fit="cover", rect=(0, 0, w, h), cx=x + w / 2, cy=y + h / 2)
        m = D.rect(f"Panel {k}", 0, d - f, x, y, w, h, [1, 1, 1, 1]); c["trackMatte"] = {"layer": m["id"], "mode": "alpha"}
        lay.append(D.group(f"Panel {k}", f, d, [c, m]))
    sh.append(shot("S12.1 Live grid", 710, 738, lay, dim=0))
    d = 9; lay2 = []
    cover = D.image("US GTA III cover (full)", "cov_III", 7, d, tr=T(960, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]))
    lay2.append(cover)
    for i, k in enumerate(order):
        x, y, w, h = G[k]; sw = i // 2
        art = D.image(f"Panel {k} cover art", "cov_III", sw, d, tr=T(960, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]))
        m = D.rect(f"Panel {k} (art)", sw, d, x, y, w, h, [1, 1, 1, 1]); art["trackMatte"] = {"layer": m["id"], "mode": "alpha"}
        c = vclip(f"Panel {k} gameplay", srcs[i][0], srcs[i][1] + 0.9, d, drift_on=False, fit="cover", rect=(0, 0, w, h), cx=x + w / 2, cy=y + h / 2)
        m2 = D.rect(f"Panel {k} (play)", 0, d, x, y, w, h, [1, 1, 1, 1]); c["trackMatte"] = {"layer": m2["id"], "mode": "alpha"}
        lay2 += [art, m, c, m2]
    sh.append(shot("S12.2 Live grid turns into the cover", 738, 747, lay2, dim=0))
    g = shot("S12.3 US box in hands", 747, 752, [vclip("B36 GTA III box in hands", "B36", 106.5, 5, scale=110, cx=960, cy=540)], dim=12)
    whip_out(g, 5, 3); sh.append(g)
    # right-aligned to x 520 around y 660, set on two lines: one line would start left of the x 96 safe margin
    tx += caption("and boxed", [85, 86], ["and", "boxed"], 630, 745, s0, x=520, align="right", size=46)
    tx += caption("them into a", [87, 88, 89], ["them", "into", "a"], 690, 745, s0, x=520, align="right", size=46)
    l = IS_big("grid.", WF[90] - s0, s1 - s0, "grid.", 240, 1400, 640, just="left"); smear_out(l, s1 - WF[90], "y", -1, 3); tx.append(l)
    return sh, tx


def S13():
    s0, s1 = SCENES[12]; sh = []; tx = []
    for i, (f0, f1, asset, rot) in enumerate([(752, 760, "bliss26", -4), (760, 780, "bliss28", 3)]):
        c = bliss_card(f"Bliss photo #{asset[-2:]}", asset, f1 - f0, rot, cx=1280); sh.append(shot(f"S13.{i + 1} Photo card", f0, f1, [c], dim=10))
    def box(d, h=760, cx=960, rot=-2):
        a = R["cov_III"]; w = a["w"] * h / a["h"]
        return iclip("C07 US GTA III box (cutout)", "cov_III", d, fit="stretch", rect=(0, 0, w, h), cx=cx, cy=540, rot=rot, shadow=SHADOW)
    d = 16; bed = [D.rect("Bed darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=60)] + [iclip(f"#34 still {k}", k, d, fit="cover", rect=(i * 640, 0, 640, H), cx=i * 640 + 320, effects=[D.gauss(45)], drift_on=False) for i, k in enumerate(["bed34a", "bed34b", "bed34c"])]
    sh.append(shot("S13.4 Cutout on collage", 780, 796, [box(d)] + bed, dim=0))
    d = 20
    tiles = mosaic_tiles(d, 0, ["cov_VC", "cov_SA", "cov_LCS", "cov_VCS", "cov_IV", "cov_EFLC", "cov_TBOGT", "cov_CW", "cov_V", "cov_VONLINE", "cov_VI"], skip=((2, 0), (3, 0), (2, 1), (3, 1), (2, 2), (3, 2)))
    behind = IS_big("template", 0, d, "template", 360, 960, 660)
    sh.append(shot("S13.5 Mosaic build", 796, 816, [box(d, rot=0), behind] + tiles, dim=0))
    for i, (f0, f1, k, nm) in enumerate([(816, 821, "cov_VC", "Vice City"), (821, 827, "cov_SA", "San Andreas"), (827, 832, "cov_IV", "GTA IV"), (832, 838, "cov_V", "GTA V")]):
        m = [box(f1 - f0, rot=0)]; m[0]["source"]["assetId"] = k; m[0]["name"] = f"{nm} box face (B07 cover, same spot and size as the III box)"
        sh.append(shot(f"S13.{6 + i} Burst box", f0, f1, m, dim=(12, 45, 12, 45)[i]))
    d = 15; fl = []
    rnd = random.Random(3)
    for i, k in enumerate(["cov_III", "cov_VC", "cov_SA", "cov_IV", "cov_V", "cov_VI", "cov_LCS", "cov_VCS", "cov_EFLC", "cov_TBOGT", "cov_CW"]):
        z = 0.35 + rnd.random() * 0.9; x = 960 + (rnd.random() - .5) * 1700; y = 540 + (rnd.random() - .5) * 900
        a = R[k]; h = 420 * z; w = a["w"] * h / a["h"]
        im = D.image(f"Floating {k[4:]}", k, 0, d, tr=T(x, y, 100, ax=w / 2, ay=h / 2, r=(rnd.random() - .5) * 14), fit="stretch", rect=(0, 0, w, h), effects=GRADE() + ([D.gauss(6 * (1.2 - z))] if z < .6 else []), shadow=SHADOW)
        settle(im, im["transform"]["rotation"], 8)
        k2 = 1 + 1.6 * z
        D.kf(im, "scaleX", [(0, 100, HOLD), (d, 100 * k2, E_IOX)]); D.kf(im, "scaleY", [(0, 100, HOLD), (d, 100 * k2, E_IOX)])
        D.kf(im, "positionX", [(0, x, HOLD), (d, 960 + (x - 960) * k2, E_IOX)]); D.kf(im, "positionY", [(0, y, HOLD), (d, 540 + (y - 540) * k2, E_IOX)])
        fl.append((z, im))
    fl.sort(key=lambda p: -p[0])
    sh.append(shot("S13.10 Floating collage", 838, 853, [p[1] for p in fl], dim=0))
    lw = words_line("That rush job?", [91, 92, 93], ["That", "rush", "job?"], "IS", IS, None, 110, 0, 120, "left", WARM, -10, 780, s0, "blur", baseline=560)[0]
    for l in lw:
        dur = l["activeRange"]["duration"] * FPS // 1000; blur_out(l, dur)
    tx += lw
    xs, ws, _ = tf.line_layout("AR", ["IT'S", "BEEN", "THE"], 30, LAB, 500, 960, "center")
    for wi, t, x in zip([94, 95, 96], ["IT'S", "BEEN", "THE"], xs): tx.append(label(t, WF[wi] - s0, 816 - s0, t, x, 200, 30, "left"))
    tx += caption("for every GTA cover since.", [98, 99, 100, 101, 102], ["for", "every", "GTA", "cover", "since."], 990, s1, s0)
    return sh, tx


def S14():
    s0, s1 = SCENES[13]; sh = []; tx = []
    def cut(k, d, cx, name, h=780):
        a = R[k]; w = a["w"] * h / a["h"]
        return iclip(name, k, d, fit="stretch", rect=(0, 0, w, h), cx=cx, cy=540, shadow=SHADOW)
    rows = [(853, 882, "cov_VC", 1240, L_duo("vice"), "C08 Vice City box"), (882, 911, "cov_SA", 960, L_half(), "C09 San Andreas box"),
            (911, 920, "cov_IV", 960, L_heat(), "C10 GTA IV box"), (920, 936, "cov_V", 960, None, "C11 GTA V box")]
    for i, (f0, f1, k, cx, lk, nm) in enumerate(rows):
        d = f1 - f0
        table = D.group("A03 table (footage look)", 0, d, [iclip("A03 table", "A03", d)], effects=lk) if lk else None
        if i == 3:
            inv, setinv = L_inv(None); table = D.group("A03 table (invert flash)", 0, d, [iclip("A03 table", "A03", d)], effects=inv); setinv(table)
        behind = []
        if i == 1: behind = [HV_big("SAN ANDREAS", WF[105] - f0, d, "SAN ANDREAS", 260, 960 - tf.advance("AR", "SAN ANDREAS", 260, HEAVY) / 2, 660)]
        if i == 2:
            sz = is_size("IV", 800); w = tf.advance("AR", "IV", sz, CAP); l = IS_big("IV", WF[107] - f0, d, "IV", 800, 960, 900); behind = [l]
            pop_in(l, w, tf.cap_height("AR", sz)); l["transform"]["position"][0] -= w / 2; l["transform"]["anchorPoint"][0] -= w / 2
        if i == 3: behind = [IS_big("V", 0, d, "V", 900, 960, 940)]
        sh.append(shot(f"S14.{i + 1} {nm[4:]}", f0, f1, [cut(k, d, cx, nm + " (cutout, B07 cover)", 780 if i == 0 else 560)] + behind + [table], dim=12))
    tx.append(HV_big("VICE / CITY", 0, 882 - s0, "VICE\nCITY", 260, 116, 440))
    return sh, tx


def S15():
    s0, s1 = SCENES[14]; sh = []; tx = []
    sh.append(shot("S15.1 GTA VI box in hands", 936, 944, [vclip("B52 GTA VI box", "B52", 13.0, 8, scale=110)], dim=12))
    sh.append(shot("S15.2 Second angle", 944, 953, [vclip("B52 GTA VI box, second angle (stand-in for #53)", "B52", 20.0, 9, scale=110)], dim=12))
    d = 16; bed = [D.rect("Bed darken", 0, d, 0, 0, W, H, [0, 0, 0, 1], o=45), iclip("GTA VI cover (blurred bed)", "cov_VI", d, fit="cover", effects=[D.gauss(60)], drift_on=False, grade=False)]
    sh.append(shot("S15.3 GTA VI cover + VI flash", 953, 969, [flash_still("GTA VI cover (B07 frame, stand-in for #41)", "cov_VI", "cov_VI_vi_mask", d, 1080, 960, 540, flash_at=WF[111] - 953 + 1)] + bed))
    tx += caption("Even GTA", [109, 110], ["Even", "GTA"], 660, 953, s0, size=50)
    return sh, tx


def carousel(name, f0, f1, steps, first):
    """Covers side by side on one strip that whips one cover to the left per step (ease-in-out expo, motion-blurred,
    with a directional smear at mid-move); each step ends settled on the next cover."""
    d = f1 - f0; a = R["cov_III"]; s = H / a["h"]; cw = a["w"] * s; pitch = cw + 160
    n = len(steps) + 1; order = [first if j % 2 == 0 else ("cov_VI" if first == "cov_III" else "cov_III") for j in range(n)]
    covs = [D.image(f"{k[4:]} cover", k, 0, d, tr=T(960 + j * pitch, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch",
                    rect=(0, 0, a["w"], a["h"])) for j, k in enumerate(order)]
    strip = D.group("Cover strip", 0, d, covs)
    smear = D.dirblur(0, 90); strip["effects"] = [smear]
    pk, bk, t = [(0, 0, HOLD)], [(0, 0, HOLD)], 0
    for j, st in enumerate(steps):
        hold = 1 if st > 3 else 0; m = st - hold
        if hold:   # a step without a held frame starts on the previous step's end key (same time) - don't overwrite its easing
            pk.append((t + hold, -j * pitch, HOLD)); bk.append((t + hold, 0, HOLD))
        pk.append((t + st, -(j + 1) * pitch, E_IOX))
        bk += [(t + hold + m / 2, 90, E_IOX), (t + st, 0, E_IOX)]
        RADIAL.append(f0 + t + hold + m / 2)
        t += st
    D.kf(strip, "positionX", pk); D.kf_fx(strip, smear, "blurLength", bk)
    return shot(name, f0, f1, [strip], dim=10)


RADIAL = []   # frames (absolute) where a fast switch peaks: the edge (radial) blur pulses there


def S16():
    s0, s1 = SCENES[15]; sh = []; tx = []
    d = 29
    L = vclip("B36 GTA III box", "B36", 106.5, d, scale=98, cx=939, cy=435)
    Rr = vclip("B52 GTA VI box", "B52", 13.4, d, scale=105, cx=1442, cy=540)
    sh.append(shot("S16.1 Split: III | VI boxes", 969, 998, panel("Left", d, 0, 0, 960, H, [L]) + panel("Right", d, 960, 0, 960, H, [Rr]), dim=12))
    def flick(name, f0, f1, step):
        d = f1 - f0; lay = []
        a = R["cov_III"]; s = H / a["h"]
        for j, f in enumerate(range(0, d, step)):
            k = "cov_III" if (j % 2 == 0) == ((d - 1 - f) // step % 2 == 0) else "cov_VI"
            k = "cov_III" if ((d - f - 1) // step) % 2 == 0 else "cov_VI"
            lay.append(D.image(f"{k[4:]} cover", k, f, min(d, f + step), tr=T(960, 540, 100 * s, ax=a["w"] / 2, ay=a["h"] / 2), fit="stretch", rect=(0, 0, a["w"], a["h"]), effects=GRADE()))
        return shot(name, f0, f1, lay, dim=10)
    sh.append(carousel("S16.2 Whip carousel III / VI", 998, 1019, [5, 5, 4, 4], "cov_III"))
    d = 20; a = R["cov_III"]; h = 900; w = a["w"] * h / a["h"]
    sh.append(shot("S16.3 Split: covers flat", 1019, 1039, panel("Left", d, 0, 0, 960, H, [iclip("GTA III cover", "cov_III", d, fit="stretch", rect=(0, 0, w, h), cx=480)]) +
                   panel("Right", d, 960, 0, 960, H, [iclip("GTA VI cover", "cov_VI", d, fit="stretch", rect=(0, 0, w, h), cx=1440)]), dim=10))
    sh.append(carousel("S16.4 Whip carousel, faster", 1039, END, [4, 3, 3, 3, 3], "cov_VI"))
    tx += caption("Same boxes.", [112, 113], ["Same", "boxes."], 990, 998, s0)
    tx += words_line("Same grid.", [114, 115], ["Same", "grid."], "IS", IS, None, 220, 0, 960, "center", WARM, -10, 1019, s0, "hard", baseline=640)[0]
    for t, x, f in [("2001", 480, WF[116]), ("2026", 1440, WF[116] + 5)]:
        l = IS_big(t, f - s0, s1 - s0, t, 240, x, 1000); track_in(l); tx.append(l)
    return sh, tx


# ============================================================== film-wide layers
def grain_layer(name, o, seed):
    lay = D.image(name, "tex_grain_a", 0, END, tr=T(0, 0), fit="stretch", rect=(0, 0, 2400, 1400), blend="overlay", o=o)
    rnd = random.Random(seed)
    keys = [(f, -round(rnd.random() * 480), HOLD) for f in range(0, END, 2)]
    D.kf(lay, "positionX", keys)
    rnd = random.Random(seed + 1)
    D.kf(lay, "positionY", [(f, -round(rnd.random() * 320), HOLD) for f in range(0, END, 2)])
    return lay


def overlays():
    vig = D.rect("6 Vignette", 0, END, 0, 0, W, H, [0, 0, 0, 1], effects=[D.shader("vignette", "vignette.wgsl", [("a42", 0, 0, 1, "Alpha at 42%"), ("a66", .26, 0, 1, "Alpha at 66%"),
                 ("a86", .6, 0, 1, "Alpha at 86%"), ("a100", .84, 0, 1, "Alpha at the edge")], "radial-gradient(ellipse 72% 72%): clear to 42%, black 26% at 66%, 60% at 86%, 84% at the edge")])
    scan = D.rect("7 CRT scan lines", 0, END, 0, 0, W, H, [0, 0, 0, 1], blend="multiply", o=42,
                  effects=[D.shader("scanlines", "scanlines.wgsl", [("dark", 2, 0, 10, "Dark px per period"), ("period", 5, 1, 20, "Period px"), ("height", H, 1, 8000, "Layer height"),
                           ("lineAlpha", .7, 0, 1, "Line opacity")], "2 px of black at 70%, then 3 px clear, repeating")])
    return D.group("Film-wide overlays", 0, END, [
        scan, vig,
        D.rect("5 Desaturate", 0, END, 0, 0, W, H, hexc("#808080"), blend="saturation", o=20),
        D.rect("4 Lift", 0, END, 0, 0, W, H, hexc("#2a2119"), blend="screen", o=30),
        D.group("3 Film grain", 0, END, [grain_layer("grain.png 2400x1400", 100, 11)], blend="overlay", o=22),
        D.image("2 Halftone", "tex_halftone", 0, END, fit="stretch", blend="overlay", o=20),
        D.image("1 Grunge", "tex_grunge", 0, END, fit="cover", blend="overlay", o=60)])


def flashes():
    out = []
    for f in FLASH_AT:
        r = D.rect(f"Flash cut @{f}", f, f + 10, 0, 0, W, H, FLASH, o=95)
        D.kf(r, "opacity", [(0, 95, HOLD), (9, 0, E_IOC)])
        out.append(r)
    return out


# ============================================================== main
def faces():
    """Face centre and width in each Bliss still, read off a pixel grid (used only to line the cards up)."""
    FACE.update({"bliss26": (570, 362, 300), "bliss27": (880, 400, 520), "bliss27b": (820, 200, 220), "bliss28": (412, 410, 260)})


def main():
    build_assets(); faces()
    scene_groups, text_groups = [], []
    for i, fn in enumerate([S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16]):
        s0, s1 = SCENES[i]
        shots, texts = fn()
        for s in shots:  # shot groups were written in absolute frames; make them scene-local
            pr = s["playback"]; st = pr["inputRange"]["start"]
            if st >= ms(s0) and fn not in ():
                pass
        scene_groups.append(D.group(f"S{i + 1:02d} {SCENE_NAMES[i]}", s0, s1, [relocal(s, s0) for s in reversed(shots)]))
        text_groups.append(D.group(f"S{i + 1:02d} text", s0, s1, texts))
    lg = R["logo"]; lw = lg["w"] * 60 / lg["h"]
    root = [D.group("Logo (RawCanvas mark)", 0, END, [D.image("logo.png", "logo", 0, END, tr=T(56, 48, o=90), fit="stretch", rect=(0, 0, lw, 60))],
                    desc="logo.png at x 56, y 48, 60 px tall, opacity 0.9; never animates, nothing above it")]
    root.append(overlays())
    root += flashes()
    root += list(reversed(text_groups))
    # edge blur on fast switches: a radial (zoom) blur adjustment over the picture, clear centre, peaking on the switch
    for f in sorted(set([104, 752] + [round(x) for x in RADIAL])):
        e = D.fx({"type": "radialBlur", "amount": 0, "centerX": 0.5, "centerY": 0.5})
        adj = D.adjust(f"Edge blur @{f}", f - 3, f + 4, [e])
        D.kf_fx(adj, e, "amount", [(0, 0, HOLD), (3, 22, E_IOX), (7, 0, E_IOX)])
        root.append(adj)
    root.append(D.group("Clip grain (60% overlay)", 0, END, [grain_layer("grain.png", 100, 21)], blend="overlay", o=60))
    root += list(reversed(scene_groups))
    root.append(D.rect("Black", 0, END, 0, 0, W, H, [0, 0, 0, 1]))
    doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "colorManagement": {"workingSpace": "legacyDisplay"},
           "composition": {"id": "main", "layers": root, "name": "GTA 9/11 Cover Reel",
                           "motionBlur": {"enabled": True, "samplesPerFrame": 6, "adaptiveSampleLimit": 24, "shutterAngle": 180, "shutterPhase": -90}}, "dimensions": {"width": W, "height": H}, "duration": END / FPS, "formatVersion": 1}
    return doc


SCENE_NAMES = ["What if I told you 9-11 is the reason", "GTA covers look like this", "This was meant to be the GTA III cover", "Six months of painting",
               "Guns, fire and burning buildings", "Then 9-11 hit", "Rockstar pulled it in the US", "The new cover couldn't show",
               "Artist Stephen Bliss had about a week", "So he chopped up his own painting", "Faces, cars and the helicopter", "Boxed them into a grid",
               "That rush job", "Vice City, San Andreas, Four, Five", "Even GTA Six", "Same boxes, same grid, 25 years later"]


def relocal(g, s0):
    """Shot groups are authored with absolute frames; shift them into their scene group's clock."""
    if g.get("type") == "Group":
        pb = g["playback"]; st = pb["inputRange"]["start"]
        if st >= ms(s0):
            off = ms(s0)
            pb["inputRange"]["start"] -= off; pb["mapping"]["input"]["start"] -= off
    return g
