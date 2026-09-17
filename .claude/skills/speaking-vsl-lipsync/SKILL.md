---
name: speaking-vsl-lipsync
description: "Gibt Menschen, die in der Quell-Ad sichtbar sprechen, einen deutschen Mund — Lip-Sync über kie.ai nur auf den Frames, in denen ein Mensch frontal spricht; alles andere im Bild bleibt Original. Zuständig für den Knoten lip-sync im Workflow „Eleven Labs Ripping Agent“ (nach der Audio-Prüfung, vor dem Schnitt) und für die Lip-Sync-Frage am Start eines Laufs. Nutzen, wenn der Nutzer sagt „Lip-Sync“, „Lippen anpassen“, „der Mund passt nicht zur deutschen Stimme“, „UGC mit Lip-Sync“, „die Sprecherin soll Deutsch sprechen“, „mach den Mund deutsch“, oder wenn eine gesprochene Ad mit sichtbar sprechender Person (UGC, Ärztin, Presenter in die Kamera) gerippt wird — auch ohne das Wort Lip-Sync. Auch bei Befunden an fertigem Lip-Sync: Farbflecken um den Mund, heller Block in Blitz oder Blende, Mund eingefroren, Farbstich im Gesicht, kie-Auftrag hängt. Nicht für Tiere, Cartoon- oder 3D-Figuren und nicht für komplett neu erzeugte Avatar-Clips."
---

# Lip-Sync — ein deutscher Mund nur für Menschen, die sichtbar sprechen

Eine deutsche Stimme über fremdsprachig sprechende Lippen fällt sofort auf, sobald ein Mensch
frontal in die Kamera spricht. Dieser Baustein tauscht nur die Mundbewegung dieser Frames;
B-Roll, Hände, Produkte und alles ohne sichtbares Sprechen bleiben Original mit der Stimme darüber.

## Nur Menschen — die harte Grenze

Lip-Sync läuft ausschließlich auf Menschen, deren Lippen im Original sichtbar sprechen. Tiere,
Cartoon- und 3D-Figuren bekommen nie einen Lip-Sync, auch wenn sie in der Quelle „sprechen“: Das
Modell macht dort Nasen grau und verwaschen, Schnauzen unscharf und Objekte im Bild doppelt, und
das Maul folgt trotzdem eher dem Original. Ihre Clips bleiben Original mit der deutschen Stimme darüber.

## Vorspann für jeden Kommando-Block

Shell-Variablen überleben keinen einzelnen Aufruf — diese Zeilen stehen vor jedem Block:

```bash
cd "<AWMS>/brands/<Brand>/<NNN> EL"      # <AWMS> = der Ordner mit workflows/; Pipeline-Ordner des Projekts
SK="../../../.claude/skills/speaking-vsl-lipsync/scripts"
BASIS="_work/bildbasis.mp4"             # das saubere Bild der Ad; hat das Projekt keine: "_work/vmake_cleaned.mp4"
```

Einmal je Lauf prüfen: `python3 -c "import cv2, numpy"` (ImportError → im Python der Kette
`pip install numpy opencv-python`), `python3 "$SK/lipsync_kie.py" --pruefen` (liest `KIE_API_KEY` aus der
Umgebung oder einer `.env`; „fehlt“ → den Nutzer bitten, den Schlüssel in die `.env` des AWMS-Ordners zu
legen, nie im Chat) und dass `$BASIS` so viele Frames hat wie `_work/source_original.mp4`
(`ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 <datei>`) —
weichen sie ab, stoppen und das dem Nutzer melden.

## Am Start des Laufs: die Lip-Sync-Frage

Beim Trigger, bevor Geld fließt: `python3 "$SK/lipsync_bereiche.py" --vorbefund _work/source_original.mp4`
(„Video fehlt“ → den Quellpfad des Triggers nehmen).

- „Lip-Sync-Frage stellen“ (ab 3 s frontales Gesicht) → den Nutzer zusammen mit den übrigen Startfragen
  fragen — mit dem Frage-Werkzeug (Optionen „Ja, einbauen“ / „Nein“), ohne Frage-Werkzeug als Frage im
  Chat. In die Frage gehören: gemessene Sekunden, Kostenregel (8 kie-Credits je volle Sekunde),
  Schätzung (Sekunden × 8) und der Kontostand aus `--pruefen`.
