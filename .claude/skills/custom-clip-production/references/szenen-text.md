# Szenen-Text per Custom Clip — der vollständige Weg (`form: text`)

Lesen vor dem ersten Text-Clip eines Laufs (Verweis aus SKILL.md §10). Die Maßstäbe stammen aus
dem Muster-Lauf `brands/VIS - Visiovance Sleep Guard/022 EL/` (Knet-Ad, fünf Text-Clips, alle von
Viktor freigegeben) — gemessene Vergleichswerte, keine Grenzen, die ein Clip automatisch besteht.

Inhalt: 0 Pfade, Werkzeuge, Meldewege · 1 Inventar, Fenster, Wortlaut · 2 Wegwahl · 3 Frames und
Rest-Scan · 4 Edit als Composite · 5 Start- und End-Frame · 6 Kling · 7 Rohclip · 8 Bau aufs
Fenster · 9 Prüfer-Zeilen · 10 Gate, Einbau, Bibliothek, Kosten

## 0. Pfade, Werkzeuge, Meldewege

`<Stamm>` = AWMS-Ordner (enthält `tools/`, `brands/`, `datenbanken/`); `<Projekt-Ordner>` =
`<Stamm>/brands/<Brand>/<NNN> EL/`. Muster-Skripte laufen mit `~/.venvs/sa/bin/python3` (cv2, numpy).

| Aufruf | Arbeitsordner |
|---|---|
| `python3 tools/sa/kie_bild.py edit` / `animate` | `<Stamm>` |
| `python3 "<Stamm>/tools/sp/render.py" …` | `<Projekt-Ordner>` |
| Muster `composite.py`, `logo_warp.py` | `<Projekt-Ordner>/_custom-clips/01-frames/` |
| Muster `custom_bau022.py`, `overlay_matte022.py`, `overlay_super_de.py`, `marker_weiss022.py` | `<Projekt-Ordner>`, Aufruf `~/.venvs/sa/bin/python3 _pipeline/<skript>` |
| Muster `vmake_umgekehrt022.py` | `<Projekt-Ordner>/_pipeline/` (sein Docstring nennt fälschlich `…020.py`) |

Muster-Skripte, alle unter `brands/VIS - Visiovance Sleep Guard/022 EL/` — lesen, am eigenen Lauf
messen, die Festwerte ersetzen, nie unverändert ausführen:
- `_custom-clips/01-frames/composite.py` — Textkasten-Composite; Festwerte `KAESTEN` je Frame (von Hand gesetzt, Messweg in 4) und 720×1280
- `_custom-clips/01-frames/logo_warp.py` — Glyphen per Homographie; Festwerte: Dateinamen, SIFT-Suchmaske (Zeilen 0–640), Glyphen-Kästen, Kernel 35/45, 720×1280, Einheitsfarbe der Glyphen; gibt keine Inlier aus (Messzeile in 5)
- `_pipeline/custom_bau022.py` — Bau aufs Fenster; Festwerte `W, H, N`, `FENSTER`, `TEILE`, `BLITZ`, `OVERLAY_BIS`, `ANKER`, `QUELLE`, `REINIGUNG`, dazu die Blitz-Szenen `ersatz["cc1"]`/`ersatz["cc2"]` und der Umschalt-Frame 236; liest die Basis fest aus `_work/bild_basis.mp4`, schreibt mit `-r 30`, nimmt den Ton aus `_work/source_original.mp4`; lädt `overlay_de.npz` immer (ohne Einblendung die Stelle entfernen); `lesen()` skaliert nicht
- `_pipeline/overlay_matte022.py` + `_pipeline/overlay_super_de.py` — Einblendung als Ebene (Matte aus dem Original, neue Zeilen gesetzt)
- `_pipeline/marker_weiss022.py` + `_pipeline/vmake_umgekehrt022.py` — Vmake-Fenster mit weiß vorgefärbten Markern, Fenster-Ersatz in die Bildbasis

