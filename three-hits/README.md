# Three Hits: Tariffs → China → 2028 (Raw Canvas, Nike reel MG)

A 6.47 s 3D motion graphic for 1:04.53–1:11.00 of the Nike reel. The orange Nike shoebox from the Shoebox Tower MG takes three hits along one continuous sideways camera move:

1. A customs stamp slams **TARIFF** onto it.
2. The China stack of 4 loses its top box (−26% in one quarter).
3. The 2025–2028 row dims down to the 2028 lamp dying.

It's built with **Tesseract by Mirage** (CLI 0.8.0). Every scene, light, camera, material, keyframe, text layer and effect is native and editable in `ThreeHits.tsrct`. Blender was used only as the rigid-body solver for the knocked-off box, and its result is baked into ordinary keyframes.

## Folder

| Path | What |
|---|---|
| `ThreeHits.tsrct` | Editable Tesseract project, with all assets and fonts packaged inside |
| `Exports/` | Final MP4s (with typography and clean) and the ProRes master |
| `BEATS.md` | Frame-accurate beat sheet against the narration |
| `build/` | Source that generates the project: `layout.py` (stations, camera), `stage.py` (Scene3D), `overlay.py` (type and effects), `make_assets.py` (TARIFF ink, dust, stamp textures) |
| `build/physics/` | The knock-off sim (`knock_blender.py`) and its baked track |
| `assets/fonts/` | The same font files as the Shoebox Tower MG: Archivo SemiCondensed Black, Instrument Serif Regular and Italic (SIL OFL, licences included) |
| `assets/logo/` | The Nike swoosh used in the Shoebox Tower MG (Wikimedia Commons vector, native proportions) |
| `assets/generated/` | The Shoebox Tower cardboard textures, plus the TARIFF ink, dust sprite and stamp textures baked here. Local only, because they derive from the licensed Texture Labs maps |
| `assets/textures/`, `assets/reference/` | Supplied Texture Labs maps and reference media. Kept local and not committed |

## Layer structure (top first)

- `100` Adjustment: impact jolts (Grunge 353 displacement map; 3 frames on the stamp hit, 2 on the knock-off)
- `200` Group: **TYPE** ("China", "−26%", "in one quarter", the four years). Hide it for the clean version. The TARIFF ink is part of the 3D scene and stays.
- `300` Adjustment: film grain. `310` Adjustment: grade (teal-green shadows, warm highlights, vignette).
- `16` Dust (stamp burst, knock-off puff, turbulent swirl) · `15` 2028 beam (stutters and distorts as it dies) · `14` Haze (spotlight cones, turbulent drift) · `12` Floor reflection (mirror pass) · `11` Stage (lit set, boxes, stamp, ink) · `10` Backdrop (dark shapes, square dust motes)
- `901–902`: Grunge 353 map layers, consumed as shader inputs and never painted

## Rebuilding

```bash
python3 build/make_assets.py
<blender-python> build/physics/knock_blender.py build/physics
python3 build/build.py
tsrct export --project ThreeHits.tsrct --fps 30 --samples 4 --output Exports/ThreeHits_MG_full.mp4 \
  --encoder-backend external-ffmpeg-command --ffmpeg-path /usr/bin/ffmpeg
```
