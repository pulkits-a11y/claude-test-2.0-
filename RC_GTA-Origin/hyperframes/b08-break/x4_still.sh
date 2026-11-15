#!/bin/sh
# Re-make the X4 "old frame" still for this beat: assets/x4/b08-old.png = this composition's own frame at the first
# torn frame (local 41 = beat f35, "breaks"), rendered WITHOUT the tear (index.html honours data-x4-capture on <html>).
# Run it after every change that alters the card (layout, footage, R7.1 in-point, grade), e.g. when the real R7.1
# arrives:   python3 tools/sync_footage.py hyperframes/b08-break && sh hyperframes/b08-break/x4_still.sh
# Kit recipe: KIT_transitions.md "Making the still". CLI pinned to hyperframes@0.9.52.
set -e
cd "$(dirname "$0")"
FRAME=41                                   # local frame of the first torn frame
OUT=assets/x4/b08-old.png
TMP=$(mktemp -d "${TMPDIR:-/tmp}/b08-x4still.XXXXXX")
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
