---
name: sprech-watch
description: "Erzeugt die deutsche Sprechspur einer Speaking-VSL und prüft sie gegen die Zeitfenster — ein durchgehender Take statt isolierter Blöcke, danach an den Sprechpausen geschnitten. Nutzen nach der Lokalisierung, wenn „Sprechspur", „Voiceover", „TTS", „Stimme bauen" fällt."
---

# sprech-watch — die Sprechspur und ihr Prüfer-Loop

## Das Grundgesetz: EIN Take, danach schneiden

**Die ganze Copy wird in EINEM Stück erzeugt — nie Block für Block.**

Warum: Ein TTS-Modell hört nur den Text, den es bekommt. Erzeugt man Block 3 isoliert,
weiß es nichts von Block 2 und 4 — es setzt an, schließt ab, und legt in jeden Block
eine Anfangs- und Schlussmelodie. Das Ergebnis klingt abgehackt: **die Stimme hört
mitten im Gedanken auf, obwohl dort kein Punkt steht.** Genau daran erkennt ein
Muttersprachler sofort die Maschine.

Der Ablauf:
1. **Ein Take** der vollständigen Copy erzeugen. Der Sprechfluss läuft durch, die
   Betonung trägt über Satzgrenzen hinweg.
2. **Sprechpausen messen**, nicht schätzen:
   `ffmpeg -i ganz.mp3 -af silencedetect=noise=-32dB:d=0.18 -f null -`
3. **An den Blockgrenzen schneiden** — die gemessene Pause, die dem erwarteten
   Zeichenanteil am nächsten liegt (Zeichen des Blocks ÷ Zeichen gesamt × Gesamtdauer).
4. **Auf die Zeitmarken legen** (`adelay`). Innerhalb eines Blocks wird der Ton NIE
   angefasst — nur die Stille dazwischen wird gedehnt oder gekürzt.

**Gemessen im QUA-001-Lauf:** Blockweise Erzeugung ergab Viktors Befund „klingt
roboterhaft, hört mitten im Satz auf, man merkt sofort das ist eine KI-Stimme". Der
durchgehende Take derselben Copy mit derselben Stimme klang zusammenhängend.

## Modell zuerst nachsehen, nie annehmen

Vor dem ersten Take die Modell-Liste des Kontos abfragen:
`GET https://api.elevenlabs.io/v1/models` (Header `xi-api-key`) und das neueste
deutschfähige nehmen. Im QUA-001-Lauf lief zuerst `eleven_multilingual_v2`, obwohl
`eleven_v3` im Konto lag — eine ganze Modellgeneration verschenkt, aus reiner Annahme.

Achtung: `eleven_v3` unterstützt `previous_text`/`next_text` **nicht** (HTTP 400,
`unsupported_model`). Das ist kein Problem, weil der EIN-Take-Weg den Kontext
ohnehin von selbst mitbringt — er ist dem Kontextfeld sogar überlegen.

## Der Prüfer-Loop: jeder Block gegen sein Fenster

Je Block Dauer messen und gegen sein Zeitfenster halten. Toleranz 0,25 s.
Die Montage schneidet an den ECHTEN Wortzeiten (Scribe auf dem Take, Grenze =
Mitte der Pause zwischen den Blöcken) — der Zeichen-Anteil ist nur Notbehelf.

**Blockkanten dürfen nie „Vakuum, dann Kante" sein** (Viktors Gate-Befund ARE 001 EL,
„Bruch bei Sekunde 13 und 36", gemessen): Zwischen den Blöcken stand digitale Null
(−180 dB), und der Rand-Trim an einer Stille-Schwelle (−40 dB) hatte den weichen
Stimm-Einsatz mitsamt Atem abgeschnitten (im Take: 200 ms Anlauf von −75 auf −47 dB; in
der Montage: 40 ms von nichts auf −13 dB). Schwellen sind der falsche Hebel — ein Atem
liegt bei −75 dB unter jeder Schwelle. Darum schneidet die Montage an den GEMESSENEN
Wortzeiten: Block = erstes Wort − 150 ms … letztes Wort + 150 ms (innerhalb der
Pausen-Mitten), das erste Wort landet auf der Marke, der Vorlauf liegt davor; je Block
15 ms Ein- und 60 ms Ausblende; ein Grundrauschen auf Take-Niveau (≈ −84 dB) läuft unter
der ganzen Spur. Das Gemini-Ohr erkennt solche Kanten nicht (A/B-blind: alt und neu beide „kein Bruch“) — hier zählt allein die Messung. Prüfung nach jeder Montage (Kanten-Scan): kein 20-ms-Fenster, in dem der
Pegel aus < −90 dB innerhalb von 40 ms um mehr als 30 dB springt.

