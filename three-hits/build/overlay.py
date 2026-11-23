"""2D layers of the Three Hits MG: typography, the three compulsory effects, grade, grain.

Root stack (top first):
  100 Adj  Impact jolts: Grunge 353 displacement across the whole frame (stamp hit 3 frames, knock-off 2 frames)
  200 Grp  TYPE (all overlay typography; hide it for the clean version; the TARIFF ink is 3D and stays)
  300 Adj  Film grain
  310 Adj  Grade (teal-green shadows, warm highlights, vignette)
  16 Dust · 15 2028 beam · 14 Haze · 12 Reflection · 11 Stage · 10 Backdrop (Scene3D, see stage.py)
  9xx      Grunge 353 map layers (consumed as shader texture inputs, never painted)

Type: numbers in the heavy grotesk (Archivo SemiCondensed Black, mint #CCF0BB), labels in the italic serif
(Instrument Serif Italic, white): the same fonts, sizes and treatment as the Shoebox Tower MG. Every text layer
has animated grain inside it and lands with a Turbulent Displace jolt that settles.
"""
import os

from PIL import ImageFont

from common import *
from layout import BOX, PITCH, STATIONS, ROW, cam
from lib import COMP, hex_srgb
from shaders import grunge, turbulent
from stage import light_2028, F_IMPACT, F_HIT

MINT = hex_srgb("#CCF0BB")
WHITE = hex_srgb("#ECECEC")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
F_ARCHIVO = os.path.join(FONT_DIR, "Archivo-SemiCondensed-Black_wdth80_wght900.ttf")
F_SERIF_I = os.path.join(FONT_DIR, "InstrumentSerif-Italic.ttf")
IDT = {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100}


def text_w(font, size, s):
    return ImageFont.truetype(font, int(round(size))).getlength(s) * size / int(round(size))


def cap_h(font, size):
    b = ImageFont.truetype(font, 400).getbbox("H")
    return (b[3] - b[1]) * size / 400


def rng_(a, b):
    return {"start": ms(a), "duration": ms(b - a)}


def tf(pos=(0, 0), anchor=(0, 0), scale=(100, 100), opacity=100):
    return {"anchorPoint": list(anchor), "position": list(pos), "scale": list(scale), "rotation": 0, "opacity": opacity}


def text_layer(lid, name, parent, t1, text, family, style, size, color, pos, anchor=(0, 0), just="left", tracking=0, opacity=100):
    return {"type": "createFxTextLayer", "compositionId": COMP, "layerId": lid, "name": name, "parentLayerId": parent,
            "activeRange": rng_(0, t1), "transform": tf(pos, anchor, opacity=opacity),
            "sourceText": {"text": text, "fontFamily": family, "fontStyle": style, "fontSize": size, "fillColor": color,
                           "justification": just, "strokeWidth": 0, "tracking": tracking, "disableAutoWrap": True}}


def group_layer(lid, name, parent, t1, transform=None, insert=None):
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


def grain_fx(lid, eid, amount=2.2, size=1.8):
    """Noise inside the letters (re-seeded 24x a second), as on the Shoebox Tower and the Elliott Hill card."""
    return [fx(lid, eid, {"type": "grain", "amount": amount, "size": size, "softness": 0.25, "aspectRatio": 1.0, "seed": 1}),
            param_js(lid, eid, "seed", "return Math.floor(input.time.seconds * 24) % 997;")]


