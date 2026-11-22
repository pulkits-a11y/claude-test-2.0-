"""Street section (MG 0.00-11.05 s): four Scene3D layers sharing one camera path.

  Backdrop   (layer 10)  distant silhouettes, warm windows, far lamps: unlit, blurred into bokeh in 2D
  Street     (layer 11)  sidewalk, kerb, asphalt, vintage lamp, light shaft, 28 lit shoeboxes
  Reflection (layer 12)  mirrored boxes/lamp (unlit) + black hold-outs, ADD-blended onto the wet ground
  Ghost      (layer 13)  dashed outline of the original 28-box tower, drawn on from 9.00 s
"""
import math

from common import *
from lib import (COMP, aim, const, color_tex_input, scalar_tex_input, image_tex, noise_tex, hex_lin, hex_srgb,
                 material_slot, mesh_data, rot_euler, world_planar_mapping)

LAYER_BACK, LAYER_STREET, LAYER_REFL, LAYER_GHOST, LAYER_HAZE = 10, 11, 12, 13, 14
ORANGE_GAIN = 0.74   # keeps the lit orange below clipping so the cardboard keeps its modelling
STREET_MS = ms(STREET_END)
BOX_W, BOX_D = 330, 200
BASE = [330, 112, 200]
LID = [338, 30, 208]
SW_W = 140


class Ids:
    def __init__(self, start):
        self.n = start

    def __call__(self):
        self.n += 1
        return self.n


def scene_layer(layer_id, name, world, start_ms=0, dur_ms=STREET_MS):
    return {"type": "createFxScene3DLayer", "compositionId": COMP, "layerId": layer_id, "name": name, "insertIndex": 0,
            "pixelsPerMeter": 1000, "view": {"id": layer_id * 1000 + 9, "exposure": 0},
            "activeRange": {"start": start_ms, "duration": dur_ms},
            "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100},
            "world": world,
            "renderSettings": {"id": layer_id * 1000 + 97, "filmGate": None, "overscan": None, "lightGroups": [],
                               "lightCollections": [], "lightLinks": [], "outputs": [], "previewOutput": None}}


def camera_actions(layer_id, cam_id, cam_fn, t0, t1, tol_pos=0.05, tol_rot=0.004):
    """cam_fn(t) -> (P, L) or (P, L, focal_mm); a focal length that changes is keyed on the lens too."""
    c0 = cam_fn(t0)
    P0, L0 = c0[0], c0[1]
    q0, _ = look_quat(P0, L0)
    acts = [{"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": layer_id, "item": {
        "type": "Camera3D", "id": cam_id, "parentId": None, "name": "Camera 35mm",
        "transform": {"position": P0, "rotation": {"type": "quaternion", "value": q0}},
        "lens": {"type": "physical", "focalLengthMm": c0[2] if len(c0) > 2 else FOCAL_MM, "sensorMm": [36, 24], "fNumber": 2.8},
        "sensorFit": "horizontal"}},
        {"type": "setFxScene3DActiveCamera", "compositionId": COMP, "layerId": layer_id, "cameraItemId": cam_id}]
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    ps, qs, fs = [], [], []
    prev = None
    for f in range(f0, f1 + 1):
        t = f / FPS
        c = cam_fn(t)
        P, L = c[0], c[1]
        if len(c) > 2:
            fs.append((t - t0, [c[2]]))
        q, _ = look_quat(P, L)
        if prev and sum(a * b for a, b in zip(prev, q)) < 0:
            q = [-c for c in q]
        prev = q
        lt = t - t0
        ps.append((lt, P))
        qs.append((lt, q))
    acts.append(anim(layer_id, cam_id, "position", kf_track(ps, "vector3", f"cam{layer_id}p", tol_pos)))
    acts.append(anim(layer_id, cam_id, "rotation", kf_track(qs, "quaternion", f"cam{layer_id}r", tol_rot)))
    if fs and max(v[0] for _, v in fs) - min(v[0] for _, v in fs) > 1e-6:
        acts.append(anim(layer_id, cam_id, "focalLengthMm", kf_track(fs, "float", f"cam{layer_id}f", 0.02)))
    return acts


def anim(layer_id, item_id, prop, keyframes):
    return {"type": "setFxAnimator", "compositionId": COMP,
            "target": {"type": "styleProperty", "layerId": layer_id, "itemId": item_id, "propertyName": prop},
            "animator": {"type": "keyframes", "enabled": True, "keyframes": keyframes},
            "dependencies": [], "layerRefBindings": []}


