---
name: sprech-watch
description: "Erzeugt die deutsche Sprechspur einer Speaking-VSL und prüft sie gegen die Zeitfenster — ein durchgehender Take statt isolierter Blöcke, danach an den Sprechpausen geschnitten. Nutzen nach der Lokalisierung, wenn „Sprechspur", „Voiceover", „TTS", „Stimme bauen" fällt."
---

# sprech-watch — die Sprechspur und ihr Prüfer-Loop

## Das Grundgesetz: EIN Take, danach schneiden

**Die ganze Copy wird in EINEM Stück erzeugt — nie Block für Block.**

Warum: Ein TTS-Modell hört nur den Text, den es bekommt. Erzeugt man Block 3 isoliert,
weiß es nichts von Block 2 und 4 — es setzt an, schließt ab, und legt in jeden Block
eine Anfangs- und Schlussmelodie. Das Ergebnis klingt abgehackt: **die Stimme hört
mitten im Gedanken auf, obwohl dort kein Punkt steht.** Genau daran erkennt ein
Muttersprachler sofort die Maschine.

Der Ablauf:
1. **Ein Take** der vollständigen Copy erzeugen. Der Sprechfluss läuft durch, die
   Betonung trägt über Satzgrenzen hinweg.
2. **Sprechpausen messen**, nicht schätzen:
   `ffmpeg -i ganz.mp3 -af silencedetect=noise=-32dB:d=0.18 -f null -`
3. **An den Blockgrenzen schneiden** — die gemessene Pause, die dem erwarteten
   Zeichenanteil am nächsten liegt (Zeichen des Blocks ÷ Zeichen gesamt × Gesamtdauer).
4. **Auf die Zeitmarken legen** (`adelay`). Innerhalb eines Blocks wird der Ton NIE
   angefasst — nur die Stille dazwischen wird gedehnt oder gekürzt.

**Gemessen im QUA-001-Lauf:** Blockweise Erzeugung ergab Viktors Befund „klingt
roboterhaft, hört mitten im Satz auf, man merkt sofort das ist eine KI-Stimme". Der
durchgehende Take derselben Copy mit derselben Stimme klang zusammenhängend.

## Modell zuerst nachsehen, nie annehmen

Vor dem ersten Take die Modell-Liste des Kontos abfragen:
`GET https://api.elevenlabs.io/v1/models` (Header `xi-api-key`) und das neueste
deutschfähige nehmen. Im QUA-001-Lauf lief zuerst `eleven_multilingual_v2`, obwohl
`eleven_v3` im Konto lag — eine ganze Modellgeneration verschenkt, aus reiner Annahme.

Achtung: `eleven_v3` unterstützt `previous_text`/`next_text` **nicht** (HTTP 400,
`unsupported_model`). Das ist kein Problem, weil der EIN-Take-Weg den Kontext
ohnehin von selbst mitbringt — er ist dem Kontextfeld sogar überlegen.

## Der Prüfer-Loop: jeder Block gegen sein Fenster

Je Block Dauer messen und gegen sein Zeitfenster halten. Toleranz 0,25 s.

| Überlänge | Mittel |
|---|---|
| bis ~10 % | `atempo` bis 1,10 — hört niemand |
| 10–15 % | `atempo` bis 1,15, aber nur bei ruhigen Blöcken |
| über 15 % | **Copy kürzen und neu erzeugen** — Tempo darüber klingt gehetzt |

Nie die Sprechgeschwindigkeit als Erstes anheben. Erst kürzen, dann Tempo.

## Abschluss-Prüfung

- Jeder Block startet exakt auf seiner Zeitmarke (durch `adelay` garantiert, nicht
  nachträglich zu messen).
- Gesamtpegel `loudnorm=I=-16:TP=-1.5` — Social-Plattformen normalisieren sonst selbst.
- Keine Überlappung: Blockende + Startmarke des nächsten prüfen.
