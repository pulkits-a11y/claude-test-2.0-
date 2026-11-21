// Retail Pop-Up MG — three miniature storefronts pop up through a studio floor.
// Pure function of time: host.render(t) draws the frame for t seconds, nothing else
// carries state between frames. Seeded randomness only (mulberry32).
import * as THREE from "three";
import { RoomEnvironment } from "./lib/RoomEnvironment.js";
import { RoundedBoxGeometry } from "./lib/RoundedBoxGeometry.js";

const host = window.__mg;
const V = host.vars || {};
const W = host.width;
const H = host.height;
const FPS = 30;

const hex = (v, fb) => (/^#[0-9a-f]{6}$/i.test(String(v)) ? String(v) : fb);
const GROUND = hex(V.ground, "#111111");
const ACCENT = hex(V.accent, "#c4f0b4");
const INK = hex(V.ink, "#eeeeea");

// ---------------------------------------------------------------- timing (MG seconds)
// Placed at 0:30.00 in the reel, the VO lands: "DSW" 1.21, "Dillard's" 1.61, "Foot Locker" 3.07.
const T = {
  plots: [0.06, 0.16, 0.26], // floor plan outlines draw on
  dsw: 0.52, // emergence start: the roof breaks the floor here, slowly, then accelerates
  dill: 1.05,
  fl: 2.6,
  swooshIn: 4.12,
  swooshHold: 4.78,
  swooshOut: 5.32,
  swooshGone: 6.02,
};

// ---------------------------------------------------------------- utilities
function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, s) => a + (b - a) * s;
const smooth = (a, b, x) => {
  const s = clamp((x - a) / (b - a));
  return s * s * (3 - 2 * s);
};
const DEG = Math.PI / 180;

// Monotone cubic (Fritsch–Carlson) through [t, v] keys; optional start/end slopes.
function track(keys, startSlope, endSlope) {
  const n = keys.length;
  const ts = keys.map((k) => k[0]);
  const vs = keys.map((k) => k[1]);
  const d = [];
  for (let i = 0; i < n - 1; i++) d.push((vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i]));
  const m = new Array(n);
  m[0] = startSlope ?? d[0];
  m[n - 1] = endSlope ?? d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  for (let i = 0; i < n - 1; i++) {
    if (d[i] === 0) {
      m[i] = 0;
      m[i + 1] = 0;
      continue;
    }
    const a = m[i] / d[i];
    const b = m[i + 1] / d[i];
    const s = a * a + b * b;
    if (s > 9) {
      const tau = 3 / Math.sqrt(s);
      m[i] = tau * a * d[i];
      m[i + 1] = tau * b * d[i];
    }
  }
  return (t) => {
    if (t <= ts[0]) return vs[0] + m[0] * (t - ts[0]);
    if (t >= ts[n - 1]) return vs[n - 1] + m[n - 1] * (t - ts[n - 1]);
    let i = 0;
    while (t > ts[i + 1]) i++;
    const h = ts[i + 1] - ts[i];
    const s = (t - ts[i]) / h;
    const s2 = s * s;
    const s3 = s2 * s;
    return (
      (2 * s3 - 3 * s2 + 1) * vs[i] +
      (s3 - 2 * s2 + s) * h * m[i] +
      (-2 * s3 + 3 * s2) * vs[i + 1] +
      (s3 - s2) * h * m[i + 1]
    );
  };
}

// ---------------------------------------------------------------- renderer
const canvas = document.getElementById("stage");
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: false,
  alpha: false,
  preserveDrawingBuffer: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace; // the post pass encodes sRGB itself
renderer.toneMapping = THREE.NoToneMapping;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const halfFloatOK =
  renderer.extensions.has("EXT_color_buffer_float") ||
  renderer.extensions.has("EXT_color_buffer_half_float");
const sceneRT = new THREE.WebGLRenderTarget(W, H, {
  type: halfFloatOK ? THREE.HalfFloatType : THREE.UnsignedByteType,
  samples: 4,
  depthBuffer: true,
});

const scene = new THREE.Scene();
const bgColor = new THREE.Color(GROUND); // linear working space
scene.background = bgColor.clone();

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.2;
scene.environmentRotation = new THREE.Euler(0, 0, 0);

// ---------------------------------------------------------------- procedural textures
const rnd = mulberry32(20261121);

function canvasTex(w, h, draw, { srgb = false, nearest = false, repeat = false } = {}) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  draw(c.getContext("2d"), w, h);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  if (nearest) {
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.generateMipmaps = false;
  }
  if (repeat) tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  return tex;
}

// Displacement map: horizontal bands of random offsets (the classic AE displacement-map plate).
const bandTex = canvasTex(
  8,
  512,
  (g, w, h) => {
    let y = 0;
    while (y < h) {
      const bh = 3 + Math.floor(rnd() * 30);
      const r = rnd();
      const v = r < 0.35 ? 0.5 : r < 0.5 ? (rnd() < 0.5 ? 0.04 : 0.96) : rnd();
      const c = Math.round(v * 255);
      g.fillStyle = `rgb(${c},${c},${c})`;
      g.fillRect(0, y, w, bh);
      y += bh;
    }
  },
  { nearest: true, repeat: true },
);

// Smooth tiling value-noise map, used as the swoosh's displacement map.
const noiseTex = canvasTex(
  256,
  256,
  (g, w, h) => {
    const img = g.createImageData(w, h);
    const lat = (n) => {
      const a = new Float32Array(n * n);
      for (let i = 0; i < a.length; i++) a[i] = rnd();
      return a;
    };
    const octs = [
      [4, lat(4), 0.5],
      [8, lat(8), 0.27],
      [16, lat(16), 0.15],
      [32, lat(32), 0.08],
    ];
    const vn = (L, n, x, y) => {
      const xi = Math.floor(x);
      const yi = Math.floor(y);
      let fx = x - xi;
      let fy = y - yi;
      fx = fx * fx * (3 - 2 * fx);
      fy = fy * fy * (3 - 2 * fy);
      const at = (i, j) => L[((j + n) % n) * n + ((i + n) % n)];
      const a = at(xi, yi);
      const b = at(xi + 1, yi);
      const c = at(xi, yi + 1);
      const d = at(xi + 1, yi + 1);
      return lerp(lerp(a, b, fx), lerp(c, d, fx), fy);
    };
    for (let y = 0; y < h; y++)
      for (let x = 0; x < w; x++) {
        let s = 0;
        for (const [n, L, amp] of octs) s += amp * vn(L, n, (x / w) * n, (y / h) * n);
        const v = Math.round(clamp(s) * 255);
        const i = (y * w + x) * 4;
        img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
        img.data[i + 3] = 255;
      }
    g.putImageData(img, 0, 0);
  },
  { repeat: true },
);

// Soft rectangle (white = opaque) for contact shadows.
const softRect = canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = "#000";
  g.fillRect(0, 0, w, h);
  g.filter = "blur(16px)";
  g.fillStyle = "#fff";
  g.fillRect(w * 0.2, h * 0.2, w * 0.6, h * 0.6);
});

// Referee stripes for the Foot Locker portal.
const stripeTex = canvasTex(
  64,
  8,
  (g, w, h) => {
    g.fillStyle = "#141414";
    g.fillRect(0, 0, w, h);
    g.fillStyle = "#e9e8e3";
    g.fillRect(0, 0, w / 2, h);
  },
  { srgb: true, repeat: true },
);
stripeTex.magFilter = THREE.LinearFilter;
stripeTex.anisotropy = 8;

async function loadImage(url) {
  const img = new Image();
  img.src = url;
  await img.decode();
  return img;
}

// Logo → white alpha mask with transparent padding (so displaced lookups never clamp).
async function logoMask(url, { width = 2048, crop = null, pad = 0.08, soften = 0.012 } = {}) {
  const img = await loadImage(url);
  const sx = crop ? crop[0] : 0;
  const sy = crop ? crop[1] : 0;
  const sw = crop ? crop[2] : img.naturalWidth;
  const sh = crop ? crop[3] : img.naturalHeight;
  const aspect = sw / sh;
  const innerW = Math.round(width / (1 + 2 * pad));
  const innerH = Math.round(innerW / aspect);
  const padPx = Math.round(innerW * pad);
  const cw = innerW + 2 * padPx;
  const ch = innerH + 2 * padPx;
  const c = document.createElement("canvas");
  c.width = cw;
  c.height = ch;
  const g = c.getContext("2d");
  g.drawImage(img, sx, sy, sw, sh, padPx, padPx, innerW, innerH);
  const id = g.getImageData(0, 0, cw, ch);
  const px = id.data;
  for (let i = 0; i < px.length; i += 4) {
    const lum = (0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]) / 255;
    const a = (px[i + 3] / 255) * clamp((1 - lum) * 1.15);
    px[i] = px[i + 1] = px[i + 2] = 255;
    px[i + 3] = Math.round(a * 255);
  }
  g.putImageData(id, 0, 0);
  if (soften > 0) {
    // widen the edge ramp so the shader's grain threshold can erode it (rough, printed edges)
    const tmp = document.createElement("canvas");
    tmp.width = cw;
    tmp.height = ch;
    const tg = tmp.getContext("2d");
    tg.filter = `blur(${(innerH * soften).toFixed(2)}px)`;
    tg.drawImage(c, 0, 0);
    g.clearRect(0, 0, cw, ch);
    g.drawImage(tmp, 0, 0);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.NoColorSpace;
  tex.anisotropy = 8;
  return { tex, canvas: c, aspect: cw / ch, inner: innerW / cw };
}

