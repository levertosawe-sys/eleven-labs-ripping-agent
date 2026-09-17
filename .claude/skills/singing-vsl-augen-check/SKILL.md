---
name: singing-vsl-augen-check
description: "Verdachtsstellen eines frischen EN-Transkripts per Augen-Beweis gegen die eingebrannten Original-Captions des Quellvideos klären — Widersprüche, Zahlen-/Namens-Garbles und Abweichungen von früheren Ads derselben Brand werden durch Anschauen entschieden, nie durch Raten (/watch-Prinzip: Frames ums Zeitfenster ziehen, Caption lesen). Pflicht-Schritt der Singing-VSL-Kette zwischen Transkription und Übersetzung; auch nutzen, wenn Viktor sagt „check das im Video nach", „schau dir die Stelle an", „was sagen die Untertitel", „da widerspricht sich was im Transkript", „ist das wirklich so gesagt worden?"."
---

**`<projekte-db>`** steht in diesem Skill für die Projekte-Datenbank der LINIE, die
dieser Lauf fährt. Aufgelöst wird sie über die Registry `datenbanken/linien/linien.json`
(Feld `projektDb` der Zeile, z. B. `datenbanken/projekte-rovina`); welche Linie gilt, sagt
der Rip-Auftrag, sonst Viktor am Trigger. Nie aus Gewohnheit die Quasi-Linie annehmen —
es entscheidet die Quell-Brand des Videos (Packshot, Marke im Bild, Page-Farm-Register
der Brand-DBs). `datenbanken/projekte` (ohne Zusatz) ist eingefrorener Alt-Bestand —
dort entsteht nie ein neues Projekt.

# Singing VSL Augen-Check — Captions schlagen Raten

Scribe hört gesprochene Zahlen und Namen gelegentlich falsch — und eine Copy, die
sich selbst widerspricht, fällt sonst erst am Gate auf oder nie. Die Quell-Ads
tragen fast immer eingebrannte englische Captions, und für WÖRTER gilt:
**Die Caption ist die Wahrheit.** Sagt eine lesbare Caption etwas anderes als
Scribe, gewinnt die Caption — auch wenn Scribes Fassung plausibler klingt, denn
Scribe rät aus dem Klang, die Caption lag beim Bau der Ad als Text vor. Ganz
caption-basiert zu arbeiten wäre zu langsam und zu teuer — Scribe bleibt der
Motor für Timing und Masse, die Captions sind der Doppel-Check an den
Verdachtsstellen. Für TIMING gilt die Caption nie — die Zeitachse bleibt Scribes
Messung, hier wird kein Stempel angefasst.

**Gotcha — Auto-Captions:** Manche Quellen brennen maschinell erzeugte Captions
ein. Erkennungszeichen: Cards, die selbst kein Wort ergeben („CAN SHOOTICLES"),
oder Cards, die Scribes Fehler fast wortgleich wiederholen. Eine LESBARE Card
bleibt auch bei solchen Quellen die Wahrheit; eine Garble-Card ist keine
Autorität, sondern ein Symptom: Liefern Scribe und Caption an derselben Stelle
VERSCHIEDENEN Unsinn, ist die Tonspur der Quelle selbst defekt → Stelle als
„Quelle defekt" ausweisen (im Anmerkungs-Format der Ausgabe ist das ein
„ungeklärt"-Eintrag mit dem Vermerk „Quelle defekt"), beide Garbles wörtlich
zitieren und die Zeile nach der Eigene-Logik-Stufe in „Entscheiden" selbst
rekonstruieren — offen gekennzeichnet, nie stillschweigend. Packshots
und Props im Bild (Produktbox, Preisschild) zählen als stärkster Wort-Beleg von
allen.

## Eingabe

Alle relativen Pfade gehen vom Projektstamm aus — dem Ordner, in dem `.claude/`,
`datenbanken/` und `brands/` nebeneinander liegen.

- Das frische Transkript
  `<projekte-db>/<projekt>/<slug>-original-<JJJJ-MM-TT>.md` (liefert
  `.claude/skills/singing-vsl-transkription/SKILL.md`); `<projekt>`, `<slug>`,
  `<JJJJ-MM-TT>` aus seinem Dateinamen übernehmen, nie neu bilden.
- Das Quellvideo: die Datei aus dem laufenden Chat (voller Pfad). Ist der Pfad
  nicht mehr greifbar (neue Session), Viktor um den vollen Pfad bitten — welcher
  Film gemeint ist, sagt die Quelle-Zeile des Transkript-Kopfs (Dateiname).
