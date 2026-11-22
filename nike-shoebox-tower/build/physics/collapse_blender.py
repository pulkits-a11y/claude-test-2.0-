"""Rigid-body collapse of the shoebox tower, simulated with Blender's Bullet solver.

Run with the bpy venv:  python collapse_blender.py <dir with layout.json> [seed] [lid_threshold] [out.json]
Writes collapse_track.json: per-frame world transforms (Blender axes, metres) from the frame the collapse
starts (on "Less", 7.30 s) to the end of the street section:
  frames[f][k]      = {"pos", "quat"}  box k's centre (the whole box incl. lid), as before
  lids[f][k]        = {"pos", "quat"}  box k's lid centre, for the boxes that fall (k >= KEEP)
Each falling box is two bodies: the base, and the lid (a 10 mm top plate) held on by a breakable fixed
constraint, so lids come off only on hard impacts. The break runs top-down: each box is released on its own
frame with its own push and spin, so the stack separates instead of swinging as one hinged column.
"""
import json
import math
import random
import sys

import bpy
from mathutils import Euler, Quaternion, Vector

args = [a for a in sys.argv[1:] if not a.startswith("-")]
D = args[0] if args else "."
SEED = int(args[1]) if len(args) > 1 else 7
LID_BREAK = float(args[2]) if len(args) > 2 else 2.2
OUT = args[3] if len(args) > 3 else f"{D}/collapse_track.json"
lay = json.load(open(f"{D}/layout.json"))
W, DEP, H = lay["box_dims"]                 # whole box: 0.338 x 0.208 x 0.122
boxes = lay["boxes"]
N = len(boxes)
KEEP = 6                                    # boxes left standing
FPS = 30
F0 = int(round(7.30 * FPS))                 # 219: collapse starts on "Less"
F_END = int(round(10.95 * FPS))
rng = random.Random(SEED)
BASE_W, BASE_D, BASE_H, BASE_DZ = 0.330, 0.200, 0.112, -0.005   # base body, centre 5 mm below the box centre
PLATE_H = 0.010
PLATE_DZ = H / 2 - PLATE_H / 2                                    # lid top plate centre above the box centre
LID_VIS_DZ = 0.046                                                # visual lid centre above the box centre

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F0 - 4, F_END
bpy.ops.rigidbody.world_add()
rw = sc.rigidbody_world
rw.substeps_per_frame = 16
rw.solver_iterations = 40
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


def body(name, size, loc, quat, active, mass=0.45, friction=0.5, restitution=0.1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = quat
    bpy.ops.rigidbody.object_add(type="ACTIVE" if active else "PASSIVE")
    rb = o.rigid_body
    rb.collision_shape = "BOX"
    rb.friction = friction
    rb.restitution = restitution
    rb.collision_margin = 0.001
    if active:
        rb.mass = mass
        rb.linear_damping = 0.04
        rb.angular_damping = 0.2
    return o


# Street colliders (Blender axes: Y away from camera; Tesseract z = 1000*Y)
collider("Sidewalk", (9.0, 3.6, 0.15), (0, 1.1, -0.075))
collider("Kerb", (9.0, 0.17, 0.16), (0, -0.615, -0.07))
collider("Asphalt", (14.0, 7.0, 0.04), (0, -4.2, -0.17))
collider("Lamp base", None, (1.15, -0.26, 0.08), shape="CYL", radius=0.055, depth=0.16)
collider("Lamp post", None, (1.15, -0.26, 1.26), shape="CYL", radius=0.022, depth=2.2)

bases, lids, rest = [], {}, []
for i, b in enumerate(boxes):
    c = Vector((b["dx"], b["dy"], b["z_bottom"] + H / 2))
    q = Euler((0, 0, math.radians(b["yaw_deg"])), "XYZ").to_quaternion()
    rest.append((c, q))
    up = q @ Vector((0, 0, 1))
    if i < KEEP:
        o = body(f"Box{i + 1:02d}", (W, DEP, H), c, q, False)
        bases.append(o)
        continue
    o = body(f"Base{i + 1:02d}", (BASE_W, BASE_D, BASE_H), c + up * BASE_DZ, q, True, mass=0.9, friction=0.62, restitution=0.06)
    bases.append(o)
    lid = body(f"Lid{i + 1:02d}", (W, DEP, PLATE_H), c + up * PLATE_DZ, q, True, mass=0.07, friction=0.55, restitution=0.12)
    lids[i] = lid
    bpy.ops.object.empty_add(location=c + up * (BASE_H / 2 + BASE_DZ))
    e = bpy.context.object
    e.name = f"LidJoint{i + 1:02d}"
    bpy.ops.rigidbody.constraint_add()
    rc = e.rigid_body_constraint
    rc.type = "FIXED"
    rc.object1, rc.object2 = o, lid
    rc.disable_collisions = False
    rc.use_breaking = True
    rc.breaking_threshold = LID_BREAK * rng.uniform(0.8, 1.25)


def set_lin(o):
    ad = o.animation_data
    if ad and ad.action:
        try:
            fcs = list(ad.action.fcurves)
        except AttributeError:
            fcs = [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
        for fc in fcs:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def key_kin(o, f, loc, quat, kin):
    sc.frame_set(f)
    o.location = loc
    o.rotation_quaternion = quat
    o.keyframe_insert("location", frame=f)
    o.keyframe_insert("rotation_quaternion", frame=f)
    o.rigid_body.kinematic = kin
    o.rigid_body.keyframe_insert("kinematic", frame=f)


def release(o, f_rel, p, q, v, w):
    """Hold o kinematic at rest, then move it rigidly with (v, w) over the last two frames and let go."""
    dt = 2.0 / FPS
    key_kin(o, F0 - 4, p, q, True)
    key_kin(o, f_rel - 2, p, q, True)
    key_kin(o, f_rel, p + v * dt, Quaternion(w.normalized(), w.length * dt) @ q if w.length > 1e-6 else q, True)
    sc.frame_set(f_rel + 1)
    o.rigid_body.kinematic = False
    o.rigid_body.keyframe_insert("kinematic", frame=f_rel + 1)
    set_lin(o)


# Failure choreography. The top gives way first (box 28 on "Less") and the break runs down the stack, one
# box every ~0.7 frames. Upper boxes are shoved left/toward camera, the middle of the stack buckles right/back,
# each with its own speed, heading and spin so they separate in the air.
TOP_FIRST, SPLIT = N - 1, 16
for i in range(N - 1, KEEP - 1, -1):
    c, q = rest[i]
    h = (i - KEEP + 1) / (N - KEEP)                       # 0..1 up the falling part
    if i >= SPLIT:
        f_rel = F0 + int(round((N - 1 - i) * 0.7))
        heading = math.radians(rng.uniform(178, 212))       # left, a little toward camera
        speed = (0.25 + 0.75 * h) * rng.uniform(0.75, 1.25)
    else:
        f_rel = F0 + 6 + int(round((SPLIT - 1 - i) * 0.9))
        heading = math.radians(rng.uniform(-20, 35))        # right, a little away from camera
        speed = (0.35 + 0.7 * h) * rng.uniform(0.75, 1.25)
    v = Vector((math.cos(heading) * speed, math.sin(heading) * speed, rng.uniform(-0.05, 0.25)))
    w = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))).normalized() * rng.uniform(1.5, 5.5)
    if i == KEEP:                                          # the box on the break line is kicked clear of box 6
        v += Vector((0.95, 0.12, 0.35))
        w += Vector((0.0, 3.0, -0.6))
    up = q @ Vector((0, 0, 1))
    release(bases[i], f_rel, c + up * BASE_DZ, q, v + w.cross(up * BASE_DZ), w)
    release(lids[i], f_rel, c + up * PLATE_DZ, q, v + w.cross(up * PLATE_DZ), w)


