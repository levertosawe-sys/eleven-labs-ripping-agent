---
name: vmake-caption-entfernen
description: "Entfernt die eingebrannte Sprech-Untertitelspur aus einem Video per Vmake-API (Task videoscreenclear) — inklusive Schlieren-Kontrolle, Schutz des Gestaltungs-Texts, Song-Remux und ehrlicher Baubarkeits-Bewertung. Nutzen, wenn Viktor sagt „entferne die Captions aus dem Video", „die englischen Untertitel müssen weg", „nutze Vmake", oder wenn eine Quell-Ad eingebrannte Untertitel trägt, die die deutschen CapCut-Captions stören. Endcards, Angebots-Störer und andere Grafik-Typo bleiben dabei stehen — dieser Skill entfernt sie nie."
---

# Vmake: die Sprech-Untertitel aus einem Video entfernen

Zweck: Die eingebrannte Sprech-Untertitelspur tilgen, ohne Timing anzufassen und
ohne den übrigen Bildtext anzurühren. Der Song/Ton des Projekts bleibt Master: nach
einer Render-Bereinigung wird er drübergemuxt, nach einer Quell-Bereinigung entsteht
er ohnehin frisch im Neu-Render.

**Vor Schritt 1: das Original sichern.** Die Nachkontrolle (Schritt 4c) und jede
Reparatur brauchen den unberührten Stand als Vergleich und als Quelle:
`cp _work/source.mp4 _work/source_original.mp4` (Render-Zweig entsprechend
`_work/render_original.mp4`). Fehlt die Sicherung, ist ein angetasteter
Gestaltungs-Text nicht mehr wiederherstellbar.

Werkzeug (ausführen, immer mit `~/.venvs/sa/bin/python3`, Arbeitsverzeichnis =
`_pipeline/`-Ordner des Projekts — dort landet `vmake_state.json`):
`tools/vmake/vmake_client.py` (Pfad relativ zum Projektstamm — dem Ordner, in dem
`.claude/`, `datenbanken/` und `brands/` nebeneinander liegen)
Subkommandos: `config` · `remove <datei|url>` · `poll <task_id>` · `download <ziel>`.
`remove` nutzt fest den Task `videoscreenclear`; der Task-Katalog steht in der
`config`-Ausgabe (relevant erst, wenn der Client um weitere Tasks erweitert wird).
Keys: `VMAKE_AK` + `VMAKE_SK` in `~/.config/leichtkraut/.env` (Access + Secret,
beide nötig — das Verfahren signiert jeden Request).

## Der Auftrag ist eng: NUR die Sprech-Untertitel

Aus einer Quell-Ad wird ausschließlich die **Sprech-Untertitelspur** entfernt.
**Eingebrannter Gestaltungs-Text bleibt unangetastet** — Endcard, Angebots-Störer
(„BUY 1 GET 1 FREE", „90-DAY MONEY-BACK GUARANTEE"), Gold-Schilder, Hero-Titel,
Siegel, Preis-Grafik. Er wird nicht getilgt, nicht abgedeckt, nicht durch eine
deutsche Fassung ersetzt, auch nicht teilweise.

Der Grund ist inhaltlich: Solche Grafik gehört zum Video, nicht zur Untertitelspur.
**Die Regel gilt unabhängig vom Werkzeug** — auch ein besseres Inpainting würde daran
nichts ändern.

Dazu kommt als Zusatzgrund, warum Versuche zusätzlich schlecht aussehen:
`videoscreenclear` ist für Wasserzeichen und dünne Untertitel gebaut, nicht für
gefüllte Flächen. An einem farbigen Balken oder einer großen Typo verschwinden die
Buchstaben, die FLÄCHE dahinter bleibt als Keil stehen. Und `delogo` oder ein Overlay
über eine große Fläche zerstört mehr, als es rettet.

**Rote Flaggen — jeder dieser Gedanken heißt STOPP:** „die Endcard ist doch auch
Text" · „nur diesen einen Störer noch" · „eine enge Box drüber fällt nicht auf" ·
„auf Deutsch wäre es stimmiger" · „der Rest sieht halb getilgt schlimmer aus, ich
mache es ganz". Der letzte Gedanke ist die gefährlichste Rationalisierung: Ein
halb getilgter Störer wird nicht durch vollständiges Tilgen gerettet, sondern durch
**Wiederherstellen** (siehe Schritt 4c).

**Prüfung trotzdem Pflicht — auch die ERSTEN Sekunden, nicht nur eine Stichprobe aus
der Mitte.** Hero-Titel stehen in Sekunde 0–4; eine Stichprobe ab Frame 30 sieht sie
nie. Acht Frames über die ersten vier Sekunden (bei 30 fps):
`ffmpeg -i _work/vmake_cleaned.mp4 -vf "select='lt(n,120)*not(mod(n,15))',tile=4x2" -vsync 0 /tmp/erste.png`
Geprüft wird hier nicht, ob der Gestaltungs-Text weg ist, sondern ob er noch **heil**
ist. Diese Prüfung ist Teil von Schritt 4c.

