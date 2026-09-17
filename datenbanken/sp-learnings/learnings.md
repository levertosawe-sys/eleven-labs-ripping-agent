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

