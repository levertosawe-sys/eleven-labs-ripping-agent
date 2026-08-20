# Eleven Labs Ripping Agent

Aus einer fremden, englischen Video-Sales-Letter wird eine eigene, deutsch
**gesprochene** Ad: gleiche Bilddramaturgie, neue Stimme, neue Copy, eigenes
Produkt-Branding.

Das hier ist **kein Programm, sondern ein Arbeitsablauf für eine KI** — eine
Workflow-Datei plus die Skills, die ihre Knoten ausführen. Gebaut für
[AWMS](https://github.com/zeveryofficial-cloud/Afrikaner-wollen-mein-Software),
läuft aber in jedem Agenten mit Datei- und Terminal-Zugriff.

## Die Kette

```
Competitor-VSL (MP4)
  └─ Transkription (ElevenLabs Scribe, wortgenaue Zeitstempel)
      └─ Augen-Check gegen die eingebrannten Original-Captions
          └─ Captions entfernen (Vmake)
              └─ Clip-Karte — jede Szene mit eigenen Augen beschrieben
                  └─ Übersetzung in Sprech-Budgets
                      └─ DACH-Lokalisierung → Gate
                          └─ Stimm-Casting → Sprechspur → Schnitt → CapCut
```

## Was hier drinsteckt und anderswo nicht

Der Wert liegt weniger im Ablauf als in den **gemessenen Regeln**, die aus echten
Läufen zurückgeschrieben wurden:

- **Stimm-Casting wird gemessen, nicht geraten.** Tonhöhen-Variation von 25–35 %
  ist das Band eines natürlichen deutschen Werbe-Reads. Darunter klingt es
  maschinell — und genau dort liegen die „DE-verifizierten" amerikanischen
  Standardstimmen. Gecastet wird aus der öffentlichen Bibliothek.
- **Eine Copy ist EIN Sprechakt.** Blockweise erzeugte TTS hört mitten im Gedanken
  auf, weil das Modell in jeden Block eine Schlussmelodie legt. Ein durchgehender
  Take, danach an den gemessenen Sprechpausen geschnitten.
- **Untertitel werden nie eingebrannt.** Die Kette liefert Bild + Sprechspur.
- **Gestaltungs-Text wird ersetzt, nicht entfernt.** Ein Hero-Titel trägt den Hook;
  wegretuschiert beginnt die Ad mit einem stummen Bild. Gefüllte Farbflächen
  hinterlassen beim Inpainting ohnehin immer Rückstand — er wird abgedeckt.
- **Ein Ton-Mux ist kein Grund, das Bild neu zu encodieren.**

Die Herleitung jeder Regel steht in [`feedback_log.md`](feedback_log.md).

## Stand: ehrlich

**16 von 26 Bausteinen sind gebaut.** Die Vorstufe läuft vollständig durch —
Transkript, Augen-Check, Caption-Entfernung, Clip-Karte, Übersetzung,
Lokalisierung, Stimm-Casting, Sprechspur. Die zehn Geister sind in der
Workflow-Datei präzise beschrieben, aber noch nicht gebaut: Projekt-Bootstrap,
Schnitt + Render, Abnahme, Musikbett, Meta-Upload und die zugehörigen Datenbanken.

Sie entstehen nach der Use-and-Break-Methode: benutzen, am echten Projekt brechen,
das Gelernte in den Baustein zurückschreiben. Wer dieses Paket bekommt, bekommt den
Bauplan plus zwei Drittel der Fabrik — nicht die ganze.

## Voraussetzungen

Siehe [`01-VORAUSSETZUNGEN.md`](01-VORAUSSETZUNGEN.md). Kurz: ein KI-Agent mit Datei-
und Terminal-Zugriff, `ffmpeg`, Python 3.9+, und eigene Konten bei ElevenLabs,
kie.ai und Vmake.

**Dieses Repository enthält keine Schlüssel.** Sie gehören in eine `.env` außerhalb
jedes Repos.

## Einstieg

| Datei | Wofür |
|---|---|
| [`00-START-FUER-KI.md`](00-START-FUER-KI.md) | Der Einstieg für die KI |
| [`LIESMICH.md`](LIESMICH.md) | Was der Workflow leistet, für Menschen |
| [`02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md`](02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md) | Jeder Knoten im Detail |
| [`03-FALLEN-UND-TRICKS.md`](03-FALLEN-UND-TRICKS.md) | Was in echten Läufen schiefging |
| [`workflows/eleven-labs-ripping-agent.json`](workflows/eleven-labs-ripping-agent.json) | Die Kette als Datei |