def map_layer(lid, name):
    return {"type": "createFxImageLayer", "compositionId": COMP, "layerId": lid, "name": name,
            "activeRange": rng_(0, DUR), "transform": dict(IDT),
            "source": {"assetId": "grunge353_dispmap", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": W, "height": H}}}


def jolt(t0, peak, settle=0.25):
    """Turbulent amount: sharp at rest, a hit at t0 that resolves in about `settle` seconds."""
    return [(max(0.0, t0 - 0.04), 0.0, "linear"), (t0, peak, "linear"), (t0 + settle * 0.35, peak * 0.35, EASE_OUT),
            (t0 + settle, 0.0, EASE_OUT)]


def track(fn, t0, t1, tol=0.4):
    """Per-frame screen positions of a projected 3D anchor -> (x keys, y keys), RDP-thinned."""
    xs, ys = [], []
    for f in range(int(t0 * FPS), int(t1 * FPS) + 2):
        t = f / FPS
        x, y = fn(t)
        xs.append((t, [x]))
        ys.append((t, [y]))
    return [(t, v[0], "linear") for t, v in rdp(xs, tol)], [(t, v[0], "linear") for t, v in rdp(ys, tol)]


def build_overlay(fonts):
    A = []
    fam = {k: (v["fontFamily"], v["fontStyle"]) for k, v in fonts.items()}
    ARC = fam["Archivo-SemiCondensed-Black_wdth80_wght900.ttf"]
    SER_I = fam["InstrumentSerif-Italic.ttf"]

    for lid, nm in [(901, "jolt"), (902, "type exit")]:
        A.append(map_layer(lid, "Grunge 353 map: " + nm))

    # ---------------- atmosphere: haze drifts, the dust swirls, the dying 2028 beam stutters and distorts
    A.append(fx(14, 1401, turbulent("hazeDrift", amount=7, size=220, evolution=0.45, seed=8)))
    A.append(fx(16, 1601, turbulent("dustSwirl", amount=7, size=70, evolution=2.2, seed=12)))
    A.append(fx(15, 1501, turbulent("beamFailing", amount=4, size=120, evolution=1.2, seed=28)))
    beam_turb = []
    for f in range(140, NFRAMES + 1):
        t = f / FPS
        m = light_2028(t) / STATIONS["y2028"]["power"]
        stutter = abs(m - 1.0)
        beam_turb.append((t, [4 + (26 * min(1.0, stutter) if f >= 176 else 6 * min(1.0, stutter))]))
    A.append({"type": "setFxLayerEffectParamAnimator", "compositionId": COMP, "layerId": 15, "effectId": 1501, "paramName": "amount",
              "dependencies": [], "animator": {"type": "keyframes", "enabled": True,
                                               "keyframes": [{"id": f"bt{i}", "layerTime": ms(t), "value": {"type": "float", "value": round(v[0], 3)},
                                                              "easing": {"type": "hold"}} for i, (t, v) in enumerate(beam_turb)]}})

    # ---------------- grade + grain (adjustments over the 3D picture), the same as the Shoebox Tower MG
    A.append({"type": "createFxAdjustmentLayer", "compositionId": COMP, "layerId": 310, "name": "Grade: teal shadows, warm highlights",
              "activeRange": rng_(0, DUR), "transform": dict(IDT), "insertIndex": 0})
    A.append(fx(310, 3101, {"type": "tintTritone", "amount": 0.16, "blackR": 0.02, "blackG": 0.10, "blackB": 0.09,
                            "whiteR": 1.0, "whiteG": 0.93, "whiteB": 0.82}))
    A.append(fx(310, 3103, {"type": "vignette", "amount": 0.42, "radius": 0.78, "feather": 0.65}))
    A.append({"type": "createFxAdjustmentLayer", "compositionId": COMP, "layerId": 300, "name": "Film grain",
              "activeRange": rng_(0, DUR), "transform": dict(IDT), "insertIndex": 0})
    A += grain_fx(300, 3001, amount=0.16, size=1.4)

    # ---------------- TYPE
    A.append(group_layer(200, "TYPE (all overlay typography)", None, DUR, insert=0))
    ch = STATIONS["china"]
    t_exit0, t_exit1 = T["quarter_end"], T["quarter_end"] + 0.14

    # Phase 2 type sits in one group: it leaves together with a quick turbulent + grunge displacement dissolve
    A.append(group_layer(205, "China type (-26%)", 200, t_exit1 + 0.05))
    A.append(fx(205, 2051, turbulent("chinaTypeExit", amount=0, size=36, evolution=10, seed=4)))
    A.append(param_keys(205, 2051, "amount", [(0, 0, "hold"), (t_exit0 - 0.02, 0, "hold"), (t_exit1, 34, EASE_IN)]))
    A.append(fx(205, 2052, grunge("chinaTypeDissolve", 902, softness=0.16, map_scale=1.6)))
    A.append(param_keys(205, 2052, "progress", [(0, 0, "hold"), (t_exit0, 0, "hold"), (t_exit1, 1.0, (0.5, 0.0, 0.6, 1.0))]))
    A.append(param_keys(205, 2052, "displace", [(0, 0, "hold"), (t_exit0, 0, "hold"), (t_exit1, 40, EASE_IN)]))

    # "China": italic serif label on the floor just in front of the stack
    SL = 84
    def china_label(t):
        x, y, _ = project([ch["x"] - 20, 0, ch["z"] - BOX["d"] / 2 - 150], cam(t))
        return x, min(y + 6, 985)
    tc = T["china"]
    kx, ky = track(china_label, tc - 0.05, t_exit1 + 0.05)
    A.append(text_layer(211, "China", 205, t_exit1 + 0.05, "China", SER_I[0], SER_I[1], SL, WHITE, (kx[0][1], ky[0][1]), just="center"))
    A.append(pkeys(211, "positionX", kx))
    A.append(pkeys(211, "positionY", [(t, v + 0.0, e) for t, v, e in ky]))
    A.append(pkeys(211, "opacity", [(tc - 0.01, 0, "linear"), (tc + 0.09, 100, EASE_OUT)]))
    A.append(fx(211, 2111, turbulent("chinaJitter", size=34, evolution=9, seed=3)))
    A.append(param_keys(211, 2111, "amount", jolt(tc + 0.02, 9, 0.24)))
    A += grain_fx(211, 2115)

    # "-26%": slams in to the right of the stack on "twenty-six"; "in one quarter" under it on "in"
    S26 = 190
    cap26 = cap_h(F_ARCHIVO, S26)
    w26 = text_w(F_ARCHIVO, S26, "−26%") - 3 * 12 * S26 / 1000
    def right_of_stack(t):
        P = cam(t)
        x1, y1, _ = project([ch["x"] + 200, -3 * PITCH, ch["z"] - 60], P)
        x0, y0, _ = project([ch["x"] + 200, 0, ch["z"] - 60], P)
        return x1, (y0 + y1) / 2
    n26 = T["n26"]
    left0 = min(right_of_stack(n26)[0] + 110, W - 96 - w26)
    def pos26(t):
        x, y = right_of_stack(t)
        return min(x + 110, W - 96 - w26) + w26 / 2, y - 115
    kx, ky = track(pos26, n26 - 0.05, t_exit1 + 0.05)
    A.append(text_layer(240, "-26%", 205, t_exit1 + 0.05, "−26%", ARC[0], ARC[1], S26, MINT, (kx[0][1], ky[0][1]),
                        anchor=(w26 / 2, -cap26 / 2), tracking=-12))
    A.append(pkeys(240, "positionX", kx))
    A.append(pkeys(240, "positionY", ky))
    A.append(pkeys(240, "opacity", [(n26 - 0.04, 0, "linear"), (n26 + 0.03, 100, "linear")]))
    A.append(pkeys(240, "scaleX", [(n26 - 0.04, 168, "linear"), (n26 + 0.20, 100, SNAP)]))
    A.append(pkeys(240, "scaleY", [(n26 - 0.04, 168, "linear"), (n26 + 0.20, 100, SNAP)]))
    A.append(fx(240, 2401, turbulent("minus26Slam", size=40, evolution=11, seed=9)))
    A.append(param_keys(240, 2401, "amount", [(n26 - 0.05, 0, "hold"), (n26, 48, "linear"), (n26 + 0.10, 16, EASE_OUT),
                                              (n26 + 0.25, 0, EASE_OUT)]))
    A += grain_fx(240, 2402)
    tq = T["in_quarter"]
    SQ = 72
    def pos_q(t):
        x, y = pos26(t)
        return x - w26 / 2 + 6, y + cap26 / 2 + 82
    kx, ky = track(pos_q, tq - 0.05, t_exit1 + 0.05)
    A.append(text_layer(241, "in one quarter", 205, t_exit1 + 0.05, "in one quarter", SER_I[0], SER_I[1], SQ, WHITE, (kx[0][1], ky[0][1])))
    A.append(pkeys(241, "positionX", kx))
    A.append(pkeys(241, "positionY", [(t, v, e) for t, v, e in ky]))
    A.append(pkeys(241, "opacity", [(tq - 0.01, 0, "linear"), (tq + 0.12, 100, EASE_OUT)]))
    A.append(fx(241, 2411, turbulent("quarterJitter", size=30, evolution=9, seed=6)))
    A.append(param_keys(241, 2411, "amount", jolt(tq + 0.02, 7, 0.28)))
    A += grain_fx(241, 2415)

    # Years: on the floor in front of each stack, landing as the stack comes into view ("2028" on the word);
    # they dim with their spotlights, and "2028" fails with its lamp
    for i, key in enumerate(ROW):
        s = STATIONS[key]
        lid = 251 + i
        ty = T[key]
        op_full = {"y2025": 100, "y2026": 86, "y2027": 68, "y2028": 52}[key]
        def ylabel(t, s=s):
            x, y, _ = project([s["x"] - 10, 0, s["z"] - BOX["d"] / 2 - 150], cam(t))
            return x, min(y + 6, 985)
        kx, ky = track(ylabel, ty - 0.05, DUR)
        A.append(text_layer(lid, s["label"], 200, DUR, s["label"], SER_I[0], SER_I[1], SL, WHITE, (kx[0][1], ky[0][1]), just="center"))
        A.append(pkeys(lid, "positionX", kx))
        A.append(pkeys(lid, "positionY", ky))
        if key != "y2028":
            A.append(pkeys(lid, "opacity", [(ty - 0.01, 0, "linear"), (ty + 0.10 + 0.02 * i, op_full, EASE_OUT)]))
        else:
            keys = [(ty - 0.01, 0, "linear"), (ty + 0.12, op_full, EASE_OUT)]
            prev = None
            for f in range(int((ty + 0.15) * FPS), NFRAMES):
                m = light_2028(f / FPS) / STATIONS["y2028"]["power"]
                v = op_full * (0.35 + 0.65 * min(m, 1.0)) if m > 0 else 9
                if prev is None or abs(v - prev) > 0.5:
                    keys.append((f / FPS, v, "hold"))
                    prev = v
            A.append(pkeys(lid, "opacity", keys))
        A.append(fx(lid, lid * 10 + 1, turbulent(f"year{s['label']}Jitter", size=32 + 3 * i, evolution=9 + i, seed=20 + i)))
        A.append(param_keys(lid, lid * 10 + 1, "amount", jolt(ty + 0.02, 8 - i * 0.6, 0.22 + 0.03 * i)))
        A += grain_fx(lid, lid * 10 + 5)

    # ---------------- impact jolts: Grunge 353 displacement map across the whole frame
    A.append({"type": "createFxAdjustmentLayer", "compositionId": COMP, "layerId": 100, "name": "Impact jolts (displacement map)",
              "activeRange": rng_(0, DUR), "transform": dict(IDT), "insertIndex": 0})
    A.append(fx(100, 1001, grunge("impactJolt", 901, softness=0.05, map_scale=1.6)))
    ti, tk = F_IMPACT / FPS, F_HIT / FPS
    A.append(param_keys(100, 1001, "displace", [(0, 0, "hold"), (ti - 0.004, 0, "hold"), (ti, 12, "hold"), (ti + 1 / FPS, 7, "hold"),
                                                (ti + 2 / FPS, 3, "hold"), (ti + 3 / FPS, 0, "hold"),
                                                (tk - 0.004, 0, "hold"), (tk, 6, "hold"), (tk + 1 / FPS, 2.5, "hold"), (tk + 2 / FPS, 0, "hold")]))
    A.append(param_keys(100, 1001, "mapShift.y", [(0, 0, "hold"), (ti, 0.17, "hold"), (ti + 1 / FPS, -0.31, "hold"), (ti + 2 / FPS, 0.44, "hold"),
                                                  (tk, 0.62, "hold"), (tk + 1 / FPS, -0.12, "hold")]))
    return A
