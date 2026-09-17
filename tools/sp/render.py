#!/usr/bin/env python3
"""Schnitt + Render der Speaking-Kette: Sprechspur + Musikbett unter das Video.

Bild-Gesetz: Ein Ton-Mux ist KEIN Grund, das Bild anzufassen — ohne Pixel-Eingriff
läuft das Video als -c:v copy (bitgleich, Frame-Zahl beweist es). Nur wenn
Abdeck-Boxen gesetzt werden (--boxen, enge delogo-Boxen über Rest-Fenster laut
Gestaltungs-Text-Liste), wird encodiert: crf 18 + bt709-Container-Tags.

CWD = Pipeline-Ordner. Aufruf:
  python3 render.py --sprechspur _work/sprechspur.wav --bett _work/musikbett.wav \
      [--bett-db -10] [--boxen _pipeline/boxen.json] [--out _work/final.mp4]
boxen.json: [{"t0":1.97,"t1":2.07,"x":200,"y":886,"w":320,"h":100}, ...]
Der Bett-Pegel (--bett-db, Default -10 dB unter der Sprechspur) ist ein Startwert —
im Lauf gegenhören und den gemessenen Wert im Projekt notieren.
"""
import argparse, json, os, subprocess, sys

BASIS = os.getcwd()
ap = argparse.ArgumentParser()
ap.add_argument("--video", default="_work/source.mp4")
ap.add_argument("--sprechspur", default="_work/sprechspur.wav")
ap.add_argument("--bett", default="_work/musikbett.wav")
ap.add_argument("--bett-db", type=float, default=-10.0)
ap.add_argument("--boxen")
ap.add_argument("--overlay", help="PNG-Ebene (720x1280, Alpha) aus tools/sp/overlays.py — Gestaltungs-Overlays 1:1 nachgebaut; erzwingt den Encode-Zweig. Oder die <stamm>_zeiten.json aus overlays.py: mehrere Ebenen mit je eigenem Zeitfenster")
ap.add_argument("--overlay-fenster", help="Zeitfenster t0:t1 in Sekunden, in dem die Overlay-Ebene sichtbar ist (Default: ganze Ad) — ein Pill/Balken, der im Original vor der Endcard endet, darf nicht über die Endcard laufen")
ap.add_argument("--out", default="_work/final.mp4")
a = ap.parse_args()

for f in (a.video, a.sprechspur):
    if not os.path.exists(f): sys.exit(f"fehlt: {f}")
bett_da = os.path.exists(a.bett)

# Ton mischen
mix = f"{BASIS}/_work/mix.wav"
if bett_da:
    fc = (f"[1]volume={a.bett_db}dB[b];[0][b]amix=inputs=2:duration=first:normalize=0,"
          f"loudnorm=I=-16:TP=-1.5[out]")
    subprocess.run(["ffmpeg","-y","-v","error","-i",a.sprechspur,"-i",a.bett,
                    "-filter_complex",fc,"-map","[out]","-ar","44100",mix],check=True)
else:
    subprocess.run(["ffmpeg","-y","-v","error","-i",a.sprechspur,
                    "-af","loudnorm=I=-16:TP=-1.5","-ar","44100",mix],check=True)
    print("Hinweis: kein Musikbett gefunden — Sprechspur pur.")

tags = ["-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-color_range","tv"]
qdauer = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
    "stream=duration","-of","csv=p=0",a.video],capture_output=True,text=True).stdout.strip()
if a.boxen or a.overlay:
    boxen = json.load(open(a.boxen)) if a.boxen else []
    # Zwei Abdeck-Arten: delogo (Default — dünne Reste, interpoliert Umgebung) und
    # blur (modus="blur" — dicke Blöcke auf Verlaufs-Hintergrund: dort hinterlässt
    # delogo Schmier-Säulen, gemessen ROV 006 Endcard; kräftiges avgblur glättet).
    delos = [b for b in boxen if b.get("modus", "delogo") != "blur"]
    blurs = [b for b in boxen if b.get("modus") == "blur"]
    kette = ",".join(f"delogo=x={b['x']}:y={b['y']}:w={b['w']}:h={b['h']}:"
                     f"enable='between(t,{b['t0']},{b['t1']})'" for b in delos) or "null"
    fc = [f"[0:v]{kette}[v0]"]
    for i, b in enumerate(blurs):
        fc.append(f"[v{i}]split[a{i}][b{i}]")
        fc.append(f"[b{i}]crop={b['w']}:{b['h']}:{b['x']}:{b['y']},avgblur=26[c{i}]")
        fc.append(f"[a{i}][c{i}]overlay={b['x']}:{b['y']}:enable='between(t,{b['t0']},{b['t1']})'[v{i+1}]")
    vf_label = f"v{len(blurs)}"
    eingaben = ["-i",a.video,"-i",mix]
    if a.overlay:
        # Eine PNG (ganze Ad oder --overlay-fenster t0:t1) ODER die <stamm>_zeiten.json aus
        # overlays.py: mehrere Ebenen mit eigenem Zeitfenster in EINEM Encode (ARE 004 EL, 08.09.2026 —
        # sieben Nummern-Cards/Labels je eigenes Fenster; ein Encode je Ebene würde das Bild 7× neu kodieren).
        if a.overlay.endswith(".json"):
            lagen = json.load(open(a.overlay))
        else:
            lagen = [{"png": a.overlay, "t0": None, "t1": None}]
            if a.overlay_fenster:
                t0, t1 = a.overlay_fenster.split(":"); lagen[0].update(t0=float(t0), t1=float(t1))
        for j, l in enumerate(lagen):
            eingaben += ["-i", l["png"]]
            en = f":enable='between(t,{l['t0']},{l['t1']})'" if l.get("t0") is not None else ""
            fc.append(f"[{vf_label}][{2+j}:v]overlay=0:0:format=auto{en}[vo{j}]"); vf_label = f"vo{j}"
    cmd = ["ffmpeg","-y","-v","error"]+eingaben+[
           "-filter_complex",";".join(fc),"-map",f"[{vf_label}]","-map","1:a",
           "-fps_mode","passthrough","-af","apad","-t",qdauer,"-c:v","libx264","-crf","18","-preset","slow"]+tags+[
           "-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",a.out]
    print(f"Encode-Zweig (Boxen: {len(boxen)}, Overlay: {a.overlay or 'nein'}) — crf 18 + bt709.")
else:
    # apad füllt den Ton bis zur Videolänge auf — -shortest endet dann am VIDEO,
    # nie umgekehrt (gemessen: ohne apad schnitt -shortest die End-Szene weg)
    cmd = ["ffmpeg","-y","-v","error","-i",a.video,"-i",mix,"-map","0:v","-map","1:a",
           # -t <Videodauer> ist Pflicht: apad erzeugt unendlichen Ton, und -shortest terminiert
           # mit -c:v copy nicht zuverlaessig (gemessen YUR 001 EL: Lauf haengt nach dem letzten Videoframe).
           "-af","apad","-t",qdauer,"-c:v","copy"]+tags+["-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",a.out]
    print("Copy-Zweig — Bild bitgleich.")
subprocess.run(cmd,check=True)
os.remove(mix)
def frames(p):
    return subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v:0",
        "-show_entries","stream=nb_read_frames","-of","csv=p=0",p],capture_output=True,text=True).stdout.strip()
print(f"Render OK → {a.out} · Frames Quelle {frames(a.video)} / Final {frames(a.out)} "
      f"(Copy-Zweig: Gleichstand = bitgleich; -shortest darf genau 1 Endframe kosten)")