function blurredCopy(srcCanvas, px) {
  const c = document.createElement("canvas");
  c.width = srcCanvas.width;
  c.height = srcCanvas.height;
  const g = c.getContext("2d");
  g.filter = `blur(${px}px)`;
  g.drawImage(srcCanvas, 0, 0);
  g.filter = `blur(${px * 0.35}px)`;
  g.drawImage(srcCanvas, 0, 0);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.NoColorSpace;
  return tex;
}

// ---------------------------------------------------------------- GLSL shared
const NOISE_GLSL = /* glsl */ `
  float hash12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
  float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
    float a = hash12(i), b = hash12(i+vec2(1.0,0.0)), c = hash12(i+vec2(0.0,1.0)), d = hash12(i+vec2(1.0,1.0));
    return mix(mix(a,b,f.x), mix(c,d,f.x), f.y); }
  float fbm(vec2 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 4; i++){ s += a*vnoise(p); p = p*2.03 + 17.1; a *= 0.5; } return s; }
`;

// Sign letters: turbulent-displaced, eroded edges, grain inside, displacement-map glitch on switch-on.
const SIGN_FRAG = /* glsl */ `
  uniform sampler2D uMask; uniform sampler2D uBands;
  uniform vec3 uColor; uniform float uShade, uBright, uGlitch, uSeed, uAspect, uRough, uErode;
  varying vec2 vUv;
  ${NOISE_GLSL}
  void main(){
    vec2 uv = vUv;
    // displacement map: band value pushes rows sideways while the sign "switches on"
    float band = texture2D(uBands, vec2(0.5, uv.y * 0.6 + floor(uSeed) * 0.137)).r;
    uv.x += (band - 0.5) * 0.16 * uGlitch;
    // turbulent displace: wobbling, organic letter edges
    vec2 q = vec2(uv.x * uAspect, uv.y) * 9.0;
    vec2 tw = vec2(fbm(q + uSeed * 0.71), fbm(q + 23.7 - uSeed * 0.53)) - 0.5;
    uv += tw * uRough * vec2(1.0 / uAspect, 1.0);
    float m = texture2D(uMask, uv).a;
    // erode the edge with screen-space grain (printed, not vector-clean)
    float g = hash12(floor(gl_FragCoord.xy / 1.5) + floor(uSeed) * 7.13);
    float thr = 0.5 + (g - 0.5) * uErode;
    float a = smoothstep(thr - 0.05, thr + 0.05, m);
    if (a < 0.03) discard;
    // noise inside the letters
    float grain = 0.7 + 0.3 * hash12(floor(gl_FragCoord.xy / 1.5) + floor(uSeed) * 3.31 + 11.0);
    vec3 col = uColor * grain * uBright * uShade;
    gl_FragColor = vec4(col, a);
  }
`;

const BASIC_VERT = /* glsl */ `
  varying vec2 vUv;
  void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
`;

const globalU = {
  uSeed: { value: 0 },
  uTime: { value: 0 },
};

// A sign made of stacked layers: a cheap extruded channel-letter look from any angle.
function makeSign(mask, width, color, { layers = 7, depth = 0.032, rough = 0.012, erode = 0.36, sideShade = 0.42 } = {}) {
  const h = width / mask.aspect;
  const group = new THREE.Group();
  const shared = {
    uBright: { value: 1 },
    uGlitch: { value: 0 },
  };
  const geo = new THREE.PlaneGeometry(width, h);
  for (let i = 0; i < layers; i++) {
    const front = i === layers - 1;
    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uMask: { value: mask.tex },
        uBands: { value: bandTex },
        uColor: { value: new THREE.Color(color) },
        uShade: { value: front ? 1 : lerp(sideShade * 0.75, sideShade, i / layers) },
        uAspect: { value: mask.aspect },
        uRough: { value: rough },
        uErode: { value: erode },
        uSeed: globalU.uSeed,
        uBright: shared.uBright,
        uGlitch: shared.uGlitch,
      },
      vertexShader: BASIC_VERT,
      fragmentShader: SIGN_FRAG,
      alphaToCoverage: true,
    });
    const m = new THREE.Mesh(geo, mat);
    m.position.z = (i / (layers - 1)) * depth;
    m.renderOrder = 2;
    group.add(m);
  }
  return { group, u: shared, height: h };
}

// ---------------------------------------------------------------- materials
const std = (color, roughness, metalness = 0, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness, ...extra });

const M = {
  concrete: std("#6d6a65", 0.95),
  curb: std("#8f8b85", 0.9),
  roof: std("#6e6b66", 0.95),
  hvac: std("#a3a19c", 0.55, 0.35),
  // DSW: light metal panels, charcoal sign panel, aluminium storefront
  dswPanel: std("#c3c0ba", 0.6, 0.08),
  dswSeam: std("#8e8b86", 0.7),
  charcoal: std("#2a2b2c", 0.55, 0.1),
  alu: std("#a9adb1", 0.3, 0.85),
  aluDark: std("#55585c", 0.35, 0.75),
  // Dillard's: warm limestone, bronze
  stone: std("#d9cdb5", 0.9),
  stoneDark: std("#bfb29a", 0.92),
  stoneLine: std("#a99c84", 0.95),
  bronze: std("#5b4631", 0.4, 0.75),
  // Foot Locker: black, referee stripes
  flBlack: std("#161616", 0.62),
  flTrim: std("#2c2c2c", 0.5),
  stripes: std("#ffffff", 0.6, 0, { map: stripeTex }),
  glass: new THREE.MeshStandardMaterial({
    color: "#1b252d",
    roughness: 0.05,
    metalness: 0.1,
    transparent: true,
    opacity: 0.34,
    envMapIntensity: 2.4,
    depthWrite: false,
  }),
  doorGlass: new THREE.MeshStandardMaterial({
    color: "#141b21",
    roughness: 0.05,
    metalness: 0.1,
    transparent: true,
    opacity: 0.5,
    envMapIntensity: 2.4,
    depthWrite: false,
  }),
};

function interiorMat(color, emissive) {
  return new THREE.MeshStandardMaterial({
    color,
    emissive,
    emissiveIntensity: 0,
    roughness: 0.9,
    side: THREE.BackSide,
  });
}

// ---------------------------------------------------------------- geometry helpers
// box with its base at y0 (not centre)
const geoCache = new Map();
function boxGeo(w, h, d) {
  const k = `${w.toFixed(4)}|${h.toFixed(4)}|${d.toFixed(4)}`;
  let g = geoCache.get(k);
  if (!g) {
    const mn = Math.min(w, h, d);
    // model-making bevel: big masses catch a thin highlight on every edge
    g = mn > 0.035 ? new RoundedBoxGeometry(w, h, d, 2, Math.min(0.011, mn * 0.22)) : new THREE.BoxGeometry(w, h, d);
    geoCache.set(k, g);
  }
  return g;
}
function box(parent, w, h, d, mat, x, y0, z, { cast = true, recv = true } = {}) {
  const m = new THREE.Mesh(boxGeo(w, h, d), mat);
  m.position.set(x, y0 + h / 2, z);
  m.castShadow = cast;
  m.receiveShadow = recv;
  parent.add(m);
  return m;
}

// A wall in the XY plane (front face at zFront) built from solid cells around rectangular openings.
function wall(parent, mat, x0, x1, y0, y1, zFront, th, openings) {
  const xs = new Set([x0, x1]);
  const ys = new Set([y0, y1]);
  for (const o of openings) {
    xs.add(o.x0);
    xs.add(o.x1);
    ys.add(o.y0);
    ys.add(o.y1);
  }
  const X = [...xs].sort((a, b) => a - b);
  const Y = [...ys].sort((a, b) => a - b);
  const hole = (cx, cy) => openings.some((o) => cx > o.x0 && cx < o.x1 && cy > o.y0 && cy < o.y1);
  for (let j = 0; j < Y.length - 1; j++) {
    let run = null;
    for (let i = 0; i < X.length - 1; i++) {
      const solid = !hole((X[i] + X[i + 1]) / 2, (Y[j] + Y[j + 1]) / 2);
      if (solid) {
        if (run) run[1] = X[i + 1];
        else run = [X[i], X[i + 1]];
      }
      if ((!solid || i === X.length - 2) && run) {
        box(parent, run[1] - run[0], Y[j + 1] - Y[j], th, mat, (run[0] + run[1]) / 2, Y[j], zFront - th / 2);
        run = null;
      }
    }
  }
}

