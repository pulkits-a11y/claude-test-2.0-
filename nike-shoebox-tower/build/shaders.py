"""WGSL custom shaders for the Shoebox Tower MG (Tesseract customShader effects).

turbulent_displace  - After Effects 'Turbulent Displace' equivalent: fractal value-noise offsets the
                      layer's pixels by `amount` px; `size` sets the feature size, `evolution` the speed.
grunge_displace     - 'Displacement Map' + dissolve driven by the Grunge 353 texture (bound as a
                      texture input). `displace` offsets pixels by the map; `progress` 0->1 dissolves the
                      layer along the grunge (edges displace hardest); `rgbSplit` adds a glitch fringe.
"""

_VS = """
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
fn hash31(p: vec3<f32>) -> f32 {
  var q = fract(p * 0.1031);
  q = q + dot(q, q.zyx + 31.32);
  return fract((q.x + q.y) * q.z);
}
fn vnoise(p: vec3<f32>) -> f32 {
  let i = floor(p);
  let f = fract(p);
  let u = f * f * (3.0 - 2.0 * f);
  let a = mix(mix(hash31(i + vec3<f32>(0.0, 0.0, 0.0)), hash31(i + vec3<f32>(1.0, 0.0, 0.0)), u.x),
              mix(hash31(i + vec3<f32>(0.0, 1.0, 0.0)), hash31(i + vec3<f32>(1.0, 1.0, 0.0)), u.x), u.y);
  let b = mix(mix(hash31(i + vec3<f32>(0.0, 0.0, 1.0)), hash31(i + vec3<f32>(1.0, 0.0, 1.0)), u.x),
              mix(hash31(i + vec3<f32>(0.0, 1.0, 1.0)), hash31(i + vec3<f32>(1.0, 1.0, 1.0)), u.x), u.y);
  return mix(a, b, u.z);
}
fn fbm(p: vec3<f32>) -> f32 {
  var s = 0.0;
  var a = 0.5;
  var q = p;
  for (var k = 0; k < 4; k = k + 1) {
    s = s + a * vnoise(q);
    q = q * vec3<f32>(2.03, 2.03, 1.6) + vec3<f32>(17.1, 9.2, 3.7);
    a = a * 0.5;
  }
  return s;
}
"""

TURBULENT_WGSL = _VS + """
struct Params {
  animationTime: f32,
  amount: f32,
  size: f32,
  evolution: f32,
  seed: f32,
  clock: f32,
  useClock: f32,
  _pad0: f32,
};
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_texture));
  let px = input.tex_coords * dims;
  let tt = select(params.animationTime, params.clock, params.useClock > 0.5);
  let z = tt * params.evolution + params.seed * 13.7;
  let p = vec3<f32>(px / max(params.size, 1.0), z);
  let d = vec2<f32>(fbm(p) - 0.5, fbm(p + vec3<f32>(41.3, 7.9, 0.0)) - 0.5) * 2.0 * params.amount;
  let c = textureSample(t_texture, s_sampler, input.tex_coords + d / dims);
  return vec4<f32>(clamp(c.rgb, vec3<f32>(0.0), vec3<f32>(c.a)), c.a);
}
"""

TURBULENT_PARAMS = [
    {"name": "animationTime", "description": "Engine-driven layer clock in seconds.", "min": 0, "max": 3600, "default": 0},
    {"name": "amount", "description": "Displacement strength in pixels (0 = sharp, untouched).", "min": 0, "max": 120, "default": 0},
    {"name": "size", "description": "Turbulence feature size in pixels; smaller = finer, more jittery wobble.", "min": 2, "max": 600, "default": 40},
    {"name": "evolution", "description": "How fast the turbulence evolves, in noise units per second.", "min": 0, "max": 40, "default": 6},
    {"name": "seed", "description": "Random seed that offsets the noise field.", "min": 0, "max": 100, "default": 1},
    {"name": "clock", "description": "Optional external clock in seconds (used when useClock is on), e.g. the slowed 'story time'.", "min": 0, "max": 100, "default": 0},
    {"name": "useClock.toggle", "description": "Drive the evolution from `clock` instead of the layer clock.", "min": 0, "max": 1, "default": 0},
    {"name": "_pad0", "description": "Unused padding slot.", "min": 0, "max": 1, "default": 0},
]

