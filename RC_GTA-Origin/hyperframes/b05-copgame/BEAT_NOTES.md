# B5 The cop game - `b05-copgame` (beat 88f = 2.933 s; composition 100f with 6f handles)

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
