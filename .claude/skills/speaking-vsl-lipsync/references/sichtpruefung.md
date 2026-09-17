# Sichtprüfung der Lip-Sync-Aufträge

Gelesen in Schritt 4 von `speaking-vsl-lipsync`. Die Prüfung ist Faktenarbeit, kein Geschmack:
je Auftrag fünf Fehlerklassen, TRUE / FALSE / unsicher.

## Wer prüft

Ein Hilfs-Agent (Agent-Werkzeug), weil die Bilder viel Kontext kosten. Er arbeitet nur lokal, ruft keine
bezahlten Dienste und löscht nur eigene Arbeitsbilder. Steht kein Hilfs-Agent zur Verfügung, prüfst du
selbst nach demselben Auftrag, Auftrag für Auftrag.

## Auftrag an den Hilfs-Agenten (Platzhalter ersetzen)

- `<PIPELINE>` = absoluter Pfad des Pipeline-Ordners (`…/brands/<Brand>/<NNN> EL`)
- `<ARBEIT>` = ein eigener Ordner im Scratchpad der Session für seine Bilder
- `<NAMEN>` = die Namen aus `_pipeline/lipsync_einbau.json` (dort sind ersetzte Erstläufe schon entfernt)
- `<SCHRIFT>` = eine vorhandene .ttf-Datei (macOS: `/System/Library/Fonts/Supplemental/Arial.ttf`)

```
Du machst eine reine SICHTPRÜFUNG (Fakten, kein Geschmack) von Lip-Sync-Clips. Nur lokal arbeiten, keine kostenpflichtigen
Dienste, nichts löschen außer eigenen Arbeitsbildern in <ARBEIT>.

Ordner: <PIPELINE>
- Aufträge: _pipeline/lipsync_auftraege.json (f0/f1 = Frames der ganzen Ad, f1 exklusiv).
- Je Auftrag: Eingang _work/lipsync/<name>_video.mp4 (Original-Bild, fremdsprachiger Mund), Ausgang
  _work/lipsync/<name>_lipsync.mp4 (Mund auf deutschen Ton), Ton _work/lipsync/<name>_audio.wav.
- Bekannte Absicht, kein Fehler: fest eingezogene Flächen/Balken aus der Bildbasis (z.B. Untertitel-Fläche).

Prüfe JEDEN dieser Aufträge: <NAMEN> — je Fehlerklasse TRUE/FALSE, bei Zweifel „unsicher":
1. mund_artefakt: verwaschener/verschmierter Mund, doppelte Lippen oder Zähne, flackernde Zähne, Mund „schwimmt" gegenüber
   dem Gesicht, sichtbare Kante oder Farbfleck um die Mundregion.
2. mund_eingefroren: Mund bewegt sich im Ausgang praktisch nicht, obwohl der deutsche Ton spricht.
3. gesicht_veraendert: Gesicht, Augen, Haare oder Hintergrund im Ausgang sichtbar anders als im Eingang (außer Mund/Kinn),
   falsche Person, Farbsprung.
4. grenz_sprung: erster oder letzter Frame des Ausgangs weicht vom Eingang ab — mittlere Pixeldifferenz (0–255, alle Kanäle)
   Frame 0 und letzter Frame Eingang↔Ausgang messen: saubere Aufträge liegen bei 1,5–2,6; über 6 → ansehen, TRUE nur wenn
   sichtbar (Helligkeit, Farbe, Lage).
5. offen_waehrend_stille: Mund deutlich offen/bewegt in Stille ≥ 0,3 s des deutschen Tons, oder geschlossen, während klar
   gesprochen wird. Stille finden: ffmpeg -i _work/lipsync/<name>_audio.wav -af silencedetect=n=-35dB:d=0.3 -f null -
Achte besonders auf Frames mit Farbblitz, Schwarz- oder Weißblende im Eingang: dort erscheint typischerweise ein heller oder
hautfarbener Block im Untergesicht.

Vorgehen: Gesicht je Auftrag mit opencv (haarcascade_frontalface_default) im Eingang finden; Mundmitte = (x + 0,5·w,
y + 0,8·h) der Gesichtsbox, Ausschnitt ~260x200 px darum. Mund-Streifen: jeden 3. Frame, höchstens 12 Kacheln je Reihe,
Eingang oben / Ausgang unten; längere Aufträge auf mehrere Reihen. Beschriftung mit drawtext:fontfile=<SCHRIFT>. Schwere
im Vollbild auf Handy-Größe (~360 px breit) beurteilen, Zoom nur zum Finden.

Rückgabe als Text:
(a) Tabelle je Auftrag: Name · mund_artefakt · mund_eingefroren · gesicht_veraendert · grenz_sprung (Pixeldifferenz
    erster/letzter Frame) · offen_waehrend_stille · Hinweis (max. 12 Wörter)
(b) Liste der Aufträge mit mindestens einem TRUE: je Fund die Frames als [von, bis) in Frames der GANZEN Ad
    (= f0 des Auftrags + Frame im Auftrag), was man sieht, ob ein Blitz/eine Blende im Eingang liegt, und ob es im
    Vollbild auf Handy-Größe sichtbar ist.
```

## Ergebnis verwerten

- TRUE → Reparatur-Tabelle von Schritt 4 im SKILL.md; die Frames aus (b) sind direkt die Fenster-Werte.
- „unsicher“ → wie FALSE behandeln, aber im Karten-Abschnitt nennen.
- Tabelle (a) gekürzt in den Karten-Abschnitt „Knoten lip-sync“ (Anzahl sauber, Befunde mit Klasse und Frames).
