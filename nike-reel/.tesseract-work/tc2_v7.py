# ================= 4b. TC2: camera follows So / WHAT / HAPPENED? (ease-out, motion blur), slides right, hard cut wide =================
(_, a, b) = SEG["TC2"]
L = WORDS[7]
BIG2 = ("archivo", 196, {"wght": 880, "wdth": 80}, 0)
xs, Wd = layout_line(["WHAT", "HAPPENED?"], [BIG2, BIG2])
x0 = 960 - Wd / 2
y2 = 652
fs, fw, fh = wf(7, 0, a), wf(7, 1, a), wf(7, 2, a)
wW = advance("WHAT", *BIG2)
xh = x0 + xs[1]
letters = list("HAPPENED?")
order = list(range(len(letters))); random.shuffle(order)
f_cut2 = min(b - 6, fh + 3 * STEP + 2)


def tc2_build(g, lo, hi, tag):
    if fs < hi:
        lid = D.text(f"TC2{tag} connector 'So'", "So", x0 + 6, 452, "serif_italic", 120, TEXT, max(fs, lo), hi, g); D.vox(lid, 120)
        if fs >= lo:
            D.ghost_to_solid(lid)
    if fw < hi:
        if fw >= lo:
            D.rect(f"TC2{tag} Block-to-word block (WHAT)", x0, y2 - 142, wW, 146, GREEN, fw, min(fw + STEP, hi), g)
        if fw + STEP < hi:
            lid = D.text(f"TC2{tag} KEY 'WHAT'", "WHAT", x0, y2, "archivo", 196, TEXT, max(fw + STEP, lo), hi, g, wght=880, wdth=80); D.vox(lid, 196)
    for n_, li in enumerate(order):
        f0 = fh + ((n_ * 3) // len(letters)) * STEP
        if f0 >= hi:
            continue
        pre = "".join(letters[:li])
        lx = xh + advance(pre, *BIG2) if pre else xh
        lid = D.text(f"TC2{tag} KEY letter '{letters[li]}'", letters[li], lx, y2, "archivo", 196, GREEN if letters[li] == "?" else TEXT,
                     max(f0, lo), hi, g, wght=880, wdth=80)
        D.vox(lid, 196)


gA = D.group("TC2 A: zoomed camera follows So / WHAT / HAPPENED?", 0, f_cut2)
tc2_build(gA, 0, f_cut2, "A")
v_so = cam_vals(x0 + 60, 410, 2.3)
v_what = cam_vals(x0 + wW / 2, y2 - 72, 1.7)
v_hap = cam_vals(xh + (Wd - xs[1]) / 2, y2 - 72, 1.45)
slide = dict(v_hap); slide["positionX"] -= 150
cam_keys(gA, [(a, v_so, "linear"), (max(a + 1, fw - 3), v_so, "linear"), (fw + 2, v_what, EOUT),
              (max(fw + 3, fh - 3), v_what, "linear"), (fh + 2, v_hap, EOUT), (f_cut2, slide, EOUT)])
gB = D.group("TC2 B: hard cut to the wide lockup", 0, b)
tc2_build(gB, f_cut2, b, "B")
cam_keys(gB, [(f_cut2, cam_vals(960, 560, 1.0), "linear"), (b, cam_vals(960, 560, 1.04), EOUT)])
plan_rows.append(("TC2", "So WHAT HAPPENED?", "Connector + keyword", "Ghost-to-solid (So)",
                  "Block-to-word (WHAT), Random letter reveal (HAPPENED?); camera follows each word, slides right, hard cut wide", "Cut out", "centered"))

