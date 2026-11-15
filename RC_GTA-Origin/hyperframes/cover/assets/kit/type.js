window.RCK = window.RCK || {}; RCK.FPS = 30; RCK.f = RCK.f || (n => n / 30); RCK.rng = RCK.rng || function (seed) { return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
/* RC_GTA-Origin style kit: TYPE (T1-T10). Docs: KIT_type.md. Source: Master Edit Plan p.9-13 + beat builds.

   Every animation helper is pure:  RCK.type.<helper>(tl, target, atSeconds, opts) -> endSeconds
   - adds tweens to the caller's paused GSAP timeline `tl`, nothing else (no timers, no Date, no Math.random);
   - `target` = selector string or Element (the T element the beat wrote in its HTML);
   - every time is snapped to the 30 fps frame grid; "ease out" = power3.out; T7 chip = 0 -> 112% -> 100% in 8f;
   - only children of the .clip are animated; start states are set with gsap.set at build time;
   - hard cuts (appear / disappear / per-frame jumps) are 0.5-frame tweens placed strictly BETWEEN two frames,
     so frame n always shows the new state and frame n-1 the old one, whatever order the renderer seeks in.
   The timing utilities (snap, attr, captionPlan, captionHTML, checkChunks) need no DOM or GSAP and also run in Node:
     node -e "globalThis.window=globalThis; require('./assets/kit/type.js'); console.log(RCK.type.attr(1.399))" */
(function () {
  'use strict';
  var FPS = 30, F = 1 / FPS;

  /* ---------------- frame grid + attribute helpers (no DOM) ---------------- */
  function frame(t) { return Math.round(t * FPS + 1e-9); }                      // seconds -> nearest frame
  function snap(t) { return frame(t) / FPS; }                                  // seconds -> seconds on the frame grid
  function floor4(n) { return Math.floor((n * 10000) / FPS + 1e-6); }          // frame -> 1e-4 s units, never above the frame time
  // data-start / data-duration strings. The runtime compares seconds raw (frame n is drawn at exactly n/30), so a value
  // rounded UP (8/30 -> "0.2667") would start one frame late. attr() floors to 4 decimals instead (8/30 -> "0.2666").
  function attr(t) { return (floor4(frame(t)) / 10000).toFixed(4); }
  function attrF(n) { return (floor4(n) / 10000).toFixed(4); }
  function dur(t0, t1) { return ((floor4(frame(t1)) - floor4(frame(t0))) / 10000).toFixed(4); }
  function durF(n0, n1) { return ((floor4(n1) - floor4(n0)) / 10000).toFixed(4); }

  /* ---------------- T1 caption timing (no DOM) ---------------- */
  function norm(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ''); }
  function splitChunks(chunks) {
    if (typeof chunks === 'string') chunks = chunks.split('/');
    return chunks.map(function (c) { return String(c).trim(); }).filter(function (c) { return c.length; });
  }
  function tokens(chunk) { return chunk.split(/\s+/).filter(function (w) { return norm(w).length; }); }
  // Validate chunks: 1-4 words each (plan: "1-3 words per chunk, never more than 4"). Returns [] when fine.
  function checkChunks(chunks, max) {
    max = max || 4;
    var out = [];
    splitChunks(chunks).forEach(function (c, i) {
      var n = tokens(c).length;
      if (n < 1) out.push({ index: i, chunk: c, words: n, problem: 'empty chunk' });
      else if (n > max) out.push({ index: i, chunk: c, words: n, problem: 'more than ' + max + ' words on screen' });
    });
    return out;
  }
  // Plan T1 clips from words.json. words = array of {text, comp_t, comp_end_t}; chunks = ["Why does", ...] or
  // "Why does / every GTA, / ..."; opts.from = index of the first chunk word (words matched by POSITION, then checked
  // by spelling); opts.end = seconds where the last chunk hard-cuts out (default: next word's comp_t, else the last
  // word's comp_end_t). Each chunk starts on its first word's comp_t snapped to the nearest frame (<= 0.5 f off) and
  // ends when the next chunk starts.
  function captionPlan(words, chunks, opts) {
    opts = opts || {};
    var list = splitChunks(chunks), bad = checkChunks(list, opts.max || 4);
    if (bad.length) throw new Error('RCK.type.captionPlan: ' + JSON.stringify(bad));
    var wi = opts.from || 0, items = [];
    list.forEach(function (c) {
      var toks = tokens(c), first = wi;
      toks.forEach(function (tk, k) {
        var w = words[wi + k];
        if (!w) throw new Error('RCK.type.captionPlan: ran out of words at "' + tk + '" in "' + c + '"');
        if (!opts.loose && norm(w.text) !== norm(tk))
          throw new Error('RCK.type.captionPlan: chunk "' + c + '" word ' + (k + 1) + ' "' + tk + '" != words[' + (wi + k) + '] "' + w.text + '" (pass opts.loose to accept)');
      });
      wi += toks.length;
      items.push({ text: c, first: first, last: wi - 1, startFrame: frame(words[first].comp_t), voiceT: words[first].comp_t });
    });
    var endT = opts.end != null ? opts.end : (words[wi] ? words[wi].comp_t : words[wi - 1].comp_end_t);
    var endFrame = frame(endT);
    items.forEach(function (it, i) {
      it.endFrame = i + 1 < items.length ? items[i + 1].startFrame : endFrame;
      if (it.endFrame <= it.startFrame) throw new Error('RCK.type.captionPlan: chunk "' + it.text + '" has no frames');
      it.start = it.startFrame / FPS;
      it.end = it.endFrame / FPS;
      it.offsetFrames = Math.round((it.start - it.voiceT) * FPS * 100) / 100;   // vs the voice, must stay within +/-2
      it.startAttr = attrF(it.startFrame);
      it.durAttr = durF(it.startFrame, it.endFrame);
    });
    return { items: items, next: wi };
  }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  // HTML lines to paste into the beat: one timed element per chunk.
  function captionHTML(plan, opts) {
    opts = opts || {};
    var prefix = opts.idPrefix || 'cap', cls = 'clip rc-t1' + (opts.low ? ' rc-t1--low' : '') + (opts.cls ? ' ' + opts.cls : '');
    var z = opts.z != null ? ' style="z-index: ' + opts.z + '"' : '';
    var track = opts.track != null ? ' data-track-index="' + opts.track + '"' : '';
    return (plan.items || plan).map(function (it, i) {
      return '<div id="' + prefix + '-' + (i + 1) + '" class="' + cls + '" data-start="' + it.startAttr + '" data-duration="' + it.durAttr + '"' + track + z + '>' + esc(it.text) + '</div>';
    }).join('\n');
  }

  /* ---------------- DOM + GSAP plumbing ---------------- */
  function G() { if (!window.gsap) throw new Error('RCK.type: GSAP not loaded'); return window.gsap; }
  function $(target, scope) {
    var e = typeof target === 'string' ? (scope || document).querySelector(target) : target;
    if (!e) throw new Error('RCK.type: target not found: ' + target);
    return e;
  }
  function $$(sel, scope) { return Array.prototype.slice.call(scope.querySelectorAll(sel)); }
  function mk(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  // hard cut: frame(t) shows `to`, frame(t)-1 shows `from` (0.5-frame tween between the two frames)
  function hard(tl, target, from, to, t) {
    var n = frame(t), pos = (n - 0.75) / FPS;
    if (pos < 0) { G().set(target, to); return; }
    tl.fromTo(target, from, Object.assign({ duration: 0.5 / FPS, ease: 'none', immediateRender: false }, to), pos);
  }
  // split the text of `node` into one span per character (class cls), keeping child elements (chips) untouched.
  // A text-only node is whitespace-normalised first, so HTML indentation never costs typing frames.
  function splitChars(node, cls) {
    if (!node.children.length) node.textContent = node.textContent.replace(/\s+/g, ' ').trim();
    $$('*', node).concat([node]).forEach(function (n) {
      Array.prototype.slice.call(n.childNodes).forEach(function (c) {
        if (c.nodeType !== 3 || !c.nodeValue.length) return;
        var frag = document.createDocumentFragment();
        Array.from(c.nodeValue).forEach(function (ch) { frag.appendChild(mk('span', cls, ch)); });
        n.replaceChild(frag, c);
      });
    });
    return $$('.' + cls, node);
  }
  function clipEnd(root) {   // seconds where the timed element (or its nearest timed ancestor) ends, or null
    for (var e = root; e && e.getAttribute; e = e.parentElement) {
      var s = e.getAttribute('data-start'), d = e.getAttribute('data-duration');
      if (s != null && d != null && !isNaN(+s) && !isNaN(+d) && !e.hasAttribute('data-composition-id')) return +s + +d;
    }
    return null;
  }
  function seedOf(str) { var h = 2166136261; for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }

  /* ---------------- T2 Punch pair ---------------- */
  // Lead-in hard cut = the clip's data-start. Keyword: 6f blur-in (30 -> 0 px) while scaling 108% -> 100%, ease out,
  // starting at `at` (the keyword's spoken frame). opts.outAt: start of the 4f fade-out of the pair (clip ends at the
  // returned time). Returns outAt + 4f, else the keyword landing time (at + 6f).
  function punchPair(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), key = root.querySelector('.rc-t2__key'), row = root.querySelector('.rc-t2__row') || key.parentNode;
    var t0 = snap(at);
    G().set(key, { opacity: 0, filter: 'blur(30px)', scale: 1.08 });
    hard(tl, key, { opacity: 0 }, { opacity: 1 }, t0);
    tl.fromTo(key, { filter: 'blur(30px)', scale: 1.08 }, { filter: 'blur(0px)', scale: 1, duration: 6 * F, ease: 'power3.out', immediateRender: false }, t0);
    var end = t0 + 6 * F;
    if (opts.outAt != null) {
      var to = snap(opts.outAt);
      tl.fromTo(row, { opacity: 1 }, { opacity: 0, duration: 4 * F, ease: 'none', immediateRender: false }, to);
      end = to + 4 * F;
    }
    return end;
  }

  /* ---------------- T3 Year card ---------------- */
  function prepYear(root) {
    var num = root.querySelector('.rc-t3__num') || root.querySelector('.rc-t3__year');
    if (!num || num.getAttribute('data-rck')) return;
    Array.prototype.slice.call(num.childNodes).forEach(function (c) {
      if (c.nodeType !== 3) return;
      var frag = document.createDocumentFragment();
      Array.from(c.nodeValue).forEach(function (ch) {
        if (/[0-9]/.test(ch)) { var m = mk('span', 'rc-t3__mask'); m.appendChild(mk('span', 'rc-t3__digit', ch)); frag.appendChild(m); }
        else frag.appendChild(document.createTextNode(ch));
      });
      num.replaceChild(frag, c);
    });
    num.setAttribute('data-rck', '1');
  }
  // Digits roll up like an odometer: each digit slides up 40 px inside its mask, 8f, ease out, staggered 2f, the
  // first digit at `at`. A month word (.rc-t3__month, "Nov") is static with the card; give it class rc-t3__digit to
  // roll it as one unit first. opts.pushUntil (s): optional slow push-in 100% -> 104% of the card content until then.
  // Returns the frame the last digit lands. Keep the card >= 1 s after that, then hard cut out (clip end).
  function yearCard(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target); prepYear(root);
    var digits = $$('.rc-t3__digit', root), t0 = snap(at);
    G().set(digits, { opacity: 0, y: 40 });
    digits.forEach(function (d, i) {
      var ti = t0 + 2 * i * F;
      hard(tl, d, { opacity: 0 }, { opacity: 1 }, ti);
      tl.fromTo(d, { y: 40 }, { y: 0, duration: 8 * F, ease: 'power3.out', immediateRender: false }, ti);
    });
    var land = t0 + (2 * Math.max(0, digits.length - 1) + 8) * F;
    if (opts.pushUntil != null) {
      var block = root.querySelector('.rc-t3__block');
      var p0 = opts.pushFrom != null ? snap(opts.pushFrom) : t0;
      tl.fromTo(block, { scale: 1 }, { scale: 1.04, duration: Math.max(F, snap(opts.pushUntil) - p0), ease: 'none', immediateRender: false }, p0);
    }
    return land;
  }

  /* ---------------- T4 Spread words ---------------- */
  // One piece: fades in over 4f (linear) while drifting 12 px up (ease out), from `at` (its spoken word).
  function spreadIn(tl, piece, at) {
    var p = $(piece), t0 = snap(at);
    G().set(p, { opacity: 0, y: 12 });
    tl.fromTo(p, { opacity: 0 }, { opacity: 1, duration: 4 * F, ease: 'none', immediateRender: false }, t0);
    tl.fromTo(p, { y: 12 }, { y: 0, duration: 4 * F, ease: 'power3.out', immediateRender: false }, t0);
    return t0 + 4 * F;
  }
  // All pieces of the T4 element leave together with a 4f fade from `at`.
  function spreadOut(tl, target, at) {
    var pieces = $$('.rc-t4__piece', $(target)), t0 = snap(at);
    tl.fromTo(pieces, { opacity: 1 }, { opacity: 0, duration: 4 * F, ease: 'none', immediateRender: false }, t0);
    return t0 + 4 * F;
  }
  // Whole T4: opts.times = [t piece1, t piece2, ...] (default: every piece at `at`); opts.outAt = joint 4f fade (omit
  // to stay until the clip's hard cut, e.g. B14). Returns the last end.
  function spreadWords(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), pieces = $$('.rc-t4__piece', root), end = snap(at);
    pieces.forEach(function (p, i) { end = Math.max(end, spreadIn(tl, p, opts.times && opts.times[i] != null ? opts.times[i] : at)); });
    if (opts.outAt != null) end = Math.max(end, spreadOut(tl, root, opts.outAt));
    return end;
  }

  /* ---------------- T7 Inline chip ---------------- */
  // Chip scales 0 -> 112% -> 100% over 8f, the only bouncy animation: 0 -> 1.12 in 5f (power3.out), 1.12 -> 1.00 in
  // 3f (power2.inOut), so frame +5 is exactly 112% and frame +8 is 100%. Same frames as RCK.motifs.bugChipPop (M4).
  // opts.ease (e.g. "back.out(1.7)", the plan's HyperFrames note, which peaks at 110%) switches to one 8f tween.
  // Returns at + 8f (settled).
  function chipPop(tl, chip, at, opts) {
    opts = opts || {};
    var c = $(chip), t0 = snap(at);
    G().set(c, { scale: 0, transformOrigin: '50% 50%' });
    if (opts.ease) {
      tl.fromTo(c, { scale: 0 }, { scale: 1, duration: 8 * F, ease: opts.ease, immediateRender: false }, t0);
    } else {
      tl.fromTo(c, { scale: 0 }, { scale: 1.12, duration: 5 * F, ease: 'power3.out', immediateRender: false }, t0);
      tl.fromTo(c, { scale: 1.12 }, { scale: 1, duration: 3 * F, ease: 'power2.inOut', immediateRender: false }, t0 + 5 * F);
    }
    return t0 + 8 * F;
  }
  // T7 sentence: words (.rc-t7__w) hard cut in; opts.wordTimes = one time per word (default: all at `at`);
  // opts.chipAt = time the chip pops (default `at`). Returns the chip landing time (or the last word time).
  function chipSentence(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), words = $$('.rc-t7__w', root), chip = root.querySelector('.rc-t7__chip'), end = snap(at);
    G().set(words, { opacity: 0 });
    words.forEach(function (w, i) {
      var t = opts.wordTimes && opts.wordTimes[i] != null ? opts.wordTimes[i] : at;
      hard(tl, w, { opacity: 0 }, { opacity: 1 }, t);
      end = Math.max(end, snap(t));
    });
    if (chip) end = Math.max(end, chipPop(tl, chip, opts.chipAt != null ? opts.chipAt : at, opts));
    return end;
  }

  /* ---------------- T5 Glow line ---------------- */
  function prepGlow(root) {
    var text = root.querySelector('.rc-t5__text');
    if (!text) throw new Error('RCK.type.glowLine: .rc-t5__text missing');
    var line = root.querySelector('.rc-t5__line');
    if (!line) { line = mk('div', 'rc-t5__line'); text.parentNode.insertBefore(line, text); line.appendChild(text); }
    if (!line.querySelector('.rc-t5__glow')) {
      ['wide', 'near'].forEach(function (k) {
        var c = text.cloneNode(true);
        c.className = 'rc-t5__glow rc-t5__glow--' + k;
        c.setAttribute('aria-hidden', 'true');
        c.setAttribute('data-layout-ignore', '');
        c.removeAttribute('id');
        $$('[id]', c).forEach(function (n) { n.removeAttribute('id'); });
        $$('.rc-t7__chip', c).forEach(function (chip) { chip.parentNode.replaceChild(mk('span', 'rc-t7__gap'), chip); });
        line.insertBefore(c, text);
      });
    }
    var leak = root.querySelector('.rc-t5__leak');
    if (!leak) {
      leak = mk('div', 'rc-t5__leak');
      leak.setAttribute('aria-hidden', 'true');
      leak.setAttribute('data-layout-ignore', '');
      ['a', 'b', 'c'].forEach(function (k) { leak.appendChild(mk('i', 'rc-t5__leak-' + k)); });
      root.insertBefore(leak, root.firstChild);
    }
    return { line: line, text: text, leak: leak };
  }
  // Fades in over 12f from blur 20 -> 0 and tracking +2% -> 0 (opacity linear, blur/tracking ease out) at `at`.
  // A light leak drifts behind from `at` to the clip end (or opts.leakUntil): rises to opts.leakPeak (default 0.16)
  // with the line, settles to opts.leakHold (default 0.1) and keeps drifting (registry organic-light-leak-overlay
  // drift paths, sine.inOut). opts.chipAt: the M4 chip in the line pops (T7) as "bug" is spoken.
  // Returns at + 12f (line landed).
  function glowLine(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), parts = prepGlow(root), t0 = snap(at), g = G();
    var line = parts.line, leak = parts.leak;
    g.set(line, { opacity: 0, filter: 'blur(20px)', '--rc-t5-track': '0.02em' });
    tl.fromTo(line, { opacity: 0 }, { opacity: 1, duration: 12 * F, ease: 'none', immediateRender: false }, t0);
    tl.fromTo(line, { filter: 'blur(20px)', '--rc-t5-track': '0.02em' }, { filter: 'blur(0px)', '--rc-t5-track': '0em', duration: 12 * F, ease: 'power3.out', immediateRender: false }, t0);
    if (opts.leak !== false) {
      var until = opts.leakUntil != null ? snap(opts.leakUntil) : clipEnd(root);
      if (until == null || until <= t0) until = t0 + 2;
      var d = until - t0, peak = opts.leakPeak != null ? opts.leakPeak : 0.16, hold = opts.leakHold != null ? opts.leakHold : 0.1;
      var a = leak.querySelector('.rc-t5__leak-a'), b = leak.querySelector('.rc-t5__leak-b'), c = leak.querySelector('.rc-t5__leak-c');
      g.set(leak, { opacity: 0 });
      g.set(a, { xPercent: -20, scale: 0.92, rotation: -4 });
      g.set(b, { xPercent: 20, yPercent: -8, scale: 1.08 });
      g.set(c, { xPercent: -28, rotation: -6 });
      var rise = Math.min(d * 0.4, Math.max(12 * F, d * 0.24));
      tl.fromTo(leak, { opacity: 0 }, { opacity: peak, duration: rise, ease: 'sine.out', immediateRender: false }, t0);
      tl.fromTo(leak, { opacity: peak }, { opacity: hold, duration: Math.max(F, d * 0.3), ease: 'sine.inOut', immediateRender: false }, t0 + rise);
      tl.fromTo(a, { xPercent: -20, scale: 0.92, rotation: -4 }, { xPercent: 18, scale: 1.1, rotation: 2, duration: d, ease: 'sine.inOut', immediateRender: false }, t0);
      tl.fromTo(b, { xPercent: 20, yPercent: -8, scale: 1.08 }, { xPercent: -16, yPercent: 8, scale: 0.94, duration: d, ease: 'sine.inOut', immediateRender: false }, t0);
      tl.fromTo(c, { xPercent: -28, rotation: -6 }, { xPercent: 24, rotation: 4, duration: d, ease: 'sine.inOut', immediateRender: false }, t0);
    }
    var chip = parts.text.querySelector('.rc-t7__chip');
    if (chip) chipPop(tl, chip, opts.chipAt != null ? opts.chipAt : t0 + 12 * F, opts);
    return t0 + 12 * F;
  }

  /* ---------------- T6 Giant type ---------------- */
  // Types on one letter every 2f (opts.every frames), reading order across the stacked lines, no fades. Returns the
  // frame the last letter appears; hold >= 1 s after it.
  function giantType(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), step = opts.every || 2, t0 = snap(at);
    if (!root.getAttribute('data-rck')) { $$('.rc-t6__line', root).forEach(function (l) { splitChars(l, 'rc-t6__ch'); }); root.setAttribute('data-rck', '1'); }
    var chars = $$('.rc-t6__ch', root).filter(function (c) { return /\S/.test(c.textContent); });
    G().set($$('.rc-t6__ch', root), { opacity: 0 });
    $$('.rc-t6__ch', root).forEach(function (c) { if (!/\S/.test(c.textContent)) G().set(c, { opacity: 1 }); });
    chars.forEach(function (c, i) { hard(tl, c, { opacity: 0 }, { opacity: 1 }, t0 + i * step * F); });
    return t0 + Math.max(0, chars.length - 1) * step * F;
  }

  /* ---------------- T8 Name / quote card ---------------- */
  // Name (+ underline) fade in over 6f; the role fades to its 60% over the same 6f. Returns at + 6f.
  function nameIn(tl, target, at) {
    var root = $(target), t0 = snap(at), g = G();
    var name = $$('.rc-t8__name', root), role = $$('.rc-t8__role', root);
    g.set(name, { opacity: 0 }); g.set(role, { opacity: 0 });
    if (name.length) tl.fromTo(name, { opacity: 0 }, { opacity: 1, duration: 6 * F, ease: 'none', immediateRender: false }, t0);
    if (role.length) tl.fromTo(role, { opacity: 0 }, { opacity: 0.6, duration: 6 * F, ease: 'none', immediateRender: false }, t0);
    return t0 + 6 * F;
  }
  // Quote types on at 2 characters per frame (opts.perFrame), first 2 characters on `at`. Returns the frame the last
  // character appears.
  function quoteType(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), q = root.classList.contains('rc-t8__quote') ? root : root.querySelector('.rc-t8__quote');
    if (!q.getAttribute('data-rck')) { splitChars(q, 'rc-t8__ch'); q.setAttribute('data-rck', '1'); }
    var chars = $$('.rc-t8__ch', q), per = opts.perFrame || 2, t0 = snap(at), last = t0;
    G().set(chars, { opacity: 0 });
    chars.forEach(function (c, i) { var t = t0 + Math.floor(i / per) * F; hard(tl, c, { opacity: 0 }, { opacity: 1 }, t); last = t; });
    return last;
  }
  // B3: moves the .rc-t8__walker slot (the Lemming) along the name's underline, left -> right (opts.reverse: right ->
  // left), linear, over opts.duration seconds (default 1). Returns the end time.
  function walk(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), u = root.classList.contains('rc-t8__underline') ? root : root.querySelector('.rc-t8__underline');
    var t0 = snap(at), d = Math.max(F, snap(opts.duration != null ? opts.duration : 1));
    var a = opts.reverse ? 1 : 0, b = opts.reverse ? 0 : 1;
    G().set(u, { '--rc-walk': a });
    tl.fromTo(u, { '--rc-walk': a }, { '--rc-walk': b, duration: d, ease: 'none', immediateRender: false }, t0);
    return t0 + d;
  }

  /* ---------------- T9 Highlight / label ---------------- */
  // Highlight swipes left -> right over 8f, ease out (clip-path reveal; size untouched). Returns at + 8f.
  function highlight(tl, target, at) {
    var h = $(target), t0 = snap(at);
    G().set(h, { clipPath: 'inset(0% 100% 0% 0%)' });
    tl.fromTo(h, { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 8 * F, ease: 'power3.out', immediateRender: false }, t0);
    return t0 + 8 * F;
  }
  // Label pops in over 4f: scale 96% -> 100% with a fade (the plan's L3 "pop in" definition), ease out. Returns at + 4f.
  function label(tl, target, at) {
    var root = $(target), l = root.classList.contains('rc-t9__label') ? root : root.querySelector('.rc-t9__label'), t0 = snap(at);
    G().set(l, { opacity: 0, scale: 0.96 });
    tl.fromTo(l, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 4 * F, ease: 'power3.out', immediateRender: false }, t0);
    return t0 + 4 * F;
  }

  /* ---------------- T10 Glitch word ---------------- */
  function prepGlitch(root) {
    var word = root.querySelector('.rc-t10__word') || root;
    if (word.getAttribute('data-rck')) return word;
    var text = word.textContent.trim();
    word.textContent = '';
    word.appendChild(mk('span', 'rc-t10__clean', text));
    var gl = mk('span', 'rc-t10__glitch');
    gl.setAttribute('aria-hidden', 'true');
    gl.setAttribute('data-layout-ignore', '');
    for (var s = 1; s <= 3; s++) {
      var slice = mk('span', 'rc-t10__slice rc-t10__slice--' + s);
      ['r', 'g', 'b'].forEach(function (ch) { slice.appendChild(mk('span', 'rc-t10__ch rc-t10__ch--' + ch, text)); });
      gl.appendChild(slice);
    }
    word.appendChild(gl);
    word.setAttribute('data-rck', '1');
    return word;
  }
  // 6f of glitch from `at` (opts.frames): RGB split (red +6 px, blue -6 px) and three horizontal slices jumping +/-20 px
  // each frame (seeded: opts.seed, default from the element id; a new pattern every frame, never all three the same
  // way), then settles clean
  // (opts.settle = false keeps the last glitch frame, e.g. "now?" breaking apart before the cut). Before `at` the word
  // shows clean. Returns at + frames (the first clean frame).
  function glitch(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), word = prepGlitch(root), g = G();
    var clean = word.querySelector('.rc-t10__clean'), gl = word.querySelector('.rc-t10__glitch'), slices = $$('.rc-t10__slice', word);
    var n = opts.frames || 6, amp = opts.amp || 20, t0 = snap(at);
    var rnd = RCK.rng(opts.seed != null ? opts.seed : seedOf(root.id || word.textContent));
    g.set(clean, { opacity: 1 }); g.set(gl, { opacity: 0 }); g.set(slices, { x: 0 });
    hard(tl, clean, { opacity: 1 }, { opacity: 0 }, t0);
    hard(tl, gl, { opacity: 0 }, { opacity: 1 }, t0);
    var prev = [0, 0, 0];
    for (var k = 0; k < n; k++) {
      // a new pattern every frame: slices never all shifted the same way, never a repeat of the previous frame
      var v, tries = 0;
      do {
        v = [0, 1, 2].map(function () { return rnd() < 0.5 ? -amp : amp; });
        if (v[0] === v[1] && v[1] === v[2]) v[1] = -v[1];
      } while (v.join() === prev.join() && ++tries < 16);
      for (var s = 0; s < 3; s++) { hard(tl, slices[s], { x: prev[s] }, { x: v[s] }, t0 + k * F); }
      prev = v;
    }
    if (opts.settle !== false) {
      var te = t0 + n * F;
      hard(tl, gl, { opacity: 1 }, { opacity: 0 }, te);
      hard(tl, clean, { opacity: 0 }, { opacity: 1 }, te);
      for (var s2 = 0; s2 < 3; s2++) hard(tl, slices[s2], { x: prev[s2] }, { x: 0 }, te);
    }
    return t0 + n * F;
  }

  RCK.type = {
    FPS: FPS,
    // frame grid + attributes
    frame: frame, snap: snap, attr: attr, attrF: attrF, dur: dur, durF: durF,
    // T1 captions
    checkChunks: checkChunks, captionPlan: captionPlan, captionHTML: captionHTML,
    // T2-T10 animation helpers: (tl, target, atSeconds, opts) -> endSeconds
    punchPair: punchPair,
    yearCard: yearCard,
    spreadIn: spreadIn, spreadOut: spreadOut, spreadWords: spreadWords,
    glowLine: glowLine,
    giantType: giantType,
    chipPop: chipPop, chipSentence: chipSentence,
    nameIn: nameIn, quoteType: quoteType, walk: walk,
    highlight: highlight, label: label,
    glitch: glitch
  };
})();
