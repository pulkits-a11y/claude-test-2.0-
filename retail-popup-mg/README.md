# Retail Pop-Up MG (Raw Canvas / Nike reel)

A 6.233 s (187 frames), 1920×1080, 30 fps motion graphic that fills the reel's MG slot exactly:
**0:27.633 → 0:33.867** in `NikeReel_v4` (the "MG" placeholder, measured frame by frame). Three miniature
storefronts (DSW, Dillard's, Foot Locker) pop up through a studio floor, one per VO mention. Then the camera
pulls back, a mint Nike swoosh flashes above them and dissolves away, and it ends on the three stores alone.

VO: *"His plan? Cut out the middleman. Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker."*

## Sync map (place the clip at 0:27.633)

| MG time | Reel | What happens |
| --- | --- | --- |
| 0.00–2.9 | 0:27.6–0:30.5 | "Cut out the middleman": the camera cranes down from high over a dark floor while three plot outlines draw on |
| 2.95 → 3.57 | 0:30.6 → 0:31.2 | **DSW** breaks the floor, rises, overshoots, drops, bounces and settles. The sign switches on at "DSW" (0:31.21) |
| 3.38 → 4.03 | 0:31.0 → 0:31.7 | **Dillard's** pops (heavier: lower hop, less bounce). The sign switches on at "Dillard's" (0:31.61) |
| 4.0 → 4.85 | 0:31.6 → 0:32.5 | Camera trucks right to frame the third plot |
| 4.83 → 5.44 | 0:32.5 → 0:33.1 | **Foot Locker** pops. The sign switches on at "Foot Locker" (0:33.07) |
| 4.85 → 6.23 | 0:32.5 → 0:33.87 | Slow pull back and crane up. Reveal of all three |
| 5.36 → 5.68 | 0:33.0 → 0:33.3 | Swoosh draws on (displacement-map wipe) |
| 5.78 → 6.08 | 0:33.4 → 0:33.7 | Swoosh breaks up and fades (turbulent displace + dissolve) |
| 6.08 → 6.23 | 0:33.7 → 0:33.87 | Clean frame of the three stores for the cut |

## The three required effects

- **Turbulent displace**: fractal-noise displacement on every sign's letter edges (organic, printed). A turbulent
  ripple churns the floor where each building breaks through, then rings out on impact. The swoosh's edges
  stay turbulent and break apart on exit. Code: `SIGN_FRAG`, `POST_FRAG` (zones/rings) and `SWOOSH_FRAG`.
- **Displacement map**: a banded displacement plate (`bandTex`) glitches each sign into place as its store lands.
  A noise displacement map (`noiseTex`) drives the swoosh's draw-on wipe and its dissolve.
- **Noise inside text**: every sign and the swoosh carry grain inside the letterforms, boiling on twos. It matches
  the "WHAT HAPPENED?" title at 0:23. The post pass adds luminance-weighted grain and leaves the `#111111`
  ground flat, so it matches the reel's title cards.

## Look

Flat `#111111` ground everywhere except a soft light pool under the stores, the same as the reel's title cards.
There's no colour grade, so it cuts against footage without a colour jump. Off-white sign ink, and the mint accent
`#c4f0b4` for the swoosh only. Grain matches the type at 0:23: inside the letters and on lit surfaces, but none on
the ground. Warm key light from front-left with soft shadows, cool rim from behind and a slowly turning environment,
so glass reflections sweep. The models have tight bevels, weathered/mottled materials, stone joints, paving joints,
downpipes, contact shadows and base occlusion.

## Files

- `index.html`: root composition (1920×1080, 6.5 s) and the linear GSAP clock that drives the scene.
  Colour variables are `ground`, `accent` and `ink`.
- `assets/scene.js`: the whole 3D scene, motion, shaders and post pass. Every frame is a pure function of time.
- `assets/lib/`: vendored, pinned three.js r170 (+ RoomEnvironment, RoundedBoxGeometry) and GSAP 3.14.2.
- `assets/logos/` (all trademarks of their owners):
  - `dsw.png`: DSW wordmark from DSW's own CDN (assets.designerbrands.com).
  - `footlocker.svg`: Foot Locker logo from footlocker.com.
  - `nike-swoosh.svg`: swoosh path as served by footlocker.com's brand-logo library.
  - `dillards.svg`: Dillard's wordmark vector (companieslogo.com; tagline cropped out). dillards.com blocks
    automated downloads. If you have the official file from Dillard's brand/press materials, drop it in with
    the same name.

## Commands (run inside this folder)

```bash
npx hyperframes preview --background
```

```bash
npx hyperframes snapshot --at 1.2,1.8,3.3,5.0
```

```bash
npx hyperframes render -q draft -o renders/retail-popup-mg_preview.mp4 --player-ready-timeout 180000
```

```bash
npx hyperframes render -q delivery -o renders/retail-popup-mg_final.mp4 --player-ready-timeout 180000
```

Renders here run on software WebGL (~1.8 s a frame). A machine with a GPU is much faster.
