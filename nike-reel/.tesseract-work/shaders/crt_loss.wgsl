// CRT signal loss: `loss` 0 = clean picture, 1 = full static. Bright collapse flash in the first frames, then
// snow (per-pixel noise every frame), horizontal tearing, a rolling bar and brightness flicker.
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
  loss: f32,
  flash: f32,
  _pad0: f32,
};
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn hash(p: vec2<f32>) -> f32 { return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453); }
fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_texture));
  let L = clamp(params.loss, 0.0, 1.0);
  let fr = floor(params.animationTime * 30.0);
  let row = floor(uv.y * dims.y / 3.0);
  let tear = (hash(vec2<f32>(row, fr)) - 0.5) * 0.06 * L;
  let c = textureSample(t_texture, s_sampler, vec2<f32>(fract(uv.x + tear), uv.y));
  let n = hash(floor(uv * dims / 2.0) + vec2<f32>(fr * 13.1, fr * 7.7));
  let roll = fract(uv.y + params.animationTime * 0.9);
  let bar = 1.0 - 0.35 * smoothstep(0.0, 0.08, roll) * (1.0 - smoothstep(0.08, 0.22, roll));
  let flick = 0.85 + 0.15 * hash(vec2<f32>(fr, 3.0));
  let snow = vec3<f32>(n * 0.85 * bar * flick);
  var rgb = mix(c.rgb, snow, L);
  rgb = mix(rgb, vec3<f32>(1.0, 0.98, 0.95), clamp(params.flash, 0.0, 1.0));
  return vec4<f32>(rgb, 1.0);
}
@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let raw = author_frag(input.tex_coords);
  return vec4<f32>(clamp(raw.rgb, vec3<f32>(0.0), vec3<f32>(raw.a)), raw.a);
}
