# --- O'Leary intro (v11): 2021 flash, Kevin inside the vintage TV (same placement as the Donahoe break), his matte grade kept,
#     no face zooms, trimmed pauses, hard-open captions beside the TV, store logos under their lead-ins,
#     THEY DON'T NEED / RETAIL. in the centre, then the TV loses its signal for a second ---
key = "CLIP_OLEARY"
a, b = tl[key][0], SEG["A1_OLEARY"][2]
info = CLIPINFO[key]
year_flash("2021", a, a + YR)

F_IN = OL_FIN
TRIMS = OL_TRIMS


def ol_e(F):
    rem = sum(min(max(F - t0, 0), t1 - t0) for t0, t1 in TRIMS)
    return F - F_IN - rem


def ol_F(e):
    F = e + F_IN
    for t0, t1 in TRIMS:
        if F >= t0:
            F += t1 - t0
    return F


OLW = {"why": 28.8, "you": 40.2, "should": 45.9, "be": 51.6, "worried": 56.4, "about": 66.9, "the": 72.6, "future": 80.4,
       "of": 90.9, "a1": 102.0, "Walmart": 112.8, "or": 123.6, "a2": 130.5, "Foot": 137.1, "They": 161.7, "don't": 165.0,
       "need": 171.6, "retail": 179.4}
WE = {k: ol_e(math.ceil(v)) for k, v in OLW.items()}
N = b - a
LOSS0 = ol_e(OL_SPEECH_END)              # the TV loses its signal once he has finished "They don't need retail"
OL_T = xf(pos=(1517, 853), scale=158)     # his framing inside the picture (hides the CNBC chyron and stock box)

# captions group first, so it sits above the TV
cg = D.group("O'LEARY CAPTIONS (hard open, one phrase at a time, beside the TV)", 0, endcard_in)
D.effect(cg, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 0], "blurRadius": 34, "spreadRadius": 4, "blendMode": "normal"})

RG = D.group("CLIMAX: THEY DON'T NEED / RETAIL. (centre)", 0, endcard_in)
D.effect(RG, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.6], "offset": [0, 0], "blurRadius": 40, "spreadRadius": 6, "blendMode": "normal"})
gO = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gO, "name": "LIVE CLIP Kevin O'Leary inside the TV (1.15x)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [922, 468], "position": [922, 468], "scale": [100, 100], "rotation": 0, "opacity": 100}})
tvdur = ms(b) - ms(a)
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "TV frame (supplied green-screen still, screen keyed out)",
       "parentLayerId": gO, "activeRange": {"start": 0, "duration": tvdur}, "transform": xf(pos=(0, 0), anchor=(0, 0)),
       "source": {"assetId": "tv_frame", "fit": "contain"}})
maskO = D.nid()
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": maskO, "name": "TV screen matte", "parentLayerId": gO,
       "activeRange": {"start": 0, "duration": tvdur}, "transform": xf(pos=(0, 0), anchor=(0, 0)), "source": {"assetId": "tv_mask", "fit": "contain"}})
gSO = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gSO, "name": "TV screen content (CRT, signal loss at the end)", "parentLayerId": gO,
       "activeRange": {"start": 0, "duration": tvdur},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": gSO, "matteLayerId": maskO, "mode": "alpha"})
# Kevin's picture (his matte-based grade kept) scaled onto the screen: eyes upper-middle of the screen
gK = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gK, "name": "Kevin picture on the screen", "parentLayerId": gSO,
       "activeRange": {"start": 0, "duration": tvdur},
       "transform": {"anchorPoint": [1090, 474], "position": [922, 440], "scale": [28, 28], "rotation": 0, "opacity": 100}})

