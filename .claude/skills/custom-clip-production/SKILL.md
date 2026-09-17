---
name: "custom-clip-production"
description: "Ersetzt die Produkt-Clips einer Resync-Ad (Competitor-Branding) durch neu animierte Custom Clips mit dem eigenen Produkt der laufenden Brand-Linie — Frame-Edit + Kling-Kette + Schnitt auf Originallänge + Handlungs-Prüfer. Nutzen, wenn Viktor sagt „Custom Clips", „Produkttausch", „ersetz das Produkt in den Clips", „rebrand die Clips" — oder wenn die Clip-Karte eines Laufs Clips mit sichtbarem Produkt markiert hat. Auch ohne diese Wörter nutzen, sobald eine fertige oder laufende Rip-Ad Competitor-Packaging zeigt, das nicht mehr ausgespielt werden darf (Rebranding, DMCA)."
---

# Skill — Custom-Clip-Production (Produkt-Clips rebranden)

Eine Resync-Ad übernimmt die Clips der Competitor-Quelle 1:1 — auch die Clips, in
denen das Competitor-Produkt samt Marke zu sehen ist. Dieser Skill ersetzt genau
diese Clips durch neu animierte Custom Clips mit unserem Produkt, ohne den Rest
der Ad anzufassen. Ein Custom Clip ist gelungen, wenn er (a) unser Produkt mit
lesbarem Markennamen zeigt, (b) alle Handlungen des Original-Clips enthält und
zu Ende führt und (c) exakt die Länge des Original-Clips hat.

## 1. Eingang: markierte Clips aus der Clip-Karte

Die Clip-Karte (`.claude/skills/singing-vsl-clip-karte/SKILL.md`) markiert beim
Kartieren jeden Clip, in dem das Produkt oder seine Verpackung sichtbar ist.
Ablage der Markierung: `[projekt]/_work/clips/custom_clips.json` — eine Zeile je
markiertem Clip:

```json
{"clip": 285, "t0": 570.08, "t1": 572.17, "dauer": 2.08, "form": "sachet", "grund": "Sachet frontal in die Kamera, Logo gross lesbar", "referenzbild": "<brandDb>/Product Reference/<referenz-datei>"}
```

`referenzbild` ist Pflicht in JEDER Zeile: der volle Pfad der Referenz-Datei, die
laut Steckbrief zur `form` gehört. Jeder Edit läuft gegen genau dieses Bild, und
sein Label wird wortwörtlich kopiert — ohne das Feld in der Zeile greift beim
Produzieren irgendwann ein Edit auf ein beschriebenes statt gezeigtes Design
zurück, und die Labels driften (erfundene Zweitzeilen, Schreibvarianten).

`form` sagt, welche Gestalt das Produkt in diesem Clip hat — sie entscheidet,
welche Referenz-Datei in den Edit geht. Zwei Werte gelten für jede Brand:
`screen` = das Produkt erscheint auf einem Bildschirm im Bild (Shop-Seite, Handy),
`sonstiges` = alles, wofür der Steckbrief keine Referenz hat (z. B. Produkt-Berg
im Hintergrund).

Alle übrigen Werte sind **produktform-Namen der jeweiligen Brand** und stehen in
ihrem `produkt-steckbrief.md` (Abschnitt 2) — z. B. `sachet` und `dose` bei einer
Masken-Brand, `flasche` bei einer Kapsel-Brand. Beim Kartieren nur Werte
verwenden, die der Steckbrief kennt; passt nichts, ist es `sonstiges`.

Fehlt `custom_clips.json`, die Clip-Karte des Projekts einmal durchgehen
(Beschreibungs-Feld `bild` nach Verpackungs-Wörtern rastern, Treffer mit eigenen
Augen am Frame verifizieren) und die Datei schreiben — erst dann produzieren.

`screen`-Clips (Shop auf einem Bildschirm): Nennt der Produkt-Steckbrief der
Linie (Abschnitt Referenzen) eine Shop-Referenz, wird der Screen-Inhalt damit auf
den eigenen Shop umgebaut — gleiche Edit-Kette wie beim Produkt. Fehlt die
Shop-Referenz, den Clip NICHT produzieren, sondern als offenen Punkt in den
Lauf-Bericht an Viktor. `sonstiges`-Clips immer als offener Punkt an Viktor.

