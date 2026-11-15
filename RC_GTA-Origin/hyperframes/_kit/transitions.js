window.RCK = window.RCK || {}; RCK.FPS = 30; RCK.f = RCK.f || (n => n / 30); RCK.rng = RCK.rng || function (seed) { return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };

/* RC_GTA-Origin style kit: TRANSITIONS (transitions.js). Docs, markup, timing and per-beat use: KIT_transitions.md.
   Source: Master Edit Plan p.15-16 "Transitions (X1-X9)" + "Into each beat", and the beat builds (p.19-28).

   X1 hard cut    = a data-start boundary, no helper.          X8 whip pan = Tesseract (not here).
   X2 drift       RCK.transitions.drift        incoming clip slides 40-80 px sideways over 20f, ease out
   X3 white flash RCK.transitions.flash        100% white: ramp 2f, hold 1f, fade 4f, centred on the cut
   X4 block tear  RCK.transitions.tear         16 x 9 blocks jump +/-30 px, some freeze on the old frame, 6 px RGB split, then cut
   X5 blinds      RCK.transitions.blindsClose / blindsOpen   12 vertical slats rotate shut / open, 8f each way
   X6 zoom        RCK.transitions.zoom (+ zoomFit, zoomGeometry)   100% <-> 600% over 8f with motion blur
   X7 light leak  RCK.transitions.leakDissolve 12-16f dissolve through a light-leak overlay (Screen blend)
   X9 siren wash  RCK.transitions.sirenWash    4f overlay: #E3262E at 35% (Overlay) 2f, then #2D5BFF 2f

   Conventions (kit-wide):
   - Every timeline helper is pure: helper(tl, target, atSeconds, opts) -> endSeconds. It only adds tweens/sets to the
     caller's paused GSAP timeline (start states are written with gsap.set at build time). No Date.now(), no Math.random()
     (RCK.rng(seed)), no timers, no repeat:-1, never display/visibility/autoAlpha on a .clip.
   - Times snap to the 30 fps grid. A hard change "on frame n" is a 0.5-frame tween placed strictly between frames n-1 and
     n, so frame n always shows the new state and frame n-1 the old one, whatever order the renderer seeks in.
   - Helpers animate only the opacity of the element you pass, and transforms/colours of its children (or of a plain,
     untimed wrapper), so the HyperFrames .clip rules hold. Elements are written in the HTML by the beat; init helpers only
     add untimed child markup (slats, leak layers, canvas).
   - No CSS filter ever touches footage: X6's motion blur on <video>/<img> uses the media-treatment blur control
     (--hf-color-grading-blur, the documented seek-safe animation contract); CSS blur only on non-media DOM. */
