# Shoebox Tower MG — working notes

## Setup (verified 2026-11-22)
- Tesseract CLI 0.8.0 (fff20c89), linux-x86_64 bundle, SHA-256 ec64c9b4b6eebda8e685697b16f62f8c85283d99062d50af6000fd7bfc32a311 OK.
  Installed at ~/.local/share/Tesseract/bin/tsrct (container-local; reinstall in a new session).
- Skills: 6 tesseract-* skills in repo .claude/skills (upstream commit d3d271d), skills-lock.json.
- Vulkan: Mesa lavapipe (apt mesa-vulkan-drivers) — CPU only, no GPU.
- H.264 export needs: --encoder-backend external-ffmpeg-command --ffmpeg-path /usr/bin/ffmpeg
- Path tracer: denoiser weights download fails (CLI pins its own TLS roots; sandbox proxy re-terminates TLS).
  --no-denoise works. Smoke: raster export ~9.8 s/frame for a 1-box scene; path tracer 16spp no-denoise 35 s/frame.
- Tesseract has no rigid-body physics (cloth only). Effects: TurbulentNoise, Grain, WaveWarp, Ripple, CustomShader (WGSL, layer textures).

## Assets
- textures/grunge-353.jpg (main displacement map, dust/scratches/fingerprints) — mapping by image order, confirm with user
- textures/grunge-352.jpg (softer), textures/grunge-351-halftone.jpg, textures/paper-363.jpg (wrinkled paper)
- reference/storefront-still.webp, reference/tv-room-still.png, reference video v4 (TIMINGS ONLY)

## Brand (sampled from v4 at 720p)
- Mint #CCF0BB (consistent across "?", "needed retail", "obsession", quote mark)
- Off-white type #ECECEC; background ~#111–#131313
- Serif: looks like Instrument Serif (Regular + Italic) — to confirm
- Heavy grotesk (WHAT HAPPENED?): unidentified — need file
- Small sans (captions, "We lost our"): Inter / Instrument Sans-like — to confirm

## Confirmed VO timings (waveform runs + isolated-clip ASR). MG t = video t − 9.10
| word(s) | video | MG |
|---|---|---|
| "more than" | 9.40–9.79 | 0.30–0.69 |
| "anyone." | 9.93–10.43 | 0.83–1.33 |
| "That was" | 10.60–11.0 | 1.50–1.90 |
| "2021." | ~11.09–11.83 | ~1.99–2.73 |
| "Nike" (onset) | 12.00 | 2.90 |
| "…soaring at almost" | –13.41 | –4.31 |
| "280" | 13.46–14.39 | 4.36–5.29 |
| "billion dollars" | 14.51–15.46 | 5.41–6.36 |
| "Today?" | 15.63–15.99 | 6.53–6.89 |
| "Less" (onset) | 16.40 | 7.30 |
| "sixty" | ~16.95–17.28 | ~7.85–8.18 |
| "billion dollars" | ~17.30–18.09 | ~8.20–8.99 |
| "Down almost" | 18.27–18.88 | 9.17–9.78 |
| "80 percent" | 19.01–19.86 | 9.91–10.76 |
| "It even got" | 20.04–20.66 | 10.94–11.56 |
| "kicked" | ~20.53–20.70 | ~11.43–11.60 |
| "out of the S&P" | 20.73–21.70 | 11.63–12.60 |
| "100" | ~21.74–22.09 | ~12.64–12.99 |
| "So" (next card) | 22.40 | 13.30 = hard cut |