// Frame of thin bars around/inside an opening.
function mullions(parent, mat, x0, x1, y0, y1, z, { vx = [], hy = [], t = 0.022, d = 0.03, frame = true } = {}) {
  const bars = [];
  if (frame) {
    bars.push([x0 + t / 2, y0, y1], [x1 - t / 2, y0, y1]);
    box(parent, x1 - x0, t, d, mat, (x0 + x1) / 2, y1 - t, z);
    box(parent, x1 - x0, t, d, mat, (x0 + x1) / 2, y0, z);
  }
  for (const x of vx) bars.push([x, y0, y1]);
  for (const [x, a, b] of bars) box(parent, t, b - a, d, mat, x, a, z);
  for (const y of hy) box(parent, x1 - x0, t, d, mat, (x0 + x1) / 2, y - t / 2, z);
}

function pane(parent, mat, x0, x1, y0, y1, z) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, y1 - y0), mat);
  m.position.set((x0 + x1) / 2, (y0 + y1) / 2, z);
  m.renderOrder = 1;
  parent.add(m);
  return m;
}

// Lit room behind an opening (BackSide box: we see its inner faces).
function room(parent, mat, x0, x1, y0, y1, zFront, depth) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0 + 0.02, y1 - y0 + 0.02, depth), mat);
  m.position.set((x0 + x1) / 2, (y0 + y1) / 2, zFront - depth / 2);
  m.receiveShadow = true;
  parent.add(m);
  return m;
}

const aoMat = new THREE.MeshBasicMaterial({
  color: "#000000",
  alphaMap: softRect,
  transparent: true,
  opacity: 0.55,
  depthWrite: false,
  polygonOffset: true,
  polygonOffsetFactor: -2,
});
function baseAO(parent, w, d, zc, y) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry((w + 0.2) / 0.6, (d + 0.2) / 0.6), aoMat);
  m.rotation.x = -Math.PI / 2;
  m.position.set(0, y, zc);
  m.renderOrder = 1;
  parent.add(m);
}
function plinth(parent, pw, pd, ph) {
  box(parent, pw, ph, pd, M.concrete, 0, 0, 0);
  box(parent, pw - 0.05, 0.014, 0.4, M.curb, 0, ph, pd / 2 - 0.225);
  // thin chamfer line at the top edge (reads as a model base)
  box(parent, pw + 0.004, 0.012, pd + 0.004, M.curb, 0, ph - 0.012, 0, { cast: false });
}

// ---------------------------------------------------------------- the stores
const PH = 0.1; // plinth height

function buildDSW(mask) {
  const g = new THREE.Group();
  const PW = 2.15;
  const PD = 1.95;
  plinth(g, PW, PD, PH);
  const w = 1.86;
  const h = 1.98;
  const d = 1.45;
  const zf = 0.45;
  const zb = zf - d;
  const y0 = PH + 0.014;
  const inner = interiorMat("#2a251f", "#ffd3a1");
  baseAO(g, w, d, (zf + zb) / 2, PH + 0.0145);
  // body shell
  box(g, w, h, d - 0.5, M.dswPanel, 0, y0, zb + (d - 0.5) / 2);
  box(g, 0.05, h, 0.52, M.dswPanel, -w / 2 + 0.025, y0, zf - 0.26);
  box(g, 0.05, h, 0.52, M.dswPanel, w / 2 - 0.025, y0, zf - 0.26);
  box(g, w + 0.03, 0.05, d + 0.02, M.roof, 0, y0 + h, (zf + zb) / 2);
  box(g, w + 0.05, 0.075, 0.05, M.charcoal, 0, y0 + h - 0.015, zf + 0.012);
  box(g, 0.05, 0.075, d, M.charcoal, -w / 2 - 0.0, y0 + h - 0.015, (zf + zb) / 2);
  box(g, 0.05, 0.075, d, M.charcoal, w / 2 + 0.0, y0 + h - 0.015, (zf + zb) / 2);
  // facade
  const store = { x0: -0.84, x1: 0.18, y0: y0 + 0.06, y1: y0 + 0.86 };
  const door = { x0: 0.32, x1: 0.82, y0: y0, y1: y0 + 0.8 };
  wall(g, M.dswPanel, -w / 2, w / 2, y0, y0 + h, zf, 0.05, [store, door]);
  // panel seams on the upper facade
  for (let i = 1; i < 7; i++) {
    const x = -w / 2 + (i * w) / 7;
    box(g, 0.008, h - 1.0, 0.004, M.dswSeam, x, y0 + 0.98, zf + 0.002, { cast: false });
  }
  box(g, w, 0.01, 0.006, M.dswSeam, 0, y0 + 0.97, zf + 0.002, { cast: false });
  // storefront glazing
  room(g, inner, store.x0, store.x1, store.y0, store.y1, zf - 0.05, 0.5);
  mullions(g, M.aluDark, store.x0, store.x1, store.y0, store.y1, zf - 0.03, {
    vx: [-0.59, -0.33, -0.08],
    hy: [store.y0 + 0.62],
  });
  pane(g, M.glass, store.x0, store.x1, store.y0, store.y1, zf - 0.035);
  // interior: low display tables + shoe wall
  const shoeRnd = mulberry32(11);
  for (let i = 0; i < 9; i++) {
    const x = store.x0 + 0.08 + i * 0.105;
    for (let r = 0; r < 3; r++) {
      const c = ["#d8d4cc", "#8b8780", "#2d2d2d", "#b9a58a"][Math.floor(shoeRnd() * 4)];
      box(g, 0.07, 0.035, 0.05, std(c, 0.7), x, store.y0 + 0.2 + r * 0.17, zf - 0.52, { cast: false });
    }
  }
  box(g, 0.32, 0.12, 0.16, M.charcoal, -0.45, store.y0, zf - 0.3, { cast: false });
  box(g, 0.22, 0.12, 0.16, M.charcoal, -0.05, store.y0, zf - 0.33, { cast: false });
  // glass vestibule entrance, projecting
  const vz = zf + 0.2;
  room(g, inner, door.x0, door.x1, door.y0, door.y1, zf - 0.05, 0.45);
  mullions(g, M.alu, door.x0, door.x1, y0, y0 + 0.78, vz, { vx: [0.57], hy: [y0 + 0.62] });
  pane(g, M.doorGlass, door.x0, door.x1, y0, y0 + 0.78, vz - 0.005);
  for (const sx of [door.x0, door.x1]) {
    box(g, 0.022, 0.78, 0.22, M.alu, sx + (sx === door.x0 ? 0.011 : -0.011), y0, zf + 0.09);
    const side = new THREE.Mesh(new THREE.PlaneGeometry(0.2, 0.76), M.doorGlass);
    side.rotation.y = Math.PI / 2;
    side.position.set(sx, y0 + 0.39, zf + 0.1);
    g.add(side);
  }
  box(g, 0.025, 0.2, 0.012, M.aluDark, 0.535, y0 + 0.3, vz + 0.012);
  box(g, 0.025, 0.2, 0.012, M.aluDark, 0.605, y0 + 0.3, vz + 0.012);
  // canopy with a lit soffit strip
  box(g, 0.66, 0.04, 0.36, M.charcoal, 0.57, y0 + 0.8, zf + 0.15);
  const strip = std("#111", 0.5, 0, { emissive: "#fff2dc", emissiveIntensity: 0 });
  box(g, 0.56, 0.006, 0.02, strip, 0.57, y0 + 0.795, zf + 0.3, { cast: false });
  // sign panel + letters
  const panelW = 1.46;
  const panelH = 0.56;
  const px = -0.14;
  const py = y0 + 1.16;
  box(g, panelW, panelH, 0.06, M.charcoal, px, py, zf + 0.025);
  const sign = makeSign(mask, 1.3, INK, { depth: 0.03 });
  sign.group.position.set(px, py + panelH / 2, zf + 0.06);
  g.add(sign.group);
  // rooftop
  box(g, 0.36, 0.17, 0.3, M.hvac, -0.48, y0 + h + 0.05, zb + 0.42);
  box(g, 0.24, 0.12, 0.22, M.hvac, 0.42, y0 + h + 0.05, zb + 0.35);
  box(g, 0.5, 0.05, 0.06, M.hvac, 0.42, y0 + h + 0.17, zb + 0.35);
  return {
    group: g,
    pw: PW,
    pd: PD,
    height: y0 + h + 0.22,
    signs: [sign],
    lights: [inner, strip],
    lightGain: [0.42, 2.2],
  };
}

