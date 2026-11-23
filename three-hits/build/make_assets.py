"""Bake the Three Hits textures.

  tariff_ink.png    the TARIFF stamp mark: blocky caps in a rectangular border, red ink, broken up with the supplied
                    Grunge 353 (it displaces the edges and makes the ink patchy), alpha = ink coverage
  dust_puff.png     a soft dust sprite for the stamp burst and the knock-off puff (Grunge 352 inside a radial falloff)
  stamp_wood.png    dark worn wood grain for the stamp handle and block (procedural, stretched noise + Grunge 353 wear)
  stamp_rubber.png  the red rubber face, ink-stained
Box textures (cardboard from Paper 363) and the Grunge 353 displacement map are the ones baked for the Shoebox Tower MG.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "assets", "textures")
OUT = os.path.join(ROOT, "assets", "generated")
FONT = os.path.join(ROOT, "assets", "fonts", "Archivo-SemiCondensed-Black_wdth80_wght900.ttf")
rng = np.random.default_rng(64)


def gray(name, size):
    im = Image.open(os.path.join(TEX, name)).convert("L").resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


def save_rgba(rgb, a, name):
    arr = np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)])
    Image.fromarray((arr * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, name))


# ---------------------------------------------------------------- TARIFF ink
Wd, Hd = 1400, 600
mask = Image.new("L", (Wd, Hd), 0)
d = ImageDraw.Draw(mask)
d.rounded_rectangle([40, 40, Wd - 40, Hd - 40], radius=26, outline=255, width=34)
font = ImageFont.truetype(FONT, 380)
txt = "TARIFF"
bb = d.textbbox((0, 0), txt, font=font)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
d.text(((Wd - tw) / 2 - bb[0], (Hd - th) / 2 - bb[1] + 6), txt, font=font, fill=255)
m = np.asarray(mask).astype(np.float32) / 255.0
# displace the edges with the grunge map (a real stamp never prints a clean edge)
g = gray("grunge-353.jpg", (Wd, Hd))
gx = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
yy, xx = np.mgrid[0:Hd, 0:Wd].astype(np.float32)
sx = np.clip(xx + (gx - 0.5) * 14, 0, Wd - 1).astype(int)
sy = np.clip(yy + (np.roll(gx, 97, axis=1) - 0.5) * 14, 0, Hd - 1).astype(int)
m = m[sy, sx]
m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
# patchy coverage: uneven pressure across the face (heavier bottom-left) and grunge dropouts
press = 0.78 + 0.22 * (1 - xx / Wd) * (yy / Hd) + 0.10 * (gray("grunge-352.jpg", (Wd, Hd)) - 0.5)
# the levelled Grunge 353 map (equalised, so its dust and scratches spread over the whole range)
drop = np.asarray(Image.open(os.path.join(OUT, "grunge353_dispmap.png")).convert("L").resize((Wd, Hd), Image.LANCZOS)).astype(np.float32) / 255
drop = np.roll(np.roll(drop, 211, axis=0), 389, axis=1)
holes = np.clip((drop - 0.60) / 0.30, 0, 1)            # light areas of the grunge = ink did not take
speck = rng.random((Hd // 3, Wd // 3)).astype(np.float32)
speck = np.asarray(Image.fromarray((speck * 255).astype(np.uint8)).resize((Wd, Hd), Image.NEAREST)).astype(np.float32) / 255
cov = m * np.clip(press, 0, 1) * (1 - 0.8 * holes) * (1 - 0.35 * (speck > 0.86))
cov = np.clip(cov * 1.25, 0, 0.98)
ink = np.array([0.47, 0.035, 0.03])                    # deep red; the decal is unlit, so this is what reads on the lid
rgb = np.ones((Hd, Wd, 3)) * ink[None, None, :] * (0.92 + 0.08 * gx[..., None])
save_rgba(rgb, cov, "tariff_ink.png")

# ---------------------------------------------------------------- dust puff sprite
S = 384
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
r = np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2) / (S / 2)
n = gray("grunge-352.jpg", (S, S))
n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255
a = np.clip(1 - r, 0, 1) ** 1.8 * (0.35 + 0.9 * n)
a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))).astype(np.float32) / 255
save_rgba(np.ones((S, S, 3)) * np.array([0.86, 0.79, 0.69]), a * 0.85, "dust_puff.png")

# ---------------------------------------------------------------- stamp wood (dark, worn, grain along U)
Wt, Ht = 1024, 512
grain = rng.normal(0, 1, (Ht, 32)).astype(np.float32)
grain = np.asarray(Image.fromarray(grain).resize((Wt, Ht), Image.BICUBIC))
fine = rng.normal(0, 1, (Ht, Wt // 4)).astype(np.float32)
fine = np.asarray(Image.fromarray(fine).resize((Wt, Ht), Image.BILINEAR))
wear = gray("grunge-353.jpg", (Wt, Ht))
lum = 1 + 0.16 * grain + 0.05 * fine + 0.25 * (wear - 0.5)
base = np.array([0.20, 0.115, 0.07])
save_rgba(base[None, None, :] * lum[..., None], np.ones((Ht, Wt)), "stamp_wood.png")

# ---------------------------------------------------------------- rubber face (red, ink-stained)
Wt, Ht = 512, 256
st = gray("grunge-352.jpg", (Wt, Ht))
rub = np.array([0.42, 0.06, 0.05])[None, None, :] * (0.75 + 0.35 * st[..., None])
save_rgba(rub, np.ones((Ht, Wt)), "stamp_rubber.png")
print("assets ->", OUT, sorted(os.listdir(OUT)))
