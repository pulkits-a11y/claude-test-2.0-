BLOCK_HELPERS = r'''
# ---------- v6 helpers: WHAT HAPPENED style (Archivo 880 / width 80 caps), soft shadow, camera ----------
def WH(size):
    return ("archivo", size, {"wght": 880, "wdth": 80}, 0)


def soft_shadow(g, alpha=0.45, blur=40, spread=4):
    """The light shadow used on the shelf/hype/athlete block (client reference: 'little to no shadow')."""
    D.effect(g, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, alpha], "offset": [0, 0], "blurRadius": blur,
                 "spreadRadius": spread, "blendMode": "normal"})


def fit_size(s, font, size, maxw, axes=None):
    while size > 20 and advance(s, font, size, axes, 0) > maxw:
        size -= 4
    return size


def wh_word(name, s, x, y, size, color, f0, f1, parent, block=False, anim="blur", vox=True):
    if f0 >= f1:
        f0 = f1 - 1
    if block:
        w = advance(s, *WH(size))
        D.rect(f"{name} block", x, y - 0.725 * size, w, 0.745 * size, GREEN, f0, min(f0 + STEP, f1), parent)
        f0 = min(f0 + STEP, f1 - 1)
    lid = D.text(name, s, x, y, "archivo", size, color, f0, f1, parent, wght=880, wdth=80)
    if anim == "blur" and not block:
        D.blur_to_sharp(lid)
    if vox:
        D.vox(lid, size)
    return lid


def wh_random(name, s, x, y, size, color_fn, f0, f1, parent):
    letters = list(s)
    order = [i for i in range(len(letters)) if letters[i] != " "]
    random.shuffle(order)
    for n_, li in enumerate(order):
        pre = "".join(letters[:li])
        lx = x + (advance(pre, *WH(size)) if pre else 0)
        batch = (n_ * 3) // max(1, len(order))
        lid = D.text(f"{name} '{letters[li]}'", letters[li], lx, y, "archivo", size, color_fn(letters[li]),
                     min(f0 + batch * STEP, f1 - 1), f1, parent, wght=880, wdth=80)
        D.vox(lid, size)


def cam_vals(cx, cy, z):
    return {"positionX": 960 - z * (cx - 960), "positionY": 540 - z * (cy - 540), "scaleX": z * 100, "scaleY": z * 100}


def cam_keys(g, keys):
    """keys: list of (frame, vals-dict, easing). Frames are program frames (group spans the program)."""
    for prop in ("positionX", "positionY", "scaleX", "scaleY"):
        kk(g, prop, [(f, round(v[prop], 3), e) for (f, v, e) in keys])
    mblur(g)

'''

