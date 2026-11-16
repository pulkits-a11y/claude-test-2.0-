# KIT_type: typography T1-T10

The RC_GTA-Origin kit's type area: `type.css`, `type.js` (exposes `RCK.type`) and this file.
Source of truth: Master Edit Plan p.9-13 ("Style kit" and "Typography styles (T1-T10)"), the rotation line on p.13 and the
beat builds on p.19-27. Every number below comes from those pages unless it is marked **kit choice** (the plan gives no
value) or **conflict** (see "Conflicts and decisions" at the end).

Demo of every item, built exactly as a beat would: `hyperframes/_demo-type/` (`index.html`, proof frames in `review/`).

## Setup (already done by `tools/new_beat.py`)

```html
<link rel="stylesheet" href="assets/kit/base.css" />
<link rel="stylesheet" href="assets/kit/type.css" />      <!-- plus motifs/transitions/screens.css -->
...
<script src="assets/kit/type.js"></script>                <!-- after the markup, before your timeline script -->
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  const T = RCK.type;
  T.punchPair(tl, '#b01-t2', 4.42, { outAt: 4.833 });     // helpers add tweens to YOUR timeline
  window.__timelines["b01-hook"] = tl;
</script>
```

## Rules every T item follows

* **Timed element = the T element.** You write it in the HTML with `class="clip rc-tN"`, a stable `id`,
  `data-start`, `data-duration` (and `data-track-index`, `style="z-index: …"`). The helpers only animate its children,
  never the `.clip` itself, and never `display`/`visibility`.
* **Hard cut in / out = `data-start` / clip end.** Nothing fades unless the plan says so.
* **Frame grid.** 30 fps. Every time you pass is snapped to the nearest frame. Helpers return seconds on the grid.
* **Write `data-start` / `data-duration` with `T.attr()` / `T.dur()`** (or `attrF`/`durF` for frame numbers).
  The renderer draws frame n at exactly n/30 s and compares raw seconds, so a value rounded *up* (frame 8 = 0.26667 s
  written "0.2667") starts a frame late. `attr` floors to 4 decimals ("0.2666"), and `dur` makes the clip end exactly
  on the frame where the next one starts (all frames 0-2499, durations 1-90 f were checked against the runtime's own
  visibility rule).
* **Hard cuts inside a clip** (a word, a digit, a letter appearing, glitch jumps) are 0.5-frame tweens placed
  strictly between two frames, so frame n always shows the new state whatever order frames are rendered in.
* **Colour.** White with the soft shadow (`--text-shadow`: 0 2 px 12 px black 45%) is the default (text on footage
  and on black). Add `rc-on-card` (from base.css) to the T element on a gray card: card ink `#111111`, no shadow.
  No outlines, no caption boxes (the T9 label is the only box).
* **Position.** `--rc-y` = vertical centre of the text line, in canvas px (set it inline: `style="--rc-y: 300px"`).
  Everything defaults inside title-safe (96 px left/right, 54 px top/bottom).
* **Fonts** come from base.css: Inter 500 captions, 600 lead-ins, 700 year numerals and label, 900 giant type and
  glitch word; Instrument Serif Italic for the emotional word, the small *In*, glow line, quotes; Instrument Serif
  Italic for T8 names too (Style kit > Fonts: "quotes and names").
