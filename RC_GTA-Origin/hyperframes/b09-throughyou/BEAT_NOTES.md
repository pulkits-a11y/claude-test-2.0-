# B9 Straight through you - `b09-throughyou` (beat 215f = 7.167 s; composition 227f with 6f handles)

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
| 0 | X1 hard cut from B8's black (Tesseract); T1 "The police cars" | |
| 0-127 | diagram pushed exactly like the L1 shot: 100% (f0) -> 104% (f127), centre anchor | linear |
| -6..127 | `#b09-track` = the player's car position per frame (template-matched on R9.1 313.7-318.14 s, mapped through the L1 105% base scale) | one `set` per frame |
| 22-46 | dotted yellow path draws from the police position S (240, 470) round to the dot | masked dash reveal, 24f linear, done before "you" f49 |
| 84-92 | on "straight": red arrow (10 px, solid head 36 x 32) shoots S -> through the dot -> 200 px past it | 8f power3.out |
| 87-95 | dot shakes (first frame the arrow is through) | kit shake, 6 px decaying, 8f, seed 9 |
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
- No SFX, no siren wash (X9 only in B1/B5/B14), no glitch here.
- Stretch nothing: the strips are vertical crops of the game pictures (cover), never squeezed.

## Footage used
| R-ID | file | in-out (s, original) | what it shows | link |
|---|---|---|---|---|
| R9.1 | `04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4` | 313.9-318.13 (Tesseract L1, crop 736:414:59:40) | GTA 1: the player's purple Beast GTS swerves through a junction among police cars, stops, and a police car drives straight down into it | https://www.youtube.com/watch?v=HX8infRFBTc&t=313 |
| R9.1 | same | 318.13-321.0 here (window 318.1-322.4, continues in B10 to 322.2), crop 276:414:274:40 | strip 1: the police car rams the Beast GTS (318.1-318.9), the player breaks away with the cops behind as the camera pulls out | https://www.youtube.com/watch?v=HX8infRFBTc&t=318 |
| R9.3 | `04_Broll/_originals/B09/R9.3__GTA2 5 Stars Gameplay [LNqEGdO9HDI].mp4` | 55.6-57.7 here (window 55.6-59.2), crop 288:480:247:0 | strip 2, GTA 2 (5 stars): white-and-blue police cars swarm the junction around the player | https://www.youtube.com/watch?v=LNqEGdO9HDI&t=55 |
| R9.5 | `04_Broll/_originals/B09/R9.5__Grand Theft Auto London 1969 Rampage (NO COMMENTARY) [3f0Zmrg9NUk].mp4` | 566.0-567.2 here (window 566.0-569.0), crop 288:480:96:0 | strip 3, London 1969: a blue van mounts the pavement and keeps driving after the player on foot | https://www.youtube.com/watch?v=3f0Zmrg9NUk&t=566 |

## Substitutions
- SUBSTITUTE (Rule 5): R9.1 GTA 1 Police Chase 001 [HX8infRFBTc] @ 05:18-05:22 for R9.2 (missing: GTA 1 full game not
  downloaded). A GTA 1 ram: a police car drives straight into the player's car, the same moment that ends the L1 shot,
  so the cut on "They ram." continues the source time.

## Interpretations / conflicts
1. **Dot tracking**: the plan's dot "marks the player's car"; the whole diagram (dot, path, arrow) is translated per
   frame so the dot rides the car (GTA 1's camera does not keep the car centred). The schematic S point and path keep
   their shape relative to the dot.
2. **Arrow vs the real ram**: the arrow fires on "straight" (f84); in the footage the real ram follows at f~117-127
   and continues in strip 1 - the diagram explains it, the footage then shows it.
3. **L3 cut frame**: strips pop in from the cut frame (frame 0 of a pop is empty), as the L3 library's "cells pop in".
4. **Strip 2 content**: the GTA 2 clip at 5 stars shows the police swarming the player (the player fires an electric
   weapon at them); chosen as the densest police moment in the GTA 2 clip for "They chase.".
5. SUGGESTION (not built): R9.4 (GTA 1 in 4K) could replace strip 1 with a sharper ram if one is found; after ~1 s the
   R9.1 strip shows the player escaping at a wider camera zoom, so the ram itself reads mainly at the pop.

## Pending / blocking
- Nothing blocking.
- Known: R9.1 (the plan's GTA 1 chase clip) carries the uploader's faint "Sakura240" watermark in every frame (lower
  left). Strip 1's crop excludes it; in the L1 shot it sits in the soft-edge zone at the lower left (a tighter crop
  would zoom the car out of frame and invalidate the dot track). SUGGESTION: R9.4 (GTA 1 4K, no watermark seen) if a
  matching chase-and-ram moment is found.

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `timeline_track_too_dense` (caption lane),
  `nested_structure_needs_subcomposition` (the SVG diagram), craft warnings (beat segment).
- Snapshots in `review/` (read): local 6, 20, 52, 93, 110 (dot on the car, path, arrow, shake, captions), 128, 133,
  137, 161, 190, 226 (L3 cut, pops, T4 phrases, tail).
- Render: `cd hyperframes/b09-throughyou && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b09-throughyou.mov` (ffprobe in the lane report).