GRUNGE_WGSL = _VS + """
struct Params {
  animationTime: f32,
  progress: f32,
  softness: f32,
  displace: f32,
  mapScale: f32,
  mapShiftX: f32,
  mapShiftY: f32,
  rgbSplit: f32,
};
@group(0) @binding(0) var t_content: texture_2d<f32>;
@group(0) @binding(1) var t_map: texture_2d<f32>;
@group(0) @binding(2) var s_sampler: sampler;
@group(0) @binding(3) var<uniform> params: Params;

fn map_at(uv: vec2<f32>) -> f32 {
  let m = textureSample(t_map, s_sampler, fract((uv - 0.5) / max(params.mapScale, 0.05) + 0.5 + vec2<f32>(params.mapShiftX, params.mapShiftY)));
  return dot(m.rgb, vec3<f32>(0.2126, 0.7152, 0.0722));
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_content));
  let uv = input.tex_coords;
  let v = map_at(uv);
  let s = max(params.softness, 0.001);
  let thr = params.progress * (1.0 + 2.0 * s) - s;
  let vis = smoothstep(thr - s, thr + s, v);
  let edge = 1.0 - abs(vis * 2.0 - 1.0);
  let gx = map_at(uv + vec2<f32>(3.0 / dims.x, 0.0)) - map_at(uv - vec2<f32>(3.0 / dims.x, 0.0));
  let gy = map_at(uv + vec2<f32>(0.0, 3.0 / dims.y)) - map_at(uv - vec2<f32>(0.0, 3.0 / dims.y));
  let dir = vec2<f32>(v - 0.5, (v - 0.5) * 0.6) + vec2<f32>(gx, gy) * 2.0;
  let off = dir * params.displace * (1.0 + 3.0 * edge) / dims;
  let sp = vec2<f32>(params.rgbSplit, 0.0) / dims;
  let cr = textureSample(t_content, s_sampler, uv + off + sp);
  let cg = textureSample(t_content, s_sampler, uv + off);
  let cb = textureSample(t_content, s_sampler, uv + off - sp);
  let a = max(cg.a, max(cr.a, cb.a)) * vis;
  let rgb = vec3<f32>(cr.r, cg.g, cb.b) * vis;
  return vec4<f32>(clamp(rgb, vec3<f32>(0.0), vec3<f32>(a)), a);
}
"""

GRUNGE_PARAMS = [
    {"name": "animationTime", "description": "Engine-driven layer clock in seconds.", "min": 0, "max": 3600, "default": 0},
    {"name": "progress", "description": "Dissolve along the grunge map: 0 = fully visible, 1 = fully gone.", "min": 0, "max": 1, "default": 0},
    {"name": "softness", "description": "Width of the dissolving edge (map units).", "min": 0.001, "max": 0.5, "default": 0.08},
    {"name": "displace", "description": "Displacement-map strength in pixels (stronger on the dissolving edge).", "min": 0, "max": 200, "default": 0},
    {"name": "mapScale", "description": "Scale of the grunge map over the frame (1 = fills the frame).", "min": 0.1, "max": 4, "default": 1},
    {"name": "mapShift.x", "description": "Horizontal offset of the map (fraction of the frame).", "min": -1, "max": 1, "default": 0},
    {"name": "mapShift.y", "description": "Vertical offset of the map (fraction of the frame).", "min": -1, "max": 1, "default": 0},
    {"name": "rgbSplit", "description": "Glitch colour fringe in pixels.", "min": 0, "max": 40, "default": 0},
]


def turbulent(name, amount=0.0, size=40, evolution=6, seed=1):
    p = [dict(x) for x in TURBULENT_PARAMS]
    for x in p:
        if x["name"] == "amount":
            x["default"] = amount
        if x["name"] == "size":
            x["default"] = size
        if x["name"] == "evolution":
            x["default"] = evolution
        if x["name"] == "seed":
            x["default"] = seed
    return {"type": "customShader", "name": name,
            "description": "Turbulent Displace: fractal noise displaces the layer's pixels; `amount` is keyed for jolts that settle sharp.",
            "wgsl": TURBULENT_WGSL, "params": p, "textureInputs": []}


def grunge(name, map_layer, displace=0.0, softness=0.08, map_scale=1.0):
    p = [dict(x) for x in GRUNGE_PARAMS]
    for x in p:
        if x["name"] == "displace":
            x["default"] = displace
        if x["name"] == "softness":
            x["default"] = softness
        if x["name"] == "mapScale":
            x["default"] = map_scale
    return {"type": "customShader", "name": name,
            "description": "Displacement Map + dissolve driven by the Grunge 353 texture (levelled). `progress` dissolves along the grunge; `displace` warps by it.",
            "wgsl": GRUNGE_WGSL, "params": p,
            "textureInputs": [{"name": "grungeMap", "description": "Levelled Grunge 353: brighter areas survive a dissolve longest and push pixels right/down.",
                               "sourceLayerId": map_layer}]}