SUBS = [0, ol_e(TRIMS[0][1]), ol_e(TRIMS[1][1])]      # sub-shots only where the pauses were trimmed (no reframes)
for si, e0 in enumerate(SUBS):
    e1 = SUBS[si + 1] if si + 1 < len(SUBS) else N
    g = D.nid()
    dur_ = ms(e1) - ms(e0)
    D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": g, "name": f"Kevin sub-shot {si} (trim join)", "parentLayerId": gK,
           "activeRange": {"start": ms(e0), "duration": dur_},
           "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
    F0 = ol_F(e0)
    src_ms = round(F0 * 1000 / 30)
    last = si == len(SUBS) - 1
    if si == 0:
        flicker(g, "m_oleary", YR, 6, round((YR + F_IN) * 1000 / 30), OL_T, FLICK_QUICK, "O'Leary", dur_ms=ms(YR + 6) - ms(YR))
    mv = D.nid()
    mi = MATTES["m_oleary"]
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": mv, "name": f"Kevin matte {si} (MODNet)", "parentLayerId": g,
           "activeRange": {"start": 0, "duration": dur_}, "sourceRange": {"start": src_ms, "duration": max(1, min(dur_, mi["durationMs"] - src_ms))},
           "sourceIntrinsicDuration": mi["durationMs"], "transform": OL_T,
           "source": {"assetId": "m_oleary", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
    pv = D.nid()
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": pv, "name": f"Kevin person {si} + own audio", "parentLayerId": g,
           "activeRange": {"start": 0, "duration": dur_}, "sourceRange": {"start": src_ms, "duration": max(1, min(dur_, info["durationMs"] - src_ms))},
           "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
           "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
           "volume": CLIPS[key][4]})
    D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": pv, "matteLayerId": mv, "mode": "luma"})
    vk = []
    if si == 0:
        vk += [(0, 0, "linear"), (2, CLIPS[key][4], "linear")]
    if last:
        se = LOSS0 - e0
        vk += [(0, CLIPS[key][4], "linear"), (se, CLIPS[key][4], "linear"), (se + 3, 0, "linear")]
    if vk:
        D.keys(pv, "volume", vk)
    grade_fx(pv, lum=0.3)
    D.effect(pv, {"type": "primaryGrade", "semanticVersion": 1, "temperature": -0.05, "tint": 0, "exposure": -0.2, "contrast": 0.05,
                  "highlights": -0.1, "shadows": 0, "whites": 0, "blacks": 0, "saturation": -0.18, "vibrance": 0})
    sk = D.nid()
    D.add({"type": "addFxLayerEffect", "compositionId": C, "layerId": pv, "effectId": sk,
           "effect": {"type": "primaryGrade", "semanticVersion": 1, "temperature": -0.06, "tint": 0.04, "exposure": 0, "contrast": 0,
                      "highlights": 0, "shadows": 0, "whites": 0, "blacks": 0, "saturation": -0.45, "vibrance": 0},
           "compositingOptions": {"effectOpacity": 1, "maskReferences": [],
                                  "qualifier": {"semanticVersion": 1, "hue": {"center": 12, "width": 34, "softness": 12},
                                                "saturation": {"low": 0.25, "high": 1, "softness": 0.1}, "luminance": {"low": 0.1, "high": 1, "softness": 0.05},
                                                "refine": {"denoise": 2, "blurRadius": 2, "choke": 0}, "invert": False}}})
    bv = D.nid()
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": bv, "name": f"Kevin background {si} (desat, darker, blurred)", "parentLayerId": g,
           "activeRange": {"start": 0, "duration": dur_}, "sourceRange": {"start": src_ms, "duration": max(1, min(dur_, info["durationMs"] - src_ms))},
           "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
           "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
    grade_fx(bv, lum=0.3)
    D.effect(bv, {"type": "primaryGrade", "semanticVersion": 1, "temperature": 0, "tint": 0, "exposure": -0.45, "contrast": 0,
                  "highlights": 0, "shadows": 0, "whites": 0, "blacks": 0, "saturation": -0.4, "vibrance": 0})
    D.effect(bv, {"type": "gaussianBlur", "blurriness": 12, "repeatEdgePixels": True})
