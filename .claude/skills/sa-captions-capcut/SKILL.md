---
name: sa-captions-capcut
description: "Baut für eine fertige Singing-Ad wortgenau getimte deutsche Captions (Lyrics + Demucs-Vocal-Stem + ElevenLabs Forced Alignment + Musik-Finder-Häppchen-Regeln, Zahlen als Ziffern), exportiert sie als natives, bearbeitbares CapCut-Projekt und übergibt sie — läuft die Rechnung nicht auf dem Mac — als geschnürtes Paket samt fertigem Kopier-Prompt fürs Mac-Fenster. Nutzen, wenn Viktor sagt „mach die Captions", „push in CapCut", „exportier nach CapCut", „übergib an den Mac", „gib mir den Prompt für CapCut", „Captions wie beim Musik-Finder" — für jede fertige SA-Ad nach dem Fakten-Check."
---

**`<projekte-db>`** steht in diesem Skill für die Projekte-Datenbank der LINIE, die
dieser Lauf fährt. Aufgelöst wird sie über die Registry `datenbanken/linien/linien.json`
(Feld `projektDb` der Zeile, z. B. `datenbanken/projekte-rovina`); welche Linie gilt, sagt
der Rip-Auftrag, sonst Viktor am Trigger. Nie aus Gewohnheit die Quasi-Linie annehmen —
es entscheidet die Quell-Brand des Videos (Packshot, Marke im Bild, Page-Farm-Register
der Brand-DBs). `datenbanken/projekte` (ohne Zusatz) ist eingefrorener Alt-Bestand —
dort entsteht nie ein neues Projekt.

# Captions für Singing-Ads + CapCut-Export

Zweck: Aus der fertigen Ad + den gesungenen Lyrics ein CapCut-Projekt mit wortgenau
getimten Caption-Häppchen bauen — Karaoke-fähig, in CapCut stylbar. Der Text kommt
IMMER aus den Lyrics (nie aus einer Transkription), die Zeit IMMER aus dem echten Ton.
Eine Ausnahme hat der Text: Zahlwörter erscheinen als Ziffern (Schritt 4c) — Captions
sind Lese-Text im Sekundentakt, „37" liest sich, „siebenunddreißig" nicht.

**Zwei Rechenorte, eine Kette:** Schritte 1–5 rechnen dort, wo die Ad gebaut wurde
(in der Regel der Server); Schritte 6–8 brauchen CapCut und laufen deshalb auf dem
Mac. Verbindungsstück ist Schritt 5b (Übergabe) — er ist Pflicht, wenn beide Teile
nicht in derselben Session laufen.

Arbeitsverzeichnis: der `_pipeline/`-Ordner des Projekts (`brands/<Brand>/<NNN SA>/`;
`<NNN>` = die dreistellige Nummer aus dem Projekt-Ordnernamen, bei `001 SA` also 001). Python: `~/.venvs/sa/bin/python3`
(maschinen-spezifisch — auf fremder Maschine jedes Python ≥ 3.10 mit den Paketen
aus `scripts/requirements.txt`; überall, wo dieser Interpreter-Pfad auftaucht,
entsprechend ersetzen).
Eingaben: `../final/` (genau eine Ad-MP4 — sonst Viktor fragen, welche) ·
`../song/song<NNN>.wav` · Lyrics via `import suno<NNN>_lib` (liegt im CWD;
`suno<NNN>_lib.parse()` liest `../song/suno-prompt_DE.md` selbst und gibt
`(style, verses)` mit `verses[n]["lines"]`).
Wiederverwendete Technologie: `captions.py` und `capcut_export.py` liegen GEVENDORT
in diesem Skill (`scripts/`-Ordner neben dieser SKILL.md) — importieren, nicht nachbauen:
`sys.path.insert(0, '<pfad-dieser-SKILL.md-ohne-dateiname>/scripts')`, dann
`import captions` / `import capcut_export`. Beide Module sind reine Standardbibliothek;
was die übrigen Schritte an Paketen/Binaries brauchen, steht in `scripts/requirements.txt`.
Die Häppchen-Regeln stehen in `references/captions-regeln.md` (neben dieser SKILL.md).

