# --- O'Leary intro (v10): 2021 flash, continuous eye-anchored drift, hard punch-ins, trimmed pauses,
#     matte-graded background, one caption idea at a time, RETAIL. climax behind his head ---
key = "CLIP_OLEARY"
a, b = tl[key][0], SEG["A1_OLEARY"][2]
info = CLIPINFO[key]
year_flash("2021", a, a + YR)

F_IN = OL_FIN                       # first fast-clip frame used (silence before "This")
TRIMS = OL_TRIMS                    # fast-clip frame ranges removed (pauses), each hidden on a framing change


def ol_e(F):
    """fast-clip frame -> edit frame (relative to clip start), accounting for trims."""
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
       "need": 171.6, "retail": 179.4}            # word onsets in fast-clip frames (Whisper + energy check)
WE = {k: ol_e(math.ceil(v)) for k, v in OLW.items()}
N = b - a
E = (1090.0, 474.0)                 # point between his eyes in the base framing
OL_T = xf(pos=(1517, 853), scale=158)     # base framing: hides the CNBC chyron (y>770) and stock box (x>1230)


def drift(e):
    u = max(0.0, min(1.0, e / N))
    return 100 + 8 * (u * u * (3 - 2 * u))


# (edit start, absolute scale %, eye x, eye y, note)
SUBS = [(0, None, E[0], E[1], "base (drift only)"),
        (WE["worried"], 115, E[0], E[1], "punch IN on 'worried'"),
        (ol_e(TRIMS[0][1]), 106, 1150, E[1], "pull OUT, face right ('a Walmart', hides trim 1)"),
        (WE["Foot"], 118, 920, E[1], "punch IN, face left on 'Foot Locker'"),
        (ol_e(TRIMS[1][1]), 118, 1010, E[1], "re-angle on 'They' (hides trim 2)"),
        (WE["retail"], 136, 980, 640, "TIGHTEST on 'retail' (slam)")]

cg = D.group("O'LEARY CAPTIONS (one phrase at a time, open side)", 0, endcard_in)
D.effect(cg, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 0], "blurRadius": 34, "spreadRadius": 4, "blendMode": "normal"})
gO = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gO, "name": "LIVE CLIP Kevin O'Leary (1.15x, drift 100->108 on his eyes)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": list(E), "position": list(E), "scale": [100, 100], "rotation": 0, "opacity": 100}})
kk(gO, "scaleX", [(0, 100, "linear"), (N, 108, EASE)])
kk(gO, "scaleY", [(0, 100, "linear"), (N, 108, EASE)])
D.effect(gO, {"type": "vignette", "amount": 0.35, "feather": 0.6, "radius": 0.55})
glitch(gO, N)

