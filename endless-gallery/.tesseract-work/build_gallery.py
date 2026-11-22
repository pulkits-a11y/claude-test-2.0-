"""Build the Endless Gallery Tesseract action batch (scene + animation).

Reads lamp_timeline.json (timeline.py) so beams, lenses, the hero spotlight and the projector
mask video (gobo_render.py) all agree on when every lamp catches, flickers and dies.

Units: pixelsPerMeter 1000 (1 px = 1 mm). Tesseract axes: X right, Y DOWN, Z into the screen.
Hero pedestal at the origin, row 0 is the front row, rows recede toward +Z, column c at x = c*1.5 m.

Usage:
  python3 build_gallery.py lamp_timeline.json OUT.json [--rows 27 --cols 20] [--gobo-layer 2]
"""
import argparse
import json
import math

FPS = 30
MS = 1000.0 / FPS
COL = 1500
ROW = 2200
PED_W, PED_H = 450, 1000
TOP_Y = -PED_H
LAMP_GAP = 1600
LAMP_Y = TOP_Y - LAMP_GAP          # lens plane, -2600
PROJ_H = 300_000
PROJ_CONE = 12.0
SCENE_LAYER = 1

# Shoe placement: asset id, vertical offset so the sole meets the pedestal top, base yaw (toe -> +X)
SHOES = {0: ('dunk', -55), 1: ('af1', 0), 2: ('aj1', 0)}
SHOE_YAW = 90           # toe points +X (screen right)
THREE_QUARTER = -22     # extra yaw so every toe turns toward the camera (three-quarter profile)
TIERS = [(0, ''), (1, '_mid'), (6, '_far')]

WARM = (1.0, 0.70, 0.42)          # tungsten-ish glow, sRGB
VOID = (0.006, 0.008, 0.010)


def lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rot(x=0.0, y=0.0, z=0.0):
    return {"type": "euler", "order": "XYZ", "orientation": [0, 0, 0],
            "rotationX": x, "rotationY": y, "rotationZ": z}


def ms(frame):
    return round(frame * MS, 3)


def bezier(x1, y1, x2, y2):
    return {"type": "cubicBezier", "x1": x1, "y1": y1, "x2": x2, "y2": y2}


HOLD = {"type": "hold"}
EASE_IN_OUT = bezier(0.42, 0.0, 0.58, 1.0)
# Snap pull-backs: whip out, then a long soft brake (most of the distance in the first ~30%).
SNAP_1 = bezier(0.25, 0.9, 0.15, 1.0)
SNAP_2 = bezier(0.2, 0.9, 0.1, 1.0)
DRIFT = bezier(0.35, 0.15, 0.75, 0.85)
PUSH_IN = bezier(0.22, 0.12, 0.45, 1.0)   # already moving at f0, settles into f18


def bezier_progress(e, t):
    """Evaluate a CSS cubic-bezier easing at normalised time t (for the printed checks)."""
    x1, y1, x2, y2 = e['x1'], e['y1'], e['x2'], e['y2']
    lo, hi = 0.0, 1.0
    for _ in range(60):
        s = (lo + hi) / 2
        x = 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
        lo, hi = (s, hi) if x < t else (lo, s)
    s = (lo + hi) / 2
    return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3


