# ================= 4a. TC1: camera follows each word (ease-out, motion blur); retail stores pop in; slide right, then a true cut wide =================
(_, a, b) = SEG["TC1"]
L = WORDS[1]
f_cut = wf(1, 6, a)
big = ("serif", 230, None, 0)
pos_s1, _ = row([w["w"] for w in L[0:4]], [SMALL] * 4, 404)
pos_b, _ = row(["needed", "retail"], [big, big], 618)
pos_s2, _ = row([w["w"] for w in L[6:9]], [SMALL] * 3, 714)


def tc1_build(g, lo, hi, tag):
    """Builds the lockup in group g, visible in [lo, hi). Words that started before lo skip their entrance."""
    out = {}
    for i, (x, y) in zip(range(0, 4), pos_s1):
        f0 = wf(1, i, a)
        if f0 >= hi:
            continue
        lid = D.text(f"TC1{tag} '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, max(f0, lo), hi, g, wght=520); D.vox(lid, 58)
        if f0 >= lo:
            D.blur_to_sharp(lid)
        out[i] = (f0, x + advance(L[i]["w"], *SMALL) / 2, y - 21)
    for k, (i, (x, y)) in enumerate(zip((4, 5), pos_b)):
        f0 = wf(1, i, a)
        if f0 >= hi:
            continue
        lid, w = centred_text(f"TC1{tag} KEY '{L[i]['w']}'", L[i]["w"], x, y, "serif", 230, GREEN, max(f0, lo), hi, g)
        D.vox(lid, 230)
        if f0 >= lo:
            D.pop(lid)
            if k == 0:
                D.flicker_in(lid)
        out[i] = (f0, x + w / 2, y - 78)
    for i, (x, y) in zip(range(6, 9), pos_s2):
        f0 = max(f_cut, wf(1, i, a))
        if f0 >= hi:
            continue
        lid = D.text(f"TC1{tag} '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, max(f0, lo), hi, g, wght=520); D.vox(lid, 58)
        if f0 >= lo:
            D.blur_to_sharp(lid)
    return out


gA = D.group("TC1 A: zoomed camera follows each word (retail stores pop in)", 0, f_cut)
fA = tc1_build(gA, 0, f_cut, "A")
ret_c = fA[5][1:]
f_ret = wf(1, 5, a)
for k, (asset, dx, dy, rot) in enumerate((("st_footlocker", 360, -300, -3), ("st_nikestore", -430, 250, 2.5), ("st_aisle", 520, 215, -2))):
    f0 = f_ret + 1 + 3 * k
    lid = D.nid()
    D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": lid, "name": f"TC1 retail pop-in {asset}", "parentLayerId": gA,
           "activeRange": {"start": ms(f0), "duration": ms(f_cut) - ms(f0)},
           "transform": {"anchorPoint": [540, 310], "position": [ret_c[0] + dx, ret_c[1] + dy], "scale": [40, 40], "rotation": rot, "opacity": 100},
           "source": {"assetId": asset, "fit": "contain"}})
    kk(lid, "scaleX", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    kk(lid, "scaleY", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    D.effect(lid, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 8], "blurRadius": 26, "spreadRadius": 0, "blendMode": "normal"})
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
slide = dict(prev_v); slide["positionX"] -= 170
keys.append((f_cut, slide, EOUT))                       # zoomed in on 'retail', the camera slides right
cam_keys(gA, keys)
gB = D.group("TC1 B: hard cut to the wide lockup", 0, b)
tc1_build(gB, f_cut, b, "B")
cam_keys(gB, [(f_cut, cam_vals(960, 560, 1.0), "linear"), (b, cam_vals(960, 560, 1.04), EOUT)])
plan_rows.append(("TC1", "Well, turns out, Nike NEEDED RETAIL more than anyone.", "Size-contrast build", "Blur-to-sharp",
                  "Flicker-in; camera follows each word (ease-out, motion blur); 3 retail stills pop in; slide right, hard cut wide", "Cut out", "centered"))