Ablage: `_custom-clips/01-frames/` (`f<NNNN>.png`, Edits `f<NNNN>_de.png`, Composites
`f<NNNN>_de_comp.png`, Prompts `p_f<NNNN>.txt`, Kling-Prompts `k_<cc>.txt`), `02-roh/<cc>_roh.mp4`,
`03-final/<cc>-custom.mp4`, `04-qa/`, `pruefer.md`. `<NNNN>` = Frame-Index vierstellig; `<cc>` =
Kennung des Text-Clips klein (`cc1`, `cc2` … in Reihenfolge der Fenster; in `custom_clips.json` groß:
`CC1`). Text-Clips heißen nach dieser Kennung statt `c<NNN>` (§8 des Skills), weil ein Text-Fenster
mehrere Clips der Karte umfassen kann.

Meldewege:
- **Entscheid nötig** (Rest bleibt, Würfe erschöpft, Wortlaut unbelegt, keine Tabellenzeile passt):
  Beleg (Crop, Clip) per SendUserFile in den Chat, dann Popup (AskUserQuestion) an Viktor. Bis zur
  Antwort bleibt das Fenster Original; die übrigen Fenster laufen weiter. Kommt bis zum Laufende
  keine Antwort, geht die Ad mit diesem Fenster im Original weiter; der offene Punkt steht im
  Lauf-Bericht samt Abschnitt, an dem der Lauf wieder einsteigt.
- **Kein Entscheid nötig:** eine Zeile im Lauf-Bericht (Projekt-`karte.md`).

## 1. Inventar, Fenster, Wortlaut

Welche Texte ersetzt werden, sagt `workflows/Eleven-Labs-Ripping-Agent.json`, Knoten `custom-clips`:
jeder englische Text im Bild. Inventar: `_work/gestaltungs-text.md`. Die Clip-Karte trägt Text-Clips
mit `form: text` je Clip ein (Schlüssel `clip`); dieser Weg fasst sie in `_work/clips/custom_clips.json`
(JSON-Liste) zu einem Eintrag je Fenster zusammen und ersetzt dabei die Clip-Einträge — zwei Schemata
in einer Datei sind ein Fehler. Eintrag aus dem Muster-Lauf:
```json
{"cc": "CC2", "clips": [2, 3], "f0": 240, "f1": 300, "t0": 8.0, "t1": 10.033, "dauer": 2.033, "form": "text",
 "grund": "3D-Knet-Titel 'MEET YOUR / THROAT MUSCLE'", "start": "<Projekt-Ordner>/_custom-clips/01-frames/f0240_de_comp.png",
 "ende": "<Projekt-Ordner>/_custom-clips/01-frames/f0300_de_comp.png", "kling_s": 3,
 "referenzbild": "— form text", "prioritaet": "muss"}
```
- **Fenster** = die Frames, in denen der Text im Original steht, nicht die Clip-Grenzen der Karte.
  Baut sich der Text auf, beginnt das Fenster beim letzten textfreien Frame (er wird der Start-Frame).
  Blenden (Weißblitz, Überblendung) gehören nicht ins Fenster, der Bau zeichnet sie nach (Abschnitt 8).
  Beginnt der Ersatz später als der Clip, steht dessen Sekunde in `t_ersatz`. Muster: CC2 beginnt bei
  240 statt beim Clip-Anfang 233 (Blitz 233–239); CC5 beginnt bei 1229, der textfreie Anfang bleibt Original.
- **Frames:** fps = `ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 <basis>`;
  `f0 = round(t0·fps)`, `f1 = round(t1·fps) − 1`. Eine durchgehende Kamerafahrt ohne Schnitt ist EIN
  Fenster, auch wenn die Karte sie teilt.
- **Basis** (`<basis>`): die erste vorhandene von `_work/bild_basis.mp4`, `_work/vmake_cleaned.mp4`,
  `_work/source.mp4` (Reihenfolge wie `tools/sp/clip_karte.py`). Nur `bild_basis` ist außerhalb des
  Caption-Bands Original — bei den anderen gilt der Rest-Scan (Abschnitt 3) dem ganzen Bild.
