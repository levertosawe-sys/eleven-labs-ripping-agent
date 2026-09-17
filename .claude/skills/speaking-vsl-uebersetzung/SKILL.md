---
name: speaking-vsl-uebersetzung
description: "Ein englisches VSL-Transkript in deutsche Sprech-Copy übersetzen, die in ihre Original-Zeitfenster passt — Budget je Clip in Wörtern pro Sekunde gerechnet, Hook-Mechanik erhalten, Produktnamen unangetastet. Vierter Schritt der Speaking-VSL-Kette zwischen Clip-Karte und DACH-Lokalisierung; auch nutzen, wenn Viktor sagt „übersetz die Copy", „mach die deutsche Fassung", „Sprech-Budgets", „passt das in die Zeit?"."
---

# Speaking VSL Übersetzung — die Zeit ist die Grenze

Anders als bei Text-Copy gibt es hier eine harte Wand: Jede deutsche Zeile muss in
das Zeitfenster ihres Original-Clips passen. Deutsch ist beim Sprechen länger als
Englisch — wer eins zu eins übersetzt, produziert eine Spur, die den Schnitt sprengt
oder die Stimme hetzen lässt. Darum wird nicht satzweise übersetzt, sondern
**fensterweise gegen ein Budget**.

## Eingabe

Alle Pfade vom Projektstamm aus (der Ordner mit `.claude/` und `datenbanken/`).

- Das englische Transkript `<projekte-db>/<projekt>/<slug>-original-<JJJJ-MM-TT>.md`
- Die Clip-Karte aus `singing-vsl-clip-karte` — sie liefert die Fenstergrenzen.
  Fehlt sie, sind die `(M:SS)`-Stempel des Transkripts die Fenster.
- Fehlt eins von beidem: bei Viktor erbitten und stoppen. Nie aus dem Gedächtnis.

## Das Budget

**Deutscher TTS-Sprechfluss trägt 2,2–2,5 Wörter pro Sekunde.** Darunter klingt es
zäh, darüber hetzt die Stimme und die Captions laufen dem Bild davon.

Das Band ist gemessen, nicht geschätzt: Eine deutsche ElevenLabs-Stimme trug in
einem vollen Lauf real 2,3 W/s; wer mit 2,6–3,2 W/s plant, produziert rund 20 %
Überlänge. Andere Stimmen können abweichen: im Zweifel EINEN Block erzeugen, messen,
und das Band für diesen Lauf daraus ableiten — das kostet 20 Sekunden und spart einen
kompletten Neu-Durchgang.

Die Formel je Fenster, in dieser Reihenfolge:
`(Sekunden − 0,45) × Basis-Rate × 1,12 = Ziel-Wortzahl`
- 0,45 s = Atem-Reserve je Blockkante (`--atem` der Montage; ohne sie kleben die Sätze).
- Basis-Rate = Ruhelage der Brand-Stimme bei Tempo 1,0, Feld `sprechrate_wps` im
  Stimmen-Register `datenbanken/stimmen/daten.csv` (deutsche v3-Stimmen: ~2,0 W/s).
- 1,12 = Tempo-Lift der Montage (`tools/sp/sprechspur.py montage --tempo`, Skill
  `sprech-watch`, Abschnitt Tempo). Das Band 2,2–2,5 W/s oben ist also das, was
  NACH dem Lift auf der Spur liegt (2,0 × 1,12 = 2,24) — nicht nochmals multiplizieren.
Beim Bau grob dagegen zählen, am Ende exakt (`wc -w` je Block).

