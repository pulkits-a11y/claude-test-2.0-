// Builds _demo-v03/index.html: the REVISION_v03 kit items (caption lockups, dark cards, star glitch-in, 104% push), used
// exactly as a beat builder would. Word times = the v02 beat map (timing/beat_map.json), shifted to this demo's timeline.
// Run from _demo-v03:  rm -rf assets/kit && cp -r ../_kit assets/kit && node tools/gen_demo.cjs
globalThis.window = globalThis;
require('../assets/kit/type.js');
const fs = require('fs');
const T = RCK.type;
const BM = require('../../../timing/beat_map.json');
const words = (id, shiftF) => BM.beats.find(b => b.id === id).words.map(w => ({ text: w.text, comp_t: w.comp_t + shiftF / 30, comp_end_t: w.comp_end_t + shiftF / 30 }));
const A = f => T.attrF(f), D = (f0, f1) => T.durF(f0, f1), S = f => (f / 30).toFixed(6);
const html = [], js = [], report = [];
const tag = (id, f0, f1, text) => html.push(`<div id="${id}" class="clip demo-tag" data-start="${A(f0)}" data-duration="${D(f0, f1)}" data-track-index="30" style="z-index: 90">${text}</div>`);
const vid = (id, src, f0, f1, extra) => `<video id="${id}" class="clip demo-fill" src="assets/footage/${src}" muted playsinline data-start="${A(f0)}" data-duration="${D(f0, f1)}"${extra || ''}></video>`;
const plan = (label, w, specs, o) => { const p = T.lockupPlan(w, specs, o); report.push('== ' + label + '\n' + T.lockupReport(p)); return p; };

/* ---------------- A: B15 lockups over footage (ref 1): solo line, 3-line lockup with a starred keyword, 3-line, key only ---------------- */
{
  const W = words('B15', 0);
  html.push(`<div id="a-cam" class="rc-cam" style="z-index: 1">${vid('a-v', 'R3.1.mp4', 0, 170)}</div>`);
  html.push(`<div id="a-dim" class="clip demo-fill demo-dim" data-start="${A(0)}" data-duration="${D(0, 170)}" style="z-index: 2"></div>`);
  const p = plan('A (B15)', W, ["Don't believe me?", 'Open [GTA Online]* and buy an arcade.', 'One of the [machines] is called', '[Race and Chase.]*'], { from: 0, end: 170 / 30 });
  html.push(T.lockups(p, null, { idPrefix: 'a-lk', z: 40, track: 20 }));
  js.push(`// A (B15): the held shot pushes 100 -> 104% (v03 default, sine.inOut)
      C.push(tl, '#a-cam', 0, { until: ${S(170)} });`);
  tag('a-tag', 0, 170, 'v03 · B15 · caption lockups (ref 1): words hard-cut on their onset · [GTA Online]* and [Race and Chase.]* pop + blur in · push 100→104%');
}

/* ---------------- B: B3 year card, dark (T3 "It's 1995") ---------------- */
{
  const W = words('B3', 148);   // It's@175, 1995@182
  const f0 = 170, f1 = 232;
  html.push(`<div id="b-t3" class="clip rc-t3" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 1"><div class="rc-t3__block"><div class="rc-t3__in">It's</div><div class="rc-t3__year"><span class="rc-t3__num">1995</span></div></div></div>`);
  js.push(`// B (B3): dark year card; the digits roll in from "1995" (f${Math.round(W[3].comp_t * 30)}), then the 104% push
      T.yearCard(tl, '#b-t3', ${W[3].comp_t.toFixed(4)}, { pushUntil: ${S(f1)} });`);
  tag('b-tag', f0, f1, 'v03 · B3 · T3 year card, dark (ref 3): near-black + charcoal lift, white digits with the soft glow');
}

