---
name: ad-upload
description: Eine fertige, aus CapCut exportierte Ad als Meta-Anzeige hochladen — Video, Anzeigengruppe und Creative anlegen, immer pausiert. Nutzen, wenn Viktor sagt „lade die Ad hoch", „ad-upload", „stell das online", „pack das in den Ads Manager", den Upload-Auftrag aus dem Ripping Sheet einfügt, oder eine fertige MP4 in den Einwurf-Ordner legt und Bescheid gibt. Nicht für das Scharfschalten laufender Anzeigen — das macht Viktor selbst.
---

# Ad hochladen

Letzter Schritt der Kette: Das Video ist gebaut, in CapCut fertig geschnitten und
exportiert. Jetzt wird daraus eine Anzeige im Werbekonto.

Das Werkzeug macht die Meta-Arbeit, du machst die Urteilsarbeit — Anzeigentext,
Headline, Plausibilität. Erfinde nichts an der Schnittstelle: alle API-Aufrufe
gehören ins Werkzeug, nicht in den Chat.

```
python3 /root/AWMS/tools/ad-upload/upload.py <pruefen|hochladen|bericht>
```

## Die eine Regel, die nicht verhandelbar ist

**Anzeigen entstehen IMMER pausiert.** Das Werkzeug erzwingt es; versuche nie, es
zu umgehen, auch wenn Viktor „mach live" sagt. Scharfschalten passiert im Ads
Manager von Hand — ein Klick für ihn, aber kein Weg, wie ein Fehler Budget
verbrennt. Sagt er, es solle direkt laufen: Anzeige pausiert anlegen, ihm den
Ads-Manager-Link geben, und dort schaltet er sie an.

## Ablauf

**1. Trockenübung — immer zuerst.**

```
python3 /root/AWMS/tools/ad-upload/upload.py pruefen
```

Zeigt, welche Videos im Einwurf-Ordner liegen, zu welchem Projekt sie gehören und
was angelegt würde. Schreibt nichts. Zeig Viktor das Ergebnis in eigenen Worten:
Konto, Kampagne, Vorlage-Anzeigengruppe, Ziel-Link.

Häufige Befunde und was sie bedeuten:

| Befund | Ursache | Was du tust |
|---|---|---|
| Kein Projektname im Dateinamen | Export heißt nicht wie der CapCut-Draft | Viktor fragen, welches Projekt — dann `--projekt` mitgeben |
| Projekt-Ordner nicht gefunden | Tippfehler oder Projekt existiert nicht | Namen gegen die Projekte-Datenbank prüfen |
| Kein Upload-Ziel für Kürzel | Brand fehlt in `tools/ad-upload/ziele.json` | Mit Viktor klären, dann Eintrag ergänzen |
| SCHON HOCHGELADEN | `upload.json` liegt im Projekt | STOPP — nachfragen, nie ungefragt `--nochmal` |

**2. Anzeigentext vorschlagen.**

Der Anzeigentext ist NICHT das VSL-Skript. Lies die finale Copy des Projekts
(`<projekt>/*-final-*.md`) für Angebot, Nutzen und Tonalität, aber schreibe
kurzen Feed-Text daraus.

Zwei Felder:
- **Primary Text** — was über dem Video steht. Ein bis drei Sätze, Problem oder
  Nutzen zuerst, kein Roman.
- **Headline** — die Zeile unter dem Video. Kurz, konkret, mit dem Angebot.

Richte dich an dem aus, was im Konto schon läuft: Die bestehenden Anzeigen der
Brand zeigen Viktors Tonalität besser als jede Regel. Schlag beides vor und lass
ihn ändern — hier liegt sein Urteil, nicht deins.

**3. Erst nach seinem ausdrücklichen OK hochladen.**

```
python3 /root/AWMS/tools/ad-upload/upload.py hochladen \
  --projekt "<KÜRZEL NNN | TT.MM.JJJJ>" \
  --text "<Primary Text>" --headline "<Headline>"
```

Das Werkzeug lädt das Video hoch, wartet auf Metas Verarbeitung, kopiert die
Anzeigengruppe aus der Vorlage (Budget, Zielgruppe, Platzierungen bleiben
unverändert), baut das Creative und legt die Anzeige an. Die Anzeigengruppe heißt
wie das Projekt — darüber finden Ripping Sheet und Meta einander wieder.

Bricht ein Aufruf ab, wiederhole ihn NICHT blind: Meta hat dann meist schon Teile
angelegt, und ein zweiter Lauf erzeugt eine zweite Anzeigengruppe. Lies die
Fehlermeldung, behebe die Ursache, und räume Halbfertiges vorher weg.

**4. Abschluss melden.**

Nenne Viktor den Ads-Manager-Link und bestätige, dass `upload.json` im
Projektordner liegt. Diese Datei ist der Beweis für das Ripping Sheet: Sobald sie
existiert, gilt das Projekt als gelauncht und verschwindet aus „Im Rip". Ohne sie
hängt das Projekt für immer in der Pipeline — deshalb nie von Hand löschen.

## Was du nicht tust

- **Kein Budget ändern, keine Zielgruppe bauen.** Alles kommt aus der Vorlage.
  Will Viktor etwas anderes, ändert er die Vorlage-Anzeigengruppe im Ads Manager
  oder den Eintrag in `ziele.json` — nie du im Vorbeigehen.
- **Keine Anzeige scharfschalten**, auch nicht auf Zuruf.
- **Nicht zweimal hochladen.** `upload.json` ist der Doppel-Upload-Schutz.

## Wenn eine neue Brand dazukommt

`tools/ad-upload/ziele.json` bekommt einen Eintrag pro Ziel-Brand-Kürzel:
Werbekonto, Seite, Pixel, Kampagne, Vorlage-Anzeigengruppe, Link, CTA. Die IDs
holst du dir mit dem Graph-Explorer oder aus dem Ads Manager — und legst sie
Viktor zur Bestätigung vor, bevor die erste Ad dorthin geht. Wo die Zugänge
wohnen, steht in `/root/AWMS/SCHLUESSEL-KARTE.md`.
