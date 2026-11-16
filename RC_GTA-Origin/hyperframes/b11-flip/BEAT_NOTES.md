# B11 The flip (v02: the glitch) - `b11-flip` (v02: beat 152f = 5.067 s; composition 164f with 6f handles)

## v02 (REVISION_v02.md; client notes 5, 10, 11, 12, 14, 15). Read this first

The v01 sections below are kept as reference; where they disagree with this section (the flip, frames, eases, fonts,
cues), this section wins.

**What changed and why**
| Change | Client note / rule |
|---|---|
| **The 180 deg L11 flip is replaced by B8's glitch**: the kit X4 pixel-block tear with B8's exact settings (b08-break v02: `X.tear(tl, el, at, { frames: 8, seed: 8 })`: still mode, 16 x 9 blocks jumping +/-30 px, 25% freezing on the old frame, 6 px RGB split, kit defaults), on "flips": it tears the front split screen for 8f, then a hard cut to the back split screen (the chased roles). No flip, no flip motion blur, no S10 whoosh | note 5 "instead of a flip animation, add a glitch animation there. for what you used when the voice over said 'it breaks'"; REVISION B11 |
| X4 still rebuilt from B11's own front frame: `assets/x4/b11-old.png` = this composition at local 23 with captions/arrow hidden, captured by `tools/make_x4_stills.py hyperframes/b11-flip` (registered in `x4_stills.json`; `--check` passes, inputs hashed in `assets/x4/SOURCES.json`). Re-run it after ANY change to index.html or the assets | note 5 / KIT_transitions X4 |
| Front = B5's exact framing, as v01: same L11 frame (halves 0-958 / 962-1920), same clips, crops and in-points, and B5 v02's own camera curve (b05-copgame: push 100 -> 108%, easeInOutSine, B5 local 0 -> 89), so B11 local 0-22 repeat B5 local 0-22 frame for frame | REVISION B11, plan p.25 "Watch out" |
| The faces lost the kit's `--front` / `--back` modifiers: the kit auto-inits every `.rc-l11` for the flip (back face at rotationY -180), which with no flip left the back side mirrored (seen in the first snapshots, fixed) | fix |
| Back side: media-start 0.4333 s, so "Now" (local 103) shows the same R9.1 moment as v01 (5:14.83) and the arrow geometry (175, 800) -> (335, 520) still lands on the getaway car | re-timing |
| Re-timed (VO 115%): beat 152f (was 162), edit 1250-1402 (41.667-46.733 s); composition 164f, root `data-duration="5.4666667"` | note 10 |
| T1 word by word, max 2 (kit `captionPlanV2`): So / the team / flips / the / whole game. / You're not / the cop / anymore. / Now you're / the one / being chased. The captions stay above the tear (steady) | note 11, rule A |
| Coolvetica | note 12 |
| Nothing linear; camera (rule D, on `.lc-push` / `.lc-key` inside each half, never on the L11 frame): front = B5's eased push; back = punch-in on the cut 115 -> 100% (10f easeOutExpo), push 100 -> 108% to the end (easeInOutSine), keyword punch 106% on "chased." (3f easeOutExpo, back 9f easeInOutSine) | notes 14, 15 |

**New frames (beat frames; local = beat + 6)**
| What | beat f | local |
|---|---|---|
| front (B5 returned), "So" | 0 | 6 |
| T1 groups first frames | 0, 3, 17, 27, 36, 59, 70, 77, 97, 111, 122 | 6, 9, 23, 33, 42, 65, 76, 83, 103, 117, 128 |
| **X4 glitch** on "flips" (first torn frame = `glitch` cue) | **17** | **23** |
| torn frames | 17-24 | 23-30 |
| hard cut to the back side + punch-in 115% | 25 | 31 |
| punch landed, push starts | 35 | 41 |
| M2 arrow on "Now" (drawn by +8) | 97 (-> 105) | 103 (-> 111) |
| keyword punch on "chased." | 128-140 (onset 129) | 134-146 (onset 135) |
| tail handle: back side + "being chased." held | 152-158 | 158-164 |

`cues.json`: `{"events": {"glitch": 17}}` (replaces `flip_start` / `flip_mid`; = the first torn frame, as B8's `breaks`
cue is its tear's first frame; the assembly maps it to the glitch impact sound).
`tesseract_shots.json`: `"shots": []` (HyperFrames only, opaque). `footage.json`: windows unchanged.

**Cross-beat notes**
* `hyperframes/cover` (not this lane) mirrors v01's B11 back side (local 170, linear 104% push, flip-era media
  timing). If the cover should follow v02 exactly: back side media-start 0.4333 s at local 31, punch-in 115 -> 100%
  local 31-41, push 100 -> 108% (easeInOutSine) local 41 -> 164, arrow unchanged.