/* ---------------- C: B4 dark calendar card + lockup "planned to take [18 months.]" ---------------- */
{
  const W = words('B4', 186);   // planned@245
  const f0 = 232, f1 = 330;
  html.push(`<div id="c-card" class="clip rc-card rc-full" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 1"></div>`);
  html.push(`<div id="c-cal" class="clip m3-cal" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 10"></div>`);
  const p = plan('C (B4)', W, ['planned to take [18 months.]'], { from: 7, loose: true, end: f1 / 30, y: 330 });
  html.push(T.lockups(p, null, { idPrefix: 'c-lk', z: 40, track: 20, y: 330 }));
  js.push(`// C (B4): 18 light squares fill 2f apart from "planned" (hard fills) on the dark card
      M.calendarFill(tl, '#c-cal', ${S(p.lockups[0].startFrame)}, { slots: 18, filled: 0, y: 560 });`);
  tag('c-tag', f0, f1, 'v03 · B4 · dark calendar card (light-grey squares) + lockup "planned to take / 18 months." (no pop: hard cuts)');
}

/* ---------------- D: B12 calendar 18 -> 30 on the dark card, red overrun squares, counter, lockup with a starred keyword ---------------- */
{
  const W = words('B12', 324);  // turn@380, thirty.@395
  const f0 = 330, f1 = 425;
  html.push(`<div id="d-card" class="clip rc-card rc-full" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 1"></div>`);
  html.push(`<div id="d-cal" class="clip m3-cal" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 10"></div>`);
  const p = plan('D (B12)', W, ['turn into [thirty.]*'], { from: 5, end: f1 / 30, y: 250 });
  html.push(T.lockups(p, null, { idPrefix: 'd-lk', z: 40, track: 20, y: 250 }));
  js.push(`// D (B12): calendar opening animation, 12 red squares 2f apart, counter 18 -> 30 landing on "thirty."
      M.calendarInit('#d-cal', { slots: 18, filled: 18, counter: 18, y: 430 });
      M.calendarIn(tl, '#d-cal', ${S(333)});
      M.calendarExtend(tl, '#d-cal', 0, { to: 30, landAt: ${W[7].comp_t.toFixed(4)} });`);
  tag('d-tag', f0, f1, 'v03 · B12 · dark calendar: light squares, siren-red overrun, glowing counter · lockup "turn into / thirty.*"');
}

/* ---------------- E: B6 dark quote card (L5 ground + T8), the quote words pop + blur in on their frames ---------------- */
{
  const W = words('B6', 328);   // “awful…@440 too@457 sim-y.”@463
  const f0 = 425, f1 = 520;
  html.push(`<div id="e-card" class="clip rc-l5__ground" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 1"></div>`);
  html.push(`<div id="e-t8" class="clip rc-t8 rc-on-card" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 10"><div class="rc-t8__block"><div class="rc-t8__quote">“awful…<br>too sim-y.”</div><div class="rc-t8__name">Gary Penn</div><div class="rc-t8__role">DMA DESIGN · GAMASUTRA, 2011</div></div></div>`);
  js.push(`// E (B6): the quote's words pop + blur in on their spoken frames (wordPops), name + role fade in after
      T.wordPops(tl, '#e-t8 .rc-t8__quote', [${W.slice(11, 14).map(w => w.comp_t.toFixed(4)).join(', ')}]);
      T.nameIn(tl, '#e-t8', ${S(475)});`);
  tag('e-tag', f0, f1, 'v03 · B6 · T8 quote on the dark card, words pop + blur in (wordPops) · white + glow');
}

/* ---------------- F: B14 hero stars glitch in (RGB split + slice jitter + flicker), lockup below them (y option) ---------------- */
{
  const W = words('B14', 431);  // The@528 wanted@533 stars.@545
  const f0 = 520, f1 = 600;
  html.push(vid('f-v', 'R1.2.mp4', f0, f1, ' data-media-start="0.6000"'));
  html.push(`<div id="f-dim" class="clip demo-fill demo-dim" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 2"></div>`);
  html.push(`<div id="f-stars" class="clip m1-stars" data-preset="hero" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 10"></div>`);
  const p = plan('F (B14)', W, ['The [wanted stars.]*'], { from: 9, end: f1 / 30, y: 800 });
  html.push(T.lockups(p, null, { idPrefix: 'f-lk', z: 40, track: 20, y: 800 }));
  js.push(`// F (B14): six hero stars glitch in 3f apart (6f each), from "The"
      M.starsGlitchIn(tl, '#f-stars', ${W[9].comp_t.toFixed(4)});`);
  tag('f-tag', f0, f1, 'v03 · B14 · M1 stars glitch in (starsGlitchIn): RGB split + slice jitter + flicker, 6f each, 3f apart');
}

