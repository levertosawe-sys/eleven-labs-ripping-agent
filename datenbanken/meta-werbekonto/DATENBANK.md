---
name: meta-werbekonto
typ: Adressbuch (JSON, auf dem Server) + externer Ablageort
zweck: Wohin die fertigen Ads gehen UND wo sie danach liegen
schreibt: tools/ad-upload (upload.py) — legt Anzeigengruppe, Creative und Anzeige an
liest: tools/ad-upload (upload.py) — je Ziel-Brand-Kürzel ein Eintrag
format: tools/ad-upload/ziele.json — je Kürzel ein Eintrag; der Ablageort selbst ist das Werbekonto bei Meta
---

**WO DAS DING WOHNT:** Das Adressbuch liegt als `ziele.json` beim Uploader auf dem
Server (`/root/AWMS/`); der Ablageort ist das Meta-Werbekonto selbst. In diesem
Mac-Ordner liegt nur diese Karte — hier fehlt nichts.

## Adressbuch — je Ziel-Brand-Kürzel ein Eintrag
Werbekonto · Seite · Pixel · Kampagne · Vorlage-Anzeigengruppe · Ziel-Link · CTA.

Neue Brand = neuer Eintrag. **Geändert wird dort, nie im Code.**

## Ablageort
Das Meta-Werbekonto, in dem die hochgeladenen Anzeigen liegen. Wiedergefunden werden
sie über den Projektnamen — „KÜRZEL NNN | DATUM“ ist zugleich der Name der
Anzeigengruppe.

## Regeln
- Der Uploader erfindet nichts: Budget, Zielgruppe und Platzierungen kommen aus der
  Vorlage-AdSet.
- Quasi-Ads laufen über eine eigene Facebook-Seite (steht im Adressbuch).
- Die Zugänge wohnen in `/root/AWMS/.env` (Karte: `SCHLUESSEL-KARTE.md`).
