---
name: vmake-caption-entfernen
description: "Entfernt eingebrannte Captions/Untertitel/Text aus einem Video per Vmake-API (Task videoscreenclear) — inklusive Schlieren-Kontrolle, Song-Remux und ehrlicher Baubarkeits-Bewertung. Nutzen, wenn Viktor sagt „entferne die Captions/den Text aus dem Video", „die englischen Untertitel müssen weg", „nutze Vmake", oder wenn eine Quell-Ad eingebrannten Text trägt, der die deutschen CapCut-Captions stört."
---

# Vmake: eingebrannten Text aus Video entfernen

Zweck: Eingebrannte Captions aus einem Video tilgen, ohne Timing anzufassen. Der
Song/Ton des Projekts bleibt Master: nach einer Render-Bereinigung wird er
drübergemuxt, nach einer Quell-Bereinigung entsteht er ohnehin frisch im Neu-Render.

Werkzeug (ausführen, immer mit `~/.venvs/sa/bin/python3`, Arbeitsverzeichnis =
`_pipeline/`-Ordner des Projekts — dort landet `vmake_state.json`):
`tools/vmake/vmake_client.py` (relativ zum Projektstamm)
Subkommandos: `config` · `remove <datei|url>` · `poll <task_id>` · `download <ziel>`.
`remove` nutzt fest den Task `videoscreenclear`; der Task-Katalog steht in der
`config`-Ausgabe (relevant erst, wenn der Client um weitere Tasks erweitert wird).
Keys: `MT_AK` + `MT_SK` in `~/.config/leichtkraut/.env` (Access + Secret, beide
nötig — SDK-HMAC-SHA256 signiert jeden Request). `VMAKE_AK`/`VMAKE_SK` werden als
Alt-Namen weiter akzeptiert. API-Host ist `wapi-skill.vmake.ai`; das früher hier
genannte `api.vmake.ai` ist eine Altlast mit abgelaufenem Zertifikat — nicht nutzen.
Stand des Clients: `preflight` und `config` laufen geprüft, `remove`/`poll`/`download`
fehlt noch der OSS-Upload (der Client sagt beim Aufruf genau, was fehlt).

## Grenze des Verfahrens: gefuellte Flaechen bleiben als Rueckstand

`videoscreenclear` ist fuer Wasserzeichen und duenne Untertitel gebaut. Ein
**gefuelltes Gestaltungs-Element** — ein roter Titelbalken, ein Preis-Stoerer, ein
Siegel — ueberfordert das Inpainting: Die Buchstaben verschwinden, die FLAECHE
dahinter bleibt als farbiger Keil oder Streifen stehen.

**Gemessen im QUA-001-Lauf:** Der rot-weisse Hero-Titel (0:00–3,5 s, gemessener
Eingriffsbereich x 0–718, y 148–394) hinterliess einen roten Keil bei x 4–485,
y 182–299. Viktors Befund: „die roten Striche muessen auf jeden Fall weg".

Daraus zwei Regeln:

1. **Immer die ERSTEN Frames pruefen, nicht nur eine Stichprobe aus der Mitte.**
   Hero-Titel stehen in Sekunde 0–4 — eine Stichprobe ab Frame 30 sieht sie nie.
   `ffmpeg -i clean.mp4 -vf "select='lt(n,6)',tile=6x1" -vsync 0 erste.png` und ansehen.
2. **Rueckstand unter einem Gestaltungs-Element wird ABGEDECKT, nicht wegretuschiert.**
   Nachtraegliches `delogo` ueber eine grosse Flaeche zerstoert mehr, als es rettet
   (im Lauf getestet: 718x270 loeschte die halbe Animation). Eine ENGE Box um den
   Rueckstand plus leichte Glaettung ist die Obergrenze des Vertretbaren — der Rest
   verschwindet unter dem deutschen Titel, der dort ohnehin hinkommt. Genau deshalb
   ist „Gestaltungs-Text ersetzen" keine Kuer, sondern die Loesung fuer den Rueckstand.

## Vor dem Entfernen: Textsorten trennen

Nicht jeder Text im Bild ist ein Untertitel. Vor dem Vmake-Lauf die Stellen
sichten und in zwei Listen schreiben:

- **Sprech-Untertitel** — klein, unteres Drittel, folgen dem Gesprochenen.
  Werden entfernt; die deutsche Fassung tritt spaeter an ihre Stelle.
