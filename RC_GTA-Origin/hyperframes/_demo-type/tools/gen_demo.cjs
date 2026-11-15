// Generates hyperframes/_demo-type/index.html: every T-style of the RC kit in sequence, built exactly as a beat would
// (kit linked from assets/kit, timed elements written as HTML, kit helpers on one paused GSAP timeline).
// Run (from hyperframes/_demo-type): node tools/gen_demo.cjs   (writes index.html and tools/marks.json)
const fs = require('fs');
const ROOT = '/home/user/claude-test-2.0-/RC_GTA-Origin';
const OUT = ROOT + '/hyperframes/_demo-type/index.html';
globalThis.window = globalThis;
require(ROOT + '/hyperframes/_demo-type/assets/kit/type.js');
const T = RCK.type;
const bm = JSON.parse(fs.readFileSync(ROOT + '/timing/beat_map.json', 'utf8'));
const W = id => bm.beats.find(b => b.id === id).words;
const S = f => T.attrF(f), D = (a, b) => T.durF(a, b), sec = f => +(f / 30).toFixed(6);

const html = [];   // timed elements
const js = [];     // timeline calls
const marks = [];  // [label, frame] for snapshots
let track = 0;
const tag = (id, f0, f1, text, card) => html.push(`<div id="${id}" class="clip demo-tag${card ? ' rc-on-card' : ''}" data-start="${S(f0)}" data-duration="${D(f0, f1)}" data-track-index="9" style="z-index: 50">${text}</div>`);
const video = (id, rid, f0, f1, extra = '', z = 1) => html.push(`<video id="${id}" class="clip demo-bg" src="assets/footage/${rid}.mp4" muted playsinline data-start="${S(f0)}" data-duration="${D(f0, f1)}" data-track-index="1" style="z-index: ${z};${extra}"></video>`);
const block = (id, f0, f1, cls, z, inner = '', style = '') => html.push(`<div id="${id}" class="clip ${cls}" data-start="${S(f0)}" data-duration="${D(f0, f1)}" data-track-index="2" style="z-index: ${z};${style}">${inner}</div>`);

