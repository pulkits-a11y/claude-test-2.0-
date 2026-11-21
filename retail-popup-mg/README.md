# Retail Pop-Up MG (Raw Canvas / Nike reel)

A 6.5 s, 1920×1080, 30 fps motion graphic for the MG beat at **0:30** in `NikeReel_v4`. Three miniature storefronts
(DSW, Dillard's, Foot Locker) rise through a plain `#111111` ground, one per VO mention. Each lands with a lit mint
Nike swoosh on its glass. DSW's and Dillard's swooshes are pulled out of the stores and break apart. Foot Locker's
shrinks and dims ("sent less"). The camera pulls back on three stores, with Nike gone from two and reduced in one.

VO: *"Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker."*

## Sync map (MG time → reel time when the clip starts at 0:30.00)

| MG time | Reel | What happens |
| --- | --- | --- |
| 0.0–0.5 | 0:30.0 | Plain ground. Floor-plan outlines draw on; the camera is already drifting |
| 0.52 → 1.14 | 0:30.5 → 0:31.1 | **DSW** rises on a damped spring (no bounce). The sign switches on at "DSW" (0:31.21) |
| 1.05 → 1.71 | 0:31.1 → 0:31.7 | **Dillard's** rises (most damped, the heaviest). The sign switches on at "Dillard's" (0:31.61) |
| ~1.25 → 2.5 | 0:31.3 → 0:32.5 | DSW's swoosh appears on its window, then gets tugged and pulled out, rising and breaking up |
| ~1.8 → 3.0 | 0:31.8 → 0:33.0 | Dillard's swoosh: the same |
| 2.60 → 3.20 | 0:32.6 → 0:33.2 | **Foot Locker** rises. The sign switches on at "Foot Locker" (0:33.07) |
| ~3.3 → 4.3 | 0:33.3 → 0:34.3 | Foot Locker's swoosh appears, then shrinks to half and dims: "sent less" |
| 3.2 → 6.5 | 0:33.2 → 0:36.5 | Slow pull back and crane up, holding on the three stores |

## The three required effects

- **Turbulent displace**: fractal-noise displacement on every sign's letter edges (organic, printed). A turbulent
  ripple churns the floor where each building breaks through, then rings out on impact. The swoosh's edges
  stay turbulent and break apart on exit. Code: `SIGN_FRAG`, `POST_FRAG` (zones/rings) and `SWOOSH_FRAG`.
- **Displacement map**: a banded displacement plate (`bandTex`) glitches each sign into place as its store lands.
  A noise displacement map (`noiseTex`) drives each swoosh's draw-on wipe and its dissolve as it's pulled out.
- **Noise inside text**: every sign and the swoosh carry grain inside the letterforms, boiling on twos. It matches
  the "WHAT HAPPENED?" title at 0:23. The post pass adds luminance-weighted grain and leaves the `#111111`
  ground flat, so it matches the reel's title cards.

## Look

Plain `#111111` everywhere, with no floor and no light pool, matching the reel's title cards. Off-white sign ink, and the mint
accent `#c4f0b4` for the swooshes only. Grain sits inside the lettering and on lit surfaces, never on the ground.
Warm key light from front-left, a cool rim from behind and a slowly turning environment, so glass reflections sweep.
The stores rise on damped springs: no drop, bounce or squash.

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
