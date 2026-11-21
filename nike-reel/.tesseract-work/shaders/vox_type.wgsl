// "VOX type": turbulent displace + displacement-map wobble + noise inside the letters.
// Time is held in steps (Stepped look): the noise field only changes every `stepSeconds`.
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
struct Params {
  animationTime: f32,
  displacePx: f32,
  turbulenceScalePx: f32,
  grainAmount: f32,
  stepSeconds: f32,
  _pad0: f32,
  _pad1: f32,
  _pad2: f32,
};
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;

fn hash2(p: vec2<f32>) -> f32 {
  let h = dot(p, vec2<f32>(127.1, 311.7));
  return fract(sin(h) * 43758.5453123);
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
fn turbulence(p: vec2<f32>) -> f32 {
  var s = 0.0;
  var amp = 0.5;
  var q = p;
  for (var k = 0; k < 4; k = k + 1) {
    s = s + amp * abs(vnoise(q) * 2.0 - 1.0);
    q = q * 2.03;
    amp = amp * 0.5;
  }
  return s;
}
fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_texture));
  let px = uv * dims;
  let step = floor(params.animationTime / max(params.stepSeconds, 0.001));
  let seed = vec2<f32>(step * 17.31, step * 9.73);
  let sc = max(params.turbulenceScalePx, 1.0);
  // two decorrelated turbulence fields drive x/y displacement
  let dx = turbulence(px / sc + seed) - 0.47;
  let dy = turbulence(px / sc + seed + vec2<f32>(41.7, 13.3)) - 0.47;
  let duv = vec2<f32>(dx, dy) * 2.0 * params.displacePx / dims;
  let c = textureSample(t_texture, s_sampler, uv + duv);
  // grain inside the glyphs only (alpha untouched)
  let g = hash2(floor(px) + seed * 3.0) - 0.5;
  let rgb = c.rgb * (1.0 + g * params.grainAmount * 2.0);
  return vec4<f32>(rgb, c.a);
}
@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let raw = author_frag(input.tex_coords);
  return vec4<f32>(clamp(raw.rgb, vec3<f32>(0.0), vec3<f32>(raw.a)), raw.a);
}
