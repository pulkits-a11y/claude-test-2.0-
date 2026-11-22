"""Light-mask (gobo) generator for the hall's overhead projector light.

One spotlight hangs high above the hall, pointing straight down. Its gobo image decides,
per pedestal, whether that pedestal's "lamp" is on: a soft disc under each lamp is a pool
of light that lights the shoe, the pedestal top and the floor around it. Animating the discs
(cascade on, flicker, die) animates every lamp in the hall with a single light.

This module holds the shared geometry (cell <-> gobo pixel mapping) and a test-pattern writer.
"""
import math
import sys

import numpy as np

COL_SPACING = 1.5   # m
ROW_SPACING = 2.2   # m
COLS = 20           # columns each side of centre
ROWS = 27

# Projector placement (metres, Tesseract world: x right, y down, z into screen)
PROJ_X = 0.0
PROJ_Z = (ROWS - 1) * ROW_SPACING / 2
PROJ_H = 300.0          # height above the floor
PROJ_CONE = 12.0        # full cone angle, degrees (mask covers the hall, x +-31.5 m)
FLIP_U = False          # set from the orientation test
FLIP_V = True
SWAP_UV = False


def half_extent(plane_y=0.0):
    """Half-width (m) of the projector square on a horizontal plane at height plane_y."""
    return (PROJ_H - plane_y) * math.tan(math.radians(PROJ_CONE / 2))


def world_to_uv(x, z, plane_y=0.0):
    h = half_extent(plane_y)
    u = 0.5 + (x - PROJ_X) / (2 * h)
    v = 0.5 + (z - PROJ_Z) / (2 * h)
    if SWAP_UV:
        u, v = v, u
    if FLIP_U:
        u = 1 - u
    if FLIP_V:
        v = 1 - v
    return u, v


def disc(img, cx, cy, r_px, soft_px, value=1.0):
    h, w = img.shape
    x0, x1 = max(0, int(cx - r_px - soft_px - 2)), min(w, int(cx + r_px + soft_px + 3))
    y0, y1 = max(0, int(cy - r_px - soft_px - 2)), min(h, int(cy + r_px + soft_px + 3))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2)
    a = np.clip((r_px + soft_px / 2 - d) / max(soft_px, 1e-6), 0, 1)
    a = a * a * (3 - 2 * a)
    img[y0:y1, x0:x1] = np.maximum(img[y0:y1, x0:x1], a * value)


def test_pattern(path, size=2048, pool_r=0.6, soft=0.35):
    from PIL import Image
    img = np.zeros((size, size), np.float32)
    px_per_m = size / (2 * half_extent(1.0))
    for r in range(ROWS):
        for c in range(-COLS, COLS + 1):
            u, v = world_to_uv(c * COL_SPACING, r * ROW_SPACING, 1.0)
            disc(img, u * size, v * size, pool_r * px_per_m, soft * px_per_m)
    # Asymmetric markers: a big disc at (c=+6, r=2) and a bar along +X at row 8 starting at c=-6
    u, v = world_to_uv(6 * COL_SPACING, 2 * ROW_SPACING, 1.0)
    disc(img, u * size, v * size, 1.4 * px_per_m, 0.2 * px_per_m)
    for i in range(12):
        u, v = world_to_uv((-6 + i * 0.25) * COL_SPACING, 8 * ROW_SPACING + 0.9, 1.0)
        disc(img, u * size, v * size, 0.25 * px_per_m, 0.1 * px_per_m)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), 'L').convert('RGB').save(path)
    print('wrote', path, 'px/m', round(px_per_m, 2))


if __name__ == '__main__':
    test_pattern(sys.argv[1])
