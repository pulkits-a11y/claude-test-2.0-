# B12 Eighteen becomes thirty — `b12-thirty` (v02: beat 78f = 2.600 s; composition 90f with 6f handles)

## v02 (REVISION_v02.md; client notes 6, 10, 11, 12, 14, 15). Read this first

The v01 sections below are kept as reference; where they disagree with this section (frames, position, eases, fonts),
this section wins.

**What changed and why**
| Change | Client note / rule |
|---|---|
| **Opening animation**: the calendar (grid + counter) comes into the screen with the kit's `M.calendarIn`: rises 90 px and scales 90 -> 100% about the grid centre over 12f (easeOutExpo) while fading in over 6f (easeOutCubic), from local 5, so the beat's first frame (local 6) already shows it arriving (42% / 94.4% / +51 px); landed by local 17 | note 6 "add a opening animation where it comes into the screen" |
| **Higher, nearer the centre**: grid top y 400 (was 520; `calendarInit` `y: 400`, the kit's suggestion). Same component, size and geometry as B4 otherwise (64 px squares, 8 px gaps, 6 columns, x 748-1172, counter at its top-left). The whole group (T2 keyword cap top ~213 to the 30-square grid bottom 752) is centred ~y 482 | note 6 "move it a bit more above to the center" |
| T2 moved above the higher grid: row `--rc-y` 260 (was 390; baseline 307, "thirty." descender ~340, >= 40 px clear of the grid top even at the push + punch peak). T1 "Of course," stays low (y 860), under the grid | note 6 / rule A layout check |
| Re-timed (VO 115%): beat 78f (was 83), edit 1402-1480 (46.733-49.333 s); composition 90f, root `data-duration="3.0000000"` | note 10 |
| Captions word by word, max 2 (kit `captionPlanV2`): T1 "Of course," (Of 6, course, 10; held until "turn" as in v01) -> T2 "turn" (56) / "into thirty." (into 67, keyword **thirty.** 71, blur punch); last group exits 3f (power2.in) on the beat end | note 11, rule A |
| Coolvetica (captions, counter) | note 12 |
| Nothing linear: counter rolls easeInOutQuad (power1.inOut, was power3.out), the push easeInOutSine (was linear 100 -> 104%), T2 exit eased (was a 4f linear fade) | note 14, rule C |
| Camera: the calendar (inside `.rc-cam` wrappers; captions outside, steady) pushes 100 -> 106% across the composition (easeInOutSine) and punches 106% on "thirty" (3f easeOutExpo, back 9f easeInOutSine, nested wrapper) | note 15, rule D |
| Same overrun logic as v01: squares 19-30 from "turn" 2f apart; the counter detached from the squares and rolled on its own schedule so 30 lands on "thirty" (the kit's `calendarExtend` still ties one roll to each square) | "as before" |

**New frames (beat frames; local = beat + 6)**
| What | beat f | local |
|---|---|---|
| head handle: gray card, calendar not in yet | -6..-2 | 0..4 |
| calendarIn (12f) | -1 .. 11 | 5 .. 17 |
| T1 "Of course," | 0 (course, 4) -> 50 | 6 (10) -> 56 |
| "turn": T2 lead + first red square + first roll | 50 | 56 |
| red squares 19-30, 2f apart | 50, 52 ... 72 | 56, 58 ... 78 |
| counter roll starts (2f each, easeInOutQuad) | 50 51 52 54 55 56 57 58 59 61 62 63 | 56 57 58 60 61 62 63 64 65 67 68 69 |
| "into thirty." | 61 | 67 |
| **"thirty"**: counter lands on 30 + T2 keyword + calendar key punch (S11 hit) | **65** | **71** |
| T2 exit | 75-78 | 81-84 |
| tail handle: 30 squares, counter 30, no text | 78-84 | 84-90 |

`cues.json`: `{"events": {"thirty": 65}}` (S11's hit on "thirty" and the counter landing).
`tesseract_shots.json`: `"shots": []` (HyperFrames only, opaque). `footage.json`: no R-IDs (built graphic; R12.1 still skipped).

**Verification (v02)**
* `check --json`: 0 errors. Warnings: `nested_structure_needs_subcomposition` (kit T2 markup), craft `first_frame_empty`
  (head handle before the entrance, by design) and `line_unread` on the rolling counter digits (odometer, as v01).
* Snapshots `review/v02/` (read, `sheet_a.jpg`, `sheet_b.jpg`, `f076_keyword-landed.png` full size): the entrance
  (5, 6, 7, 8, 11, 17), every caption word (6, 10, 56, 67, 71), rolls (56, 57, 59, 62, 65, 69, 70), the landing on 71,
  the punch (73), the last square (78), the exit (81, 83), 84, 89. Max 2 words on screen; T2 and T1 clear of the
  calendar in every frame; Coolvetica.
* Render: see the bottom of this section.

---

# v01 reference (beat 83f; superseded where the v02 section above says otherwise)


Beat: edit frames 1493-1576 (49.767-52.533 s), **83f**; composition **95f** (6f handle each end; local frame = beat frame + 6).
Render: `05_GFX/renders/b12-thirty.mov` (ProRes 4444, 1920x1080, 30 fps, 95 frames, `yuva444p12le`, no audio stream; opaque).
Golden rule: Master Edit Plan p.25 (B12 build), p.19 (overview), p.15 (L9), p.17 (M3), p.11 (T1, T2), p.37 (S11), p.40 (accuracy).
STORYBOARD.md B12. Built after B4 and on its exact calendar.

## 1. What the viewer sees

The B4 calendar returns with 18 squares filled and the counter "18"; on "turn into" twelve more squares spill out in siren red while the counter rolls to 30, landing on "*thirty.*"

## 2. Assets

| ID | What | Use |
|---|---|---|
| (built graphic) | M3 / L9 calendar from `RCK.motifs` (the B4 component) | whole beat |
| R12.1 | optional clock time-lapse "faint behind the card at 10%" | **skipped while it is a stand-in** (STORYBOARD B12); markup ready, commented out in `index.html` |
| S11 | Count-up (2) (Botanica > Countdown & List), 1.4 s, hit at 1.14 s, -12 dBFS | Tesseract, hit on `thirty` = f69 |
| MU | none in B12 | - |

Fonts: Inter Medium 500 (T1), Inter SemiBold 600 (T2 lead-in), Inter Bold 700 (counter, tabular figures), Instrument Serif Italic (T2 keyword). No cut-outs. `footage.json`: `"rids": []`.

## 3. Tool and layer stack

HyperFrames only; opaque the whole beat (`tesseract_shots.json`: `"shots": []`).

Top to bottom: `#b12-cap-1` T1 (screen space) > `#b12-cam` (pushed 100 -> 104%) = `#b12-t2` T2 > `#b12-cal` M3 calendar (squares + counter) > `#b12-card` gray card #E9E9E9.

## 4. Step-by-step build (beat frames; seconds = (frame + 6) / 30)

1. `RCK.motifs.calendarInit('#b12-cal', {slots: 18, filled: 18, counter: 18, counterPos: 'left'})`: the B4 grid (748, 520; 64 px squares, 8 px gaps, 6 columns, card ink fills), 18 filled from the first frame (head handle included); counter "18" Inter Bold 120 px, card ink, right edge 32 px left of the grid, cap top on the grid top ("at its top-left").
2. **f0-53** T1 "Of course," hard cut in on "Of" (f0), out when the T2 starts (f53). Card ink, y 860 (below the grid).
3. **f53** ("turn"): T2 lead-in "turn into" hard cut. `calendarExtend(…, B(53), {to: 30, stepF: 2, grow: 'with-fill'})`: squares 19-30 appear already filled siren red #E3262E, one every 2f: f53, 55 … 75 (grid grows from 3 to 5 rows: "the grid grows to 30 squares and the 12 extra fill red", M3).
4. **f53-69 counter** (local fix, see below): 12 odometer rolls 18 -> 30, each = the kit's roll (digit strips slide up 1 em over 2f, `power3.out`), starting f53, 54, 56, 57, 58, 59, 61, 62, 63, 64, 66, 67; the tens rolls 1 -> 2 on the 19 -> 20 step and 2 -> 3 on the last; **30 lands on f69 ("thirty")**.
5. **f69** T2 keyword "thirty." blur 30 -> 0 + scale 108 -> 100% over 6f `power3.out` (lands f75, with the 30th square).
6. **f79-83** T2 4f linear fade-out (T library "Out: 4f fade"); B13 hard cuts in.
7. **Rule 7 push**, identical to B4: `#b12-cam` 100% (f0) -> 104% (f83) linear about (960, 540), same rate through both handles (99.7% at f-6, 104.3% at f89). Gray ground still.
8. Handles: head = 18 filled + counter 18, no text; tail = 30 squares, counter 30, T2 faded out.

## 5. On-screen text

| Text (exact) | Style | Position / size | Frames |
|---|---|---|---|
| `Of course,` | T1, Inter Medium 46 px, card ink #111111 (on the gray card, no shadow) | centred x 960, y 860 (`rc-t1--low`) | f0-53 |
| `turn into` | T2 lead-in, Inter SemiBold 42 px, #111111 | pair centred on x 960, row on y 390 (baseline 437.6), above the grid (same as B4) | f53-83 |
| `thirty.` | T2 keyword, Instrument Serif Italic 140 px, #111111 | same row | f69-83 (blur-in f69-75, fade f79-83) |
| `18` -> `30` | calendar counter, Inter Bold 120 px, #111111 | grid top-left, x 567-709, cap top y 519 | whole beat |

No dates, month names or years on the calendar.

## 6. Audio

S11 Count-up (2) at -12 dBFS: its hit (1.14 s into the file = 34.2f) lines up with "thirty" and the counter landing on 30 -> cue `thirty` = **f69** (file starts ~f35, during "months"). No other SFX, no MU point in B12. `cues.json`: `{"events": {"thirty": 69}}`.

## 7. Mistakes to avoid

* It must read as the SAME calendar overflowing: never re-style or move it (same component/geometry as B4: grid bbox 748,520-1171,727 at push 100% in both renders' review frames).
* No start or end dates; only the counter numbers the plan gives (18, 30).
* Red only on the 12 overrun squares (siren red is reserved: X9, CANCELLED, these squares).
* The counter must land on 30 exactly on "thirty" (S11 hit), not with the 30th square.
* Keep "Of course," off the grid (y 860) and gone before "turn into" appears.

## Interpretations / conflicts

* **B12 build internal timing** (KIT_motifs conflict 5): "on 'turn into'" + "2f apart" + counter "landing on 'thirty'" cannot all hold if the counter steps with each square (turn -> thirty = 16f, 12 squares x 2f = 24f). STORYBOARD resolution followed: squares f53-75 on "turn", counter lands on "thirty" f69, so the counter runs ~6f ahead of the squares and the grid completes 6f after the landing.
* **T1 at y 860**: T1's default y 620 falls on the calendar grid (x 748-1172, y 520-728); the T1 rule's "drop to y 860 if a face is in the centre" is applied to the calendar in the centre. [interp]
* **"Of course," holds until "turn into"** (T1: "hard cut out on the next chunk"; "the eighteen months" is not captioned in the plan's On-screen line, the 18 filled squares + counter "18" carry it).
* **Counter position "left"** (kit default) for "at its top-left": keeps B4's T2 position above the grid unchanged.
* **Grid growth "with-fill"**: each overrun square appears already red on its frame (reads as overflowing).
* **T2 out** 4f fade at the beat end (T library), as in B4/B1.
* **Rule 7 push** on the card content, identical to B4 (100 -> 104%). [interp]
* **R12.1** skipped while it is a stand-in (STORYBOARD); optional in the plan.
* Check warnings kept: craft `line_unread` on the rolling counter digits (each shown ~2f by design, odometer) and on "the film's last line" (this is one beat); lint `nested_structure_needs_subcomposition` (kit T2 markup).

## Footage used (footage pass)

* None: B12 is a built graphic (the B4 L9/M3 calendar, same component, grid and push, extended 18 -> 30). Optional R12.1 clock
  time-lapse (10% behind the card): skipped (not downloaded; optional in the plan). No substitutions.
* Kit refreshed (identical to `_kit`); no changed kit part is used here, so `05_GFX/renders/b12-thirty.mov` (95 frames,
  yuva444p12le) stays valid; `check --json`: 0 errors. Cue `thirty` = 69 (S11 hit) unchanged.

## Pending real footage

* None required (built graphic). Optional R12.1 clock time-lapse: when the real clip exists, add `"R12.1"` to `footage.json`, run `python3 tools/sync_footage.py hyperframes/b12-thirty`, uncomment the `#b12-clock` line in `index.html` (10% opacity over the gray card, under the calendar), choose a segment with steady clock motion (>= 3.2 s), re-check, re-render. Lead's call whether to use it at all (plan: optional).

## Kit problems worked around

* **`RCK.motifs.calendarExtend` couples the counter to the squares** (one 2f roll per square), so the counter cannot land on "thirty" while the squares start on "turn" 2f apart; its `landAt` option moves the squares instead. Local fix in `index.html` (commented "LOCAL FIX"): the kit's counter object is detached (`cal.counter = null`) while `calendarExtend` fills the squares, then re-attached and rolled on its own schedule with the kit's own roll mechanics (`strip.el` y = -index x 1 em, 2f `power3.out`). Suggested kit change: a `counterAt` / `counterLandAt` option (counter schedule independent of the squares).

## Verified (snapshots in `review/`, `contact-sheet-1.jpg`)

* Handles f-6 / f-1 / f83 / f88; f0 T1 "Of course,"; f52 last T1 frame; f53 T2 lead + first red square; counter f54 19, f55 20 (tens rolled), f59 23, f63 26, f65 28, f67-68 rolling 29 -> 30, **f69 30 + keyword first frame**; f72 keyword +3; f75 keyword landed + 30th square; fade f79 / f81 / f82; f83 T2 gone.
* B4 vs B12 geometry: identical grid bbox and square edges (x 748, 812, 820 … 1172) at push 100%.
* `check --json`: 0 errors (lint 0, runtime 0, layout 0, contrast 0 errors); warnings as listed.
* Render: 95 frames, opaque.
