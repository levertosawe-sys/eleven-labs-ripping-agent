#!/usr/bin/env python3
"""Ist das extrahierte Musikbett sauber? — Loch-Messung statt Ohr.

Eine Stimmen-Trennung (Demucs) hinterlässt im Rest-Stem dort, wo die Original-Stimme
sprach, Löcher im Sprachband: die Musik-Energie 300–3400 Hz ist dort leiser als in den
Sprechpausen. Im Original deckt die Stimme das zu; unter der deutschen Sprechspur liegen
die Löcher frei und klingen als Pumpen/Wabern („nicht clean"). Das Gemini-Ohr erkennt das
nachweislich nicht (Kontroll-Snippet: unberührtes Suno-Instrumental bekam dasselbe Urteil).

CWD = Pipeline-Ordner. Aufruf:
  python3 bett_qualitaet.py [--vocals …] [--bett …] [--schwelle 5]
Misst je 2048-Sample-Frame die Sprachband-Energie des Betts in den Frames, in denen die
Original-Stimme laut ist (oberes 40 %), gegen ihre Pausen (unterstes 15 %) — Differenz =
Loch-Tiefe; dazu das gleiche für 3,4–8 kHz. Exit 0 = sauber (Loch < Schwelle), Exit 3 =
nicht sauber → Nachbau-Weg laut speaking-vsl-musikbett. Schreibt _work/bett_qualitaet.json.
"""
import argparse, json, os, sys
import numpy as np, soundfile as sf

def load(p):
    x, sr = sf.read(p); x = x.mean(axis=1) if x.ndim > 1 else x; return x, sr

def stft(x, N=2048, H=1024):
    w = np.hanning(N); m = (len(x) - N) // H
    return np.array([np.abs(np.fft.rfft(x[i*H:i*H+N] * w)) for i in range(m)])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vocals", default="_work/demucs_out/htdemucs/original_ton/vocals.wav")
    ap.add_argument("--bett", default="_work/musikbett.wav")
    ap.add_argument("--schwelle", type=float, default=5.0)
    a = ap.parse_args()
    for f in (a.vocals, a.bett):
        if not os.path.exists(f): print(f"fehlt: {f}"); sys.exit(1)
    vo, sr = load(a.vocals); re_, sr2 = load(a.bett)
    if sr2 != sr: print("Abtastraten ungleich — Bett auf die Rate der Stems bringen"); sys.exit(1)
    n = min(len(vo), len(re_)); SV = stft(vo[:n]); SR = stft(re_[:n]); f = np.fft.rfftfreq(2048, 1/sr)
    band = (f >= 300) & (f <= 3400); hi = (f > 3400) & (f <= 8000)
    ev = 20*np.log10(SV[:, band].sum(axis=1) + 1e-9)
    er = 20*np.log10(SR[:, band].sum(axis=1) + 1e-9); erh = 20*np.log10(SR[:, hi].sum(axis=1) + 1e-9)
    act = ev > np.percentile(ev, 60); pause = ev < np.percentile(ev, 15)
    loch = float(np.median(er[pause]) - np.median(er[act])); loch_hi = float(np.median(erh[pause]) - np.median(erh[act]))
    korr = float(np.corrcoef(er, ev)[0, 1])
    sauber = loch < a.schwelle
    out = {"bett": a.bett, "loch_sprachband_db": round(loch, 1), "loch_hoehen_db": round(loch_hi, 1),
           "korrelation_bett_stimme": round(korr, 2), "schwelle_db": a.schwelle, "sauber": sauber,
           "regel": "Loch = Bett-Energie in Original-Sprechpausen minus bei lauter Original-Stimme; ab Schwelle klingt das Bett unter einer anderen Stimme nicht clean → Nachbau"}
    os.makedirs("_work", exist_ok=True); json.dump(out, open("_work/bett_qualitaet.json", "w"), ensure_ascii=False, indent=1)
    print(f"Loch Sprachband {loch:.1f} dB · Höhen {loch_hi:.1f} dB · Korrelation Bett↔Stimme {korr:+.2f} → {'SAUBER' if sauber else 'NICHT SAUBER (Nachbau)'} (Schwelle {a.schwelle} dB)")
    sys.exit(0 if sauber else 3)

if __name__ == "__main__": main()
