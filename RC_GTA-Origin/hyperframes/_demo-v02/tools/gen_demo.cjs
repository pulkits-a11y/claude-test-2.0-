// Builds _demo-v02/index.html: every v02 kit item (REVISION_v02 rules A, C, D + Coolvetica), used exactly as a beat
// builder would. Word times = the v02 beat map (timing/beat_map.json), shifted to this demo's timeline.
// Run from _demo-v02:  node tools/gen_demo.cjs && bash tools/treat.sh   (treat.sh adds the media-treatment blur control)
globalThis.window = globalThis;
require('../assets/kit/type.js');
const fs = require('fs');
const T = RCK.type;
const BM = require('../../../timing/beat_map.json');
const words = (id, shiftF) => BM.beats.find(b => b.id === id).words.map(w => ({ text: w.text, comp_t: w.comp_t + shiftF / 30, comp_end_t: w.comp_end_t + shiftF / 30 }));
const A = f => T.attrF(f), D = (f0, f1) => T.durF(f0, f1), S = f => (f / 30).toFixed(6);
const html = [], js = [];
const tag = (id, f0, f1, text, card) => html.push(`<div id="${id}" class="clip demo-tag${card ? ' rc-on-card' : ''}" data-start="${A(f0)}" data-duration="${D(f0, f1)}" data-track-index="30" style="z-index: 90">${text}</div>`);
const vid = (id, src, f0, f1, cls, extra) => `<video id="${id}" class="clip ${cls || 'demo-fill'}" src="assets/footage/${src}" muted playsinline data-start="${A(f0)}" data-duration="${D(f0, f1)}"${extra || ''}></video>`;
const report = [];
const plan = (label, w, chunks, o) => { const p = T.captionPlanV2(w, chunks, o); report.push('== ' + label + '\n' + T.captionReport(p)); return p; };

/* ---------------- A: B1 hook. T1 word-by-word + T2 pair (generator), camera on the picture wrapper ---------------- */
{
  const W = words('B1', 0);
  html.push(`<div id="a-cam" class="rc-cam" style="z-index: 1"><div id="a-key" class="rc-cam">
  ${vid('a-v1', 'R1.3.mp4', 0, 40)}
  ${vid('a-v2', 'R1.2.mp4', 40, 150)}
</div></div>`);
  const p1 = plan('A T1 (B1)', W, 'Why does / every GTA, / even GTA 6, / have you running', { from: 0 });
  html.push(T.captionHTMLV2(p1, { idPrefix: 'a-cap', z: 40, track: 20 }));
  const p2 = plan('A T2 (B1)', W, 'from the cops?', { from: 10, end: 150 / 30, exitF: 3 });
  html.push(T.captionHTMLV2(p2, { style: 't2', idPrefix: 'a-t2', z: 40, track: 21 }));
  const cops = p2.groups[1].words[1].frame;
  js.push(`// A (B1): shot 1 zooms out 110 -> 100% (sine.inOut), the cut at f40 punches in 115 -> 100% (10f expo.out), then the held
      // shot pushes 100 -> 108% (sine.inOut); the keyword "cops?" punches the inner wrapper 100 -> 106% (3f expo.out, back 9f).
      C.zoomOut(tl, '#a-cam', 0, { until: ${S(40)} });
      C.punchIn(tl, '#a-cam', ${S(40)});
      C.push(tl, '#a-cam', ${S(50)}, { until: ${S(150)} });
      C.keyPunch(tl, '#a-key', ${S(cops)});`);
  tag('a-tag', 0, 150, 'v02 · B1 · T1 groups word by word (max 2) + T2 pair · camera: zoomOut, punchIn on the cut (f40), push, keyPunch on "cops?"');
}

