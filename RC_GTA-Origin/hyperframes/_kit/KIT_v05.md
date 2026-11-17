# KIT_v05: global style system + motion-graphics kit (REVISION_v05 G, with the CLIENT OVERRIDE U)

Read this first for v05. The client's override ("do not follow the instructions in the doc that reverses my earlier
notes", REVISION_v05 U) is applied throughout: **all text is Coolvetica** (U1), **caption words simply appear on their
frame, white; only chosen words pop + blur in** (U2), no zoom/punch helpers beyond the slow push and the zoom-through
(U3), no off-white paper (U4), no stamp (U5), no 3D flip (U6). Everything else in the doc applies. Sizes are @1080 (doc
@720 px x 1.5). Every helper is deterministic (seeded, no timers), eased (cuts are 0.5-frame step tweens between two
frames: frame k shows the new state, k-1 the old one) and identical every time it is called with the same arguments.
`k` = the frame of `at`; `L(n)` = n / 30.

Proof: `hyperframes/_demo-v05/` (built by `tools/gen_demo.cjs` from this kit, the way a beat uses it): `review/snap/`
(`f<frame>_<what>.png`), `review/sheet_A..K.jpg`, `review/lockups.txt` (plans + cues), `review/check.json` (0 errors).
Rebuild: `cd hyperframes/_demo-v05 && rm -r assets/kit && cp -r ../_kit assets/kit && node tools/gen_demo.cjs && bash tools/snap.sh`.

Nothing to add to a beat's `<head>`: the CSS is in base.css / type.css / motifs.css, `RCK.fx` is in motifs.js (all
beats already load the four kit CSS + JS files). Re-sync: `python3 tools/sync_kit.py`.

## 1. Fonts, palette, textures (base.css)

* Fonts (U1): Coolvetica Regular (`--sans`) and Coolvetica Italic (`--serif`) only. The v05 role variables all point at
  them: `--font-setup` = `--font-pill` = `--font-vcr` = `--font-dull` = Coolvetica Regular, `--font-display` = Coolvetica
  Italic. The Inter / Playfair / Montserrat / VT323 / Arimo files are in `fonts/` but are not loaded. The Win95-style
  window keeps its v04 UI look (system sans-serif).
* Palette: `--accent` #FF2E7E (pills, highlighter sweeps, pixel glitch, the location pin, a static pink word),
  `--annot` #FFD23F (hand-drawn arrows / circles / underlines only), `--danger` #E3262B (red grid cells, the "cop"
  strike), `--dull-grey` #8A8A8A, `--text-drop` = 0 6px 18px rgba(0,0,0,.45) (all caption text), `--card-bg` #0E0E10.
* `--grain` = `tex/grain.png` (a static, seeded 256 px monochrome grain at 8% alpha). Note for anyone adding textures: an
  SVG-filter `data:` URI (feTurbulence) paints OPAQUE BLACK in the HyperFrames renderer (it rendered fine in plain
  Chrome); use a PNG.
