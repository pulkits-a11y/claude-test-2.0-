window.RCK = window.RCK || {}; RCK.FPS = 30; RCK.f = RCK.f || (n => n / 30); RCK.rng = RCK.rng || function (seed) { return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };

/* RC_GTA-Origin style kit: MOTIFS (motifs.js). Docs, markup and timing: KIT_motifs.md.
   M1 wanted stars, M2 "you" arrow, M3 calendar grid (= L9 calendar counter), M4 bug chip,
   L8 CRT screen insert (fit + grading values + flicker), Windows 95-style error box (B2),
   CANCELLED stamp (B7), camera shake.

   Conventions (kit-wide):
   - Timeline helpers are pure: helper(tl, target, atSeconds, opts) -> endSeconds. They only add
     tweens/sets to the caller's paused GSAP timeline. Init helpers (xxxInit) build child markup and
     set the resting state once (idempotent); every timeline helper calls its init itself.
   - All times are snapped to the 30 fps frame grid (nearest frame). Hard changes are tl.set()
     placed 0.1 ms before their frame so the HyperFrames seek (floor(t*30)/30) always includes them.
   - Deterministic: no Date.now(), no Math.random() (RCK.rng(seed)), no timers, no repeat:-1.
   - Never animates a .clip itself: put class="clip" on the outer element, the helpers animate children
     (stamp/chip/shake containers are documented in KIT_motifs.md).
   - v02 (REVISION_v02 rule C): every move is eased (stars / arrow / chip / stamp were already eased; the counter roll is
     now power1.inOut = easeInOutQuad, "number rolls, counters"); fills, blinks, flicker and shake are hard per-frame
     changes (cuts, not moves). New: calendarIn (B12 note 6, the calendar's opening animation). Fonts: Coolvetica. */
