# B15 The proof — `b15-proof` (lane B)

Beat: edit frames 1978-2156 (65.933-71.867 s), **178f**; composition **190f** (6f handle each end; local frame = beat frame + 6).
Render: `05_GFX/renders/b15-proof.mov` (ProRes 4444, 1920x1080, 30 fps, 190 frames, `yuva444p12le`, no audio stream; opaque).
Golden rule: Master Edit Plan p.26-27 (B15 build), p.19 (overview), p.16 (X5, X6, into each beat), p.14 (L7), p.13 (T9), p.11 (T1),
p.31-32 (R15.x), p.34 (MU6), p.37 (S16), p.40 (accuracy: Race and Chase in GTA Online). STORYBOARD.md B15, CONFLICTS.md C13.

## 1. What the viewer sees

Blinds open on a dimmed GTA Online arcade with a spotlight on one cabinet while the captions ask "Don't believe me? / Open GTA Online / and buy an arcade. / One of the machines / is called"; a yellow RACE AND CHASE label pops beside the cabinet and the camera zooms through its screen into full-frame Race and Chase gameplay.

## 2. Assets

| ID | What | Status |
|---|---|---|
| R15.3 | GTA Online arcade interior with the Race and Chase cabinet (plan: R15.3 or R15.4; better: capture it in GTA Online yourself, p.27 / p.41) | **stand-in** `assets/footage/R15.3.mp4` |
| R15.1 | Race and Chase arcade gameplay (the proof shot): in the cabinet screen, then full frame | **stand-in** `assets/footage/R15.1.mp4` |
| R15.4 / R15.2 | alternate / reference (music) | not used |
| S16 | Data_Whoosh (PRISFX > Extra), -12 dBFS, peak at 0.96 s | Tesseract (cue `zoom_mid`) |
| MU6 | low-pass ~800 Hz and -6 dB from "Don't believe me?" until the label lands | Tesseract (cue `label`) |

Fonts: Inter Medium 500 (T1), Inter Bold 700 (T9 label). Kit: X5 `RCK.transitions.blindsOpen`, L7 `RCK.screens.spotPush`, T9 `RCK.type.label`, X6 `RCK.transitions.zoomFit` + `zoom`, held-shot `RCK.screens.push`. No cut-outs.

## 3. Tool and layer stack

HyperFrames only; opaque the whole beat (the composition carries its own footage, handoff rule 2; `tesseract_shots.json`: `"shots": []`).

Top to bottom:
1. T1 captions `#b15-cap-1..5` (z 60, screen space, above the slats).
2. X5 slats `#b15-x5` (z 50), f-6..8.
3. `#b15-full-wrap` > `#b15-full` full-frame R15.1 (z 3), f169-184 (pushed 100 -> 104%).
4. `#b15-world` (X6 zoom, z 2) > `#b15-l7` (L7 push) > `#b15-t9` T9 label > `#b15-dim` dim with hole > `#b15-screen` (R15.1 `#b15-pic` in the cabinet screen) > `#b15-plate` R15.3; f-6..168.

## 4. Step-by-step build (beat frames; seconds = (frame + 6) / 30)

