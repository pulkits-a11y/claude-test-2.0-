"""Shared timing, camera, projection and keyframe helpers for the Three Hits MG.

Scene3D axes: X right, Y DOWN, Z into the screen; pixels; pixelsPerMeter = 1000 (1 px = 1 mm). Floor at y = 0.
Physics (Blender) axes: X right, Y away from camera, Z up; metres.
"""
import json
import math
import os

FPS = 30
DUR = 6.47
NFRAMES = 194
W, H = 1920, 1080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHYS = os.path.join(ROOT, "build", "physics")

# ---------------------------------------------------------------- VO beats (MG seconds; MG 0 = video 1:04.53)
# Measured from the narration (waveform + word-level Whisper), aligned so "Tariffs" starts at MG 0.00. The take is
# the same as in the v4 edit, where the silences fall exactly where the brief puts them (3.37-3.53, 6.25-6.47).
T = {
    "tariffs": 0.00, "impact": 5 / 30,            # stamp lands on the stressed "TAR-"
    "china": 0.76, "down": 0.97, "knock": 1.03,   # the top box is hit on "down"
    "n26": 1.31, "in_quarter": 2.45, "quarter_end": 3.37,
    "and": 3.53, "y2025": 3.70, "y2026": 4.25, "y2027": 4.85, "y2028": 5.30,
    "vo_end": 6.25, "die": 6.30, "end": 6.47,
}

ms = lambda t: int(round(t * 1000))
frame_t = lambda f: f / FPS


def load_json(name):
    return json.load(open(os.path.join(PHYS, name)))


# ---------------------------------------------------------------- easing helpers
def smoothstep(a, b, x):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    u = (x - a) / (b - a)
    return u * u * (3 - 2 * u)


def smootherstep(a, b, x):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    u = (x - a) / (b - a)
    return u * u * u * (u * (u * 6 - 15) + 10)


def ease_in_out_cubic(u):
    u = min(max(u, 0.0), 1.0)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def lerp(a, b, u):
    return [x + (y - x) * u for x, y in zip(a, b)]


def hermite_path(keys, t):
    """keys: list of (time, vec). Monotone-time Catmull-Rom with zero velocity at the ends."""
    if t <= keys[0][0]:
        return list(keys[0][1])
    if t >= keys[-1][0]:
        return list(keys[-1][1])
    for i in range(len(keys) - 1):
        t0, p0 = keys[i]
        t1, p1 = keys[i + 1]
        if t0 <= t <= t1:
            break
    def tangent(j):
        if j == 0 or j == len(keys) - 1:
            return [0.0] * len(keys[j][1])
        ta, pa = keys[j - 1]
        tb, pb = keys[j + 1]
        return [(b - a) / (tb - ta) for a, b in zip(pa, pb)]
    m0, m1 = tangent(i), tangent(i + 1)
    h = t1 - t0
    u = (t - t0) / h
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1
    h10 = u ** 3 - 2 * u ** 2 + u
    h01 = -2 * u ** 3 + 3 * u ** 2
    h11 = u ** 3 - u ** 2
    return [h00 * a + h10 * h * ma + h01 * b + h11 * h * mb for a, b, ma, mb in zip(p0, p1, m0, m1)]


# ---------------------------------------------------------------- cameras
FOCAL_MM, SENSOR_W = 35.0, 36.0
F_PX = (W / 2) / (SENSOR_W / 2 / FOCAL_MM)      # 1866.7 px for a horizontally fitted 35 mm lens


def look_quat(P, L):
    """Camera looks down local +Z with local +Y pointing at world down (upright, no roll)."""
    f = [L[i] - P[i] for i in range(3)]
    n = math.sqrt(sum(x * x for x in f))
    z = [x / n for x in f]
    d = [0.0, 1.0, 0.0]
    k = sum(a * b for a, b in zip(d, z))
    y = [d[i] - k * z[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in y))
    y = [v / n for v in y]
    x = [y[1] * z[2] - y[2] * z[1], y[2] * z[0] - y[0] * z[2], y[0] * z[1] - y[1] * z[0]]
    return mat_to_quat([[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]]), (x, y, z)


def mat_to_quat(m):
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        w = 0.25 * s
        x = (m[2][1] - m[1][2]) / s
        y = (m[0][2] - m[2][0]) / s
        z = (m[1][0] - m[0][1]) / s
    elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        w = (m[2][1] - m[1][2]) / s
        x = 0.25 * s
        y = (m[0][1] + m[1][0]) / s
        z = (m[0][2] + m[2][0]) / s
    elif m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        w = (m[0][2] - m[2][0]) / s
        x = (m[0][1] + m[1][0]) / s
        y = 0.25 * s
        z = (m[1][2] + m[2][1]) / s
    else:
        s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
        w = (m[1][0] - m[0][1]) / s
        x = (m[0][2] + m[2][0]) / s
        y = (m[1][2] + m[2][1]) / s
        z = 0.25 * s
    q = [x, y, z, w]
    n = math.sqrt(sum(c * c for c in q))
    return [c / n for c in q]