(function () {
  "use strict";

  var FPS = 30;
  var F = 1 / FPS;
  var EPS = 1e-4;
  var SVGNS = "http://www.w3.org/2000/svg";

  /* ---------------------------------------------------------------- utilities */
  function $(t) {
    if (!t) throw new Error("RCK.motifs: missing target");
    if (typeof t === "string") {
      var e = document.querySelector(t);
      if (!e) throw new Error("RCK.motifs: no element matches " + t);
      return e;
    }
    if (t.jquery) return t[0];
    return t;
  }
  function frameOf(t) { return Math.round(t * FPS + 1e-6); }        // nearest frame index
  function tF(k) { return k / FPS; }                                 // frame index -> seconds
  function setAt(k) { return Math.max(0, k / FPS - EPS); }           // hard change lands ON frame k
  function pick() { for (var i = 0; i < arguments.length; i++) { var v = arguments[i]; if (v !== undefined && v !== null && v !== "") return v; } return undefined; }
  function num() { var v = pick.apply(null, arguments); return v === undefined ? undefined : Number(v); }
  function round2(v) { return Math.round(v * 100) / 100; }
  // easings.net name ('easeOutExpo') or GSAP name -> GSAP ease; 'none' / 'linear' are refused (rule C) -> dflt
  function easeOf(e, dflt) {
    if (e === undefined || e === null || e === "") e = dflt;
    if (typeof e === "function") return e;
    if (/^(none|linear|power0(\.\w+)?)$/i.test(String(e).trim())) { if (window.console) console.warn("RCK.motifs: ease \"" + e + "\" is linear (REVISION_v02 rule C), using " + dflt); e = dflt; }
    if (window.RCK && RCK.ease && RCK.ease.gsap) return RCK.ease.gsap(e);
    return e;
  }
  function svgEl(tag, attrs) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) e.setAttribute(k, attrs[k]);
    return e;
  }

  /* Shared SVG defs (the stamp's rough-edged mask). Injected once into <body>. */
  var DEFS_ID = "rcm-defs";
  function ensureDefs() {
    if (document.getElementById(DEFS_ID)) return;
    var svg = svgEl("svg", { id: DEFS_ID, width: "0", height: "0", "aria-hidden": "true", focusable: "false" });
    svg.setAttribute("style", "position:absolute;width:0;height:0;overflow:hidden;pointer-events:none");
    svg.setAttribute("data-layout-ignore", "");
    /* Rough-edged rubber-stamp mask, fixed seeds (identical every frame and every render):
       1) low-frequency noise displaces the glyph and border edges by up to +/-3 px;
       2) fine noise, thresholded, punches sparse ink voids into the solid red. */
    svg.innerHTML =
      '<defs>' +
      '<filter id="rcm-stamp-rough" x="-3%" y="-12%" width="106%" height="124%" color-interpolation-filters="sRGB">' +
      '<feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" seed="11" result="edgeNoise"/>' +
      '<feDisplacementMap in="SourceGraphic" in2="edgeNoise" scale="6" xChannelSelector="R" yChannelSelector="G" result="roughEdges"/>' +
      '<feTurbulence type="fractalNoise" baseFrequency="0.38" numOctaves="2" seed="5" result="grain"/>' +
      '<feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -9 0 0 0 6.6" result="inkMask"/>' +
      '<feComposite in="roughEdges" in2="inkMask" operator="in"/>' +
      '</filter>' +
      '</defs>';
    (document.body || document.documentElement).appendChild(svg);
  }

  /* ================================================================ M1 wanted stars */
  // White five-point star (outer radius 47.8, inner 0.48 of it) in a 100 x 100 box; the 4.5-unit
  // dark outline sits outside the fill, so the star incl. outline spans the full box width.
  var STAR_D = "M50.00 6.76 L63.49 36.00 L95.46 39.79 L71.82 61.65 L78.10 93.24 L50.00 77.51 L21.90 93.24 L28.18 61.65 L4.54 39.79 L36.51 36.00 Z";
  var STAR_PRESETS = {
    hud: { count: 5, size: 40, x: 1700, y: 80 },   // B1, B17: 40 px each, top-right, row centred on (1700, 80)
    hero: { count: 6, size: 120, x: 960, y: 540 }  // B14: 120 px each, centred on the frame
  };

  function starsInit(target, opts) {
    var root = $(target);
    if (root.__rcmStars) return root.__rcmStars;
    opts = opts || {};
    var ds = root.dataset;
    var p = STAR_PRESETS[pick(opts.preset, ds.preset, "hud")] || STAR_PRESETS.hud;
    var stars = root.querySelectorAll(".m1-star");
    var count = num(opts.count, ds.count, stars.length || undefined, p.count);
    var size = num(opts.size, ds.size, p.size);
    var gap = num(opts.gap, ds.gap, Math.round(size * 0.2));
    var x = num(opts.x, ds.x, p.x);
    var y = num(opts.y, ds.y, p.y);
    var anchor = pick(opts.anchor, ds.anchor, "center"); // where x sits on the row: center | left | right
    if (!stars.length) {
      for (var i = 0; i < count; i++) {
        var s = svgEl("svg", { class: "m1-star", viewBox: "0 0 100 100", "aria-hidden": "true" });
        s.appendChild(svgEl("path", { d: STAR_D }));
        root.appendChild(s);
      }
      stars = root.querySelectorAll(".m1-star");
    }
    count = stars.length;
    var rowW = count * size + (count - 1) * gap;
    var left = anchor === "left" ? x : anchor === "right" ? x - rowW : x - rowW / 2;
    root.style.setProperty("--m1-size", size + "px");
    root.style.setProperty("--m1-gap", gap + "px");
    root.style.left = round2(left) + "px";
    root.style.top = round2(y - size / 2) + "px";
    root.style.width = rowW + "px";
    root.style.height = size + "px";
    var st = { root: root, stars: Array.prototype.slice.call(stars), count: count, size: size, gap: gap, x: x, y: y,
      box: { left: left, top: y - size / 2, width: rowW, height: size } };
    gsap.set(st.stars, { transformOrigin: "50% 50%" });
    root.__rcmStars = st;
    return st;
  }

  // M1 pop-in: each star scales 0 -> 100% over 3f (ease out, no overshoot: T7 is the only bouncy
  // animation), stars 3f apart, left to right. opts: stepF=3, durF=3, order 'ltr'|'rtl',
  // times=[sec per star] (overrides the 3f rhythm). Returns the time the last star has landed.
  function starsPopIn(tl, target, at, opts) {
    opts = opts || {};
    var st = starsInit(target, opts);
    var stepF = num(opts.stepF, 3), durF = num(opts.durF, 3);
    var list = st.stars.slice();
    if (opts.order === "rtl") list.reverse();
    var k0 = frameOf(at), last = k0;
    list.forEach(function (star, i) {
      var k = opts.times ? frameOf(opts.times[i]) : k0 + i * stepF;
      last = Math.max(last, k);
      tl.fromTo(star, { scale: 0 }, { scale: 1, duration: durF * F, ease: easeOf(opts.ease, "power3.out"), immediateRender: true }, tF(k));
    });
    return tF(last + durF);
  }

  // M1 blink (B17): all stars together, hard on/off (no fade), deterministic rhythm:
  // ON for onF frames, OFF for offF frames, repeat; first OFF at at+onF; always ON again at `until`.
  // Default 6f on / 6f off = 2.5 blinks per second. opts: until (sec) or cycles (default 4),
  // onF=6, offF=6, offOpacity=0 (0.3 gives a GTA-V-style grey flash instead of a full blink).
  function starsBlink(tl, target, at, opts) {
    opts = opts || {};
    var st = starsInit(target, opts);
    var onF = num(opts.onF, 6), offF = num(opts.offF, 6);
    var k0 = frameOf(at);
    var kEnd = opts.until !== undefined ? frameOf(opts.until) : k0 + num(opts.cycles, 4) * (onF + offF);
    var offOp = num(opts.offOpacity, 0);
    tl.set(st.stars, { opacity: 1 }, setAt(k0));
    var k = k0 + onF;
    while (k < kEnd) {
      tl.set(st.stars, { opacity: offOp }, setAt(k));
      var kOn = Math.min(k + offF, kEnd);
      tl.set(st.stars, { opacity: 1 }, setAt(kOn));
      k = kOn + onF;
    }
    return tF(kEnd);
  }

  /* ================================================================ M2 "you" arrow */
  // Hand-drawn arrow from `from` (tail) to `to` (tip): a wobbled cubic shaft (seeded) + a head drawn as
  // one "V" stroke (barb -> tip -> barb), like a pen. Two <path>s, because SVG restarts the dash
  // pattern on every subpath: the shaft draws first, then the head, inside the same 8f.
  // Same seed = same hand-drawn character (the "same asset" for B5 and B11).
  function arrowGeometry(from, to, o) {
    var dx = to[0] - from[0], dy = to[1] - from[1];
    var L = Math.max(1, Math.hypot(dx, dy));
    var ux = dx / L, uy = dy / L, nx = -uy, ny = ux;
    var bend = num(o.bend, 0.16);                 // + bows to the left of the travel direction (screen y down)
    var rng = RCK.rng(num(o.seed, 7));
    var w = function (a) { return (rng() * 2 - 1) * a; };
    var jit = L * 0.03;
    var c1 = [from[0] + ux * L * 0.28 + nx * L * bend + w(jit), from[1] + uy * L * 0.28 + ny * L * bend + w(jit)];
    var c2 = [from[0] + ux * L * 0.72 + nx * L * bend * 0.8 + w(jit), from[1] + uy * L * 0.72 + ny * L * bend * 0.8 + w(jit)];
    var tx = to[0] - c2[0], ty = to[1] - c2[1], tlen = Math.max(1e-6, Math.hypot(tx, ty));
    var a = Math.atan2(ty / tlen, tx / tlen);
    var headLen = num(o.headLen, 34), spread = num(o.headAngle, 28) * Math.PI / 180;
    var a1 = a + Math.PI - spread + w(0.07), a2 = a + Math.PI + spread + w(0.07);
    var l1 = headLen + w(4), l2 = headLen + w(4);
    var h1 = [to[0] + Math.cos(a1) * l1, to[1] + Math.sin(a1) * l1];
    var h2 = [to[0] + Math.cos(a2) * l2, to[1] + Math.sin(a2) * l2];
    var f = function (p) { return round2(p[0]) + " " + round2(p[1]); };
    var shaftD = "M" + f(from) + " C" + f(c1) + " " + f(c2) + " " + f(to);
    var headD = "M" + f(h1) + " L" + f(to) + " L" + f(h2);
    // arc lengths (the pen moves at one speed profile across shaft + head)
    var shaftLen = 0, prev = from;
    for (var i = 1; i <= 64; i++) {
      var t = i / 64, mt = 1 - t;
      var pt = [mt * mt * mt * from[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t * t * t * to[0],
                mt * mt * mt * from[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t * t * t * to[1]];
      shaftLen += Math.hypot(pt[0] - prev[0], pt[1] - prev[1]); prev = pt;
    }
    var headLenTotal = l1 + l2;
    var sx = c1[0] - from[0], sy = c1[1] - from[1], sl = Math.max(1e-6, Math.hypot(sx, sy));
    return { shaftD: shaftD, headD: headD, d: shaftD + " " + headD, startDir: [sx / sl, sy / sl],
      shaftLen: shaftLen, headLen: headLenTotal, length: L };
  }

  // opts: from [x,y] tail, to [x,y] tip (canvas px), bend 0.16, seed 7, headLen 34, headAngle 28,
  // label "you" (null = no label), labelAt [x,y] (label centre; default: just behind the tail),
  // labelGap 14, drawn false (true = already fully drawn, e.g. an arrow carried over from a cut).
  function arrowInit(target, opts) {
    var root = $(target);
    if (root.__rcmArrow) return root.__rcmArrow;
    opts = opts || {};
    var ds = root.dataset;
    var parsePt = function (v) { return typeof v === "string" ? v.split(/[ ,]+/).map(Number) : v; };
    var from = parsePt(pick(opts.from, ds.from)), to = parsePt(pick(opts.to, ds.to));
    if (!from || !to) throw new Error("RCK.motifs.arrowInit: from/to required (opts or data-from/data-to)");
    var g = arrowGeometry(from, to, { bend: pick(opts.bend, ds.bend), seed: pick(opts.seed, ds.seed), headLen: opts.headLen, headAngle: opts.headAngle });
    var svg = root.querySelector("svg");
    if (!svg) { svg = svgEl("svg", { viewBox: "0 0 1920 1080", width: "1920", height: "1080", "aria-hidden": "true" }); root.appendChild(svg); }
    var shaft = svg.querySelector(".m2-shaft"), head = svg.querySelector(".m2-head");
    if (!shaft) { shaft = svgEl("path", { class: "m2-path m2-shaft" }); svg.appendChild(shaft); }
    if (!head) { head = svgEl("path", { class: "m2-path m2-head" }); svg.appendChild(head); }
    shaft.setAttribute("d", g.shaftD);
    head.setAttribute("d", g.headD);
    var drawn = !!opts.drawn;
    [shaft, head].forEach(function (p) {
      p.setAttribute("pathLength", "100");
      p.setAttribute("stroke-dasharray", "100 120");   // gap longer than the path: no cap dot while hidden
      gsap.set(p, { attr: { "stroke-dashoffset": drawn ? 0 : 110 } });
    });
    var labelText = opts.label === undefined ? pick(ds.label, "you") : opts.label;
    var label = root.querySelector(".m2-label");
    if (labelText !== null && labelText !== false) {
      if (!label) { label = document.createElement("span"); label.className = "m2-label"; root.appendChild(label); }
      label.textContent = labelText;
      var at = parsePt(pick(opts.labelAt, ds.labelAt));
      if (!at) {
        // centre the label just behind the tail, along the tail direction (label ~66 x 36 px)
        var gap = num(opts.labelGap, 14), u = g.startDir;
        var half = Math.abs(u[0]) * 36 + Math.abs(u[1]) * 20;
        at = [from[0] - u[0] * (gap + half), from[1] - u[1] * (gap + half)];
      }
      label.style.left = round2(at[0]) + "px";
      label.style.top = round2(at[1]) + "px";
      gsap.set(label, { opacity: drawn ? 1 : 0 });
    } else if (label) {
      label.parentNode.removeChild(label);
      label = null;
    }
    var st = { root: root, shaft: shaft, head: head, label: label, from: from, to: to, geometry: g };
    root.__rcmArrow = st;
    return st;
  }

  // dashoffset 110 = hidden, 100 - 100*v = v visible: map a visible-fraction curve v(p) to an offset ease
  function offsetEase(v) { return function (p) { return p <= 0 ? 0 : (v(p) + 0.1) / 1.1; }; }

  // M2 draw-on: #FFE14D 6 px stroke drawn on over 8f, ease out (power3.out) across the whole pen move:
  // the shaft takes its share of the curve, then the head "V" finishes on frame at+8. "you" hard-cuts in
  // on the first frame of the draw. opts: durF=8, ease="power3.out" + arrowInit opts. Returns draw end.
  function arrowDraw(tl, target, at, opts) {
    opts = opts || {};
    var st = arrowInit(target, opts);
    var k = frameOf(at), durF = num(opts.durF, 8), D = durF * F;
    var E = gsap.parseEase(easeOf(opts.ease, "power3.out"));
    var g = st.geometry, fs = g.shaftLen / (g.shaftLen + g.headLen);
    var lo = 0, hi = 1;                                   // t* where the pen reaches the tip: E(t*) = fs
    for (var i = 0; i < 40; i++) { var mid = (lo + hi) / 2; if (E(mid) < fs) lo = mid; else hi = mid; }
    var tS = (lo + hi) / 2;
    if (st.label) tl.set(st.label, { opacity: 1 }, setAt(k));
    tl.fromTo(st.shaft, { attr: { "stroke-dashoffset": 110 } }, { attr: { "stroke-dashoffset": 0 }, duration: D * tS,
      ease: offsetEase(function (p) { return Math.min(1, E(p * tS) / fs); }), immediateRender: true }, tF(k));
    tl.fromTo(st.head, { attr: { "stroke-dashoffset": 110 } }, { attr: { "stroke-dashoffset": 0 }, duration: D * (1 - tS),
      ease: offsetEase(function (p) { return Math.min(1, (E(tS + p * (1 - tS)) - fs) / (1 - fs)); }), immediateRender: true }, tF(k) + D * tS);
    return tF(k + durF);
  }

  // Optional exit (not in the plan; for a beat that needs the arrow gone before a hard cut):
  // shaft and head retract together over durF (default 6f, ease in), the label cuts out at the end.
  function arrowErase(tl, target, at, opts) {
    opts = opts || {};
    var st = arrowInit(target, opts);
    var k = frameOf(at), durF = num(opts.durF, 6);
    tl.fromTo([st.shaft, st.head], { attr: { "stroke-dashoffset": 0 } },
      { attr: { "stroke-dashoffset": 110 }, duration: durF * F, ease: easeOf(opts.ease, "power3.in"), immediateRender: false }, tF(k));
    if (st.label) tl.set(st.label, { opacity: 0 }, setAt(k + durF));
    return tF(k + durF);
  }

  /* ================================================================ M3 calendar grid = L9 calendar counter */
  // One component for B4 and B12. Squares are generated once (max slots); slots beyond `slots` are
  // hidden until the grid grows. Fill = hard change (no tween) on its frame, 2f apart, left to right.
  // v02: the counter is Coolvetica (hhea ascent 0.967 em, descent 0.233 em; digits 0.688 em tall); v01 used Inter.
  var FONT_ASC = 0.967, FONT_DESC = 0.233, FONT_DIGIT = 0.688;
  function fontBaseline(fs) { return fs * (1 - (FONT_ASC + FONT_DESC)) / 2 + fs * FONT_ASC; } // line-height 1
  function digitTop(fs) { return fontBaseline(fs) - fs * FONT_DIGIT; }

  // opts: cols 6, max 30, slots 18 (visible slots), filled 0 (already filled at the start),
  // overFrom 18 (index of the first overrun = red square), x/y = grid top-left (default x 748 = grid
  // centred on 960, y 520), counter: start value or null (B12: 18), counterPos 'left'|'above',
  // counterGap (32 left / 24 above), sq 64, gap 8.
  function calendarInit(target, opts) {
    var root = $(target);
    if (root.__rcmCal) return root.__rcmCal;
    opts = opts || {};
    var ds = root.dataset;
    var cols = num(opts.cols, ds.cols, 6), max = num(opts.max, ds.max, 30);
    var slots = num(opts.slots, ds.slots, 18), filled = num(opts.filled, ds.filled, 0);
    var overFrom = num(opts.overFrom, ds.overFrom, 18);
    var sq = num(opts.sq, 64), gap = num(opts.gap, 8);
    var rows = Math.ceil(max / cols);
    var gridW = cols * sq + (cols - 1) * gap, gridH = rows * sq + (rows - 1) * gap;
    var x = num(opts.x, ds.x, Math.round(960 - gridW / 2)), y = num(opts.y, ds.y, 520);
    root.style.setProperty("--m3-sq", sq + "px");
    root.style.setProperty("--m3-gap", gap + "px");
    root.style.setProperty("--m3-cols", String(cols));
    root.style.left = x + "px";
    root.style.top = y + "px";
    root.style.width = gridW + "px";
    root.style.height = gridH + "px";
    var grid = root.querySelector(".m3-grid");
    if (!grid) { grid = document.createElement("div"); grid.className = "m3-grid"; root.appendChild(grid); }
    var sqs = grid.querySelectorAll(".m3-sq");
    if (!sqs.length) {
      for (var i = 0; i < max; i++) {
        var s = document.createElement("div");
        s.className = "m3-sq" + (i >= overFrom ? " m3-over" : "");
        s.setAttribute("data-i", String(i));
        var fl = document.createElement("div");
        fl.className = "m3-fill";
        s.appendChild(fl);
        grid.appendChild(s);
      }
      sqs = grid.querySelectorAll(".m3-sq");
    }
    var squares = Array.prototype.slice.call(sqs);
    var fills = squares.map(function (s) { return s.querySelector(".m3-fill"); });
    squares.forEach(function (s, i) { gsap.set(s, { opacity: i < slots ? 1 : 0 }); });
    fills.forEach(function (f, i) { gsap.set(f, { opacity: i < filled ? 1 : 0 }); });
    var st = { root: root, grid: grid, squares: squares, fills: fills, cols: cols, max: max, slots: slots,
      filled: filled, overFrom: overFrom, counter: null, value: null, gridW: gridW, gridH: gridH, x: x, y: y };
    var startVal = pick(opts.counter, ds.counter);
    if (startVal !== undefined && startVal !== null && startVal !== "false") {
      st.counter = buildCounter(root, Number(startVal), max, pick(opts.counterPos, ds.counterPos, "left"), num(opts.counterGap, ds.counterGap));
      st.value = Number(startVal);
    }
    root.__rcmCal = st;
    return st;
  }

  function buildCounter(root, value, max, pos, gapOpt) {
    var fs = 120;
    var c = root.querySelector(".m3-counter");
    if (!c) { c = document.createElement("div"); c.className = "m3-counter"; root.appendChild(c); }
    c.innerHTML = "";
    c.setAttribute("data-layout-allow-overflow", ""); // the digit strips are taller than their 1em windows by design
    var digits = String(max).length, strips = [];
    for (var j = 0; j < digits; j++) {
      var place = Math.pow(10, digits - 1 - j);
      var col = document.createElement("span");
      col.className = "m3-col";
      var strip = document.createElement("span");
      strip.className = "m3-strip";
      strip.setAttribute("data-layout-allow-occlusion", ""); // off-window digits are clipped on purpose
      for (var n = 0; n <= Math.floor(max / place); n++) {
        var cell = document.createElement("span");
        cell.textContent = String(n % 10);
        cell.setAttribute("data-layout-allow-occlusion", "");
        strip.appendChild(cell);
      }
      col.appendChild(strip);
      c.appendChild(col);
      strips.push({ el: strip, place: place });
    }
    if (pos === "above") {
      var gA = gapOpt === undefined ? 24 : gapOpt;
      c.style.left = "0px";
      c.style.top = round2(-(gA + fontBaseline(fs))) + "px";    // baseline gA px above the grid
    } else {
      var gL = gapOpt === undefined ? 32 : gapOpt;
      c.style.right = "calc(100% + " + gL + "px)";
      c.style.top = round2(-digitTop(fs)) + "px";               // digit top aligned with the grid top
    }
    var cs = { el: c, strips: strips, fs: fs };
    setCounter(cs, value);
    return cs;
  }
  function counterIndex(v, place) { return Math.floor(v / place); }
  function setCounter(cs, v) {
    cs.strips.forEach(function (s) { gsap.set(s.el, { y: -counterIndex(v, s.place) * cs.fs }); });
  }

  // B4: fill squares [from, to) left to right, stepF (2) frames apart, hard fill (no tween).
  // Defaults: from = squares already filled, to = visible slots. Returns the frame time the last
  // square shows filled.
  function calendarFill(tl, target, at, opts) {
    opts = opts || {};
    var st = calendarInit(target, opts);
    var from = num(opts.from, st.filled), to = num(opts.to, st.slots), stepF = num(opts.stepF, 2);
    var k0 = frameOf(at), k = k0;
    for (var i = from; i < to; i++) {
      k = k0 + (i - from) * stepF;
      if (i >= st.slots) tl.set(st.squares[i], { opacity: 1 }, setAt(k));
      tl.set(st.fills[i], { opacity: 1 }, setAt(k));
    }
    st.filled = Math.max(st.filled, to);
    st.slots = Math.max(st.slots, to);
    return tF(k);
  }

  // B12: the grid grows from its current count to `to` (30): each new square appears and fills siren
  // red on its frame, stepF (2) frames apart; the counter rolls +1 per square (odometer: digits slide
  // up over rollF=2 frames, power1.inOut = easeInOutQuad, opts.rollEase; v01 power3.out), so it lands on `to`
  // rollF after the last square.
  // opts: to 30, stepF 2, rollF 2, grow 'with-fill' | 'before' (empty slots all appear at growAt,
  // default `at`, then fill), landAt (sec: ignore `at` and start so the counter lands on this frame).
  // Returns the time the counter has landed (or the last fill without a counter).
  function calendarExtend(tl, target, at, opts) {
    opts = opts || {};
    var st = calendarInit(target, opts);
    var to = num(opts.to, st.max), stepF = num(opts.stepF, 2), rollF = num(opts.rollF, 2);
    var from = st.filled;
    if (opts.landAt !== undefined) at = tF(frameOf(opts.landAt) - (to - from - 1) * stepF - (st.counter ? rollF : 0));
    var k0 = frameOf(at), k = k0;
    var grow = opts.grow || "with-fill";
    if (grow === "before") {
      var kg = frameOf(opts.growAt !== undefined ? opts.growAt : at);
      for (var g = st.slots; g < to; g++) tl.set(st.squares[g], { opacity: 1 }, setAt(kg));
    }
    var v = st.value;
    for (var i = from; i < to; i++) {
      k = k0 + (i - from) * stepF;
      if (grow !== "before" && i >= st.slots) tl.set(st.squares[i], { opacity: 1 }, setAt(k));
      tl.set(st.fills[i], { opacity: 1 }, setAt(k));
      if (st.counter) {
        var nv = v + 1;
        st.counter.strips.forEach(function (s) {
          var a = counterIndex(v, s.place), b = counterIndex(nv, s.place);
          if (a !== b) tl.fromTo(s.el, { y: -a * st.counter.fs }, { y: -b * st.counter.fs, duration: rollF * F, ease: easeOf(opts.rollEase, "power1.inOut"), immediateRender: false }, tF(k));
        });
        v = nv;
      }
    }
    st.filled = Math.max(st.filled, to);
    st.slots = Math.max(st.slots, to);
    st.value = v;
    return st.counter ? tF(k + rollF) : tF(k);
  }

  // v02 (B12 note 6: "add an opening animation where it comes into the screen"): grid + counter rise and scale in
  // together, opts.durF (12) frames, easeOutExpo (opts.ease; e.g. "back.out(1.7)" for a small overshoot), from
  // y + opts.rise (90 px) and scale opts.from (0.9) about the grid centre, opacity 0 -> 1 over the first 6 frames
  // (power2.out). The calendar root stays the clip; its generated children move inside an untimed .m3-body wrapper
  // created here. Place it higher with calendarInit's y (B12: "a bit more above, to the center"). Returns at + durF.
  function calendarIn(tl, target, at, opts) {
    opts = opts || {};
    var st = calendarInit(target, opts), root = st.root, body = root.querySelector(".m3-body");
    if (!body) {
      body = document.createElement("div");
      body.className = "m3-body";
      while (root.firstChild) body.appendChild(root.firstChild);
      root.appendChild(body);
    }
    var k = frameOf(at), d = num(opts.durF, 12), rise = num(opts.rise, 90), s0 = num(opts.from, 0.9), fd = Math.min(d, num(opts.fadeF, 6));
    gsap.set(body, { y: rise, scale: s0, opacity: 0, transformOrigin: "50% 50%" });
    tl.fromTo(body, { y: rise, scale: s0 }, { y: 0, scale: 1, duration: d * F, ease: easeOf(opts.ease, "expo.out"), immediateRender: false }, tF(k));
    tl.fromTo(body, { opacity: 0 }, { opacity: 1, duration: fd * F, ease: easeOf(opts.fadeEase, "power2.out"), immediateRender: false }, tF(k));
    return tF(k + d);
  }

  /* ================================================================ M4 bug chip */
  // 8-bit beetle, 11 x 10 pixels at 4 px (44 x 40), white, crisp. Same drawing as svg/motifs-bug.svg.
  var BUG_D = "M2 0h1v1h-1zM8 0h1v1h-1zM3 1h1v1h-1zM7 1h1v1h-1zM4 2h3v1h-3zM0 3h1v1h-1zM3 3h5v1h-5zM10 3h1v1h-1zM1 4h4v1h-4zM6 4h4v1h-4zM2 5h3v1h-3zM6 5h3v1h-3zM0 6h5v1h-5zM6 6h5v1h-5zM2 7h3v1h-3zM6 7h3v1h-3zM1 8h4v1h-4zM6 8h4v1h-4zM0 9h1v1h-1zM3 9h5v1h-5zM10 9h1v1h-1z";
  function bugChipInit(target) {
    var chip = $(target);
    if (chip.__rcmChip) return chip;
    if (!chip.querySelector(".m4-bug")) {
      var s = svgEl("svg", { class: "m4-bug", viewBox: "0 0 11 10", width: "44", height: "40", "shape-rendering": "crispEdges", "aria-hidden": "true" });
      s.appendChild(svgEl("path", { d: BUG_D }));
      chip.appendChild(s);
    }
    if (!chip.getAttribute("aria-label")) chip.setAttribute("aria-label", "bug");
    gsap.set(chip, { transformOrigin: "50% 50%" });
    chip.__rcmChip = true;
    return chip;
  }
  // T7 chip pop: scale 0 -> 112% -> 100% over 8f (the only bouncy animation in the edit):
  // 0 -> 1.12 in 5f (power3.out), 1.12 -> 1.00 in 3f (power2.inOut). opts.ease (e.g. "back.out(1.7)")
  // switches to a single 8f tween with that ease instead. Returns the time the chip has settled.
  function bugChipPop(tl, target, at, opts) {
    opts = opts || {};
    var chip = bugChipInit(target);
    var k = frameOf(at);
    if (opts.ease) {
      tl.fromTo(chip, { scale: 0 }, { scale: 1, duration: 8 * F, ease: easeOf(opts.ease, "back.out(1.7)"), immediateRender: true }, tF(k));
    } else {
      tl.fromTo(chip, { scale: 0 }, { scale: 1.12, duration: 5 * F, ease: "power3.out", immediateRender: true }, tF(k));
      tl.fromTo(chip, { scale: 1.12 }, { scale: 1, duration: 3 * F, ease: "power2.inOut", immediateRender: false }, tF(k + 5));
    }
    return tF(k + 8);
  }

  /* ================================================================ Windows 95-style error box (B2) */
  var ERR_TITLE = "Race'n'Chase";
  var ERR_TEXT = "This program has performed an illegal operation and will be shut down.";
  var CLOSE_D = "M0 0h2v1h-2zM6 0h2v1h-2zM1 1h2v1h-2zM5 1h2v1h-2zM2 2h4v1h-4zM3 3h2v1h-2zM2 4h4v1h-4zM1 5h2v1h-2zM5 5h2v1h-2zM0 6h2v1h-2zM6 6h2v1h-2z";
  // Builds the window inside an empty .m-errbox (or keeps pasted markup). opts: title, text,
  // x/y (top-left, canvas px), width (default 640), unit (one Win95 pixel, default 2).
  function errorBoxInit(target, opts) {
    var root = $(target);
    if (root.__rcmErr) return root.__rcmErr;
    opts = opts || {};
    var ds = root.dataset;
    if (!root.querySelector(".m-errbox__win")) {
      var win = document.createElement("div");
      win.className = "m-errbox__win";
      var title = document.createElement("div");
      title.className = "m-errbox__title";
      var tt = document.createElement("span");
      tt.className = "m-errbox__title-text";
      tt.textContent = pick(opts.title, ds.title, ERR_TITLE);
      var close = document.createElement("span");
      close.className = "m-errbox__close";
      close.setAttribute("aria-hidden", "true");
      var cs = svgEl("svg", { viewBox: "0 0 8 7", "shape-rendering": "crispEdges" });
      cs.appendChild(svgEl("path", { d: CLOSE_D }));
      close.appendChild(cs);
      title.appendChild(tt);
      title.appendChild(close);
      var body = document.createElement("div");
      body.className = "m-errbox__body";
      var msg = document.createElement("p");
      msg.className = "m-errbox__msg";
      msg.textContent = pick(opts.text, ds.text, ERR_TEXT);
      body.appendChild(msg);
      win.appendChild(title);
      win.appendChild(body);
      root.appendChild(win);
    }
    var x = num(opts.x, ds.x), y = num(opts.y, ds.y);
    if (x !== undefined) root.style.left = x + "px";
    if (y !== undefined) root.style.top = y + "px";
    var w = num(opts.width, ds.width), u = num(opts.unit, ds.unit);
    if (w !== undefined) root.style.setProperty("--m-eb-w", w + "px");
    if (u !== undefined) root.style.setProperty("--m-eb-u", u + "px");
    var st = { root: root, win: root.querySelector(".m-errbox__win") };
    root.__rcmErr = st;
    return st;
  }
  // Hard pop: the window appears on one frame, no tween. (If the error box is its own .clip, its
  // data-start already is the hard pop; use this helper when it lives inside a longer clip.)
  function errorBoxPop(tl, target, at, opts) {
    var st = errorBoxInit(target, opts);
    var k = frameOf(at);
    gsap.set(st.win, { opacity: 0 });
    tl.set(st.win, { opacity: 1 }, setAt(k));
    return tF(k);
  }

  /* ================================================================ camera shake */
  // Deterministic shake of a container ("the camera"): `frames` (4) frames of offsets, one per frame,
  // amplitude `amp` (4) px: each frame one axis sits at exactly +/-amp, the other at +/-1..3 px,
  // direction alternating frame to frame; back to 0,0 on frame at+frames. opts: amp 4, frames 4,
  // seed 4, decay false (true tapers 4,3,2,1 px). The container must not be a .clip and must not
  // have a CSS transform; only x/y are set (a scale/push-in tween on it is fine).
  function shake(tl, target, at, opts) {
    opts = opts || {};
    var c = $(target);
    var amp = num(opts.amp, 4), frames = num(opts.frames, 4);
    var rng = RCK.rng(num(opts.seed, 4));
    var k0 = frameOf(at);
    var sx = rng() < 0.5 ? 1 : -1, sy = rng() < 0.5 ? 1 : -1;
    for (var k = 0; k < frames; k++) {
      var a = opts.decay ? Math.max(1, Math.round(amp * (frames - k) / frames)) : amp;
      var minor = Math.min(a, 1 + Math.floor(rng() * 3));
      var x, y;
      if (k % 2 === 0) { x = sx * a; y = sy * minor; } else { x = sx * minor; y = sy * a; }
      tl.set(c, { x: x, y: y }, setAt(k0 + k));
      sx = -sx; sy = -sy;
      if (rng() < 0.3) sy = -sy; // break the pure diagonal now and then
    }
    tl.set(c, { x: 0, y: 0 }, setAt(k0 + frames));
    return tF(k0 + frames);
  }

  /* ================================================================ CANCELLED stamp (B7) */
  var STAMP_ROT = [-8, -4, 6];                         // plan: vary the rotation (-8, -4, +6 deg)
  var STAMP_OFF = [[0, -30], [0, 0], [0, 30]];         // plan: offset each stamp by about 30 px (vertical stack read best)
  // Anchor = stamp centre. opts: x/y (centre, canvas px or the parent's px), rotation (-8),
  // text "CANCELLED", plain false (true = no rubber-stamp border).
  function stampInit(target, opts) {
    var root = $(target);
    if (root.__rcmStamp) return root.__rcmStamp;
    opts = opts || {};
    var ds = root.dataset;
    ensureDefs();
    var slam = root.querySelector(".m-stamp__slam");
    if (!slam) {
      slam = document.createElement("div");
      slam.className = "m-stamp__slam";
      var ink = document.createElement("span");
      ink.className = "m-stamp__ink";
      ink.textContent = pick(opts.text, ds.text, "CANCELLED");
      ink.setAttribute("data-layout-allow-overlap", "");   // three stamps pile up on purpose (B7)
      ink.setAttribute("data-layout-allow-occlusion", "");
      slam.appendChild(ink);
      root.appendChild(slam);
    }
    if (opts.plain) root.classList.add("m-stamp--plain");
    var x = num(opts.x, ds.x), y = num(opts.y, ds.y);
    if (x !== undefined) root.style.left = x + "px";
    if (y !== undefined) root.style.top = y + "px";
    var rot = num(opts.rotation, ds.rotation, -8);
    gsap.set(slam, { xPercent: -50, yPercent: -50, rotation: rot, scale: num(opts.scaleFrom, 1.3), opacity: 0, transformOrigin: "50% 50%" });
    var st = { root: root, slam: slam, rotation: rot };
    root.__rcmStamp = st;
    return st;
  }
  // One slam: appears at 130% on frame `at`, scales to 100% over 2f (power2.in: accelerates into
  // the hit), lands on frame at+2f; then shakes opts.camera (4 px, 4f) from the landing frame.
  // opts: camera (container to shake, optional), shakeAmp 4, shakeF 4, seed, slamF 2, scaleFrom 1.3,
  // + stampInit opts. Returns the end of the shake (or the landing time without a camera).
  // Landing frame (for S06 sync) = at + 2f = RCK.motifs.stampLandTime(at).
  function stampSlam(tl, target, at, opts) {
    opts = opts || {};
    var st = stampInit(target, opts);
    var k = frameOf(at), slamF = num(opts.slamF, 2);
    tl.set(st.slam, { opacity: 1 }, setAt(k));
    tl.fromTo(st.slam, { scale: num(opts.scaleFrom, 1.3) }, { scale: 1, duration: slamF * F, ease: "power2.in", immediateRender: false }, tF(k));
    if (opts.camera) return shake(tl, opts.camera, tF(k + slamF), { amp: num(opts.shakeAmp, 4), frames: num(opts.shakeF, 4), seed: num(opts.seed, k) });
    return tF(k + slamF);
  }
  // B7 convenience: three stamps (rotation -8/-4/+6, offsets ~30 px) around one centre.
  // targets: [el1, el2, el3]; times: [t1, t2, t3] = slam START times (land 2f later);
  // opts: center [x,y] (required), camera, offsets [[dx,dy] x3], rotations [r x3]. Returns last end.
  function stampTriple(tl, targets, times, opts) {
    opts = opts || {};
    var c = opts.center || [960, 540], offs = opts.offsets || STAMP_OFF, rots = opts.rotations || STAMP_ROT;
    var end = 0;
    for (var i = 0; i < 3; i++) {
      end = stampSlam(tl, targets[i], times[i], {
        x: c[0] + offs[i][0], y: c[1] + offs[i][1], rotation: rots[i],
        camera: opts.camera, seed: 20 + i, plain: opts.plain
      });
    }
    return end;
  }
  function stampLandTime(at, slamF) { return tF(frameOf(at) + (slamF || 2)); }

  /* ================================================================ L8 CRT screen insert */
  // Corner-pin the screen insert onto the plate's screen. geom: {corners: [[x,y] TL, TR, BR, BL]}
  // or {rect: [x, y, w, h]} (no perspective); or data-corners="x,y x,y x,y x,y" / data-rect="x,y,w,h".
  // The element gets the quad's mean width/height as its own size (so 3 px stays ~3 px on screen) and
  // a matrix3d homography as an inline transform (set here once; never animate this element with GSAP:
  // put the X6 zoom on a wrapper that holds the plate AND the insert). Returns {w, h}.
  function homography(src, dst) {
    var A = [], b = [];
    for (var i = 0; i < 4; i++) {
      var x = src[i][0], y = src[i][1], X = dst[i][0], Y = dst[i][1];
      A.push([x, y, 1, 0, 0, 0, -x * X, -y * X]); b.push(X);
      A.push([0, 0, 0, x, y, 1, -x * Y, -y * Y]); b.push(Y);
    }
    var n = 8;
    for (var c = 0; c < n; c++) {
      var p = c;
      for (var r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      var tmp = A[c]; A[c] = A[p]; A[p] = tmp; var tb = b[c]; b[c] = b[p]; b[p] = tb;
      for (var r2 = c + 1; r2 < n; r2++) {
        var fct = A[r2][c] / A[c][c];
        for (var cc = c; cc < n; cc++) A[r2][cc] -= fct * A[c][cc];
        b[r2] -= fct * b[c];
      }
    }
    var h = new Array(n);
    for (var r3 = n - 1; r3 >= 0; r3--) {
      var s = b[r3];
      for (var c3 = r3 + 1; c3 < n; c3++) s -= A[r3][c3] * h[c3];
      h[r3] = s / A[r3][r3];
    }
    return h; // a b c d e f g h  (X = (a x + b y + c) / (g x + h y + 1), Y = (d x + e y + f) / (...))
  }
  // Pure size of the insert box for a geometry (no DOM): {w, h} = mean opposite edge lengths of the quad,
  // or the rect's own size. Use it in node to compute the grading before the browser runs.
  function crtSize(geom) {
    if (geom.rect) return { w: Math.round(geom.rect[2]), h: Math.round(geom.rect[3]) };
    var c = geom.corners, d = function (p, q) { return Math.hypot(p[0] - q[0], p[1] - q[1]); };
    return { w: Math.round((d(c[0], c[1]) + d(c[3], c[2])) / 2), h: Math.round((d(c[0], c[3]) + d(c[1], c[2])) / 2) };
  }
  function crtFit(target, geom) {
    var el = $(target);
    geom = geom || {};
    var ds = el.dataset;
    var corners = geom.corners, rect = geom.rect;
    if (!corners && !rect && ds.corners) corners = ds.corners.trim().split(/\s+/).map(function (p) { return p.split(",").map(Number); });
    if (!corners && !rect && ds.rect) rect = ds.rect.split(/[ ,]+/).map(Number);
    if (!corners && !rect) throw new Error("RCK.motifs.crtFit: corners or rect required");
    el.style.position = "absolute";
    el.style.transformOrigin = "0 0";
    var sz = crtSize(rect ? { rect: rect } : { corners: corners }), w = sz.w, h = sz.h;
    if (rect) {
      el.style.left = rect[0] + "px"; el.style.top = rect[1] + "px";
      el.style.width = w + "px"; el.style.height = h + "px";
      el.style.transform = "none";
    } else {
      var H = homography([[0, 0], [w, 0], [w, h], [0, h]], corners);
      var m = [H[0], H[3], 0, H[6], H[1], H[4], 0, H[7], 0, 0, 1, 0, H[2], H[5], 0, 1];
      el.style.left = "0px"; el.style.top = "0px";
      el.style.width = w + "px"; el.style.height = h + "px";
      el.style.transform = "matrix3d(" + m.map(function (v) { return Number(v.toFixed(10)); }).join(",") + ")";
    }
    el.setAttribute("data-l8-w", String(w));
    el.setAttribute("data-l8-h", String(h));
    return { w: w, h: h };
  }
  // The media-treatment grading for the L8 picture (persist it with the CLI, see KIT_motifs.md).
  // Measured on a calibrated test clip (crtlab): 6 px period, 3 px dark lines at -15%, 1 px R/B split.
  //  8% bulge          -> effects.crtCurvature 0.16 (the shader warps media UV by 0.5 * value: the frame's
  //                       edge midpoints move 8%; corners and the top/bottom band go black)
  //  3 px scanlines 15% -> effects.scanlines 0.15, scanlineSoftness 0 (sine: 3 px dark / 3 px light),
  //                        scanlineCount = (h/3 - 50) / 450 (lines are counted over the ELEMENT height h)
  //  1 px fringing      -> effects.chromaticAberration = 50 / mediaW, angle 0 (the split is a fraction of
  //                        the DISPLAYED MEDIA width: mediaW = w, or h * srcAspect when object-fit:cover
  //                        crops a wider source, e.g. 16:9 footage in a 4:3 screen)
  // size: {w, h} from crtFit; opts.srcAspect: source width / height (default: fills the screen exactly).
  function crtGrading(size, opts) {
    opts = opts || {};
    var w = size.w, h = size.h;
    var mediaW = opts.srcAspect ? Math.max(w, h * opts.srcAspect) : w;
    var clamp = function (v) { return Math.max(0, Math.min(1, v)); };
    return {
      intensity: 1,
      effects: {
        crtCurvature: 0.16,
        scanlines: 0.15,
        scanlineCount: Number(clamp((h / 3 - 50) / 450).toFixed(4)),
        scanlineSoftness: 0,
        chromaticAberration: Number(clamp(50 / mediaW).toFixed(4)),
        chromaticAngle: 0
      }
    };
  }
  // Brightness flicker 97%..100%: one deterministic value per frame (seeded), written to the
  // picture's --hf-color-grading-exposure (log2 of the brightness; the grade runs in display space).
  // Frame at = 100%, frame at+1 = 97%, then seeded values in [min, max]; back to 100% at `until`.
  // opts: until (sec, required), min 0.97, max 1.0, everyF 1, seed 97. Returns `until`.
  function crtFlicker(tl, target, at, opts) {
    opts = opts || {};
    var v = $(target);
    if (opts.until === undefined) throw new Error("RCK.motifs.crtFlicker: opts.until required");
    var lo = num(opts.min, 0.97), hi = num(opts.max, 1.0), every = Math.max(1, num(opts.everyF, 1));
    var rng = RCK.rng(num(opts.seed, 97));
    var k0 = frameOf(at), k1 = frameOf(opts.until), i = 0;
    for (var k = k0; k < k1; k += every, i++) {
      var b = i === 0 ? hi : i === 1 ? lo : lo + (hi - lo) * rng();
      tl.set(v, { "--hf-color-grading-exposure": Number(Math.log2(b).toFixed(5)) }, setAt(k));
    }
    tl.set(v, { "--hf-color-grading-exposure": 0 }, setAt(k1));
    return tF(k1);
  }

  /* ================================================================ export */
  RCK.motifs = {
    // M1
    starsInit: starsInit, starsPopIn: starsPopIn, starsBlink: starsBlink, STAR_PRESETS: STAR_PRESETS, STAR_D: STAR_D,
    // M2
    arrowInit: arrowInit, arrowDraw: arrowDraw, arrowErase: arrowErase, arrowGeometry: arrowGeometry,
    // M3 / L9
    calendarInit: calendarInit, calendarFill: calendarFill, calendarExtend: calendarExtend, calendarIn: calendarIn,
    // M4
    bugChipInit: bugChipInit, bugChipPop: bugChipPop, BUG_D: BUG_D,
    // B2 error box
    errorBoxInit: errorBoxInit, errorBoxPop: errorBoxPop, ERR_TITLE: ERR_TITLE, ERR_TEXT: ERR_TEXT,
    // B7 stamp + camera shake
    stampInit: stampInit, stampSlam: stampSlam, stampTriple: stampTriple, stampLandTime: stampLandTime,
    STAMP_ROT: STAMP_ROT, STAMP_OFF: STAMP_OFF, shake: shake,
    // L8
    crtFit: crtFit, crtSize: crtSize, crtGrading: crtGrading, crtFlicker: crtFlicker,
    // utilities
    frameOf: frameOf, ensureDefs: ensureDefs, ease: easeOf
  };
})();