**Vollständigkeit vor Budget.** Jeder Satz des Originals wird gesprochen —
verdichtet, nie gestrichen. Grund: Ein gestrichener Satz ist für Viktor ein
Übersetzungsfehler („du hast einen Satz einfach nicht übersetzt"), auch wenn das
Budget ihn erzwungen hat; die Bestätigung „Ja, du hast richtig gehört" gehört zur
Hook-Mechanik, nicht zum Füllmaterial. Sitzt das Budget nach der ganzen Kürzungs-
Leiter unten nicht, ist das eine Gate-Frage an Viktor (welcher Satz fällt), keine
stille Entscheidung der Übersetzung.

| Ausrede beim Übersetzen | Warum sie nicht zählt |
|---|---|
| „Das Bild trägt die Bestätigung, der Satz kann weg" | Das Bild trägt die Szene, der Satz die Mechanik — beides ist Original. |
| „Das Band ist gemessen, mehr geht nicht" | Das Band gilt bei Tempo 1,0. Tempo-Lift und wandernde Marken kommen VOR jeder Streichung. |
| „Ich weise es im Protokoll aus" | Ausweisen macht eine Streichung sichtbar, nicht zulässig. |

**Zahlwörter zählen als Wörter, sprechen sich aber wie Sätze.** „12-Milligramm-Astaxanthin"
ist EIN Wort in der Zählung und sechs Silben im Ohr. Trägt ein Fenster Zahlen, Einheiten
oder Komposita, wird sein Budget um ein Wort je zusammengesetztem Zahlwort gesenkt —
sonst sitzt die Tabelle und die Spur läuft trotzdem über.

Gekürzt wird in dieser Reihenfolge — jede Stufe erst, wenn die davor nicht reicht:
1. **Füllwörter und Doppelungen** („ganz", „wirklich", „auch")
2. **Relativsätze zu Nominalphrasen** („das Taubheitsgefühl, das dich kaum laufen
   lässt" → „das Taubheitsgefühl beim Laufen") — spart am meisten, kostet am wenigsten
3. **Kurzformen** („Operation" → „OP", spart zwei Silben)
4. **Marken wandern lassen** — Reserve, die erst `sprech-watch` zieht: Bei
   Voice-over ohne Lippen-Sync verteilt der Marken-Planer die Blockgrenzen nach
   gemessener Sprechdauer, ein Block leiht sich Sekunden vom Nachbarn. Die
   Übersetzung merkt nur an, welche Blöcke über Budget liegen.
5. **Tempo-Lift 1,12** — steckt schon in der Formel; mehr gibt es nicht.
6. **Ein Satz muss fallen** → Gate-Frage an Viktor mit dem Kandidaten und dem
   Budget-Beleg (Wortzahl je Block gegen die Formel); bis zum Entscheid bleibt der
   Satz drin, die Montage meldet die Überlänge — das ist der Beleg.

## Das erste Gesetz: natürlich fließen schlägt Strukturtreue

Die Singing-Linie übersetzt strukturgleich am englischen Satzbau entlang (1:1-Optik,
damit die Clips hart am Original geschnitten werden können). **Diese Regel gilt hier
NICHT.** In der Speaking-Kette ist die Stimme formbar (Clip vor Audio — die Sprechspur
passt sich den Clips an), also entscheidet der deutsche SPRACHFLUSS: Sätze so bauen,
wie ein Muttersprachler sie sagen würde, nicht wie das Englische sie gebaut hat.
Wörtlichkeit ist nur Mittel, nie Ziel.

Referenzpaar (aus echtem Gate-Befund — die linke Fassung fiel durch):
- ✗ strukturnah: „Deine Nieren warnen nie. Melden sie sich, ist es zu spät."
- ✓ natürlich: „Deine Nieren geben dir nie Warnsignale. Aber wenn sie es tun,
  dann ist es zu spät."

Zweites Referenzpaar (Viktors Befund ARE 002 EL, 04.09.2026 — die linke Fassung fiel durch,
obwohl sie im Budget saß):
- ✗ budget-getrimmt: „Wer das kalkuliert hat, fliegt Montag raus."
- ✓ Viktors Fassung: „Wer dieses Angebot erstellt hat, wird von uns gefeuert."
Daraus das Gesetz: **Fluss vor Budget.** Erst die natürliche Zeile schreiben, dann messen.
Sitzt sie nicht, zuerst die Blockgrenzen prüfen — über B-Roll-Strecken ohne Lippen-Sync
(Haut-Animationen, Produkt-3D) dürfen die Marken wandern (`marken.json` neu verteilen);
erst danach kürzen. Was nie geht: Wörter streichen, bis der Satz nach Telegramm klingt.

Drittes Referenzpaar (Viktors Befund an einem Hook — die linke Fassung saß im Budget,
er hörte sie als „kein Mensch redet so"):
- ✗ passiv und verknappt: „Moment, richtig gehört? Das Lager wird geräumt, weil die
  Verpackung neu wird."
- ✓ Viktors Fassung: „Warte, hab ich das richtig gehört? Die räumen ihr Lager, weil
  sie die Verpackung ändern. Ja, du hast richtig gehört."
Daraus zwei Regeln: Sprech-Deutsch hat handelnde Personen als Subjekt („die räumen",
„sie ändern") — Passiv („wird geräumt", „wird neu") klingt nach Amt; und ein
Original-Satz, der die Mechanik trägt (Ungläubigkeit → Bestätigung), bleibt als
eigener Satz stehen.

Prüf-Frage je Zeile: Würde eine deutsche Sprecherin das GENAU SO sagen? Klingt eine
Zeile nach Übersetzung, wird sie umgebaut — das Budget wird danach geprüft, nicht
als Ausrede fürs Verknappen auf Kosten des Flusses benutzt.

## Die vier Gesetze

1. **Hook-Mechanik schlägt Wörtlichkeit.** Ein Negations-Hook („Do not try X if you
   have Y") ist eine getarnte Empfehlung. Wörtlich übersetzt kippt er ins echte
   Abraten. Übersetzt wird die MECHANIK, nicht der Satz.
2. **Produkt- und Markennamen bleiben unangetastet.** Der Tausch ist Sache der
   Lokalisierung — hier steht noch der Name der Quelle.
3. **Beträge bleiben in der Quellwährung.** Die Euro-Umstellung ist eine stehende
   Entscheidung der Lokalisierung, keine Übersetzungs-Aufgabe.
4. **Fachbegriffe nach Sprechbarkeit wählen, nicht nach Präzision.** „rehydrate your
   discs" → „befeuchtet die Bandscheiben"; „rehydrieren" ist näher, klingt aber
   gesprochen nach Beipackzettel.

Anrede ist **Du** — Gattung ist „Frau erzählt Frau". Figuren innerhalb der Story
behalten das Register ihrer Szene.

## Kundensprache — die belegte Antwort auf die Prüf-Frage

Für manche Marken lässt sich „Würde eine deutsche Sprecherin das GENAU SO sagen?"
belegen statt raten. Führt die Brand-Datenbank der Ziel-Brand eine
`kundensprache-de.md` (Pfad: Spalte `brand_db` der Zeile dieser Brand in
`datenbanken/sp-brands/daten.csv`), wird sie vor dem Übersetzen gelesen. Darin stehen
die Wörter, mit denen die deutsche Zielgruppe dieser Produktkategorie über das Produkt
redet, jedes mit der Kennung des Kundenzitats, aus dem es stammt.

Sie liefert **Vokabular, keine Sätze**: Trägt ein Kundenwort dieselbe Bedeutung wie die
Übersetzer-Formulierung, wird es gesetzt; der Satzbau folgt weiter dem Fluss-Gesetz, und
der Inhalt bleibt unangetastet.

**Ein Tausch kostet nie Substanz.** Passt ein Kundenwort nicht ins Fenster, bleibt die
wörtliche Fassung stehen — ein Kundenwort löst nie eine Marken-Verschiebung, nie eine
Kürzung und nie eine Gate-Frage aus. Es ist Feinschliff, kein Anspruch. Fluss geht ihm
ebenfalls vor: Ein Kundenwort, das die Zeile hölzern macht, fällt raus, selbst wenn es
kürzer wäre.

Gleiche Wortzahl heißt nicht gleiche Dauer: „aufgepolstert" ist ein Wort wie „prall",
aber vier Silben statt einer. In kurzen Fenstern zählt das wie ein zusammengesetztes
Zahlwort (siehe Budget). Die Tabelle rechnet in Silben, weil sie auch die Song-Kette
bedient — hier entscheidet die Wörter-pro-Sekunde-Formel dieses Skills, die Silbenspalte
ist nur ein Hinweis auf die Sprechdauer.

Kein Tausch in vier Fällen, die zu drei verschiedenen Vermerken führen:
- **Deckung:** Die Übersetzung trifft das Kundenwort ohnehin. Kein Vermerk.
- **Kein Beleg:** Das Wort steht nicht in der Tabelle. Kein Vermerk.
- **Gesperrte Zeile:** Die Tabellenzeile ist als „kein Tausch-Kandidat" oder „kein
  Wortebenen-Tausch" gekennzeichnet. Vermerk ohne Stichwort, als normale Anmerkung.
- **Lücke:** Die Tabelle führt für dieses Konzept ausdrücklich eine Lücke. Vermerk mit
  dem Stichwort `Kundensprache-Lücke:` — die Lokalisierung erkennt diesen Fall nur daran.

**Vor dem Tausch das Zitat gegenlesen.** Die R-Nummer neben dem Wort (Form `R042`) zeigt
auf ein Zitat im Vollbestand, dessen Pfad die Datei im Kopf nennt. Trägt das Zitat das
Wort nicht, findet kein Tausch statt; die wörtliche Fassung bleibt stehen. Der Grund:
Die Tabelle wird von Hand erweitert, und ein ungedecktes Wort landete sonst über die Copy
in einer geschalteten Anzeige. Im Übersetzungs-Lauf wird die Tabelle nicht verändert —
sie gehört der Brand-Datenbank und wird von mehreren Ketten gelesen.

Drei Anmerkungs-Zeilen, alle unter „Anmerkungen an die Lokalisierung" (Ausgabe, Punkt 5).
Dorthin, weil die Lokalisierung ausschließlich diesen Abschnitt als Pflicht-Input liest —
unter „Übersetzer-Entscheidungen" sähe sie keinen einzigen Tausch:
```
- (M:SS) Kundensprache: „<Wort im Original>" · wörtlich „<wörtliche Übersetzung>" → „<Kundenwort>" (<R-Nummer>)
- (M:SS) Kundensprache-Lücke: „<Wort>" — kein belegtes Kundenwort, wörtlich übersetzt
- (M:SS) Kundensprache-verworfen: „<Kundenwort>" (<R-Nummer>) — <Fluss | Silbenlast im Fenster>, wörtliche Fassung bleibt
```
Die dritte Zeile ist Pflicht, sobald du ein Kundenwort bewusst ablehnst. Ohne sie meldet
die Lokalisierung dasselbe Wort als fehlend und setzt es ohne Rückfrage wieder ein.

Fehlt die Datei, wird ohne sie übersetzt.

## Ausgabe

`<projekte-db>/<projekt>/<slug>-uebersetzung-<JJJJ-MM-TT>.md`, und vollständig im Chat
zeigen. Aufbau:

1. **Kopfzeile** — Vorlage, Sprache-Budget gesamt, Stand
2. **Die Copy als ZWEI BLÖCKE, nie verschachtelt:** zuerst ein Block mit allen
   englischen Original-Zeilen (Überschrift `## Original (EN)`), darunter ein Block mit
   allen deutschen Zeilen (Überschrift `## Deutsch (Sprech-Copy)`). Beide Blöcke tragen
   dieselben `(M:SS)`-Stempel in derselben Reihenfolge — so findet das Auge jede Zeile
   im anderen Block über den Stempel. Nur die deutschen Zeilen beginnen mit `(`, damit
   der Längen-Check sie zählt; die englischen stehen unter ihrer eigenen Überschrift.
   Grund: Viktor vergleicht am Gate Original und Übersetzung — eine deutsche Copy allein
   ist für ihn nicht prüfbar, und zeilenweise verschachtelte EN/DE-Paare werden bei zwölf
   Blöcken zu einer unlesbaren Wand. Dasselbe Zwei-Block-Format gilt für jede Copy-Anzeige
   im Chat bis zur Audio-Prüfung (dort als zwei Code-Blöcke).
   Die Clip-Bindung (`Cxxx-Cyyy` je Block) steht als eigene Zeile unter den Blöcken, nicht
   in den Copy-Zeilen.
3. **Budget-Kontrolle** — Tabelle je Clip: Fenster · Sekunden · EN-Wörter ·
   DE-Wörter · W/s · sitzt ja/nein. Ein Fenster am Rand bekommt eine konkrete
   Kürzungs-Alternative als Fließtext darunter, keine vage Warnung.
4. **Übersetzer-Entscheidungen** — je Entscheidung ein Stichpunkt mit Begründung.
   Hier gehören Hook-Mechanik, Kurzformen, Fachbegriff-Wahl und alles hinein, was
   ein späterer Leser sonst für einen Fehler halten würde.
5. **Anmerkungen an die Lokalisierung** — was dort geprüft werden muss: kulturelle
   Anker, Zahlen mit Marktbezug, Produktfakten ohne Beleg. Die Lokalisierung liest
   diesen Abschnitt als Pflicht-Input. Pflicht wird er, sobald ein Kundensprache-Fall
   eingetreten ist; dann tragen seine Zeilen die Form aus dem Abschnitt
   „Kundensprache":
   ```
   - (M:SS) Kundensprache: „<Wort im Original>" · wörtlich „<wörtliche Übersetzung>" → „<Kundenwort>" (<R-Nummer>)
   - (M:SS) Kundensprache-Lücke: „<Wort>" — kein belegtes Kundenwort, wörtlich übersetzt
   - (M:SS) Kundensprache-verworfen: „<Kundenwort>" (<R-Nummer>) — <Fluss | Silbenlast im Fenster>, wörtliche Fassung bleibt
   ```
   Gab es keinen solchen Fall oder führt die Brand-Datenbank keine
   `kundensprache-de.md`, entfallen diese Zeilen.

Danach übernimmt `singing-vsl-dach-lokalisierung`.

## Fallen aus echten Läufen

- **Kurze Fenster sind gefährlicher als lange.** Ein 4-Sekunden-Fenster verzeiht kein
  einziges Wort zu viel; ein 10-Sekunden-Fenster schluckt zwei. Zuerst die kurzen bauen.
- **Aufzählungen sind der beste Kürzungs-Hebel.** „bei ausstrahlenden Beinschmerzen,
  bei steifem unterem Rücken, und bei diesem Taubheitsgefühl" → „bei Beinschmerzen,
  steifem Rücken, diesem Taubheitsgefühl": dreimal die Präposition gespart, Inhalt
  vollständig erhalten.
- **Der Gesamtschnitt lügt.** 2,9 W/s über die ganze Ad kann ein Fenster mit 3,6
  verstecken. Immer je Fenster prüfen, nie nur gesamt.
