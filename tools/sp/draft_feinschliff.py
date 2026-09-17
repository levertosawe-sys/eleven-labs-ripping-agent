#!/usr/bin/env python3
"""Feinschliff am fertigen CapCut-Draft der Speaking-Kette — rein über die JSON-Dateien,
kein Bildschirm, keine Fernsteuerung.

Läuft NACH capcut_export.draft_bauen() auf dem Mac (Paket-Anleitung Schritt 2).
Setzt deterministisch:
  - fette Caption(s): nach OBEN auf den Gestaltungs-Balken (Ziel-Höhe aus
    fette_captions.json, Feld ziel_hoehe_prozent; Default 14,3 %), Skalierung größer
  - Mitlese-Häppchen: unten mittig auf 81 % Höhe

Die Y-Achsen-Richtung wird NICHT geraten: Das Skript liest die Spender-Position der
Mitlese-Segmente (sie sitzen sichtbar unter der Mitte) und leitet das Vorzeichen ab.
Landet es trotzdem gespiegelt (Spender saß über der Mitte): --flip.

Usage:  python3 draft_feinschliff.py "<Projektname>" [--fette N] [--fette-scale 1.35] [--flip]
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capcut_export as ce

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("--fette", type=int, default=1)
ap.add_argument("--fette-scale", type=float, default=1.35)
ap.add_argument("--flip", action="store_true")
a = ap.parse_args()

pfad = ce.draft_pfad(a.name) / "draft_info.json"
if not pfad.exists():
    alt = ce.draft_pfad(a.name) / "draft_content.json"
    if alt.exists(): pfad = alt
    else: sys.exit(f"ABBRUCH: kein Draft unter {pfad.parent} — erst draft_bauen laufen lassen")
d = json.loads(pfad.read_text())
tt = next((t for t in d["tracks"] if t["type"] == "text" and t.get("segments")), None)
if not tt: sys.exit("ABBRUCH: keine Text-Spur im Draft")
segs = sorted(tt["segments"], key=lambda s: s["target_timerange"]["start"])
fette, mitlese = segs[:a.fette], segs[a.fette:]

def y_von(seg, default=0.0):
    return float(((seg.get("clip") or {}).get("transform") or {}).get("y", default))
spender_y = next((y_von(s) for s in mitlese if y_von(s) != 0.0), 0.0)
# Spender-Mitlese sitzt UNTER der Mitte: sein Vorzeichen = „unten". 0 → CapCut-Standard: positiv = unten.
unten = 1.0 if spender_y >= 0 else -1.0
if a.flip: unten = -unten

ziel_hoehe = 14.3
fc = Path("fette_captions.json")
if fc.exists():
    j = json.loads(fc.read_text())
    if j and isinstance(j, list): ziel_hoehe = float(j[0].get("ziel_hoehe_prozent", 14.3))
fette_y  = unten * (ziel_hoehe/100.0 - 0.5) * 2.0     # 14,3 % Höhe → weit oben
mitlese_y = unten * (0.81 - 0.5) * 2.0                # 81 % Höhe → unten

def setze(seg, y, scale=None):
    clip = seg.setdefault("clip", {})
    clip.setdefault("transform", {"x": 0.0, "y": 0.0})["y"] = round(y, 4)
    clip["transform"].setdefault("x", 0.0)
    if scale:
        s = clip.setdefault("scale", {"x": 1.0, "y": 1.0})
        s["x"] = round(float(s.get("x", 1.0)) * scale, 4)
        s["y"] = round(float(s.get("y", 1.0)) * scale, 4)

for s in fette: setze(s, fette_y, a.fette_scale)
for s in mitlese: setze(s, mitlese_y)
pfad.write_text(json.dumps(d, ensure_ascii=False))
print(f"Feinschliff OK: {len(fette)} fette Caption(s) → y={fette_y:+.3f} (Ziel {ziel_hoehe} % Höhe, Scale x{a.fette_scale}) · "
      f"{len(mitlese)} Mitlese → y={mitlese_y:+.3f} (81 %) · Spender-y war {spender_y:+.3f} · Achse: positiv={'unten' if unten>0 else 'oben'}")
print("Danach CapCut NEU STARTEN — es liest Drafts nur beim Start.")
