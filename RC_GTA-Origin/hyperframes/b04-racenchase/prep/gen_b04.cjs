// B4 v05: the grid's background = two kit dark cards (RCK.fx.darkCardHTML: #0E0E10 + the 1990s office blurred ~45 px at
// 25 % + grain + scanlines), angle A R3.8 (local 46-70) and angle B R3.7 (70-112): the hard cut at v04 19.0 (U3: no
// punch-in). Written into index.html between <!-- @dark --> markers.   node hyperframes/b04-racenchase/prep/gen_b04.cjs
const fs = require('fs'), path = require('path');
const PROJ = path.resolve(__dirname, '..');
globalThis.window = globalThis;
require(path.join(PROJ, 'assets/kit/type.js'));
require(path.join(PROJ, 'assets/kit/motifs.js'));
const FX = RCK.fx, F = (n) => n / 30;
const html = [
  FX.darkCardHTML({ id: 'b04-darkA', start: F(46), dur: F(24), src: 'assets/footage/R3.8.mp4', mediaStart: 0.1, opacity: 0.25, blurPx: 45, darken: 0, z: 1 }),
  FX.darkCardHTML({ id: 'b04-darkB', start: F(70), dur: F(42), src: 'assets/footage/R3.7.mp4', mediaStart: 0.1, opacity: 0.25, blurPx: 45, darken: 0, z: 1 }),
].join('\n');
let src = fs.readFileSync(path.join(PROJ, 'index.html'), 'utf8');
const re = /(<!-- @dark -->)[\s\S]*?(<!-- \/@dark -->)/;
if (!re.test(src)) throw new Error('@dark markers not found');
src = src.replace(re, (m, a, b) => a + '\n' + html + '\n' + b);
fs.writeFileSync(path.join(PROJ, 'index.html'), src);
console.log(html.replace(/data-color-grading='[^']*'/g, "data-color-grading='…'"));
