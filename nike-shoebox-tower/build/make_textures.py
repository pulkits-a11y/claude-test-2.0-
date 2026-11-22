"""Bake the set's textures from the supplied Texture Labs maps (Paper 363, Grunge 352/353).

Outputs to assets/generated/. Box faces are mapped 0..1 per face (verified with a UV test), so the
side texture carries the shadow under the lid along its top edge and light wear on every edge.
"""
import os
import random

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "assets", "textures")
OUT = os.path.join(ROOT, "assets", "generated")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(353)


def load_gray(name, size):
    im = Image.open(os.path.join(TEX, name)).convert("L").resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


def srgb(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32) / 255.0


def save(arr, name):
    Image.fromarray(np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))


def cardboard(color_hex, size, lid=False, seed=0):
    w, h = size
    paper = load_gray("paper-363.jpg", (w, h))
    paper = (paper - paper.mean()) / (paper.std() + 1e-6)
    fib = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
    fib = np.asarray(Image.fromarray(fib).resize((w, h), Image.BILINEAR))
    base = srgb(color_hex)
    lum = 1.0 + 0.045 * paper + 0.018 * fib
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / (w - 1), yy / (h - 1)
    edge = np.minimum(np.minimum(u, 1 - u) * w / h, np.minimum(v, 1 - v))
    wear = np.clip(1 - edge / 0.035, 0, 1) ** 2
    scuff = load_gray("grunge-353.jpg", (w, h))
    wear = np.clip(wear * (0.55 + 1.6 * scuff), 0, 1)
    col = base[None, None, :] * lum[..., None]
    col = col * (1 - 0.22 * wear[..., None]) + np.array([0.93, 0.85, 0.74])[None, None, :] * 0.22 * wear[..., None]
    if not lid:
        # shadow under the overhanging lid (top 20% of each side) and a soft contact line at the bottom
        under = np.clip(1 - v / 0.20, 0, 1) ** 1.6
        col *= (1 - 0.55 * under)[..., None]
        col *= (1 - 0.18 * np.clip(1 - (1 - v) / 0.05, 0, 1))[..., None]
    else:
        # the lid's lower lip edge catches less light
        col *= (1 - 0.10 * np.clip(1 - (1 - v) / 0.08, 0, 1))[..., None]
    return np.clip(col, 0, 1)


save(cardboard("#E2581A", (1024, 384)), "box_side_orange.png")
save(cardboard("#E2581A", (1024, 640), lid=True), "box_lid_orange.png")
save(cardboard("#5C5D5C", (1024, 384)), "box_side_grey.png")
save(cardboard("#626362", (1024, 640), lid=True), "box_lid_grey.png")

# Sidewalk: 4 x 4 concrete slabs per tile (each 600 mm), dark seams, grunge variation
S = 2048
g352 = load_gray("grunge-352.jpg", (S, S))
g353 = load_gray("grunge-353.jpg", (S, S))
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
cell = S / 4
seam = np.minimum(np.abs((xx % cell) - cell / 2) - (cell / 2 - 7), 0)
seam = np.maximum(seam, np.minimum(np.abs((yy % cell) - cell / 2) - (cell / 2 - 7), 0))
seam = np.clip((np.minimum(np.abs((xx % cell)), np.abs(cell - (xx % cell))) < 6) |
               (np.minimum(np.abs((yy % cell)), np.abs(cell - (yy % cell))) < 6), 0, 1).astype(np.float32)
seam = np.asarray(Image.fromarray((seam * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) / 255.0
slab_tone = np.zeros((S, S), np.float32)
r = random.Random(4)
for i in range(4):
    for j in range(4):
        slab_tone[int(i * cell):int((i + 1) * cell), int(j * cell):int((j + 1) * cell)] = r.uniform(-0.05, 0.05)
concrete = 0.20 + slab_tone + 0.10 * (g352 - g352.mean()) + 0.05 * (g353 - g353.mean())
concrete = concrete * (1 - 0.55 * seam)
save(np.repeat(np.clip(concrete, 0, 1)[..., None], 3, 2) * np.array([1.0, 0.985, 0.96]), "sidewalk_color.png")

# Puddle mask: smooth blobs from blurred grunge; 1 = standing water (glossy), 0 = damp concrete
blob = np.asarray(Image.fromarray((g352 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))) / 255.0
blob = (blob - blob.min()) / (blob.max() - blob.min() + 1e-6)
puddle = np.clip((blob - 0.48) / 0.12, 0, 1)
rough_side = 0.30 - 0.26 * puddle + 0.10 * seam          # seams stay rough
save(np.repeat(np.clip(rough_side, 0, 1)[..., None], 3, 2), "sidewalk_rough.png")

# Asphalt: near black aggregate, wetter overall
agg = rng.normal(0, 1, (S // 4, S // 4)).astype(np.float32)
agg = np.asarray(Image.fromarray(agg).resize((S, S), Image.NEAREST))
asph = 0.055 + 0.012 * agg + 0.03 * (g353 - g353.mean())
save(np.repeat(np.clip(asph, 0, 1)[..., None], 3, 2) * np.array([0.97, 1.0, 1.02]), "asphalt_color.png")
rough_asph = 0.20 - 0.17 * np.clip((blob - 0.35) / 0.2, 0, 1)
save(np.repeat(np.clip(rough_asph, 0, 1)[..., None], 3, 2), "asphalt_rough.png")
print("textures ->", OUT, sorted(os.listdir(OUT)))
