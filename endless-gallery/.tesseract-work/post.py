"""Post-production layers for the Endless Gallery (2D, above the Scene3D layer).

Layer stack (top to bottom):
  20  Grade (Phase 4 drain)        adjustment: saturation -> ~30%, cooler, -0.3 stops, f66->f83
  21  Displacement jolts           adjustment: custom shader, Grunge 353 map, 3-frame jolts f20-22 / f50-52
  22  Haze                         rect layer, soft-light blend: procedural haze with constant low
                                   Turbulent Displace; thickens in Phase 4 with a slow crawling grunge
                                   displacement (the air itself decays)
  1   Endless Gallery              Scene3D
  2   Lamp light mask (projector)  consumed by the projector light
  3   Grunge map                   consumed by the displacement shaders

Usage: python3 post.py OUT.json WIDTH HEIGHT
"""
import json
import sys

FPS = 30
MS = 1000.0 / FPS
W, H = 1920, 1080


def ms(f):
    return round(f * MS, 3)


def bez(x1, y1, x2, y2):
    return {"type": "cubicBezier", "x1": x1, "y1": y1, "x2": x2, "y2": y2}


HOLD = {"type": "hold"}
EASE = bez(0.42, 0.0, 0.58, 1.0)
DRAIN = bez(0.30, 0.0, 0.25, 1.0)

VS = """
struct VertexInput {
  @location(0) position: vec2<f32>,
  @location(1) tex_coords: vec2<f32>,
  @location(2) color: vec4<f32>,
};
struct VertexOutput {
  @builtin(position) clip_position: vec4<f32>,
  @location(0) tex_coords: vec2<f32>,
};
@vertex
fn vs_main(input: VertexInput) -> VertexOutput {
  var out: VertexOutput;
  out.clip_position = vec4<f32>(input.position, 0.0, 1.0);
  out.tex_coords = input.tex_coords;
  return out;
}
"""

NOISE = """
fn hash2(p: vec2<f32>) -> f32 {
  return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453);
}
fn vnoise(p: vec2<f32>) -> f32 {
  let i = floor(p);
  let f = fract(p);
  let u = f * f * (3.0 - 2.0 * f);
  let a = hash2(i);
  let b = hash2(i + vec2<f32>(1.0, 0.0));
  let c = hash2(i + vec2<f32>(0.0, 1.0));
  let d = hash2(i + vec2<f32>(1.0, 1.0));
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
fn fbm(p: vec2<f32>) -> f32 {
  var v = 0.0;
  var a = 0.5;
  var q = p;
  for (var i = 0; i < 5; i = i + 1) {
    v = v + a * vnoise(q);
    q = q * 2.03 + vec2<f32>(1.7, 9.2);
    a = a * 0.5;
  }
  return v;
}
"""

FS_TAIL = """
@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let raw = author_frag(input.tex_coords);
  return vec4<f32>(clamp(raw.rgb, vec3<f32>(0.0), vec3<f32>(raw.a)), raw.a);
}
"""

# Displacement map (Grunge 353): offsets every pixel by the map's value. Two decorrelated taps give
# an x and a y offset. amount is in output pixels; offset scrolls the map so each jolt differs.
GRUNGE_WGSL = VS + """
struct Params {
  amount: f32,
  offx: f32,
  offy: f32,
  mapScale: f32,
};
@group(0) @binding(0) var t_content: texture_2d<f32>;
@group(0) @binding(1) var t_map: texture_2d<f32>;
@group(0) @binding(2) var s_sampler: sampler;
@group(0) @binding(3) var<uniform> params: Params;

fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_content));
  let muv = fract(uv * params.mapScale + vec2<f32>(params.offx, params.offy));
  let m1 = textureSample(t_map, s_sampler, muv).rgb;
  let m2 = textureSample(t_map, s_sampler, fract(muv + vec2<f32>(0.371, 0.613))).rgb;
  let d = vec2<f32>(dot(m1, vec3<f32>(0.3333)) - 0.5, dot(m2, vec3<f32>(0.3333)) - 0.5) * 2.0;
  let uv2 = clamp(uv + d * params.amount / dims, vec2<f32>(0.0), vec2<f32>(1.0));
  return textureSample(t_content, s_sampler, uv2);
}
""" + FS_TAIL