for si, (e0, S, ex, ey, note) in enumerate(SUBS):
    e1 = SUBS[si + 1][0] if si + 1 < len(SUBS) else N
    d0 = drift(e0)
    s = 1.0 if S is None else S / d0
    T = (E[0] + (ex - E[0]) / (d0 / 100), E[1] + (ey - E[1]) / (d0 / 100))
    g = D.nid()
    dur_ = ms(e1) - ms(e0)
    D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": g, "name": f"O'Leary sub-shot {si}: {note}", "parentLayerId": gO,
           "activeRange": {"start": ms(e0), "duration": dur_},
           "transform": {"anchorPoint": list(E), "position": [round(T[0], 2), round(T[1], 2)], "scale": [round(100 * s, 3)] * 2, "rotation": 0, "opacity": 100}})
    F0 = ol_F(e0)
    src_ms = round(F0 * 1000 / 30)
    last = si == len(SUBS) - 1
    if last:     # 2-frame white flash on the slam, same signature as the silhouette flash
        fl = D.nid()
        D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": fl, "name": "retail slam flash (2 f)", "parentLayerId": g,
               "activeRange": {"start": 0, "duration": ms(2)}, "transform": xf(pos=(-400, -300), anchor=(0, 0)),
               "rect": {"size": [2800, 1800], "fillColor": [1, 0.97, 0.92, 1]}})
        D.keys(fl, "opacity", [(0, 90, "hold"), (1, 45, "hold")])
    if si == 0:
        flicker(g, "m_oleary", YR, 6, round((YR + F_IN) * 1000 / 30), OL_T, FLICK_QUICK, "O'Leary", dur_ms=ms(YR + 6) - ms(YR))
    # person (matted) on top of the background
    mv = D.nid()
    mi = MATTES["m_oleary"]
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": mv, "name": f"O'Leary matte {si} (MODNet)", "parentLayerId": g,
           "activeRange": {"start": 0, "duration": dur_}, "sourceRange": {"start": src_ms, "duration": min(dur_, mi["durationMs"] - src_ms)},
           "sourceIntrinsicDuration": mi["durationMs"], "transform": OL_T,
           "source": {"assetId": "m_oleary", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
    pv = D.nid()
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": pv, "name": f"O'Leary person {si} + own audio", "parentLayerId": g,
           "activeRange": {"start": 0, "duration": dur_}, "sourceRange": {"start": src_ms, "duration": min(dur_, info["durationMs"] - src_ms)},
           "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
           "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}},
           "volume": CLIPS[key][4]})
    D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": pv, "matteLayerId": mv, "mode": "luma"})
    n_ = e1 - e0
    vk = []
    if si == 0:
        vk += [(0, 0, "linear"), (2, CLIPS[key][4], "linear")]
    if last:
        se = ol_e(OL_SPEECH_END) - e0
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
    if last:     # RETAIL. behind his head (between person and background)
        RG = D.nid()
        D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": RG, "name": "CLIMAX: THEY DON'T NEED / RETAIL. (behind his head)", "parentLayerId": g,
               "activeRange": {"start": 0, "duration": dur_},
               "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
        D.effect(RG, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.5], "offset": [0, 0], "blurRadius": 36, "spreadRadius": 4, "blendMode": "normal"})
        S_abs = s * drift(e0) / 100

        def loc(qx, qy):      # final screen point -> local coords of this sub-shot group (drift taken at the slam)
            dd = drift(e0) / 100
            return (E[0] + ((qx - E[0]) / dd - (T[0] - E[0])) / s, E[1] + ((qy - E[1]) / dd - (T[1] - E[1])) / s)

        RET = WH(100)
        rs = fit_size("RETAIL.", "archivo", 520, 1150, {"wght": 880, "wdth": 80})
        rw = advance("RETAIL.", *WH(rs))
        base_y = 380          # the top of his head overlaps the lower half of the word
        top_y = base_y - 0.725 * rs
        ls = rs / S_abs
        lx, ly = loc(960 - rw / 2, base_y)
        lw = rw / S_abs
        R = D.text("CLIMAX 'RETAIL.' (slam)", "RETAIL.", lx, ly, "archivo", ls, TEXT, 0, n_, RG, wght=880, wdth=80, anchor=(lw / 2, -0.36 * ls))
        D.vox(R, ls)
        SLAM = {"type": "cubicBezier", "x1": 0.1, "y1": 0.9, "x2": 0.2, "y2": 1.0}
        kk(R, "scaleX", [(0, 120, "linear"), (3, 100, SLAM)])
        kk(R, "scaleY", [(0, 120, "linear"), (3, 100, SLAM)])
        # strike-through drawn 7 frames after it lands, over 5 frames
        st0 = 3 + 7
        th = 0.075 * rs
        sx, sy = loc(960 - rw / 2 - 14, base_y - 0.37 * rs - th / 2)
        line = D.nid()
        D.add({"type": "createFxRectLayer", "compositionId": C, "layerId": line, "name": "CLIMAX strike-through", "parentLayerId": RG,
               "activeRange": {"start": ms(st0), "duration": ms(n_) - ms(st0)}, "transform": xf(pos=(sx, sy), anchor=(0, 0)),
               "rect": {"size": [(rw + 28) / S_abs, th / S_abs], "fillColor": GREEN}})
        kk(line, "scaleX", [(0, 0, "linear"), (5, 100, EOUT)])
        # THEY DON'T NEED: small, above the R, word by word on their frames (relative to this sub-shot they come earlier -> shown from 0)
        tsz = 54
        tx, ty = loc(960 - rw / 2 + 8, top_y - 26)
        xs_t, _w = layout_line(["THEY", "DON'T", "NEED"], [("archivo", tsz, {"wght": 640, "wdth": 100}, 0)] * 3)
        for wi, (wd, xo) in enumerate(zip(["THEY", "DON'T", "NEED"], xs_t)):
            D.text(f"CLIMAX '{wd}'", wd, tx + xo / S_abs, ty, "archivo", tsz / S_abs, TEXT, 0, n_, RG, wght=640)
    bv = D.nid()
    D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": bv, "name": f"O'Leary background {si} (desat, darker, blurred)", "parentLayerId": g,
           "activeRange": {"start": 0, "duration": dur_}, "sourceRange": {"start": src_ms, "duration": min(dur_, info["durationMs"] - src_ms)},
           "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
           "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
    grade_fx(bv, lum=0.3)
    D.effect(bv, {"type": "primaryGrade", "semanticVersion": 1, "temperature": 0, "tint": 0, "exposure": -0.45, "contrast": 0,
                  "highlights": 0, "shadows": 0, "whites": 0, "blacks": 0, "saturation": -0.4, "vibrance": 0})
    D.effect(bv, {"type": "gaussianBlur", "blurriness": 12, "repeatEdgePixels": True})

# --- captions: one phrase at a time, single position on the open side, hard cuts between phrases ---
SNAP = {"type": "cubicBezier", "x1": 0.15, "y1": 0.85, "x2": 0.3, "y2": 1.0}


