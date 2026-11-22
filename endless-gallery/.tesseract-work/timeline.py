"""Per-lamp timeline for the Endless Gallery (84 frames @ 30 fps).

Every pedestal (column c, row r) has one lamp. For each frame this computes:
  level[f]  0..1.2  lamp brightness (1.0 = standard; the hero starts brighter)
  turb[f]   0..1    turbulence amount (Turbulent Displace shudder while catching or dying)

Beats (MG frames, verified against the VO):
  f0      "Dunks" already being said; hero lamp is on, shudders f0-3 as if just switched on
  f19     "Air": snap pull-back 1; row 0 ripples outward (both AF1s lit by f27)
  f49     "Retro": snap pull-back 2; the hall cascades on toward the horizon
  f63     "Jordans" lands (nearest Jordans long since lit)
  f66+    the hall goes cold: random lamps stutter and die, far rows first
Deterministic: seeded RNG, so every render and the gobo video agree.
"""
import json
import math
import random
import sys

FRAMES = 84
COLS = 20
ROWS = 27
SEED = 353


def shoe_type(c, r):
    return (abs(c) + (r % 2)) % 3


def catch_pattern(rng, strong):
    """Brightness/turbulence offsets for a lamp catching. Irregular, 3-5 frames."""
    if strong:
        lv = [rng.uniform(0.35, 0.6), rng.uniform(0.05, 0.2), rng.uniform(0.75, 1.05),
              rng.uniform(0.55, 0.8), rng.uniform(0.92, 1.02)]
        tb = [1.0, 0.85, 0.65, 0.4, 0.15]
        n = rng.choice([4, 5])
        return lv[:n], tb[:n]
    lv = [rng.uniform(0.3, 0.55), rng.uniform(0.8, 1.0)]
    return lv, [0.5, 0.2]


def die_pattern(rng):
    """2-3 quick stutters, then off. Returns per-frame levels after the failure starts."""
    stutters = rng.choice([2, 2, 3])
    seq = []
    for i in range(stutters):
        seq.append(rng.uniform(0.05, 0.25))           # dip
        if rng.random() < 0.45:
            seq.append(rng.uniform(0.05, 0.2))         # sometimes a 2-frame dip
        seq.append(rng.uniform(0.55, 0.95) * (1 - 0.18 * i))  # recover, weaker each time
    seq.append(rng.uniform(0.0, 0.08))
    seq.append(0.0)
    return seq


def build():
    rng = random.Random(SEED)
    cells = {}
    on_frame = {}
    strong = {}

    # Row 0 ripple (Phase 2). Irregular gaps, first ones quick, then spreading.
    ripple = {0: 0, 1: 23, -1: 25, 2: 30, -2: 32, 3: 35, -3: 37, 4: 40, -4: 43, 5: 45, -5: 47}
    for c, f in ripple.items():
        on_frame[(c, 0)] = f
        strong[(c, 0)] = True

    # Phase 3 cascade: a wave racing from the camera toward the horizon, f51 -> ~f62.
    max_d = math.hypot(ROWS * 2.2, COLS * 1.5 * 0.55)
    for r in range(ROWS):
        for c in range(-COLS, COLS + 1):
            if (c, r) in on_frame:
                continue
            d = math.hypot(r * 2.2, c * 1.5 * 0.55) / max_d
            f = 51.0 + 11.0 * d ** 0.8 + rng.uniform(-1.3, 1.3)
            on_frame[(c, r)] = int(round(min(max(f, 50.5), 63.0)))
            strong[(c, r)] = r <= 4 and abs(c) <= 8

    # Phase 4 failures: far rows first, spreading irregularly closer. Nearest rows mostly survive.
    fail_frame = {}
    for r in range(ROWS):
        for c in range(-COLS, COLS + 1):
            if r == 0 and abs(c) <= 3:
                continue
            p = 0.04 if r <= 2 else min(0.56, 0.18 + 0.40 * (r / (ROWS - 1)) ** 0.7)
            if rng.random() < p:
                closeness = 1 - r / (ROWS - 1)
                f = 66 + 9.0 * closeness ** 1.2 + rng.uniform(-2.0, 3.5)
                fail_frame[(c, r)] = int(round(min(max(f, 66), 76)))

    for r in range(ROWS):
        for c in range(-COLS, COLS + 1):
            lv = [0.0] * FRAMES
            tb = [0.0] * FRAMES
            f0 = on_frame[(c, r)]
            pat_l, pat_t = catch_pattern(rng, strong[(c, r)])
            if (c, r) == (0, 0):
                # Hero: already on, catches over f0-3, slightly brighter until it settles to standard f30-44
                pat_l, pat_t = [0.55, 1.05, 0.8, 1.15], [1.0, 0.8, 0.5, 0.2]
            for i in range(f0, FRAMES):
                k = i - f0
                lv[i] = pat_l[k] if k < len(pat_l) else 1.0
                tb[i] = pat_t[k] if k < len(pat_t) else 0.0
            if (c, r) == (0, 0):
                for i in range(FRAMES):
                    if i >= 4:
                        # 1.2x until f30, eased down to 1.0 by f44
                        x = min(max((i - 30) / 14.0, 0.0), 1.0)
                        lv[i] = 1.2 - 0.2 * (x * x * (3 - 2 * x))
            if (c, r) in fail_frame:
                ff = fail_frame[(c, r)]
                seq = die_pattern(rng)
                for k in range(FRAMES - ff):
                    i = ff + k
                    if lv[i] <= 0:
                        continue
                    lv[i] = (seq[k] if k < len(seq) else 0.0) * lv[i]
                    tb[i] = 1.0 if k < len(seq) - 1 else 0.0
            cells[f"{c},{r}"] = {"c": c, "r": r, "type": shoe_type(c, r), "on": f0,
                                "fail": fail_frame.get((c, r)), "level": [round(x, 4) for x in lv],
                                "turb": [round(x, 3) for x in tb]}
    return {"frames": FRAMES, "fps": 30, "cols": COLS, "rows": ROWS, "seed": SEED, "cells": cells}


if __name__ == '__main__':
    t = build()
    out = sys.argv[1] if len(sys.argv) > 1 else 'lamp_timeline.json'
    json.dump(t, open(out, 'w'))
    cells = t["cells"].values()
    failed = sum(1 for c in cells if c["fail"] is not None)
    print(f"{len(t['cells'])} lamps, {failed} fail ({100 * failed / len(t['cells']):.0f}% of the whole hall)")
    for key in ["0,0", "1,0", "-1,0", "2,0", "0,1", "0,5", "0,26"]:
        c = t["cells"][key]
        print(key, "on", c["on"], "fail", c["fail"])
