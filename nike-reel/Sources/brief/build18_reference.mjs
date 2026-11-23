// v4 generator. Same clock as v3 (tightened VO, times written on the original clock, mapped with M()).
// Changes: OPTIZither special font, rise + blur + fade text, CRT scanlines, polaroid zoom-through into the
// Excite page, Bell framed-photo scene (Koum-reel style) with fly-in objects, Alphabet flowchart,
// quote-block CTA with inline logo, $6.7B, reverted Excite->Google wipe.  Run: node build/build4.mjs
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { cards as RAW } from "./captions-data.mjs";
import { loadFont, ink } from "./fontmetrics.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FMO = loadFont(path.join(ROOT, "assets/fonts/BodoniCursive-MediumItalic.ttf")), FMA = loadFont(path.join(ROOT, "assets/fonts/Almarai-Bold.ttf"));   // v21: the cursive is Bodoni Moda 9pt Medium Italic
const FPS = 30;
const r3 = (n) => Math.round(n * 1000) / 1000;
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const LIGHT = "#F1ECE4", INK = "#141414", HL = "#FFD84D";

// ---------- time map ----------
const MAP = JSON.parse(fs.readFileSync(path.join(ROOT, "build/vo-map.json"), "utf8"));
function M(t) { let r = 0; for (const [a, b] of MAP.cuts) { if (t >= b) r += b - a; else if (t > a) { r += t - a; break; } else break; } return r3((t - r) / MAP.speed); }
function Mi(T) { let lo = 0, hi = 100; for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (M(m) < T) lo = m; else hi = m; } return r3(hi); }   // v23: M's inverse
const NEWW = JSON.parse(fs.readFileSync(path.join(ROOT, "build/vo_fast_words.json"), "utf8"));
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9$]/g, "");
const SIL = fs.readFileSync(path.join(ROOT, ".work/silences.txt"), "utf8").trim().split(/\r?\n/).map((l) => l.trim().split(/\s+/).map(Number));
function WT(text, t, isEnd = /[.,]$/.test(text)) {
  const m = M(t), n = norm(text);
  const sil = SIL.find(([a, b]) => t > a + 0.03 && t < b - 0.03);
  if (!sil) return m;
  if (!isEnd) return r3(M(sil[1]) + 0.02);
  let best = null;
  for (const w of NEWW) if (norm(w.w) === n && Math.abs(w.t - m) < 0.8 && (!best || Math.abs(w.t - m) < Math.abs(best.t - m))) best = w;
  return best ? r3(best.t) : m;
}
const VO_LEN = MAP.len;
// ---------- v14: a faster cut ----------
// the v13 clock (1.07x, 0.15 s breaths) -> the v14 clock (1.18x, 0.09 s breaths), for the few constants measured on it
const MAP13 = JSON.parse(fs.readFileSync(path.join(ROOT, "build/vo-map-v13.json"), "utf8"));
function inv13(tf) { let p0 = 0, acc = 0; const S = []; for (const [a, b] of MAP13.cuts) { S.push([p0, a]); p0 = b; } S.push([p0, 94.511]); for (const [a, b] of S) { const f0 = acc / MAP13.speed, f1 = (acc + b - a) / MAP13.speed; if (tf <= f1 + 1e-9) return a + Math.max(0, tf - f0) * MAP13.speed; acc += b - a; } return 94.511; }
const F1 = (t) => M(inv13(t));
const VOIDS = [];   // the full-screen text covers (black void shots): their captions are set bigger
const PUNCH = [];   // the big word of every caption: the B-roll shot under it punches in
RAW.forEach((c) => { const h = c.words.find((w) => w.r === "h"); if (h) PUNCH.push(WT(h.text, h.t)); else if (c.num) PUNCH.push(M(c.num.t)); });
const END = r3(M(88.37) + 2.3);   // v15: the film ends on the Raw Canvas mark
const VO_END = r3(NEWW.find((w) => w.w === "At" && w.t > 60).t - 0.05);   // the voiceover stops before "At Raw Canvas"

const FONTFACE = `
@font-face{font-family:"Bodoni Cursive";src:url("assets/fonts/BodoniCursive-MediumItalic.ttf") format("truetype");font-style:italic;font-weight:500;}
@font-face{font-family:"Heros";src:url("assets/fonts/texgyreheros-bold.otf") format("opentype");font-style:normal;font-weight:700;}
@font-face{font-family:"Heros";src:url("assets/fonts/texgyreheros-bolditalic.otf") format("opentype");font-style:italic;font-weight:700;}
@font-face{font-family:"Almarai";src:url("assets/fonts/Almarai-Bold.ttf") format("truetype");font-weight:700;font-style:normal;}`;
// v15 MANDATORY: every animation in the film runs on one of three curves - easeOutExpo (xo), easeInOutExpo (xio),
// easeInOutCirc (cio) - held on 8 fps steps (the low-frame-rate look). Nothing is linear. The older ease names used
// across the scenes are aliases of these three.
const EASE_JS = `function q_(d,f){return Math.max(2,Math.round(d*f));}
function stepUp(t,n){if(t<=0)return 0;if(t>=1)return 1;return Math.min(1,Math.ceil(t*n-1e-6)/n);}
function eOX(x){return x>=1?1:1-Math.pow(2,-10*x);}
function eIOX(x){return x<=0?0:x>=1?1:x<.5?Math.pow(2,20*x-10)/2:(2-Math.pow(2,-20*x+10))/2;}
function eIOC(x){return x<.5?(1-Math.sqrt(1-Math.pow(2*x,2)))/2:(Math.sqrt(1-Math.pow(-2*x+2,2))+1)/2;}
function xo(d){var n=q_(d,8);return function(t){return eOX(stepUp(t,n));};}
function xio(d){var n=q_(d,8);return function(t){return eIOX(stepUp(t,n));};}
function cio(d){var n=q_(d,8);return function(t){return eIOC(stepUp(t,n));};}
function sxo(d){return eOX;}function sxio(d){return eIOX;}function scio(d){return eIOC;}
function sxoP(p){var k=eOX(p);return function(t){return eOX(t*p)/k;};}
var vox=cio,voxIn=xio,voxOut=xo,dft=xo,rise=xo,loOut=xo,loIn=xio,loIO=cio;`;
// a word / element opening: from below, blurred and transparent, to sharp, in low-frame-rate steps
// v14: no pop-in. Text fades in fast instead of rising and un-blurring
// v15: text fades in on a stepped easeOutExpo (two 8 fps steps, so it reads as a snap); nothing linear
const riseIn = (sel, at, d, dy) => `tl.fromTo("${sel}",{opacity:0},{opacity:1,duration:0.25,ease:xo(0.25)},${at});`;
const riseInS = (sel, at) => `tl.fromTo("${sel}",{opacity:0},{opacity:1,duration:0.3,ease:sxo(0.3)},${at});`;   // v21: the smooth fade-in
// v16: the logos' rise-in (up from below, blurred to sharp), on a stepped easeOutExpo
const riseUp = (sel, at, d, dy) => `tl.fromTo("${sel}",{y:${dy},opacity:0,filter:"blur(14px)"},{y:0,opacity:1,filter:"blur(0px)",duration:${d},ease:xo(${d})},${at});`;
// v17: every B-roll clip gets a subtle version of the curated look of 0:13 / 0:36: the light grade in grade_lite.json (soft
// colour split, bloom, dust, vignette, grain - validated with `hyperframes media-treatment`) merged into the clip's own
// grade (the stronger value of each effect wins), plus two faint prism streaks at the edges (see Scene.video)
const GRADE_S = (f) => JSON.stringify(JSON.parse(fs.readFileSync(path.join(ROOT, "build", f), "utf8")));
function LITE(f) {
  const rd = (n) => JSON.parse(fs.readFileSync(path.join(ROOT, "build", n), "utf8"));
  const lite = rd("grade_lite.json");
  if (!f) return JSON.stringify(lite);
  const g = rd(f);
  for (const k of ["chromaticAberration", "bloom", "bloomRadius", "filmArtifacts"]) g.effects[k] = Math.max(g.effects[k] || 0, lite.effects[k]);
  for (const k of ["vignette", "grain"]) g.details[k] = Math.max(g.details[k] || 0, lite.details[k]);
  return JSON.stringify(g);
}
const FLASH17 = [];   // v17: the white flash sits on the cut onto Google's own footage (0:33)
const FLASH18 = [];   // v18: a white flash on a few hard cuts onto footage (0:09, 0:27, 0:58, 1:03) - with 0:34's, five in all
// v20 (0:09, 0:24): the Excite page on a glowing screen in the dark - the window set into a rounded screen with fine scan
// lines, an inner vignette and a glass sheen, over a blurred colour-bleeding glow of the same page, on the dark textured
// board of the curated shots, prism streaks at the edges, grain. The page itself scrolls and the cursor works as before.
const SCREEN = (id, o, winHTML, ghostHTML, wc) => `<div class="ngbg cwb" id="${id}-bd"></div>
<div class="cwghost" id="${id}-gh" data-layout-ignore><div class="win" style="left:0;top:0;width:1920px;height:1080px">${ghostHTML}</div></div>
<div class="kb" id="${id}-k"><div class="cwscr" id="${id}-sc"><div class="win" style="left:0;top:0;width:1920px;height:1080px">${winHTML}</div>${wc}<div class="cwcrt"></div></div></div>
<div class="cwfx" id="${id}-fx"><div class="ngvig" data-layout-allow-occlusion style="opacity:.75"></div><div class="pz pz2" style="opacity:.4"></div><div class="pz pz3" style="opacity:.34"></div><div class="bgrain" data-layout-allow-occlusion style="opacity:.45"></div></div>`;
const flick = (sel, at) => `tl.set("${sel}",{attr:{"data-f":"1"}},${r3(at)});tl.set("${sel}",{attr:{"data-f":"0"}},${r3(at + 0.034)});tl.set("${sel}",{attr:{"data-f":"1"}},${r3(at + 0.1)});tl.set("${sel}",{attr:{"data-f":"0"}},${r3(at + 0.167)});`;

