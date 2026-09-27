---
name: speaking-vsl-captions
description: "Bereitet die deutschen Untertitel einer Speaking-VSL als Datei für CapCut vor — Zeitfenster aus den TTS-Takes, feste Bildposition, Zwei-Zeilen-Regel. BRENNT NICHTS EIN: die Untertitel entstehen in CapCut. Nutzen nach dem Sprechspur-Bau, wenn „Captions", „Untertitel", „SRT" fällt."
---

# Speaking-VSL Captions — Vorbereitung, kein Einbrennen

## Das Grundgesetz: nicht einbrennen

**Die Kette liefert Bild + Sprechspur. Untertitel macht Viktor in CapCut.**
Eingebrannte Untertitel sind endgültig — sie lassen sich nicht mehr verschieben,
umformulieren oder stylen, ohne das ganze Video neu zu rendern. CapCut kann all das
in Sekunden. Darum liefert dieser Baustein eine **SRT-Datei**, nie ein Video mit Text.

Rote Flagge: Du tippst `subtitles=` oder `drawtext` in ein ffmpeg-Kommando für die
Auslieferung → STOPP. Das ist der Job von CapCut.
(Ausnahme: eine reine Kontroll-Vorschau für dich selbst, die nie ausgeliefert wird.)

## Zwei Gesetze für die Untertitel selbst

Beide gelten auch für das, was Viktor später in CapCut baut — die SRT-Datei muss sie
schon einhalten, sonst muss er sie von Hand nacharbeiten.

### 1. Eine feste Position, die sich NIE bewegt

Untertitel gehören **unten mittig, im unteren Fünftel** — nicht in die Bildmitte.
Der Anker ist fest: dieselbe Zeile sitzt in Sekunde 3 exakt dort, wo sie in
Sekunde 50 sitzt.

Der häufigste Fehler: Der Untertitel wird unten verankert, die Zeilenzahl schwankt,
und der Block **wächst nach oben** — dadurch wandert der Text bei langen Zeilen in
die Bildmitte oder aus dem Bild. Deshalb:

- **Höchstens zwei Zeilen je Einblendung.** Passt der Satz nicht, wird er auf zwei
  Einblendungen aufgeteilt — nie auf drei Zeilen gestreckt.
- Zeilenlänge höchstens ~34 Zeichen, damit zwei Zeilen reichen.
- Position im unteren Fünftel: bei 1280 px Höhe liegt die Textmitte bei ~1040 px
  (≈ 81 %). In CapCut die Y-Position einmal setzen und für alle Untertitel übernehmen.

**Ausnahme mit eigener Bedingung: die Quelle hat eine eigene Untertitel-Fläche.** Brennt
die Quelle ihre Untertitel auf einen deckenden Balken, bleibt der Balken nach dem Tilgen
der Buchstaben im Bild — hinter ihm existiert kein Bild, das sich wiederherstellen ließe.
Dann sitzen die deutschen Untertitel **in der Mitte dieser Fläche**, nicht im unteren
Fünftel: sonst stehen zwei Balken untereinander. Die Höhe wird an der Fläche gemessen
(Median der Ober- und Unterkanten aus dem Vollbild-OCR, Mitte ÷ Bildhöhe), nie geschätzt —
sie fällt je Quelle anders aus. Ohne solche Fläche gilt 81 %.

**Gemessen im QUA-001-Lauf:** Untertitel bei 42 % Höhe gebaut — das ist Bildmitte,
Viktors Befund: „nicht in der Mitte, sondern etwas weiter nach unten". Ein erster
Versuch mit dem vollen Sprechtext ergab sechs Zeilen, die oben aus dem Bild liefen.

### 2. Untertitel folgen dem Schnitt, nicht dem Absatz

Eine Einblendung darf nicht über mehrere Szenenwechsel stehen bleiben. Steht derselbe
Text sechs Sekunden über vier Schnitten, wirkt das Video eingefroren. Faustregel:
**je Einblendung 1,5–3 s**, und ein Szenenwechsel ist immer auch ein Textwechsel,
wenn der Satz es hergibt.

## Gestaltungs-Text ist kein Untertitel — er wird ERSETZT

