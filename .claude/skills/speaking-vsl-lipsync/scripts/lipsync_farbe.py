#!/usr/bin/env python3
"""Farbstich des Lip-Syncs messen und (als Notbehelf) korrigieren. Im Pipeline-Ordner des Projekts ausführen.
Abhängigkeiten: ffmpeg/ffprobe, numpy, opencv-python.

Messgröße „Farbstich": mittlere Cr/Cb-Abweichung (Gauß-geglättet, 0–255-Skala) in der unteren Gesichtshälfte OHNE Mundkern,
Lip-Sync-Frame gegen Vergleichs-Frame. Der Mundkern ist ausgenommen, weil sich dort Lippen und Zähne ändern sollen.
Werte (gemessen an 32 Aufträgen): sauber 0,7–1,5 · Flecken aus Farbblitzen 20–28 · Grenze AUFFÄLLIG > 4.

  python3 lipsync_farbe.py messen <name> [<name> ...] | --alle   [--ohne 60-71]
      Rohausgabe _work/lipsync/<name>_lipsync.mp4 gegen _work/lipsync/<name>_video.mp4. --alle = Namen aus
      _pipeline/lipsync_einbau.json. Fehlende Dateien werden übersprungen und gemeldet. Die Zeile nennt den Frame des
      Höchstwerts im Auftrag (0-basiert); Frame der ganzen Ad = f0 des Auftrags + dieser Wert. --ohne a-b nimmt die Auftrags-
      Frames a…b-1 aus Max und Ø heraus (Blende ausblenden, um zu sehen, ob der Rest des Clips sauber ist).
  python3 lipsync_farbe.py messen-final --final <Bild mit Lip-Sync> --basis <Bildbasis> [--einbau _pipeline/lipsync_einbau.json]
      Eingebaute Frames im fertigen Bild gegen die Bildbasis, je Eintrag mit Frame der ganzen Ad beim Höchstwert.
      AUFFÄLLIG = über max(4, 1,5 × Median aller Einträge) — eine Encode-Generation hebt alle Werte gleichmäßig an.

API für Montage-Skripte: gesicht_finden(orig_rgb, letztes) · farbstich(ls_rgb, orig_rgb, gesicht) · korrigiere(ls_rgb, orig_rgb, gesicht)
korrigiere() zieht den geglätteten Chroma-Unterschied außerhalb des Mundkerns ab (Helligkeit bleibt vom Lip-Sync). Sie wirkt nur
teilweise — ein Neu-Lauf ohne Blitz-Frames ist der eigentliche Fix; die Korrektur ist für Fälle ohne Guthaben.
"""
import argparse, json, os, statistics, subprocess, sys
import numpy as np, cv2

FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def gesicht_finden(orig_rgb, letztes=None):
    h, w = orig_rgb.shape[:2]; s = 360.0 / w
    g = cv2.cvtColor(cv2.resize(orig_rgb, (360, int(round(h * s)))), cv2.COLOR_RGB2GRAY)
    fs = FACE.detectMultiScale(g, 1.15, 5, minSize=(60, 60))
    if len(fs) == 0: return letztes
    x, y, fw, fh = max(fs, key=lambda r: r[2] * r[3])
    return tuple(int(round(v / s)) for v in (x, y, fw, fh))

def ellipse(shape, cx, cy, ax, ay, feder):
    m = np.zeros(shape[:2], np.float32)
    cv2.ellipse(m, (int(cx), int(cy)), (int(ax), int(ay)), 0, 0, 360, 1.0, -1)
    return cv2.GaussianBlur(m, (0, 0), feder)

def _maske(shape, gesicht):
    x, y, w, h = gesicht
    unten = ellipse(shape, x + 0.5 * w, y + 0.78 * h, 0.55 * w, 0.48 * h, 12)
    kern = ellipse(shape, x + 0.5 * w, y + 0.82 * h, 0.24 * w, 0.15 * h, 5)
    return unten * (1.0 - kern)