* **Eases.** "Ease out" = GSAP `power3.out` (the plan's HyperFrames translation). Where the plan names no ease the
  kit uses: fades linear (`none`), moves `power3.out` (marked **kit choice** below).
* `RCK.type.<helper>(tl, target, atSeconds, opts) -> endSeconds`. `target` is a selector or an Element.
  Helpers set start states with `gsap.set` when they are called; call each helper once per element.

## API summary

| Helper | Item | Returns |
|---|---|---|
| `T.frame(t)`, `T.snap(t)` | frame number / seconds on the frame grid | int / s |
| `T.attr(t)`, `T.attrF(n)` | safe `data-start` string | "0.2666" |
| `T.dur(t0, t1)`, `T.durF(n0, n1)` | safe `data-duration` string so the clip ends on the frame of t1 | "0.4000" |
| `T.checkChunks(chunks, max=4)` | T1 word-count check | `[]` or problems |
| `T.captionPlan(words, chunks, {from, end, loose})` | T1 timing from words.json | `{items, next}` |
| `T.captionHTML(plan, {idPrefix, low, z, track, cls})` | T1 HTML to paste | string |
| `T.punchPair(tl, el, at, {outAt})` | T2 | outAt+4f, else at+6f |
| `T.yearCard(tl, el, at, {pushUntil, pushFrom})` | T3 | frame the last digit lands |
| `T.spreadWords(tl, el, at, {times, outAt})`, `T.spreadIn(tl, piece, at)`, `T.spreadOut(tl, el, at)` | T4 | last end |
| `T.glowLine(tl, el, at, {chipAt, leak, leakPeak, leakHold, leakUntil})` | T5 (+T7 chip) | at+12f |
| `T.giantType(tl, el, at, {every})` | T6 | frame the last letter appears |
| `T.chipSentence(tl, el, at, {wordTimes, chipAt, ease})`, `T.chipPop(tl, chip, at, {ease})` | T7 | chip settle (+8f) |
| `T.nameIn(tl, el, at)`, `T.quoteType(tl, el, at, {perFrame})`, `T.walk(tl, el, at, {duration, reverse})` | T8 | at+6f / last char / walk end |
| `T.highlight(tl, el, at)`, `T.label(tl, el, at)` | T9 | at+8f / at+4f |
| `T.glitch(tl, el, at, {frames, seed, settle, amp})` | T10 | at+6f (first clean frame) |

---

## T1 Running caption

**Plan:** Inter Medium 46 px, white, soft shadow. Centred at x 960, y 620; drop to y 860 if a face is in the centre.
Hard cut in on the first syllable, hard cut out on the next chunk. 1-3 words per chunk, never more than 4; within
±2 frames of the voice. Chunks exactly as each beat's "On screen" line (slashes separate chunks).

**Markup** (one timed element per chunk; no JS animation):
```html
<div id="b01-cap-1" class="clip rc-t1" data-start="0.2333" data-duration="0.6667" data-track-index="3" style="z-index: 20">Why does</div>
<div id="b05-cap-1" class="clip rc-t1 rc-t1--low" ...>In it,</div>     <!-- face in the centre: y 860 -->
```
Geometry: box x 96-1824, 56 px line box centred on y 620 (baseline 637, Inter cap-height centre 620.3);
`rc-t1--low` centres it on y 860. Text is centred on x 960, one line, never wraps.

**Timing helper** (run once per beat in Node, paste the output; words matched by position, then spell-checked):
```bash
cd hyperframes/b01-hook && node -e "
globalThis.window = globalThis; require('./assets/kit/type.js'); const T = RCK.type;
const w = require('./words.json').words;
const plan = T.captionPlan(w, 'Why does / every GTA, / even GTA 6, / have you running', { from: 0 });
console.log(T.captionHTML(plan, { idPrefix: 'b01-cap', z: 20, track: 3 })); console.error(plan.items, 'next word', plan.next);"
```
* Each chunk starts on its first word's `comp_t` snapped to the nearest frame (≤ 0.5 f from the voice; `offsetFrames`
  in the plan shows it) and ends on the frame the next chunk starts.
* The last chunk ends on `opts.end` (seconds), else on the next word's `comp_t` (where the next T style takes over),
  else on the last word's end. Throws if a chunk has more than 4 words or a word does not match (`loose: true` to
  accept a deliberate spelling difference).
* `T.checkChunks('a / b c d e f')` → `[{index, chunk, words, problem}]`.