Bleibt nach zwei Läufen dasselbe Untertitel-Fenster unberührt (Schritt 4b liefert
identische Zeiten), ist ein dritter Lauf verschwendet: Was Vmake nicht erkennt,
erkennt es auch beim Wiederholen nicht. Dann bleibt der englische Rest stehen und
wird im Befund benannt.

## Vor dem Entfernen: Textsorten trennen

Nicht jeder Text im Bild ist ein Untertitel. Vor dem Vmake-Lauf die Stellen sichten und
in zwei Listen schreiben — eine Datei `_work/gestaltungs-text.md` mit zwei
Abschnitten, Spalten Zeitfenster (`von`–`bis` in Sekunden) · Originalwortlaut ·
Box `x,y,w,h` in Pixeln des Quellbilds:

- **Sprech-Untertitel** — klein, unteres Drittel, folgen dem Gesprochenen. Werden
  entfernt; die Fassung in der Zielsprache tritt später an ihre Stelle — das gilt
  nur für diese Spur, Gestaltungs-Text wird nie ersetzt. Ihr Bandbereich ist
  zugleich das Prüfband für Schritt 4b.
- **Gestaltungs-Text** — Hero-Titel, große farbige Typo, Preis-Störer, Endcard.
  Bleibt stehen. Die Liste wird trotzdem geführt, aber sie ist eine **Schutzliste**,
  keine Arbeitsliste: Sie sagt der Nachkontrolle (Schritt 4c), welche Bildbereiche
  nach dem Lauf unversehrt sein müssen. Sie wandert weder an die Captions noch an den
  Schnitt.

Die Position misst man, statt sie zu schätzen: einen Frame als `rgb24` dekodieren, die
Farbfläche per Schwelle maskieren und die dichten Zeilen/Spalten als Box ausgeben.
Greift die Schwelle nicht (warmes Bild hinter warmer Typo), die Box am Frame ablesen
und das im Befund so vermerken — eine abgelesene Box ist brauchbar, eine geratene nicht.

Erst danach läuft `remove`.

## Das Bild nie unnötig neu encodieren

Wird dem bereinigten Video nur eine Tonspur zugefügt, läuft das Video per **`-c:v copy`** —
Stream-Copy, kein Neu-Encode. Jede zusätzliche h264-Generation frisst zuerst die Farbe,
sichtbar an gesättigten Rot- und Orangetönen: Sie sind chroma-unterabgetastet (yuv420p)
und brechen als Erstes in Streifen und Säume auf — genau dort, wo Schmerz-Glow, Blut und
Warnfarben sitzen. Regel: **Ein Ton-Mux ist kein Grund, das Bild anzufassen.** Nur wenn
wirklich in die Pixel gegriffen wird (Overlay, Crop, Skalierung), wird encodiert — dann
mit `-crf 18` oder besser und immer mit den bt709-Tags auf Container-Ebene.

Gegenprobe vor dem Ausliefern: `ffprobe -select_streams v:0 -show_entries stream=nb_frames`
auf Eingabe und Ausgabe. Gleiche Frame-Zahl UND Stream-Copy = das Bild ist bitgleich, es
KANN keine neuen Artefakte tragen. Das beantwortet auch die Rückfrage „kommen die Streifen
von Vmake?" ohne Raterei.

## Vorgehen

1. **Caption-Stellen des Originals festhalten:** Schlieren-Scan (Schritt 4) einmal auf
   dem UNBEREINIGTEN Video laufen lassen — seine Regionen-Liste (Sekunden-Spannen)
   sind die Caption-Stellen für alle späteren Vorher/Nachher-Vergleiche.
2. **Welche Datei bereinigen?** Standard: die QUELLE (`_work/source.mp4`), NICHT der
   fertige Render. Grund (gemessen): Video-Inpainting nutzt Nachbar-Frames; der fertige
   Schnitt hat alle paar Sekunden harte Cuts und liefert schlechten Kontext — auf der
   glatten Quelle rekonstruiert Vmake sichtbar besser. Den Render direkt zu bereinigen
   ist die Ausweich-Route, wenn keine Quelle existiert.
