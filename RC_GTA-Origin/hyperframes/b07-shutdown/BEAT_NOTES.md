# B7 Shut it down - `b07-shutdown` (v02 REDESIGN: beat 90f = 3.000 s; composition 102f with 6f handles)

## v02 (REVISION_v02.md) - what changed and why
Client note 3: "at 0:31 the motion graphic is really bad again ... I don't really like the cancelled stamp as well, it
looks amateur ... so just make it turn red or something. Or pull an article broll talking about it's cancellation (if
that exists) and highlight the text which says it." -> **the L5 gray card, the framed clip and all three CANCELLED stamps
are gone.** The article exists and is used: Game Developer (formerly Gamasutra), Jan 31 2011, "Penn: First Grand Theft
Auto Was 'Almost Canned'", https://www.gamedeveloper.com/pc/penn-first-i-grand-theft-auto-i-was-almost-canned-
(manifest R-ID `R7.GD`, a live screenshot of the page, 2232 x 2352 PNG, never edited; the same Gamasutra interview as the
B6 quote). Plus notes 10 (fast pace), 11 (captions word by word, max 2), 12 (Coolvetica), 14 (nothing linear), 15
(zooms), 13 (no grain/vignette/chroma in the beat). Re-timed to the v02 beat map (VO 115%: 96f -> 90f).

### 1. What the viewer sees
Fast full-frame cuts through the office B-roll: a woman with a headset typing in an early-1990s office (push in), the
open-plan office on "above" (zoom out), a DMA Design developer at his desk in 1990, joystick in hand, a game on the CRT,
on "the team" (push in). On "keep" the picture flashes siren red and cuts to the real Game Developer article: the
headline "Penn: First Grand Theft Auto Was 'Almost Canned'" spotlit (the rest of the page dimmed), punching in. On "to"
it cuts to the article body: the sentence "It was almost canned. The publisher, BMG Interactive, wanted to can it"
spotlit while the camera pushes in and drifts to it; a yellow highlighter swipes across "It was almost canned." landing
on "shut" (the picture turns red), then across "The publisher, BMG Interactive, wanted to can it" landing on "down."
(red again). B8 carries the same shot on until it breaks.

### 2. Assets
* R7.1 early-1990s office (archival stock, PublicDomainFootage): window 0.4-9.0 s, crop 576:324:32:0 (16:9 above the
  burned-in watermark band y 335-365).
* R7.3 DMA Design office tour, 1990 (plan B7 B-roll): window 62.6-64.2 s, crop 384:216:0:24 (16:9 of the 384 x 288 VHS).
* R7.GD the article still (`04_Broll/B07/R7.GD__gamedeveloper-2011_penn-gta-almost-canned.png` + `.json` rects; added to
  `footage.json` rids, copied by `tools/sync_footage.py` to `assets/footage/R7.GD.png`).
* Kit: `RCK.cam` push / zoomOut / punchIn, `.rc-t9-hl` + `T.highlight` (T9 highlighter as B4), `X.flash` (the X3 flash
  curve, used on a siren-red multiply layer), the L7 spotlight look (#0A0A0A 65% with a rounded feathered hole, drawn in
  page pixels so it moves with the page), `captionPlanV2` / `captionHTMLV2` / `captionPops`.
* Look: R7.1 / R7.3 archival media treatment (plan p.10): temperature +0.06, saturation -0.2, warm shadows wheel (hue 35,
  0.08, +0.03); no grain / vignette (rule F). The article: no treatment.
* Audio (Tesseract): S06 x3 on the red hits, S07 riser into B8 (unchanged logic).

### 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 captions (white + soft shadow, low line y 860) | z30 three red-hit layers (#E3262E, mix-blend multiply, opacity
only) | z5 E: `#b07-driftE` (translate) > `#b07-camE` (scale) > `#b07-pageE` (static page framing: page x 50-1450, y
1564-2351.5, the article column only) > R7.GD + the two highlighter strokes + the spotlight dim (hole on the sentence) |
z4 D: `#b07-camD` > `#b07-pageD` (page x 23.5-1723.5, y 0-956) > white paper + R7.GD (clip-path crops the "Latest News"
sidebar out: x >= 1495 from y 395) + dim (hole on the headline) | z3 C `#b07-camC` > R7.3 | z2 B `#b07-camB` > R7.1 |
z1 A `#b07-camA` > R7.1. Fully opaque.

