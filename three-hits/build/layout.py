"""Stage layout and the one continuous camera move.

One long dark stage along +X. Three stations, each in its own warm spotlight pool:
  TARIFF   one box (x = 0)
  CHINA    a stack of 4 (x = 1250); the top box is knocked off on "down"
  ROW      2025 / 2026 / 2027 / 2028 stacks of 5 / 5 / 4 / 4 (x = 2800 ... 5050); the light dims down the row
Units: mm, Scene3D axes (X right, Y down, Z away from camera). Floor at y = 0.
"""
import math
import random

from common import T, hermite_path, smootherstep

BOX = {"w": 338, "d": 208, "h": 122}          # whole box incl. the overhanging lid (same model as the Shoebox Tower)
PITCH = 122

STATIONS = {
    # light = perceived brightness of the station; power = the spotlight power factor that gives it on screen
    # (the renderer's tone curve compresses: 30% brightness needs ~10% power)
    "tariff": {"x": 0, "z": 0, "n": 1, "yaw": 7.0, "light": 1.00, "power": 0.85},   # close-up: a touch less so the lid and ink do not clip
    "china": {"x": 1250, "z": 120, "n": 4, "yaw": 24.0, "light": 1.00, "power": 1.0},   # turned to the camera: three-quarter view
    "y2025": {"x": 2800, "z": 260, "n": 5, "yaw": 2.0, "light": 1.00, "power": 1.0, "label": "2025"},
    "y2026": {"x": 3550, "z": 260, "n": 5, "yaw": -3.0, "light": 0.80, "power": 0.66, "label": "2026"},
    "y2027": {"x": 4300, "z": 260, "n": 4, "yaw": 3.5, "light": 0.55, "power": 0.31, "label": "2027"},
    "y2028": {"x": 5050, "z": 260, "n": 4, "yaw": -1.5, "light": 0.30, "power": 0.09, "label": "2028"},
}
ROW = ["y2025", "y2026", "y2027", "y2028"]


def stack_boxes(key):
    """Hand-placed stack: per box (centre [x, y, z], yaw degrees). Tiny offsets and +-0.5-1.5 deg turns."""
    st = STATIONS[key]
    rnd = random.Random(sum(ord(c) * (i + 1) for i, c in enumerate(key)))   # deterministic across processes
    out = []
    for k in range(st["n"]):
        dx = rnd.uniform(-6, 6) if k else 0.0
        dz = rnd.uniform(-5, 5) if k else 0.0
        dyaw = rnd.choice([-1, 1]) * rnd.uniform(0.5, 1.5) if k else 0.0
        out.append(([st["x"] + dx, -(k * PITCH + BOX["h"] / 2), st["z"] + dz], st["yaw"] + dyaw))
    return out


# ---------------------------------------------------------------- camera
# Keys are (time, position, look-at). Catmull-Rom between them; pairs of close keys make it ease out into a
# station and glide on, so the move never stops and never runs at constant speed.
CAM_KEYS = [
    (0.00, [-470, -300, -690], [15, -95, 10]),       # low, close three-quarter on the TARIFF box
    (0.30, [-462, -298, -684], [18, -95, 10]),       # drifts through the hit (no shake)
    (0.50, [-420, -304, -700], [70, -100, 20]),      # eases into the track right
    (0.80, [700, -360, -1180], [1250, -205, 110]),
    (1.02, [1080, -390, -1330], [1400, -215, 130]),  # arrives on the China stack, space to its right for -26%
    (1.31, [1086, -390, -1322], [1403, -215, 130]),
    (1.95, [1110, -386, -1250], [1410, -215, 130]),  # slight push-in with "-26%"
    (3.30, [1128, -384, -1225], [1416, -215, 130]),  # slow drift while the line finishes
    (3.70, [1950, -540, -1950], [2200, -260, 260]),  # pulls back, rises a little, tracks right, parallel to the row
    (4.25, [2750, -560, -1950], [3000, -255, 260]),
    (4.85, [3450, -555, -1900], [3700, -252, 260]),
    (5.30, [3980, -545, -1850], [4230, -250, 260]),  # slows, dragging toward 2028
    (5.95, [4500, -520, -1700], [4730, -250, 260]),
    (6.47, [4640, -505, -1560], [4850, -248, 260]),  # slow push-in on 2028, still drifting at the cut
]


def cam(t):
    P = hermite_path([(k[0], k[1]) for k in CAM_KEYS], t)
    L = hermite_path([(k[0], k[2]) for k in CAM_KEYS], t)
    return P, L
