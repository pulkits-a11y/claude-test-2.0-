"""Tower layout and the procedural 'rise' (box drops) for the Shoebox Tower MG.

Units: metres and seconds, Blender-style axes (X right, Y depth away from camera, Z up).
Writes layout.json (per-box hand-placed offsets) and rise_track.json (per-frame transforms
for frames 0..LAST_RISE_FRAME) consumed by the Blender collapse sim and the Tesseract builder.
"""
import json
import math
import random

FPS = 30
G = 9.81
N = 28
BOX_W, BOX_D, BOX_H = 0.338, 0.208, 0.122   # collision envelope incl. lid (width X, depth Y, height Z)
PITCH = BOX_H                                # stacked boxes sit lid-top to base-bottom

T_FIRST = 2.90          # first box lands on "Nike"
# 28th box lands at 5.60 s, inside "billion" (5.41-5.80): the counter locks $280B there

rng = random.Random(20211)


GAP_FRAMES = [9, 7, 5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]   # box 28 lands 5.40 s, start of "billion"


def landing_times():
    """Accelerating drop rhythm, in whole frames: deliberate at first, a 2-frame rain at the end."""
    f = round(T_FIRST * FPS)
    out = [f / FPS]
    for g in GAP_FRAMES:
        f += g
        out.append(f / FPS)
    return out


def layout():
    boxes = []
    for i in range(N):
        boxes.append({
            "index": i + 1,
            "dx": rng.uniform(-0.006, 0.006),
            "dy": rng.uniform(-0.005, 0.005),
            "yaw_deg": rng.choice([-1, 1]) * rng.uniform(0.5, 1.5),
            "z_bottom": i * PITCH,
        })
    return boxes


def quat_from_euler_deg(rx, ry, rz):
    # XYZ intrinsic -> quaternion (Blender axes)
    cx, sx = math.cos(math.radians(rx) / 2), math.sin(math.radians(rx) / 2)
    cy, sy = math.cos(math.radians(ry) / 2), math.sin(math.radians(ry) / 2)
    cz, sz = math.cos(math.radians(rz) / 2), math.sin(math.radians(rz) / 2)
    # q = qz * qy * qx (extrinsic XYZ == intrinsic ZYX); we use small angles so order hardly matters
    w = cz * cy * cx + sz * sy * sx
    x = cz * cy * sx - sz * sy * cx
    y = cz * sy * cx + sz * cy * sx
    z = sz * cy * cx - cz * sy * sx
    return [x, y, z, w]


def drop_height(k):
    # early boxes fall further (slower, more deliberate); later ones are a short fast rain
    return 0.95 - 0.45 * min(1.0, k / 18.0)


def dip_profile(tau):
    """Stack compression after one landing: quick dip, slight overshoot, settle (~0.3 s)."""
    if tau < 0:
        return 0.0
    if tau < 0.05:
        return -math.sin(tau / 0.05 * math.pi / 2)
    s = tau - 0.05
    return -math.exp(-s / 0.07) * math.cos(s * 2 * math.pi / 0.22)


def squash_profile(tau):
    """Landing box squash: returns (scale_z, scale_xy)."""
    if tau < 0:
        return 1.0, 1.0
    a = 0.045 * math.exp(-tau / 0.06) * math.cos(tau * 2 * math.pi / 0.16)
    return 1.0 - a, 1.0 + a * 0.45


def bounce_profile(tau):
    """Tiny rebound height (m) after impact."""
    if tau < 0.02:
        return 0.0
    s = tau - 0.02
    return 0.007 * math.exp(-s / 0.05) * abs(math.sin(s * math.pi / 0.09))


def main(outdir="."):
    L = landing_times()
    boxes = layout()
    last_frame = int(7.30 * FPS)    # collapse starts on "Less"
    track = {"fps": FPS, "landing_times": L, "frames": {}}
    for f in range(0, last_frame + 1):
        t = f / FPS
        landed = [k for k in range(N) if L[k] <= t + 1e-9]
        frame = []
        for k, b in enumerate(boxes):
            z_rest = b["z_bottom"]
            # stack compression from all landings, stronger higher up the stack
            dip = 0.0
            for j in landed:
                if k <= j:   # a landing compresses the boxes beneath it, more toward the top
                    amp = 0.0055 if j < 10 else 0.0035
                    dip += amp * dip_profile(t - L[j]) * (k + 1) / (j + 1)
            yaw = b["yaw_deg"]
            if t < L[k]:
                H = drop_height(k)
                tf = math.sqrt(2 * H / G)
                t_rel = L[k] - tf
                if t < t_rel:
                    z = 60.0 + k          # parked far above, out of shot
                    vis = False
                else:
                    z = z_rest + H - 0.5 * G * (t - t_rel) ** 2
                    vis = True
                sz, sxy = 1.0, 1.0
                tilt = (0.0, 0.0)
            else:
                tau = t - L[k]
                sz, sxy = squash_profile(tau)
                z = z_rest + bounce_profile(tau) + dip
                w = 0.6 * math.exp(-tau / 0.08) * math.sin(tau * 2 * math.pi / 0.14)
                tilt = (w * (1 if k % 2 else -1), w * 0.6)
                vis = True
            # pos is the box CENTRE; squash pivots on the bottom face
            frame.append({"pos": [b["dx"], b["dy"], z + 0.5 * BOX_H * sz], "quat": quat_from_euler_deg(tilt[0], tilt[1], yaw),
                          "scale": [sxy, sxy, sz], "visible": vis})
        track["frames"][f] = frame
    json.dump({"boxes": boxes, "landing_times": L, "box_dims": [BOX_W, BOX_D, BOX_H], "pitch": PITCH},
              open(f"{outdir}/layout.json", "w"), indent=1)
    json.dump(track, open(f"{outdir}/rise_track.json", "w"))
    print("landings (s):", ", ".join(f"{x:.3f}" for x in L))
    print("gaps (frames):", [round((L[i + 1] - L[i]) * FPS) for i in range(N - 1)])


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
