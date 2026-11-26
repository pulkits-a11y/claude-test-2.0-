#!/bin/bash
# Renders the reel in two parallel segments (software Vulkan renderer here), joins them, tops up any frames the
# exporter drops at the very end of the timeline (rendered separately as ProRes), and muxes the voiceover from the
# document's own audio mix (voiceover + CTA sound). Output: GTA911_CoverReel.mp4 (1920x1080, 30 fps, H.264 + AAC, 1124 frames).
cd "$(dirname "$0")/.."
X=~/.local/share/Tesseract/bin/tsrct; E=.tesseract-work/export; mkdir -p $E; TOTAL=1124
seg() { $X export --project GTA911_CoverReel.tsrct --output $E/seg$1.mp4 --resolution 1080p --fps 30 --start-ms $2 --duration-ms $3 \
        --encoder-backend external-ffmpeg-command --ffmpeg-path "$(command -v ffmpeg)" > $E/seg$1.log 2>&1; echo "seg$1 exit $?"; }
seg 1 0 18733 & seg 2 18733 18733 & wait
$X export-audio --project GTA911_CoverReel.tsrct --output $E/mix.wav > $E/audio.log 2>&1   # voiceover + CTA sound
$X export --project GTA911_CoverReel.tsrct --output $E/tail.mov --format prores --resolution 1080p --fps 30 --start-ms 36933 --duration-ms 533 > $E/tail.log 2>&1
printf "file 'seg1.mp4'\nfile 'seg2.mp4'\n" > $E/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $E/list.txt -c copy -an $E/video.mp4
N=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $E/video.mp4); MISS=$((TOTAL - N))
echo "joined $N frames, topping up $MISS from the tail render"
if [ $MISS -gt 0 ]; then
  ffmpeg -v error -y -i $E/video.mp4 -i $E/tail.mov -i $E/mix.wav -filter_complex \
    "[0:v]setpts=PTS-STARTPTS,format=yuv420p[a];[1:v]trim=start_frame=$((16 - MISS)):end_frame=16,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[t];[a][t]concat=n=2:v=1:a=0[v]" \
    -map "[v]" -map 2:a -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -r 30 \
    -c:a aac -b:a 256k -movflags +faststart GTA911_CoverReel.mp4
else
  ffmpeg -v error -y -i $E/video.mp4 -i $E/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart GTA911_CoverReel.mp4
fi
ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration -of compact GTA911_CoverReel.mp4
echo EXPORT_DONE
