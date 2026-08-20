---
name: "`/watch` Faktencheck"
description: "Locked 2026-07-11 (User). Der /watch-Skill (~/.agents/skills/watch) lässt mich Videos wirklich ansehen — Frames + Transkript, per Timestamp. Diese Fähigkeit hat genau eine erlaubte Rolle im Ad-Workflow: Faktencheck mit echtem Auge. Sie ist NIE ein Qualitäts- oder Geschmacksurteil."
---
# Skill — `/watch` Faktencheck (echtes Auge, KEIN Geschmacksurteil)

Locked 2026-07-11 (User). Der `/watch`-Skill (`~/.agents/skills/watch`) lässt mich Videos wirklich **ansehen** — Frames + Transkript, per Timestamp. Diese Fähigkeit hat **genau eine erlaubte Rolle** im Ad-Workflow: **Faktencheck mit echtem Auge.** Sie ist NIE ein Qualitäts- oder Geschmacksurteil.

## ⚠️ EXTRA WICHTIG — die Hintertür bleibt zu (der eine Grund für diesen Skill)

`/watch` prüft **nur Dinge, die WAHR oder FALSCH sind — nie BESSER oder SCHLECHTER.**

Das Timing-System (`.claude/skills/objective-timing/SKILL.md`) wurde gebaut, um das Subjektive („schätzen, hoffen, fühlen") aus der Ausführung zu verbannen. Ein Video *anzuschauen* verführt genau dazu zurück — „fühlt sich gut an", „Pacing passt", „Emotion landet". **Das ist verboten.** Sobald `/watch` ein Geschmacksurteil abgibt, hat es die Hintertür für das Subjektive wieder aufgemacht, und wir haben verloren, wofür wir Monate gearbeitet haben.

| ✅ ERLAUBT (Fakten, binär — TRUE/FALSE) | ❌ VERBOTEN |
|---|---|
| Ist **durchgängig die richtige Frau/Protagonistin** drin? (keine fremde) | „sieht **schön** aus" / „**gut** geworden" |
| Ist das **Produkt da**, wo der Plan es vorsieht? | „**fühlt** sich richtig an" / „**Emotion** landet" |
| Zeigt **jeder Beat den Inhalt**, den Skript/Plan sagt? | „das **Pacing** wirkt gut" |
| **Kein Glitch** / falsche Anatomie / Artefakt / Text-Müll? | jede Bewertung von „**Qualität**" oder „Wirkung" |
| **Keine reingeblutete Fremdszene** (Multi-Scene-Contamination)? | **TIMING** — Sekunden/Sync sind ZAHLEN → das macht **nur** Objective-Timing |

**Zwei harte Ausschlüsse, immer nennen:**
1. **Kein Geschmack.** „Ist es gut/schön?" ist subjektiv → fällt raus. Ich urteile nur über verifizierbare Fakten gegen den Plan.
2. **Kein Timing.** Sekunden & Sync macht `.claude/skills/objective-timing/SKILL.md` mit Zahlen. Mit dem Auge auf Timing zu schauen = Schätzung = exakt das, was wir abgeschafft haben. **`/watch` fasst Timing NICHT an.**

Merksatz: **`/watch` = Faktencheck mit echtem Auge. Kein Geschmacksurteil. Kein Timing.**

## Der visuelle Zwilling zum Coverage-Audit

Der Coverage-Audit (`.claude/skills/coverage-audit-and-reconcile/SKILL.md`) prüft auf dem **PAPIER**: „jedes Skript-Element hat eine Quelle" (`NEW`/`LIB`/`GAP`). Der `/watch`-Faktencheck prüft am **BILDSCHIRM**: „jede Quelle hat auch wirklich das Richtige gerendert" (richtige Frau, richtiges Produkt, richtiger Inhalt, kein Artefakt). **Beide gegen denselben Plan** → beide objektiv (matcht den Plan: ja/nein). Zusammen = Papier-Plan **und** visuelle Realität abgeglichen.

**Fund → Ursache 1–3 Steps zurück** (Clip→Frame→Prompt→Library-Quelle), an der Wurzel fixen — nie nur das Symptom (`[[root-cause-at-source]]`). Das fremde-Frau-Beispiel aus LEI 024 Hook C bestand JEDEN Zahlen-Gate (Sync Δ0.05s, 0 Freezes) — die Zahlen waren perfekt, der **Inhalt** war falsch. Genau diese Klasse fängt der Faktencheck.

## Die zwei Fixpunkte im Workflow (nur hier — Token-Disziplin)

**1. VORNE — Winner-Teardown (Research/Learning).**
`/watch` auf eine bewiesene Winner-Ad (Competitor). Zieht **FAKTEN**: Beat-Grenzen per Timestamp, Transkript, Shot-Anzahl, Register-Mix, Hook-Mechanik. Das sind **Daten, keine Schätzung** (Timestamps liest der Report ab). Die „was macht ihren Hook stark"-Einsichten sind **Kandidaten-Bausteine** → sie werden gehärtet, sobald wir sie in unserer eigenen Pipeline durch die objektiven Gates schicken. Winner-Beat-Längen dürfen die SOLL-Werte unseres Timing-Contracts **informieren** (echte Referenz-Zahlen statt raten).

**2. HINTEN — finaler Content-Faktencheck (vor jedem „fertig").**
Nach `verify` (Gate C, Zahlen) `/watch` über die **fertige Ad** → die erlaubte Fakten-Liste oben durchgehen. FAIL an einem Fakt = nicht fertig → Ursache finden → fixen → re-check. Das ist der visuelle Teil von Non-Negotiable #6.

**Token-Zusage (ehrlich):** `/watch` NUR an diesen zwei Fixpunkten + gezielten Winner-Lern-Sessions. **NICHT** auf jeden Zwischen-Clip — dafür bleiben die billigen Frame-Montagen/Contact-Sheets (`montage.py`, ffmpeg-Frames). Bandbreite nutzen, nicht verbrennen (`[[credit-discipline]]` bleibt: erst gratis-Checks ausschöpfen).

## So läuft es (Aufruf)

- **Skill:** `~/.agents/skills/watch` (Claude-Code-symlinked) — als Skill `watch` verfügbar. Deps `ffmpeg` + `yt-dlp` liegen auf dem Standard-PATH.
- **Aufruf:** `/watch <URL oder lokaler Pfad> <konkrete Fakten-Frage>`
- **Fokus:** `--start 0:00 --end 0:15` (nur den Hook), `--detail efficient|balanced|token-burner`.
- **Stille/eigene Clips:** `--no-whisper` (unsere B-Roll ist tonlos; kein Whisper-Key nötig). Caption-lose Fremd-Videos (TikTok/lokale UGC) bräuchten einen Groq/OpenAI-Key in `~/.config/watch/.env` — optional; YouTube-Captions sind gratis.
- Der Report listet Frame-Pfade mit `t=MM:SS` → jeden mit **Read** öffnen und die Fakten binär bestätigen.

## Verankert in
- Non-Negotiable **#6** (CLAUDE.md) — visueller Zwilling des Coverage-Audits.
- Gate-Flow — Content-Faktencheck als benannter Schritt vor FERTIG (nur Fakten, nicht Timing/Geschmack).
- `.claude/skills/objective-timing/SKILL.md` „Grenzen (ehrlich)" — Timing bleibt dort numerisch; Content-Review läuft hier.
- Memory `[[watch-factcheck-not-taste]]`, `[[objective-over-subjective-tools-first]]`, `[[coverage-audit-and-reconcile]]`.
