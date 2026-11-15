# B4 Race'n'Chase — `b04-racenchase` (lane B)

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
