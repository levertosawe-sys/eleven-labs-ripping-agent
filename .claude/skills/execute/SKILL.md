---
name: execute
awms: system
description: Einen AWMS-Workflow ausführen — workflows/<name>.json als Arbeitsanweisung Knoten für Knoten abarbeiten, Gate-Dokumente schreiben und selbst entscheiden statt zu warten (Halt nur bei unbeantwortbaren Fragen), Datenbanken laut Kanten lesen/schreiben. Läuft automatisch im Hintergrund an, sobald Gaylord einen Workflow meint — „mach X", „starte X", „führe X aus" — oder den Trigger eines Workflows auslöst (z.B. eine Datei reinwirft, die zu einem Trigger passt) oder fragt, wie er einen Workflow laufen lässt. Kein Befehl, den Gaylord rufen muss.
---
# execute — ein Workflow-Lauf (System-Skill)

Die Workflow-Datei ist die Arbeitsanweisung. Du bist der Operator; Gaylord entscheidet, was nur er
entscheiden kann — alles andere entscheidest du und legst es ihm vor.

1. **Workflow laden:** Lies `workflows/<name>.json`. Ist unklar, welcher gemeint ist:
   EINE Frage mit der Namensliste. Passt eine reingeworfene Datei zum Trigger eines
   Workflows, nimm den und leg los.
1b. **Rechenort wählen — vor dem ersten Knoten.** Frag Gaylord, WO dieser Lauf
   rechnet, und leg ihm dafür die ECHTE Lage vor (nie aus dem Gedächtnis — Rechner
   kommen und gehen): welche Maschinen gerade verfügbar sind, je mit Name · Ort ·
   Adresse · Status, dazu immer die Option „lokal". Gaylords Wahl gilt für den
   GANZEN Lauf: Heavy-Arbeit (ffmpeg, Whisper, Demucs, Renders, große Downloads)
   läuft auf dem gewählten Rechner; APIs und Schlüssel bleiben lokal. Die Wahl in
   das Lauf-Artefakt schreiben, das der Workflow ohnehin anlegt (z.B. die
   Projekt-Karte) — so kennt ein Wiedereinstieg sie; legt der Workflow keins an,
   gilt die Wahl für diese Session und wird beim Wiedereinstieg neu gefragt. Nennt
   ein Skill der Kette selbst einen Rechenort, gewinnt Gaylords Wahl aus dieser
   Frage. Gibt es keine Fernrechner, die Frage trotzdem stellen — dann mit den
   Optionen „lokal" und „Adresse von dir".

2. **Kette abarbeiten**, vom Trigger aus, Knoten für Knoten entlang der `haupt`-Kanten:
   - **skill:** Lies dessen SKILL.md und führe die Prozedur aus. Eingabe = Ergebnis des
     Vorgängers. Ausgabe sauber an den Nächsten weiterreichen.
   - **datenbank-Kanten:** `liest` → hole dir die Daten von dort (Vertragskarte beachten).
     `schreibt` → lege das Ergebnis DORT ab, nicht nur in den Chat.
   - **gate:** Gate-Dokument vollständig schreiben und vorlegen — aber **nicht warten**.
     Der Lauf nimmt für jede Frage die belegte beste Option und arbeitet weiter; er hält
     nur an, wo eine Frage aus dem Material nicht beantwortbar ist. Siehe „Gates: entscheiden
     statt warten" unten. Was der Lauf selbst entschied, steht gesammelt am letzten Gate.
   - **tool:** Laut README aufrufen. Existiert (noch) kein Code, ehrlich sagen und Gaylord
     das Nötige für den Hand-Schritt übergeben (z.B. fertiges Skript für seine App).
   - **Knoten mit `bedingung`:** Das Feld nennt ein Merkmal und die Datei, in der es
     steht (z.B. `Registry: sprache = de` → Feld `sprache` im Eintrag der Linie in
     `datenbanken/linien/linien.json`). Genau dort nachlesen, nie aus dem Gedächtnis
     oder aus dem Gesprächsverlauf entscheiden. Trifft das Merkmal zu → Knoten normal
     ausführen. Trifft es nicht zu → Knoten überspringen und im Lauf-Bericht mit Merkmal
     und gelesenem Wert nennen. Nennt eine `bedingung` mehrere Merkmale (mit UND
     verbunden), müssen alle zutreffen; Merkmale, die in keiner Datei stehen, sondern im
     Auftrag (dem Text, der den Trigger auslöste), liest du dort nach. Steht die Datei nicht da oder fehlt das Feld, ist das
     kein „trifft nicht zu": STOPP und Gaylord fragen — sonst fällt ein halber
     Sprachzweig lautlos aus dem Lauf.
   - **Geist (Datei fehlt):** Nicht stillschweigend improvisieren. Sag „Knoten X ist noch
     ungebaut", mach den Schritt einmalig MIT Gaylord von Hand — und schlag danach in
     einem Satz vor, ihn per /skillcatch zu bauen.