BLOCK_TC1 = r'''# ================= 4a. TC1: camera follows each word (ease-out, motion blur); retail stores pop in; slide right, hard cut wide =================
(_, a, b) = SEG["TC1"]
g = D.group("TC1 Text Centerpiece (camera follows each word; retail stores pop in)", 0, endcard_in)
L = WORDS[1]
focus = []
pos, _ = row([w["w"] for w in L[0:4]], [SMALL] * 4, 404)
for i, (x, y) in zip(range(0, 4), pos):
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, wf(1, i, a), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
    focus.append((wf(1, i, a), x + advance(L[i]["w"], *SMALL) / 2, y - 21, 2.5))
big = ("serif", 230, None, 0)
pos, _ = row(["needed", "retail"], [big, big], 618)
ret_c = None
for k, (i, (x, y)) in enumerate(zip((4, 5), pos)):
    lid, w = centred_text(f"TC1 KEY '{L[i]['w']}'", L[i]["w"], x, y, "serif", 230, GREEN, wf(1, i, a), b, g)
    D.vox(lid, 230); D.pop(lid)
    if k == 0:
        D.flicker_in(lid)
    focus.append((wf(1, i, a), x + w / 2, y - 78, 1.55))
    if k == 1:
        ret_c = (x + w / 2, y - 78)
f_cut = wf(1, 6, a)
pos, _ = row([w["w"] for w in L[6:9]], [SMALL] * 3, 714)
for i, (x, y) in zip(range(6, 9), pos):
    lid = D.text(f"TC1 '{L[i]['w']}'", L[i]["w"], x, y, "archivo", 58, TEXT, max(f_cut, wf(1, i, a)), b, g, wght=520); D.vox(lid, 58); D.blur_to_sharp(lid)
# retail stores pop in around 'retail' inside the camera group, so the zoom crops them like objects in the scene
f_ret = wf(1, 5, a)
for k, (asset, dx, dy, rot) in enumerate((("st_footlocker", 360, -300, -3), ("st_nikestore", -430, 250, 2.5), ("st_aisle", 520, 215, -2))):
    f0 = f_ret + 1 + 3 * k
    lid = D.nid()
    D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": lid, "name": f"TC1 retail pop-in {asset}", "parentLayerId": g,
           "activeRange": {"start": ms(f0), "duration": ms(f_cut) - ms(f0)},
           "transform": {"anchorPoint": [540, 310], "position": [ret_c[0] + dx, ret_c[1] + dy], "scale": [40, 40], "rotation": rot, "opacity": 100},
           "source": {"assetId": asset, "fit": "contain"}})
    kk(lid, "scaleX", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    kk(lid, "scaleY", [(0, 26, "linear"), (2, 43, EOUT), (4, 40, EOUT)])
    D.effect(lid, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 8], "blurRadius": 26, "spreadRadius": 0, "blendMode": "normal"})
# camera: each move starts fast and ends slow; zoomed in on 'retail' it slides right, then hard-cuts to the wide lockup
keys, prev_arr, prev_v = [], None, None
for (f, cx, cy, z) in focus:
    v = cam_vals(cx, cy, z)
    if prev_v is None:
        keys.append((a, v, "linear")); prev_arr = a
    else:
        depart = max(prev_arr + 1, f - 4)
        if depart > prev_arr:
            keys.append((depart, prev_v, "linear"))
        keys.append((f + 2, v, EOUT)); prev_arr = f + 2
    prev_v = v
slide = dict(prev_v); slide["positionX"] -= 170
keys.append((f_cut - 1, slide, EOUT))
keys.append((f_cut - 0.5, cam_vals(960, 560, 1.0), "hold"))      # step between frames: no motion-blur double image
keys.append((b, cam_vals(960, 560, 1.04), EOUT))
cam_keys(g, keys)
plan_rows.append(("TC1", "Well, turns out, Nike NEEDED RETAIL more than anyone.", "Size-contrast build", "Blur-to-sharp",
                  "Flicker-in; camera follows each word (ease-out, motion blur); 3 retail stills pop in; slide right, hard cut wide", "Cut out", "centered"))

'''

BLOCK_TC3 = r'''# ================= 4c. TC3 in the WHAT HAPPENED style =================
(_, a, b) = SEG["TC3"]
g = scene_group("TC3 Text Centerpiece: and that was only HALF THE PROBLEM.", a, b)
L = WORDS[14]
S3 = fit_size("HALF THE PROBLEM.", "archivo", 190, 1640, {"wght": 880, "wdth": 80})
xs3, W3 = layout_line(["HALF", "THE", "PROBLEM."], [WH(S3)] * 3)
x0 = 960 - W3 / 2
y3 = 652
CONN3 = ("serif_italic", 104, None, 0)
pc, _ = row([L[i]["w"] for i in range(4)], [CONN3] * 4, 452, align="left", x_left=x0 + 6)
for i, (x, y) in zip(range(4), pc):
    lid = D.text(f"TC3 connector '{L[i]['w']}'", L[i]["w"], x, y, "serif_italic", 104, TEXT, wf(14, i, a), b, g); D.vox(lid, 104); D.ghost_to_solid(lid)
wh_word("TC3 KEY 'HALF'", "HALF", x0, y3, S3, GREEN, wf(14, 4, a), b, g, block=True)
wh_random("TC3 'THE'", "THE", x0 + xs3[1], y3, S3, lambda c: TEXT, wf(14, 5, a), b, g)
wh_random("TC3 'PROBLEM.'", "PROBLEM.", x0 + xs3[2], y3, S3, lambda c: GREEN if c == "." else TEXT, wf(14, 6, a), b, g)
plan_rows.append(("TC3", "and that was only HALF THE PROBLEM.", "Connector + keyword (TC2 style)", "Ghost-to-solid (connector)",
                  "Block-to-word (HALF), Random letter reveal (THE PROBLEM.)", "Cut out", "centered"))

'''

