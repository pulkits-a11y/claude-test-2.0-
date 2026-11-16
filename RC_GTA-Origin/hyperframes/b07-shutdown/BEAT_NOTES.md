# B7 Shut it down - `b07-shutdown` (beat 96f = 3.200 s; composition 108f with 6f handles)

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
