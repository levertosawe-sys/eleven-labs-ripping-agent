---
name: singing-vsl-dach-lokalisierung
description: Eine ins Deutsche übersetzte (US-)Ad-Copy für den DACH-Markt (Deutschland, Österreich, Schweiz) aus der Sicht der Avatarin (der Zielkäuferin, wie die Copy sie zeichnet) prüfen — Ausgabe ist ein Befund in Stichpunkten für Viktors Entscheid, keine umgeschriebene Copy. Nutzen, wenn nach einer Übersetzung „lokalisieren", „Lokalisierung", „DACH", „passt das für unseren Markt?" fällt oder Viktor Feedback will, was an einer US-stämmigen Copy für DACH nicht funktioniert.
---

**`<projekte-db>`** steht in diesem Skill für die Projekte-Datenbank der LINIE, die
dieser Lauf fährt. Aufgelöst wird sie über die Registry `datenbanken/linien/linien.json`
(Feld `projektDb` der Zeile, z. B. `datenbanken/projekte-yuri`); welche Linie gilt, sagt
der Rip-Auftrag, sonst Viktor am Trigger. Nie aus Gewohnheit eine Linie annehmen —
es entscheidet die Quell-Brand des Videos (Packshot, Marke im Bild, Page-Farm-Register
der Brand-DBs). `datenbanken/projekte` (ohne Zusatz) ist eingefrorener Alt-Bestand —
dort entsteht nie ein neues Projekt.

**Ausnahme Sprech-Kette:** Trägt der Projekt-Ordner das Kürzel `EL` und liegt in
`datenbanken/sp-projekte` (z. B. `YUR 003 EL | 06.09.2026`), fährt der Lauf die
ElevenLabs-Kette. Dann ist `<projekte-db>` = `datenbanken/sp-projekte`, und die
Linien-Registry gilt für den Projekt-Ort nicht.

# Singing VSL DACH Lokalisierung

Ziel ist nicht die schönere Copy, sondern die Frage: Was funktioniert bei der
**Avatarin** nicht? Die Avatarin ist die Zielkäuferin, wie die Copy sie zeichnet —
Alter, Lebenslage, Milieu und Kernwunsch aus dem Text ablesen (Anrede,
Story-Figuren, Probleme) und in 1–2 Sätzen mit Textstellen-Beleg an den Kopf des
Befunds stellen. **Community-Transfer:** Trägt die Copy eine ethnische oder
kulturelle Community als tragende Schicht (Schwarze US-Frauen,
vietnamesisch-amerikanische Frauen …), wechselt beim Prüfen nur der Markt, nie
die Community: Die Avatarin ist dieselbe Community im DACH-Markt (Schwarze
Frauen in Deutschland, vietnamesische Community in Deutschland …) — nicht die
Mehrheits-Avatarin. Grund: Die Ad targetiert diese Community auch in DACH, und
die Bestands-Visuals zeigen sie weiter; eine Mehrheits-Avatarin prüfte an Bild
und Zielgruppe vorbei. Die Community steht mit im Avatarin-Kopf des Befunds. Geprüft wird mit IHREM Glauben und IHREM vorhandenen Wissen —
wie ein Copywriter denkt, nicht wie ein Lektor und nicht wie ein Jurist. Der Ad
soll so nah wie möglich am bewiesenen Original bleiben — geändert wird nur, was
bei der Avatarin wirklich nicht funktioniert. Der Befund trennt zwei Klassen:
**Anpassungen** (wendet die KI nach dem Gate ohne Rückfrage an — Viktor liest
sie nur zur Übersicht und kann jede per Nummer kippen) und **Entscheidungen**
(trifft Viktor selbst per Options-Wahl). Eine Empfehlung zu einer Entscheidung
gibt es NUR nach vorherigem Research — nie aus dem Bauchgefühl.

## Eingabe

Alle relativen Pfade in diesem Skill gehen vom Projektstamm aus — dem Ordner,
in dem `.claude/`, `datenbanken/`, `brands/` und `inbox/` nebeneinander liegen;
nur der Research-Helfer liegt bewusst außerhalb und steht darum absolut.

Die deutsche Übersetzung — als Datei
`<projekte-db>/<projekt>/<slug>-uebersetzung-<JJJJ-MM-TT>.md` (dort legt
`.claude/skills/singing-vsl-uebersetzung/SKILL.md` sie ab; `<projekt>` = der
Projekt-Ordner in der Projekte-Datenbank, z.B. `Singing VSL 006`; liegen
mehrere Übersetzungs-Dateien da, die vom Nutzer gemeinte nehmen, im Zweifel die
neueste und das kurz dazusagen) oder direkt im Chat. Liegt beides nicht vor,
die Übersetzung von Viktor erbitten und stoppen.

