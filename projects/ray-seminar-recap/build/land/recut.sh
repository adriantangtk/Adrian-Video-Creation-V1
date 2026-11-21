#!/bin/bash
# Re-cut every shot as 1920x1080 from the 4K originals. Portrait sources get a blurred fill.
# usage: recut.sh <out.mp4> <raw source> <ss> <dur> [extra concat segments as "ss-end+ss-end"]
out=$1; src=$2; ss=$3; dur=$4
GRADE="eq=contrast=1.06:saturation=1.12:gamma=1.03,unsharp=5:5:0.45:5:5:0.0"
read w h < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$src" | tr ',' ' ')
rot=$(ffprobe -v error -select_streams v:0 -show_entries stream_side_data=rotation -of csv=p=0 "$src" | head -1)
if [ -n "$rot" ] && [ "$rot" != "0" ]; then t=$w; w=$h; h=$t; fi
if [ "$w" -ge "$h" ]; then
  VF="scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=30,$GRADE,format=yuv420p"
else
  VF="split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:2,eq=brightness=-0.12:saturation=1.1[bg];[b]scale=-2:1080:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:0,fps=30,$GRADE,format=yuv420p"
fi
ffmpeg -v error -y -ss "$ss" -i "$src" -t "$dur" -an -vf "$VF" -c:v libx264 -preset slow -crf 14 -g 6 "$out"