const BASE_CSS = `
#root{position:absolute;inset:0;overflow:hidden;background:#0d0d0e;}
.shot,.mv{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;}
.kb{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:50% 50%;}
.cover{position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover;}
.void{background:radial-gradient(ellipse at 50% 48%,#1e1e21 0%,#0f0f11 58%,#050506 100%);}
.clean{background:#F6F7FB;}
.paper{background:#ECE7E0 url("assets/tex/paper.jpg") center/cover;}
.gridbg{position:absolute;left:0;top:0;width:1920px;height:1080px;background-color:#ECEAE5;background-image:linear-gradient(rgba(40,40,40,.09) 2px,transparent 2px),linear-gradient(90deg,rgba(40,40,40,.09) 2px,transparent 2px);background-size:72px 72px;background-position:-6px -6px;}
.gridtex{position:absolute;left:0;top:0;width:1920px;height:1080px;background:url("assets/tex/paper.jpg") center/cover;mix-blend-mode:multiply;opacity:.55;}
.dim{position:absolute;left:0;top:0;width:1920px;height:1080px;background:#000;}
.bgrain{position:absolute;left:0;top:0;width:1920px;height:1080px;background:url("assets/tex/grain.png") 0 0/2400px 1400px;mix-blend-mode:overlay;opacity:.6;}
.pol{position:absolute;background:#F4F1EA;padding:20px 20px 76px;box-shadow:0 26px 50px rgba(0,0,0,.30),0 4px 10px rgba(0,0,0,.18);}
.pol .ph{position:relative;width:100%;height:100%;overflow:hidden;background:#1b1b1b;}
.pol .ph > img{width:100%;height:100%;object-fit:cover;display:block;}
.pol .age{position:absolute;inset:0;background:url("assets/tex/paper.jpg") center/cover;mix-blend-mode:multiply;opacity:.45;pointer-events:none;}
.win{position:absolute;background:#c0c0c0;border:2px solid;border-color:#fff #404040 #404040 #fff;box-shadow:0 22px 50px rgba(0,0,0,.4);overflow:hidden;font-family:Arial,Helvetica,sans-serif;}
.win-title{height:30px;background:linear-gradient(90deg,#000080,#1084d0);color:#fff;font:bold 17px Arial;display:flex;align-items:center;padding:0 10px;gap:8px;}
.win-title .bx{margin-left:auto;display:flex;gap:4px}.win-title .bx i{width:22px;height:20px;background:#c0c0c0;border:2px solid;border-color:#fff #404040 #404040 #fff;display:block}
.win-tools{height:34px;display:flex;align-items:center;gap:14px;padding:0 12px;font:14px Arial;color:#000;border-bottom:1px solid #808080}
.win-tools b{font-weight:normal;padding:3px 8px;border:1px solid;border-color:#fff #808080 #808080 #fff}
.win-url{height:34px;display:flex;align-items:center;gap:8px;padding:0 12px;font:14px Arial;color:#000;border-bottom:2px solid #808080}
.win-url span.f{flex:1;background:#fff;border:2px solid;border-color:#808080 #fff #fff #808080;padding:3px 6px;font:15px "Courier New",monospace}
.win-page{position:absolute;left:4px;right:4px;bottom:4px;background:#fff;overflow:hidden;}
.pscale{position:absolute;left:0;top:0;transform-origin:0 0;}
.pscroll{position:relative;background:#fff;color:#000;font-family:"Times New Roman",Times,serif;font-size:16px;}
.cursor{position:absolute;left:0;top:0;width:34px;height:50px;z-index:30;}
.gpage{width:1280px;padding-top:18px;text-align:center;font-family:"Times New Roman",Times,serif;font-size:16px;color:#000;background:#fff;height:900px}
.gpage table{margin:0 auto;border-collapse:separate;border-spacing:2px;width:90%}
.gpage a{color:#00c;}
.ginput{display:inline-block;width:420px;height:26px;border:2px solid;border-color:#808080 #fff #fff #808080;text-align:left;font:16px Arial;padding:2px 4px;vertical-align:middle;background:#fff;white-space:nowrap;overflow:hidden}
.gbtn{display:inline-block;font:14px Arial;padding:2px 8px;border:2px solid;border-color:#fff #404040 #404040 #fff;background:#d4d0c8;margin:4px 2px}
.caret{display:inline-block;width:2px;height:18px;background:#000;vertical-align:middle}
.hlt{background-image:linear-gradient(${HL},${HL});background-repeat:no-repeat;background-position:0 55%;background-size:0% 92%;padding:2px 4px;margin:-2px -4px;}
.lbl{position:absolute;left:0;right:0;bottom:70px;text-align:center;font:700 30px Almarai,sans-serif;color:${LIGHT};text-shadow:0 2px 12px rgba(0,0,0,.6)}
.nm{position:absolute;font-family:Almarai,sans-serif;font-weight:700;text-transform:uppercase;color:#fff;letter-spacing:-.025em;line-height:.9;white-space:nowrap;}
.nm div{text-shadow:-3px 0 0 rgba(40,190,255,.75),3px 0 0 rgba(255,150,40,.6),0 0 22px rgba(255,255,255,.55),0 0 60px rgba(150,200,255,.25),0 4px 18px rgba(0,0,0,.55);}
.nm .n1{font-size:150px;}.nm .n2{font-size:96px;margin-top:-4px;}
.win-title .bx i{font:bold 15px/16px Arial,sans-serif;color:#000;text-align:center;font-style:normal;}
.win-title .bx i[data-p="1"]{border-color:#404040 #fff #fff #404040;background:#b4b4b4;}
.msurf{position:absolute;background:radial-gradient(ellipse at 50% 46%,#6c6a67 0%,#4c4a48 40%,#2a2928 100%);}
.msurf i{position:absolute;left:0;top:0;width:100%;height:100%;background:url("assets/tex/paper.jpg") 0 0/1920px 1080px repeat;mix-blend-mode:multiply;opacity:.5;}
.mprop{position:absolute;filter:blur(5px) grayscale(.8) brightness(.5) contrast(.92);box-shadow:0 30px 60px rgba(0,0,0,.5);}
.mrot{position:absolute;}
.mcard{position:absolute;left:0;top:0;width:100%;height:100%;background:#F2EEE6;border-radius:24px;box-shadow:0 30px 70px rgba(0,0,0,.38);display:flex;align-items:center;justify-content:center;}
/* no texture edge */ .mcard::after{display:none;content:"";position:absolute;left:0;top:0;width:100%;height:100%;border-radius:24px;background:url("assets/tex/paper.jpg") center/cover;mix-blend-mode:multiply;opacity:.4;pointer-events:none;}
.mword{position:relative;z-index:1;font-family:Almarai,sans-serif;font-weight:700;font-style:italic;color:#141414;letter-spacing:-.035em;line-height:1;white-space:nowrap;}
.mword .ib{position:relative;display:inline-block;}
.mword .burst{position:absolute;left:-.07em;top:-.27em;width:.5em;height:.32em;overflow:visible;}
.mlabel{position:absolute;background:#111;border-radius:7px;color:#F4F1EA;font:italic 700 46px/1 Almarai,sans-serif;letter-spacing:-.02em;display:flex;align-items:center;justify-content:center;box-shadow:0 12px 26px rgba(0,0,0,.45);}
.mfig{position:absolute;left:0;width:1920px;text-align:center;font:italic 700 150px/1 Almarai,sans-serif;color:#F1ECE4;letter-spacing:-.03em;white-space:nowrap;}
.mfig span{display:inline-block;text-shadow:0 0 22px rgba(255,248,238,.45),0 0 60px rgba(255,248,238,.22),0 4px 16px rgba(0,0,0,.55);}
.mlines{position:absolute;left:0;top:0;overflow:visible;}
/* v10 opener: black LCD-dot field, bold words, RGB-split glow */
.opv{background:#0a0a0b;}
.opbg{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 50%,#17171a 0%,#0c0c0d 52%,#030303 100%);}
.opdot{position:absolute;left:0;top:0;width:1920px;height:1080px;background-image:radial-gradient(circle,rgba(255,255,255,.08) 0 1.4px,transparent 2.1px);background-size:11px 11px;background-position:3px 2px;}
.opk{position:absolute;left:0;top:0;width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;transform-origin:50% 50%;}
.opl{display:flex;gap:.26em;font:700 168px/1 Inter,sans-serif;letter-spacing:-.045em;color:#f6f6f4;white-space:nowrap;}
.ow{display:inline-block;text-shadow:-3px 0 0 rgba(0,225,255,.75),3px 0 0 rgba(255,40,90,.7),0 0 20px rgba(255,255,255,.5),0 0 64px rgba(255,255,255,.2);}
.opy{font:700 560px/1 Inter,sans-serif;letter-spacing:-.065em;color:#f6f6f4;white-space:nowrap;text-shadow:-7px 0 0 rgba(0,225,255,.75),7px 0 0 rgba(255,40,90,.7),0 0 34px rgba(255,255,255,.45),0 0 120px rgba(255,255,255,.18);}
.opy[data-hit="1"]{text-shadow:-22px 0 0 rgba(0,225,255,.9),22px 0 0 rgba(255,40,90,.85),0 0 40px rgba(255,255,255,.6);}
.opnz{position:absolute;left:0;top:0;width:1920px;height:1080px;background:#6d6d6d url("assets/tex/grain.png") 0 0/1200px 700px;}
/* v10 storyboard section (0:03-0:08): bold Inter type, hard vignette, LCD mesh */
.mesh{position:absolute;left:0;top:0;width:1920px;height:1080px;background-image:linear-gradient(90deg,rgba(0,0,0,.3) 1.5px,transparent 1.5px),linear-gradient(rgba(0,0,0,.2) 1.5px,transparent 1.5px);background-size:6px 6px;mix-blend-mode:multiply;}
.hvig{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 78% 82% at 50% 50%,rgba(0,0,0,0) 40%,rgba(0,0,0,.45) 68%,rgba(0,0,0,.86) 88%,rgba(0,0,0,.97) 100%);}
.sbt{position:absolute;font-family:Inter,sans-serif;font-weight:900;color:#F1ECE4;text-transform:uppercase;letter-spacing:-.025em;line-height:.98;white-space:nowrap;}
.sbl{display:block;}
.sw{display:inline-block;margin-right:.2em;text-shadow:0 0 22px rgba(255,248,238,.4),0 0 60px rgba(255,248,238,.16),0 5px 18px rgba(0,0,0,.65);}
.sw:last-child{margin-right:0;}
.gfield{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 40%,#3a3c3b 0%,#1c1d1d 70%,#0d0d0d 100%);}
.gpush{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:46% 30%;}
.gblur{position:absolute;left:0;top:0;width:1920px;height:1080px;}
.gpg{position:absolute;left:250px;top:150px;width:1280px;height:900px;transform-origin:640px 75px;transform:perspective(2200px) rotateY(-16deg) rotateX(9deg) rotateZ(-5deg) scale(2.3);box-shadow:0 40px 90px rgba(0,0,0,.6);}
.gglare{position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(115deg,rgba(255,255,255,.16) 0%,rgba(255,255,255,0) 38%),radial-gradient(ellipse at 30% 25%,rgba(200,255,240,.08) 0%,rgba(0,0,0,0) 60%);mix-blend-mode:screen;}
.fhalf{position:absolute;top:0;width:960px;height:1080px;overflow:hidden;background:#111;}
.fseam{position:absolute;left:957px;top:0;width:6px;height:1080px;background:#0b0b0b;}
.fgrad{position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(180deg,rgba(0,0,0,0) 38%,rgba(0,0,0,.55) 62%,rgba(0,0,0,.85) 100%);}
.sbdark{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 40% 38%,#3a3937 0%,#232221 50%,#101010 100%);}
.sbdark i{position:absolute;left:0;top:0;width:1920px;height:1080px;background:url("assets/tex/paper.jpg") 0 0/1920px 1080px;mix-blend-mode:multiply;opacity:.55;}
.sbarrow{position:absolute;left:0;top:0;overflow:visible;filter:drop-shadow(0 0 14px rgba(255,248,238,.45));}
.desk{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 62% 48%,#4a4845 0%,#2d2c2a 45%,#141414 100%);}
.pst{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:70% 55%;}
.psh{position:absolute;width:640px;height:820px;background:#EEEAE2 url("assets/tex/paper.jpg") center/cover;box-shadow:0 24px 46px rgba(0,0,0,.5),0 3px 8px rgba(0,0,0,.35);overflow:hidden;}
.psh .em{position:absolute;left:70px;top:70px;width:96px;height:112px;background:#8C1515;color:#fff;font:900 84px/112px Inter,sans-serif;text-align:center;}
.psh .tt{position:absolute;left:70px;top:250px;font:700 70px/1.05 Almarai,sans-serif;color:#2a2826;letter-spacing:-.02em;}
.psh .st{position:absolute;left:72px;top:345px;font:700 28px/1.4 Almarai,sans-serif;color:#6a655e;}
.psh .ln{position:absolute;left:72px;height:9px;background:#c9c3b8;}
.tgrad{position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(200deg,rgba(0,0,0,.72) 0%,rgba(0,0,0,.3) 34%,rgba(0,0,0,0) 56%);}
.bpole{position:absolute;left:300px;top:-20px;width:34px;height:1120px;background:linear-gradient(90deg,#050505,#2b2b2b 45%,#080808);}
.barm{position:absolute;left:300px;top:92px;width:700px;height:20px;background:linear-gradient(180deg,#2b2b2b,#050505);}
.bflag{position:absolute;left:380px;top:112px;width:560px;height:800px;background:linear-gradient(90deg,#6f0f0f 0%,#8C1515 22%,#9d1c1c 50%,#86140f 78%,#6a0d0d 100%);box-shadow:0 30px 60px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;}
.bflag b{font:900 600px/1 Inter,sans-serif;color:#8C1515;-webkit-text-stroke:16px #fff;paint-order:stroke fill;letter-spacing:0;}
/* v11 negotiation shot (0:15.8-0:20.1): clip framed on a dark textured board, prism streaks, glowing serif words underneath */
@font-face{font-family:"Instrument Serif";src:url("assets/fonts/InstrumentSerif-Italic.ttf") format("truetype");font-style:italic;font-weight:400;}
.ngbg{background:radial-gradient(ellipse at 50% 34%,rgba(130,92,56,.34) 0%,rgba(0,0,0,0) 62%),linear-gradient(rgba(16,12,10,.68),rgba(16,12,10,.68)),url("assets/tex/grunge.jpg") center/cover;}
.ngz{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:50% 42%;}
.ngghost{position:absolute;left:-190px;top:-110px;width:2300px;height:1294px;opacity:.5;mix-blend-mode:screen;}
.ngshade{position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(180deg,rgba(0,0,0,0) 52%,rgba(8,6,5,.55) 72%,rgba(8,6,5,.82) 100%);}
.ngframe{position:absolute;left:210px;top:44px;width:1500px;height:844px;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 13%,#000 87%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,0) 0%,#000 14%,#000 84%,rgba(0,0,0,0) 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 13%,#000 87%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,0) 0%,#000 14%,#000 84%,rgba(0,0,0,0) 100%);mask-composite:intersect;}
.ngv{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;}
.pz{position:absolute;mix-blend-mode:screen;filter:blur(18px);background:linear-gradient(90deg,rgba(255,0,80,0) 0%,rgba(255,40,60,.85) 14%,rgba(255,190,30,.85) 30%,rgba(80,255,120,.8) 48%,rgba(30,200,255,.85) 66%,rgba(110,70,255,.85) 82%,rgba(220,40,255,0) 100%);}
.pz1{left:-140px;top:880px;width:1150px;height:150px;transform:rotate(-9deg);}
.pz2{left:-90px;top:36px;width:780px;height:92px;transform:rotate(5deg);}
.pz3{left:1360px;top:14px;width:640px;height:112px;transform:rotate(-14deg);}
.pz4{left:1420px;top:360px;width:780px;height:780px;border-radius:50%;filter:blur(5px);background:conic-gradient(from 210deg,#ff2a4a,#ffd23a,#4dff7a,#2ad4ff,#7a4dff,#ff2ad4,#ff2a4a);-webkit-mask-image:radial-gradient(circle,rgba(0,0,0,0) 60%,#000 63%,#000 67%,rgba(0,0,0,0) 70%);mask-image:radial-gradient(circle,rgba(0,0,0,0) 60%,#000 63%,#000 67%,rgba(0,0,0,0) 70%);}
.ngvig{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 74% 78% at 50% 46%,rgba(0,0,0,0) 46%,rgba(0,0,0,.5) 76%,rgba(0,0,0,.9) 100%);}
.ngt{position:absolute;left:0;width:1920px;text-align:center;font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;line-height:1;color:#F6F2EA;white-space:nowrap;letter-spacing:-.01em;}
.ngt span{display:inline-block;text-shadow:0 0 30px rgba(255,255,255,.42),0 0 72px rgba(255,236,210,.3),0 4px 18px rgba(0,0,0,.55);}
.ngimg{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;}
.pz5{left:-430px;top:250px;width:760px;height:760px;border-radius:50%;filter:blur(5px);background:conic-gradient(from 30deg,#ff2a4a,#ffd23a,#4dff7a,#2ad4ff,#7a4dff,#ff2ad4,#ff2a4a);-webkit-mask-image:radial-gradient(circle,rgba(0,0,0,0) 60%,#000 63%,#000 67%,rgba(0,0,0,0) 70%);mask-image:radial-gradient(circle,rgba(0,0,0,0) 60%,#000 63%,#000 67%,rgba(0,0,0,0) 70%);}
/* v13 the CNNfn article of July 9, 1998 (0:20), laid out in page pixels; the camera div maps them to the frame */
.cnn{position:absolute;left:0;top:0;width:780px;height:760px;}
.cnn img{position:absolute;left:0;top:70px;width:780px;height:690px;}
.cnhl{position:absolute;background:#FFD84D;mix-blend-mode:multiply;transform-origin:0 50%;}
.cnvig{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 80% 85% at 50% 50%,rgba(0,0,0,0) 55%,rgba(20,16,12,.26) 85%,rgba(20,16,12,.5) 100%);}
/* v15 merge chart: rounded black pills with a cyan/red channel split (after the user's reference) on a wide grid canvas */
.mgrid{position:absolute;background-color:#ECEAE5;background-image:linear-gradient(rgba(40,40,40,.09) 2px,transparent 2px),linear-gradient(90deg,rgba(40,40,40,.09) 2px,transparent 2px);background-size:72px 72px;}
.mgrid i{position:absolute;left:0;top:0;width:100%;height:100%;background:url("assets/tex/paper.jpg") 0 0/1920px 1080px repeat;mix-blend-mode:multiply;opacity:.55;}
.mpw{position:absolute;width:0;height:0;display:flex;align-items:center;justify-content:center;}
.mpill{flex:none;display:flex;align-items:center;justify-content:center;white-space:nowrap;background:#0b0b0b;color:#f6f5f1;height:118px;padding:0 92px;border-radius:50px;font-family:"Playfair Display",serif;font-style:italic;font-weight:600;font-size:84px;line-height:1;letter-spacing:-.005em;text-shadow:-2px 0 0 rgba(0,226,255,.78),2px 0 0 rgba(255,36,92,.72);box-shadow:-3px -2px 0 rgba(0,226,255,.85),3px 2px 0 rgba(255,36,92,.8),0 16px 32px rgba(0,0,0,.26);}
.mpill.sm{height:60px;padding:0 40px;border-radius:26px;font-size:36px;}
.mpill.lg{height:206px;padding:0 120px;border-radius:88px;font-size:150px;}
.mpill.logo{height:132px;padding:0 70px;border-radius:56px;}
.mpill img{display:block;height:66px;width:auto;}
/* v15 the Guardian page (the user's screenshot, 2x) */
.gdn{position:absolute;left:0;top:0;width:1905px;height:911px;background:#fff;}
.gdn img{position:absolute;left:0;top:0;width:1905px;height:911px;}
.gdhl{position:absolute;background:#F5DD12;mix-blend-mode:multiply;transform-origin:0 50%;}
.nfix{font-family:Inter,sans-serif;font-weight:800;letter-spacing:-.035em;}
/* v16: the in-scene words on the Bell frames carry the same white glow as the ink captions */
.ftx,.fbig{text-shadow:0 0 16px rgba(255,255,255,.95),0 0 40px rgba(255,255,255,.6);}
/* v16: the $6.7 billion figure on the merge canvas, set like the money captions */
.mprice{flex:none;position:relative;color:#141414;}
.pnum{display:block;font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;font-size:300px;line-height:1;letter-spacing:-.02em;white-space:nowrap;text-shadow:0 0 16px rgba(255,255,255,.95),0 0 40px rgba(255,255,255,.65);}
.ptail{position:absolute;right:0;bottom:-34px;font:700 64px/1 Almarai,sans-serif;letter-spacing:-.02em;white-space:nowrap;text-shadow:0 0 16px rgba(255,255,255,.95),0 0 40px rgba(255,255,255,.65);}
/* v17: the CRT clip at 0:03, portrait, framed at the centre over a blurred ghost of itself */
.crtghost{position:absolute;left:-190px;top:-110px;width:2300px;height:1294px;opacity:.36;mix-blend-mode:screen;}
.crtgv{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;}
.crtpan{position:absolute;left:555px;top:0;width:810px;height:1080px;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 10%,#000 90%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,0) 0%,#000 7%,#000 91%,rgba(0,0,0,0) 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 10%,#000 90%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,0) 0%,#000 7%,#000 91%,rgba(0,0,0,0) 100%);mask-composite:intersect;}
.crtv{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;}
/* v17: the light prism streaks on every B-roll clip - edges and corners only, clear of the captions */
.pzA{left:-90px;top:36px;width:780px;height:92px;transform:rotate(5deg);}
.pzB{left:1360px;top:14px;width:640px;height:112px;transform:rotate(-14deg);}
.pzC{left:1610px;top:420px;width:640px;height:104px;transform:rotate(-74deg);}
.pzD{left:-330px;top:560px;width:640px;height:104px;transform:rotate(80deg);}
/* v17: George Bell's name, a yellow marker sweeping behind each word */
.ftx .nhl{background-image:linear-gradient(#FFD84D,#FFD84D);background-repeat:no-repeat;background-position:0 58%;background-size:0% 82%;padding:0 .1em;margin:0 -.1em;}

/* v18: the price on the merge canvas in the serif of the $1,000,000 at 0:15 (Instrument Serif italic), dark ink, no glow */
.pnum2{display:block;font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;font-size:204px;line-height:1;letter-spacing:-.01em;font-variant-numeric:tabular-nums;white-space:nowrap;color:#141414;}
/* v20: the Excite page on a glowing screen in the dark (0:09, 0:24) */
.cwb{position:absolute;left:0;top:0;width:1920px;height:1080px;}
.cwghost{position:absolute;left:0;top:0;width:1920px;height:1080px;transform:scale(.97);transform-origin:50% 50%;opacity:.55;mix-blend-mode:screen;filter:blur(36px) saturate(1.6) brightness(1.1);}
.cwscr{position:absolute;left:0;top:0;width:1920px;height:1080px;transform:translate(192px,108px) scale(.8);transform-origin:0 0;border-radius:22px;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.65),0 0 150px rgba(170,200,255,.16);}
.cwcrt{position:absolute;left:0;top:0;width:1920px;height:1080px;background:repeating-linear-gradient(180deg,rgba(0,0,0,.15) 0px,rgba(0,0,0,.15) 2px,rgba(0,0,0,0) 2px,rgba(0,0,0,0) 5px),radial-gradient(ellipse 78% 72% at 50% 46%,rgba(0,0,0,0) 52%,rgba(0,0,0,.4) 100%);mix-blend-mode:multiply;}
.cwcrt::after{content:"";position:absolute;left:0;top:0;width:100%;height:100%;background:linear-gradient(118deg,rgba(255,255,255,.14) 0%,rgba(255,255,255,.04) 26%,rgba(255,255,255,0) 42%);mix-blend-mode:screen;}
.cwfx{position:absolute;left:0;top:0;width:1920px;height:1080px;}
/* v20: the merge in the user's reference design (0:53) */
.mbg2{position:absolute;background:radial-gradient(ellipse 30% 40% at 30% 45%,rgba(255,252,247,.22),rgba(255,252,247,0) 70%),radial-gradient(ellipse 30% 40% at 62% 45%,rgba(255,252,247,.18),rgba(255,252,247,0) 70%),#f0dccf;}
.mword{position:absolute;width:0;height:0;display:flex;align-items:center;justify-content:center;}
.mword span{flex:none;display:inline-block;font:700 86px/1 Heros,"Helvetica Neue",Arial,sans-serif;color:#1b1a19;letter-spacing:-.012em;white-space:nowrap;text-shadow:0 2px 5px rgba(0,0,0,.16);}
.mfr{position:absolute;transform-origin:50% 50%;}
.mfr .mdot{position:absolute;width:9px;height:9px;background:#1d1c1b;box-shadow:-1.5px 0 0 rgba(30,110,255,.5),1.5px 0 0 rgba(255,70,40,.5);}
.mfr .mside{position:absolute;top:8px;bottom:8px;width:0;border-left:1.5px dotted rgba(28,27,26,.3);}
.mcard{position:absolute;display:flex;align-items:center;justify-content:center;border-radius:8px;background:radial-gradient(ellipse 80% 130% at 50% 38%,#2d2a29 0%,#1c1a19 68%,#131110 100%);box-shadow:0 12px 22px rgba(0,0,0,.38),0 2px 4px rgba(0,0,0,.5),-2px 0 0 rgba(40,100,255,.35),2px 0 0 rgba(255,190,40,.3);}
.mlogo{display:flex;align-items:center;font:italic 700 40px/1 Heros,"Helvetica Neue",Arial,sans-serif;color:#f3efe8;letter-spacing:-.01em;white-space:nowrap;text-shadow:0 0 10px rgba(255,255,255,.18);}
.mlogo .at{display:inline-flex;align-items:center;justify-content:center;width:50px;height:50px;margin:0 3px 0 5px;border-radius:50%;background:radial-gradient(circle at 42% 38%,#f2603f 0%,#df3a24 60%,#c42c19 100%);box-shadow:inset 0 0 0 3px #d9361f,inset 0 0 0 5px rgba(255,255,255,.88),0 0 16px rgba(240,80,40,.6);font:700 33px/1 Heros,"Helvetica Neue",Arial,sans-serif;color:#fff;}
.mvig2{position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(180deg,rgba(10,7,5,.72) 0%,rgba(10,7,5,.3) 9%,rgba(10,7,5,0) 17%,rgba(10,7,5,0) 86%,rgba(10,7,5,.35) 100%);box-shadow:inset 0 0 230px 105px rgba(14,10,7,.9),inset 0 0 50px 14px rgba(8,6,4,.92);}
.mleak{position:absolute;mix-blend-mode:screen;filter:blur(24px) saturate(1.5);opacity:1;background:linear-gradient(90deg,rgba(255,30,60,0) 0%,rgba(255,40,40,1) 10%,rgba(255,170,30,1) 27%,rgba(130,235,70,.95) 45%,rgba(40,170,255,.95) 63%,rgba(150,60,255,.95) 81%,rgba(210,40,255,0) 100%);}
.pnum3{display:block;font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;font-size:150px;line-height:1;letter-spacing:-.01em;white-space:nowrap;color:#1b1a19;}
/* v23: the text flash (one inverted frame, then two - the caption flicker) on "1999" in the opener and on the $6.7B figure */
.opB{position:relative;isolation:isolate;}
.opB[data-f="1"]{color:#141414;}
.opB[data-f="1"]::before{content:"";position:absolute;left:var(--il,0px);right:var(--ir,0px);top:var(--it,0px);bottom:var(--ib,0px);background:#f3efe8;z-index:-1;box-shadow:0 0 26px 6px rgba(255,248,238,.7);}
.mprice{isolation:isolate;}
.mprice[data-f="1"] .pnum3{color:#F1ECE4;}
.mprice[data-f="1"]::before{content:"";position:absolute;left:var(--il,0px);right:var(--ir,0px);top:var(--it,0px);bottom:var(--ib,0px);background:#141414;z-index:-1;box-shadow:0 0 22px rgba(0,0,0,.35);}
/* v21: the opener in the cursive */
.opc{flex:none;display:flex;flex-direction:column;align-items:flex-start;font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;color:#f3efe8;white-space:nowrap;line-height:1;}
.opL span{display:inline-block;}
.opB{display:inline-block;letter-spacing:-.01em;transform-origin:50% 50%;}
/* v21: the Excite@Home office under the logo card in the merge, sitting in the paper */
.mphoto{position:absolute;overflow:hidden;mix-blend-mode:multiply;-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 9%,#000 91%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,0) 0%,#000 12%,#000 82%,rgba(0,0,0,0) 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 9%,#000 91%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,0) 0%,#000 12%,#000 82%,rgba(0,0,0,0) 100%);mask-composite:intersect;}
.mphoto img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;}
/* v17: a soft shade on the left of Bell's office clip, under the quote */
.qshade{position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(90deg,rgba(8,6,5,.62) 0%,rgba(8,6,5,.44) 36%,rgba(8,6,5,.1) 58%,rgba(8,6,5,0) 68%);}
.headline{position:absolute;left:250px;top:330px;width:1420px;font:700 104px/1.08 Almarai,sans-serif;color:#111;letter-spacing:-.02em;}
.kicker{position:absolute;left:252px;top:260px;font:700 30px Almarai,sans-serif;color:#7a7a7a;letter-spacing:.02em;}
.rule{position:absolute;left:252px;top:700px;width:420px;height:4px;background:#111;}
.hls{font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;font-size:1.3em;letter-spacing:0;margin-left:.16em !important;}
.dg{letter-spacing:-.17em;margin-right:.1em;}
.hlw{background-image:linear-gradient(${HL},${HL});background-repeat:no-repeat;background-position:0 62%;background-size:0% 78%;padding:0 .08em;margin:0 -.08em;}
/* framed person (Koum-reel style): square photo, four corner marks */
.frm{position:absolute;transform-origin:50% 50%;}
.frm .ph{position:absolute;inset:0;overflow:hidden;background:#222;box-shadow:0 6px 18px rgba(0,0,0,.18);}
.frm .ph img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;}
.frm .dot{position:absolute;width:10px;height:10px;border-radius:50%;background:#1a1a1a;}
.ftx{position:absolute;font:700 54px/1 Almarai,sans-serif;color:${INK};letter-spacing:-.02em;}
.ftx span,.fbig span{display:inline-block;}
.fbig{position:absolute;font:700 118px/.96 Almarai,sans-serif;color:${INK};letter-spacing:-.03em;text-transform:uppercase;}
.fbig span[data-f="1"],.ftx span[data-f="1"]{background:${INK};color:#fff;text-shadow:0 0 14px rgba(255,255,255,.95),0 0 30px rgba(255,255,255,.6);padding:0 .06em;margin:0 -.06em;}
.obj{position:absolute;filter:drop-shadow(0 14px 18px rgba(0,0,0,.28));}
.tag{position:relative;display:inline-block;background:#F4EFE3;color:#141414;font:700 48px Almarai,sans-serif;padding:16px 30px 16px 54px;border-radius:12px;letter-spacing:-.02em;}
.tag i{position:absolute;left:18px;top:30px;width:16px;height:16px;border-radius:50%;background:#cfc8b8;display:block;}
.w98{display:inline-block;font:30px Arial,sans-serif;color:#000;background:#d4d0c8;border:4px solid;border-color:#fff #404040 #404040 #fff;padding:10px 26px;}
/* Alphabet flowchart */
.fcb{position:absolute;display:flex;align-items:center;justify-content:center;color:#fff;font:700 44px Almarai,sans-serif;letter-spacing:-.02em;box-shadow:0 10px 22px rgba(0,0,0,.18);}
.fcd{position:absolute;width:300px;text-align:center;font:700 22px Almarai,sans-serif;color:#555;}
/* quote-block CTA */
.qwrap{position:absolute;left:0;top:0;width:1920px;height:1080px;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.qblock{position:relative;font:700 96px/1.02 Almarai,sans-serif;color:${LIGHT};letter-spacing:-.025em;}
.ql{white-space:nowrap;}
.qw{display:inline-block;text-shadow:0 0 22px rgba(255,248,238,.45),0 0 60px rgba(255,248,238,.22),0 3px 14px rgba(0,0,0,.55);padding:0 .04em;margin:0 -.04em;}
.qw[data-f="1"]{background:${LIGHT};color:${INK};text-shadow:none;box-shadow:0 0 26px 6px rgba(255,248,238,.7);}
.qlogo{height:.8em;vertical-align:-.06em;margin-left:.2em;filter:drop-shadow(0 0 18px rgba(255,248,238,.45));}
.qm{position:absolute;line-height:0;}
.qimg{display:block;width:92px;height:auto;filter:drop-shadow(0 0 16px rgba(255,248,238,.5)) drop-shadow(0 0 40px rgba(255,248,238,.22));}
.qflip{transform:rotate(180deg);}
.qcta{margin-top:150px;font:700 54px Almarai,sans-serif;color:${LIGHT};opacity:.92;letter-spacing:-.02em;}
`;
const CURSOR_SVG = `<svg viewBox="0 0 17 25" width="34" height="50"><path d="M1 1 L1 20 L5.5 15.5 L8.6 23 L11.6 21.7 L8.6 14.5 L15 14.5 Z" fill="#fff" stroke="#000" stroke-width="1.3"/></svg>`;
const BIG_CURSOR = `<svg viewBox="0 0 17 25" width="78" height="115"><path d="M1 1 L1 20 L5.5 15.5 L8.6 23 L11.6 21.7 L8.6 14.5 L15 14.5 Z" fill="#fff" stroke="#000" stroke-width="1.1"/></svg>`;
const FLOPPY = `<svg viewBox="0 0 100 100" width="190" height="190"><rect x="4" y="4" width="92" height="92" rx="4" fill="#2b2d31"/><rect x="24" y="4" width="50" height="31" fill="#c9ccd1"/><rect x="56" y="9" width="10" height="21" fill="#2b2d31"/><rect x="15" y="49" width="70" height="43" rx="2" fill="#f3f1ea"/><line x1="21" y1="61" x2="79" y2="61" stroke="#c8c3b8" stroke-width="1.6"/><line x1="21" y1="71" x2="79" y2="71" stroke="#c8c3b8" stroke-width="1.6"/><line x1="21" y1="81" x2="79" y2="81" stroke="#c8c3b8" stroke-width="1.6"/><rect x="88" y="88" width="5" height="5" fill="#111"/></svg>`;
const CRT = `<svg viewBox="0 0 120 110" width="250" height="229"><rect x="6" y="4" width="108" height="82" rx="8" fill="#e3dccb" stroke="#bfb6a2" stroke-width="2"/><rect x="16" y="12" width="88" height="62" rx="6" fill="#1d2a2a"/><rect x="20" y="16" width="80" height="54" rx="4" fill="#2f6f6a" opacity=".55"/><text x="60" y="49" text-anchor="middle" font-family="Times New Roman" font-size="15" fill="#e9f5ef" opacity=".9">Google!</text><rect x="40" y="86" width="40" height="8" fill="#d2c9b5"/><rect x="24" y="94" width="72" height="10" rx="3" fill="#e3dccb" stroke="#bfb6a2" stroke-width="2"/><circle cx="100" cy="80" r="2" fill="#6c6"/></svg>`;
const EXCITE_RAW = fs.readFileSync(path.join(ROOT, "assets/pages/excite.frag.html"), "utf8");
const excitePage = (id) => EXCITE_RAW.replace("<input name=search size=30>&nbsp;<input type=submit value=Search>", `<span class="hlt" id="${id}-hlx"><input name=search size=30>&nbsp;<input type=submit value=Search></span>`);
function googlePage(id, typed = "") {
  const chars = [...typed].map((c, k) => `<span id="${id}-c${k}" style="opacity:0">${esc(c)}</span>`).join("");
  return `<div class="gpage"><img src="assets/img/google_1999.jpg" width="351" height="113" alt="Google!"><br>
<table><tr><td colspan="3" style="background:#EEEEEE;padding:8px 0"><span class="hlt" id="${id}-hlg">Search the web using Google!</span><br>
<span class="ginput">${chars}<span class="caret"></span></span><br>
<span class="gbtn">Google Search</span><span class="gbtn">I'm feeling lucky</span></td></tr>
<tr><td width="37%" style="background:#7EE5DA;padding:14px 0">Special Searches<br><a href="#">Stanford Search</a><br><a href="#">Linux Search</a></td>
<td style="background:#70CCC2;font-size:13px;padding:8px 0"><a href="#">Why use Google!</a><br><a href="#">Press about Google!</a><br><a href="#">Help!</a><br><a href="#">Company Info</a><br><a href="#">Jobs at Google</a><br><a href="#">Google! Logos</a><br><a href="#">Making Google! the Default</a></td>
<td style="background:#62B3AA;font-size:13px;padding:8px 0">Get Google!<br>updates monthly:<br><span class="ginput" style="width:170px;font-size:13px">your e-mail</span><br><span class="gbtn">Subscribe</span> <a href="#">Archive</a></td></tr></table>
<p style="font-size:13px;margin-top:14px">Copyright &copy;1999 Google Inc.</p></div>`;
}
const winChrome = (page, W, Hh, pw, inner, extra = "") => {
  const g = page === "google", sc = r3((W - 8) / pw);
  return `<div class="win-title"><span>&#9632;</span>${g ? "Google! - Netscape" : "Excite - Netscape"}<span class="bx"><i>_</i><i>&#9633;</i><i class="xb">&#215;</i></span></div>
<div class="win-tools"><b>Back</b><b>Forward</b><b>Reload</b><b>Home</b><b>Search</b><b>Netscape</b><b>Print</b><b>Security</b><b>Stop</b></div>
<div class="win-url">Location: <span class="f" data-layout-allow-occlusion>${g ? "http://www.google.com/" : "http://www.excite.com/"}</span></div>
<div class="win-page" style="top:98px;height:${Hh - 106}px"><div class="pscale" style="transform:scale(${sc});width:${pw}px">${inner}</div>${extra}</div>`;
};

