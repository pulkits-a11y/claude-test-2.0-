// Builds _demo-v05/index.html: every v05 kit item (REVISION_v05 G1-G8: caption tiers + word entry, RCK.fx motion-graphics
// kit), used exactly as a beat builder would. Word times = timing/beat_map.json (v05), shifted per section.
// Run from _demo-v05:  rm -rf assets/kit && cp -r ../_kit assets/kit && node tools/gen_demo.cjs && bash tools/snap.sh
globalThis.window = globalThis;
require('../assets/kit/type.js');
require('../assets/kit/motifs.js');
const fs = require('fs');
const T = RCK.type, FX = RCK.fx;
const BM = require('../../../timing/beat_map.json');
const words = (id, shiftF) => BM.beats.find(b => b.id === id).words.map(w => ({ text: w.text, comp_t: w.comp_t + shiftF / 30, comp_end_t: w.comp_end_t + shiftF / 30 }));
const A = f => T.attrF(f), D = (f0, f1) => T.durF(f0, f1), S = f => (f / 30).toFixed(6);
const html = [], js = [], report = [];
const tag = (id, f0, f1, text) => html.push(`<div id="${id}" class="clip demo-tag" data-start="${A(f0)}" data-duration="${D(f0, f1)}" data-track-index="30" style="z-index: 95">${text}</div>`);
const vid = (id, src, f0, f1, extra, cls) => `<video id="${id}" class="clip ${cls == null ? 'demo-fill' : cls}" src="assets/footage/${src}" muted playsinline data-start="${A(f0)}" data-duration="${D(f0, f1)}"${extra || ''}></video>`;
const host = (id, f0, f1, cls, style) => `<div id="${id}" class="clip fx-host${cls ? ' ' + cls : ''}" data-start="${A(f0)}" data-duration="${D(f0, f1)}" style="${style || ''}"></div>`;
const plan = (label, w, specs, o) => { const p = T.lockupPlan(w, specs, o); report.push('== ' + label + '\n' + T.lockupReport(p)); return p; };
const BLUR = ` data-color-grading='{"preset":null,"intensity":1,"effects":{"blur":0.01}}' style="--hf-color-grading-blur: 0"`;