/* ---------------- G: B13 "Until finally," solo lockup on a dark card (ref 3), then the title, each word pops ---------------- */
{
  const W1 = words('B13', 598);  // Until@605 finally,@614
  const W2 = words('B13', 515);  // Grand@645 Theft@651 Auto.@661
  const f0 = 600, fm = 640, f1 = 700;
  html.push(`<div id="g-card" class="clip rc-card rc-full" data-start="${A(f0)}" data-duration="${D(f0, fm)}" style="z-index: 1"></div>`);
  const p1 = plan('G1 (B13 card)', W1, ['Until finally,'], { from: 0, start: f0 / 30, end: fm / 30, card: true });
  html.push(T.lockups(p1, null, { idPrefix: 'g-lk', z: 40, track: 20 }));
  html.push(vid('g-v', 'R13.1.mp4', fm, f1));
  html.push(`<div id="g-dim" class="clip demo-fill demo-dim" data-start="${A(fm)}" data-duration="${D(fm, f1)}" style="z-index: 2"></div>`);
  const p2 = plan('G2 (B13 title)', W2, ['[Grand* Theft* Auto.*]'], { from: 11, start: 643 / 30, end: f1 / 30 });
  html.push(T.lockups(p2, null, { idPrefix: 'g-title', z: 40, track: 21 }));
  tag('g-tag', f0, f1, 'v03 · B13 · "Until finally," = solo lockup on the dark card (ref 3) · title [Grand* Theft* Auto.*]: each word pops on its frame');
}

/* ---------------- H: T9 highlight on a dark (inverted) document page + the dark error box ---------------- */
{
  const f0 = 700, f1 = 760;
  html.push(`<div id="h-bg" class="clip rc-card rc-full" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 1"></div>`);
  html.push(`<div id="h-doc" class="clip demo-doc" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 5">
  <div class="demo-doc__h">RACE'N'CHASE</div>
  <div class="demo-doc__p">Design document, March 1995. The player drives a police car</div>
  <div class="demo-doc__p">through three cities, chasing criminals before they escape.</div>
  <div class="demo-doc__p">Planned development time: <span id="h-key">eighteen months</span>.</div>
  <div id="h-hl" class="rc-t9-hl" style="left: 486px; top: 278px; width: 270px; height: 44px"></div>
</div>`);
  html.push(`<div id="h-err" class="clip m-errbox" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="left: 1190px; top: 640px; z-index: 20"></div>`);
  js.push(`// H: highlighter on the dark page (screen, 50%) + the dark error box
      T.highlight(tl, '#h-hl', ${S(708)});
      M.errorBoxPop(tl, '#h-err', ${S(720)});`);
  tag('h-tag', f0, f1, 'v03 · T9 highlight on a dark (inverted) page: yellow, screen 50% · Windows 95 error box, dark');
}

/* ---------------- I: B1 L4 grid with ink tiles (note 8): dark tiles, the two centre tiles clear to the footage ---------------- */
{
  const f0 = 760, f1 = 800;
  html.push(`<div id="i-frost" class="rc-l4 rc-l4--ink" style="z-index: 1">
  <div class="rc-l4__plate">${vid('i-v', 'R1.2.mp4', f0, f1, ' data-media-start="2.0000"').replace('class="clip demo-fill"', 'class="clip"')}</div>
  <div id="i-tiles" class="clip rc-l4__tiles" data-start="${A(f0)}" data-duration="${D(f0, f1)}"></div>
</div>`);
  js.push(`// I (B1): ink tiles; "Why" / "does" clear the two centre tiles (3f easeOutCubic each)
      S.frostClear(tl, '#i-frost', [${S(764)}, ${S(772)}], { order: [5, 6] });
      C.push(tl, '#i-frost .rc-l4__plate', ${S(f0)}, { until: ${S(f1)} });`);
  tag('i-tag', f0, f1, 'v03 · B1 · L4 grid with rc-l4--ink: the blurred tiles are card ink; the two centre tiles clear to the footage');
}

