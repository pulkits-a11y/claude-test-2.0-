# KIT_screens: screen types L3, L4, L5, L6, L7, L11 (+ the B11 flip), L12, the L10 year tag, the L2 band

Files: `screens.css`, `screens.js` (exposes `RCK.screens`), this file. No SVG/image assets (the L5 cut-out filters are
injected by the JS).
Golden rule: the Master Edit Plan (`00_Brief/GTA_VI_Edit_Plan.pdf`): "Screen types (L1-L12)" p.13-15, the beat builds
p.19-27 (B1 p.19-20, B3/B4 p.21, B5/B6 p.22, B7/B9 p.23-24, B11 p.24-25, B13 p.25, B14/B15 p.26). Every number below
comes from those pages unless it is marked **kit choice** (the plan gives no value) or **interp** (the plan is read one
way of two); all of them are listed again in section 11.
Proof: `hyperframes/_demo-screens/` plays every item in sequence, built exactly as a beat would (kit copied to
`assets/kit/`, footage via `tools/sync_footage.py`); named stills + zoom crops in `_demo-screens/review/`.
L1, L2, L10 footage framings are Tesseract-owned; L8 (CRT) and L9 (calendar) are in `KIT_motifs.md`.

## v02 (REVISION_v02.md rules C and D): camera moves, nothing linear. Read this first

The v01 reference below still describes every screen; this section lists what v02 changes and the new camera API.
Proof: `hyperframes/_demo-v02/` (sections A, B, E: push / zoomOut / punchIn / keyPunch; values in
`review/measure_v02.json` `camera`).

Easing map (easings.net name -> GSAP -> CSS bezier, and which curve the kit uses where): KIT_type.md, v02 > Easing
(`RCK.ease`, defined in type.js). Every helper's `opts.ease` accepts `'easeOutExpo'` or `'expo.out'`.

### Camera on the picture (rule D), `RCK.cam` (screens.js; the zoom-through halves come from transitions.js)

All camera helpers scale ONE untimed full-frame picture wrapper, `class="rc-cam"` (screens.css), that holds the footage /
card; captions stay outside it, steady ("zoom the picture, not the caption layer"). `force3D: false` (re-rasterised every
frame, sharp). Signature as every kit helper: `(tl, wrapper, atSeconds, opts) -> endSeconds`; `opts.ease` takes an
easings.net or GSAP name; `opts.origin` (default centre; one origin per wrapper, it applies to all its moves).

| Helper | Rule D | Defaults | Measured (demo frames) |
|---|---|---|---|
| `C.push(tl, el, at, { until \| durF, from, to, ease, origin, x, y })` | held footage: push 100 -> 106-110% across the shot, sine.inOut | from = the scale the wrapper's previous move left (else 1), to = from x 1.08, easeInOutSine; `x` / `y` = an optional drift (px) on the same curve | f50 100% -> f75 101.2% -> f100 104.0% -> f125 106.8% -> f149 108% |
| `C.zoomOut(tl, el, at, { until \| durF, from, to, ease })` | "alternate with slow zoom-outs (110 -> 100%)" | 110% -> 100%, easeInOutSine | f0 110% -> f10 108.5% -> f20 105% -> f30 101.5% -> f39 100% |
| `C.punchIn(tl, el, cutAt, { from, to, frames, ease })` | cuts: 112-118% -> 100-102% over 8-12f, expo.out | 115% -> 100% over 10f, easeOutExpo; the cut frame shows 115% | f40 115%, f41 107.6%, f42 103.8%, f43 101.8%, f45 100.4%, f50 100% |
| `C.keyPunch(tl, el, wordAt, { peak, inF, outF, lead, inEase, outEase, base })` | emphasis words: 100 -> 105-108% in 3-4f expo.out, back over 8-10f sine.inOut | 106% in 3f (easeOutExpo), back in 9f (easeInOutSine), `lead` 1: starts 1 frame before the onset so the onset frame already shows 105.4% | f124 100%, **f125 (onset) 105.4%**, f126 106.0%, f127 106% (peak), f130 104.5%, f133 101.5%, f136 100% |
| `C.zoomThroughOut` / `C.zoomThroughIn` / `C.zoomThrough` | transitions: zoom-throughs | see KIT_transitions.md v02 | |

`RCK.screens.push` is the same function as `RCK.cam.push` (also `zoomOut`, `punchIn`, `keyPunch` on `RCK.screens`).
"No more than about one punch per second" (rule D) is the builder's call; the helpers don't limit it.

**One wrapper, one move at a time; nest for overlaps.** Every helper drives the wrapper's scale. Moves on one wrapper
must follow each other in time (punchIn on the cut, then push to the next cut, then zoomThroughOut into the boundary);
each starts from the scale the previous one left. A move that overlaps another (a keyword punch during the push) goes on
a nested wrapper; the helpers keep a registry on each element and `console.warn` overlaps. Copy-paste:
```html
<div id="b05-cam" class="rc-cam" style="z-index: 1">       <!-- cut moves + held-shot push -->
  <div id="b05-key" class="rc-cam">                         <!-- keyword punches -->
    <video id="b05-v1" class="clip" src="assets/footage/R5.2.mp4" muted playsinline data-start="0.2000" data-duration="1.4000"></video>
    <video id="b05-v2" class="clip" src="assets/footage/R5.1.mp4" muted playsinline data-start="1.6000" data-duration="1.5666"></video>
  </div>
</div>
<!-- captions (rc-cap) outside the wrappers -->
```
```js
const C = RCK.cam, L = n => n / 30;
C.push(tl, '#b05-cam', L(6), { until: L(48) });           // shot 1: 100 -> 108%, sine.inOut
C.punchIn(tl, '#b05-cam', L(48), { from: 1.22, to: 1.10 });   // the cut to shot 2: punch settles at 110% (10f expo.out)
C.zoomOut(tl, '#b05-cam', L(58), { until: L(95) });       // ...then the alternate move: 110 -> 100%, sine.inOut
C.keyPunch(tl, '#b05-key', W.police);                     // "police officer": 100 -> 106 -> 100% on the inner wrapper
```
Inside the existing screens, use the screen's own untimed wrapper as the camera (e.g. `#b01-grow`, `.rc-l4__plate`,
`.rc-l12__drop` is taken by the drop: wrap the stack instead); `S.spotPush` already pushes the `.rc-l7` root (eased).
Footage-only Tesseract shots get the same moves from `tesseract_shots.json` framing keys (REVISION_v02 "framing v2").

### What changed in screens.js / screens.css

