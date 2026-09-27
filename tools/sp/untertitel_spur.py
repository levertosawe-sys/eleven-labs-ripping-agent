#!/usr/bin/env python3
"""Macht aus gebauten Text-Clips eine ECHTE Untertitel-Spur.

Warum es das braucht
--------------------
`draft_bauen()` legt jede Caption als gewoehnlichen Text an (`type: "text"`).
CapCut behandelt gewoehnlichen Text als Einzelclip: eine Stiländerung gilt nur
fuer diesen einen. Das war Viktors Befund am Lauf VIS 010 EL:
„wenn ich eine veraenderung mache soll es ueber die ganze untertitel spur gehen".

Gemessen an CapCuts eigenem Code (nicht geraten):
  * `libvideoeditor.dylib` traegt das Draft-Schema und eingebettetes Lua.
    Dort steht `if text['type'] == "subtitle" then` (Downgrade-Waechter seit
    Format-Version 81, mit `sub_type == 5` seit 91). `"subtitle"` ist also ein
    echter, von CapCut gekannter Material-Typ — kein erfundener Wert.
  * Das „auf alle anwenden" liegt in `sync_to_all_manager.cpp`; die Sammelstelle
    heisst `getSyncSegments group_id={}` und das Gate davor `hasTextCaptionSegments`.
    Gesammelt wird also ueber `group_id` — und `draft_bauen` vergibt allen Captions
    ohnehin schon dieselbe.

Dieses Werkzeug setzt darum genau drei Dinge und nichts sonst:
  1. `type` → "subtitle"   (macht aus Text einen Untertitel)
  2. `recognize_type` → 1  (markiert ihn als erkannten Untertitel)
  3. `group_id`            (eine einzige fuer die ganze Spur)
Optional `--stil-datei`: setzt denselben Stil als Prototyp auf alle.

HARTE REGEL: laeuft NUR vor dem ersten CapCut-Start dieses Drafts. CapCut rollt
jeden Patch an einem bereits geoeffneten Draft beim naechsten Speichern zurueck
(gemessen am Lauf VIS 010 EL: 22:21 und 02:37). Und alle drei Seitenwagen
(`draft_info.json`, `.bak`, `template-*.tmp`) muessen denselben Stand tragen.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

WURZEL = Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"
SIDECARS = ("draft_info.json", "draft_info.json.bak")


def capcut_laeuft() -> list[str]:
    """Nur die echte App, aber inklusive Helfer-Prozesse.

    Gemessen: `pgrep -f -i capcut` trifft sich NICHT selbst (drei Proben, 0 Treffer
    auf den eigenen Aufruf); es trifft die 8 CapCut-Prozesse, `pgrep -x CapCut` nur
    den einen Hauptprozess. Ein laufender Renderer reicht zum Ueberschreiben.
    """
    out = subprocess.run(["pgrep", "-f", "-i", "capcut"],
                         capture_output=True, text=True).stdout.split()
    treffer = []
    for pid in out:
        cmd = subprocess.run(["ps", "-o", "command=", "-p", pid],
                             capture_output=True, text=True).stdout.strip()
        if cmd.startswith("/Applications/") and "CapCut.app" in cmd:
            treffer.append(pid)
    return treffer


def draft_finden(name: str) -> Path:
    kandidat = WURZEL / name.replace(" | ", " - ")
    if kandidat.is_dir():
        return kandidat
    treffer = [p for p in WURZEL.iterdir() if p.is_dir() and name.split(" | ")[0] in p.name]
    if len(treffer) == 1:
        return treffer[0]
    sys.exit(f"Draft „{name}“ nicht eindeutig gefunden: {[p.name for p in treffer]}")


def schon_geoeffnet(d: Path) -> list[str]:
    """Spuren, die CapCut erst beim Oeffnen anlegt."""
    return [n for n in ("attachment_editing.json", "draft.extra", "Resources", ".locked")
            if (d / n).exists()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help='z.B. "VIS 010 EL | 21.09.2026"')
    ap.add_argument("--stil-datei", dest="stil_datei",
                    help="JSON mit EINEM styles-Objekt; wird Prototyp aller Untertitel")
    ap.add_argument("--gruppe", default=None, help="group_id erzwingen (sonst: die haeufigste)")
    ap.add_argument("--trotz-geoeffnet", action="store_true",
                    help="auch patchen, wenn der Draft schon offen war (CapCut rollt das zurueck)")
    a = ap.parse_args()

    if (pids := capcut_laeuft()):
        sys.exit(f"CapCut laeuft ({len(pids)} Prozesse) — es ueberschreibt Drafts beim "
                 f"Beenden. Erst beenden, dann erneut.")

    d = draft_finden(a.name)
    if (spuren := schon_geoeffnet(d)) and not a.trotz_geoeffnet:
        sys.exit(f"Draft war schon in CapCut offen ({', '.join(spuren)}). CapCut rollt "
                 f"Patches an offenen Drafts zurueck — loeschen und neu bauen, dann "
                 f"patchen. Mit --trotz-geoeffnet trotzdem erzwingen.")

    haupt = d / "draft_info.json"
    roh = haupt.read_text(encoding="utf-8")
    (d / "draft_info.json.vor-spur").write_text(roh, encoding="utf-8")
    j = json.loads(roh)
    texte = j["materials"].get("texts", [])
    if not texte:
        sys.exit("Keine Texte im Draft.")
    if (tpl := j["materials"].get("text_templates", [])):
        sys.exit(f"{len(tpl)} Textvorlagen vorhanden — erst untertitel_editierbar.py "
                 f"laufen lassen, sonst haengen die Untertitel weiter im Effekt.")

    gruppe = a.gruppe or max(
        (t.get("group_id") or "" for t in texte),
        key=lambda g: sum(1 for t in texte if (t.get("group_id") or "") == g)) \
        or f"Auto_{int(time.time() * 1000)}"

    vorlage = None
    if a.stil_datei:
        vorlage = json.loads(Path(a.stil_datei).read_text(encoding="utf-8"))

    for t in texte:
        t["type"] = "subtitle"
        t["recognize_type"] = 1
        t["group_id"] = gruppe
        if vorlage is not None:
            c = json.loads(t.get("content") or "{}")
            neu = json.loads(json.dumps(vorlage, ensure_ascii=False))   # tiefe Kopie
            neu["range"] = [0, len(c.get("text", ""))]                  # je Text eigene Laenge
            c["styles"] = [neu]
            t["content"] = json.dumps(c, ensure_ascii=False)

    inhalt = json.dumps(j, ensure_ascii=False)
    for n in SIDECARS:
        (d / n).write_text(inhalt, encoding="utf-8")
    tmps = list(d.glob("template-*.tmp")) or [d / "template-2.tmp"]
    for t in tmps:
        t.write_text(inhalt, encoding="utf-8")

    # gegenlesen — jeder Seitenwagen einzeln
    fehler = []
    for n in SIDECARS + tuple(t.name for t in tmps):
        p = d / n
        k = json.loads(p.read_text(encoding="utf-8"))["materials"]["texts"]
        n_sub = sum(1 for t in k if t.get("type") == "subtitle")
        n_grp = sum(1 for t in k if t.get("group_id") == gruppe)
        print(f"  {n:24s} {len(k):>4} Texte · {n_sub} als Untertitel · {n_grp} in der Gruppe")
        if n_sub != len(texte) or n_grp != len(texte):
            fehler.append(n)
    if fehler:
        for n in SIDECARS + tuple(t.name for t in tmps):
            (d / n).write_text(roh, encoding="utf-8")
        sys.exit(f"ROT: {', '.join(fehler)} weicht ab — alles zurueckgerollt, nichts geaendert.")

    print(f"\nGRUEN: {len(texte)} Untertitel in EINER Spur (group_id {gruppe})"
          + (f", Stil aus {a.stil_datei} als Prototyp" if vorlage else "")
          + f"\nSicherung: {(d / 'draft_info.json.vor-spur').name}")


if __name__ == "__main__":
    main()
