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
                  ├─ Custom Clips — jedes englische Wort im Bild wird deutsch
                  └─ Emotions-Karte → Übersetzung in Sprech-Budgets
                      └─ DACH-Lokalisierung → Gate
                          └─ Stimme → Sprechspur → Audio-Prüfung
                              └─ Lip-Sync (nur Menschen, die sichtbar sprechen)
                                  └─ Schnitt → Abnahme → Faktencheck → Untertitel → CapCut
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
- **Nach dem Lip-Sync bleibt die Sprechspur bitgleich.** Die Mundbewegung folgt dem Ton, der
  beim Auftrag geschnitten wurde — schon 0,2 s Verschiebung sind 6 Frames Versatz. Erst Copy
  und Montage fertig prüfen, dann lippen. kie liefert immer 25 fps; umgerechnet wird ohne Neukauf.
- **Die ganze Ad ist deutsch — auch das Bild.** Jedes englische Wort im Bild (3D-Titel, Schilder,
  Etiketten, Endcard) wird ersetzt: per Custom Clip mit Start- und End-Frame oder, wenn auf einem
  Etikett nur ein Wort wechselt, deterministisch für 0 Credits (`tools/sp/etikett_wort.py`).
  Abgenommen wird am fertigen Render per OCR, nicht an der Clip-Liste.
- **Vmake frisst je nach Quelle auch Bildinhalt** (gemusterte Kleidung, Einklinker, Endcards).
  Erst die Änderungsfläche außerhalb des Caption-Bands messen, dann entscheiden, ob das Original
  die Bildbasis wird.
- **Untertitel bleiben in CapCut bearbeitbar** — als echte Untertitel-Spur, ein Stil für alle,
  die Standzeit je Einblendung (1,5–3 s) gemessen statt geschätzt (`tools/sp/untertitel_*.py`).

Die Herleitung jeder Regel steht in [`feedback_log.md`](feedback_log.md).

## Stand: ehrlich

**Stand 28.09.2026: 26 von 27 Bausteinen liegen bei** — die Kette läuft von der fremden
MP4 bis zum CapCut-Projekt durch: Transkript, Augen-Check, Caption-Entfernung, Clip-Karte,
Emotions-Karte, Übersetzung, Lokalisierung, Sprechspur mit Prüfer-Loop, Musikbett,
**Lip-Sync**, **Custom Clips**, Schnitt + Render, Abnahme, Faktencheck, Untertitel,
CapCut-Export, dazu die Datenbank-Verträge. Es fehlt nur das Ripping-Sheet (Software des
Betreibers, nicht Teil des Pakets). Das Upload-Werkzeug liegt als Beschreibung bei
(`tools/ad-upload/README.md`), sein Code läuft beim Betreiber — ohne ihn endet die Kette
mit dem fertigen CapCut-Projekt.

### Neu seit dem 17.09.2026

- **Custom Clips für englischen Szenen-Text** (Kling mit Start- und End-Frame) —
  `custom-clip-production` §10/§11 und `references/szenen-text.md`. Die Abnahme prüft per
  OCR am fertigen Render, dass kein englisches Wort im Bild bleibt (`tools/sp/ocr_vision.swift`).
- **Deutscher Bildtext ohne Credits:** `tools/sp/etikett_wort.py` tauscht ein Wort auf einem
  Etikett, `tools/sp/bildbasis_platte.py` baut die Bildbasis für Quellen mit deckender
  Caption-Platte.
- **Untertitel:** `untertitel_regel.py` prüft die Standzeit und schneidet nach;
  `untertitel_spur.py`, `untertitel_editierbar.py` und `untertitel_stil_auf_alle.py` machen
  daraus eine echte, bearbeitbare Untertitel-Spur in CapCut mit einem Stil für alle.
- **Robuster:** Das Gemini-Ohr hat eine dritte Route, Timeouts brechen Emotions-Karte und
  Prüfer nicht mehr ab, und fällt das Ohr ganz aus, misst `emotions_messen.py` die Delivery
  am Original. Dazu ein Scribe-Cache je Take, ein Fix an der Montage-Naht, und der
  Marken-Planer verteilt übrige Luft wie im Original.
- **Jetzt mit im Paket:** der CapCut-Skill `sa-captions-capcut` (Export + Stil-Vorlage) und
  `tools/sa/kie_bild.py` (Nano Banana 2 + Kling über kie.ai). Die Kette ruft beide direkt auf.
- **Learnings** aus den Läufen seit dem 17.09. und der Feedback-Log bis 27.09.2026.

Neu entstehen Bausteine weiter nach der Use-and-Break-Methode: benutzen, am echten
Projekt brechen, das Gelernte in den Baustein zurückschreiben
([`feedback_log.md`](feedback_log.md), [`datenbanken/sp-learnings/learnings.md`](datenbanken/sp-learnings/learnings.md)).

## Voraussetzungen

Siehe [`01-VORAUSSETZUNGEN.md`](01-VORAUSSETZUNGEN.md). Kurz: ein KI-Agent mit Datei-
und Terminal-Zugriff, `ffmpeg`, Python 3.9+, CapCut, für die OCR-Abnahme ein Mac
(Apple Vision), und eigene Konten bei ElevenLabs, kie.ai und Vmake.

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
