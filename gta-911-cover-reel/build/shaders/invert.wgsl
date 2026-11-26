struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { amount: f32, _pad0: f32, _pad1: f32, _pad2: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let c = textureSample(t_texture, s_sampler, input.tex_coords);
  let o = mix(c.rgb, vec3<f32>(c.a) - c.rgb, params.amount);
  return vec4<f32>(clamp(o, vec3<f32>(0.0), vec3<f32>(c.a)), c.a);
}
