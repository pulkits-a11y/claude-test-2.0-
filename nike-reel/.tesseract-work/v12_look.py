# ================= 2. FILM-WIDE OVERLAYS (build18 stack, above every scene and all text; watermark stays on top) =================
#   top -> bottom: CRT scan lines, vignette, desaturate, lift, film grain, halftone, grunge
def jitter_script(n_frames, seed, axis):
    """Precomputed seeded offsets (build18 LCG), a new one every 2 frames; deterministic, no Math.random at render."""
    xs, ys = [], []
    s_ = seed
    for _ in range(0, n_frames + 2, 2):
        s_ = (s_ * 1664525 + 1013904223) % 4294967296; xs.append(-round(s_ / 4294967296 * 480))
        s_ = (s_ * 1664525 + 1013904223) % 4294967296; ys.append(-round(s_ / 4294967296 * 320))
    arr = xs if axis == "x" else ys
    return ("var A=[" + ",".join(map(str, arr)) + "];var k=Math.floor(input.time.seconds*15+1e-6);"
            "if(k<0)k=0;if(k>=A.length)k=A.length-1;return A[k];")


def grain_layer(name, parent, f0, n, seed, opacity):
    """grain.png as a 2400x1400 layer, overlay blend, jumped to a new seeded offset every 2 frames."""
    lid = D.nid()
    D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": lid, "name": f"{name} [blend:overlay]", "parentLayerId": parent,
           "activeRange": {"start": ms(f0), "duration": ms(f0 + n) - ms(f0)},
           "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": opacity},
           "source": {"assetId": "tex_grain", "fit": "none"}})
    for ax, prop in (("x", "positionX"), ("y", "positionY")):
        D.add({"type": "setFxPropertyAnimator", "compositionId": C, "property": {"layerId": lid, "propertyType": prop}, "dependencies": [],
               "animator": {"type": "jsScript", "layerTimeJsCode": jitter_script(n, seed, ax)}})
    return lid


def tex_layer(name, asset, f0, f1, opacity, parent=None):
    lid = D.nid()
    D.add({"type": "createFxImageLayer", "compositionId": C, "layerId": lid, "name": name, "parentLayerId": parent,
           "activeRange": {"start": ms(f0), "duration": ms(f1) - ms(f0)},
           "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": opacity},
           "source": {"assetId": asset, "fit": "none"}})
    return lid


FW = endcard_in            # the overlays run over the whole film; the attached end card stays as supplied
tex_layer("FX 7 CRT scan lines (2px / 5px) [blend:multiply]", "tex_scan", 0, FW, 42)
tex_layer("FX 6 vignette (ellipse 72%)", "tex_vig", 0, FW, 100)
D.rect("FX 5 desaturate #808080 [blend:saturation]", 0, 0, 1920, 1080, [128 / 255, 128 / 255, 128 / 255, 1], 0, FW)
D.A[-1]["transform"]["opacity"] = 20
D.rect("FX 4 lift #2a2119 [blend:screen]", 0, 0, 1920, 1080, [0x2a / 255, 0x21 / 255, 0x19 / 255, 1], 0, FW)
D.A[-1]["transform"]["opacity"] = 30
grain_layer("FX 3 film grain (2400x1400, jitter every 2 f)", None, 0, FW, 1337, 22)
tex_layer("FX 2 halftone [blend:overlay]", "tex_halftone", 0, FW, 20)
tex_layer("FX 1 grunge [blend:overlay]", "tex_grunge", 0, FW, 60)

# light glow stays as an adjustment under the overlays (grain, mesh and vignette now come from the stack above)
gid = D.nid()
D.add({"type": "createFxAdjustmentLayer", "compositionId": C, "layerId": gid, "name": "LOOK: highlight glow",
       "activeRange": {"start": 0, "duration": ms(endcard_in)}, "transform": xf()})
D.effect(gid, {"type": "glow", "glowThreshold": 75, "glowRadius": 70, "glowIntensity": 0.35})