- **Wortlaut:** gesprochene Zeilen aus der finalen Copy (`_pipeline/copy_final.json` bzw.
  `datenbanken/sp-projekte/<Projekt>/<slug>-final-<JJJJ-MM-TT>.md`; `<Projekt>` = Projektname im Format
  „<KÜRZEL> <NNN> EL | <TT.MM.JJJJ>“, `<slug>` = Dateipräfix der Projekt-Dateien dort, im Muster
  `cpap-darth-vader`). Offer und Wortmarke aus der Brand-DB (Spalte `brand_db` in
  `datenbanken/sp-brands/daten.csv` → `fakten.md`, `lokalisierungs-log.md`); bei Widerspruch gewinnt
  die Brand-DB. Nirgends gesprochener Text: natürlich übersetzen, im Lauf-Bericht ausweisen. Eine
  Angebots-Aussage, die `fakten.md` nicht deckt → Entscheid nötig (Abschnitt 0).
- **Bezahlte Schritte (Edit, Kling) erst, wenn der Wortlaut steht** (finale Copy da, Offer
  entschieden); vorher nur Inventar, Frames, Rest-Scan. Im Muster kostete ein später entschiedenes
  Offer einen zweiten Endcard-Bau.

## 2. Wegwahl

Zuerst die Bibliothek (`datenbanken/custom-clip-bibliothek/<KÜRZEL>/`, Vertrag in deren
`DATENBANK.md`): ein Text-Clip passt nur bei gleicher Quell-Szene und wortgleichem deutschem Text
nach Abschnitt 1, nie mit `veraltet: JA` in seiner `karte.md`; er wird nach Abschnitt 8 aufs Fenster
abgebildet, nicht hart geschnitten. Sonst gilt die erste passende Zeile:

| Lage des Textes | Weg |
|---|---|
| 1. bewegt sich nicht: jede Zeile bleibt auf denselben Pixeln, erscheint/verschwindet höchstens per Pop oder Blende, nichts schiebt sich davor | Ebene (Abschnitt 8), 0 Credits — Muster: Einblendung „SUPER / A REAL PATIENT WROTE THIS“ |
| 2. alles andere: bewegt sich mit Kamera oder Figur, verformt sich, baut sich mit Bewegung auf (prägt sich ein, fliegt ein, zeichnet sich) | Kling Start+End (Abschnitte 3–7) |

Fenster über 15 s an einer ruhigen Stelle teilen (Kling nimmt 3–15 ganze Sekunden). Überschneidet
sich ein Text-Fenster mit einem Lip-Sync-Fenster (`f0`/`f1` in `_pipeline/lipsync_auftraege.json`; dort ist `f1` exklusiv, beim Vergleich `f1 − 1`
nehmen), nur Zeile 1 — ein Kling-Clip würde die deutschen
Lippen überschreiben; passt Zeile 1 dort nicht → Entscheid nötig.

## 3. Frames und Rest-Scan

Start = `f0`, Ende = `f1` — der letzte Frame des Fensters, nicht 0,3 s vor der Kante wie §4 des
Skills: er ist der Anker, auf dem Kling landet. Frame-genau ziehen (aus `<Projekt-Ordner>`):
`ffmpeg -v error -y -i <basis> -vf "select=eq(n\,<f>)" -frames:v 1 _custom-clips/01-frames/f<NNNN>.png`
`f1` neben `f1−2` ansehen: zeigt `f1` schon die Folge-Szene, liegt die Fenstergrenze falsch — neu messen.
Rest-Scan: Marker-Farbe (Maske wie im Muster `_pipeline/marker_weiss022.py`), weiße Splitter, vorweggemalte Grafik
(Vmake malt Elemente, die erst später im Bild stehen, schon früher hin). Kling animiert jeden Rest
mit — im Muster wurde ein blauer Marker-Rest zur leuchtenden Platte. Rest → im selben Edit
„entfernen“ mitbestellen, oder das Fenster allein an Vmake (Marker vorher weiß färben) und per
Fenster-Ersatz zurückspleißen. Bleibt er, geht der Frame nicht an Kling → Entscheid nötig.

## 4. Edit als Composite

