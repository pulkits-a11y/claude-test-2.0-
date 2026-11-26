struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { animationTime: f32, amount: f32, width: f32, height: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn h(p: vec2<f32>) -> f32 { return fract(sin(dot(p, vec2<f32>(12.9898, 78.233))) * 43758.5453); }
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let c = textureSample(t_texture, s_sampler, input.tex_coords);
  let f = floor(params.animationTime * 30.0);
  let px = floor(input.tex_coords * vec2<f32>(params.width, params.height) / 2.0);
  let n = h(px + vec2<f32>(f * 17.0, f * 31.0));
  let bar = 0.75 + 0.25 * sin(input.tex_coords.y * 40.0 + f * 2.7);
  let s = vec3<f32>(n * bar) * c.a;
  let o = mix(c.rgb, s, params.amount);
  return vec4<f32>(clamp(o, vec3<f32>(0.0), vec3<f32>(c.a)), c.a);
}
