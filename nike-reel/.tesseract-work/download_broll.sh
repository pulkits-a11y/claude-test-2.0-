#!/bin/bash
# Downloads the Drive B-roll by file ID and verifies each byte count against Drive's metadata.
cd "$(dirname "$0")/../Sources/broll"
while IFS=$'\t' read -r bid fid size act title; do
  out="$bid.mp4"
  if [ -f "$out" ] && [ "$(stat -c %s "$out")" = "$size" ]; then echo "$bid skip"; continue; fi
  for try in 1 2 3 4; do
    curl -sL --retry 3 -A 'Mozilla/5.0' -o "$out.part" "https://drive.usercontent.google.com/download?id=$fid&export=download&confirm=t"
    got=$(stat -c %s "$out.part" 2>/dev/null || echo 0)
    if [ "$got" = "$size" ]; then mv "$out.part" "$out"; echo "$bid ok $got"; break; fi
    echo "$bid retry $try (got $got, want $size)"; sleep $((try*5))
  done
done < manifest.tsv
echo DONE