BLOCK_CLIPS = r'''# --- shared: year flash, alternating captions, TV captions ---
YR = 18     # frames the year owns the screen before any caption


def year_flash(text, f0, f1):
    """Hard on / hard off: a huge year over the dimmed shot (no entrance, no exit)."""
    gy = D.group(f"YEAR FLASH {text} (hard in / hard out)", 0, endcard_in)
    size = 470
    w = advance(text, *WH(size))
    D.text(f"year '{text}'", text, 960 - w / 2, 540 + 0.36 * size, "archivo", size, TEXT, f0, f1, gy, wght=880, wdth=80)
    D.rect(f"year flash dim ({text})", 0, 0, 1920, 1080, [BG[0], BG[1], BG[2], 0.80], f0, f1, gy)


def lr_captions(key, words, groups, slot_a, slot_b, maxw=520, xl=110, xr=1810, yc=520):
    """Reference-style captions placed beside the speaker: a left block, then a right block, then the next pair."""
    cg = D.group(f"SPECIAL CAPTIONS {key} (alternating left / right)", 0, endcard_in)
    soft_shadow(cg)
    starts = [max(slot_a, grid(cframe(key, words[g_[0]]["s"]))) for g_ in groups]
    for gi, (i0, i1, keys, side) in enumerate(groups):
        f1 = slot_b
        for gj in range(gi + 1, len(groups)):
            if groups[gj][3] == "L":
                f1 = starts[gj]; break
        ws = words[i0:i1]
        specs = []
        for j, w in enumerate(ws):
            if (i0 + j) in keys:
                specs.append(("serif", fit_size(w["w"], "serif", 156, maxw), None, 0))
            else:
                specs.append(REF_S)
        lines = [[]]
        for j in range(len(ws)):
            if lines[-1]:
                cand = layout_line([ws[k]["w"] for k in lines[-1]] + [ws[j]["w"]], [specs[k] for k in lines[-1]] + [specs[j]])[1]
                if cand > maxw:
                    lines.append([])
            lines[-1].append(j)
        hts = [max(specs[j][1] for j in ln) * 0.95 for ln in lines]
        top = yc - sum(hts) / 2
        for ln, h in zip(lines, hts):
            base = top + h * 0.78
            xs_, lw = layout_line([ws[j]["w"] for j in ln], [specs[j] for j in ln])
            x0 = xl if side == "L" else xr - lw
            for j, xo in zip(ln, xs_):
                sp, w = specs[j], ws[j]
                fw = min(max(starts[gi], grid(cframe(key, w["s"]))), f1 - 1)
                lid = D.text(f"lrcap {key} '{w['w']}'", w["w"], x0 + xo, base, sp[0], sp[1], GREEN if (i0 + j) in keys else TEXT, fw, f1, cg)
                D.blur_to_sharp(lid, 14 if sp is REF_S else 18)
                if (i0 + j) in keys:
                    D.vox(lid, sp[1])
            top += h


def tv_captions(key, words, groups, slot_a, slot_b, y=1012):
    """One centred line under the TV: hard start word by word, subtle glow, no drop shadow."""
    cg = D.group(f"SPECIAL CAPTIONS {key} (under the TV, hard start, subtle glow)", 0, endcard_in)
    D.effect(cg, {"type": "dropShadow", "enabled": True, "color": [0.93, 0.93, 0.93, 0.30], "offset": [0, 0], "blurRadius": 16,
                  "spreadRadius": 0, "blendMode": "normal"})
    SS, SB = ("serif_italic", 50, None, 0), ("serif", 100, None, 0)
    starts = [max(slot_a, grid(cframe(key, words[g_[0]]["s"]))) for g_ in groups]
    for gi, (i0, i1, keys) in enumerate(groups):
        f1 = starts[gi + 1] if gi + 1 < len(groups) else slot_b
        ws = words[i0:i1]
        specs = [SB if (i0 + j) in keys else SS for j in range(len(ws))]
        xs_, lw = layout_line([w["w"] for w in ws], specs)
        for j, w in enumerate(ws):
            fw = min(max(starts[gi], grid(cframe(key, w["s"]))), f1 - 1)
            D.text(f"tvcap {key} '{w['w']}'", w["w"], 960 - lw / 2 + xs_[j], y, specs[j][0], specs[j][1],
                   GREEN if (i0 + j) in keys else TEXT, fw, f1, cg)


# --- O'Leary: 2021 owns the screen, a quick flash on him, then captions beside him (left, right, ...) ---
key = "CLIP_OLEARY"
a, b = tl[key][0], SEG["A1_OLEARY"][2]
info = CLIPINFO[key]
src0 = round((CLIPS[key][2] - CLIPS[key][1]) / CLIPS[key][5] * 1000)
year_flash("2021", a, a + YR)
ow = clip_words(key)
lr_captions(key, ow, [(0, 3, {2}, "L"), (3, 7, {6}, "R"), (7, 10, {9}, "L"), (10, 13, {12}, "R"),
                      (13, 17, {15, 16}, "L"), (17, len(ow), {len(ow) - 2, len(ow) - 1}, "R")], a + YR, b)
gO = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gO, "name": "LIVE CLIP Kevin O'Leary (1.15x, full frame)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
OL_T = xf(pos=(1517, 853), scale=158)     # hides the CNBC chyron (y>770) and stock box (x>1230)
flicker(gO, "m_oleary", YR, 6, src0 + ms(YR), OL_T, FLICK_QUICK, "O'Leary", dur_ms=ms(YR + 6) - ms(YR))
vO = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vO, "name": "O'Leary video + own audio", "parentLayerId": gO,
       "activeRange": {"start": 0, "duration": ms(b) - ms(a)}, "sourceRange": {"start": src0, "duration": min(ms(b) - ms(a), info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": OL_T,
       "source": {"assetId": "oleary_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": CLIPS[key][4]})
end_rel = tl[key][1] - a
D.keys(vO, "volume", [(0, 0, "linear"), (2, CLIPS[key][4], "linear"), (end_rel, CLIPS[key][4], "linear"), (end_rel + 3, 0, "linear")])
ng = D.effect(vO, {"type": "grain", "amount": 0.22, "size": 1.6, "softness": 0.4, "aspectRatio": 1.0, "seed": 5})
D.effect_script(vO, ng, "seed", "return Math.floor(input.time.seconds * 24);")
zoom_transition(gO, b - a, base=100, t_in=False, t_out=True, push_to=104)
plan_rows.append(("CLIP_OLEARY", "2021 (hard) / This is WHY | you should be WORRIED | about the FUTURE | of a WALMART | or a FOOT LOCKER | They don't NEED RETAIL",
                  "Connector + keyword (reference style), alternating left / right", "Blur-to-sharp", "Blur-to-sharp + texture", "Cut out", "left / right of speaker"))

# --- Donahoe: 2024 owns the screen, then the clip plays inside a vintage TV (CRT look), captions under the TV ---
key = "CLIP_DONAHOE"
a, b = tl[key][0], SEG["A2_DONAHOE"][2]
info = CLIPINFO[key]
src0 = round((CLIPS[key][2] - CLIPS[key][1]) / CLIPS[key][5] * 1000)
year_flash("2024", a, a + YR)
dw = clip_words(key)
tv_captions(key, dw, [(0, 3, {2}), (3, 6, {5}), (6, 10, {8}), (10, len(dw), {len(dw) - 1})], a + YR, b)
gD = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gD, "name": "LIVE CLIP John Donahoe inside the TV (1.15x)",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
       "transform": {"anchorPoint": [922, 468], "position": [922, 468], "scale": [100, 100], "rotation": 0, "opacity": 100}})
tvdur = ms(b) - ms(a)
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "TV frame (supplied green-screen still, screen keyed out)",
       "parentLayerId": gD, "activeRange": {"start": 0, "duration": tvdur}, "transform": xf(pos=(0, 0), anchor=(0, 0)),
       "source": {"assetId": "tv_frame", "fit": "contain"}})
mask = D.nid()
D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": mask, "name": "TV screen matte", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": tvdur}, "transform": xf(pos=(0, 0), anchor=(0, 0)), "source": {"assetId": "tv_mask", "fit": "contain"}})
gS = D.nid()
D.add({"type": "createFxGroupLayer", "compositionId": C, "layerId": gS, "name": "TV screen content (CRT)", "parentLayerId": gD,
       "activeRange": {"start": 0, "duration": tvdur},
       "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
D.add({"type": "setFxLayerTrackMatte", "compositionId": C, "layerId": gS, "matteLayerId": mask, "mode": "alpha"})
vD = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": vD, "name": "Donahoe video + own audio", "parentLayerId": gS,
       "activeRange": {"start": 0, "duration": tvdur}, "sourceRange": {"start": src0, "duration": min(tvdur, info["durationMs"] - src0)},
       "sourceIntrinsicDuration": info["durationMs"], "transform": xf(pos=TV_POS, scale=TV_SCALE),
       "source": {"assetId": "donahoe_fast", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": CLIPS[key][4]})
D.rect("TV screen black", 0, 0, 1920, 1080, [0.02, 0.02, 0.02, 1], 0, b - a, gS)
end_rel = tl[key][1] - a
D.keys(vD, "volume", [(0, 0, "linear"), (2, CLIPS[key][4], "linear"), (end_rel, CLIPS[key][4], "linear"), (end_rel + 3, 0, "linear")])
D.effect(gS, {"type": "chromaticAberration", "amount": 4.0, "direction": 0})
D.effect(gS, {"type": "customShader", "name": "crtScanlines", "description": "CRT scanlines with a slow rolling band.",
              "wgsl": open(os.path.join(W, "shaders", "crt.wgsl")).read(),
              "params": [{"name": "animationTime", "description": "Engine clock (s).", "min": 0, "max": 3600, "default": 0},
                         {"name": "linePx", "description": "Scanline period in px.", "min": 1, "max": 20, "default": 3.0},
                         {"name": "strength", "description": "Scanline darkness 0..1.", "min": 0, "max": 1, "default": 0.38},
                         {"name": "roll", "description": "Rolling band speed (screens/s).", "min": 0, "max": 2, "default": 0.35}]})
ng = D.effect(gS, {"type": "grain", "amount": 0.30, "size": 1.4, "softness": 0.3, "aspectRatio": 1.0, "seed": 6})
D.effect_script(gS, ng, "seed", "return Math.floor(input.time.seconds * 24);")
D.effect(gS, {"type": "glow", "glowThreshold": 60, "glowRadius": 14, "glowIntensity": 0.5})
D.effect(gD, {"type": "vignette", "amount": 0.55, "feather": 0.6, "radius": 0.75})
ng2 = D.effect(gD, {"type": "grain", "amount": 0.12, "size": 1.5, "softness": 0.5, "aspectRatio": 1.0, "seed": 9})
D.effect_script(gD, ng2, "seed", "return Math.floor(input.time.seconds * 24);")
zk = [(0, 100, "linear"), (b - a, 118, EASE)]
kk(gD, "scaleX", zk); kk(gD, "scaleY", zk)
plan_rows.append(("CLIP_DONAHOE", "2024 (hard) / we had OVER-ROTATED / away from WHOLESALE / a little MORE than / we INTENDED",
                  "Connector + keyword (reference style), one line under the TV", "Hard start", "Hard start + subtle glow", "Cut out", "under the TV"))

# --- Hill: WHAT HAPPENED style quote, big photo + title, camera follows each element (ease-out, motion blur) ---
key = "CLIP_HILL"
a = tl[key][0]; b = SEG["TC4_HILL"][2]
g = D.group("TC4 Hill quote (camera follows: photo, WE LOST OUR, OBSESSION, wide)", 0, endcard_in)
hw = [w for w in CW["hill"] if CLIPS[key][2] - 0.1 <= w["s"] < CLIPS[key][3]]
fr = [max(a, grid(cframe(key, w["s"]))) for w in hw]
ph = D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": D.nid(), "name": "Hill photo (B60 still, large)", "parentLayerId": g,
            "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)},
            "transform": {"anchorPoint": [0, 0], "position": [190, 190], "scale": [82, 82], "rotation": 0, "opacity": 100},
            "source": {"assetId": "hill_photo", "fit": "contain"}})
D.blur_to_sharp(ph["layerId"], 14)
D.effect(ph["layerId"], {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.5], "offset": [0, 10], "blurRadius": 30, "spreadRadius": 0, "blendMode": "normal"})
wh_word("Hill title 'ELLIOTT HILL'", "ELLIOTT HILL", 192, 812, 78, TEXT, a + STEP, b, g)
t2 = D.text("Hill title 'NIKE CEO'", "NIKE CEO", 196, 866, "archivo", 36, GREEN, a + 2 * STEP, b, g, wght=600, tracking=80); D.blur_to_sharp(t2)
q = D.text("Hill quote mark", "“", 812, 488, "serif", 240, GREEN, a, b, g); D.vox(q, 240); D.ghost_to_solid(q)
QX, Q1, Q2, Q3 = 900, 470, 684, 792
xsq, Wq1 = layout_line([w["w"].upper() for w in hw[0:3]], [WH(96)] * 3)
for j, w in enumerate(hw[0:3]):
    wh_word(f"Hill '{w['w'].upper()}'", w["w"].upper(), QX + xsq[j], Q1, 96, TEXT, fr[j], b, g)
SO = fit_size("OBSESSION", "archivo", 210, 860, {"wght": 880, "wdth": 80})
WO = advance("OBSESSION", *WH(SO))
wh_word("Hill KEY 'OBSESSION'", "OBSESSION", QX - 6, Q2, SO, GREEN, fr[3], b, g, block=True)
last = hw[5]["w"].upper().rstrip(".") + ".”"
xsq3, Wq3 = layout_line([hw[4]["w"].upper(), last], [WH(96)] * 2)
for j, (w, s_) in enumerate(zip(hw[4:6], (hw[4]["w"].upper(), last))):
    wh_word(f"Hill '{s_}'", s_, QX + xsq3[j], Q3, 96, TEXT, fr[4 + j], b, g)
cam_keys(g, [(a, cam_vals(452, 452, 1.55), "linear"),
             (a + 5, cam_vals(452, 452, 1.55), "linear"),
             (a + 11, cam_vals(QX + Wq1 / 2, Q1 - 35, 1.6), EOUT),
             (max(a + 12, fr[3] - 3), cam_vals(QX + Wq1 / 2, Q1 - 35, 1.6), "linear"),
             (max(a + 13, fr[3] + 3), cam_vals(QX + WO / 2, Q2 - 0.36 * SO, 1.3), EOUT),
             (max(a + 14, fr[4] - 2), cam_vals(QX + WO / 2, Q2 - 0.36 * SO, 1.3), "linear"),
             (max(a + 15, fr[4] + 5), cam_vals(960, 530, 1.0), EOUT),
             (b, cam_vals(960, 530, 1.03), EOUT)])
D.add({"type": "createFxAudioLayer", "compositionId": C, "layerId": D.nid(), "name": "LIVE AUDIO Elliott Hill (earnings call)",
       "activeRange": {"start": ms(a), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceRange": {"start": round((CLIPS[key][2] - CLIPS[key][1]) * 1000), "duration": ms(tl[key][1]) - ms(a) + 60},
       "sourceIntrinsicDuration": 2800, "source": {"assetId": "hill_audio"}, "volume": CLIPS[key][4]})
plan_rows.append(("TC4", "“WE LOST OUR OBSESSION WITH SPORT.” + photo, ELLIOTT HILL / NIKE CEO", "Connector + keyword (TC2 style)",
                  "Blur-to-sharp", "Block-to-word (OBSESSION); camera follows each element", "Cut out", "photo left, quote right"))

'''

