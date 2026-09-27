#!/usr/bin/env python3
"""bildbasis_platte.py — Bildbasis für Quellen mit GEFÜLLTER Caption-Platte.

Problem (belegt VIS 006 EL, 18.09.2026): Manche Quell-Ads brennen ihre Sprech-Untertitel
als weisse Schrift auf eine DECKEND SCHWARZE Platte. Vmakes `videoscreenclear` ist für
dünne Schrift und Wasserzeichen gebaut — es tilgt die Buchstaben, lässt die FLÄCHE aber
als weichkantigen Schmierbalken stehen (Skill vmake-caption-entfernen: „die Buchstaben
verschwinden, die FLÄCHE dahinter bleibt als Keil stehen"). Ein zweiter Vmake-Lauf bringt
messbar nichts (VIS 006 EL: 62,0 % → 61,3 % dunkle Pixel im Band).

Hinter einer deckenden Platte liegt KEIN Bild — es gibt nichts wiederherzustellen, nur
zu erfinden. Der deterministische Weg (0 Credits, kein Generator, kein Vmake):

  Buchstaben schwarz übermalen, Platte bleibt — sauber statt verschmiert.

Der Trick ist die GEOMETRIE-QUELLE: nicht die dunklen Pixel (daran sind drei Anläufe
gescheitert — Buchstaben brechen jede Zeilen-Messung, dunkle Szenen kippen jedes
Spalten-Profil), sondern die **OCR-Textboxen des Originals**. Sie sagen framegenau, wo
Schrift steht. Wird dieser Kasten plus kleinem Rand mit der Plattenfarbe gefüllt, liegt
die Füllung IMMER innerhalb der Platte (deren Rand rund 15–25 px breit ist) — schwarz
auf schwarz, also unsichtbar, und kein Buchstabe bleibt stehen.

Aufruf (CWD = Pipeline-Ordner, brands/<Brand>/<NNN> EL/_pipeline):
  1. OCR-Bänder erzeugen:
     ffmpeg -i ../_work/source_original.mp4 -vf "fps=4,crop=<W>:<H>:0:<OFF>" ../_work/ocr_orig_band/f%04d.jpg
     ./ocr_vision ../_work/ocr_orig_band 4 > ocr_orig_band.jsonl
  2. python3 tools/sp/bildbasis_platte.py --quelle ../_work/source_original.mp4 \
       --ziel ../_work/bild_basis.mp4 --ocr ocr_orig_band.jsonl \
       --crop 720 150 875 [--rand-x 10 --rand-y 8]
"""
import argparse, json, os, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--quelle", required=True)
ap.add_argument("--ziel", required=True)
ap.add_argument("--ocr", required=True, help="jsonl von ocr_vision über das Caption-Band")
ap.add_argument("--crop", nargs=3, type=int, required=True, metavar=("W", "H", "Y"),
                help="Geometrie des Bandes, auf dem das OCR lief")
ap.add_argument("--rand-x", type=int, default=10, help="Rand um den Textkasten, waagerecht")
ap.add_argument("--rand-y", type=int, default=8, help="Rand um den Textkasten, senkrecht")
ap.add_argument("--conf", type=float, default=0.30)
ap.add_argument("--bandbilder", default=None,
                help="Ordner der Band-JPGs, auf denen das OCR lief. Damit wird je Textbox "
                     "gemessen, ob sie auf DUNKLEM Grund sitzt (Caption) oder auf hellem "
                     "(Produkt-Etikett). Ohne diese Trennung deckt die Fuellung auch "
                     "Gestaltungs-Text ab — belegt VIS 006 EL bei 77,0 s und 110,5 s.")
ap.add_argument("--grund-max", type=float, default=30.0,
                help="Hoechster MEDIAN-Grauwert im Kasten, damit er als Caption gilt. Median, "
                     "nicht Mittelwert: Bei kurzen Woertern mit grossen Versalien ('SWEATER', "
                     "'GRIEVING') fuellen die weissen Buchstaben so viel Flaeche, dass der "
                     "Mittelwert ueber 90 steigt und die Caption faelschlich als Etikett gilt — "
                     "gemessen VIS 006 EL: Mittel 91-95, Median 6-10. Gemessene Trennung: "
                     "Captions Median 2-10, Etikett-Text 69-210.")
ap.add_argument("--halte", type=float, default=0.30,
                help="Sekunden, um die eine Box nach vorn und hinten gilt (deckt Übergänge)")
a = ap.parse_args()
CW, CH, COFF = a.crop

probe = json.loads(subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0",
     "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", a.quelle],
    capture_output=True, text=True).stdout)["streams"][0]
W, H = int(probe["width"]), int(probe["height"])
num, den = probe["r_frame_rate"].split("/")
FPS = int(num) / int(den)

