# Die Kette, Knoten für Knoten

Legende: **[GEBAUT]** Skill/Werkzeug liegt unter `.claude/skills/` bzw. `tools/` bei · **[GEIST]** noch zu bauen
(Soll-Verhalten hier + in der Workflow-Datei; Erbgut in `referenz/`) · **[GATE]** der
Mensch entscheidet · **[TRIGGER]** hier startet etwas.

Die Workflow-Datei `workflows/eleven-labs-ripping-agent.json` ist die Wahrheit; diese
Anleitung erzählt sie in Prosa.

---

## Etappe A — Von der fremden VSL zur entscheidungsreifen Copy

**A1 · Quell-VSL [TRIGGER]**
Eine gesprochene Longform-VSL als MP4 in `inbox/` (oder per Rip-Auftrag). Zuerst
Quell-Hash gegen die Projekte-Datenbank prüfen: schon verarbeitet → STOPP, kein
Doppel-Rip. Projekt-Karte anlegen (Naming „KÜRZEL NNN | DATUM“).

**A2 · Transkription (EN) [GEBAUT]** — `skills/singing-vsl-transkription/`
ElevenLabs Scribe misst Wort-Zeitstempel direkt an der Tonspur — ein Call fürs ganze
Video, kein Drift, Lücken-Wächter bei >5 s. Ausgabe: `<slug>-original-<datum>.md` mit
(M:SS)-Stempeln in der Projekte-Ablage.

**A3 · Transkript-Augencheck [GEBAUT]** — `skills/singing-vsl-augen-check/`
Verdachtsstellen (Zahlen-Garbles, Widersprüche) mit eigenen Augen klären: Frames ums
Zeitfenster ziehen, eingebrannte EN-Captions lesen. Captions sind WORT-Autorität, nie
Timing-Autorität. Korrekturen mit Beleg ins Transkript — erst danach darf übersetzt werden.

**A4 · Captions tilgen [GEBAUT]** — `skills/vmake-caption-entfernen/`
Eingebrannte Quell-Captions per Vmake von der GLATTEN Quelle entfernen — zwingend NACH
dem Augen-Check (der braucht die Captions) und VOR der Clip-Karte (die zerlegt die
bereinigte Fassung). Dauert bei Longform ~1 h und läuft parallel zur Gate-Wartezeit.
Original als `_work/source_original.mp4` sichern, Schlieren-Scan Pflicht.

**A5 · Clip-Karte [GEBAUT]** — `skills/singing-vsl-clip-karte/`
Quelle in echte Clips zerlegen (Szenen-Erkennung), Kontakt-Sheets, JEDEN Clip mit
eigenen Augen beschreiben; EN-Text je Clip, Typ-Einordnung, Übergangs-Flags. Zusatz:
jeden Clip markieren, der das fremde Produkt zeigt → `custom_clips.json` (Eingabe der
Etappe P). Die Karte ist Pflicht-Eingabe der Übersetzung.

**A6 · Übersetzung in Sprech-Budgets [GEBAUT]** — `.claude/skills/speaking-vsl-uebersetzung/` · Soll beim Bau:
Übersetzen IN die Clip-Zeitfenster: jede Zeile an ihre Clips gebunden (Format
`Cxxx–Cyyy | Zeile`), Budget = SPRECHZEIT der Zielsprache im Fenster. Deutsch läuft
gesprochen ~20–30 % länger als Englisch — kürzen gehört zum Handwerk, das
Abweichungs-Protokoll (GEKÜRZT/ERGÄNZT/VERSCHOBEN/TAUSCH) ist Pflicht. Übersetzen ja,
lokalisieren nein (das kommt in A7). **Messauftrag an den ersten Lauf:** das exakte
Sprech-Band gegen die Sprech-Rate der gewählten Brand-Stimme messen (Silben/s aus dem
Stimmen-Register) — dann wird es Gesetz. Erbgut: die Schwester löst dasselbe Problem
mit Gesangs-Budgets (`referenz/Longform-Singing-VSL-Quasi.json`, Knoten „uebersetzung“).

**A7 · Markt-Prüfung [GEBAUT]** — `skills/singing-vsl-dach-lokalisierung/`
Prüft die Übersetzung aus Sicht der Zielkäuferin des Marktes und liefert NUR einen
Befund in Stichpunkten (Muss / Graubereich / passt) — kein Wort der Copy wird vor dem
Entscheid geändert. (Der beiliegende Skill ist auf DACH geeicht; anderer Markt = Skill
kopieren und Markt-Regeln tauschen.)

**A8 · Markt-Entscheid [GATE]**
Der Mensch liest Befund + Copy und entscheidet jeden Punkt („passt“ / „ändere …“).
Erst danach wird Freigegebenes eingearbeitet und die finale Copy mit dem Quellvideo in
`inbox/` gelegt — der Start des Sprech-Flows.

---

## Etappe B — Die Brand-Stimme (einmal je Brand, dann nie wieder)

