# B9 Straight through you - `b09-throughyou` (v02: beat 202f = 6.733 s; composition 214f with 6f handles)

## v04 (REVISION_v04.md #10, #11, #12). Read this first

Everything else as v03 below (lockups, strips, timing, cues).

| Change | Note |
|---|---|
| **More B-roll under "The police cars / stop following you / and start trying"**: three quick Tesseract L1 cut-ins (`tesseract_shots.json`, 105%, soft edges, grade b9-sat60 like the GTA 1 shot, static framing: 0.7-0.9 s cuts are not held shots), cut on the voice: **f0-21** GTA 2 police cars swinging into a junction (`B9-gta2-police-A`, R9.3 42.0 s, crop 480:270:160:150) / **f21-49** "stop": GTA 1 4K, a police car tailing the player's van (`B9-gta1-4k-follow-B`, R9.4 540.55 s, crop 1440:810:0:90) / **f49-69** "and": GTA 1 4K, a police car ramming the van's side (`B9-gta1-4k-ram-C`, R9.4 573.2 s, crop 1440:810:0:135). No watermarks in R9.3 / R9.4 (game HUD as is) | #10 |
| **The GTA 1 shot kept for "to drive straight through you."**: `B9-gta1-chase-L1` now f69-120 (was f0-120), source_in 314.1 -> 316.4 s, so every frame f69-120 shows the same source frame as v03 and it still ends at 318.1 s = strip 1's first frame; push 100 -> 104% across its 51 frames (easeInOutSine) | #11 |
| **Glow flash on each strip pop**: kit `S.glowFlash(tl, '#b09-sN', t)` on the `gridPop` frame (kit defaults: 2f in / 6f out, power2.out; white bloom + inner edge glow + outer glow on the gutter) | #12 |

Cross-beat: `b16-bug-origin/tools/make_rewind.py` reads B9's earliest R9.1 shot (still `B9-gta1-chase-L1`; the cut-ins are
R9.3 / R9.4) and samples source_in + (f - start_f)/30 for f56-120: identical source times, so B16's rewind is unchanged.
R9.4 is used for the first time (Tesseract only; not synced into this folder).

**Verification (v04)**: `check --json` 0 errors (warnings as v03). Snapshots `review/v04/` (read): `sheet_a.jpg` the cut-in
frames 6-125 (overlay only), `sheet_cutins_over-footage.jpg` + `comp/` = those frames composited over each shot's source
frame read from tesseract_shots.json (look check, not the finish), `sheet_b.jpg` the three glow flashes (126-134, 149-153,
174-182) and 197. B9 local 202 still = b10-fun local 0 (flashes end 8f after each pop). Not rendered.

## v03 (REVISION_v03.md notes 11, 12, 13, 16, 17). Read this first

Change only what the notes ask; everything else is the v02 section below (timing, footage, strips, cues unchanged).

