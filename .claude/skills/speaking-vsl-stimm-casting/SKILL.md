---
name: speaking-vsl-stimm-casting
description: "Castet EINMAL je Marke die deutsche Sprecherin einer Speaking-VSL — systematisch gefiltert aus der öffentlichen ElevenLabs-Bibliothek, nie aus den Konto-Standardstimmen, und entschieden per gemessener Tonhöhen-Variation. Nutzen, wenn eine Marke noch keinen Eintrag im Stimmen-Register hat oder Viktor „andere Stimme", „Casting", „die klingt nicht" sagt."
---

# Stimm-Casting — einmal je Marke, systematisch statt nach Gefühl

## Zwei harte Gesetze

**1. Nur deutsche Muttersprachler-Stimmen. Nie amerikanische im deutschen Modus.**
Die ~21 Stimmen in einem ElevenLabs-Konto sind die Standardbesetzung: überwiegend
amerikanisch, viele als „DE verifiziert" markiert. Das heißt nur, dass sie Deutsch
aussprechen können — sie klingen dabei nicht deutsch. Gecastet wird ausschließlich
aus der öffentlichen Bibliothek:
`GET /v1/shared-voices?page_size=100&language=de&gender=<w|m>` (über 400 weibliche
deutsche Stimmen). Shared Voices lassen sich direkt per `voice_id` ansprechen, ohne
sie vorher ins Konto zu übernehmen.

**2. Die Ausgabe ist immer deutsch**, bis Viktor ausdrücklich etwas anderes sagt.
Die Sprachfilterung ist damit kein Sonderfall, sondern der Normalzustand.

## Die Kandidaten kommen aus dem Video, nicht aus dem Bauchgefühl

Wer im Quellvideo spricht, bestimmt die Filter. Aus der Clip-Karte und dem
Lokalisierungs-Befund ablesen: **Geschlecht** und **Altersgruppe** der Avatarin.
Danach filtern:

1. `gender` — aus dem Original
2. `age` ∈ {middle_aged, old} bei einer Avatarin ab ~45; {young} darunter
3. `use_case` — **`advertisement` und `social_media` schlagen `narrative_story`.**
   Hörbuch- und Erklärstimmen tragen eine Ad nicht; sie sind auf Ruhe getrimmt.
4. `descriptive` ∈ {confident, pleasant, casual, crisp, upbeat, friendly, warm} —
   **`calm` und `chill` fliegen raus**, das ist für Direct Response zu flach.
5. Namen mit „Meditation", „ASMR", „Sleep" ausschließen.

**Gemessen im QUA-001-Lauf:** 400 weibliche DE-Stimmen → 229 nach Alter → 205 nach
Einsatzzweck → 197 nach Meditations-Ausschluss → 84 nach `descriptive` → die zehn
mit dem besten Register getestet.

## Entschieden wird gemessen, nicht geraten

Mit jedem der ~10 Finalisten **dieselbe schwere Testzeile** erzeugen — der Hook,
weil er die Ironie und den Tonwechsel tragen muss. Gleiches Modell, gleiche
`voice_settings`, nur die `voice_id` wechselt.

Dann je Take die **Tonhöhen-Variation** messen: Grundfrequenz je 40-ms-Fenster per
Autokorrelation (Suchbereich 70–300 Hz, Stille über die Energie überspringen),
danach `Streuung ÷ Mittelwert`.

| Variation | Bedeutung |
|---|---|
| unter 25 % | flach, klingt nach Maschine |
| **25–35 %** | **Band eines natürlichen deutschen Werbe-Reads** |
| über 35 % | überzeichnet, kippt ins Theatralische |

Zweites Kriterium: die **Dauer der Testzeile gegen ihr Zeitfenster**. Wer schon beim
Hook 40 % über Budget liegt, zwingt die ganze Ad ins Tempo-Trimmen.

Die höchste Variation im Band gewinnt — bei Gleichstand entscheidet das nähere
Zeitfenster, danach `use_case = advertisement`.

**Gemessen im QUA-001-Lauf:** Juli – German 30,8 % · Sissi 28,4 % · Ramona 27,2 % ·
Irene UGC 25,9 % … Emilia 21,7 %. Zum Vergleich die vorher benutzte amerikanische
Matilda: 24,7 % — unterhalb des Bands. Das war die Ursache für Viktors Befund
„klingt nicht nativ".

## Ergebnis sichern

Gewinnerin als Zeile in `datenbanken/stimmen/daten.csv`: Marke, `voice_id`, Name,
Herkunft, Alter, Register, gemessene Variation, gemessene Sprechrate, Modell und alle
`voice_settings`, Datum. Ab dann liest `sprech-watch` die Stimme dort — **das Casting
läuft nie wieder für diese Marke**, außer Viktor verlangt es.

Aussprache-Lexikon der Marke (Produktname, Zahlen, €-Beträge) daneben unter
`eintraege/<KÜRZEL>-lexikon.md`.

## Wenn nichts im Band landet

Dann greift **Voice Design**: eine Stimme aus einer Textbeschreibung erzeugen lassen.
Die Anleitung zum Schreiben eines solchen Prompts liegt im Bündel unter
`referenz/voiceover-narrator-voice-design-prompt/SKILL.md`.
