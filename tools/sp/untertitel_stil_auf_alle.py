#!/usr/bin/env python3
"""untertitel_stil_auf_alle.py — EINEN Untertitel-Stil auf ALLE uebertragen.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Viktors Befund im Lauf VIS 010 EL (22.09.2026): „ich kann die anderen untertitel
anklicken aber den stil kann ich nicht aendern … alle voreingestellte stile und so
dass ich den ganzen untertitel bearbeiten kann, nicht nur eine einzelne spur".

Nach der Entkopplung (untertitel_editierbar.py) sind die Untertitel einzeln
bearbeitbar — aber CapCut behandelt sie als 184 EINZELNE Textelemente, nicht als
Untertitel-SATZ. Auf diesem Mac existiert kein Draft mit echter Untertitel-Kennung
(recognize_type ueberall 0, caption_info ueberall leer, auch in Viktors eigenen
Projekten 0318/0319) — es gibt also kein Muster, aus dem sich die Satz-Struktur
nachbauen liesse, ohne zu raten.

Dieses Werkzeug loest das Problem von der anderen Seite: Viktor stellt an EINEM
Untertitel in CapCut genau den Look ein, den er will (Farbe, Kontur, Schatten,
Groesse, Schrift) — und hier wird dieser Stil auf alle uebrigen kopiert.
Deterministisch, 0 Credits, beliebig oft wiederholbar.

WAS ES NICHT ANFASST
--------------------
Wortlaut, Zeiten, Position, Schrift-PFAD-Gueltigkeit. Nur das `styles`-Objekt im
content jedes Textes, und `range` wird je Text auf seine eigene Laenge gesetzt
(sonst faerbt der Stil nur die ersten n Zeichen).

AUFRUF
------
    python3 tools/sp/untertitel_stil_auf_alle.py "<Draft-Name>" [--quelle N] [--zeigen]

    --zeigen   nur auflisten, welche Stile vorkommen (nichts schreiben)
    --quelle N Nummer des Untertitels, dessen Stil gilt (1-basiert).
               Ohne Angabe: der Stil, der NICHT der Mehrheitsstil ist — also der,
               den Viktor gerade von Hand gesetzt hat. Gibt es mehrere davon,
               bricht es ab und verlangt --quelle.

CapCut MUSS beendet sein (inkl. Helfer). Das Werkzeug prueft das selbst.
Danach CapCut neu starten — es liest Drafts nur beim Start.
"""
import argparse, json, shutil, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path("~/Movies/CapCut/User Data/Projects/com.lveditor.draft").expanduser()


def capcut_prozesse() -> list[str]:
    """PIDs der echten App samt Helfern. `pgrep -f -i capcut` trifft auch jede fremde
    Kommandozeile mit dem Wort (Warte-Skripte, Paket-Pfade; gemessen VIS 016 EL,
    25.09.2026) — gezaehlt wird nur, was aus /Applications/…CapCut.app laeuft."""
    out = subprocess.run(["pgrep", "-f", "-i", "capcut"], capture_output=True, text=True).stdout.split()
    treffer, fremd = [], []
    for pid in out:
        cmd = subprocess.run(["ps", "-o", "command=", "-p", pid], capture_output=True, text=True).stdout.strip()
        (treffer if cmd.startswith("/Applications/") and "CapCut.app" in cmd else fremd).append(f"{pid} {cmd[:110]}")
    if fremd:  # Selbstpruefung: sichtbar machen, was die Roh-Probe faelschlich gezaehlt haette
        print(f"Hinweis: {len(fremd)} fremde Kommandozeile(n) mit dem Wort ignoriert (keine App): "
              + " | ".join(fremd[:3]))
    return treffer