**B1 · Projekt-Bootstrap [GEBAUT]** — `tools/sp/new_sp_project.py` · Soll beim Bau:
Pipeline-Ordner anlegen, Copy+Video aus `inbox/` holen, Quelle MESSEN (Frames/fps/Dauer
per ffprobe), Konstanten in `_pipeline/sp_config.json` schreiben, Pipeline des neuesten
SP-Projekts portieren. Bekannte Falle beim Portieren: Projektnummern-Ersatz darf keine
Zahlen-Literale in Skripten verstümmeln — nach jedem Port prüfen.

**B2 · Stimm-Casting [GEBAUT]** — `.claude/skills/speaking-vsl-stimm-casting/` · Soll beim Bau:
Läuft NUR, wenn das Stimmen-Register für die Brand leer ist. 3–5 Stimm-Kandidaten
(ElevenLabs Voice Design — Ausgangs-Baustein liegt bei:
`referenz/voiceover-narrator-voice-design-prompt/` — oder Library-Stimme) sprechen
denselben Hook-Absatz der aktuellen Copy. **Hartes Gesetz: NIE die Original-Stimme der
Quelle klonen.** Ins Register schreiben: voice_id, Design-Prompt (zur Neuerzeugung),
Einstellungen, Aussprache-Lexikon der Brand, gemessene Sprech-Rate.

**B3 · Stimmen-Entscheid [GATE]**
Der Mensch hört die Kandidaten und wählt DIE Brand-Stimme — per Ohr, einmal je Brand.
Ab dann überspringen alle Läufe dieser Brand die Etappe B2/B3 komplett.

---

## Etappe C — Die Sprechspur (der Kern-Tausch gegenüber der Singing-Schwester)

**C1 · Sprechspur-Bau [GEBAUT]** — `tools/sp/sprechspur.py` · Soll beim Bau:
Die Copy absatzweise einsprechen lassen (Kontext-Verkettung, damit Ton und Energie über
Absatzgrenzen halten), je Absatz mehrere Takes; Wahl objektiv: Take muss ins Zeit-Band
seiner SOLL-Fenster passen, dann Maschinen-Ohr. Werkzeuge der Stimme: Betonungs-/
Pausen-Steuerung, Tempo über die STIMM-Einstellungen (nie über Abspiel-Beschleunigung),
Aussprache-Lexikon für Zahlen, Preise, Markennamen. **Gesetz: fertige Sprechspur =
Master, wird nie mehr angefasst.** Riesiger Vorteil dieser Linie: die Text-zu-Stimme
liefert die WORT-ZEITSTEMPEL GRATIS mit — der Wort-Cache entsteht beim Bau; kein
Demucs, kein Forced Alignment.

**C2 · sprech-watch, der Prüfer-Loop [GEBAUT]** — `.claude/skills/sprech-watch/` + `tools/sp/pruefer.py` · Soll beim Bau:
JEDE Zeile abhören (Anker-kalibriertes Maschinen-Ohr — nur Modelle, die an validierten
Referenz-Clips bestanden haben, dürfen urteilen): Aussprache von Zahlen/Namen/Garantie,
Hänger, Doppelwörter, Artefakte, Tempo je Fenster. Rote Zeile → NUR diese Zeile neu
würfeln und einsetzen (bei Text-zu-Stimme billig). Loop bis alles grün ist oder eine
Zone nach 3 Versuchen als benannter Trade-off dokumentiert wird. Erst dann ist die Spur
fürs Schneiden frei. Maschinen-Befunde stoppen den BAU, nie den Lauf auf den Menschen.

**C3 · Musikbett [GEBAUT]** — `.claude/skills/speaking-vsl-musikbett/` + `tools/sp/bett_pegel.py` · Soll beim Bau:
Eine nackte Sprechstimme klingt tot (die Singing-Schwester hatte das Problem nie — dort
IST der Song die Musik). Zwei Wege, Betreiber-Entscheid: **(a)** Instrumental der
QUELLE per Vocal-Removal ziehen — Stimmung + Dramaturgie-Timing gratis 1:1;
**(b)** eigenes Suno-Instrumental (Baustein liegt bei: `referenz/background-music-suno/`).
Pegel-Gesetz: Bett deutlich unter der Stimme, Absenkung unter Sprechpassagen. Die
Sprechspur bleibt Master.

---

## Etappe D — Bild auf Stimme

**D0 · Lip-Sync, nur Menschen [GEBAUT]** — `.claude/skills/speaking-vsl-lipsync/`
Spricht in der Quelle ein Mensch sichtbar in die Kamera (UGC, Ärztin, Presenter), bekommt er
nach der Audio-Prüfung einen deutschen Mund: kie.ai `volcengine/video-to-video-lip-sync` nur auf
den Frames mit frontalem Gesicht, alles andere bleibt Original mit der Stimme darüber. Die Frage
stellt der Agent am Start, nachdem er gemessen hat, ob überhaupt ein Mensch im Bild spricht.
Tiere, Cartoon- und 3D-Figuren bekommen nie einen Lip-Sync. Farbblitze und Blenden schneidet das
Skript aus den Aufträgen, die kie-Ausgabe bekommt die Farbkennzeichnung des Eingangs zurück, eine
Sichtprüfung Ein- gegen Ausgang entscheidet. Kosten: 8 kie-Credits je volle Sekunde. Ausgabe:
Einbau-Liste für die Bildmontage oder `_work/bild_lipsync.mp4`, das D1 rendert.

