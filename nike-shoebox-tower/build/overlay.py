"""2D layer: typography, the three compulsory effects, grade, transitions and layer structure.

Root stack (top first):
  100 Adj  Glitch warp ("Today?" displacement-map warp over the whole frame)
  200 Grp  TYPE (everything typographic; hidden for the clean version)
  400 Grp  Opening card (charcoal) -> grunge displacement dissolve into the street
  300 Adj  Film grain
  310 Adj  Grade (teal shadows / warm highlights, crushed blacks, vignette, "Today?" desaturation)
  500 Grp  Stockroom (Scene3D 20) revealed by a grunge displacement wipe
  600 Grp  Street (Scene3D 13 ghost, 12 reflection, 14 haze, 11 street, 10 backdrop)
  9xx      Grunge 353 map layers (consumed as shader texture inputs, never painted)
"""
import json
import math
import os

from PIL import ImageFont

from common import *
from lib import COMP, hex_srgb
from shaders import grunge, ripples, turbulent

MINT = hex_srgb("#CCF0BB")
WHITE = hex_srgb("#ECECEC")
CHARCOAL = hex_srgb("#121212")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
F_ARCHIVO = os.path.join(FONT_DIR, "Archivo-SemiCondensed-Black_wdth80_wght900.ttf")
F_SERIF = os.path.join(FONT_DIR, "InstrumentSerif-Regular.ttf")
F_SERIF_I = os.path.join(FONT_DIR, "InstrumentSerif-Italic.ttf")
F_INTER = os.path.join(FONT_DIR, "Inter-Medium.ttf")
IDT = {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100}


def text_w(font, size, s):
    return ImageFont.truetype(font, int(round(size))).getlength(s) * size / int(round(size))


def cap_h(font, size):
    f = ImageFont.truetype(font, 400)
    b = f.getbbox("H")
    return (b[3] - b[1]) * size / 400


def rng_(a, b):
    return {"start": ms(a), "duration": ms(b - a)}


def tf(pos=(0, 0), anchor=(0, 0), scale=(100, 100), opacity=100):
    return {"anchorPoint": list(anchor), "position": list(pos), "scale": list(scale), "rotation": 0, "opacity": opacity}


def text_layer(lid, name, parent, t0, t1, text, family, style, size, color, pos, anchor=(0, 0), just="left", tracking=0,
               leading=None, opacity=100, insert=None):
    st = {"text": text, "fontFamily": family, "fontStyle": style, "fontSize": size, "fillColor": color,
          "justification": just, "strokeWidth": 0, "tracking": tracking, "disableAutoWrap": True}
    if leading is not None:
        st["leading"] = leading
    a = {"type": "createFxTextLayer", "compositionId": COMP, "layerId": lid, "name": name, "parentLayerId": parent,
         "activeRange": rng_(0, t1), "transform": tf(pos, anchor, opacity=opacity), "sourceText": st}
    if insert is not None:
        a["insertIndex"] = insert
    return a


def group_layer(lid, name, parent, t0, t1, transform=None, insert=None):
    a = {"type": "createFxGroupLayer", "compositionId": COMP, "layerId": lid, "name": name, "activeRange": rng_(0, t1),
         "transform": transform or dict(IDT)}
    if parent is not None:
        a["parentLayerId"] = parent
    if insert is not None:
        a["insertIndex"] = insert
    return a


def fx(lid, eid, effect):
    return {"type": "addFxLayerEffect", "compositionId": COMP, "layerId": lid, "effectId": eid, "effect": effect}


def pkeys(lid, prop, keys, kind="float"):
    return {"type": "setFxPropertyKeyframes", "compositionId": COMP, "property": {"layerId": lid, "propertyType": prop},
            "keyframes": ease_kf(f"L{lid}{prop}", keys, kind)}


