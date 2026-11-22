"""Render the projector light-mask video (the gobo) from lamp_timeline.json.

Each frame is drawn in the projector's stretched canvas space (verified: the Tesseract
projector maps the full composition canvas onto its square), so a circular pool on the floor
is an ellipse here. Per lamp:
  - a soft disc whose brightness follows the lamp's level
  - Turbulent Displace while catching or dying: the disc's centre jitters and its edge
    wobbles with fresh fractal noise every frame, scaled by the lamp's turbulence
  - animated grain inside the light (noise inside light), different every frame
The hero lamp is included; a real spotlight adds its close-up shadows on top.

Usage: python3 gobo_render.py lamp_timeline.json OUT_DIR [--width 1920 --height 1080]
"""
import argparse
import json
import math
import os

import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gobo as G  # noqa: E402

POOL_R = 0.62     # m, radius of each pool
POOL_SOFT = 0.30  # m, soft edge width
GRAIN = 0.14      # grain contrast inside the light
CLOUD = 0.10      # slow, larger "printed" mottling inside the light


def value_noise(shape, cell, rng):
    """Smooth random field (bilinear-upsampled lattice noise), values 0..1."""
    h, w = shape
    gh, gw = h // cell + 2, w // cell + 2
    lattice = rng.random((gh, gw)).astype(np.float32)
    img = Image.fromarray((lattice * 255).astype(np.uint8), 'L').resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(img, np.float32)[:h, :w] / 255.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('timeline')
    ap.add_argument('out_dir')
    ap.add_argument('--width', type=int, default=1920)
    ap.add_argument('--height', type=int, default=1080)
    ap.add_argument('--frames', default=None, help='comma list for a partial render')
    a = ap.parse_args()
    t = json.load(open(a.timeline))
    W, H = a.width, a.height
    os.makedirs(a.out_dir, exist_ok=True)
    hx = G.half_extent(0.5)
    # pixels per metre along canvas x (u) and y (v)
    ppx, ppy = W / (2 * hx), H / (2 * hx)
    cells = list(t['cells'].values())
    frames = range(t['frames']) if not a.frames else [int(x) for x in a.frames.split(',')]
    for f in frames:
        rng = np.random.default_rng(1000 + f)
        img = np.zeros((H, W), np.float32)
        for cell in cells:
            lv = cell['level'][f]
            if lv <= 0.003:
                continue
            tb = cell['turb'][f]
            u, v = G.world_to_uv(cell['c'] * G.COL_SPACING, cell['r'] * G.ROW_SPACING, 0.5)
            cx, cy = u * W, v * H
            crng = np.random.default_rng(hash((cell['c'], cell['r'], f)) & 0xffffffff)
            if tb > 0:
                cx += crng.normal(0, 0.06 * tb) * ppx
                cy += crng.normal(0, 0.06 * tb) * ppy
            rx, ry = (POOL_R + POOL_SOFT) * ppx + 3, (POOL_R + POOL_SOFT) * ppy + 3
            x0, x1 = max(0, int(cx - rx)), min(W, int(cx + rx) + 1)
            y0, y1 = max(0, int(cy - ry)), min(H, int(cy + ry) + 1)
            if x0 >= x1 or y0 >= y1:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            dx = (xx + 0.5 - cx) / ppx
            dy = (yy + 0.5 - cy) / ppy
            d = np.sqrt(dx * dx + dy * dy)
            radius = POOL_R
            if tb > 0:
                ang = np.arctan2(dy, dx)
                wob = np.zeros_like(ang)
                for k in (3, 5, 7, 11):
                    wob += crng.uniform(-1, 1) / math.sqrt(k) * np.sin(k * ang + crng.uniform(0, 6.283))
                radius = POOL_R * (1 + 0.16 * tb * wob)
            a_ = np.clip((radius + POOL_SOFT / 2 - d) / POOL_SOFT, 0, 1)
            a_ = a_ * a_ * (3 - 2 * a_)
            img[y0:y1, x0:x1] = np.maximum(img[y0:y1, x0:x1], a_ * lv)
        # Noise inside the light: fine grain + slow mottling, both re-seeded each frame
        grain = rng.random((H, W), dtype=np.float32) - 0.5
        cloud = value_noise((H, W), 24, rng) - 0.5
        img *= 1 + GRAIN * 2 * grain + CLOUD * 2 * cloud
        # Gobo brightness 1.0 = standard lamp; keep headroom for the hero's 1.2x via the real spot
        out = np.clip(img / 1.2, 0, 1)
        Image.fromarray((out * 255 + 0.5).astype(np.uint8), 'L').save(os.path.join(a.out_dir, f'gobo_{f:03d}.png'))
    print('rendered', len(list(frames)), 'frames to', a.out_dir)


if __name__ == '__main__':
    main()