// ---------- scenes ----------
class Scene {
  constructor(id, t0, t1) { Object.assign(this, { id, t0: M(t0), t1: M(t1), h: [], j: [], n: 0, z: 1, shots: [] }); }
  L(t) { return r3(M(t) - this.t0); }
  D(a, b) { return r3(M(b) - M(a)); }
  nid(p) { return `${this.id}-${p}${++this.n}`; }
  wrap(cls, a, b, inner) {
    if (cls !== "void") (this.covers = this.covers || []).push([M(a), M(b)]);
    const id = this.nid("c");
    this.h.push(`<div id="${id}" class="clip shot ${cls}" data-start="${this.L(a)}" data-duration="${this.D(a, b)}" data-track-index="${this.z}" style="z-index:${this.z++}"><div class="mv" id="${id}-m">${inner(id)}</div></div>`);
    return id;
  }
  void(a, b, inner = () => "") { (this.voids = this.voids || []).push([M(a), M(b)]); return this.wrap("void", a, b, inner); }
  clean(a, b, inner = () => "") { return this.wrap("clean", a, b, inner); }
  paper(a, b, inner = () => "") { return this.wrap("paper", a, b, inner); }
  grid(a, b, inner = () => "") { return this.wrap("", a, b, (id) => `<div class="gridbg"></div><div class="gridtex"></div>${inner(id)}`); }
  drift(sel, a, b, amp = 110, sc = 1.16) { this.j.push(`tl.fromTo("${sel}",{x:${-amp},scale:${sc}},{x:${amp},scale:${sc},duration:${this.D(a, b)},ease:dft(${this.D(a, b)})},${this.L(a)});`); }
  video(name, a, b, o = {}) {
    const id = this.nid("v"), st = this.L(a), du = this.D(a, b); if (!o.noPunch) this.shots.push({ sel: `#${id}-m`, a: st, b: r3(st + du) }); (this.covers = this.covers || []).push([M(a), M(b)]);
    // v17: the subtle curated finish on every clip - its grade merged with the light treatment, two faint prism streaks
    // at the edges that breathe on eased steps, and a slow stepped zoom-out under the drift
    // v18: o.noPunch keeps a clip out of the caption punch-ins (no sudden 8% step in); o.zs = [from, to] sets a gentler
    // zoom-out (the talking heads, where the default one read as the picture snapping)
    const pz = [["pzA", "pzC"], ["pzB", "pzD"], ["pzA", "pzB"]][(this.n + this.id.charCodeAt(2)) % 3];
    this.h.push(`<div class="shot" id="${id}-m" style="z-index:${this.z}"><div class="kb" id="${id}-k">
<video id="${id}" class="clip cover" src="assets/vid/${name}.mp4" data-start="${st}" data-duration="${du}" data-media-start="${o.ms || 0}"${o.rate ? ` data-playback-rate="${o.rate}"` : ""} data-track-index="${this.z}" data-color-grading='${LITE(o.grade)}' muted playsinline></video></div>
<div id="${id}-d" class="clip dim" data-start="${st}" data-duration="${du}" data-track-index="${this.z}" style="opacity:${o.dim ?? 0.3}"></div>
<div id="${id}-x" class="clip shot" data-start="${st}" data-duration="${du}" data-track-index="${this.z}" data-layout-allow-occlusion><div class="pz ${pz[0]}" id="${id}-p0" style="opacity:.28"></div><div class="pz ${pz[1]}" id="${id}-p1" style="opacity:.22"></div></div>
<div id="${id}-g" class="clip bgrain" data-start="${st}" data-duration="${du}" data-track-index="${this.z++}"></div></div>`);
    const h2 = r3(du / 2), amp = o.amp ?? 120, zs = o.zs || [1.26, 1.16];
    this.j.push(`tl.fromTo("#${id}-p0",{opacity:.28},{opacity:.46,duration:${h2},ease:cio(${h2})},${st});tl.to("#${id}-p0",{opacity:.28,duration:${h2},ease:cio(${h2})},${r3(st + h2)});`);
    this.j.push(`tl.fromTo("#${id}-p1",{opacity:.22},{opacity:.38,duration:${h2},ease:cio(${h2})},${st});tl.to("#${id}-p1",{opacity:.22,duration:${h2},ease:cio(${h2})},${r3(st + h2)});`);
    // v23: the drift is slow and smooth on every clip (it ran on 8 fps steps and spent itself in the first moments, which
    // read as shake and as a zoom that stops): a short stretch of an easeOutExpo, so the picture keeps moving to the cut.
    // It ends on the framing each clip had (x = amp, scale = zs[1]); the travel is capped by the clip's length.
    const tr = r3(Math.min(2 * amp, 46 * du)), zt = r3(Math.min(zs[0] - zs[1], 0.03 * du));
    this.j.push(`tl.fromTo("#${id}-k",{x:${r3(amp - tr)},scale:${r3(zs[1] + zt)}},{x:${amp},scale:${zs[1]},duration:${du},ease:sxoP(0.16)},${st});`);
    return id;
  }
  photo(src, a, b, o = {}) {
    return this.wrap("", a, b, (id) => { this.shots.push({ sel: `#${id}-m`, a: this.L(a), b: this.L(b) }); this.drift(`#${id}-k`, a, b, 120, 1.18); return `<div class="kb" id="${id}-k"><img class="cover" src="assets/img/${src}" style="object-position:${o.pos || "50% 50%"}"></div><div class="dim" style="opacity:${o.dim ?? 0.25}"></div><div class="bgrain"></div>`; });
  }
  win(a, b, o) {
    const g = o.page === "google";
    return this.wrap("", a, b, (id) => {
      const inner0 = `<div class="pscroll" id="${id}-s">${g ? googlePage(id, o.typed || "") : excitePage(id)}</div>`;
      const inner = o.zoom ? `<div style="transform:scale(${o.zoom});transform-origin:${o.origin || "0 0"}">${inner0}</div>` : inner0;
      let cur = "";
      if (o.cursor) {
        cur = `<div class="cursor" id="${id}-cur">${CURSOR_SVG}</div>`;
        const p = o.cursor;
        this.j.push(`tl.set("#${id}-cur",{x:${p[0][1]},y:${p[0][2]}},${this.L(a)});`);
        for (let k = 1; k < p.length; k++) this.j.push(`tl.to("#${id}-cur",{x:${p[k][1]},y:${p[k][2]},duration:${this.D(p[k - 1][0], p[k][0])},ease:vox(${this.D(p[k - 1][0], p[k][0])})},${this.L(p[k - 1][0])});`);
        (o.clicks || []).forEach((t) => this.j.push(`tl.to("#${id}-cur",{scale:0.82,duration:0.067,yoyo:true,repeat:1,transformOrigin:"0 0",ease:"steps(1)"},${this.L(t)});`));
      }
      if (o.typed) { const n = [...o.typed].length, [ta, tb] = o.typeAt; for (let k = 0; k < n; k++) this.j.push(`tl.set("#${id}-c${k}",{opacity:1},${r3(this.L(ta) + (this.L(tb) - this.L(ta)) * k / n)});`); }
      if (o.scroll) this.j.push(`tl.fromTo("#${id}-s",{y:${o.scroll[0]}},{y:${o.scroll[1]},duration:${this.D(a, b)},ease:vox(${this.D(a, b)})},${this.L(a)});`);
      (o.hl || []).forEach(([which, t]) => this.j.push(`tl.fromTo("#${id}-${which === "excite" ? "hlx" : "hlg"}",{backgroundSize:"0% 92%"},{backgroundSize:"100% 92%",duration:0.3,ease:voxOut(0.3)},${this.L(t)});`));
      if (!o.noDrift) this.drift(`#${id}-k`, a, b, o.amp ?? 70, 1.1);
      let wc = "";
      if (o.winCursor) {
        // a cursor on the window itself (not inside the page), so it can reach the title bar
        const p = o.winCursor; wc = `<div class="cursor" id="${id}-wc">${CURSOR_SVG}</div>`;
        this.j.push(`tl.set("#${id}-wc",{x:${p[0][1]},y:${p[0][2]}},${this.L(a)});`);
        for (let k = 1; k < p.length; k++) { const d = this.D(p[k - 1][0], p[k][0]); this.j.push(`tl.to("#${id}-wc",{x:${p[k][1]},y:${p[k][2]},duration:${d},ease:dft(${d})},${this.L(p[k - 1][0])});`); }
        (o.wclicks || []).forEach((t) => this.j.push(`tl.to("#${id}-wc",{scale:0.82,duration:0.067,yoyo:true,repeat:1,transformOrigin:"0 0",ease:"steps(1)"},${this.L(t)});`));
      }
      if (o.screen) {
        // the glow copy: the same page with its ids renamed (so tweens never reach it), following the scroll
        const ghostInner = inner.replace(/ id="/g, ' id="g-');
        if (o.scroll) this.j.push(`tl.fromTo("#g-${id}-s",{y:${o.scroll[0]}},{y:${o.scroll[1]},duration:${this.D(a, b)},ease:vox(${this.D(a, b)})},${this.L(a)});`);
        if (o.push !== false) this.j.push(`tl.fromTo("#${id}-k",{scale:1},{scale:1.025,duration:${this.D(a, b)},ease:cio(${this.D(a, b)})},${this.L(a)});`);
        return SCREEN(id, o, winChrome(o.page, 1920, 1080, o.pw || (g ? 1280 : 1600), inner, cur), winChrome(o.page, 1920, 1080, o.pw || (g ? 1280 : 1600), ghostInner, ""), wc);
      }
      return `<div class="kb" id="${id}-k"><div class="win" style="left:0;top:0;width:1920px;height:1080px">${winChrome(o.page, 1920, 1080, o.pw || (g ? 1280 : 1600), inner, cur)}</div>${wc}</div><div class="bgrain" style="opacity:.4"></div>`;

    });
  }
  // the full 1920x1080 browser window, uniformly scaled down to width w (chrome included), so it can zoom back up 1:1
  miniWin(page, w) {
    const g = page === "google", id = this.nid("m"), k = w / 1920;
    return `<div data-layout-ignore style="position:relative;width:${w}px;height:${r3(1080 * k)}px;overflow:hidden"><div class="win" style="left:0;top:0;width:1920px;height:1080px;transform:scale(${r3(k)});transform-origin:0 0;box-shadow:none">${winChrome(page, 1920, 1080, g ? 1280 : 1600, `<div class="pscroll">${g ? googlePage(id) : excitePage(id)}</div>`)}</div></div>`;
  }
  polaroid(list, at, o) {
    const id = this.nid("p");
    const media = o.html ? o.html : `<img src="assets/img/${o.src}" style="object-position:${o.pos || "50% 50%"};${o.fit ? `object-fit:${o.fit};background:#fff` : ""}">`;
    list.push(`<div id="${id}" class="pol" style="left:${o.cx - o.w / 2}px;top:${o.cy - o.h / 2}px;width:${o.w}px;height:${o.h}px"><div class="ph">${media}</div><div class="age" id="${id}-age"></div></div>`);
    const d = o.rise || 0.55;
    this.j.push(`tl.fromTo("#${id}",{y:${1150 - (o.cy - o.h / 2)},rotation:${(o.r || 0) + 7}},{y:0,rotation:${o.r || 0},duration:${d},ease:voxOut(${d})},${this.L(at)});`);
    return id;
  }
  raw(a, b, html) { const id = this.nid("r"); this.h.push(`<div id="${id}" class="clip shot" data-start="${this.L(a)}" data-duration="${this.D(a, b)}" data-track-index="${this.z}" style="z-index:${this.z++}">${html(id)}</div>`); return id; }
  js(c) { this.j.push(c); }
  write() {
    const dur = r3(this.t1 - this.t0);
    for (const [va, vb] of this.voids || []) { let segs = [[va, vb]]; for (const [ca, cb] of this.covers || []) segs = segs.flatMap(([x, y]) => (cb <= x || ca >= y) ? [[x, y]] : [[x, Math.min(y, ca)], [Math.max(x, cb), y]].filter(([p, q]) => q - p > 0.05)); segs.forEach((g) => VOIDS.push(g)); }
    if (["s14", "s19"].includes(this.id)) this.h = this.h.map((x) => x.replace(/class="clip shot /g, 'data-layout-allow-occlusion class="clip shot '));
    this.h = this.h.map((x) => x.replace(/<div class="bgrain"(?! data-layout-allow-occlusion)/g, '<div class="bgrain" data-layout-allow-occlusion'));
    // v14 punch-ins: on each caption's big word the B-roll shot under it steps in 8%, the next one steps back out
    { const seen = new Map();
      for (const t of []) {   // v20: no punch-ins anywhere - the step-in on a caption's big word read as a zoom glitch
        const lt = r3(t - this.t0); if (lt < 0.25 || lt > dur - 0.25) continue;
        const sh = this.shots.find((x) => lt >= x.a + 0.22 && lt < x.b - 0.22); if (!sh) continue;
        const k = (seen.get(sh.sel) || 0) + 1; seen.set(sh.sel, k);
        this.j.push(`tl.set("${sh.sel}",{scale:${k % 2 ? 1.08 : 1}},${lt});`);
      } }
    let seed = this.id.charCodeAt(1) * 977 + this.id.charCodeAt(2) * 31, g = "";
    const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
    for (let f = 0; f < dur * FPS; f += 2) g += `tl.set(".bgrain",{backgroundPosition:"${-Math.round(rnd() * 480)}px ${-Math.round(rnd() * 320)}px"},${r3(f / FPS)});`;
    fs.writeFileSync(path.join(ROOT, "compositions", `${this.id}.html`), `<template>
<style>${FONTFACE}${BASE_CSS}</style>
<div id="root" data-composition-id="${this.id}" data-width="1920" data-height="1080" data-layout-allow-overlap data-layout-allow-overflow>
${this.h.join("\n")}
</div>
<script>
${EASE_JS}
const tl = gsap.timeline({ paused: true });
${this.j.join("\n")}
${g}
tl.set({}, {}, ${dur});
window.__timelines["${this.id}"] = tl;
</script>
</template>`);
  }
}
const scenes = [];
const S = (id, t0, t1, fn) => { const s = new Scene(id, t0, t1); fn(s); s.write(); scenes.push(s); };
function cleanLogo(s, a, b, logos) {
  s.clean(a, b, (id) => logos.map(([src, w, cy, at], k) => {
    s.js(riseUp(`#${id}-l${k}`, s.L(at), 0.42, 40));
    return `<div id="${id}-l${k}" style="position:absolute;left:${960 - w / 2}px;top:${cy}px;width:${w}px"><img src="assets/img/${src}" style="width:${w}px;display:block"></div>`;
  }).join(""));
}
// a framed portrait with four corner marks; size = outer box, dots sit 20px outside the corners
const frameHTML = (id, cx, cy, w, h, imgs) => `<div class="frm" id="${id}" style="left:${cx - w / 2}px;top:${cy - h / 2}px;width:${w}px;height:${h}px"><div class="ph">${imgs.map((src, k) => `<img id="${id}-i${k}" src="assets/img/${src}" style="opacity:${k === 0 ? 1 : 0}">`).join("")}</div>
<i class="dot" style="left:-25px;top:-25px"></i><i class="dot" style="right:-25px;top:-25px"></i><i class="dot" style="left:-25px;bottom:-25px"></i><i class="dot" style="right:-25px;bottom:-25px"></i></div>`;

// ---------- v10 helpers: clips timed in scene-local seconds on the new clock ----------
Scene.prototype.wrapL = function (cls, a, b, inner) {
  const id = this.nid("c");
  this.h.push(`<div id="${id}" class="clip shot ${cls}" data-start="${r3(a)}" data-duration="${r3(b - a)}" data-track-index="${this.z}" style="z-index:${this.z++}"><div class="mv" id="${id}-m">${inner(id)}</div></div>`);
  return id;
};
const V9SFX = [], V10FLASH = [];   // sound cues and white flashes the v10 scenes place, in seconds on the new clock
const pk = { whoosh: 0.162, "whoosh-low": 0.198, "whoosh-high": 0.135, "whoosh-short": 0.12, pop: 0.12 };
const cue = (file, t, vol, d) => V9SFX.push({ file, st: r3(Math.max(0, t - (pk[file] || 0) + 1 / FPS)), d, vol });

// S01 opener (v21) "In early 1999": the cursive, animated after the user's type reference (a 2 s clip, measured frame by
// frame): the lead words fade in one after the other (~0.2 s each, on the voice), then the big word arrives blurred and
// pale, slides in a little from the right and sharpens on a long easeOutExpo; the whole block drifts smaller the whole
// time; it leaves on a quick blur-fade, the small line first. Everything is smooth (no 8 fps steps, no static flash, no
// RGB punch) - the user asked for it not to feel quick, jittery or glitchy.
S("s01", 0, 2.03, (s) => {
  const E = r3(s.t1 - s.t0), tw = [M(0.07), M(0.26), M(0.6)], tOut = r3(E - 0.21);
  s.wrapL("opv", 0, E, (id) => {
    const SB = 380, SL = 138, LS = -0.01, G = 30;
    const Bi = ink(FMO.layout("1999", SB, LS), SB), Li = ink(FMO.layout("In early", SL, 0), SL), W = FMO.layout("1999", SB, LS).width;
    // the lead line sits G px (ink to ink) above the year, its ink flush with the year's left edge
    const BO1 = 0.5 + (FMO.win.asc - FMO.win.desc) / (2 * FMO.upm);   // baseline from the top of a line-height:1 box
    const mt = r3(G - (BO1 * SB - Bi.top) - (SL - (BO1 * SL - Li.bot))), ml = r3(Bi.left - Li.left);
    s.js(`tl.fromTo("#${id}-k",{scale:1.12},{scale:1,duration:${E},ease:sxo(${E})},0);`);
    tw.slice(0, 2).forEach((t, k) => s.js(`tl.fromTo("#${id}-w${k}",{opacity:0},{opacity:1,duration:0.22,ease:sxo(0.22)},${r3(t)});`));
    s.js(`tl.fromTo("#${id}-y",{opacity:0,x:${r3(W * 0.11)},filter:"blur(11px)"},{opacity:1,x:0,filter:"blur(0px)",duration:${r3(tOut - tw[2])},ease:sxo(${r3(tOut - tw[2])})},${r3(tw[2])});`);
    s.js(`tl.to("#${id}-l",{opacity:0,filter:"blur(8px)",duration:0.14,ease:scio(0.14)},${tOut});`);
    s.js(`tl.to("#${id}-y",{opacity:0,scale:0.97,filter:"blur(12px)",duration:0.16,ease:scio(0.16)},${r3(tOut + 0.05)});`);
    s.js(flick(`#${id}-y`, 1.08));   // v23: the text flash on "1999" (the reviewer's note at 0:01)
    return `<div class="opbg"></div><div class="opdot"></div>
<div class="opk" id="${id}-k"><div class="opc"><div class="opL" id="${id}-l" style="font-size:${SL}px;margin-left:${ml}px"><span id="${id}-w0">In</span> <span id="${id}-w1">early</span></div><div class="opB" id="${id}-y" data-f="0" style="font-size:${SB}px;margin-top:${mt}px;${inkVars(FMO, "1999", SB, LS, BO1)};--il:${Math.round(Bi.left - SB * 0.07)}px;--ir:${Math.round(W - Bi.right - SB * 0.07)}px">1999</div></div></div>
<div class="bgrain" style="opacity:.35"></div>`;
  });
});
// S02 Larry Page and Sergey Brin: on the wide shot the mosaic resolves cell by cell (three steps of detail each),
// then the camera lands on each founder as he is named, his name set beside him
S("s02", 2.03, 3.95, (s) => {
  s.wrap("", 2.03, 3.95, (id) => {
    const order = [3, 5, 1, 7, 4, 0, 8, 2, 6];
    let cells = "";
    for (let c = 0; c < 9; c++) {
      const cx = (c % 3) * 640, cy = Math.floor(c / 3) * 360, t1 = r3(0.05 + order.indexOf(c) * 0.025);
      const im = (src, key, vis) => `<img id="${id}-c${c}${key}" src="assets/img/${src}" style="position:absolute;left:${-cx}px;top:${-cy - 120}px;width:1920px;height:1337px;opacity:${vis}">`;
      cells += `<div id="${id}-c${c}" style="position:absolute;left:${cx}px;top:${cy}px;width:640px;height:360px;overflow:hidden">${im("pb_px_a.jpg", "a", 1)}${im("pb_px_b.jpg", "b", 0)}${im("pb_px_c.jpg", "c", 0)}</div>`;
      s.js(`tl.set("#${id}-c${c}b",{opacity:1},${t1});tl.set("#${id}-c${c}c",{opacity:1},${r3(t1 + 0.067)});tl.set("#${id}-c${c}",{opacity:0},${r3(t1 + 0.134)});`);
    }
    const done = r3(0.05 + 8 * 0.025 + 0.134);
    const lines = [640, 1280].map((x) => `<div class="gl" style="position:absolute;left:${x - 1}px;top:0;width:3px;height:1080px;background:rgba(15,15,18,.8)"></div>`).join("") + [360, 720].map((y) => `<div class="gl" style="position:absolute;top:${y - 1}px;left:0;height:3px;width:1920px;background:rgba(15,15,18,.8)"></div>`).join("");
    s.js(`tl.set("#${id}-k .gl",{opacity:0.4},${r3(done - 0.034)});tl.set("#${id}-k .gl",{opacity:0},${done});`);
    const tP = r3(WT("Page", 2.34) - s.t0), tS = r3(WT("Sergey", 3.07) - s.t0), tB = r3(WT("Brin", 3.51) - s.t0), z0 = r3(done - 0.02);
    // camera (origin top-left): wide while the mosaic resolves -> Larry (face at 649,483) -> Sergey (face at 1165,521)
    s.js(`tl.fromTo("#${id}-k",{x:-77,y:-43,scale:1.08},{x:-200,y:-180,scale:1.55,duration:0.6,ease:dft(0.6)},${z0});`);
    s.js(`tl.to("#${id}-k",{x:-1056,y:-220,scale:1.55,duration:0.6,ease:dft(0.6)},${r3(tS - 0.06)});`);
    s.js(riseIn(`#${id}-l1`, r3(z0 + 0.04), 0.34, 40) + riseIn(`#${id}-l2`, r3(Math.max(z0 + 0.1, tP - 0.03)), 0.34, 30));
    s.js(`tl.to(["#${id}-l1","#${id}-l2"],{opacity:0,filter:"blur(14px)",duration:0.13,ease:xo(0.13)},${r3(tS - 0.1)});`);
    // v18: as "Larry" lands the room darkens and loses its colour - the photo's own grade (exposure down, saturation down,
    // build/grade_pb_dim.json) eased in through the seek-safe intensity property - while Larry and Sergey keep their own
    // colour: a cut-out of the two of them (hyperframes remove-background, the matte tidied) sits over the photo
    const tD = r3(z0 + 0.04);
    s.js(`tl.set("#${id}-cut",{opacity:1},${tD});tl.fromTo("#${id}-bg",{"--hf-color-grading-intensity":0},{"--hf-color-grading-intensity":1,duration:0.5,ease:cio(0.5)},${tD});`);
    s.js(riseIn(`#${id}-s1`, r3(tS + 0.1), 0.34, 40) + riseIn(`#${id}-s2`, r3(tB - 0.03), 0.34, 30));
    const names = `<div class="nm" style="left:930px;top:360px"><div class="n1" id="${id}-l1">Larry</div><div class="n2" id="${id}-l2">Page</div></div>
<div class="nm" style="right:${1920 - 880}px;top:380px;text-align:right"><div class="n1" id="${id}-s1">Sergey</div><div class="n2" id="${id}-s2">Brin</div></div>`;
    return `<div class="kb" id="${id}-k" style="transform-origin:0 0"><img id="${id}-bg" src="assets/img/pb_together.jpg" data-color-grading='${GRADE_S("grade_pb_dim.json")}' style="position:absolute;left:0;top:-120px;width:1920px;height:1337px;--hf-color-grading-intensity:0">${cells}${lines}<img id="${id}-cut" src="assets/img/pb_together_cut.png" style="position:absolute;left:0;top:-120px;width:1920px;height:1337px;opacity:0"></div><div class="dim" style="opacity:.2"></div><div class="bgrain"></div>${names}`;
  });
});

// S03 (v18) "tried to sell Google": the user's horizontal clip of the 1999 Google homepage on an old CRT computer (the
// first 1.6 s of their Gemini clip - before the page turns modern - its sparkle mark removed), full frame, in the curated
// treatment it had: prism streaks at the edges, a strong vignette, grain, and a slow stepped zoom-out
S("s03", 3.95, 5.1, (s) => {
  const E = r3(s.t1 - s.t0), id = "s03-k", z = s.z++;
  (s.covers = s.covers || []).push([s.t0, s.t1]);
  // v20: no punch-in and no zoom-out on this short shot - both read as a hiccup (the user's note); held at 1.03

  s.js(`tl.fromTo("#${id}-p2",{opacity:.32},{opacity:.5,duration:${E},ease:loIO(${E})},0);tl.fromTo("#${id}-p3",{opacity:.46},{opacity:.28,duration:${E},ease:loIO(${E})},0);`);
  s.h.push(`<div class="shot" id="${id}" style="z-index:${z}">
<div class="kb" id="${id}-pu"><div class="ngz" id="${id}-z" style="transform:scale(1.03)"><video id="${id}-v" class="clip cover" src="assets/vid/google_crt_h.mp4" data-start="0" data-duration="${E}" data-media-start="0" data-track-index="${z}" muted playsinline data-color-grading='${LITE()}'></video></div></div>
<div id="${id}-d" class="clip dim" data-start="0" data-duration="${E}" data-track-index="${z}" style="opacity:.2"></div>
<div id="${id}-fx" class="clip shot" data-start="0" data-duration="${E}" data-track-index="${z}" data-layout-allow-overlap><div class="ngvig" data-layout-allow-occlusion style="opacity:.6"></div><div class="pz pz2" id="${id}-p2"></div><div class="pz pz3" id="${id}-p3"></div><div class="bgrain" data-layout-allow-occlusion style="opacity:.45"></div></div>
</div>`);
});
S("s04", 5.1, 7.08, (s) => { s.video("money", 5.1, 7.08, { dim: 0.4, ms: 0.62 }); });
// S05 PhDs at Stanford: two different Stanford photos, no repeats
// S05 (v14) "They wanted to get back to their PhDs at Stanford": the user's campus footage (Memorial Church from the air),
// the user's clip of a PhD student talking, then the Main Quad from the air (were two Stanford photos and a stock desk)
S("s05", 7.08, 10.22, (s) => { s.video("stanford_church_s", 7.08, 8.48, { dim: 0.2, amp: 70 }); s.video("phd_student", 8.48, 9.28, { dim: 0.12, amp: 30, ms: 0.3 }); s.video("stanford_quad_aerial_s", 9.28, 10.22, { dim: 0.2, amp: 70 }); });
// S06 (v18) "so they approached Excite": the text cover, then straight to the Excite page - the window popping up on the
// board and the zoom into it are gone (the user's note); a white flash on the cut
S("s06", 10.22, 11.58, (s) => { s.void(10.22, 11.58); });
S("s07", 11.58, 15.54, (s) => {
  // v20: on a glowing screen in the dark (see SCREEN); the page scrolls
  // v23: the cut to the same page zoomed in, and the second pass over it, are gone (the reviewer: "same B-roll just zoomed
  // in looks repetitive"). In their place, from the same cut point: Excite's own 1998 TV spot - the cube turning to the
  // Excite X - a part of the ad the film does not use at 0:31 (and one with no lettering of its own under the captions).
  s.win(11.58, 13.95, { page: "excite", screen: true, noDrift: true, scroll: [0, -140] });
  s.video("excite_ad98", 13.95, 15.54, { dim: 0.2, amp: 40, ms: 3.57 });
});
FLASH18.push(M(11.58));
// S08 (v17) Vinod Khosla: the polaroids land on the grid and the grid travels with them - one camera move for both
S("s08", 15.54, 18.61, (s) => {
  s.wrap("", 15.54, 18.61, (id) => {
    const L = [];
    s.polaroid(L, 15.54, { src: "khosla_web20.jpg", cx: 640, cy: 500, w: 480, h: 640, r: -4, pos: "50% 25%" });
    s.polaroid(L, 15.85, { src: "khosla_sxsw.jpg", cx: 1270, cy: 300, w: 560, h: 440, r: 5, pos: "50% 30%" });
    s.polaroid(L, 16.47, { src: "kp_logo.png", cx: 1330, cy: 740, w: 560, h: 280, r: -3, fit: "contain" });
    s.polaroid(L, 17.15, { src: "kp_office.jpg", cx: 300, cy: 860, w: 420, h: 380, r: 6 });
    // v18: the Excite logo card is gone (the user's note)
    s.drift(`#${id}-b`, 15.54, 18.61, 60, 1.02);
    const big = "left:-260px;top:-160px;width:2440px;height:1400px";
    return `<div class="kb" id="${id}-b"><div class="gridbg" style="${big}"></div><div class="gridtex" style="${big}"></div>${L.join("")}</div>`;
  });
  // v11: every move in this scene on ~8 fps eased steps (the curated VOX look)
  s.j = s.j.map((x) => x.replace(/voxOut\(/g, "loOut(").replace(/dft\(/g, "loIO("));
});
// S09 (v11) helped negotiate / the price down to $750,000: the negotiation clip framed on a dark textured board and
// treated (faded wash, channel separation, bloom, dust, vignette, grain) over a blurred colour-split ghost of itself,
// prism streaks at the edges; the shot opens on a slow zoom-out on ~8 fps steps. The words sit underneath, glowing serif
// italic, and the price steps down from $1,000,000 to $750,000. The cash-stack clip is gone.
const GRADE = (f) => JSON.stringify(JSON.parse(fs.readFileSync(path.join(ROOT, "build", f), "utf8")));
S("s09", 18.61, 23.82, (s) => {
  const T0 = s.t0, E = r3(s.t1 - T0), L = (t) => r3(t - T0), id = "s09-n", z = s.z++;
  // v23: nego3.mp4 - the man's first take, then (as the price starts down) a handshake over a desk: two different shots and one clean cut, at their own speed. The old clip cut to a second take of itself half-way.
  const W1 = [["helped", L(WT("helped", 18.63))], ["negotiate", L(WT("negotiate", 18.99))]];
  const W2 = [["the", L(WT("the", 19.62))], ["price", L(WT("price", 19.84))], ["down", L(WT("down", 20.18))], ["to", L(WT("to", 20.46))]];
  const tOut = r3(W2[0][1] - 0.1), c0 = L(M(20.64)), c1 = L(M(22.2));
  const vid = (vid, g) => `<video id="${vid}" class="clip ngv" src="assets/vid/nego3.mp4" data-start="0" data-duration="${E}" data-media-start="0" data-track-index="${z}" muted playsinline data-color-grading='${GRADE(g)}'></video>`;
  const rise8 = (sel, t, dy) => `tl.fromTo("${sel}",{y:${dy},opacity:0,filter:"blur(12px)"},{y:0,opacity:1,filter:"blur(0px)",duration:0.38,ease:loOut(0.38)},${r3(t)});`;
  const words = (ws, pre) => ws.map(([w, t], k) => { s.js(rise8(`#${id}-${pre}${k}`, t, 26)); return `<span id="${id}-${pre}${k}">${w}</span>`; }).join(" ");
  s.js(`tl.fromTo("#${id}-z",{scale:1.2},{scale:1,duration:${E},ease:sxoP(0.3)},0);`);
  // v23: no rainbow streaks or ring over this shot (the reviewer: "the rainbow texture looks odd")
  const h1 = words(W1, "h"), h2 = words(W2, "l");
  s.js(`tl.to("#${id}-h",{opacity:0,filter:"blur(12px)",duration:0.25,ease:loIn(0.25)},${tOut});`);
  s.js(rise8(`#${id}-n`, W2[0][1], 40));
  s.js(`(function(){var o={v:1000000},e=document.querySelector("#${id}-n");tl.fromTo(o,{v:1000000},{v:750000,duration:${r3(c1 - c0)},ease:loOut(${r3(c1 - c0)}),onUpdate:function(){e.textContent="$"+Math.round(o.v).toLocaleString("en-US");}},${c0});})();`);
  s.h.push(`<div class="shot" id="${id}" style="z-index:${z}">
<div id="${id}-bg" class="clip shot ngbg" data-start="0" data-duration="${E}" data-track-index="${z}"></div>
<div class="ngz" id="${id}-z"><div class="ngghost">${vid(`${id}-vg`, "grade_nego_ghost.json")}</div><div class="ngframe">${vid(`${id}-vm`, "grade_nego_main.json")}</div></div>
<div id="${id}-fx" class="clip shot" data-start="0" data-duration="${E}" data-track-index="${z}" data-layout-allow-overlap><div class="ngvig" data-layout-allow-occlusion></div><div class="ngshade" data-layout-allow-occlusion></div><div class="bgrain" data-layout-allow-occlusion style="opacity:.5"></div>
<div class="ngt" id="${id}-h" style="top:830px;font-size:112px">${h1}</div>
<div class="ngt" style="top:770px;font-size:60px">${h2}</div>
<div class="ngt" style="top:836px;font-size:150px"><span id="${id}-n">$1,000,000</span></div></div>
</div>`);
});
// S10 but Excite's CEO / George Bell / still turned it down
S("s10", 23.82, 28.12, (s) => {
  // v17: after "Excite's CEO" the camera pushes in on the frame and the name while a yellow marker sweeps "George" then
  // "Bell,"; on "still" it eases right to take in TURNED IT DOWN. The paper travels with the camera.
  s.paper(23.82, 28.12, (id) => {
    const FX = 760, FY = 520, B = 250;
    const imgs = ["bell_wharton.jpg", "bell_1999.jpg", "bell_cnbc99.jpg", "bell_portrait.jpg", "bell_tpl.jpg", "bell_jumptap.jpg", "bell_1.png"];
    const fr = `${id}-f`;
    // v23: seven photos, one after another (the reviewer: "more pics of Excite's CEO ... coming one after another") - three
    // more (his 1999 keynote, CNBC in 1999, a later interview) between the four. A swap about every quarter second, the
    // fifth and the seventh still on "George" and "Bell,"; the frame steps up a little with each, on smooth eases.
    const tG = s.L(25.04), tB = s.L(25.61), tUp = r3(s.L(26.15) - 0.2);
    const swL = [0, r3(tG / 4), r3(tG / 2), r3(3 * tG / 4), tG, r3((tG + tB) / 2), tB], sizes = [0.76, 0.8, 0.84, 0.88, 0.92, 0.96, 1.0];
    swL.forEach((t, k) => {
      if (k === 0) { s.js(`tl.set("#${fr}",{scale:${sizes[0]}},0);`); return; }
      const d = r3(Math.min(0.4, (k + 1 < swL.length ? swL[k + 1] : tUp) - t - 0.005));
      s.js(`tl.fromTo("#${fr}",{scale:${sizes[k - 1]}},{scale:${sizes[k]},duration:${d},ease:sxo(${d}),immediateRender:false},${t});`);
      s.js(`tl.fromTo("#${fr}-i${k}",{opacity:0},{opacity:1,duration:0.16,ease:sxo(0.16)},${t});`);
    });
    s.js(`tl.fromTo("#${fr}",{scale:1},{scale:1.22,duration:0.7,ease:sxio(0.7),immediateRender:false},${tUp});`);
    const words = [["George", 25.04], ["Bell,", 25.61]];
    const left = `<div class="ftx" style="right:${1920 - (FX - 175)}px;top:${FY - 64}px;text-align:right">${words.map(([w, t], k) => {
      const tw = r3(Math.max(0, WT(w, t) - s.t0 - 0.03));
      s.js(riseInS(`#${id}-n${k}`, tw, 0.27, 20));
      s.js(`tl.fromTo("#${id}-n${k}",{backgroundSize:"0% 82%"},{backgroundSize:"100% 82%",duration:0.36,ease:scio(0.36)},${r3(tw + 0.12)});`);
      return `<span class="nhl" id="${id}-n${k}">${w}</span>`;
    }).join("<br>")}</div>`;
    // right side, the punch: still / TURNED IT / DOWN.
    const R = [["still", 26.15, "ftx", 0], ["TURNED IT", 26.63, "fbig", 1], ["DOWN.", 27.36, "fbig", 2]];
    const right = R.map(([w, t, cls, row], k) => {
      s.js(riseInS(`#${id}-r${k}`, r3(Math.max(0, WT(w.split(" ")[0], t) - s.t0 - 0.03)), cls === "fbig" ? 0.3 : 0.27, cls === "fbig" ? 34 : 20));
      const top = row === 0 ? FY - 190 : row === 1 ? FY - 130 : FY - 16;
      return `<div class="${cls}" style="left:${FX + 210}px;top:${top}px"><span id="${id}-r${k}">${w}</span></div>`;
    }).join("");
    s.js(flick(`#${id}-r2`, r3(WT("down.", 27.36) - s.t0 + 0.62)));
    // the camera (origin top-left), frame centre (cx,cy) at zoom zz
    const E = r3(s.t1 - s.t0), cam = (cx, cy, zz) => ({ x: r3(960 - zz * cx), y: r3(540 - zz * cy), scale: zz });
    const tZ = r3(Math.max(0.3, WT("George", 25.04) - s.t0 - 0.08)), tS = r3(WT("still", 26.15) - s.t0 - 0.05);
    const A0 = cam(960, 540, 1), A1 = cam(900, 530, 1.06), B1 = cam(700, 505, 1.34), C1 = cam(1010, 470, 1.16), D1 = cam(1010, 470, 1.22);
    const mv = (a, b, at, d, ease, first) => s.js(`tl.fromTo("#${id}-cam",{x:${a.x},y:${a.y},scale:${a.scale}},{x:${b.x},y:${b.y},scale:${b.scale},duration:${d},ease:${ease}(${d})${first ? "" : ",immediateRender:false"}},${r3(at)});`);
    mv(B1, B1, 0, r3(tS - 0.2), "scio", true);   // v20: opens already pushed in on the frame and the name (the 0:19 framing) - no zoom-in

    mv(B1, C1, r3(tS - 0.2), 0.85, "sxio");
    mv(C1, D1, r3(tS + 0.65), r3(Math.max(0.2, E - tS - 0.65)), "sxo");
    return `<div class="kb" id="${id}-cam" style="transform-origin:0 0"><div class="paper" style="position:absolute;left:-400px;top:-300px;width:2720px;height:1680px"></div>${frameHTML(fr, FX, FY, B, B, imgs)}${left}${right}</div>`;
  });
});
S("s11", 28.12, 33.13, (s) => {
  s.void(28.12, 30.17);
  s.win(30.17, 33.13, { page: "google", typed: "search", typeAt: [31.0, 32.0], hl: [["google", 32.19]], cursor: [[30.17, 1300, 650], [30.6, 760, 270], [32.35, 820, 330], [32.6, 820, 330]], clicks: [30.6, 32.6] });
});
S("s12", 33.13, 37.03, (s) => {
  s.void(33.13, 37.03);
  // v20: the Excite page on the glowing screen (as at 0:09); the cursor goes to the close box, the window shuts, and the
  // screen, its glow and the board fade together into the black cover
  const id = s.win(33.13, 35.2, { page: "excite", screen: true, push: false, scroll: [-200, -420], noDrift: true, winCursor: [[33.13, 1404, 798], [33.95, 1040, 560], [34.56, 1895, 15]], wclicks: [34.66] });
  s.js(`tl.set("#${id}-k .xb",{attr:{"data-p":"1"}},${s.L(34.66)});`);
  const tc = r3(s.L(34.66) + 0.08);
  s.js(`tl.fromTo("#${id}-k",{opacity:1,scale:1},{opacity:0,scale:0.94,duration:0.2,ease:xio(0.2),immediateRender:false},${tc});`);
  s.js(`tl.to(["#${id}-bd","#${id}-gh","#${id}-fx"],{opacity:0,duration:0.2,ease:xio(0.2)},${tc});`);
});
// S13 Bell tells a different story: the CNBC interview where he told it
// S13 (v14) "Bell tells a different story.": Bell himself, talking, from the 2015 CNBC interview where he told it (cropped
// above CNBC's banner, archival TV grade), then the text cover for "He says the price wasn't the problem."
// S13 (v17) "Bell tells a different story. He says the price ($750,000) wasn't the problem.": Bell himself, talking, from
// the 2015 CNBC interview, then the office clip, where the quote block sits left of him over a soft shade
S("s13", 37.03, 41.97, (s) => {
  const tSays = RAW[33].t;
  // v18: no punch-in on either clip and a gentle zoom-out - on these close talking heads the 8% step-in on "different" /
  // "$750,000" read as the picture snapping (the user's note)
  s.video("bell_cnbc_talk", 37.03, tSays, { dim: 0.1, amp: 12, ms: 0.2, grade: "grade_bell_tv.json", noPunch: true, zs: [1.12, 1.08] });
  s.video("bell_office", tSays, 41.97, { dim: 0.14, amp: 12, ms: 0.2, noPunch: true, zs: [1.12, 1.08] });
  FLASH18.push(M(37.03));
  s.raw(tSays, 41.97, () => `<div class="qshade" data-layout-allow-occlusion></div>`);
});

