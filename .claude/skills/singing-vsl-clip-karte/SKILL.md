---
name: singing-vsl-clip-karte
description: "Das Quellvideo einer Singing-Ad in seine echten Clips zerlegen und JEDEN Clip mit eigenen Augen beschreiben (wer/wo/welche Handlung), bevor übersetzt wird — die Karte bindet später jede deutsche Zeile an ihre Original-Bilder. Pflicht-Schritt der Singing-VSL-Kette zwischen Transkript-Augencheck und Übersetzung; auch nutzen, wenn Viktor sagt „bestimm die Clips", „Clip-Karte", „was passiert in den Clips", „welche Szenen hat das Original"."
---

# Clip-Karte — die Bilder werden kartiert, BEVOR übersetzt wird

Warum vor der Übersetzung: Jede Original-Szene gehört zu einem bestimmten Satz.
Wer erst übersetzt, verliert diese Bindung — die deutsche Fassung wird örtlich
länger oder kürzer als ihre Bilder, und der Schnitt wirft dann Story-Szenen weg.
Die Karte macht die Bindung explizit: Clip-Grenzen + Inhalt je Clip, damit die
Übersetzung in Clip-Budgets arbeiten kann. Regeln und Bänder wohnen im Gesetz:
`.claude/skills/sa-resync-singing-ad/SKILL.md` §CLIP-ZUERST (Schritt 1–2) — dieses
Skill ist die Schritt-Regie, das Gesetz die einzige Regel-Quelle.

## Ablauf

1. **Zerlegen + Sheets:** `~/.venvs/sa/bin/python3 _pipeline/clip_karte<NNN>.py bau`
   (CWD = Projektordner `brands/<Brand>/<NNN SA>/`). Zerlegt `_work/vmake_cleaned.mp4`
   an echten Szenengrenzen (jeder Clip mit von/bis in Sekunden), zieht 2 Frames je
   Clip auf Kontakt-Sheets und hängt die EN-Transkript-Wörter je Clip an
   (braucht `_pipeline/source_words.json` aus der Transkription).
2. **Mit eigenen Augen beschreiben — KEIN Gemini für Bilder (Viktors Verbot):**
   Alle Sheets mit Read ansehen und je Clip festhalten, WAS PASSIERT — Personen,
   Ort, Handlung („Frau und Mann halten Hände", „Tochter hält Maske hoch"), nicht
   nur Kulisse. Diese Beschreibung ist es, die später die richtige Zeile auf das
   richtige Bild legt. Dazu je Clip: Typ R/A/P (Real/Animation/Phone-Screen —
   P-Clips tragen englischen Bildschirmtext und bleiben englisch) und das
   Übergangs-Flag (Blendung im Clip-Inneren → dieser Clip darf nie getrimmt werden).
3. **Einpflegen:** Beschreibungen als JSON `{clipnr: {"bild": "…", "typ": "R",
   "uebergang": false}}` speichern, dann
   `clip_karte<NNN>.py merge <datei.json>` → `_pipeline/clip_karte.json`.
   Das merge bricht ab, wenn auch nur ein Clip ohne Beschreibung bleibt — jede
   Original-Szene braucht Augen, sonst beginnt hier das stumme Wegwerfen.

## Ausgabe & Übergabe

`_pipeline/clip_karte.json` — je Clip: `clip, t0, t1, dauer, en, bild, typ,
uebergang`. Damit arbeitet die Übersetzung (Clip-Budgets, Plan-Format
`Cxxx-Cyyy | Zeile`) und später Schnitt + Abnahme (Zeile↔Clip-Kreuzcheck).
Referenz-Durchlauf mit Beispielen: `brands/QUA - Quasi/002 VZ/iteration-log.md`.