Die Quelle trägt zwei verschiedene Sorten Text im Bild, und sie werden verschieden
behandelt:

| Sorte | Erkennungszeichen | Behandlung |
|---|---|---|
| **Sprech-Untertitel** | kleine Zeilen im unteren Drittel, folgen dem Gesprochenen | entfernen, deutsche Fassung tritt an ihre Stelle |
| **Gestaltungs-Text** | Hero-Titel am Anfang, große farbige Typo, Preis-Störer, Endcard | **ersetzen, nicht weglassen** |

**Der Hero-Titel am Anfang trägt den Hook.** Wird er nur entfernt, beginnt die Ad mit
einem stummen Bild und verliert die stärkste Sekunde. Er braucht ein deutsches
Pendant in vergleichbarer Größe und Farbe — Position und Gewicht wie im Original.

**Gemessen im QUA-001-Lauf:** Der rot-weiße Titel „I WAS NOT READY FOR THIS BACK
MASSAGER TO CANCEL MY SURGERY" (0:00–0:06, oberes Bilddrittel) wurde von Vmake
entfernt und nicht ersetzt. Viktors Befund: „anstatt den auch damit zu ersetzen …
immer ersetze". Die Liste der Gestaltungs-Texte gehört in die Übergabe an CapCut,
mit Zeitfenster, Originalwortlaut und deutschem Vorschlag.

## Ausgabe

1. `_work/captions.srt` — die Sprech-Untertitel, Zwei-Zeilen-Regel eingehalten,
   Zeitfenster aus den TTS-Takes gemessen (nicht geschätzt).

   **Die Standzeit wird gemessen, nicht geschätzt.** Zu viele und zu lange Zeilen
   fallen beim Hinsehen auf, eine zu lange Standzeit nicht — darum prüft ein Werkzeug
   sie, bevor die SRT weitergeht. Im Projektordner ausführen (`<projektstamm>` =
   Stamm des AWMS-Ordners, `<NNN>` = Ad-Nummer; nur Standardbibliothek, kein venv):

   ```bash
   python3 <projektstamm>/tools/sp/untertitel_regel.py --srt _work/captions.srt --haeppchen _pipeline/captions<NNN>_haeppchen.json
   ```

   Die Häppchen-Datei ist die des Captions-Knotens; sie liefert die Wortzeiten.
   Exit 0 = grün. Exit 1 = Befund, und die Ausgabe nennt jede betroffene
   Einblendung mit ihrer Standzeit.

   **Bei Befund** dieselbe Zeile um `--kanten _pipeline/clip_karte.json` und
   `-o _work/captions.srt` erweitern: das Werkzeug schneidet zu lange Einblendungen
   an Wortgrenzen nach — bevorzugt dort, wo die Szene wechselt — und lässt den
   Wortlaut unberührt. Es prüft die Wortfolge gegen und bricht bei jeder Abweichung
   ab, ohne zu schreiben. Danach erneut messen, bis grün.

   Fehlt `_pipeline/clip_karte.json`, das Flag weglassen — dann schneidet es an der
   größten Sprechpause statt am Szenenwechsel. Fehlt die Häppchen-Datei, teilt es
   innerhalb der Einblendung proportional zur Zeichenlänge; welche Schnitte so
   entstanden sind, steht in der Datei aus `--protokoll`. Bleibt eine Einblendung
   trotz Nachschnitt zu lang, sagt es das mit `BLEIBT LANG` — dann ist der Satz an
   dieser Stelle unteilbar, und die Zeile wird gekürzt statt der Zeitgrenze
   verschoben.

   **Drei Zahlen gehören in die Übergabe:** Einblendungen, davon über 3 s, längste
   Standzeit. Ohne sie ist die Regel nur behauptet.

2. `_work/gestaltungs-text.md` — je Gestaltungs-Text eine Zeile:
   Zeitfenster · Originalwortlaut · Position im Bild · deutscher Vorschlag.
3. Im Chat: beide Dateien nennen und ausdrücklich sagen, dass NICHTS eingebrannt ist.

Danach übernimmt der CapCut-Push.
