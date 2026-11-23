"""Scene3D helpers shared by the Three Hits builders (same conventions as the Shoebox Tower build)."""
from common import *
from lib import COMP, material_slot

SW_W = 140                      # swoosh plane width on the box's long side (mm), as in the Shoebox Tower
BASE, LID = [330, 112, 200], [338, 30, 208]


class Ids:
    def __init__(self, start):
        self.n = start

    def __call__(self):
        self.n += 1
        return self.n


def scene_layer(layer_id, name, world, start_ms=0, dur_ms=None):
    return {"type": "createFxScene3DLayer", "compositionId": COMP, "layerId": layer_id, "name": name, "insertIndex": 0,
            "pixelsPerMeter": 1000, "view": {"id": layer_id * 1000 + 9, "exposure": 0},
            "activeRange": {"start": start_ms, "duration": dur_ms if dur_ms is not None else ms(DUR) - start_ms},
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
