# SKILL — Captions, die gelesen werden

Wie Untertitel in einer Facebook-Ad auszusehen haben, damit sie beim Scrollen wirklich
gelesen werden. Die Mechanik dazu steht in `software/musik-finder/captions.py`; woher die
Regeln stammen und was noch offen ist, steht in `software/musik-finder/UMBAU-PLAN.md`
(Phase 5). Alle Pfade hier sind vom AWMS-Wurzelordner aus.

> Ein Caption-Häppchen ist kein Satz. Es ist das, was das Auge in einem Blick aufnimmt,
> während das Ohr es hört.

## Die harte Regel: keine Satzzeichen

Punkte, Kommas, Doppelpunkte, Semikolons, Fragezeichen, Ausrufezeichen, Bindestriche,
Gedankenstriche, Anführungszeichen — **nichts davon gehört in eine Caption**. Sie sind
Lesehilfen für Fließtext. Eine Caption steht unter einer Sekunde; die Pause macht der
Schnitt, nicht das Komma.

Zwei Ausnahmen, beide keine Satzzeichen:
- **Apostroph im Wort** bleibt: `geht's`, `it's` — er gehört zum Wort.
- **Zeichen innerhalb einer Zahl** bleiben: `50,000`, `1.100`, `3.5` — sie trennen keine
  Sätze, sondern gehören zur Zahl.

Bindestriche zwischen Wörtern werden zur **Wortgrenze**, nicht gelöscht:
`money-back` → zwei Wörter `money` `back`.

## Häppchen-Größe: 1 bis 4 Wörter

Höchstens **4 Wörter UND höchstens 26 Zeichen**, Zielgröße 3. Ein Häppchen belegt so eine
Zeile. Ein einzelnes Wort ist ausdrücklich erlaubt und oft die stärkste Form — nach einem
Komma oder einer Pause steht es allein und schlägt ein.

Ein ganzer Satz in einer Caption ist der Fehler, den diese Regeln abschaffen: Wer
`In der Wildnis kaue ich stundenlang auf Beute herum.` zwei Sekunden stehen lässt, hat den
Zuschauer verloren, bevor er zu Ende gelesen hat. Richtig sind drei Häppchen.

## Wo gebrochen wird

Zwei Durchgänge — Sinngrenzen zuerst, Zählung danach. Genau in dieser Reihenfolge, damit
kein Bruch mitten in einer Sinneinheit landet, bloß weil die Zahl vollläuft:

1. **Trennen an Sinngrenzen:** wo im Skript ein Satzzeichen stand (das Zeichen fliegt raus,
   die Stelle bleibt) und wo der Sprecher ab 0,28 s Luft holt.
2. **Zu lange Reste aufteilen:** Alle Schnitte werden GEMEINSAM optimiert (Häppchen nahe
   der Zielgröße, Schnitte möglichst auf Sprechpausen, die Grenzen aus Häppchen-Größe als
   harte Bedingung). Nicht Schnitt für Schnitt „an der größten Lücke" — in zügig
   gesprochenem Text sind die Lücken zwischen Wörtern nur Hundertstelsekunden, die
   „größte" davon ist Rauschen. Wer danach einzeln teilt, bekommt Stückwerk
   (`In der` | `Wildnis kaue ich`) und Ein-Wort-Waisen.

## Zeit: aus dem Ton, nie geschätzt

Ein Häppchen erscheint mit seinem ersten Wort und bleibt 0,15 s über das letzte hinaus
stehen (`NACHHALL` in `captions.py`) — ohne diesen Rest blitzt es nur. Kurze Lücken zum
nächsten Häppchen (< 0,6 s) werden zugezogen, damit die Caption durchgehend steht; bei
echten Pausen ab 0,6 s verschwindet sie — leerer Kasten schlägt falscher Text.

Steht ein Häppchen trotzdem kürzer als 0,25 s (`MIN_STAND`) — eine schnell gesprochene
Phrase, dicht gefolgt vom nächsten —, verschmilzt `haeppchen()` es mit dem Nachbarn, der
die Größengrenze (1–4 Wörter / 26 Zeichen) noch hält; der kleinere Nachbar zuerst, damit
die Zielgröße gewahrt bleibt. So blitzt nichts, und der Text bleibt vollständig. Passt kein
Nachbar mehr (beide schon voll), bleibt das Häppchen kurz — das ist ein Grenzfall des
Sprechtempos, kein Fehler, und darf nichts blockieren (siehe Ablauf, Schritt 5).