```
python3 tools/sa/kie_bild.py edit --frame <f.png> --referenz <f.png> --prompt-datei <p.txt> \
  --resolution 1K --aspect <Seitenverhältnis der Basis: 9:16 | 3:4 | 4:5> --out <f_de.png>
```
Der Frame ist seine eigene Referenz. Prompt aus dem Muster (`_custom-clips/01-frames/p_f0240.txt`):
> Edit the first image. Keep the picture exactly as it is: the same claymation (stop-motion plasticine)
> scene, the same characters, poses, faces, hands, objects, background, lighting, colours, shadows,
> camera angle, framing and aspect ratio. Do not move, rescale, re-render, restyle or crop anything.
> Change only the 3D clay lettering at the bottom, on the man's dark sweater (currently two lines: a
> smaller line 'MEET YOUR', partly smeared, above the big line 'THROAT MUSCLE', with a thin bar
> underneath). Make it German in exactly the same light grey-blue chunky plasticine 3D letter style,
> the same colour, shading and depth, the same position, the same centred alignment and the same size
> relation (smaller upper line, big lower line), keep the thin bar underneath. Spelled exactly:
> upper line: 'DAS IST DEIN' / lower line: 'RACHENMUSKEL'. No other words. Do not add captions,
> subtitles, logos or other text.

Umlaute immer echt (ä, ö, ü, ß); Umschreibungen wie „ae“ verbietet der Prompt ausdrücklich.
Größe: Bei 9:16 liefert 1K 768×1376; direkt (ohne Beschnitt) auf 720×1280 skaliert sitzt es am
Original (Versatz < 2 px). Anderes Format: Ausgabegröße und Versatz neu messen (Phasenkorrelation).
**Kasten** = kleinstes Rechteck um den englischen Text im Original UND den deutschen im Edit (deutsche
Zeilen sind oft länger). Vorschlag per Differenz: Graustufen |Edit − Original| > 30, öffnen 5 px,
dehnen 25 px, Flächen über 1500 px — traf im Muster 3 von 4 Frames, bei kontrastarmer Schrift fand er
nichts; Flächen außerhalb des Textes gehören nicht hinein (dort hat das Modell nur neu gerechnet).
Immer am Bild gegenprüfen. Übernommen wird nur der Kasten + 14 px Rand, Farbangleich am Ring, weiche
Kante 5 px; alles andere bleibt Original-Pixel.
Erfolg: jede deutsche Zeile liegt vollständig im Kasten und ist im 2,5×-Zoom lesbar; Figuren-
Proportionen gegen einen Original-Frame gehalten (repariert das Modell verdeckte Stellen, erfindet
es gern Größen — im Muster zu große Füße). Sonst neuer Edit, er zählt als Wurf (Loop-Regeln §7 des Skills).

## 5. Start- und End-Frame

Zwei unabhängige Edits setzen denselben Text leicht verschieden, Kling morpht dann zwischen den
Fassungen. Darum gilt die erste passende Zeile (beide Frames nach dem Rest-Scan):

| Text im Fenster | Start-Frame | End-Frame |
|---|---|---|
| 1. fehlt im Start-Frame (baut sich auf, erscheint, fährt ins Bild) | Original ohne Text | Composite der fertigen deutschen Fassung |
| 2. fehlt im End-Frame (hat das Bild verlassen) | Composite | Original; ragt noch ein Zeilenrest ins Bild, nur ihn per Composite |
| 3. steht in beiden flach aufgedruckt auf einer starren Fläche (Wand-Logo, Schild, Karte — ohne sichtbare Tiefe) | Composite | Glyphen per Homographie aus dem Start-Composite; trägt sie nicht → Zeile 4 |
| 4. steht in beiden mit sichtbarer Tiefe (3D-Lettern), verformt sich oder sitzt auf bewegter Figur | Composite | zweiter Edit mit wortgleichem Prompt |

