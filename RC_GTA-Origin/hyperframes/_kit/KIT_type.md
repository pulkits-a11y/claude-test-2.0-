# KIT_type: typography T1-T10

The RC_GTA-Origin kit's type area: `type.css`, `type.js` (exposes `RCK.type`) and this file.
Source of truth: Master Edit Plan p.9-13 ("Style kit" and "Typography styles (T1-T10)"), the rotation line on p.13 and the
beat builds on p.19-27. Every number below comes from those pages unless it is marked **kit choice** (the plan gives no
value) or **conflict** (see "Conflicts and decisions" at the end).

Demo of every item, built exactly as a beat would: `hyperframes/_demo-type/` (`index.html`, proof frames in `review/`).

## v04 (REVISION_v04.md notes 3, 6, 7, 15): glow flicker, scanlines inside the dark text cards. Read this first

Additions on top of v03 (everything in the v03 section below still applies). Proof: `hyperframes/_demo-v03/` section K
(f910-1150): `review/snap/f0938_K1_flick-f0.png` .. `f0955_K1_steady.png` (lockup keyword), `f0977_K2_*` .. `f0995_K2_steady.png`
(T3 "It's 1995"), `f1038_K3_*` .. `f1060_K3_steady.png` (T3 "Nov 1997"); `review/check.json` 0 errors.

### `RCK.type.glowFlicker(tl, target, at, opts)`: "glow flicker on 1995" (B2, B3), "Nov 1997" (B13)

The text shows on its frame with a soft white glow that flickers like a neon tube catching: one hard step per frame
between four levels (`F` flare: glow 6 / 34 px at 95 / 70%; `o` on: 4 / 20 px at 65 / 40%; `h` half: text at 55%
opacity, faint glow; `-` off: text at 15% opacity, no glow; v05: opacity, not brightness, so a light word never turns
dark on bright footage; on a lockup word it drives the inner `.rc-lw__fx` span, layered on the v05 entry) for `frames` (10) frames, then an eased settle
(4f power2.out) to the steady soft glow (= `--glow-filter`, 2 / 10 px at 40 / 22%) that stays. It drives one CSS
`filter` on the element (brightness() dims the text and its text-shadow; two white drop-shadows = the glow, drawn after
the digit masks, so it works on the T3 year). Seeded per element (id + text), deterministic.
```js
// a lockup keyword (do NOT star it: the pop + blur also drives filter); markup from T.lockups(w, ['Because back in [1995,]'], ...)
T.lockupsWire(tl);
T.glowFlicker(tl, '#b02-lk-2 .rc-lk__row--key .rc-lw', W[3].comp_t);     // the word hard-cuts in on its frame, then flickers
// the T3 year line (digits roll in AND flicker; "It's" / "In" keep their steady glow)
T.yearCard(tl, '#b03-t3', W.y1995, { pushUntil: L(60) });
T.glowFlicker(tl, '#b03-t3 .rc-t3__year', W.y1995, { frames: 11 });
// B13 "Nov 1997": write <span class="rc-t3__num">Nov 1997</span>, flicker from "November"
T.glowFlicker(tl, '#b13-t3 .rc-t3__year', W.November, { seed: 15 });
// exact pattern instead of the seeded one (one letter per frame: F o h -)
T.glowFlicker(tl, el, at, { pattern: 'F-hh-oFo-o' });
```
`opts`: `frames` (10; 8-12), `pattern`, `seed`, `settleF` (4), `settleEase` (power2.out), `before` (`'off'` default = the
dim off state before `at`; `'steady'`; `null` = untouched), `color` (`'255, 255, 255'`). Returns the time the glow is
steady. `T.glowPattern(n, seed)` previews a pattern; `T.GLOW_STATES` holds the four levels + steady. Seeded patterns: frame
0 is visible (F or h), the last flicker frame is o, at least 2 offs, never two offs in a row, offs thin out towards the
end. Measured (`_demo-v03` K1, "1995," onset f938): f938 flare, f939 off, f940-941 half, f942 off, f943-947 on/flare,
settle f948-951, steady from f952; K2 the year rolls (2f per digit) while it flickers; "It's" unchanged. T3 change: the steady glow moved
from `.rc-t3__block` to `.rc-t3__in` and `.rc-t3__year` (same look) so the year can flicker alone.

### Scanlines only inside the dark text cards (note 7: no whole-edit CRT lines)

Built into the dark text surfaces, static, nothing to add in a beat: `.rc-card`, `.rc-t3`, `.rc-l5__ground`, a full-frame
`.rc-ink.rc-full` black screen (B8, B16, B17 grounds) and `.rc-t5`. Texture `--card-scan` (base.css): 9 px period (ref 3:
2.7 px of 275 = 9 px at 1080p), a 3 px line at 20% black with 1.5 px soft edges. Measured on the K2 card (x 960):
23 / 18 brightness, period 9 px. Not on letterbox bars (`.rc-ink` without `rc-full`), L12, footage or lockups on footage.
```html
<div id="b03-t3" class="clip rc-t3 rc-noscan" ...>                 <!-- opt out: a card with B-roll behind it -->
<div id="b03-t3" class="clip rc-t3 rc-t3--clear rc-noscan" ...>    <!-- B3 note 4: no card at all, the 1990s B-roll behind the year -->
<div id="b13-scan" class="clip rc-scan" data-start="..." data-duration="..." style="z-index: 60"></div>   <!-- optional: the lines OVER the card's text too (ref 3) -->
```

---

## v03 (REVISION_v03.md notes 11, 12, 16, 17): caption lockups, dark cards. Read this first

