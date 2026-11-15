# B8 The break - `b08-break` (beat 63f = 2.100 s; composition 75f with 6f handles)

Plan p.23 (B8), p.16 (X4), p.12 (T10), p.36 (MU4). Storyboard B8. CONFLICTS C10, C17. Bug beat (glitch allowed).
Render: `05_GFX/renders/b08-break.mov` (ProRes 4444, opaque; no Tesseract shots).

## 1. What the viewer sees
B7's stamped card simply carries on (same tilted office clip, still panning, three CANCELLED stamps, slow push) under
"Then, something". On "breaks" the whole card shatters into jumping, colour-split blocks for 10f and cuts to black.
On black, "breaks." glitches for 6f, settles clean and holds 12f, then a hard cut to B9. The only fully silent
moment besides the very end (music hard-muted).

## 2. Assets
* R7.1 (continued from B7, continuous source time). Kit: B7's L5 card (same layout, same motion functions), `X.tear`
  (X4, still mode, seed 8), `T.glitch` (T10, seed 8), `.rc-ink`.
* `assets/x4/b08-old.png` = this composition's own frame at local 41 (beat f35) without the tear (made by
  `x4_still.sh`, re-made for the real R7.1).
* Audio (Tesseract): S08 on "breaks"; S07 ends on the first black frame; MU4 15f hard mute.

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 (card ink, y 860, local 6-41) · z30 T10 "breaks." (local 51-75) · z20 X4 tear canvas (local 41-50) ·
z10 ink black (local 51-75) · z2 camera > prop > frame + R7.1 + three landed stamps (local 0-51) · z1 gray ground.

## 4. Step-by-step build
1. `footage.json` = B7's R7.1 window; the video plays from media 3.2 s (B7's 0 + 96f) = original 0:06.8.
2. Card motion: push `1 + 0.04 (e - 900) / 131` and float phase `1.6 pi` on the edit clock = B7's functions, so B7's
   last frame and B8's first frame match.
3. Stamps set landed (B7 rotations/offsets).
4. X4 on "breaks" (local 41 = beat f35): 10f tear, 16 x 9 blocks jumping +/-30 px, some frozen on the old frame,
   6 px RGB split; hard cut to black on local 51 (beat f45).
5. T10 "breaks." on local 51: 6f glitch (51-56), clean from 57, holds 12f to the hard cut at local 69 (beat f63);
   tail handle holds the clean word.
6. T1 "Then, something" local 6-41 (out at the tear).

## 5. On-screen text (plan: "T1: Then, something → T10: breaks.")
| element | text | beat f |
|---|---|---|
| T1 | Then, something | 0-35 |
| T10 (Inter Black, white, on black) | breaks. | 45 (glitch to 51), clean 51-63 |

## 6. Audio cues (`cues.json`)
`breaks` = beat f35: S08 (Glitch + Impact + PowerDown 0.5 s, -6 dBFS, all starting on this frame).
`first_black` = beat f45: S07 riser (from B7) ends here; MU4 hard-mutes the music for 15f from here, then un-mutes in
place (C10). Nothing else: do not fill the silence.

## 7. Mistakes to avoid
* The card before the break must be exactly B7's final state (layout, R7.1 time, stamps, push, float); if B7 or the R7.1
  window changes, re-run `sh hyperframes/b08-break/x4_still.sh` so the X4 still matches.
* B8 and B17 are the same break: same X4 settings and seed 8, same T10 glitch (b17-loop uses 6f on "now?").
* Glitch only here, B2, B16, B17 (motif discipline).

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.1 | `04_Broll/_originals/B07/R7.1__Early 1990's office workers archival stock footage [HtJSL-bGo_Y].mp4` | 6.8-8.5 (B7's window 3.6-9.2, +3.2 s) | 440:330:110:0 | the office clip continuing its pan right across the open-plan office (watermark band cropped off) | https://www.youtube.com/watch?v=HtJSL-bGo_Y&t=6 |

Substitutions: none.

## Pending / notes
* Nothing pending. check: 0 errors; 1 warning (closing line under the CLI's 2 s floor: the plan sets 12f).
