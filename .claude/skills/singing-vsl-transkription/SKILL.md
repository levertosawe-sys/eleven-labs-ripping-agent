---
name: singing-vsl-transkription
description: Ein Competitor-VSL-Video (MP4 im Chat) über ElevenLabs Scribe in ein englisches Transkript mit zeitachsen-treuen (M:SS)-Stempeln verwandeln — erster Schritt der Singing-VSL-Vorstufe, liefert die Vorlage für singing-vsl-uebersetzung. Nutzen, wenn Viktor ein US-Ad-Video reinwirft und die Singing-VSL-Kette starten will: „transkribier das", „Singing VSL", „Scribe", „mach das Transkript mit Zeitstempeln", „neues Projekt" plus Video. Nicht verwechseln mit ad-transkription im AWMS-Hauptprojekt (Competitor Ripping, ohne Zeitstempel).
---

**`<projekte-db>`** steht in diesem Skill für die Projekte-Datenbank der LINIE, die
dieser Lauf fährt. Aufgelöst wird sie über die Registry `datenbanken/linien/linien.json`
(Feld `projektDb` der Zeile, z. B. `datenbanken/projekte-rovina`); welche Linie gilt, sagt
der Rip-Auftrag, sonst Viktor am Trigger. Nie aus Gewohnheit die Quasi-Linie annehmen —
es entscheidet die Quell-Brand des Videos (Packshot, Marke im Bild, Page-Farm-Register
der Brand-DBs). `datenbanken/projekte` (ohne Zusatz) ist eingefrorener Alt-Bestand —
dort entsteht nie ein neues Projekt.

# Singing VSL Transkription

Das Transkript trägt das Timing des späteren Suno-Songs — die Stempel müssen
die echte Zeitachse treffen. Motor ist ElevenLabs Scribe: Es misst
Wort-Zeitstempel direkt an der Tonspur, darum kein Drift über lange Videos,
ein Call fürs ganze Video. Sprachmodelle (Gemini & Co.) sind hier tabu — sie
erzählen nach und stauchen die Zeitachse; Messwerte und der Engine-Vergleich
stehen in `DECISIONS.md`.

## Eingabe

