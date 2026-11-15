// Run (from hyperframes/_demo-type): node tools/measure_type.cjs > measure.json
// DOM measurement of the type demo: loads _demo-type/index.html in the HyperFrames headless shell, seeks the paused
// GSAP timeline to exact frame times and reads geometry / computed styles. Prints a JSON report.
const NM = '/root/.npm/_npx/56d07fea2d9f6f1f/node_modules';
const puppeteer = require(NM + '/puppeteer-core');
const fs = require('fs');
const CHROME = '/root/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/chrome-headless-shell-linux64/chrome-headless-shell';
const GSAP = NM + '/hyperframes/dist/vendor/npm/gsap@3.15.0/dist/gsap.min.js';
const PAGE = 'file:///home/user/claude-test-2.0-/RC_GTA-Origin/hyperframes/_demo-type/index.html';

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--allow-file-access-from-files', '--no-sandbox', '--force-device-scale-factor=1'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setRequestInterception(true);
  page.on('request', r => {
    if (r.url().includes('gsap')) r.respond({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(GSAP, 'utf8') });
    else r.continue();
  });
  page.on('pageerror', e => console.error('PAGEERROR', e.message));
  await page.goto(PAGE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const out = await page.evaluate(() => {
    const tl = window.__timelines['type-demo'];
    const R = {};
    const at = f => tl.totalTime(f / 30, false);
    const q = s => document.querySelector(s);
    const box = e => { const r = e.getBoundingClientRect(); return { x: +r.left.toFixed(2), y: +r.top.toFixed(2), w: +r.width.toFixed(2), h: +r.height.toFixed(2), r: +r.right.toFixed(2), b: +r.bottom.toFixed(2) }; };
    const cs = (e, p) => getComputedStyle(e).getPropertyValue(p);
    // baseline probe: a zero-size inline-block at the baseline of the element's first line
    const baseline = e => { const s = document.createElement('span'); s.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline'; e.appendChild(s); const y = s.getBoundingClientRect().top; s.remove(); return +y.toFixed(2); };
    const scaleOf = e => { const m = new DOMMatrix(getComputedStyle(e).transform); return +Math.hypot(m.a, m.b).toFixed(4); };
    const txOf = e => { const m = new DOMMatrix(getComputedStyle(e).transform); return { x: +m.e.toFixed(2), y: +m.f.toFixed(2) }; };
    const op = e => +(+getComputedStyle(e).opacity).toFixed(4);
    const font = e => { const c = getComputedStyle(e); return `${c.fontStyle} ${c.fontWeight} ${c.fontSize}/${c.lineHeight} ${c.fontFamily.split(',')[0]} ls=${c.letterSpacing} color=${c.color}`; };

    // ---- T1
    at(10);
    const c1 = q('#a-cap-1'), low = q('#b-cap-1');
    R.T1 = { box: box(c1), centreY: +(box(c1).y + box(c1).h / 2).toFixed(2), font: font(c1), shadow: cs(c1, 'text-shadow'), baseline: baseline(c1),
      capCentre: +(baseline(c1) - 0.7275 * 46 / 2).toFixed(2), lowBox: box(low), lowCentreY: +(box(low).y + box(low).h / 2).toFixed(2),
      data: [...document.querySelectorAll('[id^=a-cap-]')].map(e => [e.id, e.textContent, e.dataset.start, e.dataset.duration]) };
    // ---- T2
    const lead = q('#a-t2 .rc-t2__lead'), key = q('#a-t2 .rc-t2__key');
    const keyF = [133, 134, 135, 136, 137, 138, 139].map(f => { at(f); return { f, opacity: op(key), scale: scaleOf(key), filter: cs(key, 'filter') }; });
    at(132); const keyBefore = { opacity: op(key) };
    at(139);
    const lb = box(lead), kb = box(key);
    R.T2 = { leadFont: font(lead), keyFont: font(key), leadBaseline: baseline(lead), keyBaseline: baseline(key), gap: +(kb.x - lb.r).toFixed(2),
      groupCentreX: +((lb.x + kb.r) / 2).toFixed(2), keyBefore, keyF,
      out: [149, 150, 151, 152, 153].map(f => { at(f); return { f, rowOpacity: op(q('#a-t2 .rc-t2__row')) }; }),
      card: (() => { at(285); const k = q('#c-t2 .rc-t2__key'), l = q('#c-t2 .rc-t2__lead'); return { leadColor: cs(l, 'color'), keyColor: cs(k, 'color'), shadow: cs(k, 'text-shadow'), keyBox: box(k) }; })() };
    // ---- T3
    const t3 = q('#d-t3a'), digits = [...t3.querySelectorAll('.rc-t3__digit')], inn = t3.querySelector('.rc-t3__in'), year = t3.querySelector('.rc-t3__year');
    const roll = [347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 358, 360, 362].map(f => { at(f); return { f, y: digits.map(d => txOf(d).y), op: digits.map(d => op(d)) }; });
    at(380);
    const yb = box(year), ib = box(inn), mask = box(t3.querySelector('.rc-t3__mask'));
    R.T3 = { bg: cs(t3, 'background-color'), inFont: font(inn), yearFont: font(year), inLeft: ib.x, yearLeft: yb.x, inBottom: ib.b, yearTop: yb.y,
      yearBaseline: baseline(year), capCentre: +(baseline(year) - 0.7275 * 220 / 2).toFixed(2), yearCentreX: +(yb.x + (yb.w + 4.4) / 2).toFixed(2), maskBox: mask, maskOverflow: cs(t3.querySelector('.rc-t3__mask'), 'overflow'), roll,
      nov: (() => { at(425); const t = q('#d-t3b'); return { month: t.querySelector('.rc-t3__month').textContent, digits: [...t.querySelectorAll('.rc-t3__digit')].map(d => d.textContent).join(''), inLeft: box(t.querySelector('.rc-t3__in')).x, monthLeft: box(t.querySelector('.rc-t3__month')).x, yearBox: box(t.querySelector('.rc-t3__year')) }; })() };
    // ---- T4
    const p1 = q('#e-t4 .rc-t4__piece'), p2 = q('#e-t4 .rc-t4--right');
    R.T4 = { font: font(p1), shadow: cs(p1, 'text-shadow'),
      in: [451, 452, 453, 454, 455, 456].map(f => { at(f); return { f, op: op(p1), y: txOf(p1).y }; }),
      out: [500, 501, 502, 503, 504, 505].map(f => { at(f); return { f, op1: op(p1), op2: op(p2) }; }),
      boxes: (() => { at(495); return { left: box(p1), right: box(p2) }; })(),
      b14: (() => { at(595); return [...document.querySelectorAll('#e2-t4 .rc-t4__piece')].map(e => ({ t: e.textContent, box: box(e), op: op(e) })); })() };
    // ---- T5
    const t5 = q('#f-t5'), line = t5.querySelector('.rc-t5__line'), text = t5.querySelector('.rc-t5__text'), near = t5.querySelector('.rc-t5__glow--near'), wide = t5.querySelector('.rc-t5__glow--wide'), leak = t5.querySelector('.rc-t5__leak');
    const fadeIn = [601, 602, 603, 606, 610, 614, 620].map(f => { at(f); return { f, op: op(line), filter: cs(line, 'filter'), track: cs(line, '--rc-t5-track').trim(), letterSpacing: cs(text, 'letter-spacing'), leak: op(leak) }; });
    at(670);
    const chip5 = t5.querySelector('.rc-t7__chip');
    R.T5 = { bg: cs(t5, 'background-color'), textFont: font(text), near: { filter: cs(near, 'filter'), op: op(near), color: cs(near, 'color') }, wide: { filter: cs(wide, 'filter'), op: op(wide) },
      lineBox: box(text), fadeIn, leakHold: op(leak), leakBlend: cs(leak, 'mix-blend-mode'), chipBox: box(chip5), chipPop: [650, 651, 652, 653, 654, 655, 656, 657, 658].map(f => { at(f); return { f, s: scaleOf(chip5) }; }) };
    // ---- T6
    const t6 = q('#g-t6'), lines = [...t6.querySelectorAll('.rc-t6__line')], chars = [...t6.querySelectorAll('.rc-t6__ch')];
    at(760);
    R.T6 = { font: font(lines[0]), lineBoxes: lines.map(box), letters: chars.length,
      inkTop: +(baseline(lines[0]) - 0.7275 * 400).toFixed(2), inkBottom: baseline(lines[2]),
      typeOn: [685, 686, 687, 688, 690, 694, 702, 710, 711, 712, 713].map(f => { at(f); return { f, shown: chars.filter(c => op(c) > 0.5).length, partial: chars.filter(c => op(c) > 0.01 && op(c) < 0.99).length }; }) };
    // ---- T7
    const t7 = q('#h-t7'), words = [...t7.querySelectorAll('.rc-t7__w')], chip = t7.querySelector('.rc-t7__chip');
    at(820);
    const chipB = box(chip);
    R.T7 = { font: font(t7), box: box(t7), chip: { w: chip.offsetWidth, h: chip.offsetHeight, radius: cs(chip, 'border-radius'), bg: cs(chip, 'background-color'), centreY: +(chipB.y + chipB.h / 2).toFixed(2) },
      baseline: baseline(t7), capCentre: +(baseline(t7) - 0.7275 * 46 / 2).toFixed(2),
      words: [772, 773, 784, 785, 797, 798, 805, 806].map(f => { at(f); return { f, shown: words.map(w => op(w)) }; }),
      pop: [789, 790, 791, 792, 793, 794, 795, 796, 797, 798].map(f => { at(f); return { f, s: scaleOf(chip) }; }) };
    // ---- T8
    const i8 = q('#i-t8'), name = i8.querySelector('.rc-t8__name'), role = i8.querySelector('.rc-t8__role'), ul = i8.querySelector('.rc-t8__underline'), walker = i8.querySelector('.rc-t8__walker');
    const nameFade = [832, 833, 834, 836, 839].map(f => { at(f); return { f, name: op(name), role: op(role) }; });
    const walk = [839, 860, 881, 885].map(f => { at(f); const wb = box(walker), ub = box(ul); return { f, walkerLeft: +(wb.x - ub.x).toFixed(2), walkerRight: +(ub.r - wb.r).toFixed(2), standsOn: +(ub.y - wb.b).toFixed(2) }; });
    at(880);
    const j8 = q('#j-t8'), quote = j8.querySelector('.rc-t8__quote'), qch = [...quote.querySelectorAll('.rc-t8__ch')];
    R.T8 = { nameFont: font(name), roleFont: font(role), roleTransform: cs(role, 'text-transform'), roleText: role.textContent, nameFade, nameBaseline: baseline(name),
      underline: { box: box(ul), color: cs(ul, 'background-color') }, walk,
      quoteFont: font(quote), quoteChars: qch.length, quoteText: quote.textContent,
      typing: [892, 893, 894, 895, 896, 900, 901, 902, 903].map(f => { at(f); return { f, shown: qch.filter(c => op(c) > 0.5).length }; }),
      card: (() => { at(950); return { quoteColor: cs(quote, 'color'), nameColor: cs(j8.querySelector('.rc-t8__name'), 'color'), shadow: cs(quote, 'text-shadow'), quoteLeft: box(quote).x, nameLeft: box(j8.querySelector('.rc-t8__name')).x, roleOp: op(j8.querySelector('.rc-t8__role')) }; })() };
    // ---- T9
    const hl = q('#k-hl'), lab = q('#l-t9 .rc-t9__label');
    R.T9 = { hl: { bg: cs(hl, 'background-color'), op: op(hl), blend: cs(hl, 'mix-blend-mode'),
        swipe: [985, 986, 987, 988, 990, 994, 1000].map(f => { at(f); return { f, clip: cs(hl, 'clip-path') }; }) },
      label: (() => { at(1070); return { font: font(lab), bg: cs(lab, 'background-color'), color: cs(lab, 'color'), padding: cs(lab, 'padding'), radius: cs(lab, 'border-radius'), box: box(lab), transform: cs(lab, 'text-transform'), shadow: cs(lab, 'text-shadow') }; })(),
      pop: [1045, 1046, 1047, 1048, 1049, 1050].map(f => { at(f); return { f, op: op(lab), s: scaleOf(lab) }; }) };
    // ---- T10
    const t10 = q('#m-t10'), clean = t10.querySelector('.rc-t10__clean'), gl = t10.querySelector('.rc-t10__glitch'), slices = [...t10.querySelectorAll('.rc-t10__slice')];
    const r = t10.querySelector('.rc-t10__ch--r'), b = t10.querySelector('.rc-t10__ch--b');
    R.T10 = { font: font(clean), wordBox: box(t10.querySelector('.rc-t10__word')), rOffset: txOf(r).x, bOffset: txOf(b).x, rColor: cs(r, 'color'), bColor: cs(b, 'color'), blend: cs(r, 'mix-blend-mode'),
      frames: [1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1112].map(f => { at(f); return { f, clean: op(clean), glitch: op(gl), slicesX: slices.map(s => txOf(s).x) }; }),
      b17: [1159, 1160, 1163, 1165, 1166].map(f => { at(f); const t = q('#m2-t10'); return { f, clean: op(t.querySelector('.rc-t10__clean')), glitch: op(t.querySelector('.rc-t10__glitch')), slicesX: [...t.querySelectorAll('.rc-t10__slice')].map(s => txOf(s).x) }; }) };
    // seek-order independence: jump around and compare a few states
    const probe = () => [op(key), scaleOf(key), op(digits[3]), txOf(digits[3]).y, op(chars[5]), scaleOf(chip), txOf(slices[1]).x, op(qch[10])].join('|');
    const order = [1103, 135, 351, 700, 795, 897, 1103, 0, 351, 135, 897, 795, 700];
    const states = {}; let consistent = true;
    order.forEach(f => { at(f); const s = probe(); if (states[f] && states[f] !== s) consistent = false; states[f] = s; });
    R.seekOrderIndependent = consistent;
    return R;
  });
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