function buildDillards(mask) {
  const g = new THREE.Group();
  const PW = 2.36;
  const PD = 2.1;
  plinth(g, PW, PD, PH);
  const w = 2.06;
  const h = 2.72;
  const d = 1.75;
  const zf = 0.55;
  const zb = zf - d;
  const zc = (zf + zb) / 2;
  const y0 = PH + 0.014;
  const inner = interiorMat("#2e261d", "#ffcf98");
  baseAO(g, w, d, zc, PH + 0.0145);
  box(g, w, h, d - 0.4, M.stone, 0, y0, zb + (d - 0.4) / 2);
  box(g, 0.06, h, 0.42, M.stone, -w / 2 + 0.03, y0, zf - 0.21);
  box(g, 0.06, h, 0.42, M.stone, w / 2 - 0.03, y0, zf - 0.21);
  // cornice (two steps) + roof
  box(g, w + 0.06, 0.06, d + 0.06, M.stoneDark, 0, y0 + h - 0.06, zc);
  box(g, w + 0.13, 0.08, d + 0.13, M.stone, 0, y0 + h, zc);
  box(g, w - 0.1, 0.02, d - 0.1, M.roof, 0, y0 + h + 0.08, zc, { cast: false });
  // facade openings
  const portal = { x0: -0.3, x1: 0.3, y0: y0, y1: y0 + 1.18 };
  const winL = { x0: -0.86, x1: -0.47, y0: y0 + 0.22, y1: y0 + 0.98 };
  const winR = { x0: 0.47, x1: 0.86, y0: y0 + 0.22, y1: y0 + 0.98 };
  wall(g, M.stone, -w / 2, w / 2, y0, y0 + h - 0.06, zf, 0.06, [portal, winL, winR]);
  // base course and string course
  box(g, w + 0.02, 0.14, 0.03, M.stoneDark, 0, y0, zf + 0.012);
  box(g, w + 0.03, 0.055, 0.045, M.stoneDark, 0, y0 + 1.3, zf + 0.018);
  // rustication lines on the ground storey
  for (let k = 1; k < 7; k++) {
    const y = y0 + 0.14 + k * 0.165;
    if (y > y0 + 1.28) break;
    for (const [a, b] of [
      [-w / 2, winL.x0],
      [winL.x1, portal.x0],
      [portal.x1, winR.x0],
      [winR.x1, w / 2],
    ]) {
      if (y > winL.y0 && y < winL.y1 && (a === -w / 2 || b === w / 2)) continue;
      box(g, b - a - 0.02, 0.008, 0.004, M.stoneLine, (a + b) / 2, y, zf + 0.002, { cast: false });
    }
  }
  // corner pilasters
  for (const s of [-1, 1]) box(g, 0.11, h - 0.2, 0.05, M.stoneDark, s * (w / 2 - 0.045), y0 + 0.14, zf + 0.02);
  // portal: stone surround, recessed bronze doors and transom
  box(g, 0.08, 1.24, 0.05, M.stoneDark, portal.x0 - 0.04, y0, zf + 0.02);
  box(g, 0.08, 1.24, 0.05, M.stoneDark, portal.x1 + 0.04, y0, zf + 0.02);
  box(g, 0.76, 0.09, 0.06, M.stoneDark, 0, y0 + 1.18, zf + 0.025);
  box(g, 0.1, 0.13, 0.07, M.stone, 0, y0 + 1.16, zf + 0.04); // keystone
  room(g, inner, portal.x0, portal.x1, portal.y0, portal.y1, zf - 0.22, 0.4);
  // recess reveals
  box(g, 0.02, 1.18, 0.22, M.stoneDark, portal.x0 + 0.01, y0, zf - 0.11);
  box(g, 0.02, 1.18, 0.22, M.stoneDark, portal.x1 - 0.01, y0, zf - 0.11);
  box(g, 0.6, 0.02, 0.22, M.stoneDark, 0, y0 + 1.16, zf - 0.11);
  const dz = zf - 0.2;
  mullions(g, M.bronze, portal.x0 + 0.02, portal.x1 - 0.02, y0, y0 + 1.16, dz, {
    vx: [0],
    hy: [y0 + 0.8],
  });
  pane(g, M.doorGlass, portal.x0 + 0.02, portal.x1 - 0.02, y0, y0 + 1.16, dz - 0.006);
  box(g, 0.012, 0.22, 0.02, M.bronze, -0.04, y0 + 0.32, dz + 0.02);
  box(g, 0.012, 0.22, 0.02, M.bronze, 0.04, y0 + 0.32, dz + 0.02);
  // bronze canopy
  box(g, 0.84, 0.03, 0.34, M.bronze, 0, y0 + 1.26, zf + 0.17);
  // display windows
  const mannequinRnd = mulberry32(7);
  for (const win of [winL, winR]) {
    room(g, inner, win.x0, win.x1, win.y0, win.y1, zf - 0.06, 0.42);
    mullions(g, M.bronze, win.x0, win.x1, win.y0, win.y1, zf - 0.035, { t: 0.026 });
    pane(g, M.glass, win.x0, win.x1, win.y0, win.y1, zf - 0.04);
    box(g, win.x1 - win.x0 + 0.06, 0.03, 0.08, M.stoneDark, (win.x0 + win.x1) / 2, win.y0 - 0.03, zf + 0.03);
    for (let k = 0; k < 2; k++) {
      const x = lerp(win.x0, win.x1, 0.32 + k * 0.36);
      const z = zf - 0.24 - mannequinRnd() * 0.08;
      const fig = std(k ? "#e7e1d6" : "#3a3631", 0.6);
      box(g, 0.08, 0.012, 0.08, M.bronze, x, win.y0, z, { cast: false });
      box(g, 0.008, 0.16, 0.008, M.bronze, x, win.y0, z, { cast: false });
      const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.035, 0.24, 4, 10), fig);
      body.position.set(x, win.y0 + 0.36, z);
      g.add(body);
      const head = new THREE.Mesh(new THREE.SphereGeometry(0.028, 12, 8), fig);
      head.position.set(x, win.y0 + 0.55, z);
      g.add(head);
    }
  }
  // upper-storey shadow line + sign
  const sign = makeSign(mask, 1.62, "#1a1714", { depth: 0.026, sideShade: 0.8, rough: 0.007, erode: 0.22 });
  sign.group.position.set(0, y0 + 1.96, zf + 0.008);
  g.add(sign.group);
  // warm uplights washing the sign
  const wash = std("#111", 0.5, 0, { emissive: "#ffe3bd", emissiveIntensity: 0 });
  for (const x of [-0.55, 0, 0.55]) box(g, 0.07, 0.025, 0.05, wash, x, y0 + 1.355, zf + 0.06, { cast: false });
  // rooftop penthouse
  box(g, 1.0, 0.3, 0.62, M.stoneDark, 0.18, y0 + h + 0.08, zb + 0.5);
  box(g, 0.3, 0.12, 0.25, M.hvac, -0.62, y0 + h + 0.08, zb + 0.4);
  return {
    group: g,
    pw: PW,
    pd: PD,
    height: y0 + h + 0.4,
    signs: [sign],
    lights: [inner, wash],
    lightGain: [0.48, 1.6],
  };
}

