# ANLEITUNG FÜR DIE KI AM MAC — Speaking-Ad nach CapCut

Du baust aus diesem Paket ein natives CapCut-Projekt. Alles ist fertig gerechnet
und maschinell abgenommen — du erzeugst nur den Draft und richtest die Optik ein.
NICHTS neu transkribieren, timen oder mischen.

**Projektname exakt: "{NAME}"** · Video: `final.mp4` ({DAUER}s — trägt den
FERTIGEN Ton-Mix aus Sprechspur + Original-Instrumental: KEINE Musik-Spur dazulegen).

## Schritte

1. **Draft bauen** (Python ≥3.10, nur Standardbibliothek):
   ```python
   import sys, json, shutil
   sys.path.insert(0, "scripts")
   import capcut_export as ce
   name = "{NAME}"
   ce.platz_machen(name)
   media = ce.media_pfad(name); media.mkdir(parents=True, exist_ok=True)
   shutil.copy("final.mp4", media)
   fette = json.load(open("fette_captions.json"))
   hae   = [{"text": h["text"], "t": h["t"], "dauer": h["dauer"]}
            for h in json.load(open("captions{NR}_haeppchen.json"))]
   caps  = [{"text": f["text"], "t": f["t"], "dauer": f["dauer"]} for f in fette] + hae
   pfad, infos = ce.draft_bauen(name, clips=[{"pfad": str(media / "final.mp4"), "dauer": {DAUER}}],
                                captions=caps)
   print(pfad, infos)
   ```
2. **Mitlese-Stil setzen:** Stil aus `assets/caption-stil-default.json` auf die
   Caption-Spur anwenden (wie in Schritt 7 des Skills sa-captions-capcut).
   Position der Mitlese-Häppchen: unten mittig, Textmitte ≈ 81 % Höhe.
3. **Feinschliff — PFLICHT, direkt nach Schritt 1, NIE überspringen. DETERMINISTISCH, nichts von Hand positionieren.**
   Ohne diesen Schritt liegen fette Caption und Mitlese-Häppchen ÜBEREINANDER im
   Untertitel-Band — Viktor sieht dann „zwei Untertitel" (passiert im ROV-007-Lauf,
   21.08.2026). **Selbst-Prüfung nach dem Lauf:** Die Skript-Ausgabe muss für die
   fette Caption eine Ziel-Höhe OBEN (~14 %) und für die Häppchen ~81 % nennen;
   fehlt eine der beiden Zeilen, ist der Draft NICHT abgabefähig.
   ```bash
   python3 scripts/draft_feinschliff.py "{NAME}" --fette {NFETT}
   ```
   Das Skript setzt die fette(n) Caption(s) nach oben auf den Gestaltungs-Balken
   (Ziel-Höhe aus `fette_captions.json`, größer skaliert) und die Mitlese-Häppchen
   auf 81 % Höhe — direkt in der Draft-JSON, selbst-kalibrierend an der
   Spender-Position. Es druckt, was es gesetzt hat. Meldet Viktor danach
   „gespiegelt/oben-unten vertauscht": einmal mit `--flip` erneut laufen lassen.
   Stil-Feinheiten (gelber Balken-Look, Farbe) macht Viktor in CapCut mit zwei
   Klicks am ausgewählten Element — der Wortlaut steht in `fette_captions.json`
   und ist sein Entscheid.
4. **CapCut neu starten** (damit der Draft in der Projektliste erscheint) und
   Viktor Bescheid geben: Projekt "{NAME}" liegt bereit, {NHAE} Mitlese-Häppchen
   + {NFETT} fette Caption(s), nichts eingebrannt.
