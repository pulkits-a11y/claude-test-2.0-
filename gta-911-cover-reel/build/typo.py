"""v7 typography: the client's scene-by-scene caption spec (00:07.0 - end).

Every caption word is a group pivoting on its centre that holds its text and, where a move needs one, a matte. Its
glow is the same word built again in each of the four glow tiers (v3.GLOW_TIERS), so the glow follows every move.

Entrances (the client's letter codes):
  A rise - fades up from 18 px below          B bloom - fades in from 108% while its glow blooms in from 170%
  C slide out from behind a cover (matted)    D push - fades up from 28 px below, earlier lines step up
  F hard cut - no animation                   G settle - fades in from 118% down to 100%
  H wipe - revealed left to right (or along a crease / a cut)
  S stretch-pop - the hook's stretched drop-in (scaleY 520% -> 100%)
Exits: cut, fade-up (fade with a 10 px upward drift), fade, wipe off, slide back behind the cover, static noise,
glitch slice, dim to grey then fade, close into its cell, push off, split apart.
Positions were read off the shots (canvas pixels); frames are absolute (30 fps).
"""
import math
from lib import *
import textfit as tf
import v3

SIZE, HERO, SMALL = 47, 112, 34           # base caption, hero (used 3 times: "six", "VI,", "25"), small label
AX = {"wdth": 100, "wght": 600}
GREY = [0.56, 0.55, 0.53, 1]
DARK = {"enabled": True, "color": [0, 0, 0, 0.75], "offset": [0, 0], "blurRadius": 22, "spreadRadius": 0, "blendMode": "normal"}
HALO = {"enabled": True, "color": [0, 0, 0, 0.95], "offset": [0, 0], "blurRadius": 14, "spreadRadius": 6, "blendMode": "normal"}   # reads over any cover


def adv(t, size=SIZE): return tf.advance("AR", t, size, AX)
def caph(size=SIZE): return tf.cap_height("AR", size)
def word(i): return v3.word_text(i)
def wf(i): return v3.WF[i]


class Track:
    """Keys of one property built as consecutive segments: to(t0, t1, value) eases from the current value."""
    def __init__(self, v): self.v = v; self.keys = [(0, v, HOLD)]

    def to(self, t0, t1, v, e=E_OX):
        last = self.keys[-1][0]
        if t0 < last: t0, t1 = last, max(t1, last + 2)      # a short word: its exit starts once its entrance is done
        if t0 > last: self.keys.append((t0, self.v, HOLD))
        self.keys.append((t1, v, e)); self.v = v

    def emit(self, layer, *props):
        if len(self.keys) > 1:
            for p in props: v3.D.kf(layer, p, self.keys)


