"""Look-dev v2: relit street, swoosh decal as alpha-mask plane, UV test box, no DOF/volume."""
import sys
from lib import *

ORANGE = hex_lin("#E8641E")
LAMP_WARM = hex_srgb("#FFB46B")
RIM_TEAL = hex_srgb("#7FE0C4")

A = []
A.append({"type": "createFxScene3DLayer", "compositionId": COMP, "layerId": 1, "name": "Street",
          "pixelsPerMeter": 1000, "view": {"id": 9, "exposure": 0},
          "activeRange": {"start": 0, "duration": 3000},
          "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100},
          "world": {"id": 2},
          "renderSettings": {"id": 97, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [],
                             "lightLinks": [], "outputs": [], "previewOutput": None}})
CAM_POS = [520, -135, -1850]
LOOK = [0, -230, 0]
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Camera3D", "id": 3, "parentId": None, "name": "Camera 35mm",
    "transform": {"position": CAM_POS, "relationships": aim(80, 81, LOOK)},
    "lens": {"type": "physical", "focalLengthMm": 35, "sensorMm": [36, 24], "fNumber": 2.8}}})
A.append({"type": "setFxScene3DActiveCamera", "compositionId": COMP, "layerId": 1, "cameraItemId": 3})
A.append({"type": "setFxScene3DWorld", "compositionId": COMP, "layerId": 1, "world": {
    "id": 2, "background": {"type": "color", "color": hex_srgb("#05070B")},
    "light": {"source": {"type": "color", "color": hex_srgb("#22323E")}, "intensity": 0.06},
    "fog": {"color": hex_srgb("#05080C"), "startDistance": 2.5, "endDistance": 11.0}}})

LAMP_X, LAMP_Z, LAMP_TOP = 1150, -260, -2380
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Light3D", "id": 4, "parentId": None, "name": "Street lamp key (spot)", "castsShadows": True,
    "color": LAMP_WARM,
    "transform": {"position": [LAMP_X - 90, LAMP_TOP + 130, LAMP_Z], "relationships": aim(82, 83, [-60, 0, 40])},
    "emitter": {"type": "spot", "power": 420, "coneAngle": 58, "coneFeather": 0.7, "sourceRadius": 30}}})
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Light3D", "id": 5, "parentId": None, "name": "Lantern glow (point)", "castsShadows": False,
    "color": LAMP_WARM, "transform": {"position": [LAMP_X, LAMP_TOP + 40, LAMP_Z]},
    "emitter": {"type": "point", "power": 25, "sourceRadius": 40}}})
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Light3D", "id": 6, "parentId": None, "name": "Teal rim (spot, back-left)", "castsShadows": False,
    "color": RIM_TEAL,
    "transform": {"position": [-1500, -900, 1700], "relationships": aim(84, 85, [0, -200, 0])},
    "emitter": {"type": "spot", "power": 160, "coneAngle": 30, "coneFeather": 0.8, "sourceRadius": 60}}})

data, items = [], []
nid = [1000]


def new_id():
    nid[0] += 1
    return nid[0]


def add_mesh(name, geom, pos, inputs, rot=None, mods=None, casts=True, parent=None, extra=None):
    d = new_id()
    data.append(mesh_data(d, name + " geo", geom))
    s, b, i = new_id(), new_id(), new_id()
    slot = material_slot(s, b, name + " finish", inputs)
    if extra:
        slot["binding"].update(extra)
    items.append(mesh_item(i, name, d, slot, pos, rotation=rot, modifiers=mods, casts=casts, parent=parent))
    return i


grunge_rough = lambda asset, factor, scale: scalar_tex_input(
    image_tex(asset, scale=scale, mapping=world_planar_mapping()), factor)

add_mesh("Sidewalk", {"type": "box", "size": [9000, 150, 3600]}, [0, 75, 1100],
         {"baseColor": const(hex_lin("#232323")), "roughness": grunge_rough("grunge352", 0.9, (1, 1))})
add_mesh("Kerb", {"type": "box", "size": [9000, 170, 170]}, [0, 75, -615],
         {"baseColor": const(hex_lin("#34332F")), "roughness": const(0.35)},
         mods=[{"type": "bevel", "id": new_id(), "width": 12, "segments": 3, "profile": 0.5, "limitAngle": 30}])
add_mesh("Asphalt", {"type": "box", "size": [14000, 40, 7000]}, [0, 170, -4200],
         {"baseColor": const(hex_lin("#0A0A0B")), "roughness": grunge_rough("grunge353", 0.7, (1, 1))})