# --- OCR-Boxen einlesen und auf Bildkoordinaten umrechnen -------------------------
# Wichtig: NUR die Sprech-Captions fuellen. Produkt-Etiketten stehen dunkel auf hell,
# Captions weiss auf schwarzer Platte — der MEDIAN-Grauwert im Kasten trennt beides
# zuverlaessig (der Mittelwert NICHT: kurze Woerter mit grossen Versalien heben ihn ueber
# die Schwelle, VIS 006 EL verlor so „SWEATER", „HAD", „DRIVING", „GRIEVING"). Ohne die Trennung deckt die Fuellung Gestaltungs-Text mit ab und
# verletzt die Schutzliste (belegt VIS 006 EL: „Dietary Supplement", Bullet-Zeilen und
# das Kapsel-Badge verschwanden bei 77,0 s und 110,5 s).
bilder = None
if a.bandbilder:
    from PIL import Image
    import os
    bilder = {os.path.basename(p): os.path.join(a.bandbilder, p)
              for p in sorted(os.listdir(a.bandbilder)) if p.lower().endswith((".jpg", ".jpeg", ".png"))}

boxen = []                                   # (t, x0, x1, y0, y1)
verworfen = 0
for z in open(a.ocr):
    d = json.loads(z)
    t = [x for x in d["texte"] if x["conf"] > a.conf]
    if not t:
        continue
    if bilder is not None:
        p = bilder.get(os.path.basename(d.get("datei", "")))
        if p:
            im = np.asarray(Image.open(p).convert("L"), dtype=np.float32)
            bh, bw = im.shape
            behalten = []
            for x in t:
                cx0, cx1 = int(x["x"] * bw), int((x["x"] + x["w"]) * bw)
                cy0, cy1 = int(x["y"] * bh), int((x["y"] + x["h"]) * bh)
                aus = im[max(0, cy0):min(bh, cy1), max(0, cx0):min(bw, cx1)]
                if aus.size and float(np.median(aus)) <= a.grund_max:
                    behalten.append(x)
                else:
                    verworfen += 1
            t = behalten
            if not t:
                continue
    boxen.append((float(d["t"]),
                  min(x["x"] for x in t) * CW,
                  max(x["x"] + x["w"] for x in t) * CW,
                  min(x["y"] for x in t) * CH + COFF,
                  max(x["y"] + x["h"] for x in t) * CH + COFF))
if verworfen:
    print(f"[platte] {verworfen} Textboxen auf HELLEM Grund verworfen (Produkt-Etikett, nicht Caption)")
if not boxen:
    sys.exit("OCR-Datei enthaelt keine Textboxen — Band oder Schwelle pruefen.")
zeiten = np.array([b[0] for b in boxen])
print(f"[platte] {len(boxen)} OCR-Frames mit Text, {zeiten.min():.2f}–{zeiten.max():.2f} s")

def kasten(t):
    """Vereinigung aller OCR-Boxen im Fenster t ± halte — deckt auch Caption-Wechsel."""
    m = np.abs(zeiten - t) <= a.halte
    if not m.any():
        return None
    aus = [b for b, k in zip(boxen, m) if k]
    x0 = min(b[1] for b in aus) - a.rand_x
    x1 = max(b[2] for b in aus) + a.rand_x
    y0 = min(b[3] for b in aus) - a.rand_y
    y1 = max(b[4] for b in aus) + a.rand_y
    return (max(0, int(x0)), min(W, int(x1)), max(0, int(y0)), min(H, int(y1)))

# --- Plattenfarbe messen: dunkelster Kern im ersten Textkasten ---------------------
ers = kasten(boxen[0][0])
roh = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(boxen[0][0]), "-i", a.quelle,
                      "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     capture_output=True).stdout
f0 = np.frombuffer(roh, np.uint8)[:W * H * 3].reshape(H, W, 3)
aus = f0[ers[2]:ers[3], ers[0]:ers[1]].reshape(-1, 3)
dunkel = aus[aus.mean(axis=1) < 30]
FARBE = (dunkel.mean(axis=0).round().astype(np.uint8) if len(dunkel)
         else np.array([0, 0, 0], np.uint8))
print(f"[platte] Plattenfarbe gemessen: RGB {list(FARBE)} (n={len(dunkel)})")

# --- durchreichen und fuellen ------------------------------------------------------
lese = subprocess.Popen(
    ["ffmpeg", "-nostdin", "-v", "error", "-i", a.quelle, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    stdout=subprocess.PIPE)
schreib = subprocess.Popen(
    ["ffmpeg", "-nostdin", "-v", "error", "-y",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{FPS}", "-i", "-",
     "-i", a.quelle, "-map", "0:v", "-map", "1:a?",
     "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
     "-c:a", "copy", a.ziel],
    stdin=subprocess.PIPE)

GROESSE = W * H * 3
n = gefuellt = 0
while True:
    roh = lese.stdout.read(GROESSE)
    if len(roh) < GROESSE:
        break
    f = np.frombuffer(roh, np.uint8).reshape(H, W, 3).copy()
    k = kasten(n / FPS)
    if k:
        f[k[2]:k[3], k[0]:k[1]] = FARBE
        gefuellt += 1
    schreib.stdin.write(f.tobytes())
    n += 1

schreib.stdin.close(); schreib.wait(); lese.wait()
print(f"[platte] {n} Frames · Textkasten gefuellt in {gefuellt} ({100*gefuellt/max(n,1):.1f} %) "
      f"· Rand x{a.rand_x}/y{a.rand_y} · {a.ziel}")
