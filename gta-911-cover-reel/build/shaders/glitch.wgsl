struct VertexInput { @location(0) position: vec2<f32>, @location(1) tex_coords: vec2<f32>, @location(2) color: vec4<f32>, };
struct VertexOutput { @builtin(position) clip_position: vec4<f32>, @location(0) tex_coords: vec2<f32>, };
@vertex fn vs_main(input: VertexInput) -> VertexOutput { var out: VertexOutput; out.clip_position = vec4<f32>(input.position, 0.0, 1.0); out.tex_coords = input.tex_coords; return out; }
struct Params { animationTime: f32, amount: f32, width: f32, height: f32, seed: f32, _pad0: f32, _pad1: f32, _pad2: f32, };
@group(0) @binding(0) var t_texture: texture_2d<f32>;
@group(0) @binding(1) var s_sampler: sampler;
@group(0) @binding(2) var<uniform> params: Params;
fn h1(x: f32) -> f32 { return fract(sin(x * 91.3458) * 47453.5453); }
fn h2(p: vec2<f32>) -> f32 { return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5453); }
// Digital glitch transition: horizontal band tears, RGB split, displaced and inverted blocks, scanline flicker.
// A new pattern every frame (30 fps); 'amount' 0..1 is keyframed around the cut.
@fragment fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  let a = params.amount;
  let uv = input.tex_coords;
  if (a <= 0.001) { return textureSample(t_texture, s_sampler, uv); }
  let f = floor(params.animationTime * 30.0) + params.seed * 13.0;
  // bands of varying height
  let bandH = mix(0.012, 0.09, h1(f * 3.7 + 1.0));
  let band = floor(uv.y / bandH);
  let r = h2(vec2<f32>(band, f));
  var dx = 0.0;
  if (r > 1.0 - 0.55 * a) { dx = (h2(vec2<f32>(band * 1.3, f + 7.0)) - 0.5) * 0.18 * a; }
  // blocks
  let bs = vec2<f32>(mix(0.04, 0.16, h1(f + 3.0)), mix(0.02, 0.07, h1(f + 9.0)));
  let cell = floor(uv / bs);
  let rb = h2(cell + vec2<f32>(f * 1.7, f * 0.3));
  var inv = 0.0;
  if (rb > 1.0 - 0.12 * a) { dx = dx + (h2(cell + 3.1) - 0.5) * 0.25 * a; inv = 0.7 * step(0.82, h2(cell + f)); }
  let split = 0.012 * a + 0.02 * a * step(0.5, r);
  let base = vec2<f32>(fract(uv.x + dx), uv.y);
  let cr = textureSample(t_texture, s_sampler, vec2<f32>(fract(base.x + split), base.y));
  let cg = textureSample(t_texture, s_sampler, base);
  let cb = textureSample(t_texture, s_sampler, vec2<f32>(fract(base.x - split), base.y));
  var col = vec3<f32>(cr.r, cg.g, cb.b);
  let al = max(cg.a, max(cr.a, cb.a));
  col = mix(col, vec3<f32>(al) - col, inv * a);
  let scan = 1.0 - 0.25 * a * step(0.5, fract(uv.y * params.height / 3.0 + h1(f) ));
  col = col * scan;
  return vec4<f32>(clamp(col, vec3<f32>(0.0), vec3<f32>(al)), al);
}
