# Footage pass + finishing brief (shared by the beat agents)

The real B-roll has arrived (downloaded by the user, pulled from their Drive). Every beat now gets its real moments, and the beats that were not rendered yet get finished. The plan (`00_Brief/`) stays the golden rule; read `PRODUCTION_SPEC.md`, `STORYBOARD.md` (your beats), `CONFLICTS.md` and your beats' existing `BEAT_NOTES.md` / `index.html` first. Kit docs: `hyperframes/_kit/KIT_*.md`.

## What is where

* Originals (raw YouTube downloads, many AV1, some 4:3 pillarboxed): `04_Broll/_originals/<Bxx|Textures>/<RID>__<title> [<id>].mp4`. Never edit or move them.
* Contact sheets (5x6 grids, each thumb stamped with its source time): `04_Broll/_sheets/<RID>_sheetNN.jpg` + `<RID>.json` (duration, size, fps, what the plan needs it for). Zoom in: `python3 tools/footage_sheets.py <RID> --range START,END --every 0.5` (writes `<RID>_<start>-<end>_sheetNN.jpg`). Look at sheets with the Read tool.
* The R4.5 design-document title page is a real scan already in `04_Broll/B04/` (still; plan allows < 1.5 s with a push-in).

Available originals: R1.2 R1.3 R1.5 R1.6 R1.7 R14.1 R14.4 (B01) · R3.9 R9.1 (B02) · R3.1 R3.3 R3.6 R3.7 R3.8 (B03) · R5.1 R5.2 R5.4 (B05) · R6.1 (B06) · R7.1 R7.3 (B07) · R9.3 R9.4 R9.5 (B09) · R10.1 R10.2 (B10) · R13.1 R13.2 (B13) · R14.2 R14.3 R14.5 R14.6 (B14) · R15.2 R15.3 (B15) · R17.2 R17.4 R17.6 (B17) · RT1 RT6 (B16).

**Missing** (not downloaded / failed on the user's machine; they may upload later): R17.1 (GTA 6 Trailer 1, Lucia in custody), R17.3 (Trailer 2), R15.1 (Race and Chase gameplay), R15.4, R9.2 (GTA 1 full game), R3.5 (Lemmings PC), RT2, RT3 (police lights), RT7. Plan Rule 5: "Where a beat needs more, or a listed clip is unusable, source additional video yourself and suggest it with a link and timestamp" - so substitute ONLY from other plan-listed clips, and label every substitution in BEAT_NOTES.md as `SUBSTITUTE (Rule 5): <used R-ID> <title> [<youtube id>] @ mm:ss-mm:ss for <missing R-ID> (<why>)`:
* R17.1: look for Lucia in custody / the trailer's opening (police/cell/booking) in R17.4, R17.2, R17.6. If none shows it, keep the labelled stand-in for that one shot and flag it as BLOCKING in BEAT_NOTES (the B17 line needs Trailer 1 on screen).
* R17.3 (GTA 6 chase shots, B1 cell 6 / B17 chases): use official R17.4, R1.2, R17.2 or R17.6.
* R15.1 (full-frame Race and Chase gameplay after the X6 zoom): look in R15.3 and R15.2; else stand-in + flag.
* R9.2 (B9 strip "They ram."): a GTA 1 ram/crash moment from R9.4 or R9.1.
* R3.5 (the tiny walking Lemming): R3.6 (Amiga intro).
* RT3 (B14 police lights under "The sirens."): police lights flashing from a plan clip (e.g. R5.4 night patrol, R1.3, R14.x).
* GTA 6 rule: GTA 6 footage ONLY from official uploads: R1.2 (PlayStation), R17.2 (Netflix), R17.4, R17.6 (Rockstar). Never R1.1 or R17.5.
* Accuracy (plan p.39-40): never show design-document pages about robber modes; never name or imply a GTA 6 voice actor.

## Per beat

1. **Pick the moment** for every R-ID the beat uses from the sheets (zoom where needed): exactly what the plan/storyboard asks for (e.g. "police car in pursuit seen from the cop side", "team at their computers", "Lucia in custody"). Avoid watermarks, burned-in commentary text, channel logos, black frames, UI overlays that aren't game HUD; game HUD colours stay as they are. Prefer moving shots. Note the source time.
2. **Write the moments** into the beat's `footage.json`: `"moments": {"<RID>": {"in": <s>, "out": <s>, "crop": "<w:h:x:y or omit>", "note": "<what it shows>"}}` - seconds in the ORIGINAL file. Make the window as long as the composition needs (source time continuity across beats that continue a shot, e.g. B1->B2 GTA 6 shot, B5->B6 split screen). 4:3 content in a 16:9 upload: crop the pillarbox off; never stretch. Then `python3 tools/sync_footage.py hyperframes/<composition>` (cuts H.264 30 fps working clips into assets/footage; check `assets/footage/SOURCES.json`).
3. **Tesseract-owned shots**: in `tesseract_shots.json` set, per shot, `"source": "04_Broll/_originals/.../<file>"`, `"source_in_s"` = seconds in that ORIGINAL file, optional `"crop"`, and update `"notes"` (what the shot shows). The Tesseract assembly cuts its own working copies from the originals.
4. **Re-fit what was guessed on stand-ins** (your BEAT_NOTES "Pending real footage" list): e.g. the L8 CRT screen rectangle on R3.9, the cabinet screen rectangle on R15.3, the Gary Penn cut-out (R6.1: background removal with the HyperFrames media tools, invoke skill "media-use"), crops, spotlight boxes, path-diagram positions over R9.1.
5. **Finish** any part of the beat that is not done (see "Status" below). Follow the plan one to one.
6. `python3 tools/new_beat.py Bn --refresh` (final kit), `npx --yes hyperframes@0.9.52 check --json` with no errors, snapshots at every caption change, transition and footage change into `review/`, and LOOK at them (Read tool). Check: captions exact + timing, T-style rotation, transparency where Tesseract footage shows, nothing invented.
7. **Render**: `cd hyperframes/<composition> && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/<composition>.mov`; ffprobe: nb_frames = beat + 12, yuva444p12le.
8. **BEAT_NOTES.md**: the plan's 7-part structure (what the viewer sees; assets with R/S/MU IDs; tool + layer stack; step-by-step build; on-screen text; audio cues with frames; mistakes to avoid) + "Footage used" (R-ID, file, in-out, what it shows, link `https://www.youtube.com/watch?v=<id>&t=<s>`) + substitutions + anything still pending.
9. Keep `cues.json` event frames truthful (the audio mix is rebuilt from them).

Boundaries: edit only your beats' folders, their renders in `05_GFX/renders/`, and (for the cover) `hyperframes/cover/` + `07_Exports/RC_GTA-Origin_v01_cover.png`. Do not edit `_kit`, `tools`, `timing`, the shared .md files or other beats; report needed changes. One render at a time, always `--workers 1`; CPU and the account's usage are shared, so be economical: look at what you need, not everything. No git commits.

## Status: done (Nov 16)

All 17 beats and the cover are on real footage and rendered (`05_GFX/renders/`, beat + 12 frames, yuva444p12le); each BEAT_NOTES.md lists the footage used with links, substitutions and anything pending. Still stand-ins: R17.1 (B17 f0-107, BLOCKING for the B17 line) and R15.1 (B15 proof shot). R9.1's uploader watermark is cropped out everywhere (B2, B9, B16). Final export: `07_Exports/RC_GTA-Origin_v01_16x9.mp4` (QA.md).