Passt keine Zeile (Text nur mitten im Fenster): das Fenster teilen, bis jede Hälfte eine Zeile trifft.
**Homographie** (überträgt flache, einfarbige Glyphen — Tiefe und Schattierung von 3D-Lettern gingen verloren, darum dort Zeile 4): nur die Glyphen übertragen (Alpha aus der Helligkeit über dem Hintergrund, Opening-
Kernel breiter als der Strich — im Muster 35/45 px; dunkle Schrift auf hellem Grund: Vorzeichen
drehen), die alten Glyphen im End-Frame per Telea tilgen; ein ganzer Patch zeigt Lichtkanten.
SIFT-Suchmaske auf die Fläche legen. Inlier = Summe der Maske, die `cv2.findHomography(…, cv2.RANSAC, 2.0)`
als zweiten Wert liefert. Maßstab Muster (Wand-Logo): 90 Treffer, 74 Inlier (82 %), Rückprojektion
Median 0,44 px. Kontrolle: übertragene Glyphen im 2,5×-Zoom gegen den Start-Composite — gleiche Lage
auf der Fläche, keine Lichtkanten. Deutlich weniger Inlier oder verrutschte Glyphen → Zeile 4.
**Zweiter Edit:** beide Frames im 2,5×-Zoom nebeneinander — gleiche Buchstabenform, Dicke, Lage.
Weicht es sichtbar ab, den End-Edit neu würfeln (zählt als Wurf).

## 6. Kling Start+End

```
python3 tools/sa/kie_bild.py animate --startbild <start.png> --endbild <ende.png> \
  --prompt-datei <k.txt> --sekunden <Fensterlänge aufgerundet, min. 3> --mode std --out <roh.mp4>
```
Das Seitenverhältnis leitet Kling aus dem Startbild ab (das Werkzeug schickt keins mit). Der Hilfetext
von `--endbild` nennt nur den Produkt-Teil-Ersatz — für Szenen-Text gilt dieser Weg.
Prompt-Aufbau: Szene · EINE durchgehende Bewegung über die ganze Clip-Länge · wo der Text am Ende
steht · Text wörtlich · Verbote. Muster (`_custom-clips/01-frames/k_cc2.txt`):
> Claymation stop-motion close-up of a window into a man's neck: inside, the little round clay muscle
> character stands in the middle and holds the airway walls apart with both arms. One single continuous
> camera move over the whole clip: the camera pushes in towards the character and tilts up, so the
> German 3D clay lettering 'DAS IST DEIN / RACHENMUSKEL' at the bottom slides down out of the frame,
> ending exactly on the final frame where only the top half of 'DAS IST DEIN' is visible at the bottom
> edge. The character looks tired, blinks and opens its mouth as if sighing. The lettering stays rigid,
> crisp and unchanged. No cuts, no cross-fade, no new text, no captions.

**Abbruch** (gilt für `edit` wie `animate`): `kie_bild.py` schreibt `<out>.job.json` nur bei Erfolg;
die Task-ID steht in seiner ersten Zeile `Job <taskId> (<modell>) …`. Zeitüberschreitung („nicht
fertig — abgebrochen“), „Job fertig, aber ohne resultUrls“ oder „Download fehlgeschlagen (<URL>)“:
der Job ist womöglich bezahlt — nicht
neu würfeln, sondern Stand und Ergebnis holen (aus `<Stamm>`, der Schlüssel kommt über das Werkzeug,
nie die `.env` lesen):
```
python3 - <<'EOF'
import sys, json, subprocess; sys.path.insert(0, "tools/sa"); import kie_bild as k
d = json.loads(subprocess.run(["curl", "-s", k.STATUS + "<taskId>", "-H", "Authorization: Bearer " + k.schluessel()],
                              capture_output=True, text=True).stdout)["data"]
print(d.get("state"), d.get("creditsConsumed")); json.dump(d, open("<out>.job.json", "w"), ensure_ascii=False, indent=1)
r = json.loads(d["resultJson"]) if isinstance(d.get("resultJson"), str) else (d.get("resultJson") or {})
if r.get("resultUrls"): k.herunterladen(r["resultUrls"][0], "<out>")
EOF
```
Nur die Meldung „Job <taskId> fehlgeschlagen: …“ (Zustand „fail“) erlaubt einen Neustart: `failMsg` in
den Lauf-Bericht, der Neustart zählt als Wurf.

