# Feedback-Log — Longform Speaking VSL Quasi

Format: Datum · Feedback-Wortlaut · Diagnose · destilliertes Prinzip · geaenderte Datei(en)

## 2026-08-20

**1 · „mitten im Video so uebel rote Striche … zieht sich das ganze Video lang"**
Diagnose: In den Frames NICHT reproduzierbar. Drei Ursachen geprueft und
ausgeschlossen — Differenzbild zeigt, dass Vmake ausschliesslich das Text-Band und
das Money-Back-Siegel angefasst hat; Farb-Tags sind durchgehend bt709; die roten
Flaechen sind Original-Effekte (Schmerz-Glow). Bleibende Hypothese: das finale
Video wurde unnoetig mit libx264 crf 20 NEU ENCODIERT, obwohl nur Ton dazukam —
eine zusaetzliche h264-Generation bricht zuerst an gesaettigtem Rot in Streifen auf.
Prinzip: **Ein Ton-Mux ist kein Grund, das Bild anzufassen** — `-c:v copy`, und die
Frame-Zahl beweist Bitgleichheit. Damit ist die Frage „kommt es von Vmake?" kuenftig
ohne Raterei beantwortbar.
Geaendert: `.claude/skills/vmake-caption-entfernen/SKILL.md`

**2 · „Der Untertitel muss auf einer Position, unten mittig, nicht in der Mitte"**
Diagnose: Untertitel unten verankert (Alignment=2), aber die Zeilenzahl schwankte —
der Block waechst nach oben, dadurch wandert der Text bei langen Zeilen in die
Bildmitte. Gemessen: Textmitte bei 42 % Hoehe statt im unteren Fuenftel; ein erster
Versuch mit dem vollen Sprechtext ergab sechs Zeilen, die oben aus dem Bild liefen.
Prinzip: **Feste Position, die die Zeilenzahl nicht verschieben darf** — hoechstens
zwei Zeilen je Einblendung, laengere Saetze werden aufgeteilt statt gestreckt.
Zusatz aus derselben Sichtung: eine Einblendung darf nicht ueber vier Szenenwechsel
stehen bleiben (1,5–3 s je Einblendung).
Geaendert: `.claude/skills/speaking-vsl-captions/SKILL.md` (NEU)

**3 · „den grossen Titeltext komplett ausgeblendet, anstatt ihn zu ersetzen"**
Diagnose: Die Kette behandelte jeden Text im Bild gleich. Der Hero-Titel ist aber
kein Untertitel, sondern Gestaltung — er traegt den Hook der ersten sechs Sekunden.
Entfernt und nicht ersetzt beginnt die Ad mit einem stummen Bild.
Prinzip: **Zwei Textsorten trennen** — Sprech-Untertitel werden ersetzt durch die
neue Sprache, Gestaltungs-Text MUSS ein Pendant bekommen und darf nie fehlen. Die
Liste wandert als eigene Datei an die Captions weiter.
Geaendert: `.claude/skills/vmake-caption-entfernen/SKILL.md`,
`.claude/skills/speaking-vsl-captions/SKILL.md` (NEU)

