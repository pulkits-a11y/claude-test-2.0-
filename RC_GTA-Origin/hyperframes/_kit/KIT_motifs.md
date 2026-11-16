# KIT_motifs: M1-M4, L8 CRT, L9 calendar, B2 error box, B7 CANCELLED stamp, camera shake

Files: `motifs.css`, `motifs.js`, `svg/motifs-star.svg`, `svg/motifs-bug.svg`, `svg/motifs-bug-chip.svg`.
Golden rule: the Master Edit Plan (`00_Brief/GTA_VI_Edit_Plan.pdf`). Page refs: L8 p.14, L9 p.15, M1-M4 p.17-18,
B1/B2 p.20, B4 p.21, B5 p.22, B7 p.23, B11 p.24, B12 p.25, B14 p.26, B16/B17 p.27.
Proof: `hyperframes/_demo-motifs/` (every item in sequence, used exactly as a beat uses the kit; stills in `review/`).

## v02 (REVISION_v02.md): the calendar's opening animation, nothing linear, Coolvetica. Read this first

The v01 reference below still describes every motif; this section lists what v02 changes. Proof: `hyperframes/_demo-v02/`
section D2 (B12 calendar); values in `review/measure_v02.json` (`camera.calendarIn`, `counter`, `layout.M3counter`).

Easing map (easings.net name -> GSAP -> CSS bezier, and which curve the kit uses where): KIT_type.md, v02 > Easing
(`RCK.ease`, defined in type.js). Every helper's `opts.ease` accepts `'easeOutExpo'` or `'expo.out'`.

### What changed in motifs.js / motifs.css

| Item | v01 | v02 |
|---|---|---|
| M3 calendar opening (B12, note 6: "an opening animation where it comes into the screen ... a bit more above, to the center") | none | new `calendarIn` (below); place the calendar higher with `calendarInit`'s `y` |
| M3 counter roll | 2f per roll, power3.out | 2f per roll, power1.inOut = easeInOutQuad (REVISION_v02 table: "number rolls, counters"); the frame between two values shows the strip mid-roll (two half digits), as an odometer does. `opts.rollEase` |
| M3 counter position | Inter metrics | Coolvetica metrics (ascent 0.967, descent 0.233, digits 0.688 em): the digit top sits on the grid top (measured 399.97 vs 400) |
| M2 label "you", M3 counter, stamp | Inter SemiBold / Bold / Black | Coolvetica (one weight; `font-synthesis: none`, so no faux bold) |
| `opts.ease` (stars, arrow, chip, roll) | GSAP names | GSAP or easings.net names; `none` / `linear` refused |
| unchanged, already eased | star pop power3.out, arrow draw power3.out / erase power3.in, chip pop power3.out + power2.inOut, stamp slam power2.in | |
| unchanged, cuts (not moves) | calendar fills, star blink, error box pop, camera shake offsets, CRT flicker values | one value per frame, hard |

Not used by the v02 beats (kept, eased): the CANCELLED stamps and their shake (B7 note 3: "just make it turn red"), the
M4 bug chip (note 8: the word "bug").

### `RCK.motifs.calendarIn(tl, target, at, opts)`: the B12 opening animation

Grid and counter rise and scale in together: from `y` + `rise` (90 px) and `from` (90%) about the grid centre to rest
over `durF` (12) frames, easeOutExpo (`ease`; e.g. `'back.out(1.7)'` = easeOutBack for a small overshoot), with opacity
0 -> 1 over the first `fadeF` (6) frames (power2.out). The calendar root (`.m3-cal`) stays the clip; its generated children
move inside an untimed `.m3-body` wrapper that the helper creates. Returns at + durF.
Measured (demo, start f428): f428 90% / +90 px / 0 | f429 94.4% / +50.8 px / 0.42 | f430 96.8% / +28.7 px / 0.70 |
f431 98.2% / +15.9 px / 0.88 | f434 99.8% / +2.1 px / 1 | f440 100% / 0 / 1.
```js
const M = RCK.motifs;
M.calendarInit('#b12-cal', { slots: 18, filled: 18, counter: 18, y: 400 });   // higher than v01's 520 (note 6); first init wins
M.calendarIn(tl, '#b12-cal', L(6));                                           // comes into the screen on the beat's first frame
M.calendarExtend(tl, '#b12-cal', 0, { to: 30, landAt: W.thirty });           // 12 red squares 2f apart, counter lands on "thirty"
```
(`calendarInit` must run before `calendarIn` / `calendarExtend` when you pass layout options: the first init wins.)

