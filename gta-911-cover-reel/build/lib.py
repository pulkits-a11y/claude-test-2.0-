"""Core helpers for the GTA 9/11 cover reel generator.

Writes native Tesseract document JSON (layers, groups, effects) plus one action
batch of keyframes. Everything is timed in frames at 30 fps and converted to
milliseconds at the edges. Times inside a group are local to that group.
"""
import json, math, os

FPS = 30
W, H = 1920, 1080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHADERS = os.path.join(ROOT, "build", "shaders")


def ms(f):
    return int(round(f * 1000 / FPS))


# ---------------------------------------------------------------- colours
def hexc(h, a=1.0):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [a]


WARM = hexc("#EFE9DF")      # Instrument Serif and labels
WHITE = hexc("#FFFFFF")
INK = hexc("#1D1A17")       # paper card ink (Scene 8)
FLASH = hexc("#FFF8EE")
OFFWHITE = hexc("#EFE9DF")  # card borders

# ---------------------------------------------------------------- easing (the brief allows only these three)
E_OX = {"type": "cubicBezier", "x1": 0.16, "y1": 1.0, "x2": 0.3, "y2": 1.0}      # ease-out expo
E_IOX = {"type": "cubicBezier", "x1": 0.87, "y1": 0.0, "x2": 0.13, "y2": 1.0}    # ease-in-out expo
E_IOC = {"type": "cubicBezier", "x1": 0.85, "y1": 0.0, "x2": 0.15, "y2": 1.0}    # ease-in-out circ
HOLD = {"type": "hold"}


def T(x=0, y=0, s=100, sy=None, r=0, o=100, ax=0, ay=0):
    return {"anchorPoint": [ax, ay], "opacity": o, "orientation": [0, 0, 0], "position": [x, y],
            "rotation": r, "rotationX": 0, "rotationY": 0, "scale": [s, s if sy is None else sy],
            "skew": 0, "skewAxis": 0}


