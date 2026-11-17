# B4 Race'n'Chase — `b04-racenchase` (v05: beat 100f = 3.333 s; composition 112f with 6f handles, unchanged)

## v05 (REVISION_v05.md "Lane 5" + CLIENT OVERRIDE U1-U4; doc section 4 0:17.0-0:20.0, dead zone 2): read this first; v04 and older below are kept as reference

**Status: phase 1** (no kit v05 components yet; placeholders marked `TODO kit v05`). Not rendered. Words (local, unchanged):
It's 6, called 12, Race 22, and 29, Chase, 35, and 49, it's 52, planned 59, to 70, take 76, eighteen 81, months. 88.

| What changed | Why |
|---|---|
| **The page (0-46) is the DARK inverted page on a dark textured ground** (U4, client v03 #12; the doc's off-white paper is not followed): rebuilt from the plan's scan (`prep/race_page.py`: native 699 x 1024 JPEG, Lanczos x3, levels, light type #ECE8E1 on a charcoal #17171A paper with seeded mottling / tooth / fibres + the scan's own folds and a faint ghost of the show-through, as the v03 inverted page shows). **Shared still: `05_GFX/shared/racenchase_title_page_dark_v05.jpg`** (2097 x 3072, untilted; `_ink.png` = the type alone; `.json` = title / date / copyright boxes in page px) for B15's 10-frame flash; copied to `assets/page/` | U4; doc 17.0-18.0 + B15 66.8 |
| Full frame, tilted -4 deg, page scale 1.5 with page (1093, 540) on the frame centre (title ~527 px wide), push 100 -> 115% (6 -> 46, sine.inOut); the sheet covers the frame at every scale | doc 17.0-18.0 |
| "It's called" (6 / 12): tier A, Coolvetica Regular, white + soft shadow (54 px on screen), printed above the title box, left-aligned to "Race'n'Chase"; the printed title (with the pink sweep) is the line's key word | G10 sound-off; G3; U1 |
| **Grid (46-112)** over the 1990s DMA office (blurred, 25 %, on #0E0E10): kit M3 calendar, 18 cells 72 px / 9 px gaps, 6 x 3 at (894, 379); one cell every 2f from 47 (18th on "eighteen" 81), a tick per cell (cues) | doc 18.0-20.0 |
| "and it's planned to take" (tier A, Coolvetica 60 px) above, left-aligned; **"18" Coolvetica Italic 330 px** left of the grid (81, pops + blurs in: the beat's hero), "months." tier B 190 px under the grid's right edge (88). Block ink x 549-1371, centred | doc; U1 ("18" Coolvetica Italic); U2 |
| **Hard cut at 70** (v04 19.0, no punch-in, U3): the office behind the grid cuts from angle A (R3.8 47.6 s, a developer at his desk) to angle B (R3.7 99.8 s, a developer and the presenter at a desk, BBC 1996); grid and captions continue | doc "a hard cut or 110% punch-in at 19.0"; U3 |
| `cues.json` v05: word_pops, key_words ("18", "months."), 18 cell ticks | REVISION_v05 S, G8 |

**TODO kit v05 (phase 2)**: pink highlighter sweep (`#b04-hl`, page px 900-1288 x 360-426 over "Race'n'Chase", SCREEN blend
on the dark page, 8f from local 16 = v04 17.2, no extra push under it, U3); yellow hand-drawn circle (`#b04-circ`, page px
925-1262 x 648-754 round "March 22, 1995", 8-10f from local 28 = v04 17.6); the dark card v05 for the grid background
(grain + blurred footage; today: #0E0E10 + the office at 25 % with the media-treatment blur at its maximum, 1.0); the U2 doc pop for
"18" (kit POP3 today).

**Known / weighed**: the media-treatment blur is in source pixels (the 384 x 288 office is upscaled to 1440 x 1080 by the
sync tool): at the control's maximum (used) it reads ~30 px on screen, not the doc's ~45 px; the kit dark card may use a
low-res copy. Lint `nested_structure_needs_subcomposition` (custom lockup markup) and craft `line_unread` (beat segment) by
design. The page `<img>` carries `data-layout-allow-occlusion` (a 4 % bbox overlap false positive on the rotated page).

**Verification v05**: `check --json` 0 errors. Snapshots `review/v05/` (12 frames + `sheet.jpg`) read: dark page tilted and
pushing, "It's called" on its frames, the cut at 46, cells filling, the background cut at 70, "18" popping on 81, "months."
on 88, the tail. Not rendered.

---

# (pre-v05 title) B4 Race'n'Chase — `b04-racenchase` (v02: beat 100f = 3.333 s; composition 112f with 6f handles. v01: 108f / 120f)

## v04 (REVISION_v04.md): no B4 note

Kit refreshed to v04 (`python3 tools/new_beat.py B4 --refresh`, words.json identical, lockup markup unchanged): the dark calendar card now
carries the kit's built-in card scanlines (note 7: lines only inside dark text cards). `check --json` 0 errors; `review/v04/` (4 frames). Not rendered.

---

## v03 (REVISION_v03.md, client notes 10, 11, 12, 13, 16, 17): read this first; v02 and v01 below are kept as reference

Timing, word frames and cues unchanged (beat 100f, composition 112f, local frame = beat frame + 6). Kit refreshed to v03
(`python3 tools/new_beat.py B4 --refresh`: kit only, words.json identical).

| What changed | Why (note) |
|---|---|
| R4.5 re-synced (`python3 tools/sync_footage.py hyperframes/b04-racenchase`): the DARK (inverted) design-document title page (white letters on near-black paper), same 1700 x 2200 geometry, so the framing, the dim + hole and the highlight box are unchanged | 12 |
| T9 highlight on "Race'n'Chase": the kit's v03 dark-surface `.rc-t9-hl` (highlighter yellow at 50 %, Screen blend): a translucent yellow band on the dark page, the white letters stay white (v02's 85 % Multiply only tinted the letters on the dark page); same 8f power3.out swipe on "Race" (23) | 12 |
| Calendar card: the kit's v03 dark card (`.rc-card` = ink + charcoal lift; M3 squares light gray, empty slots a 30 % light outline); no markup change | 12 |
| Calendar camera back to v01, eased: one push 100 -> 104 % (sine.inOut, 46 -> 106, held through the tail); the v02 punch-in on the cut and the key punch on "eighteen" are deleted (and the nested `#b04-key`). The plan's L7 push 100 -> 118 % on the page is kept (eased) | 13 |
| Caption: ONE lockup (note 10, the kit's own B4 example): `planned to take [18 months.]*` ("18" = the spoken "eighteen", loose), ink centred on (960, 330) above the grid (grid top y 520): "planned" 59, "to" 70, "take" 76 small (they stay on screen), "18" 81 and "months." 88 big Coolvetica Italic, starred (pop + blur-in: the beat's one reveal, with the 18th square on 81); hard cut out on the beat end 106 (v02: planned / to take / 18 months. groups, 3f exit) | 10, 11, 16, 17 |

**v03 frames** (local): 0-6 dark page at 100 % | 6-46 L7 push 100 -> 118 % | 23-31 T9 swipe | 46 cut to the dark calendar card,
push 100 -> 104 % starts | 47 ... 81 squares fill 2f apart | 59 "planned" | 70 "to" | 76 "take" | 81 "18" pop + 18th square |
88 "months." pop | 106 beat end: caption out, calendar at 104 % | 106-112 tail.

**Verification v03**: `check --json` 0 errors (warnings: `nested_structure_needs_subcomposition` = the T9 clip and the lockup markup; craft `line_unread` "film's last line" on a beat segment). Snapshots `review/v03/` (18 frames + `sheet.jpg`; `vs_ref.jpg` = ref 3 / ref 1 next to the dark calendar card + lockup and the dark page + highlight), read: the dark page with the yellow band on "Race'n'Chase", the dark calendar card, "planned to take" staying above the big "18 months." ("18" blurred on 81 with the 18th square, "months." on 88, both sharp by 94), clear of the grid, no punch-in / key punch. Not rendered.

---

## v02 (REVISION_v02.md, client notes 10-15): read this first; the v01 notes below are kept as reference

**Beat 100f (3.333 s, v01 108f), composition 112f = 3.7333333 s** (root `data-duration`), local frame = beat frame + 6.
v02 words (local): It's 6, called 12, Race 22.5 (frame 23), and 29, Chase, 35 (ends 44.5), and 49, it's 52, planned 59,
to 70, take 76, eighteen 81, months. 88 (`tools/new_beat.py B4 --refresh`). The design-document push + T9 highlight and
the calendar fill stay as they are (REVISION B4), re-timed and eased.

| What changed | Why (note / rule) |
|---|---|
| All frames re-timed (table below); root 4.0000000 -> 3.7333333 | note 10 |
| X1 cut to the calendar at local 46 (beat f40), still in the pause after "Chase," (v01 beat f44, CONFLICTS C16): the still is on screen beat f0-40 = 1.33 s < 1.5 s | note 10, plan p.28 |
| Calendar fill starts at local 47, so the 18th square lands on 81 = the spoken "eighteen" (v01: from "and", 18th 1f before "eighteen"; 18 squares 2f apart no longer fit between "and" (49) and "eighteen" (81)) | note 10 |
| T2 "planned to take *18 months.*" -> word by word: **planned / to take / 18 months.** (59, 70/76, 81/88); lead words pop (5f expo.out), keyword words keep the blur punch (30 -> 0 px, 108 -> 100 %, 6f expo.out); the last group exits in 3f (power2.in) ending on the beat end, instead of v01's 4f linear fade. The T2 now sits outside the camera (steady), same --rc-y 390 | notes 11 + 14, rules A C D ("zoom the picture, not the caption layer") |
| Coolvetica / Coolvetica Italic (kit) | note 12 |
| L7 push 100 -> 118 % (local 6 -> 46): v01 linear -> easeInOutSine (kit `spotPush`); T9 highlight 8f power3.out (unchanged) | note 14 |
| Calendar camera: v01 `S.push(... to: 1 + 0.04 * 70 / 64)` (linear 104 %) -> **punch-in on the cut** 112 -> 100 % (10f easeOutExpo), then **push 100 -> 106 %** (local 56 -> 106, easeInOutSine), held through the tail; **key punch on "eighteen"** (nested `#b04-key`, about the grid centre (960, 624): 100 -> 106 % in 3f expo.out from 80, back over 9f sine.inOut) | notes 14 + 15, rules C D |
| R4.5 archival grade: its v01 `details.vignette 0.12` and `details.grain 0.08` set to 0 (desaturate -0.2 and the warm shadow lift stay) | rule F: the assembly adds the whole-edit grain + vignette; beats must not add their own |
| Kept: the real R4.5 title page, its framing, dim + hole, T9 box; 18 empty slots, hard 2f fills, no dates; no SFX | "don't change anything else" |

**v02 frames** (local; beat = local - 6):

| local | beat | what |
|---|---|---|
| 0-6 | -6-0 | head handle: L7 at 100 % |
| 6-46 | 0-40 | L7 push 100 -> 118 % (sine.inOut) |
| 23-31 | 17-25 | T9 highlight swipes over "Race'n'Chase" (on "Race") |
| 46 | 40 | X1 hard cut to the gray card + 18 empty slots; calendar punch-in 46-56 |
| 47 ... 81 | 41 ... 75 | squares fill 2f apart (18th on "eighteen") |
| 56-106 | 50-100 | calendar push 100 -> 106 % |
| 59 | 53 | T2 "planned" |
| 70 / 76 | 64 / 70 | T2 "to" / "take" |
| 81 / 88 | 75 / 82 | T2 keyword "18" / "months." (blur punches); key punch 80-92 |
| 103-106 | 97-100 | T2 exit (3f, power2.in), gone on the beat end |
| 106-112 | 100-106 | tail handle: full calendar at 106 %, no text |

`cues.json`: `{"events": {}}` (no SFX in B4, plan p.38). `tesseract_shots.json`: no shots (HF-owned, opaque).

**Note for B12** (another lane): B4's calendar geometry is unchanged (grid 748, 520; 64 / 8 px; 6 columns); only its
camera moves are new (v02 B12 has its own opening animation and sits higher, REVISION note 6).

**Verification v02**: `check --json` 0 errors (warnings: `nested_structure_needs_subcomposition` kit markup; craft
`line_unread` on "to take" (voice timing) and the "last line"). Snapshots `review/v02/` (22 frames + 2 sheets: handle, push,
T9 swipe, the cut, fills, every T2 word, key punch, exit, beat end, tail) read: max 2 words, words on their onsets,
Coolvetica, nothing linear, nothing cut off. Render: `05_GFX/renders/b04-racenchase.mov` = prores (4444), 1920x1080, 30 fps, **112 frames** (100 + 12),
yuva444p12le, opaque on every frame; decoded frames match the snapshots (mean diff 0.05/255).

---

Beat: edit frames 538-646 (17.933-21.533 s), **108f**; composition **120f** (6f handle each end; local frame = beat frame + 6).
Render: `05_GFX/renders/b04-racenchase.mov` (ProRes 4444, 1920x1080, 30 fps, 120 frames, `yuva444p12le`, no audio stream; opaque on every frame).
Golden rule: Master Edit Plan p.21 (B4 build), p.18 (overview), p.13-15 (T9, T2, L7, L9), p.17 (M3), p.38 (silence by design), p.40 (accuracy). STORYBOARD.md B4, CONFLICTS.md C16.

## 1. What the viewer sees

The real 1995 Race'n'Chase design-document title page, dimmed except its boxed title, pushes in while a yellow highlighter swipes across "Race'n'Chase"; hard cut to a gray card where 18 calendar squares fill under "planned to take *18 months.*"

## 2. Assets

| ID | What | File |
|---|---|---|
| R4.5 | REAL still: Race'n'Chase Game Design v1.05, title page, (c) 1995 DMA Design Ltd (manifest `source_detail`: scanned PDF linked from the plan's iGrandTheftAuto page, rendered 1700 x 2200) | `04_Broll/B04/R4.5__design-doc-1995_title-page.png` -> `assets/footage/R4.5.png` (`tools/sync_footage.py`) |
| R4.1 | optional prototype gameplay in a small frame: **not used** (the storyboard's B4 has no slot for it) | - |
| S / MU | none (B4 is silent by design: plan p.21 "Audio: no SFX", p.38) | - |

Fonts: Inter SemiBold 600 (T2 lead-in), Instrument Serif Italic (T2 keyword); kit `base.css` @font-face. Kit items: L7 (`RCK.screens.spotPush`), T9 highlight (`RCK.type.highlight`), M3/L9 calendar (`RCK.motifs.calendarFill`), T2 (`RCK.type.punchPair`), held-shot push (`RCK.screens.push`). No cut-outs.

## 3. Tool and layer stack

HyperFrames only; the whole beat is opaque (`tesseract_shots.json`: `"shots": []`). Tesseract only places the MOV on V-track at edit frame 532 (6f head handle) and owns all audio.

Top to bottom:
* f0-44 (local 0-50): `#b04-l7` (pushed 100 -> 118%) = `#b04-dim` (#0A0A0A at 65%, rounded feathered hole) > `#b04-hl` T9 highlight (#FFE14D 85%, multiply) > `#b04-doc` R4.5 page (archival media treatment) inside the static zoom wrapper `#b04-docframe`.
* f44-114 (local 50-120): `#b04-cam` (pushed 100 -> 104%) = `#b04-t2` T2 > `#b04-cal` M3 calendar; under it `#b04-card` gray card #E9E9E9 (static).

## 4. Step-by-step build (beat frames; seconds = (frame + 6) / 30 on the composition clock)

1. **Head handle f-6..-1**: the opening state held (L7 at 100%). The push may not go below 100% here: at 97.5% the 1920 x 1080 dim stopped covering the frame edges (seen in review), so the handle holds.
2. **f0-44 L7 on R4.5.** The `<img>` is frame-sized (`object-fit: cover`, `object-position: 50% 0%` = page width 1920 px, top of the page) and `#b04-docframe` zooms it statically (`scale(1.2395833)`, origin 1123.58 px 127.27 px) = 1.4 x page px, so the scanned paper fills the frame (no white PDF margin) and the boxed title's centre (page 878, 307.5) sits at (960, 400). Archival grade (plan p.10, B3-B7) via `media-treatment` on `#b04-doc`: `adjust.saturation -0.2`, `wheels.shadows {hue 35, amount 0.1, level 0.04}` (slight warm lift), `details.grain 0.08` (size 0.2, roughness 0.5), `details.vignette 0.12`. Dim: `data-hole="715,296,488,212"`, radius 16, feather 20 (L7: 35% except the target). `S.spotPush` 1.00 (f0) -> 1.18 (f44), linear, about the hole centre (959, 402).
3. **f18-26 T9 highlight** on "Race" (f18, first syllable): `clip-path` reveal left to right over 8f, `power3.out` (+1f 41%, +2f 68%, +4f 94%, +8f 100%), while the push continues. Box over the printed "Race'n'Chase" (page px 753-1004 x 263-296 + padding; screen 775-1146 x 330-392 at push 100%), inside the pushed page layer.
4. **f44 X1 hard cut** (in the pause after "Chase,", CONFLICTS C16: still on screen 44f = 1.47 s < 1.5 s) to the gray card + the M3 calendar with 18 empty slots (kit: 2 px inset outline, card ink at 35%). Grid top-left (748, 520), 64 px squares, 8 px gaps, 6 columns (L9).
5. **f46-80** `calendarFill`: squares fill hard (no tween) left to right, 2f apart, from "and" (f46); the 18th lands on f80, just before "eighteen" (f81) (STORYBOARD [interp]).
6. **f57** T2 lead-in "planned to take" hard cut on "planned".
7. **f81** T2 keyword "18 months." on "eighteen": blur 30 -> 0 px + scale 108% -> 100% over 6f, `power3.out` (lands f87).
8. **f104-108** T2 4f linear fade-out (T library "Out: 4f fade"; B4 ends on a hard cut to B5).
9. **f44-114** rule 7: `#b04-cam` (calendar + T2) pushes 100% -> 104% linear about (960, 540) across f44-108, same rate to 104.4% at the tail-handle end. The uniform gray ground stays still.
10. **Tail handle f108-113**: the closing state continued (calendar full, T2 faded out, push continuing).

## 5. On-screen text

| Text (exact) | Style | Position / size | Frames |
|---|---|---|---|
| (none added) highlight on the document's own printed title "Race'n'Chase" | T9 highlight | over the title inside the page | f18 swipe -> f44 |
| `planned to take` | T2 lead-in, Inter SemiBold 42 px, card ink #111111 | baseline-aligned with the keyword, 14 px gap, pair centred on x 960, row centred on y 390 (baseline 437.6), above the grid | f57-108 |
| `18 months.` | T2 keyword, Instrument Serif Italic 140 px, #111111 | same row | f81-108 (blur-in f81-87, fade f104-108) |

No T1 captions in B4 (the plan's On-screen line has none). No dates, month names or years on the calendar.

## 6. Audio

No SFX (plan p.21; "Silence by design: no SFX in B4-B5", p.38). Music: no MU point in B4 (it sits between MU2 "broke" and MU3 "dull"; the track's breakdown runs under it at the plan's levels). `cues.json`: `{"events": {}}` (STORYBOARD B4: Cues none).

## 7. Mistakes to avoid

* No start or end dates on the calendar ("about 18 months" only; plan p.21 / p.40).
* Keep the still under 1.5 s and always moving (44f, push 100 -> 118%); never let the push drop below 100% (the dim would uncover the frame edges).
* Show only the title page of the design document (never the robber-mode pages; plan p.39).
* Keep the highlight inside the pushed page layer so it stays on the title, and multiply (85%) so the letters stay dark.
* Do not add a counter in B4 (the counter "18" is introduced in B12).
* B12 must reuse this exact calendar: same kit component, grid (748, 520), 64/8 px, 6 columns, gray card, T2 at `--rc-y: 390px`, same push (100 -> 104% about 960, 540). Verified identical pixel geometry (grid bbox 748,520-1171,727 at push 100% in both review sets).

## Interpretations / conflicts

* **C16** (CONFLICTS.md): the cut to the calendar is at f44, not on "planned" (f57), to keep the still under 1.5 s (plan p.28: stills < 1.5 s).
* **Spotlight = both title lines** "Race'n'Chase / Game Design" (the document's boxed title) [interp of "dimmed except the title", p.21, and L7 p.14]; the T9 highlight covers only "Race'n'Chase" (On-screen line p.21).
* **The real title page also prints "Version 1.05 / March 22, 1995 / (c) 1995 DMA Design Ltd"**; it stays visible at 35% in the dimmed area. Nothing is added: it is the R4.5 scan the plan asks for (p.21, p.29). Flagged because it is a date on screen; the B4 "no dates" rule (p.21) is about the calendar.
* **Archival grade on R4.5**: the plan's 1990s/archival grade (p.10, B3-B7) is applied in HyperFrames because this still is HF-owned (Tesseract grades only its own footage, PRODUCTION_SPEC).
* **"18 months." = two serif words** vs Style rule 1 "never more than one serif word per screen" (p.10): the beat build (priority 2) italicises "18 months." as the T2 keyword (p.21), so it is followed (KIT_type conflict 3).
* **T2 out**: the T library's "Out: 4f fade" (p.11) is applied at the end of the beat (f104-108), as B1's storyboard does for its T2; B5 then hard cuts in.
* **Rule 7 push on the calendar card** (p.11): the calendar shot is 64f with constant change, but the plan asks every held shot to push 100 -> 104%; applied to calendar + T2 together (camera move), the flat ground stays still. [interp]
* **18 empty slots from the cut** (kit choice: empty slot = 2 px inset outline) so "18 squares fill in left to right" reads as a calendar being filled; the 18th square lands on f80 (STORYBOARD [interp]).
* Lint/check warnings kept on purpose: `nested_structure_needs_subcomposition` (kit T2 markup and the highlight's timed wrapper; Studio display only); craft `line_unread` on "planned to take" / "18 months." as "the film's last line" (this is one beat of the edit; the voice timing governs).

## Footage used (footage pass)

| R-ID | File | In-out | Beat f | What it shows | Link |
|---|---|---|---|---|---|
| R4.5 | `04_Broll/B04/R4.5__design-doc-1995_title-page.png` (real scan, still) | still, 44f on screen (1.47 s < 1.5 s), push 100 -> 118% | 0-44 | Race'n'Chase Game Design v1.05 title page, (c) 1995 DMA Design Ltd | plan p.29 R4.5 sources (Game Developer / iGrandTheftAuto / Engadget) |

* R4.1 (optional prototype gameplay in a small frame): not used. It is not among the downloaded originals, and the storyboard's B4
  (L7 0-44, calendar 44-108) has no slot for it without cutting the still or the calendar. SUGGESTION only, if the lead wants it.
* No substitutions. Kit refreshed (`new_beat.py B4 --refresh`, identical to `_kit`); the kit changes since the render (T8 italic
  names, X3 frame counting, X4 still capture, X6 handoff/push) touch nothing B4 uses, so `05_GFX/renders/b04-racenchase.mov`
  (120 frames, yuva444p12le) stays valid; `check --json`: 0 errors.

## Pending real footage

* R4.5 is already real; nothing pending for the picture itself.
* SUGGESTION: the scan inside the plan's PDF is only 699 x 1024 px (93 ppi JPEG); the 1700 x 2200 render is a 2.4x upscale and the frame shows it at 3.4x-4.0x (1.4 x up to 1.18 x 2.43), so the type is soft. A higher-resolution scan of the same title page (the plan's Game Developer / Engadget pages) would sharpen the push. If the file is replaced with a different size or crop: re-measure the boxed title in page px and update `#b04-docframe` (scale = wanted frame px per page px / (1920 / page width); origin so the title centre lands on 960, 400), `data-hole` and the `#b04-hl` rect, then re-check, re-snapshot, re-render.

## Kit problems worked around

None in B4 (the kit's L7, T9, T2 and M3 helpers were used as documented).

## Verified (snapshots in `review/`, contact sheets `contact-sheet-1.jpg`, `contact-sheet-2.jpg`; render frames decoded and compared)

* Handles: f-6 / f-1 (L7 held at 100%, dim covers the frame), f108 / f113 (closing state).
* L7: f0 dim 35% + hole on the title, f43 push ~118%; T9: f18 (0%), f19 (41%), f22 (94%), f26 (landed).
* X1 cut f44 (18 empty slots); calendar f46 (1st square), f69 (12), f80 (18th).
* T2: f57 lead-in, f81 keyword at blur 30 / 108%, f84, f87 landed, f104 / f106 / f107 fade, f108 gone.
* `check --json`: 0 errors (lint 0, runtime 0, layout 0, contrast 3/3 passed); warnings as listed above.
* Render: 120 frames, alpha 255 everywhere (opaque beat), frames 0/28/49/50/93/119 match the snapshots.
