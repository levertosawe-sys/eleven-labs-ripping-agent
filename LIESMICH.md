# Longform Speaking VSL — Workflow-Rahmen zum Weitergeben

Dieser Ordner enthält den **ElevenLabs-Workflow für gesprochene Longform-VSLs**: aus einer
fremden (englischen) Video-Sales-Letter-Ad wird eine eigene, deutsch GESPROCHENE Ad —
gleiche Bilder-Dramaturgie, neue Stimme, neue Copy, eigenes Produkt-Branding, fertig
geschnitten bis CapCut und Meta-Upload.

**Ehrlicher Stand:** 24 von 27 Bausteinen existieren und liegen bei — die Kette ist in
echten Läufen bis zum CapCut-Projekt durchgelaufen, inklusive Lip-Sync für sichtbar
sprechende Menschen. Drei Bausteine sind **Geister** (Ripping-Sheet, Upload-Werkzeug,
Meta-Werbekonto-Datenbank): in der Workflow-Datei beschrieben, aber nicht im Paket.

Die große Schwester dieses Workflows (Singing-VSL: gleiche Kette, aber mit Suno-GESANG
statt Sprechstimme) ist seit Wochen im Serienbetrieb — ihre Workflow-Datei liegt als
Vorbild in `referenz/`. Alles, was hier Geist ist, hat dort ein erprobtes Gegenstück.

---

## Was der Workflow macht — in einem Absatz

Du wirfst eine gesprochene Competitor-VSL (MP4) rein. Die KI transkribiert sie
wort- und zeitgenau (ElevenLabs Scribe), prüft Verdachtsstellen mit eigenen Augen an den
eingebrannten Captions, entfernt diese Captions (Vmake), zerlegt das Video in Clips und
beschreibt jeden einzelnen. Dann wird die Copy **in die Clip-Zeitfenster hinein**
übersetzt, für den Zielmarkt geprüft (Mensch entscheidet), und eine **eigene, einmal je
Brand gecastete ElevenLabs-Stimme** spricht sie Absatz für Absatz ein — mit geprüfter
Aussprache von Zahlen, Preisen und Markennamen. Die Original-Clips werden hart auf die
neue Sprechspur geschnitten, produktzeigende Clips durch eigene rebrandete Clips ersetzt,
ein Musikbett untergelegt, alles maschinell abgenommen (Zeile↔Clip, Ohr, Auge) und als
CapCut-Paket mit Karaoke-Captions übergeben. Am Ende: Upload als pausierte Meta-Ad.

**Kurzform der Kette:**

```
VSL rein
 └─► Transkript (Scribe) ─► Augen-Check ─► Captions tilgen (Vmake) ─► Clip-Karte
       └─► Übersetzung in Sprech-Budgets ─► Markt-Befund ─► MENSCH entscheidet
             └─► Stimme casten (einmal je Brand, MENSCH wählt) ─► Sprechspur bauen
                   └─► sprech-watch (jede Zeile geprüft) ─► Audio-Prüfung
                         └─► Lip-Sync (nur Menschen, die sichtbar sprechen) ─► Schnitt
                         └─► Abnahme + Faktencheck ─► Captions ─► CapCut (MENSCH sichtet)
                               └─► Meta-Upload (immer pausiert)
   (parallel: Produkt-Clips → eigene Custom Clips · Quell-Audio → Musikbett)
```

---

## Womit du anfängst — je nachdem wer du bist

| Du bist … | Fang hier an |
|---|---|
| **Mensch, willst verstehen was das ist** | diese Datei zu Ende, dann `02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md` |
| **KI-Agent** (Claude Code o. ä.), sollst den Workflow fahren/fertigbauen | `00-START-FUER-KI.md` |
| **Willst wissen, was installiert/eingeloggt sein muss** | `01-VORAUSSETZUNGEN.md` |
| **Willst den Workflow in dein Projekt einbauen** | `04-EINBAU.md` |
| **Willst nur die Stolpersteine** | `03-FALLEN-UND-TRICKS.md` |

---

## Was in diesem Ordner liegt

