#!/usr/bin/env python3
"""Projekt-Bootstrap der Speaking-Kette.

Legt brands/<Brand>/<NNN> EL/ an (_pipeline + _work), schreibt sp_config.json,
kopiert das Quellvideo als _work/source.mp4, baut _pipeline/source_words.json aus
dem Scribe-Roh-JSON des Projekts, portiert clip_karte.py und trägt den
Pipeline-Ordner in die karte.md der Projekte-DB nach.

Aufruf (vom Projektstamm, dem Ordner mit .claude/ und datenbanken/):
  python3 tools/sp/new_sp_project.py --projekt "ROV 007 | 20.08.2026" --video <mp4>
Die Brand kommt aus der karte.md des Projekts (Feld brand:), die Nummer aus dem
Projektnamen. Erfolg: Meldung mit Pipeline-Pfad; jeder Abbruch nennt, was fehlt.

NAMENS-GESETZ (Viktors Ansage 02.09.2026): Sprech-Projekte heissen
"KUERZEL NNN EL | DATUM" und haben eine EIGENE Nummern-Serie, getrennt von der
Suno-Kette. Der Ordner heisst entsprechend "NNN EL". Laeufe von VOR dem
02.09.2026 heissen "KUERZEL NNN | DATUM" mit Ordner "NNN SP" — die bleiben
gueltig und werden hier weiterhin akzeptiert (das Suffix folgt dem Namen).
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

STAMM = Path(__file__).resolve().parents[2]
DB = STAMM / "datenbanken" / "sp-projekte"

def lauf(cmd): return subprocess.run(cmd, capture_output=True, text=True)

ap = argparse.ArgumentParser()
ap.add_argument("--projekt", required=True)
ap.add_argument("--video", required=True)
a = ap.parse_args()

ordner = DB / a.projekt
karte = ordner / "karte.md"
if not karte.exists():
    sys.exit(f"karte.md fehlt: {karte} — erst das Projekt anlegen (Transkriptions-Skill).")
kt = karte.read_text(encoding="utf-8")
m = re.search(r"^brand:\s*(.+)$", kt, re.M)
if not m: sys.exit("karte.md trägt kein brand:-Feld.")
brand = m.group(1).strip()
m_name = re.match(r"^[A-ZÄÖÜ-]+ (\d{3})( EL)? \|", a.projekt)
if not m_name: sys.exit(f"Projektname passt nicht zur Konvention „KÜRZEL NNN [EL] | DATUM“: {a.projekt}")
nnn = m_name.group(1)
# Suffix folgt dem Namen: neue Projekte tragen EL, Alt-Bestand bleibt SP.
suffix = "EL" if m_name.group(2) else "SP"

P = STAMM / "brands" / brand / f"{nnn} {suffix}"
(P / "_pipeline").mkdir(parents=True, exist_ok=True)
(P / "_work").mkdir(exist_ok=True)

video = Path(a.video)
if not video.exists(): sys.exit(f"Quellvideo fehlt: {video}")
ziel = P / "_work" / "source.mp4"
if not ziel.exists(): shutil.copy2(video, ziel)

pr = lauf(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(ziel)])
dur = float(pr.stdout.strip() or 0)
if not dur: sys.exit(f"ffprobe liefert keine Dauer: {pr.stderr[:200]}")

roh = sorted(ordner.glob("*-transkript-roh-*.json"))
if not roh: sys.exit(f"Kein *-transkript-roh-*.json in {ordner} — erst transkribieren.")
d = json.loads(roh[-1].read_text(encoding="utf-8"))
slug = roh[-1].name.split("-transkript-roh-")[0]
words = [{"w": w["text"], "s": round(w["start"],2), "e": round(w["end"],2)} for w in d["woerter"]]
(P/"_pipeline"/"source_words.json").write_text(json.dumps(
    {"language":"en","quelle":video.name,"words":words}, ensure_ascii=False), encoding="utf-8")
(P/"_pipeline"/"sp_config.json").write_text(json.dumps(
    {"dur":dur,"projekt":a.projekt,"brand":brand,"slug":slug}, ensure_ascii=False), encoding="utf-8")

shutil.copy2(STAMM/"tools"/"sp"/"clip_karte.py", P/"_pipeline"/"clip_karte.py")

neu = re.sub(r"^pipeline-ordner:.*$", f"pipeline-ordner: brands/{brand}/{nnn} {suffix}", kt, flags=re.M)
if neu != kt: karte.write_text(neu, encoding="utf-8")
print(f"Bootstrap OK → {P.relative_to(STAMM)} · {dur:.2f}s · {len(words)} Wörter · slug={slug}")