// ---------- A. T1 + T2, B1 timing (composition-local comp_t, 6f handle) : frames 0-155 ----------
{
  const w = W('B1');
  video('a-bg', 'R1.2', 0, 155);
  tag('a-tag', 0, 155, 'DEMO · T1 running captions → T2 punch pair (B1 timing)');
  const plan = T.captionPlan(w, 'Why does / every GTA, / even GTA 6, / have you running');
  html.push(T.captionHTML(plan, { idPrefix: 'a-cap', z: 10, track: 3 }));
  const lead = T.frame(w[plan.next].comp_t), key = T.frame(w[12].comp_t);   // "from", "cops?"
  block('a-t2', lead, 153, 'rc-t2', 10, '<div class="rc-t2__row"><span class="rc-t2__lead">from the</span><span class="rc-t2__key">cops?</span></div>');
  js.push(`T.punchPair(tl, '#a-t2', ${sec(key)}, { outAt: ${sec(149)} });`);
  plan.items.forEach((it, i) => marks.push([`T1 chunk ${i + 1} first frame`, it.startFrame]));
  marks.push(['T2 lead-in only', lead], ['T2 key f+2', key + 2], ['T2 key settled', key + 6], ['T2 out f+2', 151]);
}
// ---------- B. T1 low (y 860), B5 timing : frames 155-255 ----------
{
  const o = 155, w = W('B5').map(x => Object.assign({}, x, { comp_t: x.comp_t + o / 30, comp_end_t: x.comp_end_t + o / 30 }));
  video('b-bg', 'R5.1', o, o + 100);
  tag('b-tag', o, o + 100, 'DEMO · T1 low (face in the centre: y 860), B5 timing');
  const plan = T.captionPlan(w, 'In it, / you play / a police officer / chasing criminals.', { end: (o + 94) / 30 });
  html.push(T.captionHTML(plan, { idPrefix: 'b-cap', low: true, z: 10, track: 3 }));
  marks.push(['T1 low', plan.items[2].startFrame + 3]);
}
// ---------- C. T2 on a gray card (B4) + the cover frame : frames 255-345 ----------
{
  block('c-card', 255, 300, 'rc-card demo-full', 1);
  tag('c-tag', 255, 300, 'DEMO · T2 on a gray card, above the L9 calendar (B4)', true);
  block('c-t2', 258, 296, 'rc-t2 rc-on-card', 10, '<div class="rc-t2__row"><span class="rc-t2__lead">planned to take</span><span class="rc-t2__key">18 months.</span></div>', ' --rc-y: 300px;');
  js.push(`T.punchPair(tl, '#c-t2', ${sec(270)}, { outAt: ${sec(292)} });`);
  marks.push(['T2 card key f0', 270], ['T2 card key f+3', 273], ['T2 card settled', 280]);
  video('c2-bg', 'R10.2', 300, 345);
  tag('c2-tag', 300, 345, 'DEMO · cover frame: "GTA started as a cop game" in T2 style');
  block('c2-t2', 300, 345, 'rc-t2', 10, '<div class="rc-t2__row"><span class="rc-t2__lead">GTA started as a</span><span class="rc-t2__key">cop game</span></div>');
  js.push(`T.punchPair(tl, '#c2-t2', ${sec(306)});`);
  marks.push(['cover settled', 330]);
}
// ---------- D. T3 year cards (B3 "In 1995", B13 "In Nov 1997") : frames 345-449 ----------
{
  block('d-t3a', 345, 397, 'rc-t3', 5, '<div class="rc-t3__block"><div class="rc-t3__in">In</div><div class="rc-t3__year"><span class="rc-t3__num">1995</span></div></div>');
  tag('d-tag', 345, 397, 'DEMO · T3 year card (B3)', true);
  js.push(`T.yearCard(tl, '#d-t3a', ${sec(348)});`);
  block('d-t3b', 397, 449, 'rc-t3', 5, '<div class="rc-t3__block"><div class="rc-t3__in">In</div><div class="rc-t3__year"><span class="rc-t3__month">Nov</span> <span class="rc-t3__num">1997</span></div></div>');
  tag('d2-tag', 397, 449, 'DEMO · T3 year card, month + year (B13)', true);
  js.push(`T.yearCard(tl, '#d-t3b', ${sec(400)});`);
  marks.push(['T3 f0', 348], ['T3 f+2', 350], ['T3 f+5', 353], ['T3 settled', 370], ['T3 Nov f+4', 404], ['T3 Nov settled', 420]);
}
// ---------- E. T4 spread words (B3 over an L2 stand-in; B14 three spots) : frames 449-599 ----------
{
  video('e-bg', 'R3.1', 449, 509);
  html.push(`<div id="e-bars" class="clip demo-full" data-start="${S(449)}" data-duration="${D(449, 509)}" data-track-index="1" style="z-index: 2"><div class="demo-bar" style="top: 0"></div><div class="demo-bar" style="top: 942px"></div></div>`);
  tag('e-tag', 449, 509, 'DEMO · T4 spread words over an L2 band stand-in (B3)');
  block('e-t4', 449, 505, 'rc-t4', 10, '<span class="rc-t4__piece rc-t4--left">Dundee,</span><span class="rc-t4__piece rc-t4--right">Scotland.</span>');
  js.push(`T.spreadWords(tl, '#e-t4', ${sec(452)}, { times: [${sec(452)}, ${sec(468)}], outAt: ${sec(501)} });`);
  marks.push(['T4 piece1 f+2', 454], ['T4 piece1 settled', 460], ['T4 both', 480], ['T4 out f+2', 503]);
  video('e2-bg', 'R1.3', 509, 599);
  tag('e2-tag', 509, 599, 'DEMO · T4, each phrase in its own spot until the beat ends (B14)');
  block('e2-t4', 509, 599, 'rc-t4', 10, '<span class="rc-t4__piece rc-t4--left rc-t4--top">The wanted stars.</span><span class="rc-t4__piece rc-t4--right">The sirens.</span><span class="rc-t4__piece rc-t4--left rc-t4--bottom">The running.</span>');
  js.push(`T.spreadWords(tl, '#e2-t4', ${sec(512)}, { times: [${sec(512)}, ${sec(549)}, ${sec(578)}] });`);
  marks.push(['T4 B14 all', 590]);
}
// ---------- F. T5 glow line + T7 chip (B16) : frames 599-680 ----------
{
  block('f-t5', 599, 680, 'rc-t5', 5, '<div class="rc-t5__text">The whole series started with a <span class="rc-t7__chip m4-chip"><img class="m4-bug" src="assets/kit/svg/motifs-bug.svg" alt="bug"></span>.</div>');
  tag('f-tag', 599, 680, 'DEMO · T5 glow line + T7 bug chip (B16)');
  js.push(`T.glowLine(tl, '#f-t5', ${sec(602)}, { chipAt: ${sec(650)} });`);
  marks.push(['T5 f0', 602], ['T5 f+4', 606], ['T5 f+8', 610], ['T5 landed', 620], ['T5 chip f+5 (112%)', 655], ['T5 chip settled', 670]);
}
// ---------- G. T6 giant type behind an L6 stand-in (B13) : frames 680-770 ----------
{
  video('g-bg', 'R13.1', 680, 770);
  block('g-dim', 680, 770, 'demo-full demo-dim', 2);
  tag('g-tag', 680, 770, 'DEMO · T6 giant type behind an L6 framed-clip stand-in (B13)');
  block('g-t6', 680, 770, 'rc-t6', 5, '<div class="rc-t6__line">GRAND</div><div class="rc-t6__line">THEFT</div><div class="rc-t6__line">AUTO</div>');
  js.push(`T.giantType(tl, '#g-t6', ${sec(686)});`);
  html.push(`<video id="g-frame" class="clip demo-l6" src="assets/footage/R13.1.mp4" muted playsinline data-start="${S(680)}" data-duration="${D(680, 770)}" data-track-index="4" data-layout-allow-occlusion style="z-index: 8"></video>`);
  marks.push(['T6 5 letters', 694], ['T6 9 letters', 702], ['T6 complete', 712], ['T6 hold', 745]);
}
// ---------- H. T7 inline chip sentence (B2 word timing) : frames 770-830 ----------
{
  const o = 773, w = W('B2'), base = w[10].comp_t;   // "And"
  const t = i => sec(o + T.frame(w[i].comp_t - base));
  video('h-bg', 'R9.1', 770, 830);
  tag('h-tag', 770, 830, 'DEMO · T7 inline chip, words hard cut on the voice (B2 timing)');
  block('h-t7', 773, 830, 'rc-t7', 10, '<span class="rc-t7__w">And</span> <span class="rc-t7__w">that</span> <span class="rc-t7__chip m4-chip"><img class="m4-bug" src="assets/kit/svg/motifs-bug.svg" alt="bug"></span> <span class="rc-t7__w">saved</span> <span class="rc-t7__w">it.</span>');
  js.push(`T.chipSentence(tl, '#h-t7', ${t(10)}, { wordTimes: [${t(10)}, ${t(11)}, ${t(13)}, ${t(14)}], chipAt: ${t(12)} });`);
  const chip = o + T.frame(w[12].comp_t - base);
  marks.push(['T7 "And that"', chip - 1], ['T7 chip f+2', chip + 2], ['T7 chip f+5', chip + 5], ['T7 settled', 820]);
}
// ---------- I. T8 name card + underline + walker slot (B3) : frames 830-890 ----------
{
  video('i-bg', 'R3.8', 830, 890);
  tag('i-tag', 830, 890, 'DEMO · T8 name card on footage, underline + Lemming slot (B3)');
  block('i-t8', 830, 890, 'rc-t8', 10, '<div class="rc-t8__block"><div class="rc-t8__name">DMA Design<span class="rc-t8__underline"><span class="rc-t8__walker"><span class="demo-walker" data-layout-ignore>L</span></span></span></div><div class="rc-t8__role">The studio behind Lemmings</div></div>');
  js.push(`T.nameIn(tl, '#i-t8', ${sec(833)});`);
  js.push(`T.walk(tl, '#i-t8', ${sec(839)}, { duration: 1.4 });`);
  marks.push(['T8 name f+3', 836], ['T8 name settled, walker start', 840], ['T8 walker mid', 860]);
}
// ---------- J. T8 quote card on gray (B6) : frames 890-980 ----------
{
  block('j-card', 890, 980, 'rc-card demo-full', 1);
  tag('j-tag', 890, 980, 'DEMO · T8 quote card on the L5 gray card (B6)', true);
  block('j-t8', 890, 980, 'rc-t8 rc-t8--right rc-on-card', 10, '<div class="rc-t8__block"><div class="rc-t8__quote">“awful… too sim-y.”</div><div class="rc-t8__name">Gary Penn</div><div class="rc-t8__role">DMA DESIGN · GAMASUTRA, 2011</div></div>');
  js.push(`T.quoteType(tl, '#j-t8', ${sec(893)});`);
  js.push(`T.nameIn(tl, '#j-t8', ${sec(905)});`);
  marks.push(['T8 quote 2 chars', 893], ['T8 quote 8 chars', 896], ['T8 quote done', 902], ['T8 name f+3', 908], ['T8 settled', 940]);
}
// ---------- K. T9 highlight on a document stand-in, with an L7-style push-in (B4) : frames 980-1040 ----------
{
  block('k-doc', 980, 1040, 'demo-full demo-docwrap', 1, '<div class="demo-doc" data-layout-ignore><div class="demo-doc-note">STAND-IN for the R4.5 design-document scan (demo only)</div><span class="demo-doc-title">Race\'n\'Chase<span id="k-hl" class="rc-t9-hl" style="left: -12px; right: -12px; top: 10px; bottom: 6px"></span></span></div>');
  tag('k-tag', 980, 1040, 'DEMO · T9 highlight (85%, multiply) swipes left → right while the camera pushes in (B4)', true);
  js.push(`T.highlight(tl, '#k-hl', ${sec(986)});`);
  js.push(`tl.fromTo('#k-doc .demo-doc', { scale: 1 }, { scale: 1.18, duration: ${sec(60)}, ease: 'none', immediateRender: true }, ${sec(980)});  // L7 push-in stand-in`);
  marks.push(['T9 hl f+2', 988], ['T9 hl f+4', 990], ['T9 hl settled', 1000]);
}
// ---------- L. T9 label next to the cabinet (B15) : frames 1040-1100 ----------
{
  video('l-bg', 'R15.3', 1040, 1100);
  tag('l-tag', 1040, 1100, 'DEMO · T9 label (B15)');
  block('l-t9', 1043, 1100, 'rc-t9', 10, '<span class="rc-t9__label">Race and Chase</span>', ' --rc-x: 1180px; --rc-y: 700px;');
  js.push(`T.label(tl, '#l-t9', ${sec(1046)});`);
  marks.push(['T9 label f+1', 1047], ['T9 label f+2', 1048], ['T9 label settled', 1060]);
}
// ---------- M. T10 glitch word (B8), then B17's "now?" : frames 1100-1190 ----------
{
  block('m-black', 1100, 1190, 'rc-ink demo-full', 1);
  tag('m-tag', 1100, 1118, 'DEMO · T10 glitch word (B8)');
  block('m-t10', 1100, 1118, 'rc-t10', 10, '<span class="rc-t10__word">breaks.</span>');
  js.push(`T.glitch(tl, '#m-t10', ${sec(1100)});`);
  tag('m2-tag', 1118, 1190, 'DEMO · B17: T2 "chasing who / now?" → T10 on "now?" at the final hit, then black');
  block('m2-t2', 1118, 1160, 'rc-t2', 10, '<div class="rc-t2__row"><span class="rc-t2__lead">chasing who</span><span class="rc-t2__key">now?</span></div>');
  js.push(`T.punchPair(tl, '#m2-t2', ${sec(1124)});`);
  block('m2-t10', 1160, 1166, 'rc-t10', 10, '<span class="rc-t10__word">now?</span>');
  js.push(`T.glitch(tl, '#m2-t10', ${sec(1160)}, { settle: false });`);
  for (let k = 0; k <= 6; k++) marks.push([`T10 f+${k}`, 1100 + k]);
  marks.push(['T10 hold', 1112], ['B17 T2 settled', 1150], ['B17 T10 f+0', 1160], ['B17 T10 f+3', 1163], ['B17 black', 1170]);
}
const TOTAL = 1190;

