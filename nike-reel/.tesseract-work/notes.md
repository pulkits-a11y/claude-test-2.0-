# Nike reel: working notes

Brief: `Sources/brief/nike_reel_video_prompt.md` (+ three PDFs). 1080x1920, 30 fps, H.264/AAC, -14 LUFS, < 1:20.

## Done (checkpoint 1-2)
- Pre-flight: VO, 3 PDFs, end card (CTA, 16:9 1920x1080, 2.26 s, #030303 vignette, own audio -21.7 LUFS), Archivo variable (wght 100-900, wdth 62-125).
- Brand green from rawcanvas.co: #C9F9B8 (serif keyword colour in the hero; only green on the site). Logo on site: white RAWCANVAS wordmark.
- Drive B-roll: 35/42 downloaded and byte-verified (manifest.tsv). Missing: B20, B36, B55, B80, B81, B82. B77 = other moment of B51 (B51 is the full 42 s video).
  Full-length sources to search: B38 (123 s), B56 (162 s), B75 (12.8 min), B76 (18.3 min).
- VO 1.07x: ffmpeg atempo (69.52 s). Rubber Band compared: same pitch, but fewer periodic (voiced) frames, i.e. more phasiness, so atempo chosen.
  Median F0 213 Hz before/after. Line timings: Timing_Pass.md (matches the prompt's 1.0x cross-check within ~60 ms; "Today?" starts 9.55 s, the prompt's 11.1 s mark is "Less than").
- Tesseract supports what's needed: fontVariations axes, posterizeTime (Stepped look), grain, turbulent displace, displacement, noise, blur, saturation, timeRemap (freeze).

## Waiting on the user
Live clips (3), logo file, Instrument Serif, missing B-roll, reference-reel recordings, end card 9:16 handling, B79/"All at once", B53-B56 placement, captions over placeholders, BTW text effects, VO 1.07 listen check.