Die Wortzeiten kommen aus **ElevenLabs Forced Alignment**: Ton rein, Skript rein, exakte
Zeit je Wort raus. Der Text bleibt damit Viktors Skript (nie verhört — kein „Kausneck"),
die Zeit kommt aus dem echten Ton.

Geschätzte Zeiten sind nicht erlaubt. Text proportional zur Dauer aufteilen („der Sprecher
spricht ja gleichmäßig") erzeugt Häppchen, die neben der Stimme liegen.

## Optik — kommt aus der CapCut-Vorlage, nicht von hier

Aussehen und Position der Captions erbt der Export vom **Spender-Projekt** in CapCut
(`capcut_export.py` → `spender_finden()`): dessen Caption-Vorlage wird geklont. Wer die
Optik ändern will, ändert sie in CapCut an einem echten Projekt — nicht hier.

Was dieser Skill an der Optik bestimmt: **keine künstliche Großschreibung am
Häppchen-Anfang**. Ein Häppchen ist ein Fragment, kein Satz — die Schreibweise der Wörter
bleibt, wie sie im Skript steht (im Deutschen also Substantive groß). Das ergibt sich von
selbst, weil kein Schritt großschreibt; es ist trotzdem eine Regel, keine Nebenwirkung.

## Ablauf für ein Projekt

Ein Projekt liegt unter `software/musik-finder/jobs/<job-id>/` (job-id = 12 Hex-Zeichen).
`job.json` trägt die Skript-Stücke in `schnitte[].text`.

Der Normalweg ist der Knopf **„Nach CapCut"** in der Oberfläche: `POST /capcut/export/<job-id>`
ruft `caption_haeppchen()` in `app.py` auf, das alles Folgende erledigt. Von Hand nur, wenn
etwas zu prüfen oder zu reparieren ist — dann in dieser Reihenfolge:

1. **Ton besorgen.** Die Ad ist `jobs/<job-id>/input.mp4` — ein **Video**, kein Ton. Erst
   per ffmpeg extrahieren (`-vn -ac 1 -ar 16000` nach `.mp3`). Die anderen Audiodateien im
   Job taugen NICHT: `ad_audio.mp3` ist auf 120 s abgeschnitten (für Gemini gebaut, richtet
   längere Ads gegen ein Fragment aus), `output.mp4` und `check_audio.mp3` haben Musik drin.
2. **Skript bauen:** `captions.skript_bauen([c["text"] for c in d["schnitte"]])` — verbindet
   die Stücke und entfernt Wort-Dopplungen an den Grenzen (siehe Gotchas).
3. **Ausrichten:** `captions.wortzeiten(ton, skript, key)`. Der ElevenLabs-Key liegt in
   `software/voice-trimmer/elevenlabs.key`.
   **Erfolg** = gleich viele Wörter zurück wie im Skript. Weichen sie ab, hat die
   Ausrichtung Wörter verschluckt oder erfunden: nicht weiterverwenden, sondern Skript und
   Ton gegeneinander prüfen (falscher Ton? Stück-Dopplung übersehen?).
   `loss` je Wort ist ein Erfahrungswert, keine belegte Schwelle: Werte um 0,05 sind normal,
   Ausreißer über ~0,5 bei einzelnen Wörtern sind unkritisch (meist Zahlen oder Namen).
   Fehlt `loss` ganz (`None`), sagt es nichts über die Güte — dann nicht darauf stützen.
4. **Schneiden:** `captions.haeppchen(woerter)`.
5. **Prüfen:** `captions.pruefen(haeppchen)` — Grenzen zählt der Rechner, nicht das Auge.
   Leere Liste = sauber. Bei Befunden nicht von Hand am Text schrauben (das nächste
   Ausrichten überschreibt es), sondern die Ursache beheben: zu viele Wörter/Zeichen →
   `max_woerter`/`max_zeichen` sind verletzt worden, das ist ein Fehler in `haeppchen()`;
   Satzzeichen drin → `saeubern()` kennt das Zeichen nicht, `RAND_ZEICHEN` ergänzen.
   Diese STRUKTUR-Befunde sind echte Fehler und brechen den Export ab. Eine zu kurze
   Standzeit dagegen ist ein Grenzfall des Sprechtempos: `haeppchen()` verschmilzt sie so
   weit möglich (siehe „Zeit"), der unvermeidbare Rest wird geduldet. Darum prüft der
   Export mit `pruefen(h, min_stand=0)` — nur STRUKTUR-Fehler stoppen ihn, nie eine
   einzelne Caption, die Millisekunden zu kurz steht und Viktors ganzes Projekt blockieren
   würde.
6. **Ausgeben:** Die Häppchen gehen als `captions=` in `capcut_export.draft_bauen()`; das
   Feld `woerter` je Häppchen wird dort zu CapCuts Wort-Timings. Macht der Export selbst.

## Beispiel

Skript-Stück: `In der Wildnis kaue ich stundenlang auf Beute herum.`
Daraus (echte Ausgabe der Kette, Zeiten in Sekunden):

| Text | ab | Dauer |
|---|---|---|
| `In der Wildnis` | 7.62 | 0.66 |
| `kaue ich stundenlang` | 8.28 | 0.88 |
| `auf Beute herum` | 9.16 | 0.80 |

Der Punkt hinter `herum` ist weg. Die drei Häppchen sitzen auf den Sinneinheiten, nicht auf
der Wortzahl — und die Lücken dazwischen sind kleiner als 0,6 s, also zugezogen.

## Gotchas

- **Die Skript-Stücke doppeln sich an den Grenzen — erwartetes Verhalten, kein Defekt.**
  Der Voice Trimmer teilt den Segment-Text proportional zur Zeit auf und rundet an
  Wortgrenzen nach außen; zwei Nachbar-Stücke greifen dann dasselbe Wort. `skript_bauen()`
  entfernt die Dopplung. Wer hier abbricht, bekommt für solche Projekte nie Captions.
- **Die Cluster-Texte sind eine Schätzung, kein Timing.** Der TEXT stimmt, die impliziten
  Zeiten (`schnitte[].dauer`) stimmen nicht — genau deshalb kommt die Zeit aus dem Forced
  Alignment.
- **Ein Häppchen ≠ ein Clip.** Ein Clip kann drei Häppchen tragen, ein Häppchen kann über
  einen Schnitt laufen. Wer Captions an Clip-Grenzen koppelt, bekommt automatisch ganze
  Sätze.
- **CapCut erwartet Wortzeiten in Millisekunden, relativ zum Segment** — und Leerzeichen
  als eigene Einträge. `haeppchen()` liefert Sekunden relativ zum Häppchen; die Umrechnung
  samt Leerzeichen macht `capcut_export.wort_zeiten()`.
