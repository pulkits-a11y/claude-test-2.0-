#!/bin/sh
# Usage: sh tools/snap.sh <name> <frame> [<frame> ...]  -> review/<name>_fNNN.png (+ review/<name>_sheet.jpg)
# Frames are 30 fps frame indices; each still is taken 0.05 ms after the frame time (inside the frame).
set -e
cd "$(dirname "$0")/.."
NAME=$1; shift
AT=$(python3 -c "import sys; print(','.join('%.5f' % (int(f)/30 + 0.00005) for f in sys.argv[1:]))" "$@")
TMP=.snap-tmp-$NAME
rm -rf "$TMP"
npx --yes hyperframes@0.9.52 snapshot . --at "$AT" --no-end -o "$TMP" >/dev/null
i=0
for f in "$@"; do
  src=$(ls "$TMP"/frame-$(printf %02d $i)-at-*.png)
  cp "$src" "review/${NAME}_f$(printf %03d $f).png"
  i=$((i+1))
done
k=1; for sh in "$TMP"/contact-sheet*.jpg; do [ -f "$sh" ] || continue; cp "$sh" "review/${NAME}_sheet$k.jpg"; k=$((k+1)); done
rm -rf "$TMP"
echo "review/${NAME}: $*"