- **Gestaltungs-Text** — Hero-Titel, grosse farbige Typo, Preis-Stoerer, Endcard.
  Wird ebenfalls entfernt, aber **er MUSS ersetzt werden** und darf nie einfach
  fehlen. Ohne Ersatz beginnt die Ad mit einem stummen Bild und verliert ihren
  Hook. Die Liste wandert als `_work/gestaltungs-text.md` weiter an die Captions
  (Zeitfenster · Originalwortlaut · Position · deutscher Vorschlag).

Erst danach laeuft `remove`.

## Vorgehen

1. **Caption-Stellen des Originals festhalten:** Schlieren-Scan (Schritt 3) einmal auf
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
   Der Scan dekodiert das ganze Video und rechnet darum auf dem Hetzner-Worker
   (Zugang, `$WORKER_IP`, `<slug>`, Rüstzeug:
   `.claude/skills/sa-resync-singing-ad/SKILL.md` §Rechenort):
   `rsync -az --partial _work/vmake_cleaned.mp4 /Users/yuviktor2004/AWMS/Longform-Singing-VSL-Agent/tools/vmake/schlieren_scan.py root@$WORKER_IP:/work/kollege/<slug>/` →
   `ssh root@$WORKER_IP 'cd /work/kollege/<slug> && /work/kollege/.venv/bin/python3 schlieren_scan.py vmake_cleaned.mp4'`
   (Exit 0 = Band ruhig, Exit 1 = Regionen-Liste als `a–b s`-Zeilen; ImportError im
   Log → fehlendes Paket ins Worker-venv nachinstallieren, siehe §Rechenort
   Rüstzeug). Dann ANSEHEN —
   je auffälliger Region UND je 2–3 Original-Caption-Stellen aus Schritt 1:
   `ffmpeg -ss <Sekunde> -i _work/vmake_cleaned.mp4 -frames:v 1 -vf "crop=iw:ih*0.30:0:ih*0.54,scale=iw*2:ih*2" /tmp/check_<Sekunde>.png`
   und die PNGs mit dem Read-Werkzeug öffnen. So beantwortet EIN Blick beides:
   Text weg? Schlieren da?
5. **Befund ehrlich bewerten:** Text weg + Band ruhig → sauber, weiter. Text weg, aber
   Leucht-Schlieren → Viktor die Wahl zeigen (überdecken lassen / Quelle-zuerst-Weg /
   lokale Nachbearbeitung, als A/B-Varianten) — nicht still durchwinken. Text NICHT
   weg → Task einmal neu einreichen; bleibt er, Befund mit Crops an Viktor.
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
   `/Users/yuviktor2004/AWMS/.usage/direkt.jsonl` anhängen, Format:
   `{"ts":"<ISO-Zeit>","workflow":"<Workflow-Name>","anbieter":"vmake","menge":<Anzahl Tasks>,"notiz":"<Kurzbeschreibung>"}`.

## Das Bild nie unnoetig neu encodieren

Wird dem bereinigten Video nur eine Tonspur zugefuegt, laeuft das Video per
**`-c:v copy`** — Stream-Copy, kein Neu-Encode. Jede zusaetzliche Generation
h264 frisst zuerst die Farbe, und zwar sichtbar an gesaettigten Rot- und
Orangetoenen: sie sind chroma-unterabgetastet (yuv420p) und brechen als Erstes
in Streifen und Saeume auf. Genau da faellt es dem Menschen auf, weil
Schmerz-Glow, Blut und Warnfarben in diesen Ads ueberall vorkommen.

Regel: **Ein Ton-Mux ist kein Grund, das Bild anzufassen.** Nur wenn wirklich
in die Pixel gegriffen wird (Overlay, Crop, Skalierung), wird encodiert — dann
mit `-crf 18` oder besser und immer mit den bt709-Tags auf Container-Ebene.

Gegenprobe vor dem Ausliefern: `ffprobe -select_streams v:0 -show_entries
stream=nb_frames` auf Eingabe und Ausgabe. Gleiche Frame-Zahl UND Stream-Copy =
das Bild ist bitgleich, es KANN keine neuen Artefakte tragen. Das beantwortet
auch die Rueckfrage „kommen die Streifen von Vmake?" ohne Raterei.

## Gotchas

- `remove` mit http(s)-URL überspringt den OSS-Upload — funktioniert nur mit URLs, die
  aus China erreichbar sind. Im Zweifel lokalen Pfad geben.
- Vmake re-encodiert das Video (Dateigröße/Bitrate ändern sich, Frames/fps bleiben) —
  deshalb dem Vmake-Ton nie trauen; der Ton kommt immer aus dem Song-Master.
- Der Scan ist ein VORFILTER: Helligkeit verwechselt Schlieren mit legitim hellen
  Szenen (Produkt-Shots, Fenster) — entscheiden tun die Crops, nie die Zahl allein.
