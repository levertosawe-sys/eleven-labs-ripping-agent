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
                          └─ Stimme → Sprechspur → Audio-Prüfung
                              └─ Lip-Sync (nur Menschen, die sichtbar sprechen)
                                  └─ Schnitt → Abnahme → Faktencheck → CapCut
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
- **Lip-Sync nur für Menschen — und nur, was gemessen sauber ist.** Farbblitze und Blenden
  fliegen aus den Aufträgen (sonst hautfarbene Flecken im Gesicht), die kie-Ausgabe bekommt
  ihre Farbkennzeichnung zurück (sonst verschobene Hauttöne), Tiere und Cartoon-Figuren
  werden nie gelippt. Details: [`03-FALLEN-UND-TRICKS.md`](03-FALLEN-UND-TRICKS.md#lip-sync).

Die Herleitung jeder Regel steht in [`feedback_log.md`](feedback_log.md).

## Stand: ehrlich

**24 von 27 Bausteinen sind gebaut** — die Kette läuft von der fremden MP4 bis zum
CapCut-Projekt durch: Transkript, Augen-Check, Caption-Entfernung, Clip-Karte,
Emotions-Karte, Übersetzung, Lokalisierung, Sprechspur mit Prüfer-Loop, Musikbett,
**Lip-Sync**, Schnitt + Render, Abnahme, Faktencheck, Captions, Custom Clips,
dazu die Datenbank-Verträge. Drei Geister bleiben: das Ripping-Sheet (Software des
Betreibers, nicht Teil des Pakets), das Upload-Werkzeug und die Meta-Werbekonto-Datenbank.

Neu entstehen Bausteine weiter nach der Use-and-Break-Methode: benutzen, am echten
Projekt brechen, das Gelernte in den Baustein zurückschreiben
([`feedback_log.md`](feedback_log.md), [`datenbanken/sp-learnings/learnings.md`](datenbanken/sp-learnings/learnings.md)).

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
| [`datenbanken/stimmen/steckbrief-ran-dr-randy.md`](datenbanken/stimmen/steckbrief-ran-dr-randy.md) | Die Stimmen eines gelaufenen Falls, mit Voice-IDs und Einstellungen |