3. **Verzweigungen:** beide Zweige abarbeiten; der Merge-Knoten bekommt beide Ergebnisse.
   **Mehrere Läufe** (z.B. zwei Ads): nacheinander, je Lauf ein sauberer Durchgang.
3b. **Verbrauch dem Workflow zuschreiben** (für die AWMS-Seite „Nutzung → Top-Workflows"):
   - Rufst du im Lauf instrumentierte Software (B-Roll-Sourcer, Musik-Finder,
     Voice-Trimmer), setze vorher die Umgebungsvariable `AWMS_WORKFLOW=<workflow-name>` —
     deren Clients stempeln sie dann selbst in die Logs.
   - Feuerst du bezahlte Generierungen DIREKT aus dem Chat (Bild- oder Video-Jobs
     an einen Anbieter), hänge je Aufruf eine Zeile an `AWMS/.usage/direkt.jsonl`:
     `{"ts":"<ISO-Zeit>","workflow":"<workflow-name>","anbieter":"<anbieter>","modell":"<modell-id>","menge":<Credits>}`.
     `anbieter`/`modell` so schreiben, wie der Aufruf sie nennt (z.B. `kie.ai` /
     `kling-3.0/video`) — sonst ist später nicht auswertbar, was das Geld gekostet hat.
   Kein Pflege-Ritual für Gaylord — das erledigt die KI beim Lauf.
4. **Lauf-Bericht am Ende, kurz:** was produziert wurde, was in welche Datenbank
   geschrieben wurde, an welchen Stellen gestoppt/offen. Keine Schönfärberei.

Nie: ein Gate-Dokument weglassen · einen Selbst-Entscheid verschweigen · fehlende Bausteine
verschweigen · Ergebnisse nur im Chat lassen, wenn eine schreibt-Kante eine Datenbank nennt ·
den Workflow „verbessern", ohne dass Gaylord es entschieden hat (Änderungswünsche → Datei
ändern, das ist ein eigener Schritt).

## Gates: entscheiden statt warten

Ein Lauf steht nicht still, weil niemand am Rechner sitzt. Warten kostet mehr Zeit als jeder
Rechenschritt — gemessen an vollständigen Läufen entfallen auf das Warten am Gate mehrere
Stunden je Ad, auf die Maschine selbst weniger. Darum:

**Das Gate-Dokument wird immer geschrieben und vorgelegt.** Es entfällt nie, es wird nie
gekürzt. Was sich ändert, ist nur: Der Lauf hält danach nicht an, sondern entscheidet und
arbeitet weiter.

### Die Testfrage: Steht die Antwort irgendwo?

Vor jeder Gate-Frage genau eine Prüfung — **ist sie aus dem Material beantwortbar?**
Material sind: die Rangfolge oder Voreinstellung im zuständigen Skill, die Brand- und
Projekt-Datenbanken, die Projekt-Karte, und ein Log-Muster (dieselbe Frage wurde schon
zweimal gleich entschieden).

| | |
|---|---|
| **Antwort steht im Material** | Der Lauf nimmt sie, vermerkt sie als Selbst-Entscheid und arbeitet weiter. Kein Halt. |
| **Antwort steht nirgends — jede Wahl wäre geraten** | STOPP und fragen. Nur hier. |

Beispiele für *steht im Material*: welches Werkzeug ein Fund bekommt (die Rangfolge steht im
Skill) · ob eine Stelle angefasst wird (die Regel steht im Skill) · eine Formulierung, für die
das Lokalisierungs-Log schon zweimal dasselbe entschieden hat · ein Preis, der in den
Zielmarkt-Fakten steht.

Beispiele für *steht nirgends*: ob ein Objekt im Bild überhaupt das fremde Produkt ist
(Grenzfall — wer das rät, tauscht vielleicht das eigene Produkt weg) · eine Offer-Zahl, die
keine Datenbank führt · zwei Lesarten eines Auftrags, die zu verschiedenen Produkten führen.
**Hier wird nicht geschätzt.** Eine geratene Antwort auf eine unbeantwortbare Frage ist kein
Tempo, sondern eine Ad, die nochmal gebaut werden muss.

### Selbst-Entscheide sind sichtbar und umkehrbar

- Jeder Selbst-Entscheid wird **als solcher markiert** — nie als Freigabe des Menschen
  ausgegeben. Im Gate-Dokument trägt das Freigabe-Feld dann statt eines Zitats den Vermerk,
  dass der Lauf selbst entschied, samt Fundstelle der Regel, die er angewendet hat.
- Am **letzten Gate** stehen alle Selbst-Entscheide gesammelt in einer Liste: was entschieden
  wurde, warum, und **welche Alternative verworfen wurde**. Das ist der Ort, an dem der Mensch
  sie kippt.