| Change | Note |
|---|---|
| **Zooms removed.** L1 (`tesseract_shots.json`): framing back to v01's held-shot push, keys `[{f:0, scale:100}, {f:120, scale:104, ease:easeInOutSine}]`; v02's punch-in 114 -> 101%, push to 108% and the punch on "straight" are gone. Strips: the plan's 4f punch-in to 115% (`gridPop`) stays; the held push after it is back to v01's x 1.04 (was x 1.06), still one easeInOutSine curve to B10's "fun" cut (`PUSH` = b10-fun's `PUSH`) | 13 |
| **Caption lockups** (kit `T.lockups` + `T.lockupsWire`, ref 1), centred (960, 540), words hard-cut in on their frames, no exit: T1 "The police cars [stop] following you" (local 7-55) / "and [start] trying" (55-75) / "to drive [straight]* through you." (75-126; "straight" pops + blurs in, the beat's only star). T4 "They [ram.]" (126-149) / "They [chase.]" (149-174) / "They don't [let go.]" (174-208, held to the beat end) | 11, 16, 17 |
| T4 phrases **centred, not in their strips**: centring fits (each lockup stays inside the middle strip, `maxWidth` 580 < 634.67 px, never across a gutter), so they follow the rest of the captions; "They ram." sits on the still-empty ink middle strip, the other two over strip 2's footage | 16 (my call) |
| Dark: nothing to change (footage on ink-black gutters) | 12 |

**Verification (v03)**: `npx --yes hyperframes@0.9.52 check --json` 0 errors (warnings: kit lockup markup nesting,
`first_frame_empty` = transparent head handle, `line_unread` on the voice-timed lockups, e.g. "and start trying" 20f).
Snapshots `review/v03/` (read): every word onset 7 ... 197, the "straight" pop 86-92, the L3 cut 126/130, 148, 202,
207, tail 208/213; `sheet_a.jpg`, `sheet_b.jpg`; `comp/*_over-L1.jpg` = the transparent overlay composited over the
R9.1 source frame (crop, 105% x the 104% push, sat -40%: a look check, not the finish); `vs_ref.jpg` = next to ref 1.
B9 local 202 / 207 and b10-fun local 0 / 5 measured pixel-identical. Not rendered (v03: snapshots only).

## v02 (REVISION_v02.md; client notes 4, 10, 11, 12, 14, 15). Read this first

The v01 sections below are kept as reference; where they disagree with this section (frames, the path diagram, eases,
fonts), this section wins.

**What changed and why**
| Change | Client note / rule |
|---|---|
| **Path diagram removed entirely**: white dot, dotted yellow path, red arrow, the per-frame TRACK, the dot shake and the diagram push. B9 f0-120 is now the Tesseract L1 footage with the T1 captions only. | note 4 "Remove the 0:38 overlayed arrow and other animations, the broll is perfect" |
| Re-timed to the v02 beat map (VO 115%): beat 202f (was 215), edit 994-1196 (33.133-39.867 s); composition 214f, root `data-duration="7.1333333"` | note 10 / REVISION "What is already done" |
| T1 word by word, max 2 words (kit `captionPlanV2` + `captionHTMLV2` + `captionPops`): The / police cars / stop / following you / and start / trying / to drive / straight / through you. | note 11, rule A |
| T4 word by word, max 2 words, one group at a time in its strip: "They ram." (strip 1) / "They chase." (strip 2) / "They don't" -> "let go." (strip 3); the last group exits 3f (power2.in) ending on the beat end | note 11, rule A |
| Coolvetica (kit base.css) | note 12 |
| Nothing linear: the v01 `ease: 'none'` strip push (115% -> x1.04) and the diagram's linear moves are gone; the strip push is ONE easeInOutSine curve 115% -> 115% x 1.06 from each punch landing to the "fun" cut in B10 (this composition plays its head with an ease that is exactly that part of easeInOutSine, b10-fun plays the rest: same function of the edit frame, B9 local 202/207 = B10 local 0/5 pixel-identical, measured) | note 14, rule C |
| L1 framing v2 (Tesseract keys, `tesseract_shots.json`): punch-in on the cut from B8's black 114 -> 101% (f0-10, easeOutExpo), push 101 -> 108% to the cut (easeInOutSine), one keyword punch on "straight" (105.86% f79 -> 112.5% f82 easeOutExpo -> 106.87% f91 easeInOutSine). Strips: kit gridPop pop + 4f punch-in to 115% (plan), then the eased push above | note 15, rule D |
| L1 `source_in_s` 313.9 -> 314.1 s so the shorter L1 shot (120f) still ends exactly where strip 1 starts (R9.1 318.1 s, continuous source time across "They ram.") | re-timing |

**New frames (beat frames; local = beat + 6)**
| What | beat f | local |
|---|---|---|
| X1 from B8's black, L1 R9.1 (Tesseract) starts; "The" | 0 / 1 | 6 / 7 |
| T1 groups first frames | 1, 5, 21, 28, 49, 61, 69, 80, 95 | 7, 11, 27, 34, 55, 67, 75, 86, 101 |
| words | The 1, police 5, cars 15, stop 21, following 28, you 47, and 49, start 53, trying 61, to 69, drive 72, straight 80, through 95, you. 102 | +6 |
| "straight" keyword punch (L1 keys) | 79-91 | 85-97 |
| X1 to L3 on "They ram.": L1 ends, strip 1 pops + punch, T4 "They ram." | 120 (ram. 128) | 126 (134) |
| strip 2 + "They chase." | 143 (chase. 149) | 149 (155) |
| strip 3 + "They don't" | 168 (don't 175) | 174 (181) |
| "let go." | 185 (go. 191), exits 199-202 | 191 (197), 205-208 |
| strip push (sine.inOut) | from each landing (124 / 147 / 172) to B10 f35 | 130 / 153 / 178 -> 243 |
| tail handle: strips, no caption | 202-208 | 208-214 |

`cues.json`: `{"events": {}}` (unchanged: the plan gives B9 no SFX and no music event).
`tesseract_shots.json`: B9-gta1-chase-L1 `start_f` 0, `end_f` 120, `source_in_s` 314.1, crop unchanged, `framing.keys` as above.
`footage.json`: windows unchanged (the strips start on the new "They" frames at media 0).

**Cross-beat note**: `b16-bug-origin/tools/make_rewind.py` reads this shot's `source_in_s` / `start_f` / `crop` live; its
B9 frames move 0.2 s later in the source if B16 re-runs it (no other effect). Nothing in this composition depends on the
L1 in-point any more (the dot track is gone).

**Verification (v02)**
* `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings: `timeline_track_too_dense` (caption lanes 9/10),
  craft `first_frame_empty` (transparent head handle by design), `line_unread` on the voice-timed groups "The" (4f),
  "stop", "trying", "to drive" and the beat-segment "let go." (the voice sets the timing, as in the kit table).
* Snapshots `review/v02/` (read): every caption word (local 7 ... 197), the L1 -> L3 cut (125/126), pops and punch
  landings (128, 130, 149, 174), the "let go." exit (205, 207), handles (0, 208, 213); sheets `review/v02/sheet_a.jpg`,
  `sheet_b.jpg`. Max 2 words on screen in every frame, each word visible on its onset frame, Coolvetica, no dot / path /
  arrow anywhere.
* Render (v02): `cd hyperframes/b09-throughyou && npx --yes hyperframes@0.9.52 render . --format mov --workers 2 -o
  ../../05_GFX/renders/b09-throughyou.mov`: ffprobe prores 4444, 1920x1080, 30 fps, **214 frames** (= 202 + 12),
  `yuva444p12le`; alpha checked on the render: frame 60 transparent except the caption (841 opaque px), frame 150 fully
  opaque (strips).

---

# v01 reference (beat 215f; superseded where the v02 section above says otherwise)


Plan: B9 build p.23-24, overview p.18, T1/T4 p.11-12, L1/L3 p.14, B-roll p.31 (R9.1-R9.5), style kit p.9-11.
Storyboard: STORYBOARD.md B9. Frames are **beat frames** (f0 = "The"; local frame = beat frame + 6).
Words: The@0 police@5 cars@15 stop@22 following@29 you@49 and@52 start@56 trying@65 to@73 drive@77 straight@84
through@100 you.@108 They@127 ram.@136 They@151 chase.@158 They@178 don't@185 let@196 go.@202.

## 1. What the viewer sees
A desaturated GTA 1 top-down chase: a white dot sits on the player's car while a dotted yellow line draws the
"normal" chase path curving in behind it; on "straight" a red arrow shoots straight at the dot and through it and the
dot shakes - and in the footage underneath a police car drives straight down into the player's car. Hard cut on
"They ram." to three vertical strips that pop in one per phrase (the GTA 1 ram, a GTA 2 police swarm, a London 1969
van chasing the player), each with its phrase.

## 2. Assets
- B-roll (real, see "Footage used"): **R9.1** (L1 chase, Tesseract; and strip 1 "They ram.", HF = SUBSTITUTE for the
  missing R9.2), **R9.3** (strip 2 GTA 2), **R9.5** (strip 3 London 1969). R9.4 (GTA 1 in 4K) listed in the plan's
  B9 B-roll, not placed.
- SFX: none (plan: "no SFX; the music is building and the voiceover is dense"). Music: MU3 runs (no event here).
- Fonts: Inter Medium 46 (T1), Inter Medium 44 (T4).
- Graphics: the path diagram (inline SVG: white dot, dotted #FFE14D path, #E3262E arrow), L3 strips (kit), camera
  shake (kit `M.shake`). Strip grade: media treatment 60% saturation + a little contrast (matches Tesseract `b9-sat60`).

## 3. Tool and layer stack
TS+HF f0-127: Tesseract L1 R9.1 (`tesseract_shots.json` B9-gta1-chase-L1) under this transparent overlay. HF-owned
(opaque) f127 to the end. Top to bottom:
1. `#b09-cap-1..5` T1 captions (z 40)
2. `#b09-t4` T4 phrases (z 30), local 133 to the end
3. `#b09-diagram` (z 20; untimed, pushed like the L1 shot) > `#b09-dg` (clip, local 0-133) > SVG > `#b09-track`
   (per-frame translation onto the player's car) > path (masked reveal) < dot `#b09-dot` < arrow `#b09-arrow`
4. `#b09-grid` L3 three strips (z 2): ground ink black, `#b09-s1..3` with `.rc-l3__media` (punch/push) > video

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b09-throughyou"]`)
| beat f | what | values / ease |
|---|---|---|
| -6..0 | head handle: transparent, dot already on the car, diagram push continued backward (99.81%) | |
| 0 | X1 hard cut from B8's black (Tesseract L1, crop 536:302:260:108 = watermark cropped out, see "Footage used"); T1 "The police cars" | |
| 0-127 | diagram pushed exactly like the L1 shot: 100% (f0) -> 104% (f127), centre anchor | linear |
| -6..127 | `#b09-track` = the player's car position per frame (template-matched on every source frame of R9.1 313.7-318.13 s in the shot's crop 536:302:260:108, reduced to 31 keypoints within 12 px, mapped through the L1 105% base scale) | one `set` per frame |
| 22-46 | dotted yellow path draws from the police position S (600, 470) round to the dot (C1 (645, 170), C2 (895, 170)) | masked dash reveal, 24f linear, done before "you" f49 |
| 84-92 | on "straight": red arrow (10 px, solid head 36 x 32) shoots S -> through the dot -> 200 px past it (E (1156.32, 578.17)) | 8f power3.out |
| 86-94 | dot shakes (first frame the arrow is through: the tip passes the dot between f85 and f86) | kit shake, 6 px decaying, 8f, seed 9 |
| 127 | **X1 hard cut on "They ram."** to L3 (8 px ink gutters); strip 1 pops + T4 "They ram." | pop 4f 96->100% + fade, then 4f punch-in to 115% |
| 151 | strip 2 pops + punch + T4 "They chase." | same |
| 178 | strip 3 pops + punch + T4 "They don't let go." | same |
| landed..B10 f37 | each strip's footage keeps pushing 115% -> 115% x 1.04, linear, to the "fun" cut in B10 | rule 7 (held shot) |
Handles: tail (local 221-227) = strips + T4 continue; b10-fun continues the same strips (media-start 82f/58f/31f into
the same windows) and fades the T4 at its f0.

## 5. On-screen text
| text | style | position | beat frames |
|---|---|---|---|
| The police cars | T1 | centred, y 620 | 0 -> 22 |
| stop following you | T1 | same | 22 -> 52 |
| and start trying | T1 | same | 52 -> 73 |
| to drive straight | T1 | same | 73 -> 100 |
| through you. | T1 | same | 100 -> 127 |
| They ram. / They chase. / They don't let go. | T4 | centred in strip 1 / 2 / 3, y 860 | 127 / 151 / 178 -> end (fade at B10 f0) |
Caption starts within +/-0.5f of the voice (words.json comp_t snapped to frames). T-style: T1 -> T4 (B8 = T10,
B10 = T2: rotation holds).

## 6. Audio cues (`cues.json`)
- `{"events": {}}`: the plan gives B9 no SFX and no music event (MU3 already running). Nothing for Tesseract to sync.

## 7. Mistakes to avoid
- Give the diagram >= 1.5 s: it is on screen f0-127 (4.2 s).
- Not full colour yet: L1 at ~60% saturation, strips matched (B10 snaps to full colour on "fun").
- The dot must sit on the player's car: if the L1 `source_in_s`, crop, 105% base or push changes, re-track (TRACK in
  `index.html`).
- No watermark on screen (plan Rule 5): R9.1 carries the uploader's "Sakura240" in every frame at x 100-258, y 352-385
  of the 854x480 upload, so every R9.1 crop starts at x >= 260. Remove it by cropping, never by blur/inpaint/stretch.
- No SFX, no siren wash (X9 only in B1/B5/B14), no glitch here.
- Stretch nothing: the strips are vertical crops of the game pictures (cover), never squeezed.

## Footage used
| R-ID | file | in-out (s, original) | what it shows | link |
|---|---|---|---|---|
| R9.1 | `04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4` | 313.9-318.13 (Tesseract L1, crop 536:302:260:108 = x 260-796, y 108-410: the uploader's "Sakura240" watermark (x 100-258, y 352-385) is cropped out, plan Rule 5; was 736:414:59:40, which showed it low-left for ~4 s) | GTA 1: the player's purple Beast GTS swerves through a junction among police cars, stops, and a police car drives straight down into it | https://www.youtube.com/watch?v=HX8infRFBTc&t=313 |
| R9.1 | same | 318.13-321.0 here (window 318.1-322.4, continues in B10 to 322.2), crop 276:414:274:40 (x 274-550: clear of the watermark, unchanged) | strip 1: the police car rams the Beast GTS (318.1-318.9), the player breaks away with the cops behind as the camera pulls out | https://www.youtube.com/watch?v=HX8infRFBTc&t=318 |
| R9.3 | `04_Broll/_originals/B09/R9.3__GTA2 5 Stars Gameplay [LNqEGdO9HDI].mp4` | 55.6-57.7 here (window 55.6-59.2), crop 288:480:247:0 | strip 2, GTA 2 (5 stars): white-and-blue police cars swarm the junction around the player | https://www.youtube.com/watch?v=LNqEGdO9HDI&t=55 |
| R9.5 | `04_Broll/_originals/B09/R9.5__Grand Theft Auto London 1969 Rampage (NO COMMENTARY) [3f0Zmrg9NUk].mp4` | 566.0-567.2 here (window 566.0-569.0), crop 288:480:96:0 | strip 3, London 1969: a blue van mounts the pavement and keeps driving after the player on foot | https://www.youtube.com/watch?v=3f0Zmrg9NUk&t=566 |

## Substitutions
- SUBSTITUTE (Rule 5): R9.1 GTA 1 Police Chase 001 [HX8infRFBTc] @ 05:18-05:22 for R9.2 (missing: GTA 1 full game not
  downloaded). A GTA 1 ram: a police car drives straight into the player's car, the same moment that ends the L1 shot,
  so the cut on "They ram." continues the source time.

## Interpretations / conflicts
1. **Dot tracking**: the plan's dot "marks the player's car"; the whole diagram (dot, path, arrow) is translated per
   frame so the dot rides the car (GTA 1's camera does not keep the car centred). The schematic S point and path keep
   their shape relative to the dot. Since the watermark-free crop (interpretation 6) the car rides further left
   (screen x ~484-1024), so S sits 360 px left of the dot instead of 720 (S (600, 470), C1 (645, 170), C2 (895, 170),
   E (1156.32, 578.17)) to stay on screen; the TRACK was re-measured in the new crop and keeps the clip's 15 fps steps
   (the dot moves with the car, it does not glide over it).
2. **Arrow vs the real ram**: the arrow fires on "straight" (f84); in the footage the real ram follows at f~117-127
   and continues in strip 1 - the diagram explains it, the footage then shows it.
3. **L3 cut frame**: strips pop in from the cut frame (frame 0 of a pop is empty), as the L3 library's "cells pop in".
4. **Strip 2 content**: the GTA 2 clip at 5 stars shows the police swarming the player (the player fires an electric
   weapon at them); chosen as the densest police moment in the GTA 2 clip for "They chase.".
5. SUGGESTION (not built): R9.4 (GTA 1 in 4K) could replace strip 1 with a sharper ram if one is found; after ~1 s the
   R9.1 strip shows the player escaping at a wider camera zoom, so the ram itself reads mainly at the pop.
6. **Watermark (plan Rule 5: a watermarked clip is unusable)**: R9.1 carries the uploader's "Sakura240" watermark in
   every frame (x 100-258, y 352-385 of the 854x480 upload). The L1 shot's old crop 736:414:59:40 left it readable at
   the lower left for ~4 s, so the L1 crop is now 536:302:260:108 (x 260-796, y 108-410; 16:9 within 0.2%, scaled
   3.58x instead of 2.61x): it is re-cropped out, never blurred, inpainted or stretched. The crop keeps the player's
   car and the police cars (the ramming car enters at the top at ~317.6 s). Its y is 108, not 100, because at y 100 the
   car sits so low at the start (313.7-314.4 s) that the white dot would dip into the T1 caption band (dot bottom 609 >
   592, over "police"); at y 108 the dot bottom stays <= 580. Strip 1 (276:414:274:40) already excluded the watermark.

## Pending / blocking
- Nothing blocking.
- Resolved: the "Sakura240" watermark is cropped out of the L1 shot (interpretation 6); strip 1 already excluded it, so
  no R9.1 frame in B9 shows it. B16's rewind reads this shot's crop live (`b16-bug-origin/tools/make_rewind.py`):
  re-run it after any change here. SUGGESTION: R9.4 (GTA 1 4K, no watermark seen) if a matching chase-and-ram moment is
  found (a sharper picture at this zoom).

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `timeline_track_too_dense` (caption lane),
  `nested_structure_needs_subcomposition` (the SVG diagram), craft warnings (beat segment).
- Snapshots in `review/` (read): local 6, 20, 52, 93, 110 (dot on the car, path, arrow, shake, captions), 128, 133,
  137, 161, 190, 226 (L3 cut, pops, T4 phrases, tail); re-shot after the watermark re-crop (new S / path / arrow).
- Watermark re-crop (L1 536:302:260:108) check: `review/l1-dotcheck-1.jpg` / `-2.jpg` = overlay snapshots at local 6,
  21, 28 ("stop"), 40, 52, 92 ("straight", arrow through), 110, 132 (end) composited over the cropped source frame
  (1920 x 1080, x 1.05 x the push about the centre); green cross = measured car centre, cyan = caption band. Read: the
  dot sits on the car in all eight, no watermark, everything on screen. Measured on every frame of the render
  (local 0-132): dot-to-car centre error max 12.7 px (mean 4.3) outside the intended shake (17.2 px with the 6 px shake
  at local 96); dot bottom <= 579; path/arrow y 65-536, x >= 116.
- `check --json` after the re-crop: 0 errors (same 2 lint + 5 craft warnings as before).
- Render: `cd hyperframes/b09-throughyou && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b09-throughyou.mov`: ffprobe prores 1920x1080, 30 fps, 227 frames, yuva444p12le.
