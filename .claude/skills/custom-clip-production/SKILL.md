---
name: "custom-clip-production"
description: "Ersetzt Produkt-Clips einer Resync-Ad (Competitor-Branding, z. B. Quasi) durch neu animierte Custom Clips mit dem eigenen rebrandeten Produkt (Areum) — Frame-Edit + Kling-Kette + Tempo-Anpassung + Handlungs-Prüfer. Nutzen, wenn Viktor sagt „Custom Clips", „Produkttausch", „ersetz das Produkt in den Clips", „rebrand die Clips", „Quasi raus, Areum rein" — oder wenn im Produkttausch-Workflow (Longform-Singing-VSL-Quasi-Produkttausch) die Clip-Karte Clips mit sichtbarem Produkt markiert hat. Auch ohne diese Wörter nutzen, sobald eine fertige oder laufende Rip-Ad Competitor-Packaging zeigt, das nicht mehr ausgespielt werden darf (Rebranding, DMCA)."
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
{"clip": 285, "t0": 570.08, "t1": 572.17, "dauer": 2.08, "form": "sachet", "grund": "Sachet frontal in die Kamera, Logo gross lesbar"}
```

`form` ∈ `sachet` | `dose` | `screen` | `sonstiges` — was für eine Produktform
im Original zu sehen ist. `sachet` = das flache Masken-Päckchen, `dose` = die
Faltschachtel/Box, `screen` = das Produkt erscheint auf einem Bildschirm im Bild
(Shop-Seite, Handy), `sonstiges` = alles andere (z. B. Produkt-Berg im
Hintergrund). Fehlt die Datei, die Clip-Karte des Projekts einmal durchgehen
(Beschreibungs-Feld `bild` nach Verpackungs-Wörtern rastern, Treffer mit eigenen
Augen am Frame verifizieren) und die Datei schreiben — erst dann produzieren.

`screen`-Clips (Shop auf einem Bildschirm): Sobald in `brands/QUA - Quasi/
QUA - Reference IMGs/` Shop-Referenz-Screenshots liegen (Dateiname beginnt mit
`QUA - Areum Shop`), wird der Screen-Inhalt mit diesen Referenzen auf den
eigenen Shop umgebaut — gleiche Edit-Kette wie beim Produkt. Fehlen die
Shop-Referenzen, den Clip NICHT produzieren, sondern als offenen Punkt in den
Lauf-Bericht an Viktor. `sonstiges`-Clips immer als offener Punkt an Viktor.

## 2. Referenzen: welches Produktbild in den Edit geht

Alle Produkt-Referenzen liegen im Unterordner `Product Reference/` der
Brand-Datenbank: `/root/AWMS/datenbanken/brand-quasi/Product Reference/`.
Es wird IMMER von dort gearbeitet — kein anderer Ablageort.

- `Areum Sachet Reference.png` — für `form: sachet`
- `Areum Box Reference.png` — für `form: dose`
- `Areum Shop *.png` — Shop-Screenshots für `form: screen` (sobald vorhanden)

Die Referenz-Datei ist die Wahrheit für Farben, Layout und Maskensymbol. Details,
die die aktuelle Verpackung trägt, die Referenz-Datei aber (noch) nicht zeigt,
werden zusätzlich als Text in den Edit-Prompt geschrieben (siehe Prompt-Vorlage);
bei Widerspruch zwischen Datei und Prompt-Text gewinnt die Datei. Liegt im
Ordner eine neuere Referenz-Fassung, die alte ersetzen — nie zwei Fassungen
derselben Form nebeneinander liegen lassen.

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

- **NUR das eigene Produkt.** Rebrandet wird ausschließlich das Masken-Produkt
  (Sachet/Dose). ALLE anderen Objekte bleiben unangetastet — auch andere
  Produkte, die die Competitor-Marke tragen. Solche Stellen nicht eigenmächtig
  umlabeln, sondern als Befund in den Lauf-Bericht an Viktor.
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
2. **Beide Frames editieren** — Modell `nano_banana_flash` (Nano Banana 2) über
   die Higgsfield CLI (`/usr/bin/higgsfield`), Referenz (1) = der Original-Frame,
   Referenz (2) = die Tier-1-Produktreferenz, `--aspect_ratio 9:16
   --resolution 2k`. Prompt-Vorlage (bewährt, nur die Produktform-Details
   austauschen):

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
3. **Ergebnis-Download:** im Job-JSON zählt NUR das Top-Level-Feld `result_url`
   — die URLs unter `params.medias[]` sind das Echo der EIGENEN Uploads (wer die
   nimmt, lädt sein Eingabebild herunter und hält es für das Ergebnis).
4. **Frame-QA in voller Auflösung:** Markenname lesbar? Genau EIN Produkt?
   Pose/Raum/Person unverändert? Wirkt etwas halluziniert, ZUERST den
   Original-Frame ansehen — was dort schon steht, ist kein Modell-Fehler.
   Durchgefallene Frames einzeln neu würfeln (gleicher Prompt), nicht die
   ganze Kette.

## 5. Animation (Kling, nur Start-Frame)

Modell `kling3_0` (Higgsfield CLI), NUR `--start-image` = der bearbeitete
Start-Frame (kein `--end-image`), `--mode std --aspect_ratio 9:16 --sound off`
(das Echo der Job-Antwort MUSS `sound: off` zeigen, sonst wurde Audio
mitbezahlt).

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
  kein Loop) über das Bildboard (`bild <datei>`) an Viktor.
- Die Custom Clips ersetzen ihre Original-Gegenstücke erst NACH Viktors Go im
  Schnitt/Render des Projekts.
- Kosten-Rahmen zur Orientierung: ~2 cr je Frame-Edit, ~4,5 cr je 3-s-Kling —
  vor großen Läufen `higgsfield account status` prüfen und Stand in den
  Lauf-Bericht schreiben.

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
1. Grenzen auf das Frame-Raster runden (`f = round(out*24)`), Fenster hinter dem
   Datei-Ende auf die Videolänge kappen (der letzte Clip ragt oft über das
   Song-Ende hinaus).
2. Einen Schnittgraphen bauen: Original-Segmente zwischen den Fenstern per
   `trim=start_frame:end_frame`, in jedem Fenster der Custom Clip — getempt mit
   `setpts=PTS*(out-Dauer/Custom-Dauer)` (= dieselbe Rate, die der Render dem
   Original-Clip gab), `fps=24`, `tpad=stop_mode=clone:stop_duration=1` und
   `trim` auf die EXAKTE Fensterframe-Zahl (so bleibt die Gesamtlänge per
   Konstruktion erhalten). Alles in EIN `concat`.
3. Rendern mit `-map "[out]" -map 0:a -c:a copy` — Audio 1:1 aus der
   Original-Ad. Ergebnis: `final/<originalname>_CUSTOM.mp4`, das Original
   bleibt liegen.
4. QA: Gesamtdauer = Original ±1 Frame UND Stichproben-Frames an mindestens
   3 ersetzten Positionen zeigen das eigene Produkt.

**CapCut-Übergabe:** das bestehende `_capcut-paket/` des Projekts auf die
CUSTOM-Datei umstellen — MP4 hineinkopieren, in `fakten.json` das `mp4`-Feld
und den `capcut_projektname` (Zusatz „CUSTOM") ändern, die ANLEITUNG und
`PROMPT-FUER-MAC.txt` auf die neue Datei umschreiben, einen vorhandenen
`CAPCUT-GEPUSHT`-Marker entfernen. Caption-Timings NICHT neu rechnen — die
Tonspur ist unverändert, die alten Timings gelten exakt weiter.
