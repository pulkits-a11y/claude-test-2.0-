#!/bin/sh
# Re-capture B2's X4 "old frame" still (run after any change to what the CRT shows before the tear, e.g. real R9.1/R3.9):
# the composition's own frame at local f101 (v02; beat f95, "broke."), CRT look included, with the camera moves (push, key
# punches, zoom-through) and the tear disabled (const STILL = true in a throwaway copy), cropped to the CRT screen rect
# -> assets/x4/b02-old.png (537 x 406). v02 keeps the same source frame as v01 (R9.1 128.5 s: media-start 0.1334).
# CROP = the GTA 1 screen box in box space (537 x 406 at 0,0: the STILL copy un-pins #b02-g1box there).
set -e
PROJ=$(cd "$(dirname "$0")/.." && pwd)
CROP="537:406:0:0"
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
(cd "$CAP" && npx --yes hyperframes@0.9.52 snapshot . --at 3.36672 --no-end -o "$CAP/out" >/dev/null)
SRC=$(ls "$CAP"/out/frame-00-at-*.png)
mkdir -p "$PROJ/assets/x4"
ffmpeg -nostdin -loglevel error -y -i "$SRC" -vf "crop=$CROP" "$PROJ/assets/x4/b02-old.png"
cp "$SRC" "$PROJ/review/x4-still-source_L101_b95.png"
rm -rf "$CAP"
echo "wrote $PROJ/assets/x4/b02-old.png"