const page = `<!doctype html>
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
      /* demo-only scaffolding (stand-ins for screens owned by other kit areas; not part of the type kit) */
      /* stand-in clips are shown 2.74x, cropped to a label-free patch of their moving pattern, so text stays readable */
      .demo-bg { position: absolute; left: -165px; top: -1755px; width: 5266px; height: 2962px; object-fit: cover; }
      .demo-full { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
      .demo-bar { position: absolute; left: 0; width: 1920px; height: 138px; background: var(--ink-black); }
      .demo-dim { background: color-mix(in srgb, var(--ink-black) 40%, transparent); }
      .demo-l6 { position: absolute; left: 365px; top: 205px; width: 1190px; height: 670px; object-fit: cover; box-sizing: border-box; border: 2px solid var(--white); }
      .demo-tag { position: absolute; left: 96px; top: 54px; height: 28px; font-family: var(--sans); font-weight: 400; font-size: 20px; line-height: 28px; letter-spacing: 0.04em; color: var(--white); opacity: 0.75; white-space: nowrap; text-shadow: var(--text-shadow); }
      .demo-tag.rc-on-card { color: var(--card-ink); text-shadow: none; }
      .demo-walker { display: inline-block; width: 18px; height: 26px; box-sizing: border-box; border: 2px solid currentColor; font: 700 14px/22px var(--sans); text-align: center; }
      .demo-docwrap { background: var(--card-gray); overflow: hidden; }
      .demo-doc { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 960px 540px; }
      .demo-doc-note { position: absolute; left: 0; width: 1920px; top: 640px; text-align: center; font: 500 24px/30px var(--sans); color: var(--card-ink); opacity: 0.6; }
      .demo-doc-title { position: absolute; left: 0; right: 0; margin: 0 auto; width: max-content; top: 470px; font: 700 96px/110px var(--sans); color: var(--card-ink); }
    </style>
  </head>
  <body>
    <!-- RC kit TYPE demo: every T-style (T1-T10) in sequence, built exactly as a beat would (assets/kit + RCK.type).
         Footage = labelled stand-ins from 04_Broll/_placeholders. Rebuild: node tools/gen_demo.cjs; measure: node tools/measure_type.cjs. -->
    <div id="root" data-composition-id="type-demo" data-start="0" data-duration="${(TOTAL / 30).toFixed(4)}" data-width="1920" data-height="1080">
      ${html.join('\n      ')}
    </div>
    <script src="assets/kit/type.js"></script>
    <script src="assets/kit/motifs.js"></script>
    <script src="assets/kit/transitions.js"></script>
    <script src="assets/kit/screens.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const T = RCK.type;
      ${js.join('\n      ')}
      window.__timelines["type-demo"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(OUT, page);
fs.writeFileSync(__dirname + '/marks.json', JSON.stringify(marks.map(([l, f]) => ({ label: l, frame: f, t: +(f / 30).toFixed(6) })), null, 1));
console.log('wrote', OUT, html.length, 'timed elements,', js.length, 'timeline calls,', marks.length, 'marks');
