"""Helpers that emit Tesseract Scene3D action JSON for the Shoebox Tower MG.

Coordinates follow Scene3D: X right, Y down, Z into the screen, in pixels.
The scene uses pixelsPerMeter = 1000, so 1 px = 1 mm.
"""
import json
import math

COMP = "main"


def srgb_to_linear(c):
    c = c / 255.0 if c > 1 else c
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    h = h.lstrip("#")
    return [round(srgb_to_linear(int(h[i:i + 2], 16)), 6) for i in (0, 2, 4)]


def hex_srgb(h, a=1.0):
    h = h.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 6) for i in (0, 2, 4)] + [a]


# ---------------------------------------------------------------- textures
def image_tex(asset, scale=(1, 1), offset=None, rotation=None, wrap="repeat", mapping=None):
    t = {"source": {"type": "image", "assetId": asset}, "magFilter": "linear", "minFilter": "linear",
         "mipFilter": "linear", "mipmaps": True, "scale": list(scale), "wrapU": wrap, "wrapV": wrap}
    if offset is not None:
        t["offset"] = list(offset)
    if rotation is not None:
        t["rotation"] = rotation
    if mapping is not None:
        t["mapping"] = mapping
    return t


def noise_tex(size=(4000, 4000), seed=1, octaves=4, persistence=0.5, lacunarity=2.0, evolution=0.0,
              evolution_per_s=0.0, scale=(1, 1), mapping=None):
    t = {"source": {"type": "procedural", "texture": {
        "size": list(size), "evolutionPerSecond": evolution_per_s,
        "generator": {"type": "noise", "seed": seed, "octaves": octaves, "persistence": persistence,
                      "lacunarity": lacunarity, "evolution": evolution}}},
         "magFilter": "linear", "minFilter": "linear", "mipFilter": "linear", "mipmaps": True,
         "scale": list(scale), "wrapU": "repeat", "wrapV": "repeat"}
    if mapping is not None:
        t["mapping"] = mapping
    return t


def world_planar_mapping(scale_pct=(100, 100, 100)):
    return {"coordinates": "world", "projection": {"type": "box"},
            "transform": {"position": [0, 0, 0], "scale": list(scale_pct)}}


def color_tex_input(tex, factor):
    return {"type": "texture", "factor": list(factor),
            "sample": {"texture": tex, "selection": {"type": "rgb"}, "interpretation": {"type": "color"}}}


def scalar_tex_input(tex, factor=1.0, channel=0, alpha=False):
    sel = {"type": "alpha"} if alpha else {"type": "channel", "channel": channel}
    return {"type": "texture", "factor": factor,
            "sample": {"texture": tex, "selection": sel, "interpretation": {"type": "data"}}}


def const(v):
    return {"type": "constant", "value": v}


# ---------------------------------------------------------------- objects
def rot_euler(x=0.0, y=0.0, z=0.0):
    return {"type": "euler", "order": "XYZ", "orientation": [0, 0, 0], "rotationX": x, "rotationY": y,
            "rotationZ": z}


def material_slot(slot_id, binding_id, name, inputs):
    return {"id": slot_id, "name": name, "binding": {"id": binding_id, "inputs": inputs}}


def mesh_data(data_id, name, geometry):
    return {"type": "mesh", "id": data_id, "name": name, "geometry": geometry,
            "regions": [{"key": "primary", "name": "Primary"}, {"key": "side", "name": "Side"}]}


def mesh_item(item_id, name, data_id, slot, position, rotation=None, scale=None, parent=None,
              modifiers=None, casts=True, receives=True):
    tr = {"position": list(position)}
    if rotation is not None:
        tr["rotation"] = rotation
    if scale is not None:
        tr["scale"] = list(scale)
    it = {"type": "Mesh3D", "id": item_id, "parentId": parent, "name": name, "dataId": data_id,
          "packing": "whole", "transform": tr, "materialSlots": [slot],
          "regionSlots": [{"region": "primary", "slotId": slot["id"]}, {"region": "side", "slotId": slot["id"]}],
          "castsShadows": casts}
    if modifiers:
        it["modifiers"] = modifiers
    return it


def group_item(item_id, name, position=(0, 0, 0), parent=None, rotation=None):
    tr = {"position": list(position)}
    if rotation is not None:
        tr["rotation"] = rotation
    return {"type": "Group3D", "id": item_id, "parentId": parent, "name": name, "transform": tr}


def aim(cid, tid, target_pos):
    return {"constraints": [{"type": "aim", "id": cid, "target": {"id": tid, "target": {"type": "world"},
                                                                  "offset": list(target_pos), "offsetSpace": "local"},
                             "up": [0, 1, 0], "upSpace": "world", "forwardAxis": "positiveZ", "influence": 1}]}


def dump(actions, path):
    with open(path, "w") as f:
        json.dump(actions, f, indent=1)
    return path
