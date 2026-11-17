#!/usr/bin/env python3
"""B3 v05 [DEPTH] "Dundee," behind the Law's ridge line: the plate and the hill cut-out.

  python3 hyperframes/b03-dundee/prep/dundee_depth.py [--preview DIR]

Source: R3.1 "Old Dundee In Colour" [n7QORDefzIE], the "La Hull from Hawkhill" slide (a still colour photograph the
upload shows for 20.2-25.1 s with a slow zoom of its own). One frame at 21.6 s (v04's in-point) is the plate: the shot
is a photograph, so HyperFrames pushes the still itself (100 -> 108 %) and the plate and the cut-out stay pixel-aligned
(one image, two layers, the same push on both).

* Plate: crop 640:360:40:0 of the 854x478 upload (16:9, the burned-in caption "La Hull from Hawkhill" at source
  y 365-398 stays out; the v04 crop), BT.709 -> RGB, Lanczos x3 -> 1920x1080. assets/footage/R3.1_plate.jpg
* Cut-out (foreground = everything that is not sky): a colour key of the overcast sky. The sky is a smooth, nearly
  neutral grey gradient; it is modelled by a 2nd-order polynomial in (x, y) fitted to the sky pixels (iterated: fit ->
  keep pixels close to the model -> refit), then every pixel's distance to the model (CIE Lab, chroma weighted x1.5)
  gives a soft alpha (D <= T0 sky, D >= T1 foreground, smoothstep between). Only the sky region connected to the top
  edge counts as sky (dark roofs further down that match the sky colour stay opaque), holes are filled, and the alpha
  is kept soft only within 6 px of the sky boundary. Saved as RGBA with the plate's own pixels (straight alpha), cropped
  to the band the word can occupy: assets/footage/R3.1_hill_cutout.png placed at CUT_BOX in the plate's coordinates.
Deterministic (no randomness). Needs ffmpeg, numpy, PIL, scipy.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
PROJ = f"{ROOT}/hyperframes/b03-dundee"
SRC = f"{ROOT}/04_Broll/_originals/B03/R3.1__Old Dundee In Colour [n7QORDefzIE].mp4"
T_SRC = 21.6                      # s in the original upload
CROP = (640, 360, 40, 0)          # w, h, x, y in the upload's pixels (v04's crop)
W, H = 1920, 1080
CUT_BOX = (240, 60, 1440, 600)    # x, y, w, h of the saved cut-out, plate pixels (covers every place the word can sit)
T0, T1 = 7.0, 17.0                # Lab distance: <= T0 sky, >= T1 foreground
EDGE_PX = 6                       # soft alpha only this close to the sky boundary


def plate():
    w, h, x, y = CROP
    vf = (f"crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int:"
          f"in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24")
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", str(T_SRC), "-i", SRC, "-frames:v", "1",
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)


def srgb_to_lab(rgb):
    c = rgb.astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1)


def poly_terms(xx, yy):
    return np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], -1)


def key(img):
    lab = srgb_to_lab(img)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    xn, yn = xx / W, yy / H
    # seed: the top band is sky everywhere (the Law's monument tip is the highest foreground point, ~y 250)
    seed = np.zeros((H, W), bool)
    seed[0:200, :] = True
    sel = seed.copy()
    for _ in range(4):
        A = poly_terms(xn[sel], yn[sel])
        coef = np.linalg.lstsq(A, lab[sel], rcond=None)[0]
        model = poly_terms(xn, yn) @ coef
        d = lab - model
        D = np.sqrt(d[..., 0] ** 2 + (1.5 * d[..., 1]) ** 2 + (1.5 * d[..., 2]) ** 2)
        sel = (D < T0) & (yy < 520)
    soft = np.clip((D - T0) / (T1 - T0), 0, 1)
    soft = soft * soft * (3 - 2 * soft)                       # smoothstep
    # sky = the near-sky region connected to the top edge (hard), holes in the foreground filled
    near = D < (T0 + T1) / 2
    lab_cc, _ = ndi.label(near)
    top_ids = np.unique(lab_cc[0, :])
    sky = np.isin(lab_cc, top_ids[top_ids > 0])
    # foreground = what is not that sky, and only the parts connected to the bottom edge (no floating specks in the
    # sky); a dark roof matching the sky colour further down is not connected to the top, so it stays foreground
    fg_cc, _ = ndi.label(~sky)
    bot_ids = np.unique(fg_cc[-1, :])
    fg_hard = np.isin(fg_cc, bot_ids[bot_ids > 0])
    # distance of every pixel to the sky/foreground boundary (inside the foreground: to the nearest sky pixel; in the
    # sky: to the nearest foreground pixel)
    dist_to_edge = np.where(fg_hard, ndi.distance_transform_edt(fg_hard), ndi.distance_transform_edt(~fg_hard))
    alpha = np.where(dist_to_edge <= EDGE_PX, soft, fg_hard.astype(np.float64))
    return np.clip(alpha, 0, 1), D, sky, coef


def sky_rgb(img, sky):
    """The sky's own colour at every pixel (RGB polynomial fitted to the hard sky region), for decontaminating edges."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    xn, yn = xx / W, yy / H
    sel = sky & (yy < 520)
    coef = np.linalg.lstsq(poly_terms(xn[sel], yn[sel]), img[sel].astype(np.float64), rcond=None)[0]
    return poly_terms(xn, yn) @ coef


