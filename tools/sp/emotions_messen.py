#!/usr/bin/env python3
"""emotions_messen.py — Emotions-Karte auf dem ERSATZWEG: gemessen statt gehört.

Wann: Nur wenn das Gemini-Ohr nachweislich ausgefallen ist — also NACH einem
Transkriptions-Test mit eigenem Schnipsel bekannten Wortlauts, bei dem ALLE Routen
durchgefallen sind (Skill speaking-vsl-emotionskarte, Anker-Regel). Solange das Ohr
antwortet, gilt `emotions_karte.py`; dieses Werkzeug ersetzt es nie freiwillig.

Warum es trotzdem geht: Delivery ist akustisch. Was das Ohr aus dem Schnipsel HÖRT
(Emotion, Ton, Tempo, Betonung, Pausen), steckt messbar in Tonhöhe, Tonhöhen-Spanne,
Lautheit, Sprechrate und Pausenlänge. Gemessen wird am ORIGINAL — die Karte überträgt
also weiterhin belegte Delivery, nur mit einem anderen Instrument.

**Ehrlichkeits-Pflicht:** Jede Zeile der Ausgabe trägt `quelle: "gemessen"` statt
`route: "<modell>/<kanal>"`. Wer die Karte später liest, muss sehen können, dass hier
kein Modell zugehört hat. Die Zahlen stehen mit in der Ausgabe, damit das Urteil
nachrechenbar bleibt.

Aufruf (CWD = Pipeline-Ordner, brands/<Brand>/<NNN> EL/):
  python3 tools/sp/emotions_messen.py --bloecke _pipeline/emo_bloecke.json
Eingabe wie beim Ohr-Werkzeug: [{"t0":…, "t1":…, "en":"…"}, …] auf SATZ-Ebene.
Ausgabe: _pipeline/emotions_karte.json
"""
import argparse, json, os, subprocess, sys
import numpy as np

TAGS = ["whispers", "sighs", "excited", "angry", "stern", "serious", "warm", "reassuring",
        "urgent", "sarcastic", "curious", "confident", "calm", "dramatic", "emphatic"]

ap = argparse.ArgumentParser()
ap.add_argument("--bloecke", required=True)
ap.add_argument("--quelle", default=None)
ap.add_argument("--aus", default="_pipeline/emotions_karte.json")
a = ap.parse_args()

BASIS = os.getcwd()
SRC = a.quelle or next((p for p in (f"{BASIS}/_work/source_original.mp4", f"{BASIS}/_work/source.mp4")
                        if os.path.exists(p)), None)
if not SRC:
    sys.exit("Keine Quelle gefunden (_work/source_original.mp4 oder source.mp4).")

import librosa
WAV = f"{BASIS}/_work/_emo_ton.wav"
subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", SRC, "-vn", "-ac", "1",
                "-ar", "22050", WAV], check=True)
y, sr = librosa.load(WAV, sr=22050)

bloecke = json.load(open(a.bloecke))

def silben(text):
    """Grobe Silbenzahl EN — Vokalgruppen, stummes -e abgezogen. Reicht fuer die Rate."""
    n = 0
    for w in text.lower().split():
        w = "".join(c for c in w if c.isalpha())
        if not w:
            continue
        g = 0; vor = False
        for c in w:
            v = c in "aeiouy"
            if v and not vor:
                g += 1
            vor = v
        if w.endswith("e") and g > 1:
            g -= 1
        n += max(1, g)
    return n