def param_keys(lid, eid, name, keys):
    return {"type": "setFxLayerEffectParamAnimator", "compositionId": COMP, "layerId": lid, "effectId": eid,
            "paramName": name, "dependencies": [],
            "animator": {"type": "keyframes", "enabled": True, "keyframes": ease_kf(f"E{lid}-{eid}-{name}", keys)}}


def param_js(lid, eid, name, code):
    return {"type": "setFxLayerEffectParamAnimator", "compositionId": COMP, "layerId": lid, "effectId": eid,
            "paramName": name, "dependencies": [], "animator": {"type": "jsScript", "layerTimeJsCode": code}}


def grain_fx(lid, eid, amount=0.35, size=1.1):
    return [fx(lid, eid, {"type": "grain", "amount": amount, "size": size, "softness": 0.25, "aspectRatio": 1.0, "seed": 1}),
            param_js(lid, eid, "seed", "return Math.floor(input.time.seconds * 24) % 997;")]


def map_layer(lid, name):
    return {"type": "createFxImageLayer", "compositionId": COMP, "layerId": lid, "name": name,
            "activeRange": rng_(0, DUR), "transform": dict(IDT),
            "source": {"assetId": "grunge353_dispmap", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": W, "height": H}}}


def jolt(t0, peak, settle=0.25, base=0.0, pre=None):
    """Turbulent-displace amount keys: sharp at rest, a hit at t0 that resolves in ~settle seconds."""
    k = [(max(0.0, (pre if pre is not None else t0) - 0.04), base, "linear"), (t0, peak, "linear"),
         (t0 + settle * 0.35, peak * 0.35, EASE_OUT), (t0 + settle, base, EASE_OUT)]
    return k


def build_overlay(fonts):
    A = []
    fam = {k: (v["fontFamily"], v["fontStyle"]) for k, v in fonts.items()}
    ARC = fam["Archivo-SemiCondensed-Black_wdth80_wght900.ttf"]
    SER = fam["InstrumentSerif-Regular.ttf"]
    SER_I = fam["InstrumentSerif-Italic.ttf"]
    INT = fam["Inter-Medium.ttf"]
    lay = load_json("layout.json")
    L = lay["landing_times"]

    # ---------------- structure: wrap the scenes
    for i, (lid, nm) in enumerate([(901, "Map: card dissolve"), (902, "Map: card text dissolve"), (903, "Map: street wipe"),
                                   (904, "Map: street-type wipe"), (905, "Map: glitch warp"), (906, "Map: date flip")]):
        A.append(map_layer(lid, "Grunge 353 " + nm))

    # ghost: 26% opacity with a constant low turbulent wobble; haze drifts on the slowed story clock
    A.append({"type": "setFxPropertyValue", "compositionId": COMP, "target": {"type": "layerProperty", "property": {"layerId": 13, "propertyType": "opacity"}},
              "value": {"type": "float", "value": 30}})
    A.append(fx(13, 1301, turbulent("ghostWobble", amount=2.6, size=46, evolution=1.6, seed=3)))
    A.append(fx(14, 1401, turbulent("hazeDrift", amount=9, size=240, evolution=0.35, seed=8)))
    A += [param_keys(14, 1401, "useClock.toggle", [(0, 1, "hold")])]
    clock = [(f / FPS, story_time(f / FPS)) for f in range(0, int(STREET_END * FPS) + 1)]
    A.append({"type": "setFxLayerEffectParamAnimator", "compositionId": COMP, "layerId": 14, "effectId": 1401, "paramName": "clock",
              "dependencies": [], "animator": {"type": "keyframes", "enabled": True,
                                               "keyframes": kf_track([(t, [v]) for t, v in clock], "float", "hzclock", 0.002)}})

    # puddle ripples: first landing on "Nike", then the visible debris impacts. Each ring's centre is keyed to
    # follow its ground point through the camera move.
    drops = [([0, 0, -60], T["nike"], 6.0), ([-1320, 0, -30], 8.70, 4.5), ([1170, 0, 1000], 8.90, 3.5), ([250, 0, 660], 9.20, 3.0)]
    A.append(fx(12, 1201, ripples("puddleRipples", [(0, 0, t0, s) for _, t0, s in drops], aspect=0.14, decay=0.38)))
    for i, (wp, t0, s) in enumerate(drops):
        xs, ys = [], []
        for f in range(int(t0 * FPS) - 1, int((t0 + 1.2) * FPS)):
            u, v, _ = project(wp, street_cam(f / FPS))
            xs.append((f / FPS, [u]))
            ys.append((f / FPS, [v]))
        for nm, tr in ((f"drop{i}.x", xs), (f"drop{i}.y", ys)):
            A.append({"type": "setFxLayerEffectParamAnimator", "compositionId": COMP, "layerId": 12, "effectId": 1201,
                      "paramName": nm, "dependencies": [],
                      "animator": {"type": "keyframes", "enabled": True, "keyframes": kf_track(tr, "float", f"rp{i}{nm}", 0.5)}})

    # ---------------- street -> stockroom: grunge displacement wipe
    w0, w1 = T["wipe"]
    A.append(fx(20, 2001, grunge("stockroomReveal", 903, softness=0.14, map_scale=1.5)))
    A.append(param_keys(20, 2001, "progress", [(0, 1.0, "hold"), (w0 - WALL_START, 1.0, "hold"), (w1 - WALL_START, 0.0, EASE_IN_OUT)]))
    A.append(param_keys(20, 2001, "displace", [(0, 0, "hold"), (w0 - WALL_START, 70, "linear"), (w1 - WALL_START, 0, EASE_OUT)]))

    # ---------------- grade + grain (adjustments over the 3D picture)
    A.append({"type": "createFxAdjustmentLayer", "compositionId": COMP, "layerId": 310, "name": "Grade: teal shadows, warm highlights",
              "activeRange": rng_(0, DUR), "transform": dict(IDT), "insertIndex": 0})
    A.append(fx(310, 3101, {"type": "tintTritone", "amount": 0.16, "blackR": 0.02, "blackG": 0.10, "blackB": 0.09,
                            "whiteR": 1.0, "whiteG": 0.93, "whiteB": 0.82}))
    A.append(fx(310, 3102, {"type": "hueSaturation", "colorize": False, "colorizeHue": 0, "colorizeLightness": 0,
                            "colorizeSaturation": 0, "hue": 0, "lightness": 0, "saturation": 0}))
    td, less = T["today"], T["less"]
    A.append(param_keys(310, 3102, "saturation", [(0, 0, "hold"), (T["slow"][0], 0, "hold"), (td, -20, EASE_IN_OUT),
                                                  (less, -20, "hold"), (less + 0.45, 0, EASE_IN_OUT)]))
    A.append(fx(310, 3103, {"type": "vignette", "amount": 0.42, "radius": 0.78, "feather": 0.65}))
    A.append({"type": "createFxAdjustmentLayer", "compositionId": COMP, "layerId": 300, "name": "Film grain",
              "activeRange": rng_(0, DUR), "transform": dict(IDT), "insertIndex": 0})
    A += grain_fx(300, 3001, amount=0.12, size=1.2)

    # ---------------- opening card (charcoal) and its dissolve into the street
    c0, c1 = T["card_out"]
    A.append(group_layer(400, "Opening card (charcoal)", None, 0, c1 + 0.05, insert=0))
    A.append({"type": "createFxRectLayer", "compositionId": COMP, "layerId": 401, "name": "Charcoal", "parentLayerId": 400,
              "activeRange": rng_(0, c1 + 0.05), "transform": dict(IDT), "rect": {"size": [W, H], "fillColor": CHARCOAL}})
    A.append(fx(400, 4001, grunge("cardDissolve", 901, softness=0.22, map_scale=1.7)))
    A.append(param_keys(400, 4001, "progress", [(0, 0, "hold"), (c0, 0, "hold"), (c1, 1.0, (0.55, 0.0, 0.45, 1.0))]))
    A.append(param_keys(400, 4001, "displace", [(0, 0, "hold"), (c0, 0, "hold"), (c0 + 0.12, 60, EASE_IN), (c1, 10, EASE_OUT)]))

    # ---------------- TYPE group
    A.append(group_layer(200, "TYPE (all typography)", None, 0, DUR, insert=0))

    # card words (same style as the preceding kinetic card: small white sans, large mint serif)
    A.append(group_layer(210, "Card words", 200, 0, c1 + 0.05))
    s1, s2 = 52, 210
    A.append(text_layer(211, "more than", 210, T["more_than"], c1 + 0.05, "more than", INT[0], INT[1], s1, WHITE,
                        (W / 2, 452), just="center"))
    A.append(text_layer(212, "anyone.", 210, T["anyone"], c1 + 0.05, "anyone.", SER[0], SER[1], s2, MINT,
                        (W / 2, 668 - 0), anchor=(0, -cap_h(F_SERIF, s2) / 2), just="center"))
    A.append(pkeys(211, "opacity", [(T["more_than"], 0, "linear"), (T["more_than"] + 0.16, 100, EASE_OUT)]))
    A.append(pkeys(211, "positionY", [(T["more_than"], 466, "linear"), (T["more_than"] + 0.24, 452, EASE_OUT)]))
    A.append(pkeys(212, "opacity", [(T["anyone"], 0, "linear"), (T["anyone"] + 0.08, 100, EASE_OUT)]))
    A.append(pkeys(212, "scaleX", [(T["anyone"], 93, "linear"), (T["anyone"] + 0.30, 100, SNAP)]))
    A.append(pkeys(212, "scaleY", [(T["anyone"], 93, "linear"), (T["anyone"] + 0.30, 100, SNAP)]))
    A.append(fx(212, 2121, turbulent("anyoneJolt", size=26, evolution=9, seed=2)))
    A.append(param_keys(212, 2121, "amount", jolt(T["anyone"], 14, 0.24)))
    for lid, eid in ((211, 2111), (212, 2122)):
        A += grain_fx(lid, eid, amount=0.55, size=1.0)
    A.append(fx(210, 2101, grunge("cardWordsDissolve", 902, softness=0.22, map_scale=1.7)))
    A.append(param_keys(210, 2101, "progress", [(0, 0, "hold"), (c0, 0, "hold"), (c1, 1.0, (0.55, 0.0, 0.45, 1.0))]))
    A.append(param_keys(210, 2101, "displace", [(0, 0, "hold"), (c0, 0, "hold"), (c0 + 0.12, 60, EASE_IN), (c1, 10, EASE_OUT)]))

    # street-section type lives in one group so the wipe takes it away with the street
    A.append(group_layer(205, "Street type", 200, T["y2021"] - 0.1, w1 + 0.05))
    A.append(fx(205, 2051, grunge("streetTypeWipe", 904, softness=0.14, map_scale=1.5)))
    A.append(param_keys(205, 2051, "progress", [(0, 0, "hold"), (w0 - 0.02, 0, "hold"), (w1 - 0.02, 1.0, EASE_IN_OUT)]))
    A.append(param_keys(205, 2051, "displace", [(0, 0, "hold"), (w0, 0, "hold"), (w0 + 0.1, 60, EASE_IN), (w1, 10, EASE_OUT)]))

    # ---- "2021" (callback to the 0:00 title) -> top-left date stamp; slot roll to 2026 on "Today?"
    BIG = 300
    w202 = text_w(F_ARCHIVO, BIG, "202")
    w1d = text_w(F_ARCHIVO, BIG, "1")
    w_all = text_w(F_ARCHIVO, BIG, "2021")
    capB = cap_h(F_ARCHIVO, BIG)
    x0 = -w_all / 2
    stamp_scale = 0.205
    stamp_left, stamp_base = 104, 232
    stamp_center = (stamp_left + w_all * stamp_scale / 2, stamp_base - capB * stamp_scale / 2)
    tY, (m0, m1) = T["y2021"], T["stamp_move"]
    A.append(group_layer(220, "Date stamp 2021 -> 2026", 205, tY - 0.05, w1 + 0.05,
                         transform=tf((W / 2, H / 2 - 10), (0, -capB / 2))))
    A.append(text_layer(221, "202", 220, tY - 0.05, w1 + 0.05, "202", ARC[0], ARC[1], BIG, WHITE, (x0, 0), tracking=-10))
    lead = BIG * 1.0
    A.append({"type": "createFxRectLayer", "compositionId": COMP, "layerId": 223, "name": "Reel window (matte)", "parentLayerId": 220,
              "activeRange": rng_(0, w1 + 0.05), "transform": tf((x0 + w202 - 6, -capB - 0.12 * BIG)),
              "rect": {"size": [w1d * 1.55 + 24, capB + 0.24 * BIG], "fillColor": [1, 1, 1, 1]}})
    A.append(text_layer(224, "Year reel 1..6", 220, tY - 0.05, w1 + 0.05, "1\n2\n3\n4\n5\n6", ARC[0], ARC[1], BIG, WHITE,
                        (x0 + w202 - 4, 0), leading=lead))
    A.append({"type": "setFxLayerTrackMatte", "compositionId": COMP, "layerId": 224, "matteLayerId": 223, "mode": "alpha"})
    A.append(pkeys(220, "opacity", [(tY - 0.05, 0, "linear"), (tY + 0.03, 100, "linear")]))
    A.append(pkeys(220, "scaleX", [(tY - 0.02, 138, "linear"), (tY + 0.26, 100, SNAP), (m0, 100, "hold"),
                                   (m1, stamp_scale * 100, OVERSHOOT)]))
    A.append(pkeys(220, "scaleY", [(tY - 0.02, 138, "linear"), (tY + 0.26, 100, SNAP), (m0, 100, "hold"),
                                   (m1, stamp_scale * 100, OVERSHOOT)]))
    A.append(pkeys(220, "positionX", [(m0, W / 2, "hold"), (m1, stamp_center[0], OVERSHOOT)]))
    A.append(pkeys(220, "positionY", [(m0, H / 2 - 10, "hold"), (m1, stamp_center[1], OVERSHOOT)]))
    # slot roll 1 -> 6 (reel moves up five lines), with a turbulent jolt and a grunge displacement hit
    r0, r1 = td, td + 0.42
    A.append(pkeys(224, "positionY", [(r0, 0, "hold"), (r1, -5 * lead, (0.20, 0.0, 0.10, 1.06))]))
    A.append(fx(220, 2201, turbulent("yearJolt", size=34, evolution=10, seed=5)))
    A.append(param_keys(220, 2201, "amount", jolt(tY, 26, 0.27) + [(m0, 0, "hold"), (m0 + 0.18, 5, EASE_OUT), (m1, 0, EASE_OUT),
                                                                   (r0 - 0.02, 0, "hold"), (r0 + 0.04, 30, "linear"),
                                                                   (r1, 3, EASE_OUT), (r1 + 0.15, 0, EASE_OUT)]))
    A.append(fx(220, 2202, grunge("yearFlipDisplace", 906, softness=0.05)))
    A.append(param_keys(220, 2202, "displace", [(0, 0, "hold"), (r0 - 0.01, 0, "hold"), (r0 + 0.03, 120, "linear"),
                                                (r0 + 0.17, 0, EASE_OUT)]))
    A.append(param_keys(220, 2202, "mapShift.x", [(0, 0, "hold"), (r0 + 0.04, 0.31, "hold"), (r0 + 0.08, 0.57, "hold"), (r0 + 0.12, 0.13, "hold")]))
    A += grain_fx(220, 2203, amount=0.5, size=1.0)

    # ---- the mint market-value counter: rises with the top box, $0B -> $280B, rolls down to $60B
    CS = 118
    capC = cap_h(F_ARCHIVO, CS)
    k0 = T["nike"] - 0.2
    pos = []
    for f in range(int(k0 * FPS), int(w1 * FPS) + 2):
        t = f / FPS
        n = sum(1 for x in L if x <= t)
        if t < less + 0.02:
            cam = street_cam(t)
            u, v, _ = project([170, -122 * max(n, 1), -104], cam)
            x = min(u + 64, 1500)
            y = min(max(v + capC * 0.55, 210), 820)
        else:
            u2 = smootherstep(less, 8.45, t)
            x = x_last + (1300 - x_last) * u2
            y = y_last + (452 - y_last) * u2
        if t < less + 0.02:
            x_last, y_last = x, y
        pos.append((t - k0, [x, y]))
    # smooth the follow (a camera operator's lag), then key it
    sm = []
    ax, ay = pos[0][1]
    for t, (x, y) in pos:
        ax += (x - ax) * 0.35
        ay += (y - ay) * 0.35
        sm.append((t, [ax, ay]))
    A.append(group_layer(230, "Market-value counter", 205, k0, w1 + 0.05, transform=tf(sm[0][1])))
    A.append(pkeys(230, "positionX", [(t + k0, p[0], "linear") for t, p in rdp(sm, 0.4)]))
    A.append(pkeys(230, "positionY", [(t + k0, p[1], "linear") for t, p in rdp(sm, 0.4)]))
    A.append(pkeys(230, "opacity", [(k0, 0, "linear"), (T["nike"] - 0.02, 100, EASE_OUT)]))
    A.append(text_layer(231, "market value (label)", 230, k0, w1 + 0.05, "market value", SER_I[0], SER_I[1], 46, WHITE,
                        (2, -capC - 26), opacity=88))
    lt = json.dumps([round(x, 4) for x in L])
    counter_js = (f"const L={lt};const t=input.time.seconds;let v;"
                  f"if(t<{less}){{let n=0;for(const x of L){{if(x<=t+1e-6)n++;}}v=n*10;}}"
                  f"else{{const u=Math.min(1,Math.max(0,(t-{less})/{T['lock60'] - less:.3f}));const e=1-Math.pow(1-u,2.4);v=280-Math.round(e*22)*10;}}"
                  "return '$'+v+'B';")
    A.append(text_layer(232, "Counter $0B -> $280B -> $60B", 230, k0, w1 + 0.05, "$0B", ARC[0], ARC[1], CS, MINT, (0, 0), tracking=-8))
    A.append({"type": "setFxAnimator", "compositionId": COMP,
              "target": {"type": "layerProperty", "property": {"layerId": 232, "propertyType": "textContent"}},
              "animator": {"type": "jsScript", "layerTimeJsCode": counter_js}, "dependencies": [], "layerRefBindings": []})
    A.append(fx(232, 2321, turbulent("digitJitter", size=22, evolution=12, seed=7)))
    jitter_js = (f"const L={lt};const t=input.time.seconds;let tc=-9;"
                 f"for(const x of L){{if(x<=t)tc=x;}}let a=0.0;"
                 f"if(t<{less}){{a=8*Math.exp(-(t-tc)/0.045);}}"
                 f"else{{const u=Math.min(1,Math.max(0,(t-{less})/{T['lock60'] - less:.3f}));const roll=(u<1)?1:0;"
                 f"a=roll*(16+10*Math.abs(Math.sin(t*61)))+22*Math.exp(-Math.max(0,t-{T['lock60']:.3f})/0.06)*(t>={T['lock60']:.3f}?1:0);}}"
                 "return a;")
    A.append(param_js(232, 2321, "amount", jitter_js))
    A += grain_fx(232, 2322, amount=0.55, size=1.0)
    A += grain_fx(231, 2311, amount=0.45, size=0.9)

    # ---- "-80%" slams in on "80 percent"
    m80 = T["minus80"]
    S80 = 204
    cap80 = cap_h(F_ARCHIVO, S80)
    A.append(text_layer(240, "-80%", 205, m80 - 0.04, w1 + 0.05, "−80%", ARC[0], ARC[1], S80, MINT, (1336, 760),
                        anchor=(text_w(F_ARCHIVO, S80, "−80%") / 2, -cap80 / 2), tracking=-12))
    A.append(pkeys(240, "positionX", [(m80, 1336 + text_w(F_ARCHIVO, S80, "−80%") / 2, "hold")]))
    A.append(pkeys(240, "positionY", [(m80, 760 - cap80 / 2, "hold")]))
    A.append(pkeys(240, "opacity", [(m80 - 0.04, 0, "linear"), (m80 + 0.03, 100, "linear")]))
    A.append(pkeys(240, "scaleX", [(m80 - 0.04, 168, "linear"), (m80 + 0.20, 100, SNAP)]))
    A.append(pkeys(240, "scaleY", [(m80 - 0.04, 168, "linear"), (m80 + 0.20, 100, SNAP)]))
    A.append(fx(240, 2401, turbulent("minus80Slam", size=30, evolution=11, seed=9)))
    A.append(param_keys(240, 2401, "amount", [(m80 - 0.05, 0, "hold"), (m80, 48, "linear"), (m80 + 0.10, 16, EASE_OUT),
                                              (m80 + 0.25, 0, EASE_OUT)]))
    A += grain_fx(240, 2402, amount=0.55, size=1.1)

    # ---- "S&P 100" over the stockroom wall
    sp = T["sp_label"]
    SPS = 128
    A.append(text_layer(250, "S&P 100", 200, sp - 0.05, DUR, "S&P 100", SER_I[0], SER_I[1], SPS, WHITE, (W / 2, 166), just="center"))
    A.append(pkeys(250, "opacity", [(sp - 0.05, 0, "linear"), (sp + 0.16, 100, EASE_OUT)]))
    A.append(pkeys(250, "positionY", [(sp - 0.05, 182, "linear"), (sp + 0.36, 166, EASE_OUT)]))
    A.append(fx(250, 2501, turbulent("spSettle", size=24, evolution=9, seed=11)))
    A.append(param_keys(250, 2501, "amount", jolt(sp, 12, 0.30)))
    A += grain_fx(250, 2502, amount=0.5, size=1.0)

    # ---------------- "Today?" glitch: displacement-map warp of the whole frame (3-4 frames)
    A.append({"type": "createFxAdjustmentLayer", "compositionId": COMP, "layerId": 100, "name": "Glitch warp (displacement map)",
              "activeRange": rng_(0, DUR), "transform": dict(IDT), "insertIndex": 0})
    A.append(fx(100, 1001, grunge("todayGlitch", 905, softness=0.05, map_scale=2.6)))
    g = td
    A.append(param_keys(100, 1001, "displace", [(0, 0, "hold"), (g - 0.005, 0, "hold"), (g + 0.03, 34, "hold"), (g + 0.065, 18, "hold"),
                                                (g + 0.10, 40, "hold"), (g + 0.135, 0, "hold")]))
    A.append(param_keys(100, 1001, "rgbSplit", [(0, 0, "hold"), (g + 0.03, 4, "hold"), (g + 0.065, 2, "hold"),
                                                (g + 0.10, 5, "hold"), (g + 0.135, 0, "hold")]))
    A.append(param_keys(100, 1001, "mapShift.y", [(0, 0, "hold"), (g + 0.03, 0.21, "hold"), (g + 0.065, -0.37, "hold"),
                                                  (g + 0.10, 0.52, "hold"), (g + 0.135, 0, "hold")]))
    return A