**Beats** (plan p.19-27; `from` = index of the chunk's first word in words.json):
B1 `Why does / every GTA, / even GTA 6, / have you running` (from 0, ends at "from" = T2) ·
B2 `Because back / in 1995, / a game about / chasing criminals / broke.` (from 0, ends at "And" = T7) ·
B3 `Here's how.` (from 0) and `starts a new game.` (from 13) ·
B5 `In it, / you play / a police officer / chasing criminals.` ·
B6 `But there's / a problem:` (ends at "it's" = T2) ·
B7 `So the people / above the team / keep trying / to shut it down.` ·
B8 `Then, something` (ends at "breaks." = T10) ·
B9 `The police cars / stop following you / and start trying / to drive straight / through you.` (ends at "They" = T4) ·
B11 `So the team / flips the whole game. / You're not the cop / anymore. / Now you're the one / being chased.` ·
B12 `Of course,` (ends at "turn" = T2) ·
B13 `Until finally,` (from 0) and `it ships with / a new name:` (from 5, ends at "Grand" = T6) ·
B14 `And every GTA since / is built around / that chase.` (ends at "The" = T4) ·
B15 `Don't believe me? / Open GTA Online / and buy an arcade. / One of the machines / is called` (ends at "Race" = T9) ·
B16 `So that's why / you're always running.` (ends at "The" = T5) ·
B17 `And GTA 6? / It opens with / Lucia already caught. / So who's` (ends at "chasing" = T2).

**Limits:** one line only (4 words at 46 px always fit). `check` may warn `line_unread` on short chunks: the plan's
voice timing wins.

## T2 Punch pair

**Plan:** lead-in Inter SemiBold 42 px, then one keyword in Instrument Serif Italic 140 px, baselines aligned, 14 px
gap, centred as a group; #111111 on gray cards. Lead-in hard cut. Keyword: 6f blur-in (30 → 0) while scaling
108% → 100%, ease out. Out: 4f fade.

**Markup:**
```html
<div id="b01-t2" class="clip rc-t2" data-start="4.0333" data-duration="0.9333">
  <div class="rc-t2__row"><span class="rc-t2__lead">from the</span><span class="rc-t2__key">cops?</span></div>
</div>
<div id="b04-t2" class="clip rc-t2 rc-on-card" style="--rc-y: 300px" ...> … </div>   <!-- gray card, above the L9 grid -->
```
**JS:** `T.punchPair(tl, '#b01-t2', keywordTime, { outAt })`

**Timing:** the lead-in shows from the clip's first frame (its spoken word). The keyword is invisible until
`keywordTime`; on that frame it appears at blur 30 px / scale 1.08 and lands at frame +6 (blur 0, 100%), `power3.out`
(measured: +1f 14.5 px/1.039, +2f 5.9/1.016, +3f 1.9/1.005, +6f 0/1.000). `outAt`: the pair fades 1 → 0 over 4f,
linear (+1f 0.75 … +4f 0); end the clip at the returned time (= outAt + 4f). Omit `outAt` when a hard cut takes it.

**Geometry:** 140 px row centred on `--rc-y` (default 540); shared baseline = `--rc-y` + 47.6 px; gap exactly 14 px
between the lead-in box and the keyword box; the pair is centred on x 960. **Kit choice:** default `--rc-y` 540.

**Beats:** B1 "from the" + "cops?" (lead on "from", keyword on "cops?") · B4 "planned to take" + "18 months."
(`rc-on-card`, above the L9 calendar: set `--rc-y`) · B6 "it's" + "dull." (on the draining split screen) ·
B10 "And suddenly, it's" + "fun." (keyword on "fun", the X3 flash frame) · B12 "turn into" + "thirty." (`rc-on-card`) ·
B17 "chasing who" + "now?" (on black; then T10) · cover frame "GTA started as a" + "cop game" ("cop game" in the serif).

## T3 Year card

**Plan:** full-frame #E9E9E9. Small *In* in Instrument Serif Italic 64 px #111111 above the left edge of a year in
Inter Bold 220 px #111111, tracking −2%. Digits roll up like an odometer: each digit slides up 40 px from a mask,
8f, staggered 2f, ease out. Hold at least 1 s. Hard cut out. M6: same design both times.

**Markup:**
```html
<div id="b03-t3" class="clip rc-t3" data-start="…" data-duration="…">
  <div class="rc-t3__block"><div class="rc-t3__in">In</div>
    <div class="rc-t3__year"><span class="rc-t3__num">1995</span></div></div>
</div>
<!-- B13: month word + year, same card -->
<div class="rc-t3__year"><span class="rc-t3__month">Nov</span> <span class="rc-t3__num">1997</span></div>
```
**JS:** `const landed = T.yearCard(tl, '#b03-t3', rollStart);` (optional `{ pushUntil: t }`: slow push-in
100% → 104% of the card content, linear, rule 7 "every held shot"; off by default).

**Timing:** each digit sits in its own mask (clips 10 px under the baseline). Digit i appears (hard cut) on frame
`rollStart + 2i` already 40 px low with its bottom cut by the mask, then slides up 40 px over 8f, `power3.out`
(+1f 23.5 px, +2f 12.7, +3f 6.1 … +8f 0). Four digits: last lands at rollStart + 14f (returned). The month word is
static with the card (only digits roll); give it class `rc-t3__digit` too if it should roll first as one unit.
Hard cut out = clip end.

**Geometry:** year caps centred on `--rc-y` (default 540, baseline 620), date line centred on x 960; *In* line
(64 px) sits directly on top of the date line, left edges equal. **Kit choice:** vertical placement and the
0 px gap between the *In* line box and the year line box (40 px from *In*'s baseline to the year's cap top).

**Beats / timing advice:** B3 "In 1995", B13 "In Nov 1997" (identical design; S04/S12 tick on the first digit
move = `rollStart`). "Hold at least 1 s" is safest read as ≥ 1 s after the landing frame, so start the roll on the
card's first frame: B3 card after the X5 blinds open (≈ local f14) lands ≈ f28, holds past f58, T4 "Dundee," at
f64; B13 card on "in" (f34) lands f48, holds to ≥ f78, T1 "it ships with" at f91.

## T4 Spread words

**Plan:** Inter Medium 44 px, white, each word or phrase placed in empty space around the subject (left, centre,
right). Each piece fades in over 4f while drifting 12 px up, on its spoken word. All leave together with a 4f fade.

**Markup:**
```html
<div id="b03-t4" class="clip rc-t4" data-start="…" data-duration="…">
  <span class="rc-t4__piece rc-t4--left">Dundee,</span>
  <span class="rc-t4__piece rc-t4--right">Scotland.</span>
</div>
```
Presets (all inside title-safe; override per shot with inline `left/right/--rc-y`): `rc-t4--left` (x 96),
`rc-t4--right` (right edge 1824), `rc-t4--centre`, `rc-t4--top` (y 160), `rc-t4--bottom` (y 920), and for B9
`rc-t4--strip1/2/3` (centred in the three L3 strips: 634.67 px wide, 8 px gutters). Default `--rc-y` 540.

**JS:** `T.spreadWords(tl, '#b03-t4', t1, { times: [t1, t2, …], outAt })` (or `T.spreadIn` per piece and
`T.spreadOut` once).

**Timing:** piece starts on its frame at opacity 0 / +12 px, reaches 1 / 0 px at +4f (opacity linear, drift
`power3.out`: +1f 0.25/3.8 px, +2f 0.5/0.75 px). `outAt`: all pieces 1 → 0 over 4f, linear; end the clip at the
returned time. **Kit choice:** the eases (plan gives none).

**Beats:** B3 "Dundee," (left) on "Dundee," / "Scotland." (right) on "Scotland." over the L2 band (keep them in the
picture area 138-942 px), leave before the cut to L12 ("DMA") · B9 one phrase per strip: "They ram." / "They chase." /
"They don't let go." (`rc-t4--strip1/2/3`) · B14 "The wanted stars." (`rc-t4--left rc-t4--top`) / "The sirens."
(`rc-t4--right`, centre-right) / "The running." (`rc-t4--left rc-t4--bottom`), staying until the beat ends: no `outAt`.

## T5 Glow line

**Plan:** Instrument Serif Italic 84 px, warm glow #FFF6E0, on black. Glow = two blurred copies (24 px at 60%,
60 px at 30%). Fades in over 12f from blur 20 → 0, tracking +2% → 0. A light leak drifts behind.