def unit(txt, f0, f1, x, mid, size=SIZE, inn="A", out=None, n_out=6, n_in=None, rot=0, moves=(), matte=None, slide=0,
         wipe_dir="lr", shadow=None, color=None, glow=False, dim_at=None, tag="Caption"):
    """One caption word. x: left edge of the text, mid: its cap-height centre (before rotation). Times are local to
    the parent (absolute for the sharp words, the glow group's clock for glow copies)."""
    D = v3.D; d = f1 - f0; w = adv(txt, size); ch = caph(size); cx, cy = x + w / 2, mid
    col = color or v3.CAP_FILL; base = mid + ch / 2
    t = D.text(txt, 0, d, txt, v3.rl.AR, size, col, x, base, axes=AX, shadow=False)
    if shadow and not glow: t["dropShadow"] = shadow
    texts = [t]
    if "grey" in inn:                                  # starts grey, settles to white
        g = D.text(txt + " (grey)", 0, d, txt, v3.rl.AR, size, GREY if not glow else [c * .4 for c in col[:3]] + [1], x, base, axes=AX, shadow=False)
        D.kf(t, "opacity", [(0, 0, HOLD), (10, 100, E_OX)]); texts = [t, g]
    if slide:                                          # C: slides out from behind the cover (and back)
        for tx in texts:
            k = [(0, x + slide, HOLD), (7, x, E_OX)]
            if out == "slide": k += [(d - n_out, x, HOLD), (d, x + slide, E_IOX)]
            D.kf(tx, "positionX", k)
    lay = texts
    if matte is not None or "H" in inn or out == "wipe":
        if matte is not None: mx, my, mw, mh = matte
        else: mx, my, mw, mh = x - 14, mid - ch / 2 - 0.42 * size, w + 28, ch + 0.84 * size
        ax_, ay_ = {"lr": (mx, my), "rl": (mx + mw, my), "tb": (mx, my), "bt": (mx, my + mh)}[wipe_dir]
        m = D.rect(f"{tag}: {txt} (matte)", 0, d, mx, my, mw, mh, [1, 1, 1, 1], tr=T(ax_, ay_, ax=ax_, ay=ay_))
        if matte is None:
            wk = Track(0 if "H" in inn else 100)
            if "H" in inn: wk.to(0, n_in or 6, 100)
            if out == "wipe": wk.to(d - n_out, d, 0, E_IOX)
            wk.emit(m, "scaleY" if wipe_dir in ("tb", "bt") else "scaleX")
        inner = D.group(f"{tag}: {txt} (text)", 0, d, texts, matte={"layer": m["id"], "mode": "alpha"})
        lay = [inner, m]
    G = D.group(f"Glow copy: {txt}" if glow else f"{tag}: {txt}", f0, f1, lay, tr=T(cx, cy, r=rot, ax=cx, ay=cy))
    if glow:
        G["motionBlur"] = False
        for l in texts: l["motionBlur"] = False
    op, px, py, sc = Track(100), Track(cx), Track(cy), Track(100)
    kind = inn.replace("grey", "").replace("+", "")
    if kind == "fade": op = Track(0); op.to(0, 3, 100); py = Track(cy + 10); py.to(0, 4, cy)
    elif kind == "A":
        n = n_in or 6; op = Track(0); op.to(0, max(3, round(n * .7)), 100); py = Track(cy + 18); py.to(0, n, cy)
    elif kind == "B": op = Track(0); op.to(0, 3, 100); sc = Track(170 if glow else 108); sc.to(0, 10 if glow else 8, 100)
    elif kind == "D": op = Track(0); op.to(0, 3, 100); py = Track(cy + 28); py.to(0, 5, cy)
    elif kind == "G": op = Track(0); op.to(0, 3, 100); sc = Track(118); sc.to(0, 7, 100)
    elif kind == "S":
        D.kf(G, "scaleY", [(0, 520, HOLD), (5, 100, E_OX)]); D.kf(G, "scaleX", [(0, 85, HOLD), (5, 100, E_OX)])
    for tm, dx, dy in moves:                            # steps (e.g. earlier lines stepping up), eased over 5 frames
        if dx: px.to(tm, tm + 5, cx + dx)
        if dy: py.to(tm, tm + 5, cy + dy)
    if out == "fade_up": op.to(d - n_out, d, 0, E_IOC); py.to(d - n_out, d, py.v - 10)
    elif out == "fade": op.to(d - n_out, d, 0, E_IOC)
    elif out == "dim": op.to(dim_at, dim_at + 6, 55); op.to(d - n_out, d, 0, E_IOC)
    elif out == "close": sc.to(d - n_out, d, 0, E_IOX); op.to(d - n_out, d, 0, E_IOX)
    elif out == "push": px.to(d - n_out, d, px.v - 1100, E_IOX)
    elif out == "noise":
        e = D.shader("textNoise", "textnoise.wgsl", [("animationTime", 0, 0, 3600, "Engine clock (s)."), ("amount", 0, 0, 1, "Noise strength."),
                     ("height", H, 1, 8000, "Layer height px."), ("seed", 0, 0, 10000, "Pattern seed, a new one every frame.")],
                     "Static noise through the text (its last 2 frames).")
        G["effects"] = [e]; D.kf_fx(G, e, "amount", [(0, 0, HOLD), (d - 2, 1, HOLD)])
        D.kf_fx(G, e, "seed", [(d - 2, 3, HOLD), (d - 1, 8, HOLD)])
    elif out == "glitch":
        e = D.shader("glitchSlice", "glitch.wgsl", [("animationTime", 0, 0, 3600, "Engine clock (s)."), ("amount", 0, 0, 1, "Strength."),
                     ("width", W, 1, 8000, "px"), ("height", H, 1, 8000, "px"), ("seed", 0, 0, 10000, "Pattern seed.")],
                     "The cut's glitch slicing through the text horizontally (its last 3 frames).")
        G["effects"] = [e]; D.kf_fx(G, e, "amount", [(0, 0, HOLD), (d - 3, .8, HOLD), (d - 2, 1, HOLD), (d - 1, .7, HOLD)])
        D.kf_fx(G, e, "seed", [(d - 3, 5, HOLD), (d - 2, 9, HOLD), (d - 1, 14, HOLD)])
    op.emit(G, "opacity"); px.emit(G, "positionX"); py.emit(G, "positionY"); sc.emit(G, "scaleX", "scaleY")
    return G