## 7. Rohclip prüfen

(a) Je nach Zeile aus Abschnitt 5: **Zeile 1** — erscheinen die Elemente in Reihenfolge und Ort wie im
Original und stehen am Ende vollständig? **Zeile 2** — verlässt der Text das Bild mit der Kamera, oder
löst er sich stückweise auf (= durchgefallen; im Muster scrollte derselbe Prompt einmal sauber und löste
sich im nächsten Wurf auf)? **Zeilen 3–4** — bleibt die Schrift starr auf ihrer Fläche, ohne zu morphen?
(b) Jede Textzeile in Frames mitten in der Bewegung im 2,5×-Zoom lesen; verformte Buchstaben =
durchgefallen. Durchgefallen → neuer Wurf nach den Loop-Regeln von §7 des Skills; einen Wurf mit
kleinem Mangel deterministisch reparieren statt weiterzuwürfeln.

## 8. Bau aufs Fenster

Basis des Baus ist die neueste Bildfassung: liegt `_work/bild_lipsync.mp4` vor, sie (sonst gehen die
deutschen Lippen verloren), sonst `<basis>` — im Muster-Skript die feste Basis ersetzen (Abschnitt 0).
Der Lip-Sync-Knoten läuft parallel und kann später fertig werden: dann den Bau auf
`bild_lipsync.mp4` wiederholen (0 Credits), bevor `schnitt` rendert.
Kling liefert die Größe des Startbilds mit 24 fps (Muster: 720×1280, 73 Frames für 3 s); weicht die
Größe von der Basis ab, beim Einlesen skalieren. Jeden Clip auf die exakte Frame-Zahl seines Fensters
abbilden, erster und letzter Frame verankert.
Raffung: Kling nimmt mindestens 3 s, kürzere Fenster werden gerafft. Maßstab Muster: Raffung 1,25× /
1,48× / 1,73× ging durchs Gate, weil Kling Bewegungen langsamer anlegt — das Bewegungsmaß (mittlere
Frame-Differenz, Graustufen 180×320, wie §8b des Skills) lag bei 0,90 / 1,06 / 0,99 des
Original-Fensters, über alle fünf Clips bei 0,66–1,42. Je Clip messen; liegt er deutlich außerhalb
dieses Bandes, im Vergleichsvideo in Originalgeschwindigkeit ansehen; wirkt er gehetzt, hinten
schneiden statt raffen (der End-Anker entfällt dann).
Lese-Phase: ist die Zeit mit voll lesbarem Titel kürzer als im Original, die Zeitachse stückweise
führen (Ruhe auf die Original-Lesezeit strecken, Rest leicht verdichten — im Muster 2,6 → 3,3 s).
Blenden (Weißblitz) nach der gemessenen Helligkeitskurve des Originals nachzeichnen. Ebene
(Abschnitt 2, Zeile 1): gleiche Wörter per Matte aus dem Original lösen, neue Zeilen in der gemessenen
Versalhöhe setzen, Ein-/Ausblendung nach der gemessenen Deckkraft des Originals.
Frame für Frame streamen, nie alle Frames als Arrays halten (drei Voll-Arrays à 3,9 GB sprengten den
Arbeitsspeicher). Ausgaben: `03-final/<cc>-custom.mp4` (Fenster plus nachgezeichnete Blende),
`_work/bild_custom.mp4` (ganze Ad), `04-qa/vergleich_gesamt.mp4` (Original | Custom).

## 9. Prüfer-Zeilen für Text-Clips (ersetzen die Zeilen aus §7 des Skills, die Loop-Regeln bleiben)

