# ================= 4a. TC1: camera follows each word; retail stores pop in; then one eased move DOWN (motion blur) to 'more than anyone.' =================
(_, a, b) = SEG["TC1"]
L = WORDS[1]
big = ("serif", 230, None, 0)
pos_s1, _ = row([w["w"] for w in L[0:4]], [SMALL] * 4, 404)
pos_b, _ = row(["needed", "retail"], [big, big], 618)
gA = D.group("TC1: camera follows each word, then moves down to 'more than anyone.'", 0, b)
fA = {}
for i, (x, y) in zip(range(0, 4), pos_s1):
    f0 = wf(1, i, a)
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, f0, b, gA, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
    fA[i] = (f0, x + advance(L[i]["w"], *SMALL) / 2, y - 21)
for k, (i, (x, y)) in enumerate(zip((4, 5), pos_b)):
    f0 = wf(1, i, a)
    lid, w = centred_text(f"TC1 KEY '{L[i]['w']}'", L[i]["w"], x, y, "serif", 230, GREEN, f0, b, gA)
    D.vox(lid, 230); D.pop(lid)
    if k == 0:
        D.flicker_in(lid)
    fA[i] = (f0, x + w / 2, y - 78)
ret_c = fA[5][1:]
f_ret = wf(1, 5, a)
for k, (asset, dx, dy, rot) in enumerate((("st_footlocker", 360, -300, -3), ("st_nikestore", -430, 250, 2.5), ("st_aisle", 520, 215, -2))):
    f0 = f_ret + 1 + 3 * k
    lid = D.nid()
    D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": lid, "name": f"TC1 retail pop-in {asset} (scrolls up with the move)", "parentLayerId": gA,
           "activeRange": {"start": ms(f0), "duration": ms(b) - ms(f0)},
           "transform": {"anchorPoint": [540, 310], "position": [ret_c[0] + dx, ret_c[1] + dy], "scale": [40, 40], "rotation": rot, "opacity": 100},
           "source": {"assetId": asset, "fit": "contain"}})
    kk(lid, "scaleX", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    kk(lid, "scaleY", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
keys, prev_arr, prev_v = [], None, None
for i in range(0, 6):
    f, cx, cy = fA[i]
    v = cam_vals(cx, cy, 2.5 if i < 4 else 1.55)
    if prev_v is None:
        keys.append((a, v, "linear")); prev_arr = a
    else:
        depart = max(prev_arr + 1, f - 4)
        if depart > prev_arr:
            keys.append((depart, prev_v, "linear"))
        keys.append((f + 2, v, EOUT)); prev_arr = f + 2
    prev_v = v
# 'more than anyone.' sits below the lockup; the camera travels down to it (ease in-out, motion blur)
DROP = 1180
MT = ("archivo", 72, {"wght": 520, "wdth": 100}, 0)
AN = ("serif_italic", 170, None, 0)
xsB, WB = layout_line(["more", "than", "anyone."], [MT, MT, AN])
Y_MT = 600 + DROP
m0 = max(prev_arr + 1, f_ret + 8)                      # start moving once the stores have popped
m1 = m0 + 14
v_end = cam_vals(960, Y_MT - 40, 1.0)
keys.append((m0, prev_v, "linear"))
keys.append((m1, v_end, EASE))
keys.append((b, cam_vals(960, Y_MT - 40, 1.03), EOUT))
cam_keys(gA, keys)


def _bez(x1, y1, x2, y2, t):
    lo_, hi_ = 0.0, 1.0
    for _ in range(40):
        u = (lo_ + hi_) / 2
        x = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u ** 2 * x2 + u ** 3
        lo_, hi_ = (u, hi_) if x < t else (lo_, u)
    u = (lo_ + hi_) / 2
    return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3


LOCK_BOTTOM = ret_c[1] + 215 + 124 * 1.0              # lowest store image edge (local)
f_clear = m1
for fr_ in range(m0, m1 + 1):                          # first frame the whole lockup + images are off the top of the screen
    p_ = _bez(EASE["x1"], EASE["y1"], EASE["x2"], EASE["y2"], (fr_ - m0) / (m1 - m0))
    z = prev_v["scaleY"] / 100 + (1.0 - prev_v["scaleY"] / 100) * p_
    py = prev_v["positionY"] + (v_end["positionY"] - prev_v["positionY"]) * p_
    if py + z * (LOCK_BOTTOM - 540) < 0:
        f_clear = fr_
        break
TC1_CLEAR = f_clear
for k_, (i, sp) in enumerate(zip((6, 7, 8), (MT, MT, AN))):
    f0 = max(f_clear, wf(1, i, a))
    if sp is AN:
        lid = D.text("TC1 'anyone.' (Instrument Serif italic)", "anyone.", 960 - WB / 2 + xsB[k_], Y_MT, "serif_italic", 170, GREEN, f0, b, gA)
        D.vox(lid, 170); D.blur_to_sharp(lid, 16)
    else:
        lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], 960 - WB / 2 + xsB[k_], Y_MT, "archivo", 72, TEXT, f0, b, gA, wght=520)
        D.vox(lid, 72); D.blur_to_sharp(lid)
plan_rows.append(("TC1", "Well, turns out, Nike NEEDED RETAIL more than anyone.", "Size-contrast build", "Blur-to-sharp",
                  "Flicker-in; camera follows each word; 3 retail stills pop in; one eased move down (motion blur) to 'more than anyone.'", "Cut out", "centered"))

