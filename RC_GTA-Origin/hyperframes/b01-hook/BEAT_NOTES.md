# B1 Hook - `b01-hook` (v02: beat 134f = 4.467 s; composition 146f with 6f handles. v01: 143f / 155f)

## v05 (REVISION_v05.md Lane 1 + the CLIENT OVERRIDE / section U, kit v05): read this first; v04 and older below are kept as reference

Rebuilt shot by shot (doc section 3, beats 1-4). Timing unchanged (beat 134 f, comp 146 f, local = beat + 6). Generator:
lane-1 scratch `gen/b01_gen.cjs` (writes index.html + cues.json from words.json with the kit's `T.lockups` / `T.lockupCues`).

| Local | Shot / event | Notes |
|---|---|---|
| 0-26 | **Light bar, night, full bleed** (`assets/work/b01_lightbar.mp4`, static, U3: no punch-in); 70% white flash on beat f0 (`FX.flash`) | **f0 = `LOOP_FRAME.json`** (+ `assets/work/b01_f0.png`): GTA V R5.4 (LSPDFR night shift, B05 originals) 633.53 s, crop 1280:720:380:200 x1.5 (mod UI out). Drive2 has no night light-bar close-up (all 12 files scanned); this is a medium shot of the sheriff SUV with its blue bar + a red-lit wall, not a macro close-up |
| 26-55 | Hard cut on "every": the full 2x3 grid, 6 px gutters, **complete on its first frame**; tiles slam on a 2-f stagger TL->BR (26-36: picture 108->100% / 4 f power3.out + a short tile flash); year labels `.fx-year` (Coolvetica 60) appear with their tile | GTA 1 R1.5 1997, III R14.1 2001, VC R1.7 2002, SA R1.6 2004, IV R14.4 2008, V R1.3 2013. "every [GTA,]" on a 60%-black pill (local `.b01-pill`), "GTA," 180 |
| 55-96 | Cell 6 grows (6 f, v04) into the GTA VI shot = working clip A (`tools/make_work_clips.py`: 100% -> eased to 85% by 69, 85% to the cut); push 100->104% | **Logo slam** on "GTA" 69: `FX.logoSlam(tl, '#b01-logo-pop', L(69), { from: 150, flash: '#b01-flash', star: '#b01-star', shakeTarget: '#b01-cam', shakePx: 9, shakeF: 6 })` (the call B13 / B17 should mirror), impact 73 (85% flash, flash-star, 9 px shake + 1.2% overscan 73-79) |
| 96-114 | Hard cut at 3.0 s to a **second GTA VI angle** (U3, instead of the doc's 150% crop): R1.2 night getaway (media 12.6 = source 20.8 s), 100% speed, static 112% framing about (400, 1080) that keeps the trailer's wanted-star HUD out | U13 lockup: "even" left (x <= 690) / logo centre / "have you [running]" right (from x 1225, key 186 so it ends inside title-safe); no [DEPTH] (no subject behind "running" in this angle; the phase-1 shooter cut-out `assets/work/b01_shotB_cutout.webm` is unused) |
| 114-146 | Hard cut on "from": the SUV flip = working clip C (40% for the 8 source frames the truck leaves the ground, 125-145); push 100->104% 114->140, held (B2 continues it) | "from the [cops?]*" 240, centred-low (y 800), pops (U2: no siren colour flicker); X9 siren wash 125 and M1 stars from 93 kept from v04 |

Captions (U1/U2): Coolvetica only; words appear on their frame, white + `--text-drop`; "Why" (hero 450) and "cops?" pop + blur in. Sound (cues.json v05): siren_whoop + sub_hit f0; six rising ticks on the tile slams (tick_3 x2, tick_1 x2, tick_2 x2: the library's three pitches); **impact_boom + sub_drop on the logo slam (beat 63, = B13 / B17)**; swipes on the cuts 20 / 90 / 108; siren_whoop 108; metal_crunch 119; word_pops / key_words from `T.lockupCues`. Seam: B1 134-140 = B2 0-6 (mean abs diff 0.4-0.5 / 255 above the caption). Snapshots: `review/v05/`. Check: 0 errors (warnings: nested lockup structure, container overflow of the grid grow, "running" 0.3 s on screen = the VO).

Open: (1) frame 0 carries the doc's 70% white flash, so the still thumbnail is a washed frame (`b01_f0.png` = the un-flashed image); (2) a true night light-bar macro close-up needs footage the project does not have.

## v04 (REVISION_v04.md, review #5): read this first; v03 and older below are kept as reference

Everything else as v03 (timing, footage, cues events). Kit refreshed to v04 (`python3 tools/new_beat.py B1 --refresh`, words.json identical).

| What changed | Why |
|---|---|
| The v03 lockup `every GTA, even [GTA 6,]` + the "have you running" half of lockup 3 are replaced by ONE composition (local 26-114, the reviewer's drawing): the official **GTA VI logo** in the middle (462.5 x 360 px, centred on 960, 540, soft drop shadow) standing in for "GTA 6,", popping + blurring in on "GTA" (69, the kit's starred-word pop via `T.wordPops`), small words left "every GTA, even" (26 / 40 / 55, right-aligned to x 690) and right "have you running" (93 / 98 / 105, from x 1230), each on its spoken frame (hard cuts, `T.lockupsWire`), cap centre on y 540; hard cut on "from" (114) to the lockup `from the [cops?]*` (114-140, "cops?" still starred). The side words carry the kit glow plus a wider dark halo (0 0 16 px 60 %, 0 0 38 px 45 %): over the bright L3 cells / sunlit street they measured 1.9-2.5:1 with the glow alone (a held contrast error) | #5 |
| **Logo file**: `04_Broll/B01/GTA6-logo__cutout.png` (848 x 660 RGBA; B17 may reuse it), copy in `assets/logo/`. Keyed from Rockstar's end card in R17.4 (`04_Broll/_originals/B17/R17.4__Grand Theft Auto VI Launch Trailer`): the last 6 frames before the city fades in (77.47-77.63 s, the logo has finished its settle), averaged to remove compression noise; flat background measured (30, 30, 42); the logo's outermost layer is a dark purple stroke (29, 0, 44) all round, so the matte = opaque core (colour distance > 20 from the background, holes filled, eroded 1 px) + a 1-3 px edge band whose alpha is the projection of each pixel on the background -> stroke line (anti-aliased edge, no fringe), band colour set to the stroke colour (decontaminated). Checked on black, light grey and mid blue, and in the B1 snapshots over the bright street: no halo, no background tint | #5 |

**v04 frames** (local): 26 "every" (cut to L3) | 40 "GTA," | 55 "even" + grow | 69 logo pops (blur 20 px / 92 %), sharp 75 | 93 "have"
| 98 "you" | 105 "running" | 114 cut to "from" | 120 "the" | 125 "cops?" pop + X9 | 140 out.

**Verification v04**: `check --json` 0 errors (warnings: lockup markup nesting; contrast 2.4-3.0:1 on the side words at single samples;
craft "last line"). Snapshots `review/v04/` (13 frames + `sheet.jpg`), read against the reviewer's drawing (comments_sheet #5). Not rendered.

---

## v03 (REVISION_v03.md, client notes 8, 11, 13, 16, 17): read this first; v02 and v01 below are kept as reference

Timing, footage, word frames and cues unchanged (beat 134f, composition 146f, local frame = beat frame + 6). Kit refreshed
to v03 (`python3 tools/new_beat.py B1 --refresh`: kit only, words.json identical). Change only what the notes ask:

| What changed | Why (note) |
|---|---|
| L4 grid: kit modifier `.rc-l4--ink` = every tile is a DARK tile in the dark-card ink (`--card-bg` #0A0A0A, not pure black) with the faint 1 px grid line; the gaussian-blur copy of R1.2 (`#b01-frost-blur`, media-treatment blur) is deleted. Only the two centre tiles (5, 6 = row 2, columns 2-3, the two police cars) show the footage: they clear from dark on "Why" (7) and "does" (15), 3f power2.out (v02's clear timing). Head handle and beat f0 = the dark grid | 8 |
| Camera back to v01, eased: L4 plate push 100 -> 104 % (sine.inOut, local 0 -> 26; was the v02 zoom-out 110 -> 100 %); no punch-in on the L3 cut (`#b01-gcam` deleted); held GTA 6 push 100 -> 104 % (sine.inOut, 61 -> 140, held through the tail; was 108 %); no key punch on "cops?" (`#b01-cam` deleted). B2's hand-off copy follows the new 104 % curve | 13 |
| Captions: v03 lockups (kit `T.lockups` + `T.lockupsWire`), centred (960, 540): small Coolvetica 60 px + one Coolvetica Italic 190 px keyword: `[Why] does` (7-26) / `every GTA, even [GTA 6,]` (26-93) / `have you running \| from the [cops?]*` (93-140). Every word appears on its own spoken frame (hard cut, no animation); only "cops?" pops + blurs in (6f expo.out, with the X9 wash); lockups hard-cut into each other; the last one cuts out on the boundary 140 (v02: 3f eased exit). The kit drops "does" below the "y" descender | 11, 16, 17 |
| Kept: R1.2 L4 moment, L3 cells and the grow (power3.out), M1 stars pop at (1640, 80), X9 wash on "cops?", contrast grade, all frames | "change only what the notes ask" |

**v03 frames** (local; beat = local - 6): 0-6 dark grid (head + beat f0) | 7 "Why" (big) + tile 5 clears | 15 "does" + tile 6
clears | 26 cut to L3, "every" | 40 "GTA," | 55 "even" + grow | 61 GTA 6 full (S01), push starts | 69 / 80 "GTA 6," (big) |
93 "have" + stars | 98 "you" | 105 "running" | 114 "from" | 120 "the" | 125 "cops?" pop + blur (X9 red 125-126, blue 127-128,
S02) | 131 sharp | 140 boundary: caption gone, picture at 104 % | 140-146 tail.

**Verification v03**: `npx --yes hyperframes@0.9.52 check --json` 0 errors (warnings: `nested_structure_needs_subcomposition` = the kit's lockup markup; craft `line_unread` "film's last line" on a beat segment; v02's `duplicate_media_discovery_risk` is gone with the frosted copy). Snapshots `review/v03/` (22 frames `f<local>_<what>.png` + `sheet.jpg`; `vs_ref.jpg` = ref 1 next to the lockups and the dark grid), read: dark tiles with faint grid lines, only the centre tiles show footage (clearing on "Why" / "does"), every lockup word on its frame, "cops?" blurred on 125 and sharp by 131, no zoom on the cut or on "cops?", nothing cut off. Seam: B1 local 140 = B2 local 6, pixel-identical outside the stars (mean diff 0.000). Not rendered (v03: snapshots only).

---

## v02 (REVISION_v02.md, client notes 10-15): read this first; the v01 notes below are kept as reference

**Beat 134f (4.467 s, v01 143f), composition 146f = 4.8666667 s** (root `data-duration`), local frame = beat frame + 6.
Re-timed from `timing/beat_map.json` v02 (`python3 tools/new_beat.py B1 --refresh`: kit + words.json). No footage,
moment or position changed; every frame below moved to the 115% voice.

| What changed | Why (note / rule) |
|---|---|
| All frames re-timed (table below); root 5.1666667 -> 4.8666667 | note 10 (VO 115%), REVISION "every beat ~6% shorter" |
| T1 chunks -> word-by-word groups of max 2 words: `Why does / every GTA, / even / GTA 6, / have you / running` (each word pops on its own onset, 5f expo.out, 1f lead; groups hard-cut) | note 11, rule A (kit `captionPlanV2` + `captionPops`) |
| T2 "from the *cops?*" -> `from / the cops?` (lead words pop; keyword blur punch 30 -> 0 px, 108 -> 100 %, 6f expo.out on its onset); the last group exits in 3f (power2.in) ending on the boundary instead of v01's 4f linear fade | note 11 + 14, rules A C |
| Coolvetica / Coolvetica Italic (kit base.css) | note 12 |
| L4 plates: v01 linear push 100 -> 104 % -> **zoom OUT 110 -> 100 %** (easeInOutSine) across the frosted shot | notes 14 + 15, rules C D ("alternate with slow zoom-outs") |
| L3 grid: **punch-in on the cut** 112 -> 100 % over 10f (easeOutExpo) on a new wrapper `#b01-gcam` | note 15, rule D ("cuts into a new shot") |
| Held GTA 6 shot: v01 linear 100 -> 104 % -> **push 100 -> 108 %** (easeInOutSine, local 61 -> 140), held at 108 % through the tail | notes 14 + 15, rules C D |
| **Key punch on "cops?"** (whole picture, new outer wrapper `#b01-cam`): 100 -> 106 % in 3f (expo.out, from 1f before the onset), back over 7f (sine.inOut), at rest on 134 | note 15, rule D ("emphasis words") |
| Frost clears (power2.out), cell pops (fade power2.out + scale power3.out), grow (power3.out), stars (power3.out): kit v02, all eased; X9 = hard frames (a cut pattern) | note 14, rule C |
| Kept: M1 stars at (1640, 80) (CONFLICTS C35), outside the camera (steady); captions outside the camera; no grain/vignette/chroma (assembly, rule F) | "don't change anything else" |

**v02 frames** (local; beat = local - 6):

| local | beat | what |
|---|---|---|
| 0-26 | -6-20 | L4 frosted tiles over R1.2 (31.6 s), zoom-out 110 -> 100 %; tiles clear on "Why" 7 and "does" 15 (3f each) |
| 7 / 15 | 1 / 9 | "Why" / "does" pop (group 1) |
| 26 | 20 | hard cut on "every" to L3 (cells pop 26, 29, 32, 35, 38, 41; landed 45); grid punch-in 26-36; "every" pops |
| 40 | 34 | "GTA," |
| 55 | 49 | "even" (group 3); cell 6 switches to GTA 6 (R1.2 8.2 s) and grows to full frame over 6f |
| 61 | 55 | full frame = `gta6_cell_full` (S01 peak); push 100 -> 108 % starts |
| 69 / 80 | 63 / 74 | "GTA" / "6," (group 4) |
| 93 / 98 | 87 / 92 | "have" / "you" (group 5); M1 stars pop 93, 96, 99, 102, 105 (landed 108) |
| 105 | 99 | "running" (group 6) |
| 114 | 108 | T2 "from" |
| 120 / 125 | 114 / 119 | T2 "the" / keyword "cops?" (blur punch, lands 131); X9 red 125-126, blue 127-128 (`cops` = beat 119, S02); key punch 124-134 |
| 137-140 | 131-134 | T2 last group exits (3f, power2.in); gone on the boundary |
| 140 | 134 | boundary (= B2 local 6): picture at 108 %, push at rest |
| 140-146 | 134-140 | tail handle: GTA 6 at 108 % + stars |

`cues.json`: `gta6_cell_full` 55, `cops` 119 (v01 58, 127). `tesseract_shots.json`: no shots (HF-owned beat, opaque).

**B1 -> B2 hand-off**: B2 local 0 = this local 134, B2's GTA 6 copies use media-start 79/30 = 2.6334 s and finish this
same easeInOutSine push (local 134 -> 140) before holding 108 %: B1 local 140 and B2 local 6 snapshots are
pixel-identical outside the stars (mean abs diff 0.00/255).

**Conflict (rule A vs plan p.20 "f0 already shows 'Why does'")**: words now pop on their own onset, so "Why" first shows
on beat f1 (local 7; its pop starts on f0 at 0 %). The client's note 11 (word by word) wins; f0 still moves (zoom-out).

**Verification v02**: `npx --yes hyperframes@0.9.52 check --json` 0 errors (warnings: `duplicate_media_discovery_risk` =
the L4 sharp/frosted pair by design; `timeline_track_too_dense` caption lane; `nested_structure_needs_subcomposition` kit
T2 markup; `contrast_aa_failure` 2.2:1 on "every GTA," over the light GTA 3 sky cell at local 40 (white caption + kit
shadow, as v01); craft `line_unread` on 1-word groups (voice timing wins)). Snapshots in `review/v02/` (25 frames + 3
contact sheets: every word onset, the cut, punch-in, grow, key punch, X9, the T2 exit, boundary, tail), read: max 2 caption
words on every frame, words appear on their onset frames, Coolvetica, nothing cut off.
Render: `05_GFX/renders/b01-hook.mov` = prores (4444), 1920x1080, 30 fps, **146 frames** (134 + 12), yuva444p12le.

---

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