class B:
    def __init__(self):
        self.A = []
        self.n = 10_000

    def id(self):
        self.n += 1
        return self.n

    def add(self, a):
        self.A.append(a)

    def anim(self, item, prop, keys):
        """keys: list of (frame, value_record, easing). Keyframe ids are stable strings."""
        kf = [{"id": f"k{item}-{prop}-{i}", "layerTime": ms(f), "value": v, "easing": e}
              for i, (f, v, e) in enumerate(keys)]
        self.add({"type": "setFxAnimator", "compositionId": "main",
                  "target": {"type": "styleProperty", "layerId": SCENE_LAYER, "itemId": item, "propertyName": prop},
                  "animator": {"type": "keyframes", "enabled": True, "keyframes": kf},
                  "dependencies": [], "layerRefBindings": []})

    def material(self, inputs, alpha=None, unlit=False, double=False):
        sid, bid = self.id(), self.id()
        bnd = {"id": bid, "inputs": inputs}
        if alpha:
            bnd["alphaMode"] = alpha
        if unlit:
            bnd["unlit"] = True
        if double:
            bnd["doubleSided"] = True
        return sid, bid, {"id": sid, "name": f"m{sid}", "binding": bnd}

    def mesh(self, name, geom, pos, mat, parent=None, rotation=None, cast=True, receive=True, modifiers=None):
        did, iid = self.id(), self.id()
        sid, _, slot = mat
        tr = {"position": list(pos)}
        if rotation:
            tr["rotation"] = rotation
        item = {"type": "Mesh3D", "id": iid, "parentId": parent, "name": name, "dataId": did, "packing": "whole",
                "transform": tr, "materialSlots": [slot],
                "regionSlots": [{"region": "primary", "slotId": sid}, {"region": "side", "slotId": sid}],
                "castsShadows": cast, "receivesShadows": receive}
        if modifiers:
            item["modifiers"] = modifiers
        self.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER,
                  "data": [{"type": "mesh", "id": did, "name": name, "geometry": geom,
                            "regions": [{"key": "primary", "name": "Primary"}, {"key": "side", "name": "Side"}]}],
                  "items": [item]})
        return iid

    def grid(self, name, pos, counts, spacing):
        gid = self.id()
        self.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER,
                  "item": {"type": "Group3D", "id": gid, "parentId": None, "name": name, "transform": {"position": list(pos)},
                           "array": {"type": "grid", "id": self.id(), "counts": list(counts), "spacing": list(spacing)}}})
        return gid


def const(v):
    return {"type": "constant", "value": v}


def color_rec(rgb, a=1.0):
    return {"type": "color", "value": [rgb[0], rgb[1], rgb[2], a]}


def level_keys(levels, to_value, settle_easing=EASE_IN_OUT):
    """Keys only where the level changes; flicker steps hold, the hero's slow dim eases."""
    keys = []
    prev = None
    for f, lv in enumerate(levels):
        if prev is None or abs(lv - prev) > 1e-4:
            ease = HOLD if prev is None or abs(lv - prev) > 0.05 else settle_easing
            keys.append((f, to_value(lv), ease))
            prev = lv
    return keys


