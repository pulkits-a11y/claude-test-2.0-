// B18 v05: the kit dark card (RCK.fx.darkCardHTML: #0E0E10 + grain + scanlines + a faint blurred footage loop), written
// into index.html between <!-- @dark --> markers.   node hyperframes/b18-cta/prep/gen_b18.cjs
// The faint footage = B1's police-lightbar footage (assets/footage/b18_lightbar.mp4: B1's LOOP_FRAME.json recipe started 2.5 s
// earlier, so its frame 81 IS B1's frame 0): the last-6-frame cross then reads as that footage coming up to full.
const fs = require('fs'), path = require('path');
const PROJ = path.resolve(__dirname, '..');
globalThis.window = globalThis;
require(path.join(PROJ, 'assets/kit/type.js'));
require(path.join(PROJ, 'assets/kit/motifs.js'));
const html = RCK.fx.darkCardHTML({ id: 'b18-dark', start: 0, dur: 87 / 30, src: 'assets/footage/b18_lightbar.mp4', mediaStart: 0, opacity: 0.2, blurPx: 40, darken: 0.5, z: 1 });
let src = fs.readFileSync(path.join(PROJ, 'index.html'), 'utf8');
const re = /(<!-- @dark -->)[\s\S]*?(<!-- \/@dark -->)/;
if (!re.test(src)) throw new Error('@dark markers not found');
fs.writeFileSync(path.join(PROJ, 'index.html'), src.replace(re, (m, a, b) => a + '\n' + html + '\n' + b));
console.log(html.replace(/data-color-grading='[^']*'/g, "data-color-grading='…'"));
