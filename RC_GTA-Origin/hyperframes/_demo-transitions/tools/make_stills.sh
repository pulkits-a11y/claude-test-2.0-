#!/bin/sh
# Capture the X4 "old frame" stills from the demo itself, exactly as a beat builder would: render the composition
# WITHOUT the tear (and without labels/captions) and snapshot the first torn frame. Crops to the tear container.
set -e
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.9.52"
OUT=.stills-tmp
rm -rf "$OUT"
python3 tools/gen_demo.py --stills
$HF snapshot . --at 5.83335,8.33335,10.50002 --no-end -o "$OUT" >/dev/null
ffmpeg -nostdin -loglevel error -y -i "$OUT"/frame-00-at-5.833s.png assets/x4/c-old.png
ffmpeg -nostdin -loglevel error -y -i "$OUT"/frame-01-at-8.333s.png -vf "crop=600:450:660:300" assets/x4/d-old.png
ffmpeg -nostdin -loglevel error -y -i "$OUT"/frame-02-at-10.5s.png assets/x4/e-old.png
rm -rf "$OUT"
python3 tools/gen_demo.py
sh tools/apply_treatments.sh
ls -la assets/x4
