# Feedback-Log — Longform Speaking VSL Quasi

Format: Datum · Feedback-Wortlaut · Diagnose · destilliertes Prinzip · geaenderte Datei(en)

## 2026-08-20

**1 · „mitten im Video so uebel rote Striche … zieht sich das ganze Video lang"**
Diagnose: In den Frames NICHT reproduzierbar. Drei Ursachen geprueft und
ausgeschlossen — Differenzbild zeigt, dass Vmake ausschliesslich das Text-Band und
das Money-Back-Siegel angefasst hat; Farb-Tags sind durchgehend bt709; die roten
Flaechen sind Original-Effekte (Schmerz-Glow). Bleibende Hypothese: das finale
Video wurde unnoetig mit libx264 crf 20 NEU ENCODIERT, obwohl nur Ton dazukam —
eine zusaetzliche h264-Generation bricht zuerst an gesaettigtem Rot in Streifen auf.
Prinzip: **Ein Ton-Mux ist kein Grund, das Bild anzufassen** — `-c:v copy`, und die
Frame-Zahl beweist Bitgleichheit. Damit ist die Frage „kommt es von Vmake?" kuenftig
ohne Raterei beantwortbar.
Geaendert: `.claude/skills/vmake-caption-entfernen/SKILL.md`

**2 · „Der Untertitel muss auf einer Position, unten mittig, nicht in der Mitte"**
Diagnose: Untertitel unten verankert (Alignment=2), aber die Zeilenzahl schwankte —
der Block waechst nach oben, dadurch wandert der Text bei langen Zeilen in die
Bildmitte. Gemessen: Textmitte bei 42 % Hoehe statt im unteren Fuenftel; ein erster
Versuch mit dem vollen Sprechtext ergab sechs Zeilen, die oben aus dem Bild liefen.
Prinzip: **Feste Position, die die Zeilenzahl nicht verschieben darf** — hoechstens
zwei Zeilen je Einblendung, laengere Saetze werden aufgeteilt statt gestreckt.
Zusatz aus derselben Sichtung: eine Einblendung darf nicht ueber vier Szenenwechsel
stehen bleiben (1,5–3 s je Einblendung).
Geaendert: `.claude/skills/speaking-vsl-captions/SKILL.md` (NEU)

**3 · „den grossen Titeltext komplett ausgeblendet, anstatt ihn zu ersetzen"**
Diagnose: Die Kette behandelte jeden Text im Bild gleich. Der Hero-Titel ist aber
kein Untertitel, sondern Gestaltung — er traegt den Hook der ersten sechs Sekunden.
Entfernt und nicht ersetzt beginnt die Ad mit einem stummen Bild.
Prinzip: **Zwei Textsorten trennen** — Sprech-Untertitel werden ersetzt durch die
neue Sprache, Gestaltungs-Text MUSS ein Pendant bekommen und darf nie fehlen. Die
Liste wandert als eigene Datei an die Captions weiter.
Geaendert: `.claude/skills/vmake-caption-entfernen/SKILL.md`,
`.claude/skills/speaking-vsl-captions/SKILL.md` (NEU)

