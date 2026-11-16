# B11 The flip - `b11-flip` (beat 162f = 5.400 s; composition 174f with 6f handles)

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
