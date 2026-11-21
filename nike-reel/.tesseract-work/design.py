"""Design layer builders for the Nike reel (horizontal 1920x1080, Stepped look).

All groups span the whole program from frame 0, so child windows and keyframes use
program frames; keyframe `layerTime` is relative to each layer's own start.
Entrances are snapped to the 10 fps grid (every 3rd frame) so Posterize Time never delays them.
"""
import random
from textkit import advance, layout_line

FPS = 30
BG = [18 / 255, 18 / 255, 18 / 255, 1]
TEXT = [237 / 255, 237 / 255, 237 / 255, 1]
GREEN = [201 / 255, 249 / 255, 184 / 255, 1]
STEP = 3                                   # Stepped look: motion updates every 3rd frame (10 fps)
WGSL = open(__file__.replace("design.py", "shaders/vox_type.wgsl")).read()
ARCHIVO_STYLE = {500: "Medium", 520: "Medium", 600: "SemiBold", 640: "SemiBold", 700: "Bold", 800: "ExtraBold", 880: "Black", 900: "Black"}


def ms(f):
    return round(f * 1000 / FPS)


def grid(f):
    """Snap an entrance down onto the 10 fps grid (appears up to 2 frames early, never late)."""
    return (f // STEP) * STEP


class Doc:
    def __init__(self, comp="main", first_id=1):
        self.C, self.A, self._id = comp, [], first_id

    def nid(self):
        self._id += 1
        return self._id

    def add(self, a):
        self.A.append(a)
        return a

    # ---------- layers ----------
    def group(self, name, f0, f1, parent=None):
        lid = self.nid()
        self.add({"type": "createFxGroupLayer", "compositionId": self.C, "layerId": lid, "name": name,
                  "parentLayerId": parent, "activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)},
                  "transform": {"anchorPoint": [960, 540], "position": [960, 540], "scale": [100, 100], "rotation": 0, "opacity": 100}})
        return lid

    def rect(self, name, x, y, w, h, color, f0, f1, parent=None, anchor=(0, 0)):
        lid = self.nid()
        self.add({"type": "createFxRectLayer", "compositionId": self.C, "layerId": lid, "name": name, "parentLayerId": parent,
                  "activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)},
                  "transform": {"anchorPoint": list(anchor), "position": [x + anchor[0], y + anchor[1]], "scale": [100, 100], "rotation": 0, "opacity": 100},
                  "rect": {"size": [w, h], "fillColor": color}})
        return lid

    def text(self, name, s, x, y, font, size, color, f0, f1, parent=None, wght=None, wdth=100, tracking=0, anchor=(0, 0)):
        if font == "archivo":
            fam, style = "Archivo SemiBold", ARCHIVO_STYLE.get(wght, "SemiBold")
        elif font == "serif":
            fam, style = "Instrument Serif", "Regular"
        else:
            fam, style = "Instrument Serif", "Italic"
        st = {"text": s, "fontFamily": fam, "fontStyle": style, "fontSize": size, "fillColor": color, "strokeWidth": 0,
              "justification": "left", "tracking": tracking}
        if font == "archivo":
            st["fontVariations"] = {"id": self.nid(), "axes": {"wght": wght, "wdth": wdth}}
        lid = self.nid()
        self.add({"type": "createFxTextLayer", "compositionId": self.C, "layerId": lid, "name": name, "parentLayerId": parent,
                  "activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)},
                  "transform": {"anchorPoint": list(anchor), "position": [x + anchor[0], y + anchor[1]], "scale": [100, 100], "rotation": 0, "opacity": 100},
                  "sourceText": st})
        return lid

    # ---------- animation ----------
    def keys(self, lid, prop, keys):
        self.add({"type": "setFxPropertyKeyframes", "compositionId": self.C, "property": {"layerId": lid, "propertyType": prop},
                  "keyframes": [{"id": f"{prop}-{lid}-{i}", "layerTime": ms(fr), "value": {"type": "float", "value": v},
                                 "easing": {"type": e}} for i, (fr, v, e) in enumerate(keys)]})

    def effect(self, lid, eff):
        eid = self.nid()
        self.add({"type": "addFxLayerEffect", "compositionId": self.C, "layerId": lid, "effectId": eid, "effect": eff})
        return eid

    def effect_keys(self, lid, eid, param, keys):
        self.add({"type": "setFxLayerEffectParamAnimator", "compositionId": self.C, "layerId": lid, "effectId": eid, "paramName": param,
                  "dependencies": [], "animator": {"type": "keyframes", "enabled": True, "keyframes": [
                      {"id": f"{param}-{eid}-{i}", "layerTime": ms(fr), "value": {"type": "float", "value": v}, "easing": {"type": e}}
                      for i, (fr, v, e) in enumerate(keys)]}})

    def effect_script(self, lid, eid, param, code):
        self.add({"type": "setFxLayerEffectParamAnimator", "compositionId": self.C, "layerId": lid, "effectId": eid, "paramName": param,
                  "dependencies": [], "animator": {"type": "jsScript", "layerTimeJsCode": code}})

    def vox(self, lid, size):
        """Typography guide 'BTW' look: turbulent displace + displacement wobble + noise inside the letters."""
        return self.effect(lid, {"type": "customShader", "name": "voxType",
                                 "description": "Turbulent displace + displacement-map wobble + noise inside the letters, stepped every 0.1 s.",
                                 "wgsl": WGSL, "params": [
                                     {"name": "animationTime", "description": "Engine clock (s).", "min": 0, "max": 3600, "default": 0},
                                     {"name": "displacePx", "description": "Max edge displacement in px.", "min": 0, "max": 20,
                                      "default": round(max(0.5, min(1.6, size / 150)), 2)},
                                     {"name": "turbulenceScalePx", "description": "Turbulence cell size in px.", "min": 1, "max": 200,
                                      "default": round(max(3.0, size / 24), 1)},
                                     {"name": "grainAmount", "description": "Noise inside the letters (0..1).", "min": 0, "max": 1, "default": 0.12},
                                     {"name": "stepSeconds", "description": "Hold time per noise step (s).", "min": 0.01, "max": 1, "default": 0.1}]})

    def posterize(self, lid):
        return self.effect(lid, {"type": "posterizeTime", "frameRate": 10})

    # ---------- named entrances (typography guide) ----------
    def ghost_to_solid(self, lid):
        self.keys(lid, "opacity", [(0, 40, "hold"), (STEP, 100, "hold")])

    def blur_to_sharp(self, lid, blur=12):
        eid = self.effect(lid, {"type": "gaussianBlur", "blurriness": 0})
        self.effect_keys(lid, eid, "blurriness", [(0, blur, "hold"), (STEP, 0, "hold")])
        self.keys(lid, "opacity", [(0, 45, "hold"), (STEP, 100, "hold")])

    def flicker_in(self, lid):
        self.keys(lid, "opacity", [(0, 100, "hold"), (STEP, 25, "hold"), (2 * STEP, 100, "hold")])

    def pop(self, lid):
        """Transition-guide MG build: scale 80->100 with blur clearing over 6 frames, in 3-frame steps."""
        self.keys(lid, "scaleX", [(0, 80, "hold"), (STEP, 90, "hold"), (2 * STEP, 100, "hold")])
        self.keys(lid, "scaleY", [(0, 80, "hold"), (STEP, 90, "hold"), (2 * STEP, 100, "hold")])
        eid = self.effect(lid, {"type": "gaussianBlur", "blurriness": 0})
        self.effect_keys(lid, eid, "blurriness", [(0, 18, "hold"), (STEP, 9, "hold"), (2 * STEP, 0, "hold")])

    def motion_blur_slide(self, lid, x, dx=160):
        self.keys(lid, "positionX", [(0, x + dx, "hold"), (STEP, x, "hold")])
        eid = self.effect(lid, {"type": "directionalBlur", "direction": 90, "blurLength": 0})
        self.effect_keys(lid, eid, "blurLength", [(0, 70, "hold"), (STEP, 0, "hold")])

    def stepped_drift(self, lid, a, b, to=103.0):
        """Slow drift on held text, updating every 3rd frame (Stepped look). a/b are program frames (group starts at 0)."""
        n = max(1, (b - a) // STEP)
        ks = [(a + k * STEP, round(100 + (to - 100) * k / n, 3), "hold") for k in range(n + 1)]
        self.keys(lid, "scaleX", ks)
        self.keys(lid, "scaleY", ks)
