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
2. `_work/gestaltungs-text.md` — je Gestaltungs-Text eine Zeile:
   Zeitfenster · Originalwortlaut · Position im Bild · deutscher Vorschlag.
3. Im Chat: beide Dateien nennen und ausdrücklich sagen, dass NICHTS eingebrannt ist.

Danach übernimmt der CapCut-Push.
