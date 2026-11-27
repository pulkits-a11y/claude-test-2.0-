struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { animationTime: f32, amount: f32, height: f32, seed: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn h2(p: vec2<f32>) -> f32 { return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453); }
// Static noise through text: rows jitter sideways, grains of the letters drop out and the rest turns to grey snow.
// Only touches pixels the text already covers (alpha is kept), so nothing appears around the words.
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let a = params.amount;
  let uv = input.tex_coords;
  if (a <= 0.001) { return textureSample(t_texture, s_sampler, uv); }
  let f = floor(params.animationTime * 30.0) + params.seed * 17.0;
  let row = floor(uv.y * params.height / 2.0);
  let jump = step(0.55, h2(vec2<f32>(row * 0.37, f + 3.0)));
  let dx = (h2(vec2<f32>(row, f)) - 0.5) * 0.035 * a * jump;
  let c = textureSample(t_texture, s_sampler, vec2<f32>(uv.x + dx, uv.y));
  let g = floor(uv * vec2<f32>(params.height * 1.7778, params.height) / 2.0);
  let n = h2(g + vec2<f32>(f, f * 1.3));
  let keep = step(0.42 * a, n);
  let col = mix(c.rgb, vec3<f32>(n) * c.a, 0.6 * a) * keep;
  return vec4<f32>(col, c.a * keep);
}