**Pflicht-Input Brand-Datenbank (vor dem Befund lesen):** Die Ziel-Brand steht
im `brand:`-Feld der `karte.md` des Projekt-Ordners (z. B. `LEI - Leichtkraut`).
Wo ihre Wissensdatenbank liegt, sagen zwei Register — welches gilt, hängt an der
Kette, die diesen Lauf fährt: Die Singing-Kette löst über das Feld `brandDb` der
Zeile dieser Linie in `datenbanken/linien/linien.json` auf, die Speaking-Kette über
die Spalte `brand_db` der Zeile dieser Brand in `datenbanken/sp-brands/daten.csv`.
Beide zeigen auf dieselben Brand-Datenbanken (z. B. `datenbanken/brand-yuri`); liegt
das Projekt in `datenbanken/sp-projekte`, gilt das Speaking-Register.
Dort in dieser Reihenfolge:
1. `lokalisierungs-log.md` — die Betriebsregeln stehen IN der Datei und gelten
   (Muster mit zwei gleichen Entscheidungen hintereinander werden angewendet
   statt gefragt; einmal Entschiedenes wird beim Fragen mitgenannt).
2. `Shopify Store/_STORE-INDEX.md` (+ verlinkte Seiten-MDs) — der Store ist der
   Maßstab: Ads müssen zu ihm passen. Hat die Brand-Datenbank keinen
   `Shopify Store/`-Ordner, entfällt die Prüf-Dimension „Store-Abgleich"; das
   gehört in den Befund-Kopf, damit niemand sie für stillschweigend bestanden hält.
3. `Research Ansammlung/_INDEX.md` — vorhandenes Zielgruppen-Wissen nutzen;
   fehlt eine Antwort, die der Befund braucht: researchen und als neues Doc +
   Index-Zeile in die Ansammlung zurückschreiben (Research-first-Regel der
   Brand-DATENBANK.md).
4. `kundensprache-de.md` — die belegten Wörter der deutschen Zielgruppe, falls
   die Datei existiert; geprüft wird damit in der Prüf-Dimension „Kundensprache".
   Hat die Brand-Datenbank die Datei nicht, entfällt diese Dimension ersatzlos.
Fehlt die Brand-Datenbank ganz (neue Brand), das offen im Befund-Kopf sagen und
ohne Store-Abgleich arbeiten — nicht raten.