// S14 (v17) "Page wanted Excite to completely replace its existing search engine with Google.": Larry on stage (the
// user's clip) with "Page wanted"; then 1998 TV spots (YouTube, "Search Engine Commercials: 1998"): Excite's own ad
// ("Get more out of the Web" / "What are you looking for?"), then a search typed and sent and the door marked TYPICAL
// SEARCH ENGINE; a white flash onto Google's own footage on "with Google." - its TGIF of December 1999 (YouTube,
// "GOOGLE TGIF 1999 video"). Replaces the Excite and Google page screenshots, which were repeats.
S("s14", 41.97, 46.97, (s) => {
  const tEx = RAW[35].words[0].t - 0.02, tRep = RAW[36].words[0].t - 0.02, tWith = RAW[38].words[0].t - 0.02;
  s.video("larry_stage", 41.97, tEx, { dim: 0.16, amp: 40, ms: 0.2 });
  s.raw(41.97, tEx, (id) => {
    const tP = r3(WT("Page", 41.99) - s.t0), tW = r3(WT("wanted", 42.29) - s.t0);
    s.js(riseIn(`#${id}-n1`, r3(Math.max(0, tP - 0.03)), 0.32, 40) + riseIn(`#${id}-n2`, r3(tW - 0.03), 0.32, 30));
    return `<div class="nm" style="left:1150px;top:380px;text-align:left"><div class="n1" id="${id}-n1">Page</div><div class="n2" id="${id}-n2">wanted</div></div>`;
  });
  s.video("excite_ad98", tEx, tRep, { dim: 0.3, amp: 40, ms: 0.2 });
  // v23: the door flying at the camera is gone (the reviewer: "door animation zooming in to front is looking bad") - the
  // search is typed and sent, then a straight cut to the sign on that door, TYPICAL SEARCH ENGINE, as "existing search
  // engine" is said. The typing plays at the ad's own speed (the whole passage ran at 1.9x); the sign is a still card.
  const tSign = RAW[37].words[1].t - 0.02;
  s.video("search_ad98", tRep, tSign, { dim: 0.36, amp: 40, ms: 0.86 });
  s.video("search_ad98", tSign, tWith, { dim: 0.36, amp: 40, ms: 3.1, rate: 0.75 });
  s.video("google_tgif99", tWith, 46.97, { dim: 0.12, amp: 40, ms: 0.4 });
  FLASH17.push(M(tWith));
});
// S15 Bell wasn't willing: Bell's portrait framed on a clean frame
S("s15", 46.97, 48.97, (s) => {
  // v16: zoomed in. v18: on "to do that" Bell's portrait turns red - the red grade (desaturated, red colour wheels,
  // build/grade_bell_red2.json, brighter and redder than v16) on the photo itself, its intensity eased from 0 to 1 through the seek-safe treatment
  // property (the v16 version cross-faded a graded copy, which never showed)
  s.clean(46.97, 48.97, (id) => {
    s.js(riseIn(`#${id}-f`, s.L(46.99), 0.3, 40)); s.js(`tl.fromTo("#${id}-z",{scale:1},{scale:1.24,duration:${s.D(46.97, 48.97)},ease:sxoP(0.16)},0);`);
    const tTo = r3(WT("to", 48.37) - s.t0);
    s.js(`tl.fromTo("#${id}-f-i0",{"--hf-color-grading-intensity":0},{"--hf-color-grading-intensity":1,duration:0.4,ease:cio(0.4)},${tTo});`);
    return `<div class="kb" id="${id}-z">${frameHTML(`${id}-f`, 960, 420, 470, 470, ["bell_rose.jpg"]).replace(`id="${id}-f-i0" src="assets/img/bell_rose.jpg" style="opacity:1"`, `id="${id}-f-i0" src="assets/img/bell_rose.jpg" data-color-grading='${GRADE("grade_bell_red2.json")}' style="opacity:1;--hf-color-grading-intensity:0"`)}</div>`;
  });
});
// S16 (v13) "And that's what makes this deal so interesting.": Google's 1999 "corkboard" server rack (Computer History
// Museum), framed on the dark textured board in the curated treatment of the negotiation shot, opening on a slow
// stepped zoom-out; the captions sit underneath. Replaces the two browser-window polaroids (that b-roll was a repeat).
S("s16", 48.97, 52.97, (s) => {
  const E = r3(s.t1 - s.t0), id = "s16-k", z = s.z++;
  const img = (g) => `<img class="ngimg" src="assets/img/corkboard_chm.jpg" data-color-grading='${GRADE(g)}'>`;
  s.js(`tl.fromTo("#${id}-z",{scale:1.22},{scale:1,duration:${E},ease:sxoP(0.3)},0);`);
  [["p1", 0.45, 0.8], ["p3", 0.6, 0.35], ["p5", 0.25, 0.45]].forEach(([p, a, b]) => s.js(`tl.fromTo("#${id}-${p}",{opacity:${a}},{opacity:${b},duration:${r3(E / 2)},ease:loIO(${r3(E / 2)})},0);tl.to("#${id}-${p}",{opacity:${a},duration:${r3(E / 2)},ease:loIO(${r3(E / 2)})},${r3(E / 2)});`));
  s.h.push(`<div id="${id}" class="clip shot ngbg" data-start="0" data-duration="${E}" data-track-index="${z}" style="z-index:${z}" data-layout-allow-overlap>
<div class="ngz" id="${id}-z"><div class="ngghost">${img("grade_cork_ghost.json")}</div><div class="ngframe">${img("grade_cork_main.json")}</div></div>
<div class="ngvig" data-layout-allow-occlusion></div><div class="ngshade" data-layout-allow-occlusion></div><div class="pz pz1" id="${id}-p1"></div><div class="pz pz3" id="${id}-p3"></div><div class="pz pz5" id="${id}-p5"></div><div class="bgrain" data-layout-allow-occlusion style="opacity:.5"></div></div>`);
});
S("s17", 52.97, 57.97, (s) => {
  // "Page was willing to" (v13): Larry Page speaking on stage at TED, from the user's clip, his name and the words beside him
  s.video("larry_ted", 52.97, 54.33, { ms: 0.2, dim: 0.16, amp: 40 });
  s.raw(52.97, 54.33, (id) => {
    const tP = r3(WT("Page", 52.99) - s.t0), tw = [["was", 53.32], ["willing", 53.57], ["to", 54.15]].map(([w, t]) => r3(WT(w, t) - s.t0));
    s.js(riseIn(`#${id}-n1`, r3(Math.max(0, tP - 0.03)), 0.32, 40) + tw.map((t, k) => riseIn(`#${id}-n2${k}`, r3(t - 0.03), 0.3, 26)).join(""));
    return `<div class="nm" style="right:${1920 - 950}px;top:380px;text-align:right"><div class="n1" id="${id}-n1">Page</div><div class="n2"><span id="${id}-n20" style="display:inline-block">was</span> <span id="${id}-n21" style="display:inline-block">willing</span> <span id="${id}-n22" style="display:inline-block">to</span></div></div>`;
  });
  s.video("larry_1998_s", 54.33, 57.97, { dim: 0.3, amp: 50 });   // v15: Larry in 1998 (the user's clip) in place of the corridor and the black text cover
});
S("s18", 57.97, 63.24, (s) => {
  s.video("excite_ad_logo", 57.97, 58.58, { dim: 0.1, amp: 40 });   // v16: Excite's 1996 TV ad, the starburst logo (YouTube, "Excite Commercial #1")
  s.video("excite_ad_search", 58.58, 59.97, { dim: 0.1, amp: 40 });   // v16: the same ad - "direction" typed into Excite's search, the button clicked
  s.video("google_garage_1998", 59.97, 60.82, { dim: 0.12, amp: 40, ms: 0.2 });   // v16: Google's first office, the garage, 1998 (YouTube, "Google's first office 1998")
  s.video("servers", 60.82, 63.24, { dim: 0.35 });
});
S("s19", 63.24, 67.92, (s) => {
  s.video("calendar", 63.24, 64.53, { dim: 0.35 });
  s.wrap("void", 64.53, 67.92, (id) => {
    const P = [["khosla_sxsw.jpg", "50% 30%", "Vinod Khosla"], ["kp_office.jpg", "60% 50%", "Kleiner Perkins"], ["doerr.jpg", "40% 30%", "John Doerr"]];
    return P.map(([src, pos, name], k) => {
      s.js(`tl.fromTo("#${id}-p${k}",{y:1100},{y:0,duration:0.5,ease:voxOut(0.5)},${r3(0.02 + k * 0.12)});`);
      s.drift(`#${id}-i${k}`, 64.53, 67.92, 55, 1.12);
      return `<div id="${id}-p${k}" style="position:absolute;left:${k * 640 + 3}px;top:0;width:634px;height:1080px;overflow:hidden"><img id="${id}-i${k}" data-color-grading='${LITE()}' src="assets/img/${src}" style="position:absolute;left:0;top:0;width:634px;height:1080px;object-fit:cover;object-position:${pos}"><div class="dim" style="opacity:.35"></div><div class="lbl">${name}</div></div>`;
    }).join("") + `<div class="bgrain"></div>`;
  });
});
S("s20", 67.92, 72.08, (s) => {
  cleanLogo(s, 67.92, 69.51, [["kp_logo_tight.png", 820, 430, 67.94], ["sequoia_logo_tight.png", 600, 567, 68.3]]);   // v16: centred as a pair, matched sizes
  s.wrap("clean", 69.51, 72.08, (id) => {
    s.js(`tl.fromTo("#${id}-w",{backgroundSize:"0% 78%"},{backgroundSize:"100% 78%",duration:0.33,ease:voxOut(0.33)},${s.L(69.56)});`);
    s.drift(`#${id}-k`, 69.51, 72.08, 55, 1.02);
    return `<div class="kb" id="${id}-k"><div class="kicker">PRESS RELEASE &nbsp;·&nbsp; JUNE 7, 1999</div><div class="headline">Google Receives <span class="hlw" id="${id}-w"><span class="nfix">$25</span> Million</span> in Equity Funding</div><div class="rule"></div></div><div class="bgrain" style="opacity:.35"></div>`;
  });
});
// S21 (v20) "Meanwhile, Excite merged with @Home Network in a deal valued at $6.7 billion": the user's reference design,
// copied - warm grey paper under fine scan lines, a heavy rounded vignette and prism light leaks along the top; "Excite"
// and "@Home" in a bold grotesque (TeX Gyre Heros, a Helvetica) inside dotted outlines with square corner marks that step
// out like George Bell's frame (0.76 -> 0.84 -> 0.92 -> 1 on 8 fps beats); thin dark curves meet under the two names and
// run down into the dark Excite@Home card (built in HTML: white bold italic, the @ on a red disc); then the price in Bodoni
// Moda. The journey is as before: the camera on Excite, then on @Home, then out to the merge as the card comes up from
// lower, then across to the price counting up to $6,700,000,000.
S("s21", 72.08, 79.2, (s) => {
  const T0 = s.t0, L = (t) => r3(t - T0), E = r3(s.t1 - T0);
  // word times from the voiceover's own word list (the old caption data for these removed cards runs late)
  const NW = (word, old) => { const n = norm(word), near = M(old); let best = null; for (const w of NEWW) if (norm(w.w) === n && (!best || Math.abs(w.t - near) < Math.abs(best.t - near))) best = w; return best ? best.t : near; };
  const tEx = L(NW("Excite", 72.99)), tMg = L(NW("merged", 73.47)), tHm = L(NW("Home", 74.28)), tNw = L(NW("Network", 75.36));
  const tIn = L(NW("in", 75.6)), tNum = L(NW("$6.7", 77.0));
  s.wrap("", 72.08, 79.2, (id) => {
    // the reference, framed at zoom 1 (canvas px): the two outlined names, where the curves meet, the card; the price to the right
    const EX = { x: 562, y: 368, w: 384, h: 134, t: "Excite" }, HM = { x: 1359, y: 368, w: 390, h: 134, t: "@Home" };
    const J = { x: 960, y: 552 }, CD = { x: 963, y: 741, w: 405, h: 80 }, PX = { x: 2560, y: 741 };
    const PW = FMO.layout("$6,700,000,000", 150, -0.01).width;
    // v23: the flash box hugs the figure's ink
    const PIK = ink(FMO.layout("$6,700,000,000", 150, -0.01), 150), BOP = 0.5 + (FMO.win.asc - FMO.win.desc) / (2 * FMO.upm);
    const PXV = `--it:${Math.round(BOP * 150 - PIK.top - 12)}px;--ib:${Math.round(150 - (BOP * 150 - PIK.bot) - 12)}px;--il:${Math.round(PIK.left - 14)}px;--ir:${Math.round(PW - PIK.right - 14)}px`;
    const frame = (fid, b) => `<div class="mfr" id="${id}-${fid}" style="left:${b.x - b.w / 2}px;top:${b.y - b.h / 2}px;width:${b.w}px;height:${b.h}px;opacity:0"><i class="mside" style="left:0"></i><i class="mside" style="right:0"></i><i class="mdot" style="left:-4px;top:-4px"></i><i class="mdot" style="right:-4px;top:-4px"></i><i class="mdot" style="left:-4px;bottom:-4px"></i><i class="mdot" style="right:-4px;bottom:-4px"></i></div>`;
    const word = (wid, b) => `<div class="mword" style="left:${b.x}px;top:${b.y}px"><span id="${id}-${wid}" style="opacity:0">${esc(b.t)}</span></div>`;
    let svg = `<svg width="3600" height="1300" viewBox="0 0 3600 1300" style="position:absolute;left:0;top:0;overflow:visible">`;
    // a curve that draws on: pathLength 100, the gap longer than the path and the offset past it (no round-cap dot early)
    const line = (lid, d, at, dur) => { svg += `<path id="${id}-${lid}" d="${d}" pathLength="100" fill="none" stroke="#262422" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="100 110" stroke-dashoffset="101"/>`; s.js(`tl.fromTo("#${id}-${lid}",{attr:{"stroke-dashoffset":101}},{attr:{"stroke-dashoffset":0},duration:${dur},ease:cio(${dur})},${r3(at)});`); };
    const xa = 568, xb = 1354, y0 = 414, xr = CD.x + CD.w / 2 + 10;
    line("la", `M${xa},${y0} C${xa},${y0 + 62} ${xa + 60},${y0 + 76} ${xa + 196},${y0 + 78} C${J.x - 60},${y0 + 80} ${J.x},${y0 + 92} ${J.x},${J.y}`, tEx + 0.16, 0.75);
    line("lb", `M${xb},${y0} C${xb},${y0 + 62} ${xb - 60},${y0 + 76} ${xb - 196},${y0 + 78} C${J.x + 60},${y0 + 80} ${J.x},${y0 + 92} ${J.x},${J.y}`, tHm + 0.12, 0.62);
    line("lc", `M${J.x},${J.y} L${J.x},${CD.y - CD.h / 2}`, tNw - 0.14, 0.38);
    const xe = r3(PX.x - PW / 2 - 60);
    line("ld", `M${xr},${CD.y} C${xr + 200},${CD.y} ${xr + 260},${CD.y - 110} ${r3((xr + xe) / 2)},${CD.y - 110} C${r3(xe - 260)},${CD.y - 110} ${r3(xe - 200)},${CD.y} ${xe},${CD.y}`, tIn, 0.9);
    svg += `</svg>`;
    // the outlines step out like George Bell's frame; the names come up into them from a little lower; the card comes up
    const steps = (fid, at) => { s.js(`tl.set("#${id}-${fid}",{opacity:1,scale:0.76},${r3(at)});`); [0.84, 0.92, 1].forEach((k, n) => s.js(`tl.set("#${id}-${fid}",{scale:${k}},${r3(at + 0.125 * (n + 1))});`)); };
    const rise = (sel, at, d, dy) => s.js(`tl.fromTo("${sel}",{opacity:0,y:${dy}},{opacity:1,y:0,duration:${d},ease:cio(${d})},${r3(Math.max(0, at))});`);
    steps("fx", tEx - 0.05); rise(`#${id}-ex`, tEx - 0.2, 0.6, 70);
    steps("fh", tHm - 0.05); rise(`#${id}-hm`, tHm - 0.2, 0.6, 70);
    rise(`#${id}-cd`, tNw - 0.22, 0.8, 200);
    rise(`#${id}-px`, tNum - 0.32, 0.6, 200);
    // the price counts up to the full figure
    s.js(`(function(){var o={v:1000000000},e=document.querySelector("#${id}-pv"),f=function(v){return "$"+String(Math.round(v)).replace(/\\B(?=(\\d{3})+(?!\\d))/g,",");};tl.fromTo(o,{v:1000000000},{v:6700000000,duration:0.75,ease:cio(0.75),onUpdate:function(){e.textContent=f(o.v);}},${r3(tNum)});})();`);
    s.js(flick(`#${id}-px`, r3(tNum + 0.75 + 0.1)));   // v23: the text flash on the figure once it has landed (the reviewer's note at 0:57)
    // camera on the canvas (origin top-left): frame centre (cx,cy) at zoom zz - Excite, then @Home, then the whole merge,
    // then the price
    const cam = (cx, cy, zz) => ({ x: r3(960 - zz * cx), y: r3(540 - zz * cy), scale: zz });
    const C0 = cam(500, 390, 1.5), C1 = cam(590, 395, 1.5), C2 = cam(1330, 395, 1.5), C3 = cam(960, 545, 1.0), C4 = cam(PX.x, PX.y, 1.04), C5 = cam(PX.x, PX.y, 1.12);
    const mv = (a, b, at, d, ease, first) => s.js(`tl.fromTo("#${id}-cam",{x:${a.x},y:${a.y},scale:${a.scale}},{x:${b.x},y:${b.y},scale:${b.scale},duration:${d},ease:${ease}(${d})${first ? "" : ",immediateRender:false"}},${r3(at)});`);
    mv(C0, C1, 0, r3(Math.max(0.3, tEx + 0.15)), "cio", true);
    mv(C1, C2, r3(tMg + 0.1), 0.42, "cio");
    mv(C2, C3, r3(tNw - 0.12), 0.4, "cio");
    mv(C3, C4, tIn, 0.8, "xio");
    mv(C4, C5, r3(tIn + 0.8), r3(E - tIn - 0.8), "xo");
    // v21: the Excite@Home office (the user's photo, its upper part) under the logo card, subtle - multiplied into the
    // paper with feathered edges, coming up with the card. The camera journey is unchanged.
    const OF = { x: CD.x, y: 826, w: 640, h: 249 };   // from the card's top edge down: the building's own sign shows just under the card
    s.js(`tl.fromTo("#${id}-of",{opacity:0,y:150},{opacity:0.82,y:0,duration:0.8,ease:cio(0.8)},${r3(Math.max(0, tNw - 0.14))});`);
    const office = `<div class="mphoto" id="${id}-of" data-layout-allow-occlusion style="left:${OF.x - OF.w / 2}px;top:${OF.y - OF.h / 2}px;width:${OF.w}px;height:${OF.h}px;opacity:0"><img src="assets/img/excitehome_office.jpg" alt=""></div>`;
    const card = `<div class="mcard" id="${id}-cd" style="left:${CD.x - CD.w / 2}px;top:${CD.y - CD.h / 2}px;width:${CD.w}px;height:${CD.h}px;opacity:0"><div class="mlogo">Excite<span class="at">@</span>Home.</div></div>`;
    return `<div class="kb" id="${id}-cam" style="transform-origin:0 0"><div class="mbg2" style="left:-500px;top:-400px;width:4600px;height:2000px"></div>${svg}
${frame("fx", EX)}${frame("fh", HM)}${word("ex", EX)}${word("hm", HM)}${office}${card}
<div class="mpw" style="left:${PX.x}px;top:${PX.y}px"><div class="mprice" id="${id}-px" data-f="0" style="opacity:0;${PXV}"><span class="pnum3" id="${id}-pv">$1,000,000,000</span></div></div></div>
<div class="mvig2" data-layout-allow-occlusion></div><div class="mleak" style="left:10px;top:28px;width:740px;height:92px"></div><div class="mleak" style="left:1350px;top:24px;width:560px;height:100px;transform:scaleX(-1)"></div><div class="bgrain" style="opacity:.35"></div>`;
  });
  // v23: the figure no longer sits still to the end of the line (the reviewer: "it's stopping at this frame for too long ...
  // add one more between"): it counts up a little quicker, flashes, and the shot cuts to a market ticker board for the
  // rest of "billion", before the flash onto the Guardian page
  s.video("ticker", Mi(57.45), 79.2, { dim: 0.12, amp: 24, ms: 1.0 });
});
// S22 (v18) "Just two years later, the company went bankrupt.": the Guardian's report of 1 October 2001 (the user's
// screenshot) from the first word - the black "Just two years later, 2001" cover is gone (the user's note). The page
// arrives on a short push and drifts right with the headline while a yellow marker sweeps it through "the company went";
// it holds on "bankrupt", then goes up out of frame on an easeOutExpo - fast, then slowing, like a shutter opening (the
// user's note). No captions over it. A white flash on the cut in.
S("s22", 79.2, 82.92, (s) => {
  const nw = (word, near) => { const n = norm(word); let best = null; for (const w of NEWW) if (norm(w.w) === n && (!best || Math.abs(w.t - near) < Math.abs(best.t - near))) best = w; return best ? best.t : near; };
  s.wrap("", 79.2, 82.92, (id) => {
    const b = s.L(82.92);
    const cam = (cx, cy, zz) => ({ x: r3(960 - zz * cx), y: r3(540 - zz * cy), scale: zz });
    const P0 = cam(830, 360, 1.78), P1 = cam(790, 330, 2.0), P2 = cam(940, 336, 2.14), P3 = { ...P2, y: r3(P2.y - 670) };   // the page is 911 px tall: this is as far up as it goes without running out
    const mv = (A, B2, at, d, ease, first) => s.js(`tl.fromTo("#${id}-cam",{x:${A.x},y:${A.y},scale:${A.scale}},{x:${B2.x},y:${B2.y},scale:${B2.scale},duration:${d},ease:${ease}(${d})${first ? "" : ",immediateRender:false"}},${r3(at)});`);
    const sw = r3(nw("later,", 58.58) - s.t0), s1 = 0.62, s2 = 0.14, up = r3(b - 0.64);
    mv(P0, P1, 0, 0.35, "xo", true); mv(P1, P2, 0.35, r3(up - 0.35), "cio"); mv(P2, P3, up, r3(b - up), "xo");
    s.js(`tl.fromTo("#${id}-h1",{scaleX:0},{scaleX:1,duration:${s1},ease:cio(${s1})},${sw});tl.fromTo("#${id}-h2",{scaleX:0},{scaleX:1,duration:${s2},ease:xo(${s2})},${r3(sw + s1)});`);
    return `<div class="kb" id="${id}-rot"><div class="kb" id="${id}-cam" style="transform-origin:0 0"><div class="gdn"><img src="assets/img/guardian_excite_2001.png" alt=""><div class="gdhl" id="${id}-h1" style="left:560px;top:282px;width:566px;height:40px"></div><div class="gdhl" id="${id}-h2" style="left:560px;top:321px;width:76px;height:34px"></div></div></div></div><div class="hvig" style="opacity:.55"></div><div class="bgrain" style="opacity:.4"></div>`;
  });
  FLASH18.push(M(79.2));
});
// S23 Today, Google's parent company: (v18) the Googleplex from the air, then Ruth Porat and David Rubenstein under the $4T figure
S("s23", 82.92, 88.37, (s) => {

  // v18 "Today, Google's parent company is worth around $4 trillion": the Googleplex from the air (YouTube, "[4K] Google
  // headquarter") from "Today" - the Bay View shot before it is gone (the user's note) - then the user's pick: Alphabet's
  // Ruth Porat with David Rubenstein, both seated (YouTube, Bloomberg's "The David Rubenstein Show", the two-shot that
  // ends at 0:24, cropped above the show's corner mark), on a gentle zoom so both stay in frame; a white flash on the cut
  s.video("googleplex_air", 82.92, 85.57, { dim: 0.24, amp: 50, ms: 0.5 });
  s.video("porat_rubenstein", 85.57, 88.37, { dim: 0.3, amp: 18, ms: 0.3, zs: [1.07, 1.01], noPunch: true });
  FLASH18.push(M(85.57));
});

