# B5 The cop game - `b05-copgame` (v02: beat 83f = 2.767 s; composition 95f with 6f handles)

## v02 (REVISION_v02.md; client notes 10, 11, 12, 14, 15) - what changed
Re-timed to the v02 beat map (VO 115%: beat 88f -> 83f, composition 100f -> 95f, root `data-duration` 3.1666667) and
the global rules applied. Nothing else changed: same L11 split, same footage windows / crops / positions (B11 reuses this
exact framing for its front side), same M2 arrow (seed 7, same geometry), same X9 wash, no SFX.
* **Rule A (note 11)**: T1 rebuilt with the kit's `captionPlanV2` / `captionHTMLV2` + `T.captionPops`: groups of max 2
  words, each word pops on its own onset (5f easeOutExpo, 1f lead). Groups: In it, (local 7) / you play (20) / a (31) /
  police officer (33) / chasing criminals. (53, held through the tail handle). Measured (headless audit): every word first
  visible on its onset frame, never more than 2 words on screen. "a" is on screen 2f (the voice: kit-reported).
* **Fonts (note 12)**: Coolvetica (kit); the M2 label "you" is Coolvetica too.
* **Rule C (note 14)**: the v01 linear 100 -> 104% push (one linear function across B5 + B6) is gone. 0 linear tweens
  (audit: 19 eased, 4 hard-cut steps = the X9 frames).
* **Rule D (note 15)**: camera inside each 958 px half (the L11 frame never moves): push 100 -> 108% easeInOutSine from
  local 0 to the B5/B6 cut (local 89), where it rests; b06-dull answers it with an eased zoom-out (108 -> 100%) to its X2
  cut. Both compositions play the other's frames in their handles on the same curve (B5 f83 = B6 f0 and B5 f89 = B6 f6,
  pixel-identical). Keyword punch on "police" (local 33, nested `.lc-key` wrapper): 100 -> 106% in 3f easeOutExpo, back
  in 9f easeInOutSine, together with the X9 wash.
* **Rule F**: no grain / vignette / chroma (the grade is contrast 0.15 only, as v01).

| element | v01 local f | v02 local f (beat f) |
|---|---|---|
| T1 groups | 6 / 20 / 32 / 56 (4 chunks) | In it, 7 (1) / you play 20 (14) / a 31 (25) / police officer 33 (27) / chasing criminals. 53 (47) |
| M2 arrow ("you") | 20, drawn by 28 | 20 (14), drawn by 28 |
| X9 wash ("police") | 34-37 | 33-36 (27-30) |
| keyword punch | - | 32-44 (peak 35) |
| push / zoom | linear 100 -> 102.6% (0-100) | push 100 -> 108% (0-89, easeInOutSine), then b06's zoom-out begins (89-95) |
| end | 100f | 95f |

Render `05_GFX/renders/b05-copgame.mov` (v02): ffprobe 95 frames (beat 83 + 12), 1920 x 1080, 30 fps, ProRes 4444
`yuva444p12le`, opaque (alpha 255). `check`: 0 errors (warnings: track density, `line_unread` on groups the voice keeps
short). `cues.json` = `{"events": {}}` (no SFX).
`tesseract_shots.json`: no shots (HF owns every frame). Review stills: `review/v02/`.

---

# v01 reference (superseded where the v02 section above differs; frames below are v01)

## B5 The cop game - `b05-copgame` (beat 88f = 2.933 s; composition 100f with 6f handles)

Plan p.22 (B5), p.15 (L11), p.17 (M2), p.16 (X9), p.11 (T1). Storyboard B5. Render: `05_GFX/renders/b05-copgame.mov`
(ProRes 4444, opaque: HyperFrames owns every frame; no Tesseract shots, `tesseract_shots.json` has none).

## 1. What the viewer sees
A hard cut (X1) into the L11 split screen: left, an LSPD police SUV with its light bar on, seen from behind (the cop's
side), chasing a taxi down a dock road (GTA 5); right, the red target car fleeing ahead of a police motorbike (GTA San
Andreas, Vigilante). On "you" a hand-drawn yellow arrow with "you" draws on and points at the police SUV. On "police
officer" a 4f red/blue siren wash flashes over the footage. T1 captions run underneath the voice.

