#!/usr/bin/env bash
# Render beat compositions one after another (HyperFrames serializes renders with a global lock anyway).
#   tools/render_all.sh                 # all 17 beats from timing/beat_map.json
#   tools/render_all.sh b03-dundee b13-gta
# Then probes each render: frames must equal the beat length + 12 (6f handles), pix_fmt yuva444p12le.
set -u
ROOT=/home/user/claude-test-2.0-/RC_GTA-Origin
IDS="$*"
[ -z "$IDS" ] && IDS=$(python3 -c "import json;print(' '.join(b['composition']['id'] for b in json.load(open('$ROOT/timing/beat_map.json'))['beats']))")
WORKERS=${WORKERS:-4}
for id in $IDS; do
  t0=$(date +%s)
  ( cd "$ROOT/hyperframes/$id" && npx --yes hyperframes@0.9.52 render . --format mov --workers "$WORKERS" -o "../../05_GFX/renders/$id.mov" ) > "/tmp/render_$id.log" 2>&1
  rc=$?
  want=$(python3 -c "import json;print([b['dur_frames']+12 for b in json.load(open('$ROOT/timing/beat_map.json'))['beats'] if b['composition']['id']=='$id'][0])")
  got=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,pix_fmt -of csv=p=0 "$ROOT/05_GFX/renders/$id.mov" 2>/dev/null)
  echo "$id rc=$rc $(( $(date +%s) - t0 ))s frames/pix: $got (want $want)"
done