function buildFootLocker(mask) {
  const g = new THREE.Group();
  const PW = 1.98;
  const PD = 1.85;
  plinth(g, PW, PD, PH);
  const w = 1.72;
  const h = 2.24;
  const d = 1.4;
  const zf = 0.48;
  const zb = zf - d;
  const zc = (zf + zb) / 2;
  const y0 = PH + 0.014;
  const inner = interiorMat("#24272a", "#eef3ff");
  baseAO(g, w + 0.1, d, zc + 0.08, PH + 0.0145);
  box(g, w, h, d - 0.5, M.flBlack, 0, y0, zb + (d - 0.5) / 2);
  box(g, 0.05, h, 0.52, M.flBlack, -w / 2 + 0.025, y0, zf - 0.26);
  box(g, 0.05, h, 0.52, M.flBlack, w / 2 - 0.025, y0, zf - 0.26);
  box(g, w + 0.03, 0.045, d + 0.02, M.roof, 0, y0 + h, zc);
  box(g, w + 0.04, 0.03, 0.04, M.flTrim, 0, y0 + h - 0.01, zf + 0.01);
  // storefront opening inside the striped portal
  const sf = { x0: -0.64, x1: 0.64, y0: y0, y1: y0 + 1.46 };
  wall(g, M.flBlack, -w / 2, w / 2, y0, y0 + h, zf, 0.05, [sf]);
  room(g, inner, sf.x0, sf.x1, sf.y0, sf.y1, zf - 0.05, 0.5);
  mullions(g, M.flTrim, sf.x0, sf.x1, sf.y0, sf.y1, zf - 0.03, {
    vx: [-0.22, 0.22],
    hy: [y0 + 0.84],
    t: 0.024,
  });
  pane(g, M.glass, sf.x0, sf.x1, y0 + 0.84, sf.y1, zf - 0.035);
  pane(g, M.glass, sf.x0, -0.22, y0, y0 + 0.84, zf - 0.035);
  pane(g, M.glass, 0.22, sf.x1, y0, y0 + 0.84, zf - 0.035);
  pane(g, M.doorGlass, -0.22, 0.22, y0, y0 + 0.84, zf - 0.035);
  box(g, 0.012, 0.24, 0.02, M.alu, -0.02, y0 + 0.32, zf - 0.01);
  box(g, 0.012, 0.24, 0.02, M.alu, 0.02, y0 + 0.32, zf - 0.01);
  // wall of kicks
  const kick = mulberry32(5);
  const shelfMat = std("#cfd2d6", 0.5);
  for (let r = 0; r < 4; r++) {
    const y = y0 + 0.34 + r * 0.26;
    box(g, 1.22, 0.012, 0.07, shelfMat, 0, y, zf - 0.5, { cast: false });
    for (let i = 0; i < 7; i++) {
      if (kick() < 0.18) continue;
      const x = -0.5 + i * 0.167;
      const c = ["#efefec", "#efefec", "#e2e2df", "#1e1e1e", "#c9c9c5"][Math.floor(kick() * 5)];
      box(g, 0.1, 0.045, 0.055, std(c, 0.55), x, y + 0.012, zf - 0.5, { cast: false });
    }
  }
  box(g, 0.5, 0.1, 0.18, std("#e7e7e4", 0.6), 0, y0, zf - 0.3, { cast: false });
  // referee-stripe portal: jambs + header, projecting from the facade
  const jd = 0.16;
  const jw = 0.2;
  const jh = 1.58;
  for (const s of [-1, 1]) {
    const x = s * (w / 2 - jw / 2 + 0.01);
    box(g, jw, jh, jd, M.flBlack, x, y0, zf + jd / 2 - 0.01);
    const front = new THREE.Mesh(new THREE.PlaneGeometry(jw, jh), M.stripes.clone());
    front.material.map = stripeTex.clone();
    front.material.map.repeat.set(4, 1);
    front.material.map.needsUpdate = true;
    front.position.set(x, y0 + jh / 2, zf + jd - 0.008);
    front.receiveShadow = true;
    g.add(front);
    const side = new THREE.Mesh(new THREE.PlaneGeometry(jd, jh), M.stripes.clone());
    side.material.map = stripeTex.clone();
    side.material.map.repeat.set(3, 1);
    side.material.map.needsUpdate = true;
    side.rotation.y = s < 0 ? Math.PI / 2 : -Math.PI / 2;
    side.position.set(x - s * (jw / 2 + 0.001), y0 + jh / 2, zf + jd / 2 - 0.01);
    side.receiveShadow = true;
    g.add(side);
  }
  // sign band header
  const hb = { y0: y0 + jh, h: 0.5 };
  box(g, w + 0.03, hb.h, jd + 0.01, M.flBlack, 0, hb.y0, zf + jd / 2 - 0.005);
  box(g, w + 0.035, 0.014, jd + 0.02, std("#e9e8e3", 0.6), 0, hb.y0 - 0.007, zf + jd / 2 - 0.005);
  const sign = makeSign(mask, 1.5, INK, { depth: 0.026 });
  sign.group.position.set(0, hb.y0 + hb.h / 2, zf + jd + 0.002);
  g.add(sign.group);
  // rooftop
  box(g, 0.42, 0.14, 0.32, M.hvac, 0.28, y0 + h + 0.045, zb + 0.4);
  box(g, 0.18, 0.2, 0.18, M.hvac, -0.45, y0 + h + 0.045, zb + 0.3);
  return {
    group: g,
    pw: PW,
    pd: PD,
    height: y0 + h + 0.25,
    signs: [sign],
    lights: [inner],
    lightGain: [0.32],
  };
}

// ---------------------------------------------------------------- pop-up motion
function cubicBezier(x1, y1, x2, y2) {
  const bx = (t) => 3 * (1 - t) * (1 - t) * t * x1 + 3 * (1 - t) * t * t * x2 + t * t * t;
  const dbx = (t) => 3 * (1 - t) * (1 - t) * x1 + 6 * (1 - t) * t * (x2 - x1) + 3 * t * t * (1 - x2);
  const by = (t) => 3 * (1 - t) * (1 - t) * t * y1 + 3 * (1 - t) * t * t * y2 + t * t * t;
  return (x) => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 10; i++) {
      const e = bx(t) - x;
      const d = dbx(t);
      if (Math.abs(e) < 1e-7 || Math.abs(d) < 1e-7) break;
      t = clamp(t - e / d);
    }
    return by(t);
  };
}

// Lowest point of the building follows: slow start under the floor → accelerating rise → long ease into an overshoot
// above the floor → gravity drop → small bounce → rest. Tilt rocks on the low edge.
function makePop(o) {
  const yStart = -o.depth;
  const tApex = o.t0 + o.tUp;
  const tf = Math.sqrt((2 * o.apex) / o.g);
  const tImpact = tApex + tf;
  const vi = o.g * tf;
  const v1 = o.e * vi;
  const tImpact2 = tImpact + (2 * v1) / o.g;
  const v2 = o.e * v1;
  const tImpact3 = tImpact2 + (2 * v2) / o.g;
  const riseEase = cubicBezier(...(o.rise || [0.42, 0, 0.16, 1]));

  function ylow(t) {
    if (t <= o.t0) return yStart;
    if (t <= tApex) {
      const s = (t - o.t0) / o.tUp;
      return yStart + (o.apex - yStart) * riseEase(s);
    }
    if (t <= tImpact) {
      const u = t - tApex;
      return o.apex - 0.5 * o.g * u * u;
    }
    if (t <= tImpact2) {
      const u = t - tImpact;
      return v1 * u - 0.5 * o.g * u * u;
    }
    if (t <= tImpact3) {
      const u = t - tImpact2;
      return v2 * u - 0.5 * o.g * u * u;
    }
    return 0;
  }
  function tilt(t) {
    if (t <= tImpact) return o.tilt * smooth(tApex - 0.22, tApex + 0.02, t);
    const u = t - tImpact;
    return o.tilt * Math.exp(-u / 0.1) * Math.cos(2 * Math.PI * 3.3 * u);
  }
  function yaw(t) {
    if (t <= o.t0) return o.yaw;
    const s = clamp((t - o.t0) / (o.tUp + 0.05));
    return o.yaw * Math.pow(1 - s, 3);
  }
  function squash(t) {
    let s = 0;
    for (const [ti, v] of [
      [tImpact, vi],
      [tImpact2, v1],
    ]) {
      if (t < ti) continue;
      const u = t - ti;
      const amp = Math.min(0.03, v * 0.0085);
      s += amp * Math.sin(2 * Math.PI * 4.6 * u) * Math.exp(-u / 0.085);
    }
    // stretch while shooting up
    if (t > o.t0 && t < tApex) {
      const s01 = (t - o.t0) / o.tUp;
      s -= 0.022 * Math.pow(1 - s01, 2);
    }
    return s;
  }
  // 0 → 1 "lights on" flicker after landing
  function lights(t, delay = 0.04) {
    const u = t - tImpact - delay;
    if (u <= 0) return 0;
    const keys = [
      [0, 0],
      [0.03, 0.75],
      [0.07, 0.12],
      [0.1, 0.9],
      [0.14, 0.55],
      [0.22, 1],
    ];
    if (u >= 0.22) return 1;
    for (let i = 0; i < keys.length - 1; i++)
      if (u < keys[i + 1][0]) return lerp(keys[i][1], keys[i + 1][1], (u - keys[i][0]) / (keys[i + 1][0] - keys[i][0]));
    return 1;
  }
  function glitch(t) {
    const u = t - tImpact + 0.03;
    if (u < 0) return 0;
    return Math.exp(-u / 0.11) * (0.6 + 0.4 * Math.cos(u * 70));
  }
  function state(t) {
    const th = tilt(t);
    const yl = ylow(t);
    const yb = yl + (o.halfW * Math.abs(Math.sin(th)) || 0);
    const sq = squash(t);
    return { yb, th, yaw: yaw(t), sy: 1 - sq, sxz: 1 + sq * 0.45 };
  }
  return { state, ylow, lights, glitch, tApex, tImpact, tEnd: tImpact3 + 0.35, o };
}

// ---------------------------------------------------------------- set dressing
const floorFade = { uCenter: { value: new THREE.Vector2(0, 0.2) }, uR: { value: new THREE.Vector2(2.4, 8.2) } };
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(90, 90),
  new THREE.MeshStandardMaterial({ color: "#222222", roughness: 0.96, metalness: 0 }),
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
floor.material.onBeforeCompile = (shader) => {
  shader.uniforms.uCenter = floorFade.uCenter;
  shader.uniforms.uR = floorFade.uR;
  shader.uniforms.uBg = { value: new THREE.Vector3(bgColor.r, bgColor.g, bgColor.b) };
  shader.vertexShader = shader.vertexShader
    .replace("#include <common>", "#include <common>\nvarying vec3 vFloorW;")
    .replace(
      "#include <project_vertex>",
      "#include <project_vertex>\nvFloorW = (modelMatrix * vec4(transformed, 1.0)).xyz;",
    );
  shader.fragmentShader = shader.fragmentShader
    .replace(
      "#include <common>",
      "#include <common>\nvarying vec3 vFloorW; uniform vec2 uCenter; uniform vec2 uR; uniform vec3 uBg;",
    )
    .replace(
      "#include <dithering_fragment>",
      `#include <dithering_fragment>
       vec2 dd = (vFloorW.xz - uCenter) * vec2(0.62, 1.0);
       float fade = smoothstep(uR.x, uR.y, length(dd));
       gl_FragColor.rgb = mix(gl_FragColor.rgb, uBg, fade);`,
    );
};
scene.add(floor);