def pose(o, dz):
    m = o.matrix_world
    q = m.to_quaternion()
    t = m.translation + q @ Vector((0, 0, dz))
    return {"pos": [t.x, t.y, t.z], "quat": [q.x, q.y, q.z, q.w]}


track = {"fps": FPS, "start_frame": F0, "end_frame": F_END, "keep": KEEP, "seed": SEED, "lid_break": LID_BREAK,
         "frames": {}, "lids": {}}
speeds = {}
prev = None
for f in range(F0 - 4, F_END + 1):
    sc.frame_set(f)
    if f < F0:
        continue
    fr = [pose(o, 0.0 if i < KEEP else -BASE_DZ) for i, o in enumerate(bases)]
    track["frames"][f] = fr
    track["lids"][f] = {i: pose(l, LID_VIS_DZ - PLATE_DZ) for i, l in lids.items()}
    if prev is not None:
        speeds[f] = max((Vector(a["pos"]) - Vector(b["pos"])).length * FPS for a, b in zip(fr[KEEP:], prev[KEEP:]))
    prev = fr

json.dump(track, open(OUT, "w"))

# ------------------------------------------------------------------ quality report (for the seed search)
last = track["frames"][F_END]
last_l = track["lids"][F_END]
on_end = on_stack = elevated = off = 0
left = right = 0
lids_off = 0
for i in range(KEEP, N):
    r = last[i]
    qq = Quaternion((r["quat"][3], r["quat"][0], r["quat"][1], r["quat"][2]))
    xax = qq @ Vector((1, 0, 0))
    p = Vector(r["pos"])
    if abs(xax.z) > 0.7:
        on_end += 1
    if abs(p.x) < 0.25 and abs(p.y) < 0.16 and p.z > KEEP * H:
        on_stack += 1
    ground = 0.0 if p.y > -0.7 else -0.15
    if p.z - ground > 0.19:
        elevated += 1
    if abs(p.x) > 2.6 or p.y < -2.0:
        off += 1
    left += p.x < -0.25
    right += p.x > 0.25
    lp = Vector(last_l[i]["pos"])
    lq = Quaternion((last_l[i]["quat"][3], last_l[i]["quat"][0], last_l[i]["quat"][1], last_l[i]["quat"][2]))
    rel = qq.inverted() @ (lp - p)
    if (rel - Vector((0, 0, LID_VIS_DZ))).length > 0.025 or (qq.rotation_difference(lq).angle > 0.25):
        lids_off += 1
settle = next((f for f in sorted(speeds) if f > F0 + 20 and all(speeds[g] < 0.08 for g in speeds if g >= f)), F_END)
rep = {"seed": SEED, "lid_break": LID_BREAK, "on_end": on_end, "on_stack": on_stack, "elevated": elevated, "off": off,
       "left": left, "right": right, "lids_off": lids_off, "settle_frame": settle}
print("REPORT " + json.dumps(rep))