- Die Brand des Projekts steht im `brand:`-Feld der `karte.md` im selben
  Projekt-Ordner — sie scoped den Brand-Gedächtnis-Vergleich unten.

## Verdachtsstellen sammeln (dieser Scan ist abschließend)

1. **Interne Widersprüche:** alle Zahlen, Eigennamen und Produkt-Fakten des
   Transkripts herausschreiben und gegeneinander halten. „Derselbe Fakt" heißt:
   gleiche Größe am gleichen Gegenstand (zweimal der Dalton-Wert der Maske,
   zweimal ihre Gramm-Füllmenge) — verschiedene Größen oder Gegenstände
   (Story-Zahl vs. Produkt-Zahl) sind kein Widerspruch. Unsicher, ob dieselbe
   Größe gemeint ist? Dann Verdacht — anschauen ist billig, ein übersehener
   Widerspruch teuer. Ein interner Widerspruch erzeugt ZWEI Verdachtsstellen:
   je Stempel ein Fenster und ein Anmerkungs-Eintrag, die aufeinander verweisen.
2. **Brand-Gedächtnis:** dieselben Fakten gegen frühere Transkripte derselben
   Brand halten:
   `grep -i "<fakt-wort>" "<projekte-db>/"*/*-original-*.md`
   — die Treffer tragen den Datei-Pfad: Treffer aus dem eigenen Projekt-Ordner
   ignorieren (das frische Transkript ist kein Beleg für sich selbst), fremde
   Ordner über das `brand:`-Feld ihrer karte.md zuordnen — nur Treffer
   derselben Brand zählen. `<fakt-wort>` = das markante Wort des Fakts; Zahlen
   in Wort- UND Ziffernform greppen („one hundred ninety-five" UND „195").
   Weicht der neue Wert von allen früheren Belegen ab, Verdacht.
3. **Anmerkungen der Transkription:** jede dort als akustisch unsicher markierte
   Stelle (Markennamen, Garbles, per Fenster nachgetragene Lücken).
4. **Kontext-Brüche:** Wörter oder Phrasen, die im Satz keinen Sinn ergeben
   (typisches Garble-Muster von Sprach-Engines).

Mehr wird nicht gesucht — ohne Verdacht keine Frame-Suche über die ganze Ad.
Keine Verdachtsstelle gefunden → unter „## Anmerkungen" des Transkripts eine
Zeile „Augen-Check: keine Verdachtsstellen" und der Schritt ist fertig.

## Je Verdachtsstelle: anschauen statt raten

1. **Fenster bestimmen:** Zeitstempel der Stelle −2 s bis +4 s; ein rechnerisch
   negativer Fensterstart (früher Stempel) wird auf 0 geklemmt — das gilt auch
   fürs Nachfassen in Schritt 4. Der Stempel ist nur der Block-Anfang: liegt das strittige Wort weiter hinten im Block, die
   Fensterlage schätzen (Wortanteil vor der Stelle × Blockdauer). Ein Fehlgriff
   ist unkritisch — das Nachfassen in Schritt 4 fängt ihn; das Rate-Verbot gilt
   für FAKTEN, nicht für die Fensterlage.
2. **Frames ziehen** (das /watch-Prinzip, gezielt; eine Handvoll Einzel-Frames
   ist I/O-Arbeit und läuft lokal — Rechenort-Regel:
   `.claude/skills/sa-resync-singing-ad/SKILL.md` §Rechenort).
   **Wer viele Frames zieht und liest, tut das in einem Subagenten:** Ab etwa einem
   Dutzend Bildern je Lauf gehören Ziehen und Ablesen in einen eigenen Agenten, der
   die abgelesenen Captions als Text zurückgibt — der Hauptlauf entscheidet damit,
   ohne die Bilder selbst zu tragen. Das ist reine Beweis-Sammlung: Die Caption sagt,
   was sie sagt, da ist nichts zu urteilen. Grund und Ausnahmen: Grundsatz P5 in
   `.claude/skills/brand-swipe-start/references/swipe-dateien.md`. Bei einer
   Verdachtsstelle mit zwei, drei Frames lohnt der Agent nicht — dann selbst ansehen.
   ```bash
   ffmpeg -y -v error -ss <fensterstart-sekunden> -t 6 -i "<quellvideo>" -vf "fps=1,scale=640:-1" "/tmp/augencheck_<m-ss>_%02d.jpg"
   ```
   640 px Breite reicht zum Lesen, `<m-ss>` = Stempel mit Bindestrich (z. B. `2-48`).
   **Das Raster hängt an der Caption-Art:** Stehende Captions (ganze Zeile,
   sekundenlang sichtbar) erwischt `fps=1` sicher. Trägt die Quelle eine
   KARAOKE-Wortspur — ein einzelnes Wort je Karte, das im Takt des Gesprochenen
   wechselt —, steht jede Karte nur rund 0,3 s: dort mit `fps=5` ziehen, sonst trifft
   das Raster das strittige Wort nur zufällig. Welche Art vorliegt, zeigt der erste
   gezogene Frame; danach gilt dasselbe Raster für alle weiteren Fenster.
   Bricht ffmpeg ab
   oder entstehen 0 Frames → Meldung wörtlich zeigen, Pfad und Stempel prüfen
   (Stempel jenseits der Videolänge?), einmal korrigiert erneut versuchen;
   scheitert auch das → Stelle „ungeklärt" + Befund an Viktor.
