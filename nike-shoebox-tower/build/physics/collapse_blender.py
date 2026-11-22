"""Rigid-body collapse of the shoebox tower, simulated with Blender's Bullet solver.

Run with the bpy venv:  python collapse_blender.py <dir with layout.json>
Writes collapse_track.json: per-frame world transforms (Blender axes, metres) of boxes 7..28
from the frame the collapse starts (on "Less", 7.30 s) to the end of the street section.
"""
import json
import math
import random
import sys

import bpy
from mathutils import Euler, Quaternion, Vector

D = sys.argv[-1] if len(sys.argv) > 1 else "."
lay = json.load(open(f"{D}/layout.json"))
W, DEP, H = lay["box_dims"]
boxes = lay["boxes"]
N = len(boxes)
KEEP = 6                       # boxes left standing
FPS = 30
F0 = int(round(7.30 * FPS))    # 219: collapse starts on "Less"
F_END = int(round(10.95 * FPS))
rng = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F0 - 4, F_END
bpy.ops.rigidbody.world_add()
rw = sc.rigidbody_world
rw.substeps_per_frame = 12
rw.solver_iterations = 30
rw.point_cache.frame_start = F0 - 4
rw.point_cache.frame_end = F_END


def collider(name, size, loc, friction=0.55, shape="BOX", radius=None, depth=None):
    if shape == "BOX":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        o = bpy.context.object
        o.scale = size
    else:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, vertices=24)
        o = bpy.context.object
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.rigidbody.object_add(type="PASSIVE")
    o.rigid_body.collision_shape = shape if shape == "BOX" else "CYLINDER"
    o.rigid_body.friction = friction
    o.rigid_body.restitution = 0.05
    o.rigid_body.collision_margin = 0.001
    return o


# Street colliders (Blender axes: Y away from camera; Tesseract z = 1000*Y)
collider("Sidewalk", (9.0, 3.6, 0.15), (0, 1.1, -0.075))
collider("Kerb", (9.0, 0.17, 0.16), (0, -0.615, -0.07))
collider("Asphalt", (14.0, 7.0, 0.04), (0, -4.2, -0.17))
collider("Lamp base", None, (1.15, -0.26, 0.08), shape="CYL", radius=0.055, depth=0.16)
collider("Lamp post", None, (1.15, -0.26, 1.26), shape="CYL", radius=0.022, depth=2.2)

objs = []
for i, b in enumerate(boxes):
    z_c = b["z_bottom"] + H / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(b["dx"], b["dy"], z_c))
    o = bpy.context.object
    o.name = f"Box{i + 1:02d}"
    o.scale = (W, DEP, H)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Euler((0, 0, math.radians(b["yaw_deg"])), "XYZ").to_quaternion()
    bpy.ops.rigidbody.object_add(type="PASSIVE" if i < KEEP else "ACTIVE")
    rb = o.rigid_body
    rb.collision_shape = "BOX"
    rb.friction = 0.5
    rb.restitution = 0.08
    rb.collision_margin = 0.001
    if i >= KEEP:
        rb.mass = 0.45
        rb.linear_damping = 0.05
        rb.angular_damping = 0.18
    objs.append(o)


def key_kinematic(o, f, loc, quat, kin):
    sc.frame_set(f)
    o.location = loc
    o.rotation_quaternion = quat
    o.keyframe_insert("location", frame=f)
    o.keyframe_insert("rotation_quaternion", frame=f)
    o.rigid_body.kinematic = kin
    o.rigid_body.keyframe_insert("kinematic", frame=f)


# Failure choreography: the tower breaks in two places. The top section (17-28) hinges over its
# left edge and topples left/toward camera first; a few frames later the middle section (7-16)
# tips over the right edge of box 6 and falls right/back. Velocities are the rigid rotation of
# each section about its hinge, handed to the solver over the last two kinematic frames.
SECTIONS = [
    # (first, last, hinge point, rotation axis, angular speed rad/s, release frame offset)
    (16, N - 1, Vector((-W / 2, 0.0, 16 * H)), Vector((0.30, -1.0, 0.0)).normalized(), 1.55, 0),
    (KEEP, 15, Vector((W / 2, 0.0, KEEP * H)), Vector((-0.25, 1.0, 0.0)).normalized(), 1.25, 5),
]
for first, last, hinge, axis, speed, off in SECTIONS:
    for i in range(first, last + 1):
        o = objs[i]
        b = boxes[i]
        rel = F0 + off + (last - i) // 4         # within a section the break still runs top-down
        p_rest = Vector((b["dx"], b["dy"], b["z_bottom"] + H / 2))
        q_rest = Euler((0, 0, math.radians(b["yaw_deg"])), "XYZ").to_quaternion()
        w_ang = axis * speed * rng.uniform(0.9, 1.1)
        v = w_ang.cross(p_rest - hinge)
        v += Vector((rng.uniform(-0.06, 0.06), rng.uniform(-0.08, 0.08), 0.0))
        w_ang += Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.3, 0.3), rng.uniform(-0.8, 0.8)))
        if i >= N - 2:                            # the very top box gives way first, a touch harder
            v *= 1.1
        if i == KEEP:                             # the box on the break line is kicked clear of box 6
            v += Vector((0.95, 0.12, 0.35))
            w_ang += Vector((0.0, 3.0, -0.6))
        dt = 2.0 / FPS
        p_rel = p_rest + v * dt
        q_rel = Quaternion(w_ang.normalized(), w_ang.length * dt) @ q_rest
        key_kinematic(o, F0 - 4, p_rest, q_rest, True)
        key_kinematic(o, rel - 2, p_rest, q_rest, True)
        key_kinematic(o, rel, p_rel, q_rel, True)
        sc.frame_set(rel + 1)
        o.rigid_body.kinematic = False
        o.rigid_body.keyframe_insert("kinematic", frame=rel + 1)
        ad = o.animation_data
        if ad and ad.action:
            try:
                fcs = list(ad.action.fcurves)
            except AttributeError:
                fcs = [fc for layer in ad.action.layers for strip in layer.strips
                       for bag in strip.channelbags for fc in bag.fcurves]
            for fc in fcs:
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"

track = {"fps": FPS, "start_frame": F0, "end_frame": F_END, "keep": KEEP, "frames": {}}
for f in range(F0 - 4, F_END + 1):
    sc.frame_set(f)
    if f < F0:
        continue
    fr = []
    for o in objs:
        m = o.matrix_world
        q = m.to_quaternion()
        t = m.translation
        fr.append({"pos": [t.x, t.y, t.z], "quat": [q.x, q.y, q.z, q.w]})
    track["frames"][f] = fr

json.dump(track, open(f"{D}/collapse_track.json", "w"))
last = track["frames"][F_END]
print("final resting positions (x,y,z):")
for i, r in enumerate(last):
    up = Quaternion((r["quat"][3], r["quat"][0], r["quat"][1], r["quat"][2])) @ Vector((0, 0, 1))
    print(f"  box {i + 1:2d}: ({r['pos'][0]:+.2f}, {r['pos'][1]:+.2f}, {r['pos'][2]:+.3f})  up.z={up.z:+.2f}")
