"""Stockroom wall: the orange box is shoved out of its slot and falls toward camera (Blender Bullet).

Boxes are stacked end-out against a back wall: in Blender axes a box's long side runs along +Y
(away from camera). The visible grid is 10 x 10; two extra columns either side continue into the
darkness so the row can close its gap. Writes wall_layout.json and wall_track.json.
"""
import json
import math
import random
import sys

import bpy
from mathutils import Euler, Quaternion, Vector

D = sys.argv[-1] if len(sys.argv) > 1 else "."
FPS = 30
BW, BD, BH = 0.208, 0.338, 0.122          # end-out: width X = box depth, depth Y = box length
PITCH_X = BW + 0.003                       # 3 mm seams between neighbouring boxes
COLS, ROWS, EXTRA = 10, 10, 2
NCOL = COLS + 2 * EXTRA
FRONT_Y = 0.0                             # front face of the wall of boxes
ORANGE = (EXTRA + 5, 5)                   # (column, row): just right of centre, row 6 of 10
F_KICK = int(round(11.43 * FPS))          # "kicked"
F_END = 399
rng = random.Random(100)

layout = []
for r in range(ROWS):
    for c in range(NCOL):
        layout.append({"col": c, "row": r,
                       "x": (c - (NCOL - 1) / 2) * PITCH_X + rng.uniform(-0.001, 0.001),
                       "y": FRONT_Y + BD / 2 + rng.uniform(-0.004, 0.006),
                       "z": r * BH + BH / 2,
                       "yaw_deg": rng.uniform(-0.3, 0.3)})

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F_KICK - 10, F_END
bpy.ops.rigidbody.world_add()
rw = sc.rigidbody_world
rw.substeps_per_frame = 12
rw.solver_iterations = 30
rw.point_cache.frame_start = F_KICK - 10
rw.point_cache.frame_end = F_END

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.0, -0.05))
floor = bpy.context.object
floor.scale = (12, 8, 0.1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.rigidbody.object_add(type="PASSIVE")
floor.rigid_body.friction = 0.6

target = None
for b in layout:
    if (b["col"], b["row"]) != ORANGE and abs(b["col"] - ORANGE[0]) > 1 and abs(b["row"] - ORANGE[1]) > 1:
        continue      # only neighbours matter for contact
    bpy.ops.mesh.primitive_cube_add(size=1, location=(b["x"], b["y"], b["z"]))
    o = bpy.context.object
    is_target = (b["col"], b["row"]) == ORANGE
    o.scale = (BW - (0.004 if is_target else 0.0), BD, BH)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Euler((0, 0, math.radians(b["yaw_deg"] if not is_target else 0.0))).to_quaternion()
    bpy.ops.rigidbody.object_add(type="ACTIVE" if is_target else "PASSIVE")
    o.rigid_body.collision_shape = "BOX"
    o.rigid_body.friction = 0.45
    o.rigid_body.collision_margin = 0.001
    if is_target:
        target, tb = o, b
        o.rigid_body.mass = 0.45
        o.rigid_body.angular_damping = 0.12

# Kinematic shove: anticipation (tiny lift, eased back 4 mm), then a hard push forward (-Y)
p0 = Vector((tb["x"], tb["y"], tb["z"]))
q0 = target.rotation_quaternion.copy()
keys = [  # (frame offset from kick, dy, yaw deg). Anticipation: eased back 4 mm, then a hard shove (-Y)
    (-8, 0.000, 0.0),
    (-3, 0.004, 0.0),
    (0, 0.003, 0.0),
    (3, -0.055, 0.0),
    (6, -0.155, 0.0),
    (9, -0.280, 0.0),
    (10, -0.328, 0.0),
]
for off, dy, yaw in keys:
    f = F_KICK + off
    sc.frame_set(f)
    target.location = p0 + Vector((0, dy, 0.0))
    target.rotation_quaternion = Quaternion((0, 0, 1), math.radians(yaw)) @ q0
    target.keyframe_insert("location", frame=f)
    target.keyframe_insert("rotation_quaternion", frame=f)
    target.rigid_body.kinematic = True
    target.rigid_body.keyframe_insert("kinematic", frame=f)
ad = target.animation_data
try:
    fcs = list(ad.action.fcurves)
except AttributeError:
    fcs = [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
for fc in fcs:            # linear keys so the shove keeps its speed through the hand-off
    if fc.data_path in ("location", "rotation_quaternion"):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
sc.frame_set(F_KICK + 11)
target.rigid_body.kinematic = False
target.rigid_body.keyframe_insert("kinematic", frame=F_KICK + 11)

track = {"fps": FPS, "kick_frame": F_KICK, "frames": {}}
for f in range(F_KICK - 10, F_END + 1):
    sc.frame_set(f)
    m = target.matrix_world
    q = m.to_quaternion()
    t = m.translation
    track["frames"][f] = {"pos": [t.x, t.y, t.z], "quat": [q.x, q.y, q.z, q.w]}

json.dump({"box": [BW, BD, BH], "pitch_x": PITCH_X, "cols": COLS, "rows": ROWS, "extra": EXTRA, "front_y": FRONT_Y,
           "orange": ORANGE, "boxes": layout}, open(f"{D}/wall_layout.json", "w"), indent=1)
json.dump(track, open(f"{D}/wall_track.json", "w"))
for f in (F_KICK, F_KICK + 6, F_KICK + 9, F_KICK + 12, F_KICK + 16, F_KICK + 20, F_KICK + 26, F_KICK + 34):
    r = track["frames"][f]
    print(f"f{f} t={f / FPS:.2f}s pos=({r['pos'][0]:+.3f},{r['pos'][1]:+.3f},{r['pos'][2]:+.3f})")
