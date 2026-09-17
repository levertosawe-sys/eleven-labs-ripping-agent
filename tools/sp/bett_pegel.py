#!/usr/bin/env python3
"""Musikbett-Pegel messen statt schätzen — liefert --bett-db für render.py.

Misst K-bewertet (ebur128, Momentary 400 ms) in den SPRECH-Fenstern (Stimme > -40 LUFS):
  Original-Abstand = Stimme-Stem (vocals) − Rest-Stem (no_vocals) der Quelle,
  Ist-Abstand      = Sprechspur − Musikbett (bei 0 dB).
bett_db = Ist-Abstand − Original-Abstand + Marken-Offset. Der Marken-Offset kommt aus
datenbanken/sp-brands/daten.csv (Spalte bett_offset_db, Kürzel der Ziel-Brand) — Viktors
Ohr-Regler je Marke; die Original-Ratio ist der Messwert, der Offset das Urteil.

CWD = Pipeline-Ordner. Aufruf:
  python3 bett_pegel.py --kuerzel ARE [--vocals …] [--rest …] [--sprechspur …] [--bett …] [--leiter]
Schreibt _work/musik_wahl.json (alle Messwerte + bett_db); --leiter erzeugt zusätzlich
_work/gate/bett_leiter_{0,-3,-6}.mp3 (Sprechspur + Bett bei bett_db, bett_db−3, bett_db−6)
für die Audio-Prüfung — Viktor hört und wählt, seine Wahl wird der neue Offset der Marke.
Exit 1 = Stem oder Spur fehlt, Exit 2 = Kürzel ohne Zeile im Brand-Adressbuch.
"""
import argparse, csv, json, os, re, subprocess, sys
import numpy as np
STAMM = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def momentary(pfad):
    out = subprocess.run(["ffmpeg","-nostats","-i",pfad,"-af","ebur128=peak=none","-f","null","-"],capture_output=True,text=True).stderr
    m = [float(x) for x in re.findall(r"TARGET:-23 LUFS\s+M:\s*(-?[\d.]+)", out)]
    return np.array(m)

def abstand(stimme, bett, schwelle=-40.0):
    n = min(len(stimme), len(bett)); s, b = stimme[:n], bett[:n]
    akt = s > schwelle
    if akt.sum() < 20: sys.exit("zu wenige Sprech-Fenster — Stimm-Datei prüfen")
    return float(np.median(s[akt]) - np.median(b[akt])), int(akt.sum()), int(n)

def offset(kuerzel):
    pfad = f"{STAMM}/datenbanken/sp-brands/daten.csv"
    for z in csv.DictReader(open(pfad, encoding="utf-8")):
        if z["kuerzel"] == kuerzel:
            return float(z.get("bett_offset_db") or 0.0)
    sys.exit(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kuerzel", required=True)
    ap.add_argument("--vocals", default="_work/demucs_out/htdemucs/original_ton/vocals.wav")
    ap.add_argument("--rest", default="_work/demucs_out/htdemucs/original_ton/no_vocals.wav")
    ap.add_argument("--sprechspur", default="_work/sprechspur.wav")
    ap.add_argument("--bett", default="_work/musikbett.wav")
    ap.add_argument("--leiter", action="store_true")
    a = ap.parse_args()
    for f in (a.vocals, a.rest, a.sprechspur, a.bett):
        if not os.path.exists(f): print(f"fehlt: {f}"); sys.exit(1)
    orig, n_o, N_o = abstand(momentary(a.vocals), momentary(a.rest))
    ist, n_u, N_u = abstand(momentary(a.sprechspur), momentary(a.bett))
    off = offset(a.kuerzel)
    bett_db = round(ist - orig + off, 1)
    w = {"original_abstand_db": round(orig, 1), "original_sprechfenster": f"{n_o}/{N_o}",
         "ist_abstand_bei_0db": round(ist, 1), "unsere_sprechfenster": f"{n_u}/{N_u}",
         "marken_offset_db": off, "bett_db": bett_db,
         "regel": "bett_db = Ist-Abstand − Original-Abstand + Marken-Offset (K-bewertet, Momentary, nur Sprech-Fenster)"}
    os.makedirs("_work", exist_ok=True); json.dump(w, open("_work/musik_wahl.json", "w"), ensure_ascii=False, indent=1)
    print(f"Original Stimme→Bett {orig:.1f} dB ({n_o}/{N_o} Sprech-Fenster) · unsere bei 0 dB {ist:.1f} dB · Marken-Offset {off:+.1f} → --bett-db {bett_db:+.1f}")
    if a.leiter:
        os.makedirs("_work/gate", exist_ok=True)
        for stufe in (0, -3, -6):
            g = bett_db + stufe; out = f"_work/gate/bett_leiter_{stufe}.mp3"
            subprocess.run(["ffmpeg","-y","-v","error","-i",a.sprechspur,"-i",a.bett,"-filter_complex",
                            f"[1]volume={g}dB[b];[0][b]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5",
                            "-c:a","libmp3lame","-b:a","160k",out],check=True)
            print(f"Leiter {stufe:+d} dB → {out} (bett_db {g:+.1f})")

if __name__ == "__main__": main()
