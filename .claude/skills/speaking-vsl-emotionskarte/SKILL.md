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
   (gemini-2.5-flash via kie.ai; Anker-Regel: nur Anker-bestandene Modelle
   dürfen urteilen) den Original-Schnipsel ab und liefert STRICT JSON:
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