def mesh(ids, name, data_id, inputs, pos, rot=None, parent=None, casts=True, binding_extra=None, scale=None, mods=None):
    s, b, i = ids(), ids(), ids()
    slot = material_slot(s, b, name, inputs)
    if binding_extra:
        slot["binding"].update(binding_extra)
    tr = {"position": list(pos)}
    if rot is not None:
        tr["rotation"] = rot
    if scale is not None:
        tr["scale"] = list(scale)
    it = {"type": "Mesh3D", "id": i, "parentId": parent, "name": name, "dataId": data_id, "packing": "whole",
          "transform": tr, "materialSlots": [slot], "castsShadows": casts,
          "regionSlots": [{"region": "primary", "slotId": s}, {"region": "side", "slotId": s}]}
    if mods:
        it["modifiers"] = mods
    return it, b


def group(gid, name, pos=(0, 0, 0), parent=None, rot=None):
    tr = {"position": list(pos)}
    if rot is not None:
        tr["rotation"] = rot
    return {"type": "Group3D", "id": gid, "parentId": parent, "name": name, "transform": tr}


UNLIT = {"unlit": True}

# ------------------------------------------------------------------ box motion (rise + collapse)


def qrot(q, v):
    x, y, z, w = q
    r = qmul(qmul(q, [v[0], v[1], v[2], 0.0]), [-x, -y, -z, w])
    return r[:3]


def box_motion():
    """Per box: list over frames 0..330 of (pos_px, quat_tesseract, scale) and lid-pop keys."""
    rise = load_json("rise_track.json")
    col = load_json("collapse_track.json")
    lay = load_json("layout.json")
    n = len(lay["boxes"])
    f_less = int(round(T["less"] * FPS))
    f_end = int(round(STREET_END * FPS))
    out = []
    for k in range(n):
        frames = []
        for f in range(0, f_end + 1):
            if f < f_less:
                r = rise["frames"][str(f)][k]
                pos, q, sc = r["pos"], r["quat"], r["scale"]
                sc_t = [sc[0] * 100, sc[2] * 100, sc[1] * 100]     # Blender (x, y, z) -> Scene3D (x, z, y)
            else:
                ff = min(f, col["end_frame"])
                r = col["frames"][str(ff)][k]
                pos, q = r["pos"], r["quat"]
                sc_t = [100, 100, 100]
            frames.append((b2t_pos(pos), b2t_quat(q), sc_t))
        out.append(frames)
    # the six survivors wobble a touch as the debris lands, then settle
    for k in range(6):
        for f in range(f_less, f_end + 1):
            tau = f / FPS - 7.95
            if tau <= 0:
                continue
            a = math.radians(0.55 * (k + 1) / 6 * math.exp(-tau / 0.22) * math.sin(tau * 2 * math.pi / 0.30))
            b = math.radians(0.35 * (k + 1) / 6 * math.exp(-tau / 0.25) * math.sin(tau * 2 * math.pi / 0.37 + 0.8))
            wob = [math.sin(a / 2), 0.0, math.sin(b / 2), 1.0]
            pos, q, sc = out[k][f]
            q2 = qmul(wob, q)
            nq = math.sqrt(sum(c * c for c in q2))
            out[k][f] = (pos, [c / nq for c in q2], sc)
    # lids: for the falling boxes the lid is its own rigid body (breakable joint in the sim). Express it in the
    # box's frame so the lid stays a child of its box: hinge = B^-1 * L * O^-1, O = the lid's offset in its hinge.
    lid_local = {}
    O = [0.0, -15.0, -104.0]
    for k in range(6, n):
        keys_p, keys_q = [], []
        prevq = None
        for f in range(f_less, f_end + 1):
            ff = str(min(f, col["end_frame"]))
            rl = col["lids"][ff][str(k)]
            pL, qL = b2t_pos(rl["pos"]), b2t_quat(rl["quat"])
            pB, qB, _ = out[k][f]
            qBi = [-qB[0], -qB[1], -qB[2], qB[3]]
            qH = qmul(qBi, qL)
            if prevq is not None and sum(x * y for x, y in zip(prevq, qH)) < 0:
                qH = [-c for c in qH]
            prevq = qH
            d = qrot(qBi, [pL[i] - pB[i] for i in range(3)])
            o = qrot(qH, O)
            keys_p.append((f / FPS, [d[i] - o[i] for i in range(3)]))
            keys_q.append((f / FPS, qH))
        lid_local[k] = (keys_p, keys_q)
    return out, lid_local


# ------------------------------------------------------------------ builder


BLOCKS = [(-7600, 2600, 6200, 7400), (-5000, 2300, 4300, 8200), (-2600, 2700, 7000, 9000),
          (100, 2300, 5200, 8600), (2600, 2500, 6400, 7800), (5200, 2400, 4600, 8400), (7700, 2800, 7200, 7600)]