def build(a, tl):
    b = B()
    C, R = a.cols, a.rows
    cells = tl['cells']
    depth = (R - 1) * ROW

    # --- Scene layer, world -------------------------------------------------------------------
    b.add({"type": "createFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER, "name": "Endless Gallery",
           "pixelsPerMeter": 1000, "view": {"id": 9001, "exposure": a.exposure},
           "activeRange": {"start": 0, "duration": 2800},
           "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100},
           "world": {"id": 9002},
           "renderSettings": {"id": 9003, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [],
                              "lightLinks": [], "outputs": [], "previewOutput": None}})
    b.add({"type": "setFxScene3DWorld", "compositionId": "main", "layerId": SCENE_LAYER,
           "world": {"id": 9002, "background": {"type": "color", "color": [*VOID, 1]},
                     "light": {"source": {"type": "color", "color": [0.45, 0.70, 0.66, 1]}, "intensity": a.ambient},
                     "fog": {"color": [*VOID, 1], "startDistance": 22, "endDistance": 78}}})

    # --- Camera rig: drift group -> camera + look target ----------------------------------------
    rig = b.id()
    b.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER,
           "item": {"type": "Group3D", "id": rig, "parentId": None, "name": "Camera drift rig", "transform": {"position": [0, 0, 0]}}})
    look = b.id()
    b.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER,
           "item": {"type": "Group3D", "id": look, "parentId": rig, "name": "Camera look target", "transform": {"position": [0, -1060, 0]}}})
    cam = b.id()
    b.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER,
           "item": {"type": "Camera3D", "id": cam, "parentId": rig, "name": "Camera",
                    "transform": {"position": [0, -1085, -750], "relationships": {"constraints": [
                        {"type": "aim", "id": b.id(), "target": {"id": b.id(), "target": {"type": "item", "item": look},
                                                                 "offset": [0, 0, 0], "offsetSpace": "local"},
                         "up": [0, 1, 0], "upSpace": "world", "forwardAxis": "positiveZ", "influence": 1}]}},
                    "lens": {"type": "physical", "focalLengthMm": 35, "sensorMm": [36, 20.25], "fNumber": 2.8}}})
    b.add({"type": "setFxScene3DActiveCamera", "compositionId": "main", "layerId": SCENE_LAYER, "cameraItemId": cam})

    def polar(dist, az_deg, height_mm, tgt=(0, -1060, 0)):
        az = math.radians(az_deg)
        return [tgt[0] + dist * math.sin(az), -height_mm, tgt[2] - dist * math.cos(az)]

    p0 = polar(750, -1.25, 1062)       # f0: Dunk ~40% of frame, low three-quarter
    p18 = polar(690, 1.25, 1058)       # f18: slow reverent push-in + 2.5 deg orbit
    p48 = [0, -1850, -8400]            # f48: the row (after snap 1 + drift)
    p83 = [0, -5300, -13600]           # f83: high wide hall (after snap 2 + drift)
    t48 = [0, -1150, 0]
    t83 = [0, -2710, 16290]            # pitch ~5 deg down: vanishing point just above centre
    v3 = lambda p: {"type": "vector3", "value": [round(x, 2) for x in p]}
    # Each snap segment starts one frame before its word so movement is visible ON f19 / f49.
    b.anim(cam, "position", [(0, v3(p0), HOLD), (18, v3(p18), PUSH_IN),
                             (48, v3(p48), SNAP_1), (83, v3(p83), SNAP_2)])
    b.anim(look, "position", [(0, v3([0, -1060, 0]), HOLD), (18, v3([0, -1060, 0]), HOLD),
                              (48, v3(t48), SNAP_1), (83, v3(t83), SNAP_2)])
    # Never static: a slow extra creep from the end of snap 1 to the cut
    b.anim(rig, "position", [(0, v3([0, 0, 0]), HOLD), (52, v3([0, 0, 0]), HOLD), (83, v3([0, -160, -420]), DRIFT)])
    fl = lambda x: {"type": "float", "value": x}
    b.anim(cam, "fNumber", [(0, fl(2.8), HOLD), (18, fl(2.8), HOLD), (30, fl(8.0), SNAP_1), (56, fl(14.0), SNAP_2)])

    # --- Floor, pedestals, lamp hardware -------------------------------------------------------------
    b.mesh("Floor (polished dark concrete)", {"type": "box", "size": [2 * C * COL + 30000, 20, depth + 40000]},
           [0, 10, depth / 2 + 4000],
           b.material({"baseColor": const([0.011, 0.011, 0.012]), "roughness": const(0.28)}), cast=False)
    g = b.grid("Pedestals", [-C * COL, 0, 0], [2 * C + 1, 1, R], [COL, 0, ROW])
    b.mesh("Pedestal (black stone)", {"type": "box", "size": [PED_W, PED_H, PED_W]}, [0, -PED_H / 2, 0],
           b.material({"baseColor": const([0.0085, 0.0085, 0.009]), "roughness": const(0.9),
                       "specular": const(0.25)}), parent=g,
           modifiers=[{"type": "bevel", "id": b.id(), "width": 7, "segments": 2, "profile": 0.5, "limitAngle": 30}])
    g = b.grid("Lamp hardware", [-C * COL, 0, 0], [2 * C + 1, 1, R], [COL, 0, ROW])
    blk = b.material({"baseColor": const([0.008, 0.008, 0.008]), "roughness": const(0.38), "metallic": const(0.7)})
    b.mesh("Lamp housing", {"type": "cylinder", "radius": 60, "height": 200}, [0, LAMP_Y - 103, 0], blk, parent=g, cast=False)
    b.mesh("Lamp cable", {"type": "cylinder", "radius": 4, "height": 7000}, [0, LAMP_Y - 3700, 0],
           b.material({"baseColor": const([0.01, 0.01, 0.01]), "roughness": const(0.5)}), parent=g, cast=False)

    warm_lin = [lin(x) for x in WARM]

    # --- Per-lamp lens (row 0 only: rows behind are only ever seen from above) and beam ----------------
    dark_lens = b.material({"baseColor": const([0.02, 0.016, 0.012]), "roughness": const(0.2)})
    g = b.grid("Lamp lenses (unlit rows)", [-C * COL, 0, ROW], [2 * C + 1, 1, R - 1], [COL, 0, ROW])
    b.mesh("Lens", {"type": "cylinder", "radius": 52, "height": 6}, [0, LAMP_Y + 2, 0], dark_lens, parent=g, cast=False)
    for c in range(-C, C + 1):
        cell = cells[f"{c},0"]
        sid, bid, slot = b.material({"baseColor": const([0.0, 0.0, 0.0]), "roughness": const(0.5),
                                     "emissiveColor": const(warm_lin), "emissiveStrength": const(0.0)})
        b.mesh(f"Lens c{c} r0", {"type": "cylinder", "radius": 52, "height": 6}, [c * COL, LAMP_Y + 2, 0],
               (sid, bid, slot), cast=False, receive=False)
        b.anim(bid, "emissiveStrength", level_keys(cell['level'],
               lambda lv: {"type": "float", "value": round(min(lv, 1.2) * a.lens_gain, 4)}))

    if not a.no_beams:
        # Beams are faint translucent cones LIT by the projector, so each one follows its lamp's
        # mask disc (on / flicker / off) and carries the mask's grain. One array, one material.
        # Row 0 without the hero column (two arrays), rows 1+ in one array
        beam_groups = [b.grid("Beams row 0 left", [-C * COL, 0, 0], [C, 1, 1], [COL, 0, ROW]),
                       b.grid("Beams row 0 right", [COL, 0, 0], [C, 1, 1], [COL, 0, ROW]),
                       b.grid("Beams rows 1+", [-C * COL, 0, ROW], [2 * C + 1, 1, R - 1], [COL, 0, ROW])]
        clear = b.material({"baseColor": const([0, 0, 0]), "roughness": const(1.0), "coverage": const(0.0)}, alpha="blend")
        fall = {"type": "texture", "factor": a.beam_alpha, "sample": {
            "texture": {"source": {"type": "image", "assetId": "beamfall"}, "scale": [1, 1], "wrapU": "repeat",
                        "wrapV": "clampToEdge", "minFilter": "linear", "magFilter": "linear", "mipmaps": False},
            "interpretation": {"type": "data"}, "selection": {"type": "alpha"}}}
        beam = b.material({"baseColor": const([1.0, 1.0, 1.0]), "roughness": const(1.0), "coverage": fall},
                          alpha="blend", double=True)
        did = b.id()
        b.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER,
               "data": [{"type": "mesh", "id": did, "name": "Beam cone", "geometry": {"type": "cone", "radius": 420, "height": LAMP_GAP},
                         "regions": [{"key": "primary", "name": "Primary"}, {"key": "side", "name": "Side"}]}], "items": []})
        for g in beam_groups:
            clear = b.material({"baseColor": const([0, 0, 0]), "roughness": const(1.0), "coverage": const(0.0)}, alpha="blend")
            beam = b.material({"baseColor": const([1.0, 1.0, 1.0]), "roughness": const(1.0), "coverage": json.loads(json.dumps(fall))},
                              alpha="blend", double=True)
            b.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER, "data": [],
                   "items": [{"type": "Mesh3D", "id": b.id(), "parentId": g, "name": "Beam", "dataId": did, "packing": "regions",
                              "transform": {"position": [0, LAMP_Y + LAMP_GAP / 2, 0]},
                              "materialSlots": [clear[2], beam[2]],
                              "regionSlots": [{"region": "primary", "slotId": clear[0]}, {"region": "side", "slotId": beam[0]}],
                              "modifiers": [{"type": "uvProject", "id": b.id(), "projection": {"type": "cylindrical", "axis": "y"}}],
                              "castsShadows": False, "receivesShadows": False}]})
        # The hero's beam is its own item: barely there while the camera sits inside it (Phase 1),
        # building to the standard beam as the snap pulls out.
        hfall = json.loads(json.dumps(fall))
        hclear = b.material({"baseColor": const([0, 0, 0]), "roughness": const(1.0), "coverage": const(0.0)}, alpha="blend")
        hbeam = b.material({"baseColor": const([1.0, 1.0, 1.0]), "roughness": const(1.0), "coverage": hfall},
                           alpha="blend", double=True)
        hid_ = b.id()
        b.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER, "data": [],
               "items": [{"type": "Mesh3D", "id": hid_, "parentId": None, "name": "Hero beam", "dataId": did, "packing": "regions",
                          "transform": {"position": [0, LAMP_Y + LAMP_GAP / 2, 0]},
                          "materialSlots": [hclear[2], hbeam[2]],
                          "regionSlots": [{"region": "primary", "slotId": hclear[0]}, {"region": "side", "slotId": hbeam[0]}],
                          "modifiers": [{"type": "uvProject", "id": b.id(), "projection": {"type": "cylindrical", "axis": "y"}}],
                          "castsShadows": False, "receivesShadows": False}]})
        b.anim(hbeam[1], "coverage", [(0, {"type": "float", "value": round(a.beam_alpha * 0.18, 5)}, HOLD),
                                      (19, {"type": "float", "value": round(a.beam_alpha * 0.18, 5)}, HOLD),
                                      (26, {"type": "float", "value": round(a.beam_alpha * 1.15, 5)}, SNAP_1)])

    # --- Shoes: every pedestal its own item (per-cell control), fixed detail tier per row -------------
    data = {}
    for k, (asset, _) in SHOES.items():
        for _, sfx in TIERS:
            did = b.id()
            data[(k, sfx)] = did
            b.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER,
                   "data": [{"type": "model", "id": did, "name": asset + sfx, "assetId": asset + sfx}], "items": []})
    hero_shoe = None
    shoe_ids = []
    near_shoe_ids = []
    for r in range(R):
        sfx = [s_ for lo, s_ in TIERS if r >= lo][-1]
        items = []
        for c in range(-C, C + 1):
            k = cells[f"{c},{r}"]['type']
            asset, yoff = SHOES[k]
            iid = b.id()
            shoe_ids.append(iid)
            if r <= 3:
                near_shoe_ids.append(iid)
            items.append({"type": "Model3D", "id": iid, "parentId": None, "name": f"{asset}{sfx} c{c} r{r}",
                          "dataId": data[(k, sfx)],
                          "transform": {"position": [c * COL, TOP_Y + yoff, r * ROW],
                                        "rotation": rot(0, SHOE_YAW + THREE_QUARTER, 0), "scale": [100, 100, 100]},
                          "materialSlots": [], "modelRegionSlots": [],
                          "castsShadows": r == 0 and abs(c) <= 1, "receivesShadows": True})
            if (c, r) == (0, 0):
                hero_shoe = iid
        b.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER, "data": [], "items": items})

    # --- Floating square dust motes (as in the ShoeboxTower MG) ------------------------------------------------
    # Tiny tumbling squares drifting slowly, concentrated in the hero lamp's beam. They are lit by the same
    # lights as everything else, so they only sparkle where there is light.
    if a.motes > 0:
        import random
        mr = random.Random(77)
        did = b.id()
        items, anims = [], []
        for i in range(a.motes):
            if i < a.motes * 0.6:      # inside the hero beam
                x, z = mr.gauss(0, 230), mr.gauss(0, 230)
                y = -mr.uniform(1080, 2450)
            else:                      # loosely around the hero row
                x, z = mr.uniform(-5200, 5200), mr.uniform(-1800, 1800)
                y = -mr.uniform(1050, 2550)
            size = mr.uniform(3.5, 7.5)
            iid = b.id()
            items.append({"type": "Mesh3D", "id": iid, "parentId": None, "name": f"Mote {i}", "dataId": did, "packing": "whole",
                          "transform": {"position": [x, y, z], "rotation": rot(mr.uniform(0, 360), mr.uniform(0, 360), 0),
                                        "scale": [size / 6 * 100] * 3},
                          "materialSlots": [], "regionSlots": [], "castsShadows": False, "receivesShadows": False})
            dx, dy, dz = mr.uniform(-45, 45), mr.uniform(-10, 55), mr.uniform(-45, 45)
            anims.append((iid, "position", [(0, {"type": "vector3", "value": [round(x, 1), round(y, 1), round(z, 1)]}, HOLD),
                                            (83, {"type": "vector3", "value": [round(x + dx, 1), round(y + dy, 1), round(z + dz, 1)]},
                                             bezier(0.3, 0.1, 0.7, 0.9))]))
            r0 = mr.uniform(0, 360)
            anims.append((iid, "rotationY", [(0, {"type": "float", "value": round(r0, 1)}, HOLD),
                                             (83, {"type": "float", "value": round(r0 + mr.uniform(-160, 160), 1)},
                                              bezier(0.25, 0.1, 0.75, 0.9))]))
        # each mote gets its own (identical) material slot: slot ids must be unique per item
        for it in items:
            sid, bid, slot = b.material({"baseColor": const([0.85, 0.80, 0.72]), "roughness": const(0.55)}, double=True)
            it["materialSlots"] = [slot]
            it["regionSlots"] = [{"region": "primary", "slotId": sid}, {"region": "side", "slotId": sid}]
        b.add({"type": "addFxScene3DFragment", "compositionId": "main", "layerId": SCENE_LAYER,
               "data": [{"type": "mesh", "id": did, "name": "Mote square", "geometry": {"type": "plane", "size": [6, 6]},
                         "regions": [{"key": "primary", "name": "Primary"}, {"key": "side", "name": "Side"}]}],
               "items": items})
        for iid, prop, keys in anims:
            b.anim(iid, prop, keys)

    # --- Lights --------------------------------------------------------------------------------------------
    hero = cells["0,0"]
    hid = b.id()
    b.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER,
           "item": {"type": "Light3D", "id": hid, "parentId": None, "name": "Hero spotlight",
                    "transform": {"position": [0, LAMP_Y, 0], "rotation": rot(-90)},
                    "emitter": {"type": "spot", "power": a.hero_power, "coneAngle": 34, "coneFeather": 0.5, "sourceRadius": 25},
                    "useTemperature": True, "temperature": a.kelvin, "castsShadows": True}})
    b.anim(hid, "power", level_keys(hero['level'], lambda lv: {"type": "float", "value": round(lv * a.hero_power, 3)}))

    if a.gobo_layer is not None:
        b.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER,
               "item": {"type": "Light3D", "id": b.id(), "parentId": None, "name": "Hall projector (every other lamp)",
                        "transform": {"position": [0, -PROJ_H, depth / 2], "rotation": rot(-90)},
                        "emitter": {"type": "spot", "power": a.proj_power, "coneAngle": PROJ_CONE, "coneFeather": 0.0,
                                    "sourceRadius": 0, "projectorSource": {"type": "layer", "layerId": a.gobo_layer},
                                    "goboDensity": 1.0, "goboWrap": "black"},
                        "useTemperature": True, "temperature": a.kelvin, "castsShadows": False}})

    # Cool teal-green rim from behind (separates shoes from the void) and a soft warm front fill (bounce).
    # "A" lights touch only the hero shoe from f0; "B" lights touch every other shoe and stay at zero until
    # the hall cascades (f50), so nothing outside the hero's pool is visible in Phase 1.
    def aimed_parallel(name, pos, target, irr, extra):
        lid = b.id()
        item = {"type": "Light3D", "id": lid, "parentId": None, "name": name,
                "transform": {"position": pos, "relationships": {"constraints": [
                    {"type": "aim", "id": b.id(), "target": {"id": b.id(), "target": {"type": "world"},
                                                             "offset": target, "offsetSpace": "local"},
                     "up": [0, 1, 0], "upSpace": "world", "forwardAxis": "positiveZ", "influence": 1}]}},
                "emitter": {"type": "parallel", "irradiance": irr}, "castsShadows": False}
        item.update(extra)
        b.add({"type": "addFxScene3DLayer", "compositionId": "main", "layerId": SCENE_LAYER, "item": item})
        return lid
    teal = {"color": [0.55, 0.95, 0.85, 1]}
    warm = {"useTemperature": True, "temperature": 4200}
    rim_a = aimed_parallel("Rim A (hero)", [0, -5000, a.rim_z], [0, -800, 0], a.rim, teal)
    rim_b = aimed_parallel("Rim B (hall)", [0, -5000, a.rim_z], [0, -800, 0], 0.0, teal)
    fill_a = aimed_parallel("Fill A (hero)", [-3000, -4000, -9000], [0, -1050, 0], a.fill, warm)
    fill_b = aimed_parallel("Fill B (front rows)", [-3000, -4000, -9000], [0, -1050, 0], 0.0, warm)
    ramp = bezier(0.4, 0.0, 0.3, 1.0)
    b.anim(rim_b, "irradiance", [(0, {"type": "float", "value": 0.0}, HOLD), (50, {"type": "float", "value": 0.0}, HOLD),
                                 (60, {"type": "float", "value": a.rim}, ramp)])
    b.anim(fill_b, "irradiance", [(0, {"type": "float", "value": 0.0}, HOLD), (50, {"type": "float", "value": 0.0}, HOLD),
                                  (60, {"type": "float", "value": a.fill}, ramp)])
    others = [i for i in shoe_ids if i != hero_shoe]
    near_others = [i for i in near_shoe_ids if i != hero_shoe]
    link = lambda lid, ids: {"lightId": lid, "illuminatedObjects": {"type": "objects", "items": ids},
                             "shadowCasters": {"type": "all"}, "shadowReceivers": {"type": "all"}}
    b.add({"type": "setFxScene3DRenderSettings", "compositionId": "main", "layerId": SCENE_LAYER,
           "settings": {"id": 9003, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [],
                        "lightLinks": [link(rim_a, [hero_shoe]), link(fill_a, [hero_shoe]),
                                       link(rim_b, others), link(fill_b, near_others)],
                        "outputs": [], "previewOutput": None}})
    return b.A, {"hero_shoe": hero_shoe, "camera": cam}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('timeline')
    ap.add_argument('out')
    ap.add_argument('--rows', type=int, default=27)
    ap.add_argument('--cols', type=int, default=20)
    ap.add_argument('--gobo-layer', type=int, default=2)
    ap.add_argument('--no-beams', action='store_true')
    ap.add_argument('--beam-alpha', type=float, default=0.06)
    ap.add_argument('--fill', type=float, default=0.08)
    ap.add_argument('--beam-flip', type=float, default=0.0)
    ap.add_argument('--lens-gain', type=float, default=6.0)
    ap.add_argument('--hero-power', type=float, default=1.2)
    ap.add_argument('--proj-power', type=float, default=15000.0)
    ap.add_argument('--kelvin', type=float, default=3600.0)
    ap.add_argument('--rim', type=float, default=0.12)
    ap.add_argument('--rim-z', type=float, default=60000)
    ap.add_argument('--ambient', type=float, default=0.004)
    ap.add_argument('--exposure', type=float, default=0.0)
    ap.add_argument('--motes', type=int, default=260)
    a = ap.parse_args()
    tl = json.load(open(a.timeline))
    actions, info = build(a, tl)
    json.dump(actions, open(a.out, 'w'))
    for name, e, f0, f1, checks in [("snap 1", SNAP_1, 18, 48, [19, 21, 24, 27, 30, 40]),
                                    ("snap 2", SNAP_2, 48, 83, [49, 51, 54, 57, 60, 70])]:
        print(name, ", ".join(f"f{f}: {100 * bezier_progress(e, (f - f0) / (f1 - f0)):.0f}%" for f in checks))
    print(len(actions), "actions", info)