/* ---------------- B: B5. v01 T1 markup converted at runtime (wordsV2), low line, split screen pushing ---------------- */
{
  const off = 150, W = words('B5', off);
  html.push(`<div id="b-cam" class="rc-cam" style="z-index: 1"><div id="b-split" class="rc-l11">
  <div id="b-ground" class="clip rc-l11__ground" data-start="${A(150)}" data-duration="${D(150, 245)}"></div>
  <div class="rc-l11__face rc-l11__face--front">
    <div class="rc-l11__half rc-l11__half--left">${vid('b-l', 'R5.2.mp4', 150, 245, ' ')}</div>
    <div class="rc-l11__half rc-l11__half--right">${vid('b-r', 'R5.1.mp4', 150, 245, ' ')}</div>
  </div>
</div></div>`);
  const v1 = T.captionPlan(W, 'In it, / you play / a police officer / chasing criminals.', { from: 0, end: 245 / 30, v01: true });
  html.push(T.captionHTML(v1, { idPrefix: 'b-cap', low: true, z: 40, track: 20, cls: 'b-cap' }));
  js.push(`// B (B5): the v01 T1 chunk clips above are converted in place (groups of max 2 words, word pops).
      T.wordsV2(tl, '.b-cap', ${JSON.stringify(W.map(w => +w.comp_t.toFixed(4)))});
      C.push(tl, '#b-cam', ${S(150)}, { until: ${S(245)} });`);
  report.push('== B T1 (B5, converted at runtime): ' + T.captionPlanV2(W, 'In it, / you play / a police officer / chasing criminals.', { from: 0, end: 245 / 30 }).groups.map(g => g.text).join(' / '));
  tag('b-tag', 150, 245, 'v02 · B5 · v01 caption markup converted at runtime (wordsV2): "a / police officer", low line');
}

/* ---------------- C: B2 -> B3 zoom-through (both halves here; in the edit they are split at the beat boundary) ---------------- */
{
  const B = 292, W2 = words('B2', 270 - 154);
  html.push(`<div id="c-cam" class="rc-cam" style="z-index: 1">${vid('c-v', 'R9.1.mp4', 250, B, 'demo-fill', ' data-media-start="0.5000" style="--hf-color-grading-blur: 0"')}</div>`);
  const pc = plan('C T1 (B2 end)', W2, 'saved it.', { from: 13, end: B / 30 });
  html.push(T.captionHTMLV2(pc, { idPrefix: 'c-cap', z: 40, track: 20 }));
  html.push(`<div id="c-card-cam" class="rc-cam" style="z-index: 2"><div id="c-t3" class="clip rc-t3" data-start="${A(B)}" data-duration="${D(B, 345)}"><div class="rc-t3__block"><div class="rc-t3__in">In</div><div class="rc-t3__year"><span class="rc-t3__num">1995</span></div></div></div></div>`);
  js.push(`// C (B2 -> B3): outgoing picture 100 -> 140% + blur (5f expo.in, peak on f${B - 1}), cut at f${B}, the year card arrives
      // from 130% blurred and settles in 9f (expo.out). Footage blur = media-treatment control, card blur = CSS (DOM).
      X.zoomThroughOut(tl, '#c-cam', ${S(B)});
      X.zoomThroughIn(tl, '#c-card-cam', ${S(B)});
      // the digits roll from the cut, so the card arrives with the year rolling in while the zoom settles (lands B+14)
      T.yearCard(tl, '#c-t3', ${S(B)}, { pushFrom: ${S(B + 14)}, pushUntil: ${S(345)} });`);
  tag('c-tag', 250, 345, 'v02 · B2 → B3 zoom-through: out 100→140% + blur (expo.in, 5f) | cut f292 | in 130→100% (expo.out, 9f) · T3 in Coolvetica');
}

/* ---------------- D1: B4 T2 on a gray card (generator) + calendar fill ---------------- */
{
  const off = 310, W = words('B4', off);
  html.push(`<div id="d-card" class="clip rc-card rc-full" data-start="${A(350)}" data-duration="${D(350, 422)}" style="z-index: 1"></div>`);
  html.push(`<div id="d-cal" class="clip m3-cal" data-start="${A(350)}" data-duration="${D(350, 422)}" style="z-index: 10"></div>`);
  const p = plan('D1 T2 (B4)', W, 'planned to take 18 months.', { from: 7, loose: true, end: 422 / 30 });
  html.push(T.captionHTMLV2(p, { style: 't2', idPrefix: 'd-t2', key: 2, onCard: true, y: 360, z: 40, track: 21 }));
  js.push(`// D1 (B4): T2 groups on the card; the 18 squares fill 2f apart from "planned" (hard fills).
      M.calendarFill(tl, '#d-cal', ${S(p.groups[0].startFrame)}, { slots: 18, filled: 0 });`);
  tag('d-tag', 350, 422, 'v02 · B4 · T2 on a card: "planned / to take / 18 months." (lead-only groups on the shared baseline)', true);
}