---

# v01 reference (still valid where the v02 section above does not override it)

## 0. How to use (all items)

* The beat skeleton (`tools/new_beat.py`) already links `assets/kit/motifs.css` and `assets/kit/motifs.js` (after GSAP and
  `base.css`). Nothing else to install. Helpers live on `RCK.motifs`.
* **Timeline helpers** are pure: `helper(tl, target, atSeconds, opts) -> endSeconds`. They only add tweens/sets to your paused
  timeline `tl`. `target` = selector string or element. Each helper calls its `xxxInit` itself (idempotent, first call wins), so
  you normally never call an init yourself. Pass composition seconds (e.g. `words.json` `comp_t`).
* **Frames**: every time is snapped to the nearest 30 fps frame. "Lands on frame k" below means the rendered frame `k`
  (local, = `round(t*30)`) shows that state. Hard changes are `tl.set()` placed 0.1 ms before their frame, so the HyperFrames
  seek (`floor(t*30)/30`) always includes them. Helpers return frame-exact seconds you can chain.
* **Where `class="clip"` goes**: on the component element itself (`.m1-stars`, `.m2-arrow`, `.m3-cal`, `.m-errbox`, `.m-stamp`)
  or on any wrapper of it. The helpers never transform the element you time; they animate its generated children
  (verified: a component can be a root-level `.clip`; HyperFrames keeps its inline position).
  Exceptions: the **M4 chip** and the **shake container** are transformed by GSAP, so they must NOT carry `class="clip"`; and in
  **L8** the `<video>` is the clip and its `.l8-screen` wrapper stays untimed (HyperFrames: "time the video, never its wrapper").
* Deterministic and seek-safe: no `Date.now()`, no `Math.random()` (seeded `RCK.rng`), no timers, no `repeat:-1`, no CSS
  transform on anything GSAP transforms (start states are set with `gsap.set`/`fromTo`).
* Palette only (base.css vars). Blends of palette colours are used in exactly two places and documented: the calendar's empty
  outline (`#111111` at 35% over `#E9E9E9`) and the error box's mid-shadow bevel line (`#111111` at 45%).
* Layout-audit attributes are set by the kit where layering is intended (counter strips, stamp ink). Demo labels are not kit.

---

## 1. M1 wanted stars (B1, B14, B17)

**Plan (p.17, p.20, p.26, p.27):** white five-point stars with a thin dark outline, styled after the GTA wanted level. 40 px each
at the top-right (x 1700, y 80) in B1 and B17; 120 px centred in B14. Each star pops in over 3f, 3f apart. B1: five stars fill in
top-right as the hook lands (across "have you running from the"). B14: six stars fill in, centred, on "The wanted stars.".
B17: the stars blink over Lucia (five, top-right).

**Built:** star = white `#FFFFFF` fill, `#0A0A0A` outline 4.5% of the star size (1.8 px at 40 px, 5.4 px at 120 px), outside
the fill, round joins; outer radius 47.8 / inner 0.48 in a 100-unit box (same drawing as `svg/motifs-star.svg`).
"40 px each" = the star box (incl. outline) is 40 x 40. Row gap = 20% of the star size (8 px at 40, 24 px at 120).
`(1700, 80)` = **centre of the star row** (my reading of "at the top-right (x 1700, y 80)"): the 5 x 40 row spans
x 1584-1816, y 60-100, inside title-safe (96/54). B14 row: 6 x 120, centred on (960, 540), spans x 540-1380, y 480-600.

**Markup** (stars are generated):
```html
<div id="b1-stars" class="clip m1-stars" data-preset="hud"  data-start="..." data-duration="..." style="z-index:20"></div>
<div id="b14-stars" class="clip m1-stars" data-preset="hero" data-start="..." data-duration="..."></div>
<!-- optional overrides: data-count, data-size, data-gap, data-x, data-y, data-anchor="center|left|right" -->
```

**JS:**
```js
RCK.motifs.starsPopIn(tl, "#b1-stars", at, { stepF: 3, durF: 3, order: "ltr", times: null }); // -> last star landed (s)
RCK.motifs.starsBlink(tl, "#b17-stars", at, { until: sec /* or cycles: 4 */, onF: 6, offF: 6, offOpacity: 0 }); // -> until
RCK.motifs.starsInit("#id", { preset: "hud"|"hero", count, size, gap, x, y, anchor }); // optional, idempotent
```