## Vorgehen

1. **Alignment-Ton bauen — NIE den Voll-Mix nehmen.** Der Demucs-Vocal-Stem rechnet
   direkt hier auf dem Server (Rechenort-Regel:
   `.claude/skills/sa-resync-singing-ad/SKILL.md` §Rechenort), im Projekt-Ordner:
   `~/.venvs/sa/bin/python3 -m demucs --two-stems=vocals -n htdemucs -o demucs_out ../song/song<NNN>.wav`
   (auf fremder Maschine ein venv nach `scripts/requirements.txt`). Dann (Sekunden):
   `ffmpeg -i demucs_out/htdemucs/song<NNN>/vocals.wav -ac 1 -ar 16000 -b:a 64k captions_ton.mp3`.
   Grund (gemessen): Whisper wie Gemini halluzinieren auf musikdichtem Gesang; der
   Stem ist maskierungsfrei.
2. **Skript = die Lyrics wortgetreu:** alle Zeilen aus `parse()` mit Leerzeichen
   verbinden. Keine Umformulierung, keine Transkription. Satzzeichen bleiben drin —
   `haeppchen()` entfernt sie regelkonform selbst.
3. **Forced Alignment:** `captions.wortzeiten('captions_ton.mp3', skript, key)` — key =
   `ELEVENLABS_API_KEY` aus `~/.config/leichtkraut/.env` (Datei lesen, String
   übergeben; der Key liegt NIE im Repo — auf fremder Maschine die eigene Key-Datei
   oder die Umgebungsvariable). Rückgabe-Schema: `[{text, start, end, loss}]`.
   Das Ergebnis SOFORT als `captions<NNN>_fa_words.json` ins CWD sichern — vor jeder
   Prüfung (ein bezahlter Call geht sonst bei einem Prüf-Fehler verloren).
   **Erfolgskriterium: exakt gleich viele Wörter zurück wie im Skript.** Weicht die
   Zahl ab → nicht weiterbauen, Ton/Skript gegeneinander prüfen (falsche Datei?
   Voll-Mix statt Stem?).
4. **Kreuz-Verifikation:** FA-Zeiten gegen den unabhängigen Wort-Cache
   `../song/words_<NNN>.json` (Schema `[{"w":wort,"s":start,"e":ende}, …]`, Sekunden)
   messen: Wörter beidseitig normalisieren (Norm = Kleinbuchstaben, alles außer
   Buchstaben/Ziffern gestrippt — dieselbe Norm nutzt Schritt 4b), exakte Matches
   in Reihenfolge als Anker
   nehmen, Median-|Δ| der Startzeiten ≤ 0,3 s ist gesund. Größer → eine der beiden
   Zeitquellen zeigt aufs falsche Audio, stoppen. Fehlt der Cache, entfällt der
   Check ersatzlos — dann trägt das Wortzahl-Kriterium aus Schritt 3 allein, und der
   Bericht nennt das offen. Der Kreuz-Check läuft auf den UN-konvertierten
   FA-Wörtern (der Cache trägt Zahlwörter, wie gesungen).
