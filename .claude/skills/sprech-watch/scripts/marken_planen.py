#!/usr/bin/env python3
"""Marken nach GEMESSENER Sprechdauer verteilen (Voice-over ohne Lippen-Sync).

Aufruf (CWD = Pipeline-Ordner):
  python3 marken_planen.py <messung.json> <marken.json> [--start 0.10] [--ende <video_s>]
messung.json = Ausgabe von `sprechspur.py montage --nur-messen`; marken.json wird IN PLACE neu
geschrieben (Texte bleiben, start/ende werden gesetzt). Jeder Block bekommt seine gemessene
Sprechdauer plus den Atem; passt die Summe nicht in die Videolänge, wird gleichmäßig gestaucht
und der nötige Block-atempo gemeldet (über 1,15 → Copy kürzen, das ist Viktors Gate-Frage).
Warum: v3 würfelt die Pace je Take um ±10 % — Marken nach Wortzahl treffen die echte Dauer nicht.
"""
import json, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("messung"); ap.add_argument("marken")
ap.add_argument("--start", type=float, default=0.10); ap.add_argument("--ende", type=float)
ap.add_argument("--kanten", help="Clip-Karte (_pipeline/clip_karte.json): Marken, deren Original-Stempel auf einer "
                "Schnittkante liegen (±0,25 s), bleiben dort verankert — nur Marken mitten im Clip wandern")
ap.add_argument("--toleranz", type=float, default=0.25)
ap.add_argument("--soll", help="marken.json mit den ORIGINAL-Stempeln (vor der ersten Planung). "
                "Liegt sie vor und bleibt Luft uebrig, beginnt jeder Block fruehestens an seinem "
                "Original-Stempel — die Luft verteilt sich dann wie im Original, statt sich als ein "
                "Loch vor dem naechsten Anker zu sammeln (belegt VIS 006 EL: 4,04 s Stille vor dem Offer).")
a = ap.parse_args()
mess = json.load(open(a.messung)); marken = json.load(open(a.marken))
soll = [m["start"] for m in json.load(open(a.soll))] if a.soll else None
ende = a.ende or mess["video_s"]; atem = mess["atem"]
d = [b["sprechdauer"] for b in mess["bloecke"]]

# Anker: Marken auf Schnittkanten (Original-Stempel = aktueller "start" beim ersten Aufruf)
anker = {}
if a.kanten:
    kanten = sorted(c["t0"] for c in json.load(open(a.kanten)))
    for i, m in enumerate(marken):
        naechste = min(kanten, key=lambda k: abs(k - m["start"]))
        if abs(naechste - m["start"]) <= a.toleranz: anker[i] = round(naechste + 0.02, 2)
    anker[0] = anker.get(0, a.start)
else:
    anker[0] = a.start

# Abschnitte zwischen zwei Ankern werden je für sich verteilt
idx = sorted(anker); grenzen = idx + [len(marken)]
schlimmster = 1.0; bericht = []
for g, start_i in enumerate(idx):
    end_i = grenzen[g + 1]
    t0 = anker[start_i]; t1 = anker[grenzen[g + 1]] if end_i < len(marken) else ende
    bloecke = list(range(start_i, end_i)); bedarf = sum(d[i] for i in bloecke) + atem * len(bloecke)
    scale = min(1.0, (t1 - t0) / bedarf) if bedarf else 1.0
    t = t0
    for n, i in enumerate(bloecke):
        # Bleibt Luft übrig (scale == 1), NICHT dicht packen: sonst sammelt sich der
        # ganze Überschuss als EIN Loch vor dem nächsten Anker. Bei VIS 006 EL waren das
        # 4,04 s Stille direkt vor dem Offer — mitten in der Ad (sp-learnings 30: „Der Weg
        # zu null toter Luft ist eine Schleife"). Stattdessen darf jeder Block frühestens
        # an seinem ORIGINAL-Stempel beginnen, solange der Rest noch hineinpasst. Das
        # verteilt die Luft dorthin, wo sie im Original auch war, statt sie zu häufen.
        if soll is not None and scale >= 1.0:
            rest = sum(d[j] for j in bloecke[n:]) + atem * len(bloecke[n:])
            spaetest = t1 - rest
            t = min(max(t, soll[i]), max(t, spaetest))
        marken[i]["start"] = round(t, 2); t += d[i] * scale + atem; marken[i]["ende"] = round(min(t, t1), 2)
    marken[end_i - 1]["ende"] = round(t1, 2)
    f = 1 / scale; schlimmster = max(schlimmster, f)
    bericht.append(f"Abschnitt Block {start_i}-{end_i-1} ({t0:.2f}-{t1:.2f}s): Bedarf {bedarf:.2f}s, atempo {f:.3f}")
json.dump(marken, open(a.marken, "w"), ensure_ascii=False, indent=0)
print("\n".join(bericht))
print(f"Marken: {[m['start'] for m in marken]} · Anker auf Kanten: {sorted(anker)} · Block-atempo nötig (max): {schlimmster:.3f}"
      + (" — über 1,15: Zeile kürzen (Gate-Frage), Kante bleibt" if schlimmster > 1.15 else ""))
sys.exit(1 if schlimmster > 1.15 else 0)