BLOCK_FC2 = r'''# ================= 4g. FC2: the supplied MG (retail pop-up) + text placed in its empty space =================
(_, a, b) = SEG["FC2"]
mg_start = tl[10][0] - 27          # DSW lands on "DSW", Dillard's on "Dillard's", Foot Locker on "Foot Locker"
sg = D.group("FC2 MG TEXT (placed next to what the MG is showing)", 0, endcard_in)
soft_shadow(sg)
# (line, word indices, x, baseline y, size, key word indices, align, max width)
PH = [(9, [0, 1], 960, 600, 150, {1}, "center", 1400),
      (9, [2, 3], 1110, 470, 120, set(), "left", 720),
      (9, [4, 5], 1110, 610, 120, {5}, "left", 720),
      (10, [0, 1, 2], 90, 200, 104, set(), "left", 790),
      (10, [3, 4, 5], 90, 200, 104, set(), "left", 610),
      (10, [6], 450, 235, 140, {6}, "center", 500),
      (10, [7, 8], 1000, 108, 88, {8}, "center", 640),
      (10, [9, 10, 11], 1840, 285, 84, {11}, "right", 600),
      (10, [12, 13, 14], 1840, 285, 84, {13, 14}, "right", 620)]
ph_starts = [max(a, wf(ln, ix[0])) for (ln, ix, *_r) in PH]
for k, (ln, ix, x, y, size, keys, align, maxw) in enumerate(PH):
    f1 = b if k == len(PH) - 1 else (ph_starts[k + 2] if k == 1 else ph_starts[k + 1])
    ws = [WORDS[ln][i]["w"].upper() for i in ix]
    size = fit_size(" ".join(ws), "archivo", size, maxw, {"wght": 880, "wdth": 80})
    xs_, lw = layout_line(ws, [WH(size)] * len(ws))
    x0 = {"left": x, "center": x - lw / 2, "right": x - lw}[align]
    for j, i in enumerate(ix):
        fw = min(max(ph_starts[k], wf(ln, i)), f1 - 1)
        wh_word(f"FC2 '{ws[j]}'", ws[j], x0 + xs_[j], y, size, GREEN if i in keys else TEXT, fw, f1, sg, block=i in keys)
mgi = MGINFO
lid = D.nid()
D.add({"type": "createFxVideoLayer", "compositionId": C, "layerId": lid, "name": "FC2 MG: retail pop-up (supplied); holds its empty first frame",
       "activeRange": {"start": ms(a), "duration": ms(b) - ms(a)}, "sourceRange": {"start": 0, "duration": mgi["durationMs"]},
       "sourceIntrinsicDuration": mgi["durationMs"], "transform": xf(),
       "source": {"assetId": "mg_retail", "fit": "cover", "sourceRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}}, "volume": 0.0})
D.add({"type": "setFxLayerTimeRemap", "compositionId": C, "layerId": lid, "timeRemap": {
    "keyframes": [{"id": "mg-a", "time": ms(a), "value": 0, "easing": {"type": "linear"}},
                  {"id": "mg-b", "time": ms(mg_start), "value": 0, "easing": {"type": "linear"}},
                  {"id": "mg-c", "time": ms(b), "value": min(mgi["durationMs"] - 34, ms(b) - ms(mg_start)), "easing": {"type": "linear"}}],
    "before": "inactive", "after": "inactive"}})
plan_rows.append(("FC2", "HIS PLAN? / CUT OUT / THE MIDDLEMAN. / NIKE PULLED OUT / OF STORES LIKE / DSW / AND DILLARD'S, / AND SENT LESS / TO FOOT LOCKER.",
                  "Caption line (special, TC2 style), placed in the MG's empty space", "Blur-to-sharp", "Block-to-word", "Cut out", "context dependent"))

# ================= 4h. JOHN / DONAHOE (left, TC2 style) with a quick flash on him =================
shj = [x for x in shots if x["clip"] == "B21" and x["src"] == 17.0][0]
gj = D.group("SPECIAL TEXT: JOHN / DONAHOE", 0, endcard_in)
soft_shadow(gj)
SJ = fit_size("DONAHOE.", "archivo", 210, 640, {"wght": 880, "wdth": 80})
wh_word("JOHN", "JOHN", 130, 500, SJ, TEXT, max(shj["start"], wf(8, 6)), shj["end"], gj, block=True)
wh_random("DONAHOE.", "DONAHOE.", 130, 500 + 0.84 * SJ, SJ, lambda c: GREEN if c == "." else TEXT, max(shj["start"], wf(8, 7)), shj["end"], gj)

'''
