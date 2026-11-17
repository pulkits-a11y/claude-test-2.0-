// B3 v05: caption lockups (kit v05 T.lockupPlan / T.lockups) and the kit card insert (RCK.fx.cardInsertHTML), written into
// index.html between <!-- @lk:<name> --> / <!-- @card --> markers, plus prep/cues_words.json (T.lockupCues, BEAT frames)
// for cues.json. Re-run after a kit sync:   node hyperframes/b03-dundee/prep/gen_captions.cjs
//
// [DEPTH] lockups are written TWICE with the same geometry (one plan): the "behind" copy (z between the plate and the
// cut-out) shows only the key / hero row; the "front" copy (z above everything) shows only the other rows. Hidden rows are
// spacers (visibility: hidden, no .rc-lw / data-rc-f), so both copies lay out identically.
// U2: words appear on their frame (white); chosen words pop + blur in ("Dundee,", "Lemmings,"); "1995" (hero) appears
// and takes the client's glow flicker (index.html).
const fs = require('fs'), path = require('path');
const PROJ = path.resolve(__dirname, '..');
globalThis.window = globalThis;
require(path.join(PROJ, 'assets/kit/type.js'));
require(path.join(PROJ, 'assets/kit/motifs.js'));
const T = RCK.type, FX = RCK.fx;
const W = require(path.join(PROJ, 'words.json')).words;
const F = (n) => n / 30;

const groups = [
  // "It's [[1995]] in": hero 420 behind the developer's head (R3.8 angle 2, local 14-41). Hero baseline ~643 at y 499;
  // box shifted +255 px (ink x ~820-1610): his head (top ~500-518 from local 20, x ~1200-1650) covers the lower ~45 % of
  // "95", "19" clear. "It's" (setup) above-left, "in" (tail) under the right edge.
  { name: 'year', specs: [{ s: "It's [[1995]] in", hero: 420 }], opts: { from: 0, end: F(41), y: 499, idPrefix: 'b03-lk-yr', track: 11, inline: 'left: 255px' },
    depth: { behind: { id: 'b03-lk-yr-key', z: 2, hide: ['lead', 'tail'] }, front: { id: 'b03-lk-yr-txt', z: 4, hide: ['key'] } } },
  // "[Dundee,] Scotland.": key baseline ~342 at y 316, ~44 px under the Law's top (skyline ~298 px at x 960 in the plate,
  // assets/depth/R3.1_depth.SOURCE.json): the hilltop covers the bottom ~1/3 of "nde"; "D", "e," stay clear.
  { name: 'dundee', specs: ['[Dundee,]* Scotland.'], opts: { from: 3, end: F(83), y: 316, idPrefix: 'b03-lk-dun', track: 12 },
    depth: { behind: { id: 'b03-lk-dun-key', z: 6, hide: ['tail'] }, front: { id: 'b03-lk-dun-tail', z: 8, hide: ['key'] } } },
  // y 500: lifted so the yellow circle round the front walker (local 137-155, top ~596 px) clears "Lemmings,"
  { name: 'dma', specs: ['the studio behind [Lemmings,]*'], opts: { from: 7, end: F(155), y: 500, idPrefix: 'b03-lk-dma', z: 30, track: 17 } },
  { name: 'starts', specs: ['starts a [new game.]'], opts: { from: 11, end: F(195), idPrefix: 'b03-lk-starts', z: 40, track: 20 } },
];

function hideRow(html, kind) {
  // hide one row (its class list starts with rc-lk__row--<kind>): keep its text for layout, drop the word wiring
  return html.replace(new RegExp('(<div class="rc-lk__row rc-lk__row--' + kind + '(?: [^"]*)?" style=")([^"]*)(">)(.*?)(</div>)', 'g'), (m, a, st, b, inner, c) =>
    a + st + '; visibility: hidden' + b + inner.replace(/<span class="rc-lw[^"]*" data-rc-f="\d+">/g, '<span>') + c);
}
function copyOf(html, prefix, spec) {
  let h = html.replace('id="' + prefix + '-1"', 'id="' + spec.id + '"');
  h = /z-index: \d+/.test(h) ? h.replace(/z-index: \d+/, 'z-index: ' + spec.z) : h.replace('style="', 'style="z-index: ' + spec.z + '; ');
  for (const k of spec.hide) h = hideRow(h, k);
  return h;
}
function put(src, name, html) {
  const re = new RegExp('(<!-- @' + name + ' -->)[\\s\\S]*?(<!-- /@' + name + ' -->)');
  if (!re.test(src)) throw new Error('markers @' + name + ' not found in index.html');
  return src.replace(re, (m, a, b) => a + '\n' + html + '\n' + b);
}

let src = fs.readFileSync(path.join(PROJ, 'index.html'), 'utf8');
const report = [], cues = { word_pops: [], key_words: [] };
for (const g of groups) {
  const plan = T.lockupPlan(W, g.specs, g.opts);
  report.push(g.name + '\n' + T.lockupReport(plan));
  const c = T.lockupCues(plan, 6);                       // beat frames (local - 6; the kit subtracts the offset)
  cues.word_pops.push(...c.word_pops); cues.key_words.push(...c.key_words);
  let html = T.lockups(plan, null, g.opts);
  if (g.depth) html = copyOf(html, g.opts.idPrefix, g.depth.behind) + '\n' + copyOf(html, g.opts.idPrefix, g.depth.front);
  src = put(src, 'lk:' + g.name, html);
}
// "starts a new game." (local 155-195): the BBC 1996 team (R3.7_team.mp4, media 0.2 = source 195.0 s) as the kit card
// insert: white 15 px border, 3 deg, shadow; background = the same clip at 130 %, blurred 60 px, darkened 50 %.
// The card's own clip gets the beat's archival look (the v04 archival colour + the kit's archivalGrading: a little
// aberration + the light VHS wobble), written here so a re-run keeps it; the blurred background keeps the kit's grading.
const ARCH = { preset: null, intensity: 1, adjust: { shadows: 0.04, temperature: 0.06, saturation: -0.2 }, effects: FX.archivalGrading().effects };
let card = FX.cardInsertHTML({ id: 'b03-card', src: 'assets/footage/R3.7_team.mp4', start: F(155), dur: F(40), mediaStart: 0.2, tilt: 3, z: 35 });
card = card.replace('<video id="b03-card-fg" ', '<video id="b03-card-fg" data-color-grading=\'' + JSON.stringify(ARCH) + '\' ');
if (!/b03-card-fg" data-color-grading/.test(card)) throw new Error('card fg grading not inserted');
src = put(src, 'card', card);
fs.writeFileSync(path.join(PROJ, 'index.html'), src);
cues.word_pops.sort((a, b) => a - b); cues.key_words.sort((a, b) => a - b);
fs.writeFileSync(path.join(__dirname, 'cues_words.json'), JSON.stringify(cues) + '\n');
console.log(report.join('\n'));
console.log('cues (beat frames):', JSON.stringify(cues));