| Item | v01 | v02 |
|---|---|---|
| `S.push` (held shots) | 100 -> 104%, linear | to = from x 1.08 (rule D), easeInOutSine; starts from the previous move's scale; x / y drift option. Old calls with explicit `from` / `to` keep their values, now eased |
| L3 `gridPop` fade | opacity linear 4f | power2.out (easeOutCubic) 4f; the 96 -> 100% scale and the B9 punch stay power3.out |
| L4 `frostClear` | each tile clears linearly in 3f | power2.out in 3f (the sharp picture "fades in") |
| L5 `propFloat` / `collage` | sine path | unchanged: each leg is exactly easeInOutSine (rule C "float loops") |
| L7 `spotPush` | 100 -> 118% linear | easeInOutSine (the 118% stays) |
| L11 `splitDrain` (B6) | intensity 0 -> 1 linear over 6f | power2.inOut (a colour change between two rests) |
| L11 `rateRamp` (B6 "slows to 50%") | one linear rate segment | rate sampled from power2.inOut every 1/4 frame (`ease` option): 1.0, 0.99 ... 0.75 at mid ... 0.5; the runtime interpolates between the points. In Node, require type.js first for other curve names |
| L12 `cardsDrift` | linear | easeInOutSine |
| `S.hard` | 0.5f tween, ease none | 0.5f `steps(1)` tween (a cut) |
| internal `span()` | default ease none | default power2.inOut (every call names its ease) |
| `.rc-cam` (css) | | new: untimed full-frame camera wrapper |
| L10 tag, L6 label | Inter Medium 22 / Instrument Serif Italic 32 | Coolvetica 22 / Coolvetica Italic 32 (base.css), no layout change needed |

The L12 stacked cards, the L5 card with CANCELLED stamps and the B11 flip are not used by the v02 beats (B3 section
redesigned, B7 card removed, B11 flip -> X4 glitch) but stay in the kit, eased.

---

# v01 reference (still valid where the v02 section above does not override it)

## 0. How to use (every item)

**Setup.** `tools/new_beat.py` already links `assets/kit/screens.css` and `assets/kit/screens.js` (after GSAP,
`base.css` and the other kit files). Helpers live on `RCK.screens` (write `const S = RCK.screens;`).

**Helper contract.** `S.helper(tl, target, atSeconds, opts) -> endSeconds`: only adds tweens to YOUR paused timeline;
no timers, no `Date`, no `Math.random` (seeded `RCK.rng`), no `repeat:-1`, no `onUpdate`. `target` = selector or Element.
Pass composition seconds (`words.json` `comp_t`; composition local frame = beat frame + 6 handle frames).

**Frames.** Times snap to the 30 fps grid. A tween placed at frame k shows its START state on frame k and its END state
on frame k + d ("lands on k + d"); with ease out (`power3.out`) most of the move happens in the first frames.
"Ease out" = `power3.out` (plan p.4); fades/clears are linear (kit choice, plan names no ease); hard changes are
`data-start` boundaries (or `S.hard`, a 0.5-frame tween placed between two frames).

**Timed leaves, untimed wrappers (important).** HyperFrames lint `video_nested_in_timed_element` (error): a `<video>`
with `data-start` must not sit inside an element that also has `data-start`. So in every screen the **wrappers**
(`.rc-l3__cell`, `.rc-l4__plate`, `.rc-l5__prop`, `.rc-l6__frame`, `.rc-l7`, `.rc-l11__face`, `.rc-l12__card` ...) are
untimed, and every **leaf** that must disappear when the screen ends (the `<video>`/`<img>`, grounds, borders, overlays,
labels) carries `class="clip"`, `id`, `data-start`, `data-duration`. Give all leaves of one screen the same window.
Write `data-start`/`data-duration` with `RCK.type.attrF(frame)` / `RCK.type.durF(f0, f1)` (floor to 4 decimals, so a
clip never starts a frame late).

**Transforms.** The kit only transforms wrappers (GSAP), never a `<video>`: a media treatment draws the video into a
canvas that copies the video's own CSS transform, so transform wrappers only. No CSS `transform` is written for anything
GSAP moves; start states are `gsap.set` at build time inside the helpers.

**Footage looks = media treatments** (never CSS filters on footage). Where a screen needs blur, darkening or
desaturation, the beat persists a treatment with the CLI, inside the beat project, after the markup exists:
```bash
npx --yes hyperframes@0.9.52 media-treatment --selector "#b01-frost-blur" --grading '{"effects":{"blur":1}}' --apply --json
```
(the CLI writes the full canonical `data-color-grading` JSON and adds `data-hf-id` attributes; harmless). The exact
payload per item is given below. A treatment's `effects.blur` is a mix between the picture and ONE fixed-radius blur
(sigma 22.8 px per layout pixel at `blur: 1`, measured); the kit gets 40 px (L4) / 50 px (L6) by laying the blurred copy
out at 1/k size and scaling it up by k (k = 1.76 / 2.2; set automatically).

**Static inits run on load.** When `screens.js` loads (end of `<body>`), it sets up what needs no timeline: L4 blur scale +
tile overlays, L6 blur scale, L5 cut-out filters, L7 dims, L11 back face, L12 tilts. They are idempotent; the helpers call
them again. Nothing is hidden by these inits (cells / cards are hidden only when you call `gridPop` / `cardDrop`).

**Held shots.** Plan rule 7: every held shot gets a slow push-in 100% -> 104%: `S.push(tl, wrapper, at, {until})`.
**v02 (rule D): `S.push` defaults to 100 -> 108%, easeInOutSine; plus zoomOut / punchIn / keyPunch (v02 section).**

### API summary

