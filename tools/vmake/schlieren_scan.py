#!/usr/bin/env python3
"""schlieren_scan.py — Vorfilter für Vmake-Rückstände im Caption-Band.

    ~/.venvs/sa/bin/python3 tools/vmake/schlieren_scan.py <video.mp4> [schwelle]

Dekodiert das ganze Video klein und in Graustufen, misst je Frame die Helligkeit im
Caption-Band (64–86 % der Bildhöhe) und meldet Zeitfenster, in denen das Band
auffällig heller ist als der Rest des Bildes — dort sitzen entweder noch Captions
(auf dem Original) oder Leucht-Schlieren (nach Vmake).

Exit 0 = Band ruhig · Exit 1 = Regionen-Liste als „a–b s"-Zeilen.

Die Schwellen sind an 033 SA kalibriert: legitime helle Szenen bleiben im unteren
Band unter 2 %. Gemeldete Region ansehen mit `crop=iw:ih*0.30:0:ih*0.54`.

Es ist ein VORFILTER: Helligkeit verwechselt Schlieren mit hellen Szenen
(Produkt-Shots, Fenster). Die gemeldeten Regionen werden angesehen, nicht geglaubt —
siehe .claude/skills/vmake-caption-entfernen/SKILL.md Schritt 4.
"""
import shutil as _sh
import subprocess
import sys

import numpy as np

# Portabel (Hybrid-Lauf 045): PATH zuerst, Homebrew als Mac-Rückfall.
FFMPEG = _sh.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FFPROBE = _sh.which("ffprobe") or "/opt/homebrew/bin/ffprobe"

W, H = 180, 320
BAND = (int(H * 0.64), int(H * 0.86))


def frames(video):
    cmd = [FFMPEG, "-v", "error", "-i", video, "-vf", f"scale={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, dtype=np.uint8).reshape(H, W)
    p.wait()


def fps(video):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", video],
                         capture_output=True, text=True).stdout.strip()
    a, b = out.split("/")
    return int(a) / int(b)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    video = sys.argv[1]
    schwelle = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    r = fps(video)
    scores = []
    for f in frames(video):
        band = f[BAND[0]:BAND[1]].astype(np.float32)
        rest = np.concatenate([f[:BAND[0]], f[BAND[1]:]]).astype(np.float32)
        # Anteil sehr heller Pixel im Band minus im Rest — Schrift/Schlieren sind fast weiß
        hell_band = (band > 225).mean() * 100
        hell_rest = (rest > 225).mean() * 100
        scores.append(hell_band - hell_rest)
    s = np.array(scores)
    auffaellig = s > (schwelle / 10.0)  # Schwelle 30 → Band hat >3 %-Punkte mehr Fast-Weiß als der Rest
    regionen, start = [], None
    for i, a in enumerate(auffaellig):
        if a and start is None:
            start = i
        if not a and start is not None:
            if i - start >= int(r * 0.4):  # kürzer als 0,4 s ist Flackern, kein Befund
                regionen.append((start / r, i / r))
            start = None
    if start is not None:
        regionen.append((start / r, len(s) / r))
    print(f"frames={len(s)} fps={r:.2f} band_y={BAND} schwelle={schwelle} "
          f"max={s.max():.1f} mittel={s.mean():.2f}")
    if not regionen:
        print("Band ruhig.")
        sys.exit(0)
    for a, b in regionen:
        print(f"{a:.1f}–{b:.1f} s")
    sys.exit(1)


if __name__ == "__main__":
    main()
