"""Stockroom section (MG 10.70-13.30 s): the S&P 100 wall.

A 10 x 10 wall of plain grey shoeboxes (ends out) against a dark back wall, two extra columns either
side fading into darkness. One warm overhead practical. The orange Nike box (row 6, just right of
centre) is shoved out on "kicked" (Blender rigid-body track), then the row closes the gap in a
staggered slide with overshoot, finished by 12.60 s. Straight-on camera, slow push-in.
"""
import math

from common import *
from lib import COMP, aim, const, color_tex_input, scalar_tex_input, image_tex, hex_lin, hex_srgb, mesh_data, rot_euler
from street import Ids, anim, camera_actions, group, mesh, scene_layer, UNLIT, BASE, LID, SW_W

SW_END = 112  # swoosh on the box end (end panel is 200 wide)

LAYER_WALL = 20
W0 = WALL_START
WALL_MS = ms(T["end"] - W0)


def quat_z(deg):
    a = math.radians(deg) / 2
    return [0.0, 0.0, math.sin(a), math.cos(a)]


def build_wall():
    lay = load_json("wall_layout.json")
    trk = load_json("wall_track.json")
    ids = Ids(90100)
    acts = [scene_layer(LAYER_WALL, "Stockroom wall (S&P 100)", {
        "id": 90002, "background": {"type": "color", "color": hex_srgb("#040506")},
        "light": {"source": {"type": "color", "color": hex_srgb("#25302F")}, "intensity": 0.05},
        "fog": {"color": hex_srgb("#040506"), "startDistance": 3.8, "endDistance": 9.0}},
        start_ms=ms(W0), dur_ms=WALL_MS)]
    acts += camera_actions(LAYER_WALL, 90003, lambda lt: wall_cam(lt), W0, T["end"], tol_pos=0.05, tol_rot=0.004)
    # camera_actions passes absolute time to the camera function and keys on layer time
    KEY, FILL, RIM = 90004, 90005, 90006
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_WALL, "item": {
        "type": "Light3D", "id": KEY, "parentId": None, "name": "Overhead practical (spot, ~2700K)", "castsShadows": True,
        "color": hex_srgb("#FFD7B0"),
        "transform": {"position": [80, -2350, -1250], "relationships": aim(90090, 90091, [0, -640, 0])},
        "emitter": {"type": "spot", "power": 19, "coneAngle": 64, "coneFeather": 0.9, "sourceRadius": 220}}})
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": LAYER_WALL, "item": {
        "type": "Light3D", "id": FILL, "parentId": None, "name": "Teal shadow fill", "castsShadows": False,
        "color": hex_srgb("#7FA39B"),
        "transform": {"position": [-1600, -500, -2200], "relationships": aim(90092, 90093, [0, -600, 0])},
        "emitter": {"type": "spot", "power": 5, "coneAngle": 70, "coneFeather": 0.9, "sourceRadius": 200}}})

    data, items = [], []
    D = {k: ids() for k in ("base", "lid", "swoosh", "swoosh_end", "unit", "bulb", "cord")}
    data += [mesh_data(D["base"], "base", {"type": "box", "size": BASE}), mesh_data(D["lid"], "lid", {"type": "box", "size": LID}),
             mesh_data(D["swoosh"], "swoosh", {"type": "plane", "size": [SW_W, SW_W / 2.806]}),
             mesh_data(D["swoosh_end"], "swoosh on the box end", {"type": "plane", "size": [SW_END, SW_END / 2.806]}),
             mesh_data(D["unit"], "unit", {"type": "box", "size": [1, 1, 1]}),
             mesh_data(D["bulb"], "bulb", {"type": "sphere", "radius": 34}),
             mesh_data(D["cord"], "cord", {"type": "cylinder", "radius": 4, "height": 900})]
    bevel = lambda w: [{"type": "bevel", "id": ids(), "width": w, "segments": 2, "profile": 0.5, "limitAngle": 30}]
    side_g = {"baseColor": color_tex_input(image_tex("box_side_grey"), [1, 1, 1]), "roughness": const(0.9)}
    lid_g = {"baseColor": color_tex_input(image_tex("box_lid_grey"), [1, 1, 1]), "roughness": const(0.88)}
    side_o = {"baseColor": color_tex_input(image_tex("box_side_orange"), [0.74] * 3), "roughness": const(0.86)}
    lid_o = {"baseColor": color_tex_input(image_tex("box_lid_orange"), [0.74] * 3), "roughness": const(0.84)}
    sw_in = {"baseColor": const([0.95, 0.95, 0.94]), "roughness": const(0.6), "emissiveColor": const([0.17, 0.17, 0.17]),
             "coverage": scalar_tex_input(image_tex("swoosh", wrap="clampToEdge"), 1.0, alpha=True), "alphaCutoff": const(0.5)}

    # room: dark back wall, concrete floor, the practical's bulb on its cord
    it, _ = mesh(ids, "Back wall", D["unit"], {"baseColor": const(hex_lin("#1A1B1C")), "roughness": const(0.95)},
                 [0, -1800, 420], scale=[9000 * 100, 4000 * 100, 100 * 100])
    items.append(it)
    it, _ = mesh(ids, "Floor", D["unit"], {"baseColor": color_tex_input(image_tex("sidewalk_color", scale=(1 / 2.0, 1 / 2.0),
                 mapping={"coordinates": "world", "projection": {"type": "box"}, "transform": {"position": [0, 0, 0], "scale": [100, 100, 100]}}), [0.8, 0.8, 0.8]),
                 "roughness": const(0.6)}, [0, 50, -1500], scale=[9000 * 100, 100 * 100, 4000 * 100])
    items.append(it)
    it, _ = mesh(ids, "Practical bulb", D["bulb"], {"baseColor": const(hex_lin("#FFE0B0"))}, [80, -2310, -1250],
                 binding_extra=UNLIT, casts=False)
    items.append(it)
    it, _ = mesh(ids, "Bulb cord", D["cord"], {"baseColor": const(hex_lin("#0D0D0D"))}, [80, -2790, -1250], casts=False)
    items.append(it)

    PX = lay["pitch_x"] * 1000
    o_col, o_row = lay["orange"]
    groups = {}
    for b in lay["boxes"]:
        c, r = b["col"], b["row"]
        is_or = (c, r) == (o_col, o_row)
        pos = b2t_pos([b["x"], b["y"], b["z"]])
        q = b2t_quat(qmul(quat_z(b["yaw_deg"]), quat_z(90)))
        if is_or:
            f0 = trk["frames"][str(min(int(k) for k in trk["frames"]))]
            pos = b2t_pos(f0["pos"])
            q = b2t_quat(qmul(f0["quat"], quat_z(90)))
        gid = ids()
        items.append({"type": "Group3D", "id": gid, "parentId": None, "name": f"{'NIKE ' if is_or else ''}Box c{c} r{r}",
                      "transform": {"position": pos, "rotation": {"type": "quaternion", "value": q}}})
        it, _ = mesh(ids, f"c{c}r{r} base", D["base"], side_o if is_or else side_g, [0, 5, 0], parent=gid, mods=bevel(2.0))
        items.append(it)
        it, _ = mesh(ids, f"c{c}r{r} lid", D["lid"], lid_o if is_or else lid_g, [0, -46, 0], parent=gid, mods=bevel(2.5))
        items.append(it)
        if is_or:
            for zz, ry, xo in ((-100.9, 0, 14), (100.9, 180, -14)):
                it, _ = mesh(ids, f"Nike swoosh {ry}", D["swoosh"], sw_in, [xo, 16, zz], parent=gid, rot=rot_euler(0, ry, 0),
                             casts=False, binding_extra={"alphaMode": "mask", "doubleSided": True})
                items.append(it)
            # boxes are shelved end-out, so the end facing camera (local -X) carries a swoosh too;
            # Ry(+90) turns the plane's front to local -X with its right edge to screen right (not mirrored)
            for xx, ry in ((-(BASE[0] / 2 + 0.9), 90), (BASE[0] / 2 + 0.9, -90)):
                it, _ = mesh(ids, f"Nike swoosh end {ry}", D["swoosh_end"], sw_in, [xx, 14, 0], parent=gid,
                             rot=rot_euler(0, ry, 0), casts=False, binding_extra={"alphaMode": "mask", "doubleSided": True})
                items.append(it)
        groups[(c, r)] = (gid, pos, q)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": LAYER_WALL, "data": data, "items": items})

    # the orange box: physics track (layer time = t - W0)
    gid = groups[(o_col, o_row)][0]
    f_first = min(int(k) for k in trk["frames"])
    samples_p, samples_q = [], []
    for f in range(int(round(W0 * FPS)), NFRAMES + 1):
        fr = trk["frames"][str(max(f_first, min(f, max(int(k) for k in trk["frames"]))))]
        samples_p.append((f / FPS - W0, b2t_pos(fr["pos"])))
        samples_q.append((f / FPS - W0, b2t_quat(qmul(fr["quat"], quat_z(90)))))
    acts.append(anim(LAYER_WALL, gid, "position", kf_track(samples_p, "vector3", "orp", 0.25)))
    acts.append(anim(LAYER_WALL, gid, "rotation", kf_track(samples_q, "quaternion", "orq", 0.1)))

    # gap closing: the boxes right of the gap are shoved one slot left as a train (nearest leads by ~half a frame)
    for i, c in enumerate(range(o_col + 1, lay["cols"] + 2 * lay["extra"])):
        g, pos, q = groups[(c, o_row)]
        start = 11.93 + i * 0.017
        dur = 0.34
        # each box is shoved into its new slot, closes the 3 mm seam on impact (no interpenetration),
        # rebounds a few mm and settles: the overshoot reads as weight, not as a spring
        slot = pos[0] - PX
        hit = [slot - 2.5, pos[1], pos[2]]
        rebound = [slot + 5.0 - 0.4 * (i % 3), pos[1], pos[2]]
        p_end = [slot, pos[1], pos[2]]
        keys = [(0.0, pos, "linear"), (start - W0, pos, "hold"),
                (start - W0 + dur * 0.56, hit, (0.5, 0.0, 0.85, 0.6)),
                (start - W0 + dur * 0.78, rebound, (0.2, 0.6, 0.4, 1.0)),
                (start - W0 + dur, p_end, (0.45, 0.0, 0.4, 1.0))]
        acts.append(anim(LAYER_WALL, g, "position", ease_kf(f"gap{c}", keys, kind="vector3")))
    return acts