**Timing:** pop-in = `scale 0 -> 1`, 3f, `power3.out` (ease out, **no overshoot**: T7 is "the only bouncy animation").
Star i starts on frame `k0 + 3i`; frame `k0+3i` shows nothing, `+1` = 70%, `+2` = 96%, `+3` = 100%. Five stars: last lands on
`k0 + 15`; six stars: `k0 + 18`. Blink: all stars together, hard on/off (no fade): ON `onF` frames, OFF `offF` frames, first OFF
at `k0 + onF`, forced ON at `until`. Default 6f on / 6f off = 2.5 blinks/s (my choice; the plan only says "blink").
`offOpacity: 0.3` gives a GTA-V-style dim flash instead of a full blink (SUGGESTION, not the default).

**Beats** (local frames from `timing/beat_map.json`, beat starts at local f6):
* B1 `b01-hook`: "have" f98 ... "the" f128, "cops?" f133. `starsPopIn(tl, "#b1-stars", W.have)` -> stars land f101, f104, f107,
  f110, f113 (done during "running"). The plan says both "3f apart" and "across 'have you running from the'" (f98-f133);
  3f apart wins by literal value; `times: [W.have, W.you, W.running, W.from, W.the]` is available if the builder prefers one star
  per word (record it as a conflict if used).
* B14 `b14-since`: "The" f102, "wanted" f108, "stars." f120. `starsPopIn(tl, "#b14-stars", W.The)` -> six stars land
  f105 ... f120 = exactly on "stars.". Stars are on screen with the T4 phrase "The wanted stars." (top-left, type kit).
* B17 `b17-loop`: stars blink over Lucia during the Trailer 1 opening (until "So who's" f112 / the chase shots). E.g.
  `const e = starsPopIn(tl, "#b17-stars", 0.2); starsBlink(tl, "#b17-stars", e, { until: W.So })`. Note: with the L2 band
  (138 px bars) the HUD row at y 60-100 sits on the top black bar; that is where the plan puts it.

**Limits:** row only (no multi-row); stars are one drawing (no "empty" star state, the plan has none).

---

## 2. M2 the "you" arrow (B5, B11)

**Plan (p.17, p.22, p.24):** #FFE14D, 6 px stroke, drawn on over 8f. "you" in Inter SemiBold 36 px, yellow. Hand-drawn look.
B5: points at the cop car (left half of the L11 split); B11: the same arrow redraws and points at the getaway car.

**Built:** a seeded, slightly wobbled cubic shaft (bow = `bend` x length) + a hand-drawn head "V" (barb -> tip -> barb,
34 px +/- 4 px, 28 deg +/- 4 deg), 6 px round-capped stroke `#FFE14D`; label "you" Inter SemiBold 36 px `#FFE14D` with the
plan's text shadow (text on footage). Start and end points are parameters, so the same asset (same `seed`) points anywhere.
Wobble/head ideas adapted from registry `hw-arrow` (its 21f draw, boil loop and Caveat font were not used).

**Markup:**
```html
<div id="b5-arrow" class="clip m2-arrow" data-start="..." data-duration="..." style="z-index:20"></div>
<!-- or put geometry in HTML: data-from="760,330" data-to="500,610" data-bend="0.16" data-seed="7" data-label="you" -->
```
The element is a 1920 x 1080 overlay (`left:0; top:0`); coordinates are canvas px. Put it inside the flipping L11 container
if the arrow must flip with the split screen; put it outside (on top) if it must stay upright.

**JS:**
```js
RCK.motifs.arrowDraw(tl, "#b5-arrow", at, { from: [x, y], to: [x, y], bend: 0.16, seed: 7, durF: 8, ease: "power3.out",
  label: "you", labelAt: null /* [x,y] centre */, labelGap: 14, headLen: 34, headAngle: 28 });   // -> draw end (s)
RCK.motifs.arrowErase(tl, "#b5-arrow", at, { durF: 6 });   // optional exit (NOT in the plan) -> end
RCK.motifs.arrowInit("#id", { ..., drawn: true });          // already drawn (e.g. carried over a cut)
```
`bend` > 0 bows to the left of the travel direction (screen y down), < 0 to the right. The label defaults to just behind the tail
along the tail direction; pass `labelAt` to place it.