## 2. Referenzen: welches Produktbild in den Edit geht

Dieser Skill gilt für jede Markt-Brand-Linie. Welches Produkt hineingehört, sagt
**die Linie des Laufs**, nie dieser Skill — sonst trägt eine Ad die Marke einer
fremden Brand.

**Die Brand ermitteln (drei Schritte, in dieser Reihenfolge):**

1. Kürzel der Linie aus dem Auftrag nehmen (z. B. `QUA`, `RES`, `ROV`) — es steht
   im Projektnamen `KÜRZEL NNN | DATUM`.
2. In `Longform-Singing-VSL-Agent/datenbanken/linien/linien.json` den Eintrag
   dieses Kürzels lesen. Das Feld `brandDb` nennt die Brand-Datenbank, z. B.
   `datenbanken/brand-resilia`. Diese Datenbanken wohnen im Stamm-Projekt, also
   unter `/root/AWMS/`.
3. Referenz-Ordner ist damit `/root/AWMS/<brandDb>/Product Reference/`.

**Der Steckbrief ist die Marken-Wahrheit.** In diesem Ordner liegt
`produkt-steckbrief.md`: Wortmarke, Referenz-Datei je `form`, die
Verpackungs-Beschreibung für den Edit-Prompt und der Render-Stil. Er wird VOR dem
ersten Edit gelesen — die Prompt-Vorlage in Abschnitt 4 füllt sich aus ihm.

**Fehlt der Steckbrief oder ist der Ordner leer:** STOPP, nichts improvisieren,
keine Referenz einer anderen Brand ausleihen. Viktor melden, dass die Linie noch
kein Custom-Clip-Onboarding hatte (`.claude/skills/custom-clip-onboarding`).

Die Referenz-Datei ist die Wahrheit für Farben, Layout und Produktsymbol. Details,
die die aktuelle Verpackung trägt, die Referenz-Datei aber nicht zeigt, stehen als
Text im Steckbrief und wandern zusätzlich in den Edit-Prompt; bei Widerspruch
zwischen Datei und Text gewinnt die Datei. Liegt im Ordner eine neuere
Referenz-Fassung, die alte ersetzen — nie zwei Fassungen derselben Form
nebeneinander liegen lassen.

## 3. Handlungs-Inventar des Originals (Pflicht vor jeder Produktion)

Je markiertem Clip den Original-Clip als Frame-Streifen ansehen (8+ Frames über
die volle Länge) und ALLE Handlungen auflisten:

- **Gestik:** Hände — was tun sie, wann (hält, hebt, zeigt, öffnet, übergibt)
- **Mimik:** Gesichtsbewegung als Bogen (lächelt → wird ernst; Augen zu → auf)
- **Objekt:** was das Produkt selbst tut (steht, wird gedreht, wird geöffnet)
- **Kamera:** statisch, Push-in, Schwenk

Das Inventar ist die Prüf-Checkliste des Prüfers (Schritt 7). Gesetz: Jede
Handlung des Originals muss im Custom Clip vorkommen und ZU ENDE geführt werden —
ein angefangenes Lächeln endet als Lächeln, eine Zeigegeste kommt beim Ziel an.

## 4. Frame-Bau (NUR der Start-Frame)

