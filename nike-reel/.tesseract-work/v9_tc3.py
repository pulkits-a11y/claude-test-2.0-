# ================= 4c. TC3 (TC2 style) with the TC2 camera: follow each word, slide right zoomed in, hard cut wide =================
(_, a, b) = SEG["TC3"]
L = WORDS[14]
S3 = fit_size("HALF THE PROBLEM.", "archivo", 190, 1640, {"wght": 880, "wdth": 80})
xs3, W3 = layout_line(["HALF", "THE", "PROBLEM."], [WH(S3)] * 3)
x03 = 960 - W3 / 2
y3 = 652
CONN3 = ("serif_italic", 104, None, 0)
pc3, Wc3 = row([L[i]["w"] for i in range(4)], [CONN3] * 4, 452, align="left", x_left=x03 + 6)
f_half, f_the, f_prob = wf(14, 4, a), wf(14, 5, a), wf(14, 6, a)
f_cut3 = min(b - 6, f_prob + 3 * STEP + 2)


def tc3_build(g, lo, hi, tag):
    for i, (x, y) in zip(range(4), pc3):
        f0 = wf(14, i, a)
        if f0 >= hi:
            continue
        lid = D.text(f"TC3{tag} connector '{L[i]['w']}'", L[i]["w"], x, y, "serif_italic", 104, TEXT, max(f0, lo), hi, g); D.vox(lid, 104)
        if f0 >= lo:
            D.ghost_to_solid(lid)
    if f_half < hi:
        wh_word(f"TC3{tag} KEY 'HALF'", "HALF", x03, y3, S3, GREEN, max(f_half, lo), hi, g, block=f_half >= lo)
    if f_the < hi:
        wh_random(f"TC3{tag} 'THE'", "THE", x03 + xs3[1], y3, S3, lambda c: TEXT, max(f_the, lo), hi, g)
    if f_prob < hi:
        wh_random(f"TC3{tag} 'PROBLEM.'", "PROBLEM.", x03 + xs3[2], y3, S3, lambda c: GREEN if c == "." else TEXT, max(f_prob, lo), hi, g)


gA3 = D.group("TC3 A: zoomed camera follows and that was only / HALF / THE PROBLEM.", 0, f_cut3)
tc3_build(gA3, 0, f_cut3, "A")
v_c = cam_vals(x03 + 6 + Wc3 / 2, 420, 2.0)
v_h = cam_vals(x03 + advance("HALF", *WH(S3)) / 2, y3 - 0.36 * S3, 1.8)
v_p = cam_vals(x03 + xs3[2] + advance("PROBLEM.", *WH(S3)) / 2, y3 - 0.36 * S3, 1.45)
sl3 = dict(v_p); sl3["positionX"] -= 150
cam_keys(gA3, [(a, v_c, "linear"), (max(a + 1, f_half - 3), v_c, "linear"), (f_half + 2, v_h, EOUT),
               (max(f_half + 3, f_prob - 3), v_h, "linear"), (f_prob + 2, v_p, EOUT), (f_cut3, sl3, EOUT)])
gB3 = D.group("TC3 B: hard cut to the wide lockup", 0, b)
tc3_build(gB3, f_cut3, b, "B")
cam_keys(gB3, [(f_cut3, cam_vals(960, 560, 1.0), "linear"), (b, cam_vals(960, 560, 1.04), EOUT)])
plan_rows.append(("TC3", "and that was only HALF THE PROBLEM.", "Connector + keyword (TC2 style)", "Ghost-to-solid (connector)",
                  "Block-to-word (HALF), Random letter reveal; camera follows each word, slides right, hard cut wide", "Cut out", "centered"))

