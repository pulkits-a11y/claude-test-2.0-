"""PLACEHOLDER for Texture Labs Grunge 353 (not supplied yet): procedural grunge, 2048x2048 grayscale.
Replace assets/generated/grunge.png with the real Grunge 353 and rebuild; nothing else changes."""
import sys
import numpy as np
from PIL import Image, ImageFilter

S = 2048
rng = np.random.default_rng(353)


def lattice(cell):
    g = rng.random((S // cell + 2, S // cell + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((g.shape[1] * cell, g.shape[0] * cell),
                                                                          Image.BICUBIC), np.float32)[:S, :S] / 255


img = sum(lattice(c) * w for c, w in [(256, 0.35), (96, 0.25), (32, 0.2), (8, 0.12), (2, 0.08)])
blot = (lattice(160) > 0.68).astype(np.float32)
img = img * (1 - 0.35 * blot)
scr = Image.new('L', (S, S), 0)
from PIL import ImageDraw
d = ImageDraw.Draw(scr)
for _ in range(240):
    x, y = rng.integers(0, S, 2)
    L = rng.integers(40, 420)
    a = rng.uniform(-0.4, 0.4) + (np.pi / 2 if rng.random() < 0.5 else 0)
    d.line([x, y, x + L * np.cos(a), y + L * np.sin(a)], fill=int(rng.integers(90, 220)), width=int(rng.integers(1, 3)))
scr = np.asarray(scr.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
img = np.clip((img - img.min()) / (img.max() - img.min()) * 0.85 + scr * 0.3, 0, 1)
Image.fromarray((img * 255).astype(np.uint8), 'L').convert('RGB').save(sys.argv[1])
print('placeholder grunge written', sys.argv[1])