// S24 (v15) the end: only the Raw Canvas mark rising into frame, as before (the quote block and its voiceover are cut)
{
  const s = new Scene("s24", 88.37, 88.37); s.t1 = END;
  const lg = 0, eid = `${s.id}-e`;
  s.h.push(`<div id="${eid}" class="clip shot void" data-start="${lg}" data-duration="${r3(END - s.t0 - lg)}" data-track-index="1" style="z-index:2"><div style="position:absolute;left:${960 - 165}px;top:${540 - 168}px;width:330px;height:335px"><img id="${eid}-lg" src="assets/img/rawcanvas_logo.png" style="position:absolute;left:0;top:0;width:330px;height:335px;filter:drop-shadow(0 0 30px rgba(255,248,238,.35))"></div></div>`);
  s.js(`tl.fromTo("#${eid}-lg",{y:460,opacity:0,filter:"blur(26px) drop-shadow(0 0 30px rgba(255,248,238,.35))"},{y:0,opacity:1,filter:"blur(0px) drop-shadow(0 0 30px rgba(255,248,238,.35))",duration:0.95,ease:dft(0.95)},${lg});`);
  s.js(`tl.set("#${eid}-lg",{filter:"invert(1) drop-shadow(0 0 40px rgba(255,248,238,.9))"},${r3(lg + 1.1)});tl.set("#${eid}-lg",{filter:"drop-shadow(0 0 30px rgba(255,248,238,.35))"},${r3(lg + 1.134)});tl.set("#${eid}-lg",{filter:"invert(1) drop-shadow(0 0 40px rgba(255,248,238,.9))"},${r3(lg + 1.2)});tl.set("#${eid}-lg",{filter:"drop-shadow(0 0 30px rgba(255,248,238,.35))"},${r3(lg + 1.267)});`);
  s.write(); scenes.push(s);
}