Die Montage trimmt jeden Block an den Rändern von Stille (der Schnitt liegt in
Pausen-Mitten — ungetrimmt beginnt jeder Block mit halber Take-Pause und der
Stimm-Einsatz verfehlt seine Marke; gemessen: bis 1,2 s tote Luft an Blockgrenzen).

**Atem-Reserve — Blöcke dürfen nicht kleben.** Das Gegenteil der toten Luft ist
genauso ein Befund: Endet ein Block exakt dort, wo der nächste auf seiner Marke
einsetzt, hört Viktor die Sätze „überlagert" — kein Absatz, kein Atem, die Stimme
rennt durch. Darum rechnet die Montage mit `--atem` (Default 0,45 s): Jeder Block außer dem
letzten muss so viel Luft zwischen seinem letzten Wort und der nächsten Marke
lassen; sein Fenster für die Längen-Leiter ist `Marke_nächste − Marke_eigene − atem`.
In diese Luft ragen die Atem-Ränder der Blöcke (`--nachlauf` 0,20 s hinter dem
letzten Wort, `--vorlauf` 0,30 s vor dem ersten Wort des Folgeblocks) — sie sind
leise (Atem, kein Wort), darum bleiben gemessen ~0,35 s hörbare Stille übrig,
nicht 0,45 − 0,50. Der
Prüfer misst die Kante nach (Stille ≥ 0,25 s vor jeder Marke), ein Verstoß ist SPUR
ROT „Blöcke kleben".

**Tempo — die Stimme darf nicht schleichen.** v3 spricht Werbe-Copy in Ruhelage
gemächlich (~2,0 W/s bei deutschen Stimmen); eine so gebaute Spur klingt monoton,
obwohl jede Zeile stimmt. Die Montage hebt darum den GANZEN Take gleichmäßig an
(`--tempo`, Default und Obergrenze 1,12; Messung und Montage laufen mit demselben
Wert) — gleichmäßig, weil ein Lift über den ganzen Take die Prosodie erhält,
während Sprünge je Block nach Schnitt klingen. Das gilt zusätzlich zur
Längen-Leiter je Block; die Übersetzung rechnet ihr Budget mit diesem Lift (Skill
`speaking-vsl-uebersetzung`, Abschnitt Das Budget). Über 1,12 wird aus Tempo Hetze
— klingt die Spur am Gate dann noch zu langsam, ist die Copy zu lang, nicht das
Tempo zu niedrig.

**Daumenregel Bild ↔ Stimme:** Passt ein Block nicht in sein Bild, wird die STIMME
schneller, nicht der Clip langsamer — Tempo-Lift und Pausen-Quetsche kommen vor
jeder Clip-Dehnung, und eine Clip-Dehnung ist nie der Standardweg. Grund: Ein
gedehnter Clip sieht sofort nach Zeitlupe aus, ein um zehn Prozent schnellerer
Sprecher klingt nur wach. Gilt, bis Viktor für einen Lauf ausdrücklich das
Gegenteil sagt.

**Stimm-Vergleich auf Zuruf (Varianten-Lauf):** Sagt Viktor „zwei Stimmen" oder
„teste Stimmen", laufen n Stimmen je als EIGENE Spur durch dieselbe Kette — Take,
Montage, Prüfer, Render, Abnahme, Captions, CapCut-Paket. Stimmen kommen aus dem
Casting-Trichter (`speaking-vsl-stimm-casting`, Band 25–35 %), nie aus dem Bauch.
Ablage je Variante mit Stimm-Slug (Kleinbuchstaben, Bindestriche): `_work/take_<slug>.mp3`,
`_work/sprechspur_<slug>.wav`, `_pipeline/marken_<slug>.json`, `_pipeline/pruefer_<slug>.json`,
`_work/final_<slug>.mp4`, `_pipeline/captions<NNN>_haeppchen_<slug>.json`,
`_capcut-paket-<slug>/` (Aufruf `tools/sp/capcut_paket.py --stimme "<Name>"`) mit
CapCut-Name `<Projektname> (Stimme <Name>)` — so erkennt Viktor im CapCut-Projekt,
welche Stimme er hört. Die Prüfer-Tabellen aller Varianten liegen der Sichtung bei;
die gewählte Stimme kommt danach ins Stimmen-Register.

