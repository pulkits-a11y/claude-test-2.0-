"""Look-dev v1: night street set with one shoebox, for comparing against the storefront still."""
import sys
from lib import *

ORANGE = hex_lin("#E8641E")        # Nike shoebox orange (sRGB #E8641E)
LAMP_WARM = hex_srgb("#FFB46B")      # ~2700K
RIM_TEAL = hex_srgb("#8FE3C8")

A = []
A.append({"type": "createFxScene3DLayer", "compositionId": COMP, "layerId": 1, "name": "Street",
          "pixelsPerMeter": 1000, "view": {"id": 9, "exposure": 0},
          "activeRange": {"start": 0, "duration": 3000},
          "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100},
          "world": {"id": 2},
          "renderSettings": {"id": 97, "filmGate": None, "overscan": None, "lightGroups": [], "lightCollections": [],
                             "lightLinks": [], "outputs": [], "previewOutput": None}})

# Camera: low, three-quarter front, 35mm
CAM_POS = [700, -150, -2100]
LOOK = [0, -260, 0]
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Camera3D", "id": 3, "parentId": None, "name": "Camera 35mm",
    "transform": {"position": CAM_POS, "relationships": aim(80, 81, LOOK)},
    "lens": {"type": "physical", "focalLengthMm": 35, "sensorMm": [36, 24], "fNumber": 2.0},
    "depthOfField": {"focusDistance": 2200, "apertureBlades": 7, "apertureRotation": 0}}})
A.append({"type": "setFxScene3DActiveCamera", "compositionId": COMP, "layerId": 1, "cameraItemId": 3})

# World: near-black navy, faint ambient, distance fog
A.append({"type": "setFxScene3DWorld", "compositionId": COMP, "layerId": 1, "world": {
    "id": 2, "background": {"type": "color", "color": hex_srgb("#05070B")},
    "light": {"source": {"type": "color", "color": hex_srgb("#1A2733")}, "intensity": 0.05, "integration": "sampled"},
    "fog": {"color": hex_srgb("#06090D"), "startDistance": 3.0, "endDistance": 14.0}}})

# Lights
LAMP_X, LAMP_Z, LAMP_TOP = 950, 380, -2380
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Light3D", "id": 4, "parentId": None, "name": "Street lamp key (spot)", "castsShadows": True,
    "color": LAMP_WARM,
    "transform": {"position": [LAMP_X - 60, LAMP_TOP + 120, LAMP_Z], "relationships": aim(82, 83, [-40, 0, -60])},
    "emitter": {"type": "spot", "power": 900, "coneAngle": 64, "coneFeather": 0.55, "sourceRadius": 25}}})
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Light3D", "id": 5, "parentId": None, "name": "Lantern glow (point)", "castsShadows": False,
    "color": LAMP_WARM, "transform": {"position": [LAMP_X, LAMP_TOP + 40, LAMP_Z]},
    "emitter": {"type": "point", "power": 60, "sourceRadius": 40}}})
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Light3D", "id": 6, "parentId": None, "name": "Teal rim (area, back-left)", "castsShadows": True,
    "color": RIM_TEAL,
    "transform": {"position": [-1700, -1400, 2000], "relationships": aim(84, 85, [0, -300, 0])},
    "emitter": {"type": "area", "power": 260, "shape": {"type": "rectangle", "areaSize": [900, 900]}}}})

data, items = [], []
nid = [1000]


def new_id():
    nid[0] += 1
    return nid[0]


def add_mesh(name, geom, pos, inputs, rot=None, mods=None, casts=True, parent=None):
    d = new_id()
    data.append(mesh_data(d, name + " geo", geom))
    s, b, i = new_id(), new_id(), new_id()
    items.append(mesh_item(i, name, d, material_slot(s, b, name + " finish", inputs), pos, rotation=rot,
                           modifiers=mods, casts=casts, parent=parent))
    return i


wet_rough = lambda lo, hi, seed, sz: scalar_tex_input(
    noise_tex(size=(sz, sz), seed=seed, octaves=5, persistence=0.55, mapping=world_planar_mapping()), hi)

# Sidewalk slab (top at y=0), kerb, asphalt road
add_mesh("Sidewalk", {"type": "box", "size": [9000, 150, 3600]}, [0, 75, 1100],
         {"baseColor": const(hex_lin("#2A2A2A")), "roughness": wet_rough(0.1, 0.55, 7, 1800)})