/* A (f0-55): B1 "[[Why]] does" hero (Coolvetica Italic 450) + "every [GTA,]" two tiers: every word's v05 entry */
{
  const W = words('B1', 0);
  html.push(`<div id="a-cam" class="rc-cam" style="z-index: 1">${vid('a-v', 'R1.2.mp4', 0, 55)}</div>`);
  const p = plan('A (B1)', W, [{ s: '[[Why]] does', hero: 450 }, 'every [GTA,]'], { from: 0, end: 55 / 30 });
  html.push(T.lockups(p, null, { idPrefix: 'a-lk', z: 40, track: 20 }));
  js.push(`C.push(tl, '#a-cam', 0, { until: ${S(55)} });`);
  tag('a-tag', 0, 55, 'v05 · B1 · hero [[Why]] 450 + tier A "does" · "every [GTA,]" setup over key · every word: pink, 112%, blur 9 → white');
}
/* B (f55-130): B2 "Because back in [[1995,]]" (Playfair Black 480) + glowFlicker on 1995 + VCR timestamp */
{
  const W = words('B2', 55);
  html.push(vid('b-v', 'R3.8.mp4', 55, 130, ' data-media-start="0.3000"'));
  html.push(host('b-vcr', 55, 130, '', 'z-index: 30'));
  const p = plan('B (B2)', W, ['Because back in [[1995,]]'], { from: 0, end: 130 / 30, hero: 480 });
  html.push(T.lockups(p, null, { idPrefix: 'b-lk', z: 40, track: 20 }));
  js.push(`FX.vcr('#b-vcr', { text: 'MAR 22 1995' });
      T.glowFlicker(tl, '#b-lk-1 .rc-lk__row--num .rc-lw', ${W[3].comp_t.toFixed(4)});`);
  tag('b-tag', 55, 130, 'v05 · B2 · hero number [[1995,]] Playfair Black 480 + glowFlicker layered on the entry · VCR timestamp (VT323 42)');
}
/* C (f130-250): B2 "broke." + error window pop + cascade, "And that [bug] saved it." with an RGB split that never settles,
   snap shut, 1-frame flash, pill types "THAT BUG SAVED IT", exits with the pink pixel glitch */
{
  const W = words('B2', 29);   // broke.@130 And@160 that@171 bug@176 saved@183 it.@191
  html.push(`<div id="c-cam" class="rc-cam" style="z-index: 1">${vid('c-v', 'R9.1.mp4', 130, 250)}</div>`);
  html.push(host('c-err', 130, 215, '', 'z-index: 20; --x: 960px; --y: 470px'));
  const p = plan('C (B2)', W, [{ s: '[[broke.]]', hero: 390, y: 800 }, 'And that [bug] saved it.'], { from: 9, end: 205 / 30 });
  html.push(T.lockups(p, null, { idPrefix: 'c-lk', z: 40, track: 20 }));
  html.push(host('c-flash', 200, 210, '', 'z-index: 60'));
  html.push(`<div id="c-pill" class="clip fx-host fx-pill" data-start="${A(212)}" data-duration="${D(212, 250)}" style="z-index: 45; --x: 960px; --y: 540px">THAT BUG SAVED IT</div>`);
  js.push(`FX.errorWindow('#c-err', { title: "Race'n'Chase", scale: 1.8 });
      FX.errorPop(tl, '#c-err', ${S(130)});
      FX.errorCascade(tl, '#c-err', ${S(136)}, { count: 10, dx: 36, dy: 27, stepF: 2 });
      FX.rgbSplit(tl, '#c-lk-2 .rc-lk__row--key .rc-lw', ${W[12].comp_t.toFixed(4)}, { px: 6, settle: 2 });
      FX.errorSnapShut(tl, '#c-err', ${S(196)}, { frames: 3, stepF: 0.5 });
      FX.flash(tl, '#c-flash', ${S(205)}, { opacity: 0.9 });
      FX.pill(tl, '#c-pill', ${S(212)});
      FX.pillOut(tl, '#c-pill', ${S(242)});`);
  tag('c-tag', 130, 250, 'v05 · B2 · errorPop + errorCascade (10, +36/+27, 2f) · [[broke.]] · [bug] RGB split never settles · snapShut · flash · pill → pixel-glitch out');
}
/* D (f250-330): B4 paper page tilted 4°, push 100 -> 115%, pink highlighter sweep, yellow circle, CANNED stamp + flash + shake */
{
  html.push(`<div id="d-cam" class="rc-cam" style="z-index: 1"><div id="d-page" class="clip fx-paper demo-page" data-start="${A(250)}" data-duration="${D(250, 330)}">
  <div class="demo-page__t">Race'n'Chase</div><div class="demo-page__t2">Game Design</div><div class="demo-page__d">Version 1.00 · March 22, 1995</div>
  <div class="demo-page__p">The player drives a police car through three cities, chasing criminals before they escape.</div>
  <div id="d-hl" class="fx-hl" style="left: 92px; top: 66px; width: 560px; height: 104px"></div></div></div>`);
  html.push(host('d-ann', 250, 330, '', 'z-index: 20'));
  html.push(host('d-stamp', 290, 330, '', 'z-index: 30; --x: 1060px; --y: 640px'));
  html.push(host('d-flash', 290, 300, '', 'z-index: 60'));
  js.push(`C.push(tl, '#d-cam', ${S(250)}, { until: ${S(330)}, to: 1.15 });
      FX.highlight(tl, '#d-hl', ${S(258)});
      FX.annotate(tl, '#d-ann', ${S(270)}, { type: 'circle', rect: [835, 618, 520, 64], seed: 3 });
      FX.stamp(tl, '#d-stamp', ${S(290)}, { text: 'CANNED', flash: '#d-flash', shakeTarget: '#d-cam' });`);
  tag('d-tag', 250, 330, 'v05 · B4/B7 · paper page (fx-paper) + highlight sweep (multiply, 8f) + annotate circle + stamp CANNED (180→95→100 / 5f, flash, shake 6 px)');
}
/* E (f330-420): card insert (4:3 archival, blurred darkened copy behind, 3° tilt) + annotate arrow + label; dark card v05 */
{
  html.push(FX.cardInsertHTML({ id: 'e-card', src: 'assets/footage/R3.8.mp4', start: 330 / 30, dur: 50 / 30, mediaStart: 0.5, tilt: 3, w: 1040, h: 780, z: 1 }));
  html.push(host('e-ann', 330, 380, '', 'z-index: 20'));
  html.push(FX.darkCardHTML({ id: 'e-dark', start: 380 / 30, dur: 40 / 30, src: 'assets/footage/R3.1.mp4', mediaStart: 0.5, opacity: 0.2, z: 2 }));
  const W = words('B13', 375);   // Until@382 finally,@391
  const p = plan('E (B13)', W, ['Until finally,'], { from: 0, start: 380 / 30, end: 420 / 30, card: true });
  html.push(T.lockups(p, null, { idPrefix: 'e-lk', z: 40, track: 20 }));
  js.push(`C.push(tl, '#e-card .fx-card__cam', ${S(330)}, { until: ${S(380)}, to: 1.06 });
      FX.annotate(tl, '#e-ann', ${S(338)}, { type: 'arrow', from: [560, 930], to: [760, 640], label: 'the managers', labelAt: [380, 950], seed: 8 });`);
  tag('e-tag', 330, 420, 'v05 · card insert (white 15 px border, 3° tilt, bg = same clip 130% blur 60 px −50%) + arrow · then the v05 dark card (#0E0E10 + loop 20% + grain + lines)');
}
/* F (f420-500): name pill lower-left + quote tier lockup (Playfair Italic) */
{
  const W = words('B6', 318);   // “awful…@430 too@447 sim-y.”@453
  html.push(vid('f-v', 'R3.8.mp4', 420, 500, ' data-media-start="1.0000"'));
  html.push(`<div id="f-name" class="clip fx-host fx-pill fx-pill--name" data-start="${A(422)}" data-duration="${D(422, 500)}" data-line2="DMA Design · Gamasutra, 2011" style="z-index: 45">GARY PENN</div>`);
  const p = plan('F (B6)', W, [{ s: '[“awful…] too sim-y.”', tier: 'quote' }], { from: 11, end: 500 / 30, loose: true });
  html.push(T.lockups(p, null, { idPrefix: 'f-lk', z: 40, track: 20 }));
  js.push(`FX.pill(tl, '#f-name', ${S(424)});`);
  tag('f-tag', 420, 500, 'v05 · B6 · name pill (Montserrat 45 / 30, typed) · quote tier: Playfair Display Italic 135 / 105');
}
/* G (f500-560): "it's [dull.]#" (no entry, Arimo grey 180) then "from the [cops?]~" (siren entry) */
{
  const W1 = words('B6', 462);   // it's@500 dull.@508
  const W2 = words('B1', 405);   // from@519 the@525 cops?@530
  html.push(vid('g-v', 'R1.2.mp4', 500, 560, ' data-media-start="2.0000"'));
  const p1 = plan('G1 (B6)', W1, ["it's [dull.]#"], { from: 4, end: 519 / 30 });
  html.push(T.lockups(p1, null, { idPrefix: 'g-lk', z: 40, track: 20 }));
  const p2 = plan('G2 (B1)', W2, [{ s: 'from the [cops?]~', keySize: 240, y: 640 }], { from: 10, end: 560 / 30 });
  html.push(T.lockups(p2, null, { idPrefix: 'g-lk2', z: 40, track: 20 }));
  tag('g-tag', 500, 560, 'v05 · "dull." = no entry, Arimo grey #8A8A8A 180 · "cops?" siren entry (#E3262B / #2E6BFF every 2f for 8f)');
}
/* H (f560-650): logo slam (same function for B1 / B13 / B17) + flash-star + flash + shake, then a whip-zoom into the next shot */
{
  html.push(`<div id="h-cam" class="rc-cam" style="z-index: 1">${vid('h-v', 'R1.2.mp4', 560, 616, ' data-media-start="0.5000"' + BLUR)}</div>`);
  html.push(`<div id="h-cam2" class="rc-cam" style="z-index: 1">${vid('h-v2', 'R13.1.mp4', 616, 650, BLUR)}</div>`);
  html.push(host('h-star', 560, 600, '', 'z-index: 18; --x: 960px; --y: 520px'));
  html.push(`<div id="h-logo-host" class="clip fx-host" data-start="${A(560)}" data-duration="${D(560, 600)}" style="z-index: 20"><div id="h-logo" class="demo-logo"><img src="assets/footage/gta6-logo.png" alt=""></div></div>`);
  html.push(host('h-flash', 560, 600, '', 'z-index: 60'));
  js.push(`FX.logoSlam(tl, '#h-logo', ${S(570)}, { from: 150, overshoot: 94, frames: 6, flash: '#h-flash', star: '#h-star', shakeTarget: '#h-cam', shakePx: 9, shakeF: 6 });
      FX.whipZoom(tl, '#h-cam', ${S(608)}, { to: 4, frames: 8, origin: '1200px 500px', in: '#h-cam2', inFrom: 1.3, inF: 6 });`);
  tag('h-tag', 560, 650, 'v05 · logoSlam 150→94→100 / 6f + flash + flash-star + shake 9 px · whipZoom 100→400% / 8f (media blur) into the next shot');
}
/* I (f650-730): 3D Y-flip of the whole frame (10f, perspective 2250), then the slot-machine counter 18 -> 30 on a dark card */
{
  html.push(`<div id="i-flip" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; z-index: 1">
  <div class="fx-flip__face fx-flip__face--front">${vid('i-v1', 'R1.2.mp4', 650, 675, ' data-media-start="1.5000"' + BLUR)}</div>
  <div class="fx-flip__face fx-flip__face--back">${vid('i-v2', 'R9.1.mp4', 650, 690, ' data-media-start="1.0000"' + BLUR)}</div></div>`);
  html.push(FX.darkCardHTML({ id: 'i-dark', start: 690 / 30, dur: 40 / 30, src: 'assets/footage/R9.1.mp4', mediaStart: 2, opacity: 0.22, z: 2 }));
  html.push(host('i-slot', 690, 730, '', 'z-index: 30; --x: 960px; --y: 540px'));
  js.push(`FX.flipY(tl, '#i-flip', ${S(658)}, { frames: 10, perspective: 2250 });
      FX.slotCounter(tl, '#i-slot', ${S(694)}, { from: '18', to: '30', frames: 14, size: 330 });`);
  tag('i-tag', 650, 730, 'v05 · flipY 180° / 10f (perspective 2250, media blur) · slotCounter "18" → "30" Playfair 330, 14f blur-roll');
}
/* J (f730-810): tear-off calendar MAR 1995 -> NOV 1997 (+ glow flicker), then the UK location tag over Dundee */
{
  html.push(FX.darkCardHTML({ id: 'j-dark', start: 730 / 30, dur: 40 / 30, src: 'assets/footage/R3.8.mp4', mediaStart: 1.5, opacity: 0.2, z: 1 }));
  html.push(host('j-cal', 730, 770, '', 'z-index: 30; --x: 960px; --y: 560px'));
  html.push(vid('j-v', 'R3.1.mp4', 770, 810));
  html.push(host('j-loc', 770, 810, '', 'z-index: 30'));
  js.push(`FX.calendarTear(tl, '#j-cal', ${S(736)}, { from: 'MAR 1995', to: 'NOV 1997', frames: 12, size: 300 });
      T.glowFlicker(tl, '#j-cal .fx-cal__text--to', ${S(738)}, { frames: 10 });
      FX.locationTag(tl, '#j-loc', ${S(774)}, { x: 96, y: 600, zoom: 3, label: 'DUNDEE, SCOTLAND' });`);
  tag('j-tag', 730, 810, 'v05 · calendarTear MAR 1995 → NOV 1997 (12f, + glowFlicker) · locationTag: UK outline zooms to the pink Dundee pin (12f)');
}
/* K (f810-850): the pink pixel glitch as a full-frame transition between two shots (cut at f822) */
{
  html.push(`<div id="k-cam" class="rc-cam" style="z-index: 1">${vid('k-v1', 'R3.1.mp4', 810, 822, ' data-media-start="1.5000"')}${vid('k-v2', 'R1.2.mp4', 822, 850, ' data-media-start="3.0000"')}</div>`);
  html.push(host('k-gl', 819, 826, '', 'z-index: 50'));
  js.push(`FX.glitch(tl, '#k-gl', ${S(819)}, { mode: 'cut', frames: 7, shake: '#k-cam', shakePx: 18 });`);
  tag('k-tag', 810, 850, 'v05 · pink pixel glitch (cut mode, 7f, RGB split 9 px f2-5) across a hard cut at f822');
}
/* Z (f850-860): archival filter calibration (chromatic aberration on a white square) */
{
  html.push(`<img id="z-ca" class="clip demo-fill" src="assets/footage/ca_test.png" data-start="${A(850)}" data-duration="${D(850, 860)}" alt="" data-color-grading='{"preset":null,"intensity":1,"effects":{"chromaticAberration":0.1,"chromaticAngle":0}}'>`);
  tag('z-tag', 850, 860, 'calibration: chromaticAberration 0.1 on a 400 px white square');
}