# Haze: procedural drifting fog, self-displaced by fractal turbulence (Turbulent Displace) and,
# in Phase 4, by the grunge map crawling slowly (displacement map on the haze).
# Output is a soft-light layer: 0.5 grey = neutral, so the haze only shows where there is light.
HAZE_WGSL = VS + """
struct Params {
  animationTime: f32,
  turbAmount: f32,
  turbScale: f32,
  density: f32,
  crawlAmount: f32,
  crawlOffset: f32,
  _pad0: f32,
  _pad1: f32,
};
@group(0) @binding(0) var t_content: texture_2d<f32>;
@group(0) @binding(1) var t_map: texture_2d<f32>;
@group(0) @binding(2) var s_sampler: sampler;
@group(0) @binding(3) var<uniform> params: Params;
""" + NOISE + """
fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let t = params.animationTime;
  let aspect = vec2<f32>(1.7778, 1.0);
  var p = uv * aspect * params.turbScale;
  // Turbulent Displace: fractal offsets that evolve over time
  let tw = vec2<f32>(fbm(p * 0.7 + vec2<f32>(t * 0.35, -t * 0.2)), fbm(p * 0.7 + vec2<f32>(4.1 - t * 0.27, 2.3 + t * 0.31)));
  p = p + (tw - 0.5) * params.turbAmount;
  // Displacement map crawl (Phase 4)
  let g = textureSample(t_map, s_sampler, fract(uv * 0.8 + vec2<f32>(params.crawlOffset, params.crawlOffset * 0.37))).r;
  p = p + vec2<f32>(g - 0.5, 0.5 - g) * params.crawlAmount;
  let fog = fbm(p + vec2<f32>(t * 0.08, t * 0.03));
  // Haze sits in the air band of the frame (lamps to floor), thinner high in the void
  let band = smoothstep(0.05, 0.55, uv.y);
  let v = 0.5 + (fog - 0.5) * params.density * band;
  return vec4<f32>(v, v, v, 1.0);
}
""" + FS_TAIL


GLOW_WGSL = VS + """
struct Params {
  strength: f32,
  cx: f32,
  cy: f32,
  radius: f32,
};
@group(0) @binding(0) var t_content: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let d = length((uv - vec2<f32>(params.cx, params.cy)) * vec2<f32>(1.7778, 1.0)) / params.radius;
  let g = params.strength * exp(-d * d * 1.6);
  let c = vec3<f32>(1.0, 0.66, 0.38) * g;
  return vec4<f32>(c, 1.0);
}
""" + FS_TAIL


def anim(target, keys):
    return {"type": "setFxAnimator", "compositionId": "main", "target": target,
            "animator": {"type": "keyframes", "enabled": True,
                         "keyframes": [{"id": f"k{target.get('effectId', 0)}-{target.get('paramName', '')}-{i}",
                                        "layerTime": ms(f), "value": {"type": "float", "value": v}, "easing": e}
                                       for i, (f, v, e) in enumerate(keys)]},
            "dependencies": [], "layerRefBindings": []}


def eff_target(layer, effect, param):
    return {"type": "effectParameter", "layerId": layer, "effectId": effect, "paramName": param}


