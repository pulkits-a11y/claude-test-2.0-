struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { animationTime: f32, amount: f32, bands: f32, height: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn h1(x: f32) -> f32 { return fract(sin(x * 12.9898) * 43758.5453); }
// CRT feed: B&W, contrast, scan lines, and stepped horizontal row tears (12 fps)
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let t = floor(params.animationTime * 12.0);
  let band = floor(input.tex_coords.y * params.bands);
  let r = h1(band * 7.13 + t * 3.1);
  var off = 0.0; if (r > 0.86) { off = (h1(band * 1.7 + t * 5.3) - 0.5) * params.amount; }
  let c = textureSample(t_texture, s_sampler, vec2<f32>(fract(input.tex_coords.x + off), input.tex_coords.y));
  let a = textureSample(t_texture, s_sampler, input.tex_coords).a;
  var l = 0.0; if (c.a > 0.0) { l = dot(c.rgb / c.a, vec3<f32>(0.2126, 0.7152, 0.0722)); }
  l = clamp(pow(l, 0.75) * 1.35 - 0.05, 0.0, 1.0);
  let scan = 0.88 + 0.12 * sin(input.tex_coords.y * params.height * 1.4);
  let o = vec3<f32>(l * scan) * a;
  return vec4<f32>(clamp(o, vec3<f32>(0.0), vec3<f32>(a)), a);
}