Jeder Custom Clip wird aus GENAU EINEM bearbeiteten Frame gebaut: dem
Start-Frame des Original-Clips. Es gibt keinen End-Frame-Edit — zwei
unabhängig editierte Frames rendern das Label leicht unterschiedlich, und
Kling morpht dann sichtbar zwischen den Layouts („das Logo baut sich um").
Ein einziger Quell-Frame macht das Label über den ganzen Clip stabil.

Gesetze für den Edit:

- **NUR das eigene Produkt.** Rebrandet wird ausschließlich das Produkt, das der
  Steckbrief der Linie beschreibt. ALLE anderen Objekte bleiben unangetastet —
  auch andere Produkte, die die Competitor-Marke tragen. Solche Stellen nicht
  eigenmächtig umlabeln, sondern als Befund in den Lauf-Bericht an Viktor.
- **Position exakt.** Das Produkt bleibt an Position, Größe und Winkel des
  Original-Frames — ein am Bildrand angeschnittenes Produkt bleibt
  angeschnitten.

1. **Frames ziehen** aus der Caption-freien Arbeitsquelle des Projekts
   (`[projekt]/_work/vmake_cleaned.mp4`; fehlt sie, erst
   `.claude/skills/vmake-caption-entfernen/SKILL.md` laufen lassen):
   Start = erster Frame des Clips; Ende = **0,3 s VOR der Schnittkante**
   (`ffmpeg -sseof -0.30`) — direkt an der Kante erwischt man den ersten Frame
   des Folge-Clips. Beide Frames ansehen und bestätigen, dass sie dieselbe Szene
   zeigen; zeigt einer eine fremde Szene, liegt der Griff an/hinter der Kante —
   weiter von der Kante weg neu greifen.
2. **Den Start-Frame editieren** — nur ihn; der End-Frame diente in Schritt 1
   allein der Szenen-Kontrolle und wird nie editiert (siehe Absatz oben: es gibt
   keinen End-Frame-Edit). Modell **Nano Banana 2** über kie.ai:

   ```
   python3 tools/sa/kie_bild.py edit \
     --frame    <projekt>/_work/clips/c<NNN>_start.png \
     --referenz <brandDb>/Product\ Reference/<referenz-datei aus dem Steckbrief> \
     --prompt-datei <projekt>/_work/clips/c<NNN>_edit.txt \
     --resolution 1K \
     --out      <projekt>/_work/clips/c<NNN>_start_rebrand.png
   ```

   Referenz (1) = der Original-Frame, Referenz (2) = die Tier-1-Produktreferenz —
   **Teil-Ersatz:** Zeigt ein Clip das Produkt erst ab der Mitte (Hand greift in die
   Tasche, Beutel taucht auf), wird nur der Teil ab dem ersten Produkt-Frame ersetzt —
   davor ist kein Fremd-Branding im Bild, das Original bleibt. `custom_clips.json`
   bekommt dann zusätzlich `t_ersatz` (Sekunde des ersten Produkt-Frames).

   **Teilweise sichtbares Produkt (lugt aus einer Tasche, von Fingern verdeckt):** die
   Vollbeschreibungs-Vorlage unten NICHT benutzen — das Modell „vervollständigt" das
   Produkt, zieht es heraus, vergrößert es (gemessen: zwei Fehlversuche, erst die
   Minimal-Fassung saß pixelgenau). Stattdessen den Edit als kleinste Änderung
   formulieren: den sichtbaren Bereich beschreiben, Form/Größe/Neigung/Griff als
   unveränderlich benennen, und NUR die Buchstaben der Wortmarke tauschen.
   in genau dieser Reihenfolge, denn die Prompt-Vorlage sagt „the first image"
   und „the second image". Das Werkzeug lädt beide hoch, ruft `nano-banana-2`
   mit `9:16` auf und legt das Ergebnis unter `--out` ab. **Auflösung immer die
   niedrigste Stufe: `--resolution 1K`** — Ziel ist ein 716×1284-Frame, 2K und 4K
   kosten mehr und werden ohnehin heruntergerechnet. Der Standardwert des Werkzeugs
   ist 2K, die Stufe gehört also in jeden Aufruf. Prompt-Vorlage
   (bewährt, nur die Produktform-Details austauschen):

   > Edit the first image. Keep EVERYTHING pixel-identical - the person, their pose,
   > hands, face, hair color, clothing, the background room, lighting, camera
   > angle and crop stay exactly as in the first image. ONLY change the
   > <PRODUKTFORM>: it currently reads '<COMPETITOR-BESCHRIFTUNG>' - remove that
   > branding completely and rebrand it to match the product in the
   > second image: <VERPACKUNGS-BESCHREIBUNG>. Render the rebranded
   > <PRODUKTFORM> in the same <RENDER-STIL> as the rest of the image. Keep its
   > exact position, size, tilt and the fingers gripping it. The word
   > '<WORTMARKE>' must be clearly legible. Do not invent a new room or new pose -
   > the scene stays exactly as in the first image. Do not add captions or any
   > other text.

   Die Platzhalter kommen aus zwei Quellen — nie aus dem Gedächtnis:

   | Platzhalter | Quelle |
   |---|---|
   | `<WORTMARKE>`, `<VERPACKUNGS-BESCHREIBUNG>`, `<RENDER-STIL>` | `produkt-steckbrief.md` der Linie (Abschnitt 2) |
   | `<PRODUKTFORM>` | Feld `form` des Clips aus `custom_clips.json` |
   | `<COMPETITOR-BESCHRIFTUNG>` | was im Original-Frame wirklich auf dem Produkt steht — am Frame ablesen |

   So sieht die ausgefüllte Vorlage für ein Sachet aus (Linie QUA):

   > Edit the first image. Keep EVERYTHING pixel-identical - the woman, her pose,
   > hands, face, hair color, clothing, the background room, lighting, camera
   > angle and crop stay exactly as in the first image. ONLY change the pink
   > sachet: it currently reads 'Quasi' and 'Collagen Glow Up Mask' - remove that
   > branding completely and rebrand the sachet to match the product in the
   > second image: light-pink sachet, large dark-pink vertical wordmark 'Areum'
   > along the left edge reading bottom-to-top, a small thin vertical line
   > 'GLASS SKIN RITUAL' in spaced letters beside the wordmark, a white 3D sheet
   > mask illustration, headline 'Kollagen-Glow-up-Maske' in dark pink. Render
   > the rebranded sachet in the same warm Pixar 3D cartoon style as the rest of
   > the image, NOT photoreal. Keep the sachet's exact position, size, tilt and
   > the fingers gripping it. The word 'Areum' must be clearly legible. Do not
   > invent a new room or new pose - the scene stays exactly as in the first
   > image. Do not add captions or any other text.

   Andere Edit-Modelle nicht verwenden: `nano_banana_pro` driftet bei Identität
   (Haarfarbe) und Komposition, `flux_kontext` verhunzt die Wortmarke.
3. **Ergebnis-Beleg:** Das Werkzeug legt neben jeder Ausgabe ein
   `<out>.job.json` ab — das ist der Beleg, den der Lauf-Bericht zitiert. Darin
   zählt NUR `resultJson.resultUrls[]`; die URLs, die du in `image_input` bzw.
   `image_urls` geschickt hast, sind das Echo der EIGENEN Uploads (wer die nimmt,
   lädt sein Eingabebild herunter und hält es für das Ergebnis). Die Upload-Links
   sterben nach 24 Stunden — die Wahrheit ist immer die lokale Datei unter
   `--out`, nie ein kie.ai-Link.
4. **Frame-QA in voller Auflösung:** Markenname lesbar? Genau EIN Produkt?
   Pose/Raum/Person unverändert? Wirkt etwas halluziniert, ZUERST den
   Original-Frame ansehen — was dort schon steht, ist kein Modell-Fehler.
   Durchgefallene Frames einzeln neu würfeln (gleicher Prompt), nicht die
   ganze Kette.

## 5. Animation (Kling, nur Start-Frame)

Modell **Kling 3.0** über kie.ai, NUR das Startbild = der bearbeitete
Start-Frame (es gibt bewusst kein Endbild):

```
python3 tools/sa/kie_bild.py animate \
  --startbild <projekt>/_work/clips/c<NNN>_start_rebrand.png \
  --prompt-datei <projekt>/_work/clips/c<NNN>_kling.txt \
  --sekunden <ziel aufgerundet, min. 3> \
  --out <projekt>/_work/clips/c<NNN>_roh.mp4
```

**Ausnahme — zweites Bild als Ziel-Frame (`--endbild`):** Zeigt der Start-Frame das
Produkt nicht vollständig (Teil-Ersatz) oder soll das Produkt nachweislich an seinem
Platz bleiben, wird der END-Frame des Original-Clips ebenfalls umgebrandet und als
zweites Bild mitgegeben. Das widerspricht der Nur-Start-Frame-Regel nicht: Dort ging es
um zwei getrennte Edits DESSELBEN vollen Labels, die gegeneinander morphen — hier
zeigen beide Frames dieselbe Gestaltung (Teil und Ganzes). Gemessen: ohne Endbild
animierte Kling den verdeckten Label-Rest als leere Fläche; mit Endbild kam das Produkt
mit vollem Label heraus, und ein Beutel, der sonst hochgehoben wurde, blieb unten.

Das Werkzeug setzt `mode: std`, `aspect_ratio` aus dem Startbild und `sound: false`. Im
`<out>.job.json` nachsehen, dass `sound` wirklich `false` ist — sonst wurde Audio
mitbezahlt, das diese Kette nie braucht (der Ton kommt aus dem Song). Auch hier gilt die
niedrigste Stufe: `mode: std`, nie `pro` oder `4K` — das Ziel ist 720×1280, höhere Stufen
zahlen für Pixel, die der Schnitt wegwirft. Gegenprobe am FERTIGEN Clip statt nur im
Job-JSON: `ffprobe` muss null Audiostreams zeigen; liegt eine Tonspur drin, wurde Audio
mitbezahlt.

- **Dauer:** ganze Sekunden, Minimum der API ist 3. Generiert wird die
  Ziel-Länge AUFGERUNDET auf die nächste ganze Sekunde, mindestens 3
  (Ziel 1,4 s → 3 s; Ziel 3,3 s → 4 s). Der Überschuss wird in Schritt 6
  abgeschnitten, nie das Tempo verzerrt.
- **Prompt — die Handlungen müssen VOR die Schnittkante:** alle Handlungen aus
  dem Inventar (Schritt 3) so ansetzen, dass sie innerhalb der ZIEL-Länge
  abgeschlossen sind — ausformulieren als „within the first ~X seconds", zügiges
  natürliches Tempo, keine Zeitlupe. Kling legt Aktionen von sich aus in die
  erste Clip-Hälfte (Front-Loading) — bei dieser Methode ist das erwünscht.
- **Gegen Erfindungen:** Ohne End-Frame halluziniert Kling gern an auffälligen
  Objekten. Immer dazu: „the sachet stays exactly as in the source image, label
  text crisp and unchanged, no new objects appear". Sprechende Person: wörtliche
  englische Original-Zeile aus der Clip-Karte (Mundbewegung), Regeln in
  `.claude/skills/prompt-patterns-kling/SKILL.md`.

## 6. Schnitt auf Originallänge (natürliches Tempo, nie Zeitraffer)

```
ffmpeg -i roh.mp4 -t <ziel_dauer> -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24" -c:v libx264 -crf 18 -an ziel.mp4
```

Abspielgeschwindigkeit bleibt 1,0× — kein setpts, kein Stauchen (doppeltes
Tempo auf 1,5-s-Clips sieht hektisch aus, deshalb wurde die Tempo-Methode
verworfen). Geschnitten wird HINTEN; ob die Handlungen das Schnittfenster
überlebt haben, entscheidet allein der Prüfer (Schritt 7) am GESCHNITTENEN
Clip. Immer crop-to-fill auf 720×1280 (Kling liefert 716×1284), nie Balken.

## 7. Prüfer-Loop (am fertigen Clip, nicht an der Rohware)

Vom FERTIGEN, getempten Clip einen Frame-Streifen ziehen und gegen die
Checkliste prüfen — jede Zeile TRUE/FALSE, keine Geschmacksurteile:

1. Jede Handlung des Inventars vorhanden UND zu Ende geführt?
2. Markenname im bewegten Bild lesbar UND Label-Design über den ganzen Clip
   stabil (kein Morphen zwischen zwei Layouts)?
2b. Nichts außer dem eigenen Produkt verändert (Nebenprodukte, Requisiten und
   ihre Beschriftungen identisch mit dem Original)?
3. Produktanzahl = Original (zeigt das Original zwei Sachets, hat der Custom Clip
   exakt zwei — nie mehr, nie weniger)?
4. Person/Szene konsistent mit dem Original (gleiche Frau, gleicher Raum)?
5. Länge = Original-Clip (±1 Frame bei 24 fps)?

Ein FALSE → Ursache benennen, Prompt gezielt nachschärfen (nur die betroffene
Klausel), neu generieren. Maximal 3 Versuche je Clip; danach den Clip mit
Befund (welche Zeile scheitert woran) in den Lauf-Bericht schreiben und Viktor
entscheiden lassen — nie einen durchgefallenen Clip stillschweigend einbauen.

## 8. Ablage und Abschluss

- Arbeitsordner: `[projekt]/_custom-clips/` mit `01-frames/` (Original + Edits),
  `02-roh/` (Kling-Rohclips), `03-final/` (getempte Clips, benannt
  `c<NNN>-custom.mp4`), `pruefer.md` (Checklisten-Ergebnis je Clip).
- Sichtung: je Clip ein Vergleichsvideo Original|Custom (hstack, EIN Durchlauf,
  kein Loop) über das Bildboard (`bild <datei>`) an Viktor — ersatzweise der
  fertige Clip bzw. Rebrand-Frame als Datei im Chat.
- **HARTES GATE: Die Custom Clips ersetzen ihre Original-Gegenstücke erst NACH
  Viktors Go.** Einbauen ohne gezeigten Clip ist ein Regelbruch, keine
  Abkürzung — auch spät im Lauf, auch wenn der Prüfer grün ist: Der Prüfer
  misst Handlungen und Lesbarkeit, aber ob das Label wie SEIN Produkt aussieht,
  beurteilt nur Viktor. Ein übersprungenes Go wurde gemessen erst in der
  fertigen Ad entdeckt und kostete den Re-Fix eines ganzen Einbau-Laufs.
- Kosten: beide Etappen laufen über das kie.ai-Guthaben, aus dem auch Suno und
  das Maschinen-Ohr bezahlt werden — ein Custom-Clip-Lauf über zehn Clips zieht
  also am selben Konto wie der Song-Bau. Vor großen Läufen den Stand im kie.ai-
  Konto ansehen und in den Lauf-Bericht schreiben; der Preis je Aufruf steht am
  Modell im kie.ai-Market und wird nicht hier festgeschrieben, weil er sich ändert.

## 8b. Endcards: Gestaltungs-Karten sind Videos, keine Standbilder

Die Endcard einer Quelle ist fast immer animiert (schwebende Kapseln, Lichtstreifen,
Glow auf dem Button, zum Schluss fliegt das Produkt auf die Kamera zu). Eine Solena-Karte,
die als Standbild über das ganze Fenster steht, fällt sofort auf — Viktor hat genau das
moniert. Darum wird die Endcard in DREI Schritten gebaut, nie nur als Bild:

1. **Karte als Standbild** per Nano-Banana-Edits aus der Original-Endcard (Headline,
   Badges, Button, Beutel — Angebot laut Brand-DB). Dazu ein **Zoom-Endbild**: gleiche
   Karte, der Beutel 1,6–1,8× größer, leicht zur Kamera gekippt, alles andere
   pixelidentisch (Edit-Prompt: „only change the pouch … has floated closer").
2. **Zwei Kling-Clips, je bis 15 s, Modus `pro`:**
   - Schweben: **nur Startbild** (Start = Ende = Karte friert Kling ein — gemessen:
     Bewegungsmaß 0,23, weniger als ein zoompan-Standbild), Prompt mit klarer
     Bewegungssprache („capsules rain down and float, golden light rays sweep, silk
     undulates, glow pulses on the button, all printed text stays perfectly still").
   - Zoom: Startbild = Karte, `--endbild` = Zoom-Endbild, Prompt „pouch slowly floats
     toward the camera, ending exactly in the final frame".
3. **Bewegungsmaß messen, nicht schätzen:** mittlere Frame-Differenz (Graustufen,
   180×320) des Original-Endcard-Fensters gegen den Clip — Ziel dieselbe Größenordnung
   (gemessen: Original 1,8–3,5; brauchbare Kling-Clips 2,6–3,4; Standbild ≤0,4). Text-
   Regionen (Headline, Badges, Button) auf den Frames lesen — bleiben sie scharf, ist
   der Clip gut; warpt der Text, die Regionen aus dem Standbild statisch darüberlegen.
4. Montage: Schweben → 0,7-s-Crossfade → Zoom, auf 720×1280 skaliert/gecroppt,
   24 fps; länger als das Endcard-Fenster ist erlaubt (der Einbau tempt aufs Fenster,
   0,9–1,1× bleibt unsichtbar). Standbild-Fassung nach `02-roh/` (Beleg), nie in
   `03-final/`.

## 9. Einbau in die fertige Ad (Custom-Fassung rendern)

Die Custom Clips ersetzen ihre Original-Stellen in der bereits gerenderten Ad
(`[projekt]/final/*.mp4`) — der Song/die Tonspur wird dabei NIE angefasst.

**Wo jeder Quell-Clip in der Ad liegt, sagt die Schnittliste des Projekts**
(in `[projekt]/_pipeline/`), eines von zwei Formaten:

- `cutlist_block.json` (Block-Ära): je Eintrag `{clip, src0, src1, out0, out1, rate}`
  — `out0/out1` sind die Position in der fertigen Ad, `rate = src-Dauer / out-Dauer`.
- `cutlist<NNN>.json` (Kaskaden-Ära): je Eintrag `{src0, src1, speed, d}` —
  `out0` = Summe aller `d` davor (Listen-Reihenfolge), `out1 = out0 + d`,
  Rate = `speed`. Fehlt im Ziel-Ordner jede Schnittliste: Befund an Viktor,
  nicht raten.

**Verfahren (ein ffmpeg-Lauf, ein Encode):**
1. Grenzen auf das Frame-Raster runden (`f = round(out*fps)`), Fenster hinter dem
   Datei-Ende auf die Videolänge kappen (der letzte Clip ragt oft über das
   Song-Ende hinaus).
2. Einen Schnittgraphen bauen: Original-Segmente zwischen den Fenstern per
   `trim=start_frame:end_frame`, in jedem Fenster der Custom Clip — getempt mit
   `setpts=PTS*(out-Dauer/Custom-Dauer)` (= dieselbe Rate, die der Render dem
   Original-Clip gab), `fps=<Render-fps>` (aus `_pipeline/sa_config.json` —
   SOL-Quellen laufen mit 30 fps, die Custom Clips kommen mit 24 fps von Kling; das
   Frame-Raster `round(out*fps)` nimmt dieselbe Zahl), `tpad=stop_mode=clone:stop_duration=1` und
   `trim` auf die EXAKTE Fensterframe-Zahl (so bleibt die Gesamtlänge per
   Konstruktion erhalten). Alles in EIN `concat`.
3. Rendern mit `-map "[out]" -map 0:a -c:a copy` — Audio 1:1 aus der
   Original-Ad. Ergebnis: `final/<originalname>_CUSTOM.mp4`, das Original
   bleibt liegen.
4. QA: Gesamtdauer = Original ±1 Frame UND Stichproben-Frames an mindestens
   3 ersetzten Positionen zeigen das eigene Produkt.

Werkzeug der Referenz-Pipeline: `brands/SOL - Solena/001 SA/_pipeline/custom_einbau001.py`
(Fenster aus `cutlist_block.json`, Teil-Ersatz ab `t_ersatz`, QA-Frames nach `_custom-clips/04-qa/`).
Liegt die Custom-Fassung als EINZIGE MP4 in `final/`, baut `tools/sa/capcut_paket.py`
das Paket direkt auf ihr (die Fassung ohne Custom Clips gehört nach `_work/`).

**CapCut-Übergabe (wenn das Paket schon auf der Original-Fassung gebaut wurde):** das bestehende `_capcut-paket/` des Projekts auf die
CUSTOM-Datei umstellen — MP4 hineinkopieren, in `fakten.json` das `mp4`-Feld
und den `capcut_projektname` (Zusatz „CUSTOM") ändern, die ANLEITUNG und
`PROMPT-FUER-MAC.txt` auf die neue Datei umschreiben, einen vorhandenen
`CAPCUT-GEPUSHT`-Marker entfernen. Caption-Timings NICHT neu rechnen — die
Tonspur ist unverändert, die alten Timings gelten exakt weiter.