// ================= captions =================
// Layout: the small lead line (above) and tail line (below) are placed from the glyph outlines of the big word,
// so the gap between the ink is always GAP_L / GAP_T px, whatever letters the script word has.
const BETA = (m) => 0.5 + (m.win.asc - m.win.desc) / (2 * m.upm);   // baseline from the top of a line-height:1 box (Chrome, measured)
const BO = BETA(FMO), BA = BETA(FMA), GAP_L = 12, GAP_T = 10;
const REMOVE = new Set([0, 16, 17, 44, 58, 61, 62, 64, 65, 66, 1, 18, 34, 42, 59, 60, 6, 20, 21, 63, 69, 70, 71, 72, 73]);   // v23: 8-15, 56 and 57 are back (the reviewer's notes at 0:09, 0:12, 0:50)
const KSET = new Set([2, 25, 58, 61, 62, 19, 24, 26, 27, 28, 39, 47, 56, 8, 9, 10, 11, 12, 13, 14, 15, 57]);
const FLK = { 24: 0.08 };
const INV = new Set([]);   // v16: no inverted captions any more; every caption carries a glow
const SMALL = new Set([13, 14, 15, 19, 39, 56, 57]);
// word times measured on the tightened audio (new clock) where the original transcript was off
const NEWT = { 5: [7.32, 7.45, 7.67, 8.07, 8.15].map(F1), 50: [50.94, 51.18, 51.35].map(F1),
  // v23: the captions brought back at 0:09, 0:12 and 0:50 (the reviewer), timed from the voiceover's own word list
  8: [8.93], 9: [9.272, 9.363, 9.445, 9.662], 10: [9.962], 11: [10.37, 10.497, 10.633], 12: [11.077, 11.149, 11.304],
  13: [11.643, 11.915], 14: [12.386, 12.451], 15: [12.843, 12.997, 13.224, 13.496],
  56: [49.762, 50.143, 50.406], 57: [50.923, 51.431, 51.866, 52.256] };
