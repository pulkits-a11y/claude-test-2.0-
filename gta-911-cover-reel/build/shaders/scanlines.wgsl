struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { dark: f32, period: f32, height: f32, lineAlpha: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
// repeating lines: 'dark' px of black at lineAlpha, then clear, every 'period' px (used with Multiply)
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let y = floor(input.tex_coords.y * params.height);
  let m = y - floor(y / params.period) * params.period;
  var a = 0.0; if (m < params.dark) { a = params.lineAlpha; }
  return vec4<f32>(0.0, 0.0, 0.0, a);
}
