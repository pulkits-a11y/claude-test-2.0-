"""Scene3D layers of the Three Hits MG: one long dark stage, three stations, one continuous camera move.

  10  Backdrop     near-black charcoal-navy, faint dark shapes, warm square dust motes drifting (soft, bokeh-like)
  11  Stage        the lit set: polished dark floor, the same orange Nike shoeboxes as the Shoebox Tower MG, the
                   customs stamp, the TARIFF ink; one warm spotlight per stack, a cool teal-green rim from behind
  12  Reflection   mirror pass across the polished floor (lit by mirrored spotlights), Add, softened
  14  Haze         the spotlight cones in haze (Screen, blurred)
  15  2028 beam    the 2028 cone and pool glow on their own layer, so the dying light can stutter and distort
  16  Dust         the stamp's dust burst and the knock-off puff (sprites, Screen, turbulent swirl)
"""
import json
import math

from common import *
from layout import BOX, PITCH, STATIONS, ROW, stack_boxes, cam
from lib import COMP, aim, const, color_tex_input, scalar_tex_input, image_tex, noise_tex, hex_lin, hex_srgb, mesh_data, rot_euler
from scene_helpers import Ids, anim, camera_actions, mesh, group, scene_layer, UNLIT, SW_W, BASE, LID

L_BACK, L_STAGE, L_REFL, L_HAZE, L_BEAM, L_DUST = 10, 11, 12, 14, 15, 16
ORANGE_GAIN = 0.74          # same as the Shoebox Tower: the lit orange keeps its modelling, no clipping
SPOT_H, SPOT_BACK = 2300, 350
import os
P_FULL = float(os.environ.get("TH_PFULL", 25))   # spotlight power at full brightness (W): narrow 30 deg cone, orange peaks ~R 230
F_IMPACT = 5                # stamp lands on frame 5 (0.167 s), on the stressed "TAR-"
F_HIT = 31                  # the top China box is hit on frame 31 (1.03 s), on "down"


def quat_z(deg):
    a = math.radians(deg) / 2
    return [0.0, 0.0, math.sin(a), math.cos(a)]


def yaw_q(deg):
    """Tesseract quaternion for a turn about the vertical axis (same convention as the Blender sim)."""
    return b2t_quat(quat_z(deg))


# ---------------------------------------------------------------- light curves (multipliers of each spot's power)
def tariff_light(t):
    f = t * FPS
    if F_IMPACT + 0.5 <= f < F_IMPACT + 2.5:           # the stage shakes: the lamp dips for two frames
        return 0.55
    if F_IMPACT + 2.5 <= f < F_IMPACT + 3.5:
        return 0.85
    return 1.0


def light_2028(t):
    """30% and unsteady from the moment it is seen; stutters 5.90-6.27; one last flicker and out at 6.30."""
    base = STATIONS["y2028"]["power"]
    f = int(round(t * FPS))
    if t < 4.7:
        return base
    unsteady = {146: 0.88, 152: 0.93, 153: 0.80, 161: 0.90, 166: 0.86, 170: 0.92, 172: 0.84}
    if t < 5.90:
        return base * unsteady.get(f, 1.0)
    stutter = {177: 0.18, 178: 0.06, 179: 0.70, 182: 0.35, 183: 1.05, 184: 0.12, 185: 0.55, 186: 0.90, 187: 0.75,
               188: 0.20, 189: 1.15, 190: 0.25, 191: 0.0}
    if f in stutter:
        return base * stutter[f]
    return base if f < 191 else 0.0


def light_mult(key, t):
    if key == "tariff":
        return tariff_light(t)
    if key == "y2028":
        return light_2028(t) / STATIONS["y2028"]["power"]
    return 1.0


def frames_keys(fn, prefix, tol=0.5, kind="float"):
    samples = [(f / FPS, [fn(f / FPS)]) for f in range(0, NFRAMES + 1)]
    # light flickers are frame-exact: keep every change, hold between them
    out, last = [], None
    for i, (t, v) in enumerate(samples):
        if last is None or abs(v[0] - last) > 1e-6 or i == len(samples) - 1:
            if out and i > 0 and abs(samples[i - 1][1][0] - out[-1][1]) < 1e-6 and samples[i - 1][0] != out[-1][0]:
                out.append((samples[i - 1][0], samples[i - 1][1][0], "hold"))
            out.append((t, v[0], "hold"))
            last = v[0]
    return ease_kf(prefix, out)