**Markup** (write only the text; the helper builds the two glow copies and the leak):
```html
<div id="b16-t5" class="clip rc-t5" data-start="…" data-duration="…">
  <div class="rc-t5__text">The whole series started with a <span class="rc-t7__chip m4-chip"><img class="m4-bug" src="assets/kit/svg/motifs-bug.svg" alt="bug"></span>.</div>
</div>
```
`rc-t5` paints ink black #0A0A0A full frame ("on black"); `rc-t5--clear` makes it transparent.

**JS:** `T.glowLine(tl, '#b16-t5', lineStart, { chipAt: bugTime })`

**Timing:** from `lineStart` the line goes opacity 0 → 1 (linear) and blur 20 → 0 px, tracking 0.02 em → 0
(`power3.out`) over 12f; returns lineStart + 12f. Copies: `blur(24px)` at 0.6 and `blur(60px)` at 0.3, same text,
same tracking (the chip is replaced by a 72 × 56 spacer in the copies). `chipAt`: the T7 chip pops (see T7).
Light leak, from lineStart to the clip end (or `leakUntil`): rises to `leakPeak` 0.16 over max(12f, 24%), settles to
`leakHold` 0.1 and keeps drifting (`sine.inOut`).

**Light leak = registry block `organic-light-leak-overlay`, adapted:** same three gradient layers, blurs, screen blend
and drift paths, but retinted from the block's amber/red/gold to the palette's warm glow #FFF6E0 (the plan allows
no other colours) and turned into a continuous drift behind the line instead of the block's rise-peak-recover flash.
At the defaults the black stays black-ish (measured 20-40 / 255 behind the line). `leak: false` turns it off.
**Kit choice:** the envelope values (plan gives none).

