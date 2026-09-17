---
name: speaking-vsl-musikbett
description: "Das Instrumental-Bett einer Speaking-VSL aus dem Original gewinnen: Demucs trennt die Original-Tonspur in Stimme und Musik, das Musikbett läuft unter die neue deutsche Sprechspur. Nutzen beim Schnitt der Speaking-Kette oder wenn „Musikbett", „Hintergrundmusik", „die Musik fehlt" fällt."
---

# Musikbett — die Original-Musik wird gerippt, nicht neu erfunden

Die bewiesene Ad hat ihre Musik schon: Sie liegt zusammen mit den Soundeffekten unter
der Original-Stimme. Demucs trennt die Tonspur in Stimme und Rest — der Rest IST das
Bett: Musik UND Effekte der Quelle, 1:1. Beides bleibt (Viktors Maßstab: „die
Soundeffekte sollen so bleiben" und „kannst du nicht die Original-Musik extrahieren").
Keine neue Musik, kein Suno — außer die Quelle hat nachweislich keine oder Viktor sagt
am Gate „nicht clean“ (Nachbau-Weg unten).

**Sauberkeit des Extrakts — messen als Beleg, entscheiden am Gate.** Die Trennung nimmt
der Musik dort Energie, wo die Original-Stimme sprach; unter der deutschen Sprechspur kann
das als Pumpen/Wabern hörbar werden. `~/.venvs/sa/bin/python3 <projektstamm>/tools/sp/bett_qualitaet.py`
misst die Loch-Tiefe im Sprachband und schreibt `_work/bett_qualitaet.json` — die Zahl gehört
in den Lauf-Bericht. Das Extrakt bleibt trotzdem das Standard-Bett: Ein Extrakt mit 7 dB Loch
wurde am Gate als gut befunden, weil der Marken-Regler (−4 dB) die Löcher unter die Sprechspur
legt. Ein Nachbau (Stil messen mit `tools/sa/quell_rhythmus.py bett "<Pipeline-Ordner>"`,
Suno-V5-Instrumental über kie.ai nach Skill `background-music-suno`, trimmen, mit `bett_pegel.py
--bett` einpegeln, A/B unter der Sprechspur) läuft nur, wenn Viktor am Gate „nicht clean“ sagt —
nie von selbst. Bessere Trennmodelle ändern das Loch nur um Zehntel-dB; das Gemini-Ohr taugt
für Trenn-Artefakte nicht (Kontroll-Snippet: unberührtes Suno-Instrumental bekam dasselbe
„leicht phasig“) — Urteile über Artefakte kommen aus Messung und Viktors Ohr.

**Genau hinhören, bevor „keine Musik" behauptet wird:** Ein mean-dB-Wert aus einem
3-Sekunden-Fenster taugt nicht — Ads wechseln zwischen Effekt-Passagen (Hook: nur
Whooshs) und Musik-Passagen. Prüfung: Rest-Stem in drei 8-s-Schnipseln (Anfang,
Mitte, Ende) ans Gemini-Ohr (kie.ai gemini-2.5-flash, `input_audio`): „Musik
vorhanden? Instrumente, Tempo, Effekte, Rest-Stimme?" Sagt das Ohr an ALLEN drei
Stellen „keine Musik", darf ein eigenes Instrumental hinzukommen (Suno V5, kie.ai,
Skill `background-music-suno`, Pegel wie oben gemessen) — sonst nie.

## Ablauf

CWD = Pipeline-Ordner (`brands/<Brand>/<NNN> EL/` — Läufe vor dem 02.09.2026: `<NNN> SP`).

1. **Tonspur ziehen:**
   `ffmpeg -y -v error -i _work/source.mp4 -vn -ar 44100 _work/original_ton.wav`
2. **Trennen (lokal, kein Dienst):**
   `~/.venvs/sa/bin/python3 -m demucs --two-stems=vocals -n htdemucs_ft --shifts 2 --overlap 0.5 -o _work/demucs_out _work/original_ton.wav`
   → `_work/demucs_out/htdemucs_ft/original_ton/no_vocals.wav` ist das Bett (das feinjustierte
   Modell lässt weniger Phasen-Reste in den Höhen; rechnet etwa viermal so lang wie htdemucs —
   auf dem Cloud-Worker rund eine Minute).
   Bricht Demucs ab (ImportError): Paket im venv `~/.venvs/sa` nachinstallieren.
3. **Als Bett ablegen:** `cp .../no_vocals.wav _work/musikbett.wav` — Musik und Effekte
   des Originals zusammen. Dann `bett_qualitaet.py` — die Loch-Zahl in den Lauf-Bericht.
   Nur wenn das Gemini-Ohr an allen drei Stellen keine Musik hört: Suno-Instrumental
   (Skill `background-music-suno`) dazumischen, Pegel gemessen.
4. **Rest-Stimme gegenhören (Pflicht):** An 2–3 Stellen, an denen das Original
   spricht, einen Schnipsel des Betts anhören (bildboard-Link) bzw. messen:
   bleibt dort hörbar Original-Sprache stehen, taugt das Bett nicht —
   dann Bett leiser fahren (weiter unter die Sprechspur) oder auf Bett
   verzichten und das im Chat sagen. Ein Bett mit durchscheinender
   US-Stimme ist schlimmer als gar keins.
5. **Pegel:** `~/.venvs/sa/bin/python3 <projektstamm>/tools/sp/bett_pegel.py --kuerzel <Kürzel> --leiter`
   → druckt `--bett-db`, schreibt `_work/musik_wahl.json` (alle Messwerte, Offset, bett_db)
   und die drei Leiter-Proben. Genau diesen bett_db in `tools/sp/render.py --bett-db` geben —
   kein Wert aus dem Gedächtnis, kein Wert aus einem früheren Lauf. Exit 2 = Kürzel fehlt
   im Brand-Adressbuch → Zeile mit Viktor anlegen, nicht mit 0 raten.

## Ausgabe

`_work/musikbett.wav` — Eingabe für `tools/sp/render.py`.
