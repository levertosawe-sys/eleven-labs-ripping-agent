# sp

Werkzeugkasten der Speaking-Kette (Eleven Labs Ripping Agent) — das Pendant zu
`tools/sa` der Singing-Linien. Alle Scripts laufen mit `~/.venvs/sa/bin/python3`,
Arbeitsverzeichnis = Pipeline-Ordner des Projekts (`brands/<Brand>/<NNN> SP/`),
Schlüssel aus `~/.config/awms/.env` (ELEVENLABS_API_KEY, KIE_API_KEY).

| Script | Schritt in der Kette | Kurz |
|---|---|---|
| `new_sp_project.py` | Projekt-Bootstrap | legt `brands/<Brand>/<NNN> SP/` an (_pipeline/_work, sp_config, source.mp4, source_words.json), portiert clip_karte.py, trägt den Pipeline-Ordner in die karte.md nach |
| `clip_karte.py` | Clip-Karte | Szenen zerlegen (scene>0,30), EN-Wörter zuordnen, Frames ziehen; `merge` heftet die Augen-Beschreibungen an |
| `emotions_karte.py` | Emotions-Karte | je Copy-Zeile Original-Schnipsel ans Anker-bestandene Gemini-Ohr (kie.ai) → Emotion/Ton/Betonung/Pausen + v3-Tag-Vorschlag → `_pipeline/emotions_karte.json` |
| `sprechspur.py` | Sprechspur-Bau | HIER wird ElevenLabs generiert: `stimme` (Register-Zeile) · `take` (EIN Take, v3 + Audio-Tags) · `montage` (an gemessenen Pausen schneiden, adelay auf Marken, loudnorm) · `woerter` (Wort-Cache via Scribe) |
| `pruefer.py` | sprech-watch | maschinelles Abhören: Rück-Transkription gegen Soll, Pausen-Messung, Fenster-Zeiten, Gemini-Ohr → `_pipeline/pruefer.json`, Exit 1 bei roter Zeile |
| `render.py` | Schnitt + Render | Sprechspur + Musikbett mischen, unter das bereinigte Video muxen — ohne Pixel-Eingriff `-c:v copy`, mit Abdeck-Boxen crf 18 + bt709 |
| `abnahme.py` | Abnahme | Zahlen statt Gefühl: Frame-Gleichstand, Dauer, Block-Startmarken per Kreuzkorrelation ±0,25 s, Loudness |

Das Musikbett braucht kein eigenes Script: Demucs läuft direkt
(`python3 -m demucs --two-stems=vocals -n htdemucs <audio>`), Regeln im Skill
`.claude/skills/speaking-vsl-musikbett/SKILL.md`.

Herkunft: destilliert aus den ersten beiden echten Läufen der Kette (Lauf bei
Levert + ROV 006/007); Stand und offene Messpunkte in DECISIONS.md.

## Bekannte Werkzeug-Fallen (VIS 015 EL, 23.09.2026 — Fixes stehen aus)
- **abnahme.py:** Der Startmarken-Check ist bei stillen Schluss-Blöcken blind — das
  Referenz-Snippet ab der Marke ist fast nur Stille, die Korrelation klebt am
  Fensterrand und meldet einen KONSTANTEN Offset (gemessen: dreimal exakt −477 ms
  trotz veränderter Spur). Beleg statt Jagd: global über 4–5 s mit Sprache
  korrelieren (0 ms = synchron).
- **sprechspur.py montage --dehnen:** schiebt den LETZTEN Block hinter gedehnte
  Vorgänger (sequenziell statt Marken-adelay) — Blöcke kleben. Chirurgen-Fix:
  Schluss-Segment per atrim/adelay auf die Marke zurückschieben.
- ~~**sprechspur.py stimmen-lookup:** stolpert über Dialog-Registerzeilen~~ — BEHOBEN
  25.09.2026 (VIS 021 EL): exakte Langform gewinnt; beim reinen Kürzel zählen Zeilen mit
  Klammer-Zusatz („(Dialog: …)") nicht mit, solange es genau eine Standard-Zeile gibt.
- **clip_karte.py Zeitachse:** rechnete FPS aus der Container-Dauer (Ton länger als Bild →
  Clip-Grenzen bis +0,13 s zu spät, das Ankleben < 0,8 s nahm die falsche Grenze) —
  BEHOBEN 25.09.2026 (VIS 021 EL): FPS aus dem Video-Strom, letzte Grenze = Bilddauer,
  Selbstprüfung „Zeitachse ok" (Median hart↔Szene), Abbruch bei Drift > 1 Frame.
- **emotions_karte.py / pruefer.py Ohr-Wiederholung:** bei HTTP 500 (Wartung) wartete jede Zeile
  20 + 40 s auf der toten Route, bevor die nächste drankam — 28 Zeilen ≈ 35 min. BEHOBEN 25.09.2026
  (VIS 021 EL): Sicherungsschalter — zwei Aufrufe in Folge nur 500 → Route für den Rest des Laufs
  übersprungen (Meldung „[ohr] … übersprungen"), jede echte Antwort setzt zurück. WORDS-Bindung unverändert.

## Scribe-Cache der Montage (VIS 017 EL, 25.09.2026)
- `sprechspur.py montage` (auch `--nur-messen`) holt die Take-Wortzeiten jetzt nur EINMAL je Take-Datei und legt sie
  neben dem Take ab: `<take>.woerter-<sha12>.json`. Vorher hörte Scribe den ganzen Take bei jedem Aufruf neu und zog
  das geteilte ElevenLabs-Kontingent leer (Befund DOG 005 EL). Neuer Take = neuer Hash = neuer Scribe-Lauf.
