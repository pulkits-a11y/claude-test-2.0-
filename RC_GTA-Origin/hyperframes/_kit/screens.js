window.RCK = window.RCK || {}; RCK.FPS = 30; RCK.f = RCK.f || (n => n / 30); RCK.rng = RCK.rng || function (seed) { return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
/* RC_GTA-Origin style kit: SCREENS (L3, L4, L5, L6, L7, L11 + the B11 flip, L12; L10 year tag and L2 band are CSS).
   Docs: KIT_screens.md. Source: Master Edit Plan p.13-15 "Screen types (L1-L12)" + beat builds p.19-27.

   Every animation helper is pure:  RCK.screens.<helper>(tl, target, atSeconds, opts) -> endSeconds
   - adds tweens to the caller's paused GSAP timeline `tl`, nothing else (no timers, no Date, no Math.random:
     seeded RCK.rng only, no repeat:-1, no onUpdate);
   - `target` = selector string or Element written by the beat in its HTML (timed leaves carry class="clip");
   - times snap to the 30 fps grid. A tween placed at frame k shows its START state on frame k and its END state on
     frame k + d ("lands on k + d"); "ease out" = power3.out; v02 (REVISION_v02 rule C): nothing is linear any more,
     fades are power2.out / power2.in, held-shot pushes sine.inOut, drifts and parallax sine.inOut, the B6 rate ramp is
     sampled from power2.inOut; hard changes are 0.5-frame step tweens (cuts, not moves); opts.ease takes an
     easings.net name ('easeOutExpo') or a GSAP name, 'none' / 'linear' are refused;
   - v02 camera (rule D, also on RCK.cam): push / zoomOut across a held shot, punchIn on a cut, keyPunch on a keyword;
     transitions.js adds zoomThroughOut / zoomThroughIn. They scale an untimed picture wrapper, never the captions;
   - only untimed wrappers / children are transformed; start states are set with gsap.set at build time (each helper
     calls its idempotent init itself), never with CSS transforms; footage is never CSS-filtered (media treatments
     are animated through their documented CSS properties --hf-color-grading-*).
   Pure helpers (rateRamp, geometry) need no DOM / GSAP and run in Node:
     node -e "globalThis.window=globalThis; require('./assets/kit/screens.js'); console.log(RCK.screens.rateRamp({clipStart:0,at:1.4}))" */
(function () {
  'use strict';
  var FPS = 30, F = 1 / FPS, EASE_OUT = 'power3.out';
  function warn(msg) { if (window.console) console.warn('RCK.screens: ' + msg); }
  // easings.net name ('easeInOutSine') or GSAP name -> GSAP ease; 'none' / 'linear' are refused (rule C) -> dflt
  function easeOf(e, dflt) {
    if (e == null || e === '') e = dflt;
    if (typeof e === 'function') return e;
    if (/^(none|linear|power0(\.\w+)?)$/i.test(String(e).trim())) { warn('ease "' + e + '" is linear (REVISION_v02 rule C), using ' + dflt); e = dflt; }
    if (window.RCK && RCK.ease && RCK.ease.gsap) return RCK.ease.gsap(e);
    var m = /^ease(InOut|In|Out)(Sine|Quad|Cubic|Quart|Quint|Expo|Circ|Back|Elastic|Bounce)$/.exec(String(e));
    if (!m) return e;
    var fam = { Sine: 'sine', Quad: 'power1', Cubic: 'power2', Quart: 'power3', Quint: 'power4', Expo: 'expo', Circ: 'circ', Back: 'back', Elastic: 'elastic', Bounce: 'bounce' }[m[2]];
    return fam + '.' + (m[1] === 'InOut' ? 'inOut' : m[1].toLowerCase());
  }
  // pure ease curves for the no-GSAP helpers (rateRamp runs in Node): RCK.ease.fn when type.js is loaded, else these
  function easeFn(name) {
    if (window.RCK && RCK.ease && RCK.ease.fn) { var f = RCK.ease.fn(easeOf(name, 'power2.inOut')); if (f) return f; }
    var n = String(easeOf(name, 'power2.inOut'));
    if (n === 'sine.inOut') return function (x) { return -(Math.cos(Math.PI * x) - 1) / 2; };
    if (n === 'power1.inOut') return function (x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; };
    return function (x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };   // power2.inOut
  }
  var W = 1920, H = 1080;

  /* ---------------- frame grid ---------------- */
  function frame(t) { return Math.round(t * FPS + 1e-9); }
  function snap(t) { return frame(t) / FPS; }

  /* ---------------- DOM + GSAP plumbing ---------------- */
  function G() { if (!window.gsap) throw new Error('RCK.screens: GSAP not loaded'); return window.gsap; }
  function $(target, scope) {
    var e = typeof target === 'string' ? (scope || document).querySelector(target) : target;
    if (!e) throw new Error('RCK.screens: target not found: ' + target);
    return e;
  }
  function $$(target, scope) {   // selector -> all matches; Element -> [el]; array/NodeList -> array
    if (typeof target === 'string') return Array.prototype.slice.call((scope || document).querySelectorAll(target));
    if (target && target.length != null && !target.nodeType) return Array.prototype.slice.call(target);
    return target ? [target] : [];
  }
  function kids(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }
  function num(v, d) { var n = parseFloat(v); return isFinite(n) ? n : d; }
  function cssNum(el, name, d) { return num(window.getComputedStyle(el).getPropertyValue(name), d); }
  function seedOf(str) { var h = 2166136261; str = String(str); for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function shuffle(arr, rnd) { var a = arr.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  // a tween of d frames placed at frame k: frame k = `from`, frame k + d = `to` (ease required: nothing is linear)
  function span(tl, target, from, to, t, dF, ease) {
    var t0 = snap(t);
    tl.fromTo(target, from, Object.assign({ duration: dF / FPS, ease: easeOf(ease, 'power2.inOut'), immediateRender: false }, to), t0);
    return t0 + dF / FPS;
  }
  // hard change: frame n shows `to`, frame n-1 shows `from` (0.5-frame step tween placed strictly between the two frames)
  function hard(tl, target, from, to, t) {
    var n = frame(t), pos = (n - 0.75) / FPS;
    if (pos < 0) { G().set(target, to); return; }
    tl.fromTo(target, from, Object.assign({ duration: 0.5 / FPS, ease: 'steps(1)', immediateRender: false }, to), pos);
  }
  // earliest data-start of the timed leaves inside `el` (seconds), or null
  function windowStart(el) {
    var t = null;
    kids(el, '[data-start]').forEach(function (c) { var v = parseFloat(c.getAttribute('data-start')); if (isFinite(v) && (t === null || v < t)) t = v; });
    return t;
  }
  function endOf(at, opts, defF) {   // opts.until (s) or opts.durF (frames) -> end time on the frame grid
    if (opts.until != null) return snap(opts.until);
    return snap(at) + (opts.durF != null ? opts.durF : defF) / FPS;
  }

  /* ================================ v02 camera on a held shot (rule D) ================================ */
  // Every camera helper scales ONE untimed picture wrapper (footage / card inside; captions stay outside it, steady).
  // Moves on one wrapper must follow each other in time: each starts from the scale the previous move left (a registry
  // on the element; overlapping moves are reported with console.warn). A keyword punch during a push needs its own
  // nested wrapper:  <div class="rc-cam" id="b05-cam"><div class="rc-cam" id="b05-key"> picture </div></div>
  function camReg(el, kind, f0, f1, s0, s1) {
    var reg = el.__rcCam || (el.__rcCam = []), first = true, prev = null;
    reg.forEach(function (r) {
      if (f0 < r.f1 && r.f0 < f1) warn(kind + ' f' + f0 + '-' + f1 + ' overlaps ' + r.kind + ' f' + r.f0 + '-' + r.f1 + ' on #' + (el.id || el.className) + ': put one of them on a nested wrapper');
      if (r.f0 <= f0) first = false;
      if (r.f1 <= f0 && (!prev || r.f1 > prev.f1)) prev = r;
    });
    reg.push({ kind: kind, f0: f0, f1: f1, s0: s0, s1: s1 });
    return { first: first, prevScale: prev ? prev.s1 : null, entry: reg[reg.length - 1] };
  }
  // scale (+ optional x/y drift) of each element from vars0 to vars1 over [f0, f1], ease; registers the move and sets
  // the start state at build time only when it is the element's earliest move. Returns f1 in seconds.
  function camMove(tl, els, kind, f0, f1, s0, s1, ease, opts) {
    els.forEach(function (el) {
      var r = camReg(el, kind, f0, f1, s0, s1), v0 = { scale: s0 }, v1 = { scale: s1 };
      if (opts.x != null || opts.y != null) { v0.x = opts.x0 || 0; v0.y = opts.y0 || 0; v1.x = opts.x || 0; v1.y = opts.y || 0; }
      if (r.first) G().set(el, Object.assign({ transformOrigin: opts.origin || '50% 50%', force3D: false }, v0));
      else if (opts.origin) G().set(el, { transformOrigin: opts.origin });   // one origin per wrapper: it applies to every move
      tl.fromTo(el, v0, Object.assign({ duration: Math.max(1, f1 - f0) * F, ease: ease, force3D: false, immediateRender: false }, v1), f0 * F);
    });
    return f1 * F;
  }
  // Held shot push (v02 rule D: "push 100 -> 106-110% across the shot (sine.inOut) instead of v01's linear 104%"):
  // scales `target` (an untimed wrapper, or several: a selector matching all of them) from opts.from (1, or the scale a
  // previous move on the wrapper left) to opts.to (1.08) between `at` and opts.until (or at + durF), easeInOutSine
  // (opts.ease). opts.origin (centre), opts.x / opts.y: optional drift (px) on the same curve. Returns the end time.
  function push(tl, target, at, opts) {
    opts = opts || {};
    var els = $$(target), f0 = frame(at), f1 = frame(endOf(at, opts, 60));
    var prev = els[0] && els[0].__rcCam ? camPrev(els[0], f0) : null;
    var a = opts.from != null ? opts.from : (prev != null ? prev : 1), b = opts.to != null ? opts.to : a * 1.08;
    return camMove(tl, els, 'push', f0, f1, a, b, easeOf(opts.ease, 'sine.inOut'), opts);
  }
  function camPrev(el, f0) { var p = null; (el.__rcCam || []).forEach(function (r) { if (r.f1 <= f0 && (!p || r.f1 > p.f1)) p = r; }); return p ? p.s1 : null; }
  // The alternate held-shot move (rule D "alternate with slow zoom-outs (110 -> 100%)"): opts.from 1.10 -> opts.to 1.0,
  // sine.inOut, between `at` and opts.until. Returns the end time.
  function zoomOut(tl, target, at, opts) {
    opts = opts || {};
    return camMove(tl, $$(target), 'zoomOut', frame(at), frame(endOf(at, opts, 60)), opts.from != null ? opts.from : 1.10,
      opts.to != null ? opts.to : 1.0, easeOf(opts.ease, 'sine.inOut'), opts);
  }
  // Punch-in on a cut (rule D "cuts into a new shot: a punch-in that settles, 112-118% -> 100-102% over 8-12f, expo.out"):
  // frame `at` (the cut, the shot's first frame) shows opts.from (1.15), settling to opts.to (1.0) over opts.frames (10),
  // easeOutExpo: k 115% | k+1 107.5% | k+2 103.8% | k+3 101.9% | ... | k+10 100%. Returns the landing time.
  function punchIn(tl, target, at, opts) {
    opts = opts || {};
    var f0 = frame(at), N = opts.frames != null ? opts.frames : 10;
    return camMove(tl, $$(target), 'punchIn', f0, f0 + N, opts.from != null ? opts.from : 1.15, opts.to != null ? opts.to : 1.0, easeOf(opts.ease, 'expo.out'), opts);
  }
  // Keyword punch (rule D "a quick frame punch: content 100 -> 105-108% in 3-4f expo.out, back over 8-10f sine.inOut";
  // max about one punch per second): opts.peak (1.06) in opts.inF (3) frames, easeOutExpo, back to the base scale over
  // opts.outF (9) frames, easeInOutSine. opts.lead (1): the punch starts 1 frame before the word's onset frame, so the
  // onset frame already shows 105.4%: k-1 100% | k 105.4% | k+1 105.9% | k+2 106% (peak) | ... | k+11 100%. Put it on its
  // own wrapper when the shot also pushes (both drive scale). opts.base: the wrapper's resting scale (1). Returns the end.
  function keyPunch(tl, target, at, opts) {
    opts = opts || {};
    var els = $$(target), k = frame(at), lead = opts.lead != null ? opts.lead : 1, inF = opts.inF || 3, outF = opts.outF || 9;
    var base = opts.base != null ? opts.base : 1, peak = base * (opts.peak != null ? opts.peak : 1.06), f0 = Math.max(0, k - lead);
    els.forEach(function (el) {
      var r = camReg(el, 'keyPunch', f0, f0 + inF + outF, base, base);
      if (r.first) G().set(el, { scale: base, transformOrigin: opts.origin || '50% 50%', force3D: false });
      else if (opts.origin) G().set(el, { transformOrigin: opts.origin });
      tl.fromTo(el, { scale: base }, { scale: peak, duration: inF * F, ease: easeOf(opts.inEase, 'expo.out'), force3D: false, immediateRender: false }, f0 * F);
      tl.fromTo(el, { scale: peak }, { scale: base, duration: outF * F, ease: easeOf(opts.outEase, 'sine.inOut'), force3D: false, immediateRender: false }, (f0 + inF) * F);
    });
    return (f0 + inF + outF) * F;
  }

  /* ================================ L3 Grid build ================================ */
  // Cell rects from the grid's resolved tracks (layout px, independent of any GSAP scale already set on the cells).
  function gridRects(grid) {
    var g = $(grid), cs = window.getComputedStyle(g);
    var cols = cs.gridTemplateColumns.split(/\s+/).map(parseFloat).filter(isFinite);
    var rows = cs.gridTemplateRows.split(/\s+/).map(parseFloat).filter(isFinite);
    var cg = num(cs.columnGap, 8), rg = num(cs.rowGap, 8), out = [], y = 0;
    rows.forEach(function (rh) {
      var x = 0;
      cols.forEach(function (cw) { out.push({ x: x, y: y, w: cw, h: rh }); x += cw + cg; });
      y += rh + rg;
    });
    return out;
  }
  // One cell pops in: 4f, scale 96% -> 100% (ease out) with a fade 0 -> 1 (power2.out = easeOutCubic; v01 linear).
  // Frame k = invisible, k+4 = landed.
  // opts.punch (B9: 1.15): the cell's .rc-l3__media also punches in 100% -> punch over opts.punchF (4f, ease out).
  // Returns the landing time.
  function gridPop(tl, cell, at, opts) {
    opts = opts || {};
    var c = $(cell), d = opts.durF || 4, s0 = opts.from != null ? opts.from : 0.96, t0 = snap(at);
    G().set(c, { opacity: 0, scale: s0, transformOrigin: '50% 50%' });
    span(tl, c, { opacity: 0 }, { opacity: 1 }, t0, d, easeOf(opts.fadeEase, 'power2.out'));
    var end = span(tl, c, { scale: s0 }, { scale: 1 }, t0, d, EASE_OUT);
    if (opts.punch) {
      var m = c.querySelector('.rc-l3__media');
      if (!m) throw new Error('RCK.screens.gridPop: punch needs a .rc-l3__media wrapper in the cell');
      var pf = opts.punchF || 4;
      m.setAttribute('data-layout-allow-overflow', '');   // the punch-in overflows the cell on purpose (clipped)
      G().set(m, { scale: 1, transformOrigin: '50% 50%' });
      end = Math.max(end, span(tl, m, { scale: 1 }, { scale: opts.punch }, t0, pf, easeOf(opts.punchEase, EASE_OUT)));
    }
    return end;
  }
  // Every .rc-l3__cell of `grid` pops in turn: DOM order (= left to right, top to bottom) or opts.order (1-based cell
  // numbers), opts.stepF apart (3f), or at explicit opts.times (s, one per cell). Returns the last landing time.
  function gridBuild(tl, grid, at, opts) {
    opts = opts || {};
    var cells = kids($(grid), '.rc-l3__cell'), order = opts.order || cells.map(function (c, i) { return i + 1; });
    var step = opts.stepF != null ? opts.stepF : 3, end = snap(at);
    order.forEach(function (n, i) {
      var t = opts.times ? opts.times[i] : snap(at) + i * step / FPS;
      end = Math.max(end, gridPop(tl, cells[n - 1], t, opts));
    });
    return end;
  }
  // A cell scales up to full frame (B1: on "even GTA 6", cell 6 -> full frame over 6f, ease out).
  // `grow` = the .rc-l3__grow layer (its own clip(s) start at the switch, e.g. R17.1 replacing R1.3 in cell 6).
  // It starts clipped to the cell's rect with its picture cover-fitted to the cell, then the clip-path opens to the
  // frame while the picture scales to 100%, same ease, so the footage stays cover-fitted (never stretched).
  // opts.cell: 1-based cell number (default data-from-cell on the grow layer); opts.durF (6); opts.ease (power3.out).
  // Returns the time it fills the frame.
  function gridGrow(tl, grow, at, opts) {
    opts = opts || {};
    var g = $(grow), grid = g.closest('.rc-l3');
    if (!grid) throw new Error('RCK.screens.gridGrow: the .rc-l3__grow layer must sit inside its .rc-l3 grid');
    var n = opts.cell != null ? opts.cell : num(g.getAttribute('data-from-cell'), 0);
    var r = gridRects(grid)[n - 1];
    if (!r) throw new Error('RCK.screens.gridGrow: no cell ' + n);
    var gw = grid.clientWidth || W, gh = grid.clientHeight || H;
    var media = g.querySelector('.rc-l3__grow-media') || g.firstElementChild;
    var s0 = Math.max(r.w / gw, r.h / gh), dx = r.x + r.w / 2 - gw / 2, dy = r.y + r.h / 2 - gh / 2;
    var ins0 = 'inset(' + r.y + 'px ' + (gw - r.x - r.w) + 'px ' + (gh - r.y - r.h) + 'px ' + r.x + 'px)';
    var ins1 = 'inset(0px 0px 0px 0px)';
    var d = opts.durF || 6, ease = easeOf(opts.ease, EASE_OUT);
    G().set(g, { clipPath: ins0 });
    G().set(media, { x: dx, y: dy, scale: s0, transformOrigin: '50% 50%' });
    span(tl, g, { clipPath: ins0 }, { clipPath: ins1 }, at, d, ease);
    return span(tl, media, { x: dx, y: dy, scale: s0 }, { x: 0, y: 0, scale: 1 }, at, d, ease);
  }

  /* ================================ L4 Frosted tile grid ================================ */
  // Idempotent. Scales each .rc-l4__blurscale by k (--rc-l4-k, 1.76) from its top-left, generates the 12 tile
  // overlays inside .rc-l4__tiles if it is empty, and fixes the seeded clear order (data-seed / opts.seed / opts.order).
  function frostInit(frost, opts) {
    opts = opts || {};
    var root = $(frost);
    if (root.__rcsFrost) return root.__rcsFrost;
    var k = cssNum(root, '--rc-l4-k', 1.76);
    kids(root, '.rc-l4__blurscale').forEach(function (b) { G().set(b, { scale: k, transformOrigin: '0px 0px' }); });
    var host = root.querySelector('.rc-l4__tiles');
    if (host && !host.querySelector('.rc-l4__tile')) {
      for (var i = 0; i < 12; i++) { var d = document.createElement('div'); d.className = 'rc-l4__tile'; d.setAttribute('data-tile', String(i)); host.appendChild(d); }
    }
    var tiles = host ? kids(host, '.rc-l4__tile') : [];
    var seed = opts.seed != null ? opts.seed : num(root.getAttribute('data-seed'), seedOf(root.id || 'rc-l4'));
    var order = opts.order ? opts.order.slice() : shuffle([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], RCK.rng(seed));
    var mask = root.querySelector('.rc-l4__frost');
    if (tiles.length) G().set(tiles, { opacity: 1 });
    var st = { root: root, mask: mask, tiles: tiles, order: order, next: 0, k: k };
    root.__rcsFrost = st;
    return st;
  }
  // One tile clears over opts.durF (3f, power2.out = easeOutCubic: the sharp picture "fades in"; v01 linear): its frosted
  // copy (mask alpha --rc-l4-a<i>) and its overlay + border fade 1 -> 0 together. tile = 0..11, row-major (0 = top-left,
  // 11 = bottom-right). Returns the clear time.
  function frostClearTile(tl, frost, tile, at, opts) {
    opts = opts || {};
    var st = frostInit(frost, opts), d = opts.durF || 3, a = {}, b = {};
    a['--rc-l4-a' + tile] = 1; b['--rc-l4-a' + tile] = 0;
    var e = easeOf(opts.ease, 'power2.out');
    if (st.mask) span(tl, st.mask, a, b, at, d, e);
    if (st.tiles[tile]) span(tl, st.tiles[tile], { opacity: 1 }, { opacity: 0 }, at, d, e);
    return snap(at) + d / FPS;
  }
  // Tiles clear one at a time in the seeded random order, one per entry of `times` (s; e.g. each spoken word's
  // comp_t). Successive calls continue the same order. Returns the time the last tile is clear.
  function frostClear(tl, frost, times, opts) {
    opts = opts || {};
    var st = frostInit(frost, opts), end = 0;
    if (st.next === 0 && (opts.seed != null || opts.order))   // the first call may (re)seed the order
      st.order = opts.order ? opts.order.slice() : shuffle([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], RCK.rng(opts.seed));
    (Array.isArray(times) ? times : [times]).forEach(function (t) {
      var tile = st.order[st.next % 12]; st.next++;
      end = Math.max(end, frostClearTile(tl, frost, tile, t, opts));
    });
    return end;
  }

  /* ================================ L5 Gray card collage ================================ */
  var CUTOUT_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute;width:0;height:0" aria-hidden="true">' +
    // 8 px white outline around the cut-out's alpha (round: blur sigma 4, threshold at alpha 2.5% = ~1.96 sigma = 8 px),
    // then the L5 soft shadow (0, 12 px, CSS blur 30 px = sigma 15, black 25%) under the outlined silhouette.
    '<filter id="rcs-l5-cutout" x="-20%" y="-20%" width="140%" height="150%" color-interpolation-filters="sRGB">' +
    '<feGaussianBlur in="SourceAlpha" stdDeviation="4" result="a"/>' +
    '<feComponentTransfer in="a" result="dil"><feFuncA type="linear" slope="40" intercept="-0.5"/></feComponentTransfer>' +
    '<feFlood flood-color="#FFFFFF" result="w"/><feComposite in="w" in2="dil" operator="in" result="outline"/>' +
    '<feGaussianBlur in="dil" stdDeviation="15" result="sb"/><feOffset in="sb" dx="0" dy="12" result="so"/>' +
    '<feFlood flood-color="#000000" flood-opacity="0.25"/><feComposite in2="so" operator="in" result="shadow"/>' +
    '<feMerge><feMergeNode in="shadow"/><feMergeNode in="outline"/><feMergeNode in="SourceGraphic"/></feMerge></filter>' +
    '<filter id="rcs-l5-cutout-shadow" x="-20%" y="-20%" width="140%" height="150%" color-interpolation-filters="sRGB">' +
    '<feGaussianBlur in="SourceAlpha" stdDeviation="15" result="sb"/><feOffset in="sb" dx="0" dy="12" result="so"/>' +
    '<feFlood flood-color="#000000" flood-opacity="0.25"/><feComposite in2="so" operator="in" result="shadow"/>' +
    '<feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge></filter></svg>';
  // Injects the cut-out matte filters once (#rcs-l5-cutout, #rcs-l5-cutout-shadow). Called automatically on load when
  // the page has a .rc-l5__cutout; safe to call again.
  function cutoutInit() {
    if (typeof document === 'undefined' || document.getElementById('rcs-l5-cutout')) return;
    var holder = document.createElement('div');
    holder.innerHTML = CUTOUT_SVG;
    var svg = holder.firstChild;
    svg.setAttribute('data-layout-ignore', '');
    (document.body || document.documentElement).appendChild(svg);
  }
  var PROP_ROT = [-4, 4];
  // Idempotent: static tilt of a prop (data-rot, opts.rot, else -4 / +4 alternating by opts.index).
  function propInit(prop, opts) {
    opts = opts || {};
    var p = $(prop);
    if (p.__rcsProp) return p.__rcsProp;
    var rot = opts.rot != null ? opts.rot : num(p.getAttribute('data-rot'), PROP_ROT[(opts.index || 0) % 2]);
    G().set(p, { rotation: rot, transformOrigin: '50% 50%' });
    p.__rcsProp = { rot: rot };
    return p.__rcsProp;
  }
  // A prop floats +/-6 px (opts.amp) on a sine path: one leg (-6 -> +6 px) takes opts.legS (2 s), then back.
  // y(t) = -amp * cos(phase + PI * (t - at) / legS); phase seeded (opts.phase in radians, else from opts.seed / the id).
  // Each leg is exactly easeInOutSine (rule C "float loops: sine.inOut"); the custom ease only chains the legs.
  // From `at` until opts.until (required, s). Returns opts.until.
  function propFloat(tl, prop, at, opts) {
    opts = opts || {};
    var p = $(prop); propInit(p, opts);
    if (opts.until == null) throw new Error('RCK.screens.propFloat: opts.until is required');
    var amp = opts.amp != null ? opts.amp : 6, leg = opts.legS || 2, t0 = snap(at), t1 = snap(opts.until), D = Math.max(F, t1 - t0);
    var phase = opts.phase != null ? opts.phase : 2 * Math.PI * RCK.rng(opts.seed != null ? opts.seed : seedOf(p.id || 'rc-l5-prop'))();
    var fn = function (q) { return -Math.cos(phase + Math.PI * D * q / leg); };
    G().set(p, { y: amp * fn(0) });
    tl.fromTo(p, { y: 0 }, { y: amp, duration: D, ease: fn, immediateRender: false }, t0);
    return t1;
  }
  // Tilts and floats every .rc-l5__prop inside `root` (alternating -4 / +4 unless data-rot), each with its own seeded
  // phase (opts.seed + index). Returns opts.until.
  function collage(tl, root, at, opts) {
    opts = opts || {};
    var base = opts.seed != null ? opts.seed : seedOf(($(root).id) || 'rc-l5');
    kids($(root), '.rc-l5__prop').forEach(function (p, i) {
      propInit(p, { index: i, rot: opts.rot });
      propFloat(tl, p, at, { until: opts.until, amp: opts.amp, legS: opts.legS, seed: base + 101 * (i + 1) });
    });
    return snap(opts.until);
  }

  /* ================================ L6 Framed clip ================================ */
  // Idempotent: scales the back copy's .rc-l6__blurscale by k (--rc-l6-k, 2.2) from its top-left so the media
  // treatment blur (sigma 22.8 px per layout px at effects.blur = 1) reads 50 px on screen.
  function framedInit(root) {
    var r = $(root);
    if (r.__rcsFramed) return r.__rcsFramed;
    var k = cssNum(r, '--rc-l6-k', 2.2);
    kids(r, '.rc-l6__blurscale').forEach(function (b) { G().set(b, { scale: k, transformOrigin: '0px 0px' }); });
    r.__rcsFramed = { k: k };
    return r.__rcsFramed;
  }

  /* ================================ L7 Spotlight ================================ */
  var spotCount = 0;
  function holeOf(dim, opts) {
    var h = (opts.hole || dim.getAttribute('data-hole') || '').toString().split(/[\s,]+/).map(parseFloat);
    if (h.length !== 4 || h.some(function (v) { return !isFinite(v); })) throw new Error('RCK.screens.spot: data-hole="x,y,w,h" (frame px) required on ' + (dim.id || '.rc-l7__dim'));
    return { x: h[0], y: h[1], w: h[2], h: h[3] };
  }
  // Idempotent. Builds the dim inside .rc-l7__dim: #0A0A0A at 65% (picture shows at 35%) with a rounded hole
  // (data-hole="x,y,w,h" in frame px, data-radius 16, data-feather 20 = Gaussian sigma feather / 4, i.e. the edge ramps
  // 2.5% -> 97.5% over ~20 px centred on the box edge). Returns {dim, rect, hole, cx, cy}.
  function spotInit(target, opts) {
    opts = opts || {};
    var t = $(target), root = t.classList.contains('rc-l7') ? t : (t.closest('.rc-l7') || t);
    var dim = root.classList.contains('rc-l7__dim') ? root : (root.querySelector('.rc-l7__dim') || t);
    if (dim.__rcsSpot) return dim.__rcsSpot;
    var b = holeOf(dim, opts);
    var rad = opts.radius != null ? opts.radius : num(dim.getAttribute('data-radius'), 16);
    var fea = opts.feather != null ? opts.feather : num(dim.getAttribute('data-feather'), 20);
    var dimA = opts.dim != null ? opts.dim : num(dim.getAttribute('data-dim'), 0.65);
    var id = 'rcs-l7-' + (dim.id || ('n' + (++spotCount)));
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('width', String(W)); svg.setAttribute('height', String(H)); svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML =
      '<defs><filter id="' + id + '-f" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">' +
      '<feGaussianBlur stdDeviation="' + (fea / 4) + '"/></filter>' +
      '<mask id="' + id + '-m" maskUnits="userSpaceOnUse" x="0" y="0" width="' + W + '" height="' + H + '">' +
      '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#FFFFFF"/>' +
      '<rect class="rc-l7__hole" x="' + b.x + '" y="' + b.y + '" width="' + b.w + '" height="' + b.h + '" rx="' + rad + '" ry="' + rad + '" fill="#000000" filter="url(#' + id + '-f)"/>' +
      '</mask></defs>' +
      '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#0A0A0A" fill-opacity="' + dimA + '" mask="url(#' + id + '-m)"/>';
    dim.appendChild(svg);
    var st = { root: root, dim: dim, svg: svg, rect: svg.querySelector('.rc-l7__hole'), hole: b, cx: b.x + b.w / 2, cy: b.y + b.h / 2 };
    dim.__rcsSpot = st;
    return st;
  }
  // Push in 100% -> 118% towards the target across the beat: scales the .rc-l7 root (picture + dim + anything inside
  // it, e.g. the T9 highlight) about the hole's centre, sine.inOut (v02; v01 linear; opts.ease), from `at` to opts.until
  // (or at + durF). opts.from (1) / opts.to (1.18). Returns the end time.
  function spotPush(tl, target, at, opts) {
    opts = opts || {};
    var st = spotInit(target, opts);
    return push(tl, st.root, at, { until: opts.until, durF: opts.durF, from: opts.from != null ? opts.from : 1, to: opts.to != null ? opts.to : 1.18,
      ease: easeOf(opts.ease, 'sine.inOut'), origin: st.cx + 'px ' + st.cy + 'px' });
  }
  // Optional: move / resize the spotlight box to opts.hole "x,y,w,h" over opts.durF (12f), ease opts.ease (power3.out).
  // Note: the push origin stays where spotInit put it. Returns the end time.
  function spotMove(tl, target, at, opts) {
    opts = opts || {};
    var st = spotInit(target, opts), b = holeOf(st.dim, { hole: opts.hole }), d = opts.durF || 12;
    return span(tl, st.rect, { attr: { x: st.hole.x, y: st.hole.y, width: st.hole.w, height: st.hole.h } },
      { attr: { x: b.x, y: b.y, width: b.w, height: b.h } }, at, d, easeOf(opts.ease, EASE_OUT));
  }

  /* ================================ L11 Split screen ================================ */
  function faces(root) {
    var r = $(root);
    return { root: r, front: r.querySelector('.rc-l11__face--front'), back: r.querySelector('.rc-l11__face--back') };
  }
  function media(el) { return el ? kids(el, 'video, img') : []; }
  // Idempotent: front face at 0 deg, back face at -180 deg (hidden: backface-visibility).
  function splitInit(root) {
    var f = faces(root);
    if (f.root.__rcsSplit) return f.root.__rcsSplit;
    if (f.front) G().set(f.front, { rotationY: 0, transformOrigin: '50% 50%' });
    if (f.back) G().set(f.back, { rotationY: -180, transformOrigin: '50% 50%' });
    f.root.__rcsSplit = f;
    return f;
  }
  // B11: the whole split screen rotates 180 deg on Y over opts.durF (10f), ease opts.ease (power2.inOut: fastest at
  // the 90 deg midpoint, frame k+5). Motion blur (seek-safe approximation): every face <video>/<img> that carries a
  // media treatment with effects.blur and an inline style="--hf-color-grading-blur: 0" ramps that blur 0 -> opts.blur
  // (1 = sigma 22 px) over the first half (power2.in) and back to 0 over the second half (power2.out).
  // opts.blur = 0 skips it. Returns the landing time (k + 10).
  function splitFlip(tl, root, at, opts) {
    opts = opts || {};
    var f = splitInit(root), d = opts.durF || 10, ease = easeOf(opts.ease, 'power2.inOut'), t0 = snap(at), end = t0 + d / FPS;
    if (f.front) span(tl, f.front, { rotationY: 0 }, { rotationY: 180 }, t0, d, ease);
    if (f.back) span(tl, f.back, { rotationY: -180 }, { rotationY: 0 }, t0, d, ease);
    var peak = opts.blur != null ? opts.blur : 1;
    if (peak > 0) {
      var vids = media(f.front).concat(media(f.back)).filter(function (v) { return v.style.getPropertyValue('--hf-color-grading-blur') !== ''; });
      if (vids.length) {
        var half = (d / 2) / FPS;
        tl.fromTo(vids, { '--hf-color-grading-blur': 0 }, { '--hf-color-grading-blur': peak, duration: half, ease: 'power2.in', immediateRender: false }, t0);
        tl.fromTo(vids, { '--hf-color-grading-blur': peak }, { '--hf-color-grading-blur': 0, duration: half, ease: 'power2.out', immediateRender: false }, t0 + half);
      }
    }
    return end;
  }
  // B6 "dull": the split screen drains to black and white over opts.durF (6f, power2.inOut = easeInOutCubic: a colour
  // change between two rests; v01 linear). Every <video>/<img> of the face
  // (opts.face 'front' | 'back' | 'both', default 'front') must carry the media treatment {"adjust":{"saturation":-1}}
  // and an inline style="--hf-color-grading-intensity: 0"; this tweens that intensity 0 -> 1. Returns the end time.
  function splitDrain(tl, root, at, opts) {
    opts = opts || {};
    var f = splitInit(root), which = opts.face || 'front', d = opts.durF || 6;
    var vids = (which === 'back' ? [] : media(f.front)).concat(which === 'front' ? [] : media(f.back));
    if (!vids.length) throw new Error('RCK.screens.splitDrain: no media in the face');
    return span(tl, vids, { '--hf-color-grading-intensity': 0 }, { '--hf-color-grading-intensity': opts.to != null ? opts.to : 1 }, at, d, easeOf(opts.ease, 'power2.inOut'));
  }
  // data-automation value for a seek-safe speed change on a <video> (HyperFrames `rate` lane, t in clip seconds).
  // {clipStart (the video's data-start, s), at (composition s where the change starts), from 1, to 0.5, durF 6
  //  (0 = a step), ease ('power2.inOut' = easeInOutCubic; v01 one linear segment), clipDur (optional: adds an end
  //  point)} -> JSON string to paste into data-automation='...'. v02: the ramp is sampled from the ease every 1/4 frame
  // (the runtime interpolates between points), so the speed follows the curve, not a straight line.
  // In Node, require type.js first if you name a curve other than sine.inOut / power1.inOut / power2.inOut.
  function rateRamp(o) {
    o = o || {};
    var a = Math.max(0, snap(o.at) - (o.clipStart || 0)), dF = o.durF != null ? o.durF : 6, d = dF / FPS;
    var from = o.from != null ? o.from : 1, to = o.to != null ? o.to : 0.5, r4 = function (v) { return Math.round(v * 10000) / 10000; };
    var pts = [{ t: 0, v: from }, { t: r4(a), v: from }];
    if (dF > 0) {
      var E = easeFn(o.ease), n = Math.max(1, Math.round(dF * 4));
      for (var i = 1; i <= n; i++) pts.push({ t: r4(a + d * i / n), v: r4(from + (to - from) * E(i / n)) });
    } else pts.push({ t: r4(a + 0.001), v: to });
    if (o.clipDur != null && o.clipDur > a + d) pts.push({ t: r4(o.clipDur), v: to });
    return JSON.stringify({ version: 1, lanes: [{ target: 'rate', points: pts }] });
  }

  /* ================================ L12 Stacked cards ================================ */
  var CARD_ROT = [-6, 3, -2];
  // Idempotent: each .rc-l12__card (DOM order) gets its tilt on its .rc-l12__drop (data-rot, else -6 / +3 / -2,
  // repeating) and the off-screen start of its drop (fully above the frame, tilt included).
  function cardsInit(root) {
    var r = $(root);
    if (r.__rcsCards) return r.__rcsCards;
    var cards = kids(r, '.rc-l12__card');
    cards.forEach(function (c, i) {
      var drop = c.querySelector('.rc-l12__drop') || c;
      var rot = num(c.getAttribute('data-rot'), CARD_ROT[i % 3]);
      var off = -(c.offsetTop + c.offsetHeight + 12 + 60 + Math.abs(Math.sin(rot * Math.PI / 180)) * c.offsetWidth / 2);
      drop.__rcsDrop = { rot: rot, off: off };
      G().set(drop, { rotation: rot, transformOrigin: '50% 50%' });
    });
    r.__rcsCards = { cards: cards };
    return r.__rcsCards;
  }
  // One card drops in from above the frame onto its spot: opts.durF (8f), ease out. From the start of the card's own
  // clips (its earliest data-start, or opts.from) until frame k it waits off-screen; frame k+8 = landed. Outside its
  // clips' window it rests at its spot (invisible: its leaves are timed). `card` = a .rc-l12__card. Returns landing time.
  function cardDrop(tl, card, at, opts) {
    opts = opts || {};
    var c = $(card), root = c.closest('.rc-l12');
    if (root) cardsInit(root);
    var drop = c.querySelector('.rc-l12__drop') || c, info = drop.__rcsDrop || { off: -(c.offsetTop + c.offsetHeight + 72) };
    var off = opts.fromY != null ? opts.fromY : info.off, t0 = snap(at);
    var w0 = opts.from != null ? snap(opts.from) : windowStart(c);
    if (w0 !== null && frame(w0) < frame(t0)) hard(tl, drop, { y: 0 }, { y: off }, w0);
    return span(tl, drop, { y: off }, { y: 0 }, t0, opts.durF || 8, easeOf(opts.ease, EASE_OUT));
  }
  // Cards drop in one at a time, DOM order (bottom card first): each takes 8f and starts when the previous lands
  // (opts.stepF, default = durF), or at explicit opts.times. Returns the last landing time.
  function cardsDrop(tl, root, at, opts) {
    opts = opts || {};
    var st = cardsInit(root), d = opts.durF || 8, step = opts.stepF != null ? opts.stepF : d, end = snap(at);
    st.cards.forEach(function (c, i) {
      var t = opts.times ? opts.times[i] : snap(at) + i * step / FPS;
      end = Math.max(end, cardDrop(tl, c, t, opts));
    });
    return end;
  }
  // Slow parallax drift: card i (DOM order, bottom -> top) drifts opts.px[i] px along x (default 8, 16, 24, 32: the top
  // card moves most) and opts.py[i] px along y (default 0), sine.inOut (v02; v01 linear), from `at` to opts.until.
  // Returns opts.until.
  function cardsDrift(tl, root, at, opts) {
    opts = opts || {};
    var st = cardsInit(root);
    if (opts.until == null) throw new Error('RCK.screens.cardsDrift: opts.until is required');
    var t0 = snap(at), t1 = snap(opts.until), D = Math.max(F, t1 - t0);
    st.cards.forEach(function (c, i) {
      var dx = opts.px ? opts.px[i] : -8 * (i + 1), dy = opts.py ? opts.py[i] : 0;
      G().set(c, { x: 0, y: 0 });
      tl.fromTo(c, { x: 0, y: 0 }, { x: dx, y: dy, duration: D, ease: easeOf(opts.ease, 'sine.inOut'), immediateRender: false }, t0);
    });
    return t1;
  }

  /* ================================ geometry (no DOM) ================================ */
  var GEOM = {
    L2: { bar: 138, bandTop: 138, bandBottom: 942, bandHeight: 804, slideF: 8 },
    L3: { gutter: 8, cell3x2: { w: (1920 - 16) / 3, h: (1080 - 8) / 2 }, strip: { w: (1920 - 16) / 3, h: 1080 },
      colX: [0, (1920 - 16) / 3 + 8, 2 * ((1920 - 16) / 3 + 8)], rowY: [0, (1080 - 8) / 2 + 8] },
    L4: { cols: 4, rows: 3, tileW: 480, tileH: 360, blurSigmaPerK: 22.8, k: 1.76 },
    L6: { scale: 0.62, w169: 1190.4, w43: 892.8, h: 669.6, k: 2.2, exposure: -0.737 },
    L7: { dim: 0.65, radius: 16, feather: 20, push: 1.18 },
    L10: { x: 96, y: 54, fontSize: 22 },
    L11: { half: 958, divider: 4, rightX: 962, perspective: 2666.67, flipF: 10 },
    L12: { border: 12, rot: CARD_ROT.slice(), dropF: 8 },
    safe: { x: 96, y: 54 }
  };

  RCK.screens = {
    FPS: FPS, frame: frame, snap: snap, geom: GEOM, hard: hard, ease: easeOf,
    // v02 camera (rule D; also RCK.cam)
    push: push, zoomOut: zoomOut, punchIn: punchIn, keyPunch: keyPunch, camReg: camReg,
    // L3
    gridRects: gridRects, gridPop: gridPop, gridBuild: gridBuild, gridGrow: gridGrow,
    // L4
    frostInit: frostInit, frostClearTile: frostClearTile, frostClear: frostClear,
    // L5
    cutoutInit: cutoutInit, propInit: propInit, propFloat: propFloat, collage: collage,
    // L6
    framedInit: framedInit,
    // L7
    spotInit: spotInit, spotPush: spotPush, spotMove: spotMove,
    // L11
    splitInit: splitInit, splitFlip: splitFlip, splitDrain: splitDrain, rateRamp: rateRamp,
    // L12
    cardsInit: cardsInit, cardDrop: cardDrop, cardsDrop: cardsDrop, cardsDrift: cardsDrift
  };

  RCK.cam = RCK.cam || {};
  RCK.cam.push = push; RCK.cam.zoomOut = zoomOut; RCK.cam.punchIn = punchIn; RCK.cam.keyPunch = keyPunch;

  // Static inits that need no timeline: L4 blur scale + tiles, L6 blur scale, L5 cut-out filters, L7 dims, L11 faces,
  // L12 tilts (no hidden states: cells / cards are hidden only once the beat calls gridPop / cardDrop).
  // They run once when the script loads (scripts sit at the end of <body>), so a screen looks right even before the
  // beat calls any helper; the helpers call the same idempotent inits.
  if (typeof document !== 'undefined' && document.querySelector) {
    try {
      if (document.querySelector('.rc-l5__cutout')) cutoutInit();
      if (window.gsap) {
        $$('.rc-l4').forEach(function (e) { frostInit(e); });
        $$('.rc-l6').forEach(function (e) { framedInit(e); });
        $$('.rc-l7__dim[data-hole]').forEach(function (e) { spotInit(e); });
        $$('.rc-l11').forEach(function (e) { splitInit(e); });
        $$('.rc-l12').forEach(function (e) { cardsInit(e); });
      }
    } catch (e) { if (window.console) console.error(e); }
  }
})();
