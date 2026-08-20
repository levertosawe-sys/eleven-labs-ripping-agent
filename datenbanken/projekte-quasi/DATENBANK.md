---
name: projekte-quasi
typ: Datei-Sammlung (Projekt-Ordner)
zweck: Ein Ordner je Singing-VSL-Projekt der QUASI-LINIE (Ziel-Brand QUA - Quasi; Lymphoria-Projekte wohnen in projekte-lymphoria) — Viktors Naming-Konvention „KÜRZEL NNN | DATUM" (z. B. „LYM 001 | 25.07.2026") — mit Identitäts-Karte (Quell-Hash = Doppel-Rip-Schutz) und den Vorstufen-Dateien der Copy-Kette (Transkript, Übersetzung, Lokalisierungs-Befund, finale Copy). Die schweren Pipeline-Artefakte (Song, Schnitt, Render) bleiben im Pipeline-Ordner unter brands/ — die Karte verlinkt ihn.
schreibt: singing-vsl-transkription (legt Projekt + Karte + Original an) · singing-vsl-uebersetzung · singing-vsl-dach-lokalisierung (Vorstufen-Dateien) · der Workflow-Lauf beim Bootstrap (trägt den Pipeline-Ordner in die Karte nach)
liest: singing-vsl-transkription (Dedup-Check vor jeder Projekt-Anlage) · Viktor (Übersicht, welche Quelle schon verarbeitet ist)
format: je Projekt ein Ordner "KÜRZEL NNN | TT.MM.JJJJ/" (Naming s.u.; Alt-Bestand "Singing VSL NNN/" bleibt liegen) mit karte.md (Frontmatter, s.u.) + den Vorstufen-Dateien "<slug>-original|-uebersetzung|-befund|-final-<JJJJ-MM-TT>.md" + dem Transkriptions-Beleg "<slug>-transkript-roh-<JJJJ-MM-TT>.json"
---
# Projekte — Singing VSL

## Naming (Viktors Konvention)
Projekte heißen **„KÜRZEL NNN | DATUM"** — z. B. `LYM 001 | 25.07.2026`.
- **KÜRZEL** = Brand-Kürzel (LYM = Lymphoria, QUA = Quasi, LEI = Leichtkraut;
  Quelle: Feld `kuerzel` in der brand.json des Ripping Sheets bzw. der
  `brands/`-Ordnername nach dem Muster `KÜRZEL - Name`).
- **NNN** = dreistellig, zählt **pro Kürzel** ab 001 — LYM und QUA haben je
  ihre eigene Zählung. Die Projekt-Nummer ist zugleich die Nummer des
  Pipeline-Ordners (`brands/KÜRZEL - Name/NNN SA`).
- **DATUM** = Tag der Projekt-Anlage, `TT.MM.JJJJ`.

Der Name kommt im Normalfall FERTIG aus dem Ripping-Sheet-Auftrag (erste
Zeile „Projekt: …") — dann gilt er exakt. Ohne Auftrag: höchste vorhandene
Nummer des Kürzels + 1, Namen beim Anlegen im Chat nennen; ruft Viktor einen
anderen Namen zu, gilt seiner. Ordner mit anderen Namensmustern (etwa
„Singing VSL NNN") sind Alt-Bestand: liegen lassen, nie umbenennen, und ihre
Nummern zählen für kein Kürzel mit.

Datei-Slugs bleiben klein-mit-bindestrichen: `<slug>` = 2–4 Wörter
aus Marke/Thema (Quelle: Video-Dateiname oder Viktors Zuruf), wird bei der
Projekt-Anlage einmal gebildet und bleibt über die ganze Kette konstant.

## karte.md — das Identitäts-Format
```markdown
---
projekt: QUA 001 | 26.07.2026
brand: QUA - Quasi
quelle-video-sha256: dbc4a3ffc855e0b42f3f13fdb3239c22f0016be4a5973b98573b24d6803ac915
quelle-kennzeile: "My ex-husband stood behind me in the checkout queue last week"
pipeline-ordner: brands/QUA - Quasi/001 SA
angelegt: 2026-07-26
---
Ein bis zwei Sätze, was das Projekt ist; Besonderheiten offen benennen.
```
`quelle-video-sha256` = `shasum -a 256 <quellvideo>`; `quelle-kennzeile` = die
ersten ~10 Wörter des EN-Transkripts (zweites Netz, falls dieselbe Ad als
anderes Encoding kommt und der Hash deshalb abweicht). `pipeline-ordner` trägt
der Workflow-Lauf nach dem Bootstrap nach — bis dahin steht dort `— (noch kein Lauf)`.

## Doppel-Rip-Schutz (Betriebsregel — zwei Prüfpunkte)
**Vor der Projekt-Anlage:**
1. `shasum -a 256 <neues-quellvideo>` rechnen.
2. `grep -rl "<hash>" "datenbanken/projekte-quasi"` (**nur diese Datenbank**) — Treffer (einer oder mehrere) =
   dieselbe Datei schon verarbeitet → STOPP, Viktor mit allen Treffer-Projekten
   fragen („Diese Quelle ist schon QUA 002 — wirklich nochmal?"). Nur
   mit seinem ausdrücklichen Ja weitermachen.

   **Der Alt-Bestand `datenbanken/projekte` (Muster „Singing VSL NNN“) wird NICHT
   mitgeprüft** (Viktors Entscheid 02.08.2026, QUA-008-Lauf): stillgelegte
   Produktionslinie — sie zählt für keine Nummer, blockiert keine Quelle und wird
   im Chat nicht mehr erwähnt. Geprüft und gezählt wird ausschließlich die QUA-Linie.

**Nach der Transkription, vor dem Abliefern** (fängt Re-Encodings derselben Ad,
deren Hash abweicht): 3–4 markante Wörter aus den ersten Transkript-Sätzen
gegen die `quelle-kennzeile:`-Zeilen der Karten in `datenbanken/projekte-quasi` greppen (tolerant — einzelne
Wortfolge, nicht der ganze Satz; Transkripte desselben Ads sind nie
buchstabengleich). Treffer → STOPP wie oben; sagt Viktor „Abbruch", den gerade
angelegten Projekt-Ordner wieder löschen.

**Zweitlauf-Vermerk** (nur nach Viktors ausdrücklichem Ja): in den Body BEIDER
Karten je eine Zeile `Zweitlauf: gleiche Quelle wie <anderes Projekt> (bewusst, <JJJJ-MM-TT>).`
— beim neuen Projekt sofort bei der Anlage, bei den Treffer-Projekten nachgetragen.