def farbstich(ls_rgb, orig_rgb, gesicht):
    if gesicht is None: return float("nan")
    m = _maske(ls_rgb.shape, gesicht)
    a = cv2.cvtColor(ls_rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32); b = cv2.cvtColor(orig_rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    d = np.abs(cv2.GaussianBlur(a[..., 1:] - b[..., 1:], (0, 0), 9)).sum(axis=2)
    return float((d * m).sum() / max(m.sum(), 1e-6))

def korrigiere(ls_rgb, orig_rgb, gesicht):
    if gesicht is None: return ls_rgb
    m = _maske(ls_rgb.shape, gesicht)[..., None]
    a = cv2.cvtColor(ls_rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32); b = cv2.cvtColor(orig_rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    d = cv2.GaussianBlur(a[..., 1:] - b[..., 1:], (0, 0), 9)
    a[..., 1:] = a[..., 1:] - d * m
    return cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_YCrCb2RGB)

def strom(pfad, f0=None, n=None):
    """Frames exakt (ffmpeg-trim, genaue Rundung) als Generator — nie alles in den Speicher."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", pfad],
                       capture_output=True, text=True)
    try: w, h = (int(v) for v in r.stdout.strip().split(",")[:2])
    except ValueError: sys.exit(f"FEHLER: Video nicht lesbar: {pfad}")
    vf = (f"trim=start_frame={f0}:end_frame={f0 + n}," if f0 is not None and n else "") + "scale=flags=accurate_rnd+full_chroma_int"
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", pfad, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    groesse = w * h * 3
    while True:
        b = pr.stdout.read(groesse)
        if len(b) < groesse: return
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)

def reihe(ls_frames, orig_frames):
    """Farbstich je Frame (NaN, solange noch kein Gesicht gefunden ist) — Liste in Frame-Reihenfolge."""
    g = None; werte = []
    for a, b in zip(ls_frames, orig_frames):
        g = gesicht_finden(b, g); werte.append(farbstich(a, b, g))
    return werte

def ersetzte(namen):
    return {n[:-1] for n in namen if len(n) > 1 and n[-1] in "bcdefgh" and n[:-1] in namen}

def einbau_liste(pfad):
    if not os.path.exists(pfad): sys.exit(f"FEHLER: {pfad} fehlt — erst lipsync_lauf.py")
    e = json.load(open(pfad)); weg = ersetzte({x["name"] for x in e})
    return [x for x in e if x["name"] not in weg]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("modus", choices=["messen", "messen-final"]); ap.add_argument("namen", nargs="*")
    ap.add_argument("--alle", action="store_true"); ap.add_argument("--ohne", default=""); ap.add_argument("--final"); ap.add_argument("--basis", default="_work/bildbasis.mp4")
    ap.add_argument("--einbau", default="_pipeline/lipsync_einbau.json")
    a = ap.parse_args()
    if a.modus == "messen":
        namen = [x["name"] for x in einbau_liste(a.einbau)] if a.alle else a.namen
        if not namen: sys.exit("FEHLER: Auftragsnamen oder --alle angeben")
        for n in namen:
            ls, vi = f"_work/lipsync/{n}_lipsync.mp4", f"_work/lipsync/{n}_video.mp4"
            if not (os.path.exists(ls) and os.path.exists(vi)): print(f"{n:12} fehlt — übersprungen"); continue
            w = np.array(reihe(strom(ls), strom(vi)))
            if a.ohne:
                o0, o1 = (int(v) for v in a.ohne.split("-")); w[o0:o1] = np.nan
            if not np.isfinite(w).any(): print(f"{n:12} kein Gesicht gefunden — von Hand ansehen"); continue
            i = int(np.nanargmax(w)); mx = float(np.nanmax(w))
            print(f"{n:12} Farbstich max {mx:5.2f} (Frame {i}) · Ø {np.nanmean(w):4.2f} · {'AUFFÄLLIG → Frame ansehen' if mx > 4 else 'ok'}")
        return
    if not a.final: sys.exit("FEHLER: --final fehlt")
    for p in (a.final, a.basis):
        if not os.path.exists(p): sys.exit(f"FEHLER: Datei fehlt: {p}")
    erg = []
    for e in einbau_liste(a.einbau):
        n = e["f1"] - e["f0"]
        w = np.array(reihe(strom(a.final, e["f0"], n), strom(a.basis, e["f0"], n)))
        if np.isfinite(w).any(): erg.append((e["name"], float(np.nanmax(w)), float(np.nanmean(w)), e["f0"] + int(np.nanargmax(w))))
    if not erg: sys.exit("FEHLER: keine Messwerte (Einbau-Liste leer oder keine Gesichter)")
    grenze = max(4.0, 1.5 * statistics.median(m for _, m, _, _ in erg))
    for name, mx, mi, fr in erg:
        print(f"{name:12} max {mx:5.2f} (Frame {fr} der Ad) · Ø {mi:4.2f} · {'AUFFÄLLIG → ansehen' if mx > grenze else 'ok'}")
    print(f"Grenze {grenze:.2f} (max(4, 1,5 × Median))")

if __name__ == "__main__": main()