class Doc:
    def __init__(self):
        self.next_id = 1000
        self.next_fx = 1
        self.next_kf = 0
        self.actions = []
        self.tracks = {}
        self.root = []

    def nid(self):
        self.next_id += 1
        return self.next_id

    def fxid(self):
        self.next_fx += 1
        return self.next_fx

    # ------------------------------------------------------------ layers
    def group(self, name, f0, f1, layers, o=100, blend="normal", effects=None, tr=None, matte=None, shadow=None, desc=None):
        g = {"blendMode": blend, "id": self.nid(), "name": name, "type": "Group",
             "transform": tr or T(o=o),
             "playback": {"inputOffsetMs": 0, "inputRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)},
                          "mapping": {"input": {"start": ms(f0), "duration": ms(f1) - ms(f0)},
                                      "output": {"start": 0, "duration": ms(f1) - ms(f0)}, "type": "linear"},
                          "type": "windowed"},
             "layers": layers}
        if tr is not None and o != 100:
            g["transform"]["opacity"] = o
        if effects: g["effects"] = effects
        if matte: g["trackMatte"] = matte
        if shadow: g["dropShadow"] = shadow
        if desc: g["description"] = desc
        return g

    def video(self, name, asset, f0, f1, src_ms, intrinsic, tr=None, fit="cover", rect=(0, 0, W, H), effects=None,
              blend="normal", matte=None, o=100, rate=1.0):
        d = ms(f1) - ms(f0)
        sd = int(round(d * rate))
        v = {"blendMode": blend, "id": self.nid(), "name": name, "type": "Video",
             "playback": {"inputOffsetMs": 0, "inputRange": {"start": ms(f0), "duration": d},
                          "mapping": {"input": {"start": ms(f0), "duration": d}, "output": {"start": src_ms, "duration": sd},
                                      "type": "linear"}, "type": "windowed"},
             "source": {"assetId": asset, "fit": fit,
                        "sourceRect": {"x": rect[0], "y": rect[1], "width": rect[2], "height": rect[3]}},
             "sourceIntrinsicDuration": intrinsic, "sourceRange": {"start": src_ms, "duration": min(sd, intrinsic - src_ms)},
             "transform": tr or T(o=o)}
        if effects: v["effects"] = effects
        if matte: v["trackMatte"] = matte
        return v

    def image(self, name, asset, f0, f1, tr=None, fit="cover", rect=(0, 0, W, H), effects=None, blend="normal",
              matte=None, o=100, shadow=None):
        im = {"activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)}, "blendMode": blend, "id": self.nid(),
              "name": name, "type": "Image",
              "source": {"assetId": asset, "fit": fit,
                         "sourceRect": {"x": rect[0], "y": rect[1], "width": rect[2], "height": rect[3]}},
              "transform": tr or T(o=o)}
        if effects: im["effects"] = effects
        if matte: im["trackMatte"] = matte
        if shadow: im["dropShadow"] = shadow
        return im

    def rect(self, name, f0, f1, x, y, w, h, color, blend="normal", o=100, effects=None, roundness=0, tr=None,
             hidden=False):
        r = {"activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)}, "blendMode": blend, "id": self.nid(),
             "name": name, "type": "Rect", "transform": tr or T(o=o),
             "rect": {"position": [x, y], "size": [w, h], "fillEnabled": True, "fillColor": color,
                      "strokeEnabled": False, "strokeWidth": 0, "roundness": roundness}}
        if effects: r["effects"] = effects
        if hidden: r["isHidden"] = True
        return r

    def text(self, name, f0, f1, txt, font, size, color, x, y, axes=None, just="left", tracking=0, leading=None,
             shadow=True, effects=None, o=100, tr=None, blend="normal"):
        st = {"text": txt, "fontFamily": font, "fontStyle": "Regular", "fontSize": size, "fillColor": color,
              "justification": just, "tracking": tracking, "applyFill": True, "applyStroke": False}
        if axes: st["fontVariations"] = {"id": self.fxid(), "axes": axes}
        if leading: st["leading"] = leading
        t = {"activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)}, "blendMode": blend, "id": self.nid(),
             "name": name, "type": "Text", "sourceText": st, "transform": tr or T(x, y, o=o)}
        if shadow: t["dropShadow"] = {"enabled": True, "color": [0, 0, 0, 0.45], "offset": [0, 4], "blurRadius": 32,
                                      "spreadRadius": 0, "blendMode": "normal"}
        if effects: t["effects"] = effects
        return t

    def adjust(self, name, f0, f1, effects, o=100):
        return {"activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)}, "blendMode": "normal", "id": self.nid(),
                "name": name, "type": "Adjustment", "transform": T(o=o), "effects": effects}

    # ------------------------------------------------------------ effects
    def fx(self, effect):
        return {"enabled": True, "id": self.fxid(), "effect": effect}

    def shader(self, name, file, params, desc):
        """params: list of (name, default, min, max, description)."""
        n = len(params)
        pad = (-n) % 4
        plist = [{"name": p[0], "description": p[4], "min": p[2], "max": p[3], "default": p[1]} for p in params]
        plist += [{"name": f"_pad{i}", "description": "Uniform padding (unused).", "min": 0, "max": 1, "default": 0}
                  for i in range(pad)]
        return self.fx({"type": "customShader", "name": name, "description": desc,
                        "wgsl": open(os.path.join(SHADERS, file)).read(), "params": plist})

    def gauss(self, b):
        return self.fx({"type": "gaussianBlur", "blurriness": b, "repeatEdgePixels": True})

    def dirblur(self, length, direction):
        return self.fx({"type": "directionalBlur", "blurLength": length, "direction": direction})

    def pin(self, ul, ur, ll, lr):
        return self.fx({"type": "cornerPin", "upperLeftX": ul[0] / W, "upperLeftY": ul[1] / H,
                        "upperRightX": ur[0] / W, "upperRightY": ur[1] / H,
                        "lowerLeftX": ll[0] / W, "lowerLeftY": ll[1] / H,
                        "lowerRightX": lr[0] / W, "lowerRightY": lr[1] / H})

    # ------------------------------------------------------------ animation
    # Keys are merged per property (a later call wins at the same time), then emitted once by finalize().
    def kf(self, layer, prop, keys):
        """keys: list of (frame_local, value, easing). value float or [x,y]."""
        track = self.tracks.setdefault(("p", layer["id"], prop), {})
        for f, v, e in keys:
            track[ms(f)] = (v, e)

    def kf_fx(self, layer, effect, param, keys):
        track = self.tracks.setdefault(("fx", layer["id"], effect["id"], param), {})
        for f, v, e in keys:
            track[ms(f)] = (v, e)

    def finalize(self):
        out = []
        for key, track in self.tracks.items():
            kfs = []
            for t in sorted(track):
                v, e = track[t]; self.next_kf += 1
                val = {"type": "float", "value": float(v)} if not isinstance(v, (list, tuple)) else {"type": "vector2", "value": list(v)}
                kfs.append({"id": f"k{self.next_kf}", "layerTime": t, "value": val, "easing": e})
            if key[0] == "p":
                out.append({"type": "setFxPropertyKeyframes", "compositionId": "main",
                            "property": {"layerId": key[1], "propertyType": key[2]}, "keyframes": kfs})
            else:
                out.append({"type": "setFxLayerEffectParamAnimator", "compositionId": "main", "layerId": key[1], "effectId": key[2],
                            "paramName": key[3], "dependencies": [], "animator": {"type": "keyframes", "enabled": True, "keyframes": kfs}})
        return out + self.actions


SHADOW = {"enabled": True, "color": [0, 0, 0, 0.55], "offset": [0, 18], "blurRadius": 60, "spreadRadius": 0,
          "blendMode": "normal"}
GLOW_WHITE = {"enabled": True, "color": [1, 1, 1, 0.85], "offset": [0, 0], "blurRadius": 40, "spreadRadius": 6,
              "blendMode": "screen"}
