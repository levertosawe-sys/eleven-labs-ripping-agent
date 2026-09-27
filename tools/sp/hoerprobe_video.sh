#!/bin/bash
# Tonprobe als kleines, im Chat abspielbares Video (Viktors stehende Regel 08.09.2026:
# Hoerproben nie als MP3 senden — er will abspielen, nicht herunterladen).
# Aufruf: hoerprobe_video.sh <audio> <titel> <untertitel> <out.mp4>
set -e
STAMM="$(cd "$(dirname "$0")/../.." && pwd)"
FONT="$STAMM/tools/sp/fonts/Inter-Variable.ttf"
AUDIO="$1"; TITEL="$2"; UNTER="$3"; OUT="$4"
# Die Farbfläche ist eine Endlos-Quelle: ohne :r=25, overlay=shortest=1 UND -shortest schreibt ffmpeg weiter,
# bis die Platte voll ist (Befund 17.09.2026: 681 MB statt 2–5 MB, Prozess hing stundenlang).
ffmpeg -y -v error -i "$AUDIO" -filter_complex \
"[0:a]showwaves=s=720x300:mode=cline:rate=25:colors=0x5BA7F7|0x2E6FB8[w];\
color=c=0x111318:s=720x380:r=25[bg];\
[bg][w]overlay=0:64:shortest=1[o];\
[o]drawtext=fontfile=${FONT}:text='${TITEL}':fontcolor=white:fontsize=32:x=26:y=18[t1];\
[t1]drawtext=fontfile=${FONT}:text='${UNTER}':fontcolor=0x9AA4B2:fontsize=22:x=26:y=340[v]" \
-map "[v]" -map 0:a -c:v libx264 -preset veryfast -crf 28 -pix_fmt yuv420p \
-c:a aac -b:a 160k -shortest -movflags +faststart "$OUT"
DAUER_A=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO")
DAUER_V=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
echo "→ $OUT · Audio ${DAUER_A}s · Video ${DAUER_V}s · $(du -h "$OUT" | cut -f1)"
awk -v a="$DAUER_A" -v v="$DAUER_V" 'BEGIN{ if (v > a + 1) { print "FEHLER: Video laenger als der Ton — Endlos-Quelle, Datei loeschen"; exit 1 } }'