**Timing:** draw-on over 8f with `power3.out` across the whole pen move: the shaft draws first (frames k..~k+4), the head "V"
finishes on frame `k+8` (stroke-dashoffset on two paths with `pathLength=100`; SVG restarts dashes per subpath, hence two
paths). "you" hard-cuts in on frame k (the first frame of the draw). Measured: f240 label only, f241-243 shaft, f243-248 head,
complete f248 (= k+8).

**Beats:**
* B5 `b05-copgame`: "you" f20. `arrowDraw(tl, "#b5-arrow", W.you, { from, to })` -> drawn by f28. Pick from/to on the real
  footage (left half x 0-958 of the L11 split).
* B11 `b11-flip`: "Now" f109 ("Now you're the one"). `arrowDraw(tl, "#b11-arrow", W.Now, { from, to: getawayCar, seed: 7 })`
  -> drawn by f117. Same seed as B5 = same hand. "Redraws" = drawn on fresh (B11 is its own composition).
* Cover frame (plan p.39): B11 flipped split with the arrow on the getaway car (the same element, any frame >= f117).

**Limits:** one arrow per element; geometry fixed per element (use a second element to retarget within one composition).

---

## 3. M3 calendar grid = L9 calendar counter (B4, B12)

**Plan (p.15, p.17, p.21, p.25):** grid of 64 px squares with 8 px gaps (6 columns), on a gray card. Squares fill in left to
right, 2f apart; overrun squares fill siren red. B4: 18 squares fill in for the planned 18 months, T2 text above it. B12: the
same composition returns with 18 filled and a counter "18" (Inter Bold 120 px) at its top-left; on "turn into", 12 more squares
fill siren red, 2f apart, while the counter rolls 18 -> 30, landing on "thirty". Reuse and extend the same composition.
Watch out: no start/end dates on the calendar.

**Built:** one component, parameterised. Filled = card ink `#111111`; overrun (month 19+) = siren red `#E3262E`;
**empty slot = 2 px inset outline in card ink at 35%** (renders `#9D9D9D` on `#E9E9E9`; a palette mix, no new hex).
Fill = hard change on its frame (no tween; the plan specifies none). The counter is an odometer: one roll per square
(digits slide up over 2f, `power3.out`), Inter Bold 120 px, card ink, tabular figures. No dates, month names or years.
"Gray card" = a full-frame `#E9E9E9` (use `<div class="clip rc-card rc-full">` from base.css behind it).
Default geometry (identical in B4 and B12): grid top-left (748, 520) = grid centred on x 960; 3 rows end at y 728, 5 rows at
y 872. Counter "at its top-left": default `counterPos: "left"` = right edge 32 px left of the grid, cap top aligned with the
grid top (measured: cap top y 519, x 567-709); `"above"` puts it over the grid's left edge (baseline 24 px above the grid).
"left" keeps the B4 layout (T2 above the grid) unchanged in B12.

**Markup** (squares and counter are generated):
```html
<div class="clip rc-card rc-full" data-start="..." data-duration="..."></div>          <!-- the gray card -->
<div id="b4-cal" class="clip m3-cal" data-start="..." data-duration="..." style="z-index:10"></div>
```

**JS:**
```js
// B4: 18 empty slots appear with the card, then fill 2f apart
RCK.motifs.calendarFill(tl, "#b4-cal", at, { slots: 18, filled: 0 });            // -> frame time the 18th square shows
// B12: same calendar, 18 filled + counter 18, grows to 30 (12 red squares, counter rolls)
RCK.motifs.calendarExtend(tl, "#b12-cal", at, { slots: 18, filled: 18, counter: 18, to: 30,
  stepF: 2, rollF: 2, grow: "with-fill" /* or "before" + growAt */, landAt: null });     // -> counter landed (s)
// init options (first call wins): cols 6, max 30, slots, filled, overFrom 18, x, y, sq 64, gap 8,
//   counter (start value or null), counterPos "left"|"above", counterGap
```

**v02:** counter rolls are power1.inOut (easeInOutQuad), and `calendarIn` adds the B12 opening animation (v02 section).
**Timing:** square i (from the first unfilled) fills on frame `k0 + 2i`. B4: 18 squares on k0 ... k0+34. B12: square 19..30 on
k0 ... k0+22; with `grow: "with-fill"` each new square appears already red on its frame (the grid grows square by square);
`grow: "before"` shows all 12 empty slots at `growAt` first. Counter = 18 + filled red squares, each roll 2f, so it lands on 30
at `k0 + 24`. `landAt: t` computes `k0 = frame(t) - 24` so the counter lands exactly on `t`.

