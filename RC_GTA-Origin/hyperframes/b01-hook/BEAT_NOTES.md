# B1 Hook - `b01-hook` (beat 143f = 4.767 s; composition 155f with 6f handles)

Plan: B1 build p.19-20, overview p.18, into each beat p.16 ("B1 opens cold"), B-roll p.28, style kit p.9-11, T1/T2 p.11,
L3/L4 p.14, X9 p.16, M1/M5 p.17. Storyboard: STORYBOARD.md B1. Frames below are **beat frames** (f0 = "Why"
beat start; composition local frame = beat frame + 6).

## 1. What the viewer sees
A frosted 4x3 grid over a GTA 6 police moment already reading "Why does", a hard cut on "every" to a 3x2 grid of
police chases from GTA 1 to GTA 5, the GTA 5 cell switching to GTA 6 and filling the screen on "even", five wanted
stars popping in, and "from the *cops?*" landing with a red/blue siren wash.

## 2. Assets
- B-roll (real footage, `assets/footage/<RID>.mp4` cut by `tools/sync_footage.py`, see "Footage used"): **R1.2**
  official PlayStation features trailer, two moments: the L4 police moment and the cell-6 switch -> full-frame GTA 6
  shot (SUBSTITUTE for the missing R17.1/R17.3; continues into B2), **R1.5** GTA 1, **R14.1** GTA 3, **R1.7** Vice
  City, **R1.6** San Andreas, **R14.4** GTA 4, **R1.3** GTA 5 (L3 cells 1-6).
  Not used: R1.1 (unofficial, plan says avoid), R17.1 / R17.3 (missing), RT7 (M1 is built).
- SFX: **S01** (Cinematic Hit 1), **S02** (Siren). Music: **MU1**.
- Fonts: Inter Medium 46 (T1), Inter SemiBold 42 + Instrument Serif Italic 140 (T2). Kit fonts (`assets/kit/fonts`).
- Graphics: M1 stars (kit `RCK.motifs`), X9 wash (kit). No cut-outs.
- Grade (plan p.10 "Game footage: punchy contrast; leave HUD colours alone"): media-treatment `adjust.contrast +0.15`
  on every video (same value as the B15 composition); the L4 frosted copy also carries `effects.blur 1`.