# ---------------------------------------------------------------- the box (identical to the Shoebox Tower model)
def box_materials():
    side_o = {"baseColor": color_tex_input(image_tex("box_side_orange"), [ORANGE_GAIN] * 3), "roughness": const(0.86)}
    lid_o = {"baseColor": color_tex_input(image_tex("box_lid_orange"), [ORANGE_GAIN] * 3), "roughness": const(0.84)}
    sw_in = {"baseColor": const([0.95, 0.95, 0.94]), "roughness": const(0.6), "emissiveColor": const([0.17, 0.17, 0.17]),
             "coverage": scalar_tex_input(image_tex("swoosh", wrap="clampToEdge"), 1.0, alpha=True), "alphaCutoff": const(0.5)}
    return side_o, lid_o, sw_in


def box_items(ids, D, mats, name, gid, pos, q, bevel, extra_children=None):
    side_o, lid_o, sw_in = mats
    items = [{"type": "Group3D", "id": gid, "parentId": None, "name": name,
              "transform": {"position": list(pos), "rotation": {"type": "quaternion", "value": q}}}]
    it, _ = mesh(ids, f"{name} base", D["base"], side_o, [0, 5, 0], parent=gid, mods=bevel(2.0))
    items.append(it)
    it, _ = mesh(ids, f"{name} lid", D["lid"], lid_o, [0, -46, 0], parent=gid, mods=bevel(2.5))
    items.append(it)
    for zz, ry, xo in ((-100.9, 0, 14), (100.9, 180, -14)):
        it, _ = mesh(ids, f"{name} swoosh {ry}", D["swoosh"], sw_in, [xo, 16, zz], parent=gid, rot=rot_euler(0, ry, 0),
                     casts=False, binding_extra={"alphaMode": "mask", "doubleSided": True})
        items.append(it)
    return items


def all_boxes():
    """Every box on the stage: list of (key, name, centre, quat). The knocked China box is 'china3'."""
    out = []
    for key in STATIONS:
        for k, (c, yaw) in enumerate(stack_boxes(key)):
            out.append((f"{key}{k}", f"{key.upper()} box {k + 1}", c, yaw_q(yaw)))
    return out


def knock_motion():
    trk = load_json("knock_track.json")
    fr = trk["frames"]
    f0 = min(int(k) for k in fr)
    ps, qs = [], []
    prev = None
    for f in range(0, NFRAMES + 1):
        r = fr[str(min(max(f, f0), max(int(k) for k in fr)))]
        q = b2t_quat(r["quat"])
        if prev is not None and sum(a * b for a, b in zip(prev, q)) < 0:
            q = [-c for c in q]
        prev = q
        ps.append((f / FPS, b2t_pos(r["pos"])))
        qs.append((f / FPS, q))
    return ps, qs


def wobble(k, t):
    """The three China boxes left standing rock a touch after the top one is dragged off them."""
    tau = t - F_HIT / FPS
    if tau <= 0:
        return [0, 0, 0, 1]
    amp = [0.0, 0.35, 0.8][k]
    a = math.radians(amp * math.exp(-tau / 0.28) * math.sin(tau * 2 * math.pi / 0.27))
    b = math.radians(amp * 0.6 * math.exp(-tau / 0.30) * math.sin(tau * 2 * math.pi / 0.33 + 0.9))
    q = [0.0, math.sin(b / 2), math.sin(a / 2), 1.0]
    n = math.sqrt(sum(c * c for c in q))
    return [c / n for c in q]


