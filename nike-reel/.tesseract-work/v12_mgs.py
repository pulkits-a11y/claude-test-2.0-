# ================= FC3: supplied 'Endless Gallery' MG (its own VO muted) + special captions DUNKS. / AIR FORCE 1S. / RETRO JORDANS. =================
(_, a, b) = SEG["FC3"]
gs3 = D.group("FC3 SPECIAL CAPTIONS (Dunks / Air Force 1s / Retro Jordans)", 0, endcard_in)
soft_shadow(gs3)
SH3 = [(16, [0], {0}), (17, [0, 1, 2], {2}), (18, [0, 1], {1})]
st3 = [max(a, wfc(ln, ix[0])) for ln, ix, _k in SH3]
for k, (ln, ix, keys) in enumerate(SH3):
    f1 = st3[k + 1] if k + 1 < len(SH3) else b
    ws = [WORDS[ln][i]["w"].upper() for i in ix]
    sz = fit_size(" ".join(ws), "archivo", 150, 1300, {"wght": 880, "wdth": 80})
    xs_, lw = layout_line(ws, [WH(sz)] * len(ws))
    for j, i in enumerate(ix):
        wh_word(f"FC3 '{ws[j]}'", ws[j], 960 - lw / 2 + xs_[j], 250, sz, GREEN if i in keys else TEXT, min(max(st3[k], wfc(ln, i)), f1 - 1), f1, gs3, block=i in keys)
g3 = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": g3, "name": "FC3 MG: Endless Gallery (supplied, its VO muted), retimed to the names",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)}, "sourceRange": {"start": 0, "duration": GALLERY["durationMs"]},
       "sourceIntrinsicDuration": GALLERY["durationMs"], "transform": xf(),
       "source": {"assetId": "mg_gallery", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
k3 = [(a, 0), (st3[1], 750), (st3[2], 1750), (b, min(GALLERY["durationMs"] - 34, 1750 + round((b - st3[2]) * 1000 / FPS)))]
D.add({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": g3, "timeRemap": {
    "keyframes": [{"id": f"g3-{q}", "time": ms(e_), "value": v_, "easing": {"type": "linear"}} for q, (e_, v_) in enumerate(k3)],
    "before": "inactive", "after": "inactive"}})
plan_rows.append(("FC3", "DUNKS. / AIR FORCE 1S. / RETRO JORDANS.", "Special captions over the supplied MG", "Blur-to-sharp", "Block-to-word", "Hard cut", "top centre"))

# ================= FC4: supplied 'Three Hits' MG retimed to Tariffs / China / -26% / in one quarter / 2025-2028 + TARIFFS. =================
(_, a, b) = SEG["FC4"]
fv4 = lambda line, t: math.ceil(t * FPS + off[line] - 1e-6)
gs4 = D.group("FC4 SPECIAL CAPTION (TARIFFS.)", 0, endcard_in)
soft_shadow(gs4)
f_china = fv4(24, 57.635)
tz = fit_size("TARIFFS.", "archivo", 170, 900, {"wght": 880, "wdth": 80})
wh_word("FC4 'TARIFFS.'", "TARIFFS.", 960 - advance("TARIFFS.", *WH(tz)) / 2, 300, tz, TEXT, a, f_china, gs4, block=True)
g4 = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": g4, "name": "FC4 MG: Three Hits (supplied), retimed to the VO",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)}, "sourceRange": {"start": 0, "duration": THREEHITS["durationMs"]},
       "sourceIntrinsicDuration": THREEHITS["durationMs"], "transform": xf(),
       "source": {"assetId": "mg_threehits", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
f28 = fv4(25, 62.56)
k4 = [(a, 0), (f_china, 750), (fv4(24, 58.16), 1250), (fv4(24, 59.44), 2500), (fv4(25, 60.559), 3500), (f28, 5250),
      (b, min(THREEHITS["durationMs"] - 34, 5250 + round((b - f28) * 1000 / FPS)))]
k4c = []
for e_, v_ in k4:
    if k4c and (e_ <= k4c[-1][0] or v_ < k4c[-1][1]):
        continue
    k4c.append((e_, v_))
D.add({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": g4, "timeRemap": {
    "keyframes": [{"id": f"g4-{q}", "time": ms(e_), "value": v_, "easing": {"type": "linear"}} for q, (e_, v_) in enumerate(k4c)],
    "before": "inactive", "after": "inactive"}})
plan_rows.append(("FC4", "TARIFFS. -> (MG) China -26% in one quarter / 2025-2028", "Special caption, then the supplied MG", "-", "Block-to-word", "Hard cut", "top centre"))

