# Einbau — den Workflow in ein eigenes Projekt holen

Drei Wege, je nachdem wie tief du einsteigen willst.

---

## Weg A — Nur loslegen, ohne Installation

1. Öffne **diesen Ordner** in Claude Code (oder einem anderen Agenten mit Datei- und
   Terminal-Zugriff).
2. Sag:

   > Lies `00-START-FUER-KI.md` und fahre den Longform-Speaking-VSL-Workflow.
   > Quelle: `<pfad/zur/vsl.mp4>` · Brand: `<KÜRZEL — Name>` · Markt: `<Sprache/Region>`

Die KI liest sich die Kette selbst zusammen, prüft die Voraussetzungen und fragt in
EINER Nachricht nach, was fehlt.

**Ehrlicher Hinweis:** Beim ersten Lauf wird sie an den Geister-Knoten (Übersetzung,
Stimme, Sprechspur, Schnitt, Captions) mit dir zusammen bauen statt nur ausführen —
das ist so gedacht (Use and Break), nicht kaputt.

---

## Weg B — Als echte Skills installieren

Damit die vorhandenen Etappen von selbst greifen, sobald du im Chat das Passende sagst:

```bash
# aus diesem Ordner heraus, ZIEL = dein Projekt
ZIEL=~/mein-projekt

mkdir -p "$ZIEL/.claude/skills" "$ZIEL/workflows" "$ZIEL/inbox" \
         "$ZIEL/datenbanken/projekte" "$ZIEL/datenbanken/stimmen" "$ZIEL/tools/sp"
cp -r skills/* "$ZIEL/.claude/skills/"
cp workflow/Longform-Speaking-VSL-Quasi.json "$ZIEL/workflows/"
cp referenz/projekte-datenbank.DATENBANK.md "$ZIEL/datenbanken/projekte/DATENBANK.md"
```

| Was | Wohin | Warum |
|---|---|---|
| die 8 Fach-Skills | `.claude/skills/` | die Arbeitsanleitung der gebauten Etappen |
| `execute` | `.claude/skills/` | **ohne den läuft die Kette nicht als Kette** — er stoppt an Gates und lässt keinen Knoten weg |
| die Workflow-Datei | `workflows/` | definiert Reihenfolge, Verzweigungen, Datenbank-Kanten |
| die Datenbank-Vertragskarte | `datenbanken/projekte/` | Naming + Ablage-Vertrag (an die eigene Brand anpassen) |
| `referenz/` | bleibt im Paket | Erbgut zum Bauen der Geister — nicht installieren |

Danach reichen Sätze wie „transkribier die VSL“, „mach die Clip-Karte“, „prüf das für
unseren Markt“ — die passende Etappe startet von selbst. Die Geister-Etappen entstehen
in den ersten Läufen und werden dabei als neue Skill-Ordner/`tools/sp`-Skripte fest;
ihre `ref`-Pfade stehen schon in der Workflow-Datei.

**Anpassen an die eigene Brand — drei Stellen:**

1. `datenbanken/brand-<kürzel>/` anlegen: Produkt-Fakten (der eigene Shop ist der
   Maßstab), Referenzbilder des eigenen Produkts in `Product Reference/`.
2. Markt-Skill kopieren/eichen: der beiliegende ist auf DACH geeicht
   (`singing-vsl-dach-lokalisierung`) — für einen anderen Markt duplizieren und die
   Markt-Regeln tauschen.
3. Fürs Upload-Ende das eigene Meta-Adressbuch anlegen (Format im Skill `ad-upload`) —
   mit eigenen Konto-/Seiten-/Pixel-IDs. Ohne das endet die Kette mit der fertigen MP4,
   was für den Anfang völlig in Ordnung ist.

---

## Weg C — In ein AWMS-Projekt

Ist das Ziel ein AWMS-Ordner, ist Weg B schon fast alles — die Ablage stimmt bereits.
Nach einem Reload erscheint „Longform-Speaking-VSL-Quasi“ unter **Workflows**.

AWMS malt nicht existierende Referenzen als **Geister** — direkt nach dem Einbau müssen
genau die 11 Geister aus `02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md` blass sein und die 15
gebauten Knoten voll. Fehlt mehr, ist beim Kopieren etwas verloren gegangen; ist alles
voll, hat jemand die Geister schon gebaut. Der Kopfbalken des Graphen zählt mit
(„N von 26 Bausteinen gebaut“) — das ist zugleich der Baufortschritt dieser Linie.

---

## Nach dem Einbau: Funktioniert es?

Ein Mini-Test ohne einen einzigen API-Call:

```bash
# 1. Workflow-Datei lesbar und vollständig?
python3 -c "import json; d=json.load(open('workflows/eleven-labs-ripping-agent.json')); print(d['name'], '·', len(d['knoten']), 'Knoten')"

# 2. Sind die Pflicht-Skills da?
ls .claude/skills/execute/SKILL.md .claude/skills/singing-vsl-transkription/SKILL.md
```

Der erste echte Lauf braucht dann die Schlüssel aus `01-VORAUSSETZUNGEN.md` — und eine
gesprochene Competitor-VSL in `inbox/`.
