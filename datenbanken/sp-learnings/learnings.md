<!-- Herkunft: referenz/speaking-learnings-konzentrat.md des Pakets (Laeufe des
     Ursprungs-Betriebs, 20.08.2026). Die Beleg-Verweise zeigen in dessen
     feedback_log, das dem Paket nicht beiliegt. Eigene Funde kommen per /rip dazu.
     Die Punkte 8-12 kamen aus den eigenen Laeufen des Pakets (ARE 002 EL); ihr
     feedback_log liegt ebenfalls nicht bei. -->

# Speaking-Kette — Learnings (Konzentrat)

1. **Eine Copy ist EIN Sprechakt.** Ganze Copy in einem Take, an GEMESSENEN Pausen
   schneiden, per adelay auf die Marken — nie blockweise erzeugen (klingt roboterhaft,
   Stimme hört mitten im Satz auf). Beleg: feedback_log 20.08.2026 #5.
2. **Deutscher TTS-Fluss trägt ~2,3 W/s** (Band 2,2–2,5). Budget je Fenster = Sekunden × 2,3;
   Zahl-Komposita kosten extra. Beleg: feedback_log Nebenbefund + Übersetzungs-Skill.
3. **Nur deutsche Muttersprachler-Stimmen** aus der öffentlichen Bibliothek; Wahl wird
   GEMESSEN (Tonhöhen-Variation 25–35 %). Konto-Standardstimmen sind amerikanisch,
   auch wenn „DE verifiziert". Beleg: feedback_log #7.
4. **Emotionen werden reverse-engineert, nie erfunden.** v3 ohne Vorgabe wiederholt
   oder würfelt Emotionen — erst die Original-Delivery je Zeile messen (Emotions-Karte),
   dann als v3-Tags auf die deutschen Zeilen.
5. **ElevenLabs one-shottet nie fehlerfrei.** Prüfer-Loop Pflicht (Rück-Transkription +
   Pausen-Messung + Gemini-Ohr); rote Zeile → nur diese Stelle neu, max. 3 Versuche.
6. **Modell-Liste des Kontos abfragen, nie annehmen** (eleven_v3 lag brach, weil
   multilingual_v2 angenommen wurde). v3 kann kein previous_text — der Ein-Take-Weg
   ersetzt es. Beleg: feedback_log #5.
7. **Ton-Mux ist kein Grund, das Bild anzufassen** — -c:v copy, Frame-Zahl beweist
   Bitgleichheit; Box-Overlay = einzige Encode-Ausnahme (crf 18 + bt709). Beleg: #1/#6.
8. **Copy am Gate immer als EN/DE-Zeilenpaar.** Viktor prüft die deutsche Zeile nur gegen
   das englische Original — eine Copy allein ist „nichts zum Vergleichen". Beleg:
   feedback_log 04.09.2026 #1 (ARE 002 EL).
9. **Szenenerkennung 0,30 ist auf einfarbigen Ads blind.** Auf der rosa Quasi-Ad fehlten
   11 harte Schnitte; Produkt-Fenster per Frame-Differenz (Diff > 18 auf 90×160 Grau)
   nachziehen, sonst bekommt ein Custom-Clip den falschen Start-Frame. Beleg: ARE 002 EL.
10. **Custom-Clips erst NACH der Audio-Prüfung starten.** 14 Clips vor dem Gate kosteten
    ~30 min Wartezeit für Viktor; das Gate braucht nur die Stimmen. Beleg: feedback_log
    04.09.2026 #2.
11. **Einbau frame-genau per Pipe, nicht per trim/concat.** Die Quelle lief 29,93 fps (VFR);
    der ffmpeg-Schnittgraph lieferte 4 Frames zu viel. `_pipeline/custom_einbau.py`
    (ARE 002 EL) reicht die Quelle Frame für Frame durch und tauscht nur die Fenster.