**Beats:**
* B4 `b04-racenchase`: "planned" f63, "eighteen" f87, "months." f94, beat ends f114. Cutting to the card on "planned" and
  `calendarFill(tl, "#b4-cal", W.planned)` puts the 18th square on f97 (right after "months." starts). T2 "planned to take /
  18 months." (type kit) sits above the grid (demo stand-in: baseline ~y 470).
* B12 `b12-thirty`: "turn" f59, "into" f71, "thirty." f75-f81, beat ends f89. **Conflict inside the B12 build:** "on 'turn into'"
  + "2f apart" + "landing on 'thirty'" need 24f but turn -> thirty is 16f in the processed VO. Options:
  (a) `calendarExtend(tl, el, W.turn, ...)` -> fill f59-f81, counter lands f83 (8f after "thirty" starts);
  (b) `calendarExtend(tl, el, 0, { ..., landAt: W.thirty })` -> fill starts f51 (on "months"), lands f75 on "thirty".
  Builder's choice; S11's hit goes on the landing frame (the plan ties it to both "thirty" and the counter landing). Record it.

**Limits:** counter digits = digits of `max` (no leading-zero hiding needed for 18-30); 6-column grid assumed by the defaults.

---

## 4. M4 the bug chip (B2, B16; B8/B17 per the plan are X4 + T10, not this chip)

**Plan (p.17, p.13, p.20, p.27):** bug chip = an 8-bit beetle icon, white on a dark chip. T7: 72 x 56 px rounded chip (12 px
radius) in an Inter Medium 46 px sentence; chip scales 0 -> 112% -> 100% over 8f (the only bouncy animation). B2: pops inside
"And that [bug chip] saved it." on "bug"; B16: pops at the end of the T5 glow line in place of "bug" as it is spoken.

**Built:** chip 72 x 56, radius 12, card ink `#111111`; beetle = 11 x 10 pixel sprite at 4 px per pixel (44 x 40), white,
`shape-rendering: crispEdges`, centred on whole pixels (14, 8). `svg/motifs-bug.svg` (icon), `svg/motifs-bug-chip.svg` (chip +
icon as one graphic for other tools).

**Markup** (inside the T7 or T5 line; combine with the type kit's chip class for its baseline alignment):
```html
And that <span id="b2-chip" class="rc-t7__chip m4-chip"></span> saved it.
```
The beetle `<svg class="m4-bug">` is inserted by `bugChipInit`/`bugChipPop` (or paste it: path `RCK.motifs.BUG_D`,
viewBox `0 0 11 10`, width 44, height 40). The chip must not be the `.clip` (it is scaled); time the sentence instead.

**JS:**
```js
RCK.motifs.bugChipPop(tl, "#b2-chip", W.bug);                        // -> settled (s) = k+8
RCK.motifs.bugChipPop(tl, "#b2-chip", W.bug, { ease: "back.out(1.7)" }); // single-tween variant (peaks ~110%)
RCK.motifs.bugChipInit("#b2-chip");                                  // only inserts the beetle (no animation)
```
If the line is built with the type kit's `RCK.type.chipSentence` / T5 helper (which already pops `.rc-t7__chip` with the same
frames), call only `bugChipInit` - never both pops on one chip.

**Timing:** frame k = scale 0 (hidden), 0 -> 1.12 over 5f (`power3.out`), 1.12 -> 1.00 over 3f (`power2.inOut`): frame k+5 is
exactly 112%, k+8 = 100%. Measured (sprite bbox): k+1 0.64, k+2 0.95, k+3..k+6 1.09-1.12, k+8 1.00.

**Beats:** B2 `b02-bug` "bug" f156 -> settles f164. B16 `b16-bug-origin` "bug." f107 -> settles f115.

**Limits:** on the B16 black (`#0A0A0A`) the `#111111` chip edge is barely visible; the white beetle carries it.

---

## 5. L8 CRT monitor screen insert (B2)

**Plan (p.14, p.20):** footage inside a 1990s CRT monitor graphic: 8% bulge, 3 px scanlines at 15%, 1 px colour fringing,
brightness flicker between 97% and 100%. Plate = real footage R3.9; the GTA 1 picture (R9.1) is composited into its screen.

**Built:** `.l8-screen` = untimed wrapper corner-pinned onto the plate's screen (CSS `matrix3d` homography, computed once);
the picture `<video>` inside it is the clip and carries a **media treatment** (canonical `data-color-grading`, written with the
CLI) for bulge, scanlines and fringe; the flicker animates the treatment's `--hf-color-grading-exposure` per frame.

