# B2 The bug - `b02-bug` (beat 180f = 6.000 s; composition 192f with 6f handles)

Plan: B2 build p.20, overview p.18, into each beat p.16 ("B2 X6, footage shrinks into the CRT"), B-roll p.28-29
(R3.9, R9.1), style kit p.9-11, T1/T7 p.11-12, L8 p.14, X4/X5/X6 p.16, M4 p.17, accuracy p.40 (error box).
Storyboard: STORYBOARD.md B2. Bug beat: glitch allowed. Frames below are **beat frames** (local = beat + 6).

## 1. What the viewer sees
B1's GTA 6 shot shrinks from full frame into the screen of a 1990s CRT monitor, the CRT picture cuts to GTA 1
top-down police footage on "1995", tears into pixel blocks on "broke", freezes under a Windows 95-style
"Race'n'Chase" error box, then "And that [bug chip] saved it." builds in and the blinds close.

## 2. Assets
- B-roll: **R17.1** (B1's GTA 6 shot, continuous source time), **R3.9** (CRT plate), **R9.1** (GTA 1 police chase).
  Optional R2.3 glitch overlay not used (the X4 is built). All stand-ins for now.
- X4 still: `assets/x4/b02-old.png` (320x240 = the composition's own CRT picture at beat f101, CRT look included;
  captured by a throwaway STILL copy, see Pending).
- SFX: **S03** (Windows Error.mp4 audio + Glitch, Flicker, Text (14)). Music: **MU2**.
- Fonts: Inter Medium 46 (T1, T7). Error box: the system `sans-serif` (B2 build "system font"; Liberation Sans here).
- Graphics: L8 CRT treatment, X6 zoom, X4 tear, M4 bug chip (`assets/kit/svg/motifs-bug.svg`), error box, X5 slats
  (all kit). No cut-outs.
- Grades (media-treatment): R17.1 + R9.1 "game" contrast +0.15 (same as B1); CRT = `crtCurvature 0.16` (8% bulge),
  `scanlines 0.15` + `scanlineCount` 0.0222 (GTA 6 band, 180 px) / 0.0667 (GTA 1, 240 px) = 3 px lines,
  `chromaticAberration` 0.1563 / 0.1172 = 1 px fringe; blur control (0.01, inline 0) on the plate and both R17.1
  copies for the X6 motion blur. R3.9 plate: no grade (see Interpretations 8).

## 3. Tool and layer stack
HyperFrames builds the whole beat (opaque every frame). Tesseract adds only audio. Top to bottom:
1. `#b02-x5` X5 slats (z 60)
2. `#b02-cap-1..5` T1 captions, `#b02-t7` T7 sentence (z 40)
3. `#b02-cam` camera wrapper (z 1; slow push), inside, top to bottom:
   `#b02-err` error box > `#b02-flick` ink veil (L8 flicker on the frozen picture) > `#b02-x4` X4 tear canvas (CRT
   screen region only) > `#b02-world` X6 world: `#b02-g1` GTA 1 (CRT) > `#b02-screen` screen box laid out at 6x
   (`#b02-band`: `#b02-g6-clean` clean R17.1 > `#b02-g6-crt` CRT R17.1, over `#b02-lbx` ink letterbox) > `#b02-plate` R3.9

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b02-bug"]`)
Geometry (stand-in, see Pending): 4:3 CRT screen 320x240 at (800, 210), centre (960, 330). The 16:9 GTA 6 picture is
letterboxed inside it: band 320x180 at (800, 240) = exactly 1/6 of the frame, so at the X6 600% the band IS the full
frame (`X.zoomFit` lays the screen box out at 6x for sharpness).
| beat f | what | values / ease |
|---|---|---|
| -6..0 | world held at 600% = B1's full-frame R17.1, clean copy on top | R17.1 media-start 2.8334 (= B1's in-point + 85/30) |
| -6..26 | B1's held-shot push continued inside the picture | scale 103.72% -> 105.22%, linear (B1: 100% at its f58 -> 104% at f143) |
| 0..8 | **X6 OUT**: world 600% -> 100% about origin (960, 288) | log-space power1.out: f1 394, f2 274, f3 201, f4 157, f5 129, f6 112, f7 103, f8 100%; per-frame media-treatment blur (`X.zoom`, defocus model) |
| 3..8 | clean R17.1 copy fades 1 -> 0 so the CRT look settles as it lands | linear |
| 0..26 | CRT GTA 6 (bulge, 3 px scanlines 15%, 1 px fringe) + flicker | flicker 97-100%, one seeded value per frame (`M.crtFlicker`, seed 97) |
| 8..180 (+6) | **slow push on the plate** (camera) | 100 -> 104% at f180, linear, origin = screen centre (960, 330) |
| 26 | hard cut of the CRT picture to GTA 1 R9.1 on "1995" | 4:3 cover in the 320x240 screen; flicker seed 98 |
| 101..108 | **X4 tear** on the CRT picture only (still mode, `X.tear`, 8f, seed 101) | 16x9 blocks (20x26.7 px), jump +/-30 px (70% of non-frozen), 25% freeze, 6 px RGB split (R +6 / B -6) |
| 109..end | picture frozen on the last torn frame (`end: 'hold'`); flicker kept alive by an ink veil 0-3% | seeded (99), one value per frame |
| 109 | **error box hard pop** (its `data-start`), 640 px wide at (640, 370), 28 px text | no tween |
| 133 / 150 / 157 | **T7**: "And that" hard cut / M4 chip pops / "saved it." hard cut | chip 0 -> 112% (5f power3.out) -> 100% (3f power2.inOut): exactly 112% on f155, 100% on f158 |
| 172..180 | **X5 CLOSE** (out half of B3's transition) | 12 ink-black slats rotationY 90 -> 0, linear (11.25 deg/frame), perspective 1000; shut from f180 through the tail handle |

## 5. On-screen text
| text | style | position / size | beat frames |
|---|---|---|---|
| Because back | T1 | Inter Medium 46 px white + soft shadow, centred x 960, y 620 | 1 -> 22 |
| in 1995, | T1 | same | 22 -> 58 |
| a game about | T1 | same | 58 -> 73 |
| chasing criminals | T1 | same | 73 -> 101 |
| broke. | T1 | same | 101 -> 133 |
| And that [bug chip] saved it. | T7 | Inter Medium 46 px white + shadow on the T1 line (y 620), 72x56 chip radius 12, card ink #111111 with the white 8-bit beetle (M4), sentence laid out centred from the start (words appear in place) | "And that" 133, chip 150, "saved it." 157 -> end |
| Race'n'Chase / This program has performed an illegal operation and will be shut down. | error box | title bar card ink + white bold, body card ink on #E9E9E9, system sans 28 px, 640 px wide at (640, 370) | 109 -> end |
Caption starts vs voice: Because +0.46f, in +0.16f, a -0.14f, chasing -0.38f, broke. -0.31f, And +0.46f, bug +0.36f,
saved -0.29f: all within +/-2f.

## 6. Audio (Tesseract, from `cues.json`; plan SFX table p.35)
- **S03** = Windows Error.mp4 (PRISFX Pack, its audio track) + Glitch, Flicker, Text (14) (Botanica > Glitch &
  Flicker). The error sound starts 0.11 s into its file: start the file 3f before the tear (beat f98) so its onset
  lands on `tear` = **f101**; layer the glitch file on the tear frame f101 with +12 dB gain. -8 dBFS combined.
- `bug_chip` = **f150**: no SFX in the plan ("no pop on every caption"); provided for sync reference only.
- **MU2**: the track's first breakdown arrives around "broke" (CONFLICTS C11: it lands at edit 8.78 s, inside the
  spoken "broke", 0.64 s after its onset; flagged). X6, X5 are silent.