```
eleven-labs-ripping-agent/
├── README.md · LIESMICH.md            ← Überblick für Menschen
├── 00-START-FUER-KI.md                ← Einstieg für KI-Agenten
├── 01-VORAUSSETZUNGEN.md              ← Umgebung, Konten, Schlüssel (KEINE Schlüssel enthalten)
├── 02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md ← die Kette, Knoten für Knoten
├── 03-FALLEN-UND-TRICKS.md            ← gemessene Fallen aus echten Läufen
├── 04-EINBAU.md                       ← in ein eigenes Projekt übernehmen
├── feedback_log.md                    ← Herleitung der Regeln
│
├── workflows/eleven-labs-ripping-agent.json   ← die Kette als Datei (die Arbeitsanweisung)
│
├── .claude/skills/                    ← die Fach-Skills + der Ausführer (execute)
│   ├── singing-vsl-transkription · singing-vsl-augen-check · vmake-caption-entfernen
│   ├── singing-vsl-clip-karte · speaking-vsl-emotionskarte · speaking-vsl-uebersetzung
│   ├── singing-vsl-dach-lokalisierung · speaking-vsl-stimm-casting · sprech-watch
│   ├── speaking-vsl-musikbett · speaking-vsl-lipsync (nur Menschen) · speaking-vsl-captions
│   └── watch-factcheck · custom-clip-production · ad-upload · execute
│
├── tools/sp/                          ← Sprech-Kette: Bootstrap, Sprechspur, Prüfer, Render, Abnahme, CapCut-Paket
├── tools/vmake/                       ← Vmake-Client + Schlieren-Scan
│
├── datenbanken/                       ← Verträge (DATENBANK.md), keine Kundendaten
│   ├── sp-projekte · sp-brands · sp-learnings (mit learnings.md) · stimmen (mit Steckbrief)
│   └── brand-vorlage · projekte-quasi (Vorlagen des ersten Pakets)
│
└── referenz/                          ← Erbgut der Singing-Schwester
```

Ein Export ist eine **Kopie zu einem Zeitpunkt**, kein Live-Spiegel (Stand: 17.09.2026).
Ein echtes Beispiel aus einem gelaufenen Fall fehlt noch — diese Linie ist jung; das
Beispiel entsteht mit dem ersten Lauf und wird dann nachexportiert.

---

## Die drei Regeln, die den Workflow ausmachen

1. **Dateien sind die Wahrheit.** Jede Etappe schreibt ihr Ergebnis in eine Datei; die
   Datei der einen Etappe ist die Eingabe der nächsten. Nichts bleibt „nur im Chat".
2. **Der Mensch entscheidet an den Gates, die KI setzt um.** Drei Mensch-Gates:
   Markt-Entscheid zur Copy, Stimmen-Wahl (einmal je Brand), End-Sichtung in CapCut.
   Maschinen-Befunde dazwischen stoppen den BAU (fixen oder als Trade-off dokumentieren),
   nie den Lauf auf den Menschen.
3. **Use and Break: Feedback ändert den WORKFLOW, nie nur das Projekt.** Jeder Fund aus
   einem Lauf wandert als Regel in Skill oder Workflow-Datei zurück — so wird die
   Blackbox mit jedem Lauf deterministischer. Ein Fix, der nur im Projekt landet, ist
   verloren; ein Fix im Workflow gilt für immer.

---

## Rechtlicher Klartext

Dieser Workflow arbeitet mit **fremden VSLs als Quelle** und macht daraus eine eigene
Ad in anderer Sprache. Drei Dinge sind nicht verhandelbar:

- **Die Stimme der Quell-Ad wird NIE geklont.** Die Original-Sprecherstimme der Quelle
  wird nicht nachgebaut — weder per ElevenLabs-Klon noch anders. Die Brand-Stimme kommt
  aus der Bibliothek, aus Voice Design oder als Klon einer Aufnahme, an der der Betreiber
  die Rechte hat (z. B. eine eigene Ad). Das schützt rechtlich UND das ElevenLabs-Konto,
  an dem die halbe Kette hängt.
- **Produkt-Branding der Quelle fliegt raus.** Die Custom-Clip-Strecke ersetzt jede
  Einstellung, die das fremde Produkt zeigt, durch eigene rebrandete Clips.
- **Verantwortung liegt beim Betreiber.** Bild-Dramaturgie und Testimonial-Material der
  Quelle bleiben fremdes Material; wie nah die eigene Ad am Original bleiben darf, ist
  eine Geschäftsentscheidung des Menschen, der den Workflow betreibt — nicht der KI.