1. **f-6..0** head handle: X5 slats shut (12 x 160 px ink black #0A0A0A); the world is under them at push 100%.
2. **f0-8 X5 in half**: `blindsOpen` at f0: slats rotate 0 -> -90 deg about their centre lines over 8f (constant 11.25 deg/frame, perspective 1000 px; coverage 100% f0, 71% f4, 19.5% f7), removed on f8. B14 plays the closing half over its last 8f.
3. **f0 T1** "Don't believe me?" hard cut in on the first syllable, above the slats.
4. **f0-160 L7 on R15.3**: dim #0A0A0A at 65% (35% shows) with a rounded hole on the cabinet `data-hole="300,120,400,840"` (radius 16, feather 20) [stand-in guess]; `spotPush` 1.00 (f0) -> 1.18 (f160), linear, about the hole centre (500, 540). The cabinet screen carries R15.1: `zoomFit('#b15-screen', {rect: [364.41, 253.73, 271.19, 152.54]}, {res: 7.08})` = laid out 1920 x 1080 at 1/7.08, so on f160 (push 118%) the picture is exactly 320 x 180 at (340, 202.2) and 1:1 at 600%.
5. **T1 chunks**, each hard cut in on its first word and out on the next chunk: f27 "Open GTA Online", f54 "and buy an arcade.", f100 "One of the machines", f129 "is called" (out f148, where T9 takes over). Offsets vs the voice: -0.06, +0.39, -0.24, +0.34, +0.45 frames.
6. **f148 T9 label** "RACE AND CHASE" pops in over 4f (scale 96 -> 100% + fade 0 -> 1, `power3.out`, lands f152), inside the pushed L7 next to the cabinet (layout top-left 730, 298; on screen ~768-1258 x 258-333 at f148).
7. **f160-168 X6 IN**: `zoom('#b15-world', f160, {screen: {rect: [340, 202.2, 320, 180]}, dir: 'in'})`: 100% -> 600% over 8f, log-space `power1.in` (100, 103, 112, 129, 157, 201, 274, 394, 600%), origin (408, 242.6) so the screen centre lands on the frame centre (measured: f166 box 880 x 492 centred 659, 379 = expected). Motion blur: per-frame media-treatment blur on the plate + screen picture, CSS blur on the dim and the label; `blurRef 540/1.18`, `blurMax 24/1.18` (see kit note). The label goes with the zoom.
8. **f168** landing frame: the screen picture is the frame (1920 x 1080), motion-blurred (fastest frame).
9. **f169-178** plain full-frame R15.1, same media time (`data-media-start 5.8333`; stand-in counter reads 00:00:05.833 on f169), push 100% -> 104% linear to the tail-handle end (f184; 102.4% on the beat's last frame). Tail handle = the shot continued.
10. Grades (media-treatment): R15.3 plate and both R15.1 videos `adjust.contrast +0.15` (game footage: punchy contrast, HUD colours untouched: no hue/saturation change); plate + screen picture also `effects.blur 0.01` with inline `--hf-color-grading-blur: 0` (X6 blur control, sharp at rest).

## 5. On-screen text

| Text (exact) | Style | Position / size | Frames |
|---|---|---|---|
| `Don't believe me?` | T1 Inter Medium 46 px, white, soft shadow | centred x 960, y 620 | f0-27 |
| `Open GTA Online` | T1 | same | f27-54 |
| `and buy an arcade.` | T1 | same | f54-100 |
| `One of the machines` | T1 (4 words, the maximum) | same | f100-129 |
| `is called` | T1 | same | f129-148 |
| `RACE AND CHASE` | T9 label: Inter Bold 40 px caps, #111111 on #FFE14D, 12 x 20 px padding, 4 px radius | next to the cabinet (pushed 116.7-118%) | f148 pop (4f) -> carried off by the zoom f160-168 |

## 6. Audio

* **S16** Data_Whoosh, -12 dBFS, peak at 0.96 s: start **f135** so the peak meets the zoom midpoint **f164** (`zoom_mid`; CONFLICTS C13: 0.96 s = 29f, the plan's "about 25f" read as the peak-alignment rule).
* **MU6**: low-pass at ~800 Hz and -6 dB from "Don't believe me?" (f0) until the label lands (`label` = **f148**, the pop completes f152), then open it again.
* No other SFX (X5 is silent). `cues.json`: `{"events": {"label": 148, "zoom_mid": 164}}`.

## 7. Mistakes to avoid

* The cabinet is "the one shot viewers can check": use real GTA Online footage where the name Race and Chase is legible (capture it in-game if possible, and confirm the name on screen; p.27, p.40).
* The screen picture must be exactly 320 x 180 px on f160 (271.19 x 152.54 at push 100%), or the 600% landing will not match the full-frame clip (or will not cover the frame).
* Keep the label inside the zoom world ("the label goes with the zoom") and the captions outside it.
* Do not let T1 cover the spotlit cabinet: on the real plate, if the cabinet sits in the centre, drop T1 to y 860 (T1 rule).
* No glitch, no siren wash in B15; slats are ink black; no fade from black.
* Never CSS-filter the footage (grade and blur only via media-treatment).

## Interpretations / conflicts

* **T1 above the X5 slats** so "Don't believe me?" reads from its first syllable on f0 while the blinds open (the kit puts the closing slats above captions in the outgoing beat). [interp]
* **L7 push**: B15 build says "slow push-in" (p.26), L7 library gives 100% -> 118% across the beat (p.14): both followed (f0 -> f160, then X6 takes over).
* **R15.1 in the cabinet screen for the whole L7 shot**: X6 needs "the screen's picture becomes the frame" (p.16); the Race and Chase gameplay is composited into the screen so the zoom lands on it. If the real cabinet screen already shows Race and Chase, the insert still guarantees the seamless landing. [interp]
* **Landing**: f168 = the world at 600% (picture = frame, motion-blurred), plain full-frame R15.1 from f169 at the same media time (kit recipe); STORYBOARD "168-178 full-frame R15.1" holds.
* **Rule 7 push on the 10f full-frame shot** (100 -> 104% to the tail-handle end) keeps momentum after the zoom. [interp]
* **Label "next to the cabinet"**: right of the cabinet, vertically centred on its screen. [interp]
* **Game grade** applied in HyperFrames because the footage is HF-owned (Tesseract grades only its own footage); contrast +0.15 is the lane's value for the plan's "punchy contrast" (p.10). [value = SUGGESTION, re-check on real footage]
* **"Don't"** keeps the locked script's straight apostrophe (the plan text and words.json both use it).
* Check warnings kept: craft `line_unread` on "Don't believe me?", "Open GTA Online" (0.90 s) and "One of the machines" (0.96 s) (voice timing governs), and on the label as "the film's last line" (0.6 s before the zoom carries it off, storyboard timing); lint `timeline_track_too_dense` (5 captions on one Studio track).

## Pending real footage (re-fit when the real clips arrive)

* **R15.3 plate** (or R15.4 / an in-game capture): pick a locked-off, ideally frontal moment with the Race and Chase cabinet fully visible, >= 5.83 s usable (local 0-175); set `source_in/source_out` in `04_Broll/broll_manifest.json`, re-run `tools/sync_footage.py hyperframes/b15-proof`.
* **Cabinet spotlight box**: `data-hole` on `#b15-dim` (now a guess: 300,120,400,840 = left third). If the camera moves, track it with `RCK.screens.spotMove` or choose a static moment.
* **Screen rect** (now a guess): `SCREEN_100` in the script = the screen picture rect at push 100% (must stay 271.19 x 152.54 px; if the real screen is smaller/larger, reframe the plate with a static zoom wrapper, as B4's `#b04-docframe`, until it is). If the screen is not frontal, use `{corners: [[x,y] TL, TR, BR, BL]}` in both `zoomFit` and `zoom` (the plain full-frame cut on f169 already handles the non-axis-aligned landing). `SCREEN_160` is derived automatically.
* **4:3 screen**: if the real cabinet screen is 4:3, letterbox the 16:9 R15.1 inside it (picture rect 16:9 within the screen) so the 600% landing equals the full-frame clip.
* **Label spot**: `--rc-x / --rc-y` on `#b15-t9` (next to the real cabinet, inside title-safe after the 118% push).
* **T1 height**: keep y 620 only if the captions stay clear of the spotlit cabinet; otherwise `rc-t1--low` (y 860).
* **R15.1 in-point**: the screen shows R15.1 media 0-5.83 s and full frame 5.83-6.33 s (f169-184); trim the real clip (manifest) so the zoom lands on a readable Race and Chase moment.
* **Grade**: re-check contrast +0.15 on the real plate and gameplay (HUD colours untouched).
* Then re-check, re-snapshot (f0, f4, f8, f100, f148, f152, f160-169), re-render.

## Kit problems worked around

* **X6 motion-blur strength with a pre-scaled world**: `RCK.transitions.zoom` sizes the per-frame blur by the zoom scale only; here everything in the world is also pushed 1.18x by L7, so the on-screen blur would be 18% too strong. Compensated locally by passing `blurRef: 540/1.18` and `blurMax: 24/1.18` (commented in `index.html`). Suggested kit option: `preScale` (an extra on-screen scale factor for the blur model).
* `zoomFit` rounds the rest size to whole pixels (271 x 153 -> 1919 x 1083 at res 7.08); the box itself is mapped exactly onto the rect (non-uniform scale 0.1413 / 0.1409), so the landing covers the frame; the picture inside differs from the full-frame clip by ~3 px horizontally on the (motion-blurred) landing frame only. Accepted, no fix.

## Verified (snapshots in `review/`, contact sheet `contact-sheet-1.jpg`)

* Handles: f-6 (slats shut, black), f178 / f183 (full-frame R15.1, push continuing).
* X5: f0 shut + T1, f2, f4 (71%), f7, f8 slats gone (L7 visible).
* T1: f0, f27, f54, f100, f129 (each on its word; check confirms the frames); f148 no text (label at 0%), f150, f152 label landed.
* X6: f160 (screen box measured 340-660 x 202-382 at push 118%), f162, f164 (mid), f166 (box 880 x 492 at 274%, centre 659, 379 = expected), f167, f168 (picture fills the frame, blurred), f169 plain clip, media time continuous (stand-in counter 00:00:05.833).
* `check --json`: 0 errors (lint 0, runtime 0, layout 0, contrast 0 errors); warnings as listed.