### 4. Step-by-step build (local frames; beat f = local - 6)
| shot | local f | picture | camera (all eased) |
|---|---|---|---|
| A | 0-22 | R7.1 @ 0:00.4, woman with headset typing | push 100 -> 108%, easeInOutSine |
| B | 22-31 ("above") | R7.1 @ 0:08.0, the open-plan office | zoom-out 112 -> 100%, easeInOutSine |
| C | 31-41 ("the team") | R7.3 @ 1:03.0, DMA developer at his desk | push 100 -> 108%, easeInOutSine |
| D | 41-58 ("keep trying") | article headline, spotlit | punch-in 112 -> 100% over 10f, easeOutExpo |
| E | 58-102 ("to shut it down.") | article sentence, spotlit + highlighted | push 100 -> 118% + drift (-93, -53) px, easeInOutSine, ONE move on the edit clock from local 58 to b08's "breaks" (b08 local 39); this beat plays its first 44 of 71 frames |
* Highlighter: swipe 1 over "It was almost canned." (page rect 247-605 x 1987-2035) from "to" (58) to 66, easeOutQuart
  (kit T9: 94% across on "shut", 62); swipe 2 over "The publisher, BMG Interactive, wanted to can it" (605-1389) from
  "it" (68) to 76 (94% on "down.", 72).
* Red hits (note 3 "just make it turn red"): kit X3 flash curve on a siren-red multiply layer, peak on "keep" (41),
  "shut" (62), "down." (72): C-3 0 | C-2 11% | C-1 44% | **C 100%** (easeInQuad) | C+1 73% ... C+6 2% | C+7 0
  (easeOutQuad). The first one ramps in over shot C and peaks on the cut to the headline.

### 5. On-screen text (plan: "T1: So the people / above the team / keep trying / to shut it down.")
| group | local f (beat f) |
|---|---|
| So | 6 (0) |
| the people | 9 (3) |
| above | 22 (16) |
| the team | 31 (25) |
| keep trying | 41 (35) |
| to shut | 58 (52) |
| it down. | 68 (62), held through the tail handle |
Each word pops on its own onset (kit T1 pop). Audit: max 2 words on screen, every word first visible on its onset frame,
Coolvetica. The article's own text is the page itself (not a caption).

### 6. Audio cues (`cues.json`, beat frames)
`stamp1` = 35 ("keep"), `stamp2` = 56 ("shut"), `stamp3` = 66 ("down.") = the red-hit peaks (the old stamp words; the
names are kept so the S06 mapping still works: Hit 1/2/3 start 3f / 8f / 4f before so their peaks land here). S07
riser: unchanged logic (`B8.first_black`, from `B7.stamp2`); B8's first black is now its beat f41.

### 7. Mistakes to avoid
* Never edit the article: no retouching, no text changes; only crops (the sidebar) and the camera. Highlight only the
  sentence that says it ("It was almost canned. The publisher, BMG Interactive, wanted to can it").
* Keep the E framing inside the article column (page x <= 1450; the sidebar starts at 1504) and above the PNG bottom
  (2352): the camera numbers are checked for every frame of the 71f move (page x 50-1450, y 1564-2351.5).
* b08-break continues shot E with the same page framing and the same camera function: change both together and re-run
  `hyperframes/b08-break/x4_still.sh`.
* No watermark: keep R7.1's crop above y 324.
* Red only on the three hits (REVISION_v02 G: the red is allowed here because note 3 asks for it).