* `.rc-card` (all beats' dark cards) = #0E0E10 + grain + the v04 scanlines. The faint footage loop behind a card:
  `RCK.fx.darkCardHTML` (section 3).

## 2. Captions v05: in place (`T.lockupPlan`, `T.lockups`, `T.lockupsWire`: the same calls as v03)

**What a kit re-sync changes in an existing beat (no spec rewrite needed):**
* Setup words (lead / tail / solo rows) are Coolvetica Regular **54 px** (v03: 60; `setupSize`), key words Coolvetica
  Italic 190 (unchanged). Old lockup HTML (no `data-rc-v="5"`) is re-laid out at wire time with these sizes (same rows,
  words and frames; the box re-centred on `--rc-y`); re-running `T.lockups(...)` writes them into the HTML.
* Plain words still just appear on their frame (hard cut, white, as v03). **Starred words now use the doc's pop**
  (below) instead of v03's 6f blur 20 px / 92% pop. Text shadow = `--text-drop` (v03: the white glow).
* No colour flash, no drift, no siren entry, no type-on (U2).

**Tiers:** A setup = Coolvetica Regular 54 (51-57; `setupSize`; a solo line on a card `card: true` = 57) / B key `[ ]`
= Coolvetica Italic 190 (165-210; `keySize`) / C hero `[[ ]]` = Coolvetica Italic 450 (330-600; `hero` / `heroSize`;
numbers and dates too: "1995", "18", "30", "NOV 1997"; may run off frame, never shrunk) / quote (`tier: 'quote'`) =
Coolvetica Italic 105, its key 135 / the "dull." gag (`#`) = Coolvetica Regular #8A8A8A 180, no shadow, no animation.

**Layout (G3, = the client's ref 1):** setup line directly above the key word, left-aligned to it; words after the key
below it, right-aligned to its right edge; the block's ink centred on `--rc-y` (540; `y` option); descender guard: a
row's highest glyph clears the previous row's deepest glyph by 8 px ("[[Why]] does": "does" sits below the y).

**How a lane marks words** (in the spec string; a spec may also be an object `{ s, ...options for that lockup }`):

| Marker | Meaning |
|---|---|
| (nothing) | the word appears on its frame, white (hard cut) |
| `word*` | **pop + blur in** (white, the doc timing): the chosen key / hero words, the B6 quote words |
| `[word]` / `[two words]` | tier B key (one group per lockup) |
| `[[word]]` | tier C hero instead of a key group; size `{ s: '[[Why]]* does', hero: 450 }` |
| `]*` / `]]*` | every word of the group pops |
| `word^` | static pink #FF2E7E ("caught.") |
| `word#` / `]#` | the "dull." gag: Coolvetica Regular grey 180, no animation |
| `\|` | forced line break among setup words |
| `!`, `~` | kept for old specs: `!` = appear (the default), `~` is ignored (no siren entry, U2; the plan warns) |

```js
// Node (paste the HTML), one timed element per lockup:
const p = T.lockupPlan(w, [{ s: '[[Why]]* does', hero: 450 }, 'every [GTA,]'], { from: 0 });
T.lockups(p, null, { idPrefix: 'b01-lk', z: 40, track: 20 });   // + T.lockupReport(p), T.lockupCues(p)
T.lockups(w, ['Because back in [[1995,]]'], { from: 0, hero: 480 })              // hero appears; glow flicker below
T.lockups(w, [{ s: '[[broke.]]', hero: 390, y: 820 }, 'And that [bug] saved it.'], { from: 9 })
T.lockups(w, ["it's [dull.]#"], { from: 4 })                                      // Coolvetica Regular grey 180
T.lockups(w, [{ s: 'from the [cops?]*', keySize: 240 }], { from: 10 })            // the key pops
T.lockups(w, [{ s: '[“awful…]* too* sim-y.”*', tier: 'quote' }], { from: 11, loose: true })   // B6: word by word
T.lockups(w, ['already [caught.]^'], { from: 8 })                                 // static pink
T.lockups(w, ['Until finally,'], { from: 0, card: true, exit: 'blur' })           // 57 px solo, 3f blur-out exit
// beat script, once after the markup:
T.lockupsWire(tl);
T.glowFlicker(tl, '#b02-lk-1 .rc-lk__row--hero .rc-lw', W[3].comp_t);   // client's glow flicker, on top of appear / pop
FX.rgbSplit(tl, '#b02-lk-3 .rc-lk__row--key .rc-lw', W.bug, { px: 6, settle: 2 });   // never settles
FX.jitter(tl, '#b02-lk-2 .rc-lw', W.broke, { px: 4.5 });                          // +/-4.5 px every frame
```
`T.lockupCues(plan, offsetF)` -> `{ word_pops, key_words }` = appear frames for cues.json v05 (key / hero / starred words
-> key_words: whoosh + thump; other words -> word_pops: tick; "dull." neither).

**Timings** (k = round(comp_t x 30), the word's words.json frame; ease = cubic-bezier(0.2, 0.8, 0.2, 1) =
`RCK.ease.trailer`: 0.25 -> 0.767, 0.5 -> 0.946, 0.75 -> 0.991):

| frame | plain word | `*` pop word |
|---|---|---|
| k-1 | hidden | hidden |
| k | visible, white, 100% | opacity 0, scale 112%, blur 9 px |
| k+1 | | opacity 0.95, 102.8%, blur 2.1 px |
| k+2 | | opacity 1, 100.6%, blur 0.5 px |
| k+3 | | 100.1%, blur 0.1 px |
| k+4 | | 100%, blur 0 (the filter is removed from k+5) |

A lockup's clip runs from its first word's frame to the next lockup's first word's frame (hard cuts). `exit: 'blur'`
(per lockup or global; `data-rc-exit="blur"`): the last 3 frames blur 0 -> 12 px + opacity 1 -> 0 (power2.in).
`T.lockupsWire(tl, scope, { pop: false })` makes starred words appear too. `T.glowFlicker` and `RCK.fx.rgbSplit` /
`fx.jitter` on a lockup word layer on top of the appear / pop (they drive the inner `.rc-lw__fx` span or other properties).

**Glow flicker** (unchanged API, `T.glowFlicker(tl, target, at, { frames: 10, pattern, seed, settleF: 4 })`): one hard step
per frame between flare / on / half (55% opacity) / off (15% opacity) with a white glow, then a 4f eased settle to a
steady soft glow; works on a lockup word, a T3 year line (`.rc-t3__year`) and the calendar's `.fx-cal__text--to`.

## 3. RCK.fx (motifs.js / motifs.css): the motion-graphics kit (G5)

Host pattern: `<div id="b02-err" class="clip fx-host" data-start="..." data-duration="..." style="--x: 960px; --y: 540px; z-index: 20"></div>`;
the helper builds the graphic inside the host and animates only its children.

| API | One-line example | Frame timings |
|---|---|---|
| `fx.pill(tl, host, at, { wipeF: 6, size: 72 })`; host `class="clip fx-host fx-pill"` with the text as its content | `FX.pill(tl, '#b02-pill', L(279))` | k..k+6 the box wipes 0 -> 100% from the left (power2.out); the text appears whole on k+6 (no type-on, U2). Coolvetica Regular uppercase, +2%, 72 px; #FF2E7E 92%, 15 px radius, 4.5 px white inner stroke inset 9 px, 36 px glow 40% |
| name pill: host `class="clip fx-host fx-pill fx-pill--name" data-line2="DMA Design · Gamasutra, 2011"`, text "GARY PENN" | `FX.pill(tl, '#b06-name', L(3))` | as above; lower-left (`--x` 96, `--b` 140); 45 px + 30 px, both lines appear on k+6 |
| `fx.pillOut(tl, host, at, opts)` | `FX.pillOut(tl, '#b02-pill', L(299))` | = `fx.glitch` mode 'out' (7f) on the pill box |
| `fx.glitch(tl, target, at, { mode: 'cut' \| 'in' \| 'out', frames: 7, split: 9, blocks: 16, shake, shakePx: 18, seed })` | `FX.glitch(tl, '#b02-gl', L(296), { mode: 'cut', shake: '#b02-cam' })` | k..k+frames-1: a new seeded layout of #FF2E7E / white blocks + pixel-sort streaks each frame (hard cuts); RGB split 9 px on k+2..k+5; 'in': target shows k, drops k+1, back k+2; 'out': 35% at k+frames-2, gone at k+frames; the element jitters +/-6-14 px per frame; `shake` jitters a footage wrapper. 'cut' = a full-frame host timed over the transition (e.g. "breaks.") |
| `fx.errorWindow(host, { title: "Race'n'Chase", text, scale: 1.8, x, y })` | `FX.errorWindow('#b02-err')` | builds the v04-look dialog (the kit's `.m-errbox`) centred on --x / --y, 640 px x scale |
| `fx.errorPop(tl, host, at, { from: 1.12 })` | `FX.errorPop(tl, '#b02-err', L(228))` | k visible at 112% -> 100% by k+3 (expo.out) |
| `fx.errorCascade(tl, host, at, { count: 10, dx: 36, dy: 27, stepF: 2 })` | `FX.errorCascade(tl, '#b02-err', L(234))` | copy i (1..count) at +i x (36, 27) px appears (hard cut) on k + (i-1) x 2; they run off frame |
| `fx.errorSnapShut(tl, host, at, { frames: 3, stepF: 1 })` | `FX.errorSnapShut(tl, '#b02-err', L(279), { stepF: 0.5 })` | last-in first: window i starts on k + round(i x stepF), scale -> 0 over 3f (power2.in), gone at +3 |
| `fx.errorFlash(tl, host, at, { frames: 2 })` | `FX.errorFlash(tl, '#b08-err', L(2))` | visible on k and k+1 only |
| `fx.flash(tl, host, at, { opacity: 1, frames: 1, color })` | `FX.flash(tl, '#b01-flash', 0, { opacity: 0.7 })` | white layer on k .. k+frames-1 |
| `fx.shake(tl, wrapper, at, { px: 6, frames: 4, seed, decay: true })` | `FX.shake(tl, '#b13-cam', L(160), { px: 12, frames: 8 })` | a seeded offset each frame k..k+n-1 (px decaying to px/3), 0 on k+n |
| `fx.jitter(tl, el, at, { px: 4.5, every: 1, until, frames, seed })` | `FX.jitter(tl, '#b02-lk-2 .rc-lw', W.broke)` | a new seeded offset (<= px) every frame until `until` / the clip end, 0 at the end |
| `fx.flashStar(tl, host, at, { x, y, size: 560, frames: 5, rotate: 18 })` | `FX.flashStar(tl, '#b10-star', L(30))` | k at 40%; k..k+2 -> 100% (expo.out); k+2..k+5 -> 125% and transparent (power2.out) |
| `fx.logoSlam(tl, el, at, { from: 150, overshoot: 94, frames: 6, flash, flashOpacity: 0.85, star, shakeTarget, shakePx: 9, shakeF: 6 })` (B1, B13, B17 call this; el = an untimed wrapper of the logo) | `FX.logoSlam(tl, '#b13-logo', L(130), { from: 160, flash: '#b13-flash', star: '#b13-star', shakeTarget: '#b13-cam', shakePx: 12, shakeF: 8 })` | k visible at `from`; k..k+4 -> overshoot (power2.in); k+4..k+6 -> 100% (power2.out); impact k+4: 1-frame flash, flash-star, shake |
| `fx.rgbSplit(tl, target, at, { px: 9, frames: 6, settle: 0, every: 2, until })` | `FX.rgbSplit(tl, '#b16-lk-2 .rc-lk__row--hero .rc-lw', W.bug, { px: 6, settle: 2 })` | k..k+frames-1 px narrowing to `settle` (hard steps); settle 0: clean on k+frames; settle > 0 = never settles: +/-1 px around it every 2f until `until` / the clip end. Text: red / cyan shadows; elements: SVG channel split |
| `fx.rgbGrading(px)` (footage, static) | `media-treatment --selector "#b02-freeze" --grading '<JSON>' --apply` | `{ effects: { chromaticAberration: px x CA_PER_PX } }` |
| `fx.highlight(tl, el, at, { frames: 8 })`; el = `<div class="fx-hl fx-hl--dark">` (screen, dark pages) or `fx-hl` (multiply) laid over the line | `FX.highlight(tl, '#b04-hl', L(6))` | k..k+8 wipe left -> right (power2.out); #FF2E7E 55%; no page push (U3) |
| `fx.annotate(tl, host, at, { type: 'arrow' \| 'circle' \| 'underline' \| 'strike', from, to, rect, label, labelAt, color, width, frames, jitter: 1.5, seed })` | `FX.annotate(tl, '#b03-ann', W.Lemmings, { type: 'circle', rect: [820, 600, 200, 180] })` | arrow: shaft k..k+6, head k+6..k+9; circle / underline k..k+9; strike (#E3262B) k..k+6 (stroke trim, power2.out); label hard-cuts in at the end; marker texture; +/-1.5 px jitter every 2f until the host ends |
| `fx.cardInsertHTML({ id, src, img, start, dur, mediaStart, x, y, w: 1080, h: 810, tilt: 3, border: 15, bg: 'blur', bgScale: 1.3, blurPx: 60, darken: 0.5, z })` (Node or browser) | `html += FX.cardInsertHTML({ id: 'b03-card', src: 'assets/footage/R3.7.mp4', start: L(105), dur: 1.5, mediaStart: 2 })` | static: the clip in a white 15 px frame, tilted, shadow 0 27px 60px 50%, on the same clip at 130%, blurred 60 px and darkened 50% (media treatment); push with `C.push(tl, '#b03-card .fx-card__cam', at, { until, to: 1.06 })` |
| `fx.darkCardHTML({ id, start, dur, src, mediaStart, opacity: 0.2, blurPx: 40, darken: 0.5, z })` | `html += FX.darkCardHTML({ id: 'b13-dark', start: 0, dur: 1.2, src: 'assets/footage/R13.2.mp4' })` | static: #0E0E10, the footage blurred + darkened at 15-25%, grain + scanlines on top; text above it (higher z) |
| `fx.archivalGrading({ ca: 2, wobble: 0.18, tracking: 0.22, noise: 0.08 })`, `fx.archivalCmd(selector, o)` | `node -e "...console.log(RCK.fx.archivalCmd('#b02-crt'))"` | media treatment for 1990s camera footage: a little chromatic aberration (px x CA_PER_PX) + tape tracking / damage = the light VHS line wobble (moves with media time; the global animated aberration stays in the finish, U8) |
| `fx.slotCounter(tl, host, at, { from: '18', to: '30', frames: 14, size: 330, spins, staggerF: 3 })` | `FX.slotCounter(tl, '#b12-slot', L(44))` | k..k+14 the digit strips roll up (expo.out; units 2 turns, tens 1; the left column lands 3f earlier); vertical motion blur follows the speed each frame, none on landing. Coolvetica Italic |
| `fx.calendarTear(tl, host, at, { from: 'MAR 1995', to: 'NOV 1997', frames: 12, size: 300, seed })` | `FX.calendarTear(tl, '#b13-cal', W.In)` + `T.glowFlicker(tl, '#b13-cal .fx-cal__text--to', W.November)` | dark pad, Coolvetica Italic; k..k+2 the page lifts (-3 deg, power2.out); k+2 the torn stub; k+2..k+12 the page rips along the torn edge and falls (-38 deg, x -260, y +1100, power2.in) |
| `fx.locationTag(tl, host, at, { x: 96, y: 640, w: 260, h: 340, zoom: 3, frames: 12, label, pin: [lon, lat] })` | `FX.locationTag(tl, '#b03-loc', W.Dundee, { label: 'Dundee, Scotland' })` | k the tag cuts in; k..k+12 the UK outline (white 3 px, non-scaling) zooms x3 toward the #FF2E7E Dundee pin (power2.inOut); label (Coolvetica, uppercase) at k+6; pin ring pulse k+10..k+20 |
| `fx.vcr(host, { text: 'MAR 22 1995', label: 'PLAY', right: 96, bottom: 70 })` | `FX.vcr('#b02-vcr')` | static "PLAY ▶ MAR 22 1995", Coolvetica 42 px uppercase (the triangle is drawn), bottom-right |
| `fx.zoomThrough(tl, outWrapper, at, { to: 4, frames: 8, origin, blur: 0.8, in, inFrom: 1.3, inF: 6 })` (alias `whipZoom`; the transition kept since v03, e.g. B2 into the monitor; not for B9, U9) | `FX.zoomThrough(tl, '#b02-cam', L(193), { origin: '1180px 420px', in: '#b02-cam2' })` | k..k+8 scale 1 -> 4 (expo.in) + the media blur ramps up; cut on k+8; the incoming wrapper k+8..k+14 1.3 -> 1 (expo.out), blur down |
| `.fx-year` (class) | `<div class="fx-year">1997</div>` inside a tile | Coolvetica 60 px, bottom-left |

Media blur for the zoom-through: give each `<video>` `data-color-grading='{"preset":null,"intensity":1,"effects":{"blur":0.01}}'`
and `style="--hf-color-grading-blur: 0"`. Footage is never CSS-filtered (HyperFrames rule 11): footage blur / grade /
aberration / wobble are media treatments; the CSS / SVG filters in this kit touch DOM graphics only.

## 4. Render cost

Pop blur runs 4 frames per starred word and is then removed; the RGB split only on its frames; the glitch is 16
transformed divs; textures are a static PNG and a gradient. Expensive: media-treatment blur (multipass) on the card-insert
and dark-card backgrounds (one full-frame layer each) and during zoom-throughs. In this container's software renderer the
demo's 118 snapshots took about 10 minutes, mostly on those layers.

## 5. Removed by the override (do not use)

Pink colour-flash entry, caption drift 100 -> 104%, siren colour flicker (`T.sirenFlicker` still exists, unused), type-on,
rubber stamp, 3D Y-flip, off-white paper, the page push under highlighter sweeps, Inter / Playfair / Montserrat / VT323 /
Arimo. The v02 camera moves (punchIn, keyPunch, zoomOut) stay retired (v03).

## 6. Limits

* [DEPTH] is a lane job (G6): cut the subject out and stack plate -> lockup -> cut-out; a lockup is one element, so a
  hero behind the subject with setup words in front = two lockup calls.
* RGB split on footage during a 'cut' glitch is carried by the blocks (rule 11); for a frozen still use `fx.rgbGrading`.
* The UK outline is hand-traced (~100 points); it reads at tag size, not as a map.
