#!/usr/bin/env python3
"""B4 v05: the Race'n'Chase Game Design title page, restyled DARK (REVISION_v05 U4, client v03 #12 "dark aesthetic": the
page stays the dark inverted page, full frame, on a dark textured ground, not flat black; the doc's off-white paper is
not followed), as a reusable still for B4 and B15 (B15 flashes the same title page for 10 frames).

  python3 hyperframes/b04-racenchase/prep/race_page.py

Source: R4.5, page 1 of 04_Broll/B04/R4.5__source_grand-theft-auto-design-doc-1995.pdf (the plan's scan, embedded as a
699 x 1024 JPEG, 93 ppi; the 1700 x 2200 PNGs in 04_Broll/B04 are renders of the same JPEG). The light original is used,
then inverted like the v03 page (light type on dark paper), but rebuilt from the scan instead of a plain inversion:
  1. the native scan, Lanczos x3 -> 2097 x 3072 (page px below are in this size)
  2. levels on the luminance: the paper, its crinkles and the mirrored show-through of the next page (>= ~215) go to
     paper, the type (<= ~70) to full ink; a light unsharp mask on the ink. ink = 1 - levels. The show-through is kept
     as a faint ghost (GHOST x its own density), as the v03 inverted page shows it, so the sheet reads as real paper
  3. a dark charcoal "paper" (#17171A, not flat black) with seeded low-frequency mottling + fine tooth + faint fibres
     (numpy RNG, seed 1995: identical on every run) plus the scan's own large-scale fold shading
  4. ink (#ECE8E1, warm off-white) composited over the dark paper with the ink as alpha
Outputs (05_GFX/shared/, copied to the beat's assets/page/):
  racenchase_title_page_dark_v05.jpg      the restyled dark page, 2097 x 3072, no tilt (tilt / push / highlights per beat)
  racenchase_title_page_dark_v05_ink.png  the type alone (RGBA, #ECE8E1 + alpha) to re-composite on another ground
  racenchase_title_page_dark_v05.json     where the title, the date, etc. sit in page px (for highlights / annotations)
"""
import json, os, shutil, subprocess
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
PDF = f"{ROOT}/04_Broll/B04/R4.5__source_grand-theft-auto-design-doc-1995.pdf"
SHARED = f"{ROOT}/05_GFX/shared"
BEAT = f"{ROOT}/hyperframes/b04-racenchase/assets/page"
TMP = "/tmp/claude-0/-home-user-claude-test-2-0-/525be23d-0b2a-556a-b90e-c2688dc886ec/scratchpad/b04/pdfimg"
K = 3
PAPER = np.array([23, 23, 26], np.float64)         # dark charcoal paper (not flat black)
INK = np.array([236, 232, 225], np.float64)        # warm off-white type
GHOST = 0.16                                       # faint show-through of the next page (v03 inverted look)
NAME = "racenchase_title_page_dark_v05"
BLACK_PT, WHITE_PT, GAMMA = 70.0, 212.0, 0.9
# native-scan boxes (x0, y0, x1, y1), measured on the 699 x 1024 JPEG (dark pixels < 90)
NATIVE = {"title_box": (89, 116, 639, 172), "race_n_chase": (306, 123, 422, 138), "game_design": (303, 150, 423, 165),
          "version": (333, 212, 396, 220), "march_22_1995": (325, 229, 403, 237), "copyright": (299, 281, 428, 289)}


def native_scan():
    os.makedirs(TMP, exist_ok=True)
    subprocess.run(["pdfimages", "-f", "1", "-l", "1", "-j", PDF, f"{TMP}/p1"], check=True)
    return Image.open(f"{TMP}/p1-000.jpg").convert("RGB")


def smooth_noise(rng, h, w, sigma):
    n = ndi.gaussian_filter(rng.standard_normal((h, w)), sigma)
    return n / (n.std() + 1e-9)