v03 overrides v02 where they conflict; everything else in the v02 / v01 sections below still applies. Proof:
`hyperframes/_demo-v03/` (built by `tools/gen_demo.cjs` from this kit, the way a beat uses it): `review/snap/` (74 frames,
`f<frame>_<what>.png`) + `review/sheet_A..H.jpg`, `review/lockups.txt` (the plans), `review/check.json` (`check`: 0
errors). Section A (f0-170) = lockups over footage, B = dark year card, C/D = dark calendar cards, E = dark quote card,
F = stars glitch-in, G = B13 card + title, H = T9 on a dark page + the dark error box, I = the L4 grid with ink tiles,
J = the descender guard ("[Why] does", "And that [bug]* saved it.", "[Dundee,] Scotland.").
Rebuild: `cd hyperframes/_demo-v03 && rm -r assets/kit && cp -r ../_kit assets/kit && node tools/gen_demo.cjs && bash tools/snap.sh`.

### What changed in type.js / type.css / base.css

| Item | v02 | v03 |
|---|---|---|
| Captions (all T1 / T2 / T4 / T5 voice captions) | groups of max 2 words, every word pops (`captionPlanV2` + `captionHTMLV2` + `captionPops`) | **lockups** like ref 1, centred (960, 540): small Coolvetica words + at most ONE big Coolvetica Italic keyword; 1-7 words per lockup (guideline); every word appears on its own onset frame with NO animation (hard cut); only starred words pop + blur in; a lockup hard-cuts to the next (`lockups` + `lockupsWire`) |
| Sizes | T1 46 px, T2 42 / 140 px | small 60 px, keyword 190 px, solo line 64 px (76 px on a dark text card, `card: true`) |
| Text glow | `--text-shadow` (dark, 12 px) | `--text-glow` (base.css): white bloom 2 / 9 / 22 px + the dark shadow; on footage and on cards |
| Cards (note 12) | `#E9E9E9` card, `#111111` ink, no shadow | `.rc-card`, `.rc-t3`, `.rc-l5__ground`, `.rc-l12__ground` = `--card-surface` (ink #0A0A0A + a charcoal radial lift to #202020 in the middle, ref 3); `.rc-on-card` / `rc-t3` text = white + glow |
| Palette variables | `--card-gray` #E9E9E9, `--card-ink` #111111 | `--card-gray` = the card background (dark), `--card-ink` = text on a card (white); the plan colours stay as `--light-gray` #E9E9E9 and `--dark-ink` #111111; new `--card-bg`, `--card-lift`, `--card-surface`, `--card-text`, `--text-glow`, `--glow-filter` |
| T3 year card | gray card, #111111 digits | dark card, white digits; glow = `filter: var(--glow-filter)` on `.rc-t3__block` (a text-shadow would be cut by the digit masks). Write the B3 text in the `In` slot: `<div class="rc-t3__in">It's</div>` |
| T8 quote card | #111111 on gray, type-on | white + glow on the dark L5 ground; B6 v03: `T.wordPops` (each quote word pops + blurs in on its spoken frame); the underline glows |
| T9 highlight | `#FFE14D` 85% multiply (behind the ink on a white page) | 50% **screen**: on a dark page it is a yellow band and the light text stays light (`rc-t9-hl--light` = the v02 multiply for a light page) |
| T9 label / T7 chip | text / chip `--card-ink` | `--dark-ink` #111111 (unchanged look) |

### Caption lockups v3: `RCK.type.lockups` + `RCK.type.lockupsWire`

**Spec syntax** (one string per lockup; or one string with ` / ` between lockups):

| Write | Means |
|---|---|
| `to their [PhDs] at Stanford,` | `[...]` = the keyword (big Coolvetica Italic; one per lockup, may hold several words). Words before it = lead (small, above, left-aligned to the keyword), after it = tail (small, below, right-aligned to the keyword) |
| `to their [PhDs]* at Stanford,` | `]*` = every keyword word pops + blurs in |
| `[Grand* Theft* Auto.*]` | `word*` = that word pops + blurs in (any word, small or big) |
| `so they approached` | no brackets = one centred small line (ref 3) |
| `it ships with \| a new name:` | `\|` = a forced line break among the small words |
| `—` and other punctuation-only tokens | join the word before them (they are not words in words.json) |

**Path A (generate in Node, paste the HTML; one timed element per lockup):**
```bash
cd hyperframes/b15-proof && node -e "
globalThis.window = globalThis; require('./assets/kit/type.js'); const T = RCK.type;
const w = require('./words.json').words;
const plan = T.lockupPlan(w, [\"Don't believe me?\", 'Open [GTA Online]* and buy an arcade.', 'One of the [machines] is called'], { from: 0 });
console.log(T.lockups(plan, null, { idPrefix: 'b15-lk', z: 40, track: 20 }));
console.error(T.lockupReport(plan));"
```
prints (one element per lockup; sizes and row offsets are computed from Coolvetica's metrics):
```html
<div id="b15-lk-2" class="clip rc-lk" data-start="1.0333" data-duration="2.3000" data-track-index="20" style="--rc-lk-c: 136.68px; z-index: 40"><div class="rc-lk__box"><div class="rc-lk__row rc-lk__row--lead" style="font-size: 60px; line-height: 60px; height: 60px"><span class="rc-lw" data-rc-f="31">Open</span></div><div class="rc-lk__row rc-lk__row--key" style="font-size: 190px; line-height: 190px; height: 190px; margin-top: -20.39px"><span class="rc-lw rc-lw--pop" data-rc-f="39">GTA</span> <span class="rc-lw rc-lw--pop" data-rc-f="45">Online</span></div><div class="rc-lk__row rc-lk__row--tail" style="font-size: 60px; line-height: 60px; height: 60px; margin-top: -19.97px"><span class="rc-lw" data-rc-f="57">and</span> ... <span class="rc-lw" data-rc-f="75">arcade.</span></div></div></div>
```
and the report (check every lockup against the voice):
```
2 f31-100 (69f)  [lead] Open@31 | [key +8px] GTA@39* Online@45* | [tail] and@57 buy@63 an@69 arcade.@75  | key 190 px, 867 x 250 px ink
```
In the beat's script, ONE call after all the lockup markup (it wires every `.rc-lk`):
```js
const T = RCK.type;
T.lockupsWire(tl);            // plain words: hard cut on data-rc-f; .rc-lw--pop words: pop + blur in
```
More copy-paste calls (`L(n)` = local frame n in seconds):
```js
// B4 on the dark calendar card: "planned to take" (small, stays) above "18 months." (big); loose: "18" = "eighteen"
T.lockups(w, ['planned to take [18 months.]'], { from: 7, loose: true, y: 330, idPrefix: 'b04-lk', z: 40 })
// B13: the "Until finally," card (ref 3 size) and the title, each word popping on its own frame
T.lockups(w, ['Until finally,'], { from: 0, card: true, idPrefix: 'b13-lk', z: 40 })
T.lockups(w, ['it ships with | a new name:', '[Grand* Theft* Auto.*]'], { from: 5, idPrefix: 'b13-title', z: 40 })
// B14: lockup under the six hero stars (y = the ink centre)
T.lockups(w, ['The [wanted stars.]*', 'The [sirens.]', 'The [running.]'], { from: 9, y: 800, idPrefix: 'b14-lk', z: 40 })
```
**Options** (`lockupPlan` and `lockups` take the same; `lockups(words, specs, opts)` builds the plan itself, or pass a
plan: `lockups(plan, null, opts)`): `from` (index of the first word in words.json), `end` (s: where the last lockup
hard-cuts out; default the next word's comp_t, else the last word's comp_end_t), `start` (s: an earlier start for the
first lockup's clip, e.g. a card's first frame; its words still appear on their own frames), `loose`, `y` (ink centre,
default 540), `smallSize` (60), `keySize` (190), `soloSize` (64), `card` (solo 76), `gap` (17 px), `clear` (8 px), `wrap` (1.15),
`maxWidth` (1728), and for the HTML `idPrefix` ('lk'), `z`, `track`, `cls` (extra classes), `inline` (extra CSS).
`lockupsWire(tl, scope, opts)`: scope = selector / element(s) (default every `.rc-lk`), `opts.pop` overrides the pop
preset (`{ frames: 6, blur: 20, scale: 0.92, ease: 'expo.out', lead: 0 }`). Plan: `{lockups: [{index, spec, text,
toks: [{text, role: lead | key | tail | solo, pop, frame, i, voiceT}], startFrame, endFrame, frames, startAttr,
durAttr, layout: {rows, box, sizes}}], next, endFrame, warnings}`.

**Layout rules** (kit choices, tuned against ref 1 at 1920 x 1080; ref 1 measured: small words 60 px Coolvetica
equivalent ("to their" 183 px wide in the ref, 192 px here), lead baseline -> keyword cap top 16.7 px, keyword baseline
-> tail cap top 16.7 px, lockup ink centred on the frame):
* Rows: lead (small, `align-self: flex-start` = left edge of the keyword row), key (Coolvetica Italic 190 px, centred),
  tail (small, `flex-end` = right edge of the keyword row), solo (centred). The box shrink-wraps the widest row and is
  centred on x 960; its ink (first cap top .. last baseline) is centred on `--rc-y` (540) through `--rc-lk-c`.
* Vertical: every row has line-height = its size (baseline 0.867 em, cap top 0.195 em below the row top); small -> key
  and key -> small: 17 px from baseline to the next cap top; small -> small: baseline pitch 1.12 em.
* **Descender guard (fix, after the B1-B4 report)**: a row's highest glyph actually present must clear the previous
  row's deepest glyph actually present by `clear` = 8 px (per-glyph ink tops / bottoms of both Coolvetica files,
  `T.cvExtent(text, italic)`: g j p q y Q 0.233 em = 44 px at 190, comma / semicolon 0.156 em = 30 px, ( ) 0.143 em;
  tops: caps 0.664, ascenders 0.672, digits / round tops 0.686-0.688, quotes 0.73). When it is needed the row moves
  down (the report shows it: `[tail +35px]`) and the ink centre (`--rc-lk-c`) is recomputed, so the lockup stays
  centred. Rows without descenders keep the tight ref 1 spacing. Measured (`_demo-v03` section J, white ink > 235):
  "[Why] does" tail +35 px, gap 9 px between the y and "does"; "And that [bug]* saved it." tail +35 px, gap 10 px;
  "[Dundee,] Scotland." tail +21 px, gap 9 px; all three ink-centred at y 539.5-540. A lead with descenders moves the
  keyword down too ("planned to take" / "Open": key +8 px). **The offsets are written inline by `lockups()`: re-run the
  generator after syncing the kit; old lockup HTML keeps the old spacing.**
* Fit (measured with the kit's Coolvetica width table, kerning included, `T.cvWidth(text, px)`; within ~1% of Chrome):
  the keyword shrinks to stay inside the 1728 px title-safe width (warning); a lead / tail row wider than 1.15 x the
  keyword (min 420 px) breaks onto 2+ balanced lines (fewest lines, smallest widest line); a solo line wider than 1400 px
  breaks the same way; `|` forces a break. Warnings for > 7 words, < 6 frames on screen, ink outside 54-1026.
* Measured in `_demo-v03` (snapshots, white ink bbox, descender guard on): "Open / GTA Online / and buy an arcade."
  x 539-1386 (centre 962.5), y 414-678 (cap-baseline centre 540); "One of the / machines / is called" x 591-1336,
  y 418-660 (centre 539); "planned to take / 18 months." at y 330: x 540-1380, y 234-429; "Race and Chase." (key only)
  x 321-1602, y 473-606.
* Timing: a lockup's clip = its first word's frame .. the next lockup's first word's frame (hard cut both ends). Inside
  it, each word is hidden until its own frame (round(comp_t x 30)), then shown (0.5f step tween = a cut). Starred words:
  full opacity on their own frame at blur 20 px / scale 92%, settling in 6f expo.out (f k: blur 20, f k+1: 6.3 px / 97.5%,
  f k+2: 2 px / 99.2%, f k+6: sharp); `_demo-v03` f39-41 ("GTA"), f145-147 ("Race"), f645-647 ("Grand").
* Which words to star (note 11 "only for certain captions where you deem fit"): a beat's one or two key reveals (a
  name, a number, a title), never every lockup.

**Word pops on other text** (B6: "the quote words pop + blur in on their spoken frames"):
```js
T.wordPops(tl, '#b06-t8 .rc-t8__quote', null);                 // the v02 markup already has <span class="rc-w" data-rc-f>
T.wordPops(tl, '#b06-t8 .rc-t8__quote', [W.awful, W.too, W.simy], { loose: true });   // or split plain text, one time per word
T.nameIn(tl, '#b06-t8', L(150));                                 // name + role fade (unchanged)
```
(do not also call `T.quoteType` on that quote; `opts.hard: true` = plain hard cuts instead of the pop.)

**Migration from v02** (one Node call per beat):
* `captionPlanV2` + `captionHTMLV2` (any style t1 / t2 / t4 / t5) -> `T.lockups(words, specs, { from, end, loose, idPrefix, z })`:
  same words.json, same `from`; rewrite the plan's chunk string as lockups (merge the v02 2-word groups back into
  phrases of 1-7 words, put the stressed content word in `[ ]`, star only the chosen reveals). Delete the old
  `.rc-cap` clips and paste the lockup HTML in their place (any z / track).