- Widerspricht er später, gilt sein Wort und der Lauf springt an die betroffene Stelle
  zurück. Ein Selbst-Entscheid ist eine Annahme, kein Beschluss.
- **Zwei gleiche Selbst-Entscheide sind noch kein Muster.** Ein Muster entsteht aus
  Entscheiden des Menschen. Was der Lauf selbst wählte, wird nie zur Begründung für den
  nächsten Selbst-Entscheid — sonst trägt sich eine Annahme durch die ganze Linie.

### Was dadurch NICHT entfällt

Maschinen-Gates, Prüfschritte und Volldeckungen laufen unverändert. Diese Regel betrifft
ausschließlich das Warten auf einen Menschen — nie das Prüfen. „Der Mensch ist nicht da"
ist kein Grund, eine Prüfung wegzulassen, sondern nur, ihr Ergebnis selbst einzuordnen.

## VOLLSTÄNDIGKEIT — jeder Knoten läuft, ausnahmslos

Ein Lauf ist die Kette, nicht eine Auswahl daraus. **Jeder Knoten auf den
`haupt`-Kanten wird ausgeführt: jeder Skill, jedes Tool, jeder Prüfer-Loop, jeder
Test, jedes Maschinen-Gate — auch die langen, auch die, deren Ergebnis absehbar
scheint.** Die einzige Ausnahme sind Knoten mit `bedingung`, deren Merkmal für diesen
Lauf nachweislich nicht zutrifft — nachgelesen in der genannten Datei und im Bericht mit
Wert genannt. Ein Knoten ohne `bedingung` hat keine Ausnahme.

**Zeit ist nie ein Grund, etwas wegzulassen.** Nicht die Uhrzeit, nicht eine
ablaufende Maschine, nicht ein langer Lauf, nicht „das dauert Stunden". Ein
Workflow hat keine Deadline — er hat eine Kette. Läuft eine äußere Frist gegen
die Vollständigkeit (Server wird gelöscht, Kontingent endet), ist das ein
**Entscheidungspunkt für Gaylord, kein Spielraum für dich**: Frist, Restaufwand
und Optionen nennen und ihn wählen lassen. Er entscheidet, was ein Ergebnis wert
ist — nie die KI im Alleingang.

Schlupflöcher, die alle geschlossen sind: nicht „verkürzt", nicht „nur die
Stichprobe statt der Volldeckung", nicht „die anderen Gates waren grün, also
reicht das", nicht „hole ich später nach", nicht „ich melde es ja im Bericht".
**Ein Schritt im Bericht als weggelassen zu deklarieren macht ihn nicht
zulässig — es dokumentiert nur den Regelbruch.**

| Ausrede | Warum sie nicht zählt |
|---|---|
| „Aus Zeitgründen übersprungen." | Der Workflow kennt keine Zeitgründe. Kollidiert eine Frist mit der Kette, fragst du Gaylord — das ist seine Entscheidung, nicht deine. |
| „Die anderen Prüfungen waren grün, dieser Loop bringt nichts Neues." | Jede Prüfung existiert, weil genau ihre Fehlerklasse durch alle anderen rutscht. Wüsstest du das Ergebnis, bräuchte es die Prüfung nicht. |
| „Der Schritt ist optional / eine Feinpolitur." | Steht er auf einer `haupt`-Kante, ist er Pflicht. Was bedingt sein soll, trägt eine `bedingung` mit prüfbarem Merkmal — alles andere läuft. |
| „Die Bedingung trifft hier sicher nicht zu." | Sicherheit ohne gelesene Datei ist ein Rateschluss. Erst die Stelle aufschlagen, dann entscheiden. |
| „Ich schreibe es ehrlich in den Bericht." | Ehrlichkeit ersetzt keine Ausführung. Beides ist Pflicht, nicht das eine statt des anderen. |
| „Die Maschine wird gleich gelöscht, ich rette lieber das Ergebnis." | Ergebnis sichern UND fragen. Ein unvollständiger Lauf, der gesichert wurde, bleibt unvollständig. |
| „Das Ergebnis ist schon gut genug." | Gut genug heißt: Jeder Prüfschritt ist gelaufen und grün — nicht: Der Rest wäre wohl in Ordnung. Selbst entscheiden darfst du (siehe „Gates: entscheiden statt warten"), Prüfungen überspringen nie. |

Rote Flaggen — jeder dieser Gedanken heißt STOPP und Rückfrage an Gaylord:
„aus Zeitgründen …" · „das reicht auch so" · „ich lasse nur diesen einen weg" ·
„das hole ich nach" · „hier ist es anders, weil …".

Merksatz: **Den Buchstaben der Kette zu verletzen IST den Geist der Kette zu
verletzen.** Ein Lauf, dem ein Knoten fehlt, ist kein schnellerer Lauf — er ist
ein unfertiger.