| Zeile | TRUE, wenn |
|---|---|
| T1 Handlung | jede Bewegung des Handlungs-Inventars (§3 des Skills) vorkommt und endet |
| T2 Text | jede deutsche Zeile in jedem Frame lesbar ist, in dem sie im Original vollständig steht (Stichprobe Anfang, Mitte, Ende dieser Spanne im 2,5×-Zoom); kein Morphen, echte Umlaute, Wortlaut nach Abschnitt 1 |
| T3 Szene | gleiche Figuren, gleicher Raum; außerhalb der Textkästen keine neuen Objekte, keine Vmake-Reste |
| T4 Länge | `_work/bild_custom.mp4` so viele Frames hat wie die Basis und jeder Clip in `03-final/` so viele wie die Spanne, die er ersetzt (Muster cc1: Fenster 233 + Blitz 7 = 240); gezählt per `ffprobe -count_frames` |
| T5 Schärfe | der Hintergrund so scharf ist wie im Original (verschwommen = FALSE). Messhilfe: Laplace-Varianz ohne Textkästen und Caption-Band gegen die Basis im selben Frame — Muster 0,36–1,35; jeden Frame unter 0,5 in 100 % gegen das Original ansehen |
| T6 Nähte | nach einem Schnitt die Korrelation (Graustufen 180×320) erster Custom-Frame ↔ letzter Frame der Vorszene VOR einer Blende höchstens 0,6 ist, sonst geistert die Vorszene (Muster −0,10 bis 0,27; gegen einen Blitz-Frame, der schon die neue Szene zeigt, misst man 0,84 ohne Geist); setzt der Clip dieselbe Einstellung fort: kein sichtbarer Sprung in Originalgeschwindigkeit (Muster-Endcard: Differenz 1,6 bei Nachbar-Differenz 0,5, unsichtbar) |

## 10. Gate, Einbau, Bibliothek, Kosten

**Gate-Dokument, immer:** `04-qa/vergleich_gesamt.mp4` + Vorher/Nachher-Bild je Clip per SendUserFile
in den Chat, Prüfer-Ergebnis in `_custom-clips/pruefer.md`. Warten richtet sich nach
`.claude/skills/execute/SKILL.md` (Gates: entscheiden statt warten): sind T1–T6 grün und ist jeder
Wortlaut nach Abschnitt 1 belegt, ist die Gate-Frage aus dem Material beantwortet — einbauen, als
Selbst-Entscheid vermerken, am letzten Gate aufführen. Das harte Gate aus §8 des Skills gilt dem
Produkt-Label, das nur Viktor beurteilen kann; ein Text-Clip ohne Produkt trägt keins. Sagt Viktor
später Nein: Fenster aufs Original zurück oder neu bauen, dann Render und CapCut-Paket neu (einen
vorhandenen `CAPCUT-GEPUSHT`-Marker entfernen).
**Einbau** (Knoten `schnitt`, aus `<Projekt-Ordner>`) — `schnitt` rendert `bild_custom.mp4`, auch in Läufen
mit Lip-Sync statt `bild_lipsync.mp4` (sie steckt als Basis darin): `python3 "<Stamm>/tools/sp/render.py" --video
_work/bild_custom.mp4 --sprechspur _work/sprechspur.wav --bett _work/musikbett.wav …` — ohne
Pixel-Eingriff läuft das Bild bitgleich durch. Erfolg: Frame-Zahl von `_work/final.mp4` =
`bild_custom`. §9 des Skills gilt nur für Läufe mit Schnittliste.
**Bibliothek:** nach der Prüfer-Abnahme ablegen; Ordner, Motiv-Slug und `karte.md` nach
`datenbanken/custom-clip-bibliothek/DATENBANK.md`.
**Kosten:** `creditsConsumed` aus jedem `<out>.job.json` summieren (fehlt eines: Abschnitt 6),
verworfene Würfe getrennt; Dollar = Credits × Kurs des gekauften kie.ai-Pakets (Abrechnung im
kie.ai-Konto; im Muster 1 Credit ≈ 0,005 $). Buchung je Aufruf in `<Stamm>/.usage/direkt.jsonl` im Format
von `.claude/skills/execute/SKILL.md` Schritt 3b, zusätzlich Feld `notiz` mit Projekt, `<cc>`, Stufe und Task-ID (erste 8 Zeichen); ohne
Job-JSON `"menge":null`.