/* ---------------- J: descender fix: keywords with descenders / a comma push the tail row down (collision guard) ---------------- */
{
  const f0 = 800, f1 = 910;
  html.push(`<div id="j-cam" class="rc-cam" style="z-index: 1">${vid('j-v', 'R3.1.mp4', f0, f1, ' data-media-start="1.0000"')}</div>`);
  html.push(`<div id="j-dim" class="clip demo-fill demo-dim" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="z-index: 2"></div>`);
  const pa = plan('J1 (B1)', words('B1', 798), ['[Why] does'], { from: 0, end: 830 / 30 });
  const pb = plan('J2 (B2)', words('B2', 704), ['And that [bug]* saved it.'], { from: 10, end: 875 / 30 });
  const pc = plan('J3 (B3)', words('B3', 819), ['[Dundee,] Scotland.'], { from: 5, end: f1 / 30 });
  html.push(T.lockups(pa, null, { idPrefix: 'j-lka', z: 40, track: 20 }));
  html.push(T.lockups(pb, null, { idPrefix: 'j-lkb', z: 40, track: 20 }));
  html.push(T.lockups(pc, null, { idPrefix: 'j-lkc', z: 40, track: 20 }));
  js.push(`C.push(tl, '#j-cam', ${S(f0)}, { until: ${S(f1)} });`);
  tag('j-tag', f0, f1, 'v03 fix · tail rows clear the keyword descenders (g j p q y, comma) by 8 px: [Why] does · And that [bug]* saved it. · [Dundee,] Scotland.');
}

/* ---------------- K: v04 additions: glow flicker (lockup word, T3 year, "Nov 1997"), card scanlines, B9 strip glow flash ---------------- */
{
  // K1 (B2): lockup "Because back in [1995,]" over footage, the keyword (not starred) glow-flickers on its frame
  const W1 = words('B2', 908);  // Because@915 back@927 in@935 1995,@938
  html.push(vid('k1-v', 'R1.2.mp4', 910, 965, ' data-media-start="3.0000"'));
  html.push(`<div id="k1-dim" class="clip demo-fill demo-dim" data-start="${A(910)}" data-duration="${D(910, 965)}" style="z-index: 2"></div>`);
  const p1 = plan('K1 (B2)', W1, ['Because back in [1995,]'], { from: 0, end: 965 / 30 });
  html.push(T.lockups(p1, null, { idPrefix: 'k1-lk', z: 40, track: 20 }));
  js.push(`// K1: glow flicker on the keyword span "1995," (seeded pattern, 10f, settles in 4f)
      T.glowFlicker(tl, '#k1-lk-1 .rc-lk__row--key .rc-lw', ${W1[3].comp_t.toFixed(4)});`);
  tag('k1-tag', 910, 965, 'v04 · B2 · T.glowFlicker on the lockup keyword "1995," (neon catching: stepped flare / on / half / off, then a steady glow)');

  // K2 (B3): T3 "It's 1995" dark card with the built-in scanlines; the digits roll in AND the year glow-flickers
  const W2 = words('B3', 943);  // It's@970 1995@977
  html.push(`<div id="k2-t3" class="clip rc-t3" data-start="${A(965)}" data-duration="${D(965, 1030)}" style="z-index: 1"><div class="rc-t3__block"><div class="rc-t3__in">It's</div><div class="rc-t3__year"><span class="rc-t3__num">1995</span></div></div></div>`);
  js.push(`// K2: year card: digits roll from "1995" + glow flicker on the year line (the "It's" line keeps its steady glow)
      T.yearCard(tl, '#k2-t3', ${W2[3].comp_t.toFixed(4)}, { pushUntil: ${S(1030)} });
      T.glowFlicker(tl, '#k2-t3 .rc-t3__year', ${W2[3].comp_t.toFixed(4)}, { frames: 11 });`);
  tag('k2-tag', 965, 1030, 'v04 · B3 · T3 "It\'s 1995": built-in card scanlines (9 px, 20%) + glowFlicker on the year');

  // K3 (B13): T3 "In / Nov 1997" with the flicker on "Nov 1997"
  const W3 = words('B13', 1002);  // in@1035 November@1038 1997,@1053
  html.push(`<div id="k3-t3" class="clip rc-t3" data-start="${A(1030)}" data-duration="${D(1030, 1090)}" style="z-index: 1"><div class="rc-t3__block"><div class="rc-t3__in">In</div><div class="rc-t3__year"><span class="rc-t3__num">Nov 1997</span></div></div></div>`);
  js.push(`// K3: "Nov 1997" rolls in from "November" with the glow flicker
      T.yearCard(tl, '#k3-t3', ${W3[3].comp_t.toFixed(4)}, { pushUntil: ${S(1090)} });
      T.glowFlicker(tl, '#k3-t3 .rc-t3__year', ${W3[3].comp_t.toFixed(4)}, { frames: 10, seed: 15 });`);
  tag('k3-tag', 1030, 1090, 'v04 · B13 · T3 "Nov 1997" with glowFlicker (seed 15)');

  // K4 (B9): three L3 strips pop in (kit gridPop, punch 115%) each with a glow flash
  const sv = (src, f0, ms) => `<video id="k4-v${f0}" class="clip" src="assets/footage/${src}" muted playsinline data-start="${A(f0)}" data-duration="${D(f0, 1150)}" data-media-start="${ms}"></video>`;
  html.push(`<div id="k4-grid" class="rc-l3 rc-l3--strips" style="z-index: 2">
  <div id="k4-ground" class="clip rc-l3__ground" data-start="${A(1090)}" data-duration="${D(1090, 1150)}"></div>
  <div id="k4-s1" class="rc-l3__cell"><div class="rc-l3__media">${sv('R1.2.mp4', 1095, '1.0000')}</div></div>
  <div id="k4-s2" class="rc-l3__cell"><div class="rc-l3__media">${sv('R3.1.mp4', 1110, '0.5000')}</div></div>
  <div id="k4-s3" class="rc-l3__cell"><div class="rc-l3__media">${sv('R13.1.mp4', 1125, '0.5000')}</div></div>
</div>`);
  js.push(`// K4: each strip pops (4f) with a glow flash (peak +2f, gone 6f later, eased out)
      [1095, 1110, 1125].forEach((f, i) => { S.gridPop(tl, '#k4-s' + (i + 1), f / 30, { punch: 1.15 }); S.glowFlash(tl, '#k4-s' + (i + 1), f / 30); });`);
  tag('k4-tag', 1090, 1150, 'v04 · B9 · L3 strips: S.gridPop + S.glowFlash (white bloom + edge glow, 2f in / 6f out, power2.out)');
}

