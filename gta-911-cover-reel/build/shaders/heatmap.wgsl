struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { amount: f32, _pad0: f32, _pad1: f32, _pad2: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
// luminance through #2B0A3D > #8E1A5C > #E8452C > #F7A43A > #FFF3C4
fn ramp(l: f32) -> vec3<f32> {
  let c0 = vec3<f32>(0.169, 0.039, 0.239); let c1 = vec3<f32>(0.557, 0.102, 0.361); let c2 = vec3<f32>(0.910, 0.271, 0.173);
  let c3 = vec3<f32>(0.969, 0.643, 0.227); let c4 = vec3<f32>(1.0, 0.953, 0.769);
  let x = clamp(l, 0.0, 1.0) * 4.0;
  if (x < 1.0) { return mix(c0, c1, x); } if (x < 2.0) { return mix(c1, c2, x - 1.0); } if (x < 3.0) { return mix(c2, c3, x - 2.0); } return mix(c3, c4, x - 3.0);
}
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let c = textureSample(t_texture, s_sampler, input.tex_coords);
  if (c.a <= 0.0) { return vec4<f32>(0.0); }
  let rgb = c.rgb / c.a;
  let l = dot(rgb, vec3<f32>(0.2126, 0.7152, 0.0722));
  let o = mix(rgb, ramp(l), params.amount) * c.a;
  return vec4<f32>(clamp(o, vec3<f32>(0.0), vec3<f32>(c.a)), c.a);
}