def project(Pw, cam):
    """cam = (P, L) or (P, L, focal_mm)."""
    P, L = cam[0], cam[1]
    fpx = F_PX * (cam[2] / FOCAL_MM if len(cam) > 2 else 1.0)
    _, (x, y, z) = look_quat(P, L)
    d = [Pw[i] - P[i] for i in range(3)]
    xc = sum(a * b for a, b in zip(d, x))
    yc = sum(a * b for a, b in zip(d, y))
    zc = sum(a * b for a, b in zip(d, z))
    return (W / 2 + fpx * xc / zc, H / 2 + fpx * yc / zc, zc)


# ---------------------------------------------------------------- physics conversion
def b2t_pos(p):
    """Blender metres (X right, Y depth, Z up) -> Scene3D pixels (X right, Y down, Z depth)."""
    return [p[0] * 1000.0, -p[2] * 1000.0, p[1] * 1000.0]


_QM = [math.sin(math.pi / 4), 0.0, 0.0, math.cos(math.pi / 4)]   # +90 deg about X
_QMi = [-_QM[0], 0.0, 0.0, _QM[3]]


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return [aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz]


def b2t_quat(q):
    r = qmul(qmul(_QM, q), _QMi)
    n = math.sqrt(sum(c * c for c in r))
    r = [c / n for c in r]
    if r[3] < 0:
        r = [-c for c in r]
    return r


def mirror_quat(q):
    """Reflection of an orientation across the ground plane (Scene3D Y axis)."""
    return [-q[0], q[1], -q[2], q[3]]


# ---------------------------------------------------------------- keyframe tracks
def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def rdp(samples, tol, is_quat=False):
    """Ramer-Douglas-Peucker on (t, vec) samples; keeps interpolation error below tol."""
    if len(samples) <= 2:
        return samples
    keep = [False] * len(samples)
    keep[0] = keep[-1] = True
    stack = [(0, len(samples) - 1)]
    while stack:
        i, j = stack.pop()
        ti, vi = samples[i]
        tj, vj = samples[j]
        worst, wk = 0.0, None
        for k in range(i + 1, j):
            tk, vk = samples[k]
            u = (tk - ti) / (tj - ti)
            interp = [a + (b - a) * u for a, b in zip(vi, vj)]
            if is_quat:
                n = max(1e-9, math.sqrt(sum(c * c for c in interp)))
                dot = abs(sum(a * b for a, b in zip(interp, vk))) / n
                d = math.degrees(2 * math.acos(min(1.0, dot)))
            else:
                d = _dist(interp, vk)
            if d > worst:
                worst, wk = d, k
        if wk is not None and worst > tol:
            keep[wk] = True
            stack.append((i, wk))
            stack.append((wk, j))
    return [s for s, k in zip(samples, keep) if k]


def kf_track(samples, kind, prefix, tol):
    """samples: list of (t_seconds, value list). Returns Tesseract keyframe dicts (linear between dense samples)."""
    pts = rdp(samples, tol, is_quat=(kind == "quaternion"))
    out = []
    last_ms = None
    for i, (t, v) in enumerate(pts):
        m = ms(t)
        if m == last_ms:
            continue
        last_ms = m
        if kind == "float":
            val = {"type": "float", "value": round(v[0], 4)}
        elif kind == "vector3":
            val = {"type": "vector3", "value": [round(c, 3) for c in v]}
        elif kind == "quaternion":
            n = math.sqrt(sum(c * c for c in v))
            val = {"type": "quaternion", "value": [round(c / n, 7) for c in v]}
        out.append({"id": f"{prefix}-{i}", "layerTime": m, "value": val, "easing": {"type": "linear"}})
    return out


def ease_kf(prefix, keys, kind="float"):
    """keys: list of (t, value, easing) with easing a tuple bezier (x1,y1,x2,y2) or 'hold' or 'linear'."""
    out = []
    for i, (t, v, e) in enumerate(keys):
        if e == "hold":
            ez = {"type": "hold"}
        elif e == "linear":
            ez = {"type": "linear"}
        else:
            ez = {"type": "cubicBezier", "x1": e[0], "y1": e[1], "x2": e[2], "y2": e[3]}
        if kind == "float":
            val = {"type": "float", "value": v}
        elif kind == "vector3":
            val = {"type": "vector3", "value": list(v)}
        elif kind == "vector2":
            val = {"type": "vector2", "value": list(v)}
        else:
            val = v
        out.append({"id": f"{prefix}-{i}", "layerTime": ms(t), "value": val, "easing": ez})
    return out


# Named easing curves (cubic-bezier control points)
EASE_OUT = (0.16, 1.0, 0.30, 1.0)
EASE_IN_OUT = (0.65, 0.0, 0.35, 1.0)
EASE_IN = (0.55, 0.0, 0.90, 0.40)
OVERSHOOT = (0.34, 1.45, 0.50, 1.0)
SNAP = (0.08, 0.95, 0.20, 1.0)