| Helper | Item | Returns |
|---|---|---|
| `S.push(tl, els, at, {until \| durF, from=1, to=1.04, ease='none', origin='50% 50%'})` (v02: to = from x 1.08, sine.inOut; + `zoomOut`, `punchIn`, `keyPunch`) | any held shot | end |
| `S.gridBuild(tl, grid, at, {stepF=3, order, times, durF=4, punch, punchF=4})` | L3 | last landing |
| `S.gridPop(tl, cell, at, {durF=4, from=0.96, punch, punchF=4})` | L3 one cell / strip | landing |
| `S.gridGrow(tl, grow, at, {cell, durF=6, ease='power3.out'})` | L3 cell -> full frame | fills the frame |
| `S.gridRects(grid)` | L3 cell rects (layout px) | `[{x,y,w,h}]` |
| `S.frostClear(tl, frost, times[], {seed, order, durF=3})` | L4 one tile per time | last tile clear |
| `S.frostClearTile(tl, frost, tileIndex, at, {durF=3})` | L4 one given tile | clear time |
| `S.frostInit(frost, {seed, order})` | L4 (auto) | state `{order, k, ...}` |
| `S.collage(tl, root, at, {until, seed, amp=6, legS=2})` | L5 all props tilt + float | until |
| `S.propFloat(tl, prop, at, {until, amp=6, legS=2, seed \| phase})`, `S.propInit(prop, {rot, index})` | L5 one prop | until |
| `S.cutoutInit()` | L5 (auto) | - |
| `S.framedInit(root)` | L6 (auto) | `{k}` |
| `S.spotPush(tl, l7, at, {until \| durF, from=1, to=1.18, ease='none'})` | L7 push towards the target | end |
| `S.spotMove(tl, l7, at, {hole:"x,y,w,h", durF=12, ease})`, `S.spotInit(l7)` | L7 | end |
| `S.splitFlip(tl, split, at, {durF=10, ease='power2.inOut', blur=1})` | L11 B11 flip | landing |
| `S.splitDrain(tl, split, at, {durF=6, face='front', to=1})` | L11 B6 drain to B&W | end |
| `S.rateRamp({clipStart, at, from=1, to=0.5, durF=6, clipDur})` | L11 B6 slow to 50% (no DOM) | `data-automation` JSON |
| `S.cardsDrop(tl, root, at, {durF=8, stepF=8, times})`, `S.cardDrop(tl, card, at, {durF=8, fromY})` | L12 | last landing |
| `S.cardsDrift(tl, root, at, {until, px=[-8,-16,-24,-32], py})` | L12 parallax | until |
| `S.hard(tl, el, from, to, t)`, `S.frame(t)`, `S.snap(t)`, `S.geom` | utilities | - |

---

## 1. L3 Grid build (B1, B9)

**Plan (p.14):** 3 x 2 cells or 3 vertical strips, 8 px black gutters. Cells pop in one at a time (4f, scale 96% -> 100%
with a fade). A cell may stay black and hold text. A cell can scale up to full frame.
**B1 (p.20):** on "every GTA" an L3 3 x 2 grid, cells pop in left to right, top to bottom, 3f apart, each playing a police
chase (GTA 1 R1.5, GTA 3 R14.1, Vice City R1.7, San Andreas R1.6, GTA 4 R14.4, GTA 5 R1.3); on "even GTA 6" the sixth
cell switches to official GTA 6 footage (R17.1 or R17.3) and scales to full frame over 6f, ease out.
**B9 (p.24):** three vertical strips, GTA 1 ram (R9.2), GTA 2 chase (R9.3), London 1969 (R9.5); one strip pops in per
phrase with a 4f punch-in to 115% and its T4 phrase.

