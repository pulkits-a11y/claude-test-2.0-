# Retail Pop-Up MG (Raw Canvas / Nike reel)

A 6.5 s, 1920×1080, 30 fps motion graphic for the MG beat at **0:30** in `NikeReel_v4`, styled to sit next to
the reel's 3D TV-screen shot. It's a wet night street. Three miniature storefronts (DSW, Dillard's, Foot Locker)
rise lit, with warm windows, orange Nike shoeboxes and a mint swoosh display inside. Then **each shop dies on its
name**: the sign flickers and glitches out, the windows go dark and the warm spill vanishes from the pavement and
road. Foot Locker only dims to ~30% ("sent less"). A slow push-in runs throughout.

VO: *"Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker."*

## Sync map (MG time → reel time when the clip starts at 0:30.00)

| MG time | Reel | What happens |
| --- | --- | --- |
| 0.0 → 1.0 | 0:30.0 → 0:31.0 | Night street. The three shops rise through the pavement in turn (damped spring) and flicker on |
| 1.15 → 1.6 | 0:31.15 → 0:31.6 | **DSW** dies on "DSW" (0:31.21): sign flicker + displacement-map glitch, windows dark |
| 1.56 → 2.0 | 0:31.56 → 0:32.0 | **Dillard's** dies on "Dillard's" (0:31.61) |
| 3.02 → 3.5 | 0:33.0 → 0:33.5 | **Foot Locker** flickers down to ~30% on "Foot Locker" (0:33.07) |
| 0 → 6.5 | | Slow push-in down the street, fog and lamp haze |

Timing lives in `T` at the top of `assets/scene.js` (`dieDsw`, `dieDill`, `dimFl`).

## The three required effects

- **Turbulent displace**: fractal-noise displacement on every sign's letter edges, a ripple through the pavement
  as each shop breaks through, and turbulence in the swoosh displays as their shops die.
- **Displacement map**: a banded displacement plate (`bandTex`) glitches each sign on as it lands and tears it
  apart as it flickers and dies.
- **Noise inside text**: grain inside every sign's letterforms, boiling on twos.

## Look (matched to the TV-screen shot) and the reel's adjustment stack

- Grade measured from the TV shot: crushed brown-black blacks with a mint lean, olive mids with the blue pulled
  out, cream highlights, plus a heavy vignette with a soft hotspot behind the stores.
- Night street: wet asphalt with real mirror reflections (a second, mirrored render pass) broken up by puddles,
  ripples and vertical streaking. Wet slab pavement, a granite kerb, two street lamps with soft shadows and haze
  cones, dark neighbouring buildings, and fog.
- Glow: two-radius bloom on signs, windows and lamps.
- `assets/textures/grunge-353.jpg`: Soft Light 18%, scaling 100 → 105% over the shot.
- `assets/textures/grunge-351-halftone.jpg`: Overlay 6% as the screen mesh, locked to the pixel grid.
- Grain: light everywhere, heavier in the mids. `grunge-352.jpg` is kept as the backup plate;
  `style-ref-tv-shot.png` is the reference frame.

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