/* ---------------- D2: B12 calendar opening animation + counter roll (power1.inOut) + T2 via punchPairV2 on v01 markup ---------------- */
{
  const off = 425, W = words('B12', off);
  html.push(`<div id="d2-card" class="clip rc-card rc-full" data-start="${A(425)}" data-duration="${D(425, 515)}" style="z-index: 1"></div>`);
  html.push(`<div id="d2-cal" class="clip m3-cal" data-start="${A(425)}" data-duration="${D(425, 515)}" style="z-index: 10"></div>`);
  const p = plan('D2 T1 (B12)', W, 'Of course,', { from: 0 });
  html.push(T.captionHTMLV2(p, { idPrefix: 'd2-cap', onCard: true, y: 940, z: 40, track: 20 }));
  const turn = W[5].comp_t, thirty = W[7].comp_t;
  html.push(`<div id="d2-t2" class="clip rc-t2 rc-on-card" data-start="${T.attr(turn)}" data-duration="${T.dur(turn, 515 / 30)}" data-track-index="21" style="z-index: 40; --rc-y: 250px"><div class="rc-t2__row"><span class="rc-t2__lead">turn into</span><span class="rc-t2__key">thirty.</span></div></div>`);
  js.push(`// D2 (B12): the calendar's opening animation (rises 90 px + scales 90 -> 100%, 12f expo.out), placed higher (y 400);
      // 12 red squares 2f apart, the counter rolls 18 -> 30 (power1.inOut per roll) landing on "thirty".
      M.calendarInit('#d2-cal', { slots: 18, filled: 18, counter: 18, y: 400 });
      M.calendarIn(tl, '#d2-cal', ${S(428)});
      M.calendarExtend(tl, '#d2-cal', 0, { to: 30, landAt: ${thirty.toFixed(4)} });
      T.punchPairV2(tl, '#d2-t2', [${W.slice(5, 8).map(w => w.comp_t.toFixed(4)).join(', ')}]);`);
  tag('d2-tag', 425, 515, 'v02 · B12 · calendarIn (opening animation) + counter roll easeInOutQuad · T2 v01 markup → punchPairV2', true);
}

/* ---------------- E1: B3 T4 "Dundee, + Scotland." (two pieces, one group) over the L2 band ---------------- */
{
  const off = 470, W = words('B3', off);
  html.push(`<div id="e-cam" class="rc-cam" style="z-index: 1">${vid('e-v', 'R3.1.mp4', 520, 575)}</div>`);
  html.push(`<div id="e-bars" class="clip demo-fill" data-start="${A(520)}" data-duration="${D(520, 575)}" style="z-index: 2"><div class="demo-bar" style="top: 0"></div><div class="demo-bar" style="top: 942px"></div></div>`);
  const p = plan('E1 T4 (B3)', W, 'Dundee, + Scotland.', { from: 5, end: 575 / 30 });
  html.push(T.captionHTMLV2(p, { style: 't4', idPrefix: 'e-t4', place: ['left', 'right'], z: 40, track: 21 }));
  js.push(`// E1 (B3): punch-in on the cut into the band shot, then a slow push.
      C.punchIn(tl, '#e-cam', ${S(520)}, { from: 1.12, frames: 9 });
      C.push(tl, '#e-cam', ${S(529)}, { until: ${S(575)}, to: 1.06 });`);
  tag('e-tag', 520, 575, 'v02 · B3 · T4 "Dundee, + Scotland." = one group of two pieces, each word pops on its onset');
}