* B8's settings are copied from `b08-break/index.html` as its lane revised it for v02 (15:03 UTC: `frames: 8, seed: 8`;
  v01 was 10f). If B8 changes them again, B11 follows with one line (`X.tear(... { frames: N, seed: 8 })`, `CUT =
  GLITCH + N`, the front/back video windows and the back media-start), then `tools/make_x4_stills.py` and a re-render.

**Verification (v02)**
* `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings: `timeline_track_too_dense` (caption lane), craft
  `line_unread` on the voice-timed groups ("So" 3f, "flips", "the", "You're not", "the cop", "the one") and the
  beat-segment "being chased.", contrast 2.61:1 on "the" (local 9, white T1 with the plan's soft shadow over the light
  asphalt of B5's left half; same picture and style as B5, no caption boxes by plan rule).
* `python3 tools/make_x4_stills.py hyperframes/b11-flip --check`: "X4 stills current (1)".
* Snapshots `review/v02/` (read; `sheet_a.jpg`, `sheet_b.jpg`, `sheet_c.jpg`): head handle 0; every caption word (6 ...
  135); the last clean front frame 22; the glitch 23, 25, 27, 29, 30 (front torn, blocks + RGB split, "flips"
  steady above it); the cut 31 (back at 115%), 32, 33, 35, 41 (landed); the arrow 103 / 107 / 111 and its tip on the
  getaway car at 111, 137 (punch peak) and 163; the "chased." punch 135 / 137 / 146; 157; 163. The first pass showed
  the back side mirrored (kit L11 auto-init, see above), fixed and re-shot. Max 2 words on screen, words on their
  onsets, Coolvetica, no flip left.
* Render (v02): `cd hyperframes/b11-flip && npx --yes hyperframes@0.9.52 render . --format mov --workers 2 -o
  ../../05_GFX/renders/b11-flip.mov` (after `make_x4_stills.py --check`): ffprobe prores 4444, 1920x1080, 30 fps,
  **164 frames** (= 152 + 12), `yuva444p12le` (opaque). Frames 22-31 of the render read: clean front, 8 torn frames
  under "flips", the back side on 31 (not mirrored).

---

# v01 reference (beat 162f, the flip; superseded where the v02 section above says otherwise)


Plan p.24-25 (B11), p.15 (L11 incl. the flip), p.17 (M2), p.39 (cover frame). Storyboard B11.
Render: `05_GFX/renders/b11-flip.mov` (ProRes 4444, opaque; no Tesseract shots, `tesseract_shots.json` has none).

## 1. What the viewer sees
The B5 split screen comes back in full colour, exactly as B5 opened (police SUV chasing the taxi | red car fleeing the
police bike). On "flips" the whole split screen turns 180 degrees on its vertical axis over 10f, blurring as it spins
(edge-on and black at the midpoint). The back side is the reverse: left, the player's getaway car in GTA 1 (purple,
white stripes) skidding away from a police car, turning and getting pinned at a corner by the chasing police cars;
right, a police SUV with its lights flashing speeding down a night street. On "Now you're the one" the yellow "you"
arrow draws on again, now pointing at the getaway car.

## 2. Assets
* Front: R5.2, R5.1 (B5's working clips, B5's in-points). Back: R9.1 (left, the getaway car; the plan allows R10.2 or
  R9.1), R5.4 (right, police chasing, as the plan names).
* Kit: `.rc-l11` + `S.splitFlip` (front 0 -> 180 deg, back -180 -> 0 deg, perspective 2666.67 px, `power2.inOut`, motion
  blur = media-treatment blur ramp 0 -> 1 -> 0), `.lc-push` push-ins, `M.arrowDraw` (M2, seed 7 = B5's hand), `.rc-t1`.
* Grade: `{"adjust":{"contrast":0.15},"effects":{"blur":1}}` per face video, inline blur control 0 (game grade, as B5).
* Audio (Tesseract): S10 on the flip.

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z30 T1 captions (y 620) · z20 M2 arrow (screen space, does not flip) · z1 `.rc-l11` (untimed, perspective): ink ground
(divider + the edge-on frame) > front face (R5.2 | R5.1) and back face (R9.1 | R5.4), each half with its `.lc-push`.

## 4. Step-by-step build
1. `footage.json` moments (below) -> `python3 tools/sync_footage.py hyperframes/b11-flip`.
2. Front videos local 0-34, media-start 0 (= B5's in-points), push from 100 % at local 0 at B5's rate, so local 0-23
   repeat B5 local 0-23 frame for frame: "the B5 split screen returns" with identical framing (QA 7).
3. Flip on "flips" (local 24 = beat f18): 10f, 90 deg edge-on on local 29 (beat f23 = `flip_mid`), back lands local 34.
4. Back videos start on the flip (local 24, media 0) and run to the end; held-shot push-in 100 -> 104 % from the landing.
5. M2 on "Now" (local 109 = beat f103): "you" hard-cuts in, drawn by local 117, from (175, 800) to (335, 520): tail on the
   open road at the lower left, tip at the getaway car's rear (from local 109 to 174 the car sits at x ~280-700 and
   drifts from y 375-490 down to y 460-585 as the camera settles, so the tip meets its rear-left corner throughout),
   clear of the police car (x 425-830, y 775-930) and of the T1 line; the top stays free for the cover.
6. T1 chunks (kit `captionPlan`): "So the team" 6 · "flips the whole game." 24 · "You're not the cop" 69 · "anymore." 88 ·
   "Now you're the one" 109 · "being chased." 135 (local frames). No X9 on "cop" (motif discipline).

## 5. On-screen text (plan: "T1: So the team / flips the whole game. / You're not the cop / anymore. / Now you're the one / being chased.")
| chunk | beat f |
|---|---|
| So the team | 0 |
| flips the whole game. | 18 |
| You're not the cop | 63 |
| anymore. | 82 |
| Now you're the one | 103 |
| being chased. | 129 |
M2 label "you" from beat f103.

## 6. Audio cues (`cues.json`)
`flip_start` = beat f18, `flip_mid` = beat f23. S10 Flip (Botanica › Transform, -12 dBFS) peaks at 0.38 s: start it 6f
before the flip (beat f12) so the peak meets the midpoint (f23). No other SFX.

## 7. Mistakes to avoid
* B5 and B11 must share the L11 frame exactly: same CSS halves (0-958 / 962-1920), same crops and in-points on the
  front; never scale the frame itself (push only inside the halves).
* The flip must read: edge-on black frame at f23, blur peaking there, the back side clearly different (GTA 1 top-down
  getaway vs GTA 5 police).
* The arrow must sit on the getaway car (re-check it if the R9.1 in-point changes: the car moves before 5:14.8).
* No siren wash on "cop" (only "cops", "police officer", "The sirens.").

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R5.2 | `04_Broll/_originals/B05/R5.2__Playing GTA 5 As A POLICE OFFICER City Patrol｜ HPD｜｜ GTA 5 Lspdfr Mod｜ [5TAB4i9P1eI].mp4` | 230.5-231.63 (front, local 0-34) | 814:918:713:162 | B5's left half returned | https://www.youtube.com/watch?v=5TAB4i9P1eI&t=230 |
| R5.1 | `04_Broll/_originals/B05/R5.1__GTA San Andreas - Vigilante [12 Levels] [wy95d3TrAIQ].mp4` | 41.2-42.33 (front) | 819:923:405:0 | B5's right half returned | https://www.youtube.com/watch?v=wy95d3TrAIQ&t=41 |
| R9.1 | `04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4` | 312.0-317.0 (back left, local 24-174) | 370:418:257:38 | GTA 1: the player's purple "Beast GTS" skids away from a police car, turns and is pinned at a corner by two chasing police cars (5:14.8-5:17, under the arrow). Crop = picture area only (no black border), the "Sakura240" channel watermark left out; game HUD (Coords, car-name banner) kept | https://www.youtube.com/watch?v=HX8infRFBTc&t=312 |
| R5.4 | `04_Broll/_originals/B05/R5.4__GTA 5 LSPDFR ｜ Sheriff Gang Unit Takes Over the Night Shift 🚔 ｜ DLSS 5 [PV1NfLjkbWg].mp4` | 702.5-707.5 (back right) | 958:1080:562:0 | GTA 5 LSPDFR: the sheriff SUV, light bar flashing (strobing), speeding down a night street, from behind; crop leaves out the mod's report list, minimap, clock, side panel and icons (the speedometer under the car stays) | https://www.youtube.com/watch?v=PV1NfLjkbWg&t=702 |

Why R9.1 and not R10.2 on the back left (plan: "R10.2 or R9.1"): in the R10.2 speedrun the player's car is one of
several small cars with no police near it; R9.1 is a police chase with the getaway car large and clearly the player's.
Substitutions: none (R9.1 is a plan-listed option).

## Pending / notes
* Built from the interrupted stand-in version: real clips, arrow re-aimed, `cues.json`, `tesseract_shots.json` and these
  notes added. Cover = this back side at local 170 (`hyperframes/cover`, `07_Exports/RC_GTA-Origin_v01_cover.png`).
* The R5.4 light bar strobes: lights visible at local ~24-70 and ~160-174, dark in between (source as is).
* check: 0 errors; warnings = T1 chunks under the CLI's reading floor (the voice sets the timing) and track density.
* Render `05_GFX/renders/b11-flip.mov`: 174 frames (beat + 12), 1920 x 1080, 30 fps, yuva444p12le (ffprobe, counted).