**D1 · Schnitt + Render [GEBAUT]** — `tools/sp/render.py` · Soll beim Bau (Erbgut: Block-Anker-Schnitt
der Schwester): Zeilen-Fenster aus dem Wort-Cache → Original-Clips hart an die Stimme
schneiden (moderates Tempo-Band je Clip, Region-Pooling, Verlust-Gate: kein Clip fällt
stumm) → Render mit Musikbett-Mischung. Nach jeder sprech-watch-Operation läuft dieser
Schritt zwingend NEU. Achtung: Sprechzeit ≠ Wanduhr — beim Rechnen gegen Clip-Fenster
immer die Wanduhr-Zeit des Videos nehmen.

**D2 · Abnahme: Zeile↔Clip-Kreuzcheck [GEBAUT]** — `tools/sp/abnahme.py` · Soll beim Bau:
Liegt jede gesprochene Zeile wirklich auf IHREM Original-Bild? Wörter aus dem Wort-Cache
gegen die Clip-Beschreibungen der Clip-Karte halten; Beweis-Frames an allen Stellen des
Abweichungs-Protokolls; Kontakt-Sheets über die volle Länge; Audio-Vollabgleich
(mittlere Abweichung pro Minute) plus Maschinen-Ohr.

**D3 · Fakten-Check mit echtem Auge [GEBAUT]** — `skills/watch-factcheck/`
Die fertige Ad ansehen und NUR Fakten gegen den Plan prüfen (richtige Person durchgängig,
Produkt da, Beat = Plan-Inhalt, kein Artefakt) — TRUE/FALSE, nie Timing, nie Geschmack.
Fund → Ursache liegt 1–3 Schritte zurück.

---

## Etappe E — Übergabe an den Menschen

**E1 · Captions [GEBAUT]** — `.claude/skills/speaking-vsl-captions/` · Soll beim Bau:
Caption-Häppchen (1–4 Wörter, max. 26 Zeichen, keine Satzzeichen) mit
Karaoke-Wort-Timings — direkt aus dem Wort-Cache des Sprechspur-Baus, ohne Umwege.
Dann das Übergabe-Paket schnüren. Zwei geerbte Gesetze gelten wörtlich:
(1) Der Lauf endet IMMER mit dem kopierfertigen Ein-Prompt IM CHAT — nie mit „das Paket
liegt bereit“. (2) Übergabe-Pfade zeigen IMMER auf die dauerhafte Werkstatt-Maschine,
NIE auf einen Wegwerf-Rechenknecht, der morgen gelöscht ist.

**E2 · CapCut-Aufbau am Rechner des Menschen [GEIST]** — Erbgut liegt bei:
`referenz/sa-captions-capcut.SKILL.md`, Schritte 6–8 — sie gelten hier unverändert:
Der Mensch fügt den Ein-Prompt in einen NEUEN lokalen Chat ein; der zieht das Paket per
rsync, baut den CapCut-Entwurf mit dem Projektnamen, wendet den Karaoke-Stil an,
Neustart, Bericht. Server-Schritte werden NIE wiederholt.

**E3 · End-Sichtung [GATE]**
Der Mensch sichtet die fertige Ad in CapCut und exportiert selbst. Sein Feedback wandert
als Workflow-/Skill-Änderung zurück (Use and Break) — nie nur als Projekt-Fix.

---

## Etappe F — Upload

**F1 · Ad-Upload [GEBAUT]** — `skills/ad-upload/`
Die exportierte MP4 landet im Einwurf-Ordner; im Chat entstehen Primary Text + Headline
aus der finalen Copy; dann legt das Upload-Werkzeug Video, Anzeigengruppe (1:1 aus einer
Vorlage-Anzeigengruppe) und Creative an — **die Anzeige IMMER pausiert**, scharf schaltet
nur der Mensch. Voraussetzung: eigenes Meta-Adressbuch (siehe `01-VORAUSSETZUNGEN.md` §4).

---

## Etappe P (parallel zu C/D) — Produkttausch

**P1 · Custom-Clip-Production [GEBAUT]** — `skills/custom-clip-production/`
Jeden in der Clip-Karte markierten Produkt-Clip durch einen eigenen Clip mit dem
rebrandeten Produkt ersetzen: Start-Frame editieren, animieren, in ganzen Sekunden
generieren, HART auf Originallänge schneiden. Referenzbilder des eigenen Produkts kommen
aus der Brand-Datenbank (`Product Reference/`).

**P2 · Custom-Clip-Prüfer [GEBAUT]** — im selben Skill
Jeder fertige Custom Clip gegen das Handlungs-Inventar des Originals: alle Handlungen
vorhanden UND zu Ende geführt, Markenname lesbar, genau EIN Produkt, Länge = Original.
TRUE/FALSE, kein Geschmack; FALSE → Prompt nachschärfen, max. 3 Versuche, dann Befund
an den Menschen. Die bestandenen Clips gehen in den Schnitt (D1).
