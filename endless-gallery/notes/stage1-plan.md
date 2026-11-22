# Endless Gallery MG — Stage 1 plan

Status: **planning only, nothing built yet.** Waiting on the missing reference files and the decisions listed at the end.

- Deliverable: 1920×1080, 30 fps, 84 frames (2.80 s), no audio, no text.
- Placement: replaces 0:51.10–0:53.90 of NikeReel_v9.
- Tool: Tesseract 0.8.0 (`tsrct`), checksum-verified and installed in this session.

---

## 1. Measured word timings

These come from the v9 audio, measured two ways: the loudness envelope at 10 ms resolution, plus a whisper `small.en` word transcript. Frame = MG frame, where 0 is video 51.10.

| Word | Onset frame | MG time | Video time | Brief said |
|---|---|---|---|---|
| "Dunks" | 0 (already speaking) – ends f14 | 0.00–0.47 | 51.10–51.57 | 0.00–0.46 ✓ |
| silence | f15–f18 | | | |
| **"Air"** | **f19** | 0.633 | 51.733 | f19 ✓ |
| "Force" | f25 | 0.833 | 51.933 | "lit by f27 during Force" ✓ |
| "1s" | f32 – ends f44 | 1.07–1.47 | 52.17–52.57 | |
| silence | f45–f48 | | | |
| **"Retro"** | **f49** – to ~f61 | 1.633 | 52.733 | f49 ✓ |
| **"Jordans"** | **f63 (±1)** – ends f78 | 2.10–2.60 | 53.20–53.70 | ⚠ brief has Jordans lit by **f55**, but at f55 the VO is still on "Retro" |
| silence | f79–f82 | | | |
| next line "Until…" | onset at f83 (last frame) | 2.767 | 53.867 | 1 frame of the next line sits under our last frame; harmless |

## 2. Scene layout (my proposed defaults — tell me if any feel wrong)

Units are metres; Tesseract runs at 1000 px/m.

- **Pedestals:** 0.45 × 0.45 m plinths, 1.0 m tall. Matte black stone with subtle veining and slightly bevelled edges.
- **Grid:** 1.5 m between pedestals along a row (X), 2.2 m between rows (Z).
  - The hero row is the **front row** of the hall. That keeps the Phase 2 foreground clean (just polished floor), and the hall extends *behind* it to the horizon.
  - About 41 columns × 27 rows ≈ 1,100 cells. Distance fog takes the far rows to black, so it reads as endless.
- **Shoe orientation:** every shoe is in side profile, **toe pointing right**, with the camera about 20° toward the toe for a three-quarter view. This matches the 0:49 B-roll Dunk.
- **Shoe pattern:** the hero Dunk sits at column 0, with an AF1 on each side.
  - Because a strict left-to-right Dunk→AF1→Jordan sequence would put a Jordan (not an AF1) to the Dunk's left, each row **mirrors at the centre column**: … J A D A J D A J …
  - Odd rows shift the sequence by one, so no diagonal stripes of one shoe.
- **Lamps:** a black cylindrical pendant (Ø 12 cm × 20 cm) on a thin cable rising into darkness, 1.6 m above each pedestal top.
  - Each casts a tight cone (~30°, soft edge) of warm tungsten light.
  - Raster's 2700 K reads as saturated orange, so the exact colour temperature gets tuned against the ShoeboxTower MG.
- **Camera:** 35 mm lens on a full-frame 36 × 24 mm sensor (≈54° horizontal field of view). Shallow focus in Phase 1, deep focus by Phase 3. No shake, no roll.

## 3. Frame-by-frame plan (0–83)

Camera positions are (x, height, z) relative to the hero pedestal base. Every move uses custom curves; nothing is linear.