def build(w, h):
    full = {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100}
    rng = {"start": 0, "duration": 2800}
    A = [
        {"type": "createFxImageLayer", "compositionId": "main", "layerId": 3, "name": "Grunge map (displacement source)",
         "activeRange": rng, "transform": full,
         "source": {"assetId": "grunge", "fit": "stretch", "sourceRect": {"x": 0, "y": 0, "width": w, "height": h}}},
        {"type": "createFxRectLayer", "compositionId": "main", "layerId": 22, "name": "Haze (soft light)",
         "activeRange": rng, "transform": full, "insertIndex": {"type": "prepend"},
         "rect": {"size": [w, h], "fillColor": [0.5, 0.5, 0.5, 1]}},
        {"type": "addFxLayerEffect", "compositionId": "main", "layerId": 22, "effectId": 2201,
         "effect": {"type": "customShader", "name": "hazeTurbulence",
                    "description": "Procedural haze for a soft-light layer (0.5 = neutral). Fractal Turbulent Displace "
                                   "keeps it alive; in Phase 4 the grunge map crawls through it so the air decays.",
                    "wgsl": HAZE_WGSL,
                    "params": [
                        {"name": "animationTime", "description": "Engine clock, seconds.", "min": 0, "max": 3600, "default": 0},
                        {"name": "turbAmount", "description": "Turbulent Displace strength, in noise cells.", "min": 0, "max": 3, "default": 0.6},
                        {"name": "turbScale", "description": "Haze feature size: cells across the frame height.", "min": 0.5, "max": 20, "default": 3.0},
                        {"name": "density", "description": "Haze contrast in the soft-light layer.", "min": 0, "max": 1, "default": 0.22},
                        {"name": "crawlAmount", "description": "Grunge displacement of the haze, in noise cells.", "min": 0, "max": 3, "default": 0.0},
                        {"name": "crawlOffset", "description": "Scroll of the grunge map (crawl).", "min": 0, "max": 1, "default": 0.0},
                        {"name": "_pad0", "description": "Uniform padding.", "min": 0, "max": 1, "default": 0},
                        {"name": "_pad1", "description": "Uniform padding.", "min": 0, "max": 1, "default": 0}],
                    "textureInputs": [{"name": "map", "description": "Grunge 353: grayscale crawl map for the haze.", "sourceLayerId": 3}]}},
        {"type": "createFxRectLayer", "compositionId": "main", "layerId": 23, "name": "Atmosphere glow (screen)",
         "activeRange": rng, "transform": full, "insertIndex": {"type": "prepend"},
         "rect": {"size": [w, h], "fillColor": [0, 0, 0, 1]}},
        {"type": "addFxLayerEffect", "compositionId": "main", "layerId": 23, "effectId": 2301,
         "effect": {"type": "customShader", "name": "atmosphereGlow",
                    "description": "Soft warm radial glow (screen blend): the warm haze the hall dissolves into.",
                    "wgsl": GLOW_WGSL,
                    "params": [
                        {"name": "strength", "description": "Glow brightness.", "min": 0, "max": 1, "default": 0.24},
                        {"name": "cx", "description": "Centre X (0-1).", "min": 0, "max": 1, "default": 0.5},
                        {"name": "cy", "description": "Centre Y (0-1).", "min": 0, "max": 1, "default": 0.46},
                        {"name": "radius", "description": "Glow size relative to frame height.", "min": 0.05, "max": 2, "default": 0.55}]}},
        {"type": "createFxAdjustmentLayer", "compositionId": "main", "layerId": 21, "name": "Displacement jolts (Grunge 353)",
         "activeRange": rng, "transform": full, "insertIndex": {"type": "prepend"}},
        {"type": "addFxLayerEffect", "compositionId": "main", "layerId": 21, "effectId": 2101,
         "effect": {"type": "customShader", "name": "grungeDisplaceJolt",
                    "description": "Displacement map: shifts every pixel by Grunge 353 (two decorrelated taps for x/y). "
                                   "Keyed to 3-frame jolts at the fastest frames of each snap pull-back.",
                    "wgsl": GRUNGE_WGSL,
                    "params": [
                        {"name": "amount", "description": "Maximum displacement, output pixels.", "min": 0, "max": 80, "default": 0},
                        {"name": "offx", "description": "Map scroll X (each jolt samples a new patch).", "min": 0, "max": 1, "default": 0},
                        {"name": "offy", "description": "Map scroll Y.", "min": 0, "max": 1, "default": 0},
                        {"name": "mapScale", "description": "Map repeats across the frame.", "min": 0.1, "max": 4, "default": 0.9}],
                    "textureInputs": [{"name": "map", "description": "Grunge 353: grayscale displacement map.", "sourceLayerId": 3}]}},
        {"type": "createFxAdjustmentLayer", "compositionId": "main", "layerId": 20, "name": "Grade (Phase 4 drain)",
         "activeRange": rng, "transform": full, "insertIndex": {"type": "prepend"}},
        {"type": "addFxLayerEffect", "compositionId": "main", "layerId": 20, "effectId": 2001,
         "effect": {"type": "primaryGrade", "semanticVersion": 1, "exposure": 0.0, "contrast": 0.0, "saturation": 0.0, "temperature": 0.0,
                    "tint": 0.0, "vibrance": 0.0, "highlights": 0.0, "shadows": 0.0, "whites": 0.0, "blacks": 0.0}},
        {"type": "addFxLayerEffect", "compositionId": "main", "layerId": 20, "effectId": 2002, "index": 0,
         "effect": {"type": "glow", "glowThreshold": 30, "glowRadius": 60, "glowIntensity": 1.1}},
        {"type": "addFxLayerEffect", "compositionId": "main", "layerId": 20, "effectId": 2003,
         "effect": {"type": "vignette", "amount": 0.55, "radius": 0.75, "feather": 0.6}},
    ]
    # Jolts: 3 frames each at the fastest point of each snap; each frame a different map patch
    jolt = [(0, 0.0, HOLD), (20, 9.0, HOLD), (21, 15.0, HOLD), (22, 6.0, HOLD), (23, 0.0, HOLD),
            (50, 11.0, HOLD), (51, 18.0, HOLD), (52, 7.0, HOLD), (53, 0.0, HOLD)]
    A.append(anim(eff_target(21, 2101, "amount"), jolt))
    offs = [(0, 0.0), (20, 0.13), (21, 0.57), (22, 0.81), (50, 0.29), (51, 0.71), (52, 0.44)]
    A.append(anim(eff_target(21, 2101, "offx"), [(f, v, HOLD) for f, v in offs]))
    A.append(anim(eff_target(21, 2101, "offy"), [(f, (v * 1.7) % 1, HOLD) for f, v in offs]))
    # Haze: alive throughout, thickens and starts crawling in Phase 4
    A.append(anim(eff_target(22, 2201, "density"), [(0, 0.20, HOLD), (66, 0.20, HOLD), (83, 0.34, DRAIN)]))
    A.append(anim(eff_target(22, 2201, "crawlAmount"), [(0, 0.0, HOLD), (66, 0.0, HOLD), (83, 0.9, DRAIN)]))
    A.append(anim(eff_target(22, 2201, "crawlOffset"), [(0, 0.0, HOLD), (66, 0.0, HOLD), (83, 0.12, EASE)]))
    A.append(anim(eff_target(22, 2201, "turbAmount"), [(0, 0.55, HOLD), (66, 0.55, HOLD), (83, 0.85, DRAIN)]))
    # Phase 4 grade drain: saturation to ~30%, cooler, about -0.3 stops
    A.append(anim(eff_target(20, 2001, "saturation"), [(0, 0.0, HOLD), (66, 0.0, HOLD), (83, -0.7, DRAIN)]))
    A.append(anim(eff_target(20, 2001, "temperature"), [(0, 0.0, HOLD), (66, 0.0, HOLD), (83, -0.35, DRAIN)]))
    A.append(anim(eff_target(20, 2001, "exposure"), [(0, 0.0, HOLD), (66, 0.0, HOLD), (83, -0.3, DRAIN)]))
    return A


if __name__ == '__main__':
    out, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    json.dump(build(w, h), open(out, 'w'))
    print('post actions written')
