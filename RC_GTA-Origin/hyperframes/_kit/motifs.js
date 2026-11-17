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

  /* ---------------------------------------------------------------- M1 v03: glitch-in (REVISION_v03 note 5) */
  // "make the wanted stars glitch in instead of the current opening animation". Each star appears through a short
  // glitch instead of the scale pop: RGB split (a siren-red copy +dx and a siren-blue copy -dx under the white star),
  // three horizontal slices jumping left / right (a new seeded pattern every frame), and 1-2 flicker frames (the star
  // gone for one frame), then the clean star. Every change is a hard cut between two frames (no tween, nothing
  // interpolated); the split narrows frame by frame. Stars start stepF apart (3f, like the v01 pop), left to right.
  var STAR_SLICES = [[-40, 38], [38, 63], [63, 140]];   // y bands in star units (the star spans 6.8 .. 93.2 of 100)
  function ensureStarClips() {
    if (document.getElementById("rcm-star-sl1")) return;
    ensureDefs();
    var defs = document.getElementById(DEFS_ID).querySelector("defs");
    STAR_SLICES.forEach(function (b, i) {
      var cp = svgEl("clipPath", { id: "rcm-star-sl" + (i + 1), clipPathUnits: "userSpaceOnUse" });
      cp.appendChild(svgEl("rect", { x: "-300", y: String(b[0]), width: "700", height: String(b[1] - b[0]) }));
      defs.appendChild(cp);
    });
  }
  function starsGlitchPrep(st) {
    if (st.glitch) return st.glitch;
    ensureStarClips();
    st.glitch = st.stars.map(function (star) {
      var clean = star.querySelector("path");
      var gl = svgEl("g", { "class": "m1-gl" });
      var slices = STAR_SLICES.map(function (b, i) {
        var g = svgEl("g", { "clip-path": "url(#rcm-star-sl" + (i + 1) + ")", transform: "translate(0 0)" });
        var r = svgEl("path", { d: STAR_D, "class": "m1-gl__r", transform: "translate(0 0)" });
        var bl = svgEl("path", { d: STAR_D, "class": "m1-gl__b", transform: "translate(0 0)" });
        g.appendChild(r); g.appendChild(bl); g.appendChild(svgEl("path", { d: STAR_D, "class": "m1-gl__w" }));
        gl.appendChild(g);
        return { g: g, r: r, b: bl };
      });
      star.appendChild(gl);
      return { star: star, clean: clean, gl: gl, slices: slices };
    });
    return st.glitch;
  }
  // opts: stepF (3) frames between star starts, frames (6; 5-8) of glitch per star, amp (14 star units = 14% of the
  // star size: slice jump), split (8 units: RGB offset on the first glitch frame, narrowing to ~2), flickers (2: frames
  // with the star gone; 0-2), flickerOpacity (0), seed (7), order 'ltr' | 'rtl', times = [sec per star] (overrides the
  // stepF rhythm). Also takes starsInit's opts (preset, size, x, y...). Returns the time the last star is clean.
  function starsGlitchIn(tl, target, at, opts) {
    opts = opts || {};
    var st = starsInit(target, opts), gls = starsGlitchPrep(st).slice();
    var stepF = num(opts.stepF, 3), nF = Math.max(3, num(opts.frames, 6)), amp = num(opts.amp, 14), split = num(opts.split, 8);
    var nFlick = Math.max(0, Math.min(2, num(opts.flickers, 2))), flickOp = num(opts.flickerOpacity, 0);
    var rnd = RCK.rng(num(opts.seed, 7)), k0 = frameOf(at), last = k0;
    var J = [-1, -0.5, 0.5, 1, 0];
    if (opts.order === "rtl") gls.reverse();
    gls.forEach(function (s, i) {
      var k = opts.times ? frameOf(opts.times[i]) : k0 + i * stepF;
      last = Math.max(last, k);
      gsap.set(s.star, { opacity: 0 });
      gsap.set(s.clean, { opacity: 0 });
      gsap.set(s.gl, { opacity: 1 });
      // flicker frames: inside the glitch, never its first or last frame, never two in a row
      var flick = {}, cand = [];
      for (var j0 = 1; j0 < nF - 1; j0++) cand.push(j0);
      for (var n = 0; n < nFlick && cand.length; n++) {
        var pickJ = cand[Math.floor(rnd() * cand.length)];
        flick[pickJ] = true;
        cand = cand.filter(function (c) { return Math.abs(c - pickJ) > 1; });
      }
      var prev = "";
      for (var j = 0; j < nF; j++) {
        var at2 = setAt(k + j), v, tries = 0;
        do {
          v = s.slices.map(function () { return J[Math.floor(rnd() * 4)] * amp; });   // +/- amp or +/- amp/2
          if (v[0] === v[1] && v[1] === v[2]) v[1] = -v[1];
        } while (v.join() === prev && ++tries < 16);
        prev = v.join();
        var dx = round2(split * (1 - 0.75 * j / (nF - 1)));
        s.slices.forEach(function (sl, q) {
          tl.set(sl.g, { attr: { transform: "translate(" + round2(v[q]) + " 0)" } }, at2);
          tl.set(sl.r, { attr: { transform: "translate(" + dx + " 0)" } }, at2);
          tl.set(sl.b, { attr: { transform: "translate(" + (-dx) + " 0)" } }, at2);
        });
        tl.set(s.star, { opacity: flick[j] ? flickOp : 1 }, at2);
      }
      var atEnd = setAt(k + nF);
      tl.set(s.star, { opacity: 1 }, atEnd);
      tl.set(s.gl, { opacity: 0 }, atEnd);
      tl.set(s.clean, { opacity: 1 }, atEnd);
      s.slices.forEach(function (sl) {
        tl.set(sl.g, { attr: { transform: "translate(0 0)" } }, atEnd);
        tl.set([sl.r, sl.b], { attr: { transform: "translate(0 0)" } }, atEnd);
      });
    });
    return tF(last + nF);
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
    starsInit: starsInit, starsPopIn: starsPopIn, starsBlink: starsBlink, starsGlitchIn: starsGlitchIn, STAR_PRESETS: STAR_PRESETS, STAR_D: STAR_D,
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

/* ======================================================================================================================
   v05 MOTION-GRAPHICS KIT: RCK.fx (REVISION_v05 G6, doc 2.4; px = doc @720 x 1.5). Docs + frame timings: KIT_v05.md.
   Build once, reuse: every helper is a pure function of its arguments (seeded jitter, no Math.random), eased (hard cuts
   are 0.5-frame step tweens between two frames), and identical every time it is called with the same arguments.
   Signature: RCK.fx.<helper>(tl, target, atSeconds, opts) -> endSeconds. `target` = a timed, empty host
   <div class="clip fx-host" ...> (selector or element); the helper builds its graphic inside and animates only that.
   ====================================================================================================================== */
(function () {
  "use strict";
  var FPS = 30, F = 1 / FPS, SVGNS = "http://www.w3.org/2000/svg";
  var PINK = "#FF2E7E", YEL = "#FFD23F", RED = "#E3262B", BLUE = "#2E6BFF", WHITE = "#FFFFFF";
  function G() { if (!window.gsap) throw new Error("RCK.fx: GSAP not loaded"); return window.gsap; }
  function $(t, scope) {
    var e = typeof t === "string" ? (scope || document).querySelector(t) : (t && t.jquery ? t[0] : t);
    if (!e) throw new Error("RCK.fx: target not found: " + t);
    return e;
  }
  function $$(t, scope) {
    if (typeof t === "string") return Array.prototype.slice.call((scope || document).querySelectorAll(t));
    if (t && t.length != null && !t.nodeType) return Array.prototype.slice.call(t);
    return t ? [t] : [];
  }
  function frame(t) { return Math.round(t * FPS + 1e-6); }
  function r2(v) { return Math.round(v * 100) / 100; }
  function num(v, d) { return v === undefined || v === null || v === "" ? d : Number(v); }
  function pct(v) { v = Number(v); return v > 3 ? v / 100 : v; }          // 150 or 1.5 -> 1.5
  function easeOf(e, d) {
    if (e === undefined || e === null || e === "") e = d;
    if (typeof e === "function") return e;
    if (/^(none|linear)$/i.test(String(e))) e = d;
    return window.RCK && RCK.ease && RCK.ease.gsap ? RCK.ease.gsap(e) : e;
  }
  function BZ() { return (RCK.ease && RCK.ease.trailer) || "expo.out"; }   // cubic-bezier(0.2, 0.8, 0.2, 1)
  // hard cut: frame k shows `to`, frame k-1 shows `from` (0.5-frame step tween strictly between the two frames)
  function hard(tl, el, from, to, k) {
    var pos = (k - 0.75) / FPS;
    if (pos < 0) { G().set(el, to); return; }
    tl.fromTo(el, from, Object.assign({ duration: 0.5 / FPS, ease: "steps(1)", immediateRender: false }, to), pos);
  }
  function span(tl, el, from, to, k, dF, ease) {
    tl.fromTo(el, from, Object.assign({ duration: Math.max(1, dF) / FPS, ease: ease, immediateRender: false }, to), k / FPS);
    return (k + dF) / FPS;
  }
  function mk(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function svg(tag, attrs) { var e = document.createElementNS(SVGNS, tag); for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) e.setAttribute(k, attrs[k]); return e; }
  function seedOf(str) { var h = 2166136261; str = String(str); for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function rng(seed) { return RCK.rng((seed >>> 0) || 1); }
  function hostAnchor(host) {               // the host's 0x0 anchor point (created once)
    var a = host.querySelector(":scope > .fx-anchor");
    if (!a) { a = mk("div", "fx-anchor"); host.appendChild(a); }
    return a;
  }
  function anim(el) { return el.classList && el.classList.contains("clip") ? (el.firstElementChild || el) : el; }
  function clipEndF(el) {
    for (var e = el; e && e.getAttribute; e = e.parentElement) {
      var s = e.getAttribute("data-start"), d = e.getAttribute("data-duration");
      if (s != null && d != null && !e.hasAttribute("data-composition-id")) return frame(+s + +d);
    }
    return null;
  }

  /* ---------------- shared SVG defs: RGB-split filters (per px), vertical motion blur, marker texture, star glow ------------ */
  var DEFS = "rck-fx-defs";
  function defs() {
    var s = document.getElementById(DEFS);
    if (!s) {
      s = svg("svg", { id: DEFS, width: "0", height: "0", "aria-hidden": "true", focusable: "false" });
      s.setAttribute("style", "position:absolute;width:0;height:0;overflow:hidden;pointer-events:none");
      s.setAttribute("data-layout-ignore", "");
      s.appendChild(svg("defs", {}));
      (document.body || document.documentElement).appendChild(s);
    }
    return s.firstChild;
  }
  // RGB split as an SVG filter for DOM graphics (text, pills, windows; never footage: footage = rgbGrading): red +px,
  // blue -px, green in place, recombined additively.
  function rgbFilter(px) {
    var id = "rck-rgb-" + Math.round(px * 10);
    if (document.getElementById(id)) return "url(#" + id + ")";
    var f = svg("filter", { id: id, x: "-10%", y: "-10%", width: "120%", height: "120%", "color-interpolation-filters": "sRGB" });
    f.innerHTML =
      '<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>' +
      '<feOffset in="r" dx="' + px + '" dy="0" result="r2"/>' +
      '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>' +
      '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/>' +
      '<feOffset in="b" dx="' + (-px) + '" dy="0" result="b2"/>' +
      '<feBlend in="r2" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b2" mode="screen"/>';
    defs().appendChild(f);
    return "url(#" + id + ")";
  }
  function vblurFilter(px) {               // vertical-only gaussian (slot counter motion blur)
    px = Math.round(px);
    if (px <= 0) return "none";
    var id = "rck-vblur-" + px;
    if (!document.getElementById(id)) {
      var f = svg("filter", { id: id, x: "-5%", y: "-40%", width: "110%", height: "180%" });
      f.appendChild(svg("feGaussianBlur", { stdDeviation: "0 " + px }));
      defs().appendChild(f);
    }
    return "url(#" + id + ")";
  }
  function markerFilter() {                 // felt-marker edge: slight displacement roughness (static, seeded)
    var id = "rck-marker";
    if (!document.getElementById(id)) {
      var f = svg("filter", { id: id, x: "-5%", y: "-5%", width: "110%", height: "110%" });
      f.innerHTML = '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5" result="n"/>' +
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G" result="d"/>' +
        '<feComponentTransfer in="n" result="a"><feFuncA type="linear" slope="0" intercept="1"/><feFuncR type="linear" slope="0.25" intercept="0.82"/></feComponentTransfer>' +
        '<feColorMatrix in="a" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="m"/>' +
        '<feComposite in="d" in2="m" operator="in"/>';
      defs().appendChild(f);
    }
    return "url(#" + id + ")";
  }

  /* ---------------- 1-frame white flash ---------------- */
  // fx.flash(tl, host, at, { opacity: 1 (e.g. 0.7), frames: 1, color }): a full-frame white layer on for `frames` frames.
  function flash(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), k = frame(at), n = num(opts.frames, 1);
    var el = host.querySelector(":scope > .fx-flash");
    if (!el) { el = mk("div", "fx-fill fx-flash"); host.appendChild(el); }
    if (opts.color) el.style.background = opts.color;
    G().set(el, { opacity: 0 });
    hard(tl, el, { opacity: 0 }, { opacity: num(opts.opacity, 1) }, k);
    hard(tl, el, { opacity: num(opts.opacity, 1) }, { opacity: 0 }, k + n);
    return (k + n) / FPS;
  }

  /* ---------------- seeded camera shake ---------------- */
  // fx.shake(tl, wrapper, at, { px: 6, frames: 4, seed, decay: true }): one seeded offset per frame (hard steps; the
  // amplitude decays to a third), back to 0 on frame at + frames. Put it on an untimed wrapper (an .rc-cam).
  function shake(tl, target, at, opts) {
    opts = opts || {};
    var els = $$(target), k0 = frame(at), n = num(opts.frames, 4), px = num(opts.px, 6);
    var R = rng(num(opts.seed, seedOf("shake" + k0)));
    var seq = [];
    for (var j = 0; j < n; j++) {
      var a = opts.decay === false ? px : px * (1 - (2 / 3) * (n > 1 ? j / (n - 1) : 0));
      var ang = R() * Math.PI * 2;
      seq.push({ x: r2(Math.cos(ang) * a), y: r2(Math.sin(ang) * a * 0.8) });
    }
    els.forEach(function (el) {
      var prev = { x: 0, y: 0 };
      seq.forEach(function (o, j) { hard(tl, el, { x: prev.x, y: prev.y }, { x: o.x, y: o.y }, k0 + j); prev = o; });
      hard(tl, el, { x: prev.x, y: prev.y }, { x: 0, y: 0 }, k0 + n);
    });
    return (k0 + n) / FPS;
  }

  /* ---------------- flash-star burst (white 4-point star flare at a cut) ---------------- */
  // fx.flashStar(tl, host, at, { x, y (or the host's --x/--y), size: 560, frames: 5, rotate: 18 }): f0 the flare at 40%,
  // f0-2 grows to 100% (expo.out) while turning, f2-end fades (power2.out) as it keeps growing to 125%.
  function flashStar(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), k = frame(at), n = num(opts.frames, 5), S = num(opts.size, 560);
    var a = hostAnchor(host);
    if (opts.x != null) host.style.setProperty("--x", opts.x + "px");
    if (opts.y != null) host.style.setProperty("--y", opts.y + "px");
    var st = a.querySelector(".fx-star");
    if (!st) {
      st = svg("svg", { "class": "fx-star", width: S, height: S, viewBox: "-100 -100 200 200" });
      st.style.left = (-S / 2) + "px"; st.style.top = (-S / 2) + "px"; st.style.position = "absolute";
      var gid = "rck-star-glow-" + seedOf(host.id || "s");
      st.innerHTML = '<defs><radialGradient id="' + gid + '"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="0.25" stop-color="#FFFFFF" stop-opacity="0.45"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>' +
        '<filter id="' + gid + '-b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>' +
        '<circle r="46" fill="url(#' + gid + ')"/>' +
        '<g filter="url(#' + gid + '-b)" fill="#FFFFFF"><path d="M0,-100 L5,-5 L100,0 L5,5 L0,100 L-5,5 L-100,0 L-5,-5 Z"/><path d="M0,-44 L3.2,-3.2 L44,0 L3.2,3.2 L0,44 L-3.2,3.2 L-44,0 L-3.2,-3.2 Z" transform="rotate(45)"/></g>' +
        '<path d="M0,-100 L2.6,-2.6 L100,0 L2.6,2.6 L0,100 L-2.6,2.6 L-100,0 L-2.6,-2.6 Z" fill="#FFFFFF"/>';
      a.appendChild(st);
    }
    G().set(st, { opacity: 0, scale: 0.4, rotation: 0, transformOrigin: "50% 50%" });
    hard(tl, st, { opacity: 0 }, { opacity: 1 }, k);
    span(tl, st, { scale: 0.4, rotation: 0 }, { scale: 1, rotation: num(opts.rotate, 18) * 0.6 }, k, 2, "expo.out");
    span(tl, st, { scale: 1, rotation: num(opts.rotate, 18) * 0.6, opacity: 1 }, { scale: 1.25, rotation: num(opts.rotate, 18), opacity: 0 }, k + 2, n - 2, "power2.out");
    return (k + n) / FPS;
  }

  /* ---------------- logo slam (B1, B13, B17 call the same function) ---------------- */
  // fx.logoSlam(tl, el, at, { from: 150 | 160, overshoot: 94, frames: 6, flash: host, flashOpacity: 0.85, star: host,
  // starSize, shakeTarget: wrapper, shakePx: 9, shakeF: 6, seed }): el (the logo, untimed child) appears on f0 at
  // `from`, slams to `overshoot` by f4 (power2.in: accelerates into the hit) and settles to 100% by f6 (power2.out).
  // Impact = f4: 1-frame white flash, flash-star behind, camera shake. Returns the landing time (f6).
  function logoSlam(tl, target, at, opts) {
    opts = opts || {};
    var el = $(target), k = frame(at), n = num(opts.frames, 6), imp = k + Math.max(1, n - 2);
    var s0 = pct(num(opts.from, 1.5)), s1 = pct(num(opts.overshoot, 0.94));
    G().set(el, { opacity: 0, scale: s0, transformOrigin: opts.origin || "50% 50%" });
    hard(tl, el, { opacity: 0 }, { opacity: 1 }, k);
    span(tl, el, { scale: s0 }, { scale: s1 }, k, imp - k, "power2.in");
    span(tl, el, { scale: s1 }, { scale: 1 }, imp, k + n - imp, "power2.out");
    if (opts.flash) flash(tl, opts.flash, imp / FPS, { opacity: num(opts.flashOpacity, 0.85) });
    if (opts.star) flashStar(tl, opts.star, imp / FPS, { size: opts.starSize, frames: opts.starF });
    if (opts.shakeTarget) shake(tl, opts.shakeTarget, imp / FPS, { px: num(opts.shakePx, 9), frames: num(opts.shakeF, 6), seed: num(opts.seed, 1997) });
    return (k + n) / FPS;
  }

  /* ---------------- rubber stamp ---------------- */
  // fx.stamp(tl, host, at, { text: "CANNED", rotate: -12, size: 180, flash: host, flashOpacity: 1, shakeTarget, shakePx: 6,
  // shakeF: 4, seed }): the stamp appears on f0 at 180%, slams to 95% by f3 (power2.in), settles 100% by f5 (power2.out);
  // impact = f3: 1-frame white flash + 6 px shake for 4f. Rough #E3262B grunge (filter #rcm-stamp-rough). Anchor: --x/--y.
  function stamp(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), k = frame(at), a = hostAnchor(host);
    if (RCK.motifs && RCK.motifs.ensureDefs) RCK.motifs.ensureDefs();
    var slam = a.querySelector(".fx-stamp__slam");
    if (!slam) {
      slam = mk("div", "fx-stamp__slam");
      var ink = mk("span", "fx-stamp__ink", opts.text || host.getAttribute("data-text") || "CANNED");
      ink.setAttribute("data-layout-allow-overlap", ""); ink.setAttribute("data-layout-allow-occlusion", "");   // stamped over a page on purpose
      if (opts.size) ink.style.setProperty("--stamp-size", opts.size + "px");
      slam.appendChild(ink); a.appendChild(slam);
    }
    var rot = num(opts.rotate, -12);
    G().set(slam, { opacity: 0, scale: 1.8, rotation: rot, transformOrigin: "50% 50%" });
    hard(tl, slam, { opacity: 0 }, { opacity: 1 }, k);
    span(tl, slam, { scale: 1.8 }, { scale: 0.95 }, k, 3, "power2.in");
    span(tl, slam, { scale: 0.95 }, { scale: 1 }, k + 3, 2, "power2.out");
    if (opts.flash) flash(tl, opts.flash, (k + 3) / FPS, { opacity: num(opts.flashOpacity, 1) });
    if (opts.shakeTarget) shake(tl, opts.shakeTarget, (k + 3) / FPS, { px: num(opts.shakePx, 6), frames: num(opts.shakeF, 4), seed: num(opts.seed, 31) });
    return (k + 5) / FPS;
  }

  /* ---------------- pink pixel glitch ---------------- */
  // fx.glitch(tl, target, at, { mode: 'cut' | 'in' | 'out', frames: 7, seed, split: 9, blocks: 16, shake: wrapper, shakePx }):
  // 'cut': target = a full-frame host timed over the transition; blocky #FF2E7E + white rectangles and pixel-sort
  // streaks tear across the frame, a new seeded layout every frame (hard steps), RGB split (9 px) on frames 2-5.
  // 'in' / 'out': target = a DOM element (text, pill box, window, lockup box; a .clip host: its first child): the same
  // blocks inside its box, the element jitters +/- 14 px per frame, RGB split on f2-5, and appears ('in': hidden before
  // f0, a dropped frame on f1) or disappears ('out': gone from f frames). Footage under a 'cut' is untouched (rule:
  // grades / filters on footage = media treatment); opts.shake jitters a footage wrapper instead. Returns at + frames.
  function glitchLayer(host, nb) {
    var L = host.querySelector(":scope > .fx-glitch__layer");
    if (L) return L;
    L = mk("div", "fx-glitch__layer");
    L.setAttribute("data-layout-ignore", "");
    for (var i = 0; i < nb; i++) L.appendChild(mk("div", "fx-glitch__b " + (i % 5 === 4 ? "fx-glitch__b--s" : i % 5 === 1 || i % 5 === 3 ? "fx-glitch__b--w" : "fx-glitch__b--p")));
    host.appendChild(L);
    return L;
  }
  function glitch(tl, target, at, opts) {
    opts = opts || {};
    var mode = opts.mode || "cut", k = frame(at), n = num(opts.frames, 7), nb = num(opts.blocks, 16);
    var root = $(target), el = mode === "cut" ? root : anim(root);
    if (mode !== "cut" && window.getComputedStyle(el).position === "static") el.style.position = "relative";
    var L = glitchLayer(mode === "cut" ? root : el, nb), bs = Array.prototype.slice.call(L.children);
    var R = rng(num(opts.seed, seedOf((root.id || "g") + k)));
    G().set(bs, { opacity: 0, xPercent: 0, yPercent: 0, scaleX: 0.01, scaleY: 0.01, transformOrigin: "0 0" });
    var prev = bs.map(function () { return { o: 0, x: 0, y: 0, sx: 0.01, sy: 0.01 }; });
    for (var j = 0; j < n; j++) {
      var dens = j === 0 || j === n - 1 ? 0.45 : 1, band = R() * 0.7;
      bs.forEach(function (b, i) {
        var streak = b.classList.contains("fx-glitch__b--s"), on = R() < (streak ? 0.55 : 0.75) * dens;
        var y = streak ? R() : band + R() * 0.45 - 0.08, h = streak ? 0.006 + R() * 0.012 : 0.02 + R() * 0.075;
        var x = streak ? -0.1 + R() * 0.3 : -0.08 + R() * 0.9, w = streak ? 0.35 + R() * 0.75 : 0.05 + R() * 0.45;
        if (R() < 0.25 && !streak) { w = 0.6 + R() * 0.5; h = 0.012 + R() * 0.02; }        // long thin tears
        var o = { o: on ? (streak ? 1 : 0.86 + R() * 0.14) : 0, x: r2(x * 100), y: r2(y * 100), sx: r2(w), sy: r2(h) };
        hard(tl, b, { opacity: prev[i].o, xPercent: prev[i].x, yPercent: prev[i].y, scaleX: prev[i].sx, scaleY: prev[i].sy },
          { opacity: o.o, xPercent: o.x, yPercent: o.y, scaleX: o.sx, scaleY: o.sy }, k + j);
        prev[i] = o;
      });
    }
    bs.forEach(function (b, i) { hard(tl, b, { opacity: prev[i].o }, { opacity: 0 }, k + n); });
    var sp = num(opts.split, 9), s0 = k + 2, s1 = Math.min(k + 6, k + n);
    if (sp > 0) {
      var tgt = mode === "cut" ? L : el, fl = rgbFilter(sp);
      hard(tl, tgt, { filter: "none" }, { filter: fl }, s0);
      hard(tl, tgt, { filter: fl }, { filter: "none" }, s1);
    }
    if (mode !== "cut") {
      var amp = num(opts.jitter, 14), px = 0;
      G().set(el, { x: 0 });
      for (var q = 0; q < n; q++) { var nx = (q % 2 ? -1 : 1) * Math.round(amp * (0.4 + R() * 0.6)); hard(tl, el, { x: px }, { x: nx }, k + q); px = nx; }
      hard(tl, el, { x: px }, { x: 0 }, k + n);
      if (mode === "in") {
        G().set(el, { opacity: 0 });
        hard(tl, el, { opacity: 0 }, { opacity: 1 }, k);
        if (n > 3) { hard(tl, el, { opacity: 1 }, { opacity: 0 }, k + 1); hard(tl, el, { opacity: 0 }, { opacity: 1 }, k + 2); }
      } else {
        hard(tl, el, { opacity: 1 }, { opacity: 0.35 }, k + n - 2);
        hard(tl, el, { opacity: 0.35 }, { opacity: 0 }, k + n);
      }
    }
    if (opts.shake) {
      var sx = 0, SR = rng(num(opts.seed, 7) + 99);
      $$(opts.shake).forEach(function (w) {
        sx = 0;
        for (var q2 = 0; q2 < n; q2++) { var v = (q2 % 2 ? -1 : 1) * Math.round(num(opts.shakePx, 18) * (0.5 + SR() * 0.5)); hard(tl, w, { x: sx }, { x: v }, k + q2); sx = v; }
        hard(tl, w, { x: sx }, { x: 0 }, k + n);
      });
    }
    return (k + n) / FPS;
  }

  /* ---------------- highlight pill + name pill ---------------- */
  // Host: <div class="clip fx-host fx-pill" style="--x; --y">THAT BUG SAVED IT</div>  (name pill: class "fx-pill--name",
  // text "GARY PENN" + data-line2="DMA Design · Gamasutra, 2011"; lower-left at --x / --b). fx.pill(tl, host, at,
  // { cps: 30, wipeF: 6, size }): f0-6 the box wipes 0 -> 100% from the left (power2.out); the text types on from f6 at
  // 30 chars/s (1 char a frame; line 2 after line 1). Returns the time the last character is in.
  function pillInit(host, opts) {
    if (host.__fxPill) return host.__fxPill;
    var line1 = (opts.text != null ? opts.text : host.textContent).replace(/\s+/g, " ").trim(), line2 = opts.line2 || host.getAttribute("data-line2");
    host.textContent = "";
    var a = hostAnchor(host), box = mk("div", "fx-pill__box"), t1 = mk("span", "fx-pill__text");
    if (opts.size) host.style.setProperty("--pill-size", opts.size + "px");
    var chars = [];
    Array.from(line1).forEach(function (ch) { var s = mk("span", "fx-pill__ch", ch); t1.appendChild(s); chars.push(s); });
    box.appendChild(t1);
    if (line2) {
      var t2 = mk("span", "fx-pill__l2");
      Array.from(line2).forEach(function (ch) { var s = mk("span", "fx-pill__ch", ch); t2.appendChild(s); chars.push(s); });
      box.appendChild(t2);
    }
    a.appendChild(box);
    host.__fxPill = { box: box, chars: chars };
    return host.__fxPill;
  }
  function pill(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), st = pillInit(host, opts), k = frame(at), wf = num(opts.wipeF, 6), cps = num(opts.cps, 30);
    G().set(st.box, { "--w": 0 });
    span(tl, st.box, { "--w": 0 }, { "--w": 1 }, k, wf, "power2.out");
    var t0 = k + wf + num(opts.typeDelayF, 0), last = t0;
    G().set(st.chars, { opacity: 0 });
    st.chars.forEach(function (c, i) { var f = t0 + Math.floor(i * FPS / cps); hard(tl, c, { opacity: 0 }, { opacity: 1 }, f); last = f; });
    return (last + 1) / FPS;
  }
  // fx.pillOut(tl, host, at, opts): the pill leaves through the pink pixel glitch (mode 'out', 7f).
  function pillOut(tl, target, at, opts) { var host = $(target); return glitch(tl, pillInit(host, opts || {}).box, at, Object.assign({ mode: "out", seed: seedOf(host.id || "pill") }, opts)); }

  /* ---------------- Win95-style error window, cascade, snap shut, 2-frame flash ---------------- */
  var ERR_TEXT = "This program has performed an illegal operation and will be shut down.";
  function errIcon() {
    return '<svg class="fx-err__icon" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14.5" fill="#E3262B" stroke="#7A0E12" stroke-width="1.5"/>' +
      '<path d="M10.5 10.5 L21.5 21.5 M21.5 10.5 L10.5 21.5" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="square"/></svg>';
  }
  // fx.errorWindow(host, { title: "Race'n'Chase", text, scale: 1.8, x, y, buttons: ['Close', 'Details >>'], theme: 'classic' | 'dark' })
  // builds the window (classic 1990s grey dialog, navy title bar, red stop icon; no OS logos) centred on --x / --y.
  // Base width 640 px x scale (doc B2: ~60% of the frame = scale 1.8). Returns the window element.
  function errorWindow(target, opts) {
    opts = opts || {};
    var host = $(target);
    if (host.__fxErr) return host.__fxErr.win;
    var s = num(opts.scale, num(host.getAttribute("data-scale"), 1.8));
    if (opts.theme === "dark") host.classList.add("fx-err--dark");
    var win = mk("div", "fx-err__win");
    win.style.setProperty("--s", s);
    win.setAttribute("data-layout-allow-overlap", "");     // the cascade piles windows on purpose
    win.setAttribute("data-layout-allow-occlusion", "");
    var btns = opts.buttons || ["Close", "Details >>"];
    win.innerHTML = '<div class="fx-err__title"><span></span><span class="fx-err__x">&#x2715;</span></div>' +
      '<div class="fx-err__body">' + errIcon() + '<p class="fx-err__msg"></p></div>' +
      '<div class="fx-err__btns">' + btns.map(function (b, i) { return '<span class="fx-err__btn' + (i === 0 ? " fx-err__btn--def" : "") + '"></span>'; }).join("") + "</div>";
    win.querySelector(".fx-err__title span").textContent = opts.title || host.getAttribute("data-title") || "Race'n'Chase";
    win.querySelector(".fx-err__msg").textContent = opts.text || host.getAttribute("data-text") || ERR_TEXT;
    Array.prototype.slice.call(win.querySelectorAll(".fx-err__btn")).forEach(function (b, i) { b.textContent = btns[i]; });
    var W = 640 * s, H = num(opts.height, 300) * s;          // layout estimate for centring (height: the 3-line message)
    var x = num(opts.x, parseFloat(getComputedStyle(host).getPropertyValue("--x")) || 960), y = num(opts.y, parseFloat(getComputedStyle(host).getPropertyValue("--y")) || 540);
    win.style.left = r2(x - W / 2) + "px"; win.style.top = r2(y - H / 2) + "px";
    host.appendChild(win);
    host.__fxErr = { win: win, copies: [], x: x - W / 2, y: y - H / 2 };
    return win;
  }
  // fx.errorPop(tl, host, at, opts): the window slams in: f0 visible at 112%, 100% by f3 (expo.out).
  function errorPop(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), win = errorWindow(host, opts), k = frame(at);
    G().set(win, { opacity: 0, scale: num(opts.from, 1.12) });
    hard(tl, win, { opacity: 0 }, { opacity: 1 }, k);
    return span(tl, win, { scale: num(opts.from, 1.12) }, { scale: 1 }, k, 3, "expo.out");
  }
  // fx.errorCascade(tl, host, at, { count: 10, dx: 36, dy: 27, stepF: 2 }): copy i (1..count) of the window appears
  // (hard cut) on f = at + (i - 1) x stepF, offset i x (dx, dy) (+36 / +27 px each: they run off frame). Returns the
  // time the last copy is in.
  function errorCascade(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), win = errorWindow(host, opts), st = host.__fxErr, k = frame(at);
    var n = num(opts.count, 10), dx = num(opts.dx, 36), dy = num(opts.dy, 27), step = num(opts.stepF, 2);
    for (var i = st.copies.length + 1; i <= n; i++) {
      var c = win.cloneNode(true);
      c.style.left = r2(st.x + i * dx) + "px"; c.style.top = r2(st.y + i * dy) + "px";
      host.appendChild(c); st.copies.push(c);
    }
    st.copies.slice(0, n).forEach(function (c, i) { G().set(c, { opacity: 0, scale: 1 }); hard(tl, c, { opacity: 0 }, { opacity: 1 }, k + i * step); });
    return (k + (n - 1) * step + 1) / FPS;
  }
  // fx.errorSnapShut(tl, host, at, { frames: 3, stepF: 1 }): every window (the copies last-in first, then the original)
  // scales to 0 over 3f (power2.in), window i starting on f round(i x stepF) (0.5 = two windows a frame); each is gone
  // (opacity 0) when it reaches 0.
  function errorSnapShut(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), st = host.__fxErr;
    if (!st) throw new Error("RCK.fx.errorSnapShut: no window in " + (host.id || host.className));
    var all = [st.win].concat(st.copies).reverse(), k = frame(at), d = num(opts.frames, 3), step = num(opts.stepF, 1), end = k;
    all.forEach(function (w, i) {
      var f = k + Math.round(i * step);
      span(tl, w, { scale: 1 }, { scale: 0 }, f, d, "power2.in");
      hard(tl, w, { opacity: 1 }, { opacity: 0 }, f + d);
      end = f + d;
    });
    return end / FPS;
  }
  // fx.errorFlash(tl, host, at, { frames: 2 }): the window shows for exactly `frames` frames (B8 "breaks.").
  function errorFlash(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), win = errorWindow(host, opts), k = frame(at), n = num(opts.frames, 2);
    G().set(win, { opacity: 0 });
    hard(tl, win, { opacity: 0 }, { opacity: 1 }, k);
    hard(tl, win, { opacity: 1 }, { opacity: 0 }, k + n);
    return (k + n) / FPS;
  }

  /* ---------------- RGB split (text and DOM elements) + its footage counterpart ---------------- */
  // fx.rgbSplit(tl, target, at, { px: 9, frames: 6, settle: 0, until, every: 2, seed }): f0 .. frames-1 the split
  // narrows in hard steps from px to `settle`; settle > 0 = "never fully settles" (B2 / B16 "bug"): from then on it
  // keeps jittering around `settle` (+/- 1 px, a new value every `every` frames) until `until` (s; default the clip end).
  // Lockup words / text: red / cyan text-shadows (cheap); other elements: an SVG channel-split filter.
  function rgbSplit(tl, target, at, opts) {
    opts = opts || {};
    var k = frame(at), n = num(opts.frames, 6), px = num(opts.px, 9), settle = num(opts.settle, 0), every = num(opts.every, 2), end = k + n;
    $$(target).forEach(function (el0) {
      var isWord = el0.classList && el0.classList.contains("rc-lw"), el = isWord && RCK.type && RCK.type.fxInner ? RCK.type.fxInner(el0) : el0;
      var textOnly = isWord || !el.querySelector("*, img, video");
      var R = rng(num(opts.seed, seedOf((el0.id || el0.textContent) + k)));
      var val = function (a) {
        if (a <= 0) return textOnly ? { textShadow: "0px 0px 0px rgba(0, 0, 0, 0)" } : { filter: "none" };
        return textOnly ? { textShadow: r2(a) + "px 0px 0px rgba(255, 30, 70, 0.85), " + r2(-a) + "px 0px 0px rgba(0, 220, 255, 0.85), 0 6px 18px rgba(0, 0, 0, 0.45)" } : { filter: rgbFilter(Math.round(a)) };
      };
      var prev = val(0), seq = [];
      for (var j = 0; j < n; j++) seq.push(px + (settle - px) * (n > 1 ? j / (n - 1) : 1));
      if (settle > 0) {
        var stop = opts.until != null ? frame(opts.until) : (clipEndF(el0) || k + n + 30);
        for (var f = k + n; f < stop; f += every) seq.push(Math.max(1, settle + (R() < 0.5 ? -1 : 1) * Math.round(R() * 1.4)));
        end = Math.max(end, stop);
      }
      var fr = k;
      seq.forEach(function (a, j) { var v = val(a); var f2 = j < n ? k + j : k + n + (j - n) * every; hard(tl, el, prev, v, f2); prev = v; fr = f2; });
      if (settle <= 0) hard(tl, el, prev, val(0), k + n);
    });
    return end / FPS;
  }
  // fx.rgbGrading(px): the media-treatment payload for footage (channel separation; static), e.g. the B2 freeze frame:
  // npx --yes hyperframes@0.9.52 media-treatment --selector "#b02-freeze" --grading '<JSON>' --apply --json
  var CA_PER_PX = 0.0125;   // chromaticAberration per px at 1920 x 1080 (measured in _demo-v05, KIT_v05.md)
  function rgbGrading(px) { return { effects: { chromaticAberration: r2(Math.min(1, num(px, 9) * CA_PER_PX) * 1000) / 1000, chromaticAngle: 0 } }; }

  /* ---------------- highlighter sweep ---------------- */
  // fx.highlight(tl, el, at, { frames: 8, page: wrapper, pushTo: 1.10, pushF: 45, origin }): el = a .fx-hl box laid over
  // the line (class fx-hl--dark on a dark page = screen; default multiply for paper). Wipes left -> right over 8f
  // (power2.out); the page wrapper pushes 100 -> 110% from f0 over pushF frames (sine.inOut). Returns the wipe end.
  function highlight(tl, target, at, opts) {
    opts = opts || {};
    var els = $$(target), k = frame(at), d = num(opts.frames, 8);
    els.forEach(function (el) { G().set(el, { "--w": 0 }); span(tl, el, { "--w": 0 }, { "--w": 1 }, k, d, "power2.out"); });
    if (opts.page) {
      $$(opts.page).forEach(function (p) {
        G().set(p, { scale: 1, transformOrigin: opts.origin || "50% 50%", force3D: false });
        span(tl, p, { scale: 1 }, { scale: num(opts.pushTo, 1.1) }, k, num(opts.pushF, 45), "sine.inOut");
      });
    }
    return (k + d) / FPS;
  }

  /* ---------------- hand-drawn annotations (yellow marker; red strike) ---------------- */
  // fx.annotate(tl, host, at, { type: 'arrow' | 'circle' | 'underline' | 'strike', from: [x, y], to: [x, y] (arrow, underline,
  // strike), rect: [x, y, w, h] (circle; strike / underline across it), label, labelAt: [x, y], color, width: 9,
  // frames: 9 (strike 6), jitter: 1.5, jitterEvery: 2, seed }): drawn on by stroke trim (power2.out) over `frames`;
  // arrows draw the shaft over the first 70% then the head; a label hard-cuts in when the stroke ends; the whole mark
  // keeps a slight seeded jitter (a new +/- 1.5 px offset every 2 frames) until the host ends. Returns the draw end.
  function wob(R, a) { return (R() * 2 - 1) * a; }
  function annPath(o, R) {
    var t = o.type, P = function (p) { return r2(p[0]) + " " + r2(p[1]); };
    if (t === "circle") {
      var rc = o.rect, cx = rc[0] + rc[2] / 2, cy = rc[1] + rc[3] / 2, rx = rc[2] / 2 + num(o.pad, 22), ry = rc[3] / 2 + num(o.pad, 22);
      var a0 = -2.2, a1 = a0 + Math.PI * 2 + 0.55, pts = [];
      for (var i = 0; i <= 28; i++) { var a = a0 + (a1 - a0) * i / 28, sc = 1 + wob(R, 0.035) + (i / 28) * 0.06; pts.push([cx + Math.cos(a) * rx * sc, cy + Math.sin(a) * ry * sc]); }
      var d = "M" + P(pts[0]);
      for (var j = 1; j < pts.length; j++) { var m0 = pts[j - 1], m1 = pts[j]; d += " Q" + P(m0) + " " + P([(m0[0] + m1[0]) / 2, (m0[1] + m1[1]) / 2]); }
      return [d];
    }
    var from = o.from, to = o.to;
    if ((t === "strike" || t === "underline") && o.rect && !from) {
      var r = o.rect, yy = t === "strike" ? r[1] + r[3] * 0.55 : r[1] + r[3] + 14;
      from = [r[0] - 14, yy + (t === "strike" ? 6 : 0)]; to = [r[0] + r[2] + 14, yy - (t === "strike" ? 8 : 4)];
    }
    var dx = to[0] - from[0], dy = to[1] - from[1], L = Math.hypot(dx, dy), nx = -dy / L, ny = dx / L;
    var bend = t === "arrow" ? num(o.bend, 0.12) : 0.03, w = L * bend;
    var c1 = [from[0] + dx * 0.33 + nx * w + wob(R, 4), from[1] + dy * 0.33 + ny * w + wob(R, 4)];
    var c2 = [from[0] + dx * 0.7 + nx * w * 0.6 + wob(R, 4), from[1] + dy * 0.7 + ny * w * 0.6 + wob(R, 4)];
    var shaft = "M" + P(from) + " C" + P(c1) + " " + P(c2) + " " + P(to);
    if (t !== "arrow") return [shaft];
    var ang = Math.atan2(to[1] - c2[1], to[0] - c2[0]), hl = num(o.head, 46), sp = 0.5;
    var h1 = [to[0] - Math.cos(ang - sp) * hl + wob(R, 3), to[1] - Math.sin(ang - sp) * hl + wob(R, 3)];
    var h2 = [to[0] - Math.cos(ang + sp) * hl + wob(R, 3), to[1] - Math.sin(ang + sp) * hl + wob(R, 3)];
    return [shaft, "M" + P(h1) + " L" + P(to) + " L" + P(h2)];
  }
  function annotate(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), k = frame(at), type = opts.type || "arrow";
    var R = rng(num(opts.seed, seedOf((host.id || "a") + type)));
    var col = opts.color || (type === "strike" ? RED : YEL), d = num(opts.frames, type === "strike" ? 6 : 9);
    var s = svg("svg", { "class": "fx-ann__svg", viewBox: "0 0 1920 1080" }), g = svg("g", { filter: markerFilter() });
    s.appendChild(g); host.appendChild(s);
    var paths = annPath(Object.assign({ type: type }, opts), R).map(function (dd) {
      var p = svg("path", { d: dd, fill: "none", stroke: col, "stroke-width": num(opts.width, type === "strike" ? 11 : 9), "stroke-linecap": "round", "stroke-linejoin": "round", opacity: "0.96" });
      g.appendChild(p); return p;
    });
    var lens = paths.map(function (p) {
      var est = 0, nums = p.getAttribute("d").match(/-?\d+(\.\d+)?/g).map(Number);
      for (var q = 2; q + 1 < nums.length; q += 2) est += Math.hypot(nums[q] - nums[q - 2], nums[q + 1] - nums[q - 1]);
      var L = 0; try { L = p.getTotalLength(); } catch (e) { L = 0; }
      return Math.max(L || 0, est * 1.05);
    });
    paths.forEach(function (p, i) { p.setAttribute("stroke-dasharray", r2(lens[i] + 2) + " " + r2(lens[i] + 2)); G().set(p, { attr: { "stroke-dashoffset": r2(lens[i] + 2) } }); });
    var sF = paths.length > 1 ? Math.max(2, Math.round(d * 0.7)) : d;
    span(tl, paths[0], { attr: { "stroke-dashoffset": r2(lens[0] + 2) } }, { attr: { "stroke-dashoffset": 0 } }, k, sF, "power2.out");
    if (paths[1]) span(tl, paths[1], { attr: { "stroke-dashoffset": r2(lens[1] + 2) } }, { attr: { "stroke-dashoffset": 0 } }, k + sF, d - sF, "power2.out");
    if (opts.label) {
      var lb = mk("div", "fx-ann__label", opts.label), lp = opts.labelAt || [(opts.from || [960, 540])[0] - 40, (opts.from || [960, 540])[1] + 20];
      lb.style.left = lp[0] + "px"; lb.style.top = lp[1] + "px"; lb.style.color = col;
      host.appendChild(lb);
      hard(tl, lb, { opacity: 0 }, { opacity: 1 }, k + d);
    }
    var jit = num(opts.jitter, 1.5);
    if (jit > 0) {
      var stop = clipEndF(host) || k + d + 30, every = num(opts.jitterEvery, 2), px = 0, py = 0;
      for (var f = k; f < stop; f += every) { var nx2 = r2(wob(R, jit)), ny2 = r2(wob(R, jit)); hard(tl, g, { x: px, y: py }, { x: nx2, y: ny2 }, f); px = nx2; py = ny2; }
    }
    return (k + d) / FPS;
  }

  /* ---------------- card insert (archival 4:3 clip or image on a designed background) ---------------- */
  // fx.cardInsertHTML({ id, src, img: false, start, dur (s), mediaStart, x: 960, y: 540, w: 1080, h: 810, tilt: 3,
  // border: 15, bg: 'blur' | 'paper', bgScale: 1.3, blurPx: 60, darken: 0.5, z }) -> HTML (Node or browser). Background =
  // the same clip at 130%, blurred 60 px and darkened 50% through a media treatment (blur 1 = sigma 22.8 px per layout px,
  // so the copy is laid out at 1/k and scaled k = blurPx / 22.8; exposure log2(1 - darken)), or off-white paper. The
  // card: white 15 px border, 2-4 deg tilt, shadow 0 27px 60px 50%. Push it with RCK.cam.push(tl, '#ID .fx-card__cam', ...).
  var GRADING_BASE = '{"preset":null,"intensity":1,"adjust":{"exposure":EXPO,"contrast":0,"highlights":0,"shadows":0,"whites":0,"blacks":0,"temperature":0,"tint":0,"vibrance":0,"saturation":0},"effects":{"blur":1}}';
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }
  function tAttr(t) { return (Math.floor(Math.round(t * FPS + 1e-6) * 10000 / FPS + 1e-6) / 10000).toFixed(4); }
  function dAttr(t0, t1) { return ((Math.floor(Math.round(t1 * FPS + 1e-6) * 10000 / FPS + 1e-6) - Math.floor(Math.round(t0 * FPS + 1e-6) * 10000 / FPS + 1e-6)) / 10000).toFixed(4); }
  function media(tag, id, cls, o, extra) {
    var timing = ' data-start="' + tAttr(o.start) + '" data-duration="' + dAttr(o.start, o.start + o.dur) + '"';
    if (tag === "img") return '<img id="' + id + '" class="clip ' + cls + '" src="' + esc(o.src) + '"' + timing + (extra || "") + ' alt="">';
    return '<video id="' + id + '" class="clip ' + cls + '" src="' + esc(o.src) + '"' + timing + (o.mediaStart != null ? ' data-media-start="' + Number(o.mediaStart).toFixed(4) + '"' : "") + ' muted playsinline' + (extra || "") + "></video>";
  }
  function blurLayer(o, id, scaleCover) {
    var k = Math.max(1, num(o.blurPx, 60) / 22.8), cover = num(scaleCover, 1.3), W = 1920 * cover, H = 1080 * cover;
    var expo = r2(Math.log(Math.max(0.01, 1 - num(o.darken, 0.5))) / Math.LN2 * 1000) / 1000;
    var grading = GRADING_BASE.replace("EXPO", String(expo));
    var tag = o.img ? "img" : "video";
    return '<div class="fx-card__bgscale" data-layout-allow-overflow style="width: ' + r2(W / k) + 'px; height: ' + r2(H / k) + 'px; transform: translate(' + r2(-(W - 1920) / 2) + 'px, ' + r2(-(H - 1080) / 2) + 'px) scale(' + r2(k * 1000) / 1000 + ')">' +
      media(tag, id, "", o, " data-color-grading='" + grading + "'") + "</div>";
  }
  function cardInsertHTML(o) {
    o = Object.assign({ x: 960, y: 540, w: 1080, h: 810, tilt: 3, border: 15, bg: "blur", z: 1 }, o);
    if (!o.id || !o.src || o.start == null || o.dur == null) throw new Error("RCK.fx.cardInsertHTML: id, src, start, dur are required");
    var tag = o.img ? "img" : "video";
    var bg = o.bg === "paper"
      ? '<div id="' + o.id + '-paper" class="clip fx-fill fx-paper" data-start="' + tAttr(o.start) + '" data-duration="' + dAttr(o.start, o.start + o.dur) + '"></div>'
      : '<div class="fx-card__bgwrap">' + blurLayer(o, o.id + "-bg", o.bgScale) + "</div>";
    return '<div id="' + o.id + '" class="fx-card" style="z-index: ' + o.z + '">' + bg +
      '<div class="fx-card__cam" data-layout-allow-overflow><div class="fx-card__frame" style="left: ' + r2(o.x - o.w / 2) + 'px; top: ' + r2(o.y - o.h / 2) + 'px; width: ' + o.w + 'px; height: ' + o.h + 'px; transform: rotate(' + o.tilt + 'deg); --b: ' + o.border + 'px">' +
      '<div id="' + o.id + '-border" class="clip fx-card__border" data-start="' + tAttr(o.start) + '" data-duration="' + dAttr(o.start, o.start + o.dur) + '"></div>' +
      media(tag, o.id + "-fg", "fx-card__media", o) + "</div></div></div>";
  }
  // fx.darkCardHTML({ id, start, dur, src, img, mediaStart, opacity: 0.2, blurPx: 40, darken: 0.5, z }) -> HTML: the v05
  // dark card: #0E0E10, the footage loop blurred + darkened at 15-25% (media treatment), grain + the v04 scanlines on top.
  // Put the card's text (lockups) above it (higher z). Without src: base + texture only.
  function darkCardHTML(o) {
    o = Object.assign({ opacity: 0.2, blurPx: 40, darken: 0.5, z: 1 }, o);
    if (!o.id || o.start == null || o.dur == null) throw new Error("RCK.fx.darkCardHTML: id, start, dur are required");
    var timing = ' data-start="' + tAttr(o.start) + '" data-duration="' + dAttr(o.start, o.start + o.dur) + '"';
    return '<div id="' + o.id + '" class="fx-dark" style="z-index: ' + o.z + '">' +
      '<div id="' + o.id + '-base" class="clip fx-fill fx-dark__base"' + timing + "></div>" +
      (o.src ? '<div class="fx-dark__loop" style="opacity: ' + o.opacity + '">' + blurLayer(o, o.id + "-loop", 1.15) + "</div>" : "") +
      '<div id="' + o.id + '-tex" class="clip fx-fill fx-dark__tex"' + timing + "></div></div>";
  }
  // archival 1990s camera footage (G8): 1.5-3 px chromatic aberration + a light VHS line wobble (tape tracking), as a
  // media-treatment payload: npx --yes hyperframes@0.9.52 media-treatment --selector "<sel>" --grading '<JSON>' --apply --json
  function archivalGrading(o) {
    o = o || {};
    return { effects: { chromaticAberration: r2(Math.min(1, num(o.ca, 2) * CA_PER_PX) * 1000) / 1000, chromaticAngle: 0,
      tapeDamage: num(o.wobble, 0.18), tapeTracking: num(o.tracking, 0.22), tapeNoise: num(o.noise, 0.08), tapeSpeed: 0.5 } };
  }
  function archivalCmd(selector, o) { return "npx --yes hyperframes@0.9.52 media-treatment --selector \"" + selector + "\" --grading '" + JSON.stringify(archivalGrading(o)) + "' --apply --json"; }

  /* ---------------- slot-machine digit counter ---------------- */
  // fx.slotCounter(tl, host, at, { from: '18', to: '30', frames: 14, spins: [1, 2], size: 330, seed }): one column per
  // digit (Playfair Display Black, white); each strip rolls up through `spins` full turns to the target digit, landing
  // on f frames (the leftmost a few frames earlier) with expo.out; vertical motion blur follows the roll speed (an SVG
  // vertical gaussian, a new value each frame) and is gone on landing. Returns the landing time.
  function slotCounter(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), a = hostAnchor(host), k = frame(at), n = num(opts.frames, 14), size = num(opts.size, 330);
    var from = String(opts.from != null ? opts.from : "18"), to = String(opts.to != null ? opts.to : "30");
    var len = Math.max(from.length, to.length); from = from.padStart(len, " "); to = to.padStart(len, " ");
    var row = a.querySelector(".fx-slot__row");
    if (!row) { row = mk("div", "fx-slot__row"); row.style.fontSize = size + "px"; a.appendChild(row); }
    row.innerHTML = "";
    var lh = Math.round(size * 1.0), cols = [];
    for (var i = 0; i < len; i++) {
      var f0 = from.charAt(i) === " " ? 0 : +from.charAt(i), t0 = to.charAt(i) === " " ? 0 : +to.charAt(i);
      var spins = Array.isArray(opts.spins) ? num(opts.spins[i], 1) : num(opts.spins, 1 + (i === len - 1 ? 1 : 0));
      var steps = spins * 10 + ((t0 - f0 + 10) % 10), seq = [];
      for (var s = 0; s <= steps; s++) seq.push((f0 + s) % 10);
      var col = mk("div", "fx-slot__col"); col.style.height = lh + "px"; col.style.lineHeight = lh + "px";
      var strip = mk("div", "fx-slot__strip");
      seq.forEach(function (dg) { var sp = mk("span", null, String(dg)); sp.style.height = lh + "px"; strip.appendChild(sp); });
      col.appendChild(strip); row.appendChild(col);
      cols.push({ strip: strip, steps: steps, land: k + n - (len - 1 - i) * num(opts.staggerF, 3) });
    }
    cols.forEach(function (c) {
      var dF = c.land - k, E = G().parseEase("expo.out");
      G().set(c.strip, { y: 0 });
      span(tl, c.strip, { y: 0 }, { y: -c.steps * lh }, k, dF, "expo.out");
      var prevB = "none";
      for (var j = 0; j < dF; j++) {
        var v = (E((j + 1) / dF) - E(j / dF)) * c.steps * lh, b = vblurFilter(Math.min(28, v * 0.22));
        if (b !== prevB) { hard(tl, c.strip, { filter: prevB }, { filter: b }, k + j); prevB = b; }
      }
      if (prevB !== "none") hard(tl, c.strip, { filter: prevB }, { filter: "none" }, c.land);
    });
    return (k + n) / FPS;
  }

  /* ---------------- tear-off calendar page ---------------- */
  // fx.calendarTear(tl, host, at, { from: 'MAR 1995', to: 'NOV 1997', frames: 12, size: 300, theme: 'dark' | 'paper', seed }):
  // a pad (binding + rings) shows `from`; f0-2 the page lifts (rotation -3 deg, power2.out), f2-frames it rips off the
  // binding along a torn edge and falls out of frame turning around its top-right corner (power2.in), revealing `to`
  // (the beat may glowFlicker '#host .fx-cal__text--to'). Returns the end time.
  function tornEdge(R, n, depth) {
    var pts = [], i;
    for (i = 0; i <= n; i++) pts.push([r2(i * 100 / n), r2(R() * depth)]);
    return pts;
  }
  function calendarTear(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), a = hostAnchor(host), k = frame(at), n = num(opts.frames, 12), size = num(opts.size, 300);
    var from = opts.from || "MAR 1995", to = opts.to || "NOV 1997", R = rng(num(opts.seed, 1997));
    var tw = RCK.type && RCK.type.fontWidth ? Math.max(RCK.type.fontWidth("pf900", from, size), RCK.type.fontWidth("pf900", to, size)) : size * 4.6;
    var W = Math.round(tw + size * 0.55), H = Math.round(size * 1.45);
    host.classList.add(opts.theme === "paper" ? "fx-cal--paper" : "fx-cal--dark");
    var pad = mk("div", "fx-cal__pad"); pad.style.width = W + "px"; pad.style.height = H + "px";
    var under = mk("div", "fx-cal__page fx-cal__page--to"), over = mk("div", "fx-cal__page fx-cal__page--from");
    var tTo = mk("span", "fx-cal__text fx-cal__text--to", to), tFrom = mk("span", "fx-cal__text fx-cal__text--from", from);
    tTo.style.display = tFrom.style.display = "inline-block";
    under.appendChild(tTo); over.appendChild(tFrom);
    under.style.fontSize = over.style.fontSize = size + "px";
    var edge = tornEdge(R, 24, 2.6);                              // the tear line, % of the page height near the top
    var cut = 6;                                                  // the tear runs ~6% below the page top
    over.style.clipPath = "polygon(" + edge.map(function (p) { return p[0] + "% " + r2(cut + p[1]) + "%"; }).join(", ") + ", 100% 100%, 0% 100%)";
    var stub = mk("div", "fx-cal__page fx-cal__stub");
    stub.style.clipPath = "polygon(0% 0%, 100% 0%, " + edge.slice().reverse().map(function (p) { return p[0] + "% " + r2(cut + p[1]) + "%"; }).join(", ") + ")";
    var bind = mk("div", "fx-cal__bind");
    for (var i = 0; i < 6; i++) bind.appendChild(mk("span", "fx-cal__ring"));
    pad.appendChild(under); pad.appendChild(stub); pad.appendChild(over); pad.appendChild(bind);
    a.appendChild(pad);
    G().set(stub, { opacity: 0 });
    hard(tl, stub, { opacity: 0 }, { opacity: 1 }, k + 2);
    G().set(over, { rotation: 0, x: 0, y: 0, transformOrigin: "100% 0%" });
    span(tl, over, { rotation: 0, y: 0 }, { rotation: -3, y: -8 }, k, 2, "power2.out");
    span(tl, over, { rotation: -3, x: 0, y: -8 }, { rotation: -38, x: -260, y: 1100 }, k + 2, n - 2, "power2.in");
    return (k + n) / FPS;
  }

  /* ---------------- UK location tag ---------------- */
  // Simplified outline of Great Britain + Northern Ireland (hand-traced lon / lat, public-domain geography), projected
  // equirectangular with cos(55.5 deg). Dundee = 2.97 W, 56.46 N.
  var GB = [[-5.71,50.06],[-5.2,49.96],[-4.2,50.37],[-3.64,50.22],[-3.4,50.62],[-2.45,50.52],[-1.95,50.6],[-1.3,50.76],[-0.8,50.73],[0.25,50.74],[0.97,50.92],[1.38,51.13],[1.45,51.38],[0.7,51.48],[0.9,51.7],[1.28,51.85],[1.35,51.95],[1.75,52.48],[1.7,52.73],[1.3,52.93],[0.35,52.95],[0.15,53.1],[0.35,53.2],[0.12,53.58],[-0.08,54.12],[-0.6,54.48],[-1.15,54.62],[-1.38,54.9],[-1.6,55.4],[-2.0,55.77],[-2.13,55.92],[-2.5,56.0],[-3.05,55.98],[-3.7,56.03],[-2.8,56.2],[-2.58,56.28],[-2.8,56.35],[-3.25,56.37],[-2.85,56.46],[-2.58,56.56],[-2.47,56.72],[-2.08,57.15],[-1.78,57.5],[-2.0,57.69],[-3.0,57.68],[-4.2,57.5],[-3.8,57.85],[-3.4,58.13],[-3.09,58.44],[-3.03,58.64],[-3.37,58.67],[-4.4,58.55],[-5.0,58.62],[-5.3,58.25],[-5.16,57.9],[-5.7,57.6],[-5.7,57.28],[-5.65,56.95],[-6.23,56.73],[-5.47,56.42],[-5.6,56.0],[-5.79,55.3],[-5.4,55.85],[-4.9,55.95],[-4.75,55.6],[-4.63,55.46],[-5.0,55.0],[-4.86,54.64],[-4.4,54.85],[-3.6,54.95],[-3.2,54.9],[-3.62,54.5],[-2.9,54.07],[-3.05,53.82],[-3.05,53.4],[-3.6,53.3],[-4.3,53.42],[-4.6,53.25],[-4.4,53.15],[-4.75,52.8],[-4.08,52.41],[-4.7,52.1],[-5.3,51.88],[-5.1,51.7],[-4.2,51.55],[-3.17,51.45],[-2.7,51.6],[-3.0,51.2],[-3.5,51.22],[-4.53,51.02],[-4.95,50.55],[-5.71,50.06]];
  var NI = [[-5.43,54.6],[-5.7,54.95],[-6.05,55.2],[-6.6,55.22],[-7.3,55.15],[-7.7,54.7],[-8.15,54.45],[-7.6,54.1],[-6.9,54.2],[-6.4,54.05],[-5.9,54.22],[-5.5,54.35],[-5.43,54.6]];
  var DUNDEE = [-2.97, 56.46];
  function proj(p, sc, ox, oy) { var c = Math.cos(55.5 * Math.PI / 180); return [r2((p[0] + 8.3) * c * sc + ox), r2((59.0 - p[1]) * sc + oy)]; }
  // fx.locationTag(tl, host, at, { x: 96, y: 640 (box top-left), w: 260, h: 340, zoom: 3, frames: 12, label: 'DUNDEE',
  // pin: [lon, lat] }): the tag pops in on f0 (hard cut), the outline (white 3 px stroke, non-scaling) zooms 1 -> zoom
  // toward the pink pin over 12f (power2.inOut); the pin ring pulses on landing. Returns the landing time.
  function locationTag(tl, target, at, opts) {
    opts = opts || {};
    var host = $(target), k = frame(at), n = num(opts.frames, 12), W = num(opts.w, 260), H = num(opts.h, 340);
    var box = mk("div", "fx-loc__box"); box.style.left = num(opts.x, 96) + "px"; box.style.top = num(opts.y, 640) + "px"; box.style.width = W + "px"; box.style.height = H + "px";
    var sc = (H - 24) / 9.2, ox = 12, oy = 8;
    var s = svg("svg", { "class": "fx-loc__svg", width: W, height: H, viewBox: "0 0 " + W + " " + H });
    var g = svg("g", {}), pin = opts.pin || DUNDEE, pp = proj(pin, sc, ox, oy);
    var line = function (pts) { return "M" + pts.map(function (p) { var q = proj(p, sc, ox, oy); return q[0] + " " + q[1]; }).join(" L") + " Z"; };
    [GB, NI].forEach(function (shape) { g.appendChild(svg("path", { d: line(shape), fill: "rgba(255,255,255,0.08)", stroke: "#FFFFFF", "stroke-width": 3, "stroke-linejoin": "round", "vector-effect": "non-scaling-stroke" })); });
    s.appendChild(g);
    var ring = svg("circle", { cx: pp[0], cy: pp[1], r: 9, fill: "none", stroke: PINK, "stroke-width": 3 });
    var dot = svg("circle", { cx: pp[0], cy: pp[1], r: 7, fill: PINK, stroke: "#FFFFFF", "stroke-width": 2 });
    s.appendChild(ring); s.appendChild(dot);
    box.appendChild(s); host.appendChild(box);
    s.style.filter = "drop-shadow(0 3px 8px rgba(0,0,0,0.5))";
    if (opts.label) { var lb = mk("div", "fx-loc__label", opts.label); lb.style.left = (num(opts.x, 96) + 4) + "px"; lb.style.top = (num(opts.y, 640) + H + 10) + "px"; host.appendChild(lb); G().set(lb, { opacity: 0 }); hard(tl, lb, { opacity: 0 }, { opacity: 1 }, k + Math.round(n / 2)); }
    var z = num(opts.zoom, 3), cx = W / 2, cy = H / 2;
    G().set(box, { opacity: 0 });
    hard(tl, box, { opacity: 0 }, { opacity: 1 }, k);
    G().set(g, { scale: 1, x: 0, y: 0, svgOrigin: pp[0] + " " + pp[1] });
    span(tl, g, { scale: 1, x: 0, y: 0 }, { scale: z, x: r2(cx - pp[0]), y: r2(cy - pp[1]) }, k, n, "power2.inOut");
    span(tl, [ring, dot], { x: 0, y: 0 }, { x: r2(cx - pp[0]), y: r2(cy - pp[1]) }, k, n, "power2.inOut");
    G().set(ring, { scale: 1, opacity: 1, svgOrigin: pp[0] + " " + pp[1] });
    span(tl, ring, { scale: 1, opacity: 1 }, { scale: 3.2, opacity: 0 }, k + n - 2, 10, "power2.out");
    return (k + n) / FPS;
  }

  /* ---------------- VCR timestamp ---------------- */
  // fx.vcr(host, { text: 'MAR 22 1995', label: 'PLAY', x, y, right: 96, bottom: 70 }): "PLAY ▶ MAR 22 1995" in VT323 42 px,
  // white, bottom-right in title-safe (the triangle is drawn). Static; returns the OSD element.
  function vcr(target, opts) {
    opts = opts || {};
    var host = $(target);
    if (host.__fxVcr) return host.__fxVcr;
    var o = mk("div", "fx-vcr__osd");
    if (opts.x != null) { o.style.left = opts.x + "px"; o.style.top = num(opts.y, 960) + "px"; }
    else { o.style.right = num(opts.right, 96) + "px"; o.style.bottom = num(opts.bottom, 70) + "px"; }
    o.appendChild(mk("span", null, opts.label || "PLAY"));
    var tri = svg("svg", { "class": "fx-vcr__tri", viewBox: "0 0 12 14" }); tri.appendChild(svg("path", { d: "M0 0 L12 7 L0 14 Z", fill: "#FFFFFF" }));
    o.appendChild(tri);
    o.appendChild(mk("span", null, opts.text || host.getAttribute("data-text") || "MAR 22 1995"));
    host.appendChild(o);
    host.__fxVcr = o;
    return o;
  }

  /* ---------------- 3D Y-flip of a whole frame ---------------- */
  // fx.flipY(tl, root, at, { frames: 10, perspective: 2250, front: '.fx-flip__face--front', back: '.fx-flip__face--back',
  // blur: 0.6, ease: 'power2.inOut' }): root = an untimed wrapper holding two full-frame faces (class fx-flip__face);
  // front 0 -> 180 deg, back -180 -> 0 deg on Y (fastest at f5); motion blur = the faces' media-treatment blur ramp
  // (0 -> blur on f0-5 power2.in, back to 0 on f5-10 power2.out) on every <video>/<img> that carries
  // style="--hf-color-grading-blur: 0" and a data-color-grading with effects.blur. Returns the landing time.
  function flipY(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), k = frame(at), n = num(opts.frames, 10), e = easeOf(opts.ease, "power2.inOut");
    root.style.perspective = num(opts.perspective, 2250) + "px";
    var fr = root.querySelector(opts.front || ".fx-flip__face--front"), bk = root.querySelector(opts.back || ".fx-flip__face--back");
    if (fr) { G().set(fr, { rotationY: 0, transformOrigin: "50% 50%" }); span(tl, fr, { rotationY: 0 }, { rotationY: 180 }, k, n, e); }
    if (bk) { G().set(bk, { rotationY: -180, transformOrigin: "50% 50%" }); span(tl, bk, { rotationY: -180 }, { rotationY: 0 }, k, n, e); }
    mediaBlurRamp(tl, [fr, bk], k, n, num(opts.blur, 0.6));
    return (k + n) / FPS;
  }
  function mediaBlurRamp(tl, hosts, k, n, peak) {
    if (!(peak > 0)) return;
    var vids = [];
    hosts.forEach(function (h) { if (h) $$("video, img", h).forEach(function (v) { if (v.style.getPropertyValue("--hf-color-grading-blur") !== "") vids.push(v); }); });
    if (!vids.length) return;
    var h1 = Math.floor(n / 2);
    span(tl, vids, { "--hf-color-grading-blur": 0 }, { "--hf-color-grading-blur": peak }, k, h1, "power2.in");
    span(tl, vids, { "--hf-color-grading-blur": peak }, { "--hf-color-grading-blur": 0 }, k + h1, n - h1, "power2.out");
  }

  /* ---------------- whip-zoom / zoom-through with motion blur ---------------- */
  // fx.whipZoom(tl, outWrapper, at, { to: 4, frames: 8, origin: '960px 540px', blur: 0.8, in: wrapper, inFrom: 1.3, inF: 6 }):
  // the outgoing shot's wrapper scales 100 -> 400% over 8f centred on `origin` (expo.in) with its media blur ramping up;
  // the cut is on f8 (time the outgoing <video> to end there, the next to start there); the incoming wrapper lands from
  // inFrom to 100% over inF (expo.out) with its media blur ramping down. Returns the landing time.
  function whipZoom(tl, target, at, opts) {
    opts = opts || {};
    var out = $$(target), k = frame(at), n = num(opts.frames, 8), cut = k + n, peak = num(opts.blur, 0.8);
    out.forEach(function (o) {
      G().set(o, { scale: 1, transformOrigin: opts.origin || "50% 50%", force3D: false });
      span(tl, o, { scale: 1 }, { scale: num(opts.to, 4) }, k, n, "expo.in");
    });
    var vids = [];
    out.forEach(function (o) { $$("video, img", o).forEach(function (v) { if (v.style.getPropertyValue("--hf-color-grading-blur") !== "") vids.push(v); }); });
    if (vids.length && peak > 0) span(tl, vids, { "--hf-color-grading-blur": 0 }, { "--hf-color-grading-blur": peak }, k, n, "expo.in");
    var end = cut;
    if (opts["in"]) {
      var inn = $$(opts["in"]), nf = num(opts.inF, 6);
      inn.forEach(function (o) { G().set(o, { scale: num(opts.inFrom, 1.3), transformOrigin: opts.inOrigin || "50% 50%", force3D: false }); span(tl, o, { scale: num(opts.inFrom, 1.3) }, { scale: 1 }, cut, nf, "expo.out"); });
      var iv = [];
      inn.forEach(function (o) { $$("video, img", o).forEach(function (v) { if (v.style.getPropertyValue("--hf-color-grading-blur") !== "") iv.push(v); }); });
      if (iv.length && peak > 0) span(tl, iv, { "--hf-color-grading-blur": peak * 0.6 }, { "--hf-color-grading-blur": 0 }, cut, nf, "expo.out");
      end = cut + nf;
    }
    return end / FPS;
  }

  RCK.fx = {
    flash: flash, shake: shake, flashStar: flashStar, logoSlam: logoSlam, stamp: stamp,
    glitch: glitch, pill: pill, pillOut: pillOut, pillInit: pillInit,
    errorWindow: errorWindow, errorPop: errorPop, errorCascade: errorCascade, errorSnapShut: errorSnapShut, errorFlash: errorFlash, ERR_TEXT: ERR_TEXT,
    rgbSplit: rgbSplit, rgbGrading: rgbGrading, rgbFilter: rgbFilter,
    highlight: highlight, annotate: annotate,
    cardInsertHTML: cardInsertHTML, darkCardHTML: darkCardHTML, archivalGrading: archivalGrading, archivalCmd: archivalCmd,
    slotCounter: slotCounter, calendarTear: calendarTear, locationTag: locationTag, vcr: vcr, flipY: flipY, whipZoom: whipZoom,
    siren: function (tl, target, at, opts) { return RCK.type.sirenFlicker(tl, target, at, opts); },
    glowFlicker: function (tl, target, at, opts) { return RCK.type.glowFlicker(tl, target, at, opts); },
    PINK: PINK, YELLOW: YEL, RED: RED, BLUE: BLUE, CA_PER_PX: CA_PER_PX
  };
})();
