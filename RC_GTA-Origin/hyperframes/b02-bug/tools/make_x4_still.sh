#!/bin/sh
# Re-capture B2's X4 "old frame" still (run after any change to what the CRT shows before the tear, e.g. real R9.1/R3.9):
# the composition's own frame at local f107 (beat f101, "broke."), CRT look included, with the camera push and the tear
# disabled (const STILL = true in a throwaway copy), cropped to the CRT screen rect -> assets/x4/b02-old.png (320 x 240).
# Keep CROP in sync with SCREEN in index.html (x, y, w, h = 800, 210, 320, 240 on the stand-in).
set -e
PROJ=$(cd "$(dirname "$0")/.." && pwd)
CROP="320:240:800:210"
CAP=$(mktemp -d)
cp -r "$PROJ/assets" "$PROJ/index.html" "$PROJ/hyperframes.json" "$PROJ/meta.json" "$PROJ/package.json" "$CAP/"
python3 - "$CAP/index.html" <<'PY'
import sys, re
p = sys.argv[1]; s = open(p).read()
assert "const STILL = false;" in s
s = s.replace("const STILL = false;", "const STILL = true;")
s = re.sub(r'<img class="rc-x4__still"[^>]*>', '', s)
open(p, "w").write(s)
PY
(cd "$CAP" && npx --yes hyperframes@0.9.52 snapshot . --at 3.56672 --no-end -o "$CAP/out" >/dev/null)
SRC=$(ls "$CAP"/out/frame-00-at-*.png)
mkdir -p "$PROJ/assets/x4"
ffmpeg -nostdin -loglevel error -y -i "$SRC" -vf "crop=$CROP" "$PROJ/assets/x4/b02-old.png"
cp "$SRC" "$PROJ/review/x4-still-source_L107_b101.png"
rm -rf "$CAP"
echo "wrote $PROJ/assets/x4/b02-old.png"
