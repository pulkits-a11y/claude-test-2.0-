// B3 v05 caption lockups, generated with the kit's T.lockupPlan / T.lockups (assets/kit/type.js) and written into
// index.html between <!-- @lk:<name> --> ... <!-- /@lk:<name> --> markers. Re-run after a kit sync (sizes, rows and
// offsets come from the kit):   node hyperframes/b03-dundee/prep/gen_captions.cjs
//
// [DEPTH] lockups are written TWICE with the same geometry: the "behind" copy (z between the plate and the cut-out)
// shows only the key row; the "front" copy (z above everything) shows only the other rows. Hidden rows are spacers
// (visibility: hidden, no .rc-lw / data-rc-f), so both copies lay out identically.
// U2 (client override): words simply appear on their frame (hard cut, white); only the chosen key words pop + blur in
// ("Dundee,", "Lemmings,"; "1995" enters with the client's glow flicker instead).
const fs = require('fs'), path = require('path');
const PROJ = path.resolve(__dirname, '..');
globalThis.window = globalThis;
require(path.join(PROJ, 'assets/kit/type.js'));
const T = RCK.type;
const W = require(path.join(PROJ, 'words.json')).words;
const F = (n) => n / 30;

const groups = [
  // "It's [1995] in": "1995" Coolvetica Italic 420 px behind the developer's head (R3.8 angle 2, local 14-41). Key baseline
  // = y + 141 px -> 640; box shifted +255 px (ink x ~820-1610): his head (top ~500-518 from local 20, x ~1200-1650) covers
  // the lower ~45 % of "95"; "19" stays clear. "It's" (lead) above-left, "in" (tail) under the right edge.
  { name: 'year', specs: ["It's [1995] in"], opts: { from: 0, end: F(41), keySize: 420, y: 499, idPrefix: 'b03-lk-yr', track: 11, inline: 'left: 255px' },
    depth: { behind: { id: 'b03-lk-yr-key', z: 2, hide: ['lead', 'tail'] }, front: { id: 'b03-lk-yr-txt', z: 4, hide: ['key'] } } },
  // "[Dundee,] Scotland.": key baseline = y + 24.4 px -> 340, ~42 px under the Law's top (skyline ~298 px at x 960 in the
  // plate, R3.1_depth.SOURCE.json): the hilltop covers the bottom ~30-37 % of "nde"; "D", "e," stay clear.
  { name: 'dundee', specs: ['[Dundee,]* Scotland.'], opts: { from: 3, end: F(83), y: 316, idPrefix: 'b03-lk-dun', track: 12 },
    depth: { behind: { id: 'b03-lk-dun-key', z: 6, hide: ['tail'] }, front: { id: 'b03-lk-dun-tail', z: 8, hide: ['key'] } } },
  // y 500: lifted 40 px so the yellow circle round the front walker (local 137-155, top ~585 px) clears "Lemmings,"
  { name: 'dma', specs: ['the studio behind [Lemmings,]*'], opts: { from: 7, end: F(155), y: 500, idPrefix: 'b03-lk-dma', z: 30, track: 17 } },
  { name: 'starts', specs: ['starts a [new game.]'], opts: { from: 11, end: F(195), idPrefix: 'b03-lk-starts', z: 40, track: 20 } },
];

function hideRow(html, kind) {
  // hide one row: keep its text for layout, drop the word wiring
  return html.replace(new RegExp('(<div class="rc-lk__row rc-lk__row--' + kind + '" style=")([^"]*)(">)(.*?)(</div>)'), (m, a, st, b, inner, c) =>
    a + st + '; visibility: hidden' + b + inner.replace(/<span class="rc-lw[^"]*" data-rc-f="\d+">/g, '<span>') + c);
}
function copyOf(html, prefix, spec) {
  let h = html.replace('id="' + prefix + '-1"', 'id="' + spec.id + '"').replace(/z-index: \d+/, 'z-index: ' + spec.z);
  if (!/z-index/.test(h)) h = h.replace('style="', 'style="z-index: ' + spec.z + '; ');
  for (const k of spec.hide) h = hideRow(h, k);
  return h;
}

let src = fs.readFileSync(path.join(PROJ, 'index.html'), 'utf8');
const report = [];
for (const g of groups) {
  const plan = T.lockupPlan(W, g.specs, g.opts);
  report.push(g.name + '\n' + T.lockupReport(plan));
  let html = T.lockups(plan, null, g.opts);
  if (g.depth) html = copyOf(html, g.opts.idPrefix, g.depth.behind) + '\n' + copyOf(html, g.opts.idPrefix, g.depth.front);
  const re = new RegExp('(<!-- @lk:' + g.name + ' -->)[\\s\\S]*?(<!-- /@lk:' + g.name + ' -->)');
  if (!re.test(src)) throw new Error('markers for ' + g.name + ' not found in index.html');
  src = src.replace(re, (m, a, b) => a + '\n' + html + '\n' + b);
}
fs.writeFileSync(path.join(PROJ, 'index.html'), src);
console.log(report.join('\n'));