4b. **Kollaps-Wächter (Pflicht — Wortzahl und Median sind hierfür blind):** Forced
   Alignment kann LOKAL kollabieren: Wörter, die im Ton fehlen oder es verwirren
   (z. B. Echo-Wiederholungen), stapelt es mit Null-Dauern auf einen Zeitpunkt —
   Wortzahl-Kriterium und globaler Median bleiben dabei grün. Wächter über die
   UN-konvertierten FA-Wörter (der Cache trägt Zahlwörter — gleiche Wortformen
   nötig): Dauer <0,03 s (kürzer als jede gesungene Silbe) ODER ≥4 Wort-Starts
   innerhalb von 0,15 s (dichter als singbar) = kollabierte Zone. Je Zone
   (±3 Wörter Rand) die Wörter im Wort-Cache verankern: exakte Norm-Sequenz im
   Zeitband der gesunden Nachbarwörter (±6 s) suchen, Treffer übernehmen die
   Cache-Zeiten; Wörter ohne Treffer proportional zur Zeichenlänge zwischen den
   nächsten verankerten Nachbarn verteilen. **Entfernt statt verteilt** wird nur
   eine ZUSAMMENHÄNGENDE Folge ab 3 Wörtern, deren Sequenz im Cache-Zeitband
   komplett fehlt — dann wurden diese Wörter nie gesungen (fuzzy Zeilen-Credit der
   Kaskade — `.claude/skills/sa-resync-singing-ad/SKILL.md` §Teil-Credits) → aus
   dem Caption-Strom nehmen und im Bericht ausweisen, denn Captions zeigen
   Gesungenes; einzelne trefferlose Wörter werden immer verteilt. Reparierte
   Wörter als `captions<NNN>_fa_words_repariert.json` ins CWD schreiben (die
   Roh-Datei aus Schritt 3 bleibt unangetastet als Beleg). Fehlt der Wort-Cache
   (Schritt 4 entfiel): nur Monotonie erzwingen + proportional verteilen, nichts
   entfernen, im Bericht ausweisen. Danach Monotonie erzwingen (Starts
   aufsteigend, Ende ≥ Start+0,02 s) und den Wächter erneut laufen lassen — weiter
   erst bei leerem Lauf; meldet er nach 3 Reparatur-Runden immer noch Zonen →
   STOPP und Befund an Viktor.