- „Lip-Sync-Knoten entfällt“ → nicht fragen.
- Die Antwort sofort ins Frontmatter der Projekt-Karte schreiben, in Anführungszeichen:
  `lip-sync: "JA — <Wortlaut>"` · `lip-sync: "NEIN"` · `lip-sync: "entfällt (kein Mensch sichtbar)"`.
  Karte = `<AWMS>/datenbanken/sp-projekte/<Projekt>/karte.md`; `<Projekt>` ist der beim Trigger angelegte
  Ordner (einziger Treffer auf `<KÜRZEL> <NNN> EL | *`; kein oder mehrere Treffer → den Nutzer fragen).
  Der Knoten lip-sync läuft nur bei `JA`.

## Eingaben

| Datei | Inhalt |
|---|---|
| `_pipeline/clip_karte.json` | JSON-Liste von Clips: `clip`, `t0`, `t1`; dazu aus Schritt 0 `mensch_spricht`, optional `mensch_rolle`, `lipsync_aus` |
| `$BASIS` | das saubere Bild der Ad, Frame für Frame deckungsgleich mit der Quelle |
| `_work/sprechspur.wav` bzw. `_work/sprechspur_<mensch_rolle>.wav` | deutsche Sprechspur auf der Zeitachse der Quelle, abgenommen an der Audio-Prüfung |

## Ablauf

Checkliste kopieren und abhaken:

```
- [ ] 0 Karte ergänzen: mensch_spricht / mensch_rolle / lipsync_aus
- [ ] 1 Aufträge: lipsync_bereiche.py, Kosten gegen Kontostand
- [ ] 2 Lauf im Hintergrund, Log auf FEHLER geprüft
- [ ] 3 Farbstich roh: jede AUFFÄLLIG-Zeile eingeordnet
- [ ] 4 Sichtprüfung aller Aufträge, Befunde repariert und nachgemessen
- [ ] 5 Einbau ins Bild
- [ ] 6 Nachprüfung im Bild aus Schritt 5
- [ ] 7 Karten-Abschnitt „Knoten lip-sync“
```

**0 Karte ergänzen.** Je Clip in `_pipeline/clip_karte.json` setzen:
- `mensch_spricht`: `true` nur, wenn die Lippen eines Menschen in `_work/source_original.mp4` sichtbar im
  Sprechtakt gehen. Pro Clip Anfang, Mitte und Ende ansehen
  (`ffmpeg -v error -ss <sekunde> -i _work/source_original.mp4 -frames:v 1 <scratchpad>/c<clip>_<sekunde>.jpg`);
  bei vielen Clips darf ein Hilfs-Agent das mit denselben Bildern tun.
- `mensch_rolle`: gibt es Rollen-Spuren `_work/sprechspur_<rolle>.wav`, bekommt jeder Clip dieser Person
  exakt den Dateinamen-Teil (`"aerztin"` für `sprechspur_aerztin.wav`).
- `lipsync_aus: true`: vom Nutzer ausgenommene Clips („nicht die Szene im Handy-Video“) — `mensch_spricht`
  bleibt dabei wahr, die Karte beschreibt weiter, was zu sehen ist.

**1 Aufträge.** `python3 "$SK/lipsync_bereiche.py" --basis "$BASIS"` schreibt `_pipeline/lipsync_auftraege.json`.
Ein Auftrag (Frames der ganzen Ad, `f1` exklusiv):
`{"name": "spr_c54", "clip": 54, "f0": 3680, "f1": 3739, "t0": 147.2, "t1": 149.56, "dauer": 2.36, "audio": "_work/sprechspur_sprecherin.wav", "blitz_ausgeschnitten": [[3739, 3751]]}`.
Farbblitze und Schwarz-/Weißblenden schneidet das Skript heraus, auch direkt vor und hinter einem Lauf:
dort malt der Lip-Sync eine hautfarbene untere Gesichtshälfte und färbt Wangen und Kinn im ganzen Clip ein.
- Exit 3 „Feld fehlt“ → Schritt 0. · Exit 4 „kein Mensch“ → `lip-sync: "entfällt (kein Mensch spricht laut Karte)"`, Knoten beenden.
  · Exit 5 „0 Aufträge“ → Befund an den Nutzer (Gesichter zu klein oder zu kurz im Bild), Knoten beenden.
- Erfolg: „N Aufträge · … s · Kosten ≈ K“. Liegt K über dem Kontostand, den Nutzer fragen (wie am Start):
  „aufladen“ · „nur eine Auswahl“ · „ohne Lip-Sync“. Auswahl = längste Aufträge zuerst, bis 80 % des
  Kontostands (20 % bleiben für Neu-Läufe) — ihre Namen gehen als `--nur` in Schritt 2. Die Wahl samt
  ausgelassenen Aufträgen in den Karten-Abschnitt.