**Beats:** B16 only: line on "The" (word 6), chip on "bug." (word 12). Keep the line ≥ 1.5 s (plan).
X7 (the RT6 light-leak dissolve into the line) belongs to the transitions area.

## T6 Giant type

**Plan:** Inter Black 300-480 px (stack long titles one word per line), white, tracking −4%, sitting behind a framed
clip (L6) so the frame overlaps the middle letters. Types on one letter every 2f, no fades. Hold 1 s.

**Markup:**
```html
<div id="b13-t6" class="clip rc-t6" data-start="…" data-duration="…" style="z-index: 5">
  <div class="rc-t6__line">GRAND</div><div class="rc-t6__line">THEFT</div><div class="rc-t6__line">AUTO</div>
</div>
<!-- the L6 framed clip goes ABOVE it (higher z-index) and carries data-layout-allow-occlusion -->
```
**JS:** `const last = T.giantType(tl, '#b13-t6', grandTime);`

**Timing:** letters appear one every 2f in reading order (spaces skipped), hard (no fades): 14 letters → first on
`grandTime`, last at +26f (returned). Hold ≥ 1 s after that.

**Geometry:** `--rc-t6-size` 400 px (plan range 300-480; **kit choice**: the largest round size that keeps all three
lines inside title-safe), `--rc-t6-pitch` 0.8 em (**kit choice**). Measured: GRAND 1404 px, THEFT 1249, AUTO 1107 wide,
ink from y 75 to 1006. The L6 frame (62% = 1190 × 670 px, centred) covers the middle letters; the outer letters and
the top of GRAND / bottom of AUTO stay visible.

**Beats:** B13 "GRAND / THEFT / AUTO" on "Grand" (word 11). Put `data-layout-allow-occlusion` on the L6 frame (or
`check` reports `text_occluded`). `check` also prints `canvas_overflow` info for the 400 px line boxes; the glyphs are
inside. **Conflict** (see end): typing + 1 s hold + the 0.8 s unboxing do not fit in the processed B13.

## T7 Inline chip

**Plan:** Inter Medium 46 px sentence with a 72 × 56 px rounded chip (12 px radius) holding an image or icon in place
of a word. Words hard cut. Chip scales 0 → 112% → 100% over 8f. The only bouncy animation.

**Markup** (the M4 bug chip; `m4-chip` and `svg/motifs-bug.svg` come from the motifs area, identical look):
```html
<div id="b02-t7" class="clip rc-t7" data-start="…" data-duration="…">
  <span class="rc-t7__w">And</span> <span class="rc-t7__w">that</span>
  <span class="rc-t7__chip m4-chip"><img class="m4-bug" src="assets/kit/svg/motifs-bug.svg" alt="bug"></span>
  <span class="rc-t7__w">saved</span> <span class="rc-t7__w">it.</span>
</div>
```
Chip: 72 × 56, radius 12, fill card ink #111111 (M4 "white on a dark chip", same as `.m4-chip`), centred on the
text's cap-height centre (y 620.3 on the T1 line). The 44 × 40 beetle is centred by motifs.css (`img.m4-bug`); any
other `<img>`/`<video>` fills the chip (`object-fit: cover`). `svg/motifs-bug-chip.svg` is the same chip as one graphic
for tools outside HyperFrames. Default line = T1's (y 620); `rc-t7--low` = y 860; or `--rc-y`.

**JS:** `T.chipSentence(tl, '#b02-t7', tAnd, { wordTimes: [tAnd, tThat, tSaved, tIt], chipAt: tBug })`
(one time per `.rc-t7__w`, default all at `at`), or `T.chipPop(tl, chipEl, tBug)` for a chip alone.

**Timing:** each word hard-cuts in on its frame. Chip: frame +0 scale 0, then 0 → 1.12 over 5f (`power3.out`),
1.12 → 1.00 over 3f (`power2.inOut`): measured 0, .661, .975, 1.091, 1.118, **1.120 (+5f)**, 1.102, 1.018, **1.000 (+8f)**.
Same frames as `RCK.motifs.bugChipPop`, so either helper gives the identical pop. `{ ease: 'back.out(1.7)' }` switches
to one 8f back.out tween (peaks at 110%, see conflicts).

