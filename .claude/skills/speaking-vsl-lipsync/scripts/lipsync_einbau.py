#!/usr/bin/env python3
"""Lip-Sync-Frames frame-genau ins Bild einsetzen — EINE Encode-Generation (crf 18, bt709). Im Pipeline-Ordner ausführen.
Abhängigkeiten: ffmpeg/ffprobe, numpy, opencv-python.

  python3 lipsync_einbau.py --basis <Bildbasis> [--out _work/bild_lipsync.mp4]
                            [--einbau _pipeline/lipsync_einbau.json] [--uebergaenge _pipeline/lipsync_uebergaenge.json]
                            [--farbkorrektur name1,name2] [--vorschau 30.8-34.4,217-221]

Regeln je Frame i der Basis:
  i in einem Einbau-Eintrag und in keinem Übergangs-Fenster → Frame aus <datei> des Eintrags (Farbkorrektur, falls der Name in
      --farbkorrektur steht; Referenz = Basis-Frame)
  i in einem Übergangs-Fenster → Basis-Frame (der Lip-Sync-Frame wird verworfen)
  sonst → Basis-Frame
Ein Eintrag „<name>b" (auch c, d …) ersetzt seinen Erstlauf „<name>".
lipsync_uebergaenge.json: {"<etikett>": [[f0, f1], ...]} — ganze Frames der ganzen Ad, f1 exklusiv; der Schlüssel ist nur ein
Etikett, jedes Fenster gilt global. Beispiel: {"spr_c54": [[3730, 3739]]}. Fenster außerhalb aller Einträge werden gemeldet.
Farbe: gelesen mit genauer Rundung, geschrieben mit ausdrücklicher bt709-Matrix — die Tags allein ändern die Matrix nicht
(sonst verschieben sich gesättigte Farben und das Bild wird je Generation ~2 Stufen dunkler).
--vorschau schreibt nur die Frames dieser Sekunden-Fenster. Ohne --vorschau muss die Ausgabe exakt so viele Frames haben wie die
Basis. Exit 1 mit Meldung: „<datei> hat N Frames statt M" (Eintrag passt nicht zu seinem Auftrag) · „Ausgabe N statt M Frames"
(Encoder/Speicher) · „Datei fehlt".
"""
import argparse, json, os, subprocess, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lipsync_farbe as LF

def sonde(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                        "stream=width,height,r_frame_rate,nb_read_frames", "-of", "json", p], capture_output=True, text=True)
    try:
        s = json.loads(r.stdout)["streams"][0]; z, n = s["r_frame_rate"].split("/")
        return int(s["width"]), int(s["height"]), float(z) / float(n), int(s["nb_read_frames"])
    except Exception:
        sys.exit(f"FEHLER: ffprobe kann {p} nicht lesen: {r.stderr[:300]}")

def quelle(p, w, h):
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-vf", "scale=flags=accurate_rnd+full_chroma_int", "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = pr.stdout.read(n)
        if len(b) < n: return
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default="_work/bildbasis.mp4"); ap.add_argument("--out", default="_work/bild_lipsync.mp4")
    ap.add_argument("--einbau", default="_pipeline/lipsync_einbau.json"); ap.add_argument("--uebergaenge", default="_pipeline/lipsync_uebergaenge.json")
    ap.add_argument("--farbkorrektur", default=""); ap.add_argument("--vorschau", default="")
    a = ap.parse_args()
    for p in (a.basis, a.einbau):
        if not os.path.exists(p): sys.exit(f"FEHLER: Datei fehlt: {p}")
    w, h, fps, n_basis = sonde(a.basis)
    einbau = LF.einbau_liste(a.einbau)
    for e in einbau:
        if not os.path.exists(e["datei"]): sys.exit(f"FEHLER: Datei fehlt: {e['datei']}")
        n = sonde(e["datei"])[3]
        if n != e["f1"] - e["f0"]: sys.exit(f"FEHLER: {e['datei']} hat {n} Frames statt {e['f1'] - e['f0']}")
    quellen = {f: e for e in einbau for f in range(e["f0"], e["f1"])}
    ueb = json.load(open(a.uebergaenge)) if os.path.exists(a.uebergaenge) else {}
    ueb_frames = set()
    for etikett, fenster_liste in ueb.items():
        for f0, f1 in fenster_liste:
            if not any(f in quellen for f in range(int(f0), int(f1))): print(f"HINWEIS: Übergangs-Fenster {etikett} [{f0}, {f1}) liegt außerhalb aller Einträge — wirkungslos")
            ueb_frames.update(range(int(f0), int(f1)))
    korrektur = {s for s in a.farbkorrektur.split(",") if s}
    fenster = [tuple(float(x) for x in s.split("-")) for s in a.vorschau.split(",") if s]
    offen = {}
    def ls_frame(e):
        if e["datei"] not in offen: offen[e["datei"]] = quelle(e["datei"], w, h)
        return next(offen[e["datei"]])
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", f"{fps:g}", "-i", "-",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-color_range", "tv", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    zaehl = {"lipsync": 0, "uebergang_basis": 0, "basis": 0, "farbkorrektur": 0}; gesicht = None
    for i, b in enumerate(quelle(a.basis, w, h)):
        t = i / fps; e = quellen.get(i)
        lf = ls_frame(e) if e else None           # Strom immer weiterschalten, sonst verrutscht der Eintrag
        if fenster and not any(s <= t < z for s, z in fenster): continue
        if e is not None and i not in ueb_frames:
            f = lf
            if e.get("name") in korrektur:
                gesicht = LF.gesicht_finden(b, gesicht); f = LF.korrigiere(lf, b, gesicht); zaehl["farbkorrektur"] += 1
            zaehl["lipsync"] += 1
        else:
            f = b; zaehl["uebergang_basis" if e is not None else "basis"] += 1
        enc.stdin.write(np.ascontiguousarray(f).tobytes())
    enc.stdin.close(); enc.wait()
    if enc.returncode != 0: sys.exit("FEHLER: Encoder abgebrochen")
    n_out = sonde(a.out)[3]
    print(f"Frames: {zaehl} → {a.out} ({n_out} Frames)")
    if not fenster and n_out != n_basis: sys.exit(f"FEHLER: Ausgabe {n_out} statt {n_basis} Frames")

if __name__ == "__main__": main()