## 3. Tool and layer stack
HyperFrames builds the whole beat (opaque every frame, verified on the render's alpha). Tesseract adds only audio.
Top to bottom:
1. `#b01-t2` T2 punch pair (z 40)
2. `#b01-cap-1..4` T1 captions (z 40)
3. `#b01-stars` M1 five stars (z 20)
4. `#b01-x9` X9 siren wash, Overlay blend 35% (z 10; direct child of the root so it blends with the picture)
5. `#b01-grid` L3 (z 2): `#b01-grow` (R1.2 police-truck shot, last child = on top) > cells 1-6 > `#b01-grid-ground` ink black
6. `#b01-frost` L4 (z 1): `#b01-frost-tiles` overlays > frosted copy of R1.2 (masked per tile) > sharp R1.2 plate

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b01-hook"]`)
| beat f | what | values / ease |
|---|---|---|
| -6..21 | L4: R1.2 sharp plate + frosted copy (same src/start/media-start) + 12 tile overlays | blur = media treatment `effects.blur 1` laid out at 1/1.76 and scaled 1.76 = sigma 40 px; tile 480x360, 10% white, 1 px white 20% border |
| -6..21 | push both plates | 100 -> 104%, linear (`S.push`) |
| 1, 9 | one tile clears per spoken word ("Why", "does"), seeded order (seed 2: tile 5, then tile 6 = row 2, columns 2-3, over the two police cars) | 3f linear (`S.frostClear`), clear on f4 / f12 |
| 21 | hard cut to L3 3x2 (8 px ink-black gutters, cells 634.67x536) | `data-start` boundary |
| 21,24,27,30,33,36 | cells 1-6 pop L->R, T->B | 4f: opacity 0->1 linear, scale 96->100% power3.out (`S.gridBuild`, stepF 3); landed f25..40 |
| 52 | cell 6 (R1.3) ends; the GTA 6 shot (R1.2, 8.2 s) starts in cell 6's rect and grows to full frame | 6f, clip-path + picture scale, power3.out (`S.gridGrow`); full on **f58** |
| 58..143 (+6) | held full-frame GTA 6 push | 100% (f58) -> 104% (f143), linear; same rate on through the tail handle (104.28% at f149) |
| 92,95,98,101,104 | M1 stars pop (40 px each, row centred on (1640, 80): x 1524-1756, y 60-100, 8 px gap; see Interpretations 12) | scale 0->1 over 3f, power3.out, no overshoot (`M.starsPopIn`); all landed f107 |
| 127-130 | X9 siren wash on "cops" | #E3262E 35% Overlay f127-128, #2D5BFF 35% Overlay f129-130, gone f131 (`X.sirenWash`) |
| 115 / 127 | T2 lead-in "from the" hard cut / keyword "cops?" blur-in | keyword 6f: blur 30->0 px, scale 108->100%, power3.out (`T.punchPair`); lands f133 |
| 139-143 | T2 out | 4f linear fade; gone on f143 |
Handles: head (local 0-5) = the frosted R1.2 opening state with "Why does" and the push already running; tail
(local 149-154) = full-frame GTA 6 (R1.2) + stars, push continuing (T2 already gone).

## 5. On-screen text (locked-script words; chunks as the plan's slashes)
| text | style | position / size | beat frames |
|---|---|---|---|
| Why does | T1 | Inter Medium 46 px white, soft shadow, centred x 960, y 620 | -6 -> 21 (already on f0) |
| every GTA, | T1 | same | 21 -> 52 |
| even GTA 6, | T1 | same | 52 -> 92 |
| have you running | T1 | same | 92 -> 115 |
| from the + *cops?* | T2 | lead Inter SemiBold 42 + keyword Instrument Serif Italic 140, baselines aligned, 14 px gap, centred as a group, shared baseline y 637.6 (`--rc-y 590`) | 115 (lead) / 127 (keyword) -> fade 139-143 |
Caption starts vs voice (words.json): Why -0.05f (shown from f0 by plan), every -0.21f, even -0.05f, have -0.37f,
from -0.0f, cops? +0.4f: all within +/-2f.

## 6. Audio (Tesseract places it from `cues.json`; levels from the plan's SFX table p.35)
- **S01** Cinematic Hit 1 (PRISFX > Hits): peak at 0.33 s, so the file starts 10f before the slam (beat f48) and the
  peak lands on `gta6_cell_full` = **f58** (the frame the GTA 6 cell fills the screen). Trim to 1.5 s, 12f fade.
  Peak -8 dBFS.
- **S02** Siren (PRISFX > Bonus SFX > Misc): slice 0.5-1.3 s of the 6.8 s file, starting on `cops` = **f127** (same
  frame as the X9 wash), 6f fade out, high-pass 300 Hz. -14 dBFS.
- **MU1**: Black Vertigo starts at full energy on f0, no fade-in (anchor re-timed on MU5 "fun", CONFLICTS C11/C12).
  Music under the voice ~-22 LUFS short-term.

## 7. Mistakes to avoid
- No fade from black and no logo before the hook; f0 must already move and read "Why does" (it does: video + push).
- The question must read with the sound off: every word is on screen (T1 chunks + T2).
- GTA 6 shots only from official uploads (here R1.2 PlayStation, both shots); never R1.1 or R17.5.
- X9 only on "cops"; no other red/blue flash. No glitch in B1.
- Stars and T2 do not carry into B2 (B2 starts on the bare GTA 6 picture).
- Keep the GTA 6 shot's source time continuous with B2 (same R1.2 window in-point 8.2 s; B2 media-start 2.8334).

## Interpretations / conflicts
1. **"Why does" on f0** (B1 build p.20, priority 2) vs T1 "hard cut in on the first syllable" (T library p.11): the
   caption is on from local 0 (head handle) so f0 already shows it; voice "Why" is at f1.05 (1 frame, inside +/-2f).
2. **Tiles "clear one per word"** (p.20) with the cut to L3 on "every": only "Why" and "does" are spoken on L4, so
   2 of the 12 tiles clear (STORYBOARD interp).
3. **M1 "3f apart" vs "across 'have you running from the'"** (both p.20): 3f apart from "have" (f92-104) as the
   storyboard and kit; the phrase spans 35f (kit conflict 4).
4. **"On 'even GTA 6'"** read as the phrase onset: switch + grow on "even" f52, full f58 (STORYBOARD interp).
5. **L3 cut frame**: cells pop from f21, so the cut frame f21 shows the black grid + "every GTA," and cell 1 appears
   at 25% on f22 (storyboard frames kept; kit offers starting 1f earlier).
6. **T2 position** (plan gives none): baseline aligned to the T1 caption baseline (y 637.6) so "from the" lands on
   the reading line of the captions it replaces; kit default would be y 540.
7. **X9 z-order**: above the picture, below the text and stars (Overlay of 35% red/blue on white = white, so text
   would read the same either way).
8. **Footage choice**: R1.2 for the L4 police moment (plan: "R1.2 or R17.1"). For the switch the plan's R17.1/R17.3
   are missing; R1.2 (official) supplies a second, different police moment (see Substitutions).
9. **Grade**: "Game footage: punchy contrast" (p.10) implemented as media-treatment contrast +0.15 (shared value with
   B15); the whole-edit grain is Tesseract's.
10. **Push**: the grid build (f21-52) is not pushed (cells pop throughout, it is a build, not a held shot); the L4
    shot and the held GTA 6 shot are.
11. SUGGESTION (not built): none.
12. **M1 position** (plan p.17: "40 px at the top-right (x 1700, y 80)"): the official trailer's own in-game HUD
    (wanted stars and icons) sits in the top-right corner of the R1.2 shot, and at x 1700 the fifth M1 star collided
    with it. The row centre is moved 60 px left to (1640, 80); same y, size, timing. DEVIATION, flagged.
13. **Cell framing**: cell 4 (San Andreas) uses object-position 70% to push the game's mission text out of the cell;
    R1.7 and R14.4 are cropped in footage.json (watermark band; corner logos).
14. **R14.4 pixel aspect (fixed)**: R14.4 is anamorphic (stored 2276x720, SAR 320:569). The first footage pass cut
    it as square pixels, so cell 5 was stretched 1.78x; `tools/sync_footage.py` now crops in stored pixels, then
    squares the pixels, then fits. New crop 1306:620:604:0 (stored) and a window inside one shot (the old
    64.0-65.5 crossed two cuts: a different shot at 64.0 and a door close-up from ~65.25). Re-synced, grid
    re-checked (`review/grid/`), re-rendered.

## Footage used
| R-ID | file (`04_Broll/_originals/B01/`) | in-out (s, original) | what it shows | link |
|---|---|---|---|---|
| R1.2 | `R1.2__Grand Theft Auto VI - Features Trailer ｜ PS5 Games [8L0CzL2V72c].mp4` | 31.6-32.5 | L4: two marked POLICE cruisers with light bars, seen from a driver's POV (official) | https://www.youtube.com/watch?v=8L0CzL2V72c&t=31 |
| R1.2 | same | 8.2-11.43 (continues in B2 to 12.1) | cell 6 -> full frame: a police truck (light bar, roof number) charges the shooter, is shot up and flips over (official) | https://www.youtube.com/watch?v=8L0CzL2V72c&t=8 |
| R1.5 | `R1.5__Wanted Levels： GTA 1 to GTA 6 Evolution (1997–2026) [nTL0QWjllf8].mp4` | 95.6-96.83 | cell 1, GTA 1: a white police car with lights spinning in on the player's limo (top-down) | https://www.youtube.com/watch?v=nTL0QWjllf8&t=95 |
| R14.1 | `R14.1__GTA 3 Epic 6 Stars Wanted Level Shootout+ Tank Rampage + Escape [6lSy09Uruz0].mp4` | 44.0-45.23 | cell 2, GTA 3: an LCPD car right behind / ramming the player's car | https://www.youtube.com/watch?v=6lSy09Uruz0&t=44 |
| R1.7 | `R1.7__GTA Vice City Epic 6-Stars Police Chase Escape [s2KJsYEngS8].mp4` | 6.4-7.63 | cell 3, Vice City: VCPD cars with flashing lights burning while Tommy fires at them (crop 782:660:560:0 keeps the uploader's watermark band out) | https://www.youtube.com/watch?v=s2KJsYEngS8&t=6 |
| R1.6 | `R1.6__The Biggest Police Chase in GTA San Andreas History! (100 Cops vs. 1 S [flgIZbQHwN8].mp4` | 46.0-47.23 | cell 4, San Andreas: an LSPD cruiser with lights in pursuit of a biker | https://www.youtube.com/watch?v=flgIZbQHwN8&t=46 |
| R14.4 | `R14.4__Deadly Pursuit (GTA IV) [WNZMK7KPZWs].mp4` | 63.75-64.98 (on screen from the pop: 64.15-64.98; one shot 63.5-65.1) | cell 5, GTA 4: an LCPD car with lights flashing following the silver sedan up the street. Anamorphic source (2276x720 stored, SAR 320:569 = 1280x720 on screen): crop in STORED px 1306:620:604:0 = 734x620 on screen (cell aspect ~1.18), excludes both corner logos | https://www.youtube.com/watch?v=WNZMK7KPZWs&t=63 |
| R1.3 | `R1.3__GTA V - ＂5 Stars＂ Police Chase [NcTdBgA3Bkg].mp4` | 46.0-47.03 | cell 6, GTA 5: a white supercar fleeing past POLICE cars (5 stars) | https://www.youtube.com/watch?v=NcTdBgA3Bkg&t=46 |

## Substitutions
- SUBSTITUTE (Rule 5): R1.2 Grand Theft Auto VI - Features Trailer | PS5 Games [8L0CzL2V72c] @ 00:08-00:11 for R17.3
  (missing: Trailer 2 not downloaded; R17.1, the plan's other option for the switch, is missing too). Official
  PlayStation upload, a police-chase moment (police truck charging and flipping). Chosen over R17.4/R17.2/R17.6 because
  it is the clearest police moment among the official clips, and it keeps B1/B2 on one official source.

## Pending / blocking
- Nothing blocking. If R17.1/R17.3 are uploaded later, the switch can move to them (change B1 `#b01-gta6` and B2
  `#b02-g6-*` together, same in-point rule).

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `duplicate_media_discovery_risk` (the L4
  sharp/frosted pair, by design), `timeline_track_too_dense` (all T1 chunks on one caption lane, by design),
  `nested_structure_needs_subcomposition` (kit T2 markup), craft `line_unread` (plan's voice timing wins; "film's last
  line" does not apply to a beat segment).
- Snapshots in `review/` (read, real footage): local 0, 6, 12, 20, 26, 27, 40, 52, 58, 64, 110, 133, 135, 149, 154
  (handle, frost clears, the L3 cut and pops, switch/grow, stars, X9, T2 blur-in, tail); decoded MOV frames checked.
- B1 -> B2 seam: B1 local 149 and B2 local 6 show the same source frame (R1.2 11.233 s) at the same 104% push
  (B2's straight hand-off copy), apart from the stars.
- Render: `cd hyperframes/b01-hook && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b01-hook.mov` -> see the final ffprobe in the lane report (1920x1080, 30 fps, 155 frames,
  yuva444p12le, no audio; alpha opaque on all frames).
