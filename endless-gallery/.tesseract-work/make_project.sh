#!/bin/bash
# Assemble the Endless Gallery Tesseract project from source assets + generated actions.
# usage: make_project.sh OUT.tsrct WIDTH HEIGHT [extra build_gallery.py flags...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
TS="${TSRCT:-$HOME/.local/share/Tesseract/bin/tsrct}"
OUT="$1"; W="$2"; H="$3"; shift 3
M="$ROOT/assets/models"
WORK="$HERE/build"; mkdir -p "$WORK"
rm -f "$OUT"
"$TS" project create --project "$OUT" --width "$W" --height "$H" >/dev/null
for a in dunk=standin/dunk_scan_lit.glb af1=cleaned/nike_air_force_1_uvfix.glb aj1=cleaned/nike_air_jordan_1_left.glb \
         dunk_mid=standin/dunk_scan_lit_mid.glb dunk_far=standin/dunk_scan_lit_far.glb af1_mid=lod/af1_mid.glb af1_far=lod/af1_far.glb \
         aj1_mid=lod/aj1_mid.glb aj1_far=lod/aj1_far.glb; do
  "$TS" project import-asset --project "$OUT" --file "$M/${a#*=}" --asset-id "${a%%=*}" --kind model3d >/dev/null
done
"$TS" project import-asset --project "$OUT" --file "$ROOT/assets/generated/beam_falloff.png" --asset-id beamfall --kind image >/dev/null
"$TS" project import-video --project "$OUT" --file "$ROOT/assets/generated/gobo.mp4" --asset-id gobo > "$WORK/gobo-import.json"
python3 - "$W" "$H" "$WORK/pre.json" <<'PY'
import json, sys
W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
json.dump([
  {"type": "updateFxComposition", "compositionId": "main", "startTimeMs": 0, "durationMs": 2800},
  {"type": "createFxVideoLayer", "compositionId": "main", "layerId": 2, "name": "Lamp light mask (projector gobo)",
   "activeRange": {"start": 0, "duration": 2800}, "sourceRange": {"start": 0, "duration": 2800},
   "sourceIntrinsicDuration": 2800,
   "transform": {"anchorPoint": [0, 0], "position": [0, 0], "scale": [100, 100], "rotation": 0, "opacity": 100},
   "source": {"assetId": "gobo", "fit": "stretch", "sourceRect": {"x": 0, "y": 0, "width": W, "height": H}}},
], open(out, "w"))
PY
"$TS" project apply --project "$OUT" --actions "$WORK/pre.json" >/dev/null
python3 "$HERE/build_gallery.py" "$HERE/lamp_timeline.json" "$WORK/gallery.json" "$@"
"$TS" project apply --project "$OUT" --actions "$WORK/gallery.json" > "$WORK/apply.json"
python3 -c "import json,sys; w=json.load(open('$WORK/apply.json')).get('warnings'); print('warnings:', w if w else 'none')"
ls -la "$OUT"