**Jede Variante ist ein eigenes Projekt mit eigener Nummer.** Zwei Ads unter einem
Projektnamen kollidieren überall dahinter — Export-Zuordnung im Ripping Sheet,
Anzeigengruppen-Name bei Meta, upload.json, Archiv. Darum bekommt jede Variante
VOR dem Sprechspur-Bau ihr eigenes Projekt in `datenbanken/sp-projekte/`: die erste
Variante behält die Auftragsnummer, jede weitere zieht die nächste freie EL-Nummer
(frei in sp-projekte UND unter `brands/<Brand>/`); alle tragen den Zusatz
`(Stimme <Name>)` im Projektnamen — `ARE 012 EL | 08.09.2026 (Stimme Darinka)`,
`ARE 013 EL | 08.09.2026 (Stimme Tia Mirza)`. Die karte.md der Folge-Varianten trägt
`variante-von: <erstes Projekt>` und `stimme: <Name>`; die gemeinsame Vorstufe
(Transkript bis Custom-Clips) wird nicht neu gerechnet, sondern aus dem ersten
Projekt übernommen (Pipeline-Ordner `<NNN> EL` je Variante, Kopie von `_work/` und
`_pipeline/` des ersten). Damit heißt das Paket wieder `_capcut-paket/`, der
CapCut-Name ist der Projektname, und der Export des Mac trägt automatisch die
richtige Nummer. Der Stimm-Slug-Weg oben (`--stimme`) bleibt nur für Läufe, die
schon vor der Projekt-Anlage gebaut wurden.

**Marken nach gemessener Dauer, nicht nach Wortzahl.** v3 würfelt die Pace je Take
um ±10 % (ein Take mit weniger Wörtern kann länger sein); Marken aus dem Wortanteil
treffen die echte Dauer nicht, und die Montage bricht an einem Block mit ×1,16 ab.
Darum vor der Montage messen und planen — führe aus (CWD = Pipeline-Ordner,
Pfade der Werkzeuge vom Projektstamm `/root/AWMS/Longform-Singing-VSL-Agent`):
1. Vorläufige `_pipeline/marken.json` aus der final-Copy schreiben — je Block eine
   Zeile `{"start": <Sekunde des (M:SS)-Stempels>, "ende": <Start des Folgeblocks>, "text": "<Copy-Zeile ohne Tags>"}`,
   letztes `ende` = Videolänge (`dur` aus `_pipeline/sp_config.json`).
2. `~/.venvs/sa/bin/python3 tools/sp/sprechspur.py montage --take _work/take.mp3 --marken _pipeline/marken.json --tempo 1.12 --nur-messen --messung _pipeline/messung.json`
3. `~/.venvs/sa/bin/python3 .claude/skills/sprech-watch/scripts/marken_planen.py _pipeline/messung.json _pipeline/marken.json`
4. `~/.venvs/sa/bin/python3 tools/sp/sprechspur.py montage --take _work/take.mp3 --marken _pipeline/marken.json --tempo 1.12`
Der Planer schreibt die Marken in `_pipeline/marken.json` (Texte bleiben) und nennt
den nötigen Block-atempo; Exit 1 = über 1,15 → Copy kürzen ist Viktors Gate-Frage
(Skill `speaking-vsl-uebersetzung`, Kürzungs-Leiter Stufe 6). Ist der Bedarf
KLEINER als die Videolänge, dehnt der Planer nichts — die Restluft landet hinter
dem letzten Block als Ausklang; mehr als 1,0 s Restluft heißt: Copy ist zu kurz
(Unterlängen-Befund im Lauf-Bericht, Viktor entscheidet, ob eine Zeile wächst).
Das gilt für Voice-over ohne Lippen-Sync; muss eine Zeile auf einem Lippen-Clip
sitzen, wird ihre Marke NACH dem Planer von Hand auf den Clip-Start gesetzt und
die Nachbarn entsprechend verschoben.

**Schnittkanten sind Anker, keine Verhandlungsmasse.** Ein Block, der im Original
auf einer Schnittkante beginnt (Stempel der Copy-Zeile liegt höchstens 0,25 s neben
einem `t0` der Clip-Karte), behält diese Kante als Marke — der Zuschauer hört den
neuen Gedanken mit dem neuen Bild. Vorgezogen klingt der Block abrupt: er beginnt
über dem alten Bild, und die Pause davor ist auf digitale Stille geschrumpft.
Wandern dürfen nur Marken, die im Original mitten in einem Clip liegen (B-Roll
ohne Kante). Darum liest der Planer die Clip-Karte
(`marken_planen.py … --kanten _pipeline/clip_karte.json`): Kanten-Marken bleiben
fest, die Blöcke dazwischen bekommen ihre gemessene Dauer und den Atem, und wo die
Copy nicht in ihr Kanten-Fenster passt, meldet der Planer den nötigen atempo je
Abschnitt — über 1,15 heißt: diese Zeile kürzen (Gate-Frage), nicht die Kante
lösen. Bleibt vor einer Kante Luft, ist sie Atem, keine tote Luft: bis 1,0 s ist
sie erlaubt, darüber dehnt der Vorblock (Längen-Leiter) oder die Zeile wächst.

