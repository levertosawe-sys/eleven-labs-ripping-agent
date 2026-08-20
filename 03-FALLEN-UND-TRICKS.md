# Fallen und Tricks

Gesammelt aus dem Serienbetrieb der Singing-Schwester (dutzende Läufe) — hier stehen nur
die, die für die Speaking-Linie gelten. Jede Falle wurde mindestens einmal wirklich
bezahlt; keine ist theoretisch.

---

## Vorstufe

- **Augen-Check VOR dem Caption-Entfernen.** Der Augen-Check liest die eingebrannten
  EN-Captions als Wort-Beweis. Wer erst Vmake laufen lässt, hat den Beweis gelöscht.
- **Vmake immer auf der glatten Quelle, nie auf einem geschnittenen Render.** Das
  Inpainting nutzt Nachbar-Frames — auf der ungeschnittenen Quelle rekonstruiert es
  sichtbar besser, und EIN Quell-Lauf deckt alle späteren Re-Renders ab. Danach
  Frame-Zahl gegen die Config prüfen und Schlieren-Scan ansehen, nicht durchwinken.
- **Quell-Hash zuerst.** Vor jeder Projekt-Anlage den Hash des Quellvideos gegen die
  Projekte-Datenbank prüfen — sonst rippt man dieselbe VSL zweimal und merkt es erst
  beim Upload.
- **Captions sind Wort-Autorität, nie Timing-Autorität.** Zeiten kommen IMMER aus der
  gemessenen Tonspur (Scribe), nie aus dem, was wann eingeblendet ist.

## Übersetzung & Copy

- **Sprechzeit ist nicht Wanduhr-Zeit.** Budgets und Prüfungen rechnen gegen die
  Wanduhr des Videos (Clip-Fenster), nicht gegen aufsummierte Sprechdauer — sonst
  verwirft man gute Takes oder quetscht gute Zeilen.
- **Abweichungs-Protokoll ist Pflicht, nicht Kür.** Jede Kürzung/Verschiebung gegenüber
  der wortgetreuen Fassung wird benannt — die Abnahme (D2) prüft GENAU an diesen Stellen
  mit Beweis-Frames.
- **Markt-Regeln sind Betreiber-Gesetze, nicht Vorlagen-Gesetze.** Beispiele aus dem
  DACH-Betrieb: Garantie-Versprechen der US-Vorlage nie ungeprüft übernehmen, US-Feste
  (Thanksgiving) durch lokale ersetzen — samt aller Folge-Aufzählungen im Text.

## Stimme

- **Klon-Tabu.** Die Original-Sprecherstimme der Quelle wird NIE nachgebaut. Punkt.
  Rechtsrisiko + Kontorisiko (an demselben ElevenLabs-Konto hängt die halbe Kette).
- **Zahlen, Preise, Markennamen ins Aussprache-Lexikon.** „39,90 €“, Rabatt-Codes und
  Kunstnamen sind die häufigsten Stolperstellen jeder Text-zu-Stimme — einmal je Brand
  pflegen, jeder Lauf profitiert.
- **Tempo über die Stimm-Einstellungen regeln, nicht über Abspiel-Beschleunigung.**
  Beschleunigtes Playback klingt sofort künstlich; die Stimme selbst kann schneller
  oder langsamer SPRECHEN.
- **Master-Gesetz.** Die abgenommene Sprechspur wird nie mehr angefasst — jede spätere
  Korrektur ersetzt die betroffene Zeile im Bau-Schritt und läuft dann NEU durch
  Schnitt und Abnahme.

## Prüfer & Maschinen-Ohr

- **Nur Anker-bestandene Modelle dürfen urteilen.** Das Maschinen-Ohr wird an zwei
  validierten Referenz-Clips kalibriert; ein Modell, das die Anker nicht besteht,
  urteilt nicht — egal wie neu es ist.
- **Maschinen-Gates stoppen den BAU, nie den Lauf.** Befund fixen oder als benannten
  Trade-off dokumentieren und weiterarbeiten. Auf den Menschen wartet nur ein
  Mensch-Gate (Markt-Entscheid, Stimmen-Wahl, End-Sichtung).
- **Nach 3 Fehlversuchen: Trade-off benennen statt endlos würfeln.** Ein dokumentierter
  Kompromiss am Mensch-Gate ist ehrlicher als eine stille Endlos-Schleife.

## Schnitt

- **Verlust-Gate: kein Clip fällt stumm.** Wenn der Schnitt einen Quell-Clip komplett
  verliert, ist das ein Befund, kein Schulterzucken.
- **Nach jeder Zeilen-Operation am Ton: Schnitt + Render zwingend NEU.** Der Schnitt
  hängt am Wort-Cache; ein veränderter Ton mit altem Schnitt ist eine kaputte Ad, die
  auf den ersten Blick heil aussieht.

## Übergabe & Upload

- **Der Lauf endet mit dem Ein-Prompt IM CHAT.** Nie mit „das Paket liegt bereit“ —
  der Mensch kopiert einen Block und fängt an, ohne eine Datei zu öffnen.
- **Übergabe-Pfade zeigen auf die dauerhafte Werkstatt, nie auf einen Wegwerf-Worker.**
  Gemessener Fall bei der Schwester: der Prompt trug die IP eines Miet-Workers, der
  Minuten später gelöscht war — der Abhol-Befehl lief ins Leere.
- **Anzeigen entstehen IMMER pausiert.** Scharf schalten ist Handarbeit des Menschen im
  Ads Manager — ohne Ausnahme.
- **Beim Skript-Portieren auf Zahlen-Literale achten.** Ein Suchen-und-Ersetzen der
  Projektnummer hat bei der Schwester schon Kommazahlen in Skripten verstümmelt
  (0.031 → 0.029). Nach jedem Port die Konstanten prüfen.

## Methode

- **Feedback wandert in den Workflow, nie nur ins Projekt.** Das ist Use and Break:
  jeder Fund wird als Regel in Skill/Workflow-Datei festgeschrieben, damit er beim
  nächsten Lauf automatisch gilt. Ein Fix, der nur im Projekt landet, ist beim
  nächsten Projekt wieder da.
- **Nichts „fertig“ melden ohne Zahlen-Beleg.** Abdeckung, Abgleich-Werte und
  Prüf-Ergebnisse werden vorgezeigt (Datei nennen), nicht behauptet.
