# B2 The bug - `b02-bug` (beat 180f = 6.000 s; composition 192f with 6f handles)

Plan: B2 build p.20, overview p.18, into each beat p.16 ("B2 X6, footage shrinks into the CRT"), B-roll p.28-29
(R3.9, R9.1; real footage + substitutions below), style kit p.9-11, T1/T7 p.11-12, L8 p.14, X4/X5/X6 p.16, M4 p.17, accuracy p.40 (error box).
Storyboard: STORYBOARD.md B2. Bug beat: glitch allowed. Frames below are **beat frames** (local = beat + 6).

## 1. What the viewer sees
B1's GTA 6 shot shrinks from full frame into the screen of a 1990s CRT monitor, the CRT picture cuts to GTA 1
top-down police footage on "1995", tears into pixel blocks on "broke", freezes under a Windows 95-style
"Race'n'Chase" error box, then "And that [bug chip] saved it." builds in and the blinds close.

## 2. Assets
- B-roll (real, see "Footage used"): **R1.2** (B1's GTA 6 shot, continuous source time; SUBSTITUTE for R17.1),
  **R3.7** (the CRT plate; SUBSTITUTE for R3.9, which is unusable), **R9.1** (GTA 1 police chase).
  Optional R2.3 glitch overlay not used (the X4 is built).
- X4 still: `assets/x4/b02-old.png` (537x406 = the composition's own GTA 1 CRT picture at beat f101, CRT look included,
  unwarped; captured by a throwaway STILL copy: `sh tools/make_x4_still.sh`).
- SFX: **S03** (Windows Error.mp4 audio + Glitch, Flicker, Text (14)). Music: **MU2**.
- Fonts: Inter Medium 46 (T1, T7). Error box: the system `sans-serif` (B2 build "system font"; Liberation Sans here).
- Graphics: L8 CRT treatment, X6 zoom, X4 tear, M4 bug chip (`assets/kit/svg/motifs-bug.svg`), error box, X5 slats
  (all kit). No cut-outs.
- Grades (media-treatment): R1.2 + R9.1 "game" contrast +0.15 (same as B1); CRT = `crtCurvature 0.16` (8% bulge),
  `scanlines 0.15` + `scanlineCount` 0.1126 (GTA 6 band, 302 px) / 0.1896 (GTA 1, 406 px) = 3 px lines,
  `chromaticAberration` 0.0931 / 0.0693 = 1 px fringe (`RCK.motifs.crtGrading` for the real screen); blur control
  (0.01, inline 0) on the plate and both GTA 6 copies for the X6 motion blur. R3.7 plate: no grade.

## 3. Tool and layer stack
HyperFrames builds the whole beat (opaque every frame). Tesseract adds only audio. Top to bottom:
1. `#b02-x5` X5 slats (z 60)
2. `#b02-cap-1..5` T1 captions, `#b02-t7` T7 sentence (z 40)
3. `#b02-cam` camera wrapper (z 1; slow push), inside, top to bottom:
   `#b02-err` error box > `#b02-flick` ink veil (L8 flicker on the frozen picture) > `#b02-x4` X4 tear canvas (CRT
   screen region only) > `#b02-world` X6 world: `#b02-g1` GTA 1 (CRT) > `#b02-screen` screen box laid out at 6x
   (`#b02-band`: `#b02-g6-clean` clean R1.2 > `#b02-g6-crt` CRT R1.2, over `#b02-lbx` ink letterbox) > `#b02-plate-fit`
   (R3.7 plate, 4:3 picture rotated +6.5 deg, scaled 149.97%); `#b02-hand` (z 2) = the straight full-frame R1.2 hand-off copy,
   local 0-6; `#b02-pin` (corner-pinned screen box: X4 tear + flicker veil)

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b02-bug"]`)
Geometry (real plate R3.7): the CRT glass is the quad TL (286.6, 196.4) TR (838.2, 217.7) BR (818.6, 601.9) BL
(296.7, 624.0), centre (560, 410), ~537 x 406 px (measured on the BBC frame, mapped through the plate transform). The
16:9 GTA 6 picture is letterboxed in it: band quad TL (287.9, 254.1) TR (835.5, 269.3) BR (821.0, 555.0) BL (295.5,
572.0). Screen boxes are corner-pinned with `X.zoomFit(..., {corners})` (GTA 6 box laid out at 3.5754x so the band is
1920 x 1080 layout px; GTA 1 box and the X4/flicker box at 1x, 537 x 406). The glass is ~537 px wide (not 320), so the
X6 runs at the band's exact cover scale (`scale: 'fill'`, ~3.7x) instead of 600%, and a perspective screen is not
axis-aligned when zoomed, so the first frame is the straight hand-off copy (`handoff: '#b02-g6-hand'`).
| beat f | what | values / ease |
|---|---|---|
| -6..0 | hand-off copy = B1's full-frame R1.2 shot (straight, B1's push continued) over the zoom world held at 'fill' | R1.2 media-start 2.8334 (= B1's in-point + 85/30; source 11.033 s) |
| -6..26 | B1's held-shot push continued inside the picture | scale 103.72% -> 105.22%, linear (B1: 100% at its f58 -> 104% at f143) |
| 0..8 | **X6 OUT**: hand-off copy hides from f1; world 'fill' (~370%) -> 100% about the band's zoom origin | log-space power1.out (kit `X.zoom`); per-frame media-treatment blur (`X.zoom`, defocus model) |
| 3..8 | clean R1.2 copy fades 1 -> 0 so the CRT look settles as it lands | linear |
| 0..26 | CRT GTA 6 (bulge, 3 px scanlines 15%, 1 px fringe) + flicker | flicker 97-100%, one seeded value per frame (`M.crtFlicker`, seed 97) |
| 8..180 (+6) | **slow push on the plate** (camera) | 100 -> 104% at f180, linear, origin = screen centre (560, 410) |
| 26 | hard cut of the CRT picture to GTA 1 R9.1 on "1995" | 16:9 picture covered into the 537x406 pinned screen; flicker seed 98 |
| 101..108 | **X4 tear** on the CRT picture only (still mode, `X.tear`, 8f, seed 101) | 16x9 blocks (20x26.7 px), jump +/-30 px (70% of non-frozen), 25% freeze, 6 px RGB split (R +6 / B -6) |
| 109..end | picture frozen on the last torn frame (`end: 'hold'`); flicker kept alive by an ink veil 0-3% | seeded (99), one value per frame |
| 109 | **error box hard pop** (its `data-start`), 640 px wide at (240, 395) = centred on the screen, 28 px text | no tween |
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
| Race'n'Chase / This program has performed an illegal operation and will be shut down. | error box | title bar card ink + white bold, body card ink on #E9E9E9, system sans 28 px, 640 px wide at (240, 395) | 109 -> end |
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
- Keep the GTA 6 shot continuous with B1 (same R-ID R1.2, same window in-point 8.2 s, media-start 2.8334) or the X6
  start will jump.
- If the plate transform or the screen quad changes, re-run `sh tools/make_x4_still.sh` (the X4 still must be the
  current picture).
- T1 captions stay one line, <= 4 words; the T7 chip is the only bouncy animation in the edit.

## Interpretations / conflicts
1. **X6 factor** (X library p.16 "100% -> 600%", priority 4; B2 build p.20 gives no factor): the real CRT glass on the
   plate is ~537 x 406 px, so the GTA 6 band covers the frame at ~370%, not 600%; the zoom runs at the exact cover
   scale (`scale: 'fill'`) so the picture IS the frame at the start (600% would crop B1's frame 1.6x and jump).
   DEVIATION from the library's number, flagged. The 16:9 picture is letterboxed in the 4:3 CRT (as a 1990s CRT shows
   16:9); GTA 1 fills the screen after the cut.
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
8. **Plate grade**: the archival grade is listed for B3-B7 and B13 (p.10), not B2, so the R3.7 plate is left neutral.
   SUGGESTION: give it the archival grade if the real clip is genuine 1990s footage.
9. **X6 clean copy** (kit-recommended): an untreated R1.2 copy over the CRT copy fades out over f3-8, so f0 matches
   B1's clean frame and the CRT look settles as the picture lands. Measured B1 local 149 vs B2 local 6: mean pixel
   difference 0.74/255 (same source frame, same push).
10. **X6 motion blur** is the kit's media-treatment defocus (peaks with zoom speed), not a radial streak.
11. Optional R2.3 glitch overlay not used (plan lists it as optional; the X4 carries the glitch).
12. SUGGESTION (not built): a generic "OK" button would complete the Win95 look but adds on-screen text.

## Footage used
| R-ID | file | in-out (s, original) | what it shows | link |
|---|---|---|---|---|
| R1.2 | `04_Broll/_originals/B01/R1.2__Grand Theft Auto VI - Features Trailer ｜ PS5 Games [8L0CzL2V72c].mp4` | 11.03-12.10 (window 8.2-12.4, shared with b01-hook) | official GTA 6 trailer: the police truck flipping after the shooter fires at it (B1's full-frame shot continued) | https://www.youtube.com/watch?v=8L0CzL2V72c&t=11 |
| R3.7 | `04_Broll/_originals/B03/R3.7__GRAND THEFT AUTO 1996 Making Of ... BBC Archive [7vWSi44ZTSw].mp4` | 60.4-66.8 | BBC 1996: static over-the-shoulder shot of a DMA developer at a beige 1990s CRT monitor and keyboard (the plate; its own screen content is fully covered by the composited picture). Crop 1440:1080:240:0 | https://www.youtube.com/watch?v=7vWSi44ZTSw&t=60 |
| R9.1 | `04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4` | 126.0-128.5 (window 126.0-131.6; frozen on the torn frame from f101) | GTA 1 top-down: a white police car with lights right on the player's red car's tail (crop 736:414:59:40 removes the black borders) | https://www.youtube.com/watch?v=HX8infRFBTc&t=126 |

## Substitutions
- SUBSTITUTE (Rule 5): R1.2 Grand Theft Auto VI - Features Trailer | PS5 Games [8L0CzL2V72c] @ 00:11-00:12 for R17.1
  (missing: Trailer 1 not downloaded). B2's X6 must continue B1's GTA 6 shot, which is R1.2 (official PlayStation
  upload; B1 cell 6 used it for the missing R17.3/R17.1, see b01-hook BEAT_NOTES).
- SUBSTITUTE (Rule 5): R3.7 GRAND THEFT AUTO 1996 Making Of - BBC Archive [7vWSi44ZTSw] @ 01:00-01:07 for R3.9
  (unusable: the R3.9 stock clip carries a burned-in "TVDATA.TV" watermark across the middle of the frame, is 492x360,
  and shows no frontal screen: the foreground monitor faces away and the only visible CRT is ~35 px wide in the
  background). R3.7 is a plan-listed clip (B3) with a real 1990s CRT seen almost frontally from a locked-off camera.
  Its BBC corner logo is framed out by the plate transform. The GTA picture covers the monitor's own screen content.

## Pending / blocking
- Nothing blocking. If R17.1 (Trailer 1) is uploaded later, B1 cell 6 + B2 can switch together (same in-point rule).
- Known: R9.1 carries the uploader's faint "Sakura240" watermark (lower left of the game picture); inside the CRT it
  is small and under the scanlines. A tighter crop would lose the police car behind the player.

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `timeline_track_too_dense` (caption lane),
  `nested_structure_needs_subcomposition` (kit T7 markup), `contrast_aa_failure` on the error box text at local 181
  (the closing slats cover it: transient false positive), craft `line_unread` (voice timing; beat segment).
- Snapshots in `review/` (read): frames at local 0, 6, 7, 9, 11, 14, 25, 32, 60, 106, 110, 116, 140, 158, 182, 191 (real
  footage: hand-off, X6 frames, CRT GTA 6, the cut to GTA 1, tear, error box, T7, slats); earlier stand-in notes:
  captions), `B_*` local 107-191 (tear frames, error box pop, T7 words + chip 0/112/100%, slats closing, shut tail),
  `G_*` graded frames, `x4-still-source_L107_b101.png` (the still's source frame).
- Render: `cd hyperframes/b02-bug && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b02-bug.mov` (ffprobe in the lane report).
