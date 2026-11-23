# ================= 3b. B-roll captions in the 'shelf / hype / athlete' style (small connectors above a big serif keyword) =================
# (line, connector word indices, keyword word indices) - every keyword gets the green block-to-word, groups hard-cut
HC_GROUPS = {11: [([], [0]), ([1, 2, 3], [4])],
             12: [([0], [1]), ([2, 3, 4], [5]), ([6, 7], [8]), ([9], [10]), ([11, 12], [13, 14, 15])],
             13: [([0, 1, 2], [3]), ("LOGOS", [4, 5, 6]), ([7, 8, 9], [10])],
             15: [([0, 1], [2]), ([3], [4]), ([5, 6, 7], [8])],
             19: [([0, 1, 2, 3], [4]), ([5, 6], [7])],
             20: [([0], [1]), ([2, 3], [4])],
             21: [([0], [1]), ([], [2, 3]), ([4, 5], [6])],
             22: [([0], [1]), ([2, 3], [4])],
             26: [([0, 1, 2, 3], [4, 5])]}
HCONN = ("archivo", 50, {"wght": 520, "wdth": 100}, 0)
HYC, HYK = 418, 642
hcg = D.group("B-ROLL CAPTIONS ('shelf / hype / athlete' style)", 0, endcard_in)
D.effect(hcg, {"type": "dropShadow", "enabled": True, "color": [0, 0, 0, 0.6], "offset": [0, 0], "blurRadius": 46, "spreadRadius": 10, "blendMode": "normal"})
hc_items = []
for ln, groups in HC_GROUPS.items():
    for conn, kws in groups:
        idx = (kws if conn == "LOGOS" else conn + kws)
        hc_items.append((wfc(ln, min(idx), floor=seg_start_of(ln)), ln, conn, kws))
hc_items.sort()
for k, (g0, ln, conn, kws) in enumerate(hc_items):
    g1 = min(hc_items[k + 1][0] if k + 1 < len(hc_items) else endcard_in, seg_end_of(ln))
    if g1 <= g0:
        continue
    W_ = WORDS[ln]
    if conn == "LOGOS":       # alo  and  vuori - the logos are the keyword (block-to-word on each logo)
        from PIL import Image as _P
        szl = {k_: _P.open(os.path.join(R, "Sources", "logos", f_)).size for k_, f_ in (("logo_alo", "alo_logo.png"), ("logo_vuori", "vuori_logo.png"))}
        HL = {"logo_alo": 150, "logo_vuori": 92}
        seq = [("logo_alo", HL["logo_alo"] * szl["logo_alo"][0] / szl["logo_alo"][1]), ("and", advance("and", *HCONN)),
               ("logo_vuori", HL["logo_vuori"] * szl["logo_vuori"][0] / szl["logo_vuori"][1])]
        gap = 34
        x = 960 - (sum(wv for _, wv in seq) + 2 * gap) / 2
        base = HYK - 20
        for (val, wv), fr_i in zip(seq, kws):
            fw = min(max(g0, wfc(ln, fr_i)), g1 - 1)
            if val == "and":
                lid = D.text("HC cap 'and'", "and", x, base, "archivo", 50, TEXT, fw, g1, hcg, wght=520); D.blur_to_sharp(lid)
            else:
                hh = HL[val]
                D.rect(f"HC block ({val})", x - 6, base - hh - 8, wv + 12, hh + 16, GREEN, fw, min(fw + STEP, g1), hcg)
                f2 = min(fw + STEP, g1 - 1)
                img = D.nid()
                D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": img, "name": f"HC logo {val}", "parentLayerId": hcg,
                       "activeRange": {"start": ms(f2), "duration": ms(g1) - ms(f2)},
                       "transform": {"anchorPoint": [0, 0], "position": [x, base - hh], "rotation": 0, "opacity": 100,
                                     "scale": [round(100 * wv / szl[val][0], 3)] * 2},
                       "source": {"assetId": val, "fit": "contain"}})
            x += wv + gap
        cap_rows.extend((ln, i, W_[i]["w"], 0, "HC style (logos)") for i in kws)
        continue
    cws = [W_[i]["w"] for i in conn]
    kw_words = [W_[i]["w"] for i in kws]
    ksz = fit_size(" ".join(kw_words), "serif", 262, 1500)
    KWS = ("serif", ksz, None, 0)
    kxs, kwid = layout_line(kw_words, [KWS] * len(kw_words))
    cxs, cwid = layout_line(cws, [HCONN] * len(cws)) if cws else ([], 0)
    xl = 960 - max(cwid, kwid) / 2
    for i, xo in zip(conn, cxs):
        fw = min(max(g0, wfc(ln, i)), g1 - 1)
        lid = D.text(f"HC connector '{W_[i]['w']}'", W_[i]["w"], xl + xo, HYC, "archivo", 50, TEXT, fw, g1, hcg, wght=520); D.blur_to_sharp(lid)
    for j, (i, xo) in enumerate(zip(kws, kxs)):
        fw = min(max(g0, wfc(ln, i)), g1 - 1)
        ww = advance(W_[i]["w"], *KWS)
        if j == 0:
            D.rect(f"HC block-to-word ({W_[i]['w']})", xl + xo - 2, HYK - 0.65 * ksz, ww + 12, 0.672 * ksz, GREEN, fw, min(fw + STEP, g1), hcg)
        lid = D.text(f"HC KEY '{W_[i]['w']}'", W_[i]["w"], xl + xo, HYK, "serif", ksz, GREEN, min(fw + (STEP if j == 0 else 0), g1 - 1), g1, hcg)
        D.vox(lid, ksz)
    cap_rows.extend((ln, i, W_[i]["w"], 0, "HC style") for i in (list(conn) + list(kws)))