4c. **Zahlwörter → Ziffern (nach dem Kollaps-Wächter, vor den Häppchen):** ausführen:
   `~/.venvs/sa/bin/python3 <pfad-dieser-SKILL.md-ohne-dateiname>/scripts/ziffern.py captions<NNN>_fa_words_repariert.json captions<NNN>_ziffern_words.json`
   (Input = die reparierte Datei aus Schritt 4b; lief der Wächter dort leer,
   stattdessen die Roh-Datei `captions<NNN>_fa_words.json`)
   (das Skript liegt im `scripts/`-Ordner direkt neben dieser SKILL.md)
   Das Skript konvertiert Kardinalzahlen zu Ziffern („siebenunddreißig" → „37",
   „fünftausend" → „5.000"), merged Mehr-Wort-Zahlen samt Timings
   („siebenunddreißig Komma fünf" → EIN Token „37,5") und trägt die harte Sperre:
   „ein/eine/einen/einem/einer/eines" und „eins" werden NIE konvertiert (Artikel-
   Homonym — die „eine Katze → 1 Katze"-Falle), Ordinale und Bindestrich-Komposita
   bleiben Wörter. Warum vor den Häppchen: die Häppchen-Packung (max. Zeichen)
   soll mit den kurzen Ziffern rechnen. Erfolg = das Skript druckt die
   Konvertierungs-Bilanz und die Ausgabe-Datei existiert; bei einem Skript-Fehler
   STOPP (nicht von Hand konvertieren — Hand-Konvertierung bringt genau die
   Artikel-Fehler zurück, die das Skript verhindert). Vor dem ersten Einsatz einer
   Session einmal `~/.venvs/sa/bin/python3 <pfad-dieser-SKILL.md-ohne-dateiname>/scripts/ziffern.py --test`
   laufen lassen (muss „ALLE TESTS OK" drucken).
5. **Häppchen:** `captions.haeppchen(woerter_ziffern)` (die Datei aus 4c laden) →
   `captions.pruefen(h)` mit AKTIVER Standzeit-Prüfung: Bei Gesang steht jedes
   ehrlich getimte Häppchen über 0,25 s — ein Standzeit-Befund heißt hier immer,
   dass kollabierte Zeiten durchgerutscht sind → zurück zu Schritt 4b, nie
   exportieren; findet der Wächter dort zum Befund KEINE Zone, ist es eine
   Detektor-Lücke → STOPP und Befund an Viktor, nicht im Kreis laufen.
   Zusätzlich prüfen: Häppchen-Starts monoton aufsteigend. Ablage im
   CWD: `captions<NNN>_haeppchen.json`
   (die Ziffern-Fassung; die FA-Rohdatei aus Schritt 3 bleibt als Beleg liegen).
5b. **ÜBERGABE — Pflicht, sobald die Schritte 1–5 NICHT auf dem Mac liefen.**
   CapCut ist ein Programm mit Bildschirm und lebt nur auf Viktors Mac; die
   Schritte 1–5 rechnen auf dem Server. Zwischen beiden klafft sonst eine Lücke,
   die Viktor von Hand füllen müsste — und genau die darf er nie füllen müssen.
   Darum endet der Server-Teil IMMER so. Ausgeführt wird im **Agenten-Stamm** —
   das ist der Ordner, in dem `brands/`, `tools/` und `.claude/` nebeneinander
   liegen; vom Arbeitsverzeichnis der Schritte 1–5 aus sind das drei Ebenen
   hoch (`_pipeline/` → `<NNN SA>/` → `<KÜRZEL - Brand>/` → Stamm):
   ```bash
   cd ../../..
   ~/.venvs/sa/bin/python3 tools/sa/capcut_paket.py \
     --projekt "<NNN SA>" --brand "<KÜRZEL - Brand>" --name "<Projektname>"
   ```
   Die drei Werte kommen aus dem Dateisystem, nicht aus dem Kopf:
   - `<KÜRZEL - Brand>` und `<NNN SA>` = die beiden Ordnernamen des
     Produktionspfads `brands/<KÜRZEL - Brand>/<NNN SA>/`, in dem gearbeitet wird.
   - `<Projektname>` = der Ordnername unter `<projekte-db>/`, dessen
     `karte.md` auf genau diesen Produktionspfad zeigt. Mechanisch finden:
     ```bash
     grep -rl "pipeline-ordner: brands/<KÜRZEL - Brand>/<NNN SA>" <projekte-db>/*/karte.md
     ```
     Genau ein Treffer → dessen Ordnername ist der Wert. Kein Treffer oder mehrere
     → nicht raten, sondern Viktor die Kandidaten nennen und ihn wählen lassen;
     der Name landet später als CapCut-Projektname auf seinem Mac und ist dort
     seine Wiedererkennung.

   Das Werkzeug schnürt `brands/<KÜRZEL - Brand>/<NNN SA>/_capcut-paket/` (Ad-MP4,
   Häppchen, gevendorte Skripte, `fakten.json`, `ANLEITUNG-FUER-DIE-KI.md`) und
   schreibt den fertigen Mac-Prompt als Datei —
   `brands/<KÜRZEL - Brand>/<NNN SA>/PROMPT-FUER-MAC.txt`, identisch auch im Paket.

   **Bricht das Werkzeug ab**, nennt es den Grund; danach handeln, nie den Prompt
   von Hand basteln (er zeigte sonst auf ein Paket, das es nicht gibt):
   - fehlende Ad-MP4 / Häppchen / Song → den zugehörigen Schritt nachholen, dann 5b.
   - Vmake-Gate („Render lief auf unbereinigter Quelle") → Quelle nach
     `.claude/skills/vmake-caption-entfernen/SKILL.md` bereinigen, neu rendern,
     dann 5b. Bewusste Ausnahme nur auf Viktors Zuruf: `--ohne-vmake`.
   - jeder andere Abbruch (Python-Fehler, Skript nicht gefunden) → Fehlermeldung
     wörtlich an Viktor, nicht improvisieren.
   **Danach den Prompt zusätzlich WÖRTLICH in den Chat stellen** — in einem
   einzigen Codeblock, ohne Kommentar dazwischen, damit Viktor ihn in einem Zug
   kopieren kann.

   **Fertig ist der Lauf erst, wenn beides existiert: die Datei UND der Codeblock
   im Chat.** Ohne das ist die Ad nicht übergeben, egal wie fertig sie gerendert ist.
   Und im Abschluss-Bericht ehrlich bleiben: Nach 5b liegt die Ad **noch nicht in
   CapCut** — sie liegt übergabefertig bereit. „In CapCut" ist sie erst nach den
   Schritten 6–8 auf dem Mac.

   | Ausrede | Warum sie nicht zählt |
   |---|---|
   | „Der Pfad steht doch oben im Verlauf." | Viktor sucht nicht im Verlauf. Ein Lauf endet mit EINEM Block zum Kopieren. |
   | „Ich beschreibe die Schritte kurz in Worten." | Beschreibung ≠ kopierbarer Prompt. Der Mac-Chat braucht den Wortlaut, nicht die Zusammenfassung. |
   | „Das Paket liegt ja da, er findet es." | Das Paket ohne Prompt zwingt ihn, sich den Auftrag selbst auszudenken — das ist die Lücke. |
   | „Er hat diesmal nicht nach CapCut gefragt." | Der Skill heißt sa-captions-capcut. Der Export IST das Ziel. |

   Rote Flaggen (alle heißen: zurück zu 5b): „Ich melde nur kurz, dass es fertig
   ist" · „Den Prompt kann er sich aus dem Paket ziehen" · „Das ist hier anders,
   weil …".

   Läuft die Session ausnahmsweise AUF dem Mac (Bildschirm-Zugriff vorhanden),
   entfällt 5b — dann macht dieselbe Session direkt mit Schritt 6 weiter.
6. **CapCut-Export:** Projektname = der Name des Rip-Projekts (Ordnername unter
   `<projekte-db>/`, Konvention „KÜRZEL NNN | DATUM" — siehe dortige
   DATENBANK.md; bei Alt-Projekten anderer Muster gilt deren Ordnername
   wörtlich). Dann: `capcut_export.platz_machen(name)` →
   `media = capcut_export.media_pfad(name)` (Ordner; anlegen) → Ad-MP4 dorthin
   kopieren → Cover: `ffmpeg -ss 1.0 -i <media-Kopie> -frames:v 1 -q:v 3 cover.jpg` →
   `capcut_export.draft_bauen(name, clips=[{'pfad': <media-Kopie>, 'dauer': <Song-Dauer>}],
   captions=h, cover='cover.jpg')`. Die exakte Song-Dauer misst man am Song-WAV
   (soundfile: frames ÷ samplerate) — nie an der MP4 (AAC-Padding). Den Stil-Spender
   wählt `draft_bauen` selbst (neuestes echtes CapCut-Projekt); kein Argument nötig.
6b. **Default-Caption-Stil herstellen (nach draft_bauen; drei Stufen, alle Pflicht).**
   Warum: Die geerbte Schablone kann auf eine Text-Template-Ressource zeigen, die
   es im CapCut-Store nicht mehr gibt — dann tragen alle Caption-Clips rote
   Nachlade-Icons, das Text-Panel öffnet sich nicht, und der Renderer zeigt nichts
   oder den Demo-Text der Vorlage. Gemessen: die Skript-Stufe allein repariert das
   Rendering NICHT (sie macht nur Icons weg und das Panel bedienbar), und die
   UI-Stufe allein scheitert, solange die tote Ressource das Panel blockiert —
   darum beide, in dieser Reihenfolge:
   1. **Skript:** CapCut beenden (läuft es, verweigert das Skript mit Meldung), dann
      `~/.venvs/sa/bin/python3 <pfad-dieser-SKILL.md-ohne-dateiname>/scripts/caption_stil.py "<Projektname>"`
      — biegt die Template-Referenzen aller Captions auf den eingefrorenen Default
      (`assets/caption-stil-default.json`), pro-Caption-Verdrahtung bleibt
      unangetastet. Erfolg = Ausgabe endet mit „Bindungen individuell ✅"; jeder
      andere Ausgang (FEHLER-Zeile) → STOPP, Draft liegt als `.bak-stilfix`
      gesichert, Befund an Viktor.
   2. **UI-Apply — die Render-Strukturen baut nur CapCut selbst:** CapCut starten,
      Projekt öffnen, eine Caption in der Text-Spur anklicken → Panel
      „Text → Vorlagen", Haken „Auf alle Hauptuntertitel anwenden" gesetzt lassen →
      unter „Gespeichert" ERST eine ANDERE Vorlage anwenden, DANN die
      Karaoke-Default-Vorlage (Wort-Highlight gelb). Warum zwei Klicks: CapCut
      wendet nur bei echtem Vorlagen-WECHSEL an — nach Stufe 1 trägt das Material
      bereits die Ziel-Vorlage, ein Einzelklick wäre ein No-op. Texte und Timings
      bleiben bei beiden Klicks erhalten. Ohne Bildschirm-Zugriff in der Session:
      Viktor im Chat bitten (zwei Klicks in den Vorlagen, Haken ist gesetzt).
   3. **Render-Kontrolle:** an 2–3 Playhead-Positionen (Anfang/Mitte/Ende) prüfen,
      dass die DEUTSCHEN Caption-Wörter im Player stehen — nicht „Flexible
      editing …", nicht leer (ohne Bildschirm-Zugriff: Viktor bitten). Rendert
      weiter nichts oder Demo-Text → STOPP und Befund an Viktor, nicht raten.
   Soll ausnahmsweise bewusst die Schablonen-Optik behalten werden (Viktors
   ausdrücklicher Zuruf), entfällt dieser ganze Schritt.
7. **CapCut neu starten** (Projektliste wird nur beim Start gelesen):
   läuft `pgrep -x CapCut`, dann `osascript -e 'quit app "CapCut"'`, bis zu 5 s auf
   Prozess-Ende warten, notfalls `killall CapCut`; danach `open -a CapCut`. CapCut
   speichert Drafts laufend — der Neustart verliert nichts.
8. **Bestätigen:** Draft-Pfad + Anzahl Captions melden, plus die Ziffern-Bilanz aus
   Schritt 4c (wie viele Zahlen konvertiert) und etwaige Kollaps-Reparaturen bzw.
   entfernte nie-gesungene Wörter aus Schritt 4b. Optik/Position erben vom Spender —
   Stil ändert Viktor in CapCut, nicht wir. Lief ein bezahlter Dienst
   (ElevenLabs-FA), Verbrauch buchen wie in
   `.claude/skills/vmake-caption-entfernen/SKILL.md` §Abschluss-Beweis beschrieben
   (anbieter "elevenlabs", menge = Anzahl FA-Calls).

## Gotchas

- **Fremder Mac (Portabilität):** `scripts/captions.py` + `scripts/capcut_export.py`
  sind reine Standardbibliothek; `ffprobe` löst die Vendor-Kopie über den PATH auf
  (Homebrew-Orte als Fallback). Voraussetzungen auf der Ziel-Maschine:
  `scripts/requirements.txt` (Pakete + Binaries) und mindestens EIN echtes, von Hand
  gebautes CapCut-Projekt (Clips + Musik + Untertitel) als Schablonen-Spender —
  sonst bricht `spender_finden()` mit sprechender Meldung ab. Der Default-Stil
  (`assets/caption-stil-default.json`) trägt Store-Ressourcen: Karaoke-Vorlage
  „逐词高亮-黄" (resource_id 7331663243842227461) und Font „ZY Resolve"
  (resource_id 7317175475195875841) — beide lädt CapCut online über die
  resource_id nach; die eingefrorenen `Cache/effect/…`-PFADE in der Datei sind
  maschinen-spezifisch und dürfen auf fremden Macs tot sein (rotes Icon → Projekt
  öffnen/anklicken, online). Die Font liegt bewusst NICHT im Repo (Lizenz);
  scheitert ihr Nachladen dauerhaft, greift die Font-Reparatur im Gotcha
  „Rote Nachlade-Icons" bzw. der eigene Stil des Nutzers.
- **Ändert sich das Audio nachträglich NICHT** (z. B. nur Video per Vmake bereinigt),
  bleiben Häppchen + Timings gültig — Export einfach mit der vorhandenen
  `captions<NNN>_haeppchen.json` neu bauen (Schritte 6, 6b und 7), kein neues
  Alignment nötig.
- **Mehrere Text-Spuren oder Mikro-Sliver in CapCut = Häppchen-Zeiten kaputt.** Der
  Export baut genau EINE Text-Spur; überlappende oder Null-Dauer-Segmente verteilt
  CapCut beim Öffnen selbst auf Extra-Spuren. Die Ursache liegt dann immer in den
  Häppchen-Zeiten (Schritt 4b übersprungen oder durchgerutscht), nie in CapCut.
- `platz_machen` löscht nur EIGENE Exporte (erkennbar an `awms_media/`); ein echtes
  Viktor-Projekt gleichen Namens bricht mit Fehlermeldung ab — dann Namen klären,
  nie erzwingen.
- Kosten: 1 FA-Call fürs ganze Video (ElevenLabs); Demucs kostet nichts (eigener Server).
- Die Ziffern-Konvertierung gilt NUR für den Caption-Text — Lyrics/Suno-Prompt
  behalten Zahlwörter (Gesangs-Regel der Suno-Kaskade), der Wort-Cache bleibt wie
  gemessen. Niemals „zur Konsistenz" rückwärts angleichen.
- **Rote Nachlade-Icons auf ALLEN Caption-Clips** nach dem Export: erst Schritt 6b
  gelaufen? Der behebt die häufigste Ursache (tote Template-/Font-Referenz der
  Schablone). Bleiben Icons trotz 6b, sind es meist frisch geräumte Cache-Effekte:
  Projekt öffnen und abspielen bzw. ein Icon anklicken (online) — CapCut lädt den
  Effekt über seine Store-ID nach. Bei jedem Hand-Eingriff am Draft gilt: CapCut
  BEENDEN, Backup der *.json ziehen, JSON validieren vor dem Schreiben, zuerst
  Häppchen-Daten prüfen (Dauern/Monotonie) — nie Timings oder Häppchen wegen
  eines Stil-Problems anfassen.
- **Demo-Text statt Caption-Wörtern auf allen Clips** („Flexible editing …"):
  die pro-Caption-Verdrahtung (`text_info_resources` in den text_templates-
  Materialien) wurde überschrieben — passiert, wenn Template-Einträge im Draft
  komplett geklont statt feldweise ersetzt werden. `scripts/caption_stil.py`
  macht es richtig (KEEP-Felder); Rettung: Draft aus dem jüngsten `.bak-*`
  wiederherstellen und 6b erneut laufen lassen.
- Auch der Gedankenstrich „—" der Lyrics läuft als eigenes FA-Token mit
  Null-Dauer mit — unschädlich (die Merge-Schleife in `haeppchen()` fängt ihn),
  aber im Kollaps-Wächter (Schritt 4b) nicht als gesungenes Wort zählen
  (erkennbar an leerer Norm nach der Schritt-4-Regel: nichts übrig, wenn man
  alles außer Buchstaben/Ziffern strippt).