def stil_kurz(st):
    f = (st.get("fill") or {}).get("content", {}).get("solid", {}).get("color")
    s = st.get("strokes") or []
    sc = s[0]["content"]["solid"]["color"] if s else None
    return (f"fuell={f} kontur={sc} breite={s[0].get('width') if s else None} "
            f"schatten={'ja' if st.get('shadows') else 'nein'} groesse={st.get('size')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--quelle", type=int)
    ap.add_argument("--zeigen", action="store_true")
    ap.add_argument("--stil-datei", dest="stil_datei",
                    help="JSON mit EINEM styles-Objekt. Damit laesst sich der Stil VOR dem\nersten CapCut-Start setzen (Prototyp-Weg) — nachtraegliche Patches rollt CapCut zurueck.")
    a = ap.parse_args()

    d_dir = ROOT / a.draft
    if not d_dir.is_dir():
        d_dir = ROOT / a.draft.replace(" | ", " - ")
    if not d_dir.is_dir():
        sys.exit(f"Draft nicht gefunden: {a.draft}")
    ziel = d_dir / "draft_info.json"
    d = json.loads(ziel.read_text(encoding="utf-8"))
    texte = d["materials"]["texts"]
    if not texte:
        sys.exit("Der Draft hat keine Texte.")

    inhalte = [json.loads(x["content"]) for x in texte]
    stile = [c.get("styles", [{}])[0] for c in inhalte]
    schluessel = [json.dumps({k: v for k, v in s.items() if k != "range"},
                             ensure_ascii=False, sort_keys=True) for s in stile]
    zaehl = Counter(schluessel)

    print(f"Draft „{d_dir.name}“: {len(texte)} Untertitel, {len(zaehl)} verschiedene Stile")
    for k, n in zaehl.most_common():
        i = schluessel.index(k)
        print(f"  {n:4d}x  (z.B. #{i+1}: {inhalte[i].get('text','')[:32]!r})  {stil_kurz(stile[i])}")
    if a.zeigen:
        return

    if a.stil_datei:
        vorlage_extern = json.loads(Path(a.stil_datei).read_text(encoding="utf-8"))
        q = None
    elif a.quelle:
        vorlage_extern = None
        q = a.quelle - 1
        if not 0 <= q < len(texte):
            sys.exit(f"--quelle {a.quelle} liegt ausserhalb 1..{len(texte)}")
    else:
        vorlage_extern = None
        mehrheit = zaehl.most_common(1)[0][0]
        abweichend = [i for i, k in enumerate(schluessel) if k != mehrheit]
        if not abweichend:
            sys.exit("Alle Untertitel tragen denselben Stil — nichts zu uebertragen. "
                     "Stell in CapCut an EINEM den gewuenschten Look ein, dann erneut.")
        eindeutig = {schluessel[i] for i in abweichend}
        if len(eindeutig) > 1:
            sys.exit(f"{len(eindeutig)} abweichende Stile gefunden (#{', #'.join(str(i+1) for i in abweichend)}) — "
                     "bitte mit --quelle N sagen, welcher gilt.")
        q = abweichend[0]

    if vorlage_extern is not None:
        vorlage = vorlage_extern
        print(f"\nQuelle: Stil-Datei {a.stil_datei}")
    else:
        vorlage = stile[q]
        print(f"\nQuelle: #{q+1} {inhalte[q].get('text','')[:40]!r}")
    print(f"  {stil_kurz(vorlage)}")

    if capcut_prozesse():
        sys.exit("CapCut laeuft (oder Helfer haengen nach) — erst beenden und warten, bis "
                 "'pgrep -f -i capcut' leer ist.")
    if (d_dir / ".locked").exists():
        sys.exit(f"{d_dir}/.locked liegt noch da — CapCut hat den Draft belegt.")

    shutil.copy(ziel, str(ziel) + ".vor-stil")
    gesetzt = 0
    for x, c in zip(texte, inhalte):
        neu = json.loads(json.dumps(vorlage, ensure_ascii=False))   # tiefe Kopie
        neu["range"] = [0, len(c.get("text", ""))]                  # je Text eigene Laenge
        c["styles"] = [neu]
        x["content"] = json.dumps(c, ensure_ascii=False)
        gesetzt += 1

    inhalt = json.dumps(d, ensure_ascii=False)
    # Sidecar-Regel: alle drei Dateien gleich, sonst rollt CapCut zurueck
    for n in ("draft_info.json", "draft_info.json.bak"):
        (d_dir / n).write_text(inhalt, encoding="utf-8")
    tmps = list(d_dir.glob("template-*.tmp")) or [d_dir / "template-2.tmp"]
    for t in tmps:
        t.write_text(inhalt, encoding="utf-8")

    p = json.loads(ziel.read_text(encoding="utf-8"))
    nach = Counter(json.dumps({k: v for k, v in json.loads(x["content"])["styles"][0].items()
                               if k != "range"}, ensure_ascii=False, sort_keys=True)
                   for x in p["materials"]["texts"])
    ranges_ok = all(json.loads(x["content"])["styles"][0]["range"][1] == len(json.loads(x["content"])["text"])
                    for x in p["materials"]["texts"])
    print(f"\nGesetzt auf {gesetzt} Untertitel · Stile danach: {len(nach)} · range je Textlaenge: "
          f"{'ja' if ranges_ok else 'NEIN'}")
    if len(nach) != 1 or not ranges_ok:
        for n in ("draft_info.json", "draft_info.json.bak", "template-2.tmp"):
            shutil.copy(str(ziel) + ".vor-stil", d_dir / n)
        sys.exit("ROT — zurueckgerollt, nichts veraendert.")
    print("GRUEN in allen drei Dateien. Sicherung:", str(ziel) + ".vor-stil")
    print("CapCut NEU STARTEN.")


if __name__ == "__main__":
    main()
