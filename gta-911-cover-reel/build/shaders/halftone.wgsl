struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { cell: f32, contrast: f32, width: f32, height: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let px = input.tex_coords * vec2<f32>(params.width, params.height);
  // rotate the screen 45 degrees like a print halftone
  let r = vec2<f32>(px.x * 0.7071 - px.y * 0.7071, px.x * 0.7071 + px.y * 0.7071);
  let cellc = (floor(r / params.cell) + 0.5) * params.cell;
  let back = vec2<f32>(cellc.x * 0.7071 + cellc.y * 0.7071, -cellc.x * 0.7071 + cellc.y * 0.7071);
  let c = textureSample(t_texture, s_sampler, clamp(back / vec2<f32>(params.width, params.height), vec2<f32>(0.0), vec2<f32>(1.0)));
  let a = textureSample(t_texture, s_sampler, input.tex_coords).a;
  var l = 0.0; if (c.a > 0.0) { l = dot(c.rgb / c.a, vec3<f32>(0.2126, 0.7152, 0.0722)); }
  l = clamp((l - 0.5) * params.contrast + 0.5, 0.0, 1.0);
  let d = length(r - cellc) / (params.cell * 0.5);
  let radius = sqrt(l) * 1.12;
  let ink = 1.0 - smoothstep(radius - 0.12, radius + 0.12, d);
  let dark = vec3<f32>(0.055, 0.050, 0.045); let paper = vec3<f32>(0.937, 0.914, 0.875);
  let o = mix(dark, paper, ink) * a;
  return vec4<f32>(clamp(o, vec3<f32>(0.0), vec3<f32>(a)), a);
}