### Footage used (v02)
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.1 | `04_Broll/_originals/B07/R7.1__Early 1990's office workers archival stock footage [HtJSL-bGo_Y].mp4` | 0.4-1.13 (A), 8.0-8.3 (B) (window 0.4-9.0) | 576:324:32:0 | A: woman with a headset typing, colleagues behind; B: the open-plan office after the pan | https://www.youtube.com/watch?v=HtJSL-bGo_Y |
| R7.3 | `04_Broll/_originals/B07/R7.3__(1990) DMA Design Office Tour [iSoYy4Go_sg].mp4` | 63.0-63.33 (window 62.6-64.2) | 384:216:0:24 | a DMA Design developer with glasses at his desk, joystick in hand, a game on the CRT (1990) | https://www.youtube.com/watch?v=iSoYy4Go_sg&t=63 |
| R7.GD | `04_Broll/B07/R7.GD__gamedeveloper-2011_penn-gta-almost-canned.png` (live screenshot, captured 2026-11-16) | still, local 41-102 (+ b08) | sidebar cropped out | Game Developer, Jan 31 2011: headline "Penn: First Grand Theft Auto Was 'Almost Canned'"; body "It was almost canned. The publisher, BMG Interactive, wanted to can it, as it didn't seem to be going anywhere." | https://www.gamedeveloper.com/pc/penn-first-i-grand-theft-auto-i-was-almost-canned- |
Substitutions: none (R7.1 and R7.3 are the plan's B7 B-roll; R7.GD answers note 3).

---

# v01 reference (SUPERSEDED by the v02 redesign above: no L5 card, no CANCELLED stamps any more)

## B7 Shut it down - `b07-shutdown` (beat 96f = 3.200 s; composition 108f with 6f handles)

Plan p.23 (B7), p.14 (L5), p.17 (stamp motif), p.10 (archival grade). Storyboard B7. CONFLICTS C10, C17.
Render: `05_GFX/renders/b07-shutdown.mov` (ProRes 4444, opaque; no Tesseract shots).

## 1. What the viewer sees
A flat gray card with a tilted, white-bordered early-1990s office clip floating on it: a woman with a headset typing at
her desk, CRT monitors, colleagues in the cubicles behind. Three red CANCELLED stamps slam onto the picture, on "keep",
"shut" and "down", each harder-looking, with a short camera shake; after the third the camera in the clip starts to pan
across the open-plan office. T1 captions in card ink under the picture.

## 2. Assets
* R7.1 early-1990s office workers (archival stock). R7.3 (DMA Design office tour, 1990) is a plan alternative, not
  used: the build names R7.1. R7.2 (green-screen stamp) not used: the kit's CANCELLED stamp is the plan's spec.
* Kit: `.rc-l5__ground`, `.rc-l5__prop` + `.rc-l5__frame` (8 px white border, soft shadow), `M.stampTriple` (Inter
  Black 120 px, #E3262E, rough mask, 130 -> 100 % over 2f, 4 px shake for 4f), `S.push`, `S.propFloat`, `.rc-t1--low`.
* Archival media treatment on R7.1 (plan p.10: desaturate ~20 %, slight warm lift, subtle grain, light vignette).
* Audio (Tesseract): S06 x3, S07 riser.

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 captions (card ink, y 860) · z2 `#b07-cam` (push-in + shakes) > `#b07-prop` (tilt -4 deg, float) > white frame,
R7.1 (800 x 600, 4:3), stamp1-3 · z1 L5 gray ground (outside the camera, never shows a shaken edge).

## 4. Step-by-step build
1. `footage.json`: R7.1 3.6-9.2 s, crop 440:330:110:0 (4:3 from the top 330 px: the burned-in
   "www.PublicDomainFootage.com" watermark at y 335-365 is left out) -> `python3 tools/sync_footage.py`.
2. Video media-start 0 (= original 0:03.6); b08-break plays it on from 3.2 s.
3. Camera push: 100 % at B7 f0 -> 104 % at B8 f35 (the shatter), linear on the edit clock (shared with b08-break).
4. Stamps land on "keep" (local 43), "shut" (65), "down" (76): slam starts 2f before, 130 -> 100 %, shake 4 px for 4f;
   on-screen rotations -8 / -4 / +6 deg (prop -4 deg + stamp -4 / 0 / +10), offsets ~30 px.
5. T1 chunks: "So the people" 6 · "above the team" 23 · "keep trying" 43 · "to shut it down." 61 (local), the last holds
   through the tail handle.

## 5. On-screen text (plan: "T1: So the people / above the team / keep trying / to shut it down.")
| chunk | beat f |
|---|---|
| So the people | 0 |
| above the team | 17 |
| keep trying | 37 |
| to shut it down. | 55 |
CANCELLED x3 (stamp motif) at beat f37, f59, f70.

## 6. Audio cues (`cues.json`)
`stamp1` = 37, `stamp2` = 59, `stamp3` = 70 (beat frames). S06 Hit 1/2/3 (-12, -10, -8 dBFS) start 3f, 8f and 4f
before each landing (peaks 0.09 / 0.26 / 0.12 s). S07 riser: its end lands on B8's first black frame (B8 f45); the
assembly starts it at B7 f77 (C17: the 2.133 s file cannot start on the second stamp and still end on the black).

## 7. Mistakes to avoid
* No watermark: keep the 330 px crop if the R7.1 window changes.
* Never stretch the 4:3 archive into 16:9; the frame is 800 x 600.
* B8 continues this exact card: same layout, push/float functions of the edit frame, R7.1 continuous source time
  (B8 media-start = 3.2 s); re-run `hyperframes/b08-break/x4_still.sh` after any change here.

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.1 | `04_Broll/_originals/B07/R7.1__Early 1990's office workers archival stock footage [HtJSL-bGo_Y].mp4` | 3.6-7.2 (window 3.6-9.2; B8 continues 6.8-8.5) | 440:330:110:0 | woman with a headset typing at her desk, CRT monitors, colleagues behind; the camera starts panning right across the office at ~6.5 s | https://www.youtube.com/watch?v=HtJSL-bGo_Y&t=3 |

Substitutions: none.

## Pending / notes
* Nothing pending. check: 0 errors; warnings = T1/stamp lines under the CLI's reading floor (voice timing) and track
  density.
* Render `05_GFX/renders/b07-shutdown.mov`: 108 frames (beat + 12), 1920 x 1080, 30 fps, yuva444p12le (ffprobe, counted).