**2 Lauf.** Im Hintergrund starten (Bash mit `run_in_background`) und die Fertig-Meldung abwarten:

```bash
python3 "$SK/lipsync_lauf.py" --basis "$BASIS" [--nur <namen>] > _work/lipsync/lauf.log 2>&1; echo "Exit $?"
```

Danach `grep -E "FEHLER|BUDGET|Einbau:" _work/lipsync/lauf.log`. Exit 0 + „Einbau: N Einträge“ = fertig.
Exit 6 „BUDGET-STOPP“ = nichts gestartet, Frage wie in Schritt 1. Exit 1 → je FEHLER-Zeile in
[references/fehlerwege.md](references/fehlerwege.md) nachsehen (lesen, sobald eine FEHLER-Zeile auftaucht) —
vor allem: einen hängenden Auftrag nie neu einreichen, der nächste Lauf holt ihn ab.

**3 Farbstich roh.** `python3 "$SK/lipsync_farbe.py" messen --alle`. Sauber 0,7–1,5, Flecken aus Blitzen
20–28, AUFFÄLLIG über 4. Jede AUFFÄLLIG-Zeile nennt den Frame k im Auftrag; Eingang und Ausgang ansehen:

```bash
ffmpeg -v error -i _work/lipsync/<name>_video.mp4   -vf "select=eq(n\,<k>)" -frames:v 1 <scratchpad>/<name>_<k>_ein.jpg
ffmpeg -v error -i _work/lipsync/<name>_lipsync.mp4 -vf "select=eq(n\,<k>)" -frames:v 1 <scratchpad>/<name>_<k>_aus.jpg
```

Zeigt der Eingang dort einen Blitz oder eine Blende: deren Frames im Auftrag bestimmen (Frames rund um k
ansehen, bis das Bild wieder normal ist) und mit `messen <name> --ohne <a>-<b>` nachmessen — weiter in
Schritt 4, Zeile „Blende/Blitz“. Ohne Blitz im Eingang: Schritt 4, Zeile „Farbschleier ohne Blitz“.

**4 Sichtprüfung.** Jeden Auftrag aus der Einbau-Liste Ein- gegen Ausgang prüfen lassen — nach
[references/sichtpruefung.md](references/sichtpruefung.md) (lesen, wenn dieser Schritt beginnt). Die Messung
Mundbewegung ↔ Tonhülle taugt nicht als Beweis: der Original-Mund korreliert mit dem deutschen Ton oft
genauso stark. Reparatur je Befund:

| Befund | Reparatur |
|---|---|
| Blende/Blitz: Fleck oder heller Block, `messen <name> --ohne <Blende>` ist ok | Fenster in `_pipeline/lipsync_uebergaenge.json`: `{"<name>": [[<f0+a>, <f0+b>]]}` (Frames der ganzen Ad, Ende exklusiv) — dort bleibt das Bild Basis, 0 Credits |
| Blende/Blitz, und auch ohne die Blende AUFFÄLLIG | Neu-Lauf ohne die Blende: in `_pipeline/lipsync_auftraege.json` `<name>b` mit gekürztem `f0`/`f1` (dazu `t0`, `t1`, `dauer` neu) anhängen; liegt die Blende mitten im Auftrag, `<name>b` davor und `<name>c` dahinter; dann `lipsync_lauf.py --nur <name>b[,<name>c]` und Schritt 3–4 für die neuen Namen |
| Farbschleier ohne Blitz (`mund_artefakt` mit Farbfleck, `gesicht_veraendert` mit Farbsprung) | `ffprobe -v error -show_entries stream=color_space -of csv=p=0` auf `_lipsync.mp4` und `_video.mp4`: verschieden → `python3 "$SK/lipsync_kie.py" --kennzeichnen <lipsync.mp4> <video.mp4>`, nachmessen (Ziel ≤ 4); gleich → Neu-Lauf wie unten |
| `mund_eingefroren`, `mund_artefakt` ohne Farbe (verschmiert, doppelte Zähne), `grenz_sprung`, `gesicht_veraendert` ohne Farbe | Neu-Lauf nach [references/fehlerwege.md](references/fehlerwege.md), Abschnitt Neu-Lauf eines Auftrags |
| `offen_waehrend_stille` = unsicher | belassen, in der Karte vermerken — ein Neu-Lauf trifft die Mundform nicht gezielt |

