# Fehlerwege des Lip-Sync-Bausteins

Gelesen, sobald `lipsync_lauf.py` eine FEHLER-Zeile schreibt, `lipsync_einbau.py` mit Exit 1 endet oder ein
Auftrag neu laufen muss. Befehle mit dem Vorspann aus der SKILL.md (`SK`, `BASIS`, Pipeline-Ordner).

## FEHLER-Zeilen von lipsync_lauf.py

| Zeile beginnt mit | Bedeutung | Maßnahme |
|---|---|---|
| `FEHLER Ausschnitt:` | ffmpeg konnte Video oder Audio nicht schneiden | Meldung lesen: fehlt die Sprechspur (`audio` im Auftrag) oder passt `$BASIS` nicht → Pfad korrigieren, Lauf erneut (fertige Aufträge kosten nichts) |
| `FEHLER keine Antwort in 1500 s` | Auftrag läuft bei kie weiter und ist bezahlt; die taskId liegt in `_work/lipsync/<name>_lipsync.mp4.task` | frühestens 10 min später denselben Lauf erneut starten — er holt die taskId ab statt neu einzureichen |
| `FEHLER offene taskId nicht abholbar (Exit 1)` | kie meldet den Auftrag als fehlgeschlagen oder die Antwort ist unlesbar | `_work/lipsync/<name>.log` lesen; `failMsg` enthält „busy“ → `.task`-Datei löschen, Lauf erneut (kostet 0 Credits); sonst Meldung an den Nutzer |
| `FEHLER` mit `createTask fehlgeschlagen` (Wiederholungen aufgebraucht) | 402 trotz Wartezeit oder anderer kie-Fehler | `python3 "$SK/lipsync_kie.py" --pruefen`; Kontostand reicht nicht → Frage wie in SKILL.md Schritt 1; sonst später mit `--nur <name> --parallel 1` erneut |
| `FEHLER Ausgabe hat N Frames statt M` | die Ausgabe folgt der Audio-Länge; das Audio im Ausschnitt ist zu kurz oder zu lang | `ffprobe -show_entries format=duration` auf `_work/lipsync/<name>_audio.wav` gegen (f1 − f0)/fps; Sprechspur reicht nicht bis f1 → Sprechspur prüfen. Die bezahlte Ausgabe NICHT löschen: umbenennen (siehe Neu-Lauf) und erst nach Reparatur neu |
| `WARNUNG: kein AWMS-Ordner` | Verbrauch nicht gebucht | je neuem Auftrag eine Zeile an `<AWMS>/.usage/direkt.jsonl`: `{"ts":"<ISO-Zeit>","workflow":"Eleven Labs Ripping Agent","anbieter":"kie","menge":<creditsConsumed aus _work/lipsync/<name>_lipsync.mp4.job.json>}` |

## Neu-Lauf eines Auftrags

1. Kontostand prüfen (`--pruefen`); reicht er nicht für 8 × volle Sekunden des Auftrags → Frage wie in SKILL.md Schritt 1.
2. Die bezahlte Ausgabe nicht löschen, sondern beiseitelegen:
   `mv _work/lipsync/<name>_lipsync.mp4 _work/lipsync/<name>_lipsync_verworfen1.mp4` (ebenso `.job.json` und `.auftrag.json`).
3. `python3 "$SK/lipsync_lauf.py" --basis "$BASIS" --nur <name> --parallel 1` im Hintergrund, danach SKILL.md Schritt 3–4 für diesen Namen.
4. Höchstens EIN Neu-Lauf je Auftrag. Zeigt auch er den Fehler: Mund-Fehler → Auftrag aus der Einbau-Liste nehmen
   (`_pipeline/lipsync_einbau.json` ohne diesen Eintrag neu schreiben, die Frames bleiben Basis); Farbe → `--farbkorrektur <name>`.
   Beides als offen in die Karte.

## lipsync_bereiche.py erneut laufen lassen

Nach Schritt 2 nur, wenn sich die Karte geändert hat. Das Skript vergibt Namen und Frames neu; `lipsync_lauf.py`
erkennt über `_work/lipsync/<name>.auftrag.json`, ob eine vorhandene Ausgabe noch zu f0/f1 passt — passt sie
nicht, wird der Auftrag neu gerechnet. Vorher angehängte `<name>b`/`c`-Aufträge gehen beim Neuschreiben verloren:
sie danach wieder anhängen.

## Exit 1 von lipsync_einbau.py

| Meldung | Maßnahme |
|---|---|
| `FEHLER: Datei fehlt: …` | Pfad prüfen; fehlt eine Lip-Sync-Ausgabe → `lipsync_lauf.py` erneut, er schreibt die Einbau-Liste neu |
| `FEHLER: <datei> hat N Frames statt M` | Einbau-Liste und Ausgabe passen nicht (Auftrag nachträglich geändert) → `lipsync_lauf.py --basis "$BASIS"` neu laufen lassen (rechnet nur Unpassendes neu, Budget-Stopp greift) |
| `FEHLER: Ausgabe N statt M Frames` / `Encoder abgebrochen` | Plattenplatz (`df -h .`) und ffmpeg-Meldung prüfen, dann Einbau erneut |