const cards = [];
RAW.forEach((c, i) => {
  if (REMOVE.has(i)) return;
  let src = c.words;
  if (i === 43) src = [...c.words, ...RAW[44].words.map((w) => ({ ...w, r: "t" }))];   // v16: "walk away from a sale worth" as one caption
  if (i === 5) src = [{ text: "to", r: "l" }, { text: "their", r: "l" }, { text: "PhDs", r: "h" }, { text: "at", r: "t" }, { text: "Stanford,", r: "t" }];
  if (i === 57) src = [{ text: "$25", r: "l" }, { text: "million", r: "l" }, { text: "funding", r: "l" }, { text: "round.", r: "l" }];   // v23: small, under the headline that already shows the figure
  let words = src.map((w, j) => ({ ...w, t: NEWT[i] ? NEWT[i][j] : WT(w.text, w.t, j === src.length - 1 && /[.,]$/.test(w.text)) }));
  let num = c.num ? { ...c.num, t: M(c.num.t), t0: M(c.num.t0), t1: M(c.num.t1) } : null;
  if (i === 0) num = { ...num, from: 1999, to: 1999, t0: num.t, t1: num.t, big: 400 };
  if (i === 45) num = { ...num, from: 500000, t1: r3(num.t0 + 0.85), ease: "cio" };   // v17 0:40: counts up to $750,000
  if (i === 63) num = { ...num, roll: true, big: 300, t1: r3(num.t0 + 0.6) };            // v17 0:58: the year rolls on a drum
  if (i === 57) num = null;
  const k = { ...c, i, t: Math.min(words.length ? words[0].t : 1e9, num ? num.t : 1e9), words, num, mode: KSET.has(i) ? "K" : "L", inv: INV.has(i), small: SMALL.has(i), strike: c.strike ? M(c.strike) : undefined };
  { const s0 = k.t, s1 = Math.max(k.t + 0.3, (k.words.length ? k.words[k.words.length - 1].t : k.t) + 0.35); k.onVoid = VOIDS.some(([a, b]) => Math.min(b, s1) - Math.max(a, s0) >= 0.6 * (s1 - s0)); }
  if (k.small) { k.words = k.words.map((w) => ({ ...w, r: "l" })); k.layout = undefined; k.pos = [19, 39, 56].includes(i) ? "below" : undefined; }
  if (i === 39) { k.punchText = "willing"; k.pos = "below2"; }
  if (i === 15) k.punchText = "Excite";
  if (i === 33) { k.layout = "quote"; k.pos = "quote"; }                    // v17 0:30: the quote block left of Bell
  if (i === 63) k.gapL = 100;                                               // v17: room above the year drum for its sliver
  if (i === 16) k.pos = undefined;                                          // 0:16: centred like its neighbours
  if (i === 40 || i === 41) k.layout = undefined;                          // 0:36 corkboard
  if (k.t >= M(48.97) && k.pos === "low") k.pos = undefined;               // v15: from 0:36 on, captions sit in the centre
  if (i === 19 || i === 39) k.pos = "below3";                              // under the Bell portraits
  // v23: 0:09 over the Excite page, all three in its lower part; 0:12 small, in the free strip under the polaroids; 0:50
  // small, under the logos and the press-release headline
  if (i === 9 || i === 10) k.pos = "low";
  if (i === 13 || i === 14 || i === 15) k.pos = "low2";
  if (i === 56 || i === 57) k.pos = "below3";
  if (i === 58) { k.words = k.words.map((w) => ({ ...w, r: "l" })); k.leadSize = 92; }   // "Meanwhile," in the sans
  if (i === 68) {
    { const ws68 = k.words.filter((w) => w.r !== "t").map((w) => ({ ...w, r: "l" }));   // v17: over the campus footage, two words at a time, centred, lit
      for (let g = 0; g < ws68.length; g += 2) { const ws = ws68.slice(g, g + 2); cards.push({ ...k, i: g + 2 >= ws68.length ? "68a" : `68ac${g}`, num: null, words: ws, mode: "L", pos: undefined, t: ws[0].t }); } }
    cards.push({ ...k, i: "68b", layout: "chunks", num: null, words: [], chunks: [["$4", F1(71.13)], [",000,000", F1(71.45)], [",000,000", F1(71.75)]], t: F1(71.13) });
    return;
  }
  // v15: over footage, a one-line caption shows two words at a time (stacked layouts stay as they are)
  const oneLine = !k.num && !k.words.some((w) => w.r === "h") && k.layout !== "chunks";
  if (oneLine && !k.onVoid && k.words.length > 2) {
    for (let g = 0; g < k.words.length; g += 2) {
      const ws = k.words.slice(g, g + 2), last = g + 2 >= k.words.length;
      cards.push({ ...k, i: last ? k.i : `${k.i}c${g}`, words: ws, t: ws[0].t, punchText: ws.some((w) => w.text === k.punchText) ? k.punchText : undefined });
    }
    return;
  }
  cards.push(k);
});
const ENDS = { 63: 80.98, 15: 18.61, 0: 2.03, 7: 11.58, 12: 15.54, 19: 25.02, 30: 37.03, 33: 41.97, 41: 52.97, 55: 67.92, 57: 72.08, 58: 72.99, 66: 83.45, "68a": 85.57, "68b": 88.37 };
cards.forEach((c, n) => { c.end = ENDS[c.i] !== undefined ? M(ENDS[c.i]) : c.end !== undefined ? M(c.end) : (cards[n + 1] ? r3(cards[n + 1].t - 0.06) : END); });
cards.forEach((c) => { if (c.i === "68a") c.end = r3(F1(71.13) - 0.06); });   // v17: "around" holds over the city until the $4 lands
const capSize = (text, base, per) => Math.round(Math.min(base, 1650 / Math.max(1, text.length * per)));
const HK = 0.8;   // v20: Bodoni Moda is wider and taller than OPTI Zither - the big words at 80% keep the old footprint
function fmtNum(v, f) { if (f === "B") return "$" + (Math.round(v * 10) / 10).toFixed(1) + "B"; if (f === "ishort") return "$" + Math.round(v); if (f === "year") return String(Math.round(v)); if (f === "short") return "$" + (Math.round(v * 10) / 10); return "$" + Math.round(v).toLocaleString("en-US"); }
const numLs = (fmt) => (fmt === "B" || fmt === "short" ? -0.02 : -0.01);   // v20: Bodoni Moda figures keep their own spacing
const SPAN_GAP = 0.24;
function runOf(texts, font, size, ls) {
  let x = 0; const glyphs = [];
  texts.forEach((t, k) => { if (k) x += SPAN_GAP * size; const r = font.layout(t, size, ls); r.glyphs.forEach((g) => glyphs.push({ ...g, x0: g.x0 + x })); x += r.width; });
  return { glyphs, width: x };
}
// css vars that size the punch-flicker box to the word's ink rather than the font's line box
function inkVars(font, text, size, ls, beta) {
  const i = ink(font.layout(text, size, ls), size), pad = Math.round(size * 0.07);
  return `--it:${Math.round(beta * size - i.top - pad)}px;--ib:${Math.round(size - (beta * size - i.bot) - pad)}px`;
}

// v17 (0:58): the year rolls on a drum, after the user's "ROLL" reference - 1999 -> 2000 -> 2001 coming down from above,
// each face squashed by its angle on the cylinder and widened a touch at the edges (the reference's warp); the
// neighbours show as slivers at the window's hard top and bottom edges. The drum turns on a stepped easeInOutCirc, so it
// rolls on the film's 8 fps steps; the faces are set from the turn in an onUpdate (seek-safe: a pure function of it).
function ROLL(id, wid, n, sz, J) {
  const H = ink(FMO.layout("2001", sz, -0.17), sz);
  const hInk = H.top - H.bot, cy = r3(BO * sz - (H.top + H.bot) / 2);   // digit ink height; ink centre from the box top
  const R = r3(hInk * 1.02), STEP = 60, years = [1998, 1999, 2000, 2001, 2002], pad = Math.round(hInk * 0.42);
  const D = r3(n.t1 - n.t0);
  const face = (j) => { const a = ((j - 1) * STEP) * Math.PI / 180, c = Math.cos(a); return `opacity:${c > 0.06 ? 1 : 0};transform:translateY(${r3(-R * Math.sin(a))}px) scale(${r3(1 + 0.07 * (1 - c))},${r3(Math.max(c, 0.001))})`; };
  J.push(`(function(){var o={p:0},fs=document.querySelectorAll("#${id}-drum .rf");tl.fromTo(o,{p:0},{p:1,duration:${D},ease:cio(${D}),onUpdate:function(){for(var j=0;j<fs.length;j++){var a=((j-1)*${STEP}-o.p*${2 * STEP})*Math.PI/180,c=Math.cos(a);fs[j].style.opacity=c>0.06?1:0;fs[j].style.transform="translateY("+(-${R}*Math.sin(a)).toFixed(2)+"px) scale("+(1+0.07*(1-c)).toFixed(4)+","+Math.max(c,0.001).toFixed(4)+")";}}},${r3(n.t0)});})();`);
  const top = r3(cy - hInk / 2 - pad);
  const faces = years.map((y, j) => `<span class="rf g" style="transform-origin:50% ${cy}px;${face(j)}">${y}</span>`).join("");
  return `<span id="${wid}" class="w num roll f-${n.fmt}" data-f="0" data-layout-allow-occlusion style="font-size:${sz}px;${inkVars(FMO, "2001", sz, -0.17, BO)}"><span class="tx" id="${wid}-t"><span class="g rsz">2001</span><span class="rwin" style="top:${top}px;height:${r3(hInk + 2 * pad)}px"><span class="rdrum" id="${id}-drum" style="top:${-top}px">${faces}</span></span></span></span>`;
}
function buildCaptionComp(compId, list, inv) {
  const H = [], J = [];
  list.forEach((c) => {
    const id = `${compId}-${c.i}`, ink2 = c.mode === "K";
    const lead = c.words.filter((w) => w.r === "l" || w.r === "m"), hero = c.words.filter((w) => w.r === "h"), tail = c.words.filter((w) => w.r === "t");
    const heroText = hero.map((w) => w.text).join(" ");
    const hs = Math.min(Math.round(capSize(heroText, 236, 0.4) * HK), Math.floor(1000 / Math.max(0.1, FMO.layout(heroText, 1, 0).width)));
    let k = 0; const rises = [];
    const span = (w, cls, size) => {
      const wid = `${id}-w${k++}`, isH = cls === "hero";
      rises.push({ wid, t: w.t, size, hero: isH, text: w.text });
      const v = isH ? inkVars(FMO, w.text, size, 0, BO) : inkVars(FMA, w.text, size, -0.02, BA);
      return `<span id="${wid}" class="w ${cls}${w.slide ? " slide" : ""}" data-f="0" style="font-size:${size}px;${v}"><span class="tx" id="${wid}-t">${esc(w.text)}</span></span>`;
    };
    const numSpan = (n, sz) => {
      const wid = `${id}-num`; rises.push({ wid, t: n.t, size: sz, hero: true, num: true }); if (n.roll) return ROLL(id, wid, n, sz, J);
      if (n.t1 > n.t0) J.push(`(function(){var o={v:${n.from}},e=document.querySelector("#${id}-nv");tl.fromTo(o,{v:${n.from}},{v:${n.to},duration:${r3(n.t1 - n.t0)},ease:${n.ease || "xo"}(${r3(n.t1 - n.t0)}),onUpdate:function(){e.textContent=fmt(o.v,"${n.fmt}")}},${n.t0});})();`);
      const v = inkVars(FMO, fmtNum(n.to, n.fmt), sz, numLs(n.fmt), BO);
      return `<span id="${wid}" class="w num f-${n.fmt}" data-f="0" data-layout-allow-occlusion style="font-size:${sz}px;${v}"><span class="tx" id="${wid}-t"><span class="g" data-layout-allow-occlusion id="${id}-nv">${fmtNum(n.from, n.fmt)}</span></span></span>`;
    };
    let body;
    const has = hero.length || c.num;
    if (c.layout === "chunks") {
      // $4,000,000,000,000 in the sans, building $4 | ,000,000 | ,000,000 on four / trillion / dollars
      const full = c.chunks.map((x) => x[0]).join("");
      const NS = 132;   // v17: Inter ExtraBold figures; v18: a touch smaller (~1250 px) so it sits between Ruth Porat and David Rubenstein, clear of both
      body = `<div class="hl chunks">${c.chunks.map(([txt, t], j) => { const wid = `${id}-k${j}`; rises.push({ wid, t, size: NS, hero: true, num: true }); return `<span id="${wid}" class="w num f-T sans" data-f="0" data-layout-allow-occlusion style="font-size:${NS}px;${inkVars(FMA, full, NS, -0.03, BA)}"><span class="tx" id="${wid}-t"><span class="g" data-layout-allow-occlusion>${esc(txt)}</span></span></span>`; }).join("")}</div>`;
    } else if (c.layout === "quote") {
      // v17 (0:30): a left-aligned quote block beside Bell (after the user's reference): opening mark, "He says the price",
      // $750,000 with the strike through it, "wasn't the problem.", closing mark
      // v18: every word only blurs in (no pop-up), and $750,000 is set exactly like the figure at 0:41 - the display serif
      // figures with the same light fill and glow (the caption .num style) - sized to the block, its strike through the
      // middle of the digits' ink
      const QS = 80, NTXT = fmtNum(c.num.to, c.num.fmt), NLS = numLs(c.num.fmt), NSZ = Math.min(210, Math.floor(660 / FMO.layout(NTXT, 1, NLS).width));
      const NI = ink(FMO.layout(NTXT, NSZ, NLS), NSZ), ncy = r3(BO * NSZ - (NI.top + NI.bot) / 2), padT = r3(BO * NSZ - NI.top), padB = r3(NSZ - (BO * NSZ - NI.bot));
      const qspan = (w) => { const wid = `${id}-w${k++}`; rises.push({ wid, t: w.t, size: QS, text: w.text, anim: "blur" }); return `<span id="${wid}" class="w lead qw2" style="font-size:${QS}px"><span class="tx" id="${wid}-t">${esc(w.text)}</span></span>`; };
      const mk = (q, t, flip) => { const wid = `${id}-q${q}`; rises.push({ wid, t, anim: "blur" }); return `<span id="${wid}" class="w qmk"><span class="tx" id="${wid}-t"><img src="assets/img/quote.png" alt=""${flip ? ' class="qflip"' : ""}></span></span>`; };
      const nwid = `${id}-num`; rises.push({ wid: nwid, t: c.num.t, anim: "blur" });
      if (c.strike) J.push(`tl.fromTo("#${id}-st",{scaleX:0},{scaleX:1,duration:0.45,ease:cio(0.45)},${r3(c.strike)});`);
      const lastT = tail.length ? tail[tail.length - 1].t : c.num.t;
      body = `<div class="qb"><div class="qrow">${mk(0, c.t, false)}</div>
<div class="qrow">${lead.map(qspan).join("")}</div>
<div class="qrow" style="margin-top:${r3(22 - padT)}px;margin-bottom:${r3(4 - padB)}px"><span id="${nwid}" class="w num f-${c.num.fmt}" data-layout-allow-occlusion style="font-size:${NSZ}px"><span class="tx" id="${nwid}-t"><span class="g" data-layout-allow-occlusion>${NTXT}</span><i class="qstrike" id="${id}-st" style="top:${r3(ncy - 7)}px;margin-top:0"></i></span></span></div>
<div class="qrow">${tail.map(qspan).join("")}</div>
<div class="qrow qend">${mk(1, r3(lastT + 0.12), true)}</div></div>`;
    } else if (c.layout === "inline") {
      const NS = c.num ? (c.num.big || 330) : 0, parts = [];
      if (c.num) parts.push(numSpan(c.num, NS));
      c.words.forEach((w) => parts.push(w.r === "h" ? span(w, "hero", Math.round((c.num ? NS * 0.5 : 150) * HK)) : span(w, "lead", 64)));
      body = `<div class="il">${parts.join("")}</div>`;
    } else if (!has) {
      const Ls = c.leadSize || (c.small ? (c.inv ? 84 : 56) : 70);
      // v15: a one-line text cover on black gets uneven, wide word spacing
      const GAPS = [0, 1.3, 0.75, 1.55, 1.0, 1.25, 0.65];
      body = `<div class="ll1">${lead.map((w, j) => { const h = span(w, "lead", Ls); return c.onVoid && j && c.i === 22 ? h.replace('style="', `style="margin-left:${GAPS[j % GAPS.length]}em;`) : h; }).join("")}</div>`;
    } else {
      // big word(s) or figure, with the small lead line above and the tail line below placed from the glyph ink
      const Ls = 56, Ts = 56;
      let S, Htexts, Hls, heroHTML;
      if (c.num) { S = Math.min(Math.round((c.num.big || capSize(fmtNum(c.num.to, c.num.fmt) + "0", 330, 0.5)) * HK), Math.floor(1250 / FMO.layout(fmtNum(c.num.to, c.num.fmt), 1, numLs(c.num.fmt)).width)); Htexts = [fmtNum(c.num.to, c.num.fmt)]; Hls = numLs(c.num.fmt); heroHTML = numSpan(c.num, S); }
      else { S = hs; Htexts = hero.map((w) => w.text); Hls = 0; heroHTML = hero.map((w) => span(w, "hero", S)).join(""); }
      const Hrun = runOf(Htexts, FMO, S, Hls), Hi = ink(Hrun, S);
      let strike = "";
      if (c.strike) {
        strike = `<div class="strike" id="${id}-st" style="top:${Math.round(BO * S - 0.25 * S - 7)}px"></div>`;
        J.push(`tl.fromTo("#${id}-st",{scaleX:0},{scaleX:1,duration:0.3,ease:voxOut(0.3)},${r3(c.strike)});`);
      }
      const rows = [{ cls: "hl", html: heroHTML + strike, x: 0, y: 0, ink: { l: Hi.left, r: Hi.right, t: BO * S - Hi.top, b: BO * S - Hi.bot } }];
      if (lead.length) {
        const Lrun = runOf(lead.map((w) => w.text), FMA, Ls, -0.02), Li = ink(Lrun, Ls);
        const under = ink(Hrun, S, Hi.left, Hi.left + (Li.right - Li.left));
        const x = Hi.left - Li.left, y = (BO * S - under.top) - GAP_L - (c.gapL || 0) - (BA * Ls - Li.bot);
        rows.push({ cls: "ll", html: lead.map((w) => span(w, "lead", Ls)).join(""), x, y, ink: { l: x + Li.left, r: x + Li.right, t: y + BA * Ls - Li.top, b: y + BA * Ls - Li.bot } });
      }
      if (tail.length) {
        const Trun = runOf(tail.map((w) => w.text), FMA, Ts, -0.02), Ti = ink(Trun, Ts);
        const under = ink(Hrun, S, Hi.right - (Ti.right - Ti.left), Hi.right);
        const x = Hi.right - Ti.right, y = (BO * S - under.bot) + GAP_T - (BA * Ts - Ti.top);
        rows.push({ cls: "tl2", html: tail.map((w) => span(w, "lead", Ts)).join(""), x, y, ink: { l: x + Ti.left, r: x + Ti.right, t: y + BA * Ts - Ti.top, b: y + BA * Ts - Ti.bot } });
      }
      // the group box is the union of the visible ink, so the caption centres on what you can see
      const mx = Math.min(...rows.map((r) => r.ink.l)), Mx = Math.max(...rows.map((r) => r.ink.r)), my = Math.min(...rows.map((r) => r.ink.t)), My = Math.max(...rows.map((r) => r.ink.b));
      body = `<div class="grp2" style="width:${Math.round(Mx - mx)}px;height:${Math.round(My - my)}px">${rows.map((r) => `<div class="row ${r.cls}" style="left:${Math.round(r.x - mx)}px;top:${Math.round(r.y - my)}px">${r.html}</div>`).join("")}</div>`;
    }
    for (const r of rises) {
      const t0 = r3(Math.max(c.t, r.t - 0.03));
      // v15: on the black text covers, and for the big words and figures, words just appear one by one (no animation);
      // the small words over footage fade in fast on a stepped easeOutExpo (nothing linear)
      if (r.anim === "blur") J.push(`tl.fromTo("#${r.wid}-t",{opacity:0,filter:"blur(14px)"},{opacity:1,filter:"blur(0px)",duration:0.4,ease:cio(0.4)},${t0});`);   // v18: blur in only, no pop-up (on the inner box, so the figure keeps its glow)
      else if (c.onVoid || r.hero || r.num) J.push(`tl.set("#${r.wid}-t",{opacity:0},0);tl.set("#${r.wid}-t",{opacity:1},${t0});`);
      else J.push(`tl.fromTo("#${r.wid}-t",{opacity:0},{opacity:1,duration:0.25,ease:xo(0.25)},${t0});`);
    }
    if (!inv && c.layout !== "quote" && !(c.num && c.num.roll)) {
      let p = c.punchText ? rises.find((r) => r.text === c.punchText) : null;
      if (!p) p = [...rises].reverse().find((r) => r.hero) || null;
      if (!p && rises.length >= 3 && /[.,]$/.test(rises[rises.length - 1].text || "")) p = rises[rises.length - 1];
      if (p) {
        const land = Math.max(c.t, p.t - 0.03) + 0.05;
        // v23: FLK - a flash asked for on a caption too short for the usual one sits earlier ("Google" at 0:22)
        const fo = FLK[c.i], f0 = land + (fo ?? 0.25);
        if (fo !== undefined || c.end - land > 0.5) J.push(`tl.set("#${p.wid}",{attr:{"data-f":"1"}},${r3(f0)});tl.set("#${p.wid}",{attr:{"data-f":"0"}},${r3(f0 + 0.034)});tl.set("#${p.wid}",{attr:{"data-f":"1"}},${r3(f0 + 0.1)});tl.set("#${p.wid}",{attr:{"data-f":"0"}},${r3(f0 + 0.167)});`);
      }
    }
    const pos = c.pos === "low" ? "align-items:flex-end;padding-bottom:150px" : c.pos === "right" ? "justify-content:flex-end;padding-right:170px" : c.pos === "below" ? "align-items:flex-start;padding-top:600px" : c.pos === "below3" ? "align-items:flex-start;padding-top:760px" : c.pos === "low2" ? "align-items:flex-end;padding-bottom:64px" : c.pos === "below2" ? "align-items:flex-start;padding-top:690px" : c.pos === "top" ? "align-items:flex-start;padding-top:24px" : c.pos === "top2" ? "align-items:flex-start;padding-top:70px" : c.pos === "quote" ? "justify-content:flex-start;padding-left:140px" : "";
    const st = r3(Math.max(0.03, c.t - 0.05));
    H.push(`<div id="${id}" class="clip cap ${inv ? "invc" : ink2 ? "ink" : "lit"}" data-layout-allow-overlap data-start="${st}" data-duration="${r3(Math.max(0.2, c.end - st))}" data-track-index="1" style="${pos}">${body}</div>`);
  });
  const css = `${FONTFACE}
#root{position:absolute;inset:0;overflow:visible;}
.cap{position:absolute;left:0;top:0;width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;overflow:visible;}
.grp2{position:relative;flex:none;}
.row{position:absolute;font-size:0;line-height:0;white-space:nowrap;}
.ll1{font-size:0;line-height:0;white-space:nowrap;}
.hl{white-space:nowrap;line-height:1;}
.il{white-space:nowrap;line-height:1;display:flex;align-items:baseline;}
.il .w + .w{margin-left:.22em;}
.il .lead + .hero{margin-left:.26em;}
.w{position:relative;display:inline-block;line-height:1;}
.tx{position:relative;z-index:0;display:inline-block;padding:0 .08em;margin:0 -.08em;}
.lead{font-family:Almarai,sans-serif;font-weight:700;letter-spacing:-.02em;white-space:pre;}
.hero{font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;letter-spacing:-.005em;}
.num{font-family:"Bodoni Cursive",serif;font-style:italic;font-weight:500;letter-spacing:-.01em;}
.num.f-B,.num.f-short{letter-spacing:-.02em;}
.num.f-T{font-family:Almarai,sans-serif;font-weight:700;letter-spacing:-.03em;}
.lit .w{color:${LIGHT};}
.lit .tx{text-shadow:0 0 20px rgba(255,248,238,.45),0 0 56px rgba(255,248,238,.22),0 3px 14px rgba(0,0,0,.55);}
.ink .w{color:${INK};}
.ink .tx{text-shadow:0 0 16px rgba(255,255,255,.95),0 0 40px rgba(255,255,255,.65);}
.invc .w{color:#fff;opacity:.9;}
.num .tx{text-shadow:none;padding:0 .12em;margin:0 -.12em;}


.num .g{color:inherit;}   /* v21: solid figures - the fade to transparent at the foot softened the strokes */
.ink .num .g{color:inherit;}
.lit .num{filter:none;}
/* v21: the cursive stays crisp - no tight halo on its edges, only a wide soft glow and the shadow that lifts it off footage */
.lit .hero .tx{text-shadow:0 2px 5px rgba(0,0,0,.42),0 6px 28px rgba(0,0,0,.6),0 0 60px rgba(255,244,228,.22);}
.lit .num .tx{text-shadow:0 2px 5px rgba(0,0,0,.42),0 6px 28px rgba(0,0,0,.6),0 0 54px rgba(255,244,228,.38),0 0 110px rgba(255,236,210,.24);}
.lit .qb .num .tx{text-shadow:0 2px 5px rgba(0,0,0,.42),0 6px 24px rgba(0,0,0,.5);}   /* 0:30: no glow on the struck figure (the user's note) */
.lead + .lead{margin-left:.24em;}
.hero + .hero{margin-left:.24em;}
.hero + .hero.slide{margin-left:0;}
.strike{position:absolute;left:-3%;right:-3%;height:14px;background:#C8102E;transform-origin:0 50%;box-shadow:0 0 12px rgba(200,16,46,.45);}
.chunks{display:flex;align-items:baseline;}
.chunks .g{display:inline-block;padding:0 .22em;margin:0 -.22em;}
/* v17: the bold-sans figures ($4,000,000,000,000 at 1:03): Inter ExtraBold digits, solid fill, the caption glow */
.num.sans{font-family:Inter,sans-serif;font-weight:800;letter-spacing:-.035em;font-variant-numeric:tabular-nums;}
.num.sans .g{background:none;-webkit-text-fill-color:currentColor;color:inherit;}
.lit .num.sans{filter:none;}
.lit .num.sans .tx{text-shadow:0 0 20px rgba(255,248,238,.45),0 0 56px rgba(255,248,238,.22),0 3px 14px rgba(0,0,0,.55);}
/* v17: the quote block at 0:30 */
.qb{position:relative;flex:none;display:flex;flex-direction:column;align-items:flex-start;}
.qrow{white-space:nowrap;line-height:1;font-size:0;}
.qrow + .qrow{margin-top:16px;}
.qw2 + .qw2{margin-left:.24em;}
.qmk{display:inline-block;line-height:0;}
.qmk .tx{padding:0;margin:0;}
.qmk img{display:block;width:84px;height:auto;filter:drop-shadow(0 0 16px rgba(255,248,238,.5)) drop-shadow(0 0 40px rgba(255,248,238,.22));}
.qmk img.qflip{transform:rotate(180deg);}
.qend{align-self:flex-end;margin-top:20px;}
.qnum{font-family:Inter,sans-serif;font-weight:800;letter-spacing:-.035em;font-variant-numeric:tabular-nums;line-height:1;}
.qstrike{position:absolute;left:-3%;right:-3%;top:50%;height:14px;margin-top:-4px;background:#C8102E;transform-origin:0 50%;display:block;}
/* v17: the year drum at 0:58 */
.roll .rsz{visibility:hidden;}
.rwin{position:absolute;left:-.3em;right:-.3em;overflow:hidden;}
.rdrum{position:absolute;left:.3em;right:.3em;height:1em;}
.rf{position:absolute;left:0;right:0;top:0;text-align:center;line-height:1;white-space:nowrap;}
/* punch flicker: one inverted frame, the box hugs the word's ink */
.w[data-f="1"] .tx::before{content:"";position:absolute;left:0;right:0;top:var(--it,0px);bottom:var(--ib,0px);z-index:-1;}
.lit .w[data-f="1"] .tx{color:${INK};text-shadow:none;}
.lit .w[data-f="1"] .tx::before{background:${LIGHT};box-shadow:0 0 26px 6px rgba(255,248,238,.7);}
.ink .w[data-f="1"] .tx{color:#fff;text-shadow:0 0 14px rgba(255,255,255,.95),0 0 30px rgba(255,255,255,.6);}
.ink .w[data-f="1"] .tx::before{background:${INK};box-shadow:0 0 22px rgba(0,0,0,.35);}
.w[data-f="1"] .g{background:none;-webkit-text-fill-color:${INK};color:${INK};}
.ink .w[data-f="1"] .g{-webkit-text-fill-color:#fff;color:#fff;}
`;
  fs.writeFileSync(path.join(ROOT, "compositions", `${compId}.html`), `<template>
<style>${css}</style>
<div id="root" data-composition-id="${compId}" data-width="1920" data-height="1080" data-layout-allow-overlap data-layout-allow-overflow>
${H.join("\n")}
</div>
<script>
${EASE_JS}
function fmt(v,f){if(f==="B")return "$"+(Math.round(v*10)/10).toFixed(1)+"B";if(f==="ishort")return "$"+Math.round(v);if(f==="year")return String(Math.round(v));if(f==="short")return "$"+(Math.round(v*10)/10);return "$"+Math.round(v).toLocaleString("en-US");}
const tl = gsap.timeline({ paused: true });
${J.join("\n")}
tl.set({}, {}, ${END});
window.__timelines["${compId}"] = tl;
</script>
</template>`);
}
buildCaptionComp("captions", cards.filter((c) => !c.inv), false);
buildCaptionComp("capinv", cards.filter((c) => c.inv), true);


