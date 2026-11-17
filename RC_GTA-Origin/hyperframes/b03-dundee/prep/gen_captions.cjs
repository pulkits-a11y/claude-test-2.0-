// B3 v05 caption lockups, generated with the kit's T.lockupPlan / T.lockups (assets/kit/type.js) and written into
// index.html between <!-- @lk:<name> --> ... <!-- /@lk:<name> --> markers. Re-run after a kit sync (sizes, rows and
// offsets come from the kit):   node hyperframes/b03-dundee/prep/gen_captions.cjs
//
// [DEPTH] "Dundee,": the lockup "[Dundee,] Scotland." is written TWICE with the same geometry: copy A (z between the
// plate and the hill cut-out) shows only the key row "Dundee,"; copy B (z above everything) shows only the tail row
// "Scotland.". The hidden row in each copy is a spacer (visibility: hidden, no .rc-lw / data-rc-f), so both copies lay
// out (and, with the kit v05 drift, scale) identically.
const fs = require('fs'), path = require('path');
const PROJ = path.resolve(__dirname, '..');
globalThis.window = globalThis;
require(path.join(PROJ, 'assets/kit/type.js'));
const T = RCK.type;
const W = require(path.join(PROJ, 'words.json')).words;
const F = (n) => n / 30;

// y = the ink centre. Dundee: key baseline = y + 24.4 px (kit layout) -> 340 px, ~42 px under the Law's top
// (skyline ~298 px at x 960 in the plate, R3.1_depth.SOURCE.json): the hilltop covers the bottom ~30 % of "nde" at
// 100 % and ~45 % at the end of the 108 % push; "D", "e," stay clear.
const groups = [
  { name: 'dundee', specs: ['[Dundee,] Scotland.'], opts: { from: 0, end: F(46), y: 316, idPrefix: 'b03-lk-dun', z: 2, track: 11 }, depth: true },
  // y 500: lifted 40 px so the yellow circle round the front walker (local 100-118, top ~585 px) clears "Lemmings,"
  { name: 'dma', specs: ['the studio behind [Lemmings,]'], opts: { from: 4, end: F(118), y: 500, idPrefix: 'b03-lk-dma', z: 30, track: 12 } },
  { name: 'starts', specs: ['starts a [new game.]'], opts: { from: 8, end: F(158), idPrefix: 'b03-lk-starts', z: 40, track: 20 } },
];

function stripRow(html, kind) {
  // hide one row: keep its text for layout, drop the word wiring
  return html.replace(new RegExp('(<div class="rc-lk__row rc-lk__row--' + kind + '" style=")([^"]*)(">)(.*?)(</div>)'), (m, a, st, b, inner, c) =>
    a + st + '; visibility: hidden' + b + inner.replace(/<span class="rc-lw[^"]*" data-rc-f="\d+">/g, '<span>') + c);
}

let src = fs.readFileSync(path.join(PROJ, 'index.html'), 'utf8');
const report = [];
for (const g of groups) {
  const plan = T.lockupPlan(W, g.specs, g.opts);
  report.push(g.name + '\n' + T.lockupReport(plan));
  let html = T.lockups(plan, null, g.opts);
  if (g.depth) {
    const a = stripRow(html, 'tail').replace('id="b03-lk-dun-1"', 'id="b03-lk-dun-key"');
    const b = stripRow(html, 'key').replace('id="b03-lk-dun-1"', 'id="b03-lk-dun-tail"').replace('z-index: 2', 'z-index: 4');
    html = a + '\n' + b;
  }
  const re = new RegExp('(<!-- @lk:' + g.name + ' -->)[\\s\\S]*?(<!-- /@lk:' + g.name + ' -->)');
  if (!re.test(src)) throw new Error('markers for ' + g.name + ' not found in index.html');
  src = src.replace(re, (m, a, b) => a + '\n' + html + '\n' + b);
}
fs.writeFileSync(path.join(PROJ, 'index.html'), src);
console.log(report.join('\n'));