3. **Entfernen:** `remove <datei>` — lädt selbst zu Vmakes OSS hoch (fremde Hosts wie
   litterbox erreichen deren China-Server NICHT: „Video Download Error") und startet
   den Task. `poll <task_id>` wiederholen, bis FERTIG oder FEHLGESCHLAGEN gedruckt
   wird — die gemeldete `predict_elapsed`-Schätzung ist viel zu optimistisch (~84 s
   gemeldet, >10 min real bei ~5-min-Videos). Nach 45 min ohne Terminal-Status oder
   bei FEHLGESCHLAGEN: einmal neu einreichen; scheitert auch das, Viktor mit der
   Fehlermeldung stoppen (häufig: Quota leer — steht in der CONSUME-Antwort).
   Ergebnis: `download _work/vmake_cleaned.mp4`.
4. **Schlieren-Scan + Sichtung (Pflicht):** Vmakes bekannte Schwäche sind helle
   Karaoke-Highlight-Boxen — dort hinterlässt das Inpainting weiße Leucht-Schlieren.
   Der Scan dekodiert das ganze Video und läuft mit dem Rechen-venv:
   `~/.venvs/sa/bin/python3 tools/vmake/schlieren_scan.py <video.mp4> 30`
   (Exit 0 = Band ruhig, Exit 1 = Regionen-Liste als `a–b s`-Zeilen; ImportError =
   fehlendes Paket im venv nachinstallieren). Der Scan ist ein VORFILTER: Er misst
   Helligkeit und verwechselt darum helle Produkt-Shots mit Schlieren — die gemeldeten
   Regionen werden angesehen, nicht geglaubt. Dann ANSEHEN — je auffälliger Region UND
   je 2–3 Original-Caption-Stellen aus Schritt 1:
   `ffmpeg -ss <Sekunde> -i _work/vmake_cleaned.mp4 -frames:v 1 -vf "crop=iw:ih*0.30:0:ih*0.54,scale=iw*2:ih*2" /tmp/check_<Sekunde>.png`
   und die PNGs mit dem Read-Werkzeug öffnen. So beantwortet EIN Blick beides:
   Text weg? Schlieren da?

4b. **Rest-Karten messen statt schätzen.** Ob wirklich alles weg ist, entscheidet nicht
   der Blick auf drei Stichproben, sondern der Vergleich Frame für Frame: Wo Vmake
   gearbeitet hat, unterscheidet sich das Caption-Band vom Original; wo es NICHTS getan
   hat, ist der Unterschied null — und dort steht das englische Wort noch. Beide Videos
   klein dekodieren (`scale=180:320`, `-pix_fmt gray`), je Frame den mittleren Betrag der
   Differenz im Band y 64–86 % rechnen und die Frames mit Differenz < 0,6 zu Zeit-Fenstern
   clustern. Ausgabe: Zahl der unberührten Frames + die Fenster in Sekunden. Diese Fenster
   sind der Befund für Schritt 5 — mit Sekunden, nicht mit „sieht sauber aus".

4c. **Gestaltungs-Text auf Unversehrtheit prüfen (Pflicht).** Je Eintrag der
   Schutzliste aus `_work/gestaltungs-text.md` einen Frame aus der Mitte seines
   Zeitfensters ziehen — aus `_work/vmake_cleaned.mp4` UND aus dem gesicherten
   Original — und beide mit dem Read-Werkzeug nebeneinander ansehen:
   ```bash
   ffmpeg -y -v error -ss <sekunde> -i _work/vmake_cleaned.mp4 -frames:v 1 -vf "scale=400:-1" /tmp/g_neu.png
   ffmpeg -y -v error -ss <sekunde> -i _work/source_original.mp4 -frames:v 1 -vf "scale=400:-1" /tmp/g_alt.png
   ```
   Unversehrt = der Text ist vollständig lesbar und die Fläche dahinter trägt keinen
   Keil oder Schleier. Gegenprobe in Zahlen, damit das nicht am Geschmack hängt:
   mittlere Pixeldifferenz alt↔neu INNERHALB der Schutzbox — unter 1,0 (Graustufe
   0–255) hat Vmake dort nichts angefasst, darüber ansehen und entscheiden. Ist alles
   heil, ist nichts zu tun — genau so soll es sein.

   **Angetastet (Buchstaben teilweise weg, Fläche verwaschen) → wiederherstellen,
   nicht fertig tilgen.** Der Original-Bildbereich wird aus dem gesicherten Original
   zurückkopiert, nur im Zeitfenster und nur in der Box der Schutzliste:
   ```bash
   ffmpeg -y -i _work/vmake_cleaned.mp4 -i _work/source_original.mp4 -filter_complex \
     "[1:v]crop=<w>:<h>:<x>:<y>[o];[0:v][o]overlay=<x>:<y>:enable='between(t,<von>,<bis>)'[v]" \
     -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy \
     -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
     _work/vmake_repariert.mp4
   ```
   Vorbedingung: Beide Eingänge müssen dieselbe Auflösung und fps haben (Vmake
   re-encodiert — einmal `ffprobe` auf beide). Weichen sie ab, kein Overlay, sondern
   Befund an Viktor.
   Danach `vmake_repariert.mp4` → `_work/vmake_cleaned.mp4`, Frame-Zahl gegenprüfen
   (`ffprobe -count_frames`, muss gleich bleiben) und den Eingriff im Befund nennen.
   Der Re-Encode ist hier unvermeidlich, weil in die Pixel gegriffen wird — deshalb
   `-crf 18` und die bt709-Tags.

5. **Befund ehrlich bewerten:** Untertitel weg + Band ruhig + Gestaltungs-Text heil
   → sauber, weiter. Untertitel weg, aber Leucht-Schlieren → den betroffenen Bereich
   aus dem gesicherten Original zurückkopieren (Verfahren wie 4c) und den Eingriff im
   Befund nennen; überdeckt wird nichts. Bleibt die Schliere danach sichtbar, Viktor
   den Befund mit Crops zeigen statt still durchzuwinken. Untertitel NICHT weg → Task
   einmal neu einreichen;
   liefert Schritt 4b danach dieselben unberührten Fenster, ist es kein Zufall —
   Befund mit Crops UND Sekunden an Viktor, und der englische Rest bleibt stehen
   statt in einen dritten Vmake-Lauf zu gehen.
6. **Weiterverarbeiten je Zweig:**
   - **Quelle bereinigt:** Original sichern als `_work/source_original.mp4`, dann
     `vmake_cleaned.mp4` → `_work/source.mp4`. Frame-Zahl muss stimmen:
     `ffprobe -count_frames -select_streams v:0 -show_entries stream=nb_read_frames`
     gegen Feld `frames` in `_pipeline/sa_config.json` (legt der Bootstrap an).
     Dann den Renderer des Projekts neu laufen lassen: `_pipeline/render<NNN>.py`
     (der Frame-Map-Renderer; liest `_pipeline/cutlist<NNN>.json` — die bleibt gültig,
     weil Frames/fps identisch sind — und schreibt die finale MP4 samt Song-Ton und
     Farb-Tags selbst). Er rechnet auf dem Hetzner-Worker: seine Eingaben
     (`render<NNN>.py`, `cutlist<NNN>.json`, `sa_config.json`, `_work/source.mp4`,
     `../song/song<NNN>.wav`) mit gespiegelter Ordnerstruktur nach
     `/work/kollege/<slug>/` syncen, dort laufen lassen, die finale MP4 sofort
     zurücksyncen (Muster + Erfolgskriterien:
     `.claude/skills/sa-resync-singing-ad/SKILL.md` §Rechenort); meldet das Log
     dort eine fehlende Datei, den genannten Pfad nachsyncen und erneut starten.
   - **Render bereinigt:** Song-Master (`../song/song<NNN>.wav`) als einzige Tonspur
     drübermuxen: `ffmpeg -i _work/vmake_cleaned.mp4 -i ../song/song<NNN>.wav -map 0:v
     -map 1:a -c:v copy -c:a aac -b:a 192k -color_primaries bt709 -color_trc bt709
     -colorspace bt709 -color_range tv -movflags +faststart -shortest <final.mp4>`.
     Der `-shortest`-Mux darf genau 1 Endframe kosten (liegt im Fade-out) — mehr ist
     ein Befund. Farb-Tags dabei NUR auf Container-Ebene (wie im Kommando); den
     Bitstream-Filter `h264_metadata` auf Vmake-Ausgaben NIE anwenden — er scheitert
     an deren SEI-Einheiten und wirft still Pakete weg (gemessen: 6751 statt 8838
     Frames, Datei unbrauchbar).
7. **Abschluss-Beweis:** Frame-Zahl + Dauer per ffprobe; beim Remux-Zweig zusätzlich
   A/V-Sync per Kreuzkorrelation Song↔Mux-Audio an ≥3 Zeitpunkten (soundfile +
   numpy.correlate auf 2-s-Fenstern; Offset ~0 ms erwartet); /watch-Stichprobe an den
   Caption-Stellen aus Schritt 1. Verbrauch buchen: eine Zeile an
   `/root/AWMS/.usage/direkt.jsonl` anhängen, Format:
   `{"ts":"<ISO-Zeit>","workflow":"<Workflow-Name>","anbieter":"vmake","menge":<Anzahl Tasks>,"notiz":"<Kurzbeschreibung>"}`.

## Gotchas

- `remove` mit http(s)-URL überspringt den OSS-Upload — funktioniert nur mit URLs, die
  aus China erreichbar sind. Im Zweifel lokalen Pfad geben.
- Vmake re-encodiert das Video (Dateigröße/Bitrate ändern sich, Frames/fps bleiben) —
  deshalb dem Vmake-Ton nie trauen; der Ton kommt immer aus dem Song-Master.
- Der Scan ist ein VORFILTER: Helligkeit verwechselt Schlieren mit legitim hellen
  Szenen (Produkt-Shots, Fenster) — entscheiden tun die Crops, nie die Zahl allein.