* `T.captionPops(tl)` -> `T.lockupsWire(tl)` (keep `captionPops` only while v02 clips remain; the two never touch each
  other's elements). Remove `onCard`, `low`, `y: 860` placements: lockups are centred (pass `y` only to clear a motif).
* `wordsV2` / `punchPairV2` / `spreadWordsV2` / `glowLineV2` on v01 markup: delete those clips and generate lockups.
  The T5 line (B16 "The whole series started with a bug.") becomes a lockup over a black `rc-ink` clip (lockups have
  no T5 glow copies or leak).
* T10 glitch word (`T.glitch`): unchanged. T6 giant type: not used in v03 (B13 is the lockup title).
* No `rc-on-card` on lockups: they are white + glow everywhere (cards are dark).

### Dark cards in a beat (nothing to change in the markup)

`sync_kit.py` brings the new CSS; every `.rc-card`, `.rc-t3`, `.rc-l5__ground`, `.rc-l12__ground` and `.m3-cal`
turns dark, `rc-on-card` text turns white + glow. Check what a beat drew itself: inline `#E9E9E9` / `#111111` (none
found in the beats' markup today, only comments), SVG fills, and `rc-t9-hl` on a page that is still light
(add `rc-t9-hl--light`). Measured in `_demo-v03` (f430, empty card): centre #202020, edge middles #111111, corners
#0C0C0C (ref 3, which carries the finish's vignette and scanlines: centre about #292425, corners #050303).

---

## v02 (REVISION_v02.md): captions word by word, nothing linear, Coolvetica. Read this first

Everything after this section is the v01 reference (markup, geometry, plan values) and still applies, except where this
section says otherwise: fonts are Coolvetica, nothing is linear any more, and every caption that transcribes the voice is
word by word with max 2 words on screen. Proof: `hyperframes/_demo-v02/` (built by its `tools/gen_demo.cjs` from this kit,
the way a beat uses it); `review/snap/` + `review/sheet_*.jpg` = snapshots, `review/measure_v02.json` = measurements
(`node tools/measure_v02.cjs`), `review/check.json` = `check` (0 errors).

### What changed in type.js / type.css

| Item | v01 | v02 |
|---|---|---|
| T1 captions | one clip per plan chunk (1-4 words), hard cut, no animation | groups of max 2 words; each word pops on its own frame (`captionPlanV2` + `captionHTMLV2` + `captionPops`) |
| T2 pair | lead-in hard cut, keyword 6f blur punch (power3.out), 4f linear fade | split into groups of max 2 words (`from / the cops?`); lead words pop, the keyword keeps its blur punch (30 -> 0 px, 108 -> 100%, 6f, expo.out); optional 2-3f eased exit of the last group |
| T4 spread words | each piece fades in 4f (linear) + drifts 12 px; all pieces stay | pieces split into groups of max 2 words that replace each other; words pop (opacity, 12 px rise, 90 -> 100%, 5f expo.out); two one-word pieces can share a group (B3 `Dundee, + Scotland.`) |
| T5 glow line | the whole line fades in over 12f (linear opacity) | one line per group; each word blurs in (14 -> 0 px expo.out, opacity power2.out, 6f) in the text and both glow copies; the leak is unchanged (sine eases) |
| T6 type-on | a letter every 2f (constant rate) | same total length ((n-1) x 2f), start times placed on easeOutQuad (GSAP stagger ease `power1.out`): GRAND THEFT AUTO = +0 4 7 11 14 16 18 20 22 24 25 25 26 26f |
| T8 quote type-on | 2 characters a frame (constant) | same total length (floor((n-1)/2) f), eased the same way (18 characters: +0 1 2 3 3 4 5 5 6 6 7 7 7 8 8 8 8 8f) |
| T8 name / role fade | 6f linear | 6f power2.out (easeOutCubic) |
| T8 walk | linear | sine.inOut |
| T3 push (`pushUntil`) | 100 -> 104% linear | sine.inOut; `pushTo` (1.04), `pushEase` |
| T2 / T4 v01 helpers (`punchPair`, `spreadIn/Out/Words`) | linear fades | fade in power2.out, fade out power2.in (they still work, but break rule A: switch to the v2 calls) |
| T5 v01 `glowLine` | linear opacity | power2.out (still works; v02 uses `glowLineV2` / style t5) |
| hard cuts (word / letter appears, glitch jumps) | 0.5f tween, ease `none` | 0.5f tween, ease `steps(1)`: still a cut between two frames (rule C exempts cuts); no `ease: 'none'` is left in the kit |
| `captionPlan` (v01) | | still works and prints a reminder to use `captionPlanV2` (`{ v01: true }` silences it) |
| `opts.ease` on every helper | GSAP names | GSAP or easings.net names (`'easeOutExpo'`); `'none'` / `'linear'` are refused (console warning, the helper's default is used) |
| fonts | Inter / Instrument Serif | Coolvetica / Coolvetica Italic; the layout constants are re-derived (Fonts, below) |

### Captions v2 (rule A)

Every word that transcribes the voice (T1, T2 pairs, T4 phrases, the T5 line; T10 is one word and needs nothing) appears on
its own first syllable, frame = round(comp_t x 30) (<= 0.5f from the voice), never more than 2 words on screen. A group
holds 1-2 words; it is replaced by a hard cut when the next group's first word starts. An eased exit (2-3f, power2.in:
opacity 1 -> 0, scale 1 -> 0.96, blur 0 -> 4 px, ending exactly on the cut) is optional, by default only on the LAST group
of a run (before the next style takes over); `exitAll: true` gives every group one.

**Chunk syntax** (the plan's "On screen" line): `/` = a plan chunk boundary (a group never crosses it); `|` = force a group
break inside a chunk (`a | police officer`); `+` = keep two phrases in ONE group (T4: two pieces on screen together,
`Dundee, + Scotland.`). A chunk of 3+ words without `|` is split automatically by `RCK.type.groupWords`.

**Automatic grouping** (kit heuristic, tuned on the locked script): it chooses the breaks with the lowest total cost:
after punctuation 0; before an article / preposition / conjunction 0.5; before a verb form (-ed, -ing) or an adverb 1.5;
after a conjunction or an auxiliary ("it's", "don't") 3; after an article or a preposition 6; inside a two-word content
unit ("police | officer", "drive | straight" is cheap: an adverb follows) 8; an object pronoun stays with its verb
("following you") 8; name parts ("GTA 6", "GTA Online") 9; plus 1 per one-word group, 4 for a group ending on an article,
and groups that would be on screen for less than 2 frames are avoided. It reproduces the client's examples
"a / police officer" and "have you / running": a short function word goes with the word after it, unless that would split
a two-word unit, then it stands alone. Always read `captionReport(plan)` and override with `|` where a group reads badly.

**Per-beat groups** (computed by the kit from `timing/beat_map.json` v02; pass exactly the chunk string, `from` = index
of the first word in the beat's words.json; frames = composition frames of each group's first word):

| Beat | Style | Chunk string (`from`) | Groups on screen | First frames |
|---|---|---|---|---|
| B1 | T1 | `Why does / every GTA, / even GTA 6, / have you running` (0) | Why does / every GTA, / even / GTA 6, / have you / running | 7, 26, 55, 69, 93, 105 |
| B1 | T2 | `from the cops?` (10) | from / the cops? | 114, 120 |
| B2 | T1 | `Because back / in 1995, / a game about / chasing criminals / broke.` (0) | Because back / in 1995, / a game / about / chasing criminals / broke. | 7, 27, 61, 69, 75, 101 |
| B2 | T1 | `And that bug saved it.` (10; note 8: the word, no chip) | And / that bug / saved it. | 131, 142, 154 |
| B3 | T4 | `Dundee, + Scotland.` (5; place `['left', 'right']`) | Dundee, Scotland. (one group, two pieces) | 61 |
| B3 | T1 / new layout | `DMA Design, / the studio behind Lemmings,` (7) | DMA Design, / the studio / behind Lemmings, | 103, 135, 148 |
| B3 | T1 | `starts a new game.` (13) ("Here's how." has no caption, rule B) | starts / a / new game. | 175, 185, 188 |
| B4 | T2 | `planned to take 18 months.` (7, `loose: true`; `key: 2`) | planned / to take / 18 months. | 59, 70, 81 |
| B5 | T1 | `In it, / you play / a police officer / chasing criminals.` (0) | In it, / you play / a / police officer / chasing criminals. | 7, 20, 31, 33, 53 |
| B6 | T1 | `But there's / a problem:` (0) | But there's / a problem: | 6, 17 |
| B6 | T2 | `it's dull.` (4) | it's dull. | 38 |
| B7 | T1 | `So the people / above the team / keep trying / to shut it down.` (0) | So / the people / above / the team / keep trying / to shut / it down. | 6, 9, 22, 31, 41, 58, 68 |
| B8 | T1 | `Then, something` (0) (then T10 `breaks.`) | Then, something | 7 |
| B9 | T1 | `The police cars / stop following you / and start trying / to drive straight / through you.` (0) | The / police cars / stop / following you / and start / trying / to drive / straight / through you. | 7, 11, 27, 34, 55, 67, 75, 86, 101 |
| B9 | T4 | `They ram. / They chase. / They don't let go.` (14; place `['strip1', 'strip2', 'strip3']`) | They ram. / They chase. / They don't / let go. | 126, 149, 174, 191 |
| B10 | T2 | `And suddenly, it's fun.` (0) | And suddenly, / it's fun. | 7, 34 |
| B11 | T1 | `So the team / flips the whole game. / You're not the cop / anymore. / Now you're the one / being chased.` (0) | So / the team / flips / the / whole game. / You're not / the cop / anymore. / Now you're / the one / being chased. | 6, 9, 23, 33, 42, 65, 76, 83, 103, 117, 128 |
| B12 | T1 | `Of course,` (0) | Of course, | 6 |
| B12 | T2 | `turn into thirty.` (5) | turn / into thirty. | 56, 67 |
| B13 | T1 | `Until finally,` (0) | Until finally, | 7 |
| B13 | T1 | `it ships with / a new name:` (5) | it ships / with / a / new name: | 86, 97, 104, 107 |
| B14 | T1 | `And every GTA since / is built around / that chase.` (0) | And / every GTA / since / is built / around / that chase. | 7, 15, 32, 39, 53, 65 |
| B14 | T4 | `The wanted stars. / The sirens. / The running.` (9; place `['left top', 'right', 'left bottom']`) | The / wanted stars. / The sirens. / The running. | 97, 102, 132, 159 |
| B15 | T1 | `Don't believe me? / Open GTA Online / and buy an arcade. / One of the machines / is called` (0) | Don't / believe me? / Open / GTA Online / and buy / an arcade. / One of / the machines / is called | 6, 11, 31, 39, 57, 69, 100, 108, 127 |
| B16 | T1 | `So that's why / you're always running.` (0) | So that's / why / you're always / running. | 7, 18, 20, 36 |
| B16 | T5 | `The whole series started with a bug.` (6; note 8: the word) | The / whole series / started with / a bug. | 57, 61, 80, 100 |
| B17 | T1 | `And GTA 6? / It opens with / Lucia already caught. / So who's` (0) | And / GTA 6? / It opens / with / Lucia / already caught. / So who's | 7, 13, 42, 54, 60, 68, 103 |
| B17 | T2 | `chasing who now?` (11) (then T10 on "now?") | chasing who / now? | 115, 135 |

Short groups the voice forces (report warnings): B5 "a" 2f, B16 "why" 2f, B11 "So" / B7 "So" 3f. `check` will also print
`line_unread` craft warnings for 1-word groups; the voice timing wins (same as v01).

**Path A, generate the HTML in Node** (recommended: one timed element per group, Studio shows each on the captions track):
```bash
cd hyperframes/b01-hook && node -e "
globalThis.window = globalThis; require('./assets/kit/type.js'); const T = RCK.type;
const w = require('./words.json').words;
const plan = T.captionPlanV2(w, 'Why does / every GTA, / even GTA 6, / have you running', { from: 0 });
console.log(T.captionHTMLV2(plan, { idPrefix: 'b01-cap', z: 40, track: 20 }));
console.error(T.captionReport(plan));"
```
It prints one element per group, each word with its frame:
```html
<div id="b01-cap-1" class="clip rc-t1 rc-cap" data-start="0.2333" data-duration="0.6333" data-track-index="20" style="z-index: 40"><span class="rc-g"><span class="rc-w" data-rc-f="7">Why</span> <span class="rc-w" data-rc-f="15">does</span></span></div>
```
and in the beat's script, ONE call after all the caption markup (it animates every `.rc-cap`):
```js
const T = RCK.type;
T.captionPops(tl);
```
The other styles, same two steps (`L(n)` = local frame n in seconds):
```js
// T2 (key = how many words at the end are keyword words, default 1; the last group exits in 3f, eased)
T.captionHTMLV2(T.captionPlanV2(w, 'from the cops?', { from: 10, end: L(149), exitF: 3 }), { style: 't2', idPrefix: 'b01-t2', z: 40 })
// B4 on the gray card: "18" for "eighteen" needs loose
T.captionHTMLV2(T.captionPlanV2(w, 'planned to take 18 months.', { from: 7, loose: true }), { style: 't2', idPrefix: 'b04-t2', key: 2, onCard: true, y: 300 })
// T4 (place = one placement per phrase: left / right / centre / top / bottom / strip1-3, or rc- classes; pieceStyle = inline CSS per phrase)
T.captionHTMLV2(T.captionPlanV2(w, 'The wanted stars. / The sirens. / The running.', { from: 9 }), { style: 't4', idPrefix: 'b14-t4', place: ['left top', 'right', 'left bottom'] })
T.captionHTMLV2(T.captionPlanV2(w, 'Dundee, + Scotland.', { from: 5, end: L(103) }), { style: 't4', idPrefix: 'b03-t4', place: ['left', 'right'] })
// T5: ONE clip (black + leak), one line per group inside it; clipStart lets the black start before the first word
T.captionHTMLV2(T.captionPlanV2(w, 'The whole series started with a bug.', { from: 6 }), { style: 't5', id: 'b16-t5', clipStart: L(50) })
```
For T5 leak options call `T.captionPops(tl, '#b16-t5', { leakFrom: L(50), leakPeak: 0.16 })` BEFORE the global
`T.captionPops(tl)` (a processed clip is skipped by later calls). `captionHTMLV2` options: `style` t1 | t2 | t4 | t5,
`idPrefix`, `id` (t5), `z`, `track`, `low` (T1 y 860), `onCard`, `y` (--rc-y px), `cls`, `inline`, `exitF`, `exitAll`,
`key` (t2), `place` / `pieceStyle` (t4), `clipStart` / `clipEnd` (t5). `captionPlanV2` options: `from`, `end` (s; default
the next word's comp_t, else the last word's comp_end_t), `start` (s, an earlier clip start for the first group; its words
still pop on their own frames), `loose`, `exitF`, `max` (2). The plan: `{groups: [{text, words: [{text, i, frame, voiceT,
offsetFrames}], startFrame, endFrame, frames, startAttr, durAttr}], next, endFrame, warnings}`.

**Path B, convert v01 markup at runtime** (fastest switch: keep the beat's v01 caption clips, replace the old helper call;
each clip keeps its window, its groups are stacked in place and shown one after the other):
```js
// T1 chunk clips (any number, reading order = DOM order); words: one time per word, or words.json entries (spell-checked)
T.wordsV2(tl, '#b01-cap-1, #b01-cap-2, #b01-cap-3, #b01-cap-4', [W.Why, W.does, W.every, W.GTA_1, W.even, W.GTA_2, W.six, W.have, W.you, W.running]);
T.punchPairV2(tl, '#b01-t2', [W.from, W.the, W.cops], { exitF: 3 });     // was T.punchPair(tl, '#b01-t2', W.cops, { outAt })
T.spreadWordsV2(tl, '#b14-t4', [W.The1, W.wanted, W.stars, W.The2, W.sirens, W.The3, W.running]);   // was T.spreadWords
T.glowLineV2(tl, '#b16-t5', [W.The, W.whole, W.series, W.started, W.with, W.a, W.bug]);              // was T.glowLine; write the word "bug"
```
`opts`: `from` (index into a words.json array), `loose`, `end` (s), `exitF` (last group), `exitAll`, `join` (T4: two
neighbouring one-word pieces share a group; default true), `pop` (preset overrides), T5 leak options. A `|` written in the
v01 text forces a break and is removed.

**Word pops** (`RCK.type.POP`, kit choices inside rule A's "4-5f opacity 0 -> 1 + scale 0.86 -> 1 + small rise"; `lead` =
frames the pop starts before the onset, so the onset frame already shows the word):

| Style | frames | lead | from | ease | measured (B1 "does", onset f15) |
|---|---|---|---|---|---|
| T1 | 5 | 1 | opacity 0, scale 0.86, y +8 px | expo.out | f14 hidden, f15 75% / 96.5% / +2.0 px, f16 94% / 99.2%, f17 99%, f19 100% |
| T2 lead | 5 | 1 | opacity 0, scale 0.86, y +6 px | expo.out | as T1 |
| T2 keyword | 6 | 0 | full opacity on its frame, blur 30 px, scale 1.08 | expo.out | f125 blur 30 / 108%, f126 9.5 px / 102.6%, f127 2.9 px, f128 0.7 px, f131 sharp |
| T4 | 5 | 1 | opacity 0, scale 0.9, y +12 px | expo.out | |
| T5 | 6 | 1 | opacity 0 (power2.out), blur 14 px (expo.out) | | text and both glow copies together |

`T.captionPops(tl, scope, { pop: { t1: { ease: 'back.out(1.7)', scale: 0.8 } } })` overrides a preset.
Measured in the demo (`review/measure_v02.json` `ruleA`): 50 words, every frame of the 36 s demo has at most 2 caption
words visible, and all 50 words are first visible exactly on their onset frame.

**Migration from v01 `captionPlan`** (one Node line per beat): replace `captionPlan` -> `captionPlanV2` and `captionHTML`
-> `captionHTMLV2` (same `words`, same chunk string, same `from` / `end` / `loose`), paste the new HTML over the old T1
clips, add `T.captionPops(tl)` once. T2 / T4 / T5 markup: either regenerate it with `style: 't2' | 't4' | 't5'` or keep it
and swap `punchPair` / `spreadWords` / `glowLine` for `punchPairV2` / `spreadWordsV2` / `glowLineV2` with one time per word.
T7 sentences become plain T1 captions ("bug" is a word, note 8). T10 (`glitch`) is unchanged.

### Easing (rule C): `RCK.ease`

Defined by type.js (every beat loads it). `RCK.ease.<easings.net name>` = the GSAP ease; `RCK.ease.css.<name>` = the
easings.net CSS bezier; `RCK.ease.fn(nameOrGsap)` = the reference curve (Node too); `RCK.ease.name('expo.out')` =
'easeOutExpo'; `RCK.ease.get(e)` / any helper's `opts.ease` accept both spellings and refuse `none` / `linear`.

| easings.net | GSAP | CSS cubic-bezier | kit use (REVISION_v02 table) |
|---|---|---|---|
| easeInOutSine | `sine.inOut` | 0.37, 0, 0.63, 1 | pushes / zoom-outs across a held shot, drifts, floats, leak drift |
| easeOutExpo | `expo.out` | 0.16, 1, 0.3, 1 | word pops, T2 keyword punch, punch-ins settling, zoom-through in-half, calendar opening |
| easeOutQuart | `power3.out` | 0.25, 1, 0.5, 1 | T3 digit roll, T9, X2 drift, X5 open, stars, arrow |
| easeOutBack | `back.out(1.70158)` | 0.34, 1.56, 0.64, 1 | optional pops (`opts.pop`, chip `ease`) |
| easeInExpo | `expo.in` | 0.7, 0, 0.84, 0 | zoom-through out-half |
| easeInQuart | `power3.in` | 0.5, 0, 0.75, 0 | X5 close, arrow erase |
| easeOutCubic / easeInCubic | `power2.out` / `power2.in` | 0.33, 1, 0.68, 1 / 0.32, 0, 0.67, 0 | fades in / out (T8 name, L3 cell, L4 tile, X7, caption exits) |
| easeInOutCubic | `power2.inOut` | 0.65, 0, 0.35, 1 | moves between two rests (L11 drain, flip, rate ramp) |
| easeInQuad / easeOutQuad | `power1.in` / `power1.out` | 0.11, 0, 0.5, 0 / 0.5, 1, 0.89, 1 | X3 flash ramp / fade; type-on timing (stagger ease power1.out) |
| easeInOutQuad | `power1.inOut` | 0.45, 0, 0.55, 1 | counter rolls (M3) |
| every other easings.net name | `sine.in/out`, `power1-4.*`, `expo.*`, `circ.*`, `back.*`, `elastic.*(1, 0.3 / 0.45)`, `bounce.*` | `RCK.ease.css` (no bezier for elastic / bounce) | |

All GSAP curves equal the easings.net formulas to 4 decimals except `expo`: GSAP 3.15's expo is corrected to end exactly
at 0 and 1 and differs from easings.net's 2^(10x-10) by up to 0.008 of the range mid-curve (measured, invisible on screen).

Measured in the demo (`node tools/measure_v02.cjs`): the demo timeline has 238 tweens = 106 eased + 89 hard cuts (0.5f
step tweens) + 43 sets, 0 linear; an audit timeline calling all 49 kit helpers (type, transitions, screens, motifs, camera)
has 0 linear tweens; 184 tween properties sampled at 25 / 50 / 75 % render their curve within 0.0011 and are never closer
than 0.10 (10% of the move) to a straight line.

### Fonts (Coolvetica), checked in the render Chrome

* base.css: `--sans` = Coolvetica (Regular file), `--serif` = "Coolvetica Italic" (Italic file), every weight 100-900 maps
  to the one face, `font-synthesis: none`.
* All four `@font-face` rules load (`document.fonts`), `document.fonts.check` is true for both families, and the text is
  not a fallback (canvas: "Hamburgefonts 1995?" at 120 px is 1062 px wide in Coolvetica, 1187 px in the fallback, the
  pixels differ).
* No faux bold: weights 400 / 600 / 900 render pixel-identical glyphs (the faces cover 100-900, and synthesis is off).
  No faux oblique: `italic` on `--sans`, `italic` on `--serif` and "Coolvetica Italic" upright all render the same pixels
  = the real Italic file (italicAngle -10 deg); the Regular renders differently. Computed `font-synthesis: none` on the
  caption words.
* Snapshots through `hyperframes snapshot` (`_demo-v02/review/snap`) show Coolvetica / Coolvetica Italic in T1, T2, T3,
  T5, T6, T8, T9, T10.
* Metrics the kit uses (`RCK.type.METRICS`, em): line box ascent 0.967 / descent 0.233 (hhea, used by Chrome; Coolvetica
  has no USE_TYPO_METRICS), H 0.672, digits and round tops 0.688, x-height 0.5, underline 0.133 under the baseline, 0.02
  thick, italic angle -10 deg. In a line box of height LH the baseline sits at LH/2 + 0.367 em and the cap centre at
  LH/2 + 0.031 em (Inter's caps were centred), so every "centred on --rc-y" style moved up by 0.031 em.

| Style | Constant | v01 (Inter / Instrument Serif) | v02 (Coolvetica) | Measured in `_demo-v02` |
|---|---|---|---|---|
| T1 | line top | --rc-y - 28 px | - 28 px - 0.031 em | cap centre y 619.1 (want 620) |
| T2 | row top; lead-only rows | --rc-y - 70 px | - 74.34 px; a keyword-size zero-width `::after` strut | keyword cap centre 539.6; shared baseline --rc-y + 47.0 for pairs AND lead-only groups ("from", "to take"); gap 14 px; centred on 960 |
| T3 | block top; "In"; mask; tracking | --rc-y - 110 - 64; 0; 200 px (baseline 190); -2% | --rc-y - 115 - 64; "In" `top: 8px`; 200 px (baseline 190.7); -1% | digits centred 540.3; In baseline to digit top 40.7 px (v01 40); mask clips 9 px under the baseline |
| T4 | piece top | --rc-y - 28 px | - 28 px - 0.031 em | |
| T5 | line top; --rc-cap | --rc-y - 50 px; 0.72 | - 52.6 px; 0.672 | |
| T6 | size; pitch; tracking; line lift | 400 px; 0.8; -4%; 0 | 420 px; 0.79; -1%; `top: -0.0395 x size` per line | ink y 55.7-1022.3 inside title-safe 54-1026; GRAND 1270, THEFT 1133, AUTO 973 px wide, x 322-1593 |
| T7 | line top; --rc-cap | - 28 px; 0.7275 | - 28 px - 0.031 em; 0.672 | (no chips in v02) |
| T8 | underline; quote size | top 1.17 em, 0.038 em thick; 110 px | top 1.15 em, max(2 px, 0.02 em); `var(--rc-t8-quote, 110px)` | "“awful… too sim-y.”" = 911 px at 110 px, wider than the 816 px `rc-t8--right` column: write `“awful…<br>too sim-y.”` (2 lines, 496 x 242 px, demo) or set `--rc-t8-quote: 96px` (one line, ~795 px) |
| T9 | label padding | 12 / 20 px | 11 / 20 / 13 px | caps centre 732.6 vs box centre 732 |
| T10 | line top; slice cuts | --rc-y - 80; 61 / 99 px | --rc-y - 85; 67 / 103 px (`rc-t10--key`: - 74; 59 / 90) | cap centre 540.2; caps 31.5-139 px of the line, cut in thirds |
| M3 counter, M2 label | Inter metrics | Coolvetica metrics (motifs.js) | counter digit top 399.97 on the grid top 400 |

**Looks that changed noticeably in Coolvetica** (all intended by note 12, flagged so nobody is surprised):
* T6: Coolvetica has one weight, lighter and much narrower than Inter Black: GRAND 1270 px (v01 1404). THEFT (1133 px) is
  now fully hidden behind the 62% L6 frame (1190 px); in v01 its outer letters peeked out. The stack reads as GRAND
  above and AUTO below the frame.
* T3 and T6 tracking relaxed (-2% -> -1%, -4% -> -1%): at the plan's values Coolvetica's digits / letters touch
  ("99", R-A-N merge).
* T2: lead-in and keyword are one family now (Coolvetica / Coolvetica Italic): the keyword is set apart by size and slant
  only, no serif contrast. T3 "In", T5, T8 quote / name, L6 label: the serif roles are a slanted sans.
* T8 quote: two lines (or 96 px) at the right of the L5 card.
* T10 and the CANCELLED stamp: no Black weight, the glitch word reads lighter.
* The B2 error box keeps the system sans (Liberation Sans, bold exists, so `font-synthesis: none` does not affect it).

---

# v01 reference (still valid where the v02 section above does not override it)

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
  Italic for T8 names too (Style kit > Fonts: "quotes and names"). **v02: all of these are Coolvetica (sans roles) and
  Coolvetica Italic (serif roles), one weight; see "v02 > Fonts".**
* **Eases.** "Ease out" = GSAP `power3.out` (the plan's HyperFrames translation). Where the plan names no ease the
  kit uses: fades linear (`none`), moves `power3.out` (marked **kit choice** below). **v02: nothing is linear: fades
  are power2.out / power2.in, type-ons eased, hard cuts are steps(1) cuts; see "v02 > What changed".**
* `RCK.type.<helper>(tl, target, atSeconds, opts) -> endSeconds`. `target` is a selector or an Element.
  Helpers set start states with `gsap.set` when they are called; call each helper once per element.

## API summary

v02 adds (see the v02 section): `captionPlanV2`, `captionHTMLV2`, `captionReport`, `groupWords`, `captionPops`,
`wordsV2`, `punchPairV2`, `spreadWordsV2`, `glowLineV2`, `typeOnOffsets`, `ease`, `METRICS`, `POP`, and `RCK.ease`.

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

**v02: T1 is word by word, max 2 words (v02 > Captions v2); the v01 chunk mechanics below are kept for reference.**

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