**Beats:** B2 "And that [bug chip] saved it." (words 10-14: And, that, bug → chip, saved, it.) · B16 the chip inside
the T5 line (use `glowLine`'s `chipAt`).

## T8 Name / quote card

**Plan:** name in Instrument Serif 72 px, role in Inter Medium 22 px caps (tracking +15%, 60% opacity). Quote in
Instrument Serif Italic 110 px. #111111 on gray cards, white on footage. Name and role fade in over 6f. Quotes type on
at 2 characters per frame.

**Markup:**
```html
<!-- B3: on the L12 footage cards, white; the underline the Lemming walks on -->
<div id="b03-t8" class="clip rc-t8" data-start="…" data-duration="…">
  <div class="rc-t8__block">
    <div class="rc-t8__name">DMA Design<span class="rc-t8__underline"><span class="rc-t8__walker"><!-- Lemming clip here --></span></span></div>
    <div class="rc-t8__role">The studio behind Lemmings</div>
  </div>
</div>
<!-- B6: L5 gray card, quote at the right -->
<div id="b06-t8" class="clip rc-t8 rc-t8--right rc-on-card" data-start="…" data-duration="…">
  <div class="rc-t8__block">
    <div class="rc-t8__quote">“awful… too sim-y.”</div>
    <div class="rc-t8__name">Gary Penn</div>
    <div class="rc-t8__role">DMA DESIGN · GAMASUTRA, 2011</div>
  </div>
</div>
```
Role text is uppercased by CSS. Keep the quote exactly as the locked script: curly quotes, the single `…` character.

**JS:** `T.nameIn(tl, '#b06-t8', t)` (name + underline 0 → 1, role 0 → 0.6, linear 6f) ·
`T.quoteType(tl, '#b06-t8', t)` (2 characters per frame, first 2 on `t`; 19 characters → last at +9f, returned) ·
`T.walk(tl, '#b03-t8', t, { duration: 2.0 })` (the walker slot travels the whole underline, left → right, linear;
`reverse: true` for right → left).

**Geometry:** centred block (default), `rc-t8--right` (left edge x 1008, left-aligned: B6 quote at the right of the
L5 card), `rc-t8--left`. Underline: the font's own underline (post table: 0.18 em under the baseline, 0.038 em thick
= 2.7 px at 72 px), full name width, text colour (+ soft shadow on footage). Walker slot: bottom on the underline's top
edge; put the tiny Lemming clip inside it (size it yourself). **Kit choices:** quote → name gap 24 px, name → role
8 px, quote line-height 1.1.

