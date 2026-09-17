#!/usr/bin/env python3
"""Frame-genauer Ausschnitt für EINEN Lip-Sync-Auftrag: Video [f0, f1) aus der Bildbasis (crf 12, fast verlustfrei — der
Lip-Sync soll das Original-Bild bekommen, nicht eine weitere Kompressionsstufe) + Audio exakt gleich lang (mono 44,1 kHz).
Im Pipeline-Ordner des Projekts ausführen. Abhängigkeit: ffmpeg/ffprobe.

  python3 lipsync_schnitt.py <name> <f0> <f1> <audio.wav> [--basis _work/bildbasis.mp4]
  → _work/lipsync/<name>_video.mp4 + _work/lipsync/<name>_audio.wav
Erfolg = Konsole meldet Frames == f1 − f0 und Audio-Dauer == (f1 − f0) / fps (±1 ms); sonst Exit 1.
"""
import argparse, json, os, subprocess, sys

def fps_von(pfad):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "json", pfad],
                       capture_output=True, text=True)
    try:
        z, n = json.loads(r.stdout)["streams"][0]["r_frame_rate"].split("/"); return float(z) / float(n)
    except Exception:
        sys.exit(f"FEHLER: ffprobe kann {pfad} nicht lesen: {r.stderr[:300]}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("f0", type=int); ap.add_argument("f1", type=int); ap.add_argument("audio")
    ap.add_argument("--basis", default="_work/bildbasis.mp4")
    a = ap.parse_args()
    for p in (a.basis, a.audio):
        if not os.path.exists(p): sys.exit(f"FEHLER: Datei fehlt: {p}")
    if a.f1 <= a.f0: sys.exit("FEHLER: f1 muss größer als f0 sein")
    fps = fps_von(a.basis)
    os.makedirs("_work/lipsync", exist_ok=True)
    v = f"_work/lipsync/{a.name}_video.mp4"; au = f"_work/lipsync/{a.name}_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.basis, "-vf", f"trim=start_frame={a.f0}:end_frame={a.f1},setpts=PTS-STARTPTS",
                    "-an", "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", f"{fps:g}", v], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-af", f"atrim=start={a.f0 / fps:.4f}:end={a.f1 / fps:.4f},asetpts=PTS-STARTPTS",
                    "-ar", "44100", "-ac", "1", au], check=True)
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                            "-of", "csv=p=0", v], capture_output=True, text=True).stdout.strip() or 0)
    da = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", au],
                              capture_output=True, text=True).stdout.strip() or 0)
    soll_n, soll_d = a.f1 - a.f0, (a.f1 - a.f0) / fps
    print(f"{a.name}: {n} Frames (soll {soll_n}) · Audio {da:.3f} s (soll {soll_d:.3f} s)")
    if n != soll_n or abs(da - soll_d) > 0.001 + 1 / 44100: sys.exit(f"FEHLER: Ausschnitt {a.name} nicht frame-genau")

if __name__ == "__main__": main()
