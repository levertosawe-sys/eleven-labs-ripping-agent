---
name: sp-projekte
typ: Datei-Sammlung (Projekt-Ordner)
zweck: Ein Ordner je Projekt der SPEAKING-Kette (Eleven Labs Ripping Agent) — brand-übergreifend, bewusst getrennt von den Projekte-DBs der Singing-Linien. Naming „KÜRZEL NNN EL | DATUM" mit Identitäts-Karte (Quell-Hash = Doppel-Rip-Schutz) und den Vorstufen-Dateien der Copy-Kette; die schweren Artefakte liegen im Pipeline-Ordner brands/<Brand>/<NNN> EL (Alt-Bestand: <NNN> SP).
schreibt: singing-vsl-transkription (Projekt + Karte + Original) · singing-vsl-augen-check · speaking-vsl-emotionskarte (Emotions-Beleg) · speaking-vsl-uebersetzung · singing-vsl-dach-lokalisierung · tools/sp/new_sp_project.py (trägt Pipeline-Ordner nach) · ad-upload
liest: Doppel-Rip-Schutz jeder Anlage · Viktor (Übersicht)
format: je Projekt ein Ordner "KÜRZEL NNN EL | TT.MM.JJJJ/" mit karte.md + quelle-<meta-ad-id>.md + "<slug>-original|-uebersetzung|-befund|-final-<JJJJ-MM-TT>.md" + "<slug>-transkript-roh-<JJJJ-MM-TT>.json"
---
# Projekte — Speaking-Kette

## Naming (Viktors Konvention, geändert 02.09.2026)
Projekte heißen **„KÜRZEL NNN EL | DATUM"** (z. B. `ARE 001 EL | 02.09.2026`).
- **KÜRZEL** = Ziel-Brand-Kürzel aus dem Brand-Adressbuch `datenbanken/sp-brands`.
- **EL** = das Ketten-Kürzel dieses Agenten (Eleven Labs). Es steht IMMER zwischen
  Nummer und Trenner und ist Pflicht — daran erkennen Sheet, Export-Zuordnung und
  Bootstrap die Sprech-Kette.
- **NNN** = dreistellig, **eigene Serie je Kürzel**: gezählt wird NUR unter den
  EL-Projekten. `ARE 001` (Suno-Kette) und `ARE 001 EL` existieren nebeneinander und
  sind kein Konflikt — die Ketten nehmen sich keine Nummern mehr weg (Viktors Ansage
  02.09.2026, ersetzt die frühere geteilte Serie). Frei sein muss `KÜRZEL NNN EL`
  in DIESER Datenbank und der Ordner `NNN EL` unter `brands/<Kürzel - Name>/`.
- **DATUM** = Tag der Projekt-Anlage, `TT.MM.JJJJ`.
- **Alt-Bestand:** Läufe vor dem 02.09.2026 heißen `KÜRZEL NNN | DATUM` ohne EL und
  liegen in `NNN SP` (ROV 006, ROV 007). Sie behalten ihren Namen; alle Werkzeuge
  erkennen beide Formen.
Den Namen vergibt das **Ripping Sheet** beim ⚡-Klick (seit 02.09.2026, Agent
„🎙 Eleven Labs" im Rip-Dialog — es zählt nur die EL-Projekte); der
Auftrag nennt ihn, er wird NICHT neu gewürfelt. Hand-Weg bleibt: wirft Viktor das
Video in UPLOAD/Chat, vergibt die KI die nächste freie Nummer; ruft Viktor einen
Namen zu, gilt seiner. Die Datei `quelle-<meta-ad-id>.md` ist Pflicht — daran
erkennt das Sheet den laufenden Auftrag und räumt ihn aus der Auftragsleiste. Datei-Slugs: 2–4 kleine Wörter mit
Bindestrichen, einmal gebildet, über die ganze Kette konstant.

## karte.md — das Identitäts-Format
Wie in den Singing-Projekt-DBs: Frontmatter mit `projekt`, `brand`,
`quelle-video-sha256`, `quelle-kennzeile`, `meta-ad-id` (falls bekannt),
`pipeline-ordner` (`brands/<Brand>/<NNN> EL`, Alt-Bestand `<NNN> SP`), `angelegt` + 1–2 Sätze Body.

## Doppel-Rip-Schutz (zwei Prüfpunkte)
1. **Vor der Anlage:** `sha256sum <video>` → `grep -rl "<hash>" datenbanken/*projekte*`
   im Longform-Projekt UND in dessen Singing-DBs — jeder Treffer = STOPP, Viktor
   fragen (Speaking-Rip einer schon gesungenen Quelle ist ein bewusster Entscheid,
   kein Versehen).
2. **Nach der Transkription:** 3–4 markante Wörter der ersten Sätze gegen die
   `quelle-kennzeile:`-Zeilen aller Karten greppen — fängt Re-Encodings.
Zweitlauf nur nach Viktors Ja, mit Zweitlauf-Vermerk in beiden Karten.