// ================= sound effects =================
const sfx = [];
const peak = { whoosh: 0.162, "whoosh-low": 0.198, "whoosh-high": 0.135, "impact-bass-1": 0.073, pop: 0.12, click: 0.073, "glitch-1": 0.82, "glitch-3": 1.823, sparkle: 0.027 };
const durs = { whoosh: 0.575, "whoosh-low": 0.7, "whoosh-high": 0.48, "impact-bass-1": 1.6, pop: 0.72, click: 0.36, "glitch-1": 1.4, "glitch-3": 2.2, sparkle: 1.3 };
const add = (file, tOrig, vol, o = {}) => sfx.push({ file, st: r3(Math.max(0, M(tOrig) - (peak[file] || 0) + 1 / FPS)), d: o.d || durs[file], vol, ms: o.ms });
const W3 = ["whoosh", "whoosh-low", "whoosh-high"];
// one whoosh per cut between shots, rotating three takes
[2.03, 3.95, 7.08, 8.48, 9.28, 15.54, 18.61, 23.82, 25.02, 30.17, 33.13, 37.03, 37.87, 41.97, 42.67, 46.97, 52.97, 54.33, 58.58, 59.97, 60.82, 63.24, 64.53, 67.92, 69.51, 72.08, 79.2, 80.72, 83.45, 85.57, 88.37]
  .forEach((t, k) => add(W3[k % 3], t, 0.2));
add("whoosh-low", 12.05, 0.32);                                    // the zoom into the Excite page
add("whoosh-low", 34.2, 0.14);                                     // the camera eases back to the whole window
[5.95, 22.2, 27.36, 32.19, 56.15, 77.05, 82.0].forEach((t) => add("impact-bass-1", t, 0.14));
[11.62, 15.6, 15.9, 16.52, 17.2, 18.05, 23.9, 47.05, 50.99, 51.12, 67.99, 68.35, 83.5, 83.98, 84.25, 88.55].forEach((t) => add("pop", t, 0.26));
[25.02, 25.24, 25.46, 25.66].forEach((t) => add("click", t, 0.42)); // photo swaps in Bell's frame
add("whoosh-high", 26.15, 0.24);                                    // the frame steps up on "still"
[32.25, 58.72, 60.27, 69.6].forEach((t) => add("click", t, 0.4));   // highlighter strokes
[30.6, 32.6, 34.66].forEach((t) => add("click", t, 0.55));          // cursor clicks (the last one is the close box)
add("pop", 34.76, 0.2);                                             // the browser window shuts
add("glitch-1", 2.07, 0.13); add("glitch-1", 43.95, 0.2);
add("impact-bass-1", 43.97, 0.12);                                  // the bright flash, Excite -> Google
add("glitch-3", 82.0, 0.28);
add("whoosh-high", 40.29, 0.26);                                    // the line through $750,000
add("whoosh-low", 3.03, 0.2);                                       // the camera moves to Sergey
// the merge diagram: cards land, the dashed lines run, the camera opens out twice
[73.01, 73.7, 74.3, 75.64, 77.03].forEach((t) => add("pop", t, 0.24));


[71.13, 71.45, 71.75].forEach((t) => sfx.push({ file: "pop", st: r3(t - 0.12 + 1 / FPS), d: 0.6, vol: 0.3 }));   // $4 | ,000,000 | ,000,000
sfx.push({ file: "impact-bass-1", st: r3(71.83 - 0.073 + 1 / FPS), d: 1.6, vol: 0.15 });
add("whoosh-high", 83.75, 0.22);
sfx.push({ file: "typing", st: M(31.0), d: r3(M(32.0) - M(31.0)), vol: 0.45 });
[[5.4, 5.95], [20.64, 22.2], [79.6, 80.2]].forEach(([a, b]) => sfx.push({ file: "typing", st: M(a), d: r3(M(b) - M(a)), vol: 0.26 }));
sfx.push({ file: "riser", st: r3(M(85.59) - 3.0), d: 3.1, vol: 0.15, fo: 0.25, ms: 0.47 });
add("sparkle", 94.5, 0.14);

V9SFX.forEach((x) => sfx.push(x));
for (let i = sfx.length - 1; i >= 0; i--) if (sfx[i].file === "pop") sfx.splice(i, 1);
sfx.length = 0;   // v14: no sound effects anywhere, voiceover only
const flashes = [...V10FLASH, ...FLASH17, ...FLASH18].sort((p, q) => p - q);   // v18: five flash transitions - 0:09, 0:27, 0:34, 0:58, 1:03
const inverts = [];
const dips = [];


// ================= index =================
const hosts = scenes.map((s, k) => `      <div id="${s.id}" class="clip" data-composition-id="${s.id}" data-composition-src="compositions/${s.id}.html" data-start="${r3(s.t0)}" data-duration="${r3(s.t1 - s.t0)}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:${k + 1}"></div>`).join("\n");
const aud = sfx.map((x, k) => `      <audio id="sfx${k}" src="assets/sfx/${x.file}.mp3" data-start="${x.st}" data-duration="${r3(Math.min(x.d, END - x.st - 0.01))}"${x.ms ? ` data-media-start="${x.ms}"` : ""} data-track-index="${3 + (k % 3)}" data-volume="${x.vol}"${x.fo ? ` data-fade-out="${x.fo}"` : ""}></audio>`).join("\n");
let js = ""; let seed = 1337;
const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
for (let f = 0; f < END * FPS; f += 2) js += `tl.set("#grain",{x:${-Math.round(rnd() * 480)},y:${-Math.round(rnd() * 320)}},${r3(f / FPS)});\n`;
// v18: a flash transition - near-white on the cut itself, then a stepped easeInOutCirc decay over the incoming shot. Nothing
// before the cut: a lift over an outgoing black text cover read as a grey frame (the 0:26 complaint)
flashes.forEach((t, k) => (js += `tl.set("#fl${k}-i",{opacity:0.95},${r3(t)});tl.fromTo("#fl${k}-i",{opacity:0.95},{opacity:0,duration:0.3,ease:cio(0.3),immediateRender:false},${r3(t + 0.034)});\n`));
fs.writeFileSync(path.join(ROOT, "index.html"), `<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }
      body { font-family: "Inter", sans-serif; }
      .fx { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; pointer-events: none; }
      #grunge { background: url("assets/tex/grunge.jpg") center / cover; mix-blend-mode: overlay; opacity: 0.6; z-index: 59; }
      #halftone { background: url("assets/tex/halftone.png") 0 0 / 1920px 1080px; mix-blend-mode: overlay; opacity: 0.2; z-index: 60; }
      #grainwrap { overflow: hidden; z-index: 61; mix-blend-mode: overlay; opacity: 0.22; }
      #grain { position: absolute; left: 0; top: 0; width: 2400px; height: 1400px; background: url("assets/tex/grain.png") 0 0 / 2400px 1400px; }
      #lift { background: #2a2119; mix-blend-mode: screen; opacity: 0.3; z-index: 62; }
      #desat { background: #808080; mix-blend-mode: saturation; opacity: 0.2; z-index: 63; }
      #vig { background: radial-gradient(ellipse 72% 72% at 50% 50%, rgba(0,0,0,0) 42%, rgba(0,0,0,.26) 66%, rgba(0,0,0,.6) 86%, rgba(0,0,0,.84) 100%); z-index: 64; }
      #flick { background: #fff; z-index: 65; opacity: 0; }
      /* CRT scanlines: thin dark lines every 6px, mild */
      #scan { background: repeating-linear-gradient(0deg, rgba(0,0,0,.7) 0px, rgba(0,0,0,.7) 2px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 5px); mix-blend-mode: multiply; opacity: 0.42; z-index: 66; }
      #capinv { mix-blend-mode: difference; }
      .fx-flash > div { position:absolute; inset:0; background:#fff8ee; }
      .fx-inv { background:#fff; mix-blend-mode: difference; }
      .fx-dip { background:#000; opacity:.65; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${END}" data-width="1920" data-height="1080" data-fps="30">
${hosts}
      <div id="grunge" class="clip fx" data-layout-allow-occlusion data-start="0" data-duration="${END}" data-track-index="7"></div>
      <div id="halftone" class="clip fx" data-start="0" data-duration="${END}" data-track-index="7"></div>
      <div id="grainwrap" class="clip fx" data-start="0" data-duration="${END}" data-track-index="7"><div id="grain"></div></div>
      <div id="lift" class="clip fx" data-start="0" data-duration="${END}" data-track-index="7"></div>
      <div id="desat" class="clip fx" data-start="0" data-duration="${END}" data-track-index="7"></div>
      <div id="vig" class="clip fx" data-layout-allow-occlusion data-start="0" data-duration="${END}" data-track-index="7"></div>
      <div id="flickwrap" class="clip fx" data-start="0" data-duration="${END}" data-track-index="7" style="z-index:65"><div id="flick" class="fx"></div></div>
      <div id="scan" class="clip fx" data-start="0" data-duration="${END}" data-track-index="7"></div>
      <div id="capinv" class="clip" data-composition-id="capinv" data-composition-src="compositions/capinv.html" data-start="0" data-duration="${END}" data-track-index="8" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:57"></div>
      <div id="captions" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="${END}" data-track-index="8" data-track-kind="captions" data-width="1920" data-height="1080" style="z-index:58"></div>
${flashes.map((t, k) => `      <div id="fl${k}" class="clip fx-flash" data-start="${r3(t)}" data-duration="0.4" data-track-index="9" style="z-index:90"><div id="fl${k}-i" style="opacity:0"></div></div>`).join("\n")}
${inverts.map((t, k) => `      <div id="iv${k}" class="clip fx-inv" data-start="${r3(t)}" data-duration="0.067" data-track-index="9" style="z-index:89"></div>`).join("\n")}
${dips.map((t, k) => `      <div id="dp${k}" class="clip fx-dip" data-start="${r3(t - 0.067)}" data-duration="0.067" data-track-index="9" style="z-index:88"></div>`).join("\n")}
      <audio id="mix" src="assets/audio/v23_mix.wav" data-start="0" data-duration="${END}" data-track-index="2" data-volume="1"></audio>
${aud}
    </div>
    <script>
      window.__timelines = window.__timelines || {};
${EASE_JS}
      const tl = gsap.timeline({ paused: true });
${js}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>`);
console.log("v23 END", END, "scenes", scenes.length, "cards", cards.length, "sfx", sfx.length);
