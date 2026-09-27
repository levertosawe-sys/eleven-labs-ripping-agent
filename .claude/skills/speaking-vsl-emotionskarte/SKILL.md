---
name: speaking-vsl-emotionskarte
description: "Die Delivery der Original-Stimme einer Speaking-VSL je Copy-Zeile reverse-engineeren (Emotion, Ton, Tempo, betonte Wörter, Pausen) und daraus ElevenLabs-v3-Audio-Tags für die deutschen Zeilen bauen — Schritt der Speaking-Kette zwischen Clip-Karte und Übersetzung. Nutzen, wenn „Emotionen", „Emotions-Karte", „wie spricht das Original", „die Stimme klingt langweilig/emotionslos" fällt."
---

# Emotions-Karte — die Delivery wird gemessen, nie erfunden

ElevenLabs v3 ohne Emotions-Vorgabe hat zwei Ausfallarten: Es wiederholt eine
Emotion über die ganze Spur, oder es würfelt unpassende. Beides klingt sofort
nach Maschine. Der Ausweg ist Reverse-Engineering: Das Original hat jede Zeile
schon einmal richtig gesprochen — diese Delivery wird gemessen und auf die
deutsche Fassung übertragen. Die KI erfindet keine Emotionen, sie überträgt
belegte.

## Eingabe

Alle Pfade vom Pipeline-Ordner des Projekts aus (`brands/<Brand>/<NNN> EL/` — Läufe vor dem 02.09.2026 heißen `<NNN> SP`).

- `_work/source_original.mp4` (oder `source.mp4`) — die Tonspur des Originals.
- Die Copy-Zeilen mit Zeitfenstern: aus dem EN-Transkript des Projekts die
  Blöcke als `_pipeline/emo_bloecke.json` schreiben:
  `[{"t0": 0.08, "t1": 8.48, "en": "Your kidneys never ..."}, ...]`
  (t0 = Start des ersten Worts, t1 = Start des Folgeblocks; Quelle ist das
  Scribe-Roh-JSON). Eine Zeile je SATZ, nicht je Sprech-Block: Satzgrenzen sind
  die Wörter mit Satzzeichen im Roh-JSON. Ein Block fasst mehrere Sätze mit
  verschiedener Delivery zusammen — gemessen auf Block-Ebene wird daraus ein
  Mittelwert, und ein Mittelwert klingt monoton.

## Ablauf

1. **Messen:** `~/.venvs/sa/bin/python3 <projektstamm>/tools/sp/emotions_karte.py
   --bloecke _pipeline/emo_bloecke.json` — je Zeile hört das Gemini-Ohr
   (Route: **gemini-2.5-pro über den Kanal `image_url`** als Daten-URI — NICHT
   `input_audio` und NICHT flash als erste Wahl; über `input_audio` bekommt das
   Modell gar kein Audio durchgereicht und erfindet die Antwort, gemessen RYZ 002 EL
   16.09.2026. Das Werkzeug `tools/sp/emotions_karte.py` probiert die Routen bereits
   in dieser Reihenfolge; Anker-Regel: nur Anker-bestandene Modelle dürfen urteilen) den Original-Schnipsel ab und liefert STRICT JSON:
   Emotion, Ton, Tempo, betonte Wörter, Pausen, v3-Tag-Vorschlag aus der
   festen Tag-Liste des Scripts. Exit 1 = mindestens eine Zeile ohne gültiges
   Urteil → diese Zeilen einzeln nachfahren; bleibt es leer, die Zeile ohne
   Tags weitergeben und das im Chat sagen (nie selbst raten).
2. **Plausibilität mit eigenen Augen:** Die Karte gegen die Clip-Karte halten —
   ein „excited" auf einem Angst-Bild (kaputte Niere) ist ein Widerspruch:
   dann gewinnt das, was Bild UND Text stützen, und die Abweichung wird in der
   Karte als `korrektur` notiert.
3. **Auf Deutsch übertragen:** Nach der Übersetzung die Tags den DEUTSCHEN
   Zeilen zuordnen (gleiche Block-Nummer) und betonte Wörter auf ihre
   deutschen Entsprechungen mappen. Ergebnis in
   `_pipeline/emotions_karte.json` ergänzen (Feld `de` + `de_betonung`).