D.rect("TV screen black", 0, 0, 1920, 1080, [0.02, 0.02, 0.02, 1], 0, N, gSO)
# the same screen treatment as the Donahoe break, with the signal loss in front of it
lo = D.effect(gSO, {"type": "customShader", "name": "crtSignalLoss", "description": "CRT signal loss: collapse flash, then snow, tearing and a rolling bar.",
                    "wgsl": open(os.path.join(W, "shaders", "crt_loss.wgsl")).read(),
                    "params": [{"name": "animationTime", "description": "Engine clock (s).", "min": 0, "max": 3600, "default": 0},
                               {"name": "loss", "description": "0 = picture, 1 = full static.", "min": 0, "max": 1, "default": 0},
                               {"name": "flash", "description": "Bright collapse flash 0..1.", "min": 0, "max": 1, "default": 0}]})
ekk(gSO, lo, "loss", [(0, 0, "hold"), (LOSS0, 0.55, "hold"), (LOSS0 + 1, 0.85, "hold"), (LOSS0 + 2, 1, "hold")])
ekk(gSO, lo, "flash", [(0, 0, "hold"), (LOSS0, 0.9, "hold"), (LOSS0 + 1, 0.45, "hold"), (LOSS0 + 2, 0, "hold")])
D.effect(gSO, {"type": "chromaticAberration", "amount": 0.15, "direction": 0})
D.effect(gSO, {"type": "customShader", "name": "crtScanlines", "description": "CRT scanlines with a slow rolling band.",
               "wgsl": open(os.path.join(W, "shaders", "crt.wgsl")).read(),
               "params": [{"name": "animationTime", "description": "Engine clock (s).", "min": 0, "max": 3600, "default": 0},
                          {"name": "linePx", "description": "Scanline period in px.", "min": 1, "max": 20, "default": 3.0},
                          {"name": "strength", "description": "Scanline darkness 0..1.", "min": 0, "max": 1, "default": 0.38},
                          {"name": "roll", "description": "Rolling band speed (screens/s).", "min": 0, "max": 2, "default": 0.35}]})
ngO = D.effect(gSO, {"type": "grain", "amount": 0.30, "size": 1.4, "softness": 0.3, "aspectRatio": 1.0, "seed": 6})
D.effect_script(gSO, ngO, "seed", "return Math.floor(input.time.seconds * 24);")
D.effect(gSO, {"type": "glow", "glowThreshold": 60, "glowRadius": 14, "glowIntensity": 0.5})
D.effect(gO, {"type": "vignette", "amount": 0.55, "feather": 0.6, "radius": 0.75})
ng2O = D.effect(gO, {"type": "grain", "amount": 0.12, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0, "seed": 9})
D.effect_script(gO, ng2O, "seed", "return Math.floor(input.time.seconds * 24);")
zkO = [(0, 100, "linear"), (N, 110, EASE)]          # slow push on the whole TV, like the Donahoe break
kk(gO, "scaleX", zkO); kk(gO, "scaleY", zkO)
glitch(gO, N)

# --- captions: hard open, one phrase at a time, beside the TV (left / right) ---
LEAD = ("serif_italic", 66, None, 0)
PHR = [([("This", WE["why"]), ("is", WE["why"])], ("why", WE["why"]), TEXT, "L", None),
       ([("you", WE["you"]), ("should", WE["should"]), ("be", WE["be"])], ("worried", WE["worried"]), GREEN, "L", None),
       ([("about", WE["about"]), ("the", WE["the"])], ("future", WE["future"]), GREEN, "L", None),
       ([("of", WE["of"]), ("a", WE["a1"])], (None, WE["Walmart"]), TEXT, "L", ("logo_walmart", 430)),
       ([("or", WE["or"]), ("a", WE["a2"])], (None, WE["Foot"]), TEXT, "R", ("logo_footlocker", 470))]