/* ---------------- E2: B14 T4, v01 markup converted (spreadWordsV2): groups replace each other ---------------- */
{
  const off = 490, W = words('B14', off);
  html.push(`<div id="e2-cam" class="rc-cam" style="z-index: 1"><div id="e2-key" class="rc-cam">${vid('e2-v', 'R1.2.mp4', 580, 680, 'demo-fill', ' data-media-start="0.6000"')}</div></div>`);
  html.push(`<div id="e2-t4" class="clip rc-t4" data-start="${A(587)}" data-duration="${D(587, 680)}" data-track-index="21" style="z-index: 40"><span class="rc-t4__piece rc-t4--left rc-t4--top">The wanted stars.</span><span class="rc-t4__piece rc-t4--right">The sirens.</span><span class="rc-t4__piece rc-t4--left rc-t4--bottom">The running.</span></div>`);
  js.push(`// E2 (B14): zoom out 110 -> 100% across the shot; keyword punch on "sirens"; T4 v01 markup converted.
      C.zoomOut(tl, '#e2-cam', ${S(580)}, { until: ${S(680)} });
      C.keyPunch(tl, '#e2-key', ${W[13].comp_t.toFixed(4)});
      T.spreadWordsV2(tl, '#e2-t4', [${W.slice(9, 16).map(w => w.comp_t.toFixed(4)).join(', ')}]);`);
  tag('e2-tag', 580, 680, 'v02 · B14 · T4 v01 markup → spreadWordsV2: "The / wanted stars." → "The sirens." → "The running."');
}

/* ---------------- F: B16 T5 glow line, word by word (generator) ---------------- */
{
  const off = 635, W = words('B16', off);
  const p = plan('F T5 (B16)', W, 'The whole series started with a bug.', { from: 6, end: 760 / 30 });
  html.push(T.captionHTMLV2(p, { style: 't5', id: 'f-t5', clipStart: 685 / 30, clipEnd: 760 / 30, z: 5, track: 21 }));
  tag('f-tag', 685, 760, 'v02 · B16 · T5 glow line word by word: "The / whole series / started with / a bug." (the word "bug", no chip)');
}

/* ---------------- G: B13 T6 giant type (eased type-on) behind a framed clip stand-in ---------------- */
{
  html.push(`<video id="g-bg" class="clip demo-fill" src="assets/footage/R13.1.mp4" muted playsinline data-start="${A(765)}" data-duration="${D(765, 860)}" style="z-index: 1"></video>`);
  html.push(`<div id="g-dim" class="clip demo-fill demo-dim" data-start="${A(765)}" data-duration="${D(765, 860)}" style="z-index: 2"></div>`);
  html.push(`<div id="g-t6" class="clip rc-t6" data-start="${A(765)}" data-duration="${D(765, 860)}" style="z-index: 5"><div class="rc-t6__line">GRAND</div><div class="rc-t6__line">THEFT</div><div class="rc-t6__line">AUTO</div></div>`);
  html.push(`<video id="g-frame" class="clip demo-l6" src="assets/footage/R13.1.mp4" muted playsinline data-start="${A(765)}" data-duration="${D(765, 860)}" data-layout-allow-occlusion style="z-index: 8"></video>`);
  js.push(`// G (B13): 14 letters over the v01 length (26f), start times on easeOutQuad (stagger ease power1.out).
      T.giantType(tl, '#g-t6', ${S(770)});`);
  tag('g-tag', 765, 860, 'v02 · B13 · T6 GRAND / THEFT / AUTO in Coolvetica 420 px, type-on eased (power1.out timing)');
}

/* ---------------- H: B6 T8 quote card (eased type-on, eased fades) ---------------- */
{
  html.push(`<div id="h-card" class="clip rc-card rc-full" data-start="${A(865)}" data-duration="${D(865, 955)}" style="z-index: 1"></div>`);
  html.push(`<div id="h-t8" class="clip rc-t8 rc-t8--right rc-on-card" data-start="${A(865)}" data-duration="${D(865, 955)}" style="z-index: 10"><div class="rc-t8__block"><div class="rc-t8__quote">“awful…<br>too sim-y.”</div><div class="rc-t8__name">Gary Penn</div><div class="rc-t8__role">DMA DESIGN · GAMASUTRA, 2011</div></div></div>`);
  js.push(`// H (B6): quote types on over the v01 length with eased timing; name and role fade in power2.out.
      T.quoteType(tl, '#h-t8', ${S(868)});
      T.nameIn(tl, '#h-t8', ${S(884)});`);
  tag('h-tag', 865, 955, 'v02 · B6 · T8 quote (Coolvetica Italic 110 px, 2 lines) on the L5 card: eased type-on + eased fades', true);
}

