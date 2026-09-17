#!/usr/bin/env python3
"""Lip-Sync-Bereiche finden: nur Menschen, nur wo sie sichtbar sprechen, nie über Farbblitze oder Blenden.
Im Pipeline-Ordner des Projekts ausführen (brands/<Brand>/<NNN> EL/). Abhängigkeiten: ffmpeg/ffprobe, numpy, opencv-python.

  python3 lipsync_bereiche.py --vorbefund _work/source_original.mp4
      Messung am Trigger: Sekunden mit frontalem, ausreichend großem Gesicht (2 fps). Nur Konsole.

  python3 lipsync_bereiche.py --basis <Bildbasis> [--karte _pipeline/clip_karte.json] [--audio _work/sprechspur.wav]
                              [--out _pipeline/lipsync_auftraege.json]
      Aufträge aus der Clip-Karte (JSON-Liste von Clips): Clips mit mensch_spricht = true (Alias sprecherin_spricht) und ohne
      lipsync_aus = true → Frame-Läufe mit frontalem Gesicht → Blitz-/Blenden-Frames samt Rand herausschneiden, auch direkt vor
      und hinter einem Lauf → Läufe ≥ MIN_LAUF als Aufträge. Audio je Auftrag: _work/sprechspur_<mensch_rolle>.wav, wenn der Clip
      mensch_rolle trägt und die Datei existiert (sonst WARNUNG und --audio). Legt _work/lipsync/ an und
      _pipeline/lipsync_uebergaenge.json als {}, falls sie fehlt (vorhandene Fenster bleiben stehen).
      Exit 0 = Aufträge geschrieben · Exit 3 = Karte ohne Feld mensch_spricht (erst ergänzen) · Exit 4 = kein Mensch spricht laut
      Karte (Knoten entfällt) · Exit 5 = Clips mit mensch_spricht, aber 0 Aufträge (Gesichter zu klein/zu kurz: Befund melden).

Zahlen und ihr Grund:
  GESICHT_MIN 0,25  Gesichtsbreite ≥ 25 % der Bildbreite — kleinere Münder ändert der Lip-Sync kaum, er kostet aber voll.
  LUECKE 4          Haar-Aussetzer bei Kopfdrehung (bis 4 Frames) werden geschlossen, sonst zerfällt ein Satz in Stücke.
  MIN_LAUF 13       Läufe unter 0,5 s (bei 25 fps) lohnen keinen Auftrag.
  BLITZ_Y 25 / BLITZ_C 8   Abweichung eines Frames vom Median seines Laufs (Luma bzw. Chroma-Abstand Cr/Cb, 0–255).
                    Normale Sprecher-Clips schwanken bis ~4 Luma / ~3,5 Chroma; Farbblitze und Schwarz-/Weißblenden lagen
                    bei 82–151 Luma oder 47–92 Chroma (Schwarzblende ohne Farbe: Luma 96, Chroma 7 → Luma-Schwelle greift).
  RAND 2            Frames vor/nach einem Blitz mit ausschneiden — die Blende setzt 1–2 Frames vor der Messschwelle ein.
  NACHBAR 6         so viele Frames vor/hinter einem Lauf werden auf Blitze geprüft (die Gesichtserkennung verliert das
                    Gesicht oft schon in der Blende, der Lauf endet dann knapp davor).
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2

GESICHT_MIN, LUECKE, MIN_LAUF, BLITZ_Y, BLITZ_C, RAND, NACHBAR = 0.25, 4, 13, 25.0, 8.0, 2, 6
FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def sonde(pfad):
    if not os.path.exists(pfad): sys.exit(f"FEHLER: Video fehlt: {pfad}")
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                        "-of", "json", pfad], capture_output=True, text=True)
    try:
        s = json.loads(r.stdout)["streams"][0]; z, n = s["r_frame_rate"].split("/")
        return int(s["width"]), int(s["height"]), float(z) / float(n)
    except Exception:
        sys.exit(f"FEHLER: ffprobe kann {pfad} nicht lesen: {r.stderr[:300]}")

def frames(pfad, breite, hoehe, fps_filter=None):
    """Kleine RGB-Frames (Breite 360) als Generator."""
    w = 360; h = int(round(hoehe * w / breite / 2) * 2)
    vf = (f"fps={fps_filter}," if fps_filter else "") + f"scale={w}:{h}"
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", pfad, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = pr.stdout.read(n)
        if len(b) < n: return
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)

def gesicht_gross(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    fs = FACE.detectMultiScale(g, 1.15, 5, minSize=(40, 40))
    return len(fs) > 0 and max(r[2] for r in fs) >= GESICHT_MIN * rgb.shape[1]

def vorbefund(pfad):
    breite, hoehe, fps = sonde(pfad)
    werte = [gesicht_gross(f) for f in frames(pfad, breite, hoehe, fps_filter=2)]
    if not werte: sys.exit("FEHLER: keine Frames gelesen")
    s = sum(werte) / 2.0; ges = len(werte) / 2.0
    print(f"Vorbefund: frontales Gesicht ≥ {GESICHT_MIN:.0%} Bildbreite in {s:.0f} s von {ges:.0f} s ({s / ges:.0%}).")
    print("→ Lip-Sync-Frage stellen." if s >= 3 else "→ kein Mensch sichtbar im Bild: Lip-Sync-Knoten entfällt.")

def schliesse_luecken(v):
    i = 0
    while i < len(v):
        if not v[i]:
            j = i
            while j < len(v) and not v[j]: j += 1
            if i > 0 and j < len(v) and j - i <= LUECKE: v[i:j] = [True] * (j - i)
            i = j
        else: i += 1
    return v

def laeufe(v):
    out, i = [], 0
    while i < len(v):
        if v[i]:
            j = i
            while j < len(v) and v[j]: j += 1
            out.append((i, j)); i = j
        else: i += 1
    return out

def ist_blitz(wert, ref):
    return abs(wert[0] - ref[0]) > BLITZ_Y or np.hypot(wert[1] - ref[1], wert[2] - ref[2]) > BLITZ_C

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vorbefund"); ap.add_argument("--basis", default="_work/bildbasis.mp4")
    ap.add_argument("--karte", default="_pipeline/clip_karte.json"); ap.add_argument("--audio", default="_work/sprechspur.wav")
    ap.add_argument("--out", default="_pipeline/lipsync_auftraege.json")
    a = ap.parse_args()
    if a.vorbefund: return vorbefund(a.vorbefund)
    if not os.path.exists(a.karte): sys.exit(f"FEHLER: Clip-Karte fehlt: {a.karte}")
    karte = json.load(open(a.karte))
    if not isinstance(karte, list): sys.exit(f"FEHLER: {a.karte} muss eine JSON-Liste von Clips sein (gefunden: {type(karte).__name__})")
    if not any(("mensch_spricht" in c or "sprecherin_spricht" in c) for c in karte):
        print("Feld mensch_spricht fehlt in der Clip-Karte — erst je Clip setzen (SKILL.md Schritt 0)."); sys.exit(3)
    ziel = [c for c in karte if c.get("mensch_spricht", c.get("sprecherin_spricht")) and not c.get("lipsync_aus")]
    if not ziel: print("Kein Mensch spricht laut Clip-Karte (oder alle per lipsync_aus ausgenommen) — Knoten entfällt."); sys.exit(4)
    breite, hoehe, fps = sonde(a.basis)
    zielframes = {}
    for c in ziel:
        for f in range(int(round(c["t0"] * fps)), int(round(c["t1"] * fps))): zielframes[f] = c
    gesicht, ycc = {}, {}
    for f, rgb in enumerate(frames(a.basis, breite, hoehe)):
        if f in zielframes:
            gesicht[f] = gesicht_gross(rgb)
            ycc[f] = cv2.cvtColor(cv2.resize(rgb, (90, int(90 * rgb.shape[0] / rgb.shape[1]))), cv2.COLOR_RGB2YCrCb).reshape(-1, 3).mean(axis=0)
    auftraege, namen = [], set()
    for c in ziel:
        fr = list(range(int(round(c["t0"] * fps)), int(round(c["t1"] * fps))))
        fr = [x for x in fr if x in ycc]
        if not fr: continue
        v = schliesse_luecken([gesicht.get(x, False) for x in fr])
        rolle = c.get("mensch_rolle") or ("sprecherin" if c.get("sprecherin_spricht") else "mensch")
        audio = a.audio
        if c.get("mensch_rolle"):
            kandidat = f"_work/sprechspur_{c['mensch_rolle']}.wav"
            if os.path.exists(kandidat): audio = kandidat
            else: print(f"WARNUNG: Clip {c['clip']}: {kandidat} fehlt — nehme {a.audio} (Rollen-Name prüfen, sonst spricht eine fremde Stimme mit)")
        for i, j in laeufe(v):
            seg = np.array([ycc[fr[k]] for k in range(i, j)]); ref = np.median(seg, axis=0)
            weg = np.zeros(j - i, bool)
            for k in range(j - i):
                if ist_blitz(seg[k], ref): weg[max(0, k - RAND):k + RAND + 1] = True
            # Blitz direkt hinter dem Lauf-Ende bzw. vor dem Lauf-Anfang (Gesicht schon in der Blende verloren)
            if any(ist_blitz(ycc[fr[q]], ref) for q in range(j, min(len(fr), j + NACHBAR))): weg[max(0, j - i - RAND):] = True
            if any(ist_blitz(ycc[fr[q]], ref) for q in range(max(0, i - NACHBAR), i)): weg[:RAND] = True
            ausgeschnitten = [[fr[i + p], fr[i + q - 1] + 1] for p, q in laeufe(list(weg))]
            for p, q in laeufe(list(~weg)):
                if q - p < MIN_LAUF: continue
                name = f"{rolle[:3]}_c{int(c['clip']):02d}"; n = 2
                while name in namen: name = f"{rolle[:3]}_c{int(c['clip']):02d}_{n}"; n += 1
                namen.add(name)
                f0, f1 = fr[i + p], fr[i + q - 1] + 1
                auftraege.append({"name": name, "clip": c["clip"], "f0": f0, "f1": f1, "t0": round(f0 / fps, 3), "t1": round(f1 / fps, 3),
                                  "dauer": round((f1 - f0) / fps, 2), "audio": audio, "blitz_ausgeschnitten": ausgeschnitten})
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); os.makedirs("_work/lipsync", exist_ok=True)
    json.dump(auftraege, open(a.out, "w"), indent=1, ensure_ascii=False)
    ueb = os.path.join(os.path.dirname(a.out) or ".", "lipsync_uebergaenge.json")
    if not os.path.exists(ueb): json.dump({}, open(ueb, "w"))
    if not auftraege:
        print(f"0 Aufträge, obwohl {len(ziel)} Clips mit mensch_spricht — Gesichter zu klein (< {GESICHT_MIN:.0%} Bildbreite) oder Läufe zu kurz. Befund an den Nutzer.")
        sys.exit(5)
    ges = sum(x["dauer"] for x in auftraege); kosten = sum(8 * int(x["dauer"]) for x in auftraege)
    print(f"{len(auftraege)} Aufträge · {ges:.1f} s · Kosten ≈ {kosten} kie-Credits (lite: 8 je volle Sekunde) → {a.out}")
    for x in auftraege:
        print(f"  {x['name']:12} {x['t0']:8.2f}–{x['t1']:8.2f} s ({x['dauer']:.2f} s)" + (f" · Blitz/Blende ausgeschnitten {x['blitz_ausgeschnitten']}" if x["blitz_ausgeschnitten"] else ""))

if __name__ == "__main__": main()
