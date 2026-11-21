# Nike reel: working notes

Brief: `Sources/brief/nike_reel_video_prompt.md` (+ 3 PDFs). Now HORIZONTAL 1920x1080 (user, 2026-11-20), 30 fps, H.264/AAC, -14 LUFS, < 1:20.

## Build
- `edit_plan.py`: script lines (VO times), segments, B-roll shots, burst, freeze, reverse.
- `build_edit.py [oleary_f donahoe_f hill_f]`: builds NikeReel.tsrct from scratch (footage, placeholders, VO, captions, TCs, overlays, look, mastering).
  Needs Sources/broll/*.mp4 (download_broll.sh from Drive) and the trimmed mezzanines it makes in mezz/.
- `align_words.py`: script words aligned to Whisper times on the 1.07x VO (`vo_words_aligned.json`).
- `design.py`, `textkit.py` (HarfBuzz layout, verified against Tesseract within 1.4 px), `shaders/vox_type.wgsl` (BTW effects).

## State (v2 build, 81.30 s with estimated clip slots)
- Done: all B-roll lines except L13, TC1-TC3, '2021' overlay, Half Cover shelf/hype/athlete/all at once, captions (own group),
  watermark, grain, stepped animation (hand-keyed 3-frame steps; Posterize Time removed: it delayed exits past cuts),
  freeze + B&W drain (B52), static-shot edge blurs + 5% push, crops for CNBC/WSJ/Bloomberg/ABC7/LilJohn504 bugs, master chain.
- Loudness v2: -14.1 LUFS / -1.52 dBTP (will change once live clips are in).
- Decisions: B44 market-value chart for '2021' (B04 chart is a 2024 chart); freeze moved to B52 (B51's ABC7 logo needs 30% crop);
  B51 used only for the 'hype' shot (B77) with a bottom crop; B79 reversed under 'all at once'; B53/B54/B56 unused;
  B20/B36/B55 substituted by other moments; captions not shown during TCs (TC text is the caption).

## Blocked
- CLIP_OLeary / CLIP_Donahoe / CLIP_Hill: not received; YouTube downloads blocked here (sign-in wall; permission guard).
- B80-B82 (Alo/Vuori) not in Drive, so L13 plays over a dark slot.
- After clips: O'Leary/Donahoe Half Covers (+ person matte), lower thirds, clip captions (transcribe), Hill TC (quote, photo from B60/B61),
  runtime check (trim O'Leary if > 1:20), loudness re-check, critic review (2 critics, >= 8.5), final cut list/placeholder list.
