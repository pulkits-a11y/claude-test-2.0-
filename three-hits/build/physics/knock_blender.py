"""The China stack loses its top box (Blender Bullet). Run with the bpy venv: python knock_blender.py <out dir>

The top box of the 4-stack is hit on its left side on "down" (MG 1.03 s, frame 31): a short kinematic shove hands it
~1.2 m/s to the right with a clockwise spin; it tips off the stack, falls and lands flat at the edge of the light
to the right. The three boxes below are static here (their wobble is added in the build). Writes knock_track.json:
per-frame world transforms of the top box (Blender axes, metres) for frames F0..F_END.
"""
import json
import math
import sys

import bpy
from mathutils import Euler, Quaternion, Vector

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
from layout import STATIONS, stack_boxes  # noqa: E402

OUT = sys.argv[-1] if len(sys.argv) > 1 else "."
FPS = 30
F_HIT = 31
F0, F_END = F_HIT - 6, 194
W, D, H = 0.338, 0.208, 0.122

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F0, F_END
bpy.ops.rigidbody.world_add()
rw = sc.rigidbody_world
rw.substeps_per_frame = 16
rw.solver_iterations = 40
rw.point_cache.frame_start = F0
rw.point_cache.frame_end = F_END


def body(name, size, loc, quat, kind, mass=0.9, friction=0.5, restitution=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = quat
    bpy.ops.rigidbody.object_add(type=kind)
    rb = o.rigid_body
    rb.collision_shape = "BOX"
    rb.friction = friction
    rb.restitution = restitution
    rb.collision_margin = 0.001
    if kind == "ACTIVE":
        rb.mass = mass
        rb.linear_damping = 0.05
        rb.angular_damping = 0.15
    return o


body("Floor", (30, 10, 0.1), (3, 0, -0.05), Quaternion(), "PASSIVE", friction=0.55)
boxes = stack_boxes("china")
objs = []
for k, (c, yaw) in enumerate(boxes):
    loc = Vector((c[0] / 1000, c[2] / 1000, -c[1] / 1000))
    q = Euler((0, 0, math.radians(yaw)), "XYZ").to_quaternion()
    top = k == len(boxes) - 1
    o = body(f"China{k + 1}", (W - (0.002 if top else 0), D, H), loc, q, "ACTIVE" if top else "PASSIVE")
    objs.append((o, loc, q))

top, p0, q0 = objs[-1]
# the hit: shove right (+X), a touch toward camera, slight lift; clockwise spin as seen from the camera (+Y axis)
v = Vector((1.20, -0.25, 0.05))
w = Vector((0.5, 4.0, -1.4))


def key(o, f, loc, quat, kin):
    sc.frame_set(f)
    o.location = loc
    o.rotation_quaternion = quat
    o.keyframe_insert("location", frame=f)
    o.keyframe_insert("rotation_quaternion", frame=f)
    o.rigid_body.kinematic = kin
    o.rigid_body.keyframe_insert("kinematic", frame=f)


dt = 2.0 / FPS
key(top, F0, p0, q0, True)
key(top, F_HIT - 2, p0, q0, True)
key(top, F_HIT, p0 + v * dt, Quaternion(w.normalized(), w.length * dt) @ q0, True)
sc.frame_set(F_HIT + 1)
top.rigid_body.kinematic = False
top.rigid_body.keyframe_insert("kinematic", frame=F_HIT + 1)
ad = top.animation_data
try:
    fcs = list(ad.action.fcurves)
except AttributeError:
    fcs = [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
for fc in fcs:
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

track = {"fps": FPS, "hit_frame": F_HIT, "frames": {}}
for f in range(F0, F_END + 1):
    sc.frame_set(f)
    m = top.matrix_world
    q = m.to_quaternion()
    t = m.translation
    track["frames"][f] = {"pos": [t.x, t.y, t.z], "quat": [q.x, q.y, q.z, q.w]}
json.dump(track, open(f"{OUT}/knock_track.json", "w"))
for f in (F_HIT, F_HIT + 4, F_HIT + 8, F_HIT + 12, F_HIT + 18, F_HIT + 26, F_HIT + 40, F_END):
    r = track["frames"][f]
    up = Quaternion((r["quat"][3], r["quat"][0], r["quat"][1], r["quat"][2])) @ Vector((0, 0, 1))
    print(f"f{f} pos=({r['pos'][0]:+.3f},{r['pos'][1]:+.3f},{r['pos'][2]:+.3f}) up.z={up.z:+.2f}")