3. **Frames mit dem Read-Werkzeug öffnen** und die eingebrannte Caption
   WÖRTLICH ablesen.
4. **Entscheiden:**
   - Caption zeigt den Fakt klar → im Transkript NUR die strittigen Wörter
     korrigieren (nichts glätten, nichts umformulieren) + Anmerkung mit Beleg.
     Rote Flagge: „Scribe hat es aber deutlich gehört" — zählt nicht, die
     Caption gewinnt.
   - Bestätigen die Captions bei einem internen Widerspruch BEIDE Stellen (das
     Original widerspricht sich wirklich selbst) → nichts korrigieren, beide
     Einträge „bestätigt", und der Widerspruch wandert als Anmerkung an die
     Lokalisierung — entschieden wird er an Viktors Gate.
   - Keine lesbare Caption im Fenster → einmal nachfassen:
     `-ss <stempel−4> -t 8` mit `fps=2` erneut ziehen. Bleibt es leer → Stelle
     bleibt wie gehört, Anmerkung „ungeklärt".
   - Caption ist lesbar, ergibt aber keinen Sinn → erst den Auto-Caption-Verdacht
     prüfen (Gotcha oben; bei großen Brands seltener, aber möglich). Erst wenn
     die Caption absolut keinen Sinn ergibt — die Eigene-Logik-Stufe: eine Zeile
     bauen, die in die ganze Story passt, in der Anmerkung als Rekonstruktion
     mit beiden Zitaten (Scribe + Caption) ausweisen; bestätigt wird sie am
     Lokalisierungs-Gate, das ohnehin folgt.
   - Sprechzeit-Grenze jeder selbst gebauten Zeile: Sie muss in ihr Zeitfenster
     passen — Fensterlänge = Abstand zwischen den belegten Nachbar-Stempeln; in
     ein 2-Sekunden-Loch gehört keine 10-Sekunden-Zeile. Grund: Der Resync
     schneidet die Clips auf genau diese Zeitachse — eine zu lange Zeile bricht
     später den Schnitt.
   - Caption-Schreibweise eines Markennamens widerspricht `brands/` → `brands/`
     gewinnt in unserer Copy; die On-Screen-Schreibweise kommt als Anmerkung dazu.
5. `/tmp/augencheck_*`-Frames danach löschen — Beleg ist die Anmerkung mit
   Fensterzeit und Caption-Zitat.

## Ausgabe

Direkt im Transkript `<slug>-original-<JJJJ-MM-TT>.md`: die korrigierten
Copy-Zeilen, und unter „## Anmerkungen" je Verdachtsstelle GENAU EIN Eintrag:

```markdown
- (M:SS) Augen-Check <korrigiert|bestätigt|ungeklärt>: Caption „<wörtliches Zitat>" (Fenster M:SS–M:SS) — <korrigiert von „…" zu „…" / bestätigt wie gehört / bleibt wie gehört>.
```

Fehlt dem Transkript der Abschnitt „## Anmerkungen", ihn ans Datei-Ende setzen.
Erfolg = jede gesammelte Verdachtsstelle hat ihren Eintrag mit Ausgang — erst
dann übernimmt `.claude/skills/singing-vsl-uebersetzung/SKILL.md` das Transkript.

„Quelle ohne Captions" ist ein eigener, prüfbarer Fall: die Videolänge einmal
messen (`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "<quellvideo>"`),
dann drei Stichproben-Frames bei ~5 %, ~50 % und ~90 % der Länge ziehen —
zeigen sie NIRGENDS eine Caption → eine
Gesamt-Anmerkung „Augen-Check entfällt (Quelle ohne Captions)", alles bleibt wie
gehört. Zeigt die Ad anderswo Captions, ist eine leere Einzelstelle immer
„ungeklärt", nie „ohne Captions".