| Plan | Treatment value | Measured (calibrated gray test clip, `crtlab`) |
|---|---|---|
| 8% bulge | `crtCurvature: 0.16` (shader warps media UV by 0.5 x value: edge midpoints 8%) | 25 px black band top/bottom on a 720 px screen, black corners |
| 3 px scanlines at 15% | `scanlines: 0.15`, `scanlineSoftness: 0`, `scanlineCount: (h/3 - 50)/450` | 6 px period, 3 px dark rows, 128 -> 109 (-14.8%) |
| 1 px colour fringing | `chromaticAberration: 50 / mediaW`, `chromaticAngle: 0` | R/B split ~1 px each side (pixel-rounded) |
| flicker 97-100% | exposure `log2(b)`, b seeded per frame in [0.97, 1.00] | 118.35 -> 114.80 (97.0%) ... back to 100% at `until` |

`h` = the insert's height, `mediaW` = the displayed media width (= insert width when the source fills it; `h * 16/9` when a
16:9 source is `object-fit: cover`ed into a 4:3 screen).

**Markup:**
```html
<video id="b2-plate" class="clip" src="assets/footage/R3.9.mp4" data-start="..." data-duration="..." muted playsinline></video>
<div id="b2-crt" class="l8-screen" data-corners="TLx,TLy TRx,TRy BRx,BRy BLx,BLy">   <!-- untimed, no background -->
  <video id="b2-crt-pic" class="clip l8-picture" src="assets/footage/R9.1.mp4" data-start="..." data-duration="..." muted playsinline></video>
</div>
```
Put the plate and the `.l8-screen` inside ONE untimed wrapper if the X6 zoom (transitions kit) scales them together; never
GSAP-transform `.l8-screen` itself (its transform is the corner pin). `--l8-object-position` moves the crop.

**JS / CLI:**
```js
RCK.motifs.crtFit("#b2-crt");                                   // reads data-corners (or {corners:[[x,y]x4]} / {rect:[x,y,w,h]}) -> {w,h}
RCK.motifs.crtFlicker(tl, "#b2-crt-pic", tStart, { until: tEnd, min: 0.97, max: 1.0, seed: 97, everyF: 1 }); // -> until
```
Grading JSON for your corners, then persist it (run inside the beat project):
```bash
G=$(node -e 'global.window=global;require("vm").runInThisContext(require("fs").readFileSync("assets/kit/motifs.js","utf8"));
const s=RCK.motifs.crtSize({corners:[[1060,230],[1760,250],[1750,770],[1070,790]]});
console.log(JSON.stringify(RCK.motifs.crtGrading(s,{srcAspect:16/9})))')
npx --yes hyperframes@0.9.52 media-treatment --selector "#b2-crt-pic" --grading "$G" --apply --json
```
(The CLI normalises the file and adds `data-hf-id` attributes; harmless.)

**Timing:** flicker = one value per frame from `tStart` (frame 0 = 100%, frame 1 = 97%, then seeded values), exactly 100% from
`until`. Bulge/scanlines/fringe are static for the whole clip.

**Beats:** B2 `b02-bug`: X6 out (transitions kit) lands on the plate; picture = R9.1; on "broke" (f107) the X4 tear runs on the
picture only (transitions kit; it can patch `digitalGlitch` onto the same `<video>` with the CLI), then the error box pops.
Flicker for the whole time the picture is visible.

**Limits / to do with real footage:** the demo uses an **assumed** screen quad on the R3.9 stand-in
(1060,230 1760,250 1750,770 1070,790). Re-fit `data-corners` to the real R3.9 frame (if the camera moves, the quad would have
to be tracked: this insert is static). The bulge is defined on the media frame: with `cover` and a wider source, the side edges
show no black band (only top/bottom). Grading applies to the whole `<video>` only (not to DOM layers on top).

---

## 6. Windows 95-style error box (B2)

**Plan (p.20, p.40):** on "broke", after the X4 tear on the CRT picture, a Windows 95-style error box pops on top: title
"Race'n'Chase", text "This program has performed an illegal operation and will be shut down." Grey box, system font, hard pop.
Stylised recreation, not a real screenshot: generic, no fake date, no file paths.