## 2. Assets
* R5.2 (left half; the plan's alternative to R5.4, see Footage used), R5.1 (right half). R5.3 not downloaded (not needed).
* Kit: `.rc-l11` (L11), `RCK.motifs.arrowDraw` (M2, seed 7), `RCK.transitions.sirenWash` (X9), `.rc-t1` (T1).
* Grade: media treatment `{"adjust":{"contrast":0.15}}` on both halves (plan p.10 "Game footage: punchy contrast; leave
  game HUD colours alone"). No SFX, no music cue (plan: "no SFX; the wash is visual only").

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z30 T1 captions (y 620) · z20 M2 arrow (screen space) · z15 X9 wash · z1 `.rc-l11`: ink-black ground (shows as the
4 px divider x 958-962) + two 958 x 1080 halves, each with an untimed `.lc-push` wrapper (push-in 100 -> 104 % inside the
half, so the L11 frame itself never moves) holding the `<video>`.

## 4. Step-by-step build
1. `footage.json` moments -> `python3 tools/sync_footage.py hyperframes/b05-copgame` cuts 958 x 1080 working clips
   (crops below), media-start 0 = composition local 0.
2. L11 halves: left `assets/footage/R5.2.mp4`, right `assets/footage/R5.1.mp4`, both `data-start 0`, 3.333 s.
3. Push-in: one linear move defined on the edit clock from B5 local 0 (100 %) to the B6 X2 cut (104 %, 155f later);
   B5 covers its first 100f, b06-dull continues it.
4. M2 on "you" (local 20 = beat f14): label hard-cuts in, shaft + head drawn by local 28, `power3.out`; geometry
   from (772, 900) to (552, 728): tail on the asphalt right of the SUV, tip on its right flank, below the T1 line.
5. X9 on "police" (local 34 = beat f28): red 2f, blue 2f, gone on local 38.
6. T1 chunks (kit `captionPlan`, each on its first word's frame): "In it," local 6 · "you play" 20 · "a police
   officer" 32 · "chasing criminals." 56 (holds through the tail handle).

## 5. On-screen text (plan: "T1: In it, / you play / a police officer / chasing criminals.")
| chunk | beat f | local f |
|---|---|---|
| In it, | 0 | 6 |
| you play | 14 | 20 |
| a police officer | 26 | 32 |
| chasing criminals. | 50 | 56 |
M2 label "you" (Inter SemiBold 36 px, #FFE14D) from beat f14.

## 6. Audio cues
None (plan B5 Audio: "no SFX (the wash is visual only here, to keep sirens rare)"). `cues.json` = `{"events": {}}`.
Silence by design B4-B5 (SFX sheet).

## 7. Mistakes to avoid
* Both cars must stay readable: the crops keep the SUV and the taxi (left) and the bike and the red car (right) inside
  each half for the whole window; do not re-crop one beat without the others (B6 continues, B11 returns to this frame).
* Never move or scale the L11 frame itself (QA 7: B5/B11 identical framing); push only inside the halves.
* X9 only on "police officer" (motif discipline); no siren sound here.
* Keep the M2 arrow seed 7 (B11 redraws the same hand).

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R5.2 | `04_Broll/_originals/B05/R5.2__Playing GTA 5 As A POLICE OFFICER City Patrol｜ HPD｜｜ GTA 5 Lspdfr Mod｜ [5TAB4i9P1eI].mp4` | 230.5-233.83 (window cut 230.5-235.8; B6 continues it) | 814:918:713:162 | LSPD SUV (V54, light bar on) chasing a taxi, third person from behind the police car; crop leaves out the AXON bodycam timestamp, minimap, speed HUD | https://www.youtube.com/watch?v=5TAB4i9P1eI&t=230 |
| R5.1 | `04_Broll/_originals/B05/R5.1__GTA San Andreas - Vigilante [12 Levels] [wy95d3TrAIQ].mp4` | 41.2-44.53 (window 41.2-46.4) | 819:923:405:0 | the red target car (red marker over it) fleeing ahead of the police motorbike; crop leaves out radar, TIME LEFT/LEVEL/KILLS HUD, zone-name text | https://www.youtube.com/watch?v=wy95d3TrAIQ&t=41 |

Why R5.2 and not R5.4 on the left (plan: "R5.4 or R5.2"): on its contact sheets (one frame every 10 s, plus a 1 s zoom
at 11:30-12:00) R5.4 (LSPDFR night shift) shows patrol driving with the lights on and on-foot scenes, but no car being
pursued; R5.2 @ 3:50 is a police car pursuing another car, both clearly visible. (B11 uses R5.4 for "police cars
chasing", as the plan asks.)
Substitutions: none (R5.2 is a plan-listed alternative for this half).

## Pending / notes
* Nothing pending. Render `05_GFX/renders/b05-copgame.mov`: 100 frames, 1920 x 1080, 30 fps, yuva444p12le.
* check: 0 errors; warnings = T1 chunks shorter than the CLI's reading floor (timing is the voice's, plan rule) and
  track density (single-file composition by design).