## 7. Mistakes to avoid
- The error box is a stylised recreation: generic, no date, no file path, no icon/buttons beyond plain window chrome.
- X4 on the CRT picture only (the tear container is clipped to the screen region), and glitch visuals only in bug
  beats: this is one of them.
- Keep R17.1 continuous with B1 (same R-ID, source time continued) or the X6 start will jump.
- The CRT screen must stay 1/6 of the frame (320x180 picture) for the 600% X6 to land exactly on B1's frame.
- T1 captions stay one line, <= 4 words; the T7 chip is the only bouncy animation in the edit.

## Interpretations / conflicts
1. **CRT screen size vs X6 600%** (X library p.16, priority 4; B2 build p.20 gives no factor; storyboard "from
   600%"): the GTA 6 picture must be 320x180 on the plate for 600% to make it exactly the frame. The 4:3 CRT screen
   is therefore 320x240 with the 16:9 picture letterboxed (as a 1990s CRT shows 16:9), and GTA 1 (4:3) fills it
   after the cut. The CRT reads small in the frame by design of the 600% (see Pending).
2. **Picture cut on "1995"** (f26) [STORYBOARD interp; plan: "the picture inside cuts to GTA 1"].
3. **Freeze on the torn frame** after the X4 [STORYBOARD interp] = kit still mode with `end: 'hold'`.
4. **T7 chip curve**: T library "0 -> 112% -> 100% over 8f" (p.12, priority 4) vs the HyperFrames note "T7
   overshoot = back.out(1.7)" (p.4, priority 5) and the storyboard's "8f back.out": T library wins (kit default,
   112% exactly on frame +5); `{ease: 'back.out(1.7)'}` is one option away.