**Built:** palette grey face `#E9E9E9`; 2-line raised bevel (white `#FFFFFF` top-left, card ink `#111111` bottom-right, inner
mid-shadow = card ink at 45%); title bar card ink `#111111` with white bold title; a plain pixel "x" close box (generic window
chrome). No icon, no buttons, no file path, no date. Font = the generic `sans-serif` keyword = the render machine's own UI
sans (Liberation Sans, Arial-metric, here). Text 28 px (`--m-eb-fs`), Win95 "pixel" `--m-eb-u` 2 px, width 640 px default
(two text lines). Texts exactly as the plan (straight apostrophes as in the plan text: `Race'n'Chase`).

**Markup** (window generated; the clip start IS the hard pop):
```html
<div id="b2-err" class="clip m-errbox" data-start="<pop time>" data-duration="..." style="left:1110px; top:340px; z-index:30"></div>
<!-- vars: --m-eb-w (640px), --m-eb-fs (28px), --m-eb-u (2px); data-title / data-text override the copy (do not) -->
```

**JS:**
```js
RCK.motifs.errorBoxInit("#b2-err", { x, y, width });   // builds the window (call once; no animation)
RCK.motifs.errorBoxPop(tl, "#b2-err", at);              // only if the box sits inside a longer clip: shows it on frame k (no tween)
```

**Timing:** visible from frame `round(data-start*30)`; measured: f749 absent, f750 present (data-start 25.0).

**Beats:** B2: "broke." f107; X4 tear 6-10f on the picture -> pop at ~f113-f117 (S03 starts 3f before the tear). Keep it above
the caption band (T1/T7 at y 592-648): default height ~184 px, e.g. top <= 400.

**Limits:** renders ~640 x 184 px at defaults; the message wraps to 2 lines (3 at 520 px).

---

## 7. CANCELLED stamp (B7) + camera shake