def snap_word(name, s_, x, y, font, size, color, f0, f1, parent, wght=None, wdth=100):
    """Appears on its frame: 4-frame ease-out, scale 110->100, blur 8->0, opacity 0->1. Hard cut at f1."""
    w = advance(s_, font, size, {"wght": wght, "wdth": wdth} if font == "archivo" else None, 0)
    lid = D.text(name, s_, x, y, font, size, color, f0, f1, parent, wght=wght, wdth=wdth, anchor=(w / 2, -0.35 * size))
    kk(lid, "opacity", [(0, 0, "linear"), (3, 100, SNAP)])
    kk(lid, "scaleX", [(0, 110, "linear"), (3, 100, SNAP)])
    kk(lid, "scaleY", [(0, 110, "linear"), (3, 100, SNAP)])
    bl = D.effect(lid, {"type": "gaussianBlur", "blurriness": 0})
    ekk(lid, bl, "blurriness", [(0, 8, "linear"), (3, 0, SNAP)])
    return lid, w


LEAD = ("serif_italic", 66, None, 0)
# (lead-in words with their frames, keyword, keyword font, colour, side, logo)
PHR = [([("This", WE["why"]), ("is", WE["why"])], ("why", WE["why"]), "serif", TEXT, "L", None),
       ([("you", WE["you"]), ("should", WE["should"]), ("be", WE["be"])], ("worried", WE["worried"]), "serif", GREEN, "L", None),
       ([("about", WE["about"]), ("the", WE["the"])], ("future", WE["future"]), "serif", GREEN, "L", None),
       ([("of", WE["of"]), ("a", WE["a1"])], ("WALMART", WE["Walmart"]), "wh", TEXT, "L", ("logo_walmart", 300)),
       ([("or", WE["or"]), ("a", WE["a2"])], ("FOOT LOCKER.", WE["Foot"]), "wh", TEXT, "R", ("logo_footlocker", 300))]
ph_start = [YR] + [min([f for _, f in p[0]] + [p[1][1]]) for p in PHR[1:]]
ph_end = ph_start[1:] + [WE["They"]]
for pi, (lead, (kw, kf), kfont, kcol, side, logo) in enumerate(PHR):
    p0, p1 = a + ph_start[pi], a + ph_end[pi]
    maxw = 700 if side == "L" else 540
    if kfont == "wh":
        ksz = fit_size(kw, "archivo", 300, maxw, {"wght": 880, "wdth": 80}); kspec = WH(ksz)
    else:
        ksz = fit_size(kw, "serif", 312, maxw); kspec = ("serif", ksz, None, 0)
    kwid = advance(kw, *kspec)
    lws = [w for w, _ in lead]
    lxs, lwid = layout_line(lws, [LEAD] * len(lws))
    lead_y = 430
    kw_y = lead_y + 0.80 * ksz + 6
    if side == "L":
        x_lead, x_kw = 110, 104
    else:
        x_lead, x_kw = 1830 - lwid, 1830 - kwid
    for (w, f), xo in zip(lead, lxs):
        snap_word(f"OL cap '{w}'", w, x_lead + xo, lead_y, "serif_italic", 66, TEXT, max(p0, a + f), p1, cg)
    if kfont == "wh":
        snap_word(f"OL KEY '{kw}'", kw, x_kw, kw_y, "archivo", ksz, kcol, max(p0, a + kf), p1, cg, wght=880, wdth=80)
    else:
        snap_word(f"OL KEY '{kw}'", kw, x_kw, kw_y, "serif", ksz, kcol, max(p0, a + kf), p1, cg)
    if logo:      # the real store logo pops in small next to the word for ~0.5 s
        asset, lw_ = logo
        lh = lw_ * LOGO_W[asset][1] / LOGO_W[asset][0]
        lx_ = x_kw if side == "L" else 1830 - lw_
        ly_ = kw_y + 34
        img = D.nid()
        f0l = max(p0, a + kf)
        D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": img, "name": f"OL logo {asset} (0.5 s)", "parentLayerId": cg,
               "activeRange": {"start": ms(f0l), "duration": ms(min(f0l + 15, p1)) - ms(f0l)},
               "transform": {"anchorPoint": [0, 0], "position": [lx_, ly_], "scale": [round(100 * lw_ / LOGO_W[asset][0], 3)] * 2, "rotation": 0, "opacity": 100},
               "source": {"assetId": asset, "fit": "contain"}})
        kk(img, "opacity", [(0, 0, "linear"), (3, 100, SNAP)])
plan_rows.append(("CLIP_OLEARY", "2021 / This is WHY / you should be WORRIED / about the FUTURE / of a WALMART / or a FOOT LOCKER. / THEY DON'T NEED RETAIL.",
                  "One phrase at a time on the open side; serif keywords (green: worried, future), heavy condensed brands + logos",
                  "Snap (4 f ease-out: 110->100, blur 8->0)", "RETAIL. slam behind head + strike-through", "Hard cut", "open side of framing"))

