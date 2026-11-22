"""Shared timing, camera paths, projection and keyframe helpers for the Shoebox Tower MG.

Scene3D axes: X right, Y DOWN, Z into the screen; pixels; pixelsPerMeter = 1000 (1 px = 1 mm).
Physics (Blender) axes: X right, Y away from camera, Z up; metres.
"""
import json
import math
import os

FPS = 30
DUR = 13.30
NFRAMES = 399
W, H = 1920, 1080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHYS = os.path.join(ROOT, "build", "physics")

# ---------------------------------------------------------------- confirmed VO beats (MG seconds)
T = {
    "more_than": 0.30, "anyone": 0.83, "card_out": (1.36, 1.64),
    "y2021": 1.99, "stamp_move": (2.42, 2.86),
    "nike": 2.90, "lock280": None,                  # filled from rise landing times
    "slow": (6.40, 6.55), "today": 6.55, "less": 7.30, "lock60": 8.10,
    "ghost": (9.00, 9.70), "minus80": 9.92, "wipe": (10.78, 11.00),
    "sp_label": 11.04, "kick": 11.43, "gap_closed": 12.60, "end": 13.30,
}
STREET_END = 11.05    # street scene layers stop after the wipe
WALL_START = 10.70

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


# ---------------------------------------------------------------- "Today?" time-break
def story_time(t):
    """Camera/haze clock: runs at 1x, ramps to ~5% over 6.40-6.55, creeps, snaps back on 'Less'."""
    a, b = T["slow"]
    less = T["less"]
    if t <= a:
        return t
    # integrate speed s(t): 1 -> 0.05 over [a,b] (smootherstep), 0.05 until less, then 1
    def speed(x):
        if x < a:
            return 1.0
        if x < b:
            return 1.0 - 0.95 * smootherstep(a, b, x)
        if x < less:
            return 0.05
        return 1.0
    n = 200
    acc = a
    x0 = a
    end = min(t, less)
    for k in range(n):
        x1 = a + (end - a) * (k + 1) / n
        acc += 0.5 * (speed(x0) + speed(x1)) * (x1 - x0)
        x0 = x1
    if t > less:
        acc += t - less
    return acc


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


# Street camera control poses (time, position, look-at). Tower at the origin, ground at y = 0.
LAMP = {"x": 1150, "z": -260, "head_y": -2380}  # vintage lamp: right of the tower, slightly in front (= physics collider)

STREET_KEYS_P = [
    (0.00, [470, -420, -2700]),     # low, looking slightly down: the wet sidewalk reads as a surface, the street below
    (2.90, [440, -405, -2580]),     # slow push-in on the empty pool of light
    (3.45, [600, -380, -2800]),
    (4.13, [1000, -330, -3600]),    # pulls back, swings right and sinks as the stack climbs (box 28 lands 5.40)
    (4.60, [1500, -290, -4400]),
    (5.40, [1950, -265, -5000]),
    (6.40, [2100, -255, -5250]),    # heroic low three-quarter angle: 26 mm, lens 25 cm off the sidewalk, tilted up
    (6.80, [2110, -255, -5290]),    # story-time drift target through "Today?"
]
STREET_KEYS_L = [
    (0.00, [130, -150, 0]),
    (2.90, [115, -160, 0]),
    (3.45, [40, -420, 0]),
    (4.13, [20, -880, 0]),
    (4.60, [0, -1250, 0]),
    (5.40, [0, -1520, 0]),
    (6.40, [0, -1546, 0]),
    (6.80, [0, -1550, 0]),
]
# lens: 35 mm, widening to 26 mm as the tower tops out (stronger low-angle perspective), back to 35 mm as the
# camera follows the collapse down
FOCAL_KEYS = [(0.0, 35.0), (4.13, 35.0), (5.40, 26.0), (7.30, 26.0), (8.10, 35.0)]


def street_focal(t):
    for (t0, f0), (t1, f1) in zip(FOCAL_KEYS, FOCAL_KEYS[1:]):
        if t <= t1:
            return f0 + (f1 - f0) * smootherstep(t0, t1, t)
    return FOCAL_KEYS[-1][1]
POST_P = [
    (7.62, [1500, -420, -5600]),
    (8.10, [900, -430, -3300]),
    (8.75, [690, -440, -2600]),     # eye level on the six boxes
    (9.00, [700, -460, -2640]),
    (9.75, [1450, -1250, -7500]),   # pull back and crane up: the emptiness above
    (10.30, [1420, -1230, -7250]),  # small push-in on "80 percent"
    (11.05, [1440, -1240, -7280]),
]
POST_L = [
    (7.62, [0, -1350, 0]),
    (8.10, [0, -720, 0]),
    (8.75, [0, -430, 0]),
    (9.00, [0, -440, 0]),
    (9.75, [0, -1640, 0]),
    (10.30, [0, -1640, 0]),
    (11.05, [0, -1645, 0]),
]


def street_cam(t):
    if t < T["less"]:
        st = story_time(t)
        P = hermite_path(STREET_KEYS_P, st)
        L = hermite_path(STREET_KEYS_L, st)
    else:
        st0 = story_time(T["less"])
        p0, l0 = hermite_path(STREET_KEYS_P, st0), hermite_path(STREET_KEYS_L, st0)
        P = hermite_path([(T["less"], p0)] + POST_P, t)
        L = hermite_path([(T["less"], l0)] + POST_L, t)
    # tiny decaying shake on the heaviest collapse impact (about 1-2 px on screen)
    tau = t - 8.40
    if 0 <= tau < 0.4:
        a = 2.2 * math.exp(-tau / 0.09)
        P = [P[0] + a * math.sin(tau * 97), P[1] + a * 0.8 * math.sin(tau * 131 + 1.3), P[2]]
    return P, L, street_focal(t)


WALL_CAM = {"p0": [0, -774, -3330], "p1": [0, -776, -3030], "l0": [0, -774, 0], "l1": [0, -776, 0]}   # the whole 10 x 10 wall stays in frame


def wall_cam(t):
    u = smoothstep(WALL_START, T["end"] + 0.4, t)      # never fully stops before the cut
    u = 0.15 * u + 0.85 * (1 - (1 - u) ** 2)
    return lerp(WALL_CAM["p0"], WALL_CAM["p1"], u), lerp(WALL_CAM["l0"], WALL_CAM["l1"], u)


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
