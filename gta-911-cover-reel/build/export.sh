#!/bin/bash
# Renders the reel in two parallel halves (software Vulkan renderer here). The MP4 exporter drops a few frames at the
# end of each range, so each half's missing tail frames are rendered again as a short ProRes clip and put back in
# place; the halves are then joined frame-exact and muxed with the document's own audio mix (voiceover + CTA sound).
# Output: GTA911_CoverReel.mp4 - 1920x1080, 30 fps, H.264 + AAC, 1124 frames.
# Usage: build/export.sh [--join-only]   (--join-only reuses the rendered halves)
cd "$(dirname "$0")/.."
X=~/.local/share/Tesseract/bin/tsrct; E=.tesseract-work/export; mkdir -p $E
TOTAL=1124; HALF=562                                  # frames; half 1 = 0-561, half 2 = 562-1123
ms() { python3 -c "print(round($1*1000/30))"; }
seg() { $X export --project GTA911_CoverReel.tsrct --output $E/seg$1.mp4 --resolution 1080p --fps 30 --start-ms $(ms $2) --duration-ms $(( $(ms $3) - $(ms $2) )) \
        --encoder-backend external-ffmpeg-command --ffmpeg-path "$(command -v ffmpeg)" > $E/seg$1.log 2>&1; echo "seg$1 exit $?"; }
tailclip() { $X export --project GTA911_CoverReel.tsrct --output $E/tail$1.mov --format prores --resolution 1080p --fps 30 \
        --start-ms $(ms $2) --duration-ms $(( $(ms $3) - $(ms $2) )) > $E/tail$1.log 2>&1; }
frames() { ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1"; }
if [ "$1" != "--join-only" ]; then
  seg 1 0 $HALF & seg 2 $HALF $TOTAL & wait
  $X export-audio --project GTA911_CoverReel.tsrct --output $E/mix.wav > $E/audio.log 2>&1
fi
# each half's tail: the last 16 frames of its range, rendered as ProRes (which keeps every frame)
tailclip 1 $((HALF - 16)) $HALF & tailclip 2 $((TOTAL - 16)) $TOTAL & wait
N1=$(frames $E/seg1.mp4); N2=$(frames $E/seg2.mp4); M1=$((HALF - N1)); M2=$((TOTAL - HALF - N2))
echo "half 1: $N1 + $M1 from its tail; half 2: $N2 + $M2 from its tail"
V="[0:v]setpts=PTS-STARTPTS,format=yuv420p[a];[1:v]trim=start_frame=$((16 - M1)):end_frame=16,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[b];"
V+="[2:v]setpts=PTS-STARTPTS,format=yuv420p[c];[3:v]trim=start_frame=$((16 - M2)):end_frame=16,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[d];"
V+="[a][b][c][d]concat=n=4:v=1:a=0,setpts=N/(30*TB)[v]"
ffmpeg -v error -y -i $E/seg1.mp4 -i $E/tail1.mov -i $E/seg2.mp4 -i $E/tail2.mov -i $E/mix.wav -filter_complex "$V" \
  -map "[v]" -map 4:a -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -fps_mode passthrough -c:a aac -b:a 256k -shortest -movflags +faststart GTA911_CoverReel.mp4
ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration -of compact GTA911_CoverReel.mp4
echo EXPORT_DONE
