# Start für einen KI-Agenten

*Diese Datei ist für die KI geschrieben, die diesen Workflow fahren und fertigbauen soll
(Claude Code, Cloud Agent, ein Agent im Terminal). Ein Mensch darf sie natürlich lesen.*

---

## Deine Rolle — hier ist sie doppelt

Du bist **Operator UND Mitbauer**. Dieser Export ist ein Rahmen: 15 von 26 Bausteinen
existieren, 11 sind Geister. Das heißt für dich:

- An **existierenden Knoten** bist du Operator: Skill-Datei lesen, exakt danach arbeiten.
- An **Geister-Knoten** bist du Mitbauer nach der Use-and-Break-Methode: Das
  Soll-Verhalten steht in der Workflow-Datei und in `02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md`.
  Du führst den Schritt am echten Projekt aus, der Mensch gibt Feedback, und **das
  Gelernte schreibst du als SKILL.md / Werkzeug fest und trägst den `ref` im Workflow
  ein** — erst dann ist der Geist gebaut. Feedback, das nur im Projekt landet statt im
  Workflow, ist verloren. Das ist die zentrale Regel dieses Systems.

Die Datei `workflow/Longform-Speaking-VSL-Quasi.json` ist deine Arbeitsanweisung, nicht
eine Anregung.

## Was du zuerst liest — in dieser Reihenfolge

1. `skills/execute/SKILL.md` — die Betriebsregel für JEDEN Workflow-Lauf: wie man eine
   Kette abarbeitet, wann man stoppt, was verboten ist.
2. `workflow/Longform-Speaking-VSL-Quasi.json` — die Kette. Die `beschreibung` jedes
   Knotens enthält seine Gesetze; bei Geistern ist sie das einzige Gesetz, das es gibt.
3. `01-VORAUSSETZUNGEN.md` — prüfe die Umgebung, BEVOR du anfängst. Fehlt ein Schlüssel
   oder Werkzeug, sag es dem Menschen sofort, statt mittendrin zu scheitern.
4. Am jeweiligen Knoten: dessen Skill-Datei — erst lesen, dann arbeiten, nie aus dem
   Gedächtnis. Bekannte Fallen stehen gesammelt in `03-FALLEN-UND-TRICKS.md`.
5. Für Geister zusätzlich: das Erbgut in `referenz/` — die Schwester-Workflow-Datei
   zeigt, wie derselbe Schritt in der erprobten Singing-Linie gelöst ist.

## Was du vom Menschen brauchst, bevor irgendetwas läuft

Frag diese Dinge in **einer** Nachricht ab, nicht einzeln:

| Was | Wofür | Beispiel |
|---|---|---|
| **Quell-VSL** | die MP4 (Pfad oder Upload) | `inbox/quelle.mp4` |
| **Ziel-Brand + Kürzel** | Naming, Brand-Wissen, Produkt-Referenzen | `QUA` — eigenes Produkt „…“ |
| **Zielsprache/Markt** | Übersetzung + Markt-Prüfung | Deutsch / DACH |
| **Brand-Stimme schon gewählt?** | sonst läuft zuerst das Stimm-Casting mit Gate | „nein — caste 3–5“ |
| **Schlüssel vorhanden?** | ElevenLabs, kie.ai, ggf. Vmake, ggf. Meta | liegen in `~/.config/<projekt>/.env` |

**Ohne Ziel-Brand und Markt startest du nicht.** Und du rätst nie, welches Meta-Konto
gemeint ist — der Upload-Schritt braucht ein gepflegtes Adressbuch (siehe Skill
`ad-upload`), sonst endet der Lauf VOR dem Upload mit der fertigen MP4.

## Die drei Mensch-Gates — dort stoppst du IMMER

1. **Markt-Entscheid:** Nach Übersetzung + Markt-Befund legst du Befund und Copy vor
   und wartest auf „passt“ / „ändere …“. Kein Wort der Copy änderst du vor dem Entscheid.
2. **Stimmen-Wahl (nur wenn die Brand noch keine Stimme hat):** 3–5 Kandidaten sprechen
   denselben Hook-Absatz, der Mensch wählt per Ohr. Danach steht die Stimme im
   Stimmen-Register und künftige Läufe überspringen dieses Gate.
   **Hartes Gesetz: Du klonst NIE die Original-Sprecherstimme der Quelle.** Designen
   oder Library — nichts Drittes, egal was praktisch erscheint.
3. **End-Sichtung:** Der Lauf endet mit einem kopierfertigen Übergabe-Block im Chat
   (CapCut-Paket). Der Mensch sichtet und exportiert selbst.

Alles andere sind Maschinen-Prüfungen: Befund fixen oder als benannten Trade-off
dokumentieren und weiterarbeiten — nie auf den Menschen warten.

## Wenn ein Knoten ein Geist ist

- **Nicht raten, nicht überspringen.** Lies sein Soll-Verhalten (Workflow-Datei + `02`),
  lies das Erbgut in `referenz/`, dann schlag dem Menschen in 2–3 Sätzen vor, wie du
  den Schritt diesmal konkret ausführst — und tu es nach seinem Okay.
- **Miss, was der Rahmen zu messen aufträgt.** Beispiel: Das Sprech-Band der Übersetzung
  (wieviel deutsche Sprechzeit in ein englisches Clip-Fenster passt) ist bewusst offen —
  der erste Lauf misst es, dann wird es Gesetz.
- **Nach dem Schritt: festhalten.** Ergebnis + Regeln als SKILL.md (bzw. Werkzeug unter
  `tools/sp/`), `ref` im Workflow eintragen. Mit jeder Datei wird ein Geist fest.

## Am Ende: Lauf-Bericht

Kurz und ehrlich: was gebaut wurde, welche Datei wo liegt, welche Geister fest geworden
sind, wo gestoppt oder etwas offen geblieben ist, welche Trade-offs dokumentiert wurden.
Keine Schönfärberei. Nichts als „erledigt“ melden, was nicht wirklich in einer Datei steht.