RIPPLE_WGSL = _VS + """
struct Params {
  animationTime: f32,
  x0: f32, y0: f32, t0: f32, s0: f32,
  x1: f32, y1: f32, t1: f32, s1: f32,
  x2: f32, y2: f32, t2: f32, s2: f32,
  x3: f32, y3: f32, t3: f32, s3: f32,
  speed: f32, wavelength: f32, decay: f32, aspect: f32,
  _pad0: f32, _pad1: f32, _pad2: f32,
};
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;

fn ring(px: vec2<f32>, c: vec2<f32>, t0: f32, strength: f32) -> vec3<f32> {
  let tau = params.animationTime - t0;
  if (tau < 0.0 || strength <= 0.0) { return vec3<f32>(0.0); }
  let d = vec2<f32>(px.x - c.x, (px.y - c.y) / max(params.aspect, 0.05));
  let r = length(d);
  let front = params.speed * tau;
  let env = exp(-tau / params.decay) * exp(-pow((r - front) / (params.wavelength * 1.6), 2.0));
  let w = sin(6.2831853 * (r - front) / params.wavelength) * env * strength;
  let dir = select(vec2<f32>(0.0), d / r, r > 0.001);
  return vec3<f32>(dir * w, max(w, 0.0));
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_texture));
  let px = input.tex_coords * dims;
  var acc = ring(px, vec2<f32>(params.x0, params.y0), params.t0, params.s0);
  acc = acc + ring(px, vec2<f32>(params.x1, params.y1), params.t1, params.s1);
  acc = acc + ring(px, vec2<f32>(params.x2, params.y2), params.t2, params.s2);
  acc = acc + ring(px, vec2<f32>(params.x3, params.y3), params.t3, params.s3);
  let c = textureSample(t_texture, s_sampler, input.tex_coords + vec2<f32>(acc.x, acc.y * params.aspect) / dims);
  let glint = vec3<f32>(1.0, 0.78, 0.55) * acc.z * 0.035;
  let a = clamp(c.a + acc.z * 0.035, 0.0, 1.0);
  let rgb = c.rgb + glint;
  return vec4<f32>(clamp(rgb, vec3<f32>(0.0), vec3<f32>(a)), a);
}
"""


def ripples(name, drops, speed=520.0, wavelength=26.0, decay=0.55, aspect=0.22):
    """drops: up to 4 (x_px, y_px, t_seconds_on_layer_clock, strength_px)."""
    drops = (list(drops) + [(0, 0, 999, 0)] * 4)[:4]
    p = [{"name": "animationTime", "description": "Engine-driven layer clock in seconds.", "min": 0, "max": 3600, "default": 0}]
    for i, (x, y, t, s) in enumerate(drops):
        p += [{"name": f"drop{i}.x", "description": f"Impact {i} centre x (px).", "min": -4000, "max": 6000, "default": x},
              {"name": f"drop{i}.y", "description": f"Impact {i} centre y (px).", "min": -4000, "max": 6000, "default": y},
              {"name": f"drop{i}Time", "description": f"Impact {i} time on the layer clock (s).", "min": 0, "max": 999, "default": t},
              {"name": f"drop{i}Strength", "description": f"Impact {i} ripple strength (px of displacement).", "min": 0, "max": 40, "default": s}]
    p += [{"name": "speed", "description": "Ring expansion speed (px/s).", "min": 10, "max": 4000, "default": speed},
          {"name": "wavelength", "description": "Ripple wavelength (px).", "min": 2, "max": 200, "default": wavelength},
          {"name": "decay", "description": "Ripple lifetime constant (s).", "min": 0.05, "max": 5, "default": decay},
          {"name": "aspect", "description": "Vertical squash of the rings: ground circles seen in perspective.", "min": 0.05, "max": 1, "default": aspect}]
    p += [{"name": f"_pad{i}", "description": "Unused padding slot.", "min": 0, "max": 1, "default": 0} for i in range(3)]
    return {"type": "customShader", "name": name,
            "description": "Puddle ripples: up to four impacts send expanding, decaying rings through the wet-ground reflection.",
            "wgsl": RIPPLE_WGSL, "params": p, "textureInputs": []}