**Beats:** B3 name card on "DMA" (word 7) over L12 · B6 card after "dull." (X2 into the L5 card), quote on
"“awful…" (word 11), then hold (the plan's deliberate B6 quote hold).

## T9 Highlight / label

**Plan:** highlight = #FFE14D box at 85% opacity, Multiply blend, behind the text; swipes left to right over 8f,
ease out, while the camera pushes in. Label = Inter Bold 40 px caps #111111 on a #FFE14D box, 12 × 20 px padding,
4 px radius; pops in over 4f.

**Markup:**
```html
<!-- inside the document layer that the L7 push-in scales, sized over the title -->
<div id="b04-hl" class="rc-t9-hl" style="left: 812px; top: 470px; width: 520px; height: 96px"></div>
<!-- label: --rc-x / --rc-y = its top-left corner -->
<div id="b15-t9" class="clip rc-t9" data-start="…" data-duration="…" style="--rc-x: 1180px; --rc-y: 700px">
  <span class="rc-t9__label">Race and Chase</span>
</div>
```
**JS:** `T.highlight(tl, '#b04-hl', tRace)` · `T.label(tl, '#b15-t9', tRace)`

**Timing:** highlight reveal with `clip-path` from the left edge, 8f `power3.out` (+1f 41%, +2f 68%, +4f 94%, +8f 100%),
size untouched. Label: 4f pop = scale 96% → 100% with a fade 0 → 1 (`power3.out`); "pop in" uses the plan's own L3
definition (4f, 96% → 100% with a fade), no overshoot (T7 is the only bouncy animation).

**Beats:** B4 highlight on "Race'n'Chase" in the R4.5 design-document scan (L7, push-in 100% → 118% is the screen's;
place the highlight inside the pushed layer) on "Race" (word 2) · B15 label "RACE AND CHASE" next to the cabinet on
"Race" (word 16).

## T10 Glitch word

**Plan:** Inter Black 160 px, white, on black. 6f of glitch (RGB split, red +6 px and blue −6 px; three horizontal
slices jumping ±20 px each frame), then settles clean. Twice in the whole edit (B8, B17). Glitch visuals only in B2,
B8, B16, B17.

**Markup** (the helper builds the clean copy, three slices and the R/G/B channel copies):
```html
<div id="b08-t10" class="clip rc-t10" data-start="…" data-duration="…"><span class="rc-t10__word">breaks.</span></div>
```
Put it over black (an ink-black element or `rc-ink` from base.css underneath).

**JS:** `T.glitch(tl, '#b08-t10', tBreaks)` · B17: `T.glitch(tl, '#b17-t10', tHit, { settle: false })` and end the
clip at the returned time (the word "breaks apart", then black).

**Timing:** before `at` the word is clean. Frames at … at+5f: the glitch layer replaces the clean word: the word split
into its red, green and blue channels, red +6 px, blue −6 px (additive: aligned they sum to the clean white), cut into
three horizontal slices (whole-pixel cuts at 61 / 99 px of the 160 px line, the cap-height thirds; keep `--rc-y` an
integer) that jump to ±20 px every frame (seeded with `seed` or the
element id; a new pattern every frame, never all three the same way). Frame at+6f: clean white again (returned).
B8: glitch 6f, clean, hold 12f, hard cut (clip end = at + 18f).

**Geometry:** 160 px line centred on `--rc-y` (default 540) and x 960. `rc-t10--key` keeps the T2 keyword face
(Instrument Serif Italic 140 px) for B17 if "now?" should break apart in the serif (see conflicts).

---

## Conflicts and decisions (plan order: locked script > beat builds > beat overview > T/L/X libraries > rest)

1. **T7 overshoot.** T library: "scales 0 → 112% → 100% over 8f"; HyperFrames note: "T7 overshoot = back.out(1.7)",
   which peaks at 110.0% (back.out(s) peak = 1 + 4s³/27(s+1)²). The T library wins: 0 → 112% (5f) → 100% (3f), exactly
   112% on frame +5, identical to `RCK.motifs.bugChipPop`. `ease: 'back.out(1.7)'` is available.
2. **T8 name face.** Fonts list: Instrument Serif Italic for "quotes and names"; the T8 row says only "Name in
   Instrument Serif 72 px" and does not say upright, so there is no conflict: names are italic by default
   (`.rc-t8__name { font-style: italic }`).
3. **One serif word per screen** (style rule 1) vs B4's T2 keyword "18 months." and the cover's "cop game" (two serif
   words each) and T5/T8 (already CONFLICTS.md C4). The beat build (B4) and the explicit cover instruction are followed.
4. **4 words on screen** (rule 5, written for T1 captions) vs B4's T2 "planned to take 18 months." (5) and the cover
   line (6). Not T1, so allowed; `checkChunks` only enforces T1.
5. **B13 timing.** Resolved by CONFLICTS.md C14 (41f title-hold gap after "Auto."): B13 is 214f, so the type-on
   (from "Grand", beat f132-160), the 1 s hold (to f190) and the 0.8 s L2 unboxing (f190-214) all fit.
6. **T3 "hold at least 1 s"**: read as ≥ 1 s after the last digit lands (the stricter reading). See T3 timing advice.
7. **B17 "now?"**: T library T10 is Inter Black 160 px; B17's "now?" is the T2 serif keyword that "breaks apart with
   T10". Default = the T10 look; `rc-t10--key` keeps the serif.
8. **Ease out.** The plan defines it as cubic-bezier(0.2, 0, 0, 1) and translates it to GSAP `power3.out` for
   HyperFrames; GSAP's power3.out is quartic (1 − (1 − t)⁴), close to but not the same curve. The kit uses `power3.out`
   as the plan instructs for HyperFrames.
9. **Light leak colours.** The registry leak is amber/red/gold; retinted to #FFF6E0 (palette rule). The RGB split's
   pure red/green/blue are the channels of the white word, not design colours (and not the siren colours).

Validated in `_demo-type` (DOM measurements of every value above and `review/` frames).
