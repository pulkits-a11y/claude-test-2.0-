#!/usr/bin/env bash
# B18 working copy (git-ignored like every assets/footage clip): B1's police-lightbar footage, cut with B1's own recipe
# (hyperframes/b01-hook/LOOP_FRAME.json) but starting 2.5 s earlier (631.0333 instead of 633.5333 s), 3.0 s long, so that
# its frame 81 (= B18 local 81 at media time local / 30) is B1's clip frame 6 = B1's frame 0 (checked: mean diff 0.9/255).
set -e
cd "$(dirname "$0")/../../.."
ffmpeg -nostdin -loglevel error -y -ss 631.0333 \
  -i "04_Broll/_originals/B05/R5.4__GTA 5 LSPDFR ｜ Sheriff Gang Unit Takes Over the Night Shift 🚔 ｜ DLSS 5 [PV1NfLjkbWg].mp4" \
  -t 3.0 -an -vf "fps=30,crop=1280:720:380:200,scale=1920:1080:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 14 -preset medium -pix_fmt yuv420p -movflags +faststart hyperframes/b18-cta/assets/footage/b18_lightbar.mp4