**Built:** a CSS grid, gutters = 8 px of ink black `#0A0A0A` (the timed `.rc-l3__ground` shows through) **between** cells;
cells touch the frame edges (**kit choice**, same geometry as the type kit's `rc-t4--strip1/2/3`).
3 x 2 cell = 634.67 x 536 px at x 0 / 642.67 / 1285.33, y 0 / 544. Strip = 634.67 x 1080. Footage is `object-fit: cover`
(never stretched; `--rc-pos` sets `object-position`). Pop = cell opacity 0 -> 1 (linear) + scale 0.96 -> 1.00
(`power3.out`), 4f. B9 punch = the cell's `.rc-l3__media` scales 1.00 -> 1.15 over the same 4f (`power3.out`) and stays
at 115% (**interp**: the strip still pops like every L3 cell; the beat's "4f punch-in to 115%" is the footage inside).
Grow = the `.rc-l3__grow` layer starts clipped (`clip-path: inset()`) to the cell's rect with its picture cover-fitted to
the cell, then the clip opens to the frame while the picture scales to 100%, same ease, so it stays cover-fitted.

**Markup (3 x 2, B1):**
```html
<div id="b01-grid" class="rc-l3 rc-l3--3x2" style="z-index: 2">          <!-- untimed -->
  <div id="b01-grid-ground" class="clip rc-l3__ground" data-start="S" data-duration="D"></div>
  <div class="rc-l3__cell" id="b01-c1"><div class="rc-l3__media">
    <video id="b01-c1-v" class="clip" src="assets/footage/R1.5.mp4" data-start="S" data-duration="D" muted playsinline></video>
  </div></div>
  ... cells 2-5 the same (R14.1, R1.7, R1.6, R14.4) ...
  <div class="rc-l3__cell" id="b01-c6"><div class="rc-l3__media">
    <video id="b01-c6-v" class="clip" src="assets/footage/R1.3.mp4" data-start="S" data-duration="SWITCH-S" muted playsinline></video>
  </div></div>
  <div id="b01-grow" class="rc-l3__grow" data-from-cell="6">            <!-- untimed; last child = on top -->
    <div class="rc-l3__grow-media">
      <video id="b01-gta6" class="clip" src="assets/footage/R17.1.mp4" data-start="SWITCH" data-duration="..." muted playsinline></video>
    </div>
  </div>
</div>
```
Strips (B9): `class="rc-l3 rc-l3--strips"` with three cells. A black cell holding text: a cell whose only child is a
timed text leaf, e.g. `<div class="rc-l3__cell"><div id="..." class="clip rc-l3__celltext" data-start data-duration>…</div></div>`
(white + soft shadow; style the text with the T-style the beat calls for).

**JS:**
```js
S.gridBuild(tl, '#b01-grid', tEvery, { stepF: 3 });            // -> last cell lands (tEvery + 5*3f + 4f)
S.gridGrow(tl, '#b01-grow', tEven, { durF: 6 });               // -> full frame at tEven + 6f (power3.out)
S.push(tl, '#b01-grow', tEven + 6/30, { until: tEnd });         // then the held full-frame shot pushes 100 -> 104%
// B9, one strip per phrase, with its T4 phrase (type kit) on the same frame:
[tRam, tChase, tLetGo].forEach((t, i) => { S.gridPop(tl, '#b09-s' + (i + 1), t, { punch: 1.15 });
  RCK.type.spreadIn(tl, document.querySelectorAll('#b09-t4 .rc-t4__piece')[i], t); });
```

**Timing (measured, `_demo-screens`):** pop at frame k: k = opacity 0 / scale 0.96, k+1 = 0.25 / 0.987, k+2 = 0.50 /
0.998, k+3 = 0.75, k+4 = 1.00 / 1.00. Six cells 3f apart from k: last starts k+15, lands k+19. Punch: k+2 = 114.1%,
k+4 = 115%. Grow from k (switch frame = cell rect, R17.1 already in the cell): k+1 52%, k+2 80%, k+3 94%, k+6 = full.

**Beats:** B1 (`b01-hook`): `gridBuild` on "every" (beat f21), cells f21-36, last lands f40; cell 6's R1.3 clip ends and
the grow layer's R17.1 clip starts on "even" (f52); `gridGrow` at f52 -> full frame f58 (S01 lands here); then
`push` on `#b01-grow` to the end; end the other cells' clips at f58 to save decoding. The grid needs no ground before
its first frame: the hard cut on "every" is the clip start (frame f21 shows the black grid, cell 1 is 25% on f22; start
`gridBuild` 1f earlier if cell 1 must show on the cut frame). B9 (`b09-throughyou`): strips on "They"(ram) f127,
"They"(chase) f151, "They"(don't) f178 with `rc-t4--strip1/2/3` phrases. B10 keeps the landed strips under its lead-in:
same markup, no pops, `gsap.set('#b10-strips .rc-l3__media', { scale: 1.15 })`.

**Limits:** cell rects come from the grid's CSS tracks, so the grid must be laid out (in the DOM, not `display:none`)
when `gridGrow` is called. `gridPop` hides a cell (opacity 0) from build time until its pop. The grow layer must be the
last child of the grid (on top).

---

## 2. L4 Frosted tile grid (B1 f0)

**Plan (p.14):** 4 x 3 tiles over footage. Each tile: 40 px blur, 10% white overlay, 1 px white border at 20%. Tiles
clear one at a time in random order (3f each), synced to words. **B1 (p.20):** f0: the first frame is already moving and
already shows "Why does"; the grid sits over a police moment from an official GTA 6 trailer (R1.2 or R17.1); tiles clear
one per word, 3f each, in random order.

**Built:** tiles 480 x 360 (row-major index 0-11). The blur is ON FOOTAGE, so it is a media treatment on a second copy
of the same `<video>` (`effects.blur: 1`) laid out at 1/k (1091 x 614) and scaled k = 1.76 -> Gaussian sigma 40 px
(measured 40.2 px, edge fit; **interp**: "40 px blur" = CSS-style blur radius = sigma 40). The copy shows only inside
uncleared tiles: `.rc-l4__frost` has a 12-layer CSS mask whose alphas are `--rc-l4-a0..a11` (1 = frosted). The overlays
are DOM: `rgba(255,255,255,.10)` + `1px solid rgba(255,255,255,.20)` per tile (adjacent tiles' borders sit side by side:
2 px line between tiles, 1 px at the frame edge). A clear = that tile's mask alpha and overlay go 1 -> 0 together over 3f,
linear. Order = seeded shuffle (`data-seed` on `.rc-l4`, or `opts.seed`/`opts.order`).

**Markup:**
```html
<div id="b01-frost" class="rc-l4" data-seed="1" style="z-index: 1">       <!-- untimed -->
  <div class="rc-l4__plate">                                               <!-- sharp picture -->
    <video id="b01-frost-sharp" class="clip" src="assets/footage/R1.2.mp4" data-start="S" data-duration="D" data-media-start="M" muted playsinline></video>
  </div>
  <div class="rc-l4__frost"><div class="rc-l4__plate"><div class="rc-l4__blurscale">   <!-- frosted copy -->
    <video id="b01-frost-blur" class="clip" src="assets/footage/R1.2.mp4" data-start="S" data-duration="D" data-media-start="M" muted playsinline></video>
  </div></div></div>
  <div id="b01-frost-tiles" class="clip rc-l4__tiles" data-start="S" data-duration="D"></div>  <!-- 12 tiles generated -->
</div>
```
Both videos: same `src`, `data-start`, `data-duration`, `data-media-start` (frame-locked). Then:
```bash
npx --yes hyperframes@0.9.52 media-treatment --selector "#b01-frost-blur" --grading '{"effects":{"blur":1}}' --apply --json
```
**JS:**
```js
S.frostClear(tl, '#b01-frost', [tWhy, tDoes], { seed: 1 });          // one tile per word -> last tile clear (+3f)
S.push(tl, '#b01-frost .rc-l4__plate', start, { until: tCut });      // both plates together, 100 -> 104%
```
**Timing (measured):** clear at frame k: k = frosted (alpha 1), k+1 = 0.667, k+2 = 0.333, k+3 = clear. Seed 1 order:
4, 10, 2, 6, 9, 3, 1, 11, 8, 5, 0, 7. Later `frostClear` calls continue the same order.
**Beats:** B1 (`b01-hook`) f0-21: clears on "Why" (f1) and "does" (f9) (STORYBOARD: the L3 cut comes on "every", so 2 of
12 tiles clear), T1 "Why does" from f0 (type kit), push 100 -> 104%; the head handle (local f0-5) shows the fully
frosted grid already moving.
**Limits:** lint warns `duplicate_media_discovery_risk` (two videos with the same source/start/duration): expected; both
copies were verified in snapshots and in an MP4 render. Two decodes of the same clip. `--rc-l4-k` (CSS) changes the blur
radius (sigma = 22.8 x k).

---

## 3. L5 Gray card collage (B6, B7; B8 holds B7's card)

**Plan (p.14):** #E9E9E9 background. A cut-out photo or clip in a frame with 8 px white border and a soft drop shadow
(0, 12, 30 px blur, black 25%). Props rotated +/-4 deg float +/-6 px over 2 s. **B6 (p.22):** X2 into an L5 gray card: a
moving clip of Gary Penn (R6.1) masked out from the background on the left, the quote typing on at the right.
**B7 (p.23):** the early-1990s office clip (R7.1) in a white-bordered frame; CANCELLED stamps slam onto the frame.

**Built:** `.rc-l5__ground` = `#E9E9E9` full frame (timed). Two prop kinds (**interp** of "a cut-out photo or clip in a
frame with 8 px white border"): (a) **framed clip**: `.rc-l5__frame` = white box 8 px larger on every side behind the
clip, `box-shadow: 0 12px 30px 0 rgba(0,0,0,.25)`; (b) **cut-out** (background-removed alpha clip): `.rc-l5__cutout`
wrapper with an SVG matte filter = 8 px white outline around the silhouette (round: alpha blurred sigma 4, thresholded
at 2.5%) + the same shadow (offset 12, CSS blur 30 = sigma 15, black 25%). The filter reads only the clip's alpha:
footage pixels are untouched (it is not a treatment). Props: static tilt (`data-rot`, default -4 / +4 alternating), float
y = -6 cos(phase + pi (t - t0) / 2 s): one leg -6 -> +6 px takes 2 s (**interp**: "over 2 s" = one leg, period 4 s),
sine path, seeded phase per prop.

**Markup:**
```html
<div id="b07-ground" class="clip rc-l5__ground" data-start="S" data-duration="D" style="z-index: 1"></div>
<div id="b07-card" class="rc-scr" style="z-index: 2">                              <!-- untimed card wrapper -->
  <div id="b07-p1" class="rc-l5__prop" data-rot="-4" style="--x: 432px; --y: 243px; --w: 1056px; --h: 594px;">
    <div id="b07-p1-frame" class="clip rc-l5__frame" data-start="S" data-duration="D"></div>
    <video id="b07-p1-v" class="clip rc-l5__media" src="assets/footage/R7.1.mp4" data-start="S" data-duration="D" muted playsinline></video>
    <!-- B7: put the CANCELLED stamps (motifs kit) here if they should float with the frame -->
  </div>
</div>
<!-- B6 cut-out prop (alpha clip made with: npx --yes hyperframes@0.9.52 remove-background assets/footage/R6.1.mp4 -o assets/footage/R6.1_cutout.webm) -->
<div id="b06-p1" class="rc-l5__prop" style="--x: 96px; --y: 200px; --w: 860px; --h: 880px; --rc-pos: 50% 100%;">
  <div class="rc-l5__cutout">                          <!-- add rc-l5__cutout--no-outline for shadow only -->
    <video id="b06-penn" class="clip" src="assets/footage/R6.1_cutout.webm" data-start="S" data-duration="D" muted playsinline></video>
  </div>
</div>
```
`--x/--y` = top-left of the picture, `--w/--h` = picture size (frame adds 8 px outside). Cut-out: `object-fit: contain`,
`--rc-pos` default `50% 100%` (feet/shoulders on the box bottom).
**JS:** `S.collage(tl, '#b07-card', start, { until: end, seed: 7 });` (every `.rc-l5__prop` inside: tilt + float) or
`S.propFloat(tl, '#b06-p1', start, { until: end })`. X2 into the card (B6): `RCK.transitions.drift` on the card wrapper
(transitions kit).
**Timing (measured):** rotation exactly -4 / +4 deg; y range over 3 s = [-6.00, +6.00] px; e.g. prop 1 +5.35 px at the
start, -5.35 px 2 s later.
**Beats:** B6 (`b06-dull`) from "One" (f61): cut-out of R6.1 on the left (x <= 960), T8 quote card `rc-t8--right` (type
kit, starts at x 1008) at the right; float to the end (the B6 quote hold). B7 (`b07-shutdown`) f0-96: framed R7.1, stamps
(motifs kit) on "keep" f37, "shut" f59, "down" f70. B8 (`b08-break`) f0-35: same card, final state, keep floating.
**Limits:** the stand-in cut-out in the demo is a synthetic silhouette (no real R6.1 yet). The cut-out filter costs two
small blurs per frame. With `remove-background` WebM (VP9 alpha) the edge quality is the tool's.

---

## 4. L6 Framed clip (B13)

**Plan (p.14):** clip at 62% scale with a 2 px white border and a 30 px warm outer glow (#FFF6E0 at 40%), over a 50 px
blurred, 40% darker copy of the same clip. Small label under it in Instrument Serif Italic 32 px. **T6 (p.12):** giant
type sits behind the framed clip so the frame overlaps the middle letters. **B13 (p.25):** the GTA 1 intro (R13.1) framed
over its own blurred copy; T6 GRAND / THEFT / AUTO types on behind the frame.

**Built:** frame box 62% of 1920 x 1080 = 1190.4 x 669.6 centred (x 364.8, y 205.2; measured 364.8, 205.2,
1190.4 x 669.6). `.rc-l6--4x3`: 892.8 x 669.6 (62% of a 4:3 picture 1440 x 1080; plan: keep 4:3 material in a band or
frame, never stretch). Border 2 px white outside the picture; glow `box-shadow: 0 0 30px 0 rgba(255,246,224,.40)`
(**interp**: glow size = shadow blur 30 px). Back copy = the same clip full frame, media treatment
`{"effects":{"blur":1},"adjust":{"exposure":-0.737}}` at layout 1/k, scaled k = 2.2: sigma 50 px (measured 49.9) and
2^-0.737 = 0.60 (measured 255 -> 153 = 40% darker). Label: Instrument Serif Italic 32 px / 40 px line, white + soft
shadow (text on footage), centred, 22 px under the border (**kit choice**).
**Layer order (DOM order inside `.rc-l6`): `.rc-l6__bg` (back) < the T6 element < `.rc-l6__frame`.**

**Markup:**
```html
<div id="b13-l6" class="rc-l6" style="z-index: 2">                          <!-- untimed; add rc-l6--4x3 for 4:3 -->
  <div class="rc-l6__bg"><div class="rc-l6__blurscale">
    <video id="b13-l6-bg" class="clip" src="assets/footage/R13.1.mp4" data-start="S" data-duration="D" data-media-start="M" muted playsinline></video>
  </div></div>
  <div id="b13-t6" class="clip rc-t6" data-start="S" data-duration="D">       <!-- type kit T6, BETWEEN back and frame -->
    <div class="rc-t6__line">GRAND</div><div class="rc-t6__line">THEFT</div><div class="rc-t6__line">AUTO</div>
  </div>
  <div class="rc-l6__frame" data-layout-allow-occlusion>                       <!-- untimed -->
    <div id="b13-l6-border" class="clip rc-l6__border" data-start="S" data-duration="D"></div>
    <video id="b13-l6-clip" class="clip rc-l6__media" src="assets/footage/R13.1.mp4" data-start="S" data-duration="D" data-media-start="M" muted playsinline></video>
    <!-- optional: <div id="…" class="clip rc-l6__label" data-start data-duration>label</div> -->
  </div>
</div>
```
```bash
npx --yes hyperframes@0.9.52 media-treatment --selector "#b13-l6-bg" --grading '{"effects":{"blur":1},"adjust":{"exposure":-0.737}}' --apply --json
```
**JS:** nothing required (`framedInit` runs on load). Held shot: `S.push(tl, '#b13-l6', start, { until: end });` (pushes
back copy, T6 and frame together); T6: `RCK.type.giantType(tl, '#b13-t6', tGrand)`.
**Beats:** B13 (`b13-gta`) f85-190: X3 flash into L6 at f85 (transitions kit), T6 from "Grand" (f132, 14 letters, 2f
apart), hold 1 s; the plan gives B13 no label text, so leave the label out (never add facts).
**Limits:** a label under the frame collides with T6's last line; use one or the other. Lint warns
`duplicate_media_discovery_risk` when back copy and framed clip share src/start/duration (expected).

---

## 5. L7 Spotlight (B4, B15)

**Plan (p.14):** a document or screen recording, dimmed to 35% except a rounded spotlight box (20 px feather) on the
target. Push in 100% -> 118% towards the target across the beat. **B4 (p.21):** the 1995 design-document title page
(R4.5; a still is allowed here, under 1.5 s, always with a push-in), dimmed except the title, push 100% -> 118%, T9
highlight swipes across "Race'n'Chase". **B15 (p.26):** arcade interior (R15.3/R15.4) dimmed to 35% except a spotlight box
on the Race and Chase cabinet; slow push-in; the T9 label pops next to the cabinet.

**Built:** no filter on the footage: a solid `#0A0A0A` overlay at 65% (35% of the picture shows through; measured
src 37 -> 20 = 0.35 x 37 + 0.65 x 10) with a rounded hole, as an inline SVG mask built from data attributes:
`data-hole="x,y,w,h"` (frame px), `data-radius` (16, **kit choice**), `data-feather` (20 = Gaussian sigma 5: the edge
ramps 2.5% -> 97.5% over ~20 px centred on the box edge; measured 21 px). Push = the whole `.rc-l7` (picture + dim +
anything you put inside, e.g. the T9 highlight / label) scales 1 -> 1.18 about the hole's centre, linear across the shot
(**kit choice**: linear; the target stays where it is and grows).

**Markup:**
```html
<div id="b04-l7" class="rc-l7" style="z-index: 2">                                          <!-- untimed -->
  <img id="b04-doc" class="clip rc-l7__media" src="assets/footage/R4.5.png" data-start="S" data-duration="D" alt="" />  <!-- or <video … muted playsinline> -->
  <!-- B4: the T9 highlight (type kit) goes HERE, between the picture and the dim, so it pushes with the page -->
  <div id="b04-dim" class="clip rc-l7__dim" data-hole="640,270,640,200" data-radius="16" data-feather="20" data-start="S" data-duration="D"></div>
  <!-- B15: the T9 label goes here (above the dim, inside .rc-l7) so it stays next to the cabinet -->
</div>
```
**JS:** `S.spotPush(tl, '#b04-l7', start, { until: end });` -> end. Optional `S.spotMove(tl, '#b15-l7', t, { hole:
'x,y,w,h', durF: 12 })` if the target moves in the footage (tween the hole; the push origin stays).
**Timing (measured):** scale 1.000 at the start, 1.09 halfway, 1.18 at the end; origin = hole centre (e.g. 960px 370px).
**Beats:** B4 (`b04-racenchase`) f0-44 (44f = 1.47 s, still < 1.5 s, CONFLICTS C16): hole on the title, push across
f0-44, T9 swipe on "Race" (f18). B15 (`b15-proof`) f8-160 after the X5 open: hole on the cabinet, push to f160, T9 label
"RACE AND CHASE" on "Race" (f148), then X6 zoom (transitions kit) through the cabinet.
**Limits:** the hole is static unless you `spotMove` it (no tracking). Use `data-dim` only to deviate from 0.65 (don't).

---

## 6. L11 Split screen (B5, B6, B11) incl. the B11 flip

**Plan (p.15):** two 958 px halves with a 4 px black divider. In B11 the whole split screen flips 180 deg on the Y axis
over 10f with motion blur. **B5 (p.22):** left a police car in pursuit seen from the cop side (R5.4 or R5.2), right the
car being chased (R5.1). **B6:** on "dull" the B5 split screen drains to black and white over 6f and slows to 50%.
**B11 (p.24-25):** the B5 split screen returns in full colour; on "flips" it rotates 180 deg on Y over 10f with motion
blur; the back shows left the player's getaway car fleeing (R10.2 or R9.1), right police cars chasing (R5.4). B5 and B11
must use the same frame size and position.

**Built:** halves x 0-958 and 962-1920, full height; the 4 px divider (x 958-962, measured) is the timed ink-black
`.rc-l11__ground` showing between them. Same CSS in every beat = identical framing in B5, B6, B11. Footage `cover`;
`--rc-pos` per `<video>` reframes. Flip: `.rc-l11` has `perspective: 2666.67px` (After Effects' default 50 mm camera
for a 1920 px comp, **kit choice**); front face 0 -> 180 deg, back face -180 -> 0 deg (`backface-visibility: hidden`),
10f, `power2.inOut` (**kit choice**, as the registry's 3D card flip: fastest at 90 deg = frame k+5, where S10 peaks).
Motion blur (seek-safe approximation, **interp**): each face video carries a media treatment `{"effects":{"blur":1}}`
with inline `--hf-color-grading-blur: 0`; the flip ramps it 0 -> 1 (power2.in) to the midpoint and back to 0
(power2.out) - an isotropic blur peaking with the angular speed. HyperFrames' own `data-motion-blur="on"` was tested on
this flip and draws no visible blur on a 3D turn ("turns are only softened"), so it is not used.
B6 drain: the face videos carry `{"adjust":{"saturation":-1}}` + inline `--hf-color-grading-intensity: 0`; `splitDrain`
tweens the intensity 0 -> 1 over 6f, linear (= colour -> black and white). B6 slow-down: a HyperFrames `rate` lane
(`data-automation`) on each half video, 1.0 -> 0.5 over the same 6f (**interp**: "slows to 50%" ramped with the drain;
`durF: 0` makes it a step). Seek-safe: verified against the clip's burned-in frame counter.

**Markup (B11; B5/B6 = the front face only):**
```html
<div id="b11-split" class="rc-l11" style="z-index: 2">                                    <!-- untimed -->
  <div id="b11-ground" class="clip rc-l11__ground" data-start="S" data-duration="D"></div>
  <div class="rc-l11__face rc-l11__face--front">
    <div class="rc-l11__half rc-l11__half--left"><video id="b11-fl" class="clip" src="assets/footage/R5.4.mp4" data-start="S" data-duration="D" muted playsinline style="--hf-color-grading-blur: 0"></video></div>
    <div class="rc-l11__half rc-l11__half--right"><video id="b11-fr" class="clip" src="assets/footage/R5.1.mp4" data-start="S" data-duration="D" muted playsinline style="--hf-color-grading-blur: 0"></video></div>
  </div>
  <div class="rc-l11__face rc-l11__face--back">
    <div class="rc-l11__half rc-l11__half--left"><video id="b11-bl" class="clip" src="assets/footage/R10.2.mp4" data-start="S" data-duration="D" muted playsinline style="--hf-color-grading-blur: 0"></video></div>
    <div class="rc-l11__half rc-l11__half--right"><video id="b11-br" class="clip" src="assets/footage/R5.4.mp4" data-start="S" data-duration="D" data-media-start="M" muted playsinline style="--hf-color-grading-blur: 0"></video></div>
  </div>
</div>
<!-- M2 arrow / X9 wash / captions: outside .rc-l11 (screen space; they do not flip) -->
```
```bash
for s in b11-fl b11-fr b11-bl b11-br; do npx --yes hyperframes@0.9.52 media-treatment --selector "#$s" --grading '{"effects":{"blur":1}}' --apply --json; done
# B6 instead: inline style="--hf-color-grading-intensity: 0" and
for s in b06-l b06-r; do npx --yes hyperframes@0.9.52 media-treatment --selector "#$s" --grading '{"adjust":{"saturation":-1}}' --apply --json; done
```
B6 rate lane on each half (`t` in clip seconds; generate it in Node and paste):
```bash
node -e "globalThis.window=globalThis; require('./assets/kit/screens.js'); console.log(RCK.screens.rateRamp({clipStart: S, at: tDull, durF: 6, clipDur: D}))"
# -> {"version":1,"lanes":[{"target":"rate","points":[{"t":0,"v":1},{"t":a,"v":1},{"t":a+0.2,"v":0.5},{"t":D,"v":0.5}]}]}
```
`<video … data-automation='{"version":1,"lanes":[…]}'>` (single quotes around the JSON).
**JS:** `S.splitFlip(tl, '#b11-split', tFlips);` -> landing (+10f). `S.splitDrain(tl, '#b06-split', tDull);` -> +6f.
**Timing (measured):** flip from k: k+1 0.7 deg, k+3 19.4 deg (blur 0.22), k+5 90 deg (edge-on: that frame is ink black,
blur 1), k+7 160.6 deg, k+10 = back face flat, blur 0. Drain from k: intensity k 0, k+1 0.167, k+3 0.5, k+6 1 (B&W).
Rate: media time = 1x until the ramp, 0.75x average across the 6f ramp, then 0.5x.
**Beats:** B5 (`b05-copgame`) f0-88 front face only (M2 arrow on "you" f14, X9 on "police officer" f28: other kits).
B6 (`b06-dull`) f0-61: the same split continuing (continuous source time = `data-media-start`), drain + slow on "dull"
(f43 -> f49), then X2 into L5 at f61. B11 (`b11-flip`) f0-162: front = B5's clips in full colour, flip on "flips" f18 ->
lands f28 (S10 peak meets f23), back face to the end; M2 redraw on "Now" f103 (motifs). Cover frame (plan p.39) = a B11
frame after the flip.
**Limits:** the blur is isotropic, not a directional smear. Four treated videos blur only during the 10f (zero blur
costs nothing). Keep identical `--rc-pos` per clip across B5/B6/B11.

---

## 7. L12 Stacked cards (B3)

**Plan (p.15):** 3-4 short video clips (not photos) as cards with 12 px white borders, rotated -6, +3 and -2 deg,
dropping in one at a time (8f each, ease out) with a slow parallax drift. **B3 (p.21):** three short clips drop in as
tilted cards from R3.8, R3.7 and R3.3; the T8 name card sits on top; a tiny Lemming (cropped from R3.5 or R3.6) walks
along the underline of "DMA Design".

**Built:** each card = 12 px white border box behind a `cover` clip, tilt by DOM order -6 / +3 / -2 deg (`data-rot`
overrides; a 4th card has no plan angle and repeats -6). Drop (**interp** of "dropping in"): from fully above the frame
straight down to its spot, 8f, `power3.out`; the next card starts when the previous lands (8f apart). Drift: card i moves
-8 x (i+1) px along x (top card most), linear, over the shot (**kit choice**). Default pile (**kit choice**): 640 x 480
(4:3) pictures, card 3 (top) in the middle so a centred T8 sits on footage: data-card 1 at (400, 210), 2 at (880, 250),
3 at (640, 360), 4 at (1000, 420). Override with `--x --y --w --h`. Background: `.rc-l12__ground` (#E9E9E9, optional;
B3 = history = gray card, STORYBOARD).

**Markup:**
```html
<div id="b03-l12-ground" class="clip rc-l12__ground" data-start="S" data-duration="D" style="z-index: 1"></div>
<div id="b03-cards" class="rc-l12" style="z-index: 2">                               <!-- untimed -->
  <div class="rc-l12__card" data-card="1"><div class="rc-l12__drop">               <!-- untimed (drift / drop) -->
    <div id="b03-cb1" class="clip rc-l12__border" data-start="S" data-duration="D"></div>
    <video id="b03-cv1" class="clip rc-l12__media" src="assets/footage/R3.8.mp4" data-start="S" data-duration="D" muted playsinline></video>
  </div></div>
  ... data-card="2" R3.7, data-card="3" R3.3 ...
</div>
<div id="b03-t8" class="clip rc-t8" data-start="S" data-duration="D" style="z-index: 5">…</div>   <!-- T8 on top (type kit) -->
```
**JS:**
```js
S.cardsDrop(tl, '#b03-cards', tDMA, { durF: 8 });        // -> last card lands (tDMA + 24f for three cards)
S.cardsDrift(tl, '#b03-cards', tDMA, { until: tEnd });   // parallax drift to the end of the shot
RCK.type.nameIn(tl, '#b03-t8', tDMA);  RCK.type.walk(tl, '#b03-t8', t, { duration: 2.0 });
```
**Timing (measured):** card off-screen from its clips' first frame until its drop frame k (y -795 px for card 1),
k+1 = -466 px, k+4 = -50 px, k+8 = landed; drift 0 -> -8 / -16 / -24 px.
**Beats:** B3 (`b03-dundee`) hard cut on "DMA" f103: drops f103 / f111 / f119, all landed f127, drift to f180; T8 name
f103, role on "the studio" f137 (type kit), Lemming walk (type kit `walk`). X2 into the band before is Tesseract's.
**Limits:** outside its clips' window a card rests at its spot (invisible, all leaves timed).

---

## 8. L10 year tag (B14, over the Tesseract montage burst)

**Plan (p.15, p.26):** tiny year tag, Inter Medium 22 px, top-left; B14 tags "2001" (R14.1), "2002" (R14.2), "2004"
(R14.3), "2008" (R14.4), "2013" (R14.5); "the year tags are the only text during the burst; keep them tiny".
**Built:** `.rc-l10-tag`: Inter 500, 22 px / 28 px, white, soft shadow, at (96, 54) = inside title-safe (measured).
**Markup:** one timed element per clip (or per year spanning that year's clips), hard cut with the clip:
```html
<div id="b14-tag-2001" class="clip rc-l10-tag" data-start="…" data-duration="…" style="z-index: 6">2001</div>
```
**Beats:** B14 (`b14-since`) f0-60, 10 clips x 6f (STORYBOARD/C15): "2001" f0-12, "2002" f12-24, "2004" f24-36,
"2008" f36-48, "2013" f48-60 (use the Tesseract cut frames from the beat's `tesseract_shots.json`).

## 9. L2 band geometry (bars drawn in Tesseract)

**Plan (p.13):** black bars 138 px top and bottom (2.39:1); bars slide in over 8f when entering a cinematic moment.
The picture band is **y 138 .. 942** (1920 x 804). HF overlays that must sit in the band use `.rc-l2-band` (untimed box
at x 0, y 138, 1920 x 804; children position relative to the band: `--rc-y` of a T element inside it counts from y 138)
or `.rc-l2-safe` (the band minus the 96 px side margins). `S.geom.L2 = {bar:138, bandTop:138, bandBottom:942,
bandHeight:804, slideF:8}`. Keep text out of y < 138 and y > 942 for the whole shot (during the 8f slide the bars are
moving in from the frame edges). Beats: B3 (Dundee f58-103 with T4; team f180-215 with T1), B13 (unboxing f190-214),
B17 (Trailer 1 f0-103 with T1 + M1 stars).

---

## 10. Verification (`_demo-screens`, all in `review/`)

`npx --yes hyperframes@0.9.52 check --json`: 0 errors (warnings: `duplicate_media_discovery_risk` = the L4 pair, by
design; type-kit `nested_structure_needs_subcomposition`; craft warnings for the silent demo and its short demo lines).
Measured on the snapshots / in the DOM (headless Chrome, timeline seeked):
* L3 gutters 8 px ink black at x 635-642 / 1277-1284, y 536-543 (`B_L3-3x2_f098_…`); pop opacity/scale per frame as in
  section 1 (`B_…f079/f080/f090`); grow 52% / 80% / full (`B_L3-grow_f127/f128/f132`); punch 114% -> 115%
  (`C_…f170/f172`); black text cell (`D_…`).
* L4 blur sigma 40.2 px (`Z_calib_f937_…`), overlay 10% (frosted 54.1 vs 0.9 x 31.3 + 25.5 = 53.7), border 20%
  (94 = 0.8 x 55 + 51), clear 1 -> .667 -> .333 -> 0 (`A_…f000/f004/f007/f050`).
* L5 border 8 px, shadow `0 12px 30px rgba(0,0,0,.25)`, ground rgb(233,233,233), tilt -4/+4, float [-6, +6] px
  (`E_…f300/f345`, `zoom/L5_*`).
* L6 frame 364.8, 205.2, 1190.4 x 669.6, border 2 px white, warm glow (`zoom/L6_frame_corner_glow`), back copy sigma
  49.9 px and 60% brightness (`Z_calib_f952_…`), T6 between (`F_…f430`).
* L7 dim = 0.35 x picture + 0.65 x #0A0A0A, hole untouched, feather 21 px (2.5-97.5%), push 1 -> 1.18 about the hole
  centre (`G_…`, `H_…`, `zoom/L7_feather_corner`).
* L11 halves 0/958 and 962/958, divider 958-961 (`I_…`, `zoom/L11_divider`); drain 0 -> .5 -> 1 over 6f and half speed
  via the frame counter (`J_…f659/f663/f666/f700`: f14 -> f17 -> f19 -> f36); flip angles + blur (`K_…`).
* L12 drop -795 -> -466 -> -50 -> 0 px, landed f791 / f807, drift -8/-16/-24 px, T8 on top (`L_…`).
* L10 tag at (96, 54), Inter 500 22 px white + shadow (`M_…f871/f897`); L2 band box 0,138,1920,804 (`M_L2-band_f915`).
* Short MP4 renders (`--workers 1`) of the L4, L5, L7 and flip ranges match the snapshots (media treatments, masks and
  the cut-out filter work in the render path too).

## 11. Conflicts, interpretations and kit choices

* **L3 B9 (beat build) vs L3 library:** the beat says "one strip pops in per phrase with a 4f punch-in to 115%", the
  library "cells pop in (4f, 96% -> 100% with a fade)". Not contradictory as built: the strip pops as an L3 cell and its
  footage punches 100 -> 115% over the same 4f (beat value wins for the punch).
* **L4 "40 px blur", L6 "50 px blurred":** read as Gaussian sigma (CSS `blur()` convention, as the type kit's blurs).
  Media treatments cap at sigma 22.8 px per layout pixel, so the copies are laid out small and scaled up (k 1.76 / 2.2).
* **L5 "a cut-out photo or clip in a frame with 8 px white border":** read as two prop kinds: a clip in a white frame
  (B7) and a cut-out with an 8 px white outline (B6); both with the plan's shadow.
* **L5 "float +/-6 px over 2 s":** one leg (-6 -> +6) per 2 s (the plan's "over N" = duration of the move).
* **L7 "dimmed to 35%":** done with the palette's ink black (#0A0A0A) at 65%, so pure black lifts to 2.5% (10/255 x 0.65);
  pure #000 is not in the palette.
* **L11 "with motion blur":** isotropic treatment-blur ramp (no seek-safe directional blur on a 3D turn exists here);
  HF native motion blur tested, no visible effect on the flip.
* **B6 "slows to 50%":** ramped over the drain's 6f (could be a step: `durF: 0`).
* **L12 "dropping in":** from above the frame; no shadow (the plan gives none); parallax magnitudes and default pile are
  kit choices; a 4th card's angle is not in the plan.
* **Kit choices:** L3 no outer gutter; L7 radius 16 px, feather = sigma 5, linear push; L6 label gap 22 px, glow = 30 px
  shadow blur; L11 perspective 2666.67 px, flip ease power2.inOut; L5 default tilt order -4 / +4; fades linear.
* **base.css (not this area):** `--sans` lists "Neue Haas Grotesk" (plan fallback) with no `@font-face`; HyperFrames lint
  reports `font_family_without_font_face` as an ERROR in every project linking base.css. `_demo-screens` links a demo-only
  `assets/demo-lint-fix.css` that re-declares `--sans` without it (no visual change: Inter always loads). Fix belongs in
  base.css (drop the name or give it an `@font-face`).

## 12. SUGGESTIONS (not built)

* L12: a soft shadow under the cards (e.g. the L5 values) would separate white borders from the #E9E9E9 ground; the plan
  gives L12 no shadow, so the kit has none.
* L11 flip: a light darkening of each face as it turns edge-on would sell the 3D turn; not in the plan.
* L7 B15: if the real arcade capture moves, key the hole with `spotMove` to follow the cabinet.
* B10: keep B9's strips identical (same `--rc-pos`, landed 115%) so the handoff into the X3 flash is seamless.