ph_start = [YR] + [min([f for _, f in p[0]] + [p[1][1]]) for p in PHR[1:]]
ph_end = ph_start[1:] + [WE["They"]]
LEAD_Y = 430
for pi, (lead, (kw, kf), kcol, side, logo) in enumerate(PHR):
    p0, p1 = a + ph_start[pi], a + ph_end[pi]
    lws = [w for w, _ in lead]
    lxs, lwid = layout_line(lws, [LEAD] * len(lws))
    x_lead = 110 if side == "L" else 1830 - lwid
    for (w, f), xo in zip(lead, lxs):
        D.text(f"OL cap '{w}'", w, x_lead + xo, LEAD_Y, "serif_italic", 66, TEXT, max(p0, a + f), p1, cg)
    if kw:
        ksz = fit_size(kw, "serif", 312, 520)
        kwid = advance(kw, "serif", ksz, None, 0)
        x_kw = 104 if side == "L" else 1830 - kwid
        D.text(f"OL KEY '{kw}'", kw, x_kw, LEAD_Y + 0.80 * ksz + 6, "serif", ksz, kcol, max(p0, a + kf), p1, cg)
    if logo:      # the store logo takes the keyword's place, a consistent gap under the lead-in
        asset, lw_ = logo
        lh = lw_ * LOGO_SZ[asset][1] / LOGO_SZ[asset][0]
        lx_ = 110 if side == "L" else 1830 - lw_
        ly_ = LEAD_Y + 34                    # lead-in baseline + 34 px (descender + breathing room)
        img = D.nid()
        D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": img, "name": f"OL logo {asset}", "parentLayerId": cg,
               "activeRange": {"start": ms(max(p0, a + kf)), "duration": ms(p1) - ms(max(p0, a + kf))},
               "transform": {"anchorPoint": [0, 0], "position": [lx_, ly_], "scale": [round(100 * lw_ / LOGO_SZ[asset][0], 3)] * 2, "rotation": 0, "opacity": 100},
               "source": {"assetId": asset, "fit": "contain"}})
# climax in the centre: THEY DON'T NEED / RETAIL. (hard open), held through the signal loss, then the strike-through
rs = fit_size("RETAIL.", "archivo", 520, 1180, {"wght": 880, "wdth": 80})
rw = advance("RETAIL.", *WH(rs))
base_y = 540 + 0.36 * rs + 40
top_y = base_y - 0.725 * rs
TSZ = 64
TSP = ("archivo", TSZ, {"wght": 640, "wdth": 100}, 0)
xs_t, wt = layout_line(["THEY", "DON'T", "NEED"], [TSP] * 3)
for (wd, f), xo in zip((("THEY", WE["They"]), ("DON'T", WE["don't"]), ("NEED", WE["need"])), xs_t):
    D.text(f"CLIMAX '{wd}'", wd, 960 - wt / 2 + xo, top_y - 34, "archivo", TSZ, TEXT, a + f, b, RG, wght=640)
R = D.text("CLIMAX 'RETAIL.'", "RETAIL.", 960 - rw / 2, base_y, "archivo", rs, TEXT, a + WE["retail"], b, RG, wght=880, wdth=80)
D.vox(R, rs)
st0 = a + WE["retail"] + 10
th = 0.075 * rs
line = D.nid()
D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": line, "name": "CLIMAX strike-through", "parentLayerId": RG,
       "activeRange": {"start": ms(st0), "duration": ms(b) - ms(st0)}, "transform": xf(pos=(960 - rw / 2 - 14, base_y - 0.37 * rs - th / 2), anchor=(0, 0)),
       "rect": {"size": [rw + 28, th], "fillColor": GREEN}})
kk(line, "scaleX", [(0, 0, "linear"), (5, 100, EOUT)])
plan_rows.append(("CLIP_OLEARY", "2021 / This is WHY / you should be WORRIED / about the FUTURE / of a [Walmart logo] / or a [Foot Locker logo] / THEY DON'T NEED RETAIL.",
                  "Kevin inside the TV (Donahoe placement); captions beside the TV, hard open; logos under their lead-ins",
                  "Hard open", "RETAIL. centred + strike-through; TV signal loss for 1 s", "Hard cut", "left / right of the TV, climax centre"))