(function () {
  'use strict';

  var FPS = 30, F = 1 / FPS, FW = 1920, FH = 1080;

  /* ---------------------------------------------------------------- utilities */
  function frame(t) { return Math.round(t * FPS + 1e-9); }            // seconds -> nearest frame index
  function snap(t) { return frame(t) / FPS; }                          // seconds -> seconds on the frame grid
  function tF(n) { return n / FPS; }                                   // frame index -> seconds
  function G() { if (!window.gsap) throw new Error('RCK.transitions: GSAP not loaded'); return window.gsap; }
  function $(target, scope) {
    var e = typeof target === 'string' ? (scope || document).querySelector(target) : (target && target.jquery ? target[0] : target);
    if (!e) throw new Error('RCK.transitions: target not found: ' + target);
    return e;
  }
  function $$(target, scope) {
    if (!target) return [];
    if (typeof target === 'string') return Array.prototype.slice.call((scope || document).querySelectorAll(target));
    if (target.length != null && !target.nodeType) return Array.prototype.slice.call(target);
    return [target];
  }
  function mk(tag, cls) { var e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function num(v, d) { return v === undefined || v === null || v === '' || isNaN(+v) ? d : +v; }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function warn(msg) { if (window.console) console.warn('RCK.transitions: ' + msg); }
  function seedOf(str) { var h = 2166136261; str = String(str || 'rck'); for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  // Hard change landing ON frame n: a 0.5-frame tween between frames n-1 and n (frame n-1 = from, frame n = to).
  function hard(tl, target, from, to, n) {
    var pos = (n - 0.75) / FPS;
    if (pos < 0) { G().set(target, to); return; }
    tl.fromTo(target, from, Object.assign({ duration: 0.5 / FPS, ease: 'none', immediateRender: false }, to), pos);
  }
  // Non-tweenable property (clip-path strings) changing ON frame n: a set strictly between frames n-1 and n.
  function setOn(tl, target, vars, n) {
    var pos = (n - 0.5) / FPS;
    if (pos < 0) { G().set(target, vars); return; }
    tl.set(target, vars, pos);
  }
  function readyKey(prefix, el) { return 'rck-' + prefix + '-' + (el.id || seedOf(el.outerHTML.slice(0, 200))); }
  function registerReady(key, promise) {
    window.__hf = window.__hf || {};
    window.__hf.buildReady = window.__hf.buildReady || {};
    window.__hf.buildReady[key] = promise;
  }
  function clipEndOf(el) {   // seconds where the element's nearest timed ancestor (itself included) ends, or null
    for (var e = el; e && e.getAttribute; e = e.parentElement) {
      var s = e.getAttribute('data-start'), d = e.getAttribute('data-duration');
      if (s != null && d != null && !isNaN(+s) && !isNaN(+d) && !e.hasAttribute('data-composition-id')) return +s + +d;
    }
    return null;
  }
  function boxSize(el) {
    var w = el.offsetWidth || parseFloat(el.style.width) || FW, h = el.offsetHeight || parseFloat(el.style.height) || FH;
    return { w: w, h: h };
  }

  /* ================================================================ X2 cut, then drift */
  // After the cut the incoming clip slides px (40-80, default 60) sideways over 20f, ease out (power3.out), landing on
  // its designed position. dir 'left' = moves right-to-left (starts +px), 'right' = starts -px. `target` = a plain wrapper
  // inside the incoming clip (never the .clip itself). at = the cut frame. Returns at + 20f (landed).
  function drift(tl, target, at, opts) {
    opts = opts || {};
    var el = $(target), n0 = frame(at), N = num(opts.frames, 20), px = num(opts.px, 60);
    if (px < 40 || px > 80) warn('drift: px ' + px + ' is outside the plan range 40-80');
    var x0 = (opts.dir || 'left') === 'right' ? -px : px;
    G().set(el, { x: x0 });
    tl.fromTo(el, { x: x0 }, { x: 0, duration: N * F, ease: opts.ease || 'power3.out', immediateRender: false }, tF(n0));
    return tF(n0 + N);
  }

  /* ================================================================ X3 white flash */
  // 100% white (#FFFFFF): ramp 2f, hold 1f, fade out 4f, centred on the cut. at = the cut frame C (the first frame of the
  // new picture, the frame the flash "lands"). Linear opacity keyframes at C-2 (0), C (1), C+1 (1), C+5 (0), so the frames
  // read C-2 0% | C-1 50% | C 100% | C+1 100% | C+2 75% | C+3 50% | C+4 25% | C+5 0%.
  // opts.half: 'out' = only the ramp, then holds 100% (outgoing composition of a boundary flash); 'in' = 100% from the
  // clip start, hold, fade (incoming composition). Default: whole flash. Returns C + 5f (C for half 'out').
  function flash(tl, target, at, opts) {
    opts = opts || {};
    var el = $(target), c = frame(at), r = num(opts.ramp, 2), h = num(opts.hold, 1), f = num(opts.fade, 4), half = opts.half;
    G().set(el, { opacity: half === 'in' ? 1 : 0 });
    if (half !== 'in') tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: r * F, ease: 'none', immediateRender: false }, tF(Math.max(0, c - r)));
    if (half === 'out') return tF(c);
    tl.fromTo(el, { opacity: 1 }, { opacity: 0, duration: f * F, ease: 'none', immediateRender: false }, tF(c + h));
    return tF(c + h + f);
  }

  /* ================================================================ X4 pixel-block tear */
  // Pure plan of the tear (no DOM): per frame, each of the cols x rows blocks is 'freeze' (old frame, in place, stays
  // frozen once frozen), 'jump' (displaced by integer dx, dy in [-jump, +jump]) or 'pass' (in place: the old frame in
  // still mode, the live picture in live mode, dropped out to the gap colour with opts.gap).
  // opts: frames 8 (6-10), cols 16, rows 9, jump 30, freeze 0.25 (share of blocks frozen by the last frame), pJump 0.7
  // (of the non-frozen blocks), seed, views K (live mode: jump blocks are dealt to K groups, one shared dx/dy per group).
  function tearPlan(opts) {
    opts = opts || {};
    var N = num(opts.frames, 8), cols = num(opts.cols, 16), rows = num(opts.rows, 9), J = num(opts.jump, 30);
    var pF = num(opts.freeze, 0.25), pJ = num(opts.pJump, 0.7), K = num(opts.views, 0);
    if (N < 6 || N > 10) warn('tear: ' + N + 'f is outside the plan range 6-10f');
    var rnd = RCK.rng(num(opts.seed, 4));
    var nb = cols * rows, freezeAt = [];
    for (var b = 0; b < nb; b++) freezeAt.push(rnd() < pF ? Math.floor(rnd() * N) : Infinity);
    var off = function () { return Math.round((rnd() * 2 - 1) * J); };
    var frames = [];
    for (var k = 0; k < N; k++) {
      var groups = [];
      for (var g = 0; g < K; g++) groups.push({ dx: off(), dy: off() });
      var blocks = [];
      for (var i = 0; i < nb; i++) {
        var role = freezeAt[i] <= k ? 'freeze' : (rnd() < pJ ? 'jump' : 'pass');
        var blk = { i: i, c: i % cols, r: Math.floor(i / cols), role: role, dx: 0, dy: 0, g: -1 };
        if (role === 'jump') {
          if (K > 0) { blk.g = Math.floor(rnd() * K); blk.dx = groups[blk.g].dx; blk.dy = groups[blk.g].dy; }
          else { blk.dx = off(); blk.dy = off(); }
        }
        blocks.push(blk);
      }
      frames.push({ k: k, blocks: blocks, groups: groups });
    }
    return { frames: N, cols: cols, rows: rows, jump: J, frameList: frames };
  }

  // Markup (the beat writes it):  <div id="b8-x4" class="rc-x4" style="left:0;top:0;width:1920px;height:1080px">
  //   <img class="rc-x4__still" src="assets/x4/b8-old.png" alt="">          (a) still of the old frame (container size)
  //   <div class="rc-x4__view">...a live copy of the picture...</div>      (b) optional live views, 0..K
  // </div>
  // tearInit adds the canvas, sizes it, and registers a window.__hf.buildReady promise (the still is decoded and split
  // into R/G/B planes before the first seek). Idempotent.
  function tearInit(target, opts) {
    opts = opts || {};
    var root = $(target);
    if (root.__rckTear) return root.__rckTear;
    var sz = boxSize(root);
    var still = root.querySelector('img.rc-x4__still');
    var views = $$('.rc-x4__view', root);
    var cv = root.querySelector('canvas.rc-x4__canvas');
    if (!cv) {
      cv = mk('canvas', 'rc-x4__canvas');
      cv.setAttribute('aria-hidden', 'true');
      cv.setAttribute('data-layout-ignore', '');
      root.appendChild(cv);
    }
    cv.width = Math.round(sz.w); cv.height = Math.round(sz.h);
    G().set(cv, { opacity: 0 });
    views.forEach(function (v) { G().set(v, { opacity: 0, x: 0, y: 0 }); });
    var st = { root: root, w: Math.round(sz.w), h: Math.round(sz.h), still: still, views: views, canvas: cv, ctx: cv.getContext('2d'), planes: null, work: null };
    var prep = function () {
      if (!still) return;
      var mkc = function () { var c = document.createElement('canvas'); c.width = st.w; c.height = st.h; return c; };
      st.planes = ['#FF0000', '#00FF00', '#0000FF'].map(function (mask) {      // channel masks (technical, never shown as colours)
        var c = mkc(), x = c.getContext('2d');
        x.drawImage(still, 0, 0, st.w, st.h);
        x.globalCompositeOperation = 'multiply'; x.fillStyle = mask; x.fillRect(0, 0, st.w, st.h);
        x.globalCompositeOperation = 'destination-in'; x.drawImage(still, 0, 0, st.w, st.h);
        return c;
      });
      st.work = [mkc(), mkc(), mkc(), mkc()];   // three torn channel planes + the split composite
    };
    if (still) {
      var loaded = still.complete && still.naturalWidth ? Promise.resolve() : new Promise(function (res, rej) {
        still.addEventListener('load', res, { once: true });
        still.addEventListener('error', function () { rej(new Error('X4 still failed to load: ' + still.getAttribute('src'))); }, { once: true });
      });
      st.ready = loaded.then(function () { return still.decode ? still.decode().catch(function () {}) : null; }).then(prep);
      registerReady(readyKey('x4', root), st.ready);
      st.ready.then(function () { if (st.redraw) st.redraw(); });   // preview only: redraw once the still arrives
    } else {
      st.ready = Promise.resolve();
    }
    root.__rckTear = st;
    return st;
  }

  function rectPath(list) { return list.map(function (r) { return 'M' + r[0] + ',' + r[1] + 'h' + r[2] + 'v' + r[3] + 'h' + (-r[2]) + 'z'; }).join(''); }

  // X4: `frames` (6-10, default 8) frames from `at` (the first torn frame), then cut. The block grid covers opts.grid
  // [x, y, w, h] (container px; default the whole container) in cols x rows (16 x 9); the container clips to its box.
  // Still mode (no views): the torn picture = the old frame in place (every block that does not jump is frozen on it)
  // with the jumping blocks on top, each displaced by its own dx, dy in [-30, +30]; with opts.gap (a colour, e.g.
  // 'var(--ink-black)') the base is that colour and only frozen + jumping blocks are drawn (the rest drop out: a shatter).
  // The 6 px RGB split (opts.rgb; red +6 px, blue -6 px like T10) is applied to that whole torn picture after the tear,
  // clamped and clipped to the grid, so displaced edges fringe and flat areas stay flat.
  // Live mode (.rc-x4__view copies present): jumping blocks show the live views (K views = K shared offsets per frame,
  // clip-path windows; split them with media-treatment chromaticAberration), frozen blocks come from the split still (if
  // any), the rest shows the original picture under the container. opts.end: 'cut' (default: nothing of the tear from
  // at+frames on; the caller's hard cut lands there) or 'hold' (keeps the last torn frame until opts.until seconds, else
  // until the nearest timed ancestor ends, else for good). Returns at + frames.
  function tear(tl, target, at, opts) {
    opts = opts || {};
    var st = tearInit(target, opts), g = G();
    var n0 = frame(at), N = num(opts.frames, 8);
    var grid = opts.grid || [0, 0, st.w, st.h];
    var cols = num(opts.cols, 16), rows = num(opts.rows, 9), rgb = num(opts.rgb, 6);
    var K = st.views.length;
    var seed = opts.seed != null ? opts.seed : seedOf(st.root.id || 'x4');
    var plan = tearPlan({ frames: N, cols: cols, rows: rows, jump: num(opts.jump, 30), freeze: num(opts.freeze, st.still ? 0.25 : 0),
      pJump: num(opts.pJump, 0.7), seed: seed, views: K });
    var bw = grid[2] / cols, bh = grid[3] / rows;
    var cell = function (b) {   // integer block rect (edges shared exactly between neighbours)
      var x0 = Math.round(grid[0] + b.c * bw), y0 = Math.round(grid[1] + b.r * bh);
      return [x0, y0, Math.round(grid[0] + (b.c + 1) * bw) - x0, Math.round(grid[1] + (b.r + 1) * bh) - y0];
    };
    var gap = opts.gap ? String(opts.gap) : null;
    if (gap && gap.indexOf('var(') === 0) gap = getComputedStyle(document.documentElement).getPropertyValue(gap.slice(4, -1).trim()).trim() || '#0A0A0A';
    var gapRGB = null;
    if (gap) {   // the gap colour's three channel planes (it is split like the rest of the torn picture)
      var pc = document.createElement('canvas').getContext('2d');
      pc.fillStyle = gap; pc.fillRect(0, 0, 1, 1);
      var px = pc.getImageData(0, 0, 1, 1).data;
      gapRGB = ['rgb(' + px[0] + ',0,0)', 'rgb(0,' + px[1] + ',0)', 'rgb(0,0,' + px[2] + ')'];
    }
    var hold = opts.end === 'hold';
    var clipGrid = function (x) { x.beginPath(); x.rect(grid[0], grid[1], grid[2], grid[3]); x.clip(); };
    // RGB split of a whole torn picture held as three channel planes: red +rgb px, blue -rgb px, clamped at the grid
    // edges (the uncovered rgb-px strip repeats the edge column, so no coloured band appears at the region border).
    var compose = function (planes, dst) {
      var sx = dst.getContext('2d'), gx = grid[0], gw = grid[2];
      sx.setTransform(1, 0, 0, 1, 0, 0);
      sx.globalCompositeOperation = 'source-over';
      sx.clearRect(0, 0, st.w, st.h);
      sx.save(); clipGrid(sx);
      sx.drawImage(planes[0], rgb, 0);
      if (rgb > 0) sx.drawImage(planes[0], gx, 0, 1, st.h, gx, 0, rgb, st.h);
      sx.globalCompositeOperation = 'lighter';
      sx.drawImage(planes[1], 0, 0);
      sx.drawImage(planes[2], -rgb, 0);
      if (rgb > 0) sx.drawImage(planes[2], gx + gw - 1, 0, 1, st.h, gx + gw - rgb, 0, rgb, st.h);
      sx.restore();
    };
    // live mode: frozen blocks are cut from the still AFTER its split (no false fringes against the live picture)
    var splitStill = function () {
      if (!st.splitStill) { st.splitStill = document.createElement('canvas'); st.splitStill.width = st.w; st.splitStill.height = st.h; compose(st.planes, st.splitStill); }
      return st.splitStill;
    };

    var proxy = { f: 0 };
    var draw = function () {
      var ctx = st.ctx;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, 0, st.w, st.h);
      if (!st.planes) return;
      var k = clamp(Math.floor(proxy.f + 1e-6), 0, N - 1), fr = plan.frameList[k];
      var r;
      if (K) {
        var ss = splitStill();
        ctx.save(); clipGrid(ctx);
        fr.blocks.forEach(function (b) { if (b.role === 'freeze') { r = cell(b); ctx.drawImage(ss, r[0], r[1], r[2], r[3], r[0], r[1], r[2], r[3]); } });
        ctx.restore();
        return;
      }
      // still mode: the torn picture = base + jumping blocks on top, built per channel plane, then split as a whole.
      // base = the old frame in place (every block that does not jump is frozen on it), or with opts.gap the gap colour
      // with the frozen blocks in place (non-jumping, non-frozen blocks drop out to the gap colour).
      for (var ch = 0; ch < 3; ch++) {
        var x = st.work[ch].getContext('2d');
        x.setTransform(1, 0, 0, 1, 0, 0);
        x.globalCompositeOperation = 'source-over';
        x.clearRect(0, 0, st.w, st.h);
        x.save(); clipGrid(x);
        if (gapRGB) {
          x.fillStyle = gapRGB[ch]; x.fillRect(grid[0], grid[1], grid[2], grid[3]);
          fr.blocks.forEach(function (b) { if (b.role === 'freeze') { r = cell(b); x.drawImage(st.planes[ch], r[0], r[1], r[2], r[3], r[0], r[1], r[2], r[3]); } });
        } else {
          x.drawImage(st.planes[ch], 0, 0);
        }
        fr.blocks.forEach(function (b) { if (b.role === 'jump') { r = cell(b); x.drawImage(st.planes[ch], r[0], r[1], r[2], r[3], r[0] + b.dx, r[1] + b.dy, r[2], r[3]); } });
        x.restore();
      }
      compose(st.work, st.work[3]);
      ctx.drawImage(st.work[3], 0, 0);
    };
    st.redraw = draw;
    // 'cut': the tear layer is gone on frame at+frames. 'hold': it stays until opts.until (seconds), else the end of the
    // nearest timed ancestor of the container, else for good (the container itself is untimed).
    var nEnd = n0 + N;
    if (hold) {
      var until = opts.until != null ? opts.until : clipEndOf(st.root);
      nEnd = until != null ? Math.max(n0 + N, frame(until)) : null;
    }
    g.set(st.canvas, { opacity: 0 });
    hard(tl, st.canvas, { opacity: 0 }, { opacity: 1 }, n0);
    tl.fromTo(proxy, { f: 0 }, { f: N, duration: N * F, ease: 'none', immediateRender: false, onUpdate: draw }, tF(n0));
    if (nEnd != null) hard(tl, st.canvas, { opacity: 1 }, { opacity: 0 }, nEnd);

    // live views: per frame, view j shows its blocks (clip-path) shifted by its group's offset
    if (K) {
      var none = 'path("M0,0z")';
      st.views.forEach(function (v) { g.set(v, { clipPath: none, x: 0, y: 0, opacity: 0 }); });
      st.views.forEach(function (v) { hard(tl, v, { opacity: 0 }, { opacity: 1 }, n0); });
      plan.frameList.forEach(function (fr, k) {
        st.views.forEach(function (v, j) {
          var rects = fr.blocks.filter(function (b) { return b.role === 'jump' && b.g === j; }).map(cell);
          setOn(tl, v, { clipPath: rects.length ? 'path("' + rectPath(rects) + '")' : none, x: fr.groups[j].dx, y: fr.groups[j].dy }, n0 + k);
        });
      });
      if (nEnd != null) st.views.forEach(function (v) { hard(tl, v, { opacity: 1 }, { opacity: 0 }, nEnd); });
    }
    return tF(n0 + N);
  }

  /* ================================================================ X5 blinds wipe */
  // 12 vertical slats (160 px each on 1920) of ink black #0A0A0A rotating about their own vertical centre line.
  // Shut = rotationY 0 (the frame is covered); open = +/-90 (edge-on, invisible).
  function blindsInit(target, opts) {
    opts = opts || {};
    var root = $(target), n = num(opts.slats, 12);
    var slats = $$('.rc-x5__slat', root);
    if (slats.length !== n) {
      slats.forEach(function (s) { s.parentNode.removeChild(s); });
      var sz = boxSize(root), w = sz.w / n;
      for (var i = 0; i < n; i++) {
        var s = mk('div', 'rc-x5__slat');
        s.setAttribute('aria-hidden', 'true');
        s.setAttribute('data-layout-ignore', '');
        // integer edges, each slat 1 px wider on the right so shut slats leave no hairline seam
        var x0 = Math.round(i * w), x1 = Math.round((i + 1) * w);
        s.style.left = x0 + 'px'; s.style.width = (x1 - x0 + (i < n - 1 ? 1 : 0)) + 'px';
        root.appendChild(s);
      }
      slats = $$('.rc-x5__slat', root);
    }
    if (opts.color) slats.forEach(function (s) { s.style.background = opts.color; });
    return slats;
  }
  // Ease: none by default = constant angular speed (11.25 deg a frame), one continuous rotation +90 -> 0 -> -90 through
  // the shut point, so the two halves (two compositions) join seamlessly and all 8 frames of each half visibly move.
  // OUTGOING half: slats rotate shut over the 8f before the boundary (frames B-8..B-1 animate, shut from B on and held
  // through the tail handle). at = the boundary B (local time of the incoming beat's first frame). Returns at.
  function blindsClose(tl, target, at, opts) {
    opts = opts || {};
    var slats = blindsInit(target, opts), b = frame(at), N = num(opts.frames, 8), p = num(opts.perspective, 1000);
    G().set(slats, { rotationY: 90, transformPerspective: p, transformOrigin: '50% 50%' });
    tl.fromTo(slats, { rotationY: 90 }, { rotationY: 0, duration: N * F, ease: opts.ease || 'none', immediateRender: false }, tF(b - N));
    return tF(b);
  }
  // INCOMING half: shut from the clip start (head handle) to the boundary B, then rotate open over 8f (B..B+8; slats gone
  // from B+8). Returns at + 8f.
  function blindsOpen(tl, target, at, opts) {
    opts = opts || {};
    var slats = blindsInit(target, opts), b = frame(at), N = num(opts.frames, 8), p = num(opts.perspective, 1000);
    G().set(slats, { rotationY: 0, transformPerspective: p, transformOrigin: '50% 50%', opacity: 1 });
    tl.fromTo(slats, { rotationY: 0 }, { rotationY: -90, duration: N * F, ease: opts.ease || 'none', immediateRender: false }, tF(b));
    hard(tl, slats, { opacity: 1 }, { opacity: 0 }, b + N);
    return tF(b + N);
  }
  // Both halves in one composition (demo / a blinds wipe that does not sit on a beat boundary): shut at `at`, open after.
  function blinds(tl, target, at, opts) {
    opts = opts || {};
    var slats = blindsInit(target, opts), b = frame(at), N = num(opts.frames, 8), p = num(opts.perspective, 1000);
    G().set(slats, { rotationY: 90, transformPerspective: p, transformOrigin: '50% 50%', opacity: 1 });
    tl.fromTo(slats, { rotationY: 90 }, { rotationY: 0, duration: N * F, ease: (opts.easeClose || 'none'), immediateRender: false }, tF(b - N));
    tl.fromTo(slats, { rotationY: 0 }, { rotationY: -90, duration: N * F, ease: (opts.easeOpen || 'none'), immediateRender: false }, tF(b));
    hard(tl, slats, { opacity: 1 }, { opacity: 0 }, b + N);
    return tF(b + N);
  }

  /* ================================================================ X6 zoom through a screen */
  // Geometry (no DOM). screen = {rect: [x, y, w, h]} or {corners: [[x,y] TL, TR, BR, BL]} in 1920 x 1080 frame px.
  // The world scales about origin P = (S*c - F0) / (S - 1) (c = screen centre, F0 = frame centre), so at scale S the screen
  // centre sits on the frame centre. fill = the smallest scale at which the screen covers the frame (the plan's 600%
  // needs a screen of at least 320 x 180 px, i.e. fill <= 6). picture = where the screen box lands at scale S.
  function quadCentre(c) {   // intersection of the diagonals TL-BR and TR-BL
    var p = c[0], r = [c[2][0] - c[0][0], c[2][1] - c[0][1]], q = c[1], s = [c[3][0] - c[1][0], c[3][1] - c[1][1]];
    var den = r[0] * s[1] - r[1] * s[0];
    if (Math.abs(den) < 1e-9) return [(c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4, (c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4];
    var t = ((q[0] - p[0]) * s[1] - (q[1] - p[1]) * s[0]) / den;
    return [p[0] + t * r[0], p[1] + t * r[1]];
  }
  function parseScreen(screen, el) {
    screen = screen || {};
    if (!screen.rect && !screen.corners && el) {
      var ds = el.dataset || {};
      if (ds.x6Rect) screen = { rect: ds.x6Rect.split(/[ ,]+/).map(Number) };
      else if (ds.x6Corners) screen = { corners: ds.x6Corners.trim().split(/\s+/).map(function (p) { return p.split(',').map(Number); }) };
    }
    if (!screen.rect && !screen.corners) throw new Error('RCK.transitions.zoom: screen {rect} or {corners} required');
    return screen;
  }
  function zoomGeometry(screen, opts) {
    opts = opts || {};
    screen = parseScreen(screen);
    var c, inner, size;
    if (screen.rect) {
      var r = screen.rect;
      c = [r[0] + r[2] / 2, r[1] + r[3] / 2];
      inner = [r[0], r[1], r[2], r[3]];
      size = { w: r[2], h: r[3] };
    } else {
      var q = screen.corners, d = function (a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); };
      c = quadCentre(q);
      var x0 = Math.max(q[0][0], q[3][0]), x1 = Math.min(q[1][0], q[2][0]), y0 = Math.max(q[0][1], q[1][1]), y1 = Math.min(q[2][1], q[3][1]);
      inner = [x0, y0, x1 - x0, y1 - y0];       // axis-aligned box inside the quad
      size = { w: (d(q[0], q[1]) + d(q[3], q[2])) / 2, h: (d(q[0], q[3]) + d(q[1], q[2])) / 2 };
    }
    // the screen centre lands on the frame centre, so the box covers the frame once every half-extent reaches it
    var e = 1e-6;
    var fill = Math.max((FW / 2) / Math.max(e, c[0] - inner[0]), (FW / 2) / Math.max(e, inner[0] + inner[2] - c[0]),
      (FH / 2) / Math.max(e, c[1] - inner[1]), (FH / 2) / Math.max(e, inner[1] + inner[3] - c[1]));
    var S = opts.scale === 'fill' ? fill : num(opts.scale, 6);
    var P = [(S * c[0] - FW / 2) / (S - 1), (S * c[1] - FH / 2) / (S - 1)];
    var map = function (pt) { return [P[0] + S * (pt[0] - P[0]), P[1] + S * (pt[1] - P[1])]; };
    var tl0 = map([inner[0], inner[1]]), br0 = map([inner[0] + inner[2], inner[1] + inner[3]]);
    return { scale: S, origin: P, centre: c, fill: fill, covers: S >= fill - 1e-6, size: size, inner: inner,
      pictureAtScale: [tl0[0], tl0[1], br0[0] - tl0[0], br0[1] - tl0[1]] };
  }
  function homography(src, dst) {
    var A = [], b = [], i, c, r;
    for (i = 0; i < 4; i++) {
      var x = src[i][0], y = src[i][1], X = dst[i][0], Y = dst[i][1];
      A.push([x, y, 1, 0, 0, 0, -x * X, -y * X]); b.push(X);
      A.push([0, 0, 0, x, y, 1, -x * Y, -y * Y]); b.push(Y);
    }
    for (c = 0; c < 8; c++) {
      var p = c;
      for (r = c + 1; r < 8; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      var t = A[c]; A[c] = A[p]; A[p] = t; var tb = b[c]; b[c] = b[p]; b[p] = tb;
      for (r = c + 1; r < 8; r++) { var f = A[r][c] / A[c][c]; for (var k = c; k < 8; k++) A[r][k] -= f * A[c][k]; b[r] -= f * b[c]; }
    }
    var h = new Array(8);
    for (r = 7; r >= 0; r--) { var s = b[r]; for (var k2 = r + 1; k2 < 8; k2++) s -= A[r][k2] * h[k2]; h[r] = s / A[r][r]; }
    return h;
  }
  // Lay the screen picture box out at `res` x its on-screen size (default res = the zoom scale, 6) and map it onto the
  // screen (rect: scale(1/res); corners: matrix3d homography). Media inside a box that GSAP later magnifies is rasterised
  // at its LAYOUT size; laid out at 6x it stays sharp at 600% (a box at 1x would be a 6x upscale, blocky once treated).
  // Sets data-x6-res. Returns {w, h, W, H, res}: w/h = the on-screen size at 100% (use it for media-treatment maths,
  // e.g. RCK.motifs.crtGrading({w, h})), W/H = layout size. Static inline transform: never animate this element.
  function zoomFit(target, screen, opts) {
    opts = opts || {};
    var el = $(target), sc = parseScreen(screen, el), res = num(opts.res, num(opts.scale, 6));
    var g = zoomGeometry(sc, { scale: res });
    var w = Math.round(g.size.w), h = Math.round(g.size.h), W = Math.round(w * res), H = Math.round(h * res);
    el.style.position = 'absolute';
    el.style.transformOrigin = '0 0';
    el.style.width = W + 'px'; el.style.height = H + 'px';
    if (sc.rect) {
      el.style.left = sc.rect[0] + 'px'; el.style.top = sc.rect[1] + 'px';
      el.style.transform = 'scale(' + (sc.rect[2] / W) + ',' + (sc.rect[3] / H) + ')';
    } else {
      var Hm = homography([[0, 0], [W, 0], [W, H], [0, H]], sc.corners);
      var m = [Hm[0], Hm[3], 0, Hm[6], Hm[1], Hm[4], 0, Hm[7], 0, 0, 1, 0, Hm[2], Hm[5], 0, 1];
      el.style.left = '0px'; el.style.top = '0px';
      el.style.transform = 'matrix3d(' + m.map(function (v) { return Number(v.toFixed(10)); }).join(',') + ')';
    }
    el.setAttribute('data-x6-res', String(res));
    return { w: w, h: h, W: W, H: H, res: res };
  }
  // media-treatment blur control: value (0..1) -> blur in layout px, measured on 0.9.52 (2 px line, energy sigma).
  var BLUR_CAL = [[0, 0], [0.1, 0.43], [0.15, 0.69], [0.2, 1.16], [0.3, 2.23], [0.4, 3.45], [0.5, 5.24], [0.6, 8.9], [0.7, 11.63], [0.8, 14.58], [1, 21.78]];
  function blurValue(px) {
    if (px <= 0.05) return 0;
    for (var i = 1; i < BLUR_CAL.length; i++) if (px <= BLUR_CAL[i][1]) {
      var a = BLUR_CAL[i - 1], b = BLUR_CAL[i];
      return Number((a[0] + (b[0] - a[0]) * (px - a[1]) / (b[1] - a[1])).toFixed(4));
    }
    return 1;
  }
  // The zoom curve: scale interpolated in LOG space (the eye reads a zoom by its ratio per frame), quadratic ease
  // (GSAP power1.in for 'in': accelerates into the screen; power1.out for 'out': decelerates as it lands in the screen),
  // so every one of the 8 frames moves and the ratio per frame changes by the same step. s(p) for p in [0, 1].
  function zoomCurve(dir, S, ease) {
    var E = G().parseEase(ease || (dir === 'out' ? 'power1.out' : 'power1.in')), L = Math.log(S);
    return function (p) { p = clamp(p, 0, 1); return Math.exp(L * (dir === 'out' ? 1 - E(p) : E(p))); };
  }
  // Per-frame plan (no DOM): scale and screen-space blur sigma for frames 0..N+1 of the zoom.
  // Motion blur model: trailing 180-degree shutter (frame k integrates the motion of the half frame before it), radial
  // streak at refPx (540 px, half the frame height) from the zoom centre: streak = refPx * |ln s(k) - ln s(k - 0.5)|,
  // sigma = streak / sqrt(12) (box -> gaussian), capped at maxPx (24). A static frame (before/after the move) is sharp.
  function zoomPlan(opts) {
    opts = opts || {};
    var N = num(opts.frames, 8), S = num(opts.scale, 6), dir = opts.dir || 'in';
    var sAt = zoomCurve(dir, S, opts.ease);
    var refPx = num(opts.blurRef, 540), maxPx = num(opts.blurMax, 24), sh = num(opts.shutter, 0.5);
    var out = [];
    for (var k = 0; k <= N + 1; k++) {
      var sc = sAt(k / N), sPrev = sAt((k - sh) / N);
      var streak = refPx * Math.abs(Math.log(sc) - Math.log(sPrev));
      out.push({ k: k, scale: sc, sigma: Math.min(maxPx, streak / Math.sqrt(12)) });
    }
    return { frames: N, scale: S, dir: dir, list: out };
  }
  // X6: scale the world (an UNTIMED wrapper holding the plate and the screen picture) 100% -> 600% (dir 'in') or
  // 600% -> 100% (dir 'out') over 8f about the origin that brings the screen to the frame centre, on the zoomCurve
  // (log-space, power1.in for 'in', power1.out for 'out'; opts.ease overrides the ease name). Motion blur: every
  // <video>/<img> in the world that carries a media-treatment blur control gets per-frame --hf-color-grading-blur values
  // (sharp at rest, peaking with the zoom speed, sized for each element's on-screen scale); non-media elements listed in
  // opts.blurDom get the same blur as CSS filter: blur(). Before `at` the world holds its start scale (head handle), after
  // the end its end scale. opts: screen, dir, frames 8, scale 6 | 'fill', ease, blur true, blurMedia (selector/elements,
  // default all media in the world with data-color-grading), blurDom, blurRef 540, blurMax 24. Returns at + 8f.
  function zoom(tl, world, at, opts) {
    opts = opts || {};
    var el = $(world), sc = parseScreen(opts.screen, el), g = G();
    var N = num(opts.frames, 8), dir = opts.dir || 'in';
    var geo = zoomGeometry(sc, { scale: opts.scale });
    var S = geo.scale, n0 = frame(at);
    if (!geo.covers) warn('zoom: at ' + Math.round(S * 100) + '% the screen does not cover the frame (needs ' + Math.round(geo.fill * 100) + '%); frame the plate so the screen is at least 320 x 180 px');
    var s0 = dir === 'out' ? S : 1, s1 = dir === 'out' ? 1 : S;
    var sAt = zoomCurve(dir, S, opts.ease);
    var easeFn = function (p) { return (sAt(p) - s0) / (s1 - s0); };   // GSAP ease = progress along s0 -> s1
    // 2D matrix (force3D false): no cached compositor layer, so every frame is re-rasterised at its own scale
    g.set(el, { transformOrigin: geo.origin[0] + 'px ' + geo.origin[1] + 'px', scale: s0, force3D: false });
    tl.fromTo(el, { scale: s0 }, { scale: s1, duration: N * F, ease: easeFn, force3D: false, immediateRender: false }, tF(n0));
    if (opts.blur === false) return tF(n0 + N);
    var plan = zoomPlan({ frames: N, scale: S, dir: dir, ease: opts.ease, blurRef: opts.blurRef, blurMax: opts.blurMax });
    var base = function (m) { var box = m.closest ? m.closest('[data-x6-res]') : null; return box && el.contains(box) ? 1 / num(box.getAttribute('data-x6-res'), 1) : 1; };
    var media = opts.blurMedia ? $$(opts.blurMedia, el) : $$('video[data-color-grading], img[data-color-grading]', el);
    media.forEach(function (m) {
      var gr = m.getAttribute('data-color-grading') || '';
      if (!/"blur"\s*:\s*(0\.0*[1-9]|[1-9])/.test(gr)) warn('zoom: ' + (m.id || m.tagName) + ' has no media-treatment blur control (run media-treatment --grading \'{"effects":{"blur":0.01}}\'); it will stay sharp');
      if (!m.style.getPropertyValue('--hf-color-grading-blur')) m.style.setProperty('--hf-color-grading-blur', '0');
      var b = base(m), prev = 0;
      plan.list.forEach(function (p) {
        var v = blurValue(p.sigma / (p.scale * b));
        if (p.k > 0) tl.fromTo(m, { '--hf-color-grading-blur': prev }, { '--hf-color-grading-blur': v, duration: F, ease: 'none', immediateRender: false }, tF(n0 + p.k - 1));
        prev = v;
      });
    });
    $$(opts.blurDom, el).forEach(function (d) {
      var b = base(d), prev = 0;
      g.set(d, { filter: 'blur(0px)' });
      plan.list.forEach(function (p) {
        var px = Number((p.sigma / (p.scale * b)).toFixed(3));
        if (p.k > 0) tl.fromTo(d, { filter: 'blur(' + prev + 'px)' }, { filter: 'blur(' + px + 'px)', duration: F, ease: 'none', immediateRender: false }, tF(n0 + p.k - 1));
        prev = px;
      });
    });
    return tF(n0 + N);
  }

  /* ================================================================ X7 light-leak dissolve */
  // Leak layers adapted from registry block "organic-light-leak-overlay" (3 drifting gradient layers, Screen blend),
  // retinted to the palette's warm glow #FFF6E0 (same treatment as the T5 leak). Stand-in for RT6 light-leak footage:
  // when RT6 exists, put it in the .rc-x7 container as a muted <video class="clip rc-x7__footage"> instead (no layers).
  function leakInit(target) {
    var root = $(target);
    if (!root.querySelector('.rc-x7__footage') && !root.querySelector('.rc-x7__layer')) {
      ['a', 'b', 'c'].forEach(function (k) {
        var l = mk('i', 'rc-x7__layer rc-x7__layer--' + k);
        l.setAttribute('aria-hidden', 'true');
        root.appendChild(l);
      });
    }
    root.setAttribute('data-layout-ignore', '');
    return root;
  }
  // X7: a `frames` (12-16, default 14) dissolve from opts.from (opacity 1 -> 0, linear) to opts.to (0 -> 1, if given)
  // through the light leak (Screen blend): leak opacity 0 -> peak (0.9) at the midpoint (sine.out) -> 0 at the end
  // (sine.in) while its layers drift. at = the first dissolve frame. Returns at + frames.
  function leakDissolve(tl, target, at, opts) {
    opts = opts || {};
    var root = leakInit(target), g = G(), n0 = frame(at), N = num(opts.frames, 14), peak = num(opts.peak, 0.9);
    if (N < 12 || N > 16) warn('leakDissolve: ' + N + 'f is outside the plan range 12-16f');
    var half = Math.floor(N / 2), t0 = tF(n0), d = N * F;
    g.set(root, { opacity: 0 });
    tl.fromTo(root, { opacity: 0 }, { opacity: peak, duration: half * F, ease: 'sine.out', immediateRender: false }, t0);
    tl.fromTo(root, { opacity: peak }, { opacity: 0, duration: (N - half) * F, ease: 'sine.in', immediateRender: false }, tF(n0 + half));
    var a = root.querySelector('.rc-x7__layer--a'), b = root.querySelector('.rc-x7__layer--b'), c = root.querySelector('.rc-x7__layer--c');
    if (a && opts.drift !== false) {
      g.set(a, { xPercent: -20, scale: 0.92, rotation: -4 });
      g.set(b, { xPercent: 20, yPercent: -8, scale: 1.08 });
      g.set(c, { xPercent: -28, rotation: -6 });
      tl.fromTo(a, { xPercent: -20, scale: 0.92, rotation: -4 }, { xPercent: 0, scale: 1.01, rotation: -1, duration: d, ease: 'sine.inOut', immediateRender: false }, t0);
      tl.fromTo(b, { xPercent: 20, yPercent: -8, scale: 1.08 }, { xPercent: 2, yPercent: 0, scale: 1.01, duration: d, ease: 'sine.inOut', immediateRender: false }, t0);
      tl.fromTo(c, { xPercent: -28, rotation: -6 }, { xPercent: -2, rotation: -1, duration: d, ease: 'sine.inOut', immediateRender: false }, t0);
    }
    if (opts.from) $$(opts.from).forEach(function (e) { tl.fromTo(e, { opacity: 1 }, { opacity: 0, duration: d, ease: 'none', immediateRender: false }, t0); });
    if (opts.to) $$(opts.to).forEach(function (e) { g.set(e, { opacity: 0 }); tl.fromTo(e, { opacity: 0 }, { opacity: 1, duration: d, ease: 'none', immediateRender: false }, t0); });
    return tF(n0 + N);
  }

  /* ================================================================ X9 siren wash */
  // 4f overlay (Overlay blend, 35%): siren red #E3262E on frames W and W+1, siren blue #2D5BFF on W+2 and W+3, gone on
  // W+4. at = the cop word's first frame W. COP WORDS ONLY: "cops" (B1), "police officer" (B5), "The sirens." (B14).
  // The element (.rc-x9) must sit in the same stacking context as the picture it washes (a direct child of the
  // composition root, above it); its fill child is created here. Returns W + 4f.
  function sirenWash(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), g = G(), w = frame(at), op = num(opts.opacity, 0.35), half = num(opts.frames, 4) / 2;
    var fill = root.querySelector('.rc-x9__fill');
    if (!fill) { fill = mk('i', 'rc-x9__fill'); fill.setAttribute('aria-hidden', 'true'); root.appendChild(fill); }
    root.setAttribute('data-layout-ignore', '');
    var red = opts.red || '#E3262E', blue = opts.blue || '#2D5BFF';
    g.set(root, { opacity: 0 });
    g.set(fill, { backgroundColor: red });
    hard(tl, fill, { backgroundColor: blue }, { backgroundColor: red }, w);   // red on W even after an earlier wash
    hard(tl, root, { opacity: 0 }, { opacity: op }, w);
    hard(tl, fill, { backgroundColor: red }, { backgroundColor: blue }, w + half);
    hard(tl, root, { opacity: op }, { opacity: 0 }, w + 2 * half);
    return tF(w + 2 * half);
  }

  /* ================================================================ export */
  RCK.transitions = {
    FPS: FPS, frame: frame, snap: snap,
    // X2
    drift: drift,
    // X3
    flash: flash,
    // X4
    tear: tear, tearInit: tearInit, tearPlan: tearPlan,
    // X5
    blindsInit: blindsInit, blindsClose: blindsClose, blindsOpen: blindsOpen, blinds: blinds,
    // X6
    zoom: zoom, zoomFit: zoomFit, zoomGeometry: zoomGeometry, zoomCurve: zoomCurve, zoomPlan: zoomPlan, blurValue: blurValue, BLUR_CAL: BLUR_CAL,
    // X7
    leakInit: leakInit, leakDissolve: leakDissolve,
    // X9
    sirenWash: sirenWash
  };
})();
