// Run from _demo-v02:  node tools/measure_v02.cjs  -> review/measure_v02.json (+ a summary on stdout)
// Loads index.html in the HyperFrames 0.9.52 headless shell (GSAP from the CLI's vendored copy), builds the paused
// timeline, then measures:
//  1. ease audit: every tween on the demo timeline AND on an audit timeline that calls every kit helper once:
//     linear eases are reported (hard cuts = <= 0.5f step tweens / sets are counted separately);
//  2. curve check: each eased numeric tween is seeked to 25 / 50 / 75 % and the rendered value's progress is compared
//     with the easings.net reference curve of its ease (RCK.ease.fn) and with a straight line;
//  3. rule A: every frame, the caption words visible (clip window as the runtime's [start, start+duration), effective
//     opacity > 0.05) are counted (max 2) and each word's first visible frame is compared with its data-rc-f;
//  4. Coolvetica layout: T1 / T2 / T3 / T6 / T8 / T9 / T10 positions, fonts really used, no synthetic bold / italic.
const NM = '/root/.npm/_npx/56d07fea2d9f6f1f/node_modules';
const puppeteer = require(NM + '/puppeteer-core');
const fs = require('fs');
const path = require('path');
const CHROME = '/root/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/chrome-headless-shell-linux64/chrome-headless-shell';
const GSAP = NM + '/hyperframes/dist/vendor/npm/gsap@3.15.0/dist/gsap.min.js';
const DIR = path.resolve(__dirname, '..');

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--allow-file-access-from-files', '--no-sandbox', '--force-device-scale-factor=1'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setRequestInterception(true);
  page.on('request', r => { if (r.url().includes('gsap')) r.respond({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(GSAP, 'utf8') }); else r.continue(); });
  const warnings = [];
  page.on('pageerror', e => warnings.push('PAGEERROR ' + e.message));
  page.on('console', m => { if (m.type() === 'warning' || m.type() === 'error') warnings.push(m.type() + ': ' + m.text()); });
  await page.goto('file://' + DIR + '/index.html', { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);

  const out = await page.evaluate(() => {
    const R = {}, FPS = 30, tl = window.__timelines['kit-v02-demo'];
    const END = Math.round(tl.duration() * FPS);
    const at = f => tl.totalTime(f / FPS + 1e-6, false);
    const q = s => document.querySelector(s), qa = (s, r) => [...(r || document).querySelectorAll(s)];
    const box = e => { const r = e.getBoundingClientRect(); return { x: +r.left.toFixed(2), y: +r.top.toFixed(2), w: +r.width.toFixed(2), h: +r.height.toFixed(2), r: +r.right.toFixed(2), b: +r.bottom.toFixed(2) }; };
    const baseline = e => { const s = document.createElement('span'); s.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline'; e.appendChild(s); const y = s.getBoundingClientRect().top; s.remove(); return +y.toFixed(2); };
    const fontOf = e => { const c = getComputedStyle(e); return { family: c.fontFamily, style: c.fontStyle, weight: c.fontWeight, size: c.fontSize, synthesis: c.fontSynthesis }; };

    /* ---------- 1 + 2: ease audit and curve check ---------- */
    const lin = f => Math.abs(f(0.25) - 0.25) < 1e-3 && Math.abs(f(0.5) - 0.5) < 1e-3 && Math.abs(f(0.75) - 0.75) < 1e-3;
    const audit = (timeline, label, sampleCurves) => {
      const res = { label, tweens: 0, cuts: 0, sets: 0, eased: 0, linear: [], byEase: {}, curve: { checked: 0, maxErr: 0, worst: null, minDistLinear: 1, flat: [] } };
      timeline.getChildren(true, true, false).forEach(tw => {
        res.tweens++;
        const d = tw.duration();
        if (d === 0) { res.sets++; return; }
        const ev = tw.vars.ease, name = typeof ev === 'function' ? 'function' : String(ev == null ? 'default(power1.out)' : ev);
        const E = gsap.parseEase(ev == null ? 'power1.out' : ev);
        if (/^steps/.test(name) && d <= 0.5 / FPS + 1e-6) { res.cuts++; return; }
        if (/^steps/.test(name)) { res.byEase[name] = (res.byEase[name] || 0) + 1; res.cuts++; return; }
        res.byEase[name] = (res.byEase[name] || 0) + 1;
        if (lin(E)) { res.linear.push({ ease: name, start: +(tw.startTime() * FPS).toFixed(2), frames: +(d * FPS).toFixed(2), targets: tw.targets().map(t => t.id || t.className || t.tagName).join(','), props: Object.keys(tw.vars).filter(k => !/^(duration|ease|immediateRender|force3D|onUpdate)$/.test(k)).join(',') }); return; }
        res.eased++;
        if (!sampleCurves) return;
        // curve check on simple numeric props (fromTo tweens: vars.startAt holds the from values)
        const from = tw.vars.startAt || {}, tgt = tw.targets()[0];
        Object.keys(tw.vars).forEach(k => {
          if (/^(duration|ease|immediateRender|force3D|onUpdate|startAt|attr|transformOrigin|stagger|delay)$/.test(k)) return;
          const v1 = parseFloat(tw.vars[k]), v0 = parseFloat(from[k]);
          if (!isFinite(v0) || !isFinite(v1) || Math.abs(v1 - v0) < 1e-6 || !(tgt instanceof Element)) return;
          const t0 = tw.startTime();   // local to the root timeline (its own startTime is on GSAP's global clock: not added)
          const ps = [0.25, 0.5, 0.75], obs = [];
          for (const p of ps) {
            tl === timeline ? tl.totalTime(t0 + p * d, false) : timeline.totalTime(t0 + p * d, false);
            let v = gsap.getProperty(tgt, k);
            if (k === 'filter') return;
            v = parseFloat(v);
            obs.push((v - v0) / (v1 - v0));
          }
          if (obs.length < 3) return;
          let err = 0, distLin = 0;
          ps.forEach((p, i) => { err = Math.max(err, Math.abs(obs[i] - E(p))); distLin = Math.max(distLin, Math.abs(obs[i] - p)); });
          const refF = typeof ev === 'string' ? RCK.ease.fn(ev) : null;
          if (refF) { res.curve.vsEasingsNet = res.curve.vsEasingsNet || { checked: 0, maxErr: 0, byEase: {} }; const en = RCK.ease.name(ev);
            ps.forEach((p, i) => { const e2 = Math.abs(obs[i] - refF(p)); res.curve.vsEasingsNet.maxErr = Math.max(res.curve.vsEasingsNet.maxErr, +e2.toFixed(5)); res.curve.vsEasingsNet.byEase[en] = Math.max(res.curve.vsEasingsNet.byEase[en] || 0, +e2.toFixed(5)); });
            res.curve.vsEasingsNet.checked++; }
          res.curve.checked++;
          if (err > 0.01) (res.curve.bad = res.curve.bad || []).push({ ease: name, prop: k, target: tgt.id || tgt.className, start: +(t0 * FPS).toFixed(3), frames: +(d * FPS).toFixed(2), v0, v1, obs: obs.map(o => +o.toFixed(4)) });
          if (err > res.curve.maxErr) { res.curve.maxErr = +err.toFixed(5); res.curve.worst = { ease: name, prop: k, target: tgt.id || tgt.className, start: +(t0 * FPS).toFixed(2), obs: obs.map(o => +o.toFixed(4)), curve: ps.map(p => +E(p).toFixed(4)) }; }
          res.curve.minDistLinear = Math.min(res.curve.minDistLinear, distLin);
          if (distLin < 0.02) res.curve.flat.push({ ease: name, prop: k, target: tgt.id || tgt.className, obs });
        });
      });
      res.curve.minDistLinear = +res.curve.minDistLinear.toFixed(4);
      return res;
    };
    R.easeDemo = audit(tl, 'demo timeline', true);

    // reference curves: the named kit eases against easings.net formulas (RCK.ease.fn) at 25/50/75%
    R.easeRef = {};
    ['expo.out', 'expo.in', 'sine.inOut', 'power1.in', 'power1.out', 'power1.inOut', 'power2.in', 'power2.out', 'power2.inOut', 'power3.in', 'power3.out', 'back.out(1.70158)'].forEach(n => {
      const g = gsap.parseEase(n), ref = RCK.ease.fn(n);
      R.easeRef[n] = { easings: RCK.ease.name(n), gsap: [0.25, 0.5, 0.75].map(p => +g(p).toFixed(4)), easingsNet: [0.25, 0.5, 0.75].map(p => +ref(p).toFixed(4)) };
    });

    /* ---------- 3: rule A per frame ---------- */
    const timed = [...document.querySelectorAll('[data-start]')].filter(e => !e.hasAttribute('data-composition-id'));
    const win = new Map(timed.map(e => [e, [Math.round(+e.dataset.start * FPS + 0.49), +e.dataset.start + +e.dataset.duration]]));
    const visibleAt = (el, f) => {
      const t = f / FPS;
      for (let e = el; e && e.id !== 'root'; e = e.parentElement) {
        if (win.has(e)) { const s = +e.dataset.start, d = +e.dataset.duration; if (!(t >= s - 1e-9 && t < s + d - 1e-9)) return false; }
      }
      return true;
    };
    const effOpacity = el => { let o = 1; for (let e = el; e && e.id !== 'root'; e = e.parentElement) { const c = getComputedStyle(e); if (c.display === 'none' || c.visibility === 'hidden') return 0; o *= +c.opacity; } return o; };
    const words = qa('.rc-w[data-rc-f]').filter(w => !w.closest('.rc-t5__glow'));
    const first = new Map(), maxOn = { n: 0, f: -1, words: [] }, over2 = [];
    for (let f = 0; f <= END; f++) {
      at(f);
      const on = words.filter(w => visibleAt(w, f) && effOpacity(w) > 0.05);
      if (on.length > maxOn.n) { maxOn.n = on.length; maxOn.f = f; maxOn.words = on.map(w => w.textContent); }
      if (on.length > 2) over2.push({ f, words: on.map(w => w.textContent) });
      words.forEach(w => { if (!first.has(w) && visibleAt(w, f) && effOpacity(w) > 0.3) first.set(w, f); });
    }
    const onset = words.map(w => ({ word: w.textContent, onset: +w.dataset.rcF, firstVisible: first.has(w) ? first.get(w) : null }));
    R.ruleA = { words: words.length, maxOnScreen: maxOn, framesOver2: over2.length, over2: over2.slice(0, 10),
      onsetMismatch: onset.filter(o => o.firstVisible == null || Math.abs(o.firstVisible - o.onset) > 1), onsetExactly: onset.filter(o => o.firstVisible === o.onset).length, onsets: onset };
    // pop curve of one word (B1 "does", onset 15) and the T2 keyword ("cops?")
    const wDoes = words.find(w => w.textContent === 'does'), wCops = words.find(w => w.textContent === 'cops?');
    const tr = e => { const m = new DOMMatrix(getComputedStyle(e).transform); return { s: +Math.hypot(m.a, m.b).toFixed(4), y: +m.f.toFixed(2) }; };
    R.popDoes = [13, 14, 15, 16, 17, 18, 19].map(f => { at(f); return { f, opacity: +(+getComputedStyle(wDoes).opacity).toFixed(4), ...tr(wDoes) }; });
    R.popCops = [124, 125, 126, 127, 128, 131].map(f => { at(f); return { f, opacity: +(+getComputedStyle(wCops).opacity).toFixed(4), filter: getComputedStyle(wCops).filter, ...tr(wCops) }; });

    /* ---------- camera values per frame ---------- */
    const sc = s => { const m = new DOMMatrix(getComputedStyle(q(s)).transform); return +Math.hypot(m.a, m.b).toFixed(4); };
    R.camera = {
      zoomOut_a: [0, 10, 20, 30, 39].map(f => { at(f); return [f, sc('#a-cam')]; }),
      punchIn_a: [40, 41, 42, 43, 45, 50].map(f => { at(f); return [f, sc('#a-cam')]; }),
      push_a: [50, 75, 100, 125, 149].map(f => { at(f); return [f, sc('#a-cam')]; }),
      keyPunch_cops: [123, 124, 125, 126, 127, 130, 133, 136].map(f => { at(f); return [f, sc('#a-key')]; }),
      zoomThroughOut: [285, 286, 287, 288, 289, 290, 291].map(f => { at(f); return [f, sc('#c-cam'), getComputedStyle(q('#c-v')).getPropertyValue('--hf-color-grading-blur').trim()]; }),
      zoomThroughIn: [292, 293, 294, 295, 296, 298, 301].map(f => { at(f); return [f, sc('#c-card-cam'), getComputedStyle(q('#c-card-cam')).filter]; }),
      calendarIn: [428, 429, 430, 431, 434, 440].map(f => { at(f); const b = q('#d2-cal .m3-body'), m = new DOMMatrix(getComputedStyle(b).transform); return [f, +Math.hypot(m.a, m.b).toFixed(4), +m.f.toFixed(2), +(+getComputedStyle(b).opacity).toFixed(3)]; })
    };
    R.x3 = [1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045].map(f => { at(f); return [f, +(+getComputedStyle(q('#j-x3')).opacity).toFixed(4)]; });
    R.x5 = [1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1068, 1070, 1072].map(f => { at(f); const s = q('#j-x5 .rc-x5__slat'), m = new DOMMatrix(getComputedStyle(s).transform); const ang = Math.atan2(-m.m13, m.m11) * 180 / Math.PI; return [f, +ang.toFixed(2), +Math.abs(Math.cos(ang * Math.PI / 180)).toFixed(3)]; });
    R.typeOnT6 = (() => { const chars = qa('#g-t6 .rc-t6__ch').filter(c => /\S/.test(c.textContent)), firstF = []; for (let f = 766; f <= 800; f++) { at(f); chars.forEach((c, i) => { if (firstF[i] == null && +getComputedStyle(c).opacity > 0.5) firstF[i] = f - 770; }); } return firstF; })();
    R.typeOnQuote = (() => { const chars = qa('#h-t8 .rc-t8__ch'), firstF = []; for (let f = 866; f <= 880; f++) { at(f); chars.forEach((c, i) => { if (firstF[i] == null && +getComputedStyle(c).opacity > 0.5) firstF[i] = f - 868; }); } return firstF; })();
    R.counter = (() => { const strips = qa('#d2-cal .m3-strip'), o = []; for (let f = 470; f <= 498; f++) { at(f); o.push([f, strips.map(s => +new DOMMatrix(getComputedStyle(s).transform).f.toFixed(1)).join('/')]); } return o; })();

    /* ---------- 4: Coolvetica layout ---------- */
    const L = {};
    at(20); { const c = q('#a-cap-1'), b = baseline(c.querySelector('.rc-g')); L.T1 = { font: fontOf(c.querySelector('.rc-w')), baseline: b, capCentre: +(b - 0.672 * 46 / 2).toFixed(2), wantCapCentre: 620 }; }
    at(118); { const r = q('#a-t2-1 .rc-t2__row'), lead = r.querySelector('.rc-t2__lead'); L.T2leadOnly = { leadBaseline: baseline(lead), font: fontOf(lead.querySelector('.rc-w')) }; }
    at(140); { const r = q('#a-t2-2 .rc-t2__row'), lead = r.querySelector('.rc-t2__lead'), key = r.querySelector('.rc-t2__key'), lb = box(lead), kb = box(key);
      L.T2pair = { leadBaseline: baseline(lead), keyBaseline: baseline(key), keyCapCentre: +(baseline(key) - 0.672 * 140 / 2).toFixed(2), wantCapCentre: 540, gap: +(kb.x - lb.r).toFixed(2), groupCentreX: +((lb.x + kb.r) / 2).toFixed(2), keyFont: fontOf(key.querySelector('.rc-w')) }; }
    at(400); { const k = q('#d-t2-3 .rc-t2__key'); L.T2card = { keyBaseline: baseline(k), color: getComputedStyle(k).color, keyFont: fontOf(k.querySelector('.rc-w')) }; }
    at(385); { const l = q('#d-t2-2 .rc-t2__lead'); L.T2cardLeadOnly = { leadBaseline: baseline(l) }; }
    at(308); { const t3 = q('#c-t3'), year = t3.querySelector('.rc-t3__year'), inn = t3.querySelector('.rc-t3__in'), yb = baseline(year), ib = baseline(inn), mask = box(t3.querySelector('.rc-t3__mask'));
      const block = t3.querySelector('.rc-t3__block'), bm = new DOMMatrix(getComputedStyle(block).transform);
      L.T3 = { yearFont: fontOf(year), inFont: fontOf(inn), yearBaseline: yb, digitTop: +(yb - 0.688 * 220).toFixed(2), digitCentre: +(yb - 0.344 * 220).toFixed(2), wantDigitCentre: 540,
        inBaseline: ib, inToDigitTop: +((yb - 0.688 * 220) - ib).toFixed(2), maskBottomBelowBaseline: +(mask.b - yb).toFixed(2), inLeft: box(inn).x, yearLeft: box(year).x, blockScaleAtF308: +Math.hypot(bm.a, bm.b).toFixed(4) }; }
    at(830); { const lines = qa('#g-t6 .rc-t6__line'), cv = document.createElement('canvas').getContext('2d');
      L.T6 = lines.map(l => { const c = getComputedStyle(l), fs = parseFloat(c.fontSize); cv.font = c.fontWeight + ' ' + c.fontSize + ' ' + c.fontFamily; cv.letterSpacing = c.letterSpacing;
        const m = cv.measureText(l.textContent.trim()), b = baseline(l), lb = box(l);
        const inkW = m.actualBoundingBoxRight + m.actualBoundingBoxLeft; const left = lb.x + (lb.w - m.width) / 2 - m.actualBoundingBoxLeft;
        return { text: l.textContent.trim(), size: fs, baseline: b, inkTop: +(b - m.actualBoundingBoxAscent).toFixed(1), inkBottom: +(b + m.actualBoundingBoxDescent).toFixed(1), inkWidth: +inkW.toFixed(1), inkLeft: +left.toFixed(1), inkRight: +(left + inkW).toFixed(1) }; });
      L.T6safe = { top: L.T6[0].inkTop >= 54, bottom: L.T6[2].inkBottom <= 1026, sides: L.T6.every(x => x.inkLeft >= 96 && x.inkRight <= 1824) }; }
    at(940); { const qd = q('#h-t8 .rc-t8__quote'), qb = box(qd), col = { left: 1008, right: 1824 }, name = q('#h-t8 .rc-t8__name');
      L.T8 = { quoteFont: fontOf(qd), quoteBox: qb, insideColumn: qb.x >= col.left - 1 && qb.r <= col.right + 1, lines: Math.round(qb.h / (110 * 1.1)), nameFont: fontOf(name), nameBox: box(name), roleOpacity: +getComputedStyle(q('#h-t8 .rc-t8__role')).opacity }; }
    at(1010); { const lab = q('#i2-t9 .rc-t9__label'), lb = box(lab), b = baseline(lab); L.T9 = { box: lb, capCentre: +(b - 0.672 * 40 / 2).toFixed(2), boxCentre: +(lb.y + lb.h / 2).toFixed(2), font: fontOf(lab) }; }
    at(985); { const w = q('#i-t10 .rc-t10__clean'), b = baseline(w), lineTop = box(q('#i-t10')).y; L.T10 = { baseline: b, lineTop, capTopInLine: +(b - 0.672 * 160 - lineTop).toFixed(2), baselineInLine: +(b - lineTop).toFixed(2), cuts: [67, 103], capCentre: +(b - 0.336 * 160).toFixed(2), font: fontOf(w) }; }
    at(700); { const t = q('#f-t5 .rc-t5__text'); L.T5 = { font: fontOf(t), lines: qa('#f-t5 .rc-t5__line').length, copiesPerLine: qa('#f-t5 .rc-t5__line')[0].querySelectorAll('.rc-t5__glow').length }; }
    // fonts actually used + no synthesis (DOM): same text at 400 / 900 and italic / "Coolvetica Italic" normal
    const probe = (css, text) => { const s = document.createElement('span'); s.style.cssText = 'position:absolute;left:0;top:2000px;white-space:nowrap;' + css; s.textContent = text; document.body.appendChild(s); const w = s.getBoundingClientRect().width; s.remove(); return +w.toFixed(3); };
    const TXT = 'Hamburgefonts 1995? GRAND THEFT AUTO';
    L.fonts = { faces: [...document.fonts].map(f => f.family + ' ' + f.style + ' ' + f.status), sans400: probe('font: 400 100px var(--sans)', TXT), sans900: probe('font: 900 100px var(--sans)', TXT), sansFallback: probe('font: 400 100px sans-serif', TXT),
      serifNormal: probe('font: 400 100px var(--serif)', TXT), serifItalic: probe('font: italic 400 100px var(--serif)', TXT), sansItalic: probe('font: italic 900 100px var(--sans)', TXT), synthesis: getComputedStyle(q('#a-cap-1 .rc-w')).fontSynthesis };
    at(445); { const grid = q('#d2-cal .m3-grid'), col = q('#d2-cal .m3-col'), b = baseline(col.querySelectorAll('.m3-strip > span')[1]), g = box(grid);   // tens column of "18": cell 1 is in the window
      L.M3counter = { gridTop: g.y, digitTop: +(b - 0.688 * 120).toFixed(2), baseline: b, font: fontOf(q('#d2-cal .m3-counter')) }; }
    R.layout = L;
    return R;
  });

  // audit timeline: call every kit helper once on scratch elements (helpers the demo does not use included)
  out.easeAllHelpers = await page.evaluate(() => {
    const FPS = 30, scratch = document.createElement('div');
    scratch.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px;visibility:hidden';
    scratch.innerHTML = `
      <div id="z-t2" class="clip rc-t2" data-start="0" data-duration="3"><div class="rc-t2__row"><span class="rc-t2__lead">from the</span><span class="rc-t2__key">cops?</span></div></div>
      <div id="z-t3" class="clip rc-t3" data-start="0" data-duration="3"><div class="rc-t3__block"><div class="rc-t3__in">In</div><div class="rc-t3__year"><span class="rc-t3__num">1997</span></div></div></div>
      <div id="z-t4" class="clip rc-t4" data-start="0" data-duration="3"><span class="rc-t4__piece rc-t4--left">They ram.</span><span class="rc-t4__piece rc-t4--right">Two</span></div>
      <div id="z-t5" class="clip rc-t5" data-start="0" data-duration="3"><div class="rc-t5__text">The whole series</div></div>
      <div id="z-t5b" class="clip rc-t5" data-start="0" data-duration="3"><div class="rc-t5__text">started with a bug.</div></div>
      <div id="z-t6" class="clip rc-t6" data-start="0" data-duration="3"><div class="rc-t6__line">GTA</div></div>
      <div id="z-t7" class="clip rc-t7" data-start="0" data-duration="3"><span class="rc-t7__w">And</span> <span class="rc-t7__chip m4-chip"></span></div>
      <div id="z-t8" class="clip rc-t8" data-start="0" data-duration="3"><div class="rc-t8__block"><div class="rc-t8__quote">quote</div><div class="rc-t8__name">Name<span class="rc-t8__underline"><span class="rc-t8__walker"></span></span></div><div class="rc-t8__role">role</div></div></div>
      <div id="z-hl" class="rc-t9-hl"></div><div id="z-t9" class="clip rc-t9" data-start="0" data-duration="3"><span class="rc-t9__label">x</span></div>
      <div id="z-t10" class="clip rc-t10" data-start="0" data-duration="3"><span class="rc-t10__word">x</span></div>
      <div id="z-x2" class="rc-x2"></div><div id="z-x3" class="rc-x3"></div><div id="z-x5" class="clip rc-x5" data-start="0" data-duration="3"></div>
      <div id="z-x7" class="rc-x7"></div><div id="z-x7from" class="clip" data-start="0" data-duration="3"></div><div id="z-x9" class="rc-x9"></div>
      <div id="z-x4" class="rc-x4"></div>
      <div id="z-x6" class="rc-x6"><div class="rc-x6__screen"></div></div>
      <div id="z-cam" class="rc-cam"><div id="z-key" class="rc-cam"></div></div><div id="z-cam2" class="rc-cam"></div>
      <div id="z-grid" class="rc-l3 rc-l3--3x2"><div class="rc-l3__cell" id="z-c1"><div class="rc-l3__media"></div></div><div class="rc-l3__cell"><div class="rc-l3__media"></div></div>
        <div id="z-grow" class="rc-l3__grow" data-from-cell="1"><div class="rc-l3__grow-media"></div></div></div>
      <div id="z-l4" class="rc-l4" data-seed="1"><div class="rc-l4__frost"></div><div class="clip rc-l4__tiles" data-start="0" data-duration="3"></div></div>
      <div id="z-l5" class="rc-scr"><div class="rc-l5__prop" id="z-p1"></div></div>
      <div id="z-l7" class="rc-l7"><div class="clip rc-l7__dim" data-hole="10,10,100,100" data-start="0" data-duration="3"></div></div>
      <div id="z-l11" class="rc-l11"><div class="rc-l11__face rc-l11__face--front"><img alt="" style="--hf-color-grading-blur: 0"></div><div class="rc-l11__face rc-l11__face--back"></div></div>
      <div id="z-l12" class="rc-l12"><div class="rc-l12__card"><div class="rc-l12__drop"></div></div></div>
      <div id="z-stars" class="clip m1-stars" data-start="0" data-duration="3"></div>
      <div id="z-arrow" class="clip m2-arrow" data-start="0" data-duration="3"></div>
      <div id="z-cal" class="clip m3-cal" data-start="0" data-duration="3"></div><div id="z-cal2" class="clip m3-cal" data-start="0" data-duration="3"></div>
      <span id="z-chip" class="m4-chip"></span>
      <div id="z-err" class="clip m-errbox" data-start="0" data-duration="3"></div>
      <div id="z-shake"><div id="z-stamp" class="clip m-stamp" data-start="0" data-duration="3"></div></div>
      <div id="z-crt" class="l8-screen"><video id="z-crtv"></video></div>`;
    document.body.appendChild(scratch);
    const tl = gsap.timeline({ paused: true }), T = RCK.type, X = RCK.transitions, S = RCK.screens, M = RCK.motifs, C = RCK.cam, t = 0.5;
    const calls = {
      punchPair: () => T.punchPair(tl, '#z-t2', t, { outAt: 1 }), yearCard: () => T.yearCard(tl, '#z-t3', t, { pushUntil: 2 }), spreadWords: () => T.spreadWords(tl, '#z-t4', t, { outAt: 1.5 }),
      glowLine: () => T.glowLine(tl, '#z-t5', t), glowLineV2: () => T.glowLineV2(tl, '#z-t5b', [0.5, 0.6, 0.8, 1.0]), giantType: () => T.giantType(tl, '#z-t6', t), chipSentence: () => T.chipSentence(tl, '#z-t7', t),
      nameIn: () => T.nameIn(tl, '#z-t8', t), quoteType: () => T.quoteType(tl, '#z-t8', t), walk: () => T.walk(tl, '#z-t8', t), highlight: () => T.highlight(tl, '#z-hl', t), label: () => T.label(tl, '#z-t9', t),
      glitch: () => T.glitch(tl, '#z-t10', t), punchPairV2: () => T.punchPairV2(tl, '#z-t2b', [0.5, 0.7, 0.9]), spreadWordsV2: () => T.spreadWordsV2(tl, '#z-t4b', [0.5, 0.6, 0.7], { exitF: 3 }),
      drift: () => X.drift(tl, '#z-x2', t), tear: () => X.tear(tl, '#z-x4', t, { frames: 8 }), flash: () => X.flash(tl, '#z-x3', 0.2), blinds: () => X.blinds(tl, '#z-x5', 1), blindsClose: () => X.blindsClose(tl, X.blindsInit('#z-x5') && '#z-x5', 2.5),
      leakDissolve: () => X.leakDissolve(tl, '#z-x7', t, { from: '#z-x7from', to: '#z-x7from' }), sirenWash: () => X.sirenWash(tl, '#z-x9', t),
      zoom: () => X.zoom(tl, '#z-x6', t, { screen: { rect: [800, 450, 320, 180] }, blurDom: '#z-x6 .rc-x6__screen' }),
      zoomThrough: () => X.zoomThrough(tl, '#z-cam2', '#z-cam', 1), push: () => C.push(tl, '#z-cam', 2, { until: 3 }), zoomOut: () => C.zoomOut(tl, '#z-cam2', 2, { until: 3 }),
      punchIn: () => C.punchIn(tl, '#z-cam2', 3.2), keyPunch: () => C.keyPunch(tl, '#z-key', 2.5),
      gridBuild: () => S.gridBuild(tl, '#z-grid', t, { punch: 1.15 }), gridGrow: () => S.gridGrow(tl, '#z-grow', 1), frostClear: () => S.frostClear(tl, '#z-l4', [0.5, 0.7]), collage: () => S.collage(tl, '#z-l5', t, { until: 2 }),
      spotPush: () => S.spotPush(tl, '#z-l7', t, { until: 2 }), spotMove: () => S.spotMove(tl, '#z-l7', 1, { hole: '20,20,50,50' }), splitFlip: () => S.splitFlip(tl, '#z-l11', t), splitDrain: () => S.splitDrain(tl, '#z-l11', 1.5),
      cardsDrop: () => S.cardsDrop(tl, '#z-l12', t), cardsDrift: () => S.cardsDrift(tl, '#z-l12', t, { until: 2 }),
      starsPopIn: () => M.starsPopIn(tl, '#z-stars', t), starsBlink: () => M.starsBlink(tl, '#z-stars', 1, { until: 2 }), arrowDraw: () => M.arrowDraw(tl, '#z-arrow', t, { from: [100, 100], to: [300, 300] }),
      arrowErase: () => M.arrowErase(tl, '#z-arrow', 1.5), calendarFill: () => M.calendarFill(tl, '#z-cal', t, { slots: 18 }), calendarIn: () => M.calendarIn(tl, '#z-cal', 0.2), calendarExtend: () => M.calendarExtend(tl, '#z-cal2', 1.5, { slots: 18, filled: 18, to: 30, counter: 18 }),
      bugChipPop: () => M.bugChipPop(tl, '#z-chip', t), stampSlam: () => M.stampSlam(tl, '#z-stamp', t, { camera: '#z-shake' }), crtFlicker: () => M.crtFlicker(tl, '#z-crtv', t, { until: 1 }), errorBoxPop: () => M.errorBoxPop(tl, '#z-err', t)
    };
    // v01 markup for the converters
    scratch.insertAdjacentHTML('beforeend', '<div id="z-t2b" class="clip rc-t2" data-start="0" data-duration="3"><div class="rc-t2__row"><span class="rc-t2__lead">turn into</span><span class="rc-t2__key">thirty.</span></div></div><div id="z-t4b" class="clip rc-t4" data-start="0" data-duration="3"><span class="rc-t4__piece rc-t4--left">The wanted stars.</span></div>');
    const errors = {};
    Object.keys(calls).forEach(k => { try { calls[k](); } catch (e) { errors[k] = e.message; } });
    // the same audit as above, on this timeline
    const lin = f => Math.abs(f(0.25) - 0.25) < 1e-3 && Math.abs(f(0.5) - 0.5) < 1e-3 && Math.abs(f(0.75) - 0.75) < 1e-3;
    const res = { helpers: Object.keys(calls).length, errors, tweens: 0, cuts: 0, sets: 0, eased: 0, linear: [], byEase: {} };
    tl.getChildren(true, true, false).forEach(tw => {
      res.tweens++;
      const d = tw.duration(), ev = tw.vars.ease, name = typeof ev === 'function' ? 'function' : String(ev == null ? 'default(power1.out)' : ev);
      if (d === 0) { res.sets++; return; }
      if (/^steps/.test(name)) { res.cuts++; return; }
      res.byEase[name] = (res.byEase[name] || 0) + 1;
      if (lin(gsap.parseEase(ev == null ? 'power1.out' : ev))) res.linear.push({ ease: name, start: +(tw.startTime() * FPS).toFixed(2), frames: +(d * FPS).toFixed(2), targets: tw.targets().map(x => x.id || x.className || x.tagName).join(',') }); else res.eased++;
    });
    // rateRamp: the B6 speed lane must follow its ease, not a straight line
    const rr = JSON.parse(RCK.screens.rateRamp({ clipStart: 0, at: 1.0, durF: 6, clipDur: 3 })).lanes[0].points.filter(p => p.t > 1 && p.t < 1.2);
    res.rateRamp = rr.map(p => [+(p.t - 1).toFixed(4), p.v]);
    scratch.remove();
    return res;
  });
  out.consoleWarnings = warnings;
  fs.writeFileSync(path.join(DIR, 'review', 'measure_v02.json'), JSON.stringify(out, null, 1));
  const E = out.easeDemo, A = out.easeAllHelpers, RA = out.ruleA;
  console.log('demo timeline:', E.tweens, 'tweens |', E.cuts, 'hard cuts (0.5f steps) |', E.sets, 'sets |', E.eased, 'eased |', E.linear.length, 'LINEAR');
  console.log('  curve check:', E.curve.checked, 'tween props sampled at 25/50/75%: max |rendered - easings.net curve| =', E.curve.maxErr, '; min distance from a straight line =', E.curve.minDistLinear, '; flat:', E.curve.flat.length);
  console.log('  vs the easings.net formulas themselves:', JSON.stringify(E.curve.vsEasingsNet));
  console.log('all helpers (' + A.helpers + '):', A.tweens, 'tweens |', A.cuts, 'cuts |', A.sets, 'sets |', A.eased, 'eased |', A.linear.length, 'LINEAR', Object.keys(A.errors).length ? 'ERRORS ' + JSON.stringify(A.errors) : '');
  console.log('  eases used:', JSON.stringify(A.byEase));
  console.log('rule A:', RA.words, 'words | max on screen', RA.maxOnScreen.n, 'at f' + RA.maxOnScreen.f, JSON.stringify(RA.maxOnScreen.words), '| frames with > 2:', RA.framesOver2, '| first visible == onset:', RA.onsetExactly + '/' + RA.words, '| off by > 1f:', RA.onsetMismatch.length);
  console.log('console warnings:', warnings.length ? warnings.slice(0, 8) : 'none');
  await browser.close();
})();
