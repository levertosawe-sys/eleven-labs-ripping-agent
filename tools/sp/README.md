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