**4 · „Gib mir das Video ohne Untertitel — die mach ich selbst in CapCut"**
Diagnose: Ich habe die Untertitel eingebrannt, weil ich eine fertige Ad als Ziel
annahm. Der Workflow hat CapCut-Push als eigenen spaeten Knoten — Untertitel sind
Viktors Arbeit, nicht die der Kette. Eingebrannt sind sie endgueltig; in CapCut in
Sekunden verschiebbar.
Prinzip: **Die Kette liefert Bild + Sprechspur, nie eingebrannten Text.** Rote
Flagge: `subtitles=` oder `drawtext` in einem Auslieferungs-Kommando.
Geaendert: `.claude/skills/speaking-vsl-captions/SKILL.md` (NEU),
`workflows/eleven-labs-ripping-agent.json` (Knoten „captions" praezisiert + ref)

**Nebenbefund aus demselben Lauf (kein eigenes Feedback):** Das W/s-Band im
Uebersetzungs-Skill war zu optimistisch — 2,6–3,2 notiert, real 2,3 gemessen.
Geaendert: `.claude/skills/speaking-vsl-uebersetzung/SKILL.md`

**5 · „klingt nicht nativ, nicht fluessig, hoert mitten im Satz auf, roboterhaft"**
Diagnose: Jeder der sieben Bloecke wurde ISOLIERT erzeugt. Das Modell kannte den
Nachbarkontext nicht und legte in jeden Block eine Anfangs- und Schlussmelodie —
daher die Stopps ohne Satzzeichen und der zerhackte Gesamteindruck. Zweiter Fund:
Es lief `eleven_multilingual_v2`, obwohl `eleven_v3` im Konto liegt — eine ganze
Modellgeneration aus reiner Annahme verschenkt.
Prinzip: **Eine Copy ist EIN Sprechakt.** Ganze Copy in einem Take erzeugen, danach
an den GEMESSENEN Sprechpausen schneiden und auf die Zeitmarken legen; innerhalb
eines Blocks wird der Ton nie angefasst. Dazu: Modell-Liste des Kontos abfragen,
nie annehmen.
Geaendert: `.claude/skills/sprech-watch/SKILL.md` (NEU),
`workflows/eleven-labs-ripping-agent.json`

**6 · „erster bis fuenfter Frame: da sind immer noch die roten Striche"**
Diagnose: Viktors Zeitangabe war der fehlende Hinweis — meine frueheren Stichproben
begannen bei Frame 30 und haben den Hero-Titel nie gesehen. `videoscreenclear` ist
fuer Wasserzeichen und duenne Untertitel gebaut; der GEFUELLTE rote Titelbalken
ueberfordert das Inpainting: Buchstaben weg, Flaeche bleibt als Keil (gemessen:
Eingriff x 0–718 / y 148–394, Rueckstand x 4–485 / y 182–299, 0–3,5 s).
Prinzip: **Gefuellte Gestaltungs-Elemente hinterlassen immer Rueckstand — er wird
ABGEDECKT, nicht wegretuschiert.** Grossflaechiges delogo zerstoert mehr als es
rettet (718x270 loeschte im Test die halbe Animation); enge Box + leichte Glaettung
ist die Obergrenze, der Rest verschwindet unter dem deutschen Titel. Zusatzregel:
immer die ERSTEN Frames pruefen, nicht nur eine Stichprobe aus der Mitte.
Geaendert: `.claude/skills/vmake-caption-entfernen/SKILL.md`

**7 · „auf gar keine amerikanischen Stimmen … nimm die Stimme, die am besten zum Original passt"**
Diagnose: Ich hatte die Stimme aus den ~21 Konto-Standardstimmen gewaehlt (Matilda,
amerikanisch, „DE verifiziert"). Das Flag heisst nur, dass die Stimme Deutsch
aussprechen kann — nicht, dass sie deutsch klingt. Der eigentliche Pool ist die
oeffentliche Bibliothek: 400 weibliche deutsche Stimmen. Gemessen: Matilda 24,7 %
Tonhoehen-Variation, unterhalb des natuerlichen Bands von 25–35 %.
Prinzip: **Nur deutsche Muttersprachler, und die Wahl wird GEMESSEN statt geraten.**
Filterkette aus dem Quellvideo (Geschlecht + Alter der Avatarin) → Register
advertisement/social_media schlaegt Hoerbuch → descriptive ohne calm/chill →
Testzeile mit allen Finalisten → hoechste Variation im Band gewinnt. Ergebnis ins
Stimmen-Register, Casting laeuft nie wieder fuer dieselbe Marke.
Ergebnis: Juli – German, 30,8 % (Matilda 24,7 %).
Geaendert: `.claude/skills/speaking-vsl-stimm-casting/SKILL.md` (NEU),
`datenbanken/stimmen/` (NEU), `workflows/eleven-labs-ripping-agent.json`

## 2026-09-17

**1 · „Das Lip-Sync ist gut geworden … bei dem Hund musst du kein Lip-Sync machen, nur bei der UGC … nur immer Lip-Sync für Menschen machen … mach einfach Lip-Sync als Baustein"**
Diagnose: Im Lauf RAN 001 EL lief der Lip-Sync als Einschub neben der Kette; der Workflow kannte
keinen Knoten dafür. Drei Fehler dieses Laufs wären in jedem neuen Lauf wiedergekommen:
(1) Farbblitze und Schwarz-/Weißblenden im Lip-Sync-Eingang → 8 von 32 Clips mit hautfarbenem Block
im Untergesicht und Farbschleier über den ganzen Clip (Farbstich 20–28, sauber ≈ 1);
(2) sprechende 3D-Hunde gelippt → graue, verwaschene Nase, unscharfe Schnauze, doppelte Flasche;
(3) kie-Ausgabe ohne Farbkennzeichnung → ffmpeg las bt601 statt bt709 (YUV unverändert, U/V-Abweichung
< 0,1), Hauttöne verschoben (Farbstich Ø 3,63 → 1,00 nach Übertragen der Kennzeichnung, bitgleich).
Prinzip: Lip-Sync ist ein Werkzeug für sichtbar sprechende Menschen; was der Eingang an Nicht-Gesicht
mitbringt (Blitze, Blenden, Figuren) und was die Ausgabe an Metadaten verliert, wird vor dem Einbau
abgefangen — gemessen, nicht erhofft. Die Mund-Ton-Korrelation beweist nichts, die Sichtprüfung schon.
Geändert: `.claude/skills/speaking-vsl-lipsync/` (neu, 6 Skripte; der Blitz-Erkenner fand am Lauf alle
8 Stellen, die zuvor von Hand repariert wurden) · `workflows/eleven-labs-ripping-agent.json` (Knoten
`lip-sync` zwischen Audio-Prüfung und Schnitt, Startfrage am Trigger) · `datenbanken/sp-learnings/learnings.md`
(35–38) · `03-FALLEN-UND-TRICKS.md` · `02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md` (D0).

**2 · Nachprüfung nach dem Lip-Sync-Farbfix: Farbstich im fertigen Bild stieg von 2,4 auf 5,1, auch am sauberen Clip**
Diagnose: Die Bildmontage schrieb RGB mit nur bt709-Tags — ffmpeg rechnet dann bt601. Vorher hob die unkennzeichnete kie-Ausgabe
das auf. Hin-/Rückweg gemessen: nur Tags → gelber Blitz Rot +2,0 / Blau −4,5; mit `out_color_matrix=bt709` neutral; Lesen ohne
`accurate_rnd` −2 Stufen.
Prinzip: Kennzeichnung ist Metadatum, Umrechnung ist Rechnung — beides muss stimmen; nach jedem Farb-Fix die ganze Kette messen.
Geändert: `.claude/skills/speaking-vsl-lipsync/scripts/lipsync_einbau.py`, `lipsync_farbe.py` · `datenbanken/sp-learnings/learnings.md` (39) · `03-FALLEN-UND-TRICKS.md`.