Braucht eine Reparatur Credits, die der Kontostand nicht hergibt: dieselbe Frage wie in Schritt 1. Ohne
Neu-Lauf gilt je Befund: Farbe → `--farbkorrektur <name>` beim Einbau (wirkt nur teilweise); Mund-Fehler →
Auftrag aus der Einbau-Liste nehmen (die Frames bleiben Basis mit englischem Mund); beides als offen in die Karte.

**5 Einbau.** Hat das Projekt ein eigenes Montage-Skript, das das Bild frame-genau zusammensetzt, liest es
`_pipeline/lipsync_einbau.json` und `_pipeline/lipsync_uebergaenge.json` und baut dort ein — eine
Encode-Generation. Regeln je Frame: Einbau-Eintrag ohne Übergangs-Fenster → Lip-Sync-Frame; im Fenster →
Basis-Frame; `<name>b`/`c` ersetzen `<name>`. Ein eigenes Skript liest mit
`-vf scale=flags=accurate_rnd+full_chroma_int` und schreibt mit `-vf scale=out_color_matrix=bt709:out_range=tv`
plus bt709-Tags — Tags allein lassen die Matrix auf bt601. Ohne eigenes Skript:

```bash
python3 "$SK/lipsync_einbau.py" --basis "$BASIS"      # → _work/bild_lipsync.mp4
```

Erfolg = „Frames: {…} → _work/bild_lipsync.mp4 (N Frames)“ mit N = Frames der Basis; HINWEIS-Zeilen nennen
Übergangs-Fenster außerhalb aller Einträge (Tippfehler oder Rest eines ersetzten Erstlaufs — prüfen).
Exit 1 → [references/fehlerwege.md](references/fehlerwege.md), Abschnitt Einbau. Der Knoten schnitt
rendert danach mit `--video _work/bild_lipsync.mp4`.

**6 Nachprüfung.** Direkt nach Schritt 5:
`python3 "$SK/lipsync_farbe.py" messen-final --final _work/bild_lipsync.mp4 --basis "$BASIS"` (bei eigenem
Montage-Skript dessen Ausgabe). Jede AUFFÄLLIG-Zeile nennt den Frame der Ad — ansehen, Befund in die Tabelle
von Schritt 4. Dazu jeden reparierten und die drei längsten Aufträge je einmal auf Handy-Größe (~360 px
breit, ganzes Bild) gegen `$BASIS` halten; bestanden = kein Fleck, keine Kante, Mund bewegt sich. Schwere wird
im Vollbild beurteilt, nie im Zoom.

**7 Karte.** In `<AWMS>/datenbanken/sp-projekte/<Projekt>/karte.md` anhängen:

```
## Knoten lip-sync · <JJJJ-MM-TT> — <fertig | fertig mit offenen Punkten | entfällt>
- Aufträge: <N> · <Sekunden> s · verbraucht <Summe creditsConsumed aus _work/lipsync/*.job.json> Credits · Blitz/Blende ausgeschnitten: <Namen>
- Budget: <„reichte“ | Wahl des Nutzers + ausgelassene Aufträge>
- Farbstich roh (max): sauber <kleinster–größter Wert> · auffällig <Name: Wert, Grund>
- Sichtprüfung: <N> sauber · Befunde <Name: Klasse, Frames der Ad> · Reparatur <was>
- Einbau: <Skript> → <Datei> · <Frames Lip-Sync> von <Frames gesamt>
- Nachprüfung: <max-Werte, Grenze> · offen: <Punkte oder „nichts“>
```

## Gotchas

- **kie liefert ohne Farbkennzeichnung.** Die YUV-Werte des Eingangs kommen unverändert zurück, aber
  `color_space` fehlt; ffmpeg liest dann bt601 statt bt709, Hauttöne verschieben sich (Farbstich Ø 3,6 statt
  1,0). `lipsync_kie.py` überträgt die Kennzeichnung nach dem Download selbst.
- **402 „Credits insufficient“ trotz Guthaben**, wenn parallele Aufträge Credits reservieren — `lipsync_lauf.py`
  wählt bei knappem Kontostand selbst einzeln. **„The server is busy“ kostet 0 Credits.**
- Die Lip-Sync-Ausgabe ist etwa eine Luma-Stufe dunkler als der Eingang. An Schnitten unsichtbar — nicht korrigieren.
- Ein Auftrag dauert 40 s bis 15 min; das Warten erledigt das Skript im Hintergrund, nicht die Session.
