#!/bin/sh
# Re-make the X4 "old frame" still for this beat: assets/x4/b17-old.png = this composition's own frame at the first
# torn frame (local 167 = beat f161 in v02, the final hit: the logo landed at 115%, sharp, no text), rendered WITHOUT the tear (index.html honours data-x4-capture on <html>).
# Run it after every change that alters the end card (R17.4 in-point, framing), e.g. when the real R17.4
# arrives:   python3 tools/sync_footage.py hyperframes/b17-loop && sh hyperframes/b17-loop/x4_still.sh
# Kit recipe: KIT_transitions.md "Making the still". CLI pinned to hyperframes@0.9.52.
set -e
cd "$(dirname "$0")"
FRAME=167                                  # local frame of the first torn frame (beat f161, the final hit; v02)
OUT=assets/x4/b17-old.png
TMP=$(mktemp -d "${TMPDIR:-/tmp}/b17-x4still.XXXXXX")
cp index.html hyperframes.json meta.json "$TMP/"
cp -r assets "$TMP/assets"
sed -i 's/<html lang="en">/<html lang="en" data-x4-capture>/' "$TMP/index.html"
grep -q 'data-x4-capture>' "$TMP/index.html" || { echo "capture flag not set" >&2; exit 1; }
AT=$(python3 -c "print('%.5f' % ($FRAME / 30 + 0.00005))")
npx --yes hyperframes@0.9.52 snapshot "$TMP" --at "$AT" --no-end -o "$TMP/out" >/dev/null
mkdir -p assets/x4
cp "$TMP"/out/frame-00-at-*.png "$OUT"
rm -rf "$TMP"
python3 -c "from PIL import Image; im=Image.open('$OUT'); print('$OUT', im.size, im.mode)" 2>/dev/null || ls -la "$OUT"
