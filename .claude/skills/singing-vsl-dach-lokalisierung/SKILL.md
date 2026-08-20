---
name: singing-vsl-dach-lokalisierung
description: Eine ins Deutsche übersetzte (US-)Ad-Copy für den DACH-Markt (Deutschland, Österreich, Schweiz) aus der Sicht der Avatarin (der Zielkäuferin, wie die Copy sie zeichnet) prüfen — Ausgabe ist ein Befund in Stichpunkten für Viktors Entscheid, keine umgeschriebene Copy. Nutzen, wenn nach einer Übersetzung „lokalisieren", „Lokalisierung", „DACH", „passt das für unseren Markt?" fällt oder Viktor Feedback will, was an einer US-stämmigen Copy für DACH nicht funktioniert.
---

**`<projekte-db>`** steht in diesem Skill für die Projekte-Datenbank der
Linie: `datenbanken/projekte-lymphoria` (Ziel-Brand LEI - Leichtkraut) oder
`datenbanken/projekte-quasi` (Ziel-Brand QUA - Quasi). Der Rip-Auftrag nennt
den Ordner ausdrücklich; fehlt er, entscheidet die Ziel-Brand des Projekts.
`datenbanken/projekte` (ohne Zusatz) ist eingefrorener Alt-Bestand — dort
entsteht nie ein neues Projekt.

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
im `brand:`-Feld der `karte.md` des Projekt-Ordners (z. B. `LEI - Leichtkraut`);
ihre Wissensdatenbank liegt unter `/root/AWMS/datenbanken/brand-<name-klein>/`
(LEI - Leichtkraut → `brand-leichtkraut`, QUA - Quasi → `brand-quasi`). Dort in
dieser Reihenfolge:
1. `lokalisierungs-log.md` — die Betriebsregeln stehen IN der Datei und gelten
   (Muster mit zwei gleichen Entscheidungen hintereinander werden angewendet
   statt gefragt; einmal Entschiedenes wird beim Fragen mitgenannt).
2. `Shopify Store/_STORE-INDEX.md` (+ verlinkte Seiten-MDs) — der Store ist der
   Maßstab: Ads müssen zu ihm passen.
3. `Research Ansammlung/_INDEX.md` — vorhandenes Zielgruppen-Wissen nutzen;
   fehlt eine Antwort, die der Befund braucht: researchen und als neues Doc +
   Index-Zeile in die Ansammlung zurückschreiben (Research-first-Regel der
   Brand-DATENBANK.md).
Fehlt die Brand-Datenbank ganz (neue Brand), das offen im Befund-Kopf sagen und
ohne Store-Abgleich arbeiten — nicht raten.

Enthält die Datei den Abschnitt „Anmerkungen an die Lokalisierung", ist er
Pflicht-Input: Jede Anmerkung bekommt einen Platz im Befund — in ihrer
passenden Rubrik; fällt sie in keine Prüf-Dimension, in die Entscheidungen.
Vier Ausnahmen: Anmerkungen zu Währungs-Beträgen fließen in die automatische
Euro-Umstellung (Prüf-Dimension „Stehende Entscheidung: Währung") statt in den
Befund; Anmerkungen zur Anrede gehen in die stehende Anrede-Entscheidung
(Prüf-Dimension „Stehende Entscheidung: Anrede") statt in den Befund; rein
rechtliche Anmerkungen und reine Wirkungs-Bedenken entfallen ersatzlos
(Kriterien in der Prüf-Dimension „Rechtliches und Wirkungs-Bedenken sind kein
Befund-Inhalt").

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
entschieden hat. Alles andere — jeder Punkt mit echtem Ermessensspielraum —
ist eine Entscheidung. Im Zweifel Entscheidung, nie Anpassung.

Rote Flagge: Du tippst gerade am Copy-Text statt am Befund → stoppen, zurück
zum Befund. Der Grund für die Härte: Viktor liest die Copy selbst noch einmal
durch; eine vorab veränderte Fassung macht sein Lesen wertlos, weil er nicht
mehr sieht, was Original war und was Eingriff.

## Prüf-Dimensionen

Jeden Punkt der Copy dagegen halten. Für eigene Funde ist diese Liste
abschließend — was in keine Dimension fällt, ist Geschmack und bleibt
unangetastet (Anmerkungen aus der Übersetzung werden dagegen immer gelistet,
mit den zwei Ausnahmen aus „Eingabe"):

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
     `python3 /Users/yuviktor2004/AWMS/_research/officialquasi-dach/ask_perplexity.py sonar-pro "<Frage>"`
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
  Nie mechanisch übersetzen (US-Stadt → deutsche Stadt): Der wörtliche
  Geografie-Tausch zerstört die Funktion, wenn die Avatarin mit dem Ersatz-Ort
  etwas anderes verbindet (Frankfurt = Banken, nicht Beauty-Reichtum).
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
  streichen.

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
1. (M:SS) „<Zitat>" → <neue Fassung> — <Grund: Store-/Fakten-Bruch ODER „Log: so entschieden in <Projekt>">
2. …

**Entscheidungen (deine Wahl per Nummer + Buchstabe):**
1. (M:SS) „<Zitat>"
   - A: Original lassen
   - B: <Vorschlag> — Empfehlung, weil <Research-Ergebnis in einem Halbsatz (Quelle)>
   - C: <Alternative> — <was dafür spricht>
2. …

**Geprüft, passt (Beleg des Store-/Anker-Abgleichs, keine Aktion nötig):**
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
  nennen, nicht stillschweigend anders entscheiden.
- **Eigene Änderungswünsche** → übernehmen; sie schlagen jede Option.

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
