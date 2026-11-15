# B1 Hook - `b01-hook` (beat 143f = 4.767 s; composition 155f with 6f handles)

Plan: B1 build p.19-20, overview p.18, into each beat p.16 ("B1 opens cold"), B-roll p.28, style kit p.9-11, T1/T2 p.11,
L3/L4 p.14, X9 p.16, M1/M5 p.17. Storyboard: STORYBOARD.md B1. Frames below are **beat frames** (f0 = "Why"
beat start; composition local frame = beat frame + 6).

## 1. What the viewer sees
A frosted 4x3 grid over a GTA 6 police moment already reading "Why does", a hard cut on "every" to a 3x2 grid of
police chases from GTA 1 to GTA 5, the GTA 5 cell switching to GTA 6 and filling the screen on "even", five wanted
stars popping in, and "from the *cops?*" landing with a red/blue siren wash.

## 2. Assets
- B-roll (all `assets/footage/<RID>.mp4`, stand-ins for now): **R1.2** (L4 police moment, official PlayStation
  features trailer), **R1.5** GTA 1, **R14.1** GTA 3, **R1.7** Vice City, **R1.6** San Andreas, **R14.4** GTA 4,
  **R1.3** GTA 5 (L3 cells 1-6), **R17.1** official GTA 6 Trailer 1 (cell 6 switch -> full frame; continues into B2).
  Not used: R1.1 (unofficial, plan says avoid), R17.3 (the plan's alternative to R17.1), RT7 (M1 is built).
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
5. `#b01-grid` L3 (z 2): `#b01-grow` (R17.1, last child = on top) > cells 1-6 > `#b01-grid-ground` ink black
6. `#b01-frost` L4 (z 1): `#b01-frost-tiles` overlays > frosted copy of R1.2 (masked per tile) > sharp R1.2 plate

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b01-hook"]`)
| beat f | what | values / ease |
|---|---|---|
| -6..21 | L4: R1.2 sharp plate + frosted copy (same src/start/media-start) + 12 tile overlays | blur = media treatment `effects.blur 1` laid out at 1/1.76 and scaled 1.76 = sigma 40 px; tile 480x360, 10% white, 1 px white 20% border |
| -6..21 | push both plates | 100 -> 104%, linear (`S.push`) |
| 1, 9 | one tile clears per spoken word ("Why", "does"), seeded order (seed 1: tile 4, then tile 10) | 3f linear (`S.frostClear`), clear on f4 / f12 |
| 21 | hard cut to L3 3x2 (8 px ink-black gutters, cells 634.67x536) | `data-start` boundary |
| 21,24,27,30,33,36 | cells 1-6 pop L->R, T->B | 4f: opacity 0->1 linear, scale 96->100% power3.out (`S.gridBuild`, stepF 3); landed f25..40 |
| 52 | cell 6 (R1.3) ends; R17.1 starts in cell 6's rect and grows to full frame | 6f, clip-path + picture scale, power3.out (`S.gridGrow`); full on **f58** |
| 58..143 (+6) | held full-frame GTA 6 push | 100% (f58) -> 104% (f143), linear; same rate on through the tail handle (104.28% at f149) |
| 92,95,98,101,104 | M1 stars pop (40 px each, row centred on (1700, 80): x 1584-1816, y 60-100, 8 px gap) | scale 0->1 over 3f, power3.out, no overshoot (`M.starsPopIn`); all landed f107 |
| 127-130 | X9 siren wash on "cops" | #E3262E 35% Overlay f127-128, #2D5BFF 35% Overlay f129-130, gone f131 (`X.sirenWash`) |
| 115 / 127 | T2 lead-in "from the" hard cut / keyword "cops?" blur-in | keyword 6f: blur 30->0 px, scale 108->100%, power3.out (`T.punchPair`); lands f133 |
| 139-143 | T2 out | 4f linear fade; gone on f143 |
Handles: head (local 0-5) = the frosted R1.2 opening state with "Why does" and the push already running; tail
(local 149-154) = full-frame R17.1 + stars, push continuing (T2 already gone).

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
- GTA 6 shots only from official uploads (R1.2 PlayStation, R17.1 Rockstar); never R1.1.
- X9 only on "cops"; no other red/blue flash. No glitch in B1.
- Stars and T2 do not carry into B2 (B2 starts on the bare R17.1 picture).
- Keep R17.1's source time continuous with B2 (see Pending: R17_IN).

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
8. **Footage choice**: R1.2 for the L4 police moment (plan: "R1.2 or R17.1"), R17.1 for the switch (plan: "R17.1 or
   R17.3"), so the hook shows two different official GTA 6 images.
9. **Grade**: "Game footage: punchy contrast" (p.10) implemented as media-treatment contrast +0.15 (shared value with
   B15); the whole-edit grain is Tesseract's.
10. **Push**: the grid build (f21-52) is not pushed (cells pop throughout, it is a build, not a held shot); the L4
    shot and the held GTA 6 shot are.
11. SUGGESTION (not built): none.

## Pending real footage
- **R1.2**: pick the police moment in the official features trailer; set the same `data-media-start` on
  `#b01-frost-sharp` and `#b01-frost-blur` (stand-in 0).
- **R1.5, R14.1, R1.7, R1.6, R14.4, R1.3**: in-points of a police-chase moment in each (`data-media-start` on
  `#b01-c1-v..#b01-c6-v`), reframe inside the 634.67x536 cells with `--rc-pos` (object-position) if the action is
  off-centre. R1.5 is a GTA 1-to-GTA 6 compilation: use its GTA 1 part.
- **R17.1 (R17_IN)**: a police-pursuit moment of Trailer 1 (not the opening Lucia-in-custody seconds, which B17
  uses). Set `#b01-gta6` `data-media-start` = R17_IN and in B2 `#b02-g6-crt` / `#b02-g6-clean` `data-media-start`
  = R17_IN + 2.8334 (B1 local f143 = B2 local f0). If the manifest gets a `source_in/out` window for R17.1, it must
  contain both this moment and B17's opening, or the offsets change.
- Re-check the contrast +0.15 game grade and the caption legibility (y 620) on the real pictures.
- Re-render: `python3 tools/sync_footage.py hyperframes/b01-hook`, then the render command below.

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `duplicate_media_discovery_risk` (the L4
  sharp/frosted pair, by design), `timeline_track_too_dense` (all T1 chunks on one caption lane, by design),
  `nested_structure_needs_subcomposition` (kit T2 markup), craft `line_unread` (plan's voice timing wins; "film's last
  line" does not apply to a beat segment).
- Snapshots in `review/` (read): `A_*` local 0-121 (handles, frost clears, grid pops, switch/grow, stars),
  `B_*` local 132-154 (X9 red/blue frames, T2 blur-in, fade, tail handle), `G_*` graded frames,
  `render_check_strip.jpg` (decoded frames of the MOV).
- B1 -> B2 seam: B1 local 149 vs B2 local 6 snapshot, mean pixel difference 0.74/255 (same source frame 91, same
  104% push) apart from the stars.
- Render: `cd hyperframes/b01-hook && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b01-hook.mov` -> see the final ffprobe in the lane report (1920x1080, 30 fps, 155 frames,
  yuva444p12le, no audio; alpha opaque on all frames).