# =================================================================== layout helpers
def line(words, x, align="left", size=SIZE):
    """[(text, left x)] for words laid out as one line from x (left), around x (center) or up to x (right)."""
    xs, _, _ = tf.line_layout("AR", list(words), size, AX, 0, x, align)
    return list(zip(words, xs))


class Scene:
    def __init__(self, label): self.label = label; self.items = []

    def add(self, txt, f0, f1, x, mid, **kw):
        """Frames are absolute here; moves are converted to the word's own clock."""
        if "moves" in kw: kw["moves"] = [(t - f0, dx, dy) for t, dx, dy in kw["moves"]]
        self.items.append(dict(txt=txt, f0=f0, f1=f1, x=x, mid=mid, **kw)); return self

    def build(self):
        sharp = [unit(**it) for it in self.items]
        f0 = min(i["f0"] for i in self.items); f1 = max(i["f1"] for i in self.items); glow = []
        for blur, o, col in v3.GLOW_TIERS:
            units = [unit(**{**it, "f0": it["f0"] - f0, "f1": it["f1"] - f0, "color": col, "glow": True}) for it in self.items]
            g = v3.D.group(f"Glow {blur} px at {o}%: {self.label}", f0, f1, units, blend="add", o=o,
                           effects=[v3.D.fx({"type": "gaussianBlur", "blurriness": blur, "repeatEdgePixels": False})])
            g["motionBlur"] = False; glow.append(g)
        return sharp, glow