iron = {"baseColor": const(hex_lin("#121314")), "roughness": const(0.4), "metallic": const(0.7)}
add_mesh("Lamp base", {"type": "cylinder", "radius": 55, "height": 160}, [LAMP_X, -80, LAMP_Z], iron)
add_mesh("Lamp post", {"type": "cylinder", "radius": 20, "height": 2200}, [LAMP_X, -1260, LAMP_Z], iron)
add_mesh("Lamp collar", {"type": "cylinder", "radius": 42, "height": 40}, [LAMP_X, LAMP_TOP + 150, LAMP_Z], iron)
add_mesh("Lantern glass", {"type": "box", "size": [130, 190, 130]}, [LAMP_X, LAMP_TOP + 40, LAMP_Z],
         {"baseColor": const(hex_lin("#FFD7A0")), "emissiveColor": const(hex_lin("#FFB66E")),
          "emissiveStrength": const(10.0)}, casts=False, extra={"unlit": True})
add_mesh("Lantern cap", {"type": "cone", "radius": 110, "height": 90}, [LAMP_X, LAMP_TOP - 100, LAMP_Z], iron)

BOX, LID = [330, 112, 200], [338, 30, 208]
paper = image_tex("paper363")
box_inputs = {"baseColor": color_tex_input(paper, ORANGE), "roughness": const(0.85)}
bevel = lambda w: [{"type": "bevel", "id": new_id(), "width": w, "segments": 2, "profile": 0.5, "limitAngle": 30}]
box_ids = []
box_ids.append(add_mesh("Box base", {"type": "box", "size": BOX}, [0, -56, 0], box_inputs, mods=bevel(2.0)))
box_ids.append(add_mesh("Box lid", {"type": "box", "size": LID}, [0, -107, 0], box_inputs, mods=bevel(2.5)))
SW_W = 140
sw_inputs = {"baseColor": const([0.85, 0.85, 0.85]), "roughness": const(0.55),
             "coverage": scalar_tex_input(image_tex("swoosh", wrap="clampToEdge"), 1.0, alpha=True),
             "alphaCutoff": const(0.5)}
box_ids.append(add_mesh("Swoosh front", {"type": "plane", "size": [SW_W, SW_W / 2.806]}, [12, -46, -100.8], sw_inputs,
                        casts=False, extra={"alphaMode": "mask", "doubleSided": True}))
# UV test box, to the left
add_mesh("UV test", {"type": "box", "size": BOX}, [-520, -56, 120],
         {"baseColor": color_tex_input(image_tex("uvtest"), [1, 1, 1]), "roughness": const(0.8)})

bld = {"baseColor": const(hex_lin("#0B0E13")), "roughness": const(0.85)}
win = {"baseColor": const(hex_lin("#FFC489")), "emissiveColor": const(hex_lin("#FFB878")), "emissiveStrength": const(4.0)}
for k, (x, w, h, z) in enumerate([(-5200, 2400, 5200, 6200), (-2600, 2200, 3800, 7000), (-300, 2600, 6200, 7600),
                                   (2500, 2000, 4400, 6800), (4800, 2600, 5600, 6300)]):
    add_mesh(f"Building {k}", {"type": "box", "size": [w, h, 1500]}, [x, -h / 2, z], bld)
for k, (x, y, z) in enumerate([(-5600, -2600, 5440), (-4700, -3600, 5440), (-2300, -2200, 6240), (300, -4200, 6840),
                                (-700, -2800, 6840), (2800, -3000, 6040), (5200, -2200, 5540), (4400, -4300, 5540)]):
    add_mesh(f"Window {k}", {"type": "box", "size": [260, 360, 20]}, [x, y, z], win, casts=False, extra={"unlit": True})

A.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": 1, "data": data, "items": items})
# Rim light only touches the boxes (no ground hotspot)
A.append({"type": "setFxScene3DRenderSettings", "compositionId": COMP, "layerId": 1, "settings": {
    "id": 97, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [], "outputs": [],
    "previewOutput": None,
    "lightLinks": [{"lightId": 6, "illuminatedObjects": {"type": "objects", "items": box_ids},
                    "shadowCasters": {"type": "all"}, "shadowReceivers": {"type": "all"}}]}})

dump(A, sys.argv[1] if len(sys.argv) > 1 else "lookdev2.json")
print(len(A), "actions,", len(items), "mesh items")