const END = 1150;
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
      .demo-dim { background: color-mix(in srgb, var(--ink-black) 35%, transparent); }
      .demo-tag { position: absolute; left: 96px; top: 20px; height: 26px; font-family: var(--sans); font-size: 19px; line-height: 26px; letter-spacing: 0.02em; color: var(--white); opacity: 0.75; white-space: nowrap; text-shadow: var(--text-shadow); }
      .demo-doc { position: absolute; left: 300px; top: 140px; width: 1320px; height: 520px; box-sizing: border-box; padding: 60px 80px; background: color-mix(in srgb, var(--white) 6%, var(--ink-black)); color: var(--light-gray); font-family: var(--sans); }
      .demo-doc__h { font-size: 56px; line-height: 80px; margin-bottom: 20px; }
      .demo-doc__p { font-size: 36px; line-height: 56px; opacity: 0.9; }
    </style>
  </head>
  <body>
    <!-- RC kit v03 demo (REVISION_v03 notes 5, 11, 12, 13, 16, 17), generated by tools/gen_demo.cjs from the kit itself.
         Word times: timing/beat_map.json, shifted per section. Footage: copies of the beats' working clips. -->
    <div id="root" data-composition-id="kit-v03-demo" data-start="0" data-duration="${(END / 30).toFixed(7)}" data-width="1920" data-height="1080">
${html.join('\n')}
    </div>
    <script src="assets/kit/type.js"></script>
    <script src="assets/kit/motifs.js"></script>
    <script src="assets/kit/transitions.js"></script>
    <script src="assets/kit/screens.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const T = RCK.type, M = RCK.motifs, X = RCK.transitions, C = RCK.cam, S = RCK.screens;
      // every lockup (class rc-lk): words hard-cut on their onset frame, starred words pop + blur in
      T.lockupsWire(tl);
      ${js.join('\n      ')}
      tl.set({}, {}, ${(END / 30).toFixed(6)});
      window.__timelines["kit-v03-demo"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(__dirname + '/../index.html', out);
fs.writeFileSync(__dirname + '/../review/lockups.txt', report.join('\n') + '\n');
console.log('wrote index.html (' + END + ' frames)');
console.log(report.join('\n'));
