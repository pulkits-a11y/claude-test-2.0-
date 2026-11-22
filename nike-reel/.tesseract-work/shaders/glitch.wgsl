// Glitch transition: horizontal block tearing + RGB split + blocky dropout, driven by `amount` (0 = clean).
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
  amount: f32,
  _pad0: f32,
  _pad1: f32,
};
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn hash(p: vec2<f32>) -> f32 { return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453); }
fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let a = clamp(params.amount, 0.0, 1.0);
  let fr = floor(params.animationTime * 30.0);
  let band = floor(uv.y * 26.0);
  let r = hash(vec2<f32>(band, fr));
  let tear = select(0.0, (hash(vec2<f32>(band, fr + 7.0)) - 0.5) * 0.22, r < 0.45 * a);
  let blk = floor(uv * vec2<f32>(18.0, 12.0));
  let drop = hash(blk + vec2<f32>(fr, fr * 1.3)) < 0.10 * a;
  let off = 0.018 * a + abs(tear) * 0.4;
  let u = vec2<f32>(fract(uv.x + tear), uv.y);
  let cr = textureSample(t_texture, s_sampler, vec2<f32>(fract(u.x + off), u.y));
  let cg = textureSample(t_texture, s_sampler, u);
  let cb = textureSample(t_texture, s_sampler, vec2<f32>(fract(u.x - off), u.y));
  var col = vec4<f32>(cr.r, cg.g, cb.b, max(cg.a, max(cr.a, cb.a)));
  let line = select(1.0, 0.55, fract(uv.y * 540.0 + fr * 0.37) < 0.5 * a * 0.6);
  col = vec4<f32>(col.rgb * line, col.a);
  if (drop) { col = vec4<f32>(col.rgb * 0.15 + vec3<f32>(0.0, col.a * 0.2, 0.0), col.a); }
  return col;
}
@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let raw = author_frag(input.tex_coords);
  return vec4<f32>(clamp(raw.rgb, vec3<f32>(0.0), vec3<f32>(raw.a)), raw.a);
}