def squash(t):
    """TARIFF box: (scaleY %, scaleXZ %) under the stamp: squash on impact, rebound, settle."""
    f = t * FPS
    keys = [(F_IMPACT - 0.01, 100, 100), (F_IMPACT + 1, 93.5, 102.6), (F_IMPACT + 3, 95.5, 101.8), (F_IMPACT + 4.5, 102.2, 99.2),
            (F_IMPACT + 6.5, 99.3, 100.3), (F_IMPACT + 9, 100, 100)]
    if f <= keys[0][0] or f >= keys[-1][0]:
        return 100.0, 100.0
    for (fa, ya, xa), (fb, yb, xb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            u = (f - fa) / (fb - fa)
            u = u * u * (3 - 2 * u)
            return ya + (yb - ya) * u, xa + (xb - xa) * u
    return 100.0, 100.0


def stamp_face_y(t):
    """Height of the stamp's rubber face (Scene3D y, negative = up). Drops out of the dark, hits, presses,
    a tiny anticipation lift, then rises out of frame."""
    f = t * FPS
    top_y = -BOX["h"]
    y_high = -1180.0
    if f <= F_IMPACT:
        u = max(0.0, f / F_IMPACT)
        return y_high + (top_y - y_high) * (u ** 2.2)                         # accelerating, like a hand driving it
    sy, _ = squash(t)
    pressed = -BOX["h"] * sy / 100
    if f <= F_IMPACT + 2:
        return pressed
    if f <= F_IMPACT + 3.5:                                                    # a tiny lift as the rubber unsticks
        u = (f - F_IMPACT - 2) / 1.5
        return pressed - 7 * (u * u * (3 - 2 * u))
    u = min(1.0, (f - F_IMPACT - 3.5) / 5.5)
    e = u ** 2.2                                                               # then lifts away, accelerating
    return (pressed - 7) + (y_high - 120 - (pressed - 7)) * e


def build_stage():
    acts = []
    ids_b, ids_s, ids_r, ids_h, ids_e, ids_d = Ids(10100), Ids(20100), Ids(50100), Ids(60100), Ids(70100), Ids(80100)
    t_end = DUR
    st = STATIONS

    # ================= BACKDROP + MOTES (10)
    acts.append(scene_layer(L_BACK, "Backdrop (dark stage, dust motes)",
                            {"id": 10002, "background": {"type": "color", "color": hex_srgb("#080C0D")}}))
    acts += camera_actions(L_BACK, 10003, cam, 0, t_end, tol_pos=0.3, tol_rot=0.02)
    data, items = [], []
    d_box = ids_b()
    data.append(mesh_data(d_box, "unit", {"type": "box", "size": [1, 1, 1]}))
    import random
    rnd = random.Random(2028)
    # faint dark shapes far back (the same family as the Shoebox Tower's silhouettes)
    for i, (x, w, h) in enumerate([(-2600, 2400, 3600), (300, 2000, 4600), (2600, 2600, 3900), (5100, 2200, 4800), (7600, 2600, 4100)]):
        it, _ = mesh(ids_b, f"Far shape {i}", d_box, {"baseColor": const(hex_lin("#040606"))}, [x, -h / 2, 7600 + 300 * (i % 2)],
                     scale=[w * 100, h * 100, 800 * 100], binding_extra=UNLIT, casts=False)
        items.append(it)
    # the floor carries on into the dark (no horizon line)
    it, _ = mesh(ids_b, "Far floor", d_box, {"baseColor": const(hex_lin("#050707"))}, [2500, 40, 5000],
                 scale=[40000 * 100, 80 * 100, 9000 * 100], binding_extra=UNLIT, casts=False)
    items.append(it)
    # warm square dust motes: four drifting groups at different depths
    mote_groups = []
    for gi in range(4):
        gid = ids_b()
        mote_groups.append(gid)
        items.append({"type": "Group3D", "id": gid, "parentId": None, "name": f"Dust motes {gi}", "transform": {"position": [0, 0, 0]}})
        for mi in range(11):
            x = rnd.uniform(-1500, 7500)
            z = rnd.uniform(1400, 5200) + gi * 300
            y = -rnd.uniform(350, 2400)
            s = rnd.choice([60, 80, 95, 110])
            warm = rnd.choice(["#FFB870", "#FFC98A", "#FFAA60", "#FFD7A6"])
            gain = rnd.uniform(0.22, 0.55)
            it, _ = mesh(ids_b, f"Mote {gi}.{mi}", d_box, {"baseColor": const([v * gain for v in hex_lin(warm)])}, [x, y, z],
                         scale=[s * 100, s * 1.25 * 100, 10 * 100], binding_extra=UNLIT, casts=False)
            items.append(it)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": L_BACK, "data": data, "items": items})
    for gi, gid in enumerate(mote_groups):
        dx, dy = [(60, -90), (-40, -70), (80, -110), (-55, -60)][gi]
        keys = [(0.0, [0, 0, 0], "linear"), (t_end, [dx, dy, 0], (0.42, 0.0, 0.58, 1.0))]
        acts.append(anim(L_BACK, gid, "position", ease_kf(f"mote{gi}", keys, kind="vector3")))
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": L_BACK, "effectId": 10901,
                 "effect": {"type": "gaussianBlur", "blurriness": 9}})
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": L_BACK, "effectId": 10902,
                 "effect": {"type": "glow", "glowThreshold": 16, "glowRadius": 30, "glowIntensity": 1.3}})

    # ================= STAGE (11)
    acts.append(scene_layer(L_STAGE, "Stage (lit set, boxes, stamp)", {
        "id": 20002, "light": {"source": {"type": "color", "color": hex_srgb("#26302F")}, "intensity": 0.05},
        "fog": {"color": hex_srgb("#070A0B"), "startDistance": 3.0, "endDistance": 12.0}}))
    acts += camera_actions(L_STAGE, 20003, cam, 0, t_end)
    spots = {}
    sid = 20010
    for key, s in st.items():
        sid += 3
        spots[key] = sid
        acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": L_STAGE, "item": {
            "type": "Light3D", "id": sid, "parentId": None, "name": f"Spot {key} (~2700K)", "castsShadows": True,
            "color": hex_srgb("#FFB067"),
            "transform": {"position": [s["x"] - 120, -SPOT_H, s["z"] - SPOT_BACK],
                          "relationships": aim(sid + 1, sid + 2, [s["x"], 0, s["z"]])},
            "emitter": {"type": "spot", "power": P_FULL * s["power"], "coneAngle": 22, "coneFeather": 0.45, "sourceRadius": 40}}})
    RIM = 20090
    acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": L_STAGE, "item": {
        "type": "Light3D", "id": RIM, "parentId": None, "name": "Teal-green rim (behind)", "castsShadows": False,
        "color": hex_srgb("#8FE8CF"),
        "transform": {"position": [2400, -1900, 3400], "relationships": aim(20091, 20092, [2400, -250, 100])},
        "emitter": {"type": "spot", "power": float(os.environ.get("TH_RIM", 300)), "coneAngle": 120, "coneFeather": 0.9, "sourceRadius": 300}}})

    data, items = [], []
    D = {}
    for key, geom in [("base", {"type": "box", "size": BASE}), ("lid", {"type": "box", "size": LID}),
                      ("swoosh", {"type": "plane", "size": [SW_W, SW_W / 2.806]}),
                      ("unit", {"type": "box", "size": [1, 1, 1]}),
                      ("ink", {"type": "plane", "size": [172, 172 / (1400 / 600)]}),
                      ("rubber", {"type": "box", "size": [176, 12, 92]}),
                      ("block", {"type": "box", "size": [190, 54, 104]}),
                      ("collar", {"type": "cylinder", "radius": 37, "height": 16}),
                      ("neck", {"type": "cylinder", "radius": 25, "height": 70}),
                      ("knob", {"type": "sphere", "radius": 47})]:
        D[key] = ids_s()
        data.append(mesh_data(D[key], key + " geo", geom))
    bevel = lambda w: [{"type": "bevel", "id": ids_s(), "width": w, "segments": 2, "profile": 0.5, "limitAngle": 30}]
    mats = box_materials()
    # polished dark floor, scuffed (the Grunge 353 map varies its gloss)
    fmap = {"coordinates": "world", "projection": {"type": "box"}, "transform": {"position": [0, 0, 0], "scale": [100, 100, 100]}}
    floor_in = {"baseColor": const(hex_lin("#34302C")),
                "roughness": scalar_tex_input(image_tex("grunge353_dispmap", scale=(1 / 2.2, 1 / 2.2), mapping=fmap), 0.55)}
    it, _ = mesh(ids_s, "Stage floor", D["unit"], floor_in, [2500, 20, 1500], scale=[16000 * 100, 40 * 100, 7000 * 100])
    items.append(it)

    box_gid = {}
    for key, name, c, q in all_boxes():
        gid = ids_s()
        box_gid[key] = (gid, c, q)
        items += box_items(ids_s, D, mats, name, gid, c, q, bevel)
    # TARIFF ink on the lid of the stamped box (part of the 3D scene; patchy ink baked from Grunge 353)
    tgid = box_gid["tariff0"][0]
    ink_g = ids_s()
    items.append({"type": "Group3D", "id": ink_g, "parentId": tgid, "name": "TARIFF ink (appears on impact)",
                  "transform": {"position": [6, -61.7, -4], "rotation": rot_euler(0, -4, 0), "scale": [1, 1, 1]}})
    ink_in = {"baseColor": color_tex_input(image_tex("tariff_ink", wrap="clampToEdge"), [1, 1, 1]),
              "coverage": scalar_tex_input(image_tex("tariff_ink", wrap="clampToEdge"), 1.0, alpha=True), "alphaCutoff": const(0.38)}
    it, _ = mesh(ids_s, "TARIFF ink", D["ink"], ink_in, [0, 0, 0], parent=ink_g, rot=rot_euler(-90, 0, 0), casts=False,
                 binding_extra={"unlit": True, "alphaMode": "mask", "doubleSided": True})   # ink absorbs: reads dark red on the lit lid
    items.append(it)
    # the customs stamp: dark worn wooden handle and block, red rubber face (origin = centre of the face)
    wood = {"baseColor": color_tex_input(image_tex("stamp_wood"), [0.62, 0.62, 0.62]), "roughness": const(0.5)}
    rubber = {"baseColor": color_tex_input(image_tex("stamp_rubber"), [1, 1, 1]), "roughness": const(0.45)}
    stamp = ids_s()
    s0 = st["tariff"]
    items.append({"type": "Group3D", "id": stamp, "parentId": None, "name": "Customs stamp",
                  "transform": {"position": [s0["x"] + 6, stamp_face_y(0), s0["z"] - 4], "rotation": rot_euler(0, s0["yaw"] - 4, -2.5)}})
    for name, dk, mat, pos, sc, mods in [("Stamp rubber face", "rubber", rubber, [0, -6, 0], None, bevel(1.5)),
                                         ("Stamp block", "block", wood, [0, -39, 0], None, bevel(5.0)),
                                         ("Stamp collar", "collar", wood, [0, -74, 0], None, None),
                                         ("Stamp neck", "neck", wood, [0, -115, 0], None, None),
                                         ("Stamp knob", "knob", wood, [0, -186, 0], [100, 88, 100], None)]:
        it, _ = mesh(ids_s, name, D[dk], mat, pos, parent=stamp, scale=sc, mods=mods)
        items.append(it)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": L_STAGE, "data": data, "items": items})
    box_mesh_ids = [it["id"] for it in items if it["type"] == "Mesh3D" and " box " in it["name"]]
    receivers = [it["id"] for it in items if it["type"] == "Mesh3D" and (it["name"] == "Stage floor" or it["name"] == "TARIFF box 1 lid")]
    acts.append({"type": "setFxScene3DRenderSettings", "compositionId": COMP, "layerId": L_STAGE, "settings": {
        "id": L_STAGE * 1000 + 97, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [],
        "outputs": [], "previewOutput": None,
        "lightLinks": [{"lightId": RIM, "illuminatedObjects": {"type": "objects", "items": box_mesh_ids},
                        "shadowCasters": {"type": "all"}, "shadowReceivers": {"type": "all"}}]
        + [{"lightId": sid_, "illuminatedObjects": {"type": "all"}, "shadowCasters": {"type": "all"},
            "shadowReceivers": {"type": "objects", "items": receivers}} for sid_ in spots.values()]}})

    # ---- animation
    # stamp: drop, hit, press, lift
    sp = [(f / FPS, [s0["x"] + 6, stamp_face_y(f / FPS), s0["z"] - 4]) for f in range(0, 24)]
    acts.append(anim(L_STAGE, stamp, "position", kf_track(sp, "vector3", "stamp", 0.3)))
    # TARIFF box squash (bottom stays on the floor) and the ink appearing under the stamp at the hit
    tg, tc, tq = box_gid["tariff0"]
    ps, ss = [], []
    for f in range(0, 24):
        sy, sx = squash(f / FPS)
        ps.append((f / FPS, [tc[0], -BOX["h"] / 2 * sy / 100, tc[2]]))
        ss.append((f / FPS, [sx, sy, sx]))
    acts.append(anim(L_STAGE, tg, "position", kf_track(ps, "vector3", "tsq_p", 0.05)))
    acts.append(anim(L_STAGE, tg, "scale", kf_track(ss, "vector3", "tsq_s", 0.05)))
    acts.append(anim(L_STAGE, ink_g, "scale", ease_kf("ink", [(0.0, [1, 1, 1], "hold"), ((F_IMPACT + 0.5) / FPS, [100, 100, 100], "hold")],
                                                     kind="vector3")))
    # the knocked China box, and the wobble of the three left standing
    kps, kqs = knock_motion()
    g3 = box_gid["china3"][0]
    acts.append(anim(L_STAGE, g3, "position", kf_track(kps, "vector3", "knp", 0.3)))
    acts.append(anim(L_STAGE, g3, "rotation", kf_track(kqs, "quaternion", "knq", 0.003)))
    for k in (1, 2):
        g, c, q = box_gid[f"china{k}"]
        qs = [(f / FPS, qmul(wobble(k, f / FPS), q)) for f in range(F_HIT - 1, F_HIT + 40)]
        acts.append(anim(L_STAGE, g, "rotation", kf_track(qs, "quaternion", f"wob{k}", 0.002)))
    # lights: the stamp dip, the 2028 lamp failing
    acts.append(anim(L_STAGE, spots["tariff"], "power", frames_keys(lambda t: P_FULL * tariff_light(t), "tdip")))
    acts.append(anim(L_STAGE, spots["y2028"], "power", frames_keys(lambda t: P_FULL * light_2028(t), "l28")))

    # ================= REFLECTION (12): mirror across the floor (y = 0), lit by mirrored spots
    acts.append(scene_layer(L_REFL, "Floor reflection (mirror pass)", {
        "id": 50002, "light": {"source": {"type": "color", "color": hex_srgb("#26302F")}, "intensity": 0.05},
        "fog": {"color": hex_srgb("#070A0B"), "startDistance": 3.0, "endDistance": 12.0}}))
    acts += camera_actions(L_REFL, 50003, cam, 0, t_end, tol_pos=0.15, tol_rot=0.01)
    rid = 50010
    mspots = {}
    for key, s in st.items():
        rid += 3
        mspots[key] = rid
        acts.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": L_REFL, "item": {
            "type": "Light3D", "id": rid, "parentId": None, "name": f"Mirrored spot {key}", "castsShadows": False,
            "color": hex_srgb("#FFB067"),
            "transform": {"position": [s["x"] - 120, SPOT_H, s["z"] - SPOT_BACK], "relationships": aim(rid + 1, rid + 2, [s["x"], 0, s["z"]])},
            "emitter": {"type": "spot", "power": P_FULL * s["power"], "coneAngle": 22, "coneFeather": 0.45, "sourceRadius": 40}}})
    acts.append(anim(L_REFL, mspots["tariff"], "power", frames_keys(lambda t: P_FULL * tariff_light(t), "mtdip")))
    acts.append(anim(L_REFL, mspots["y2028"], "power", frames_keys(lambda t: P_FULL * light_2028(t), "ml28")))
    data, items = [], []
    R = {k: ids_r() for k in ("base", "lid")}
    data += [mesh_data(R["base"], "base", {"type": "box", "size": BASE}), mesh_data(R["lid"], "lid", {"type": "box", "size": LID})]
    black = {"baseColor": const([0, 0, 0])}
    rside = {"baseColor": color_tex_input(image_tex("box_side_orange"), [ORANGE_GAIN] * 3), "roughness": const(0.9)}
    rlid = {"baseColor": color_tex_input(image_tex("box_lid_orange"), [ORANGE_GAIN] * 3), "roughness": const(0.9)}
    rgroups = {}
    for key, name, c, q in all_boxes():
        hg, mg = ids_r(), ids_r()
        items.append({"type": "Group3D", "id": hg, "parentId": None, "name": f"Hold-out {name}",
                      "transform": {"position": c, "rotation": {"type": "quaternion", "value": q}}})
        for nm, dk, pos in (("base", "base", [0, 5, 0]), ("lid", "lid", [0, -46, 0])):
            it, _ = mesh(ids_r, f"Hold-out {name} {nm}", R[dk], black, pos, parent=hg, binding_extra=UNLIT, casts=False)
            items.append(it)
        items.append({"type": "Group3D", "id": mg, "parentId": None, "name": f"Mirror {name}",
                      "transform": {"position": [c[0], -c[1], c[2]], "rotation": {"type": "quaternion", "value": mirror_quat(q)}}})
        for nm, dk, pos, mat in (("base", "base", [0, -5, 0], rside), ("lid", "lid", [0, 46, 0], rlid)):
            it, _ = mesh(ids_r, f"Mirror {name} {nm}", R[dk], mat, pos, parent=mg, casts=False)
            items.append(it)
        rgroups[key] = (hg, mg)
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": L_REFL, "data": data, "items": items})
    hg, mg = rgroups["china3"]
    acts.append(anim(L_REFL, hg, "position", kf_track(kps, "vector3", "rknp_h", 0.6)))
    acts.append(anim(L_REFL, hg, "rotation", kf_track(kqs, "quaternion", "rknq_h", 0.01)))
    acts.append(anim(L_REFL, mg, "position", kf_track([(t, [p[0], -p[1], p[2]]) for t, p in kps], "vector3", "rknp_m", 0.6)))
    acts.append(anim(L_REFL, mg, "rotation", kf_track([(t, mirror_quat(q)) for t, q in kqs], "quaternion", "rknq_m", 0.01)))
    hg, mg = rgroups["tariff0"]
    for g, sgn in ((hg, 1), (mg, -1)):
        acts.append(anim(L_REFL, g, "position", kf_track([(t, [p[0], sgn * p[1], p[2]]) for t, p in ps], "vector3", f"rtsq{g}", 0.1)))
        acts.append(anim(L_REFL, g, "scale", kf_track(ss, "vector3", f"rtss{g}", 0.1)))
    acts.append({"type": "updateLayerField", "compositionId": COMP, "layerId": L_REFL, "propertyName": "blendMode", "value": "add"})
    acts.append({"type": "setFxPropertyValue", "compositionId": COMP, "target": {"type": "layerProperty", "property": {"layerId": L_REFL, "propertyType": "opacity"}},
                 "value": {"type": "float", "value": 24}})
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": L_REFL, "effectId": 50901,
                 "effect": {"type": "gaussianBlur", "blurriness": 7}})

    # ================= HAZE (14) and the 2028 BEAM (15)
    def cone_items(ids, d_cone, d_disc, key, gain, with_pool):
        s = st[key]
        out = []
        tip = [s["x"] - 120, -SPOT_H, s["z"] - SPOT_BACK]
        base = [s["x"], 0, s["z"]]
        ax = [b - a for a, b in zip(tip, base)]
        Lc = math.sqrt(sum(c * c for c in ax))
        mid = [(a + b) / 2 for a, b in zip(tip, base)]
        # the cone primitive points along -Y (apex up); tilt it onto the tip->base axis
        tilt_x = math.degrees(math.atan2(ax[2], ax[1]))
        tilt_z = -math.degrees(math.atan2(ax[0], ax[1]))
        for i, (sc_r, cov) in enumerate([(1.0, 0.045), (0.55, 0.075)]):
            it, _ = mesh(ids, f"{key} cone {i}", d_cone, {"baseColor": const([c * gain for c in hex_lin("#FFC796")]),
                                                          "coverage": const(cov)},
                         mid, rot=rot_euler(tilt_x, 0, tilt_z), scale=[sc_r * 100, Lc / 1000 * 100, sc_r * 100],
                         binding_extra={"unlit": True, "alphaMode": "blend", "doubleSided": True}, casts=False)
            out.append(it)
        if with_pool:
            it, _ = mesh(ids, f"{key} pool glow", d_disc, {"baseColor": const([c * 0.10 * gain for c in hex_lin("#FFB06A")]), "coverage": const(0.6)},
                         [s["x"], -2, s["z"]], scale=[100, 100, 100], binding_extra={**UNLIT, "alphaMode": "blend", "doubleSided": True}, casts=False)
            out.append(it)
        return out

    cone_r = SPOT_H * math.tan(math.radians(11)) * 1.05
    for lid_, ids_x, nm in ((L_HAZE, ids_h, "Haze (spotlight cones)"), (L_BEAM, ids_e, "2028 beam (cone + pool glow)")):
        acts.append(scene_layer(lid_, nm, {"id": lid_ * 1000 + 2}))
        acts += camera_actions(lid_, lid_ * 1000 + 3, cam, 0, t_end, tol_pos=0.3, tol_rot=0.02)
        data, items = [], []
        d_cone, d_disc = ids_x(), ids_x()
        data.append(mesh_data(d_cone, "cone", {"type": "cone", "radius": cone_r, "height": 1000}))
        data.append(mesh_data(d_disc, "pool", {"type": "cylinder", "radius": cone_r * 0.9, "height": 2}))
        keys = [k for k in st if k != "y2028"] if lid_ == L_HAZE else ["y2028"]
        for key in keys:
            items += cone_items(ids_x, d_cone, d_disc, key, st[key]["light"] / (1.0 if key != "y2028" else st[key]["light"]), key == "y2028")
        acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": lid_, "data": data, "items": items})
        acts.append({"type": "updateLayerField", "compositionId": COMP, "layerId": lid_, "propertyName": "blendMode", "value": "screen"})
        acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": lid_, "effectId": lid_ * 1000 + 901,
                     "effect": {"type": "gaussianBlur", "blurriness": 40 if lid_ == L_HAZE else 26}})
    acts.append({"type": "setFxPropertyValue", "compositionId": COMP, "target": {"type": "layerProperty", "property": {"layerId": L_HAZE, "propertyType": "opacity"}},
                 "value": {"type": "float", "value": 30}})
    # the 2028 beam's brightness follows its lamp exactly (30% -> stutter -> out)
    beam_op = lambda t: 30 * 0.5 * light_2028(t) / STATIONS["y2028"]["power"]   # same haze as the others, at its lamp's level
    acts.append({"type": "setFxPropertyKeyframes", "compositionId": COMP, "property": {"layerId": L_BEAM, "propertyType": "opacity"},
                 "keyframes": frames_keys(beam_op, "beamop")})

    # ================= DUST (16): the stamp's burst and the knock-off puff
    acts.append(scene_layer(L_DUST, "Dust (stamp burst, knock-off puff)", {"id": 80002}))
    acts += camera_actions(L_DUST, 80003, cam, 0, t_end, tol_pos=0.3, tol_rot=0.02)
    data, items = [], []
    d_sprite = ids_d()
    data.append(mesh_data(d_sprite, "sprite", {"type": "plane", "size": [100, 100]}))
    dust_mat = {"baseColor": color_tex_input(image_tex("dust_puff", wrap="clampToEdge"), [0.95, 0.88, 0.78]),
                "coverage": scalar_tex_input(image_tex("dust_puff", wrap="clampToEdge"), 1.0, alpha=True)}
    rnd = random.Random(353)
    sprites = []

    def face_cam(p, t):
        P, _ = cam(t)
        q, _ = look_quat(p, P)
        return q

    def burst(prefix, origin, t0, n, spread, rise, s0_, s1_, life, ring_r):
        for i in range(n):
            a = 2 * math.pi * i / n + rnd.uniform(-0.25, 0.25)
            p0 = [origin[0] + math.cos(a) * ring_r[0], origin[1] - rnd.uniform(0, 20), origin[2] + math.sin(a) * ring_r[1]]
            p1 = [p0[0] + math.cos(a) * spread * rnd.uniform(0.7, 1.2), p0[1] - rise * rnd.uniform(0.6, 1.3),
                  p0[2] + math.sin(a) * spread * 0.7 * rnd.uniform(0.7, 1.2)]
            gid = ids_d()
            q = face_cam(p0, t0 + 0.2)
            items.append({"type": "Group3D", "id": gid, "parentId": None, "name": f"{prefix} puff {i}",
                          "transform": {"position": p0, "rotation": {"type": "quaternion", "value": q}, "scale": [1, 1, 1]}})
            it, _ = mesh(ids_d, f"{prefix} puff sprite {i}", d_sprite, dust_mat, [0, 0, 0], parent=gid,
                         binding_extra={**UNLIT, "alphaMode": "blend", "doubleSided": True}, casts=False)
            items.append(it)
            sprites.append((gid, p0, p1, t0, s0_ * rnd.uniform(0.8, 1.2), s1_ * rnd.uniform(0.8, 1.25), life * rnd.uniform(0.8, 1.15)))

    tc0 = st["tariff"]
    burst("Stamp", [tc0["x"], -BOX["h"] + 10, tc0["z"]], F_IMPACT / FPS, 11, 230, 70, 60, 260, 1.0, (185, 120))
    kc = [kps[F_HIT][1][0] - 150, kps[F_HIT][1][1] - 40, kps[F_HIT][1][2]]
    burst("Knock", kc, F_HIT / FPS, 5, 90, 50, 40, 150, 0.7, (40, 40))
    acts.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": L_DUST, "data": data, "items": items})
    for gid, p0, p1, t0, s0_, s1_, life in sprites:
        e_out = (0.12, 0.75, 0.35, 1.0)
        pk = [(0.0, p0, "hold"), (t0, p0, "hold"), (t0 + life, p1, e_out)]
        sk = [(0.0, [1, 1, 1], "hold"), (t0 - 0.001, [1, 1, 1], "hold"), (t0, [s0_, s0_, s0_], "hold"), (t0 + life, [s1_, s1_, s1_], e_out)]
        acts.append(anim(L_DUST, gid, "position", ease_kf(f"dp{gid}", pk, kind="vector3")))
        acts.append(anim(L_DUST, gid, "scale", ease_kf(f"ds{gid}", sk, kind="vector3")))
    ti, tk = F_IMPACT / FPS, F_HIT / FPS
    acts.append({"type": "setFxPropertyKeyframes", "compositionId": COMP, "property": {"layerId": L_DUST, "propertyType": "opacity"},
                 "keyframes": ease_kf("dustop", [(0.0, 0, "hold"), (ti - 0.001, 0, "hold"), (ti + 0.05, 62, EASE_OUT),
                                                 (ti + 0.45, 34, EASE_IN_OUT), (ti + 1.05, 0, EASE_IN_OUT),
                                                 (tk - 0.001, 0, "hold"), (tk + 0.04, 40, EASE_OUT), (tk + 0.75, 0, EASE_IN_OUT)])})
    acts.append({"type": "updateLayerField", "compositionId": COMP, "layerId": L_DUST, "propertyName": "blendMode", "value": "screen"})
    acts.append({"type": "addFxLayerEffect", "compositionId": COMP, "layerId": L_DUST, "effectId": 16901,
                 "effect": {"type": "gaussianBlur", "blurriness": 5}})

    info = {"spots": spots, "box_gid": {k: v[0] for k, v in box_gid.items()}}
    return acts, info
