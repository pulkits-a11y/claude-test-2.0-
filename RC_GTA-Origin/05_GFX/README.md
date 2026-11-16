# 05_GFX: reusable graphics pieces

Transparent PNG stills (RGBA, straight from the kit's own rendering, ~16 px transparent padding) of the pieces the Master Edit Plan
(p.41) lists for `RC_GTA-Origin / 05_GFX`. The **animated versions live in the style kit** (`hyperframes/_kit`: `motifs.css/js`,
docs in `KIT_motifs.md`); these stills are the resting states only. Nothing here is newly designed.

| File | Plan ID | Size (px) | What it is | How it was made |
|---|---|---|---|---|
| `M1_stars_hud_40px_x5.png` | M1 | 264 x 72 | 5 wanted stars, 40 px each, cropped | kit `starsPopIn` on `.m1-stars` `data-preset="hud"`, frame after the last pop (stars landed) |
| `M1_stars_hud_40px_x5_fullframe.png` | M1 | 1920 x 1080 | same, full frame, shows the position (row centred on x 1700, y 80; spans x 1584-1816, y 60-100) | same render, uncropped |
| `M1_stars_hero_120px_x6.png` | M1 | 872 x 148 | 6 wanted stars, 120 px each, centred row (in frame: x 540-1380, y 480-600) | `.m1-stars` `data-preset="hero"` + `starsPopIn` |
| `M2_arrow.png` | M2 | 393 x 343 | the yellow "you" arrow (#FFE14D, 6 px stroke, hand-drawn, "you" Inter SemiBold 36 px), fully drawn | `arrowDraw(tl, el, at, { from: [760, 330], to: [500, 610] })` (default seed 7, bend 0.16); in frame at x 494-855, y 302-613 |
| `M3_calendar_18.png` | M3 | 456 x 240 | calendar grid, 18 squares (64 px squares, 8 px gap, 6 columns), all filled (#111111); no card, no counter | `calendarFill(tl, el, at, { slots: 18, filled: 0 })`, after the 18th square |
| `M3_calendar_30.png` | M3 | 456 x 384 | calendar grid, 30 squares: 18 ink + 12 siren red (#E3262E); no card, no counter | `calendarExtend(tl, el, at, { slots: 18, filled: 18, counter: null, to: 30 })`, after landing |
| `M4_bug_chip.png` | M4 | 104 x 88 | bug chip: 72 x 56 px, 12 px radius, #111111, white 8-bit beetle (44 x 40) | `bugChipPop` on `.m4-chip`, after the pop settled (100%) |
| `L8_CRT_plate.png` + `L8_CRT_plate.json` | L8 | 1920 x 1080 (opaque) | CRT plate. The plate is real footage (R3.9), not a graphic, so this is an opaque still of the `_demo-motifs` L8 insert (stand-in plate + R9.1 picture in the CRT screen, error box not yet shown). The JSON holds the screen corners and the CRT grading values (bulge, scanlines, fringe, flicker range) | `hyperframes snapshot --at 24.5` of `_demo-motifs` (demo-only label removed); values from `RCK.motifs.crtSize` / `crtGrading` |
| `error_box.png` | B2 error box | 672 x 216 | Windows 95-style error box, "Race'n'Chase" / "This program has performed an illegal operation and will be shut down." (box itself 640 x 184) | `.m-errbox` + `errorBoxInit`, default width 640 px |
| `CANCELLED_stamp.png` | B7 stamp | 852 x 290 | red CANCELLED stamp (Inter Black 120 px, #E3262E, rough mask, rubber-stamp frame), rotated -8 deg, landed (100%) | `stampSlam(tl, el, at, { x: 960, y: 540, rotation: -8 })`, no camera shake |
| `motifs-star.svg`, `motifs-bug.svg`, `motifs-bug-chip.svg` | M1 / M4 | vector | existing kit SVGs, copied unchanged from `hyperframes/_kit/svg/` | copy |

The stills were rendered by the throwaway project `hyperframes/_gfx-export/` (one 1920x1080 transparent composition, one piece per
window; `npx --yes hyperframes@0.9.52 render . --format mov`, ProRes 4444 with alpha, then ffmpeg `-pix_fmt rgba` + crop to the
alpha bounding box + 16 px). The kit is the source of truth: re-export from there if the kit changes. `renders/` holds the animated renders.