def main():
    prev_dir = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    img = plate()
    alpha, D, sky, _ = key(img)
    out = f"{PROJ}/assets/footage"
    os.makedirs(out, exist_ok=True)
    Image.fromarray(img).save(f"{out}/R3.1_plate.jpg", quality=93, subsampling=0, optimize=True)
    # edge decontamination: a semi-transparent edge pixel is foreground mixed with sky; take the sky out
    # (C = a F + (1 - a) S  ->  F = (C - (1 - a) S) / a), so no grey sky halo shows over the word behind the ridge
    S = sky_rgb(img, sky)
    a3 = alpha[..., None]
    fg_rgb = np.where(a3 > 0.02, (img - (1 - a3) * S) / np.maximum(a3, 0.02), img)
    fg_rgb = np.where((a3 > 0) & (a3 < 1), np.clip(fg_rgb, 0, 255), img).round().astype(np.uint8)
    x, y, w, h = CUT_BOX
    rgba = np.dstack([fg_rgb, np.round(alpha * 255).astype(np.uint8)])[y:y + h, x:x + w]
    Image.fromarray(rgba, "RGBA").save(f"{out}/R3.1_hill_cutout.png", optimize=True)
    # skyline (first row from the top with alpha >= 0.5) every 40 px, for placing the word
    sk = {int(c): int(np.argmax(alpha[:, c] >= 0.5)) for c in range(0, W, 40)}
    meta = {"source": os.path.relpath(SRC, ROOT), "t_s": T_SRC, "crop": "%d:%d:%d:%d" % CROP, "scale": 3,
            "plate": "assets/footage/R3.1_plate.jpg", "cutout": "assets/footage/R3.1_hill_cutout.png",
            "cutout_box_xywh": list(CUT_BOX), "key": {"T0": T0, "T1": T1, "edge_px": EDGE_PX},
            "skyline_y_at_x": sk}
    json.dump(meta, open(f"{out}/R3.1_depth.SOURCE.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != "skyline_y_at_x"}))
    print("skyline", sk)
    if prev_dir:
        os.makedirs(prev_dir, exist_ok=True)
        Image.fromarray(np.round(alpha * 255).astype(np.uint8)).save(f"{prev_dir}/alpha.png")
        Image.fromarray(np.clip(D * 6, 0, 255).astype(np.uint8)).save(f"{prev_dir}/dist.png")
        # composite test: a pink band behind the cut-out
        test = img.astype(np.float64).copy()
        band = np.zeros((H, W), bool)
        band[200:420, 300:1620] = True
        test[band] = [255, 46, 126]
        comp = test * (1 - alpha[..., None]) + fg_rgb.astype(np.float64) * alpha[..., None]
        Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8)).save(f"{prev_dir}/composite.png")


if __name__ == "__main__":
    main()
