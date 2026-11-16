window.RCK = window.RCK || {}; RCK.FPS = 30; RCK.f = RCK.f || (n => n / 30); RCK.rng = RCK.rng || function (seed) { return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
/* RC_GTA-Origin style kit: TYPE (T1-T10). Docs: KIT_type.md ("v02" section first). Source: Master Edit Plan p.9-13 + beat
   builds, overridden where REVISION_v02.md says so (rule A captions, rule C easing, Coolvetica).

   Every animation helper is pure:  RCK.type.<helper>(tl, target, atSeconds, opts) -> endSeconds
   - adds tweens to the caller's paused GSAP timeline `tl`, nothing else (no timers, no Date, no Math.random);
   - `target` = selector string or Element (the T element the beat wrote in its HTML);
   - every time is snapped to the 30 fps frame grid;
   - only children of the .clip are animated; start states are set with gsap.set at build time;
   - hard cuts (appear / disappear / per-frame jumps) are 0.5-frame STEP tweens (ease 'steps(1)') placed strictly BETWEEN
     two frames, so frame n always shows the new state and frame n-1 the old one, whatever order the renderer seeks in.
     They are cuts, not animations (rule C exempts cuts); nothing in the kit uses ease 'none' / 'linear' any more.
   v02 (REVISION_v02.md):
   - RCK.ease: easings.net name -> GSAP ease ('easeOutExpo' -> 'expo.out'), CSS cubic-beziers, reference curves. Every kit
     helper that takes opts.ease accepts either spelling; 'none' / 'linear' are refused (warning + the helper's default).
   - Captions v2 (rule A): words pop in one by one on their own onset frame, max 2 words on screen, groups hard-cut when the
     next group's first word starts. Node: captionPlanV2 + captionHTMLV2 (T1, T2 pairs, T4 pieces, T5 line). Browser:
     captionPops (animates generated markup) or wordsV2 / punchPairV2 / spreadWordsV2 / glowLineV2 (convert v01 markup).
   The timing utilities (snap, attr, captionPlan, captionPlanV2, captionHTMLV2, groupWords, RCK.ease) need no DOM or GSAP
   and also run in Node:
     node -e "globalThis.window=globalThis; require('./assets/kit/type.js'); console.log(RCK.type.attr(1.399))" */
(function () {
  'use strict';
  var FPS = 30, F = 1 / FPS;

  /* ---------------- easing (rule C): easings.net names -> GSAP, never linear ---------------- */
  var EASE_FAM = { Sine: 'sine', Quad: 'power1', Cubic: 'power2', Quart: 'power3', Quint: 'power4', Expo: 'expo', Circ: 'circ', Back: 'back', Elastic: 'elastic', Bounce: 'bounce' };
  // 'easeOutExpo' -> 'expo.out' (easeInOutBack -> back.inOut(2.5949095) and Elastic periods as on easings.net);
  // anything that is not an easings.net name is returned unchanged (GSAP names pass through).
  function gsapEase(name) {
    var m = /^ease(InOut|In|Out)(Sine|Quad|Cubic|Quart|Quint|Expo|Circ|Back|Elastic|Bounce)$/.exec(String(name));
    if (!m) return name;
    var dir = m[1] === 'InOut' ? 'inOut' : m[1].toLowerCase();
    var arg = m[2] === 'Back' ? (dir === 'inOut' ? '(2.5949095)' : '(1.70158)') : m[2] === 'Elastic' ? (dir === 'inOut' ? '(1, 0.45)' : '(1, 0.3)') : '';
    return EASE_FAM[m[2]] + '.' + dir + arg;
  }
  var warnedLinear = {};
  // opts.ease resolver used by every helper: easings.net or GSAP name (or a function); 'none'/'linear' -> the default.
  function easeOf(e, dflt) {
    if (e == null || e === '') return gsapEase(dflt);
    if (typeof e === 'function') return e;
    if (/^(none|linear|power0(\.\w+)?)$/i.test(String(e).trim())) {
      if (!warnedLinear[e] && window.console) console.warn('RCK: ease "' + e + '" is linear (REVISION_v02 rule C), using ' + dflt);
      warnedLinear[e] = 1;
      return gsapEase(dflt);
    }
    return gsapEase(e);
  }
  var PI = Math.PI, C1 = 1.70158, C2 = C1 * 1.525, C3 = C1 + 1, C4 = 2 * PI / 3, C5 = 2 * PI / 4.5;
  function bounceOut(x) { var n = 7.5625, d = 2.75; if (x < 1 / d) return n * x * x; if (x < 2 / d) return n * (x -= 1.5 / d) * x + 0.75; if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + 0.9375; return n * (x -= 2.625 / d) * x + 0.984375; }
  // reference curves exactly as published on easings.net (for checks in Node; GSAP's own eases match them)
  var EASE_FN = {
    easeInSine: function (x) { return 1 - Math.cos(x * PI / 2); }, easeOutSine: function (x) { return Math.sin(x * PI / 2); }, easeInOutSine: function (x) { return -(Math.cos(PI * x) - 1) / 2; },
    easeInQuad: function (x) { return x * x; }, easeOutQuad: function (x) { return 1 - (1 - x) * (1 - x); }, easeInOutQuad: function (x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; },
    easeInCubic: function (x) { return x * x * x; }, easeOutCubic: function (x) { return 1 - Math.pow(1 - x, 3); }, easeInOutCubic: function (x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; },
    easeInQuart: function (x) { return Math.pow(x, 4); }, easeOutQuart: function (x) { return 1 - Math.pow(1 - x, 4); }, easeInOutQuart: function (x) { return x < 0.5 ? 8 * Math.pow(x, 4) : 1 - Math.pow(-2 * x + 2, 4) / 2; },
    easeInQuint: function (x) { return Math.pow(x, 5); }, easeOutQuint: function (x) { return 1 - Math.pow(1 - x, 5); }, easeInOutQuint: function (x) { return x < 0.5 ? 16 * Math.pow(x, 5) : 1 - Math.pow(-2 * x + 2, 5) / 2; },
    easeInExpo: function (x) { return x === 0 ? 0 : Math.pow(2, 10 * x - 10); }, easeOutExpo: function (x) { return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); },
    easeInOutExpo: function (x) { return x === 0 ? 0 : x === 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2; },
    easeInCirc: function (x) { return 1 - Math.sqrt(1 - x * x); }, easeOutCirc: function (x) { return Math.sqrt(1 - Math.pow(x - 1, 2)); },
    easeInOutCirc: function (x) { return x < 0.5 ? (1 - Math.sqrt(1 - Math.pow(2 * x, 2))) / 2 : (Math.sqrt(1 - Math.pow(-2 * x + 2, 2)) + 1) / 2; },
    easeInBack: function (x) { return C3 * x * x * x - C1 * x * x; }, easeOutBack: function (x) { return 1 + C3 * Math.pow(x - 1, 3) + C1 * Math.pow(x - 1, 2); },
    easeInOutBack: function (x) { return x < 0.5 ? (Math.pow(2 * x, 2) * ((C2 + 1) * 2 * x - C2)) / 2 : (Math.pow(2 * x - 2, 2) * ((C2 + 1) * (x * 2 - 2) + C2) + 2) / 2; },
    easeInElastic: function (x) { return x === 0 ? 0 : x === 1 ? 1 : -Math.pow(2, 10 * x - 10) * Math.sin((x * 10 - 10.75) * C4); },
    easeOutElastic: function (x) { return x === 0 ? 0 : x === 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * C4) + 1; },
    easeInOutElastic: function (x) { return x === 0 ? 0 : x === 1 ? 1 : x < 0.5 ? -(Math.pow(2, 20 * x - 10) * Math.sin((20 * x - 11.125) * C5)) / 2 : (Math.pow(2, -20 * x + 10) * Math.sin((20 * x - 11.125) * C5)) / 2 + 1; },
    easeInBounce: function (x) { return 1 - bounceOut(1 - x); }, easeOutBounce: bounceOut,
    easeInOutBounce: function (x) { return x < 0.5 ? (1 - bounceOut(1 - 2 * x)) / 2 : (1 + bounceOut(2 * x - 1)) / 2; }
  };
  var EASE_CSS = {
    easeInSine: 'cubic-bezier(0.12, 0, 0.39, 0)', easeOutSine: 'cubic-bezier(0.61, 1, 0.88, 1)', easeInOutSine: 'cubic-bezier(0.37, 0, 0.63, 1)',
    easeInQuad: 'cubic-bezier(0.11, 0, 0.5, 0)', easeOutQuad: 'cubic-bezier(0.5, 1, 0.89, 1)', easeInOutQuad: 'cubic-bezier(0.45, 0, 0.55, 1)',
    easeInCubic: 'cubic-bezier(0.32, 0, 0.67, 0)', easeOutCubic: 'cubic-bezier(0.33, 1, 0.68, 1)', easeInOutCubic: 'cubic-bezier(0.65, 0, 0.35, 1)',
    easeInQuart: 'cubic-bezier(0.5, 0, 0.75, 0)', easeOutQuart: 'cubic-bezier(0.25, 1, 0.5, 1)', easeInOutQuart: 'cubic-bezier(0.76, 0, 0.24, 1)',
    easeInQuint: 'cubic-bezier(0.64, 0, 0.78, 0)', easeOutQuint: 'cubic-bezier(0.22, 1, 0.36, 1)', easeInOutQuint: 'cubic-bezier(0.83, 0, 0.17, 1)',
    easeInExpo: 'cubic-bezier(0.7, 0, 0.84, 0)', easeOutExpo: 'cubic-bezier(0.16, 1, 0.3, 1)', easeInOutExpo: 'cubic-bezier(0.87, 0, 0.13, 1)',
    easeInCirc: 'cubic-bezier(0.55, 0, 1, 0.45)', easeOutCirc: 'cubic-bezier(0, 0.55, 0.45, 1)', easeInOutCirc: 'cubic-bezier(0.85, 0, 0.15, 1)',
    easeInBack: 'cubic-bezier(0.36, 0, 0.66, -0.56)', easeOutBack: 'cubic-bezier(0.34, 1.56, 0.64, 1)', easeInOutBack: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)'
  };
  if (!RCK.ease || !RCK.ease.gsap) {
    var EZ = {};
    Object.keys(EASE_FN).forEach(function (n) { EZ[n] = gsapEase(n); });
    var BACK = {};
    Object.keys(EASE_FN).forEach(function (n) { BACK[EZ[n].replace(/\(.*\)$/, '')] = n; });
    EZ.css = EASE_CSS;                                   // RCK.ease.css.easeOutExpo -> 'cubic-bezier(0.16, 1, 0.3, 1)'
    EZ.names = Object.keys(EASE_FN);
    EZ.gsap = gsapEase;                                  // RCK.ease.gsap('easeOutExpo') -> 'expo.out'
    EZ.get = function (e, dflt) { return easeOf(e, dflt || 'power2.out'); };
    EZ.name = function (g) { return EASE_FN[g] ? g : BACK[String(g).replace(/\(.*\)$/, '')] || null; };   // 'expo.out' -> 'easeOutExpo'
    EZ.fn = function (e) { var n = EZ.name(e); return n ? EASE_FN[n] : null; };                         // reference curve
    EZ.isLinear = function (f) { return Math.abs(f(0.25) - 0.25) < 1e-3 && Math.abs(f(0.5) - 0.5) < 1e-3 && Math.abs(f(0.75) - 0.75) < 1e-3; };
    RCK.ease = EZ;
  }

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
  function norm(s) { return String(s).toLowerCase().replace(/[‘’]/g, "'").replace(/[^a-z0-9]+/g, ''); }
  function splitChunks(chunks) {
    if (typeof chunks === 'string') chunks = chunks.split('/');
    return chunks.map(function (c) { return String(c).trim(); }).filter(function (c) { return c.length; });
  }
  function tokens(chunk) { return String(chunk).split(/\s+/).filter(function (w) { return norm(w).length; }); }
  // Validate chunks: 1-4 words each (plan: "1-3 words per chunk, never more than 4"). Returns [] when fine.
  // v02: groups on screen are max 2 words (captionPlanV2 splits longer chunks itself; checkChunks(chunks, 2) lists them).
  function checkChunks(chunks, max) {
    max = max || 4;
    var out = [];
    splitChunks(chunks).forEach(function (c, i) {
      var n = tokens(c.replace(/[|+]/g, ' ')).length;
      if (n < 1) out.push({ index: i, chunk: c, words: n, problem: 'empty chunk' });
      else if (n > max) out.push({ index: i, chunk: c, words: n, problem: 'more than ' + max + ' words on screen' });
    });
    return out;
  }
  var warnedV01 = false;
  // v01 T1 plan (one clip per plan chunk, up to 4 words, no word pops). KEPT for compatibility; v02 captions must use
  // captionPlanV2 (word by word, max 2 words). opts.v01 = true silences the reminder.
  // words = array of {text, comp_t, comp_end_t}; chunks = ["Why does", ...] or "Why does / every GTA, / ..."; opts.from =
  // index of the first chunk word (words matched by POSITION, then checked by spelling); opts.end = seconds where the
  // last chunk hard-cuts out (default: next word's comp_t, else the last word's comp_end_t). Each chunk starts on its first
  // word's comp_t snapped to the nearest frame (<= 0.5 f off) and ends when the next chunk starts.
  function captionPlan(words, chunks, opts) {
    opts = opts || {};
    if (!opts.v01 && !warnedV01 && typeof console !== 'undefined') {
      console.warn('RCK.type.captionPlan is the v01 (whole-chunk) caption; v02 rule A needs RCK.type.captionPlanV2 (word by word, max 2 words). See KIT_type.md "v02".');
      warnedV01 = true;
    }
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
  // v01 HTML lines to paste into the beat: one timed element per chunk.
  function captionHTML(plan, opts) {
    opts = opts || {};
    var prefix = opts.idPrefix || 'cap', cls = 'clip rc-t1' + (opts.low ? ' rc-t1--low' : '') + (opts.cls ? ' ' + opts.cls : '');
    var z = opts.z != null ? ' style="z-index: ' + opts.z + '"' : '';
    var track = opts.track != null ? ' data-track-index="' + opts.track + '"' : '';
    return (plan.items || plan).map(function (it, i) {
      return '<div id="' + prefix + '-' + (i + 1) + '" class="' + cls + '" data-start="' + it.startAttr + '" data-duration="' + it.durAttr + '"' + track + z + '>' + esc(it.text) + '</div>';
    }).join('\n');
  }

  /* ================= v02 captions (rule A): word by word, max 2 words on screen (no DOM in this block) =================
     Chunk syntax (the plan's "On screen" line): '/' = a plan chunk boundary (never crossed by a group); '|' = force a group
     break inside a chunk ("a | police officer"); '+' = keep two phrases in ONE group (T4: "Dundee, + Scotland." = two
     pieces, left and right, on screen together). Chunks of 3+ words without '|' are split automatically (groupWords). */
  var LEX = (function () {
    var L = {
      det: 'a an the this that these those every each some any no my your his her its our their another',
      prep: 'in on at of for to with from by into about around behind above below through over under after before since until like as than without against during onto upon off via per across',
      conj: 'and or but so because if then when while nor yet though although whether',
      aux: "is are was were be been being am has have had do does did will would can could should may might must shall not it's that's there's here's who's what's he's she's you're we're they're i'm i've you've we've they've i'll you'll we'll they'll don't doesn't didn't isn't aren't wasn't weren't won't can't couldn't shouldn't wouldn't let's",
      pron: 'i you he she it we they me him us them who what which',
      objpron: 'you it them him her me us',
      adv: 'already always even just still never also only now then finally suddenly anymore later again ever really very too soon once straight down up out away back here there together'
    }, out = {};
    Object.keys(L).forEach(function (k) { out[k] = {}; L[k].split(' ').forEach(function (w) { out[k][w.replace(/'/g, '')] = 1; }); });
    return out;
  })();
  function lex(kind, tok) { return !!LEX[kind][norm(tok)]; }
  function isCapTok(t) { return /^[A-Z0-9]/.test(String(t).replace(/^[^A-Za-z0-9]+/, '')); }
  function isAllCaps(t) { var s = String(t).replace(/[^A-Za-z]/g, ''); return s.length >= 2 && s === s.toUpperCase(); }
  function isNumTok(t) { return /^[^A-Za-z0-9]*\d/.test(String(t)); }
  function looksVerb(t) { var s = norm(t); return s.length >= 5 && /(ed|ing)$/.test(s); }
  // Cost of a group break between token a and token b (lower = a more natural place to break). aFirst: a is the
  // phrase's first word (a capitalised first word is sentence case, not a name). Kit heuristic, tuned on the locked
  // script; the per-beat groups are listed in KIT_type.md, override any of them with '|'.
  function cutCost(a, b, aFirst) {
    if (/[,.;:!?…)"”]$/.test(String(a))) return 0;                          // punctuation: a natural break
    if (lex('conj', a)) return 3;                                                    // "And | that bug" (but "and start | trying")
    if (lex('det', a)) return 6;                                                     // strands an article
    if (lex('prep', a)) return 6;                                                    // strands a preposition
    if (lex('objpron', b)) return 8;                                                 // never "following | you"
    if ((isAllCaps(a) || (isCapTok(a) && !aFirst)) && (isCapTok(b) || isNumTok(b))) return 9;   // names: "GTA 6", "GTA Online"
    if (lex('aux', a)) return 3;
    if (lex('det', b) || lex('prep', b) || lex('conj', b)) return 0.5;               // a new phrase starts at b
    if (lex('adv', b)) return 1.5;
    if (looksVerb(b)) return 1.5;                                                    // subject | verb / participle
    if (lex('adv', a)) return 4;
    if (lex('pron', a)) return 2;
    return 8;                                                                         // content | content ("police | officer")
  }
  // ws: one phrase [{text, frame?}], opts: {max 2, forced: [indices that must start a group], endFrame (frame the phrase
  // ends: the next phrase's first word)} -> array of groups (arrays of ws items). Dynamic programming over the break
  // costs above + group penalties: 1-word group +1, a group ending on an article +4, a group shown < 2 frames +40,
  // < 4 frames +0.5, an empty group (two groups on one frame) +1000.
  function groupPenalty(ws, i, s, opts) {
    var p = 0.01;
    if (s === 1) p += 1;
    if (s >= 2 && lex('det', ws[i + s - 1].text)) p += 4;
    var f0 = ws[i].frame, next = i + s < ws.length ? ws[i + s].frame : opts.endFrame;
    if (f0 != null && next != null) { var d = next - f0; if (d < 1) p += 1000; else if (d < 2) p += 40; else if (d < 4) p += 0.5; }
    return p;
  }
  function groupWords(ws, opts) {
    opts = opts || {};
    ws = ws.map(function (w) { return typeof w === 'string' ? { text: w } : w; });
    var n = ws.length, max = opts.max || 2, forced = {}, best = [], pick = [];
    (opts.forced || []).forEach(function (i) { forced[i] = true; });
    best[n] = 0;
    for (var i = n - 1; i >= 0; i--) {
      best[i] = Infinity;
      for (var s = 1; s <= max && i + s <= n; s++) {
        if (s > 1 && forced[i + s - 1]) break;                                          // a forced break inside the group
        var cut = i + s < n ? (forced[i + s] ? 0 : cutCost(ws[i + s - 1].text, ws[i + s].text, i + s - 1 === 0)) : 0;
        var c = groupPenalty(ws, i, s, opts) + cut + best[i + s];
        if (c < best[i] - 1e-9) { best[i] = c; pick[i] = s; }
      }
    }
    var out = [];
    for (var k = 0; k < n; k += pick[k]) out.push(ws.slice(k, k + pick[k]));
    return out;
  }
  // '/', '|', '+' chunk syntax -> phrases [{text, tokens, forced, join}] (join: same group as the previous phrase)
  function parsePhrases(chunks) {
    var list = splitChunks(chunks), out = [];
    list.forEach(function (c) {
      c.split('+').forEach(function (part, k) {
        var toks = [], forced = [];
        part.split('|').forEach(function (g, gi) { var t = tokens(g); if (gi > 0 && toks.length) forced.push(toks.length); toks = toks.concat(t); });
        if (toks.length) out.push({ text: toks.join(' '), tokens: toks, forced: forced, join: k > 0 && out.length > 0 });
      });
    });
    return out;
  }
  function wordTime(w) { return typeof w === 'number' ? w : (w.comp_t != null ? w.comp_t : (w.t != null ? w.t : w.start)); }
  // v02 caption plan. words = words.json `words` (or an array of seconds), chunks = the plan's chunk string with the
  // syntax above; opts: from (index of the first word), end (s, where the last group hard-cuts out; default the next
  // word's comp_t, else the last word's comp_end_t), start (s, optional earlier start of the first group's clip; its
  // words still pop on their own frames), max (2), loose (accept deliberate spelling differences, e.g. "18" for
  // "eighteen"), exitF (0 = hard cut; 2-3 = eased exit of the last group before `end`, see captionPops).
  // Returns {groups, phrases, next, endFrame, warnings}; each group {index, text, words:[{text, i, frame, voiceT,
  // offsetFrames, phrase}], startFrame, endFrame, start, end, startAttr, durAttr, frames}.
  function captionPlanV2(words, chunks, opts) {
    opts = opts || {};
    var max = opts.max || 2, phrases = parsePhrases(chunks), wi = opts.from || 0, warnings = [];
    if (!phrases.length) throw new Error('RCK.type.captionPlanV2: no words in "' + chunks + '"');
    phrases.forEach(function (ph, pi) {
      ph.words = ph.tokens.map(function (tk, k) {
        var w = words[wi];
        if (w == null) throw new Error('RCK.type.captionPlanV2: ran out of words at "' + tk + '" in "' + ph.text + '"');
        if (!opts.loose && w.text != null && norm(w.text) !== norm(tk))
          throw new Error('RCK.type.captionPlanV2: "' + ph.text + '" word ' + (k + 1) + ' "' + tk + '" != words[' + wi + '] "' + w.text + '" (pass opts.loose to accept)');
        var t = wordTime(w), o = { text: tk, i: wi, voiceT: t, frame: frame(t), phrase: pi };
        o.offsetFrames = Math.round((o.frame - t * FPS) * 100) / 100;
        wi++;
        return o;
      });
    });
    var nextW = words[wi], lastW = words[wi - 1];
    var endT = opts.end != null ? opts.end : (nextW != null ? wordTime(nextW) : (lastW.comp_end_t != null ? lastW.comp_end_t : wordTime(lastW) + 0.5));
    var endFrame = frame(endT), groups = [];
    for (var p = 0; p < phrases.length;) {
      var q = p;
      while (q + 1 < phrases.length && phrases[q + 1].join) q++;
      var nextF = q + 1 < phrases.length ? phrases[q + 1].words[0].frame : endFrame;
      if (q > p) {
        var ws = [];
        for (var r = p; r <= q; r++) ws = ws.concat(phrases[r].words);
        if (ws.length > max) throw new Error('RCK.type.captionPlanV2: "' + ws.map(function (w) { return w.text; }).join(' ') + '" joined with + has ' + ws.length + ' words (max ' + max + ')');
        groups.push(ws);
      } else {
        groupWords(phrases[p].words, { max: max, forced: phrases[p].forced, endFrame: nextF }).forEach(function (g) { groups.push(g); });
      }
      p = q + 1;
    }
    var out = groups.map(function (ws, gi) {
      return { index: gi, text: ws.map(function (w) { return w.text; }).join(' '), words: ws, startFrame: ws[0].frame };
    });
    out.forEach(function (g, gi) {
      g.endFrame = gi + 1 < out.length ? out[gi + 1].startFrame : endFrame;
      if (gi === 0 && opts.start != null) g.startFrame = Math.min(g.startFrame, frame(opts.start));
      g.frames = g.endFrame - g.startFrame;
      if (g.frames < 1) throw new Error('RCK.type.captionPlanV2: group "' + g.text + '" has no frames (its first word starts on the same frame as the next group\'s); join or regroup with |');
      if (g.frames < 3) warnings.push('group "' + g.text + '" is on screen only ' + g.frames + 'f');
      g.start = g.startFrame / FPS;
      g.end = g.endFrame / FPS;
      g.startAttr = attrF(g.startFrame);
      g.durAttr = durF(g.startFrame, g.endFrame);
    });
    return { groups: out, items: out, phrases: phrases, next: wi, endFrame: endFrame, exitF: opts.exitF || 0, warnings: warnings };
  }
  // One line per group, for the builder to check against the voice: "1 f7-25 (18f)  Why does   Why@7 does@15"
  function captionReport(plan) {
    return plan.groups.map(function (g) {
      return (g.index + 1) + ' f' + g.startFrame + '-' + g.endFrame + ' (' + g.frames + 'f)  ' + g.text + '   ' +
        g.words.map(function (w) { return w.text + '@' + w.frame; }).join(' ');
    }).join('\n') + (plan.warnings && plan.warnings.length ? '\nwarnings: ' + plan.warnings.join('; ') : '');
  }
  var T4_PLACE = { left: 'rc-t4--left', right: 'rc-t4--right', centre: 'rc-t4--centre', center: 'rc-t4--centre', top: 'rc-t4--top', bottom: 'rc-t4--bottom', strip1: 'rc-t4--strip1', strip2: 'rc-t4--strip2', strip3: 'rc-t4--strip3' };
  function placeClass(spec) {
    return String(spec || 'centre').split(/\s+/).filter(Boolean).map(function (t) { return /^rc-/.test(t) ? t : (T4_PLACE[t] || t); }).join(' ');
  }
  function wordSpan(w, extra) { return '<span class="rc-w' + (extra ? ' ' + extra : '') + '" data-rc-f="' + w.frame + '">' + esc(w.text) + '</span>'; }
  // v02 HTML to paste. opts: style 't1' (default) | 't2' | 't4' | 't5'; idPrefix; z; track; low (T1 y 860); onCard
  // (rc-on-card); y (--rc-y px); cls (extra classes); inline (extra inline CSS); exitF (2-3: an eased exit on the LAST group,
  // data-rc-exit-f; exitAll: true puts it on every group; default a hard cut); t2: key = number of keyword words at
  // the end of the pair (default 1); t4: place = one placement per phrase ('left top', 'right', 'strip2', or rc- classes),
  // pieceStyle = inline style per phrase; t5: id, clipStart (s, the black + leak may start before the first word),
  // clipEnd (s). T1/T2/T4: one timed element per group. T5: one timed element, one line per group inside it.
  function captionHTMLV2(plan, opts) {
    opts = opts || {};
    var style = opts.style || 't1', prefix = opts.idPrefix || (style === 't1' ? 'cap' : style);
    var base = { t1: 'rc-t1', t2: 'rc-t2', t4: 'rc-t4', t5: 'rc-t5' }[style];
    if (!base) throw new Error('RCK.type.captionHTMLV2: style must be t1, t2, t4 or t5');
    var cls = 'clip ' + base + ' rc-cap' + (style === 't1' && opts.low ? ' rc-t1--low' : '') + (opts.onCard ? ' rc-on-card' : '') + (opts.cls ? ' ' + opts.cls : '');
    var css = [opts.y != null ? '--rc-y: ' + opts.y + 'px' : '', opts.z != null ? 'z-index: ' + opts.z : '', opts.inline || ''].filter(Boolean).join('; ');
    var st = css ? ' style="' + css + '"' : '';
    var track = opts.track != null ? ' data-track-index="' + opts.track + '"' : '';
    var exF = opts.exitF != null ? opts.exitF : plan.exitF, nG = plan.groups.length;
    var exitOf = function (gi) { return exF && (opts.exitAll || gi === nG - 1) ? ' data-rc-exit-f="' + exF + '"' : ''; };
    var nWords = 0; plan.groups.forEach(function (g) { nWords += g.words.length; });
    var keyFrom = nWords - (opts.key != null ? opts.key : 1), wordIx = 0;
    if (style === 't5') {
      var g0 = plan.groups[0], gl = plan.groups[plan.groups.length - 1];
      var s0 = opts.clipStart != null ? frame(opts.clipStart) : g0.startFrame, s1 = opts.clipEnd != null ? frame(opts.clipEnd) : gl.endFrame;
      var lines = plan.groups.map(function (g, gi) {
        return '<div class="rc-t5__text rc-g" data-rc-from-f="' + g.startFrame + '"' + (gi < nG - 1 ? ' data-rc-to-f="' + g.endFrame + '"' : '') + exitOf(gi) + '>' + g.words.map(function (w) { return wordSpan(w); }).join(' ') + '</div>';
      });
      return '<div id="' + (opts.id || prefix) + '" class="' + cls + '" data-start="' + attrF(s0) + '" data-duration="' + durF(s0, s1) + '"' + track + st + '>' + lines.join('') + '</div>';
    }
    return plan.groups.map(function (g, gi) {
      var inner;
      if (style === 't2') {
        var lead = [], key = [];
        g.words.forEach(function (w) { (wordIx++ >= keyFrom ? key : lead).push(w); });
        inner = '<div class="rc-t2__row rc-g">' +
          (lead.length ? '<span class="rc-t2__lead">' + lead.map(function (w) { return wordSpan(w); }).join(' ') + '</span>' : '') +
          (key.length ? '<span class="rc-t2__key">' + key.map(function (w) { return wordSpan(w, 'rc-w--key'); }).join(' ') + '</span>' : '') + '</div>';
      } else if (style === 't4') {
        var byPhrase = [];
        g.words.forEach(function (w) { var last = byPhrase[byPhrase.length - 1]; if (last && last.phrase === w.phrase) last.ws.push(w); else byPhrase.push({ phrase: w.phrase, ws: [w] }); });
        inner = byPhrase.map(function (b) {
          var ps = opts.pieceStyle && opts.pieceStyle[b.phrase] ? ' style="' + opts.pieceStyle[b.phrase] + '"' : '';
          return '<span class="rc-t4__piece rc-g ' + placeClass(opts.place && opts.place[b.phrase]) + '"' + ps + '>' + b.ws.map(function (w) { return wordSpan(w); }).join(' ') + '</span>';
        }).join('');
      } else {
        inner = '<span class="rc-g">' + g.words.map(function (w) { return wordSpan(w); }).join(' ') + '</span>';
      }
      return '<div id="' + prefix + '-' + (gi + 1) + '" class="' + cls + '" data-start="' + g.startAttr + '" data-duration="' + g.durAttr + '"' + track + exitOf(gi) + st + '>' + inner + '</div>';
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
  function list(target) {   // selector -> all matches; Element -> [el]; NodeList/array -> array
    if (typeof target === 'string') return Array.prototype.slice.call(document.querySelectorAll(target));
    if (target && target.length != null && !target.nodeType) return Array.prototype.slice.call(target);
    return target ? [target] : [];
  }
  function mk(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  // hard cut: frame(t) shows `to`, frame(t)-1 shows `from` (0.5-frame step tween between the two frames; a cut, not a move)
  function hard(tl, target, from, to, t) {
    var n = frame(t), pos = (n - 0.75) / FPS;
    if (pos < 0) { G().set(target, to); return; }
    tl.fromTo(target, from, Object.assign({ duration: 0.5 / FPS, ease: 'steps(1)', immediateRender: false }, to), pos);
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
  function clipStart(root) {
    for (var e = root; e && e.getAttribute; e = e.parentElement) {
      var s = e.getAttribute('data-start'), d = e.getAttribute('data-duration');
      if (s != null && d != null && !isNaN(+s) && !e.hasAttribute('data-composition-id')) return +s;
    }
    return null;
  }
  function seedOf(str) { var h = 2166136261; for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  // Type-on timing (rule C, "easeOutQuad timing over the same total length"): n reveals placed on the ease curve over
  // totalF frames (= GSAP stagger ease 'power1.out'), rounded to whole frames. Returns frame offsets [0 .. totalF].
  function typeOnOffsets(n, totalF, ease) {
    var E = G().parseEase(easeOf(ease, 'power1.out')), out = [];
    for (var i = 0; i < n; i++) out.push(n > 1 ? Math.round(totalF * E(i / (n - 1)) + 1e-9) : 0);
    return out;
  }

  /* ---------------- T2 Punch pair (v01 helper; v02 captions use punchPairV2 / captionHTMLV2 style 't2') ---------------- */
  // Lead-in hard cut = the clip's data-start. Keyword: 6f blur-in (30 -> 0 px) while scaling 108% -> 100%, ease out
  // (power3.out = easeOutQuart, opts.ease), starting at `at`. opts.outAt: start of the 4f fade-out of the pair (power2.in
  // = easeInCubic; clip ends at the returned time). Returns outAt + 4f, else the keyword landing time (at + 6f).
  function punchPair(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), key = root.querySelector('.rc-t2__key'), row = root.querySelector('.rc-t2__row') || key.parentNode;
    var t0 = snap(at);
    G().set(key, { opacity: 0, filter: 'blur(30px)', scale: 1.08 });
    hard(tl, key, { opacity: 0 }, { opacity: 1 }, t0);
    tl.fromTo(key, { filter: 'blur(30px)', scale: 1.08 }, { filter: 'blur(0px)', scale: 1, duration: 6 * F, ease: easeOf(opts.ease, 'power3.out'), immediateRender: false }, t0);
    var end = t0 + 6 * F;
    if (opts.outAt != null) {
      var to = snap(opts.outAt);
      tl.fromTo(row, { opacity: 1 }, { opacity: 0, duration: 4 * F, ease: easeOf(opts.outEase, 'power2.in'), immediateRender: false }, to);
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
  // Digits roll up like an odometer: each digit slides up 40 px inside its mask, 8f, ease out (power3.out, opts.ease),
  // staggered 2f, the first digit at `at`. A month word (.rc-t3__month, "Nov") is static with the card; give it class
  // rc-t3__digit to roll it as one unit first. opts.pushUntil (s): slow push of the card content 100% -> opts.pushTo
  // (1.04) until then, sine.inOut (v02; v01 was linear). Returns the frame the last digit lands. Keep the card >= 1 s
  // after that, then hard cut out (clip end).
  function yearCard(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target); prepYear(root);
    var digits = $$('.rc-t3__digit', root), t0 = snap(at);
    G().set(digits, { opacity: 0, y: 40 });
    digits.forEach(function (d, i) {
      var ti = t0 + 2 * i * F;
      hard(tl, d, { opacity: 0 }, { opacity: 1 }, ti);
      tl.fromTo(d, { y: 40 }, { y: 0, duration: 8 * F, ease: easeOf(opts.ease, 'power3.out'), immediateRender: false }, ti);
    });
    var land = t0 + (2 * Math.max(0, digits.length - 1) + 8) * F;
    if (opts.pushUntil != null) {
      var block = root.querySelector('.rc-t3__block');
      var p0 = opts.pushFrom != null ? snap(opts.pushFrom) : t0;
      G().set(block, { transformOrigin: '50% 50%' });
      tl.fromTo(block, { scale: 1 }, { scale: opts.pushTo != null ? opts.pushTo : 1.04, duration: Math.max(F, snap(opts.pushUntil) - p0), ease: easeOf(opts.pushEase, 'sine.inOut'), immediateRender: false }, p0);
    }
    return land;
  }

  /* ---------------- T4 Spread words (v01 helpers; v02 captions use spreadWordsV2 / captionHTMLV2 style 't4') ---------------- */
  // One piece: fades in over 4f (power2.out = easeOutCubic) while drifting 12 px up (power3.out), from `at`.
  function spreadIn(tl, piece, at) {
    var p = $(piece), t0 = snap(at);
    G().set(p, { opacity: 0, y: 12 });
    tl.fromTo(p, { opacity: 0 }, { opacity: 1, duration: 4 * F, ease: 'power2.out', immediateRender: false }, t0);
    tl.fromTo(p, { y: 12 }, { y: 0, duration: 4 * F, ease: 'power3.out', immediateRender: false }, t0);
    return t0 + 4 * F;
  }
  // All pieces of the T4 element leave together with a 4f fade (power2.in = easeInCubic) from `at`.
  function spreadOut(tl, target, at) {
    var pieces = $$('.rc-t4__piece', $(target)), t0 = snap(at);
    tl.fromTo(pieces, { opacity: 1 }, { opacity: 0, duration: 4 * F, ease: 'power2.in', immediateRender: false }, t0);
    return t0 + 4 * F;
  }
  // Whole T4: opts.times = [t piece1, t piece2, ...] (default: every piece at `at`); opts.outAt = joint 4f fade (omit
  // to stay until the clip's hard cut). Returns the last end. (v02: more than 2 words on screen breaks rule A.)
  function spreadWords(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), pieces = $$('.rc-t4__piece', root), end = snap(at);
    pieces.forEach(function (p, i) { end = Math.max(end, spreadIn(tl, p, opts.times && opts.times[i] != null ? opts.times[i] : at)); });
    if (opts.outAt != null) end = Math.max(end, spreadOut(tl, root, opts.outAt));
    return end;
  }

  /* ---------------- T7 Inline chip (v02: the bug chip is replaced by the word "bug", note 8; kept for compatibility) ---------------- */
  // Chip scales 0 -> 112% -> 100% over 8f: 0 -> 1.12 in 5f (power3.out), 1.12 -> 1.00 in 3f (power2.inOut), so frame +5
  // is exactly 112% and frame +8 is 100%. opts.ease (e.g. "back.out(1.7)") switches to one 8f tween. Returns at + 8f.
  function chipPop(tl, chip, at, opts) {
    opts = opts || {};
    var c = $(chip), t0 = snap(at);
    G().set(c, { scale: 0, transformOrigin: '50% 50%' });
    if (opts.ease) {
      tl.fromTo(c, { scale: 0 }, { scale: 1, duration: 8 * F, ease: easeOf(opts.ease, 'back.out(1.7)'), immediateRender: false }, t0);
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

  /* ---------------- T5 Glow line (v01 helper; v02 captions use glowLineV2 / captionHTMLV2 style 't5') ---------------- */
  function addLeak(root) {
    var leak = root.querySelector('.rc-t5__leak');
    if (!leak) {
      leak = mk('div', 'rc-t5__leak');
      leak.setAttribute('aria-hidden', 'true');
      leak.setAttribute('data-layout-ignore', '');
      ['a', 'b', 'c'].forEach(function (k) { leak.appendChild(mk('i', 'rc-t5__leak-' + k)); });
      root.insertBefore(leak, root.firstChild);
    }
    return leak;
  }
  function glowCopies(line, text) {
    if (line.querySelector('.rc-t5__glow')) return;
    ['wide', 'near'].forEach(function (k) {
      var c = text.cloneNode(true);
      c.className = 'rc-t5__glow rc-t5__glow--' + k;
      c.setAttribute('aria-hidden', 'true');
      c.setAttribute('data-layout-ignore', '');
      c.removeAttribute('id');
      ['data-rc-from-f', 'data-rc-to-f', 'data-rc-exit-f'].forEach(function (a) { c.removeAttribute(a); });
      $$('[id]', c).forEach(function (n) { n.removeAttribute('id'); });
      $$('.rc-t7__chip', c).forEach(function (chip) { chip.parentNode.replaceChild(mk('span', 'rc-t7__gap'), chip); });
      line.insertBefore(c, text);
    });
  }
  function prepGlow(root) {
    var text = root.querySelector('.rc-t5__text');
    if (!text) throw new Error('RCK.type.glowLine: .rc-t5__text missing');
    var line = root.querySelector('.rc-t5__line');
    if (!line) { line = mk('div', 'rc-t5__line'); text.parentNode.insertBefore(line, text); line.appendChild(text); }
    glowCopies(line, text);
    return { line: line, text: text, leak: addLeak(root) };
  }
  // The light leak behind a T5 line (registry organic-light-leak-overlay, retinted): rises to peak (0.16) with sine.out
  // over max(12f, 24%), settles to hold (0.1) with sine.inOut, its three layers drift sine.inOut, from t0 to `until`.
  function leakDrift(tl, leak, t0, until, opts) {
    var g = G(), d = until - t0, peak = opts.leakPeak != null ? opts.leakPeak : 0.16, hold = opts.leakHold != null ? opts.leakHold : 0.1;
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
  // Fades in over 12f from blur 20 -> 0 and tracking +2% -> 0 (opacity power2.out, blur/tracking power3.out) at `at`.
  // A light leak drifts behind from `at` to the clip end (or opts.leakUntil). opts.chipAt: the M4 chip pops (T7).
  // Returns at + 12f (line landed).
  function glowLine(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), parts = prepGlow(root), t0 = snap(at), g = G();
    var line = parts.line;
    g.set(line, { opacity: 0, filter: 'blur(20px)', '--rc-t5-track': '0.02em' });
    tl.fromTo(line, { opacity: 0 }, { opacity: 1, duration: 12 * F, ease: 'power2.out', immediateRender: false }, t0);
    tl.fromTo(line, { filter: 'blur(20px)', '--rc-t5-track': '0.02em' }, { filter: 'blur(0px)', '--rc-t5-track': '0em', duration: 12 * F, ease: 'power3.out', immediateRender: false }, t0);
    if (opts.leak !== false) {
      var until = opts.leakUntil != null ? snap(opts.leakUntil) : clipEnd(root);
      if (until == null || until <= t0) until = t0 + 2;
      leakDrift(tl, parts.leak, t0, until, opts);
    }
    var chip = parts.text.querySelector('.rc-t7__chip');
    if (chip) chipPop(tl, chip, opts.chipAt != null ? opts.chipAt : t0 + 12 * F, opts);
    return t0 + 12 * F;
  }

  /* ---------------- T6 Giant type ---------------- */
  // Types on letter by letter in reading order across the stacked lines, hard (no fades). v02: the letters keep the v01
  // total length ((n-1) x opts.every frames, every = 2) but are placed on an ease (opts.ease, default power1.out =
  // easeOutQuad timing, the stagger ease rule C names) instead of a constant step. opts.totalF overrides the length.
  // Returns the frame the last letter appears; hold >= 1 s after it.
  function giantType(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), step = opts.every || 2, t0 = snap(at);
    if (!root.getAttribute('data-rck')) { $$('.rc-t6__line', root).forEach(function (l) { splitChars(l, 'rc-t6__ch'); }); root.setAttribute('data-rck', '1'); }
    var chars = $$('.rc-t6__ch', root).filter(function (c) { return /\S/.test(c.textContent); });
    G().set($$('.rc-t6__ch', root), { opacity: 0 });
    $$('.rc-t6__ch', root).forEach(function (c) { if (!/\S/.test(c.textContent)) G().set(c, { opacity: 1 }); });
    var total = opts.totalF != null ? opts.totalF : Math.max(0, chars.length - 1) * step;
    var offs = typeOnOffsets(chars.length, total, opts.ease);
    chars.forEach(function (c, i) { hard(tl, c, { opacity: 0 }, { opacity: 1 }, t0 + offs[i] * F); });
    return t0 + (offs.length ? offs[offs.length - 1] : 0) * F;
  }

  /* ---------------- T8 Name / quote card ---------------- */
  // Name (+ underline) fade in over 6f (power2.out = easeOutCubic); the role fades to its 60% over the same 6f.
  // Returns at + 6f.
  function nameIn(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), t0 = snap(at), g = G(), e = easeOf(opts.ease, 'power2.out');
    var name = $$('.rc-t8__name', root), role = $$('.rc-t8__role', root);
    g.set(name, { opacity: 0 }); g.set(role, { opacity: 0 });
    if (name.length) tl.fromTo(name, { opacity: 0 }, { opacity: 1, duration: 6 * F, ease: e, immediateRender: false }, t0);
    if (role.length) tl.fromTo(role, { opacity: 0 }, { opacity: 0.6, duration: 6 * F, ease: e, immediateRender: false }, t0);
    return t0 + 6 * F;
  }
  // Quote types on character by character, first character(s) on `at`. v02: the v01 length (2 characters per frame:
  // floor((n-1)/2) frames, opts.perFrame) is kept, the reveals are placed on an ease (opts.ease, default power1.out)
  // instead of a constant rate. Returns the frame the last character appears.
  function quoteType(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), q = root.classList.contains('rc-t8__quote') ? root : root.querySelector('.rc-t8__quote');
    if (!q.getAttribute('data-rck')) { splitChars(q, 'rc-t8__ch'); q.setAttribute('data-rck', '1'); }
    var chars = $$('.rc-t8__ch', q), per = opts.perFrame || 2, t0 = snap(at);
    G().set(chars, { opacity: 0 });
    var total = opts.totalF != null ? opts.totalF : Math.floor(Math.max(0, chars.length - 1) / per);
    var offs = typeOnOffsets(chars.length, total, opts.ease), last = t0;
    chars.forEach(function (c, i) { var t = t0 + offs[i] * F; hard(tl, c, { opacity: 0 }, { opacity: 1 }, t); last = Math.max(last, t); });
    return last;
  }
  // B3 (v01): moves the .rc-t8__walker slot (the Lemming) along the name's underline, left -> right (opts.reverse: right ->
  // left), sine.inOut (v02; opts.ease), over opts.duration seconds (default 1). Returns the end time.
  function walk(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), u = root.classList.contains('rc-t8__underline') ? root : root.querySelector('.rc-t8__underline');
    var t0 = snap(at), d = Math.max(F, snap(opts.duration != null ? opts.duration : 1));
    var a = opts.reverse ? 1 : 0, b = opts.reverse ? 0 : 1;
    G().set(u, { '--rc-walk': a });
    tl.fromTo(u, { '--rc-walk': a }, { '--rc-walk': b, duration: d, ease: easeOf(opts.ease, 'sine.inOut'), immediateRender: false }, t0);
    return t0 + d;
  }

  /* ---------------- T9 Highlight / label ---------------- */
  // Highlight swipes left -> right over 8f, ease out (power3.out; clip-path reveal; size untouched). Returns at + 8f.
  function highlight(tl, target, at, opts) {
    opts = opts || {};
    var h = $(target), t0 = snap(at);
    G().set(h, { clipPath: 'inset(0% 100% 0% 0%)' });
    tl.fromTo(h, { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 8 * F, ease: easeOf(opts.ease, 'power3.out'), immediateRender: false }, t0);
    return t0 + 8 * F;
  }
  // Label pops in over 4f: scale 96% -> 100% with a fade (the plan's L3 "pop in" definition), ease out. Returns at + 4f.
  function label(tl, target, at, opts) {
    opts = opts || {};
    var root = $(target), l = root.classList.contains('rc-t9__label') ? root : root.querySelector('.rc-t9__label'), t0 = snap(at);
    G().set(l, { opacity: 0, scale: 0.96 });
    tl.fromTo(l, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 4 * F, ease: easeOf(opts.ease, 'power3.out'), immediateRender: false }, t0);
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
  // each frame (hard per-frame cuts, seeded: opts.seed, default from the element id; a new pattern every frame, never all
  // three the same way), then settles clean (opts.settle = false keeps the last glitch frame). Before `at` the word shows
  // clean. One word = rule A compliant as is (it appears on its own frame). Returns at + frames (the first clean frame).
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

  /* ================= v02 captions: runtime (DOM + GSAP) ================= */
  // Word pop presets per style (kit choices inside rule A's "4-5f opacity 0->1 + scale 0.86->1 + small rise, expo.out").
  // lead = frames the pop starts BEFORE the word's onset frame, so the onset frame already shows the word (75% at expo.out).
  var POP = {
    t1:   { frames: 5, lead: 1, scale: 0.86, rise: 8, ease: 'expo.out' },
    t4:   { frames: 5, lead: 1, scale: 0.9, rise: 12, ease: 'expo.out' },             // keeps T4's 12 px drift up
    lead: { frames: 5, lead: 1, scale: 0.86, rise: 6, ease: 'expo.out' },             // T2 lead-in words
    key:  { frames: 6, lead: 0, scale: 1.08, blur: 30, ease: 'expo.out', hard: true }, // T2 keyword: v01 blur punch, eased
    t5:   { frames: 6, lead: 1, blur: 14, ease: 'expo.out', fade: 'power2.out' }      // T5: soft blur-in + fade, no scale
  };
  function styleOf(root) {
    var c = root.classList;
    return c.contains('rc-t2') ? 't2' : c.contains('rc-t4') ? 't4' : c.contains('rc-t5') ? 't5' : 't1';
  }
  function popWord(tl, w, k, p) {
    var g = G(), targets = [w].concat(w.__rcCopies || []), d = p.frames * F;
    g.set(targets, { transformOrigin: '50% 75%' });
    if (p.hard) {                                   // visible at full opacity on its own frame, then the punch settles
      g.set(targets, { opacity: 0, scale: p.scale, filter: 'blur(' + p.blur + 'px)' });
      hard(tl, targets, { opacity: 0 }, { opacity: 1 }, k / FPS);
      tl.fromTo(targets, { scale: p.scale, filter: 'blur(' + p.blur + 'px)' }, { scale: 1, filter: 'blur(0px)', duration: d, ease: p.ease, immediateRender: false }, k / FPS);
      return (k + p.frames) / FPS;
    }
    var k0 = Math.max(0, k - p.lead), t0 = k0 / FPS, from = {}, to = {};
    if (p.scale != null && p.scale !== 1) { from.scale = p.scale; to.scale = 1; }
    if (p.rise) { from.y = p.rise; to.y = 0; }
    if (p.blur) { from.filter = 'blur(' + p.blur + 'px)'; to.filter = 'blur(0px)'; }
    g.set(targets, Object.assign({ opacity: 0 }, from));
    if (p.fade) {
      tl.fromTo(targets, { opacity: 0 }, { opacity: 1, duration: d, ease: p.fade, immediateRender: false }, t0);
      tl.fromTo(targets, from, Object.assign({ duration: d, ease: p.ease, immediateRender: false }, to), t0);
    } else {
      tl.fromTo(targets, Object.assign({ opacity: 0 }, from), Object.assign({ opacity: 1, duration: d, ease: p.ease, immediateRender: false }, to), t0);
    }
    return (k0 + p.frames) / FPS;
  }
  // A group's window inside a longer clip: hidden before fromF, shown fromF .. toF-1, gone from toF (hard cut), or an
  // eased exit (exitF 2-3 frames: opacity 1 -> 0, scale 1 -> 0.96, blur 0 -> 4 px, power2.in) ending exactly on toF.
  // The last group (no toF) ends with the clip; with exitF it exits before clipEndF instead. An exit is skipped (hard
  // cut) when it would start before the group's last word has landed.
  function groupWindow(tl, g, fromF, toF, exitF, lastPopF, clipEndF) {
    G().set(g, { opacity: 0 });
    hard(tl, g, { opacity: 0 }, { opacity: 1 }, fromF / FPS);
    if (toF == null) {
      if (exitF && clipEndF != null && clipEndF - exitF >= lastPopF) groupExit(tl, g, clipEndF, exitF);
      return;
    }
    if (exitF && toF - exitF >= lastPopF) groupExit(tl, g, toF, exitF);
    else hard(tl, g, { opacity: 1 }, { opacity: 0 }, toF / FPS);
  }
  function groupExit(tl, g, endF, exitF) {
    G().set(g, { transformOrigin: '50% 60%' });
    tl.fromTo(g, { opacity: 1, scale: 1, filter: 'blur(0px)' }, { opacity: 0, scale: 0.96, filter: 'blur(4px)', duration: exitF * F, ease: 'power2.in', immediateRender: false }, (endF - exitF) / FPS);
  }
  var groupSeq = 0;
  function wordsOf(scope) { return $$('.rc-w[data-rc-f]', scope).filter(function (w) { return !w.closest('.rc-t5__glow'); }); }
  // T5 v02: every .rc-t5__text (one per group) gets its own .rc-t5__line with the two glow copies; the group window
  // attributes move to the line; each word is linked to its two copies so they pop together. Adds the leak.
  function prepGlowV2(root) {
    if (root.__rckGlow) return root.__rckGlow;
    var texts = $$('.rc-t5__text', root).filter(function (t) { return !t.closest('.rc-t5__glow'); });
    var lines = texts.map(function (text) {
      var line = text.parentNode.classList.contains('rc-t5__line') ? text.parentNode : null;
      if (!line) { line = mk('div', 'rc-t5__line'); text.parentNode.insertBefore(line, text); line.appendChild(text); }
      ['data-rc-from-f', 'data-rc-to-f', 'data-rc-exit-f'].forEach(function (a) { if (text.hasAttribute(a)) { line.setAttribute(a, text.getAttribute(a)); text.removeAttribute(a); } });
      if (text.classList.contains('rc-g')) { text.classList.remove('rc-g'); line.classList.add('rc-g'); }
      glowCopies(line, text);
      var ws = $$('.rc-w', text), wide = $$('.rc-w', line.querySelector('.rc-t5__glow--wide')), near = $$('.rc-w', line.querySelector('.rc-t5__glow--near'));
      ws.forEach(function (w, i) { w.__rcCopies = [wide[i], near[i]].filter(Boolean); });
      return line;
    });
    root.__rckGlow = { lines: lines, leak: addLeak(root) };
    return root.__rckGlow;
  }
  // Animates v02 caption markup (captionHTMLV2 output, or anything wordsV2 converted): every .rc-w[data-rc-f] pops on
  // its frame with its style's preset (opts.pop overrides any preset field, e.g. { t1: { ease: 'back.out(1.7)' } });
  // groups with data-rc-from-f / data-rc-to-f are shown only in that window. Between groups: a hard cut. Exits (rule A
  // "<= 3f, eased"): a data-rc-exit-f attribute on a group / a one-group clip (captionHTMLV2 writes it on the LAST group
  // only) gives that group a 2-3f eased exit; opts.exitF does the same for the last group of each converted clip, and
  // opts.exitAll = true applies opts.exitF to every group. T5: glow copies + leak (opts.leak false, leakFrom (s),
  // leakUntil (s), leakPeak, leakHold). scope: selector / element(s); default every .rc-cap.
  // Call once per element (later calls skip processed clips). Returns the time the last word has landed.
  function captionPops(tl, scope, opts) {
    opts = opts || {};
    var roots = scope == null ? list('.rc-cap') : list(scope), end = 0;
    roots.forEach(function (root) {
      if (root.__rckPops) return;
      root.__rckPops = true;
      var style = styleOf(root), presets = {};
      Object.keys(POP).forEach(function (k) { presets[k] = Object.assign({}, POP[k], opts.pop && opts.pop[k]); });
      if (style === 't5') prepGlowV2(root);
      var words = wordsOf(root);
      if (!words.length && window.console) console.warn('RCK.type.captionPops: no .rc-w[data-rc-f] words in ' + (root.id || root.className));
      var lastPopF = {}, rootLast = 0;
      words.forEach(function (w) {
        var k = parseInt(w.getAttribute('data-rc-f'), 10);
        var p = style === 't2' ? (w.classList.contains('rc-w--key') || w.closest('.rc-t2__key') ? presets.key : presets.lead) : presets[style];
        var e = popWord(tl, w, k, p);
        end = Math.max(end, e);
        var grp = w.closest('.rc-g') || root;
        if (!grp.__rcgId) grp.__rcgId = 'g' + (++groupSeq);
        lastPopF[grp.__rcgId] = Math.max(lastPopF[grp.__rcgId] || 0, frame(e));
        rootLast = Math.max(rootLast, frame(e));
      });
      var ceT = clipEnd(root), ceF = ceT != null ? frame(ceT) : null, optEx = opts.exitF || 0;
      var windows = $$('[data-rc-from-f]', root).filter(function (g) { return !g.closest('.rc-t5__glow'); });
      windows.forEach(function (g) {
        var toF = g.hasAttribute('data-rc-to-f') ? +g.getAttribute('data-rc-to-f') : null;
        var ex = g.hasAttribute('data-rc-exit-f') ? +g.getAttribute('data-rc-exit-f') : (opts.exitAll || toF == null ? optEx : 0);
        groupWindow(tl, g, +g.getAttribute('data-rc-from-f'), toF, ex, lastPopF[g.__rcgId] || 0, ceF);
      });
      if (!windows.length) {                        // a one-group clip (captionHTMLV2): exit before the clip end
        var ex1 = root.hasAttribute('data-rc-exit-f') ? +root.getAttribute('data-rc-exit-f') : (opts.exitAll ? optEx : 0), g1 = root.querySelector('.rc-g');
        if (ex1 && ceF != null && g1 && ceF - ex1 >= rootLast) groupExit(tl, g1, ceF, ex1);
      }
      if (style === 't5' && opts.leak !== false) {
        var first = words.length ? Math.min.apply(null, words.map(function (w) { return +w.getAttribute('data-rc-f'); })) : frame(clipStart(root) || 0);
        var t0 = opts.leakFrom != null ? snap(opts.leakFrom) : first / FPS;
        var until = opts.leakUntil != null ? snap(opts.leakUntil) : clipEnd(root);
        if (until == null || until <= t0) until = t0 + 2;
        leakDrift(tl, root.__rckGlow.leak, t0, until, opts);
      }
    });
    return end;
  }

  /* ---------------- v02 converter: v01 caption markup -> word by word (in place) ---------------- */
  function barTokens(text) {   // like tokens(), but keeps '|' (a forced group break written in v01 markup)
    return String(text).replace(/\|/g, ' | ').split(/\s+/).filter(function (w) { return w === '|' || norm(w).length; });
  }
  function phrasesOf(root, style) {
    if (style === 't2') {
      var row = root.querySelector('.rc-t2__row') || root, lead = row.querySelector('.rc-t2__lead'), key = row.querySelector('.rc-t2__key'), toks = [];
      if (lead) barTokens(lead.textContent).forEach(function (t) { toks.push({ text: t, role: 'lead' }); });
      if (key) barTokens(key.textContent).forEach(function (t) { toks.push({ text: t, role: 'key' }); });
      return [{ toks: toks, host: row }];
    }
    if (style === 't4') return $$('.rc-t4__piece', root).map(function (p) { return { toks: barTokens(p.textContent).map(function (t) { return { text: t }; }), host: p }; });
    if (style === 't5') {
      var tx = root.querySelector('.rc-t5__text');
      if (!tx) throw new Error('RCK.type.glowLineV2: .rc-t5__text missing');
      if (tx.querySelector('.rc-t7__chip, img, svg')) throw new Error('RCK.type.glowLineV2: v02 note 8 replaces the bug chip with the word "bug"; write the word in .rc-t5__text');
      return [{ toks: barTokens(tx.textContent).map(function (t) { return { text: t }; }), host: tx }];
    }
    return [{ toks: barTokens(root.textContent).map(function (t) { return { text: t }; }), host: root }];
  }
  function spans(ws, keyCls) { return ws.map(function (w) { return wordSpan(w, keyCls && w.role === 'key' ? keyCls : ''); }).join(' '); }
  // Converts v01 caption clips to v02 and animates them (captionPops). targets: one or more clips in reading order (T1
  // .rc-t1 chunks, a T2 .rc-t2 pair, a T4 .rc-t4, a T5 .rc-t5); words: seconds per word (array of numbers) or words.json
  // entries ({text, comp_t}; spelling checked unless opts.loose), consumed in order across the targets from opts.from.
  // Each clip's text is split into groups of max 2 words (groupWords; '|' in the text forces a break and is removed),
  // stacked in place; a group shows from its first word's frame to the next group's first frame (the last one to the clip
  // end). T4: each piece is a phrase; neighbouring one-word pieces share a group (opts.join false to stop it). Other
  // opts as captionPops (exitF, pop, leak...). Returns the time the last word has landed.
  function wordsV2(tl, targets, words, opts) {
    opts = opts || {};
    var roots = list(targets), wi = opts.from || 0, end = 0, max = opts.max || 2;
    if (!roots.length) throw new Error('RCK.type.wordsV2: no target ' + targets);
    roots.forEach(function (root) {
      if (root.__rckPops) return;
      var style = styleOf(root), phrases = phrasesOf(root, style);
      phrases.forEach(function (ph) {
        var forced = [], clean = [];
        ph.toks.forEach(function (t) { if (t.text === '|') { if (clean.length) forced.push(clean.length); } else clean.push(t); });
        ph.forced = forced;
        ph.words = clean.map(function (t) {
          var w = words[wi];
          if (w == null) throw new Error('RCK.type.wordsV2: ran out of word times at "' + t.text + '"');
          if (!opts.loose && w && w.text != null && norm(w.text) !== norm(t.text))
            throw new Error('RCK.type.wordsV2: "' + t.text + '" != words[' + wi + '] "' + w.text + '" (pass opts.loose to accept)');
          wi++;
          return { text: t.text, role: t.role, frame: frame(wordTime(w)) };
        });
      });
      var ce = clipEnd(root), endF = opts.end != null ? frame(opts.end) : (ce != null ? frame(ce) : null);
      // groups (in order) with the phrase they belong to
      var groups = [];
      phrases.forEach(function (ph, pi) {
        var nextF = pi + 1 < phrases.length ? phrases[pi + 1].words[0].frame : endF;
        var gs = ph.words.length ? groupWords(ph.words, { max: max, forced: ph.forced, endFrame: nextF }) : [];
        gs.forEach(function (g) { groups.push({ words: g, parts: [{ phrase: pi, ws: g }] }); });
      });
      if (style === 't4' && opts.join !== false) {    // one-word pieces next to each other share a group (B3 Dundee, / Scotland.)
        for (var i = 0; i + 1 < groups.length; i++) {
          var a = groups[i], b = groups[i + 1];
          if (a.words.length + b.words.length <= max && a.parts.length === 1 && b.parts.length === 1 && a.parts[0].phrase !== b.parts[0].phrase &&
              phrases[a.parts[0].phrase].words.length === 1 && phrases[b.parts[0].phrase].words.length === 1) {
            a.words = a.words.concat(b.words); a.parts = a.parts.concat(b.parts); groups.splice(i + 1, 1);
          }
        }
      }
      groups.forEach(function (g, gi) { g.from = g.words[0].frame; g.to = gi + 1 < groups.length ? groups[gi + 1].words[0].frame : null; });
      var attrs = function (g) { return ' data-rc-from-f="' + g.from + '"' + (g.to != null ? ' data-rc-to-f="' + g.to + '"' : ''); };
      if (style === 't2') {
        var row = phrases[0].host, stack = mk('div', 'rc-stack rc-t2__stack');
        stack.innerHTML = groups.map(function (g) {
          var lead = g.words.filter(function (w) { return w.role !== 'key'; }), key = g.words.filter(function (w) { return w.role === 'key'; });
          return '<div class="rc-t2__row rc-g"' + attrs(g) + '>' + (lead.length ? '<span class="rc-t2__lead">' + spans(lead) + '</span>' : '') +
            (key.length ? '<span class="rc-t2__key">' + spans(key, 'rc-w--key') + '</span>' : '') + '</div>';
        }).join('');
        row.parentNode.replaceChild(stack, row);
      } else if (style === 't4') {
        phrases.forEach(function (ph, pi) {
          var mine = [];
          groups.forEach(function (g) { g.parts.forEach(function (pt) { if (pt.phrase === pi) mine.push({ g: g, ws: pt.ws }); }); });
          ph.host.innerHTML = '<span class="rc-stack">' + mine.map(function (m) { return '<span class="rc-g"' + attrs(m.g) + '>' + spans(m.ws) + '</span>'; }).join('') + '</span>';
        });
      } else if (style === 't5') {
        var tx = phrases[0].host;
        groups.forEach(function (g) {
          var t = mk('div', 'rc-t5__text rc-g');
          t.setAttribute('data-rc-from-f', g.from);
          if (g.to != null) t.setAttribute('data-rc-to-f', g.to);
          t.innerHTML = spans(g.words);
          tx.parentNode.insertBefore(t, tx);
        });
        tx.parentNode.removeChild(tx);
      } else {
        root.innerHTML = '<span class="rc-stack">' + groups.map(function (g) { return '<span class="rc-g"' + attrs(g) + '>' + spans(g.words) + '</span>'; }).join('') + '</span>';
      }
      root.classList.add('rc-cap');
      end = Math.max(end, captionPops(tl, root, opts));
    });
    return end;
  }
  // v01-markup wrappers with the v01 helper names (same signature as wordsV2: (tl, target, words, opts)).
  function punchPairV2(tl, target, words, opts) {
    if (typeof words === 'number') throw new Error('RCK.type.punchPairV2: pass one time per word (lead-in words + keyword), not the keyword time');
    return wordsV2(tl, target, words, opts);
  }
  function spreadWordsV2(tl, target, words, opts) { return wordsV2(tl, target, words, opts); }
  function glowLineV2(tl, target, words, opts) { return wordsV2(tl, target, words, opts); }

  /* ================= v03 caption lockups (REVISION_v03 notes 11, 16, 17; refs_v03/1 + 3) ================= */
  // Coolvetica advance widths (1/1000 em; the Regular and Italic files share advances and kerning) for CV_CHARS, and the
  // GPOS pair kerning (|v| >= 10 units), read from fonts/Coolvetica-*.otf with fontTools. Used in Node to choose sizes and
  // line breaks (the browser lays the text out itself; the table reproduces Chrome's widths within ~1%).
  var CV_CHARS = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~’‘“”…–—éèáàüöä€£';
  var CV_ADV = '241,245,289,501,484,669,505,145,326,326,539,523,187,280,187,300,490,296,465,479,476,490,487,478,495,487,171,175,523,523,523,491,708,643,574,613,607,532,505,658,587,187,454,604,501,695,591,670,534,671,578,563,554,586,593,856,605,602,532,319,294,316,459,478,352,486,524,481,523,503,295,530,503,192,195,483,185,754,503,539,523,513,321,472,453,500,501,714,496,502,445,334,338,330,555,193,193,386,386,936,436,617,503,503,486,486,500,539,486,616,482'.split(',').map(Number);
  var CV_KERN = {"\",":-40,"\".":-40,"\"/":-60,"\"4":-38,"\"8":-16,"\"A":-90,"\"J":-113,"\"a":-23,"\"c":-40,"\"d":-40,"\"e":-40,"\"g":-34,"\"o":-40,"\"q":-40,"\"s":-19,"\"à":-23,"\"á":-23,"\"ä":-23,"\"è":-40,"\"é":-40,"\"ö":-40,"\"…":-40,"&A":-32,"&T":-151,"&V":-96,"&W":-69,"&X":-52,"&Y":-129,"&j":46,"&v":-30,"&w":-30,"&x":-49,"',":-40,"'.":-40,"'/":-60,"'4":-38,"'8":-16,"'A":-90,"'J":-113,"'a":-23,"'c":-40,"'d":-40,"'e":-40,"'g":-34,"'o":-40,"'q":-40,"'s":-19,"'à":-23,"'á":-23,"'ä":-23,"'è":-40,"'é":-40,"'ö":-40,"'…":-40,"(j":224,",\"":-40,",'":-40,",-":-34,",0":-31,",1":-123,",3":-21,",4":-21,",5":-27,",6":-27,",7":-44,",8":-22,",9":-15,",C":-33,",G":-33,",O":-33,",Q":-33,",S":-10,",T":-147,",U":-18,",V":-111,",W":-91,",Y":-133,",f":-50,",g":-28,",j":73,",t":-23,",u":-17,",v":-60,",w":-60,",y":-23,",ü":-17,",–":-34,",—":-34,",‘":-40,",’":-40,",“":-40,",”":-40,"-,":-30,"-.":-30,"-/":-34,"-1":-94,"-2":-57,"-3":-64,"-7":-108,"-8":-15,"-9":-13,"-A":-73,"-S":-31,"-T":-137,"-V":-83,"-W":-62,"-X":-105,"-Y":-112,"-Z":-58,"-f":-60,"-s":-14,"-v":-35,"-w":-35,"-x":-67,"-z":-47,"-…":-30,".\"":-40,".'":-40,".-":-34,".0":-31,".1":-123,".3":-21,".4":-21,".5":-27,".6":-27,".7":-44,".8":-22,".9":-15,".C":-33,".G":-33,".O":-33,".Q":-33,".S":-10,".T":-147,".U":-18,".V":-111,".W":-91,".Y":-133,".f":-50,".g":-28,".j":73,".t":-23,".u":-17,".v":-60,".w":-60,".y":-23,".ü":-17,".–":-34,".—":-34,".‘":-40,".’":-40,".“":-40,".”":-40,"/&":-38,"/,":-132,"/-":-40,"/.":-132,"/A":-149,"/C":-46,"/G":-46,"/J":-91,"/O":-46,"/Q":-46,"/S":-27,"/a":-68,"/c":-78,"/d":-78,"/e":-78,"/f":-23,"/g":-72,"/m":-40,"/n":-40,"/o":-78,"/p":-40,"/q":-78,"/r":-40,"/s":-65,"/u":-39,"/v":-19,"/w":-19,"/x":-35,"/y":-35,"/z":-50,"/à":-68,"/á":-68,"/ä":-68,"/è":-78,"/é":-78,"/ö":-78,"/ü":-39,"/–":-40,"/—":-40,"/…":-132,"0,":-31,"0.":-31,"07":-26,"0…":-31,"2-":-37,"22":11,"2–":-37,"2—":-37,"3\"":-13,"3'":-13,"3,":-21,"3.":-21,"31":-10,"37":-23,"3‘":-13,"3’":-13,"3“":-13,"3”":-13,"3…":-21,"4\"":-33,"4'":-33,"41":-51,"47":-36,"4‘":-33,"4’":-33,"4“":-33,"4”":-33,"5,":-21,"5.":-21,"5…":-21,"6\"":-14,"6'":-14,"6,":-26,"6.":-26,"69":-19,"6‘":-14,"6’":-14,"6“":-14,"6”":-14,"6…":-26,"7,":-137,"7-":-113,"7.":-137,"70":-39,"72":-22,"73":-21,"74":-114,"76":-35,"77":10,"78":-44,"79":-22,"7A":-169,"7–":-113,"7—":-113,"7…":-137,"8\"":-17,"8'":-17,"8,":-20,"8-":-18,"8.":-20,"80":-11,"87":-46,"89":-22,"8–":-18,"8—":-18,"8‘":-17,"8’":-17,"8“":-17,"8”":-17,"8…":-20,"9,":-39,"9.":-39,"97":-33,"9…":-39,"@j":164,"A\"":-90,"A&":-26,"A'":-90,"A-":-71,"A?":-148,"AC":-70,"AG":-70,"AJ":-26,"AO":-70,"AQ":-70,"AS":-31,"AT":-169,"AU":-62,"AV":-185,"AW":-155,"AY":-153,"Aa":-18,"Ac":-40,"Ad":-40,"Ae":-40,"Af":-59,"Ag":-38,"Aj":20,"Ao":-40,"Aq":-40,"As":-25,"At":-39,"Au":-34,"Av":-116,"Aw":-116,"Ay":-37,"Aà":-18,"Aá":-18,"Aä":-18,"Aè":-40,"Aé":-40,"Aö":-40,"Aü":-34,"A–":-71,"A—":-71,"A‘":-90,"A’":-90,"A“":-90,"A”":-90,"BA":-30,"BJ":12,"BT":-23,"BV":-45,"BW":-28,"BX":-62,"BY":-60,"Bj":-12,"C,":-22,"C-":-28,"C.":-22,"C/":-25,"CA":-45,"CT":-24,"CV":-39,"CW":-28,"CX":-58,"CY":-62,"CZ":-22,"Cj":23,"C–":-28,"C—":-28,"C…":-22,"D,":-40,"D.":-40,"D/":-36,"DA":-72,"DT":-61,"DV":-69,"DW":-63,"DX":-104,"DY":-96,"DZ":-32,"Da":-13,"Dj":10,"Dx":-15,"Dz":-14,"Dà":-13,"Dá":-13,"Dä":-13,"D…":-40,"F,":-122,"F.":-122,"F/":-73,"FA":-113,"FC":-31,"FG":-31,"FJ":-181,"FO":-31,"FQ":-31,"FT":12,"Fa":-44,"Fc":-37,"Fd":-37,"Fe":-37,"Fg":-32,"Fj":-13,"Fm":-20,"Fn":-20,"Fo":-37,"Fp":-20,"Fq":-37,"Fr":-20,"Fs":-27,"Fu":-20,"Fy":-25,"Fz":-34,"Fà":-44,"Fá":-44,"Fä":-44,"Fè":-37,"Fé":-37,"Fö":-37,"Fü":-20,"F…":-122,"G\"":-13,"G'":-13,"GK":59,"GT":-36,"GV":-53,"GW":-45,"GX":-11,"GY":-70,"Gj":62,"G‘":-13,"G’":-13,"G“":-13,"G”":-13,"J,":-20,"J.":-20,"J/":-19,"JA":-39,"JB":12,"J…":-20,"K\"":-15,"K&":-58,"K'":-15,"K-":-133,"K?":-63,"KC":-84,"KG":-84,"KJ":-34,"KO":-84,"KQ":-84,"KS":-39,"KU":-11,"Ka":-22,"Kc":-63,"Kd":-63,"Ke":-63,"Kf":-49,"Kg":-31,"Ko":-63,"Kq":-63,"Kt":-42,"Ku":-29,"Kv":-99,"Kw":-99,"Ky":-49,"Kà":-22,"Ká":-22,"Kä":-22,"Kè":-63,"Ké":-63,"Kö":-63,"Kü":-29,"K–":-133,"K—":-133,"K‘":-15,"K’":-15,"K“":-15,"K”":-15,"L\"":-88,"L'":-88,"L-":-101,"L?":-131,"LC":-39,"LG":-39,"LO":-39,"LQ":-39,"LT":-182,"LU":-27,"LV":-162,"LW":-135,"LY":-182,"Lc":-26,"Ld":-26,"Le":-26,"Lg":-20,"Lo":-26,"Lq":-26,"Lt":-18,"Lu":-17,"Lv":-103,"Lw":-103,"Ly":-20,"Lè":-26,"Lé":-26,"Lö":-26,"Lü":-17,"L–":-101,"L—":-101,"L‘":-88,"L’":-88,"L“":-88,"L”":-88,"O,":-40,"O.":-40,"O/":-36,"OA":-72,"OT":-61,"OV":-69,"OW":-63,"OX":-104,"OY":-96,"OZ":-32,"Oa":-13,"Oj":10,"Ox":-15,"Oz":-14,"Oà":-13,"Oá":-13,"Oä":-13,"O…":-40,"P,":-120,"P-":-17,"P.":-120,"P/":-81,"PA":-114,"PJ":-99,"PV":-31,"PW":-28,"PX":-65,"PY":-55,"PZ":-22,"Pa":-18,"Pg":-19,"Ps":-10,"Pà":-18,"Pá":-18,"Pä":-18,"P–":-17,"P—":-17,"P…":-120,"Q,":-40,"Q.":-40,"Q/":-36,"QA":-72,"QT":-61,"QV":-69,"QW":-63,"QX":-104,"QY":-96,"QZ":-32,"Qa":-13,"Qj":10,"Qx":-15,"Qz":-14,"Qà":-13,"Qá":-13,"Qä":-13,"Q…":-40,"R-":-31,"RV":-31,"RW":-26,"RX":-13,"RY":-54,"Rj":70,"R–":-31,"R—":-31,"SA":-31,"ST":-31,"SV":-58,"SW":-47,"SX":-45,"SY":-73,"Sj":23,"Sv":-21,"Sw":-21,"Sx":-22,"T,":-84,"T-":-137,"T.":-84,"T/":-121,"TA":-173,"TC":-31,"TG":-31,"TJ":-171,"TO":-31,"TQ":-31,"TS":-21,"Ta":-77,"Tc":-104,"Td":-104,"Te":-104,"Tg":-78,"Tm":-52,"Tn":-52,"To":-104,"Tp":-52,"Tq":-104,"Tr":-52,"Ts":-89,"Tu":-53,"Tv":-55,"Tw":-55,"Tx":-39,"Ty":-50,"Tz":-31,"Tà":-77,"Tá":-77,"Tä":-77,"Tè":-104,"Té":-104,"Tö":-104,"Tü":-53,"T–":-137,"T—":-137,"T…":-84,"U,":-27,"U.":-27,"UA":-58,"UX":-14,"Ug":-10,"Uj":12,"U…":-27,"V&":-46,"V,":-118,"V-":-77,"V.":-118,"V/":-122,"V?":-30,"VA":-176,"VC":-62,"VG":-62,"VJ":-114,"VO":-62,"VQ":-62,"VS":-39,"Va":-88,"Vc":-79,"Vd":-79,"Ve":-79,"Vf":-37,"Vg":-100,"Vm":-57,"Vn":-57,"Vo":-79,"Vp":-57,"Vq":-79,"Vr":-57,"Vs":-85,"Vu":-57,"Vv":-32,"Vw":-32,"Vx":-49,"Vy":-54,"Vz":-57,"Và":-88,"Vá":-88,"Vä":-88,"Vè":-79,"Vé":-79,"Vö":-79,"Vü":-57,"V–":-77,"V—":-77,"V…":-118,"W&":-34,"W,":-87,"W-":-62,"W.":-87,"W/":-102,"W?":-28,"WA":-155,"WC":-67,"WG":-67,"WJ":-92,"WO":-67,"WQ":-67,"WS":-34,"Wa":-75,"Wc":-80,"Wd":-80,"We":-80,"Wf":-30,"Wg":-78,"Wm":-50,"Wn":-50,"Wo":-80,"Wp":-50,"Wq":-80,"Wr":-50,"Ws":-72,"Wu":-50,"Wv":-40,"Ww":-40,"Wx":-30,"Wy":-40,"Wz":-40,"Wà":-75,"Wá":-75,"Wä":-75,"Wè":-80,"Wé":-80,"Wö":-80,"Wü":-50,"W–":-62,"W—":-62,"W…":-87,"X&":-48,"X-":-105,"X?":-63,"XC":-81,"XG":-81,"XJ":-32,"XO":-81,"XQ":-81,"XS":-43,"XT":-10,"XU":-15,"Xa":-23,"Xc":-64,"Xd":-64,"Xe":-64,"Xo":-64,"Xq":-64,"Xs":-32,"Xt":-29,"Xu":-35,"Xv":-85,"Xw":-85,"Xy":-40,"Xà":-23,"Xá":-23,"Xä":-23,"Xè":-64,"Xé":-64,"Xö":-64,"Xü":-35,"X–":-105,"X—":-105,"Y&":-51,"Y,":-134,"Y-":-112,"Y.":-134,"Y/":-135,"Y?":-40,"YA":-151,"YC":-97,"YG":-97,"YJ":-179,"YO":-97,"YQ":-97,"YS":-44,"Ya":-123,"Yc":-140,"Yd":-140,"Ye":-140,"Yg":-122,"Ym":-86,"Yn":-86,"Yo":-140,"Yp":-86,"Yq":-140,"Yr":-86,"Ys":-109,"Yu":-66,"Yv":-64,"Yw":-64,"Yx":-64,"Yy":-59,"Yz":-57,"Yà":-123,"Yá":-123,"Yä":-123,"Yè":-140,"Yé":-140,"Yö":-140,"Yü":-66,"Y–":-112,"Y—":-112,"Y…":-134,"Z-":-80,"ZC":-32,"ZG":-32,"ZO":-32,"ZQ":-32,"ZZ":18,"Zc":-21,"Zd":-21,"Ze":-21,"Zo":-21,"Zq":-21,"Zè":-21,"Zé":-21,"Zö":-21,"Z–":-80,"Z—":-80,"[j":228,"a\"":-25,"a'":-25,"a?":-53,"af":-27,"aj":25,"av":-39,"aw":-39,"a‘":-25,"a’":-25,"a“":-25,"a”":-25,"b\"":-30,"b'":-30,"b,":-24,"b.":-24,"b/":-24,"b?":-56,"bf":-39,"bv":-34,"bw":-34,"bx":-74,"bz":-29,"b‘":-30,"b’":-30,"b“":-30,"b”":-30,"b…":-24,"c\"":-23,"c'":-23,"c,":-10,"c.":-10,"c?":-34,"cv":-31,"cw":-31,"cx":-42,"cz":-15,"c‘":-23,"c’":-23,"c“":-23,"c”":-23,"c…":-10,"e\"":-30,"e'":-30,"e,":-24,"e.":-24,"e/":-24,"e?":-56,"ef":-39,"ev":-34,"ew":-34,"ex":-74,"ez":-29,"e‘":-30,"e’":-30,"e“":-30,"e”":-30,"e…":-24,"f\"":15,"f'":15,"f,":-55,"f-":-61,"f.":-55,"f]":12,"fa":-24,"fc":-32,"fd":-32,"fe":-32,"fg":-28,"fj":12,"fo":-32,"fq":-32,"fs":-21,"f}":12,"fà":-24,"fá":-24,"fä":-24,"fè":-32,"fé":-32,"fö":-32,"f–":-61,"f—":-61,"f‘":15,"f’":15,"f“":15,"f”":15,"f…":-55,"g?":-20,"gj":221,"h\"":-25,"h'":-25,"h?":-53,"hf":-27,"hj":25,"hv":-39,"hw":-39,"h‘":-25,"h’":-25,"h“":-25,"h”":-25,"jj":209,"k&":-14,"k-":-89,"ka":-40,"kc":-52,"kd":-52,"ke":-52,"kg":-49,"kj":22,"ko":-52,"kq":-52,"ks":-39,"kà":-40,"ká":-40,"kä":-40,"kè":-52,"ké":-52,"kö":-52,"k–":-89,"k—":-89,"lj":58,"m\"":-25,"m'":-25,"m?":-53,"mf":-27,"mj":25,"mv":-39,"mw":-39,"m‘":-25,"m’":-25,"m“":-25,"m”":-25,"n\"":-25,"n'":-25,"n?":-53,"nf":-27,"nj":25,"nv":-39,"nw":-39,"n‘":-25,"n’":-25,"n“":-25,"n”":-25,"o\"":-30,"o'":-30,"o,":-24,"o.":-24,"o/":-24,"o?":-56,"of":-39,"ov":-34,"ow":-34,"ox":-74,"oz":-29,"o‘":-30,"o’":-30,"o“":-30,"o”":-30,"o…":-24,"p\"":-30,"p'":-30,"p,":-24,"p.":-24,"p/":-24,"p?":-56,"pf":-39,"pv":-34,"pw":-34,"px":-74,"pz":-29,"p‘":-30,"p’":-30,"p“":-30,"p”":-30,"p…":-24,"q,":55,"q.":55,"qf":22,"qg":83,"qj":330,"ql":77,"qm":75,"qn":75,"qp":75,"qr":75,"qy":77,"q…":55,"r,":-85,"r-":-32,"r.":-85,"r/":-68,"ra":-24,"rc":-30,"rd":-30,"re":-30,"rg":-27,"ro":-30,"rq":-30,"rs":-19,"rà":-24,"rá":-24,"rä":-24,"rè":-30,"ré":-30,"rö":-30,"r–":-32,"r—":-32,"r…":-85,"s\"":-31,"s'":-31,"s-":-11,"s?":-52,"sf":-19,"sv":-33,"sw":-33,"sx":-26,"s–":-11,"s—":-11,"s‘":-31,"s’":-31,"s“":-31,"s”":-31,"t,":-16,"t.":-16,"t/":-26,"t…":-16,"v,":-60,"v-":-35,"v.":-60,"v/":-83,"va":-40,"vc":-34,"vd":-34,"ve":-34,"vg":-39,"vo":-34,"vq":-34,"vs":-31,"và":-40,"vá":-40,"vä":-40,"vè":-34,"vé":-34,"vö":-34,"v–":-35,"v—":-35,"v…":-60,"w,":-60,"w-":-35,"w.":-60,"w/":-83,"wa":-40,"wc":-34,"wd":-34,"we":-34,"wg":-39,"wo":-34,"wq":-34,"ws":-31,"wà":-40,"wá":-40,"wä":-40,"wè":-34,"wé":-34,"wö":-34,"w–":-35,"w—":-35,"w…":-60,"x-":-84,"xa":-22,"xc":-72,"xd":-72,"xe":-72,"xg":-25,"xj":11,"xo":-72,"xq":-72,"xs":-45,"xt":-12,"xà":-22,"xá":-22,"xä":-22,"xè":-72,"xé":-72,"xö":-72,"x–":-84,"x—":-84,"yj":214,"zc":-20,"zd":-20,"ze":-20,"zo":-20,"zq":-20,"zè":-20,"zé":-20,"zö":-20,"{j":230,"à\"":-25,"à'":-25,"à?":-53,"àf":-27,"àj":25,"àv":-39,"àw":-39,"à‘":-25,"à’":-25,"à“":-25,"à”":-25,"á\"":-25,"á'":-25,"á?":-53,"áf":-27,"áj":25,"áv":-39,"áw":-39,"á‘":-25,"á’":-25,"á“":-25,"á”":-25,"ä\"":-25,"ä'":-25,"ä?":-53,"äf":-27,"äj":25,"äv":-39,"äw":-39,"ä‘":-25,"ä’":-25,"ä“":-25,"ä”":-25,"è\"":-30,"è'":-30,"è,":-24,"è.":-24,"è/":-24,"è?":-56,"èf":-39,"èv":-34,"èw":-34,"èx":-74,"èz":-29,"è‘":-30,"è’":-30,"è“":-30,"è”":-30,"è…":-24,"é\"":-30,"é'":-30,"é,":-24,"é.":-24,"é/":-24,"é?":-56,"éf":-39,"év":-34,"éw":-34,"éx":-74,"éz":-29,"é‘":-30,"é’":-30,"é“":-30,"é”":-30,"é…":-24,"ö\"":-30,"ö'":-30,"ö,":-24,"ö.":-24,"ö/":-24,"ö?":-56,"öf":-39,"öv":-34,"öw":-34,"öx":-74,"öz":-29,"ö‘":-30,"ö’":-30,"ö“":-30,"ö”":-30,"ö…":-24,"–,":-30,"–.":-30,"–/":-34,"–1":-94,"–2":-57,"–3":-64,"–7":-108,"–8":-15,"–9":-13,"–A":-73,"–S":-31,"–T":-137,"–V":-83,"–W":-62,"–X":-105,"–Y":-112,"–Z":-58,"–f":-60,"–s":-14,"–v":-35,"–w":-35,"–x":-67,"–z":-47,"–…":-30,"—,":-30,"—.":-30,"—/":-34,"—1":-94,"—2":-57,"—3":-64,"—7":-108,"—8":-15,"—9":-13,"—A":-73,"—S":-31,"—T":-137,"—V":-83,"—W":-62,"—X":-105,"—Y":-112,"—Z":-58,"—f":-60,"—s":-14,"—v":-35,"—w":-35,"—x":-67,"—z":-47,"—…":-30,"‘,":-40,"‘.":-40,"‘/":-60,"‘4":-38,"‘8":-16,"‘A":-90,"‘J":-113,"‘a":-23,"‘c":-40,"‘d":-40,"‘e":-40,"‘g":-34,"‘o":-40,"‘q":-40,"‘s":-19,"‘à":-23,"‘á":-23,"‘ä":-23,"‘è":-40,"‘é":-40,"‘ö":-40,"‘…":-40,"’,":-40,"’.":-40,"’/":-60,"’4":-38,"’8":-16,"’A":-90,"’J":-113,"’a":-23,"’c":-40,"’d":-40,"’e":-40,"’g":-34,"’o":-40,"’q":-40,"’s":-19,"’à":-23,"’á":-23,"’ä":-23,"’è":-40,"’é":-40,"’ö":-40,"’…":-40,"“,":-40,"“.":-40,"“/":-60,"“4":-38,"“8":-16,"“A":-90,"“J":-113,"“a":-23,"“c":-40,"“d":-40,"“e":-40,"“g":-34,"“o":-40,"“q":-40,"“s":-19,"“à":-23,"“á":-23,"“ä":-23,"“è":-40,"“é":-40,"“ö":-40,"“…":-40,"”,":-40,"”.":-40,"”/":-60,"”4":-38,"”8":-16,"”A":-90,"”J":-113,"”a":-23,"”c":-40,"”d":-40,"”e":-40,"”g":-34,"”o":-40,"”q":-40,"”s":-19,"”à":-23,"”á":-23,"”ä":-23,"”è":-40,"”é":-40,"”ö":-40,"”…":-40,"…\"":-40,"…'":-40,"…-":-34,"…0":-31,"…1":-123,"…3":-21,"…4":-21,"…5":-27,"…6":-27,"…7":-44,"…8":-22,"…9":-15,"…C":-33,"…G":-33,"…O":-33,"…Q":-33,"…S":-10,"…T":-147,"…U":-18,"…V":-111,"…W":-91,"…Y":-133,"…f":-50,"…g":-28,"…j":73,"…t":-23,"…u":-17,"…v":-60,"…w":-60,"…y":-23,"…ü":-17,"…–":-34,"…—":-34,"…‘":-40,"…’":-40,"…“":-40,"…”":-40};
  var cvIdx = null;
  // width in px of `s` set in Coolvetica (Regular or Italic) at `size` px, kerning included
  function cvWidth(s, size) {
    if (!cvIdx) { cvIdx = {}; for (var i = 0; i < CV_CHARS.length; i++) cvIdx[CV_CHARS[i]] = CV_ADV[i]; }
    var a = Array.from(String(s)), u = 0;
    for (var j = 0; j < a.length; j++) {
      u += cvIdx[a[j]] != null ? cvIdx[a[j]] : 560;
      if (j + 1 < a.length) u += CV_KERN[a[j] + a[j + 1]] || 0;
    }
    return u * (size || 1) / 1000;
  }
  // Lockup layout constants (px on the 1920 x 1080 canvas; kit choices tuned against ref 1, see KIT_type.md v03):
  // small = Coolvetica Regular words (ref 1 "to their" / "at Stanford," measure 60 px), key = the Coolvetica Italic keyword,
  // solo = a lockup without a keyword (one centred line, ref 3), gap = baseline -> next cap top between small and key
  // rows (ref 1: 5 px of 323 = 16.7 px), pitch = baseline-to-baseline of two small lines (em), wrap = a small row longer
  // than wrap x the keyword's width (or than the title-safe width) is set on 2+ balanced lines.
  var LK = { small: 60, key: 190, solo: 64, gap: 17, pitch: 1.12, wrap: 1.15, safeW: 1728, safeTop: 54, safeBottom: 1026, y: 540, maxWords: 7,
    asc: 0.672, base: 0.867, italicOver: 0.12 };
  // Starred words (spec "word*", "[key]*"): visible on their own frame at full opacity, blurred + slightly small, then
  // settle (6f expo.out). Every other lockup word: a hard cut on its frame, no animation (note 11).
  var POP3 = { frames: 6, blur: 20, scale: 0.92, ease: 'expo.out', lead: 0 };

  // "to their [PhDs]* at Stanford," -> tokens with roles. [ ] = the keyword (one per lockup, 1+ words); "*" after a word =
  // that word pops + blurs in; "]*" = every keyword word pops; "|" = a forced line break among the small words;
  // punctuation-only tokens ("—") join the word before them.
  function parseLockup(spec) {
    var s = String(spec).trim(), toks = [], role = 'lead', seenKey = false, inKey = false, keyStart = 0, br = false, m;
    var re = /\[|\]\*?|\||[^\s\[\]|]+/g;
    while ((m = re.exec(s))) {
      var t = m[0];
      if (t === '[') {
        if (seenKey) throw new Error('RCK.type.lockups: one [keyword] per lockup: "' + s + '"');
        inKey = seenKey = true; role = 'key'; keyStart = toks.length; br = false; continue;
      }
      if (t.charAt(0) === ']') {
        if (!inKey) throw new Error('RCK.type.lockups: "]" without "[" in "' + s + '"');
        inKey = false; role = 'tail'; br = false;
        if (t === ']*') for (var k = keyStart; k < toks.length; k++) toks[k].pop = true;
        continue;
      }
      if (t === '|') { br = true; continue; }
      var pop = t.length > 1 && t.charAt(t.length - 1) === '*';
      if (pop) t = t.slice(0, -1);
      if (!norm(t).length) { if (toks.length) { toks[toks.length - 1].text += ' ' + t; continue; } }
      toks.push({ text: t, role: role, pop: pop, br: br });
      br = false;
    }
    if (inKey) throw new Error('RCK.type.lockups: unclosed [ in "' + s + '"');
    if (!toks.length) throw new Error('RCK.type.lockups: empty lockup "' + s + '"');
    if (!seenKey) toks.forEach(function (tk) { tk.role = 'solo'; });
    return { spec: s, toks: toks, hasKey: seenKey };
  }
  function specList(specs) {
    if (Array.isArray(specs)) return specs.slice();
    return String(specs).split(/\s+\/\s+|\n+/).map(function (x) { return x.trim(); }).filter(Boolean);
  }
  // split tokens into lines no wider than maxW (forced "|" breaks first, then balanced: fewest lines, smallest widest line)
  function lockupLines(toks, size, maxW) {
    if (!toks.length) return [];
    var segs = [[]];
    toks.forEach(function (tk, i) { if (tk.br && i > 0) segs.push([]); segs[segs.length - 1].push(tk); });
    var out = [];
    segs.forEach(function (seg) {
      var wOf = function (a, b) { return cvWidth(seg.slice(a, b).map(function (t) { return t.text; }).join(' '), size); };
      if (wOf(0, seg.length) <= maxW || seg.length === 1) { out.push(seg); return; }
      for (var n = 2; n <= seg.length; n++) {
        var best = null;
        (function rec(start, left, cuts) {
          if (left === 1) {
            var parts = cuts.concat([[start, seg.length]]), worst = 0;
            parts.forEach(function (p) { worst = Math.max(worst, wOf(p[0], p[1])); });
            if (!best || worst < best.worst) best = { worst: worst, parts: parts };
            return;
          }
          for (var e = start + 1; e <= seg.length - left + 1; e++) rec(e, left - 1, cuts.concat([[start, e]]));
        })(0, n, []);
        if (best.worst <= maxW || n === seg.length) { best.parts.forEach(function (p) { out.push(seg.slice(p[0], p[1])); }); return; }
      }
    });
    return out;
  }
  // Rows + vertical geometry of one lockup. Every row has line-height = its font size, so its baseline sits 0.867 em and
  // its cap / ascender top 0.195 em below the row top (Coolvetica hhea metrics, KIT_type.md v02 > Fonts). Gaps are set
  // from baseline to the next row's cap top. The ink block (first cap top .. last baseline) is centred on --rc-y.
  function layoutLockup(lk, opts, warnings) {
    var S = opts.smallSize || LK.small, K = opts.keySize || LK.key, SOLO = opts.soloSize || LK.solo;
    var safeW = opts.maxWidth || LK.safeW, gap = opts.gap != null ? opts.gap : LK.gap, pitch = opts.pitch || LK.pitch;
    var by = function (r) { return lk.toks.filter(function (t) { return t.role === r; }); };
    var txt = function (ts) { return ts.map(function (t) { return t.text; }).join(' '); };
    var rows = [];
    if (!lk.hasKey) {
      lockupLines(by('solo'), SOLO, Math.min(safeW, opts.soloMax || 1400)).forEach(function (ts) { rows.push({ kind: 'solo', toks: ts, size: SOLO }); });
    } else {
      var key = by('key'), keyW = cvWidth(txt(key), K) + LK.italicOver * K;
      if (keyW > safeW) {
        var K2 = Math.floor(K * safeW / keyW);
        warnings.push('lockup "' + lk.spec + '": keyword "' + txt(key) + '" shrunk ' + K + ' -> ' + K2 + ' px to stay inside title-safe');
        K = K2; keyW = cvWidth(txt(key), K) + LK.italicOver * K;
      }
      var maxSmall = Math.min(safeW, Math.max(keyW * (opts.wrap || LK.wrap), 420));
      lockupLines(by('lead'), S, maxSmall).forEach(function (ts) { rows.push({ kind: 'lead', toks: ts, size: S }); });
      rows.push({ kind: 'key', toks: key, size: K });
      lockupLines(by('tail'), S, maxSmall).forEach(function (ts) { rows.push({ kind: 'tail', toks: ts, size: S }); });
    }
    var y = 0, prevBase = null, prevKind = null, width = 0;
    rows.forEach(function (r) {
      var capTop = prevBase == null ? LK.asc * 0 : (r.kind === prevKind || (r.kind !== 'key' && prevKind !== 'key') ? prevBase + pitch * r.size - LK.asc * r.size : prevBase + gap);
      r.top = prevBase == null ? 0 : capTop - (LK.base - LK.asc) * r.size;
      r.base = r.top + LK.base * r.size;
      r.width = cvWidth(txt(r.toks), r.size) + (r.kind === 'key' ? LK.italicOver * r.size : 0);
      width = Math.max(width, r.width);
      prevBase = r.base; prevKind = r.kind;
    });
    var inkTop = rows[0].top + (LK.base - LK.asc) * rows[0].size, inkBottom = rows[rows.length - 1].base;
    var box = { width: width, inkTop: inkTop, inkBottom: inkBottom, centre: (inkTop + inkBottom) / 2, height: rows[rows.length - 1].top + rows[rows.length - 1].size };
    var yC = opts.y != null ? opts.y : LK.y;
    if (yC - (box.centre - inkTop) < LK.safeTop || yC + (inkBottom - box.centre) > LK.safeBottom)
      warnings.push('lockup "' + lk.spec + '": ink y ' + Math.round(yC - box.centre + inkTop) + '-' + Math.round(yC - box.centre + inkBottom) + ' leaves title-safe 54-1026');
    if (width > safeW) warnings.push('lockup "' + lk.spec + '": ' + Math.round(width) + ' px wide (title-safe ' + safeW + ')');
    return { rows: rows, box: box, sizes: { small: S, key: K, solo: SOLO } };
  }
  // v03 caption plan: words = words.json `words` (or seconds), specs = an array of lockup specs (or one string with " / "
  // between lockups). opts: from (index of the first word), end (s; where the last lockup hard-cuts out; default the next
  // word's comp_t, else the last word's comp_end_t), start (s; an earlier start for the first lockup's clip), loose
  // (accept spelling differences, e.g. "18" for "eighteen"), y (ink centre, default 540), smallSize (60), keySize (190),
  // soloSize (64), gap (17), wrap (1.15), maxWidth (1728). Returns {lockups, next, endFrame, warnings}; each lockup
  // {index, spec, text, toks: [{text, role lead|key|tail|solo, pop, frame, i, voiceT}], startFrame, endFrame, frames,
  // startAttr, durAttr, layout: {rows, box, sizes}}.
  function lockupPlan(words, specs, opts) {
    opts = opts || {};
    var list = specList(specs), wi = opts.from || 0, warnings = [];
    var lks = list.map(function (spec) {
      var p = parseLockup(spec);
      p.toks.forEach(function (tk, k) {
        var w = words[wi];
        if (w == null) throw new Error('RCK.type.lockups: ran out of words at "' + tk.text + '" in "' + p.spec + '"');
        if (!opts.loose && w.text != null && norm(w.text) !== norm(tk.text))
          throw new Error('RCK.type.lockups: "' + p.spec + '" word ' + (k + 1) + ' "' + tk.text + '" != words[' + wi + '] "' + w.text + '" (pass opts.loose to accept)');
        var t = wordTime(w);
        tk.i = wi; tk.voiceT = t; tk.frame = frame(t); wi++;
      });
      return p;
    });
    var nextW = words[wi], lastW = words[wi - 1];
    var endT = opts.end != null ? opts.end : (nextW != null ? wordTime(nextW) : (lastW.comp_end_t != null ? lastW.comp_end_t : wordTime(lastW) + 0.5));
    var endFrame = frame(endT);
    lks.forEach(function (lk, i) {
      lk.index = i;
      lk.text = lk.toks.map(function (t) { return t.text; }).join(' ');
      lk.startFrame = lk.toks[0].frame;
      if (i === 0 && opts.start != null) lk.startFrame = Math.min(lk.startFrame, frame(opts.start));
      lk.endFrame = i + 1 < lks.length ? lks[i + 1].toks[0].frame : endFrame;
      lk.frames = lk.endFrame - lk.startFrame;
      if (lk.frames < 1) throw new Error('RCK.type.lockups: lockup "' + lk.spec + '" has no frames (the next lockup starts on its first frame)');
      var lastF = lk.toks[lk.toks.length - 1].frame;
      if (lastF >= lk.endFrame) throw new Error('RCK.type.lockups: "' + lk.toks[lk.toks.length - 1].text + '" (f' + lastF + ') starts after its lockup ends (f' + lk.endFrame + ')');
      if (lk.toks.length > LK.maxWords) warnings.push('lockup "' + lk.spec + '" has ' + lk.toks.length + ' words (guideline 1-' + LK.maxWords + ')');
      if (lk.frames < 6) warnings.push('lockup "' + lk.spec + '" is on screen only ' + lk.frames + 'f');
      lk.start = lk.startFrame / FPS; lk.end = lk.endFrame / FPS;
      lk.startAttr = attrF(lk.startFrame); lk.durAttr = durF(lk.startFrame, lk.endFrame);
      lk.layout = layoutLockup(lk, opts, warnings);
    });
    return { lockups: lks, next: wi, endFrame: endFrame, warnings: warnings };
  }
  // "1 f31-100 (69f) [lead] Open@31 | [key] GTA@39* Online@45* | [tail] and@57 buy@63 / an@69 arcade.@75 | key 190 px, 1012 x 309"
  function lockupReport(plan) {
    return plan.lockups.map(function (lk) {
      var L = lk.layout;
      return (lk.index + 1) + ' f' + lk.startFrame + '-' + lk.endFrame + ' (' + lk.frames + 'f)  ' + L.rows.map(function (r) {
        return '[' + r.kind + '] ' + r.toks.map(function (t) { return t.text + '@' + t.frame + (t.pop ? '*' : ''); }).join(' ');
      }).join(' | ') + '  | ' + (L.rows.some(function (r) { return r.kind === 'key'; }) ? 'key ' + L.sizes.key + ' px, ' : '') +
        Math.round(L.box.width) + ' x ' + Math.round(L.box.inkBottom - L.box.inkTop) + ' px ink';
    }).join('\n') + (plan.warnings.length ? '\nwarnings: ' + plan.warnings.join('; ') : '');
  }
  function r2(v) { return Math.round(v * 100) / 100; }
  // v03 HTML to paste: one timed element per lockup (class "clip rc-lk"), rows inside a centred box. opts: everything
  // lockupPlan takes (words, specs, opts are passed through), plus idPrefix ('lk'), z, track, y (px: the ink centre,
  // default 540), cls (extra classes, e.g. 'rc-lk--card'), inline (extra inline CSS). Pass a plan instead of words to
  // reuse one: lockups(plan, null, opts).
  function lockups(words, specs, opts) {
    opts = opts || {};
    var plan = words && words.lockups ? words : lockupPlan(words, specs, opts);
    var prefix = opts.idPrefix || 'lk', track = opts.track != null ? ' data-track-index="' + opts.track + '"' : '';
    return plan.lockups.map(function (lk) {
      var L = lk.layout, css = [opts.y != null ? '--rc-y: ' + opts.y + 'px' : '', '--rc-lk-c: ' + r2(L.box.centre) + 'px', opts.z != null ? 'z-index: ' + opts.z : '', opts.inline || ''].filter(Boolean).join('; ');
      var prevEnd = 0;
      var rows = L.rows.map(function (r) {
        var mt = r2(r.top - prevEnd); prevEnd = r.top + r.size;
        return '<div class="rc-lk__row rc-lk__row--' + r.kind + '" style="font-size: ' + r.size + 'px; line-height: ' + r.size + 'px; height: ' + r.size + 'px' + (mt ? '; margin-top: ' + mt + 'px' : '') + '">' +
          r.toks.map(function (t) { return '<span class="rc-lw' + (t.pop ? ' rc-lw--pop' : '') + '" data-rc-f="' + t.frame + '">' + esc(t.text) + '</span>'; }).join(' ') + '</div>';
      }).join('');
      return '<div id="' + prefix + '-' + (lk.index + 1) + '" class="clip rc-lk' + (opts.cls ? ' ' + opts.cls : '') + '" data-start="' + lk.startAttr + '" data-duration="' + lk.durAttr + '"' + track +
        ' style="' + css + '"><div class="rc-lk__box">' + rows + '</div></div>';
    }).join('\n');
  }
  // pop + blur-in of one word on frame k (POP3): full opacity on its own frame, blur 20 px -> 0 and scale 0.92 -> 1 over 6f
  // (expo.out). opts.lead > 0 starts the settle earlier (the word still appears on frame k).
  function popBlur(tl, w, k, p) {
    var g = G(), k0 = Math.max(0, k - (p.lead || 0));
    g.set(w, { opacity: 0, scale: p.scale, filter: 'blur(' + p.blur + 'px)', transformOrigin: '50% 60%' });
    hard(tl, w, { opacity: 0 }, { opacity: 1 }, k / FPS);
    tl.fromTo(w, { scale: p.scale, filter: 'blur(' + p.blur + 'px)' }, { scale: 1, filter: 'blur(0px)', duration: p.frames * F, ease: easeOf(p.ease, 'expo.out'), immediateRender: false }, k0 / FPS);
    return (k0 + p.frames) / FPS;
  }
  // Wires every lockup (default: all .rc-lk; scope = selector / element(s)): plain words hard-cut on their data-rc-f frame,
  // .rc-lw--pop words pop + blur in (opts.pop overrides POP3 fields). The lockup itself appears / disappears with its clip
  // window (hard cuts). Call once after the lockup markup; later calls skip processed lockups. Returns the time the last
  // word has landed.
  function lockupsWire(tl, scope, opts) {
    opts = opts || {};
    var roots = scope == null ? list('.rc-lk') : list(scope), end = 0, p = Object.assign({}, POP3, opts.pop);
    roots.forEach(function (root) {
      if (root.__rckLk) return;
      root.__rckLk = true;
      var ws = $$('.rc-lw[data-rc-f]', root);
      if (!ws.length && window.console) console.warn('RCK.type.lockupsWire: no .rc-lw[data-rc-f] words in ' + (root.id || root.className));
      ws.forEach(function (w) {
        var k = parseInt(w.getAttribute('data-rc-f'), 10);
        if (w.classList.contains('rc-lw--pop')) end = Math.max(end, popBlur(tl, w, k, p));
        else { G().set(w, { opacity: 0 }); hard(tl, w, { opacity: 0 }, { opacity: 1 }, k / FPS); end = Math.max(end, k / FPS); }
      });
    });
    return end;
  }
  // Word-by-word pop + blur-in on any text (v03 B6 quote: "the quote words pop + blur in on their spoken frames").
  // target: the element holding the words (e.g. '#b06-t8 .rc-t8__quote'). words: one time per word (seconds or words.json
  // entries, spell-checked unless opts.loose; opts.from = index of the first) -> the text is split into .rc-lw spans
  // (child elements such as <br> are kept); or null when the words are already spans with data-rc-f (v02 markup).
  // opts.hard: true = plain hard cuts instead of the pop; opts.pop overrides POP3. Returns the time the last word lands.
  function wordPops(tl, target, words, opts) {
    opts = opts || {};
    var root = $(target), spansIn = $$('[data-rc-f]', root), p = Object.assign({}, POP3, opts.pop), end = 0;
    if (words != null) {
      if (!root.__rckSplit) {
        var texts = [];
        (function walk(n) { Array.prototype.slice.call(n.childNodes).forEach(function (c) { if (c.nodeType === 3) texts.push(c); else if (c.nodeType === 1) walk(c); }); })(root);
        texts.forEach(function (tn) {
          var frag = document.createDocumentFragment();
          tn.nodeValue.split(/(\s+)/).forEach(function (pt) { if (!pt) return; frag.appendChild(/^\s+$/.test(pt) ? document.createTextNode(pt) : mk('span', 'rc-lw', pt)); });
          tn.parentNode.replaceChild(frag, tn);
        });
        root.__rckSplit = true;
      }
      var wi = opts.from || 0, prevF = null;
      spansIn = $$('.rc-lw', root);
      spansIn.forEach(function (sp) {
        if (!norm(sp.textContent).length && prevF != null) { sp.setAttribute('data-rc-f', prevF); return; }
        var w = words[wi];
        if (w == null) throw new Error('RCK.type.wordPops: ran out of word times at "' + sp.textContent + '"');
        if (!opts.loose && w.text != null && norm(w.text) !== norm(sp.textContent))
          throw new Error('RCK.type.wordPops: "' + sp.textContent + '" != words[' + wi + '] "' + w.text + '" (pass opts.loose to accept)');
        prevF = frame(wordTime(w)); sp.setAttribute('data-rc-f', prevF); wi++;
      });
    }
    spansIn.forEach(function (sp) {
      if (sp.__rckPop) return;
      sp.__rckPop = true;
      if (getComputedStyle(sp).display === 'inline') sp.style.display = 'inline-block';
      var k = parseInt(sp.getAttribute('data-rc-f'), 10);
      if (opts.hard) { G().set(sp, { opacity: 0 }); hard(tl, sp, { opacity: 0 }, { opacity: 1 }, k / FPS); end = Math.max(end, k / FPS); }
      else end = Math.max(end, popBlur(tl, sp, k, p));
    });
    return end;
  }

  RCK.type = {
    FPS: FPS,
    // Coolvetica metrics (em; hhea line metrics as Chrome uses them, glyph heights measured): for placement maths
    METRICS: { ascent: 0.967, descent: 0.233, cap: 0.672, digit: 0.688, xHeight: 0.5, italicAngle: -10, underline: 0.133, underlineThickness: 0.02 },
    // frame grid + attributes
    frame: frame, snap: snap, attr: attr, attrF: attrF, dur: dur, durF: durF,
    // easing (also RCK.ease)
    ease: easeOf, gsapEase: gsapEase,
    // T1 captions v01 (kept) and v02
    checkChunks: checkChunks, captionPlan: captionPlan, captionHTML: captionHTML,
    captionPlanV2: captionPlanV2, captionHTMLV2: captionHTMLV2, captionReport: captionReport, groupWords: groupWords, cutCost: cutCost,
    captionPops: captionPops, wordsV2: wordsV2, punchPairV2: punchPairV2, spreadWordsV2: spreadWordsV2, glowLineV2: glowLineV2, POP: POP,
    // T2-T10 animation helpers: (tl, target, atSeconds, opts) -> endSeconds
    punchPair: punchPair,
    yearCard: yearCard,
    spreadIn: spreadIn, spreadOut: spreadOut, spreadWords: spreadWords,
    glowLine: glowLine,
    giantType: giantType, typeOnOffsets: typeOnOffsets,
    chipPop: chipPop, chipSentence: chipSentence,
    nameIn: nameIn, quoteType: quoteType, walk: walk,
    highlight: highlight, label: label,
    glitch: glitch,
    // v03 caption lockups (notes 11, 16, 17) + word pops (B6 quote)
    lockupPlan: lockupPlan, lockups: lockups, lockupsWire: lockupsWire, lockupReport: lockupReport, parseLockup: parseLockup,
    wordPops: wordPops, cvWidth: cvWidth, LK: LK, POP3: POP3
  };
})();