# --- je Satz messen ---------------------------------------------------------------
roh = []
for i, b in enumerate(bloecke):
    s0, s1 = int(b["t0"] * sr), int(min(b.get("sprech_ende", b["t1"]), b["t1"]) * sr)
    seg = y[s0:max(s1, s0 + sr // 10)]
    f0, vf, _ = librosa.pyin(seg, fmin=70, fmax=400, sr=sr)
    v = f0[~np.isnan(f0)]
    rms = librosa.feature.rms(y=seg)[0]
    db = 20 * np.log10(np.maximum(np.median(rms), 1e-8))
    dauer = (s1 - s0) / sr
    roh.append({
        "f0_med": float(np.median(v)) if len(v) else None,
        "f0_iqr": float(np.percentile(v, 75) - np.percentile(v, 25)) if len(v) > 8 else None,
        "db": float(db),
        "silben_s": silben(b["en"]) / max(dauer, 0.1),
        "pause_davor": round(b["t0"] - bloecke[i-1].get("sprech_ende", bloecke[i-1]["t1"]), 2) if i else 0.0,
        "pause_danach": round(b["t1"] - b.get("sprech_ende", b["t1"]), 2),
        "dauer": round(dauer, 2),
    })

# --- Bezugsgroessen der GANZEN Spur: alles ist relativ zur eigenen Ad ---------------
def med(k):
    w = [r[k] for r in roh if r[k] is not None]
    return float(np.median(w)) if w else 0.0

M = {k: med(k) for k in ("f0_med", "f0_iqr", "db", "silben_s")}

def tags(r, rolle):
    """Tags aus MESSUNG + Rolle im Pitch. Hoehe/Spanne/Lautheit/Tempo relativ zur Ad."""
    t = []
    hoch = r["f0_med"] and r["f0_med"] > M["f0_med"] * 1.05
    tief = r["f0_med"] and r["f0_med"] < M["f0_med"] * 0.95
    weit = r["f0_iqr"] and r["f0_iqr"] > M["f0_iqr"] * 1.25
    eng  = r["f0_iqr"] and r["f0_iqr"] < M["f0_iqr"] * 0.75
    laut = r["db"] > M["db"] + 2.0
    leise = r["db"] < M["db"] - 2.5
    schnell = r["silben_s"] > M["silben_s"] * 1.12
    langsam = r["silben_s"] < M["silben_s"] * 0.88

    if rolle == "cta":
        t.append("confident")
        if laut or schnell: t.append("urgent")
    elif rolle == "hook":
        t.append("curious" if weit else "serious")
    elif rolle == "problem":
        t.append("serious")
        if leise or langsam: t.append("sighs")
        if weit and laut: t.append("dramatic")
    elif rolle == "loesung":
        t.append("confident" if not leise else "calm")
        if weit: t.append("excited")
    elif rolle == "beweis":
        t.append("emphatic" if laut or weit else "confident")
    elif rolle == "anker":
        t.append("warm")
        if leise or langsam: t.append("reassuring")
    else:
        t.append("calm")

    if leise and eng and "whispers" not in t: t.append("whispers")
    if hoch and weit and "excited" not in t and rolle != "problem": t.append("excited")
    if tief and langsam and "serious" not in t: t.append("serious")
    aus, seen = [], set()
    for x in t:
        if x in TAGS and x not in seen:
            aus.append(x); seen.add(x)
    return aus[:2]

rollen = json.load(open(a.bloecke.replace(".json", "_rollen.json"))) if \
    os.path.exists(a.bloecke.replace(".json", "_rollen.json")) else {}

rows = []
for i, (b, r) in enumerate(zip(bloecke, roh)):
    rolle = rollen.get(str(i), "mitte")
    rows.append({
        "zeile": i, "t0": b["t0"], "t1": b["t1"], "en": b["en"],
        "rolle": rolle,
        "messung": {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()},
        "v3_tags": tags(r, rolle),
        "quelle": "gemessen (Gemini-Ohr ausgefallen — Anker-Test aller Routen durchgefallen)",
    })

json.dump({"bezug": {k: round(v, 2) for k, v in M.items()}, "zeilen": rows},
          open(a.aus, "w"), ensure_ascii=False, indent=1)
os.remove(WAV)
print(f"[emo] {len(rows)} Zeilen gemessen -> {a.aus}")
print(f"[emo] Bezug der Ad: F0 {M['f0_med']:.0f} Hz · Spanne {M['f0_iqr']:.0f} Hz · "
      f"Pegel {M['db']:.1f} dB · Tempo {M['silben_s']:.2f} Silben/s")