**4 · „Gib mir das Video ohne Untertitel — die mach ich selbst in CapCut"**
Diagnose: Ich habe die Untertitel eingebrannt, weil ich eine fertige Ad als Ziel
annahm. Der Workflow hat CapCut-Push als eigenen spaeten Knoten — Untertitel sind
Viktors Arbeit, nicht die der Kette. Eingebrannt sind sie endgueltig; in CapCut in
Sekunden verschiebbar.
Prinzip: **Die Kette liefert Bild + Sprechspur, nie eingebrannten Text.** Rote
Flagge: `subtitles=` oder `drawtext` in einem Auslieferungs-Kommando.
Geaendert: `.claude/skills/speaking-vsl-captions/SKILL.md` (NEU),
`workflows/eleven-labs-ripping-agent.json` (Knoten „captions" praezisiert + ref)

**Nebenbefund aus demselben Lauf (kein eigenes Feedback):** Das W/s-Band im
Uebersetzungs-Skill war zu optimistisch — 2,6–3,2 notiert, real 2,3 gemessen.
Geaendert: `.claude/skills/speaking-vsl-uebersetzung/SKILL.md`

**5 · „klingt nicht nativ, nicht fluessig, hoert mitten im Satz auf, roboterhaft"**
Diagnose: Jeder der sieben Bloecke wurde ISOLIERT erzeugt. Das Modell kannte den
Nachbarkontext nicht und legte in jeden Block eine Anfangs- und Schlussmelodie —
daher die Stopps ohne Satzzeichen und der zerhackte Gesamteindruck. Zweiter Fund:
Es lief `eleven_multilingual_v2`, obwohl `eleven_v3` im Konto liegt — eine ganze
Modellgeneration aus reiner Annahme verschenkt.
Prinzip: **Eine Copy ist EIN Sprechakt.** Ganze Copy in einem Take erzeugen, danach
an den GEMESSENEN Sprechpausen schneiden und auf die Zeitmarken legen; innerhalb
eines Blocks wird der Ton nie angefasst. Dazu: Modell-Liste des Kontos abfragen,
nie annehmen.
Geaendert: `.claude/skills/sprech-watch/SKILL.md` (NEU),
`workflows/eleven-labs-ripping-agent.json`

**6 · „erster bis fuenfter Frame: da sind immer noch die roten Striche"**
Diagnose: Viktors Zeitangabe war der fehlende Hinweis — meine frueheren Stichproben
begannen bei Frame 30 und haben den Hero-Titel nie gesehen. `videoscreenclear` ist
fuer Wasserzeichen und duenne Untertitel gebaut; der GEFUELLTE rote Titelbalken
ueberfordert das Inpainting: Buchstaben weg, Flaeche bleibt als Keil (gemessen:
Eingriff x 0–718 / y 148–394, Rueckstand x 4–485 / y 182–299, 0–3,5 s).
Prinzip: **Gefuellte Gestaltungs-Elemente hinterlassen immer Rueckstand — er wird
ABGEDECKT, nicht wegretuschiert.** Grossflaechiges delogo zerstoert mehr als es
rettet (718x270 loeschte im Test die halbe Animation); enge Box + leichte Glaettung
ist die Obergrenze, der Rest verschwindet unter dem deutschen Titel. Zusatzregel:
immer die ERSTEN Frames pruefen, nicht nur eine Stichprobe aus der Mitte.
Geaendert: `.claude/skills/vmake-caption-entfernen/SKILL.md`

**7 · „auf gar keine amerikanischen Stimmen … nimm die Stimme, die am besten zum Original passt"**
Diagnose: Ich hatte die Stimme aus den ~21 Konto-Standardstimmen gewaehlt (Matilda,
amerikanisch, „DE verifiziert"). Das Flag heisst nur, dass die Stimme Deutsch
aussprechen kann — nicht, dass sie deutsch klingt. Der eigentliche Pool ist die
oeffentliche Bibliothek: 400 weibliche deutsche Stimmen. Gemessen: Matilda 24,7 %
Tonhoehen-Variation, unterhalb des natuerlichen Bands von 25–35 %.
Prinzip: **Nur deutsche Muttersprachler, und die Wahl wird GEMESSEN statt geraten.**
Filterkette aus dem Quellvideo (Geschlecht + Alter der Avatarin) → Register
advertisement/social_media schlaegt Hoerbuch → descriptive ohne calm/chill →
Testzeile mit allen Finalisten → hoechste Variation im Band gewinnt. Ergebnis ins
Stimmen-Register, Casting laeuft nie wieder fuer dieselbe Marke.
Ergebnis: Juli – German, 30,8 % (Matilda 24,7 %).
Geaendert: `.claude/skills/speaking-vsl-stimm-casting/SKILL.md` (NEU),
`datenbanken/stimmen/` (NEU), `workflows/eleven-labs-ripping-agent.json`

## 2026-09-17

**1 · „Das Lip-Sync ist gut geworden … bei dem Hund musst du kein Lip-Sync machen, nur bei der UGC … nur immer Lip-Sync für Menschen machen … mach einfach Lip-Sync als Baustein"**
Diagnose: Im Lauf RAN 001 EL lief der Lip-Sync als Einschub neben der Kette; der Workflow kannte
keinen Knoten dafür. Drei Fehler dieses Laufs wären in jedem neuen Lauf wiedergekommen:
(1) Farbblitze und Schwarz-/Weißblenden im Lip-Sync-Eingang → 8 von 32 Clips mit hautfarbenem Block
im Untergesicht und Farbschleier über den ganzen Clip (Farbstich 20–28, sauber ≈ 1);
(2) sprechende 3D-Hunde gelippt → graue, verwaschene Nase, unscharfe Schnauze, doppelte Flasche;
(3) kie-Ausgabe ohne Farbkennzeichnung → ffmpeg las bt601 statt bt709 (YUV unverändert, U/V-Abweichung
< 0,1), Hauttöne verschoben (Farbstich Ø 3,63 → 1,00 nach Übertragen der Kennzeichnung, bitgleich).
Prinzip: Lip-Sync ist ein Werkzeug für sichtbar sprechende Menschen; was der Eingang an Nicht-Gesicht
mitbringt (Blitze, Blenden, Figuren) und was die Ausgabe an Metadaten verliert, wird vor dem Einbau
abgefangen — gemessen, nicht erhofft. Die Mund-Ton-Korrelation beweist nichts, die Sichtprüfung schon.
Geändert: `.claude/skills/speaking-vsl-lipsync/` (neu, 6 Skripte; der Blitz-Erkenner fand am Lauf alle
8 Stellen, die zuvor von Hand repariert wurden) · `workflows/eleven-labs-ripping-agent.json` (Knoten
`lip-sync` zwischen Audio-Prüfung und Schnitt, Startfrage am Trigger) · `datenbanken/sp-learnings/learnings.md`
(35–38) · `03-FALLEN-UND-TRICKS.md` · `02-ANLEITUNG-KNOTEN-FUER-KNOTEN.md` (D0).

**2 · Nachprüfung nach dem Lip-Sync-Farbfix: Farbstich im fertigen Bild stieg von 2,4 auf 5,1, auch am sauberen Clip**
Diagnose: Die Bildmontage schrieb RGB mit nur bt709-Tags — ffmpeg rechnet dann bt601. Vorher hob die unkennzeichnete kie-Ausgabe
das auf. Hin-/Rückweg gemessen: nur Tags → gelber Blitz Rot +2,0 / Blau −4,5; mit `out_color_matrix=bt709` neutral; Lesen ohne
`accurate_rnd` −2 Stufen.
Prinzip: Kennzeichnung ist Metadatum, Umrechnung ist Rechnung — beides muss stimmen; nach jedem Farb-Fix die ganze Kette messen.
Geändert: `.claude/skills/speaking-vsl-lipsync/scripts/lipsync_einbau.py`, `lipsync_farbe.py` · `datenbanken/sp-learnings/learnings.md` (39) · `03-FALLEN-UND-TRICKS.md`.

---

# Nachtrag 17.09.–27.09.2026 — Einträge dieser Kette aus dem Haupt-Log

## 17.09.2026 · hoerprobe_video.sh lief endlos und füllte die Platte — Dauer-Bezug und Selbstprüfung eingebaut
**Meldung (Schwester-Session, 20:10):** In `brands/RAN - Dr Randy/001 EL/_work/gate/` lag `hoerprobe_doreen.mp4`
mit 681 MB statt 2–5 MB; die Platte war um 19:55 bei 241 MB frei.
**Diagnose:** Werkzeug — `tools/sp/hoerprobe_video.sh` baut den Hintergrund aus `color=…` (Endlos-Quelle) ohne Bildrate, das
`overlay` ohne `shortest=1` und den Encode ohne `-shortest`. ffmpeg schreibt dann weiter, bis die Platte voll ist; der Prozess
hing im gemeldeten Fall über fünf Stunden mit offenem Schreib-Handle (Löschen allein gibt den Platz nicht frei).
Im Lauf RAN 001 EL war der Befund schon aufgefallen, aber nur in einer Projekt-Kopie (`_pipeline/hoerprobe.sh`) umschifft —
Werkstück statt Baustein, also kam der Fehler in der nächsten Session zurück.
**Prinzip:** Ein Fix im Projekt ist kein Fix. Und jede Endlos-Quelle in einem Filtergraph braucht ihren Dauer-Bezug plus eine
Erfolgskontrolle, die genau diesen Fehler sichtbar macht.
**Gebaut:** `tools/sp/hoerprobe_video.sh` — `color=…:r=25`, `overlay=…:shortest=1`, `-shortest`, dazu eine Schlusszeile, die
Audio- gegen Videodauer misst und bei Video > Audio + 1 s mit Fehler endet. Getestet: 60-s-Probe → 60,0 s Video, 3,2 MB.
**Besitz-Irrtum, korrigiert:** Ich hielt Datei und Prozess zuerst für fremd, weil die Zeitstempel (15:21 / 20:12) Stunden nach meiner
letzten Arbeit lagen — beides stammte aber aus MEINEM eigenen Hintergrund-Auftrag der Nacht („Hörproben je Stimm-Variante"), der seit
03:41 im selben Bug hing; die späten Zeiten sind Folge des Hängens, kein Besitz-Beweis. Beleg: der gekillte PID 85486 steht im Protokoll
dieses Auftrags. Lehre: Besitz an laufender Arbeit über die Prozess-Kette klären (`ps -o ppid`, cwd per `lsof`), nicht über mtime.
Nach Viktors Entscheid beendet und gelöscht (4,8 → 5,4 GB frei). Der Auftrag lief danach weiter und baute die letzte Hörprobe mit dem
reparierten Werkzeug in Sekunden (3,3 MB) — Gegenprobe bestanden. Die übrigen laufenden ffmpeg gehörten wirklich fremden Läufen
(DOG 001/003 EL, KRA 002/003 EL) und blieben unberührt.

## 25.09.2026 · VIS 019 EL · Gemini-Ohr: dritte Route gemini-3-pro (Werkzeug-Fix)
- Befund (gemessen 25.09.2026 ~19:15): kie.ai gemini-2.5-pro → 500 „The server is currently being
  maintained"; gemini-2.5-flash und gemini-3-flash → 422 „The channel is not supported";
  gemini-3-pro → Nur-Text „OK" UND Transkription des bekannten Hook-Satzes wortgleich
  (WORDS-Bindung 1,0, Kanal image_url, mono 48k). Am 21./22.09. war gemini-3-pro noch tot (422/500).
- Fix am WERKZEUG (nicht an einer Projekt-Kopie): tools/sp/emotions_karte.py und tools/sp/pruefer.py —
  ROUTEN um ("gemini-3-pro","image_url") als DRITTE Sprosse ergänzt. Geltende Reihenfolge (2.5-pro,
  2.5-flash) unverändert, WORDS-Bindung je Aufruf unverändert; die neue Sprosse greift nur bei Ausfall.
- Offen für Viktor: Ob gemini-3-pro als geltende Route ins Ohr-Gesetz der Workflow-Notiz wandert
  (spart ~60 s Wartezeit je Zeile, weil 2.5-pro bei 500 dreimal mit 20/40 s Pause probiert wird).

## 25.09.2026 · VIS 018 EL · Emotions-Karte: Timeout-Absturz (Werkzeug-Fix)
- Befund: `tools/sp/emotions_karte.py` brach bei Zeile 12 von 23 mit unbehandelter
  `subprocess.TimeoutExpired` ab (curl an gemini-3-pro, 300 s). Die Karte wurde erst am Ende
  geschrieben → alle 11 bereits bezahlten Urteile verloren; der Traceback druckt zudem den
  kie-Key ins Task-Log.
- Fix am WERKZEUG: Timeout zählt als Ausfall („kein Urteil", Ohr-Gesetz Punkt 3) → nächste Route;
  `_pipeline/emotions_karte.json` wird nach JEDER Zeile gesichert. Schwester-Sessions informiert.

## 25.09.2026 · VIS 020 EL · Prüfer: derselbe Timeout-Absturz wie in der Emotions-Karte (Werkzeug-Fix)
- Befund: `tools/sp/pruefer.py` ruft das Ohr per `subprocess.run(... timeout=300)` OHNE try — ein
  300-s-Timeout (gemini-3-pro, 25.09.2026 mehrfach gemessen) bricht den ganzen Prüfer-Lauf ab und druckt
  den kie-Schlüssel im Traceback ins Log. Gleiche Ursache wie VIS 018 EL in `emotions_karte.py`
  (mein eigener Emotions-Lauf starb daran bei Satz 18; Schlüssel im Projekt-Log geschwärzt).
- Fix am WERKZEUG: Timeout = Ausfall dieses Versuchs (`continue` zur nächsten Wartestufe/Route),
  nie Absturz. Laufende Prozesse behalten den alten Stand.
- Zweiter Befund (Vmake, VIS 020 EL): Voll-Lauf malte auf glatten/strukturierten 3D-Flächen ins
  Caption-Band (dunkle Bänder, Kästen in Blenden, orange/rote Flecken). Szenen-exakte Fenster-Läufe
  halfen bei 6 von 10 Szenen; wo nicht (Blende + Muskel-Szene, dunkler Rachen, Etui-Kante), trugen
  NB2-Clean-Plates bzw. eine Kanten-Plate per lokaler ECC-Affin + Poisson-Einsetzen. Maske muss den
  Caption-Schatten decken: gemessen oben ~30 px, unten ~45 px (Glyph-Umfeld ±7 px ließ einen Grau-Hof).
  Werkzeuge: brands/VIS - Visiovance Sleep Guard/020 EL/_pipeline/bild_basis020.py + kanten_fuellung020.py.

## 25.09.2026 · VIS 022 EL „Test Custom Clip" — Custom Clips für englischen Szenen-Text (Start+End-Frame)
- **Viktors Auftrag (Chat):** „all das, was in der Ad im Hintergrund auf Englisch ist, mit einem generierten Custom Clip
  ins native Deutsch ersetzen … Dafür kannst du auch Kling benutzen. Du weißt ja, wie es geht mit Start Frame und End Frame."
- **Ergebnis:** 5 Custom Clips (3D-Titel, Knet-Aufschrift, Figuren-Label, Wand-Logo, Endcard), Gate „Alle 5 einbauen";
  740 kie-Credits ≈ 3,70 $ (davon ~1,60 $ verworfene Würfe). Viktors Entscheid danach: „Ja, ab jetzt jede Ad" → Workflow
  Eleven-Labs-Ripping-Agent, Knoten custom-clips (KOMPLETT-DEUTSCH-REGEL). Später: „schreib … Custom Clips als Workflow auf" →
  Skill custom-clip-production §10 (Szenen-Text, Start+End-Frame) + Hinweis in §4.
- **Befunde, die §10 tragen (gemessen):** Vmake-Reste im End-Frame wurden von Kling zu Objekten animiert (blaue Platte,
  vorweggemaltes Pfeil-Dreieck) → Rest-Scan vor Kling; Neuwurf mit identischem Prompt löste den Titel stückweise auf statt
  zu scrollen → Text-Abgang im Rohclip prüfen, guten Wurf behalten; zwei freie Edits desselben Logos → Lichtkante beim
  Patch-Warp → Glyphen-Transfer per Homographie; Nano-Banana-Edits rechnen das ganze Bild neu (Median-Abweichung 1,7–3,9)
  → nur Textkästen übernehmen; Bau mit drei Voll-Arrays starb zweimal am RAM → streamen.
- **Offen gelassen (Viktor: „lass es einfach"):** Sprechspur-Sync — „Es heißt Sleep Guard Pro" ~2 s vor dem Wand-Logo, Ton
  nennt 99,99 € statt „bis zu 240 €" (ffmpeg-Schnitt der ElevenLabs-MP3 lag ~3 s neben den Wortzeiten). Ad trotzdem in
  CapCut gepusht („VIS 022 EL | 25.09.2026").

## 25.09.2026 · VIS 022 EL — Trockenlauf custom-clip-production §10, Befunde eingearbeitet
- **Anlass:** skill-crafter Schritt 5 (fremde Augen) fand 12 Rate-Stellen in §10: Geltung der Abschnitte für `form: text`,
  Frame-Formel, Seitenverhältnis, Wegwahl, End-Frame je Lage des Textes, Prüfer-Zeilen, Pfade/Arbeitsordner,
  Wortlaut-Quellen, Workflow-Verweise auf §4b/§4c, die es im Skill nicht gibt.
- **Umbau:** §10 kurz (Geltungstabelle + Abhak-Liste), der ganze Weg in `references/szenen-text.md`; §1 kennt `text` als
  markenunabhängigen Wert, der §2-STOPP gilt nicht für `text`. Workflow: Verweis-Nachtrag in den Knoten custom-clips und
  custom-pruefer.
- **Vorgeschlagene Schwellen am freigegebenen Material geprüft und verworfen:** Raffung ≤ 1,25× (freigegeben waren 1,48× und
  1,73× — Kling bewegt langsamer, Bewegungsmaß 0,90–1,06 des Originals) · Naht ≤ 3 × Nachbar-Differenz (Endcard-Naht 3,06×,
  unsichtbar) · Schärfe ≥ 0,5 als Grenze (Push-in-Clip 0,36, freigegeben) → die Referenz nennt gemessene Maßstäbe statt Grenzen.
- **Befund Geister-Messung:** gegen den letzten Frame VOR einer Blende messen — der Weißblitz-Frame, der schon die neue Szene
  zeigt, korreliert 0,84 mit dem geisterfreien CC2 (Frame vor dem Blitz: 0,10). Nachtrag im Workflow-Knoten custom-pruefer.
- **Kosten nachgebucht** (`.usage/direkt.jsonl`): f1389_240 (8) + cc5_roh der 240-€-Endcard (84) → Custom Clips VIS 022
  gesamt 832 Credits ≈ 4,16 $.
- **Nicht gebaut:** Die Muster-Skripte (composite, logo_warp, custom_bau) sind lauf-spezifisch; ein allgemeines Werkzeug fehlt.
- **Zweiter Trockenlauf (12 Befunde) eingearbeitet:** Wegwahl und End-Frame-Tabelle mit Vorrang (erste passende Zeile);
  Fenster = Text-Spanne statt Clip-Grenzen (Blenden außerhalb, `t_ersatz`); Basis-Reihenfolge wie `tools/sp/clip_karte.py`;
  bezahlte Schritte erst nach feststehendem Wortlaut (das spät entschiedene Offer kostete 92 Credits); Lip-Sync-Fassung ist
  Bau-Basis; ein Meldeweg (Beleg per Datei, Entscheid per Popup, Fenster bleibt bis dahin Original); Abbruch-Zweig für
  `kie_bild.py` (Stand per Task-ID holen statt neu würfeln); Arbeitsordner je Aufruf; Doppelregeln auf einen Ort gezogen.
- **Gate für Text-Clips (Selbst-Entscheid dieser Überarbeitung, Viktor kann ihn kippen):** Das harte Go aus §8 begründet
  der Skill mit dem Produkt-Label, das nur Viktor beurteilen kann. Text-Clips folgen deshalb `execute` („entscheiden statt
  warten“, Viktors Dauerregel „frag mich halt nicht“ vom 21.09.): Gate-Dokument immer vorlegen, bei grünem Prüfer und
  belegtem Wortlaut einbauen, am letzten Gate als Selbst-Entscheid aufführen.
- **Dritter Trockenlauf (8 Blocker) eingearbeitet:** `schnitt` rendert bei Text-Clips `bild_custom.mp4`, gebaut auf
  `bild_lipsync.mp4` (Nachtrag im Workflow-Knoten schnitt); versteckte Festwerte der Muster-Skripte benannt; Bibliothek:
  Text-Clip passt nur bei gleicher Quell-Szene und wortgleichem Text (Nachtrag in DATENBANK.md), `veraltet: JA` wird nie
  genommen — die Endcard `knet-endcard-spare-160` trug ein Offer, das nicht mehr gilt, Nachfolger `knet-endcard-spare-240`
  (der Clip aus der Ad); Abbruch-Zweig trennt Download-Fehler von „Job … fehlgeschlagen“; 3D-Lettern per zweitem Edit statt
  Homographie; ein Schema je Text-Fenster in custom_clips.json; §2 zeigte auf Server-Pfade (`/root/AWMS/`) und einen Skill,
  den es nicht gibt → auf `datenbanken/linien/linien.json` im Stamm umgestellt.
- **Befund am Rand:** Neben `<Stamm>/.usage/direkt.jsonl` (2.196 Zeilen) gibt es `~/AWMS/.usage/direkt.jsonl` (95 Zeilen,
  zuletzt VIS 016 EL) — `execute` 3b schreibt „AWMS/.usage“, das lesen Sessions verschieden. Nicht angefasst.

## 25.09.2026 · VIS 020 EL · Montage-Naht (Werkzeug-Fix) + Knoten-Reihenfolge (nur gemeldet)
- Befund: `tools/sp/sprechspur.py` (Montage) hängte das erste Wort eines Blocks an das Ende des vorigen, wenn
  Scribe dieses Wort anders hört („Folg" → „Folgt"): „…passiert. Folg · 0,5 s · der Luft". Die Blockgrenze
  rückte eine Wortstelle zu weit.
- Fix am WERKZEUG: Blockstart richtet sich nach der ersten Abbildungsstelle ≥ Grenze (`k_frei`), `i_l` nie vor
  die linke Hörstelle. Spur neu montiert, alle 8 Nähte gegengeprüft (Audio-Prüfungs-Gate grün, Viktor „Passt").
- Befund Workflow (NICHT geändert, zur Entscheidung): Knoten `clip-karte` läuft laut Graph vor `bootstrap`, braucht
  aber dessen `sp_config.json`/`source_words.json` → bricht ab. In VIS 020 EL Bootstrap vorgezogen (idempotent).
  Vorschlag: haupt-Kante bootstrap → clip-karte statt umgekehrt (Änderung per /feedback, nicht still).

- **27.09.2026** · „Jede Ad, die gerade aktiv arbeitet, soll bei jedem englischen Wort, das da steht, direkt einen Custom Clip haben. Die ganze Ad soll immer auf Deutsch sein. Deswegen ist der Lauf 29 auch falsch." (VIS 029 EL hatte eine `final.mp4` gemeldet, obwohl englischer Bildtext im Render stand) · **Diagnose:** Die Kette prüfte Bildtext nur gegen die Clip-Karte — also gegen das, was beim ERSTEN Durchgang auffiel. Es gab keine Bedingung, die den fertigen Render gegen englische Wörter hält, deshalb konnte ein Lauf „fertig" melden, ohne dass jemand log. · **Prinzip:** Die Abnahme prüft das ERGEBNIS, nicht die Absichtsliste — und Vollständigkeit wird gemessen (OCR über den Render), nicht geschätzt. · **Geändert:** `.claude/skills/custom-clip-production/SKILL.md` (neuer Abschnitt 11 „Abnahme: kein englisches Wort bleibt im Bild"), `workflows/Eleven-Labs-Ripping-Agent.json`, `workflows/Longform-Singing-VSL.json`, `workflows/Brands-VSA-Sing-Songs.json` (Knoten `abnahme`: Bildtext-Gegenprobe als Abnahme-Bedingung). Offen: `workflows/UGC-Ripper.json` hat keinen `abnahme`-Knoten — dort greift die Regel nur über den Skill.

## Kandidaten für den Workflow-Umbau — gesammelt 27.09.2026, gebaut wird NACH den VIS-Läufen 025–029
Viktors Ansage: „würde sagen wir müssten später, wenn die Ads fertig sind, den Workflow etwas anpassen."
Nichts davon ist umgesetzt — das ist die Vorlage für die Entscheidung.

1. **Weg-Entscheid nach vorn.** Heute kam das Preisschild erst, als bei VIS 029 schon 1.558 Credits weg waren.
   Der Knoten `custom-clips` soll nach der Bildtext-Inventur ein Popup stellen: Fundstellen, Kosten beider
   Wege, Messbefund — DANN erst bezahlte Aufrufe. (Belegt: 026 deterministisch 276 Cr fertig gegen 029
   Kling 1.558 Cr unfertig, Rest ~950 Cr.)
2. **Format-Riegel vor dem bezahlten Aufruf.** Bei VIS 029 sind 16 von 61 Nano-Banana-Edits im falschen
   9:16-Format erzeugt und verworfen worden (192 Cr). Seitenverhältnis des Ziel-Frames prüfen, bevor der
   Auftrag rausgeht.
3. **Pilot vor Serie.** Erst EIN Clip bauen und durch den Prüfer schicken, dann die restlichen. Bei 029
   waren 7 von 12 Clips rot — der Fehler wäre am ersten sichtbar gewesen.
4. **Buchungspflicht in den Knoten.** Jeder bezahlte Aufruf sofort nach `.usage/direkt.jsonl` mit
   Projektname im `notiz`-Feld. Heute mussten drei Läufe nachbuchen; ohne Projektname ist keine
   Ad-Kostenrechnung möglich.
5. **Preis-Datenbank.** ElevenLabs- und Vmake-Preise stehen nirgends im Repo, deshalb enden alle Bilanzen
   in Credits statt Euro. Eine kleine Datenbank mit Preis je Anbieter/Modell macht daraus Euro.
6. **ECC-Nachführung als Muster festschreiben** (Vollbild + Maske wie VIS 018/020/021/024). Die Variante
   „Matrix im Ausschnitt" rechnet ohne (I−A)·o falsch — bei 026 bis 13 px Versatz, „SLEEPEASE" fast 1 s sichtbar.
7. **UGC-Ripper hat keinen `abnahme`-Knoten.** Die Bildtext-Gegenprobe greift dort nur über den Skill,
   nicht über die Struktur.

**Nachtrag zu den Umbau-Kandidaten (27.09.2026, aus der Schluss-Bilanz VIS 029 EL):**
8. **Audio-Neuwürfe sind ein eigener Kostenblock.** 11 von 12 ElevenLabs-Takes waren Neuwürfe fürs
   Timing (9.994 Zeichen für eine 80-s-Ad). Der Sprechspur-Knoten sollte die Timing-Korrektur
   messen, bevor er einen neuen Take zieht.
9. **Verworfene Bild-Edits sind der größte vermeidbare Posten:** bei VIS 029 576 von 828 Credits
   (16 im Fehlformat, 14 für einen abgebrochenen Versuch 2, 13 Anker vor einem Fenster-Neuschnitt,
   3 ersetzte Fassungen, 2 Glitch-Tests). Kandidat 1 (Weg-Entscheid vorn) und 2 (Format-Riegel)
   hätten davon rund 360 Credits verhindert.
GEBAUT statt vorgemerkt: Die OCR-Gegenprobe in custom-clip-production Abschnitt 11 liest jetzt
JEDEN Frame statt eines 4-fps-Rasters (Beleg: „NO TMJ RISK" bei F2109 in VIS 029 EL).
10. **Text-lastige Szene → deterministisch, nicht Kling (gemessen bei VIS 025 EL).** Kling verzieht
    eingebrannte Schrift: Runde 1 fielen 13 von 14 Würfen durch, bei den Neuwürfen 4 von 10.
    17 von 24 Clips verworfen = 1.092 von 1.770 Credits (62 %). Der Knoten `custom-clips` sollte
    beim Typ `form: text` den deterministischen Weg vorschlagen und Kling nur anbieten, wo sich
    das BILD bewegt. Beleg gegenüber: VIS 026 EL, dieselbe Aufgabe, 276 Credits, OCR 0 Funde.
