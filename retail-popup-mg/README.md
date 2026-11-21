# Retail Pop-Up MG (Raw Canvas / Nike reel)

A 6.5 s, 1920×1080, 30 fps motion graphic for the MG slot at **0:30** in `NikeReel_v4`. Three miniature
storefronts (DSW, Dillard's, Foot Locker) pop up through a studio floor, one per VO mention. Then the camera pulls
back, a mint Nike swoosh appears above them and dissolves away. It ends on the three stores standing alone.

VO: *"Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker."*

## Sync map (MG time → reel time when the clip starts at 0:30.00)

| MG time | Reel | What happens |
| --- | --- | --- |
| 0.00–0.55 | 0:30.0 | Empty studio. Floor-plan outlines draw on for three plots; the camera is already drifting |
| 0.52 → 1.17 | 0:30.5 → 0:31.2 | **DSW** breaks the floor, rises, overshoots, drops, bounces and settles. The sign switches on as "DSW" is spoken (0:31.21) |
| 1.05 → 1.71 | 0:31.1 → 0:31.7 | **Dillard's** pops (heavier: lower hop, less bounce). It lands on "Dillard's" (0:31.61) |
| 1.6 → 2.6 | 0:31.6 → 0:32.6 | Camera trucks right to frame the empty third plot |
| 2.60 → 3.22 | 0:32.6 → 0:33.2 | **Foot Locker** pops. It lands on "Foot Locker" (0:33.07) |
| 3.2 → 6.5 | 0:33.2 → 0:36.5 | Slow pull back and crane up. Reveal of all three |
| 4.12 → 4.78 | 0:34.1 → 0:34.8 | Swoosh draws on (displacement-map wipe) |
| 5.32 → 6.02 | 0:35.3 → 0:36.0 | Swoosh breaks up and fades (turbulent displace + dissolve) |
| 6.0 → 6.5 | 0:36.0 → 0:36.5 | Clean hold of the three stores for the cut |

To move a beat, edit `T` at the top of `assets/scene.js` (emergence start times; landing ≈ start + 0.6 s).

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

Ground `#111111` (exact, same as the reel's cards), off-white sign ink, mint accent `#c4f0b4` for the swoosh only.
Warm key light from front-left with soft shadows, cool rim from behind and a slowly turning environment, so glass
reflections sweep. The models have bevelled edges, contact shadows and base occlusion. There's a light foreground
depth of field and vertical motion blur on the pops.

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
