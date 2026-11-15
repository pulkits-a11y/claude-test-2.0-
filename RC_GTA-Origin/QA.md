# Final QA checklist (plan p.42) - status per item

"Run every check before exporting; any 'no' goes back to the beat it names."
Status: `PASS` (verified, evidence named), `FAIL` (what, which beat), `PENDING` (waiting on something named), `N/A`.

| # | Check (plan wording) | How it is verified here | Status | Evidence |
|---|---|---|---|---|
| 1 | B1: the first frame is already moving and shows "Why does"; the question reads with the sound off. | Frame 0 and 1 of the export differ; T1 "Why does" visible on frame 0; muted watch-through of B1. | PENDING | |
| 2 | Every caption matches the voiceover word for word, shows at most 4 words at once and is within +/-2 frames of the speech. | Script compares every caption element's text + data-start (all beats) against `01_VO/VO_words_108.json` and the locked script. | PENDING | |
| 3 | No two neighbouring beats feature the same T-style (check against the rotation line). | Per-beat featured T-styles from the compositions vs the plan's rotation line. | PENDING | |
| 4 | Glitch visuals and sounds appear only in B2, B8, B16 and B17; siren wash and sounds only on "cops", "police officer" and "sirens". | Grep compositions for X4/T10/glitch/X9 usage; SFX cue table (S02/S14 sirens on cops/sirens only; S03/S08/S19 glitch only in B2/B8/B17). | PENDING | |
| 5 | Nothing holds still for more than 2 s, except the B6 quote and the B8 black frame. | Frame-difference scan of the export: longest run of near-identical frames per beat. | PENDING | |
| 6 | On "fun" (B10), the music drop, S09 and the X3 flash hit the same frame. | Edit frame of "fun" (1311) = MU5 anchor = S09 start = X3 white hold frame; waveform + frame check. | PENDING | |
| 7 | The B5 and B11 split screens have identical framing, and the flip reads clearly. | Pixel geometry of the L11 frame in B5 vs B11 snapshots; flip mid-frames. | PENDING | |
| 8 | The B12 calendar is the same composition as B4, extended. | Same kit component + same geometry in b04/b12. | PENDING | |
| 9 | Every GTA 6 shot comes from an official Rockstar or PlayStation upload. | Manifest R-IDs used for GTA 6: R1.2, R17.1, R17.3, R17.4 (official); R1.1/R17.5 never used. Real files pending. | PENDING | |
| 10 | The B17 wording decision is made, and the B6 quote carries its attribution. | User decision: keep "It opens with Lucia already caught" with Trailer 1 on screen. B6: "Gary Penn / DMA DESIGN · GAMASUTRA, 2011". | PENDING | |
| 11 | Loudness is -14 LUFS +/-1 with peaks no higher than -1 dBTP, and the voice is clear on a phone speaker. | ffmpeg ebur128 on the final file; tesseract_sound.py measure + mobile-preview. | PENDING | |
| 12 | Watched three times: muted, on earbuds, and on a phone at arm's length. | Cannot be done by an AI; muted pass approximated by frame review; earbuds/phone passes are for you. | PENDING (you) | |
| 13 | Export settings and file name are correct, the cover frame is set, and the post caption credits the footage sources. | ffprobe of RC_GTA-Origin_v01_16x9.mp4; cover PNG; POST_CAPTION.md credits. | PENDING | |