| Frames | VO | Camera | Lights | Effects / grade |
|---|---|---|---|---|
| **0–3** | "Dun-" | (−0.25, 1.08, −0.66): low three-quarter, Dunk ≈40% of frame width, sharp; background soft | Hero spot **already on**, ~20% brighter than the later standard | Turbulent Displace shudder on the hero cone and pool, decaying over 4 frames. Grain inside the beam from f0 |
| 4–18 | "-ks." / silence | Slow push-in ~8% closer plus a 2.5° orbit toward the toe, ease in-out | Hero spot steady | Dust motes drift through the cone; low-level haze turbulence |
| **19** | **"Air"** | **Snap pull-back begins** | | |
| 19–28 | "Air For-" | ~85% of the distance covered in 9 frames (expo-out), cranes up to 1.75 m, tilts slightly down | Ripple starts: AF1 at +1 on at f23, −1 at f25 (each with its own shudder) | **Displacement jolt f20–22** (Grunge 353, peak at f21) |
| 25–27 | "Force" | Braking hard | **Both AF1s lit by f27** | |
| 28–48 | "-orce 1s" / silence | Slow drift to (0, 1.85, −8.4); ~7 pedestals across the frame | Outward ripple with irregular gaps: ±2 at f30/f32, ±3 at f35/f37, ±4 (pools at frame edges) at f40/f43 | Hero spot dims to standard brightness over f30–44 |
| **49** | **"Retro"** | **Second, bigger snap begins** | | |
| 49–57 | "Retro" | 85% of the move in 8 frames: pull back and crane up to ≈(0, 5.5, −13), tilt ~5° down | Cascade starts row by row behind the hero row, racing toward the horizon | **Displacement jolt f50–52** |
| 57–65 | "-tro Jor-" | Hard brake into a slow drift. Final framing is symmetrical: hero row along the bottom edge, vanishing point slightly above centre | Cascade continues to the far rows by ~f61. Nearer lamps shudder as they catch; far ones just pop on. **Nearest Jordans lit by f63** (see question 3) | Haze catches every cone; receding lamp lines read clearly |
| **66** | "-dans" | Still drifting (never stops) | First failures in the far rows | **Grade starts draining** |
| 66–83 | "-dans" + silence | Slow drift to (0, 5.8, −13.8) | Random lamps stutter 2–3 times, then die, spreading irregularly closer. **40–50% dark by f83**; nearest 2–3 rows mostly lit | Saturation down to ~30%, warm shifts toward grey, exposure −15–20%, Jordan red clearly muted. Haze thickens with a slow crawling Grunge 353 displacement. Turbulent Displace on each dying cone and pool |
| **83** | | | Half-dark, cold hall | Last frame. **Hard cut. No fade.** |

## 4. How the three compulsory effects are built (all native Tesseract)

- **Displacement map (Grunge 353):** a `customShader` layer effect whose texture input is a Grunge 353 image layer. It has keyframed amount and offset params: two 3-frame jolts, plus a slow crawl on the haze in Phase 4.
- **Turbulent Displace:** a `customShader` that displaces using animated fractal noise (or the native `turbulentNoise` layer as its map).
  - Per lamp: a quick 3–4 frame shudder on switch-on and on failure.
  - Whole frame: a constant, very faint warp in the haze.
- **Noise inside the light:** each spotlight's **gobo** (`projectorSource`) is an animated noise layer, so the grain is physically inside every beam and pool. It also lands on the pedestal faces. A luminance-limited `grain` effect on top matches the printed texture of the reel's type.
- **Grade:** native `primaryGrade`, `hueSaturation`, `temperatureTint`, `exposure` and `vignette`, keyframed for the Phase 4 drain.

## 5. Technical findings and risks

- **Models:**
  - The AF1 and Jordan wouldn't import until an unused third UV channel (`TEXCOORD_2`) was stripped. No texture uses it, so this is lossless and the originals are kept.
  - The Jordan file is a pair plus a shoebox; I'll keep only the left shoe.
  - The Dunk is a lumpy phone scan with an *unlit* material (see `model-check/model-check-sheet.png` and question 1).
- **Renderer:** this cloud machine has no GPU (CPU, 4 cores).
  - **Raster:** 300 pedestals + shoes render in ~40 s/frame at draft quality, so final quality is likely a few minutes per frame (a few hours for 84 frames).
  - **Path tracer:** works, but takes 44 s for *one box* at draft samples, and its denoiser download was blocked by this session's permissions.
  - Raster draws distance fog; whether it draws volumetric beams is unconfirmed (it didn't in my test). Fallback: soft emissive "beam" cones with noise.
- **Lights:** spotlights placed inside a Tesseract grid array didn't light anything in my test, and one configuration threw a numeric render error. Individually placed, aimed spots work fine.
  - Plan: real spotlights for the near rows (where shoes are readable).
  - Far rows: emissive lamp lenses, light-pool decals and beam cones. At that distance they read the same and cost almost nothing.
  - Lamp failures are animated per lamp from a seeded list, so they're irregular but reproducible.
- **Level of detail:** Tesseract has no LOD system. I'll make reduced-detail copies of each shoe (geometry and textures) for rows beyond ~12 m. A row never switches version during the shot, so nothing can pop.

## 6. Still needed from you

**Missing files** (none of the attachments reached this cloud session). Please drop them in the same Google Drive folder as the models; I can pull from there directly.
1. `ShoeboxTower_full_r2.mp4`
2. Vibe still A (endless gallery)
3. Vibe still B (three sneakers, green stripes)
4. The storefront still
5. Grunge 353 and Grunge 352 (Texture Labs)

**Decisions:** see the questions in the chat message (the Dunk model, the renderer, the "Jordans" beat, and whether to bake in the vignette and grain).