**Plan (p.23):** a red CANCELLED stamp (Inter Black 120 px, #E3262E, rough-edged mask, rotated -8 deg) slams onto the frame
three times: on "keep trying", "shut" and "down". Each slam scales 130% -> 100% over 2f with a 4 px camera shake for 4f.
Offset each stamp by about 30 px and vary the rotation (-8, -4, +6 deg). Third stamp lands just before "Then" (CONFLICTS C10).

**Built:** "CANCELLED" Inter Black 120 px `#E3262E` with a **rubber-stamp border frame** (10 px `#E3262E`, 16 px radius, 4/28 px
padding; part of the "stamp" look; drop it with `.m-stamp--plain` / `plain: true`), ~812 x 148 px. Rough-edged mask = inline
SVG filter `#rcm-stamp-rough` (injected once): fixed-seed `feTurbulence` -> `feDisplacementMap` (edges +/-3 px) + thresholded
fine noise (ink voids). Identical every frame. Three stamps: rotations -8 / -4 / +6, offsets (0,-30) (0,0) (0,+30) px around one
centre (vertical stacking read best of four variants tested; still "about 30 px").

**Markup:**
```html
<div id="b7-cam">                                   <!-- untimed "camera": wraps the L5 frame + stamps; no CSS transform -->
  ... L5 framed clip (screens kit) ...
  <div id="b7-stamp1" class="clip m-stamp" data-start="..." data-duration="..."></div>
  <div id="b7-stamp2" class="clip m-stamp" data-start="..." data-duration="..."></div>
  <div id="b7-stamp3" class="clip m-stamp" data-start="..." data-duration="..."></div>
</div>
```
Keep the uniform gray card OUTSIDE the camera (a shaken full-frame card would expose its edges; a flat card looks the same).

**JS:**
```js
RCK.motifs.stampTriple(tl, ["#b7-stamp1", "#b7-stamp2", "#b7-stamp3"], [t1, t2, t3],
  { center: [x, y], camera: "#b7-cam" /*, offsets, rotations, plain */ });     // -> end of the last shake (s)
RCK.motifs.stampSlam(tl, "#b7-stamp1", at, { x, y, rotation: -8, camera: "#b7-cam", seed, slamF: 2, scaleFrom: 1.3,
  shakeAmp: 4, shakeF: 4, plain: false });                                       // one slam -> shake end
RCK.motifs.stampLandTime(at);                                                    // landing frame time = at + 2f
RCK.motifs.shake(tl, "#container", at, { amp: 4, frames: 4, seed: 4, decay: false });   // -> at + 4f
```

**Timing:** `at` = slam START: frame k shows the stamp at 130% (hard cut in), k+1 ~122% (`power2.in`, accelerating into the
hit), **k+2 = 100% = landing**; shake on frames k+2..k+5 (one offset per frame: one axis exactly +/-4 px, the other +/-1..3 px,
direction alternating), back to 0,0 on k+6. To land on a word: `at = W.word - 2/30`. S06: start each hit 3f, 8f, 4f before
`stampLandTime(at)`. Measured: red bbox 1062 px (f825, 130%) -> 816 px (f827, 100%); frame offsets f827 (-4,+2), f828 (+2,+4),
f829 (-4,+3), f830 (+2,-4), f831 (0,0).

**Beats:** B7 `b07-shutdown`: "keep" f43, "trying" f50, "shut" f65, "down." f76, beat ends f102 ("Then" = B8). E.g. land on
"keep" (start f41), "shut" (start f63), "down" (start f74). The plan's "third stamp just before Then" is handled by S07 (C10).
B8 then shatters the stamp card (X4, transitions kit).

**Limits:** the three stamps overlap by design (~30 px offsets on a 148 px tall stamp); the shake moves only x/y of the
container (a push-in scale tween on it is fine).

---

## 8. What was verified (demo `_demo-motifs`, stills in `review/`)

`npx --yes hyperframes@0.9.52 check --json`: runtime, layout, motion, contrast all clean; **1 lint error remains and it is not
in this area**: `font_family_without_font_face: neue haas grotesk` comes from `base.css` (`--sans`); removing
`"Neue Haas Grotesk"` from `--sans` makes lint 0 errors / 0 warnings (tested on a copy). Craft warnings left on purpose:
no audio (Tesseract owns audio), rolling counter digits shown 2f each (by design), demo-length holds.
Measured on snapshots: star sizes/positions/gaps/pop frames/blink rhythm; arrow colour (255,225,77) and 6 px width, shaft
then head, done at k+8; calendar 64/8 px, 6 cols, fills 2f apart, ink (17,17,17), red (227,38,46), empty outline (157,157,157)
2 px, counter cap top on the grid top, 18 -> 30 landing; chip scale curve; CRT values (table above); error box frame-exact pop;
stamp 130% -> 100% and the 4 px / 4f shake.

## 9. Conflicts and deviations (plan order applied)

1. **System font vs "use only Inter / Instrument Serif"** (B2 build, priority 2, beats the Style kit, priority 5): the error box
   uses the generic `sans-serif` (renders Liberation Sans here). Tahoma/Arial/Helvetica/Verdana are remapped to Inter by the
   HyperFrames compiler; "MS Sans Serif" fails lint, so they are not listed.
2. **Grey box vs palette-only colours**: grey = card gray `#E9E9E9`; title bar card ink (Windows navy is not in the palette);
   mid-shadow bevel = card ink at 45%.
3. **T7 "0 -> 112% -> 100%" (T library, priority 4) vs "T7 overshoot = back.out(1.7)" (toolchain note, priority 5)**:
   back.out(1.7) peaks at 110%; keyframes hit exactly 112% on frame +5. `opts.ease` restores back.out if wanted. The type kit
   uses the same frames.
4. **B1 "3f apart" vs "across 'have you running from the'"** (both B1 build): 3f apart used; the phrase spans 35f.
5. **B12 "on 'turn into'" + "2f apart" + "landing on 'thirty'"** (all B12 build): not simultaneously possible with the processed
   VO (16f vs 24f); both resolutions are one option away (section 3).
6. **"40 px each at the top-right (x 1700, y 80)"**: read as the centre of the row (keeps the row inside title-safe).
7. Choices where the plan is silent (documented, overridable): blink rhythm 6f/6f; star outline 4.5%; star gap 20%; arrow ease
   `power3.out`, bend, head size; empty-slot style; counter position "left"; hard square fills; stamp border, offsets
   (0,+-30), slam ease `power2.in`; error box 28 px text; flicker one value per frame.

## 10. SUGGESTIONS (not built)

* B17: `offOpacity: 0.3` would match GTA V's grey "evading" flash more closely than a full blink.
* M2: a soft shadow under the arrow (same as the text shadow) would help on bright footage; the plan only shadows text.
* Error box: a generic "OK" button would make the Windows 95 look more complete (it adds on-screen text, so not built).
* M4 on B16 black: a 1 px white 20% chip border (as on L4 tiles) would show the chip edge; not in the plan.
* Export stars / arrow / chip / error box / stamp / calendar stills to `05_GFX/` for the Tesseract side (plan p.41 lists them).