4. **Tags setzen — gezielt, nicht sparsam bis zur Leblosigkeit.** Zwei Fehlbilder,
   beide aus echten Gates: zu viele Tags (ein Label macht die Passage „fett emotional")
   UND zu wenige — eine Spur mit einem einzigen Tag hört Viktor als „monoton, bin fast
   eingeschlafen". Das Ohr misst das Original meist als „professionell-informativ";
   daraus folgt NICHT „kein Tag", sondern: Die Delivery einer Werbe-Stimme lebt von
   Wendepunkten. Regel: ein Tag an jedem Wendepunkt der Copy — Hook (curious),
   Problem-Aufriss (curious/dramatic), Mechanik-Lösung (warm/confident), Beweis
   (excited/confident), Autoritäts-Anker (warm), CTA (urgent). Bemessungsgrundlage
   ist der SATZ: jeder Satz, den die Karte als Wendepunkt misst (Emotion oder Tempo
   wechselt gegenüber dem Vorsatz, oder emotionsstaerke = stark), bekommt seinen
   eigenen Tag — auch wenn der Nachbarsatz im selben Block schon einen trägt; reine
   Erklär-Sätze bleiben ohne. Prüfmaß vor dem Take-Text: kein Abschnitt über 8 s
   Sprechzeit ohne Tag-Wechsel — sonst hört der Mensch eine Ebene, egal wie gut
   jeder Satz für sich klingt. Ein Tag wirkt auf das, was NACH ihm kommt, auch mitten
   im Block. Dazu die Stimm-Einstellung: v3 `stability` 0,25 (lebendig) statt 0,5 —
   0,5 klingt sauber, aber flach; 0,3 ist noch als monoton hörbar. Betonung einzelner Wörter über
   GROSSSCHREIBUNG bleibt sparsam (höchstens 2 Wörter je Copy, Caps kosten Sprechzeit).

## Ausgabe

`_pipeline/emotions_karte.json` — je Zeile: `t0, t1, en, emotion, ton, tempo,
betonte_woerter, pausen, v3_tags, note` (+ nach Schritt 3: `de, de_betonung`,
ggf. `korrektur`). Die FINALE Copy im Projekt-Ordner bleibt tag-frei — Viktors
Gate liest saubere Copy; die Tags konsumiert ausschließlich der Take-Text des
Sprechspur-Baus.

## Fallen

- **Tags gehören in den Take-Text, nie in die final-Datei** — sonst liest die
  Lokalisierung Tags als Copy und der Längen-Check zählt sie als Wörter.
- **Ein Tag wirkt auf das, was NACH ihm kommt.** Tag ans Zeilenende ist wirkungslos.
- **Karaoke-Wortfarben des Originals sind KEIN Emotions-Signal** — die Farben
  wechseln mechanisch je Wort. Nur das Ohr zählt.

## Wenn das Ohr ausfällt (Ersatzweg, belegt VIS 004 EL 18.09.2026)

Erst messen, ob es wirklich tot ist — in DREI Stufen, nicht einer (ergänzt VIS 004 EL
19.09.2026, weil die einstufige Prüfung die Ursache nicht trennt):
1. **Nur-Text-Aufruf** an dieselbe Route („Answer with exactly: OK"). Kommt eine Antwort,
   läuft der Anbieter und nur der AUDIO-Kanal ist kaputt → Kanal wechseln (image_url).
   Kommt 500, ist der Dienst unten und kein Kanalwechsel hilft.
2. **Transkriptions-Test** mit eigenem Schnipsel und BEKANNTEM Wortlaut, Ankerwörter zählen.
   Antwortet das Modell, ohne die Ankerwörter zu treffen, bekommt es kein Audio — es
   erfindet. Das ist schlimmer als ein Fehler, weil es wie ein Urteil aussieht.
3. **Modell-Liste durchgehen.** 422 „model is not supported" heißt: das Modell gibt es auf
   diesem Konto gar nicht — das ist KEIN Ausfall und darf nicht als solcher gezählt werden.
Erst wenn Stufe 1 UND 2 bei allen unterstützten Modellen durchfallen, gilt das Ohr als tot —
mit Datum, Modellnamen und wörtlicher Fehlermeldung im Protokoll.
Gemessen am 19.09.2026: gemini-2.5-pro 500 „server is currently being maintained",
gemini-2.5-flash 500 „Network error", gemini-3-flash 500 „internal error";
gemini-3-pro-preview, gemini-2.0-flash und gemini-2.5-flash-lite antworten 422 (nicht auf
dem Konto). Auch der Nur-Text-Aufruf fällt durch → Anbieter-Ausfall, kein Kanal-Problem.

Dann wird die Delivery LOKAL gemessen statt geraten (librosa, Original-Tonspur, je SATZ):
Silben/s · Pegel dB · F0-Median · F0-Spanne (p90−p10) · betonte Wörter über Wort-Energie ·
Pausen > 0,22 s. **Wendepunkt** = |ΔSilben/s| ≥ 0,45 ODER |ΔF0| ≥ 12 Hz ODER |ΔdB| ≥ 2,5
gegenüber dem Vorsatz. Jeder Wendepunkt bekommt seinen Tag, Erklär-Sätze bleiben ohne,
das 8-s-Prüfmaß gilt unverändert.

**Was der Ersatzweg NICHT kann:** Er misst Tempo, Pegel, Tonhöhe, Betonung und Pausen —
nicht die Emotion selbst. Die Zuordnung Messwert→Tag ist eine Ableitung aus Messung plus
Clip-Bild. Darum gehört je Zeile der Messbeleg in die Karte (Feld `beleg`), damit der
Mensch am Gate jede Zuordnung kippen kann, und das Feld `quelle` trägt
„lokale Messung (Ersatzweg)" statt einer Modell-Route.
