---
name: stimmen
typ: CSV (Tabelle)
zweck: Das Stimmen-Register — je Marke die einmal gecastete Sprecherin mit voice_id, Einstellungen und gemessener Sprechrate. Casting laeuft EINMAL je Marke, nie je Ad.
schreibt: speaking-vsl-stimm-casting (nach dem Casting-Lauf)
liest: sprech-watch (holt die Stimme der Marke, bevor ein Take erzeugt wird)
format: daten.csv mit Kopfzeile; je Marke eine Zeile; Aussprache-Lexikon je Marke unter eintraege/<KUERZEL>-lexikon.md
---
# Stimmen-Register

**Harte Regel (Viktors Ansage 20.08.2026): nur deutsche Muttersprachler-Stimmen.**
Keine amerikanischen Stimmen im deutschen Modus — auch nicht die, die ElevenLabs als
„DE verifiziert" fuehrt. Die 21 Standardstimmen eines Kontos sind ueberwiegend
amerikanisch; gecastet wird aus der oeffentlichen Bibliothek (`/v1/shared-voices`,
`language=de`), wo ueber 400 weibliche deutsche Stimmen liegen.

Die Spalte `variation` ist der Messwert aus dem Casting: Streuung der Grundfrequenz
geteilt durch ihren Mittelwert. Unter 25 % klingt flach, 25–35 % ist das Band eines
natuerlichen deutschen Werbe-Reads.