Enthält die Datei den Abschnitt „Anmerkungen an die Lokalisierung", ist er
Pflicht-Input: Jede Anmerkung bekommt einen Platz im Befund — in ihrer
passenden Rubrik; fällt sie in keine Prüf-Dimension, in die Entscheidungen.
Fünf Ausnahmen: Anmerkungen zu Währungs-Beträgen fließen in die automatische
Euro-Umstellung (Prüf-Dimension „Stehende Entscheidung: Währung") statt in den
Befund; Anmerkungen zur Anrede gehen in die stehende Anrede-Entscheidung
(Prüf-Dimension „Stehende Entscheidung: Anrede") statt in den Befund; rein
rechtliche Anmerkungen und reine Wirkungs-Bedenken entfallen ersatzlos
(Kriterien in der Prüf-Dimension „Rechtliches und Wirkungs-Bedenken sind kein
Befund-Inhalt"); `Kundensprache:`-Anmerkungen protokollieren einen bereits
vollzogenen Wortebenen-Tausch und werden als EINE Sammelzeile unter „Geprüft,
passt" ausgewiesen (`Kundensprache: <Anzahl> Wörter getauscht — <je Tausch: R-Nummer
(Wort, M:SS)>`) statt einzeln in die Entscheidungen — sonst wächst jede Copy mit
vielen Tauschen zu einem Gate, das Viktor nicht mehr lesen kann. Wort und
Zeitstempel gehören in die Zeile, weil dieselbe R-Nummer mehrere Wörter belegen
kann und dasselbe Wort an mehreren Stellen steht; ohne sie ist ein gekippter Tausch
nicht auffindbar. Kippen kann Viktor sie trotzdem, den Wortlaut hält die
Übersetzungs-Datei. `Kundensprache-Lücke:`-Anmerkungen gehen dagegen in die
Prüf-Dimension „Kundensprache".

## Das Gate: erst Befund, dann Entscheid, dann erst Änderungen

Im ersten Durchgang wird **kein Wort der Copy geändert** — die Ausgabe ist
ausschließlich der Befund (Gerüst unten). Auch Anpassungen werden erst NACH dem
Gate eingearbeitet — der Unterschied ist nur, dass sie dort keine Bestätigung
brauchen (Schweigen = sie gelten; ein Einwand per Nummer kippt sie). Auch nicht:

- eine „schon lokalisierte Fassung nur zur Ansicht" beilegen,
- Formulierungen beim Zitieren glätten.

**Einordnung Anpassung vs. Entscheidung:** Ein Punkt ist nur dann eine
Anpassung, wenn (a) ein harter Fakten-/Logik- oder Store-Bruch vorliegt
(Widerspruch Copy ↔ Store-Doku, unmöglicher Anlass, kaputter Bezug) ODER
(b) das lokalisierungs-log der Brand dieselbe Frage-Art bereits gleich
entschieden hat ODER (c) ein Wort der Copy hat in der `kundensprache-de.md` der
Brand ein belegtes Kundenwort gleicher Bedeutung, und der Tausch lässt Satzbau,
Sinn und Zeilenlänge unverändert. Alles andere — jeder Punkt mit echtem
Ermessensspielraum — ist eine Entscheidung. Im Zweifel Entscheidung, nie
Anpassung; für (c) ist das kein Ermessen, weil die Datei das Wort und seinen
Beleg vorgibt — fehlt dort der Beleg, ist es kein Fall von (c).

Rote Flagge: Du tippst gerade am Copy-Text statt am Befund → stoppen, zurück
zum Befund. Der Grund für die Härte: Viktor liest die Copy selbst noch einmal
durch; eine vorab veränderte Fassung macht sein Lesen wertlos, weil er nicht
mehr sieht, was Original war und was Eingriff.

## Prüf-Dimensionen

Jeden Punkt der Copy dagegen halten. Für eigene Funde ist diese Liste
abschließend — was in keine Dimension fällt, ist Geschmack und bleibt
unangetastet (Anmerkungen aus der Übersetzung werden dagegen immer gelistet,
mit den fünf Ausnahmen aus „Eingabe"):

- **Store-Abgleich (Pflicht-Dimension — der Store ist der Maßstab):** Jeden
  Produkt-Fakt der Copy gegen die `Shopify Store/`-Doku der Ziel-Brand halten:
  Zutaten-/Kräuternamen (die Store-Schreibweise gewinnt — eine Ad, die die
  Zutaten anders nennt als der Store, bricht das Vertrauen beim Klick),
  Dosierung/Anwendungsform, Kur-/Garantie-Dauern, Zahlen-Claims, Produkt- und
  Markennamen. Widerspruch Copy ↔ Store = Anpassung mit dem Store-Wert als
  neuer Fassung; deckungsgleiche Fakten kommen als „Geprüft, passt" mit
  Store-Beleg. Nur Fakten, die der Store gar nicht kennt (reine Story-Elemente),
  bleiben Story.
- **Geo- und Markt-Bezüge:** Angebots-/Versand-Logik mit Länderbezug
  (z.B. „Angebote für die USA"). Standard-Vorschlag: Länderbezug ersatzlos
  streichen — nicht durch „DACH" o.Ä. ersetzen, das sagt im Werbedeutsch niemand.
- **Markennamen:** bleiben stehen. Entfernen oder Ersetzen nur, wenn Viktor es
  ausdrücklich verlangt.
- **Figuren-Namen:** Voreinstellung fürs Vorschlagen: sehr gängige Vornamen aus
  der Welt der Avatarin — bei der Mehrheits-Avatarin gängige deutsche Vornamen,
  bei einer Community-Avatarin (Community-Transfer, s. o.) die in dieser
  Community in DACH gängigen Vornamen (Research-first über die Brand-DB — nicht
  raten, welche Namen eine Community trägt). Die Avatarin soll beim Hören
  niemanden „fremd" einordnen müssen, und fremd heißt: fremd für IHRE Welt.
  Über die Läufe variieren statt immer dieselben Namen zu setzen. Als
  Entscheidung listen (A = Original, B = Tausch-Vorschlag nach Research). Zwei eigene Bedingungen:
  Ein Name, der ein Herkunfts- oder Autoritäts-Signal trägt (die koreanische
  Expertin einer K-Beauty-Story), bleibt unangetastet; ein Name, der in der
  Ziel-Welt ohnehin geläufig ist (Emma), braucht keinen Tausch-Vorschlag.
- **Stehende Entscheidung: Währung — wird nie gefragt.** Fremdwährungs-Beträge
  (Dollar, Pfund …) sind kein Entscheidungspunkt: Beim Bau der final-Datei wird
  jeder Betrag zu Euro — die Avatarin kauft und denkt in Euro. Werbe-Logik statt
  Wechselkurs: die glatte Zahl behalten (achtzig Dollar → achtzig Euro), nie
  kursgenau umrechnen — krumme Beträge wirken wie Rechen-Ergebnisse, nicht wie
  Preise; Story-Beträge und Offer-Beträge in derselben Größenordnung halten,
  sonst bricht die Story. Steht der echte DACH-Offer-Preis fest
  (`brands/<Brand>/CLAUDE.md` — `<Brand>` = Feld `brand:` aus der `karte.md`
  des Projekt-Ordners — oder Viktors Zuruf im Lauf), gewinnt der echte
  Preis vor der übernommenen Zahl; nennt keine der beiden Quellen einen Preis
  (auch wenn `karte.md`, ihr `brand:`-Feld oder die Brand-CLAUDE.md fehlen),
  bleibt die glatt übernommene Zahl. Währung taucht weder im Befund noch in der
  Gate-Nachricht auf — mit keinem Wort, auch nicht als Fußnote „wird automatisch
  umgestellt"; die Umstellung läuft still beim final-Bau. Einzig der
  Abschluss-Bericht danach nennt eine Zeile („<n> Beträge automatisch → Euro").
  Datums-, Zahlen- und Maß-FORMATE dagegen normal prüfen (DACH-Konventionen)
  und nur listen, wenn die Avatarin über einen Fakten-Bruch stolpert.
- **Kulturelle Anker — Funktions-Analyse mit Avatar-Brille.** Orte,
  Institutionen, Personen, Feiertage wirken nicht als Geografie, sondern über
  ihre FUNKTION: Reichtums-Signal, Autoritäts-Signal, Herkunfts-Authentizität,
  Vertrautheit. Je Anker drei Schritte:
  1. Funktion im Original benennen — was soll der Anker beim Publikum des
     ORIGINALS bewirken, was soll es glauben oder fühlen?
     (Beispiel aus echter Arbeit: „Beverly Hills" = „hier wohnen die Reichsten,
     also sind ihre Beauty-Geheimnisse die besten" — automatischer
     Produkt-Uplift. „Top-Modelagentur in LA" = Autoritäts-Beleg der Mentorin.)
  2. Avatar-Check: Löst derselbe Anker diese Funktion auch bei der Avatarin
     aus — mit ihrem Wissen, nicht mit deinem? Erst aus dem eigenen Weltwissen
     begründen; bleibt es Spekulation, research:
     `python3 /root/AWMS/_research/officialquasi-dach/ask_perplexity.py sonar-pro "<Frage>"`
     — die Frage nennt die Avatarin-Demografie + den Anker und fragt Bekanntheit
     und Assoziation in dieser Gruppe ab. Bricht der Helfer ab (Datei fehlt,
     Key fehlt, HTTP-Fehler): dieselbe Frage über das WebSearch-Tool. Liefert auch das
     nichts Belastbares: Anker in die Entscheidungen mit Vermerk „Avatar-Wirkung
     ungeklärt" (dann ohne Empfehlung).
  3. Ergebnis in den Befund: Trägt der Anker → „Geprüft, passt" mit benannter
     Funktion. Trägt er nicht oder wackelig → Anpassung (nur bei hartem Funktions-Bruch oder Log-Deckung) bzw. Entscheidung mit
     Optionen, die die FUNKTION im Kopf der Avatarin erfüllen — das darf ein
     anderer internationaler Anker sein (die Reichen-Funktion erfüllen für
     DACH oft Monaco oder St. Moritz besser als ein US-Vorort) oder eine
     funktionale Umschreibung („eine der reichsten Familien der Stadt").
  Signal-Anker nie mechanisch übersetzen (US-Stadt → deutsche Stadt): Der
  wörtliche Geografie-Tausch zerstört die Funktion, wenn die Avatarin mit dem
  Ersatz-Ort etwas anderes verbindet (Frankfurt = Banken, nicht
  Beauty-Reichtum).
  **Alltags-Anker sind die Gegenklasse und werden immer ersetzt.** Ein
  Alltags-Anker ist ein Ort oder Laden aus dem eigenen Leben der Avatarin: der
  Supermarkt, in dem sie einkauft, die Drogerie mit dem Regal, die Stadt, in der
  sie wohnt, die Herkunft der Pillen in diesem Regal. Seine Funktion ist
  gelebte Selbstverständlichkeit („das könnte ich sein, in meinem Laden") — und
  die kann ein fremder Name per Definition nicht erfüllen, auch wenn die
  Avatarin ihn aus Filmen kennt. Wiedererkennen ist nicht Erleben: Sie weiß, was
  Walmart ist, aber sie war nie dort, und der Satz verrät sich als Übersetzung.
  Darum stehen Alltags-Anker als **Anpassung** im Befund, nie als Entscheidung
  mit „Original lassen" — die deutsche Entsprechung ist nicht die Frage, sie ist
  die Antwort:

  | Alltags-Anker der Quelle | eingesetzt wird (Default zuerst) |
  |---|---|
  | Supermarkt-Kette (Walmart, Target, Costco) | Lidl; passt die Story-Region besser zu einer anderen, dann Aldi, Rewe, Edeka oder Kaufland |
  | Supplement-/Drogerie-Kette (GNC, Vitamin Shoppe, CVS) | „jeder Supplement-Shop"; nur wenn die Zeile einen Laden zum Betreten braucht, dm |
  | Herkunft im Satz („US Supplements", „amerikanische Tabletten") | „deutsche Supplements" (parallel gebaut zum Original) |
  | Einkaufs- oder Weg-Ort der Story (Wohnort, Nachbarschaft, Bundesstaat) | die ortlose Fassung („eine Klinik zwei Städte weiter"); eine benannte deutsche Stadt nur, wenn die Zeile den Ort wirklich braucht |
  | Alltags-Maße (Meilen, Fuß, Pfund, Gallonen) | Kilometer, Meter, Kilo, Liter — mit glatter Zahl wie bei der Währung, nicht exakt umgerechnet |

  Die Liste ist nicht abschließend: Entscheidend ist der Test „kommt dieser Ort
  im Alltag der Avatarin wirklich vor?", nicht ob er auf der Liste steht. Für
  Alltags-Maße gilt sie auch dann, wenn die Avatarin über kein Fakt stolpert —
  das ist die Ausnahme von der Maß-Formate-Regel der Dimension Fakten und
  Angaben. **Beträge bleiben außen vor:** Währung fällt unter die stehende
  Entscheidung Währung und taucht im Befund nicht auf, auch nicht als Alltags-Anker.
  **Zugehörigkeits-Aussagen sind keine Alltags-Anker.** Sagt die Copy nicht, WO
  jemand einkauft, sondern WER er ist („alle andalusischen Männer über 60",
  „bei uns im Süden"), ändert ein Ortstausch die Erzählstimme und nicht die
  Kulisse — solche Stellen gehen als **Entscheidung** in den Befund, mit der
  ortlosen Fassung („Männer über 60, die ich kenne", „hier bei uns") als
  Empfehlung. Trägt ein Ort dagegen Weg-Aufwand oder Fach-Autorität („dafür
  fuhr ich 30 Meilen"), läuft er über die Funktions-Analyse dieser
  Prüf-Dimension, nicht über die Tabelle.
  **Kippt Viktor eine Alltags-Anker-Anpassung**, gilt sein Wort wie überall —
  aber nicht als „Original lassen" ohne Wortlaut: dann seinen eigenen Wortlaut
  erfragen (Popup mit der betroffenen Zeile) und die Entscheidung als eigene
  Zeile ins `lokalisierungs-log.md` schreiben, damit der nächste Lauf sie kennt.
  **Diese Regel schlägt das Log.** Trägt das `lokalisierungs-log.md` der Brand
  für einen Alltags-Anker ein Muster „bleibt Original", wird es nicht angewendet
  — ein Muster kann eine Abkürzung sein, aber keine Regel aufheben. Im
  Abschluss-Bericht steht dann eine Zeile „Log-Muster <Punkt> nicht angewendet:
  Alltags-Anker".
  **Ein anderes Ausland ist keine Lokalisierung.** Trägt die Quelle spanische
  oder italienische Orte, werden auch die deutsch — sonst wandert der
  Fremdheits-Effekt nur, statt zu verschwinden. **Figurennamen bleiben dagegen
  bei ihrer Dimension:** Sie sind Entscheidungen mit „Original lassen" als
  Option (Prüf-Dimension Figuren-Namen), weil ein Name die Figur benennt und
  nicht ihre Umgebung — ein Miguel darf in Deutschland leben. Ein Name wird nur
  dann zum Alltags-Anker, wenn die Zeile ihn als Herkunfts-Aussage benutzt
  („typisch für uns Andalusier").
  **Herkunftsangaben werden als Ganzes geprüft, nicht nur ihr Substantiv.** Wer
  bei „voller US Supplements" nur fragt, ob „Supplements" das richtige Wort ist,
  übersieht das Land davor. Darum vor dem Schreiben des Befunds ausführen:
  `python3 scripts/anker_scan.py <projekte-db>/<projekt>/<slug>-uebersetzung-<JJJJ-MM-TT>.md`
  — findet Ketten-Namen, Herkunfts-Bauteile, fremde Währung und Maßeinheiten
  zeilengenau, damit die Suche nicht am Augenschein hängt. Exit 1 heißt Funde:
  jeder davon wird eine Anpassung. Bricht das Skript mit Exit 2 ab (Pfad falsch,
  Datei nicht UTF-8), erst den Pfad aus dem Abschnitt Eingabe prüfen und erneut
  ausführen — ohne Scan keinen Befund schreiben, sonst fehlt genau die Klasse
  Funde, die man mit den Augen übersieht. Was das Skript nicht abdeckt, sagt es
  selbst: Personen- und Ortsnamen einer fremdsprachigen Quelle prüft die
  Prüf-Dimension Figuren-Namen.
  **Gegenprobe vor dem Abliefern:** Trägt eine Entscheidung im Befund einen
  Laden-, Orts- oder Herkunfts-Anker mit Option „Original lassen", ist sie
  falsch eingeordnet — sie gehört nach oben zu den Anpassungen. Ausreden, die
  hier auftauchen und alle nicht zählen: „die Kulisse IST ein US-Markt" (ein
  Grund, die Kulisse zu tauschen, nicht das Wort zu behalten) · „im Log stand
  mehrfach ‚passt'" (frühere Fälle waren Atmosphäre, kein genannter fremder
  Laden) · „der Satzkontext erklärt die Funktion selbst" (er erklärt sie, aber
  sie gehört ihr nicht).
  Bei einer Community-Avatarin (Community-Transfer, s. o.) erfüllen Ersatz-Anker
  die Funktion in IHRER Community im DACH-Markt: Ein Schwarzer US-Promi-Anker
  wird zum Schwarzen Promi-Anker, den die Community in DACH kennt (Research-first
  über die Brand-DB) — kein Mehrheits-Promi, der die In-Group-Funktion verliert.
- **Stehende Entscheidung: Anrede — wird nie gefragt.** Die Zuschauer-Anrede
  ist Du (Gattung: Frau erzählt Frau); Figuren innerhalb der Story behalten
  das Register ihrer Szene — das ist KEINE Abweichung. Nur wenn die
  Zuschauer-Anrede selbst vom Du abweichen soll, entscheidet das die KI und
  weist es im Abschluss-Bericht in einer Zeile aus. Im Befund taucht die
  Anrede nicht auf.
- **Kundensprache (nur wenn die Brand-Datenbank eine `kundensprache-de.md` hat):**
  Drei Funde. Beleg für (a) und (b) ist ein wörtliches Kundenzitat mit R-Nummer —
  aus den Zitat-Abschnitten der Datei oder über die Beleg-Spalte ihrer Tabelle,
  nie aus den Ableitungs-Absätzen („Konsequenz", „Deutung"). Ohne solches Zitat
  gibt es keinen Fund (a) und keinen Fund (b).
  (a) *Wort fehlt:* Die Copy nennt einen Zustand, für den die Datei ein belegtes
  Kundenwort führt, in einer Übersetzer-Formulierung, die dort nicht vorkommt →
  **Anpassung** nach (c) der Einordnung oben, neue Fassung = das Kundenwort.
  Zeilen, die die Datei als „kein Tausch-Kandidat" oder „kein Wortebenen-Tausch"
  ausweist, liefern keinen Fund (a) — ihr Inhalt kann aber (b) tragen. Ebenso
  liefert eine Stelle keinen Fund (a), wenn die Übersetzung dort eine
  `Kundensprache-verworfen:`-Anmerkung trägt: Dort wurde das Wort bewusst abgelehnt,
  weil es den Sprachfluss oder das Zeitfenster gesprengt hätte. Es wieder einzusetzen
  hieße, diese Entscheidung ungefragt zu kippen.
  (b) *Belegter Skepsis-Widerspruch:* Die Copy behauptet etwas, das ein
  wörtliches Kundenzitat der Datei direkt bestreitet (etwa ein Wirkungs-Versprechen
  ohne Grenze gegen Zitate, die an der Dauer messen) → **Entscheidung** für
  Viktor, weil eine Grenze die Aussage ändert. Das R-Zitat IST der Research-Beleg
  der B-Empfehlung; zusätzlicher Research ist dafür nicht nötig.
  (c) *Lücke:* Eine `Kundensprache-Lücke:`-Anmerkung der Übersetzung oder eine
  Tabellenzeile, die die Datei ausdrücklich als Lücke führt → **Entscheidung ohne
  Empfehlung**, Vermerk „Kundensprache-Lücke": Für diesen Zustand hat die
  Zielgruppe kein belegtes Wort, die Copy steht wörtlich übersetzt da. Hier fehlt
  der Beleg per Definition — das ist der Punkt, nicht ein Mangel des Fundes.
  Findet sich zu einem Punkt weder ein Zitat noch eine ausgewiesene Lücke, bleibt
  er ein Wirkungs-Bedenken und entfällt nach der Dimension unten.
- **Rechtliches und Wirkungs-Bedenken sind kein Befund-Inhalt.** Abmahnbarkeit,
  Wettbewerbs- und Werberecht, Health-Claims: Das prüft Viktors Anwalt am
  fertigen Text. Und ob ein Claim übertrieben wirkt, zu viel Kauf-Druck macht
  oder „nicht gut ankommen könnte", beurteilt dieser Skill ebenfalls nicht —
  nichts wird gelistet oder geändert, nur weil die KI etwas nicht gut findet;
  solche Wirkungs-Urteile fällen Mensch und Anwalt am fertigen Text. Im Befund
  steht dazu nichts, auch nicht als Entscheidung oder Fußnote. Für Anmerkungen
  aus der Übersetzung gilt: „Rein rechtlich" ist eine Anmerkung, die ohne
  Rechts-Begriffe keinen Inhalt mehr trägt — sie entfällt ersatzlos;
  Misch-Anmerkungen (Marketing-Kern + rechtlicher Beigeschmack) behalten ihren
  Marketing-Kern und gehen in dessen Rubrik, nur das Rechts-Vokabular fällt weg.
  Rote Flaggen: Du tippst „abmahnbar", „UWG", „rechtlich riskant" — oder „wirkt
  übertrieben", „könnte unangenehm wirken", „die Kundin ist … müde" → Zeile
  streichen. Ausgenommen sind allein die Funde (b) und (c) der Prüf-Dimension
  „Kundensprache": (b) hängt an einem wörtlichen Kundenzitat mit R-Nummer, nicht am
  Urteil der KI; (c) meldet eine Lücke, die die Datenbank selbst ausweist. Alles
  andere aus dieser Richtung fällt unter diese Regel.

Maßstab bei jedem Fund: Stolpert die Avatarin über einen Fakten- oder
Logik-Bruch (unmöglicher Anlass, kaputter Bezug, Anker ohne Funktion in ihrem
Kopf)? Nur das ist ein Befund. Bloß „anders, als du es formuliert hättest" oder
eine vermutete Wirkung („zu aggressiv", „unglaubwürdig") ist keiner. Im
Zweifel Entscheidung, nie Anpassung.

## Ausgabe: der Befund

Als Datei `<projekte-db>/<projekt>/<slug>-befund-<JJJJ-MM-TT>.md`
ablegen (Projekt/Slug/Datum wie die Übersetzungs-Datei) UND vollständig im
Chat zeigen. Exakt dieses Gerüst —
Punkte mit Einzelstelle tragen ihren Zeitstempel, copy-weite Punkte das
Präfix `gesamt:` (dann ohne Zitat); bei kulturellen Ankern nennt der Halbsatz
die Funktion, Research-Belege in Klammern dahinter (Quelle/Kernaussage):

```markdown
## Lokalisierungs-Befund: <slug>
**Avatarin (aus der Copy belegt):** <1–2 Sätze: wer sie ist — mit Textstellen>

**Anpassungen (wende ich an — kippe einzelne per Nummer):**
1. (M:SS) „<Zitat>" → <neue Fassung> — <Grund: Store-/Fakten-Bruch ODER „Log: so entschieden in <Projekt>" ODER „Kundensprache: <R-Nummer>">
2. …

**Entscheidungen (deine Wahl per Nummer + Buchstabe):**
1. (M:SS) „<Zitat>"
   - A: Original lassen
   - B: <Vorschlag> — Empfehlung, weil <Research-Ergebnis in einem Halbsatz (Quelle)>
   - C: <Alternative> — <was dafür spricht>
2. (M:SS) „<Zitat>" — Kundensprache-Lücke: kein belegtes Kundenwort, steht wörtlich übersetzt da
   - A: so lassen
   - B: <eigener Wortlaut von dir>
3. …

**Geprüft, passt (Beleg des Store-, Anker- und Kundensprache-Abgleichs, keine Aktion nötig):**
- Kundensprache: <Anzahl> Wörter getauscht — <R-Nummer (Wort, M:SS); …>
- <Anker/Element> — <Funktion + warum sie trägt, ein Halbsatz>
```

Vor jeder B-Empfehlung einer Entscheidung steht Research (Reihenfolge:
Research-Ansammlung der Brand → Perplexity-Helfer → WebSearch — wie in der
Prüf-Dimension „Kulturelle Anker" beschrieben); der Research-Beleg steht in
Klammern hinter der Empfehlung. Liefert der Research nichts Belastbares, wird
KEINE Empfehlung markiert — die Optionen stehen dann gleichwertig da, mit dem
Vermerk „Research unergiebig".

Danach stoppen und auf Viktors Entscheid warten. Bricht die Session hier ab,
trägt der Wiedereinstieg sich selbst: Befund-Datei plus Übersetzungs-Datei im
Projekt-Ordner — beim nächsten Lauf die Befund-Datei erneut zeigen, nicht neu
erfinden.

## Nach dem Entscheid

Viktors Antwort fällt selten als reines „passt" — die Formen und ihre Wege:

- **Anpassungen:** gelten ohne Bestätigung. Nur eine ausdrücklich gekippte
  Nummer („Anpassung 2 nicht") bleibt Original; sein eigener Wortlaut schlägt
  den Vorschlag.
- **Entscheidungen:** je Nummer die gewählte Option (A/B/C oder eigener
  Wortlaut) einarbeiten. **Unbeantwortete Entscheidungen = Option A (Original
  lassen)** — im Abschluss-Bericht je Nummer als „unbeantwortet → Original"
  nennen, nicht stillschweigend anders entscheiden. Diese Voreinstellung darf
  nie einen Alltags-Anker erreichen: Laden-, Orts- und Herkunfts-Anker stehen
  als Anpassung im Befund (siehe Prüf-Dimension Kulturelle Anker) und haben
  damit kein „Original", das ein Schweigen behalten könnte.
- **Eigene Änderungswünsche** → übernehmen; sie schlagen jede Option.
- **Gekippte Kundensprache-Tausche:** Die Sammelzeile unter „Geprüft, passt"
  nennt die R-Nummern; kippt Viktor eine davon, wird dieses Wort beim final-Bau
  auf die wörtliche Fassung aus der Übersetzungs-Datei zurückgesetzt (dort steht
  sie in der `Kundensprache:`-Anmerkung im Feld `wörtlich`) und im
  Abschluss-Bericht als zurückgesetzt ausgewiesen.

**Log-Pflege (direkt nach dem Entscheid, vor dem final-Bau):** Jede Frage-Art,
die Viktor an diesem Gate entschieden hat (auch „bleibt Original"-Entscheide),
als Zeile ans `lokalisierungs-log.md` der Ziel-Brand anhängen (Format steht in
der Datei). Aus dem Log angewendete Muster werden NICHT erneut geloggt — sie
stehen schon drin; der Abschluss-Bericht weist sie als „aus Log übernommen" aus.

Eingearbeitet wird in einer neuen Datei
`<projekte-db>/<projekt>/<slug>-final-<JJJJ-MM-TT>.md` — sie entsteht
auch dann, wenn nichts einzuarbeiten war (dann als Kopie der
Übersetzungs-Blöcke), damit die fertige Copy immer am selben Ort liegt.
Beim Bau der final-Datei werden zusätzlich die stehenden Entscheidungen
angewendet — Währung → Euro nach den Regeln der Prüf-Dimension, auch ohne dass
sie im Befund standen — und im Abschluss-Bericht in einer Zeile ausgewiesen.
Rekonstruierte oder von Viktor frei zugerufene Zeilen halten dabei die
Sprechzeit-Grenze ihres Zeitfensters ein (Regel und Grund:
`.claude/skills/singing-vsl-augen-check/SKILL.md`, Abschnitt „Entscheiden").
Inhalt: nur die Zeitstempel-Blöcke der Copy — der Anmerkungs-Abschnitt wandert
nicht mit (Offenes gehört in den Abschluss-Bericht, nicht in die Copy).
Übersetzungs- und Befund-Datei bleiben als Beleg liegen. Projekt/Slug/Datum
wie bei der Übersetzungs-Datei; kam die Copy nur aus dem Chat: erst das
Projekt anlegen wie in `<projekte-db>/DATENBANK.md` beschrieben
(Naming + Doppel-Rip-Schutz), `<slug>` = 2–4 kleine Wörter mit Bindestrichen
aus Marke/Hook, Datum = heute.

Erfolg = die final-Datei existiert und enthält alle freigegebenen Punkte.
Der Abschluss-Bericht ist die Chat-Nachricht direkt nach dem Bau der
final-Datei: je freigegebenem Punkt kurz bestätigen, wo er gelandet ist, die
Zeile zu den stehenden Entscheidungen („<n> Beträge → Euro"; weicht die
Zuschauer-Anrede vom Du ab, dazu eine Anrede-Zeile), und offen
gebliebene Punkte beim Namen nennen.