def backdrop_lights():
    """Lit windows on the distant blocks and far street lamps: (name, position, size, colour, gain)."""
    import random
    rnd = random.Random(31)
    out = []
    for bi, (x, w, h, z) in enumerate(BLOCKS):
        for wi in range(rnd.randint(1, 3)):
            wx = x + rnd.uniform(-w / 2 + 300, w / 2 - 300)
            wy = -rnd.uniform(900, h - 500)
            warm = rnd.choice(["#FFB870", "#FFC98A", "#FFAA60", "#FFD7A6"])
            gain = rnd.uniform(0.40, 0.75)
            out.append((f"Window {bi}.{wi}", (wx, wy, z - 805), (rnd.choice([120, 150, 170]), 200, 10), warm, gain))
    for li, (x, z) in enumerate([(-4200, 5200), (-1500, 5600), (3800, 5000), (6400, 5800)]):
        out.append((f"Far lamp {li}", (x, -2300, z), (90, 60, 90), "#FFC07A", 1.0))
    return out


def build_street(assets):
    acts = []
    ids_back, ids_st, ids_rf, ids_gh = Ids(10100), Ids(20100), Ids(50100), Ids(80100)
    motion, lid_local = box_motion()
    lay = load_json("layout.json")
    t_end = STREET_END

    # ================= BACKDROP (layer 10) =================
    acts.append(scene_layer(LAYER_BACK, "Backdrop (city, bokeh)",
                            {"id": 10002, "background": {"type": "color", "color": hex_srgb("#0C1312")}}))
    acts += camera_actions(LAYER_BACK, 10003, street_cam, 0, t_end, tol_pos=0.3, tol_rot=0.02)
    data, items = [], []
    d_box = ids_back()
    data.append(mesh_data(d_box, "Block geo", {"type": "box", "size": [1, 1, 1]}))
    silhouette = {"baseColor": const(hex_lin("#040605"))}
    window = lambda c, s: {"baseColor": const([v * s for v in hex_lin(c)])}
    for bi, (x, w, h, z) in enumerate(BLOCKS):
        it, _ = mesh(ids_back, f"Block {bi}", d_box, silhouette, [x, -h / 2, z], scale=[w * 100, h * 100, 1600 * 100],
                     binding_extra=UNLIT, casts=False)
        items.append(it)
    for name, (wx, wy, wz), (sx, sy, sz), col, gain in backdrop_lights():
        it, _ = mesh(ids_back, name, d_box, window(col, gain), [wx, wy, wz], scale=[sx * 100, sy * 100, sz * 100],
                     binding_extra=UNLIT, casts=False)
        items.append(it)
    it, _ = mesh(ids_back, "Far ground (street continues to the blocks)", d_box, {"baseColor": const(hex_lin("#060807"))},
                 [0, 40, 6000], scale=[40000 * 100, 80 * 100, 9000 * 100], binding_extra=UNLIT, casts=False)
    items.append(it)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": LAYER_BACK, "data": data, "items": items})
    # shallow depth of field: the distant city melts into soft warm bokeh
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": LAYER_BACK, "effectId": 10901,
                 "effect": {"type": "gaussianBlur", "blurriness": 14}})
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": LAYER_BACK, "effectId": 10902,
                 "effect": {"type": "glow", "glowThreshold": 16, "glowRadius": 34, "glowIntensity": 1.35}})

    # ================= STREET (layer 11) =================
    acts.append(scene_layer(LAYER_STREET, "Street (lit set + boxes)", {
        "id": 20002,
        "light": {"source": {"type": "color", "color": hex_srgb("#26302F")}, "intensity": 0.05},
        "fog": {"color": hex_srgb("#070B0A"), "startDistance": 3.2, "endDistance": 11.0}}))
    acts += camera_actions(LAYER_STREET, 20003, street_cam, 0, t_end)
    LX, LZ, LY = LAMP["x"], LAMP["z"], LAMP["head_y"]
    KEY, LANTERN, FILL, RIM = 20004, 20005, 20006, 20007
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_STREET, "item": {
        "type": "Light3D", "id": KEY, "parentId": None, "name": "Street lamp key (spot, ~2700K)", "castsShadows": True,
        "color": hex_srgb("#FFB067"),
        "transform": {"position": [LX - 70, LY + 140, LZ], "relationships": aim(20090, 20091, [0, 0, -40])},
        "emitter": {"type": "spot", "power": 300, "coneAngle": 66, "coneFeather": 0.75, "sourceRadius": 30}}})
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_STREET, "item": {
        "type": "Light3D", "id": LANTERN, "parentId": None, "name": "Lantern spill (point)", "castsShadows": False,
        "color": hex_srgb("#FFB46B"), "transform": {"position": [LX, LY + 30, LZ]},
        "emitter": {"type": "point", "power": 48, "sourceRadius": 40}}})
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_STREET, "item": {
        "type": "Light3D", "id": FILL, "parentId": None, "name": "Teal shadow fill (front-left)", "castsShadows": False,
        "color": hex_srgb("#9DAAA8"),
        "transform": {"position": [-1800, -700, -2600], "relationships": aim(20092, 20093, [0, -900, 0])},
        "emitter": {"type": "spot", "power": 26, "coneAngle": 70, "coneFeather": 0.9, "sourceRadius": 200}}})
    # cool teal-green rim from camera-left, just behind the tower: grazes the front faces, bevels and lid lips
    # on the shadow side and carries the top of the tower (above the lamp) against the night sky
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_STREET, "item": {
        "type": "Light3D", "id": RIM, "parentId": None, "name": "Teal-green rim (camera-left, behind)", "castsShadows": False,
        "color": hex_srgb("#8FE8CF"),
        "transform": {"position": [-2700, -2300, -650], "relationships": aim(20094, 20095, [0, -1800, -100])},
        "emitter": {"type": "spot", "power": 320, "coneAngle": 62, "coneFeather": 0.9, "sourceRadius": 150}}})

    data, items = [], []
    D = {}
    for key, geom in [("base", {"type": "box", "size": BASE}), ("lid", {"type": "box", "size": LID}),
                      ("swoosh", {"type": "plane", "size": [SW_W, SW_W / 2.806]}),
                      ("unit", {"type": "box", "size": [1, 1, 1]}),
                      ("post", {"type": "cylinder", "radius": 22, "height": 2200}),
                      ("pbase", {"type": "cylinder", "radius": 58, "height": 170}),
                      ("collar", {"type": "cylinder", "radius": 44, "height": 46}),
                      ("cap", {"type": "cone", "radius": 118, "height": 95}),
                      ("finial", {"type": "sphere", "radius": 18}),
                      ("glass", {"type": "box", "size": [124, 180, 124]}),
                      ("shaft", {"type": "cone", "radius": 1100, "height": 2250})]:
        D[key] = ids_st()
        data.append(mesh_data(D[key], key + " geo", geom))
    bevel = lambda w: [{"type": "bevel", "id": ids_st(), "width": w, "segments": 2, "profile": 0.5, "limitAngle": 30}]

    side_o = {"baseColor": color_tex_input(image_tex("box_side_orange"), [ORANGE_GAIN] * 3), "roughness": const(0.86)}
    lid_o = {"baseColor": color_tex_input(image_tex("box_lid_orange"), [ORANGE_GAIN] * 3), "roughness": const(0.84)}
    sw_in = {"baseColor": const([0.95, 0.95, 0.94]), "roughness": const(0.6), "emissiveColor": const([0.17, 0.17, 0.17]),
             "coverage": scalar_tex_input(image_tex("swoosh", wrap="clampToEdge"), 1.0, alpha=True),
             "alphaCutoff": const(0.5)}
    sw_extra = {"alphaMode": "mask", "doubleSided": True}

    # ground
    side_map = {"coordinates": "world", "projection": {"type": "box"}, "transform": {"position": [0, 0, 0], "scale": [100, 100, 100]}}
    sidewalk_in = {"baseColor": color_tex_input(image_tex("sidewalk_color", scale=(1 / 2.4, 1 / 2.4), mapping=side_map), [1, 1, 1]),
                   "roughness": scalar_tex_input(image_tex("sidewalk_rough", scale=(1 / 2.4, 1 / 2.4), mapping=side_map), 0.62)}
    asphalt_in = {"baseColor": color_tex_input(image_tex("asphalt_color", scale=(1 / 3.0, 1 / 3.0), mapping=side_map), [1, 1, 1]),
                  "roughness": scalar_tex_input(image_tex("asphalt_rough", scale=(1 / 3.0, 1 / 3.0), mapping=side_map), 1.0)}
    for name, inputs, pos, size in [("Sidewalk", sidewalk_in, [0, 75, 3800], [16000, 150, 9000]),
                                    ("Asphalt", asphalt_in, [0, 170, -4700], [24000, 40, 8000])]:
        it, _ = mesh(ids_st, name, D["unit"], inputs, pos, scale=[s * 100 for s in size])
        items.append(it)
    it, _ = mesh(ids_st, "Kerb", D["unit"], {"baseColor": const(hex_lin("#3B3935")), "roughness": const(0.32)},
                 [0, 75, -615], scale=[16000 * 100, 170 * 100, 170 * 100])
    items.append(it)

    # vintage lamp
    iron = {"baseColor": const(hex_lin("#141516")), "roughness": const(0.38), "metallic": const(0.75)}
    for name, dk, pos in [("Lamp plinth", "pbase", [LX, -85, LZ]), ("Lamp post", "post", [LX, -1270, LZ]),
                          ("Lamp collar", "collar", [LX, LY + 135, LZ]), ("Lantern cap", "cap", [LX, LY - 95, LZ]),
                          ("Lantern finial", "finial", [LX, LY - 155, LZ])]:
        it, _ = mesh(ids_st, name, D[dk], iron, pos)
        items.append(it)
    it, lantern_binding = mesh(ids_st, "Lantern glass (glow)", D["glass"],
                               {"baseColor": const(hex_lin("#FFD9A6"))}, [LX, LY + 20, LZ],
                               binding_extra=UNLIT, casts=False)
    items.append(it)
    shaft_binding = None
    # 28 shoeboxes
    box_groups = []
    lid_hinges = {}
    for k in range(len(lay["boxes"])):
        gid = ids_st()
        pos0, q0, sc0 = motion[k][0]
        items.append({"type": "Group3D", "id": gid, "parentId": None, "name": f"Box {k + 1:02d}",
                      "transform": {"position": pos0, "rotation": {"type": "quaternion", "value": q0}, "scale": sc0}})
        it, _ = mesh(ids_st, f"Box {k + 1:02d} base", D["base"], side_o, [0, 5, 0], parent=gid, mods=bevel(2.0))
        items.append(it)
        hid = ids_st()
        items.append({"type": "Group3D", "id": hid, "parentId": gid, "name": f"Box {k + 1:02d} lid hinge",
                      "transform": {"position": [0, -31, 104], "rotation": {"type": "quaternion", "value": [0, 0, 0, 1]}}})
        lid_hinges[k] = hid
        it, _ = mesh(ids_st, f"Box {k + 1:02d} lid", D["lid"], lid_o, [0, -15, -104], parent=hid, mods=bevel(2.5))
        items.append(it)
        it, _ = mesh(ids_st, f"Box {k + 1:02d} swoosh", D["swoosh"], sw_in, [14, 16, -100.9], parent=gid,
                     casts=False, binding_extra=sw_extra)
        items.append(it)
        it, _ = mesh(ids_st, f"Box {k + 1:02d} swoosh (back)", D["swoosh"], sw_in, [-14, 16, 100.9], parent=gid,
                     rot=rot_euler(0, 180, 0), casts=False, binding_extra=sw_extra)
        items.append(it)
        box_groups.append(gid)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": LAYER_STREET, "data": data, "items": items})
    box_mesh_ids = [it["id"] for it in items if it["type"] == "Mesh3D" and it["name"].startswith("Box")]
    non_lid_ids = [it["id"] for it in items if it["type"] == "Mesh3D" and " lid" not in it["name"] and "swoosh" not in it["name"]
                   and "glow" not in it["name"]]
    acts.append({"type": "setFxScene3DRenderSettings", "compositionId": COMP, "layerId": LAYER_STREET, "settings": {
        "id": LAYER_STREET * 1000 + 97, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [],
        "outputs": [], "previewOutput": None,
        "lightLinks": [{"lightId": lid, "illuminatedObjects": {"type": "objects", "items": box_mesh_ids},
                        "shadowCasters": {"type": "all"}, "shadowReceivers": {"type": "all"}} for lid in (FILL, RIM)]
        + [{"lightId": KEY, "illuminatedObjects": {"type": "all"},
            "shadowCasters": {"type": "objects", "items": non_lid_ids}, "shadowReceivers": {"type": "all"}}]}})

    # box animation
    for k, gid in enumerate(box_groups):
        fr = motion[k]
        acts.append(anim(LAYER_STREET, gid, "position", kf_track([(f / FPS, v[0]) for f, v in enumerate(fr)], "vector3", f"b{k}p", 0.35)))
        acts.append(anim(LAYER_STREET, gid, "rotation", kf_track([(f / FPS, v[1]) for f, v in enumerate(fr)], "quaternion", f"b{k}r", 0.12)))
        acts.append(anim(LAYER_STREET, gid, "scale", kf_track([(f / FPS, v[2]) for f, v in enumerate(fr)], "vector3", f"b{k}s", 0.08)))
    for k, (kp, kq) in lid_local.items():
        acts.append(anim(LAYER_STREET, lid_hinges[k], "position", kf_track(kp, "vector3", f"lid{k}p", 0.4)))
        acts.append(anim(LAYER_STREET, lid_hinges[k], "rotation", kf_track(kq, "quaternion", f"lid{k}r", 0.004)))

    # lamp flicker on "Today?" (dims for ~3 frames, returns a little weaker)
    td = T["today"]
    flick = [(0.0, 300, "linear"), (td - 0.01, 300, "hold"), (td + 0.02, 70, "linear"), (td + 0.07, 120, "linear"),
             (td + 0.10, 40, "linear"), (td + 0.15, 235, EASE_OUT), (T["less"], 235, "hold"), (T["less"] + 0.4, 245, EASE_IN_OUT)]
    acts.append(anim(LAYER_STREET, KEY, "power", ease_kf("keyflicker", flick)))
    acts.append(anim(LAYER_STREET, LANTERN, "power", ease_kf("lanflicker", [(t, v * 0.16, e) for t, v, e in flick])))

    # ================= HAZE (layer 14): the lamp's beam in drifting haze, softened in 2D =================
    acts.append(scene_layer(LAYER_HAZE, "Haze (lamp beam)", {"id": 85002}))
    acts += camera_actions(LAYER_HAZE, 85003, street_cam, 0, t_end, tol_pos=0.3, tol_rot=0.02)
    hz = Ids(85100)
    data, items = [], []
    cone_d = []
    for ci, (r, cov) in enumerate([(1150, 0.035), (860, 0.045), (560, 0.06), (300, 0.07)]):
        d = hz()
        data.append(mesh_data(d, f"beam {ci}", {"type": "cone", "radius": r, "height": 2250}))
        noise = noise_tex(size=(700 + 150 * ci, 700 + 150 * ci), seed=5 + ci, octaves=4, persistence=0.55,
                          evolution_per_s=0.10 + 0.03 * ci,
                          mapping={"coordinates": "world", "projection": {"type": "box"},
                                   "transform": {"position": [0, 0, 0], "scale": [100, 100, 100]}})
        it, _ = mesh(hz, f"Beam shell {ci}", d, {"baseColor": color_tex_input(noise, hex_lin("#FFC796")), "coverage": const(cov)},
                     [LX - 470, LY + 1125, LZ - 40], rot=rot_euler(0, 0, 12),
                     binding_extra={"unlit": True, "alphaMode": "blend", "doubleSided": True}, casts=False)
        items.append(it)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": LAYER_HAZE, "data": data, "items": items})
    acts.append({"type": "updateLayerField", "compositionId": COMP, "layerId": LAYER_HAZE, "propertyName": "blendMode", "value": "screen"})
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": LAYER_HAZE, "effectId": 85901,
                 "effect": {"type": "gaussianBlur", "blurriness": 60}})
    acts.append({"type": "setFxPropertyKeyframes", "compositionId": COMP, "property": {"layerId": LAYER_HAZE, "propertyType": "opacity"},
                 "keyframes": ease_kf("hazeop", [(0.0, 22, "linear"), (2.9, 22, "hold"), (4.2, 38, EASE_IN_OUT)])})

    # ================= REFLECTION (layer 12) =================
    # The wet asphalt (top at y = YM) is the mirror. The mirrored world is lit by a mirrored copy of the
    # lamp key, so the reflection falls off up the tower exactly like the lit set does. Black hold-outs
    # (sidewalk block, kerb, boxes) occlude it wherever the camera does not actually see asphalt.
    YM = 150.0
    my = lambda y: 2 * YM - y
    acts.append(scene_layer(LAYER_REFL, "Wet-asphalt reflection (mirror pass)", {
        "id": 50002, "light": {"source": {"type": "color", "color": hex_srgb("#26302F")}, "intensity": 0.05}}))
    acts += camera_actions(LAYER_REFL, 50003, street_cam, 0, t_end, tol_pos=0.15, tol_rot=0.01)
    MKEY = 50004
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_REFL, "item": {
        "type": "Light3D", "id": MKEY, "parentId": None, "name": "Mirrored lamp key", "castsShadows": False,
        "color": hex_srgb("#FFB067"),
        "transform": {"position": [LX - 70, my(LY + 140), LZ], "relationships": aim(50090, 50091, [0, my(0), -40])},
        "emitter": {"type": "spot", "power": 300, "coneAngle": 66, "coneFeather": 0.75, "sourceRadius": 30}}})
    acts.append(anim(LAYER_REFL, MKEY, "power", ease_kf("mkeyflicker", flick)))
    data, items = [], []
    R = {k: ids_rf() for k in ("base", "lid", "unit", "post", "glass", "pbase")}
    data += [mesh_data(R["base"], "base", {"type": "box", "size": BASE}), mesh_data(R["lid"], "lid", {"type": "box", "size": LID}),
             mesh_data(R["unit"], "unit", {"type": "box", "size": [1, 1, 1]}),
             mesh_data(R["post"], "post", {"type": "cylinder", "radius": 22, "height": 2200}),
             mesh_data(R["pbase"], "plinth", {"type": "cylinder", "radius": 58, "height": 170}),
             mesh_data(R["glass"], "glass", {"type": "box", "size": [124, 180, 124]})]
    black = {"baseColor": const([0, 0, 0])}
    refl_side = {"baseColor": color_tex_input(image_tex("box_side_orange"), [0.85, 0.85, 0.85]), "roughness": const(0.9)}
    refl_lid = {"baseColor": color_tex_input(image_tex("box_lid_orange"), [0.85, 0.85, 0.85]), "roughness": const(0.9)}
    for name, pos, size in [("Hold-out sidewalk", [0, 75, 3800], [16000, 150, 9000]),
                            ("Hold-out kerb", [0, 75, -615], [16000, 170, 170])]:
        it, _ = mesh(ids_rf, name, R["unit"], black, pos, scale=[v * 100 for v in size], binding_extra=UNLIT, casts=False)
        items.append(it)
    for name, dk, pos, mat, unlit in [("Mirror post", "post", [LX, my(-1270), LZ], {"baseColor": const(hex_lin("#141516")), "roughness": const(0.5)}, False),
                                      ("Mirror plinth", "pbase", [LX, my(-85), LZ], {"baseColor": const(hex_lin("#141516")), "roughness": const(0.5)}, False),
                                      ("Mirror lantern", "glass", [LX, my(LY + 20), LZ], {"baseColor": const(hex_lin("#FFC890"))}, True)]:
        it, b_ = mesh(ids_rf, name, R[dk], mat, pos, binding_extra=UNLIT if unlit else None, casts=False)
        items.append(it)
    # the distant lit windows and far lamps also streak in the wet street
    for name, (wx, wy, wz), (sx, sy, sz), col, gain in backdrop_lights():
        it, _ = mesh(ids_rf, "Mirror " + name, R["unit"], {"baseColor": const([v * gain * 0.55 for v in hex_lin(col)])},
                     [wx, my(wy), wz], scale=[sx * 100, sy * 100, sz * 100], binding_extra=UNLIT, casts=False)
        items.append(it)
    refl_groups, hold_groups = [], []
    for k in range(len(lay["boxes"])):
        pos0, q0, sc0 = motion[k][0]
        hg, mg = ids_rf(), ids_rf()
        items.append({"type": "Group3D", "id": hg, "parentId": None, "name": f"Hold-out box {k + 1:02d}",
                      "transform": {"position": pos0, "rotation": {"type": "quaternion", "value": q0}, "scale": sc0}})
        it, _ = mesh(ids_rf, f"Hold-out base {k + 1:02d}", R["base"], black, [0, 5, 0], parent=hg, binding_extra=UNLIT, casts=False)
        items.append(it)
        it, _ = mesh(ids_rf, f"Hold-out lid {k + 1:02d}", R["lid"], black, [0, -46, 0], parent=hg, binding_extra=UNLIT, casts=False)
        items.append(it)
        mp = [pos0[0], my(pos0[1]), pos0[2]]
        items.append({"type": "Group3D", "id": mg, "parentId": None, "name": f"Mirror box {k + 1:02d}",
                      "transform": {"position": mp, "rotation": {"type": "quaternion", "value": mirror_quat(q0)}, "scale": sc0}})
        it, _ = mesh(ids_rf, f"Mirror base {k + 1:02d}", R["base"], refl_side, [0, -5, 0], parent=mg, casts=False)
        items.append(it)
        it, _ = mesh(ids_rf, f"Mirror lid {k + 1:02d}", R["lid"], refl_lid, [0, 46, 0], parent=mg, casts=False)
        items.append(it)
        refl_groups.append(mg)
        hold_groups.append(hg)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": LAYER_REFL, "data": data, "items": items})
    acts.append({"type": "updateLayerField", "compositionId": COMP, "layerId": LAYER_REFL, "propertyName": "blendMode", "value": "add"})
    acts.append({"type": "setFxPropertyValue", "compositionId": COMP, "target": {"type": "layerProperty", "property": {"layerId": LAYER_REFL, "propertyType": "opacity"}},
                 "value": {"type": "float", "value": 55}})
    # wet asphalt: reflections smear vertically, soften, and shimmer with slow puddle ripples
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": LAYER_REFL, "effectId": 50902,
                 "effect": {"type": "gaussianBlur", "blurriness": 2.5}})
    # (the shimmer is a slow turbulent displacement added with the puddle ripples in overlay.py)
    for k in range(len(lay["boxes"])):
        fr = motion[k]
        acts.append(anim(LAYER_REFL, hold_groups[k], "position", kf_track([(f / FPS, v[0]) for f, v in enumerate(fr)], "vector3", f"h{k}p", 0.6)))
        acts.append(anim(LAYER_REFL, hold_groups[k], "rotation", kf_track([(f / FPS, v[1]) for f, v in enumerate(fr)], "quaternion", f"h{k}r", 0.25)))
        acts.append(anim(LAYER_REFL, refl_groups[k], "position", kf_track([(f / FPS, [v[0][0], my(v[0][1]), v[0][2]]) for f, v in enumerate(fr)], "vector3", f"m{k}p", 0.6)))
        acts.append(anim(LAYER_REFL, refl_groups[k], "rotation", kf_track([(f / FPS, mirror_quat(v[1])) for f, v in enumerate(fr)], "quaternion", f"m{k}r", 0.25)))
        acts.append(anim(LAYER_REFL, refl_groups[k], "scale", kf_track([(f / FPS, v[2]) for f, v in enumerate(fr)], "vector3", f"m{k}s", 0.15)))

    # ================= GHOST (layer 13) =================
    g0 = ms(T["ghost"][0])
    acts.append(scene_layer(LAYER_GHOST, "Ghost tower outline", {"id": 80002}, start_ms=g0, dur_ms=STREET_MS - g0))
    acts += camera_actions(LAYER_GHOST, 80003, lambda lt: street_cam(lt), T["ghost"][0], t_end, tol_pos=0.15, tol_rot=0.01)
    data, items = [], []
    dash = ids_gh()
    data.append(mesh_data(dash, "dash", {"type": "box", "size": [15, 46, 15]}))
    hdash = ids_gh()
    data.append(mesh_data(hdash, "hdash", {"type": "box", "size": [46, 15, 15]}))
    ghost_mat = {"baseColor": const(hex_lin("#D9F5E4"))}
    top6 = -6 * 122
    span = 28 * 122 - 6 * 122
    n_dash = int(span // 70)
    arrays = []
    for ci, (cx, cz) in enumerate([(-169, -104), (169, -104), (169, 104), (-169, 104)]):
        gid, aid = ids_gh(), ids_gh()
        items.append({"type": "Group3D", "id": gid, "parentId": None, "name": f"Ghost edge {ci}",
                      "transform": {"position": [cx, top6 - 30, cz]},
                      "array": {"type": "linear", "id": aid, "count": 0, "offset": [0, -70, 0]}})
        it, _ = mesh(ids_gh, f"Dash {ci}", dash, ghost_mat, [0, 0, 0], parent=gid, binding_extra=UNLIT, casts=False)
        items.append(it)
        arrays.append(aid)
    # top rectangle of the ghost, revealed when the edges arrive
    top_items = []
    for side, (pos, n_h, off) in enumerate([([-150, -28 * 122, -104], 5, [70, 0, 0]), ([-150, -28 * 122, 104], 5, [70, 0, 0])]):
        gid, aid = ids_gh(), ids_gh()
        items.append({"type": "Group3D", "id": gid, "parentId": None, "name": f"Ghost top {side}",
                      "transform": {"position": pos}, "array": {"type": "linear", "id": aid, "count": 0, "offset": off}})
        it, _ = mesh(ids_gh, f"Top dash {side}", hdash, ghost_mat, [0, 0, 0], parent=gid, binding_extra=UNLIT, casts=False)
        items.append(it)
        top_items.append((aid, n_h))
    # a faint volume fill rises with the dashes, so the missing 22 boxes read as a shape at phone size
    fill_geo, fill_g = ids_gh(), ids_gh()
    data.append(mesh_data(fill_geo, "ghost volume", {"type": "box", "size": [338, span, 208]}))
    items.append({"type": "Group3D", "id": fill_g, "parentId": None, "name": "Ghost volume (grows up)",
                  "transform": {"position": [0, top6, 0], "scale": [100, 0.5, 100]}})
    it, _ = mesh(ids_gh, "Ghost volume fill", fill_geo, {"baseColor": const([v * 0.10 for v in hex_lin("#D9F5E4")])},
                 [0, -span / 2, 0], parent=fill_g, binding_extra=UNLIT, casts=False)
    items.append(it)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": LAYER_GHOST, "data": data, "items": items})
    acts.append({"type": "updateLayerField", "compositionId": COMP, "layerId": LAYER_GHOST, "propertyName": "blendMode", "value": "add"})
    gs, ge = T["ghost"]
    acts.append(anim(LAYER_GHOST, fill_g, "scale", ease_kf("ghfill", [(0.0, [100, 0.5, 100], "linear"),
                                                                      (ge - gs, [100, 100, 100], (0.45, 0.0, 0.25, 1.0))], kind="vector3")))
    for ci, aid in enumerate(arrays):
        keys = [(0.0, 0, "linear"), (ge - gs, n_dash, (0.45, 0.0, 0.25, 1.0))]
        acts.append(anim(LAYER_GHOST, aid, "count", ease_kf(f"gh{ci}", keys)))
    for aid, n_h in top_items:
        keys = [(0.0, 0, "linear"), (ge - gs - 0.05, 0, "hold"), (ge - gs + 0.12, n_h, EASE_OUT)]
        acts.append(anim(LAYER_GHOST, aid, "count", ease_kf(f"gt{aid}", keys)))
    return acts, {"lid_pops": {}, "lantern_binding": lantern_binding, "shaft_binding": shaft_binding}
