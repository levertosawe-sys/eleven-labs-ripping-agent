# ad-upload

Das Werkzeug hinter dem Upload-Skill: `upload.py` spricht die Meta Marketing API und
legt die fertige Ad im Werbekonto an — immer pausiert.

**WO DAS DING WOHNT:** auf dem Server (`/root/AWMS/`), nicht auf dem Mac. Diese Karte
beschreibt es, der Code liegt dort. Der Skill dazu ist `.claude/skills/ad-upload`.

## Ablauf
1. liest das Adressbuch `ziele.json` (siehe `datenbanken/meta-werbekonto`)
2. holt die MP4 aus dem Einwurf-Ordner `/root/AWMS/UPLOAD` — der Dateiname trägt den
   Projektnamen; passt kein Muster, landet sie unter „unklar“ und der Chat fragt nach
3. lädt das Video hoch
4. legt Anzeigengruppe (Einstellungen 1:1 aus der Vorlage-AdSet), Creative und
   Anzeige an — die Anzeige **immer pausiert**
5. schreibt `upload.json` in den Projektordner: meldet dem Sheet den Launch und ist
   zugleich der Doppel-Upload-Schutz

## Befehle
`pruefen` (Trockenübung) · `hochladen` · `bericht [--live]`

## Gesetz
Der Uploader erfindet nichts. Budget, Zielgruppe und Platzierungen kommen aus der
Vorlage-AdSet; geändert wird im Adressbuch, nie im Code.