12. **Eingebackene $-Texte in 3D-Szenen im Frame-Edit mitübersetzen** („$210" → „210 €",
    „70% OFF" → „70 % RABATT") — der Edit-Schritt kann Typo; was erst später im Shot
    auftaucht (glühendes „FREE"), wird fette CapCut-Caption. Beleg: ARE 002 EL C02/C06/C11/C27.
13. **Vmake-Reparatur-Patch muss die VOLLE Kasten-Höhe des Untertitels decken.** Die Box
    aus dem Original messen (helle Pixel je Frame über die ganze Kasten-Zeit, y-Ausdehnung
    wandert: 877–1001 bei 0–2 s, 987–1111 bei 2–3,9 s), nie aus dem Band schätzen. YUR 003 EL
    v1 ließ so den ersten Untertitel stehen, obwohl Vmake ihn entfernt hatte. Beleg: karte
    YUR 003 EL, _work/repair_cmd.sh vs repair_cmd_v5.sh.
14. **Vmake ist deterministisch.** Zweiter Lauf derselben Quelle = bitgleich (gleiche
    Scan-Regionen, gleiche Weiß-Werte) — Skill-Schritt „einmal neu einreichen" kostet nur
    Credits. Leucht-Schlieren auf dunklem Grund glättet ein dreistufiges delogo (enge Boxen
    je 3 Frames → breite Boxen mit Rand ≥ Halo, gemessen 60 px → statische Box + avgblur 4);
    EINE große Box schmiert, enge Boxen allein lassen eine Geisterlinie. Beleg: YUR 003 EL
    _pipeline/boxen.json, _work/check/schlieren_varianten*.png.
15. **Aufzählungen sprengen das Silben-Budget.** Yasmin dehnt Listenwörter auf 0,7–0,8 s
    („kaufen,", „gratis,", „Gratisversand"); eine vier-teilige Offer-Liste braucht ~40 %
    mehr Zeit als das Englische, unabhängig von Pausen (Squeeze greift nicht). Erst die
    kurzen Listen-Fenster bauen und EINEN Block messen; sonst Gate-Frage (Kürzung vs Bild).
    Beleg: YUR 003 EL B15 (4,65–4,90 s für 3,46 s).
16. **Prüfer-Rot ist erst rot, wenn die Zahl dahinter steht.** tools/sp/pruefer.py färbt
    falsch bei Bindestrich-Komposita („Collagen-Botox" ↔ Scribe „Collagen Botox"), beim
    Tausenderpunkt („142.000") und an Nähten ohne Stille ≥ 0,35 s (Einsatz-Suche findet die
    vorige Phrase). Wahrheit für Marken ist die Abnahme-Kreuzkorrelation (0 ms); Nähte gegen
    das Original messen (DE 0,12–0,14 s vs EN 0,16–0,20 s). /feedback-Kandidat. Beleg: YUR 003 EL.
17. **Knappes ElevenLabs-Kontingent: Block-Würfel statt ganzer Take.** Ein Block als
    eigener Mini-Take (70–110 Zeichen, zwei Würfe, der passende gewinnt) an den gemessenen
    Pausen in den Take gesetzt hält das Ein-Take-Gesetz an allen anderen Nähten und kostet
    ein Zehntel. Take v3 → v4 in YUR 003 EL: zwei Würfel, alle 17 Blöcke grün. Beleg: karte.
18. **Die Stimme entscheidet über die Copy-Länge, nicht umgekehrt.** Irene UGC spricht
    dieselbe Copy 17 % langsamer als Yasmin (Hook 4,90 s gegen 4,20 s); Viktor wählte sie
    bewusst („langsamer = mehr Betonung"). Folge: zweite Kürzungsrunde über alle 17 Blöcke
    (Silben-Ziel = gemessene Blockdauer × Stimm-Faktor ÷ Fenster × 1,06). Erst die Stimme
    am Hook messen, dann übersetzen — sonst wird zweimal gekürzt. Beleg: YUR 003 EL.
19. **Casting bei leerem Kontingent:** Bibliotheks-Previews (`preview_url`) kosten nichts,
    tragen die Rangfolge (Variation dort 4–6 Punkte unter der Testzeile, weil ohne Tags),
    dann EIN Hook-Test je Finalistin (68 Zeichen) — Viktor hört die echte Zeile, der Rest
    des Kontingents geht in den einen Take. Amerikanische „DE-verifizierte" Stimmen
    (Brittney, Juniper, Arabella) tauchen im `language=de`-Filter auf: immer zusätzlich
    `locale` auf `de-*` filtern. Beleg: YUR 003 EL Casting 06.09.2026.
20. **Fluss ist messbar: Ø-Pause zwischen den Sätzen.** Viktors Befund „die Cuts sind nicht
    flüssig" ließ sich in einer Zahl fassen — seine guten Ads (ARE 001/002) atmen Ø 0,45 s
    zwischen den Sätzen, die beanstandete Spur nur 0,32 s. Ursache war nicht die Stimme,
    sondern die Montage: harter Rand-Trim (0,05 s), DEHNEN kurzer Blöcke (atempo 0,94 frisst
    den Absatz-Atem) und harte Schnitte. Fix `_pipeline/montage_fluss.py` (YUR 003 EL):
    Ziel-Atem 0,45 s vor jeder Marke, Anlauf 0,10 s stehen lassen, nie dehnen, 15-ms-Fades,
    Eskalation Pausen-Quetsche → atempo ≤ 1,08 → Atem opfern mit Befund. Vor jedem Fluss-Urteil
    die Ø-Pause messen, nicht hören.
21. **Der Atem muss in die Copy eingeplant werden, nicht danach gesucht.** Ziel-Sprechzeit je
    Block = Fenster − 0,45 s (letzter Block: volles Fenster). Bei einer 1:1-gerippten Quelle,
    die fast pausenlos durchspricht (Stille 1,4 %), heißt das: die deutsche Copy muss kürzer
    sein als das Fenster suggeriert. In YUR 003 EL waren das 24 Silben (8 %) zusätzlich zur
    normalen Kürzung.
22. **Stimmen aus eigenen Gewinner-Ads klonen (IVC) schlägt die Bibliothek.** Demucs-Vocal-Stem →
    Hochpass 80 Hz → Stillen > 0,6 s raus → loudnorm −18 → `/v1/voices/add` mit
    remove_background_noise=true. Kostet keine Zeichen, braucht einen Voice-Slot, und der Klon
    spricht Deutsch akzentfrei (Akzent-Ohr `_pipeline/akzent_ohr.py`) — auch der Klon einer
    ENGLISCHEN Sprecherin. Vor der Wahl immer den echten Hook mit jedem Klon messen: in
    YUR 003 EL lagen zwei Klone derselben Machart 15 % auseinander (4,32 s gegen 4,96 s).
23. **Take-Streuung schlägt Copy-Feinjustierung — deshalb blockweise aus mehreren Takes wählen.**
    Derselbe Stimm-Klon sprach fast dieselbe Copy einmal in 75,96 s, einmal in 82,21 s (8 %).
    Wer die Copy nachjustiert, um 0,3 s Atem zu gewinnen, jagt einem Zufallswert hinterher.
    `_pipeline/block_auswahl.py` (YUR 003 EL) vermisst jeden Block in JEDEM vorliegenden Take
    und nimmt je Block die Fassung, die am nächsten an (Fenster − Atem) liegt; Überlänge doppelt
    gewichtet. Wichtig: die gewählten Copy-Zeilen zurück in de_copy.json und marken.json
    schreiben, sonst beschriften die Captions einen Ton, der so nie gesprochen wurde.
24. **Zu viel Atem ist auch ein Fehler.** Der Prüfer meldet Stille > 0,8 s zwischen Blöcken als
    tote Luft, und Viktors Referenz hat als längste Pause 0,71 s. Die Atem-Regel braucht also
    beide Grenzen: Ziel 0,45 s, Deckel bei ~0,7 s. Ein Loch entsteht dort, wo die Copy für ihr
    Fenster zu kurz ist — Gegenmittel ist die originalnähere, längere Formulierung, nicht Dehnen.
25. **Zahlen über 100 zerreißen jedes Wort-Alignment — und damit den Schnitt.** Die Copy trägt
    „142.000", der Ton sagt „Hundertzweiundvierzigtausend": ein einziges gehörtes Token gegen
    zwei geschriebene. difflib findet keinen Match, die Blockgrenze rutscht MITTEN ins Zahlwort,
    und der Schnitt macht aus „142.000" ein „42.000" — ein Faktenfehler, den kein Ohr-Urteil
    meldet, weil die Aussprache ja sauber ist. Jede Alignment-Stelle braucht deshalb: Ziffern zu
    Zahlwörtern normieren UND das Ergebnis an den Fugen zerlegen („hundert", „tausend",
    „million"), weil „einhundert…" und „hundert…" sonst wieder auseinanderlaufen. Gegenprobe:
    den fertigen Block einzeln zurücktranskribieren und die Zahl lesen. Beleg: YUR 003 EL B11.
26. **Der Prüfer findet, was die Messung nicht sieht.** Atem-Profil, Frame-Zahl und Loudness waren
    grün, während die Ad einen falschen Zahlen-Claim trug. Reihenfolge deshalb immer: messen,
    montieren, rendern — und DANN den Prüfer laufen lassen, bevor irgendetwas als fertig gilt.
27. **Marken planen schlägt Blöcke quetschen — aber nur, wenn Anker Platz lassen.** `marken_planen.py`
    verteilt die Zeitmarken aus der gemessenen Sprechdauer und verankert dabei jede Marke, die im
    Original auf einer Bildschnittkante liegt. Bei einer dicht geschnittenen Quelle (YUR 003 EL:
    16 von 17 Marken auf Kanten) bleibt dem Planer fast kein Spielraum — dort entscheidet weiterhin
    die Copy-Länge je Block. Reihenfolge, die funktioniert: Block-Fassungen wählen → messen MIT
    --ersatz → planen → montieren. Wer nach der Auswahl nicht neu plant, montiert gegen die alten
    Fenster und bekommt Löcher.
28. **Jedes eigene Alignment-Skript braucht dieselbe Zahlwort-Normierung.** Der Fehler „42.000"
    statt „142.000" kam beim Neubau zurück, weil das Auswahl-Skript die Normierung nicht hatte,
    obwohl das Montage-Werkzeug sie trug. Wo eine Blockgrenze berechnet wird, muss die Normierung
    stehen. Sicherste Lösung für Sätze mit großen Zahlen: den Block als eigene Aufnahme montieren,
    dann kann keine Grenze ins Zahlwort rutschen.
29. **Eine schnellere Stimme kauft Copy-Nähe zum Original.** Bei fest verankerten Marken entscheidet
    die Sprechrate, wie viel Text ins Fenster passt. Ela (Hook 4,23 s) trug an vier Stellen die
    vollere Originalfassung, wo Irene (4,90 s) gekürzt werden musste. Vor der Stimmwahl deshalb nicht
    nur den Klang beurteilen, sondern den Hook messen und hochrechnen, wie viele Silben die Ad dann
    verträgt. Beleg: YUR 003 EL, drei Durchgänge mit derselben Kette.
30. **Der Weg zu null toter Luft ist eine Schleife, keine Einstellung.** Reihenfolge, die im dritten
    Durchgang zum Ziel führte: zwei Takes unterschiedlicher Copy-Länge → je Block die passende Fassung
    wählen → Luft je Block messen → Blöcke über 0,72 s Luft mit der volleren Formulierung neu würfeln
    → erst dann Marken planen und montieren. Wer nach dem Füllen nicht neu misst, kippt in Überlänge
    (gemessen: eine zu volle Fassung sprengte das Fenster mit atempo 1,16 und brach die Montage ab).
31. **Kommentar-Blasen aus der Quelle werden nachgebaut, nicht überklebt.** Für englische
    TikTok-Reply-Bubbles im Bild reicht keine CapCut-Caption: Das Original hat Box, Radius,
    Avatar-Kreis, graue Kopfzeile und Zeilenraster exakt gesetzt. `tools/sp/overlays.py` (Art
    „blase") baut das deterministisch nach, wenn die Zahlen aus dem Frame gemessen werden:
    Boxkanten über die weiße Fläche, Farben über die hellsten und dunkelsten Pixel darin,
    Zeilenhöhen über den Anteil dunkler Pixel je Bildzeile. Deutsche Zeilen müssen kürzer sein
    als die englischen, sonst laufen sie aus schmalen Boxen; auch die Kopfzeile („Antwort an
    username" statt der wörtlichen Übersetzung). Immer erst `--vorschau` über den Original-Frame
    ansehen, dann brennen. Beleg: YUR 003 EL, fünf Blasen.
32. **Einbrennen ist erlaubt für statische Gestaltungs-Elemente, nicht für Mitlese-Captions.**
    Viktors Entscheid 08.09.2026. Der Render läuft dann im Encode-Zweig; Gegenprobe pflicht:
    mittlere Pixeldifferenz außerhalb des Overlay-Fensters gegen die Copy-Fassung messen, sie
    muss auf Encode-Rauschen bleiben (gemessen 0,55–0,74), sonst wurde mehr angefasst als geplant.
33. **Die Kundensprache-Datei ist ein Pflicht-Input der Übersetzung, kein Extra.** Sie wurde im
    YUR-003-EL-Lauf komplett übersehen, obwohl der Skill sie als Pflicht führt und die Brand-DB
    sie hat. Vor dem ersten Take prüfen: Führt die Ziel-Brand eine `kundensprache-de.md`
    (Spalte `brand_db` in sp-brands)? Dann jede Zeile ihrer Tabelle gegen die Copy halten und
    jeden Fund protokollieren — auch die Lücken, denn die Lokalisierung liest nur diesen
    Abschnitt. Wer sie überspringt, merkt es nicht: die Copy ist trotzdem korrekt, nur eben
    ohne ein einziges Wort der Zielgruppe.
34. **Wenig Tausch ist ein Befund, kein Fehler.** In dieser Ad war genau ein Wort belegt
    tauschbar. Grund: Die Datei ist stark bei Anwendung, Handhabung und Skepsis, die Ad spricht
    aber über Sofort-Wirkung und Angebot. Das gehört so in den Bericht — nicht mit ungedeckten
    Wörtern aufgefüllt. Themen aus der Datei (Schlafkomfort, Verträglichkeit) sind kein
    Wortebenen-Tausch: sie hinzuzufügen wäre Inhalt, den das Original nicht sagt.
35. **Lip-Sync nur für Menschen, deren Lippen im Original sichtbar sprechen.** Tiere, Cartoon- und 3D-Figuren nie: das Modell
    macht Nasen grau, Schnauzen unscharf, Objekte doppelt, und das Maul folgt trotzdem dem Original. Beleg: feedback_log
    17.09.2026 (RAN 001 EL, Fassung B). Knoten `lip-sync`, Skill `speaking-vsl-lipsync`.
36. **Farbblitze und Blenden gehören nie in einen Lip-Sync-Auftrag.** Dort malt der Lip-Sync eine hautfarbene untere
    Gesichtshälfte und färbt den ganzen Clip ein (8 von 32 Clips; Farbstich 20–28, sauber ~1). Bereiche davor enden lassen,
    die Blitz-Frames bleiben Original. Beleg: feedback_log 17.09.2026.
37. **kie-Ausgaben tragen keine Farbkennzeichnung.** Die YUV-Werte kommen unverändert zurück, aber ohne color_space — ffmpeg
    liest dann bt601 statt bt709 und verschiebt Hauttöne (Ø 3,6 statt 1,0). Kennzeichnung des Eingangs per h264_metadata
    übertragen (bitgleich, kein Neu-Encode). Gilt für jede kie-Video-Ausgabe, die in ein bt709-Bild eingebaut wird.
38. **Mund-Ton-Korrelation beweist keinen Lip-Sync.** Der Original-Mund korrelierte mit dem deutschen Ton so stark wie mit dem
    englischen; die Fehler fand erst die Sichtprüfung Ein- gegen Ausgang, Clip für Clip.
39. **Eine RGB-Pipe braucht die Farbmatrix ausdrücklich — Tags allein codieren bt601.** Ein Montage-Encoder mit nur
    `-colorspace bt709` verschob gesättigte Farben (gelber Blitz: Blau −4,5, Rot +2); Lesen ohne genaue Rundung machte das Bild
    ~2 Stufen dunkler. Schreiben mit `-vf scale=out_color_matrix=bt709:out_range=tv`, Lesen mit
    `-vf scale=flags=accurate_rnd+full_chroma_int` → Rückweg < 0,3 je Kanal. Nach einem Farb-Fix die ganze Kette nachmessen:
    zwei Fehler hatten sich aufgehoben, erst der eine Fix machte den anderen sichtbar. Beleg: feedback_log 17.09.2026.

40. **kie-Lip-Sync liefert IMMER 25 fps — unabhängig vom Eingang.** Ein 30-fps-Clip kommt als 25-fps-Datei zurück (gleiche
    Dauer, weniger Frames). Wer die Ausgabe frameweise einbaut, verschiebt den Ton gegen das Bild und verliert am Clip-Ende
    1–2 Frames. Abbildung statt Neu-Kauf: Ausgabe-Frame = round(t · 25) auf die Soll-Frames des Auftrags legen
    (`lipsync_fps_angleich.py`, 0 Credits), bezahlte Originale als `*_lipsync_25fps.mp4` behalten. Der Rest-Versatz von 1–2
    Frames am Clip-Ende liegt in den Schnitten und ist nicht sichtbar. Beleg: DOG 001 EL, 17 Clips, 12 mit Versatz.
41. **Ein Prüfer muss die Geometrie MESSEN, nicht nachbauen.** Der Caption-Deckungs-Prüfer modellierte die schwarze Karte per
    Aufruf des Render-Moduls nach und meldete „Rest sichtbar" in 1473 von 1514 Frames — die Karte im Bild kam aber aus einem
    anderen Skript und war größer. Das Maß, das das Karten-Rechteck aus dem fertigen Bild selbst holt (größter reiner
    Schwarz-Block im Band), fand 0 Frames mit Rest. Zwei Schwestern der Regel „nie mit dem Werkzeug des Eingriffs prüfen":
    der Prüfer darf weder dasselbe Werkzeug benutzen NOCH dessen Ergebnis nachrechnen. Beleg: DOG 001 EL 22:1x,
    `_pipeline/caption_deckung2.py`.
42. **Schwarze Caption-Karte: die Fläche bestimmt der Fleck, nicht die Schrift.** Wo eine Tilgung (Vmake) schwarze Flecken
    hinterlässt, muss die Karte die Vereinigung der Fleck-Boxen ihrer Karten-Zeit tragen — bei einer zweizeiligen
    Original-Caption wird sie dadurch groß, auch wenn nur ein Wort darin steht. Das ist kein Bau-Fehler, sondern die Folge der
    Tilgung; „klein" gilt relativ zum Fleck. Je Karte messen (nicht global), sonst springt die Fläche. Beleg: DOG-Linie,
    `datenbanken/brand-dogbiotics/captions-regel.md` (Viktors Stil-Entscheid 19:30).
43. **„Dunkel" ist kein Beweis für „verdeckt".** Wer prüft, ob eine schwarze Fläche einen schwarzen Rest verdeckt, darf nicht
    die Helligkeit des Ergebnisses zählen: Karte und Rest verschmelzen zu einer schwarzen Fläche, und das Maß meldet vor und
    nach dem Fix dieselbe Zahl (DOG 001: ~80 Frames, Maximum 175 px, identisch mit und ohne Randbündig-Fix). Es braucht eine
    Größe, die die Deckung selbst kennt — hier das ALPHA der eingebrannten Ebene gegen die Rest-Maske, volle Auflösung. Dieselbe
    Familie wie Lehre 41: der Prüfer muss messen, was er behauptet, nicht das Nachbild davon.
44. **Halbe Auflösung plus Sicherheitsrand blendet den Bildrand aus.** Ein Deckungs-Maß auf halber Auflösung mit 1 px Rand um
    die Karte verschluckt genau die 3–4 px am Bildrand, an denen ein geklemmter Platten-Einzug den Rest frei lässt (DOG 002 fand
    es, DOG 001 hatte es auch: 36 von 155 Platten). Randspalten immer getrennt und ungeschrumpft prüfen.

40. **kie liefert Lip-Sync-Ausgaben mit 25 fps.** Bei 30-fps-Quellen meldet `lipsync_lauf.py` dann „Ausgabe hat N Frames
    statt M" und würde jeden Auftrag NEU einreichen und neu bezahlen. Erst umrechnen (Frame-Wiederholung auf die
    Soll-Framezahl, Original als `*_lipsync_25fps.mp4` behalten), dann den Lauf erneut starten — er erkennt die Aufträge
    als fertig und schreibt nur die Einbau-Liste neu. Nebenwirkung, gemessen in KRA 002 EL: Die Umrechnung verschiebt den
    Bildinhalt in rund der Hälfte der Ausgaben um 2–3 Frames; sichtbar wird das nur bei schneller Bewegung am Clip-Ende —
    diese Frames als Übergangs-Fenster auf Basis stellen (0 Credits). Beleg: KRA 002 EL, 17 Aufträge.
41. **`lipsync_einbau.py` dekodiert die Basis ohne `-fps_mode passthrough`.** Ist die Vmake-Ausgabe leicht VFR
    (avg 29,98 statt 30,00 fps), dupliziert ffmpeg Frames und die Montage endet mit mehr Frames als die Quelle
    (KRA 002 EL: 4654 statt 4651, Abbruch mit „FEHLER: Ausgabe … statt … Frames"). Projekt-eigene Montage mit
    passthrough lesen — und gleich Bild-Texte und Untertitel mitnehmen, dann bleibt es bei EINER Encode-Generation.
42. **Vmake tilgt auch den Gestaltungs-Text — und verschmiert Endcards.** In KRA 002 EL waren nach `videoscreenclear`
    Titel-Balken, Pop-in-Titel, Namens-Einblendung, Zahl-Grafiken und beide Offer-Karten weg; die schwarze Endcard-Typo
    blieb als schwarze Klumpen stehen. Das ist kein Schaden, sondern die bessere Ausgangslage: Die sauberen Platten
    nehmen den deutschen Neusatz ohne zweites Überdecken auf. Nur verschmierte Flächen müssen im gemessenen Grund
    (hier Weiß 251,251,252) neu gedeckt werden. Vorher IMMER die Textsorten-Liste schreiben, sonst weiß man hinterher
    nicht mehr, was dort stand.
43. **Lange deutsche Komposita sprengen die Caption-Zeile.** „FÜNFUNDACHTZIGTAUSEND" lief bei 46 px aus dem 720er Bild.
    Die Karten-Schrift deshalb je Karte auf die Bildbreite einpassen (Schrittweite 2 px, Untergrenze 30 px) statt eine
    feste Größe zu fahren — Zeichen zählen reicht nicht, gemessen wird die Textbreite.
44. **Die letzte Copy-Zeile kann über das Videoende hinauslaufen.** Die Montage lässt den letzten Block ohne Längen-Leiter
    laufen; in KRA 002 EL endete er 0,17 s nach dem letzten Frame, das letzte Wort wäre angeschnitten worden. Nach jeder
    Montage das Ende des letzten Worts gegen die Videolänge halten und notfalls NUR den letzten Block straffen — dann
    bleibt der Lip-Sync aller früheren Clips gültig und nur der letzte Auftrag muss neu gerechnet werden.

## KRA 001 EL · 17.09.2026 (neue Linie Krallenflüsterer, heusom-Rip)
- **Atem am Original messen, nicht die Voreinstellung nehmen.** Die Montage-Voreinstellung 0,45 s je Blockkante stammt aus
  Viktors Referenz-Ads; diese Quelle hat an ihren 20 Blockgrenzen **Median 0,28 s**. Mit 0,45 s brauchte die Spur 3,6 s mehr,
  als das Video hergibt. Regel: Pausen der Quelle an den eigenen Blockgrenzen messen und als `--atem` setzen.
- **Take-Streuung schlägt Copy-Rechnen.** Derselbe Klon sprach dieselbe Copy-Menge einmal mit 2,44 W/s, einmal mit 2,36 W/s
  (3 %). Wer die Copy exakt auf ein Budget rechnet, baut beim nächsten Take wieder daneben: erst Take messen, dann Copy
  nachziehen — und Löcher lieber mit zurückgeholtem Original-Detail füllen als mit Dehnen.
- **Vmake tilgt auf dieser Ad auch den Gestaltungs-Text** (Titel, Zitatkarte, Siegel, Rabatt-Text, Endcard) und hinterlässt
  im Caption-Band **orange Kasten-Reste in 94 % der Frames**. Beides ist kein Schaden, wenn die Kette ohnehin deutsch neu setzt:
  Boxen aus der Differenz Original↔Vmake messen (das ist die exakte Text-Maske), deutsch rendern, Reste mit der Caption-Karte decken.
- **Deckung nie mit einem Helligkeits- oder Differenz-Detektor prüfen.** Drei naheliegende Detektoren meldeten 1199–1655 Frames
  Fehlalarm (Bewegung, Fell, Holzboden). Der Detektor, der hält: Pixel, die (1) Vmake verändert hat, (2) im Fertigen unverändert
  blieben und (3) die Farbe der Reste tragen → hier 0 Frames (`_pipeline/rest_offen.py`).
- **kie-Lip-Sync liefert 25 fps.** Ohne Umrechnung auf die Soll-Frame-Zahl hält der Lauf jeden Auftrag für gescheitert und
  bezahlt ihn neu (`lipsync_30fps.py` aus DOG 002 portieren, Reihenfolge: Lauf → 30 fps → Lauf erneut für die Einbau-Liste).
- **Der Frontal-Gesichts-Filter des Lip-Syncs ist streng:** von 10 Clips, in denen die Groomerin spricht, blieben 5 übrig
  (Split-Screens und Bild-im-Bild-Kreise fallen raus). Das ist richtig so — kleine Gesichter zeigen die englischen Lippen kaum.
45. **Die 0,45 s Atem sind Viktors REFERENZ, keine Konstante.** Wer die Montage blind auf 0,45 s Sprechpause baut, kriegt eine
    deutsche Spur, die nicht mehr ins Video passt. Den Wert je Lauf an den BLOCKGRENZEN DIESER Quelle messen — KRA 001 EL
    (heusom) lag im Median bei 0,28 s, DOG 001 EL arbeitet mit 0,12–0,55 s elastisch. Beleg: KRA 001 EL, 17.09.2026.
46. **Wo Vmake auch den Gestaltungstext tilgt, sind die Text-Boxen exakt messbar.** Auf den heusom-Ads bleiben orange
    Kasten-Reste in 94 % der Frames; die Boxen lassen sich aus der Differenz Original↔Vmake holen und deutsch neu setzen
    (0 Credits, `brands/KRA - Krallenfluesterer/001 EL/_pipeline/grafik_deutsch.py`). Die Farbe der Reste ist dabei das
    Erkennungsmerkmal — Helligkeits- und Differenz-Detektoren melden dort 1200–1650 Frames Fehlalarm, die Farbe der Reste
    trennt sauber (`_pipeline/rest_offen.py`). Gegenstück zur schwarzen Karte der DOG-Linie: dort deckt man zu, hier setzt man neu.
47. **Beim Einordnen von Rest-Kandidaten gibt es ein falsches und ein richtiges Kriterium — sie sehen sich zum Verwechseln
    ähnlich.** FALSCH: „im Original ist die Stelle auch dunkel und flach → Bildinhalt". Ein echter Kastenrest ist im Original
    ebenfalls dunkel und flach, der Kasten steht dort ja — das Kriterium sortiert genau die echten Funde weg (DOG 004:
    210 von 304 Blöcken so abgeräumt). Ebenfalls falsch: „weiße Caption-Schrift im Umfeld" — in hellen Szenen trennt das
    nichts (DOG 002: Schrift-Anteil 0,94–0,96 in einer weißen Infografik, drei Fehlalarme).
    RICHTIG ist die Drei-Wege-Messung: Original, getilgte Fassung und Lieferung an derselben Stelle messen. Sind alle drei
    gleich, hat die Tilgung dort nie gearbeitet → Bildinhalt, in einer Zeile erledigt, ohne Bildsichtung (DOG 001: Schatten
    unter einem Tisch, 52,3/51,9/52,2). Ihre eigene Restlücke — ein Kasten des Originals, den die Tilgung schwarz auf schwarz
    übermalt hat, wäre auch in allen drei gleich — schließt der Anteil kasten-schwarzer Pixel (< 25) im ORIGINAL: ein Kasten
    ist über fast seine ganze Fläche nahezu schwarz, ein dunkler Schatten liegt bei 40–60 mit Streuung (DOG 001: 0,0 % in
    beiden Kandidaten). Belege: DOG 001/002/004 EL, 17.09.2026 23:00–23:55.
- **Vmake tilgt nicht nur Text — es frisst auch Bildinhalt.** In KRA 001 EL hat das Inpainting einen weißen
  Hervorhebungs-Kreis, zwei Bild-im-Bild-Kreise und Kacheln einer UGC-Collage als Wasserzeichen behandelt und überpinselt
  (Viktor fand eine davon am fertigen Video). Pflicht-Prüfung nach jedem Vmake-Lauf: Differenz Original↔Vmake **oberhalb
  des Caption-Bands** über das ganze Video (`vmake_schaden.py`); echte Schäden von den absichtlich getilgten
  Gestaltungs-Texten trennen. Reparatur = Original-Pixel maskiert zurück, im selben Encode-Durchgang wie Captions/Grafik,
  Caption-Band nie restaurieren.
- **Overlay-Fenster am Original messen, nicht aus der Clip-Karte schätzen.** Die roten Labels lagen bei 7,17–9,23 s, das
  deutsche Overlay auf 8,40–9,25 s: 1,2 s lang stand die getilgte Fläche leer. Fenster aus der Farbfläche im Original messen.

45. **Vmake tilgt nicht nur Text — es retuschiert gemusterte Kleidung weg.** In KRA 002 EL hielt `videoscreenclear` die
    Pfoten-Schürze der Sprecherin für ein Wasserzeichen und verschmierte sie über 300 Bildzeilen; an einer Stelle
    verschwand auch ein Einklinker-Foto samt rotem X, und die schwarze Endcard-Typo wurde zu Klumpen. Viktor sah es
    sofort („sieht nicht so toll aus"). **Konsequenz für die Bildgrundlage:** Nicht die bereinigte Fassung als Basis
    nehmen, sondern das ORIGINAL — und die Vmake-Fassung nur dort einsetzen, wo wirklich englischer Text stand
    (Caption-Band, gemessene Kästen der Gestaltungs-Texte, Mund-Fenster des Lip-Syncs). Prüfsignal vor dem Render:
    Differenz Original ↔ bereinigt AUSSERHALB des Caption-Bands; ist sie großflächig, hat Vmake Bildinhalt gefressen.
46. **Die Untertitel-Karte wird an der ENGLISCHEN Caption bemessen, nicht an der Vmake-Fläche.** Deckt man die
    Vereinigung aller Flächen ab, in denen Vmake gearbeitet hat, wird die Karte bei Schlieren fast bildbreit — Viktors
    Befund „schwarzer Balken". Richtig: je Frame die dichten Diff-Spalten IM Band messen (das ist die getilgte Caption),
    je Karte den Median nehmen, auf einen Rand klemmen — dann ist die Karte so breit wie die Karte des Originals.
47. **Zeitfenster von Bild-Grafiken frame-genau messen, nie aus Kontaktbögen schätzen.** In KRA 002 EL fehlte dem Titel
    dadurch die dritte Zeile („EVER!" → „NIEMALS!"), und an drei Stellen blitzte der englische Text vor oder nach dem
    deutschen Ersatz durch (BEFORE/AFTER 0,3 s, 85.000-Zähler 0,4 s, „sharper than you do"). Messung: je Region die
    Diff-Pixel Original ↔ bereinigt pro Frame zählen, Fenster = alle Frames über 12 % des Maximums. Danach jede Grafik
    an ihrem ERSTEN und LETZTEN Frame einzeln ansehen — ein Sweep im 2-Sekunden-Raster findet solche Ränder nicht.
    **Nachtrag 18.09.2026 (Gegenmessung DOG 002 EL):** Der Schaden ist QUELLEN-abhängig, nicht generell. Dort lag die
    Änderungsfläche oberhalb des Bands im Median bei 0 px (95-Perzentil 2 px), das gestreifte Hemd des Sprechers blieb
    unversehrt (Streifen-Energie 7514 gegen 8243 im Original) — die bereinigte Fassung durfte dort Bildbasis bleiben.
    Also: erst messen (Änderungsfläche außerhalb des Caption-Bands je Frame), dann entscheiden. Nur wenn großflächig
    Bildinhalt verschwindet, lohnt der Umbau auf „Original als Basis". Ebenfalls dort bestätigt: Eine Mund-Region aus der
    größten kie-Änderung abzuleiten traf die HAND statt des Mundes — Gesichtserkennung ist auch ohne Frame-Versatz der
    richtige Weg.
- **Bildgrundlage ist das ORIGINAL, nicht die Vmake-Fassung** (KRA 001/002 EL, 18.09.2026). Die bereinigte Fassung kommt
  nur in den gemessenen Fußabdruck der englischen Caption und in die Kästen der englischen Gestaltungs-Texte; Lip-Sync-Frames
  aus dem Lip-Sync-Bild. Damit sind alle Vmake-Schäden strukturell weg statt einzeln repariert — und die Untertitel-Karte
  darf schmal bleiben, weil außerhalb des Textfußabdrucks gar keine Schlieren mehr im Bild sind.
  Werkzeug: `brands/KRA - Krallenfluesterer/001 EL/_pipeline/bild_final3.py` (+ `tilg_boxen.json`).
- **Untertitel-Karte an der ENGLISCHEN Caption bemessen, nie an der Vmake-Fläche.** Gemessen: englische Caption 532 px
  Median, Vmake-Schliere 610 px, daraus gebaute Karte 720 px = bildbreiter schwarzer Balken (Viktors Befund an KRA 002 EL).
40. **kie liefert Lip-Sync mit 25 fps — bei 30-fps-Quellen meldet der Lauf FEHLER und würde neu bezahlen.** Gemessen KRA 003 EL:
    Ausgabe 144 statt 173 Frames bei gleicher Dauer (5,77 s). Die bezahlte Ausgabe ist gut, nur das Raster stimmt nicht:
    `lipsync_30fps.py` rechnet sie per Frame-Wiederholung auf die Soll-Frame-Zahl (Original als `*_25fps.mp4` behalten),
    danach baut `lipsync_lauf.py` die Einbau-Liste ohne einen einzigen neuen Auftrag. Gilt für jede Quelle ≠ 25 fps.
41. **Ändert sich die Sprechspur nach dem Lip-Sync, ist der Lip-Sync ungültig.** Die Mundbewegung folgt dem Audio-Ausschnitt,
    der beim Auftrag geschnitten wurde; schon 0,2 s Marken-Verschiebung sind 6 Frames Versatz. In KRA 003 EL mussten alle 19
    Aufträge nach dem Copy-Fix neu gerechnet werden (2 × 488 Credits). Reihenfolge deshalb: Copy und Montage FERTIG prüfen
    (Prüfer + Lücken-Messung), erst dann Lip-Sync starten.
42. **Der Marken-Planer sammelt den Spielraum vor dem nächsten Anker — das wird eine hörbare Lücke.** KRA 003 EL: 5,6 s Stille
    bei 220 s, dazu 17 Löcher um 0,85 s. Zwei Hebel in dieser Reihenfolge: (a) Spielraum je Anker-Abschnitt gleichmäßig auf die
    Blöcke verteilen (Marken nachrechnen), (b) wo die Copy zu stark gekürzt wurde, die originalnähere, LÄNGERE Fassung
    zurückholen — nicht dehnen. Danach größte Pause 0,78 s. Messen statt hören: RMS-Fenster 20 ms, Schwelle max−45 dB.
43. **Vmake tilgt die Caption-Schrift, lässt aber farbige Marker-Kästen stehen.** Bei KRA 003 EL blieben die GELBEN Kästen der
    Karaoke-Spur in 92 % der Frames (Median 602×114 px). Messen: Gelb-Maske UND Nähe zu einer Vmake-Änderung (sonst zählt
    gelbe Szenen-Deko mit). Die eingebrannte Untertitel-Karte wird über die Vereinigung aus Text + Rest gelegt — genau das meint
    Viktors „verdeckt".
44. **Gestaltungs-Grafik ist nicht nur Text — auch Marker (rote X, Kreise, Siegel) verschwinden.** Und sie verschwinden NICHT
    überall: in KRA 003 EL war der rote X bei 131 s getilgt (22.146 → 454 rote Pixel), bei 187–191 s stand er weiter im Bild
    (57.023 → 57.122). Vor dem Nachbau je Fenster messen, ob das Element wirklich fehlt — sonst zeichnet man es doppelt.
45. **Fenster von Grafik-Elementen am Bild messen, nicht aus der Differenz übernehmen.** Die Differenz Original↔Vmake umfasst
    auch die getilgten Captions desselben Zeitraums; so startete eine schwarze Text-Karte 1,6 s zu früh über der Sprecherin.
    Schwarze/weiße Karten am mittleren Helligkeitswert des Originals abgrenzen (hier: 129 → 1,3 bei 180,3 s).
46. **`tools/sp/emotions_karte.py` stirbt am kie-Timeout und verliert alles.** `subprocess.TimeoutExpired` (curl 300 s) ist nicht
    abgefangen, und die JSON wird erst am Ende geschrieben — vier Parallel-Läufe verloren 48 gemessene Zeilen ins Log.
    Ausweg im Lauf: Log-Zeilen (`Zeile N: … · Tags [...]`) zurücklesen und nur die fehlenden nachfahren (`_pipeline/emo_resume.py`).
    /rip-Kandidat: Timeout abfangen + je Zeile zwischenspeichern.

47. **Vmake beschädigt Grafik außerhalb des Caption-Bands — und die Pixel-Zahl verrät es nicht.** In KRA 003 EL blieb die
    Rot-Fläche der X-Marker fast gleich (57.023 → 57.122 px), die FORM war trotzdem zerstört; der Röntgen-Einschub wurde zum
    Schmierer. Prüfen heißt: Differenz außerhalb von Band UND Grafik-Fenstern messen (Schwelle ~500 px), die Treffer clustern
    und die größten FRAMEWEISE ansehen — Zahl allein reicht nicht. Reparatur ohne Neu-Rendern der ganzen Kette: in genau
    diesen Fenstern das Original oberhalb der Bandkante zurückholen (ein Overlay-Encode), unten bleibt die bereinigte Fassung.

48. **Der Trigger des Ripping-Workflows heißt „Competitor-VSL" — das ist die Provenienz-Antwort, keine offene Frage.**
    Lauf 18.09.2026 (Quelle: VISIOVANCE Augen-VSL, 143 s, reines CGI): Der Deepfake-Riegel greift dort NICHT — es spricht
    kein Mensch, nur 3D-Figuren, also kein Stimmklon und kein Lip-Sync auf eine reale Person. Der zweite Grund greift
    trotzdem: `vmake-clean` + `produkt-abgleich` + `musikbett` („Original-Musik") + `schnitt` auf Originalframes heißt,
    die fertige Animation eines Wettbewerbers am Stück zu übernehmen. Prüfen lässt sich das in 30 s: Marke im Bild gegen
    `datenbanken/linien/linien.json` halten (VISIOVANCE = keine Linie) und den Dateinamen ansehen (sha256-Hash = Scrape,
    kein Master-Export). **Was stattdessen läuft und geliefert wurde:** der Bauplan der Quelle — Makro-Struktur, die
    Vierschritt-Schablone je Figur, Tempo-Profil (4,39 Silben/s EN, Median 4,5, Name 2,4–3,4 vs. Mechanismus 5,5–6,0),
    19 % Sprechpause, Bildrhythmus (8 harte Schnitte, 26 Einstellungen, Median 6,7 s) und das DE-Silbenbudget
    (509 → ~660 Silben, also 155–165 s Laufzeit statt 143 s). Siehe `analysen/BAUPLAN-visiovance-augen-vsl-2026-09-18.md`.

49. **Eine lesbare Caption, die medizinisch unmöglich ist, ist ein Auto-Caption-Garble — nicht die Wahrheit.**
    Lauf VIS 005 EL (18.09.2026, Quelle 3d001ad1, Visiovance-Skizzenbuch-VSL): Die eingebrannte Caption schreibt bei
    0:35 zweimal klar lesbar „CELLS CALLED **PARASITES**", Scribe hört „cells called **pericytes**". Die Caption-Regel
    („die Caption gewinnt") hätte hier den Satz zerstört: „Zellen namens Parasiten, die die Gefäße fest und tight
    halten" ist keine Aussage, die eine Ad über ihr eigenes Produkt macht. Perizyten sind die realen Zellen, die
    Kapillaren ummanteln — Scribes Fassung ist die einzige, die den Satz trägt.
    **Der Test, der es entscheidet, ist nicht „ist die Caption lesbar", sondern „ergibt die Caption im Satz einen Sinn".**
    Ist sie lesbar UND sinnlos, greift die Auto-Caption-Stufe des Augen-Check-Skills, und die Tonspur gewinnt.
    Diese Quell-Familie ist nachweislich maschinell untertitelt — VIS 001 EL fand unabhängig „POURING REFUELLING"
    statt gesprochenem „Taurine refueling" (dort entschied das Supplement-Facts-Panel im Bild). Zwei Belege aus zwei
    verschiedenen Ads derselben Marke am selben Abend: bei Visiovance-Quellen ist die Caption ein Indiz, kein Urteil.
    Reihenfolge, die trägt: (1) Packshot/Prop im Bild — stärkster Beleg, (2) Caption, wenn sie im Satz Sinn ergibt,
    (3) Scribe. Fachbegriffe sind der Ort, an dem Auto-Captions am häufigsten kippen.

19. **Vmakes Schutzlisten-Schwelle 1,0 liegt UNTER dem Re-Encode-Rauschen — erst eichen, dann urteilen.**
    Vmake gibt das ganze Video neu encodiert zurück, also unterscheidet sich JEDER Pixel ein wenig.
    Gemessen an VIS 002 EL (18.09.2026, 704×1280): in Bildstreifen, die Vmake unmöglich angefasst
    haben kann (oberste 200 px, unterste 130 px), liegt die mittlere Graustufen-Differenz alt↔neu
    bei **0,85–0,97**, im Bildschnitt bei 1,75. Die Schwelle „unter 1,0 = unberührt" aus
    `vmake-caption-entfernen` Schritt 4c meldet damit fast jede Schutzbox als „ansehen" —
    zwölf Boxen, zehn Fehlalarme. Zum Vergleich das Caption-Band, wo Vmake wirklich gearbeitet
    hat: **10–44**. Der Abstand ist also riesig, die absolute Schwelle nur falsch gesetzt.
    **How to apply:** Je Frame zuerst zwei Referenz-Streifen weit weg vom Caption-Band messen,
    dann die Schutzbox gegen DIESEN Wert halten (Faustregel: Box ≤ 2× Referenz = unberührt),
    nicht gegen 1,0. Siehe auch „Prüfer erst an bekannt gutem Material eichen".

20. **Vmake kann einzelne Frames am Karten-Anfang stehen lassen — Reste in Frames zählen, nicht in Sekunden.**
    VIS 002 EL: von 430 Caption-Treffern im Original blieben nach dem Lauf **2** übrig; einer davon
    (181,25 s) war ein Fehlalarm (violette 3D-Figur ohne schwarze Kontur im Farbfilter), der andere
    ein echter Rest — die Karte „15" bei **147,27 / 147,30 / 147,37 s**, also 3 Frames von 5594,
    Box y 968–1015, x 323–380. Die Fenster-Messung aus Schritt 4b findet so etwas NICHT: sie meldete
    20 „unberührte Fenster", davon 19 schlicht caption-freie Pausen. **How to apply:** Nach dem Lauf
    denselben Farb+Kontur-Detektor auf ORIGINAL und BEREINIGT laufen lassen und die Trefferzahlen
    vergleichen (430 → 2 ist der Beleg); jeden Resttreffer mit fps=30 nachmessen und mit Augen gegen
    das Original halten, bevor er als Rest gilt. Ein 3-Frame-Rest rechtfertigt keinen zweiten
    Vmake-Lauf (Punkt 14: deterministisch, bitgleich) — er wird mit den übrigen Pixel-Arbeiten
    gesammelt und in EINEM Encode gepatcht.

## Vmake auf Packshot-Ads: die Caption liegt AUF dem Etikett (VIS 003 EL, 18.09.2026)
**Befund.** Bei Produkt-Ads, deren Untertitel-Karte im Packshot-Fenster ueber dem
Etikett liegt, nimmt `videoscreenclear` die Karte weg und verschmiert den Etikett-Text
darunter zu weissen Streifen. Messbar: Caption-Oberkante in Szenen-Frames y 858, in
Packshot-Frames y 856 — der Etikett-Text liegt wirklich UNTER der Karte, nicht daneben.
**Darum ist es NICHT durch Rueckkopieren aus dem Original heilbar** (das braechte die
englische Caption mit). Wer das nicht misst, probiert Rueckkopieren und wundert sich.

**Was trotzdem gemacht wird (und viel bringt):** Nicht Vmakes Video als Basis nehmen,
sondern das ORIGINAL — Vmakes Ergebnis nur in das gemessene Caption-Band einsetzen.
Dann ist ausserhalb des Bands garantiert kein Vmake-Pixel im Bild (bei VIS 003 EL hatte
Vmake in 3 Frames ausserhalb gemalt), und die Re-Encode-Verluste sind dort ebenfalls weg.

**fps-Falle, die erst am Frame-Beweis auffaellt:** Vmake gibt eine krumme Bildrate zurueck
(gemessen 53700000/1790839 = 29,9858 statt 30/1). Mit Vmake als Overlay-Basis dupliziert
ffmpeg Frames — 4298 statt 4296. Fix: `setpts=N/(30*TB)` auf BEIDE Spuren, Original als
Basis, `-r 30 -vsync cfr`. Die Ziel-fps je Quelle messen, nie 30 annehmen.

**Uebergabe statt Reparatur:** Der beschaedigte Etikett-Bereich wird in der
Gestaltungs-Text-/Frame-Edit-Strecke als EINE gemessene Flaeche deutsch neu gesetzt,
nie zeilenweise — sonst blitzt der verschmierte Untergrund zwischen den Zeilen durch.
Zeilen oberhalb des Bands bleiben heil und werden nur uebersetzt.

## Vmake: wanderndes Caption-Band und der gefressene Frame 0 (VIS 004 EL, 18.09.2026)

**Befund 1 — das Caption-Band ist nicht immer ortsfest.** In der Real-Footage-Quelle
894d25e2 sitzt die Caption normal auf y 935–1059 von 1280 (73–83 %), springt aber bei
8,7–10,8 s auf y 561–624 (44–49 %) und trägt dort zusätzlich ein zweites Wort auf ~88 %
(y 1069–1224). Wer die Band-Box einmal misst und dann glaubt, bekommt zwei Folgefehler:
Schritt 4b meldet „unberührte Fenster" (= angeblich stehengebliebenes Englisch), die in
Wahrheit hochstehende Captions sind; und beim Zurückkopieren holt man die englische
Caption wieder ins Bild. **Die Caption-Lage über die VOLLE Höhe und die VOLLE Länge
messen, nicht in einem angenommenen Korridor.** Messsignatur, die zuverlässig trennt:
Pixel > 235 mit einem Pixel < 60 in 6 px Abstand darüber ODER darunter (weisse Versalie
mit schwarzer Kontur); Zeilen mit > 8 solchen Pixeln sind Schriftzeilen.

**Befund 2 — Vmake frisst den ersten Frame.** Gemessen an den ersten acht Frames:
Original 0,0 · 8,0 · 58,1 · 60,1 …, nach Vmake 66,8 · 8,0 · 58,1 · 60,0 …
Die schwarze Anfangsblende (Frame 0) wird durch ein helles Bild ersetzt, alle übrigen
Frames bleiben an ihrem Platz — es ist also KEIN globaler Versatz, sondern genau ein
zerstörter Frame. Effekt in der fertigen Ad: ein Aufblitzer in Bild 1. Fällt in keiner
Stichprobe auf, weil Stichproben bei Frame 30 anfangen. **Prüfung: mittlere Helligkeit
der ersten 6 Frames vorher/nachher vergleichen.** Fix: Frame 0 als eigenes Overlay-Fenster
(`enable='lt(t,0.02)'`, voller Frame) aus dem Original zurückholen.

**Befund 3 — die 4c-Schwelle 1,0 schlägt nach einem Re-Encode falsch an.** Nach der
Reparatur liegt der Rauschgrund bei ~1,2 statt bei 0. Alle neun Schutzeinträge lagen
zwischen 0,5 und 1,4 und wären mit der Skill-Schwelle 1,0 als „angetastet" gemeldet worden,
obwohl sie heil sind. **Den Rauschgrund je Lauf messen und die Schwelle darüber legen**
(hier 1,6), statt die feste 1,0 zu nehmen.

**Methoden-Ergänzung zur Lehre von VIS 003 EL.** Dort gilt: Original als Basis nehmen und
Vmakes Ergebnis nur ins Caption-Band einsetzen. Das ist der bessere Weg — setzt aber ein
ORTSFESTES Band voraus. Bei wanderndem Band (Befund 1) trägt er nicht, weil die Vereinigung
aller Caption-Lagen (y 561–1224) den Gestaltungs-Text mit einschliesst. Dann gilt der
umgekehrte Weg: Vmake als Basis, und per Vollängen-Scan ALLES ausserhalb des Bandes
zurückholen. Scan: beide Videos auf 240x426 gray dekodieren, je Frame die mittlere Differenz
oberhalb und unterhalb des Bandes rechnen, Rauschgrund bestimmen (hier 0,60), alles über
5× Rauschgrund ist ein Fenster zum Ansehen. Fand bei VIS 004 EL drei Schäden, von denen
zwei (ASTAXANTHIN, BILBERRY/GINKGO) auf keiner vorher erstellten Schutzliste standen.
Alle Fenster in EINER ffmpeg-Runde reparieren, sonst stapeln sich h264-Generationen.

## Vmake-Reparatur: Per-Pixel-Glyphenmaske schlaegt Band-Overlay (VIS 003/005 EL, 18.09.2026)
Beide Wege nehmen das Original als Bildbasis und Vmake nur punktuell — aber das BAND-Overlay
opfert jeden Gestaltungs-Text, der im Band liegt (Etikett-Zeilen, Siegel-Kacheln, 3D-Titel).
Die **Glyphen-Maske** nimmt Vmake nur dort, wo wirklich ein Caption-Buchstabe stand:
  text = reinweiss(>244) ODER Highlight-Farbe · kontur = reinschwarz(<45)
  kern = (text & dilate(kontur)) | (kontur & dilate(text)) · maske = dilate(kern,15)
  nur innerhalb des gemessenen Bands anwenden, sonst frisst sie schwarze Strichzeichnung.
Die Highlight-Farbe je Quelle MESSEN (VIS 003: gelb 241/168/46; VIS 005: gruen). Ersetzte
Flaeche bei VIS 003: 3,5 % des Bildes statt 12 % beim Band-Overlay.

**Und der Pruefer dazu, der leicht falsch gewaehlt wird:** Die mittlere Pixeldifferenz gegen
das Original taugt NICHT — Caption-Entfernung ist selbst Abweichung, der Wert steigt also bei
guter Arbeit. Bei VIS 003 zeigte er die schlechtere Fassung teils als besser. Was entscheidet:
Apple-Vision-OCR zweimal zaehlen — (a) Caption-Woerter im Band (muss 0 sein, gegen das
Original geeicht: dort 712) und (b) die bekannten Etikett-Woerter in der Etikett-Box (Band-
Overlay 38 % des Originals, Glyphen-Maske 70 %). Immer ein Mass nehmen, das die GEWUENSCHTE
Eigenschaft direkt zaehlt, nie den Abstand zu einem Zustand, den man gerade veraendern will.

21. **Weich blendende Ads sind für `scene>0,30` unsichtbar — zweiter Erkenner über 15 Frames.**
    VIS 002 EL (3D-Animation, durchgehend rot): Szenenfilter fand 19 Clips à Ø 9,8 s, einer
    50 s lang. Grund: die Ad blendet weich. An den verschluckten Kanten liegt die
    **Nachbar-Frame-Differenz bei nur 5–8 Punkten** (unter jeder Sprung-Schwelle), über
    **15 Frames (0,5 s) aber bei 20–60**. Eine Blende verteilt die Änderung auf 10–20 Frames.
    `tools/sp/clip_karte.py` fährt seit 18.09.2026 drei Erkenner: scene>0,30 · Nachbar-Diff>18
    (harte Schnitte, sp-learnings 9) · **15-Frame-Diff>18 (weiche Blenden)**, Klebe-Schwelle
    0,5→0,8 s. Ergebnis 52 Clips à Ø 3,6 s. **How to apply:** Ist Ø-Clipdauer > 6 s oder trägt
    ein Clip mehr als zwei Sätze, ist der Erkenner blind — nicht die Ad langsam.

22. **Hat die Quelle zwei Sprecher, bekommt sie zwei Stimmen — und das misst man in zwei Minuten.**
    VIS 002 EL wechselt bei 85 s von **110 Hz** (Antagonist, „I'm the oxidative damage") auf
    **189 Hz** (Produkt, „I'm Visiovance"): zwei über je eine Minute stabile Blöcke, 79 Hz
    Abstand. Messweg: `librosa.pyin(fmin=60,fmax=400)` über 8-s-Fenster der ganzen Ad auf dem
    Demucs-Vocal-Stem, Median je Fenster. Präzedenz RAN 001 EL („drei Stimmen wie im Original").
    **Das Ein-Take-Gesetz gilt dann JE ROLLE** — ein durchgehender Take pro Stimme; sein Grund
    (Prosodie über Satzgrenzen) bleibt damit intakt. Formanten taugen für die Gegenprobe NICHT,
    wenn das Original Musik unter der Stimme hat und die Kandidaten trocken sind — die Tonhöhe
    ist der robuste Wert. **Wer den Wechsel übersieht, lässt Bösewicht und Produkt gleich
    klingen und der Hook läuft ins Leere.**

23. **„Tote Luft" des Prüfers immer gegen die Pausen des ORIGINALS und den Bett-Pegel halten.**
    VIS 002 EL: 13 gemeldete Stille-Fenster ≥ 0,8 s. Gegengehalten gegen (a) die **9 eigenen
    Pausen des Originals** ≥ 0,8 s (aus `source_words.json`) und (b) den Bett-Pegel in genau
    diesen Fenstern, blieb **ein einziges** übrig. 6 lagen dort, wo das Original auch pausiert,
    6 trägt das Musikbett (−18,7 bis −34,2 dB gegen −34,1 dB Mittel). Ohne die Eichung hätte
    man zwölf Löcher gestopft, die keine sind — und dafür Copy erfunden.

24. **v3 liest „15-in-1" als Ordnungszahl — Zahlen im Take-Text ausschreiben.**
    VIS 002 EL: aus „die 15-in-1 Augen-Pflege-Formel" wurde hörbar „die fünfte"; Scribe UND
    lokaler Whisper hörten unabhängig Unsinn. „fünfzehn-in-eins" ausgeschrieben löst es.
    **Zugleich die Falle des Prüfers:** derselbe Lauf meldete 7 rote Blöcke, davon **5 falsch** —
    leerer Scribe-String (match 0.0 bei einwandfreiem Audio), Scribe blutet das erste Wort des
    Folgeblocks ein („…Entzündung und"), Engine-Schreibweisen („Gingko", „PresaVision"), und
    veralteter Marken-Text nach einem Copy-Fix. **How to apply:** Jede rote Zeile mit einer
    ZWEITEN Transkription gegenhören (lokaler Whisper reicht), bevor ein Block neu gewürfelt
    wird — sonst würfelt man gute Blöcke neu und lässt den echten Fehler stehen.

## Per-Pixel-Caption-Maske: die feste Untergrenze ist das Loch (VIS 004 EL, 18.09.2026)

**Die Methode** (aus VIS 005 EL): Nicht Vmakes Video als Basis nehmen, sondern das Original,
und Vmake NUR dort einsetzen, wo die Caption-Glyphen stehen — Maske aus „sehr hell (>244)
neben sehr dunkel (<45), dilatiert". Das räumt Vmakes Helligkeitshebung und seine
Re-Encode-Verluste aus dem ganzen übrigen Bild. **Messbar besser:** bei VIS 004 EL
Helligkeit −0,30 gegenüber dem Original statt +1,19, Abweichung ausserhalb des Bands
max 7,6 statt 103,4.

**Das Loch:** Die Maske fängt auch dunkle Schrift auf hellem Grund — jedes Etikett, jedes
Preisschild. Darum braucht sie eine räumliche Begrenzung, und VIS 005 EL hat dafür eine
FESTE Untergrenze gesetzt (y 960). Genau da bricht sie: **Die Caption sitzt nicht immer im
selben Korridor.** Bei VIS 004 EL steht sie normal auf y 935–1059, bei 3,0 s aber reicht sie
bis **y 768** hinauf und bei 8,7–10,8 s auf y 561–624. Unter der festen Grenze sieht die Maske
sie nicht, das Original-Pixel bleibt stehen — und damit die englische Caption.

**Gemessen, nicht vermutet:** Apple-Vision-OCR (fps=4, ganze Fläche) über die so gebaute
Fassung fand englische Caption-Wörter bei 0,50–6,00 s (NOTICING · RANDOM · SPECIFIC · LAYER ·
RUNNING · NEEDS), 10,00–10,50 s (A SIGN) und 27,50 s. Über die Vmake-Reparatur derselben
Quelle fand dasselbe OCR **keinen** Rest.

**Regel:** Die Per-Pixel-Maske ist der bessere Weg, aber ihre Zone muss **je Frame aus dem
Original abgeleitet** werden (Glyph-Signatur über die VOLLE Höhe, dann die zusammenhängende
Zeilengruppe als Zone), nie als feste Box. Wer die feste Box nimmt, muss danach zwingend
den OCR-Beweis fahren — das Auge findet einen Caption-Rest in Sekunde 3 nicht, weil es
dort das Bild ansieht und nicht die Schrift sucht.

**Und die Gegenprobe gehört dazu:** Caption-Freiheit schlägt Bildqualität. Ein englischer
Caption-Rest ist ein harter Mangel, 0,5 % Helligkeit sind unsichtbar. Wer zwischen zwei
Fassungen wählt, entscheidet am OCR, nicht am Helligkeits-Mittelwert.

25. **Die Stimmen-Bibliothek hat 14 Seiten — ein Casting ohne Paginierung sieht 7 % davon.**
    Der Aufruf aus `speaking-vsl-stimm-casting`
    (`GET /v1/shared-voices?page_size=100&language=de&gender=male`) liefert **100** Stimmen und
    das Feld `has_more: true`. Wer `page=` nicht mitzählt, castet aus 100 statt aus **1400**.
    Gemessen am 19.09.2026 für VIS 002 EL: Seite 1 enthielt nur **8** Männerstimmen mit
    `use_case ∈ {advertisement, social_media}`; über alle 14 Seiten sind es 163, dazu
    **103 mit `characters_animation`**, die auf Seite 1 praktisch nicht vorkamen.
    **How to apply:** Immer alle Seiten ziehen (`while d["has_more"]: page += 1`), Trichter erst
    danach anlegen und die Zahl im Casting-Eintrag ausweisen.

26. **Für eine FIGUR ist `advertisement`/`social_media` der falsche Filter — Charaktere liegen
    unter `characters_animation`.** Die Regel des Casting-Skills („advertisement und social_media
    schlagen narrative_story") gilt für die Erzählstimme einer Ad. Spricht die Ad aber eine
    Rolle — ein Monster in der Ich-Form, ein sprechendes Produkt —, filtert dieselbe Regel genau
    die Stimmen weg, die dafür gebaut sind. Bei VIS 002 EL lieferte der Rollen-Trichter
    (Alter + `use_case ∈ {characters_animation, entertainment_tv, narrative_story, advertisement,
    social_media}` + `descriptive ∈ {deep, intense, serious, modulated, …}` + Namens-/
    Beschreibungs-Stichworte wie „villain", „evil", „dark", „monster") **245 Kandidaten** statt 8 —
    darunter „Mordred – Evil Villain", „Bartholomeus – Maximum Evil", „Smoky Sam – Cold-hearted
    Villain". **How to apply:** Erst fragen, WER spricht (Erzähler oder Figur), dann den Trichter
    wählen. Die Tonhöhe der Original-Rolle bleibt in beiden Fällen das Ziel-Maß.

27. **Ein Take-Neuwurf löscht stillschweigend jeden Fix, der nur im Ersatz-Block lebte.**
    VIS 002 EL: Block 12 („PreserVision") war per Mini-Take und `--ersatz` repariert. Danach
    wurde Take A als GANZES neu gewürfelt (um ein Stille-Loch in Block 8 zu füllen) — dabei
    entstand `take_a.txt` neu aus der Copy, `ersatz_a.json` wurde gelöscht, und der Block kam
    wieder aus dem Haupt-Take. Der Fehler war zurück, ohne dass irgendein Prüfer anschlug:
    Scribe schrieb weiterhin brav „Preservision", erst die ZWEITE Transkription (Whisper
    large-v3) hörte „Presavision". **How to apply:** Phonetische Schreibungen gehören in die
    Copy-/Take-Quelle (und ins Marken-Lexikon), nie nur in eine Ersatz-Datei. Nach jedem
    Take-Neuwurf die Lexikon-Wörter erneut gegenhören — mit zwei Engines.

28. **Eine phonetische Umschreibung ist eine Hypothese, kein Fix — erst messen, dann eintragen.**
    Gleicher Lauf: „Preser Vision" (getrennt geschrieben, um die verschluckte Silbe zu retten)
    machte aus „Presa-Vision" ein **„Prisa-Vision"** — beide Engines einig, also schlechter als
    vorher. Sechs Schreibungen gegeneinander getestet ergaben: die ursprüngliche Ein-Wort-Form
    war die beste; „Presähr Vision" klang zwar richtig, ließ Whisper small aber „Präservision"
    schreiben. **How to apply:** Varianten im Block erzeugen (kostet je ~80 Zeichen), beide
    Transkriptionen gegenhalten, Gewinner ins `<KÜRZEL>-lexikon.md` mit der Tabelle. Nie eine
    Umschreibung „weil sie logisch aussieht" in einen Take schreiben.

---

## Aus VIS 001 EL (Visiovance, 19.09.2026)

21. **Die Sprech-Rate der Casting-Testzeile taugt nicht als Budget-Grundlage.** Dieselbe Stimme
    („Christian – Professional and Confident") trug in der 5-Sekunden-Testzeile **2,06 W/s**, im
    236-Sekunden-Take aber nur **1,84 W/s** — 11 % weniger. Wer mit dem Testzeilen-Wert plant,
    baut eine Copy, die 25 s zu lang ist. **How to apply:** Budget mit der Testzeile grob rechnen,
    nach dem ERSTEN vollen Take die Rate neu bestimmen (Woerter ÷ Take-Dauer) und die Budgets
    nachziehen, BEVOR gekuerzt wird.

22. **Bei einem langsamen Take neu wuerfeln, nicht Copy streichen.** Fuenf Takes derselben Copy:
    237,0 · 253,6 · 258,0 · 276,4 · 278,1 s — Streuung **17 %**, nicht die im Skill genannten ±10 %.
    Nach dem langsamsten Take habe ich 90 Woerter gestrichen; die Spur bekam dadurch **23,5 s tote
    Luft in 17 Loechern**, obwohl die Quelle durchgehend spricht. 30 Woerter mussten zurueck.
    **How to apply:** Erst 2–3 Takes erzeugen und den schnellsten nehmen; Copy kuerzen erst, wenn
    auch der schnellste nicht passt.

23. **Den Atem je Quelle messen — 0,45 s ist oft doppelt so viel wie noetig.** Die Wortluecken an
    den Satzgrenzen der Quelle: Median **0,22 s**, Maximum 0,36 s. Mit dem Referenzwert 0,45 s
    entstehen 38 × 0,23 s = **8,7 s** kuenstliche Stille, die das Original nicht hat.
    **How to apply:** Vor der Montage die Satzgrenzen-Luecken aus dem Scribe-Roh-JSON messen und
    den Median nehmen; nicht unter die Pruefer-Schwelle 0,25 s gehen (dann meldet er „Bloecke
    kleben") — bei einem Median von 0,22 also den P75 fahren.

24. **v3 macht aus einem Gedankenstrich eine Pause.** „… ins Auge kommt — und die Sehkraft weiter
    nachlaesst." ergab **1,96 s** Stille mitten im Satz. Mit Komma statt Gedankenstrich: keine Pause.
    **How to apply:** Im Take-Text Gedankenstriche durch Kommas ersetzen, wo der Satz fliessen soll.
    Der Gedankenstrich bleibt in der Copy-Datei und in den Captions.

25. **v3 kann einen Markennamen mitten in der Spur neu erfinden.** In Block 33 sprach dieselbe
    Stimme „**Leo Vance**" statt „Visiovance" — in Block 18 desselben Takes war der Name korrekt.
    Das Ohr haette es gemeldet, die Zeile klang fluessig; gefunden hat es die Rueck-Transkription.
    **How to apply:** Den Markennamen je Nennung einzeln gegen die Rueck-Transkription halten,
    nicht nur den Gesamt-Match. Reparatur: Block einzeln neu erzeugen, Schreibweise variieren
    („Visio-Vance" ergab wieder „Visio Vans"), per `montage --ersatz` einsetzen — Ersatz-Dateien
    vorher auf Take-Tempo bringen und eng trimmen, sonst passen sie nicht ins Fenster.

26. **Eine Blockgrenze kann mitten in einem Wort liegen — dann wird es doppelt gesprochen.**
    Nach dem Ersatz von Block 33 sagte die fertige Ad „VisioVance, VisioVance ist fast
    ausverkauft": Block 32 endete laut Alignment erst bei 205,08 s, das Satzende lag aber bei
    203,54 s — die 1,5 s dazwischen trugen das erste Wort des Folgeblocks aus dem Take.
    **How to apply:** Nach jedem Ersatz-Einsatz den FINALEN Ton zurueck-transkribieren und auf
    Einfuegungen pruefen (difflib-Opcodes „insert"), nicht nur auf den Match-Wert. Reparatur:
    den Vorgaengerblock ebenfalls als Ersatz sauber am Satzende schneiden.

27. **Vmake malt ins ganze Bild — der Schaden ist gross und der Schlieren-Scan blind dafuer.**
    51 Fenster ausserhalb des Untertitel-Bands, bis 691.573 Pixel je Frame; das komplette Offer
    („LOW STOCK!", „50% DISCOUNT") war weg, ein ganzer Frame an einer Schnittkante ueberschrieben.
    Der mitgelieferte Schlieren-Scan meldete „Band ruhig".
    **How to apply:** Nach jedem Vmake-Lauf einen INDEX-basierten Schadens-Scan gegen das Original
    fahren (`select='not(mod(n,2))'`, NICHT `fps=N` — zeitbasiert misst man den Re-Encode-Versatz
    als Schaden, Gegenprobe: Versatz-Test, Minimum muss scharf bei 0 liegen). Bildbasis dann als
    **Per-Pixel-Komposit in YUV420p**: Original ueberall, Vmake nur auf den dilatierten
    Caption-Glyphen. Das Band-Komposit (ganze Zeilen aus Vmake) erzeugte an 11 Frames sichtbare
    **Nahtspruenge bis 76 Helligkeitsstufen**.

28. **Ein weisser Stoerer im Caption-Band braucht zusaetzlich ein Zeitfenster.** Die Glyphen-Maske
    trennt Caption von Gestaltungs-Text nur, wenn der Gestaltungs-Text farbig oder dunkel ist.
    „LOW STOCK! / GET YOURS BEFORE IT'S GONE" ist selbst weisse Schrift im Band — Maske UND Fenster.
    Das Fenster muss auf die Frames zugeschnitten sein, in denen der Stoerer wirklich steht:
    ein zu grosses Fenster liess zwei ENGLISCHE Captions stehen, gefunden nur per OCR.

29. **Die OCR-Gegenprobe braucht eine Eichung am Original.** „0 Caption-Reste" heisst nur etwas,
    wenn derselbe Detektor am Original etwas findet. Gemessen: Original **775** Caption-Zeilen,
    reparierte Bildbasis **24** — und diese 24 waren Gestaltungs-Text, der bleiben soll.
    Werkzeug: `ocr_vision.swift` (Apple Vision) aus `brands/DOG - Dogbiotics/004 EL/_pipeline`,
    mit `swiftc` uebersetzen, fps=4 ueber das gecroppte Band.

30. **Wo die Caption auf Etikett-Text lag, ist der Text nach der Tilgung weg — und nicht
    rueckholbar.** Im Supplement-Facts-Panel (1,8 s) hat Vmake die Zeile „Bilberry Extract 50mg"
    mitgenommen. Kein Frame des Clips ist caption-frei, das Panel ist gewoelbt und bewegt sich.
    **How to apply:** Solche Stellen vor dem Rip finden (Band-Helligkeit je Sekunde: wo das Band
    ueber 20 % hell ist, liegt Etikett/Panel darunter — sonst 4–7 %) und Viktor die Wahl vorlegen:
    englische Caption stehen lassen ODER Etikett-Zeile verlieren. Nicht still entscheiden.

31. **Die Schnittkanten-Anker begrenzen, wie weit die deutsche Spur fliessen darf.** Drei Wege
    gemessen: proportional innerhalb der Anker (Versatz gegen die Quelle max **1,20 s**, gewaehlt),
    gleiche Luft je Block (mehr Kanten ueber 0,8 s), freier Fluss ohne Anker (**−6,91 s** Versatz —
    die Zeile laeuft 7 s vor ihrem Bild). **How to apply:** Den Versatz immer mitmessen, nicht nur
    die Luecken; ohne Anker sieht die Verteilung gut aus und die Ad ist trotzdem kaputt.

32. **Ein Einwort-Block mit ungewoehnlichem Kompositum sprengt die Montage.** „Blutzuckerneutral."
    hoert Scribe getrennt, difflib findet die Woerter nicht, die Blockgrenze faellt auf Laenge 0 und
    ffmpeg stirbt mit „-to value smaller than -ss" — ohne Block und ohne Text in der Meldung.
    `tools/sp/sprechspur.py` faengt das jetzt ab (Warnung mit Blocknummer, Grenze aus den Nachbarn
    interpoliert). **How to apply:** Einwort-Bloecke vermeiden; mindestens zwei gelaeufige Woerter.

50. **Die deutsche Copy muss gegen die gemessene Rate DER GEWÄHLTEN STIMME gebaut werden, nicht gegen die des Originals.**
    Lauf VIS 005 EL (18./19.09.2026): Die Übersetzung wurde auf das Silben-Budget des Originals gebaut — 901 deutsche
    Silben gegen 912 englische, also gleiche Sprechlast bei 4,76 gegen 4,81 Silben/s. Auf dem Papier perfekt. Der erste
    Take lief trotzdem **17 % zu lang** (221,9 s Bedarf für 189,5 s Video), weil die deutsche v3-Stimme nur
    **4,35 Silben/s bei Tempo 1,12** trägt, nicht 4,81. Es brauchte drei Verdichtungs-Durchgänge (−13 %) bis es saß.
    **Die Reihenfolge, die das spart:** (1) Stimme casten, (2) EINEN Block mit ihr erzeugen und die echte Silben-Rate
    messen, (3) erst dann die Copy gegen DIESE Rate schreiben. Der Skill nennt den Ein-Block-Test bereits
    („kostet 20 Sekunden und spart einen kompletten Neu-Durchgang") — er gehört VOR die Übersetzung, nicht danach.
    Zweiter Fallstrick derselben Klasse: Nach dem Kürzen entstanden Löcher, weil die Copy nun zu KURZ war. Wer kürzt,
    muss gegen die Blockfenster messen, nicht nur gegen die Gesamtlänge — bei VIS 005 EL mussten in vier Blöcken
    Nebensätze wieder zurück. Und: v3 würfelt die Pace je Take um ±10 % (gemessen 211,3 / 214,4 / 226,8 s für dieselbe
    Copy) — drei Würfe erzeugen und den kürzesten nehmen ist billiger als ein Kürzungs-Durchgang.

51. **Der Prüfer misst die Kanten-Stille an der geplanten Marke — die Montage legt die Sprache aber erst nach dem Vorlauf dorthin.**
    Lauf VIS 005 EL: `tools/sp/pruefer.py` meldete 9× „Blöcke kleben an Marke X". Nachgemessen hatten alle neun Kanten
    **0,20–0,32 s** Pause — auf oder über dem Median der Quelle (0,20 s). Ursache: Der Prüfer suchte die Stille im festen
    Fenster [t−0,45 ; t+0,05] um die Marke, die Montage legt den Block aber MIT seinem `--vorlauf` dorthin, die Sprache
    setzt also erst bei t+vorlauf ein. **Werkzeug korrigiert** (Sicherung `tools/sp/pruefer.py.vor-VIS005`): erst den
    echten Sprech-Einsatz ab der Marke suchen, dann die Stille davor prüfen.
    **Der zweite Teil bleibt offen und gehört zu „Prüfer erst an bekannt gutem Material eichen":** Die absolute Schwelle
    0,25 s passt nicht zu jeder Quelle. Diese hier hat 178 Wort-Lücken mit Median **0,16 s** und Minimum 0,14 s — eine
    Spur, die 0,22 s Pause macht, ist dieser Quelle gegenüber großzügig und trotzdem „rot". Wer die Schwelle setzt,
    sollte sie aus dem Wort-Cache der QUELLE ableiten, nicht fest verdrahten.

52. **Eine Caption, die auf einem Gestaltungs-Text liegt, macht ihn unrettbar — aber erst prüfen, ob er im Original überhaupt sichtbar war.**
    Lauf VIS 005 EL: Nach dem Vmake-Lauf fehlte im Gold-Siegel die mittlere Zeile „MONEYBACK", an ihrer Stelle ein
    Schmierer — das Siegel las „90 DAY … GUARANTEE". Reflex wäre: Original-Pixel zurückholen oder die Zeile neu setzen.
    **Beides falsch.** Die Messung über die ganze Siegel-Lebensdauer (184,0–186,0 s, 10 fps) zeigte: Die englische
    Caption verdeckt diese Zeile in JEDEM Frame — im Original war sie nie zu sehen, und es gibt keinen sauberen Frame
    zum Zurückholen. Die deutsche Caption deckt dieselbe Stelle wieder ab.
    **Regel:** Bei fehlendem Gestaltungs-Text erst am ORIGINAL messen, ob und wann er sichtbar war. Fehlt er auch dort
    hinter der Caption, ist nichts zu reparieren — dann gehört in die CapCut-Übergabe der Hinweis, dass die Caption an
    dieser Stelle nicht verschoben werden darf. (Gegenstück zum Befund von VIS 003 EL, wo das Dosen-Etikett unter der
    Karte lag und dort dasselbe Muster auftrat.)

## 1:1-Rip heisst: Bildtext bleibt ORIGINAL (VIS 003 EL, Viktors Entscheid 19.09.2026)
Im Lauf VIS 003 EL wurde das Symptom-Schild der Quelle deterministisch deutsch nachgebaut
(gemessenes Zeilenraster, lokaler Hintergrund je Bildzeile, Template-Nachfuehrung; OCR-Beleg
0 englische / 550 deutsche Schild-Woerter). Viktor hat es am fertigen Video gesehen und
zurueckgenommen: **„lass bitte das original … da hast du versucht es neu zu machen, aber
lass es das original."**

**Regel:** Bei einer 1:1-Rip-Linie (Ziel-Produkt = Quell-Produkt, Original-Clips, keine
Custom Clips) bleibt ALLER Bildtext im Original — Schilder, Etiketten, Siegel, Endcard.
Getilgt werden NUR die eingebrannten Sprech-Untertitel, weil an ihre Stelle die deutschen
CapCut-Untertitel treten. Das Gestaltungs-Text-Gesetz („Szenen-Text wird deutsch nachgebaut,
nie CapCut-Caption") gilt fuer Linien mit Produkttausch — nicht fuer den 1:1-Rip.

**Praktische Folge, die Zeit spart:** Vor jedem Gestaltungs-Text-Nachbau erst die Linien-Art
pruefen (sp-brands `custom_clips`). Steht dort `false` UND ist Ziel-Produkt = Quell-Produkt,
ist der Nachbau gar nicht gefragt. Bei VIS 003 EL waren das mehrere Stunden Arbeit fuer ein
Ergebnis, das der Mensch nicht wollte — und der Nachbau schleppte dabei eigene Probleme ein
(falsche Szenenfenster, Fehl-Nachfuehrung in einer Zoom-Blende), die ohne ihn nie entstanden
waeren.

**Nicht weggeworfen:** Das Verfahren selbst ist in Ordnung und liegt bereit
(`_pipeline/schild_de.py`, `_pipeline/schild_video.py` in VIS 003 EL) — fuer den Tag, an dem
eine Produkttausch-Linie es braucht. Die verworfene Bildfassung bleibt als
`_work/bildbasis_de_verworfen.mp4` liegen, ein Render-Aufruf holt sie zurueck.

## „Tote Luft" des Prüfers im MIX messen, nicht in der Sprechspur (VIS 003 + 006 EL, 19.09.2026)
`tools/sp/pruefer.py` meldet Lücken auf der ISOLIERTEN Sprechspur — einer Spur, die nie
allein zu hören ist. Unter ihr liegt das Musikbett. Zwei unabhängige Läufe, gleiches Bild:

| Lauf | gemeldete Spannen | Sprechspur allein | fertiger Mix | Referenz Sprech-Stelle |
|---|---|---|---|---|
| VIS 003 EL | 10 (1,4–3,1 s) | −21 bis −73 dBFS | **−20 bis −35 dBFS** | −20,1 dBFS |
| VIS 006 EL | 12 | −53,8 bis −70,9 | **−35,3 bis −39,8** | −19,4 dBFS |

**Regel:** Bevor jemand wegen einer „tote Luft"-Meldung Copy kürzt, dehnt oder umbaut —
erst den fertigen Mix an derselben Stelle messen. Trägt das Bett dort, ist die Meldung ein
Werkzeug-Artefakt. Beide Läufe hätten sonst Copy-Durchgänge verbrannt (VIS 006 EL war
schon dabei, ein 4,04-s-Loch durch Umschreiben zu schließen).

**Der billigste echte Hebel, wenn wirklich ein Loch bleibt: der Tempo-Lift.**
1,12 ist laut Skill die OBERGRENZE, kein Sollwert. VIS 006 EL senkte 1,12 → 1,09 und brachte
3,46 s Gesamt-Luft auf 1,20 s — ohne ein Wort zu ändern. VIS 003 EL fuhr den Lift je STIMME
(1,12 / 1,05 / 1,00) und brachte damit ein 4,54-s-Loch vor dem CTA auf 1,05 s.

**Und die Grenze des Hebels, gemessen:** Er ist erschöpft, sobald EIN Block der Stimme exakt
auf Budget sitzt. Bei VIS 003 EL sprengte eine weitere Senkung bei vier von fünf Stimmen
genau diese Blöcke (yurklon −0,38 s, juli −0,28 s, elise −0,39 s, lenny +0,10 s Restatem bei
Mindestmaß 0,30 s). Vor dem Senken also je Stimme durchrechnen, nicht global drehen —
sonst tauscht man ein Loch gegen einen klebenden Block.

## Fremde Marke im Bild — die Trennlinie ist nicht „Text ja/nein" (VIS 006 EL, 19.09.2026)

Die Regel „bei einer 1:1-Rip-Linie bleibt ALLER Bildtext im Original" (Viktors Ansage bei
VIS 003 EL) hat eine Voraussetzung, die man leicht überliest: **Ziel-Produkt = Quell-Produkt.**
Bei VIS 006 EL stimmte die Produkt*art* (beide „15-in-1 Advanced Eye Formula", Etiketten sogar
layout-gleich), aber **nicht die Marke**: Die Quelle bewarb **NEUROBELLA**, nicht Visiovance.

**Regel:** Die Trennlinie ist **nicht „Bildtext ja/nein", sondern „fremde Marke ja/nein".**
- Was die **fremde Marke** trägt, wird getauscht — auch in einer 1:1-Rip-Linie. Sonst liefert
  man den Namen eines Wettbewerbers in der eigenen Ad aus, und Bild und Ton widersprechen sich
  (die deutsche Stimme sagt zweimal „Visiovance", das Etikett zeigt „NEUROBELLA").
- **Gewöhnlicher Szenen-Text der Quelle bleibt** — auch wenn er englisch ist. Bei VIS 006 EL
  blieben damit: die Terminkarte am Kühlschrank („Appointment Card / Monday, Thursday /
  7 - 9:30 pm"), „Premium Eye Supplement", die Wirkstoff-Bänder, die Bullet-Zeilen, die Siegel.
  Der deutsche Nachbau der Terminkarte war geplant und vorbereitet — und wurde nach Viktors
  VIS-003-Ansage gestrichen, bevor eine Zeile Code dafür entstand.

**Praktisch:** Vor jedem Bild-Eingriff zwei Fragen in dieser Reihenfolge stellen —
(1) Ist die Linie ein 1:1-Rip? Wenn ja, bleibt Bildtext grundsätzlich stehen.
(2) Trägt die Stelle eine FREMDE Marke? Nur dann wird trotzdem getauscht, und nur diese Stelle.

**Werkzeug:** `tools/sp/etikett_wort.py` tauscht EIN Wort deterministisch im Bild (0 Credits,
kein Kling) — gemessene Versalhöhe, Neigung, Schriftfarbe und Etikett-Untergrund je Frame.
Vier Fallen, alle gemessen:
- **Adaptive Schwelle (Otsu) statt fester.** Bei Bewegungsunschärfe fasst eine feste Schwelle
  nur die Buchstaben-Kerne; der Saum bleibt als Geist hinter dem neuen Wort stehen.
- **ZWEI Masken.** Eine enge (Otsu pur) MISST Geometrie, eine weite (Otsu × 1,35) LÖSCHT den
  Saum. Mit nur einer Maske wird das neue Wort entweder zu groß oder der Geist bleibt.
- **Keine Extrapolation über die OCR-Stützstellen hinaus.** Mit 0,30 s Zugabe geriet die Box in
  Frames, wo das Wort noch nicht da war — Messung entgleiste auf 146 px statt 48.
- **Aussetzer ERBEN, nicht überspringen.** Ein Plausibilitäts-Wächter, der unplausible Frames
  auslässt, zeigt dort die FREMDMARKE. Bei VIS 006 EL waren das vier Lücken von 0,10–0,17 s —
  lang genug zum sichtbaren Aufblitzen. Der Frame erbt Höhe/Breite/Winkel von den Nachbarn,
  die Position kommt weiter aus dem eigenen Frame.
- Der Wächter muss **je Fenster** zurückgesetzt werden und gegen den Median ALLER bisherigen
  Messungen laufen: Packshot-Fenster haben echt verschiedene Schriftgrößen (45 px gegen 24 px),
  und ein einziger kaputter erster Frame vergiftet sonst den ganzen Lauf (1 statt 488 Frames).

## CapCut-Stil bringt eine fremde Schrift mit (VIS 004 EL, 19.09.2026)
`scripts/caption_stil.py` setzt mit dem Stil „逐词高亮-黄" auch dessen Schrift-Referenz, und
die zeigt auf den Cache-Pfad der Maschine, auf der der Stil aufgenommen wurde:
`/Users/<aufnahme-rechner>/.../Cache/effect/160949616/.../ZY Resolve.ttf`. Auf dem Mac, der den
Draft öffnet, existiert dieser Pfad nicht — CapCut wählt dann für ALLE Untertitel
eine Ersatzschrift, ohne zu warnen.
**Erkennen:** je Text die `font.path` aus `materials.texts[].content` lesen und mit
`os.path.exists` prüfen. **Nicht** `grep -c` benutzen — `draft_info.json` steht auf einer
einzigen Zeile, `grep -c` zählt Zeilen und meldet darum immer „1", egal ob ein Text oder
alle betroffen sind. Das sah bei mir zuerst nach einem Einzelfall aus, waren aber 64 von 64.
**Beheben:** `font` in allen Texten auf eine lokal vorhandene Schrift setzen. Referenz, die
nachweislich trägt: `Montserrat-Bold.otf` unter
`~/.../Cache/effect/3912492/91d28cfa5e7db054f4872f1ae2417ac2/`, id
`7148699779147502082` — so machen es RAN 001 EL (222 Texte) und der Spender 0319-spender007.
Füllfarbe und Kontur dabei NICHT anfassen, der Stil soll bleiben.
**Vor dem Melden prüfen:** CapCut beenden, bevor die Draft-JSON angefasst wird — CapCut
überschreibt Drafts beim Beenden.

## Eine Regel ohne Werkzeug wird je Lauf neu vergessen

**Befund VIS 006 EL, 19.09.2026.** `speaking-vsl-captions` schreibt seit dem QUA-001-Lauf
klar: **„je Einblendung 1,5–3 s"**, höchstens zwei Zeilen, höchstens ~34 Zeichen. Der Skill
lieferte aber nur die SKILL.md, **kein Skript**. Ergebnis in diesem Lauf: Zeilen- und
Zeichenregel eingehalten (max 2 Zeilen à 33), **Standzeit gerissen** — 10 von 44
Einblendungen über 3,0 s, die längste 3,98 s.

**Das Muster, nicht der Einzelfall:** Von drei Regeln in einem Satz wurden die zwei
geprüft, die man **beim Hinsehen** bemerkt (eine dritte Zeile und ein Überlauf fallen im
Bild auf), und die eine vergessen, die man **nur durch Messen** bemerkt. Eine Standzeit von
3,98 s sieht in keinem Kontakt-Sheet falsch aus. Niemand hat geschlampt — die Regel hatte
einfach keinen Ort, an dem sie automatisch greift.

**Daraus die Lehre:** Eine Zahl in einer SKILL.md, die kein Skript durchsetzt, ist eine
Absichtserklärung. **Steht in einem Skill eine messbare Schwelle und liegt daneben kein
Prüfer, ist das Fehlen des Prüfers selbst der Befund** — noch bevor irgendetwas schiefgeht.
Gebaut: `tools/sp/untertitel_regel.py` (Exit 1 bei Befund, `-o` schneidet nach).

**Und die zweite Lehre, teurer gelernt:** Der erste Nachschnitt tauschte den Fehler nur aus.
Der Bonus für „Textwechsel am Szenenschnitt" überstimmte die Strafe für zu kurze
Einblendungen und ließ **„Vielleicht" 0,26 s** aufblitzen — 38,5 Zeichen/s statt 3,10 s
Standzeit. Gemessen, nicht gesehen. **Eine Reparatur ist erst fertig, wenn die Gegenrichtung
mitgemessen ist:** Wer eine Obergrenze erzwingt, muss die Untergrenze im selben Durchgang
prüfen, sonst wandert der Fehler nur. Weiche Strafen taugen dafür nicht — was nie passieren
darf, gehört als **Ausschluss** in die Kandidatenwahl, nicht als Punktabzug. Seitdem:
harter Boden 0,80 s, Lesetempo-Deckel, und kein Schnitt darf das Tempo seiner
Ausgangs-Einblendung verschlechtern.

## Untertitel-Höhe: die Quelle entscheidet, nicht die 81 %

`speaking-vsl-captions` nannte als Position nur das untere Fünftel (≈ 81 % Bildhöhe) —
gemessen weichen aber fünf Läufe begründet davon ab: RAN 001 EL, DOG 001/002 EL und
KRA 003/004 EL bauten auf **72 %**, VIS 006 EL auf **74,2 %**. Der Grund ist jedes Mal
derselbe, und er stand bisher nur in einer Projekt-Karte statt im Skill:

**Brennt die Quelle ihre Untertitel auf einen deckenden Balken, bleibt der Balken im Bild.**
Hinter ihm existiert kein Bild — es gibt dort nichts wiederherzustellen, nur zu erfinden.
Die Buchstaben lassen sich übermalen, die Fläche nicht wegnehmen. Setzt man die deutschen
Untertitel dann ins untere Fünftel, stehen **zwei Balken untereinander**; setzt man sie in
die Mitte der Fläche, sieht die Ad aus wie die Quelle, nur deutsch.

**Die Höhe wird gemessen, nicht übernommen.** Sie fällt je Quelle anders aus (72 / 74,2 %),
weil die Fläche anders sitzt: Median der Ober- und Unterkanten der Caption-Boxen aus dem
Vollbild-OCR, Mitte ÷ Bildhöhe. Für VIS 006 EL: 932 und 968 px von 1280 → 950 px → 74,2 %.
Min/Max taugen dafür nicht — im Fenster liegen Ausreißer (880 und 1058 px), die eine
zweizeilige Caption nie füllt.

**Und die eigentliche Lehre:** Die Regel war vier Läufe lang gültig und lebte doch nur als
Klammer-Bemerkung in `VIS 001 EL/karte.md`. Beim fünften Lauf habe ich sie als offene Frage
auf die Parkliste geschrieben, statt sie zu finden. **Eine Begründung, die dreimal in einem
Pusher-Kommentar auftaucht, ist eine Regel — sie gehört in den Skill, sonst wird sie beim
nächsten Mal neu verhandelt.** Suchreflex bei „das steht nirgends": vor der Parkliste die
Pusher und Karten der eigenen Linie nach der Zahl greppen, nicht nur die Skills.

## CapCut: caption_stil.py setzt eine Wort-Highlight-Vorlage — Untertitel nicht auswählbar (VIS 004 EL, 19.09.2026)
**Symptom (Viktors Befund):** Nach dem Push lassen sich die Untertitel in CapCut nicht
auswählen. Der Draft sieht in ALLEN sonst geprüften Punkten korrekt aus — Spuren, Segmente,
Bindung, Medienpfad, Dauer, Meta — und genau das macht die Suche schwer.

**Ursache, im Quervergleich gefunden:** `scripts/caption_stil.py` hat bei diesem Lauf die
Vorlage **`逐词高亮-黄`** (Wort-für-Wort-Highlight gelb, resource_id 7331663243842227461)
gesetzt. Alle anderen Drafts auf dieser Maschine — VIS 001/002/003/005/006 EL und
RAN 001 EL — nutzen **`排列-白`** (resource_id 7331663590962777349). Meiner war der einzige
Ausreisser. Eine Wort-Highlight-Vorlage erwartet Wortzeiten in `current_word_info`; die ist
beim maschinellen Bau leer, und CapCut behandelt das Element dann nicht wie einen normalen
Untertitel.

**So findet man es:** NICHT einzeln prüfen, sondern quer über die Drafts vergleichen —
je Draft `materials.text_templates[*].name` und `.resource_id` auflisten. Der Ausreisser
fällt sofort auf. Einzeln betrachtet wirkt jeder Draft korrekt.

**Beheben (0 Credits, Texte bleiben):** Aus einem funktionierenden Draft die Felder
`effect_id · name · path · preview_time · resource_id · resources · third_resource_id`
auf ALLE eigenen `text_templates` kopieren, und aus dessen erstem Text-Material die
Stilfelder `fill · size · strokes · useLetterColor · font` auf alle eigenen Text-Stile.
**`range` je Text behalten** (das ist [0, Textlänge] und gehört zum eigenen Wortlaut),
`text_info_resources` und `id` nicht anfassen. Danach CapCut NEU STARTEN.

**Zwei Fallen dabei:**
1. `draft_info.json` steht auf EINER Zeile — `grep -c` zählt Zeilen und meldet darum immer
   „1", egal ob ein Text oder alle 64 betroffen sind. Immer je Text auszählen.
2. CapCut schreibt Drafts beim Beenden zurück. Vor jedem Eingriff prüfen, ob CapCut läuft,
   und nach dem Eingriff die Datei noch einmal gegenlesen.

## Die Untertitel-Fläche der Quelle ist selten ein Balken — Breite mitmessen, nicht nur Höhe

Nachtrag zur Höhen-Regel darüber. Die Höhe allein reicht nicht: Viele Quellen setzen ihre
Untertitel nicht auf einen durchgehenden Balken, sondern auf eine **Platte, die den Text
umschließt** — sie ist damit je Einblendung verschieden breit (VIS 006 EL gemessen:
168 bis 547 px von 720).

**Deutsch ist länger als Englisch, und das trifft genau hier auf.** Über 54 Einblendungen
gemessen: 20 deutsche Zeilen breiter als ihre Platte, Überstand Median 181 px, max 517 px.
Kein Schriftgrad repariert das — für die schmalste Platte müsste die Schrift auf rund ein
Drittel schrumpfen.

**Die Regel:** Sitzen die deutschen Untertitel auf der Fläche der Quelle, braucht der
CapCut-Caption-Stil einen **eigenen Hintergrund-Kasten**. Dann deckt der deutsche Kasten die
alte Platte und geht darüber hinaus — es bleibt bei EINEM Balken. Nur verschieben und den
Stil nicht anfassen ergibt die einzige wirklich hässliche Kombination: halbe Zeile auf
Schwarz, halbe auf dem Bild.

**Zweitens, für den Schriftgrad:** Die Quelle misst man an der Versalhöhe der OCR-Boxen
(VIS 006: Median 36 px → Schriftgrad ≈ 50 px). Die deutsche Fassung braucht davon rund
**20 % weniger**, sonst läuft die längste Zeile aus dem Bild — hier: 32 Zeichen bei 42 px
= 702 px in einem 720-px-Bild, bei 40 px = 662 px. Die 34-Zeichen-Regel sichert die
Zeilenzahl, nicht die Bildbreite; die hängt am Schriftgrad und muss eigens gerechnet werden.

**Und die Arbeitslehre:** Ich hatte „Untertitel gehören auf die Platte" empfohlen, ohne je
die Breite zu messen — die Höhe gemessen, die Breite angenommen. Bei einer Fläche werden
**beide** Maße gemessen; eine halb gemessene Empfehlung ist eine Vermutung mit Zahlen davor.

## Betriebs-Ansage — Token-Sparsamkeit (Viktors Befehl, 20.09.2026)
Jeder Lauf und jede Schwester-Session arbeitet ab sofort TOKEN-SPARSAM, Qualität
unverändert: Messungen per Skript statt Agenten-Frame-Reads, Sichtung nur auf
Top-Treffer (klein + gekachelt), knappe Ausgaben, keine Doppel-Lektüre, Hilfs-Agenten
nur für unvermeidbaren Augen-Beweis. Kein Knoten fällt aus — nur der Weg wird billiger.
Diese Ansage ist beim Lesen dieser Datei verbindlich auszuführen.

## Szenen-Text-Rebrand auf 3D-Knet (VIS 001 EL, 20.09.2026)
Deterministischer Composite (cv2.inpaint des alten Textes + geprägte PIL-Schrift) trägt bei
STABILEN Shots sauber — Endcard-Schriftzug „SleepEase Pro" → „Sleep Guard Pro" gelang framestabil
(Band inpainten, Text mittig, heller Highlight + dunkelbraun für Prägung). Er SCHEITERT bei
bewegten 3D-Objekten mit Verdeckung: die Push-in-Box (~2× Skalierung) mit überlappendem Etui —
weiße Schrift liegt nicht in der Blau-Maske (Bug: onface-Filter tilgt sie mit), Perspektive dreht,
Etui frisst die rechte Fläche. Sauberes Werkzeug dafür ist Nano Banana (kie-Gemini image_url) —
war 18.–20.09. im Anbieter-Ausfall (alle Routen 500). Regel: bei Ohr/Bild-Ausfall die stabilen
Text-Spots deterministisch lösen, die bewegten dem Menschen-Gate vorlegen. Viktor entschied an
der CapCut-Sichtung „Box original lassen" — ein Fremd-Produktname auf einem schwer rebrandbaren
bewegten Packshot ist seine Abwäg-Entscheidung, nicht die der KI.

## VIS 002 EL (20.09.2026) — drei Werkstatt-Lehren
- **capcut_paket.py --projekt will den PIPELINE-Ordnernamen** („002 EL"), nicht den
  Projektnamen — mit vollem Namen bricht es mit „final.mp4 fehlt" ab (Pfad P=brands/
  <brand>/<projekt> + nr=split()[0]).
- **Whisper-Wortzeiten als Montage-Grundlage: Kanten-Anker-Woerter gegenpruefen.** difflib
  verlegte die Blockgrenze („Mann A nimmt" → „Man ahn im den") und haengte den Satzanfang
  VOR die Bild-Kante; der Block-Slice-Transkript-Check (Hoerung endet mit fremdem
  Wortanfang) findet es. Reparatur am WAV: Chunk hinter die Kante, Rest bitidentisch.
- **ElevenLabs-Quota-Null-Lage:** Scribe/TTS teilen EIN Zeichen-Konto; bei 0 laufen
  Montage-Schnittzeiten, Pruefer-Ruecktranskription und Wort-Cache lokal (faster-whisper
  als VORLAUF, nie Beweis — Captions dann aus SOLL-Woertern + Cache-ZEITEN bauen, sonst
  stehen Garbles im Untertitel). Keine Neuwuerfe/Takes bis Reset — Gate ehrlich ausweisen.

## Linien-Löschung erfasst auch CapCut-Drafts (VIS, 20.09.2026)
„Eine Linie restlos löschen" (Projekt-Karten, brands-Pipeline, final/, Brand-DB, Stimmen-Zeile,
inbox-Quellen) übersieht leicht die CapCut-Drafts unter ~/Movies/CapCut/User Data/Projects/
com.lveditor.draft/. Beim Neu-Vergeben eines Kürzels (VIS Augen → VIS Sleep Guard) blieben 6
Alt-Drafts liegen und verdeckten den neuen als Namens-Duplikat ("VIS 001 EL - 18.09" neben
"- 19.09"). Regel: Beim restlosen Löschen einer Linie auch die zugehörigen CapCut-Drafts
entfernen — aber nur die eindeutig alten (Datum/Slug), nie die frischen der laufenden Schwestern.

## Multi-Charakter-Quelle = Stimmen je Charakter (Viktors Gate-Befund VIS 004 EL, 20.09.2026)
Quelle mit mehreren FIGUREN-ICHS („I'm your throat muscles/heart/brain/CPAP …"): EINE
Register-Stimme spricht alle Figuren flacher als das Original — der Quell-Sprecher
verstellt sich messbar je Figur (VIS 004: F0-Median 137→213 Hz zwischen den Figuren).
Regel: Erkennt die Clip-Karte/Emotionskarte mehrere Sprecher-Figuren, wird je Figur
eine eigene Stimme gecastet (gleicher Casting-Trichter, Figuren-Register als Filter:
tief/müde, panisch, professoral, weinerlich, energisch) und der Take JE FIGUR als ein
Stück erzeugt — das Ein-Take-Gesetz gilt je Stimme, Kontextbruch am Figurenwechsel ist
natürlich. Die Montage-Infrastruktur (Marken/Segmente) trägt das ohne Umbau.
Viktors Wort im Lauf: „du solltest eig für jeden charakter eine andere stimme usen".

## caption_stil.py macht Captions unter CapCut 185 unbearbeitbar (VIS 004 EL + VIS 003 EL, 20.09.2026)
Der Stil-Pass verpackt jede Mitlese-Zeile als TEXT-VORLAGE: materials.text_templates
bekommt je Zeile einen Eintrag und die Track-Segmente zeigen mit material_id auf das
Template statt auf materials.texts — Vorlagen-Segmente sind in CapCut (Migration auf
185.0.0) nicht frei editierbar; Viktors Befund „KANN ES NICHT BEARBEITEN". Stil-Werte
im Template zu patchen aendert nichts (Bindung bleibt).
FIX (deterministisch): CapCut killall (haelt .locked, ueberschreibt beim Beenden) →
in draft_info.json je text-Segment material_id von text_templates[i].id auf texts[i].id
umbiegen (Reihenfolge 1:1) → materials.text_templates=[] → CapCut neu starten.
Nebeneffekt: Highlight-Stil weg, Standard-Text voll editierbar — und genau so ist das
Gesetz (capcut-export-immer-wie-sol002: Stil macht Viktor per „auf alle anwenden").
REGEL AB JETZT: caption_stil.py NICHT mehr in der Push-Kette aufrufen; Anleitung-
Schritt „Mitlese-Stil setzen" entfaellt, bis das Werkzeug plain-Texte stylt.

## NACHTRAG CapCut 185 (VIS 004, 20.09.2026, byte-bewiesen): tmp-Rueckroll + 6-Hex-Falle + Fox
(1) Ein von 185 einmal geoeffneter Draft traegt template-2.tmp/Resources — spaetere
draft_info.json-Patches werden beim naechsten Start/Autosave ZURUECKGEROLLT
(draft_info wird byte-gleich zum tmp). Ein migrierter Draft wird darum NICHT geflickt,
sondern GELOESCHT und jungfraeulich neu gebaut; ALLE Patches VOR dem ersten Start.
(2) Patch-Paket vor Erstkontakt: explizites Mapping seg.material_id →
tpl.text_info_resources[0].text_material_id → texts.id (NIE Reihenfolge — Fehlerquelle),
text_templates=[], 185-Farbfix je text (text_color '#ffffffff' 8-HEX — 6-Hex parst 185
als TRANSPARENT/unsichtbar; check_flag 47, use_effect_default_color true, shadow 8-Hex;
Quelle awms-09), config.subtitle_keywords_config leeren (Schablonen-Fox 'THE QUICK
BROWN FOX' = Stil-Preview-Futter), draft_feinschliff --fette N.
(3) CapCut-Tod vor jedem Draft-Schreiben BEWEISEN: osascript quit → sleep → pgrep leer
(killall-Fallback, wieder pruefen) — ein lebendes CapCut ueberschreibt mit RAM-Stand.

## KORREKTUR zur 185-Falle (awms-22 / VIS 006, 20.09.2026): Taeter ist die SCHABLONE
Die text_templates entstehen bereits in capcut_export.draft_bauen — die Schablone
0319-spender007 ist selbst template-basiert (VIS 006: 87 Templates ganz OHNE
caption_stil.py). caption_stil.py stellte sie nur um und bleibt trotzdem draussen
(nutzlos + 6-Hex-Farbrisiko). Der Ketten-Fix gehoert damit fest HINTER draft_bauen
(Entkopplungs-Schritt: material_id ← tpl.text_info_resources[0].text_material_id,
dann text_templates=[]) — oder draft_bauen baut kuenftig nativ (/rip-Kandidat,
Analyse-Kette: awms-09 → awms-22 → VIS 004).

## Ohr-Ausfall: der Ersatzweg ist gebaut, nicht improvisiert (VIS 010 EL, 21.09.2026)
Das Gemini-Ohr war an ALLEN Routen tot (kie.ai 500 Wartung; `gemini-3-pro-preview` gibt
422). Wichtiger als der Ausfall ist, was an seine Stelle tritt — und dafür existiert
bereits ein Werkzeug, das im Lauf VIS 010 EL beinahe übersehen worden wäre:
**`tools/sp/emotions_messen.py`** misst die Delivery am Original (F0, F0-Spanne, Pegel,
Silben/s, Pausen) statt sie zu hören. Wer bei totem Ohr zur Wendepunkt-Regel greift,
ohne dieses Werkzeug zu fahren, liefert eine abgeleitete statt einer belegten Karte.

**Aber: das Werkzeug allein reicht bei gleichmäßigen Sprechern nicht.** Bei einer Quelle
mit F0 87 Hz und nur 17 Hz Spanne vergab es „calm" auf ALLE 152 Sätze — messtechnisch
richtig, als v3-Vorgabe aber genau die Monotonie, die Viktor in VIS 001 EL gerügt hat.
**Das Rezept ist die Kombination:** Wendepunkt-Regel als Gerüst (damit die Spur atmet),
überschrieben von der Messung überall dort, wo das Original messbar vom eigenen
Grundton abweicht. In VIS 010 EL waren das 16 Überschreibungen plus 6 Flüster-Stellen —
darunter der Kipp-Punkt „It never ends it.", den das Original LEISE spricht (−22,6 dB
gegen −18,8 dB Grundpegel). Solche Regie-Entscheidungen der Quelle findet keine Textregel.

## Der Tempo-Lift 1,12 ist eine Obergrenze, kein Zielwert (VIS 010 EL)
Bei 1,12 blieben in einer 5:47-Longform **33 Lücken ≥ 0,8 s** in der Spur stehen, während
die QUELLE keine einzige Lücke ≥ 0,8 s hat (größte 0,74 s). Der richtige Wert wird gegen
das Rhythmus-Profil der Quelle gesucht, nicht aus der Voreinstellung übernommen: Median-
Wortlücke, 90-%-Quantil, größte Lücke und Stille-Anteil von Spur und Original
nebeneinander. Die Montage ist frei wiederholbar (keine Credits) — dieser Vergleich
kostet nichts und ist Pflicht bei Longform.

## Silben statt Wörter, und Tags kosten 15 % Tempo (VIS 010 EL)
Die Registerspalte `sprechrate_wps` ist als Budget-Grundlage unbrauchbar: Für Damien
führt sie 2,30 W/s, gemessen wurden **2,99 W/s** — ein Drittel Unterschied, weil W/s mit
der Wortlänge kippt. Gerechnet wird in **Silben** (streut nur ~22 %). Zweiter Fallstrick:
Der tag-freie Messblock ergab 4,22 Si/s, der fertige Take MIT v3-Audio-Tags nur
**3,61 Si/s** — die Tags kosten 15 % Tempo. Wer mit dem tag-freien Wert budgetiert,
produziert eine Copy, die nicht ins Bild passt (in VIS 010 EL: 8 % Überlänge, 123 Silben
mussten nachträglich verdichtet werden).

## Der blockweise Prüfer gibt falsch-rot, die Vollspur entscheidet (VIS 010 EL)
`pruefer.py` meldete 40 von 42 Blöcken rot; die Rückhörung der GANZEN Spur gegen die
Soll-Copy ergab 99,35 % Wort-Deckung und genau EINEN echten Fehler. Der Prüfer sagt das
selbst („Scribe verliert am Schnitt den Kontext"), aber nur für einzelne Blöcke. Regel:
Block-Rot ist ein Verdacht, kein Befund — bestätigt wird er an der Vollspur-Hörung.

## Der CapCut-Spender macht Untertitel UNVERÄNDERBAR (VIS 010 EL, 21.09.2026)
Viktors Befund am fertigen Draft: „untertitel sind falsch, kann nicht ändern". Der
Wortlaut war richtig, die Zeiten waren richtig, die Position war richtig — aber alle
184 Untertitel hingen an einem **`text_template`** statt an einem echten `text`. Eine
CapCut-Textvorlage ist ein verpackter Effekt: anklicken und umtippen geht nicht.

**Ursache: der Spender, nicht das Skript.** `capcut_export.draft_bauen()` erbt die
Struktur des neuesten echten CapCut-Projekts, und `0319-spender007` hat seine eigenen
17 Untertitel als Textvorlagen. Weder `caption_stil.py` noch der Schriftfix haben das
verursacht — beide liefen sauber.

**Betroffen sind alle Läufe aus diesem Spender.** Gemessen über alle 30 Drafts auf dem Mac:
- unveränderbar (an Textvorlage): VIS 001 EL (67), VIS 002 EL (70), VIS 007 EL (38),
  VIS 008 EL (54), RAN 001 EL (222), VIS 010 EL (184) und die Spender 0319/0319 (1)/(2)
- **editierbar (an echtem Text): VIS 004 EL (74), VIS 005 EL (58), VIS 006 EL (87),
  sleepease-cpap-reise (66)**

**Erkennen (eine Zeile):** je Text-Segment prüfen, ob `material_id` in
`materials.texts` liegt (gut) oder in `materials.text_templates` (unveränderbar).
Nicht am Bild erkennbar — beide sehen im Player gleich aus.

**Beheben (0 Credits, deterministisch):** Die Text-Spur aus einem editierbaren Draft
nachbauen — Text-Material und Segment von dort als Muster deepcopy'en, je Untertitel
neue id, `content.text` + `styles[].range` setzen, `material_id` auf den neuen Text
zeigen lassen, Zeiten und `clip.transform.y` aus dem alten Draft übernehmen,
`text_templates` leeren. In VIS 010 EL: 184/184 umgestellt, 0 Zeitabweichung > 50 ms,
0 fehlende Schriften.

**Nebenwirkung, die Viktor kennen muss:** Der gelbe Look (`逐词高亮-黄`) steckte IN der
Textvorlage. Nach der Umstellung tragen die Untertitel den Stil des editierbaren
Musters (weiß mit Schatten, Montserrat-Bold). Farbe und Look setzt Viktor in CapCut —
und das geht jetzt.

**BEHOBEN am 21.09.2026 auf Viktors Zuruf „dann mach":** Neues Werkzeug
**`tools/sp/untertitel_editierbar.py`** stellt die Text-Spur eines fertigen Drafts nach
dem Bau um — deterministisch, 0 Credits. Es sucht sich automatisch einen Draft mit
bearbeitbaren Untertiteln als Muster, übernimmt Wortlaut, Zeiten und Y-Position 1:1,
prüft am Ende gegen und **rollt bei jeder Abweichung zurück**. Es weigert sich zu
schreiben, solange CapCut läuft (der Fehler, der diesen Lauf zweimal aufgehalten hat).
`--pruefen` misst nur, ohne zu schreiben.

**Warum nicht in `draft_bauen()` selbst:** Die Vorlagen-Bauweise ist dort Absicht
(`spender_finden` verlangt ausdrücklich einen Spender MIT `text_templates`), und der
Bauer bedient ALLE Ketten — Singing, DOG, KRA, RAN. Ein Eingriff im Kern hätte alle
getroffen. Die Umstellung danach ist der kleinere, prüfbare Schnitt.

**Verdrahtet:** `tools/sp/capcut_paket.py` packt das Werkzeug ab sofort mit ins Paket,
und `tools/sp/capcut_anleitung_vorlage.md` trägt es als **Pflicht-Schritt 2b** zwischen
Draft-Bau und Feinschliff, mit Selbst-Prüfung (muss mit GRUEN enden und „0 an
Textvorlage" melden). Damit läuft es in jedem künftigen Lauf von selbst.

**Die Alt-Drafts sind NICHT angefasst** (VIS 001/002/007/008 EL, RAN 001 EL) — das wäre
ein Eingriff in fertige Projekte ohne Auftrag. Wer sie braucht, fährt
`untertitel_editierbar.py "<Name>"` darüber; das Werkzeug erkennt sie von selbst.

## Vmake tilgt Schrift, aber keine gefüllten Flächen (21.09.2026, VIS 009 EL + VIS 010 EL)
**Gemessen an zwei Quellen derselben Linie am selben Tag:**
- VIS 009 EL — Karaoke-Captions MIT Kasten (weiße Versalien + ein blau HINTERLEGTES Wort):
  Vmake tilgt die Schrift restlos, die blaue Fläche bleibt stehen — in **55 % der Frames**,
  Spitzenlast 278 px/Frame im Band y 660–840. Zweiter Vmake-Lauf: bitgleiches Ergebnis
  (Skill-Regel „was es nicht erkennt, erkennt es auch beim Wiederholen nicht" bestätigt).
- VIS 010 EL — Karaoke-Captions OHNE Kasten (weiß + gelbes Wort), 347 s Quelle: Vmake tilgt
  restlos. Gemessen von levert-awms-98: **0 Fenster ≥ 0,5 s unberührt**, Restschaden nur
  kleine dunkle Flecken — 15,9 % der Frames mit Querlauf gegen **21,7 % in einem
  caption-freien Kontrollband derselben Ad**, also unter dem Bildrauschen.

**Die Trennlinie ist nicht Karaoke ja/nein, sondern ob das Highlight eine FLÄCHE hat.**
`videoscreenclear` ist für Schrift und Wasserzeichen gebaut, nicht für gefüllte Kästen —
an einer Fläche verschwinden die Buchstaben, der Kasten bleibt als Keil.

**Konsequenz für die Trigger-Prüfung:** Beim Augen-Check die Caption-Optik der Quelle
benennen (Schrift allein / Schrift auf Kasten). Trägt sie Kästen, ist der Vmake-Ausgang
absehbar — dann NICHT erst sechs Reparatur-Varianten durchprobieren (so verlor VIS 009 EL
rund eine Stunde), sondern direkt die deckende Untertitel-Karte einplanen (DOG-Weg).

**Die Karte richtig setzen (VIS 009 EL):** Fleck-Band vorher MESSEN (Differenz Original ↔
Vmake-Fassung, zeilenweise Dichte) statt schätzen — bei VIS 009 lagen 90 % der Reste in
y 660–840, die Karte wurde y 652–848. Über Custom-Clip-Fenstern die Karte AUSSETZEN (dort
ist das Bild neu gerendert, es gibt nichts zu decken) und dort Untertitel mit Kontur statt
Kasten setzen; auf einer Offer-Card den Untertitel in die freie Fläche versetzen, sonst
verdeckt er den Preis.

**Folge für die Kette:** Mit eingebrannten Untertiteln entfällt das CapCut-Paket. Das ist
eine bewusste Abweichung vom Captions-Knoten und gehört in den Lauf-Bericht.

**Dokumentierte Alternative (nicht eingebaut, Stand 21.09.2026):** Will jemand den
Karaoke-Look ZWINGEND schon im Bau, braucht CapCuts Vorlage 逐词高亮-黄 ein gefülltes
`current_word_info` mit Wort-Timings — sonst rendert sie ihren Demo-Text
(„THE QUICK BROWN FOX", Befund levert-awms-98 im Lauf VIS 010 EL). Die Daten liegen in
jedem EL-Lauf bereits als `_pipeline/sprech_words.json` (Scribe auf der fertigen Spur,
Format `{"w","s","e"}`; erzeugt `sprechspur.py woerter --audio _work/sprechspur.wav`).
Die Kette baut es trotzdem NICHT ein: Viktor kann Untertitel nur an ECHTEN Texten
bearbeiten — jede Vorlage, ob gefüttert oder nicht, nimmt ihm das. Statischer Stil
排列-白 bleibt die Bau-Vorgabe, den Karaoke-Look setzt Viktor selbst in CapCut.

## Frames aus zwei Videos IMMER framegenau ziehen (21.09.2026, VIS 009 EL)
`ffmpeg -ss <t> -i <datei>` springt auf den nächsten Keyframe — und zwei Fassungen desselben
Videos (Original vs. Vmake) haben verschiedene Keyframe-Positionen. Ein Vergleich solcher
Frames misst zwei VERSCHIEDENE Zeitpunkte. Das hat in VIS 009 EL vier Reparatur-Varianten
verbrannt: Die Differenz-Maske war von Anfang an richtig, lag aber auf versetzten Frames und
sah darum falsch aus. Richtig: `-i <datei> -vf "select='eq(n\,<frame>)'" -vsync 0`.

## Szenengrenzen der Clip-Karte gegenprüfen, bevor ein Custom Clip einsetzt (21.09.2026, VIS 009 EL)
Die Clip-Karte setzte den Endcard-Beginn auf Frame 2198; gemessen (Nachbar-Frame-Differenz)
liegt der Schnitt bei **2180**. Der Custom Clip startete dadurch 0,6 s zu spät — 18 Frames
mit fremdem Brandname am Ende der Ad. Viktors Befund: „der Schluss ist unclean, bei 1:13."
Regel: Vor dem Einsetzen jedes Custom Clips seine Grenzen am ORIGINAL nachmessen, nicht der
Szenenerkennung glauben. Und den Start-Frame am Clip-ANFANG greifen — ein Frame aus der
Clip-Mitte erzeugt einen Sprung, den kein Prüfer als Naht erkennt.

## Kling-Prompt gegen das Handlungs-Inventar schreiben, nicht aus der Erwartung (21.09.2026, VIS 009 EL)
Der erste Endcard-Prompt sagte „a hand sets the box down and lifts away" — im Original bleibt
die Hand die ganze Zeit auf der Box. Ergebnis: ein Clip, der sichtbar nicht zur Quelle passte.
Das Handlungs-Inventar (§3 des Custom-Clip-Skills) ist genau dagegen gebaut; es war hier aus
Zeitdruck übersprungen worden.

## Entkopplung hält — der Beweis fehlte bisher (VIS 010 EL, 22.09.2026, 02:21)
Der „NACHTRAG CapCut 185" schrieb den Weg vor (geöffneten Draft löschen, jungfräulich
neu bauen, ALLE Patches vor dem ersten Start), aber niemand hatte belegt, dass CapCut
den entkoppelten Zustand danach auch BEHÄLT. Jetzt ist es belegt:

Ablauf, der getragen hat: CapCut-Tod beweisen → Draft-Ordner wegnehmen → `draft_bauen`
neu → **`caption_stil.py` WEGLASSEN** → `untertitel_editierbar.py` (Entkopplung über
`text_info_resources`, 185-Farbfix, alle drei Dateien bit-identisch) → `draft_feinschliff`
→ Sidecars nach dem Feinschliff nochmal angleichen → erst dann CapCut starten.
Ergebnis nach CapCuts EIGENEM Speichern um 02:21: alle drei Dateien 184 an echtem Text,
0 Vorlagen, Wortlaut deutsch, 0-mal „QUICK BROWN", text_color 8-Hex, Schrift lokal.
Dateigröße fiel auf CapCuts kompaktes JSON (1.284.492) — es hat den Zustand übernommen,
nicht zurückgerollt.

**Zwei Fallen, die dabei Zeit gekostet haben:**
1. **Nach `osascript quit` hängen die Helfer nach — und `pgrep -x` sieht sie nicht.**
   Gemessen bei laufendem CapCut: `pgrep -f -i capcut` findet ACHT Prozesse
   (Hauptprozess, drei Renderer-Helfer, zwei weitere Helfer, GPU-Helfer,
   `parfait_crash_handler`), `pgrep -x CapCut` nur EINEN. Die Helfer halten Dateien
   weiter. **Richtig ist `pgrep -f -i capcut` plus `ps aux | grep -i capcut`** — und
   darauf WARTEN statt abzubrechen (Schleife mit Zeitschranke, `killall` als Notausgang,
   danach erneut prüfen); nachhängende Helfer sind der Normalfall, kein Fehlerfall.
   ZURÜCKGENOMMEN: In diesem Lauf stand hier zuerst, `pgrep -f` sei ein Eigentreffer und
   man solle auf `-x` wechseln. Das ist FALSCH und hätte den Schutz abgebaut — drei
   Proben mit einem nur in der eigenen Kommandozeile vorkommenden Wort zeigen keinen
   Selbsttreffer, macOS-pgrep nimmt sich selbst aus. Gemeldet und gemessen von der
   Schwester-Session levert-awms-3e, hier nachgeprüft und bestätigt.
2. **Der Feinschliff schreibt nur `draft_info.json`.** Wer ihn NACH der Entkopplung
   fährt, bricht die Sidecar-Gleichheit wieder auf. Reihenfolge einhalten oder die
   Sidecars danach erneut angleichen.

**Korrektur einer Fehldiagnose aus diesem Lauf:** Das „THE QUICK BROWN FOX" im Player
wurde zuerst der leeren `current_word_info` der Karaoke-Vorlage `逐词高亮-黄` zugeschrieben.
Gemessen steht der Text 0-mal im Draft und `subtitle_keywords_config` ist `null` — er
kommt aus der Vorlagen-Ressource selbst. Die Entkopplung behebt es, weil sie die Vorlage
ganz entfernt; die Karaoke-Erklärung war falsch.

**Viktors Entscheid dazu (21.09.2026, Popup):** „Editierbar ist wichtiger" als das
Wort-Highlight aus seiner Ansage vom 17.09. Das Highlight setzt er in CapCut selbst —
deckt sich mit dem Ketten-Gesetz capcut-export-immer-wie-sol002.

**Lücke im Workflow, gemeldet:** Der Knoten `capcut-push` der Workflow-Datei verweist
NICHT auf diese Lernkartei. Wer ihn abarbeitet, ohne sie gelesen zu haben, läuft in
genau dieselbe Runde. Kandidat für /feedback am Workflow.

## VIS 021 EL · 25.09.2026 — zwei Werkzeug-Lehren am Trigger und an der Clip-Karte
- **Clip-Grenzen driften, wenn der Ton länger ist als das Bild.** `tools/sp/clip_karte.py` rechnete
  `FPS = Frames / dur`, und `dur` (sp_config) ist die CONTAINER-Dauer — sie folgt der längeren Spur. Bei
  65,734 s Ton gegen 1968 Frames (65,600 s Bild) lagen die harten Schnitte um den Faktor 1,002 zu spät
  (+0,03 s bei 15 s, +0,13 s bei 64 s), und das Ankleben < 0,8 s übernahm jeweils die falsche, spätere
  Grenze. Behoben: FPS aus dem Video-Strom, letzte Grenze = Bilddauer, Selbstprüfung (Median der
  Abweichung harter Schnitt ↔ ffmpeg-Szenenschnitt, Abbruch über 1 Frame). Einzel-Ausreißer sind KEIN
  Achsenfehler: Blitz-Doppelschnitte (3 Frames) und harte Sprünge ohne Szenenschnitt gibt es wirklich.
  **Regel:** Wer Zeit aus Frame-Indizes rechnet, nimmt die Bildrate des Video-Stroms, nie eine Dauer.
- **Der Lip-Sync-Vorbefund zählt Knet-Gesichter mit.** `lipsync_bereiche.py --vorbefund` meldete 32 von
  66 s „frontales Gesicht" — es waren 3D-Knet-Figuren (Opa, Ehefrau). Das Werkzeug misst Gesichter, nicht
  Menschen; die Entscheidung „Mensch oder Figur" bleibt beim Augen-Blick. Knoten-Regel (17.09.2026): nie
  Cartoon-/3D-Figuren → keine Lip-Sync-Frage. Bei VIS 016 EL (derselbe Knet-Look) blieb der Detektor
  still (0 s) — ob er anschlägt, hängt an der Nahaufnahme, nicht am Stil.

## VIS 016 EL · 25.09.2026 — Vmake lässt die schwarze KONTUR von Karaoke-Captions als Punkte stehen
- **Befund:** Weiße/gelbe Versalien-Captions MIT schwarzer Kontur (SleepEase-Knet-Ads): `videoscreenclear`
  tilgt die Füllung, lässt aber Stücke der Kontur als dunkle Punkte/Striche stehen — sichtbar auf hellen
  Flächen (Handfläche im Hook 0–3 s, Decke, Sand, Tisch, weißer Teller). Schlieren-Scan („Band ruhig") und
  OCR (0 Text) melden GRÜN — nur die Voll-Sichtung des Bands (Kacheln 2 fps, alle Sekunden) zeigt es.
- **Was trug (0 zusätzliche Credits außer 1 Vmake-Task):** zweiter Vmake-Lauf auf einer Quelle, in der die
  Buchstaben-Zone (Glyphe + 4 px) NUR in den OCR-Caption-Kästen weiß gefärbt ist (sonst weißt die
  Farbschwelle helle Hintergründe mit) → dunkle Reste fast weg, dafür helle Halos an WEISSEN Flächen.
  Fusion beider Läufe je Pixel nach lokaler Anomalie (|V − Median21|, Gauss σ 4: wo ein Lauf heraussticht,
  gewinnt der andere), Fenster mit weißen Flächen nach Augen-Entscheid aus Lauf 1, dazu eine geeichte
  Punkt-Retusche (Telea r=3). Werkzeuge: `brands/VIS - Visiovance Sleep Guard/016 EL/_pipeline/`
  `kontur_weiss016.py`, `umkehr_fusion016.py`, `restpunkte_lib016.py`.
- **Was NICHT trug (am Bild geprüft):** Vmake nur auf dem Fenster (dieselben Striche); Rest-Detektoren
  „lokales 5-%-Quantil", „Telea-Erwartungshintergrund", „karten-statisch (Rest steht fest, Szene wandert)"
  — alle markierten echte Steppnähte, Schattenbänder, Anatomie-Kanten oder verfehlten die Striche.
  Ein Maß, das die Retusche freigibt, ist vor dem Render an bekannt-schlechten UND bekannt-guten Frames zu
  eichen und das Ergebnis AM BILD zu prüfen: die erste „grüne" Retusche radierte das echte Schattenband.
- **Regel:** Bei Captions mit schwarzer Kontur gehört die Voll-Sichtung des Caption-Bands (nicht nur
  Stichproben) zum Vmake-Knoten; der Vorweiß-Lauf ist der erste Fix, Fusion + Augen-Fenster der zweite.

## Vmake-Geist auf flachen Flächen — die Band-Differenz sieht ihn nicht (25.09.2026, VIS 017 EL)
**Befund:** Karaoke-Captions ohne Kasten (weiß + gelbes Wort, dunkle Kontur + weicher Schatten) auf einer
Illustrations-Quelle. Die 4b-Messung (Band-Differenz Original↔Vmake) meldete „überall gearbeitet" (Mittel 18,9,
nur Caption-Pausen unberührt). Tatsächlich blieb auf FLACHEN Flächen (Hellblau, Papier, Boden, Dunkelblau) ein
lesbarer dunkler Buchstaben-Geist stehen — „gearbeitet" heißt nicht „getilgt". Auf Struktur (Anatomie, Schlafzimmer)
war Vmake sauber. Gegensatz zu VIS 010 EL (gleiche Caption-Optik, dort restlos): quellenabhängig, also je Lauf messen.
**Messung, die es findet (0 Credits, ~1 min):** Apple-Vision-OCR (`tools/sp/ocr_vision.swift`) über das Caption-Band
ALLER Frames der Vmake-Fassung bzw. der fertigen Bildbasis; Treffer mit Transkript-Wörtern = Rest. Band-Differenz
und Schlieren-Scan (Helligkeit) sind dafür blind.
**Fix, der trug:** `brands/VIS - Visiovance Sleep Guard/017 EL/_pipeline/caption_tilgen.py` — Bildbasis = Original;
Maske = OCR-Wortkästen der Captions im ORIGINAL (framegenau, +12 px, ±1 Frame); Füllung je 120-px-Streifen: Vmake,
wo es Struktur trägt, Telea aus dem Original, wo Vmake geistert (Bandpass-Energie der Vmake-Füllung > 1,4× Ring-Energie
ODER Korrelation mit dem Buchstabenmuster > 0,30), zeitlich geglättet, plus gesichtete Pflicht-Fenster. Direkt in YUV
(keine Farbmatrix-Falle). Verworfen, gemessen: Glyphen-Maske + Telea (Halo breiter als Maske → fleckig),
Frequenz-Splice Vmake-Hochpass + Telea-Tiefpass (falsche Grundfarbe an Hand/Nachttisch).
**Filter-Fallen dabei (alle drei passiert):** Gestaltungs-Text nie per WORT schonen (das gesprochene „COMFORT"/„FOREVER"/
„NO" hieß wie das Label) — nur räumlich (≥ 80 % im Element-Kasten) UND nur in seinem Zeitfenster; ein Schonkasten, der
die Caption-Zeile überdeckt (Stempel 49,5–50,4 s), schont die Caption mit → lieber das Element mit tilgen und im Slot
neu setzen. Höhen-Grenzen für OCR-Kästen großzügig (zweizeilige/verschmolzene Karten bis 120 px).
- **Eine Route in Wartung ist kein Wackler — nach zwei 500er-Aufrufen überspringen.** Die Ohr-Werkzeuge
  (`emotions_karte.py`, `pruefer.py`) wiederholten bei HTTP 500 jede Zeile mit 20/40 s Pause — bei
  gemini-2.5-pro in Wartung (25.09.2026) kostete das ~60 s je Zeile, die Emotions-Karte von VIS 021 EL
  (28 Sätze) lief ~35 min statt ~10. Sicherungsschalter eingebaut (s. tools/sp/README.md). Beim Prozess-
  Check NIE `ps -o command` auf curl-Kinder: die Kommandozeile trägt den kie-Schlüssel im Header —
  nur `ps -o pid,etime,comm`.
**NACHTRAG (VIS 017 EL, abends): Die OCR-Probe ist notwendig, nicht hinreichend.** Nach der Streifen-Hybrid-Tilgung
meldete OCR 0 Wörter — die 2-fps-Voll-Sichtung (480 px Kacheln) zeigte trotzdem dunkle Vmake-Geister und Telea-Balken
(1-fps-Kacheln mit 300 px waren zu klein dafür). Getragen hat der VIS-016-Weg: Kontur+Schatten in den OCR-Kästen vorab
weiß (Glyphe + 6 px), zweiter Vmake-Lauf, dann v2 als STANDARD (die Anomalie-Fusion mittelt flächige v1-Schlieren nur),
v1 nur bei hellem v2-Halo und in gesichteten Weiß-Fenstern, Telea nur auf wirklich flachem Grund
(`brands/VIS - Visiovance Sleep Guard/017 EL/_pipeline/fusion017.py`). Reihenfolge künftig: OCR-Probe UND 2-fps-Sichtung.

## Vmake auf 3D-Anatomie: Szenen-Fenster, Clean-Plates, Schatten-Maske (VIS 020 EL, 25.09.2026)
1. **Der Caption-Schatten ist größer als die Schrift.** Gemessen an der Etui-Szene (gegen eine saubere
   Plate): Abdunkelung oberhalb der Glyphen bis ~30 px, UNTERHALB bis ~45 px (Drop-Shadow nach unten
   versetzt; 19 px unter der Schrift noch −20 Graustufen). Eine Montage-Maske „Glyphe + 7 px" lässt auf
   glatten Flächen einen grauen Hof stehen. Maske asymmetrisch dilatieren (oben 30 / unten 45 / seitlich 30).
2. **Szenen-exakte Fenster schlagen den Voll-Lauf** — aber nicht überall. Kinn, Chart, Blitz, Schlafender,
   Tunnel: Fenster sauber (rote Flecken und Kästen des Voll-Laufs weg). Zunge, Muskel-Blende, Etui-Kante:
   auch das Fenster malt (Vmake ist dort deterministisch schlecht).
3. **Was dann trägt, je Fall:** (a) glatte Fläche mit dunklem Band → Vmake-Textur behalten, Niederfrequenz
   aus der Laplace-Füllung des Original-Umfelds (NICHT bei dunkler Höhle zwischen hellen Wänden — dort
   entsteht ein heller Fleck); (b) Kante eines Objekts unter der Schrift → Kante in freien Spalten fitten,
   Band an der Kante flachziehen, zeilenweise interpolieren, als Plate per lokaler ECC-Affin in die
   Nachbar-Frames ziehen; (c) strukturierte Anatomie, die nie frei liegt → NB2-Edit EINES Frames als
   Clean-Plate, per ECC in jeden Frame, Poisson-Einsetzen (nur der Randversatz wandert nach innen).
   Blenden: Überblend-Anteil je Frame per Regression messen und die sauberen Enden mischen.
4. **ECC-Plate nur, wo ECC ≥ 0,98.** Zoomt die Kamera stark (Rachen F340–F394: cc 0,2–0,7), fällt der
   Warp aus — dort das Vmake-Fenster behalten.
5. **Animierte Leuchteffekte im Band** (blauer Glüh-Bogen der Muskel-Szene) lassen sich nicht sauber
   synthetisch nachzeichnen (kastige Ränder). Beste Lösung: Maske oben auf 12 px verkleinern, damit der
   Bogen über der Schrift original bleibt; hinter der Schrift verschwindet er — wie im Original.
- **Die Budget-Rate einer Stimme ist kein Festwert — Damien sprach 4,4 statt 3,61 Si/s (VIS 021 EL).** Die Copy war
  gegen die VIS-010-Rate gebaut und lief 20 % zu kurz: tote Luft genau an den Stellen, an denen die Übersetzung wegen
  des Budgets Original-Inhalt gekürzt hatte. Reihenfolge, die das spart: erst EINEN Wurf der fertigen Copy erzeugen,
  Rate messen, DANN die GEKÜRZT-Stellen gegen die gemessene Rate entscheiden (sp-learnings 50 bestätigt).
- **marken_planen.py überschätzt atempo in verankerten Fenstern.** `--nur-messen` meldet die Block-DATEI inkl.
  Vorlauf 0,30 + Nachlauf 0,20 s, der Planer rechnet den Atem 0,35 s obendrauf — zwischen zwei Kanten-Ankern ergibt
  das 1,18–1,24 „über 1,15 → kürzen", während die Montage (Wortdauer gegen Fenster) nur 1,04–1,10 brauchte. Vor einer
  Kürzungs-Gate-Frage die echte Montage bauen und ihr Protokoll lesen.
- **Scribe schreibt „Sleep Guard" zusammen („Sleepguard").** pruefer.py wertete das als fehlendes Wort (0,8 → rot);
  Abgleich um Leerzeichen-Paare ergänzt (VIS 021 EL). Die Website schreibt übrigens auch „SleepGuard Pro".

## Letztes Fenster endet am letzten BILD, nicht an der Container-Dauer (VIS 023 EL, 25.09.2026)
`sp_config.json` trägt `dur` = Container-Dauer (ffprobe format) — bei VIS 023 EL 60,18 s, weil die Tonspur länger ist
als das Bild (1.802 Frames = 60,07 s). Die vorläufige `marken.json` setzt das `ende` des letzten Blocks auf `dur`; die
Montage plante den Schluss-Block damit 0,11 s zu lang, und das letzte Wort („unten.") lief 0,15 s hinter das letzte
Bild (gemessen: Sprache bis 60,22 s). **Regel:** das letzte `ende` = Bilddauer (nb_frames/fps) minus ~0,1 s Ausklang;
nach jeder Montage prüfen: letzter Pegel > −45 dB liegt vor dem letzten Frame. Fix im Lauf: `ende` 59,95 → Sprache
endet 59,98 s. /feedback-Kandidat: `tools/sp/sprechspur.py`/`new_sp_project.py` sollen die Bilddauer führen.

## VIS 016 EL · 25.09.2026 — dichte Quelle (4,9 Si/s): Viktors Entscheid „volle Copy im Original-Tempo"
- **Befund:** Die Quelle spricht 266 Wörter/351 Silben in 72 s. Die deutsche Copy lag nach Leiter-Stufe 1–3 bei Silben-
  GLEICHSTAND (354 Si, ×1,01) — trotzdem 100,1 s Roh-Take, weil Damien mit v3-Tags ~3,5 Si/s spricht. Werkzeug-Grenze
  (Tempo 1,12, Block-atempo 1,15) → Kürzungs-Leiter Stufe 6 = Viktors Frage. Hörprobe A (Take ×1,388, 93 % Rück-
  Transkription) + Optionen B (kürzen) / C (weniger Tags) vorgelegt; **Viktor wählte A** (erste Entscheidung dieser Art).
- **So gebaut, ohne das geteilte Werkzeug zu ändern:** Roh-Take einmal mit atempo vorbeschleunigen (_work/take_A.wav),
  Montage darauf mit `--tempo 1.0 --atem 0.0`. Grund für Atem 0: `montage --nur-messen` meldet je Block die Dateidauer
  INKLUSIVE Vor-/Nachlauf-Rand — die natürlichen Satzpausen des Takes stecken also schon drin; jeder zusätzliche Atem
  zählt doppelt (mit 0,30 s: 79,5 s Bedarf statt 72,0 s). DE-Satzpausen danach median 0,32 s gegen 0,25 s im Original.
  Anker-Konflikte (einzelne Zeilen länger als ihr Kanten-Fenster) durch gezieltes Lösen von 5 Kanten-Ankern gelöst — die
  Zeile setzt NACH dem Schnitt ein (+0,1…1,1 s), nie davor; Restluft je Abschnitt gleichmäßig verteilt (tote Luft weg).
- **Prüfer-Folge:** „Blöcke kleben" (Stille < 0,25 s) an 11 Marken = Rhythmus der dichten Quelle (das Original hätte 13
  solche Stellen) → dokumentierter Trade-off, am Gate „Passt".
- **Musikbett:** Das Demucs-Bett trug Rest-Stimme (Whisper erkennt die EN-Copy im auf −16 LUFS verstärkten Bett). Ein
  ZWEITER Demucs-Durchgang auf das Bett tilgte sie restlos (0 Wörter) bei nur −2,5 dB Bett-Verlust. Prüfung ist billig:
  Bett normalisieren, Whisper small drüber, Wörter zählen.
- **CapCut bei Parallel-Sessions:** Eine Schwester-Session startet CapCut nach ihrem Push neu (Anleitung Schritt 4) —
  dann ist es für den eigenen Draft-Bau wieder offen. Nie ein fremd genutztes CapCut beenden: auf `pgrep -f '[C]apCut.app/Contents'`
  leer (mehrfach hintereinander) warten, dann bauen.

## VIS 019 EL (25.09.2026) — Hook-Variante als voller Zweitlauf: was trug, was hakte
1. **Hook-Variante = gleicher Körper, gleiche Pixel, ganzzahliger Frame-Versatz.** Ton-Hüllkurve r 0,99 und
   Bild-MAD 0,84 bei exakt 83 Frames gegen VIS 015 EL. Damit passt der abgenommene Bild-Slot-Satz der Bibliothek
   PIXELGENAU — nur Zeitfenster verschieben (`019 EL/_pipeline/slots_einbau019.py --versatz`), vorher den Compositor
   an der Schwester-Bildspur eichen (MAD ≈ 1). Die gespeicherten Bibliotheks-Skripte kennen nur Runde 1–2 der
   Reparaturen; der ENDSTAND steckt in den fertigen Overlay-Dateien + overlays_statisch.json.
2. **Overlays nur einblenden, nie ausblenden, wenn ein Deck unter einem Text-Slot liegt.** Ausblenden der Abdeckung
   unter dem einblendenden Endcard-Text ließ in VIS 015 ~8 Frames „TREATMENT THAT TRAVELS WITH YOU" durchblitzen.
3. **Tempo-Lift 1,00 statt 1,12 bei diesem Körper.** Bei 1,12 blieben 12 Lücken bis 2,55 s; bei 1,00 spricht Damien
   ~4,2 Silben/s = Original 4,25 und es bleiben 5 Absatz-Atem ≤ 1,04 s. Engpass-Blöcke an Kanten (Hook) separat
   vorbeschleunigen, statt den ganzen Take zu heben.
4. **Mini-Takes allein sprechen ~10 % langsamer als im Fluss.** Block-Würfel darum IM KONTEXT (Block + Folgesatz)
   erzeugen und an Scribe-Wortzeiten herausschneiden (Hook: 6,0/6,2 s allein vs 5,42 s im Kontext).
5. **Preis mit Cents gesprochen kostet ~2–3 s.** „neunundneunzig Euro neunundneunzig, mit Gratisgeschenken" drückt
   die letzten 20 s bis 3,3 s vor ihre Bilder (Viktor wählte es trotzdem, VIS 019 Gate A).
6. **Umkehr-Montage: Weiß-Schwelle verfehlt einblendende (graue) Karten** → Maske ∪ Tilgung (Original > Vmake + 25);
   Nachmessung mit Tilgungs-Detektor (Memory vmake-umgekehrt-montieren-original-als-basis, Nachtrag 25.09.).
7. **Objekt-Tausch auf ruhiger Kamerafahrt deterministisch:** EIN Nano-Banana-Edit (Crop 1:1, 1K) + geglättete
   SIFT-Homographie je Frame, in der Überblendung als Delta mit gemessenem Gewicht — 0 Kling-Credits, Handlungen
   und Einblendungen bleiben Original (Bibliothek VIS/euro-muenze-statt-quarter).
8. **Gemini-Ohr 25.09.:** 2.5-pro 500 (Wartung), 2.5-flash/3-flash 422, gemini-3-pro hörte (Bindung 1,0) — aber unter
   Last langsam (2–10 min je Block) und ab ~19:45 ebenfalls 500. Kalibrierung: Aussprache/Hänger erkannt, Roboter/
   Artefakt-Klang NICHT (blind) → diese Klasse bleibt Messung + Viktors Ohr.
9. **/watch fehlt auf dem Mac** — Fakten-Check lief mit derselben Methode (Clip-Mitten-Frames + Scribe-Rücklesung).

## VIS 016 EL (25.09.2026) — `pgrep -f -i capcut` trifft FREMDE Kommandozeilen (Nachtrag zu „ZURÜCKGENOMMEN" oben)
- **Beide Messungen stimmen, sie messen Verschiedenes:** pgrep nimmt nur SICH selbst aus (Schwester levert-awms-3e,
  bestätigt). Jeden ANDEREN Prozess, dessen Kommandozeile das Wort trägt, trifft `-f -i` mit — etwa ein Warte-Skript
  `capcut_draft016.sh`, ein `tail -f …capcut….log`, ein Python-Aufruf mit Pfad `_capcut-paket/…`. Gemessen 21:51:46:
  0 echte App-Prozesse (App-Start erst 21:52:24 laut `ps lstart`), trotzdem brach `untertitel_editierbar.py` mit
  „CapCut laeuft" ab — der Draft blieb mit 83 Captions an Textvorlage liegen, das Bau-Fenster war verloren.
  Gegenprobe mit Attrappe (`/bin/sleep` als Symlink `capcut_attrappe`): Roh-Probe 9 Treffer, echte App 8.
- **Fix (Master `tools/sp/`):** `untertitel_editierbar.py` und `untertitel_stil_auf_alle.py` zählen nur noch Treffer,
  deren Kommandozeile mit `/Applications/` beginnt und `CapCut.app` enthält (`capcut_prozesse()`, dieselbe Filterung,
  die `untertitel_spur.py` schon hatte). Alle 8 echten Prozesse liegen dort, auch `parfait_crash_handler` — der Schutz
  bleibt vollständig, `-x` bleibt falsch. Meldetexte unverändert (Warter, die auf „laeuft" greppen, gehen weiter).
- **Ältere Paket-Kopien** (`<NNN>/_capcut-paket/scripts/untertitel_editierbar.py`, vor dem 25.09. ~22:00 kopiert)
  tragen noch die Roh-Probe: Warte-Skripte und Logs darum NIE nach der App benennen, Pfade mit dem Wort nur über
  Python-stdin statt als Argument (Muster: `016 EL/_pipeline/draft_bau016.sh`).
- **Selbst-Spur bei `--pruefen` (Nachtrag, gleicher Lauf):** Nach JEDER Entkopplung warnte `untertitel_editierbar.py
  --pruefen` „schon geöffnet, LÖSCHEN und neu bauen" — die einzige „Spur" war die `template-2.tmp`, die das Werkzeug
  selbst schreibt (Sidecar-Regel). Wer der Warnung folgt, baut endlos neu. Geeicht an allen 45 Drafts dieses Macs:
  28/28 von CapCut geöffnete tragen zusätzlich `draft.extra`/`Resources`/`attachment_editing.json`; nur
  `template-2.tmp` + `draft_info.json.vor-entkopplung` = frisch entkoppelt, ungeöffnet (5/5). CapCut schreibt
  `template-2.tmp` übrigens byte-gleich zu `draft_info.json` — Byte-Gleichheit trennt NICHT. Fix: dieser Fall wird
  als Hinweis gemeldet, die echte Warnung bleibt (Gegenprobe VIS 015 EL warnt weiter).

## WIDERRUF zu „1:1-Rip heisst: Bildtext bleibt ORIGINAL" (Linie VIS, 25.09.2026)
Viktor hat zweimal in Folge das Gegenteil verlangt: VIS 022 EL (Test-Auftrag „alles, was im Hintergrund auf Englisch ist, ins native
Deutsch“) und VIS 024 EL (nach dem Gate: „bitte auch alle englischen Clips bei dieser Ad vor allem auf Deutsch machen“). Für VIS gilt
ab jetzt: englischer Bildtext wird deutsch nachgebaut (deterministisch: Lage je Frame per Template, Retusche, Neusatz in gemessener
Schrift — Werkzeuge in brands/VIS - Visiovance Sleep Guard/024 EL/_pipeline/). Die Regel oben (VIS 003 EL) bleibt als Beleg stehen.

## Text-Clips in Blenden, Zooms und Rollen: Englisch TILGEN, Deutsch als eigene Ebene (VIS 020 EL, 25.09.2026)
Werkzeug: `brands/VIS - Visiovance Sleep Guard/020 EL/_custom-clips/labels3_clip020.py` (0 Kling, 3 NB2-Referenz-Edits).
1. **Das Differenz-Modell `f + a·W(ed − ref)` geistert, sobald das Label sich bewegt.** Es muss das Englische pixelgenau
   aufheben; bei Zoom-Einblendung (Skala 0,65 → 1,03), Einschweben (+25 px) oder Blende reichen 0,02-Skalenraster und
   ganzzahlige Lage nicht — „THROAT"/„AIRWAY"-Kanten standen hinter dem Deutschen. ECC-Feinlage (affin, auf der
   Hochpass-Textschicht) hob die Korrelation von 0,90 auf 0,99, die Geister blieben trotzdem sichtbar.
   **Tragender Weg:** Englisch per Fläche tilgen (Vmake-Fensterlauf NUR in der Buchstaben-Maske + LF-Korrektur; in einer
   Szenen-Blende, wo Vmake schmiert, Laplace-Fill aus dem eigenen Umfeld), Deutsch als EIGENE Alpha-Schicht aus dem
   NB2-Edit mit Lage + Deckkraft des Originals darüber. Die Lage muss dann nur noch ±1 px stimmen.
2. **Deckkraft in verwischten Zoom-Frames per Energie, nicht per Regression:** Die Hochpass-Regression unterschätzt
   unscharfe Schrift (F396: 0,002 statt 0,085). Σ(Frame − Vmake-Hintergrund) in der Maske / (Referenz-Energie · det(W))
   trifft in scharfen Frames die Regression auf 0,995 und bleibt in Unschärfe richtig.
3. **Buchstaben-Maske fetter Versalien:** Y − Median61 fängt die Mitte breiter Buchstaben (M, W) nicht — dort IST der
   Median Schrift. Dazu absolut hell (Y > 215), Cyan-Linien ausschließen, Glanzlichter per Mindestfläche raus, Zeiger-
   Linien per Zeilen-Filter raus (sonst Knick in der Linie an der Box-Kante).
4. **Clip-Karten-Grenze ≠ Sichtbarkeit:** „50 / HOUR" stand noch 9 Frames in der Wischblende des Folge-Clips (F890–F898).
   Fenster immer bis zum letzten Frame mit sichtbarem Text messen; in der Wischblende Deutsch nur in den Spalten der
   alten Szene.
5. **Rollender Text (Slot-Zähler):** Versatz + senkrechte Unschärfe + Fensterkante je Frame passen, Suchfenster je Frame
   auf Zeilen ohne Ziffern-Übermacht begrenzen (sonst gewinnt eine Ziffer die Korrelation); Boden = Hintergrund-Plate.
6. **Selbst-Sichtung vor dem Gate fand zwei Fremdmarken-/Artefakt-Reste, die jeder Prüfer-Zahl standhielten:**
   Schachtel-Seitenwand trug weiter „SleepEase PRO" (Maske nahm nur die blaue Front, der NB2-Edit hatte die Seite schon
   richtig) und die Endkarte zeigte ein Textfeld-Rechteck (NB2 malt das Feld 4–6 Stufen dunkler; eine Matte gegen die
   Plate nimmt das als Tinte → Matte nur aus den Buchstaben gegen den EIGENEN Hintergrund des Edits).
7. **Blitz-Frames:** Vmake lässt in fast weißen Blitz-Frames einen blassen Kasten mit Buchstabenspuren; Glyphen-Fill im
   Original scheitert dort am dunklen Caption-Glow (dunkler Fleck). Nur Frames mit Helligkeit ≥ 225 glatt füllen.

## VIS 024 EL (26.09.2026) — englischen Bildtext deutsch nachbauen: was trägt (Engine `brands/VIS - Visiovance Sleep Guard/024 EL/_pipeline/bildtext024.py`)
1. **Schrift per Form-Überdeckung wählen, nicht per Augenmaß:** Glyphen-Maske des Originals gegen alle Mac-Schriften (IoU nach
   Breiten-Normierung). Poppins lief 10–14 % breiter als der Titel → Treffer Avenir Next Bold (Laufweite −0,10); Labels = Inter
   SemiBold; Unterzeile/Endkarte = Sukhumvit Set Bold. Das ganze Video ist zudem ~0,9 horizontal gestaucht → Breite je Zeile am
   englischen Wort eichen (gleiche Schrift, gleiche Versalhöhe; Laufweite einrechnen, sonst doppelt gestaucht).
2. **Erst ALLES Englische entfernen, dann ALLES Deutsche zeichnen** — sonst zieht die Füllung der nächsten Zeile die frischen deutschen
   Glyphen als weiße Schlieren hoch. Füllung: Spalten-Verlauf als Start + Laplace-Glättung (keine Spalten-Streifen). Schlagschatten
   am Ruhe-Frame fitten (Versatz/Unschärfe/Stärke) und beim Entfernen mitnehmen.
3. **Linien schützen:** Unterstriche/Hinweislinien per Öffnung mit Linien-Kernen abtrennen (nur bei kleiner Schrift — große Titel haben
   selbst lange Striche), vor dem Füllen wegretuschieren, danach zurücklegen. Ohne das verschwand der Unterstrich unter „CPAP-Gerät“.
4. **Bewegung:** Glättung symmetrisch (an den Kanten roh), Ein-/Ausblendung über die Bahn fortsetzen; Szenenschnitt am GANZEN Bild
   messen (bewegtes Objekt ist kein Schnitt); Überblendung über Textur per Blend-Modell (Text abziehen, Deutsch addieren); schneller
   Einflug: größere starre Umgebung verfolgen (ganzer Pass statt 9-px-Schrift), Drehung + Bildrand-Überhang in der Suche, deutscher
   Satz mit gleicher Bewegungsunschärfe; Szenen-Wisch: Sichtbarkeit spaltenweise gegen den Frame vor dem Wisch.
5. **Nachweis statt Stichprobe:** macOS-Vision-OCR (`tools/sp/ocr_vision.swift`, per swiftc gebaut) auf jedem 2. Frame aller Fenster,
   Liste englischer Wörter — geeicht am Original (29 Wörter, >1.800 Treffer) → Ad: 0. Fand vorher genau die 2 übersehenen Stellen
   (Unterzeile im Wisch-Frame, Pass im Einflug), die keine Sichtung gesehen hatte.
6. Kleine Schrift 4× überabgetastet setzen (bei 9 px Versalhöhe verklumpen sonst die E-Zähler); Lage-Cache je Item mit Versionsnummer
   der Geometrie-Logik (sonst liefert der Cache nach Code-Änderungen alte Bahnen).

## VIS 017 EL (26.09.2026) — deutscher Bildtext auf BEWEGTEN Flächen ohne Kling + Faktencheck fand Füll-Schäden (Engine `brands/VIS - Visiovance Sleep Guard/017 EL/_pipeline/slots017.py`, Basis-Reparatur `rueckholung017.py`)
1. **Ebene statt Kling auch bei Bewegung — wenn die Bewegung messbar ist:** 10 Fenster (Zoom, Einfahrt, Stempel-Pop,
   Kreisblende, Schiebe-/Wisch-Blende) als nachgeführte Ebene, 0 Credits, Viktors Go 26.09. Je Fenster die passende Messung:
   SIFT-Ähnlichkeit je Frame (Zoom/Kamera), ECC-Affin der Schriftmaske (roter Titel), Kreuzkorrelation (Einfahrt, Etui-
   Wippen), Tinten-Rechteck je Frame (Stempel-Pop — ECC lief beim winzigen Stempel weg), Schriftbreite (Etikett-Pop),
   Homographie verkettet (unscharfe Karton-Einfahrt). Bewegungsmaß danach 0,92–0,98 des Originals.
2. **Referenz-Frame muss das Objekt im gleichen Zustand zeigen:** Etui-Aufdruck mit dem OFFENEN Etui (2640) als Referenz
   → falsch; eigener Slot mit dem geschlossenen Deckel (2580). Endlage nie im letzten Frame vor einem Schnitt/Übergang messen.
3. **Fenstergrenzen per OCR über JEDEN Frame prüfen:** drei Rest-Wörter lagen genau am Fensterrand (1064 „ANN/$200“ im
   End-Wisch, 2419/2420 „sleepease“ in der unscharfen Einfahrt, 2482 „100-NIGHT“ beim Einblenden) — keine Vorschau sah sie.
4. **Faktencheck (Sekunden-Kontaktbogen, volle Breite) fand, was OCR und Prüfer nie melden:** die Telea-Füllung der Fusion
   war auf FLACHEM Grund heller als der Grund (sichtbare Streifen 26–35 s, 0–3,5 s, 47 s) und verschmierte Symbole unter der
   Caption (Filter/Flasche/Karton). Fix „Flach-Füllung“: außerhalb der Caption = Original (OHNE Schwelle), in der Caption
   spaltenweise senkrecht zwischen den Rändern interpolieren (Randwert, der vom Grund abweicht → Grundfarbe; Palette bei
   Wisch-Frames mit zwei Gründen), Symbolteile aus Vmake v2 nur, wo sie an Symbol-Pixel außerhalb anschließen, ruhender
   Symbol-Stapel aus einer Median-Platte der caption-freien Momente. Senkrechte Kanten (Wischkante) bleiben so erhalten.
5. **cap_streng statt Zone auf Szenen mit Weiß+Dunkel:** die breite Caption-Zone (L<50 = „Kontur“) trifft dunkle Endcards
   und Symbol-Konturen — für Masken in solchen Szenen die strenge Caption-Maske (Füllung neben TIEFSCHWARZER Kontur L<32,
   Komponenten ≥ 30 px) UND die OCR-Caption-Kästen schneiden.