- Die Video-Datei aus dem Chat (voller Pfad).
- **Doppel-Rip-Schutz zuerst** — die Prozedur steht in
  `<projekte-db>/DATENBANK.md` (Abschnitt „Doppel-Rip-Schutz",
  Prüfpunkt „vor der Projekt-Anlage"): Quell-Hash rechnen, gegen die Karten
  greppen; Treffer → STOPP und Viktor fragen.
- Der Projektname nach der Naming-Konvention **„KÜRZEL NNN | DATUM"** (z. B.
  `LYM 001 | 25.07.2026`; Details in `<projekte-db>/DATENBANK.md`,
  Abschnitt „Naming"). Vorrang: (1) Viktors Zuruf gilt immer · (2) sonst der
  Name aus dem Ripping-Sheet-Auftrag (erste Zeile „Projekt: …") EXAKT
  übernehmen · (3) sonst selbst vergeben: Brand-Kürzel bestimmen, nächste
  freie Nummer DIESES Kürzels nach `<projekte-db>/DATENBANK.md` §Naming
  bestimmen (frei sein muss sie in der Datenbank UND unter `brands/<Kürzel - Name>/`;
  Ordner anderer Muster zählen nicht mit), Datum von heute anhängen — und den
  Namen im Chat ansagen.
- Die Brand: der passende Ordnername aus `brands/` (erkennbar an Marke im
  Video/Dateinamen); ist sie nicht eindeutig, zusammen mit dem Projektnamen
  bei Viktor erfragen.
- Dann den Projekt-Ordner `<projekte-db>/<projekt>/` anlegen und die
  `karte.md` nach dem Format der DATENBANK.md schreiben — `quelle-kennzeile`
  bleibt zunächst leer (sie wird beim Abliefern nachgetragen),
  `pipeline-ordner` bleibt `— (noch kein Lauf)`.
- Platzhalter überall: `<projekt>` = der Projektname (z. B. `LYM 001 | 25.07.2026`),
  `<slug>` = 2–4 kleingeschriebene Wörter mit Bindestrichen aus Marke/Thema,
  Quelle: Video-Dateiname oder Viktors Zuruf (z. B. `quasi-vier-fehler`) —
  einmal gebildet, bleibt er über die ganze Kette konstant;
  `<JJJJ-MM-TT>` = heutiges Datum.
- Den Schlüssel liest das Script selbst aus `~/.config/leichtkraut/.env`
  (`ELEVENLABS_API_KEY`). Bricht es mit „…fehlt" ab: Viktor fragen und
  stoppen — nie auf einen anderen Key im System ausweichen. Nennt Viktor
  daraufhin einen Key: als `ELEVENLABS_API_KEY=…` in
  `~/.config/leichtkraut/.env` eintragen (fehlt die Datei, mit `chmod 600`
  anlegen), dann Schritt 1 erneut.

## Schritte

1. **Script ausführen** — vom Projektstamm aus (der Ordner, in dem `.claude/`
   und `datenbanken/` liegen):
   ```bash
   python3 .claude/skills/singing-vsl-transkription/scripts/transcribe.py \
     "<video>" --out "<projekte-db>/<projekt>/<slug>-transkript-roh-<JJJJ-MM-TT>.json" \
     --bloecke "<projekte-db>/<projekt>/<slug>-bloecke-roh-<JJJJ-MM-TT>.md"
   ```
   Ein Call fürs ganze Video, Laufzeit ~1 Minute. Erfolg = Exit 0, die
   `--out`-Datei existiert, Meldung „… Wörter". Abbruch mit „…fehlt" → siehe
   Eingabe; jeden anderen Abbruch (ffmpeg, Netz, „Scribe nach 3 Versuchen
   gescheitert") wörtlich im Chat zeigen und Viktor fragen — nicht auf eigene
   Faust umbauen.
2. **Lücken prüfen.** Scribe lässt selten eine kurze Passage aus; das Script
   listet darum jede Wort-Lücke > 5 s als `LÜCKE von–bis`. Je Lücke ein
   Fenster nachprüfen: `<start>` = von − 3, `<laenge>` = (bis − von) + 6,
   beide auf ganze Sekunden gerundet:
   ```bash
   python3 .claude/skills/singing-vsl-transkription/scripts/transcribe.py \
     "<video>" --out "<projekte-db>/<projekt>/<slug>-fenster-<start>s.json" \
     --start <start> --dauer <laenge>
   ```
   Die Fenster-Zeiten kommen bereits absolut (um `--start` versetzt) zurück.
   Hört das Fenster Text, der im Hauptlauf fehlt → die Wörter an ihrer
   Zeitposition ins Transkript einarbeiten und unter „Anmerkungen" ausweisen
   (Fenster-Beleg, keine Erfindung). Bleibt das Fenster leer, ist die Lücke
   eine echte Pause (Musik, Szenenwechsel) — stehen lassen, nie aus dem
   Gefühl auffüllen. Fenster-Dateien nach der Entscheidung löschen — Beleg
   ist das Roh-JSON plus die Anmerkung.
3. **Transkript bauen:** Grundlage ist die `--bloecke`-Datei — Blöcke von
   ~4–10 s an Satzgrenzen, jeder Block beginnt mit `(M:SS)` = abgerundete
   Startsekunde seines ersten Worts. Beim Übernehmen prüfen, nicht blind
   kopieren: Fenster-Funde aus Schritt 2 einarbeiten, offensichtliche
   Satzzeichen-Brüche an Blockgrenzen glätten (nur Zeichensetzung — nie
   Wörter ändern). Endet die Sprache vor dem Video-Ende (Endcard/Outro),
   gehört das in die Kopfzeile — der nächste Schritt muss wissen, wie lang
   wirklich gesprochen wird. Quellen: Video-Länge = `audio_dauer_s` im
   Roh-JSON, Sprach-Ende = `end` des letzten Worts.
4. **Markennamen:** Klingt ein Wort wie eine Marke aus `brands/`
   (Ordnernamen ansehen, z. B. „QUA - Quasi"), die dortige Schreibweise
   verwenden und unter „Anmerkungen" festhalten, was akustisch zu hören war.
   Alles andere Unsichere bleibt wie gehört im Text und wird nur angemerkt —
   die Übersetzung braucht das unverfälschte Original, still „korrigiert"
   wird nichts.
5. **Abliefern:** Zuerst den zweiten Dedup-Prüfpunkt fahren („nach der
   Transkription" in `<projekte-db>/DATENBANK.md` — Kennzeilen-Grep
   gegen die Karten; Treffer → STOPP wie dort beschrieben). Dann als
   `<projekte-db>/<projekt>/<slug>-original-<JJJJ-MM-TT>.md`
   ablegen — exakt dieses Namensmuster, `.claude/skills/singing-vsl-uebersetzung/SKILL.md`
   erwartet es als Vergleichsbasis — die `<slug>-bloecke-roh-…`-Datei danach
   löschen (Arbeitskopie; Beleg sind Roh-JSON und Original), die
   `quelle-kennzeile` (erste ~10 Wörter) in die `karte.md` nachtragen und
   das Transkript vollständig im Chat zeigen. Damit übernimmt die Übersetzung.

## Ausgabe-Gerüst

Copy-Zeilen beginnen mit `(` — Kopf und Anmerkungen nie. So zählt der
Längen-Check der Übersetzung in beiden Dateien nur die Copy.

```markdown
# Transkript (EN): <slug>
Quelle: <Video-Dateiname> · Video <M:SS> · Sprache bis <M:SS>, danach <Outro ohne Sprache / nichts>

(0:00) This collagen mask only works if you stop making these four mistakes.
(0:06) One, you're putting way too much skincare underneath.

## Anmerkungen
- (1:13) Markenname: akustisch „Quazi"/„Obvi", geschrieben nach brands/: Quasi.
- (5:58–6:03) Lücke im Hauptlauf, per Fenster belegt nachgetragen: „…".
```