add_mesh("Kerb", {"type": "box", "size": [9000, 170, 170]}, [0, 75, -615],
         {"baseColor": const(hex_lin("#3A3936")), "roughness": const(0.3)},
         mods=[{"type": "bevel", "id": new_id(), "width": 12, "segments": 3, "profile": 0.5, "limitAngle": 30}])
add_mesh("Asphalt", {"type": "box", "size": [14000, 40, 7000]}, [0, 170, -4200],
         {"baseColor": const(hex_lin("#0C0C0D")), "roughness": wet_rough(0.04, 0.4, 11, 2600)})

# Street lamp (vintage post + lantern)
iron = {"baseColor": const(hex_lin("#141516")), "roughness": const(0.35), "metallic": const(0.8)}
add_mesh("Lamp base", {"type": "cylinder", "radius": 55, "height": 160}, [LAMP_X, -80, LAMP_Z], iron)
add_mesh("Lamp post", {"type": "cylinder", "radius": 20, "height": 2200}, [LAMP_X, -1260, LAMP_Z], iron)
add_mesh("Lamp collar", {"type": "cylinder", "radius": 42, "height": 40}, [LAMP_X, LAMP_TOP + 150, LAMP_Z], iron)
add_mesh("Lantern glass", {"type": "box", "size": [130, 190, 130]}, [LAMP_X, LAMP_TOP + 40, LAMP_Z],
         {"baseColor": const(hex_lin("#FFD7A0")), "emissiveColor": const(hex_lin("#FFB66E")),
          "emissiveStrength": const(14.0), "roughness": const(0.2)}, casts=False)
add_mesh("Lantern cap", {"type": "cone", "radius": 110, "height": 90}, [LAMP_X, LAMP_TOP - 100, LAMP_Z], iron)

# One shoebox (base + overhanging lid + swoosh decal plane)
BOX = [330, 112, 200]
LID = [338, 28, 208]
paper = image_tex("paper363", scale=(1.0, 1.0))
box_inputs = {"baseColor": color_tex_input(paper, ORANGE), "roughness": const(0.82)}
bevel = lambda w: [{"type": "bevel", "id": new_id(), "width": w, "segments": 2, "profile": 0.5, "limitAngle": 30}]
add_mesh("Box base", {"type": "box", "size": BOX}, [0, -56, 0], box_inputs, mods=bevel(2.0))
add_mesh("Box lid", {"type": "box", "size": LID}, [0, -106, 0], box_inputs, mods=bevel(2.5))
SW_W = 150
add_mesh("Swoosh", {"type": "plane", "size": [SW_W, SW_W / 2.806]}, [10, -44, -101.2],
         {"baseColor": const([0.9, 0.9, 0.9]), "roughness": const(0.6),
          "coverage": scalar_tex_input(image_tex("swoosh", wrap="clampToEdge"), 1.0, alpha=True)}, casts=False)

# Background buildings with a few warm windows
bld = {"baseColor": const(hex_lin("#0B0E13")), "roughness": const(0.8)}
win = {"baseColor": const(hex_lin("#FFC489")), "emissiveColor": const(hex_lin("#FFB878")),
       "emissiveStrength": const(6.0)}
for k, (x, w, h, z) in enumerate([(-5200, 2400, 5200, 6200), (-2600, 2200, 3800, 7000), (-300, 2600, 6200, 7600),
                                   (2500, 2000, 4400, 6800), (4800, 2600, 5600, 6300)]):
    add_mesh(f"Building {k}", {"type": "box", "size": [w, h, 1500]}, [x, -h / 2, z], bld)
for k, (x, y, z) in enumerate([(-5600, -2600, 5440), (-4700, -3600, 5440), (-2300, -2200, 6240), (300, -4200, 6840),
                                (-700, -2800, 6840), (2800, -3000, 6040), (5200, -2200, 5540), (4400, -4300, 5540)]):
    add_mesh(f"Window {k}", {"type": "box", "size": [260, 360, 20]}, [x, y, z], win, casts=False)

A.append({"type": "addFxScene3DFragment", "compositionId": COMP, "layerId": 1, "data": data, "items": items})

# Haze volume around the lamp cone
A.append({"type": "addFxScene3DLayer", "compositionId": COMP, "layerId": 1, "item": {
    "type": "Volume3D", "id": 30, "parentId": None, "name": "Haze", "isHidden": False,
    "transform": {"position": [0, -1800, 800]}, "size": [9000, 3800, 6000],
    "density": 0.05, "scatteringColor": [0.85, 0.85, 0.85, 1], "anisotropy": 0.45}})

dump(A, sys.argv[1] if len(sys.argv) > 1 else "lookdev.json")
print(len(A), "actions,", len(items), "mesh items")