Längen-Leiter (in dieser Reihenfolge, die Montage fährt sie selbst):
| Fall | Mittel |
|---|---|
| Überlänge 1 | **Pausen quetschen** — Stille > 0,4 s auf 0,32 s (silenceremove); v3 legt mit Tags theatralische Pausen, die Wörter bleiben unberührt |
| Überlänge 2 | `atempo` bis 1,10 — hört niemand; bis 1,15 nur bei ruhigen Blöcken |
| Überlänge 3 | **Copy kürzen und neu erzeugen** — Tempo darüber klingt gehetzt |
| UNTER-Länge (> 0,6 s Luft vor der nächsten Marke) | **sanft dehnen** bis atempo 0,94 (nie beschleunigen, leicht verlangsamen ist das Werkstatt-Gesetz); ~0,5 s bleiben als Absatz-Atem |

Der Prüfer hört zusätzlich auf SPUR-Ebene: tote Luft > 1,0 s zwischen den Blöcken
(vor einer Schnittkante) bzw. > 0,8 s (mitten im Clip), klebende Blöcke (keine
Stille ≥ 0,25 s vor einer Marke), Stimm-Einsatz ± 0,3 s neben seiner Marke,
Kanten-Treue (jede Kanten-Marke aus der Clip-Karte liegt auf ihrer Kante ± 0,25 s),
und Stimm-Identität über die ganze Spur
(Gemini-Ohr: same_speaker + Wechsel-Sekunde) — Block-GRÜN allein ist kein FERTIG.

Betonungs-Regel dazu: GROSSSCHREIBUNG lässt v3 jede Stelle zelebrieren und kostet
messbar Zeit — höchstens 1–2 Wörter je Copy in Caps, den Rest trägt die
Emotions-Delivery der Tags.

## Abschluss-Prüfung

- Jeder Block startet exakt auf seiner Zeitmarke (durch `adelay` garantiert, nicht
  nachträglich zu messen).
- Gesamtpegel `loudnorm=I=-16:TP=-1.5` — Social-Plattformen normalisieren sonst selbst.
- Keine Überlappung: Blockende + Startmarke des nächsten prüfen.

## Werkzeug und Emotions-Tags

Die Ausführung läuft über `tools/sp/sprechspur.py` (CWD = Pipeline-Ordner):
`stimme <KÜRZEL>` holt die Brand-Stimme aus dem Register (leer → erst Casting),
`take` erzeugt den EINEN Take, `montage` schneidet an den gemessenen Pausen und
legt die Blöcke per adelay auf ihre Marken, `woerter` schreibt den Wort-Cache
für die Captions (Scribe, de).

Der Take läuft mit v3 und `--stability 0.25` (lebendig; 0,5 klingt sauber, aber
monoton — Gate-Befund). Zahlen stehen im Take-Text ausgeschrieben, und kein Block
beginnt mit einem Zahlwort (die Montage schneidet sonst in die Zahl).
Der Take-Text entsteht aus der finalen Copy PLUS den v3-Audio-Tags aus
`_pipeline/emotions_karte.json`: Welche Tags an welche Wendepunkte gehören, sagt
allein `.claude/skills/speaking-vsl-emotionskarte/SKILL.md` (Abschnitt Tags setzen)
— eine Spur mit einem einzigen Tag hört Viktor als monoton. Betonung per
GROSSSCHREIBUNG bleibt sparsam (1–2 Wörter je Copy). Die final-Datei im
Projekt-Ordner bleibt tag-frei — Tags leben nur im Take-Text (`_pipeline/take.txt`).

## Der Prüfer ist ein Werkzeug, danach steht ein Gate

`tools/sp/pruefer.py --audio _work/sprechspur.wav --marken <marken.json>` hört
maschinell ab: Rück-Transkription gegen die Soll-Copy (Versprecher, Doppelwörter,
Auslassungen), Pausen > 0,8 s mitten im Block, Fensterzeiten, dazu das
Anker-kalibrierte Gemini-Ohr (Aussprache, Artefakte, Roboter-Stellen). Exit 1 =
rote Zeile → NUR diese Stelle neu erzeugen (Take-Würfel mit gleichem Text und
Tags, an den Pausen der Nachbarblöcke einsetzen), höchstens 3 Versuche, dann
Befund an Viktor.

Nach GRÜN stoppt der Lauf am **Übergangs-Gate Sprechspur-Abnahme**: die Blöcke
als bildboard-Links im Chat zeigen (je Block ein Link + die Prüfer-Zeile),
Viktor hört und sagt „passt" oder gibt Befund je Block. Jeder Befund läuft als
/feedback in den Prüfer oder die Bausteine davor — das Gate trainiert den
Prüfer und fällt weg, sobald mehrere Läufe in Folge ohne Viktor-Befund
durchgehen. Bis dahin geht KEIN Lauf ohne dieses Gate in den Schnitt.
