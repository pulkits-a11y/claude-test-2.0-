// Screen mesh: two Venetian-blind passes (0 and 90 degrees), multiplied over the image.
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
  periodPx: f32,
  lineFrac: f32,
  strength: f32,
  _pad0: f32,
};
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn author_frag(uv: vec2<f32>) -> vec4<f32> {
  let dims = vec2<f32>(textureDimensions(t_texture));
  let c = textureSample(t_texture, s_sampler, uv);
  let p = uv * dims / max(params.periodPx, 1.0);
  let h = select(0.0, 1.0, fract(p.y) < params.lineFrac);
  let v = select(0.0, 1.0, fract(p.x) < params.lineFrac);
  let m = 1.0 - params.strength * max(h, v);
  return vec4<f32>(c.rgb * m, c.a);
}
@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let raw = author_frag(input.tex_coords);
  return vec4<f32>(clamp(raw.rgb, vec3<f32>(0.0), vec3<f32>(raw.a)), raw.a);
}
