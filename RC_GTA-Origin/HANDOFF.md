# Handoff: continue RC_GTA-Origin in a new chat/environment

## 1. Code + docs (everything small) = git
Repo: https://github.com/pulkits-a11y/claude-test-2.0-  branch `claude/kind-ritchie-wypra4`
```
git clone -b claude/kind-ritchie-wypra4 https://github.com/pulkits-a11y/claude-test-2.0-
```
Contains: plan + all revision notes (REVISION_v02..v05.md, CONFLICTS.md, QA.md), the v05 instruction doc
(00_Brief/refs_v05/), timing (timing/beat_map.json = v05), all 18 HyperFrames beats (hyperframes/b01..b18), the kit
(hyperframes/_kit, KIT_v05.md), every tool (tools/*.py: retime, sync_footage, render_all.sh, build_tesseract*.py,
qa_v05.py), SFX library recipes (03_SFX/v05/library.json), fonts (06_Fonts).

## 2. Media NOT in git (gitignored, too big)
* `RC_GTA_media_pack.tar` (sent with this handoff): 01_VO (source ElevenLabs mp3 + processed VO wavs incl.
  VO_processed_v05.wav), 02_Music, 03_SFX (S01-S19 + v05 library wavs), every beat's hand-cut working clips
  (hyperframes/b*/assets/footage, assets/work). Extract it at the repo's RC_GTA-Origin/ folder.
* B-roll originals (~11 GB, 04_Broll/_originals): re-download from your Drive folders
  (https://drive.google.com/drive/folders/1APIoPV33AJtwUDGXHMSdOKwfdM6C9xBz and the GTA VI library
  https://drive.google.com/drive/folders/1Li0fFSxSyK9EHdm2Y2T8mp5Pjg2TYvHK); file names/R-ids in 04_Broll/broll_manifest.json.
  Only needed to re-cut footage; the pack already has the cut clips.
* Beat renders (05_GFX/renders, 3.4 GB): regenerate with `cd RC_GTA-Origin && WORKERS=3 tools/render_all.sh`
  (~45 min), then `python3 tools/build_tesseract.py --version v05 --preview`.

## 3. Tools needed
Node + `npx hyperframes@0.9.52`, Python 3 (numpy, soundfile, scipy, Pillow), ffmpeg, Tesseract CLI v0.7.0 (`tsrct`,
skill `npx skills add mirage-hq/Tesseract`), Chromium. Cloud: set NODE_USE_ENV_PROXY=1.

## 4. State (v05 delivered as a preview)
07_Exports/RC_GTA-Origin_v05_preview.mp4 (sent separately). Open items: CTA needs the Instagram handle, follower
count and avatar (config `PROFILE` at the top of hyperframes/b18-cta/index.html); music bed off (switch MUSIC in
tools/build_tesseract_audio.py); no true light-bar close-up in the library (B1 opening).
Rule from the client: never apply instruction-doc items that reverse earlier notes (REVISION_v05.md section U).

## 5. Prompt to start the new chat
"Continue the RC_GTA-Origin video project. Read RC_GTA-Origin/HANDOFF.md, CLAUDE.md, REVISION_v05.md (section U is
binding) and REVISION_v02-v04.md first. Extract RC_GTA_media_pack.tar into RC_GTA-Origin/. Then: <your next notes>."