// lights
const key = new THREE.DirectionalLight("#ffead4", 3.2);
key.position.set(-5.5, 9.5, 7.5);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -6.5, right: 6.5, top: 6.5, bottom: -6.5, near: 2, far: 30 });
key.shadow.bias = -0.0005;
key.shadow.normalBias = 0.018;
scene.add(key);
scene.add(key.target);
const rim = new THREE.DirectionalLight("#cddcf5", 2.4);
rim.position.set(2.2, 6.5, -9);
scene.add(rim);
const fill = new THREE.DirectionalLight("#e8eef7", 0.2);
fill.position.set(6, 3, 8);
scene.add(fill);
scene.add(new THREE.HemisphereLight("#dfe3e8", "#15120e", 0.26));

// ---------------------------------------------------------------- swoosh material
const SWOOSH_FRAG = /* glsl */ `
  uniform sampler2D uMask; uniform sampler2D uNoise;
  uniform vec3 uColor; uniform float uReveal, uOut, uSeed, uAspect, uTime;
  varying vec2 vUv;
  ${NOISE_GLSL}
  void main(){
    vec2 uv = vUv;
    vec2 q = vec2(uv.x * uAspect, uv.y);
    // displacement map drives the reveal: a noisy front sweeps along the stroke (tail → tip)
    float n = texture2D(uNoise, q * 0.42 + vec2(0.0, uTime * 0.05)).r;
    float front = mix(-0.25, 1.25, uReveal);
    float edge = uv.x + (n - 0.5) * 0.34;
    float near = 1.0 - smoothstep(0.0, 0.16, abs(edge - front));
    uv += vec2(-(n - 0.5) * 0.05, (n - 0.5) * 0.16) * near;
    // turbulent displace: always a little, a lot as it leaves
    vec2 tw = vec2(fbm(q * 5.0 + uTime * 0.9), fbm(q * 5.0 + 9.4 - uTime * 0.7)) - 0.5;
    uv += tw * (0.007 + 0.11 * uOut * uOut);
    uv.y -= uOut * 0.05;
    float m = texture2D(uMask, uv).a;
    float g = hash12(floor(gl_FragCoord.xy / 1.5) + floor(uSeed) * 5.7);
    float thr = 0.5 + (g - 0.5) * 0.4;
    float a = smoothstep(thr - 0.08, thr + 0.08, m);
    a *= 1.0 - smoothstep(front - 0.03, front + 0.03, edge);
    // leave through the same map: pixels dissolve from the noise's low values up
    float n2 = texture2D(uNoise, q * 0.9 + 3.7).r;
    a *= smoothstep(uOut * 1.2 - 0.3, uOut * 1.2 + 0.05, n2 * 0.75 + 0.2);
    a *= 1.0 - smoothstep(0.25, 1.0, uOut);
    float grain = 0.8 + 0.2 * hash12(floor(gl_FragCoord.xy / 1.5) + floor(uSeed) * 2.9 + 4.0);
    gl_FragColor = vec4(uColor * grain, a);
  }
`;
const GLOW_FRAG = /* glsl */ `
  uniform sampler2D uMask; uniform vec3 uColor; uniform float uAmt;
  varying vec2 vUv;
  void main(){ float m = texture2D(uMask, vUv).a; gl_FragColor = vec4(uColor * m * uAmt, 1.0); }
`;

// ---------------------------------------------------------------- plot outlines (floor plan)
const PLOT_FRAG = /* glsl */ `
  uniform vec2 uSize; uniform vec2 uHalf; uniform float uProg, uAlpha, uSeed; uniform vec3 uColor;
  varying vec2 vUv;
  ${NOISE_GLSL}
  void main(){
    vec2 p = (vUv - 0.5) * uSize;
    vec2 q = abs(p) - uHalf;
    float dist = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
    float lw = 0.007;
    float line = 1.0 - smoothstep(lw, lw + 0.006, abs(dist));
    float ext = 0.17;
    float tickA = (1.0 - smoothstep(lw, lw + 0.006, abs(abs(p.y) - uHalf.y))) * step(uHalf.x, abs(p.x)) * (1.0 - step(uHalf.x + ext, abs(p.x)));
    float tickB = (1.0 - smoothstep(lw, lw + 0.006, abs(abs(p.x) - uHalf.x))) * step(uHalf.y, abs(p.y)) * (1.0 - step(uHalf.y + ext, abs(p.y)));
    float ang = fract(atan(p.x, -p.y) / 6.2831853 + 0.5);
    float drawn = 1.0 - smoothstep(uProg - 0.01, uProg + 0.01, ang);
    float a = max(line, max(tickA, tickB)) * drawn;
    a *= 0.75 + 0.25 * hash12(floor(gl_FragCoord.xy / 1.5) + floor(uSeed));
    gl_FragColor = vec4(uColor, a * uAlpha);
  }
`;

// ---------------------------------------------------------------- post: turbulent displace + motion blur + grade + grain
const POST_FRAG = /* glsl */ `
  uniform sampler2D tScene;
  uniform vec2 uRes; uniform float uSeed, uTime, uExposure;
  uniform vec3 uBg;
  uniform float uFocusY, uDofPx;
  uniform vec4 zRect[3];  // building bbox in uv (x0, y0, x1, y1)
  uniform vec4 zFoot[3];  // footprint ellipse: centre.xy, radii.xy (uv)
  uniform vec4 zData[3];  // x: turbulence amp, y: vertical blur length, z: ring radius, w: ring amp
  varying vec2 vUv;
  ${NOISE_GLSL}
  vec3 shoulder(vec3 x){ vec3 k = vec3(0.72); return mix(x, k + (1.0 - k) * (1.0 - exp(-(x - k) / (1.0 - k))), step(k, x)); }
  vec3 toSRGB(vec3 c){ c = max(c, 0.0); return mix(c * 12.92, 1.055 * pow(c, vec3(1.0/2.4)) - 0.055, step(0.0031308, c)); }
  void main(){
    vec2 uv = vUv;
    float aspect = uRes.x / uRes.y;
    vec2 off = vec2(0.0);
    float blurLen = 0.0;
    for (int i = 0; i < 3; i++){
      vec4 r = zRect[i];
      vec4 dta = zData[i];
      if (dta.x > 0.00001 || dta.y > 0.00001){
        float mx = smoothstep(r.x, r.x + 0.008, uv.x) * (1.0 - smoothstep(r.z - 0.008, r.z + 0.01, uv.x));
        float my = smoothstep(r.y - 0.03, r.y + 0.005, uv.y) * (1.0 - smoothstep(r.w - 0.005, r.w + 0.03, uv.y));
        float mask = mx * my;
        if (mask > 0.001){
          vec2 p = vec2(uv.x * aspect, uv.y) * 7.0;
          vec2 tw = vec2(fbm(p + uTime * 2.1), fbm(p + 13.7 - uTime * 1.7)) - 0.5;
          off += tw * dta.x * mask;
          blurLen = max(blurLen, dta.y * mask);
        }
      }
      if (dta.w > 0.00001){
        vec4 f = zFoot[i];
        vec2 dv = (uv - f.xy) / f.zw;
        float rr = length(dv);
        float ring = exp(-pow((rr - dta.z) / 0.22, 2.0)) * dta.w;
        if (ring > 0.00001){
          vec2 p2 = vec2(uv.x * aspect, uv.y) * 16.0;
          vec2 tw2 = vec2(fbm(p2 + 5.1 + uTime * 3.0), fbm(p2 - 9.2 - uTime * 2.6)) - 0.5;
          off += (tw2 * 1.4 + normalize(dv + 1e-5) * vec2(1.0, 0.6) * 0.35) * ring;
        }
      }
    }
    vec3 col;
    if (blurLen > 0.0008){
      col = vec3(0.0);
      for (int k = 0; k < 16; k++){
        float s = (float(k) / 15.0 - 0.5) * blurLen;
        col += texture2D(tScene, uv + off + vec2(0.0, s)).rgb;
      }
      col /= 16.0;
    } else {
      col = texture2D(tScene, uv + off).rgb;
    }
    float dof = clamp((uFocusY - uv.y) / 0.22, 0.0, 1.0);
    dof = dof * dof * uDofPx;
    if (dof > 0.6 && blurLen <= 0.0008){
      vec3 acc = col;
      float wsum = 1.0;
      for (int k = 0; k < 12; k++){
        float fk = float(k);
        float rr = sqrt((fk + 0.5) / 12.0) * dof;
        float th = fk * 2.39996 + hash12(gl_FragCoord.xy) * 6.283;
        vec2 o2 = vec2(cos(th), sin(th)) * rr / uRes;
        acc += texture2D(tScene, uv + off + o2).rgb;
        wsum += 1.0;
      }
      col = acc / wsum;
    }
    // exposure + vignette act on the image above the ground colour, so the ground stays exact
    vec2 vc = (uv - 0.5) * vec2(aspect, 1.0);
    float vig = 1.0 - 0.28 * smoothstep(0.25, 0.95, length(vc) * 1.35);
    col = uBg + (col - uBg) * uExposure * vig;
    col = shoulder(col);
    // restrained split tone: cool shadows, warm highlights (lifted only above the ground level)
    float lum = dot(col, vec3(0.2126, 0.7152, 0.0722));
    vec3 tint = mix(vec3(0.985, 1.0, 1.025), vec3(1.03, 1.0, 0.965), smoothstep(0.03, 0.5, lum));
    col = mix(col, col * tint, smoothstep(0.008, 0.03, lum));
    vec3 s = toSRGB(col);
    // grain: barely in the blacks, more in mids and highs (the reel's type texture)
    float sl = dot(s, vec3(0.333));
    float gn = hash12(floor(gl_FragCoord.xy / 1.25) + uSeed * 17.0) - 0.5;
    s += gn * (0.006 + 0.07 * smoothstep(0.08, 0.7, sl));
    gl_FragColor = vec4(s, 1.0);
  }
`;

