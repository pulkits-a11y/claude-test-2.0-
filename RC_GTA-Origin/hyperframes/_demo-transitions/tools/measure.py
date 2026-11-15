#!/usr/bin/env python3
"""Re-measure every transition spec value from the proof frames in review/ (run tools/snap.sh first).
   python3 tools/measure.py
Each line: what the plan / kit doc says, what the frames show."""
import math
import os

import numpy as np
from PIL import Image

R = "review"


def load(name, f, mode="RGB"):
    return np.asarray(Image.open(f"{R}/{name}_f{f:03d}.png").convert(mode)).astype(float)


def have(name, frames):
    return all(os.path.exists(f"{R}/{name}_f{f:03d}.png") for f in frames)


def runs(mask):
    out, start = [], None
    for x, v in enumerate(list(mask) + [False]):
        if v and start is None:
            start = x
        if not v and start is not None:
            out.append((start, x))
            start = None
    return out


# X2: card content (white L5 border, CSS left 120 px) slides 60 px left over 20f, power3.out = 1-(1-p)^4
if have("X2_drift", [30, 31, 35, 40, 50, 60]):
    def edge(f, row=540, thr=245.0):
        a = load("X2_drift", f, "L")[row]
        for x in range(60, 400):
            if a[x] < thr <= a[x + 1]:
                return x + (thr - a[x]) / (a[x + 1] - a[x]) - 0.5
    base = edge(60)
    for f in (30, 31, 35, 40, 50):
        p = (f - 30) / 20
        print(f"X2 f{f}: offset {edge(f) - base:6.2f} px | expected {60 * (1 - p) ** 4:6.2f} (60 px, 20f, power3.out)")

# X3: white opacity on a flat patch; cut at f110
if have("X3_flash", range(107, 117)):
    def m(f):
        return load("X3_flash", f)[700:900, 200:600].mean()
    exp = {107: 0, 108: 0, 109: .5, 110: 1, 111: 1, 112: .75, 113: .5, 114: .25, 115: 0, 116: 0}
    lo, ln = m(107), m(116)
    for f in range(107, 117):
        u = lo if f < 110 else ln
        print(f"X3 f{f}: white {(m(f) - u) / (255 - u):.3f} | expected {exp[f]:.2f}")

# X5: share of the row y=900 that is ink black, and slat count; boundary f375, 11.25 deg a frame
if have("X5_blinds", range(366, 384)):
    for f in range(366, 384):
        row = load("X5_blinds", f)[900]
        ink = np.all(np.abs(row - 10) <= 3, axis=1)
        k = abs(f - 375)
        exp = math.cos(math.radians(11.25 * k)) if k < 8 else 0.0
        print(f"X5 f{f}: coverage {ink.mean():.3f} | expected {exp:.3f} | runs {len(runs(ink))}")


# X6: scale from crisp #0A0A0A stand-ins (CRT screen 320 x 240 at 1040,330 / bezel 352 x 212 at 1184,384)
def zoom_rows(name, frames, dir_, P, ref_x, ref_y, ref_w):
    L = math.log(6)
    for k, f in enumerate(frames):
        p = k / 8
        s = math.exp(L * (1 - (1 - (1 - p) ** 2))) if dir_ == "out" else math.exp(L * p * p)
        y = int(round(P[1] + s * (ref_y - P[1])))
        if not 0 <= y < 1080:
            print(f"X6 {dir_} f{f}: expected {s * 100:6.1f}% (reference row off-frame: the screen covers the frame)")
            continue
        r = runs(load(name, f, "L")[y] <= 14)
        x0, x1 = max(r, key=lambda t: t[1] - t[0])
        print(f"X6 {dir_} f{f}: scale {100 * (x1 - x0) / ref_w:6.1f}% | expected {s * 100:6.1f}% | left {x0} vs {P[0] + s * (ref_x - P[0]):.1f}")


if have("X6_out_B2", range(435, 444)):
    zoom_rows("X6_out_B2", range(435, 444), "out", (1248.0, 432.0), 1040, 345, 320)
if have("X6_in_B15", range(530, 539)):
    zoom_rows("X6_in_B15", range(530, 539), "in", (1440.0, 480.0), 1184, 392, 352)

# X7: brightness through the dissolve; last frame pure #0A0A0A
if have("X7_leak_B16", [599, 600, 602, 604, 607, 609, 611, 613, 614]):
    for f in (599, 600, 602, 604, 607, 609, 611, 613, 614):
        print(f"X7 f{f}: mean RGB {np.round(load('X7_leak_B16', f).mean(axis=(0, 1)), 1)}")
    a = load("X7_leak_B16", 614).astype(int)[200:1000, 100:1800]
    print(f"X7 f614: share of #0A0A0A pixels {np.all(a == 10, axis=2).mean():.3f} (dissolve ends on black)")

# X9: Overlay at 35%: red W, W+1; blue W+2, W+3; none W+4
RED, BLUE, A = np.array([0xE3, 0x26, 0x2E]) / 255, np.array([0x2D, 0x5B, 0xFF]) / 255, 0.35
for name, w in (("X9_siren_B1", 670), ("X9_siren_B5", 700)):
    if not have(name, range(w - 1, w + 5)):
        continue
    def crop(f):
        return load(name, f)[120:1000, 100:1820] / 255
    b = crop(w - 1)
    for f, col in zip(range(w, w + 4), (RED, RED, BLUE, BLUE)):
        ov = np.where(b <= 0.5, 2 * b * col, 1 - 2 * (1 - b) * (1 - col))
        exp = ((1 - A) * b + A * ov).mean(axis=(0, 1)) * 255
        got = crop(f).mean(axis=(0, 1)) * 255
        print(f"X9 {name[-2:]} f{f}: RGB {np.round(got, 1)} | expected {np.round(exp, 1)} ({'red' if col is RED else 'blue'} 35% Overlay)")
    print(f"X9 {name[-2:]} f{w + 4}: RGB {np.round(crop(w + 4).mean(axis=(0, 1)) * 255, 1)} | unwashed {np.round(b.mean(axis=(0, 1)) * 255, 1)}")

# X4: RGB split of the torn picture: best horizontal shift of R and B against G on a text/edge-rich crop
for name, f, crop in (("X4_still_B8", 178, (300, 520, 600, 1350)), ("X4_still_B17", 317, (200, 560, 500, 1450))):
    if not have(name, [f]):
        continue
    a = load(name, f)[crop[0]:crop[1], crop[2]:crop[3]]
    g = a[:, :, 1] - a[:, :, 1].mean()

    def best(ch):
        c = a[:, :, ch] - a[:, :, ch].mean()
        sc = []
        for s in range(-12, 13):
            if s >= 0:
                sc.append((np.sum(c[:, s:] * g[:, :c.shape[1] - s]), s))
            else:
                sc.append((np.sum(c[:, :s] * g[:, -s:]), s))
        return max(sc)[1]
    print(f"X4 {name.split('_')[-1]} f{f}: red shifted {best(0):+d} px, blue {best(2):+d} px vs green (expected +6 / -6)")