def main():
    src = native_scan()
    W, H = src.width * K, src.height * K
    big = src.resize((W, H), Image.LANCZOS)
    lum = np.asarray(big.convert("L")).astype(np.float64)
    lv = np.clip((lum - BLACK_PT) / (WHITE_PT - BLACK_PT), 0, 1) ** GAMMA
    ink = 1.0 - lv
    ink_img = Image.fromarray(np.round(ink * 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    ink = np.asarray(ink_img).astype(np.float64) / 255.0
    ink[ink < 0.04] = 0.0                                                # no speckle left from the show-through
    # the show-through (mirrored next page, luminance ~150-235 in the scan) as a faint ghost, like the v03 inverted page
    ghost = np.clip((236.0 - ndi.gaussian_filter(lum, 1.2)) / 70.0, 0, 1) * (1 - ink)
    ghost[ghost < 0.08] = 0.0
    rng = np.random.default_rng(1995)
    mottle = 0.10 * smooth_noise(rng, H, W, 90) + 0.05 * smooth_noise(rng, H, W, 25)
    tooth = 0.05 * smooth_noise(rng, H, W, 0.9)
    fib = np.zeros((H, W))
    for _ in range(420):                                                # faint short fibres
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ang, ln = rng.uniform(0, np.pi), rng.uniform(20, 90)
        t = np.linspace(0, 1, int(ln))
        xs = np.clip((x + np.cos(ang) * ln * t).astype(int), 0, W - 1)
        ys = np.clip((y + np.sin(ang) * ln * t + 6 * np.sin(t * 3)).astype(int), 0, H - 1)
        fib[ys, xs] += rng.choice([-1, 1]) * rng.uniform(0.4, 1.0)
    fib = ndi.gaussian_filter(fib, 0.7) * 0.25
    folds = ndi.gaussian_filter(lum, 36)
    folds = -1.2 * (folds - np.median(folds)) / 255.0                  # inverted: the scan's darker folds read lighter
    shade = 1.0 + mottle + tooth + fib + folds
    paper = np.clip(PAPER[None, None, :] * shade[..., None], 0, 255)
    paper = paper + (INK - paper) * (GHOST * ghost)[..., None]
    out = paper * (1 - ink[..., None]) + INK[None, None, :] * ink[..., None]
    os.makedirs(SHARED, exist_ok=True)
    page = f"{SHARED}/{NAME}.jpg"
    Image.fromarray(np.round(out).astype(np.uint8)).save(page, quality=90, subsampling=0, optimize=True)
    rgba = np.dstack([np.broadcast_to(INK.astype(np.uint8), (H, W, 3)), np.round(ink * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(f"{SHARED}/{NAME}_ink.png", optimize=True)
    boxes = {k: [v[0] * K, v[1] * K, (v[2] + 1) * K, (v[3] + 1) * K] for k, v in NATIVE.items()}
    meta = {"what": "Race'n'Chase Game Design v1.05 title page (c) 1995 DMA Design Ltd, dark (inverted) page on a dark textured ground",
            "source": "04_Broll/B04/R4.5__source_grand-theft-auto-design-doc-1995.pdf page 1 (embedded 699x1024 JPEG)",
            "size": [W, H], "scale_from_native": K, "boxes_page_px_x0y0x1y1": boxes,
            "paper": "#17171A", "ink": "#ECE8E1", "ghost": GHOST, "levels": [BLACK_PT, WHITE_PT, GAMMA], "seed": 1995,
            "recipe": "hyperframes/b04-racenchase/prep/race_page.py",
            "use": "B4 (full frame, tilt -4 deg, push 100 -> 115%) and B15 (10-frame split-screen flash of the same page)"}
    json.dump(meta, open(f"{SHARED}/{NAME}.json", "w"), indent=1)
    os.makedirs(BEAT, exist_ok=True)
    for f in (NAME + ".jpg", NAME + ".json"):
        shutil.copy2(f"{SHARED}/{f}", f"{BEAT}/{f}")
    print(json.dumps(boxes), os.path.getsize(page) // 1024, "KB")


if __name__ == "__main__":
    main()