5. **T7 words**: "And that" @133 and "saved it." @157 as chunks (storyboard); plan T7 only says "Words hard cut".
6. **Error box font/colours**: B2 build "Grey box, system font" (priority 2) vs style kit "Inter / Instrument Serif
   only" and the fixed palette: system `sans-serif` (kit), grey = card gray #E9E9E9, title bar = card ink #111111
   (Windows navy is not in the palette). Placement (plan gives none): centred on the CRT screen over its lower third,
   above the caption band.
7. **L8 flicker on the frozen picture**: the treatment's exposure flicker only acts on live video, so after the tear
   an ink-black veil 0-3% over the screen region keeps the 97-100% flicker (a solid overlay, not a filter on footage).
8. **R3.9 plate grade**: the archival grade is listed for B3-B7 and B13 (p.10), not B2, so the plate is left neutral.
   SUGGESTION: give it the archival grade if the real clip is genuine 1990s footage.
9. **X6 clean copy** (kit-recommended): an untreated R17.1 copy over the CRT copy fades out over f3-8, so f0 matches
   B1's clean frame and the CRT look settles as the picture lands. Measured B1 local 149 vs B2 local 6: mean pixel
   difference 0.74/255 (same source frame, same push).
10. **X6 motion blur** is the kit's media-treatment defocus (peaks with zoom speed), not a radial streak.
11. Optional R2.3 glitch overlay not used (plan lists it as optional; the X4 carries the glitch).
12. SUGGESTION (not built): a generic "OK" button would complete the Win95 look but adds on-screen text.

## Pending real footage
- **R3.9 (CRT plate)**: pick a frontal, static moment with the monitor screen visible; re-fit `SCREEN` / `BAND` in
  the script and the CSS boxes `#b02-g1`, `#b02-x4`, `#b02-flick` (all the screen rect), plus `#b02-err` and the camera
  push origin. For the seamless X6 the 16:9 picture must stay 320x180 (1/6 frame): if the real screen is larger,
  either reframe the plate or use `X.zoom(..., {scale: 'fill'})` (a deviation from 600%, flag it); a perspective screen
  needs `corners` (then f0 will not match B1 pixel for pixel); a moving camera would need tracking (insert is static).
  Recompute the CRT values with `RCK.motifs.crtGrading({w, h}, {srcAspect})` if the screen size changes.
- **R9.1**: in-point of a top-down police-chase moment (`#b02-g1` `data-media-start`; stand-in 0); the 4:3 cover crops
  a pillarboxed 16:9 upload to its 4:3 game picture.
- **R17.1**: B1's in-point R17_IN + 2.8334 on `#b02-g6-crt` and `#b02-g6-clean` (both identical).
- **X4 still**: re-capture after ANY change before the tear: the throwaway copy sets `const STILL = true` (no camera
  push, no tear), snapshots local 107 (`--at 3.56672`), crops `320x240+800+210` to `assets/x4/b02-old.png`:
  `sh tools/make_x4_still.sh` (keep its CROP equal to SCREEN).
- Re-check the error box position against the real monitor and the T1 line legibility over the real plate.

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `timeline_track_too_dense` (caption lane),
  `nested_structure_needs_subcomposition` (kit T7 markup), `contrast_aa_failure` on the error box text at local 181
  (the closing slats cover it: transient false positive), craft `line_unread` (voice timing; beat segment).
- Snapshots in `review/` (read): `A_*` local 0-106 (handle at 600%, every X6 frame 6-14, CRT GTA 6, the cut to GTA 1,
  captions), `B_*` local 107-191 (tear frames, error box pop, T7 words + chip 0/112/100%, slats closing, shut tail),
  `G_*` graded frames, `x4-still-source_L107_b101.png` (the still's source frame).
- Render: `cd hyperframes/b02-bug && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b02-bug.mov` (ffprobe in the lane report).
