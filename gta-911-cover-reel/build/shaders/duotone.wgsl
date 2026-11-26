struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { shadow_r: f32, shadow_g: f32, shadow_b: f32, high_r: f32, high_g: f32, high_b: f32, contrast: f32, _pad0: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let c = textureSample(t_texture, s_sampler, input.tex_coords);
  if (c.a <= 0.0) { return vec4<f32>(0.0); }
  var l = dot(c.rgb / c.a, vec3<f32>(0.2126, 0.7152, 0.0722));
  l = clamp((l - 0.5) * params.contrast + 0.5, 0.0, 1.0);
  let o = mix(vec3<f32>(params.shadow_r, params.shadow_g, params.shadow_b), vec3<f32>(params.high_r, params.high_g, params.high_b), l) * c.a;
  return vec4<f32>(clamp(o, vec3<f32>(0.0), vec3<f32>(c.a)), c.a);
}
