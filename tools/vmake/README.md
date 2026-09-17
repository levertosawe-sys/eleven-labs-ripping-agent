# vmake

Entfernt eingebrannte Untertitel und Wasserzeichen aus der Quell-VSL, bevor der eigene
Text daraufkommt. Gesetz und Grenzen: `.claude/skills/vmake-caption-entfernen/SKILL.md`.

| Script | Kurz |
|---|---|
| `vmake_client.py` | Client der Vmake-Cloud. Subkommandos `preflight` · `config` · `remove <datei\|url> [--out ziel.mp4]` · `poll <task_id> [--out …]` · `download <ziel>`; `remove` nutzt fest den Task `videoscreenclear`. Signiert jeden Request. |
| `schlieren_scan.py` | Vorfilter für Vmake-Rückstände im Caption-Band. Aufruf `schlieren_scan.py <video.mp4> [schwelle]`; Exit 0 = Band ruhig, Exit 1 = Regionen als „a–b s"-Zeilen. Meldet auch helle Szenen — die Regionen werden angesehen, nicht geglaubt. |

Schlüssel: `MT_AK` + `MT_SK` aus `~/.config/leichtkraut/.env` (`VMAKE_AK`/`VMAKE_SK` werden
als Alt-Namen ebenfalls akzeptiert). Arbeitsverzeichnis = `_pipeline/`-Ordner des Projekts,
dort landet `vmake_state.json` (trägt `task_id` und die Ergebnis-URLs, damit `poll` und
`download` einen abgebrochenen Lauf fortsetzen, ohne neu hochzuladen).
Aufruf mit `~/.venvs/sa/bin/python3`.

**Upload-Weg:** Hauptweg ist das Paket `alibabacloud-oss-v2` im `~/.venvs/sa` (dort 1.3.2).
Fehlt es, greift ein eingebauter Signatur-Rückfall ohne Fremd-Bibliothek — der Lauf bricht
also nicht ab, meldet aber „Upload fertig (Rueckfall ohne SDK)".
