# Longform Speaking VSL — Workflow-Rahmen zum Weitergeben

Dieser Ordner enthält den **ElevenLabs-Workflow für gesprochene Longform-VSLs**: aus einer
fremden (englischen) Video-Sales-Letter-Ad wird eine eigene, deutsch GESPROCHENE Ad —
gleiche Bilder-Dramaturgie, neue Stimme, neue Copy, eigenes Produkt-Branding, fertig
geschnitten bis CapCut und Meta-Upload.

**Ehrlicher Stand: Das ist ein RAHMEN-Export, kein fertig gelaufener Workflow.**
15 von 26 Bausteinen existieren und liegen als Skills bei (die komplette Vorstufe, der
Faktencheck, die Produkttausch-Strecke, der Upload). 11 Bausteine sind **Geister** — sie
sind in der Workflow-Datei präzise beschrieben (Soll-Verhalten, Gesetze, Messaufträge),
aber noch nicht gebaut. Sie entstehen nach der Use-and-Break-Methode: benutzen, am
echten Projekt brechen, das Gelernte in den Workflow zurückschreiben. Wer dieses Paket
bekommt, bekommt also den Bauplan PLUS die halbe Fabrik — nicht die ganze.

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
                   └─► sprech-watch (jede Zeile geprüft) ─► Schnitt auf die Stimme
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
longform-speaking-vsl-quasi/
├── LIESMICH.md                        ← diese Datei
├── 00-START-FUER-KI.md                ← Startbefehl + Geister-Regel für KI-Agenten
├── 01-VORAUSSETZUNGEN.md              ← Umgebung, Konten, Schlüssel (KEINE Schlüssel enthalten)
├── 02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md ← die Kette, Knoten für Knoten, Geister markiert
├── 03-FALLEN-UND-TRICKS.md            ← gemessene Fallen aus dem Serienbetrieb der Schwester
├── 04-EINBAU.md                       ← in ein eigenes Projekt übernehmen
│
├── workflow/
│   └── Longform-Speaking-VSL-Quasi.json   ← die Kette als Datei (die Arbeitsanweisung)
│
├── skills/                            ← die 8 EXISTIERENDEN Fach-Skills + der Ausführer
│   ├── execute/                         ← der AUSFÜHRER (wie eine Kette abläuft) — nie weglassen
│   ├── singing-vsl-transkription/       ← Transkript mit Zeitstempeln (samt Scripts)
│   ├── singing-vsl-augen-check/         ← Verdachtsstellen per Frame-Beweis klären
│   ├── vmake-caption-entfernen/         ← eingebrannte Captions tilgen
│   ├── singing-vsl-clip-karte/          ← Quelle in beschriebene Clips zerlegen
│   ├── singing-vsl-dach-lokalisierung/  ← Markt-Befund für den Mensch-Entscheid
│   ├── watch-factcheck/                 ← Faktencheck mit echtem Auge
│   ├── custom-clip-production/          ← Produkt-Clips rebranden + prüfen
│   └── ad-upload/                       ← Meta-Upload, immer pausiert
│
└── referenz/                          ← Erbgut für die 11 Geister
    ├── Longform-Singing-VSL-Quasi.json  ← die große Schwester (erprobtes Vorbild)
    ├── sa-captions-capcut.SKILL.md      ← CapCut-Übergabe der Schwester (Schritte 6–8 erben)
    ├── voiceover-narrator-voice-design-prompt/ ← Ausgangs-Baustein fürs Stimm-Casting
    ├── background-music-suno/           ← Musikbett-Weg B (eigenes Instrumental)
    └── projekte-datenbank.DATENBANK.md  ← Vertragskarte der Projekt-Ablage (Naming-Vorlage)
```

Ein Export ist eine **Kopie zu einem Zeitpunkt**, kein Live-Spiegel (Stand: 20.08.2026).
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

- **Stimmen werden NIE geklont.** Die Original-Sprecherstimme der Quelle wird nicht
  nachgebaut — weder per ElevenLabs-Klon noch anders. Die Brand-Stimme wird neu
  designt (Voice Design) oder aus der Library gewählt. Das schützt rechtlich UND das
  ElevenLabs-Konto, an dem die halbe Kette hängt.
- **Produkt-Branding der Quelle fliegt raus.** Die Custom-Clip-Strecke ersetzt jede
  Einstellung, die das fremde Produkt zeigt, durch eigene rebrandete Clips.
- **Verantwortung liegt beim Betreiber.** Bild-Dramaturgie und Testimonial-Material der
  Quelle bleiben fremdes Material; wie nah die eigene Ad am Original bleiben darf, ist
  eine Geschäftsentscheidung des Menschen, der den Workflow betreibt — nicht der KI.
