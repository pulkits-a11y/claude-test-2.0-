# Shoebox Tower — Nike market-value MG (Raw Canvas)

3D motion graphic for MG section 0:09.10–0:22.40 of the Nike reel: Nike's market value as a physical tower of
orange Nike shoeboxes (one box = $10B). 28 boxes rise (2021, ~$280B), collapse to 6 (today, ~$60B), then the
orange box is shoved out of a 10 × 10 wall of 100 grey boxes (S&P 100), leaving 99 and a hole.

Built with **Tesseract by Mirage** (CLI 0.8.0): every scene, light, camera, material, keyframe, text layer,
effect and transition is native and editable in `ShoeboxTower.tsrct`. Blender 5.3 was used only as the
rigid-body physics solver (collapse with breakable lid joints, wall ejection); its results are baked into ordinary
Tesseract keyframes. The street camera's lens is keyed too (35 mm, widening to 26 mm for the hero angle).

## Folder

| Path | What |
|---|---|
| `ShoeboxTower.tsrct` | Editable Tesseract project (all assets and fonts packaged inside) |
| `Exports/` | Final MP4s (with typography / clean), ProRes master (local only, not in git) |
| `Previews/` | Review renders and filmstrips |
| `BEATS.md` | Frame-accurate beat sheet against the narration |
| `build/` | Source that generates the project (see below) |
| `build/physics/` | Blender collapse/ejection sims, the procedural rise, and their baked tracks |
| `assets/fonts/` | Archivo SemiCondensed Black (Archivo wdth 80 / wght 900 instance), Instrument Serif Regular + Italic, Inter Medium — all SIL OFL, licences included |
| `assets/logo/` | Nike swoosh (Wikimedia Commons vector, rasterised at native 2.806:1 proportions) |
| `assets/generated/` | Textures baked from the supplied Texture Labs maps (cardboard, sidewalk, asphalt, levelled Grunge 353 displacement map) |
| `assets/textures/`, `assets/reference/` | Supplied Texture Labs maps and reference media — **kept local, not committed** (licensed / client media) |

## Layer structure (top first)

- `100` Adjustment — Glitch warp: Grunge 353 displacement map on "Today?" (frames 197–200)
- `200` Group — **TYPE** (all typography; hide this group for the clean version)
- `400` Group — Opening card (charcoal) with the Grunge 353 displacement dissolve
- `300` Adjustment — Film grain · `310` Adjustment — Grade (teal shadows / warm highlights, vignette, "Today?" desaturation)
- `20` Scene3D — Stockroom wall (S&P 100): exactly 10 × 10 boxes, revealed by a Grunge 353 displacement wipe
- `13` Ghost tower (dashed outline + faint volume, Add) · `12` Wet-street reflection (mirror pass across the asphalt, lit by a mirrored lamp, Add) · `14` Haze (lamp beam, Screen) · `11` Street (lit set + boxes, lids on simulated hinges) · `10` Backdrop (building silhouettes against the city glow, bokeh windows)
- `901–906` Grunge 353 map layers, consumed as shader inputs (never painted)

The three compulsory effects are Tesseract custom shaders (WGSL, editable parameters):
`turbulentDisplace` (Turbulent Displace), `grunge` (Displacement Map + dissolve with Grunge 353) and native
**Grain** inside every text layer (re-seeded every frame). Puddle ripples are a fourth shader on the reflection.

## Editing

Open `ShoeboxTower.tsrct` in Tesseract, or edit via the CLI (`tsrct project checkout` → edit JSON → `tsrct project commit`).
Typical tweaks: text layers `213/214` (the preceding card's lines), `211/215/212` ("more", "than", "anyone."), `221/224/231/232/240/250`; the "−80%" bracket is group `245`; effect params by effect id (e.g. `-80%` jolt is
effect `2401` param `amount`); camera keys on Scene3D camera items `20003` (street) and `90003` (stockroom).

## Rebuilding from source

```bash
python3 build/make_textures.py          # textures from the supplied Texture Labs maps
python3 build/physics/rise.py build/physics
<blender-python> build/physics/collapse_blender.py build/physics
<blender-python> build/physics/wall_blender.py build/physics
python3 build/build.py                  # writes ShoeboxTower.tsrct
```

Rendering (raster renderer; Linux needs an external FFmpeg for H.264):

```bash
tsrct export --project ShoeboxTower.tsrct --fps 30 --samples 4 --output Exports/ShoeboxTower_MG_full.mp4 \
  --encoder-backend external-ffmpeg-command --ffmpeg-path /usr/bin/ffmpeg
```