# =================================================================== the scenes
def scenes(END):
    S = []

    # 00:07.0 "of painting." - low, under the Camp Funk painting like its label; H in, fade-up out
    s = Scene("of painting."); x = 545
    for t, xx in line([word(26), word(27)], x): s.add(t, wf(26 if t == "of" else 27), 229, xx, 975, inn="H", out="fade_up")
    S.append(s)

    # 00:07.6-00:10.4 "It had guns, fire, and burning buildings all over it." - everything leaves on the cut to the TV
    s = Scene("It had guns, fire, and burning buildings all over it.")
    for (t, xx), i in zip(line([word(28), word(29)], 200), (28, 29)): s.add(t, wf(i), 320, xx, 200, inn="A")     # the anchor, top left
    s.add(word(30), 236, 247, 1035, 940, inn="A")                     # by the rifle's barrel (key art)
    s.add(word(30), 247, 320, 1290, 880, inn="A")                     # by Claude's barrel (gameplay)
    s.add(word(31), 260, 320, 1040 - adv(word(31)) / 2, 600, inn="F", shadow=DARK)   # on the explosion core, hard cut on the blast frame
    for (t, xx), i in zip(line([word(32), word(33), word(34)], 1100, "center"), (32, 33, 34)):
        s.add(t, wf(i), 320, xx, 210, inn="H")                        # high, against the burning skyline
    for (t, xx), i in zip(line([word(35), word(36), word(37)], 960, "center"), (35, 36, 37)):
        s.add(t, wf(i), 320, xx, 985, inn="G")                        # under the cover (the bottom of the frame - the cover fills it)
    S.append(s)

    # 00:12.0-00:13.2 "six weeks before launch." - centred, stacked; "six" hero, the rest pushes in under it
    s = Scene("six weeks before launch.")
    words_ = [(42, HERO), (43, SIZE), (44, SIZE), (45, SIZE)]
    rel = [0, 80, 142, 204]                                           # line mids relative to "six"
    tops = -caph(HERO) / 2
    cen = [(tops + (rel[k] + caph(sz) / 2)) / 2 for k, (_, sz) in enumerate(words_)]   # block centre after line k lands
    for k, (i, sz) in enumerate(words_):
        mid = 540 - cen[k] + rel[k]
        mv = [(wf(words_[j][0]), 0, cen[k] - cen[j]) for j in range(k + 1, len(words_))]
        s.add(word(i), wf(i), 400, 960 - adv(word(i), sz) / 2, mid, size=sz, inn="B" if k == 0 else "D", out="fade", n_out=8, moves=mv,
              tag="Caption (statement)")
    S.append(s)

    # 00:13.33-00:14.9 "Rockstar pulled it in the US."
    s = Scene("Rockstar pulled it in the US.")
    s.add(word(46), 403, 413, 955 - adv(word(46)) / 2, 700, inn="B", out="wipe", n_out=4)            # under the R* logo
    for (t, xx), i in zip(line([word(47), word(48)], 1345, "center"), (47, 48)):
        s.add(t, wf(i), 430, xx, 540, inn="H", wipe_dir="tb", out="wipe", n_out=4)                   # on the crease, wiped along it
    ch = caph()
    for (t, xx), i in zip(line([word(49), word(50), word(51)], 840), (49, 50, 51)):
        s.add(t, wf(i), 445, xx, 990 - ch / 2, inn="G", out="wipe", n_out=4)                        # right of the cover, on its bottom edge
    S.append(s)

    # 00:15.0 "The new cover" - hung on the gallery wall between two frames
    s = Scene("The new cover")
    for (t, xx), i in zip(line([word(52), word(53)], 1372, "center"), (52, 53)): s.add(t, wf(i), 462, xx, 505, inn="A")
    s.add(word(54), wf(54), 462, 1372 - adv(word(54)) / 2, 560, inn="A")
    S.append(s)

    # 00:15.33-00:15.9 "couldn't show" - either side of the cover at its top, sliding out from behind it and back
    s = Scene("couldn't show"); wl, wr = adv(word(55)), adv(word(56))
    s.add(word(55), wf(55), 476, 484 - wl, 110, inn="C", slide=wl + 60, matte=(0, 0, 518, 300), out="slide", n_out=5)
    s.add(word(56), wf(56), 476, 1435, 110, inn="C", slide=-(wr + 60), matte=(1401, 0, 519, 300), out="slide", n_out=5)
    S.append(s)

    # 00:16.0-00:17.4 the list - each line pushes in, earlier lines step up; grey settling to white; static noise out
    s = Scene("guns, buildings, or fire."); P = 66
    s.add(word(57), wf(57), 524, 760, 606, inn="D+grey", out="noise", moves=[(wf(58), 0, -P), (wf(59), 0, -2 * P)])
    s.add(word(58), wf(58), 524, 760, 606, inn="D+grey", out="noise", moves=[(wf(59), 0, -P)])
    for (t, xx), i in zip(line([word(59), word(60)], 760), (59, 60)): s.add(t, wf(i), 524, xx, 606, inn="D+grey", out="noise")
    S.append(s)

    # 00:17.67-00:18.4 "Artist Stephen Bliss" - pinned to his eye line through every cut
    s = Scene("Artist Stephen Bliss"); EYE = 432
    s.add(word(61), wf(61), 558, 640 - adv(word(61)), EYE, inn="G")
    for (t, xx), i in zip(line([word(62), word(63)], 1280), (62, 63)): s.add(t, wf(i), 558, xx, EYE, inn="S")
    S.append(s)

    # 00:18.67-00:19.5 "had about a week," - one line left of his head, word by word; the glitch slices it out
    s = Scene("had about a week,")
    for (t, xx), i in zip(line([word(k) for k in (64, 65, 66, 67)], 680, "right"), (64, 65, 66, 67)):
        s.add(t, wf(i), 583, xx, EYE, inn="A", out="glitch")
    S.append(s)

    # 00:19.67-00:21.0 "so he chopped up his own painting." - one line at the knife blade's angle (held still)
    s = Scene("so he chopped up his own painting."); ang = -45; ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ids = [68, 69, 70, 71, 72, 73, 74]; ws = [word(i) for i in ids]; sp = adv(" ")
    total = sum(adv(t) for t in ws) + sp * (len(ws) - 1); along = -total / 2; LX, LY = 960, 540
    for i, t in zip(ids, ws):
        c = along + adv(t) / 2; ccx, ccy = LX + c * ux, LY + c * uy; along += adv(t) + sp
        side = -1 if i <= 70 else 1                                  # the line splits at the cut point: "chopped" | "up"
        inn = "A" if i < 70 else ("F" if i == 70 else "H")
        s.add(t, wf(i), 634, ccx - adv(t) / 2, ccy, rot=ang, inn=inn, out="fade", n_out=6,
              moves=[(627, side * 8 * ux, side * 8 * uy)], tag="Caption (blade angle)")
    S.append(s)

    # 00:21.33-00:23.3 "He only kept" - locked top-left third, rises in once; dims on the road shot, then fades
    s = Scene("He only kept")
    for (t, xx), i in zip(line([word(75), word(76), word(77)], 240), (75, 76, 77)):
        s.add(t, 640, 699, xx, 300, inn="A", out="dim", dim_at=685 - 640, n_out=6)
    S.append(s)

    # 00:23.67-00:25.0 "and boxed them into a grid." - one word per cell of the gameplay grid, popping with the cells,
    # closing into the cover with them
    s = Scene("and boxed them into a grid."); G, _, _ = v3.rl.grid_rects()
    for cell, ids_, t0 in [("L1", (85,), 724), ("M1", (86,), 725), ("L3", (87, 88), 730), ("R4", (89, 90), 736)]:
        x, y, w, h = G[cell]
        for t, xx in line([word(i) for i in ids_], x + w / 2, "center"): s.add(t, t0, 744, xx, y + h / 2, inn="F", out="close", n_out=4)
    S.append(s)

    # 00:25.33-00:25.9 "That rush job?" - either side of the photo, on his eye line; "job?" blooms and holds 4 frames more
    s = Scene("That rush job?"); EYE2 = 520
    for (t, xx), i in zip(line([word(91), word(92)], 586, "right"), (91, 92)): s.add(t, wf(i), 782, xx, EYE2, inn="A")
    s.add(word(93), wf(93), 786, 1334, EYE2, inn="B")
    S.append(s)

    # 00:26.0-00:27.9 "It's been the template for every GTA cover"
    s = Scene("It's been the template for every GTA cover")
    for (t, xx), i in zip(line([word(k) for k in (94, 95, 96)], 966, "center", SMALL), (94, 95, 96)):
        s.add(t, wf(i), 796, xx, 765, size=SMALL, inn="A")                                        # small, under the GTA III logo
    for ids_, mid in [((97,), 470), ((98, 99), 530), ((100, 101), 590)]:                       # in the gap left of the box
        for (t, xx), i in zip(line([word(k) for k in ids_], 480, "center"), ids_):
            s.add(t, wf(i), 838, xx, mid, inn="C", slide=660 - xx, matte=(0, 300, 648, 380), out="push", n_out=4)
    S.append(s)

    # 00:28.33-00:31.0 the titles as labels under each cover, wiped on and off
    for ids_, f0, f1 in [((103, 104), 853, 882), ((105, 106), 883, 911), ((107,), 912, 920), ((108,), 920, 936)]:
        s = Scene(" ".join(word(i) for i in ids_))
        for t, xx in line([word(i) for i in ids_], 960, "center"): s.add(t, f0, f1, xx, 925, inn="H", out="wipe", n_out=4)
        S.append(s)

    # 00:31.33-00:32.0 "even GTA VI," - centred at the bottom of the VI cover, "VI," at hero size, stretch-pop
    s = Scene("even GTA VI,"); bl = 1000; sp = adv(" ")
    wl = adv(word(109)) + sp + adv(word(110)) + sp; total = wl + adv(word(111), HERO); x0 = 960 - total / 2
    s.add(word(109), wf(109), 969, x0, bl - caph() / 2, inn="A")
    s.add(word(110), wf(110), 969, x0 + adv(word(109)) + sp, bl - caph() / 2, inn="A")
    s.add(word(111), wf(111), 969, x0 + wl, bl - caph(HERO) / 2, size=HERO, inn="S")
    S.append(s)

    # 00:32.33-00:33.9 "same boxes," / "same grid," - the same spot between the cases, the same settle
    for ids_, f1 in [((112, 113), 998), ((114, 115), 1021)]:
        s = Scene(" ".join(word(i) for i in ids_))
        for i, mid in zip(ids_, (300, 362)): s.add(word(i), wf(i), f1, 905 - adv(word(i)) / 2, mid, inn="G", out="fade_up", shadow=HALO)
        S.append(s)

    # 00:34.0-end "25 years later." - centred between the covers; "25" hero blooms, "years later." rises slowly;
    # held still, then the only slow exit: a 20-frame fade before the covers fade
    s = Scene("25 years later.")
    s.add(word(116), wf(116), 1105, 960 - adv(word(116), HERO) / 2, 495, size=HERO, inn="B", out="fade", n_out=20, tag="Caption (end title)")
    for t, xx in line([word(117), word(118)], 960, "center"):
        s.add(t, wf(117), 1105, xx, 590, inn="A", n_in=14, out="fade", n_out=20, tag="Caption (end title)")
    S.append(s)

    sharp, glow = [], []
    for sc in S:
        a, b = sc.build(); sharp += a; glow += b
    return sharp, glow
