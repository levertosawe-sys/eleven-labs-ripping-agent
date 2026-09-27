# Einbau — den Workflow in ein eigenes Projekt holen

Drei Wege, je nachdem wie tief du einsteigen willst.

---

## Weg A — Nur loslegen, ohne Installation

1. Öffne **diesen Ordner** in Claude Code (oder einem anderen Agenten mit Datei- und
   Terminal-Zugriff).
2. Sag:

   > Lies `00-START-FUER-KI.md` und fahre den Workflow „Eleven Labs Ripping Agent“.
   > Quelle: `<pfad/zur/vsl.mp4>` · Brand: `<KÜRZEL — Name>` · Markt: `<Sprache/Region>`

Die KI liest sich die Kette selbst zusammen, prüft die Voraussetzungen und fragt in
EINER Nachricht nach, was fehlt.

**Ehrlicher Hinweis:** Alle Knoten bis auf das Ripping-Sheet sind gebaut. Bricht ein
Schritt an deinem Material, schreibt die KI das Gelernte in den Skill zurück statt nur
ins Projekt — das ist so gedacht (Use and Break), nicht kaputt.

---

## Weg B — Als echte Skills installieren

Damit die vorhandenen Etappen von selbst greifen, sobald du im Chat das Passende sagst:

```bash
# aus diesem Ordner heraus, ZIEL = dein Projekt
ZIEL=~/mein-projekt

mkdir -p "$ZIEL/.claude/skills" "$ZIEL/workflows" "$ZIEL/inbox" "$ZIEL/tools" "$ZIEL/datenbanken"
cp -r .claude/skills/* "$ZIEL/.claude/skills/"
cp workflows/eleven-labs-ripping-agent.json "$ZIEL/workflows/"
cp -r tools/sp tools/vmake tools/sa tools/ad-upload "$ZIEL/tools/"
cp -r datenbanken/sp-projekte datenbanken/sp-brands datenbanken/sp-learnings \
      datenbanken/stimmen datenbanken/meta-werbekonto "$ZIEL/datenbanken/"
```

| Was | Wohin | Warum |
|---|---|---|
| die 15 Fach-Skills + `sa-captions-capcut` | `.claude/skills/` | die Arbeitsanleitung der Etappen |
| `execute` | `.claude/skills/` | **ohne den läuft die Kette nicht als Kette** — er stoppt an Gates und lässt keinen Knoten weg |
| die Workflow-Datei | `workflows/` | definiert Reihenfolge, Verzweigungen, Datenbank-Kanten |
| die Datenbank-Verträge | `datenbanken/` | Naming + Ablage-Verträge, Learnings, Stimmen-Register (an die eigene Brand anpassen) |
| die Werkzeuge | `tools/` | die Skripte, die die Skills aufrufen |
| `referenz/` | bleibt im Paket | Erbgut zum Bauen der Geister — nicht installieren |

Danach reichen Sätze wie „transkribier die VSL“, „mach die Clip-Karte“, „prüf das für
unseren Markt“ — die passende Etappe startet von selbst.

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
Nach einem Reload erscheint „Eleven Labs Ripping Agent“ unter **Workflows**.

AWMS malt nicht existierende Referenzen als **Geister** — direkt nach dem Einbau ist
genau ein Knoten blass (das Ripping-Sheet, Software des Betreibers), alle übrigen sind
voll. Fehlt mehr, ist beim Kopieren etwas verloren gegangen. Der Kopfbalken des Graphen
zählt mit („26 von 27 Bausteinen gebaut“).

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