const END = 860;
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
      .demo-tag { position: absolute; left: 96px; top: 20px; height: 26px; font-family: var(--font-setup); font-weight: 600; font-size: 19px; line-height: 26px; color: var(--white); opacity: 0.8; white-space: nowrap; text-shadow: var(--text-drop); }
      .demo-page { position: absolute; left: 260px; top: 150px; width: 1400px; height: 780px; transform: rotate(-4deg); box-shadow: 0 27px 60px rgba(0,0,0,0.5); color: #1A1A1A; }
      .demo-page__t { position: absolute; left: 110px; top: 70px; font-family: var(--font-display); font-style: italic; font-weight: 400; font-size: 96px; }
      .demo-page__t2 { position: absolute; left: 110px; top: 190px; font-family: var(--font-display); font-style: italic; font-weight: 400; font-size: 72px; }
      .demo-page__d { position: absolute; left: 580px; top: 470px; font-family: var(--font-display); font-style: italic; font-weight: 400; font-size: 46px; }
      .demo-page__p { position: absolute; left: 110px; top: 600px; width: 1180px; font-family: var(--font-display); font-style: italic; font-size: 38px; line-height: 1.4; }
      .demo-logo { position: absolute; left: 660px; top: 190px; width: 600px; height: 660px; }
      .demo-logo img { width: 100%; height: 100%; object-fit: contain; }
    </style>
  </head>
  <body>
    <!-- RC kit v05 demo (REVISION_v05 G1-G8), generated by tools/gen_demo.cjs from the kit itself. -->
    <div id="root" data-composition-id="kit-v05-demo" data-start="0" data-duration="${(END / 30).toFixed(7)}" data-width="1920" data-height="1080">
${html.join('\n')}
    </div>
    <script src="assets/kit/type.js"></script>
    <script src="assets/kit/motifs.js"></script>
    <script src="assets/kit/transitions.js"></script>
    <script src="assets/kit/screens.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const T = RCK.type, M = RCK.motifs, X = RCK.transitions, C = RCK.cam, FX = RCK.fx;
      // every lockup: the v05 entry on every word, key / hero words hold pink to f4, flags (* ! ~ # ^), block drift 104%
      T.lockupsWire(tl);
      ${js.join('\n      ')}
      tl.set({}, {}, ${(END / 30).toFixed(6)});
      window.__timelines["kit-v05-demo"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(__dirname + '/../index.html', out);
fs.writeFileSync(__dirname + '/../review/lockups.txt', report.join('\n') + '\n');
console.log('wrote index.html (' + END + ' frames)');
console.log(report.join('\n'));
