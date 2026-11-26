struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { a42: f32, a66: f32, a86: f32, a100: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
// CSS radial-gradient(ellipse 72% 72% at 50% 50%, transparent 42%, black a66 at 66%, a86 at 86%, a100 at 100%)
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let d = length((input.tex_coords - vec2<f32>(0.5)) / vec2<f32>(0.72, 0.72));
  var a = 0.0;
  if (d < 0.42) { a = 0.0; } else if (d < 0.66) { a = mix(0.0, params.a66, (d - 0.42) / 0.24); }
  else if (d < 0.86) { a = mix(params.a66, params.a86, (d - 0.66) / 0.20); } else if (d < 1.0) { a = mix(params.a86, params.a100, (d - 0.86) / 0.14); } else { a = params.a100; }
  return vec4<f32>(0.0, 0.0, 0.0, a);
}