/* ---------------- I: T10 glitch word + T9 label (Coolvetica caps in the box) ---------------- */
{
  html.push(`<div id="i-black" class="clip rc-ink rc-full" data-start="${A(960)}" data-duration="${D(960, 990)}" style="z-index: 1"></div>`);
  html.push(`<div id="i-t10" class="clip rc-t10" data-start="${A(962)}" data-duration="${D(962, 990)}" style="z-index: 10"><span class="rc-t10__word">breaks.</span></div>`);
  html.push(vid('i2-v', 'R3.8.mp4', 990, 1022));
  html.push(`<div id="i2-t9" class="clip rc-t9" data-start="${A(992)}" data-duration="${D(992, 1022)}" style="z-index: 10; --rc-x: 1180px; --rc-y: 700px"><span class="rc-t9__label">Race and Chase</span></div>`);
  js.push(`T.glitch(tl, '#i-t10', ${S(962)});
      T.label(tl, '#i2-t9', ${S(993)});`);
  tag('i-tag', 960, 1022, 'v02 · T10 glitch word (hard per-frame cuts) · T9 label caps centred in Coolvetica');
}

/* ---------------- J: X3 flash (eased ramps) and X5 blinds (eased slats) ---------------- */
{
  html.push(vid('j-v1', 'R1.3.mp4', 1025, 1040));
  html.push(vid('j-v2', 'R1.2.mp4', 1040, 1065, 'demo-fill', ' data-media-start="2.0000"'));
  html.push(vid('j-v3', 'R3.1.mp4', 1065, 1085));
  html.push(`<div id="j-x3" class="rc-x3" style="z-index: 50"></div>`);
  html.push(`<div id="j-x5" class="clip rc-x5" data-start="${A(1055)}" data-duration="${D(1055, 1075)}" style="z-index: 50"></div>`);
  js.push(`X.flash(tl, '#j-x3', ${S(1040)});
      X.blinds(tl, '#j-x5', ${S(1065)});`);
  tag('j-tag', 1025, 1085, 'v02 · X3 flash: ramp easeInQuad, fade easeOutQuad · X5 blinds: close easeInQuart, open easeOutQuart');
}

const END = 1085;
const out = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/kit/base.css" />
    <link rel="stylesheet" href="assets/kit/type.css" />
    <link rel="stylesheet" href="assets/kit/motifs.css" />
    <link rel="stylesheet" href="assets/kit/transitions.css" />
    <link rel="stylesheet" href="assets/kit/screens.css" />
    <style>
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #0A0A0A; }
      #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0A0A0A; }
      /* demo-only scaffolding (not kit) */
      .demo-fill { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }
      .demo-bar { position: absolute; left: 0; width: 1920px; height: 138px; background: var(--ink-black); }
      .demo-dim { background: color-mix(in srgb, var(--ink-black) 45%, transparent); }
      .demo-l6 { position: absolute; left: 365px; top: 205px; width: 1190px; height: 670px; object-fit: cover; box-sizing: border-box; border: 2px solid var(--white); }
      .demo-tag { position: absolute; left: 96px; top: 20px; height: 26px; font-family: var(--sans); font-size: 19px; line-height: 26px; letter-spacing: 0.02em; color: var(--white); opacity: 0.8; white-space: nowrap; text-shadow: var(--text-shadow); }
      .demo-tag.rc-on-card { color: var(--card-ink); text-shadow: none; }
    </style>
  </head>
  <body>
    <!-- RC kit v02 demo (REVISION_v02 rules A, C, D, Coolvetica), generated by tools/gen_demo.cjs from the kit itself.
         Word times: timing/beat_map.json (v02), shifted per section. Footage: copies of the beats' real working clips. -->
    <div id="root" data-composition-id="kit-v02-demo" data-start="0" data-duration="${(END / 30).toFixed(7)}" data-width="1920" data-height="1080">
${html.join('\n')}
    </div>
    <script src="assets/kit/type.js"></script>
    <script src="assets/kit/motifs.js"></script>
    <script src="assets/kit/transitions.js"></script>
    <script src="assets/kit/screens.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const T = RCK.type, M = RCK.motifs, X = RCK.transitions, C = RCK.cam;
      // every generated caption clip (class rc-cap): words pop on their own onset frame
      T.captionPops(tl);
      ${js.join('\n      ')}
      tl.set({}, {}, ${(END / 30).toFixed(6)});
      window.__timelines["kit-v02-demo"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(__dirname + '/../index.html', out);
fs.writeFileSync(__dirname + '/../review/caption_groups.txt', report.join('\n') + '\n');
console.log('wrote index.html (' + END + ' frames)');
console.log(report.join('\n'));