// ---------------------------------------------------------------- build
async function build() {
  const [dswMask, dillMask, flMask, nikeMask] = await Promise.all([
    logoMask("assets/logos/dsw.png", { width: 1600, crop: [40, 4, 709, 255] }),
    logoMask("assets/logos/dillards.svg", { width: 2400 }),
    logoMask("assets/logos/footlocker.svg", { width: 2600, crop: [0, 0, 182, 29] }),
    logoMask("assets/logos/nike-swoosh.svg", { width: 1600, pad: 0.14 }),
  ]);

  // layout: three plinths in a row, gaps of ~0.3
  const defs = [
    { name: "dsw", build: () => buildDSW(dswMask), x: -2.52, z: 0.08 },
    { name: "dill", build: () => buildDillards(dillMask), x: 0, z: -0.12 },
    { name: "fl", build: () => buildFootLocker(flMask), x: 2.45, z: 0.12 },
  ];
  const pops = [
    // weight differences: Dillard's is the heaviest (lower hop, less bounce, slower)
    { t0: T.dsw, tUp: 0.5, apex: 0.26, g: 30, e: 0.3, tilt: 1.7 * DEG, yaw: -5 * DEG, rise: [0.42, 0, 0.16, 1] },
    { t0: T.dill, tUp: 0.53, apex: 0.19, g: 34, e: 0.22, tilt: -1.2 * DEG, yaw: 4 * DEG, rise: [0.5, 0, 0.2, 1] },
    { t0: T.fl, tUp: 0.47, apex: 0.3, g: 29, e: 0.34, tilt: 2.0 * DEG, yaw: -6 * DEG, rise: [0.36, 0, 0.14, 1] },
  ];
  const stores = defs.map((def, i) => {
    const s = def.build();
    // rest-pose bounds (local) for the screen-space effect zones; the soft AO quads are
    // mostly transparent margin, so they stay out of the bounds
    s.group.updateMatrixWorld(true);
    s.localBox = new THREE.Box3();
    s.group.traverse((o) => {
      if (!o.isMesh || o.material === aoMat) return;
      if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
      s.localBox.union(o.geometry.boundingBox.clone().applyMatrix4(o.matrixWorld));
    });
    const mover = new THREE.Group();
    mover.position.set(def.x, 0, def.z);
    const squashG = new THREE.Group();
    squashG.add(s.group);
    mover.add(squashG);
    scene.add(mover);
    s.mover = mover;
    s.squash = squashG;
    s.x = def.x;
    s.z = def.z;
    s.pop = makePop({ ...pops[i], depth: s.height + 0.06, halfW: s.pw / 2 });
    // contact shadow
    const cs = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1),
      new THREE.MeshBasicMaterial({
        color: "#000000",
        alphaMap: softRect,
        transparent: true,
        depthWrite: false,
        opacity: 0,
      }),
    );
    cs.rotation.x = -Math.PI / 2;
    cs.position.set(def.x, 0.002, def.z);
    cs.renderOrder = 1;
    scene.add(cs);
    s.contact = cs;
    // floor plan outline
    const margin = 0.36;
    const size = new THREE.Vector2(s.pw + margin * 2, s.pd + margin * 2);
    const pm = new THREE.ShaderMaterial({
      uniforms: {
        uSize: { value: size },
        uHalf: { value: new THREE.Vector2(s.pw / 2 + 0.05, s.pd / 2 + 0.05) },
        uProg: { value: 0 },
        uAlpha: { value: 0 },
        uSeed: globalU.uSeed,
        uColor: { value: new THREE.Color(INK) },
      },
      vertexShader: BASIC_VERT,
      fragmentShader: PLOT_FRAG,
      transparent: true,
      depthWrite: false,
    });
    const plot = new THREE.Mesh(new THREE.PlaneGeometry(size.x, size.y), pm);
    plot.rotation.x = -Math.PI / 2;
    plot.position.set(def.x, 0.003, def.z);
    plot.renderOrder = 1;
    scene.add(plot);
    s.plot = pm;
    return s;
  });

  // swoosh, floating above the row
  const swooshW = 1.45;
  const swH = swooshW / nikeMask.aspect;
  const swU = {
    uMask: { value: nikeMask.tex },
    uNoise: { value: noiseTex },
    uColor: { value: new THREE.Color(ACCENT) },
    uReveal: { value: 0 },
    uOut: { value: 0 },
    uSeed: globalU.uSeed,
    uTime: globalU.uTime,
    uAspect: { value: nikeMask.aspect },
  };
  const swoosh = new THREE.Mesh(
    new THREE.PlaneGeometry(swooshW, swH),
    new THREE.ShaderMaterial({
      uniforms: swU,
      vertexShader: BASIC_VERT,
      fragmentShader: SWOOSH_FRAG,
      transparent: true,
      depthWrite: false,
    }),
  );
  swoosh.renderOrder = 5;
  const glowU = {
    uMask: { value: blurredCopy(nikeMask.canvas, 34) },
    uColor: { value: new THREE.Color(ACCENT) },
    uAmt: { value: 0 },
  };
  const glow = new THREE.Mesh(
    new THREE.PlaneGeometry(swooshW * 1.02, swH * 1.02),
    new THREE.ShaderMaterial({
      uniforms: glowU,
      vertexShader: BASIC_VERT,
      fragmentShader: GLOW_FRAG,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  glow.renderOrder = 4;
  const swooshG = new THREE.Group();
  swooshG.add(glow);
  swooshG.add(swoosh);
  glow.position.z = -0.01;
  scene.add(swooshG);
  const swooshBase = new THREE.Vector3(-0.05, 3.72, -0.1);

  // ---------------------------------------------------------------- camera
  const aspect = W / H;
  const camera = new THREE.PerspectiveCamera(24, aspect, 0.5, 120);
  // 16:9: starts close on the DSW plot, trucks right as each store arrives (all three framed
  // before Foot Locker breaks the floor), then a slow pull back and crane up for the reveal.
  const CAM = {
    tx: track([[0, -1.6], [1.55, -1.08], [2.55, -0.1], [6.5, -0.02]], 0.25, 0.0),
    ty: track([[0, 1.05], [1.55, 1.38], [2.55, 1.42], [6.5, 1.5]], 0.1, 0.0),
    dist: track([[0, 7.7], [1.55, 9.3], [2.55, 11.3], [6.5, 14.7]], 0.75, 0.18),
    yaw: track([[0, 25], [6.5, 15.5]], -1.6, -1.2),
    pitch: track([[0, 17], [2.55, 18], [6.5, 20]], 0.35, 0.3),
  };
  const tgt = new THREE.Vector3();
  function placeCamera(t) {
    tgt.set(CAM.tx(t), CAM.ty(t), 0);
    const yaw = CAM.yaw(t) * DEG;
    const pitch = CAM.pitch(t) * DEG;
    const dist = CAM.dist(t);
    camera.position.set(
      tgt.x + dist * Math.sin(yaw) * Math.cos(pitch),
      tgt.y + dist * Math.sin(pitch),
      tgt.z + dist * Math.cos(yaw) * Math.cos(pitch),
    );
    camera.lookAt(tgt);
    camera.updateMatrixWorld();
  }

  // ---------------------------------------------------------------- post pass
  const postU = {
    tScene: { value: sceneRT.texture },
    uRes: { value: new THREE.Vector2(W, H) },
    uSeed: { value: 0 },
    uTime: { value: 0 },
    uExposure: { value: 1.0 },
    uFocusY: { value: 0.3 },
    uDofPx: { value: 6.0 },
    uBg: { value: new THREE.Vector3(bgColor.r, bgColor.g, bgColor.b) },
    zRect: { value: [new THREE.Vector4(), new THREE.Vector4(), new THREE.Vector4()] },
    zFoot: { value: [new THREE.Vector4(), new THREE.Vector4(), new THREE.Vector4()] },
    zData: { value: [new THREE.Vector4(), new THREE.Vector4(), new THREE.Vector4()] },
  };
  const postGeo = new THREE.BufferGeometry();
  postGeo.setAttribute("position", new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
  const post = new THREE.Mesh(
    postGeo,
    new THREE.ShaderMaterial({
      uniforms: postU,
      vertexShader: "varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }",
      fragmentShader: POST_FRAG,
      depthTest: false,
      depthWrite: false,
    }),
  );
  post.frustumCulled = false;
  const postScene = new THREE.Scene();
  postScene.add(post);
  const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  // ---------------------------------------------------------------- per-frame
  const v3 = new THREE.Vector3();
  const corners = Array.from({ length: 8 }, () => new THREE.Vector3());
  const toUV = (v) => {
    v3.copy(v).project(camera);
    return [v3.x * 0.5 + 0.5, v3.y * 0.5 + 0.5];
  };

  function poseStore(s, t) {
    const st = s.pop.state(t);
    s.mover.position.y = st.yb;
    s.mover.rotation.set(0, st.yaw, st.th);
    s.squash.scale.set(st.sxz, st.sy, st.sxz);
    s.mover.visible = st.yb + s.height > -0.01;
    return st;
  }

  function zonesFor(s, i, t) {
    const st = poseStore(s, t);
    s.mover.updateMatrixWorld(true);
    // bbox of the part above the floor
    const b = s.localBox;
    let k = 0;
    for (const x of [b.min.x, b.max.x])
      for (const y of [b.min.y, b.max.y])
        for (const z of [b.min.z, b.max.z]) corners[k++].set(x, y, z).applyMatrix4(s.group.matrixWorld);
    let x0 = 1e9;
    let y0 = 1e9;
    let x1 = -1e9;
    let y1 = -1e9;
    // corners are ordered x-major, then y, then z: indices 1 and 3 are the front-left ones
    corners.forEach((c, ci) => {
      c.y = Math.max(0, c.y);
      const [u, v] = toUV(c);
      // the camera sits right of centre, so a store's visible left edge is its front-left edge;
      // the hidden back-left corners would push the zone over the neighbour on the left
      if (ci >= 4 || ci === 1 || ci === 3) x0 = Math.min(x0, u);
      x1 = Math.max(x1, u);
      y0 = Math.min(y0, v);
      y1 = Math.max(y1, v);
    });
    postU.zRect.value[i].set(x0, y0, x1, y1);
    // screen velocity from the roof point one frame apart
    const roof = new THREE.Vector3(s.x, st.yb + s.height, s.z);
    const prevSt = s.pop.state(t - 1 / FPS);
    const roofPrev = new THREE.Vector3(s.x, prevSt.yb + s.height, s.z);
    const [, va] = toUV(roof);
    const [, vb] = toUV(roofPrev);
    const above = st.yb + s.height > 0.02;
    const speed = above ? Math.abs(va - vb) : 0;
    const turb = Math.min(0.0022, speed * 0.05);
    const blur = Math.min(0.03, speed * 0.42);
    // footprint ellipse
    let fx0 = 1e9;
    let fy0 = 1e9;
    let fx1 = -1e9;
    let fy1 = -1e9;
    for (const [dx, dz] of [
      [-1, -1],
      [1, -1],
      [-1, 1],
      [1, 1],
    ]) {
      const [u, v] = toUV(new THREE.Vector3(s.x + (dx * s.pw) / 2, 0, s.z + (dz * s.pd) / 2));
      fx0 = Math.min(fx0, u);
      fx1 = Math.max(fx1, u);
      fy0 = Math.min(fy0, v);
      fy1 = Math.max(fy1, v);
    }
    postU.zFoot.value[i].set((fx0 + fx1) / 2, (fy0 + fy1) / 2, (fx1 - fx0) / 2 * 1.08, (fy1 - fy0) / 2 * 1.25);
    // ring: churn while breaking through, then an expanding ripple on impact
    const o = s.pop.o;
    let ringR = 1.0;
    let ringA = 0;
    const tBreak = o.t0; // roof meets the floor almost immediately
    const tClear = (() => {
      // when the plinth's underside clears the floor (ylow crosses 0 on the way up)
      let lo = o.t0;
      let hi = s.pop.tApex;
      for (let n = 0; n < 24; n++) {
        const mid = (lo + hi) / 2;
        if (s.pop.ylow(mid) < 0) lo = mid;
        else hi = mid;
      }
      return hi;
    })();
    if (t >= tBreak && t < tClear + 0.12) {
      ringR = 1.02;
      ringA = 0.0042 * smooth(tBreak - 0.02, tBreak + 0.05, t) * (1 - smooth(tClear - 0.02, tClear + 0.12, t));
    }
    const ti = s.pop.tImpact;
    if (t >= ti - 0.01) {
      const u = Math.max(0, t - ti);
      const r2 = 1.0 + 1.25 * (1 - Math.exp(-u / 0.16));
      const a2 = 0.0048 * Math.exp(-u / 0.17) * smooth(ti - 0.01, ti + 0.02, t);
      if (a2 > ringA) {
        ringR = r2;
        ringA = a2;
      }
    }
    postU.zData.value[i].set(turb, blur, ringR, ringA);
    return st;
  }

  host.render = (tRaw) => {
    const t = clamp(tRaw, 0, host.duration);
    const frame = Math.round(t * FPS);
    globalU.uSeed.value = Math.floor(frame / 2); // boil on twos
    globalU.uTime.value = t;
    postU.uSeed.value = frame % 97;
    postU.uTime.value = t;
    placeCamera(t);
    scene.environmentRotation.y = (-35 + t * 9) * DEG;

    stores.forEach((s, i) => {
      const st = zonesFor(s, i, t);
      // contact shadow: tight and dark on the floor, soft and faint when airborne
      const hgt = Math.max(0, st.yb);
      const spread = 1 + hgt * 0.9 + Math.abs(st.th) * 3;
      const visible = st.yb + s.height > 0;
      s.contact.material.opacity = visible ? 0.78 * (1 - smooth(0, 0.42, hgt)) + 0.12 : 0;
      s.contact.scale.set((s.pw + 0.55) * spread, (s.pd + 0.55) * spread, 1);
      s.contact.position.x = s.x + st.yb * 0.0;
      // lights on after landing
      const L = s.pop.lights(t);
      s.lights.forEach((m, k) => {
        m.emissiveIntensity = s.lightGain[k] * L;
      });
      for (const sign of s.signs) {
        sign.u.uBright.value = lerp(0.62, 1.08, s.pop.lights(t, 0.0));
        sign.u.uGlitch.value = s.pop.glitch(t);
      }
      // plot outline: draws on, then fades once the store has settled
      const tp = T.plots[i];
      s.plot.uniforms.uProg.value = smooth(tp, tp + 0.55, t) * 1.02;
      s.plot.uniforms.uAlpha.value = 0.34 * smooth(tp, tp + 0.08, t) * (1 - smooth(s.pop.tImpact + 0.25, s.pop.tImpact + 0.9, t));
    });

    // swoosh
    const rev = smooth(T.swooshIn, T.swooshHold, t);
    const out = smooth(T.swooshOut, T.swooshGone, t);
    swU.uReveal.value = rev;
    swU.uOut.value = out;
    glowU.uAmt.value = 0.22 * smooth(T.swooshIn + 0.25, T.swooshHold + 0.1, t) * (1 - smooth(T.swooshOut, T.swooshOut + 0.45, t));
    swooshG.visible = t > T.swooshIn - 0.05 && t < T.swooshGone + 0.05;
    const rise = (1 - Math.pow(1 - smooth(T.swooshIn - 0.1, T.swooshHold + 0.3, t), 2)) * 0.12 + out * 0.14;
    swooshG.position.set(swooshBase.x, swooshBase.y - 0.12 + rise, swooshBase.z);
    swooshG.quaternion.copy(camera.quaternion);

    // focus line just under the lowest landed plinth front edge
    let fy = 1;
    stores.forEach((s, i) => {
      const f = postU.zFoot.value[i];
      fy = Math.min(fy, f.y - f.w * 1.1);
    });
    postU.uFocusY.value = fy - 0.015;

    renderer.setRenderTarget(sceneRT);
    renderer.render(scene, camera);
    renderer.setRenderTarget(null);
    renderer.render(postScene, postCam);
  };

  placeCamera(0);
  await renderer.compileAsync(scene, camera);
  await renderer.compileAsync(postScene, postCam);
  host.render(host.clock.t);
  // read one pixel so a software GPU finishes the first (slowest) frame inside setup
  const px = new Uint8Array(4);
  const gl = renderer.getContext();
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  host.debug = { stores, camera, CAM, T, postU };
}

build()
  .then(() => host.ready())
  .catch((err) => {
    console.error("[retail-popup] build failed", err);
    host.fail(err);
  });
