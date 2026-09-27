#!/usr/bin/env python3
"""untertitel_editierbar.py — macht die Untertitel eines CapCut-Drafts BEARBEITBAR.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Viktors Befund am Lauf VIS 010 EL (21.09.2026): „untertitel sind falsch, kann nicht
aendern, beim paket ist fehler passiert". Wortlaut, Zeiten und Position waren richtig —
aber alle 184 Untertitel hingen an einem `text_template` statt an einem echten `text`.
Eine CapCut-Textvorlage ist ein verpackter Effekt: anklicken und umtippen geht nicht.

Die Ursache sitzt in `capcut_export.spender_finden()`: Sie verlangt ausdruecklich einen
Spender MIT `text_templates` („nur die geben Captions den Vorlagen-Tab"), und
`draft_bauen()` baut daraufhin jede Caption als Vorlage nach. Das ist Absicht des
Bauers — aber der Preis ist, dass Viktor nichts mehr aendern kann.

Statt in `draft_bauen()` zu operieren (das treffen ALLE Ketten: Singing, DOG, KRA, RAN)
stellt dieses Werkzeug die Text-Spur NACH dem Bau um. Deterministisch, 0 Credits,
kein Generator.

WAS ES TUT
----------
Es nimmt die Bauweise eines Drafts, dessen Untertitel nachweislich bearbeitbar sind
(Segment-`material_id` zeigt in `materials.texts`), und baut die Text-Spur des Ziels
danach neu: je Untertitel ein frisches Text-Material mit dem Wortlaut aus dem alten
Draft, ein frisches Segment mit den ALTEN Zeiten und der ALTEN Y-Position,
`text_templates` geleert.

WAS ES NICHT TUT
----------------
Es formuliert nichts um und verschiebt nichts. Wortlaut, Start/Dauer und Y-Position
werden 1:1 uebernommen und am Ende gegengeprueft; weicht etwas ab, schreibt es nicht.

NEBENWIRKUNG, DIE MAN KENNEN MUSS
---------------------------------
Der Stil steckt IN der Textvorlage (z.B. der gelbe Karaoke-Look `逐词高亮-黄`). Nach der
Umstellung tragen die Untertitel den Stil des editierbaren Musters. Das ist der Handel:
Look gegen Bearbeitbarkeit. Farbe und Look setzt Viktor in CapCut mit zwei Klicks — und
das geht dann auch.

AUFRUF
------
    python3 tools/sp/untertitel_editierbar.py "<Draft-Name>" [--muster "<Draft-Name>"] [--pruefen]

    --pruefen   nur messen und berichten, nichts schreiben
    --muster    Draft, dessen Bauweise uebernommen wird (Default: automatisch der
                juengste Draft mit bearbeitbaren Untertiteln)

CapCut MUSS beendet sein — es ueberschreibt Drafts beim Beenden. Das Werkzeug prueft
das selbst und bricht sonst ab.
"""
import argparse, copy, json, os, shutil, subprocess, sys, uuid
from pathlib import Path

ROOT = Path(os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft"))


def capcut_prozesse() -> list[str]:
    """PIDs der echten App samt Helfern. `pgrep -f -i capcut` trifft auch jede fremde
    Kommandozeile mit dem Wort (Warte-Skripte, Paket-Pfade) — gezaehlt wird nur, was
    aus /Applications/…CapCut.app laeuft (Filter wie untertitel_spur.py)."""
    out = subprocess.run(["pgrep", "-f", "-i", "capcut"], capture_output=True, text=True).stdout.split()
    treffer, fremd = [], []
    for pid in out:
        cmd = subprocess.run(["ps", "-o", "command=", "-p", pid], capture_output=True, text=True).stdout.strip()
        (treffer if cmd.startswith("/Applications/") and "CapCut.app" in cmd else fremd).append(f"{pid} {cmd[:110]}")
    if fremd:  # Selbstpruefung: sichtbar machen, was die Roh-Probe faelschlich gezaehlt haette
        print(f"Hinweis: {len(fremd)} fremde Kommandozeile(n) mit dem Wort ignoriert (keine App): "
              + " | ".join(fremd[:3]))
    return treffer


def lade(pfad: Path):
    return json.loads(pfad.read_text(encoding="utf-8"))


def bindung(d):
    """(an_text, an_vorlage) — woran haengen die Text-Segmente?"""
    texte = {x["id"] for x in d.get("materials", {}).get("texts", [])}
    tmpl = {x["id"] for x in d.get("materials", {}).get("text_templates", [])}
    an_t = an_tt = 0
    for tr in d.get("tracks", []):
        if tr.get("type") != "text":
            continue
        for s in tr.get("segments", []):
            if s.get("material_id") in tmpl:
                an_tt += 1
            elif s.get("material_id") in texte:
                an_t += 1
    return an_t, an_tt


def muster_finden(ausser: str):
    """Juengster Draft, dessen Untertitel an ECHTEN Texten haengen."""
    kand = []
    for p in sorted(ROOT.iterdir()):
        f = p / "draft_info.json"
        if not f.is_file() or p.name == ausser:
            continue
        try:
            d = lade(f)
        except Exception:
            continue
        an_t, an_tt = bindung(d)
        if an_t >= 3 and an_tt == 0:
            kand.append((f.stat().st_mtime, p, an_t))
    if not kand:
        sys.exit("Kein Draft mit bearbeitbaren Untertiteln gefunden — --muster angeben.")
    kand.sort()
    return kand[-1][1], kand[-1][2]


def text_und_zeiten(d):
    """Wortlaut je Segment (in Segment-Reihenfolge) + Zeiten + Y."""
    tr = next((x for x in d["tracks"] if x.get("type") == "text"), None)
    if not tr:
        sys.exit("Der Draft hat keine Text-Spur.")
    texte = {x["id"]: x for x in d["materials"]["texts"]}
    tmpl = {x["id"]: x for x in d["materials"].get("text_templates", [])}
    raus = []
    for i, s in enumerate(tr["segments"]):
        wortlaut = None
        mid = s.get("material_id")
        if mid in texte:
            wortlaut = json.loads(texte[mid]["content"]).get("text", "")
        elif mid in tmpl:
            # Vorlage zeigt ueber text_info_resources auf ihr inneres Text-Material
            for tir in tmpl[mid].get("text_info_resources", []):
                inner = texte.get(tir.get("text_material_id"))
                if inner:
                    wortlaut = json.loads(inner["content"]).get("text", "")
                    break
        if wortlaut is None:
            # KEIN Reihenfolge-Notnagel: die Lernkartei (NACHTRAG CapCut 185) nennt das
            # Mapping ueber die Reihenfolge ausdruecklich als Fehlerquelle. Lieber
            # abbrechen als stillschweigend falsch zuordnen.
            sys.exit(f"Segment {i}: kein Wortlaut ueber text_info_resources auffindbar — "
                     "Abbruch statt Zuordnung ueber die Reihenfolge.")
        y = s.get("clip", {}).get("transform", {}).get("y", -0.62)
        raus.append((wortlaut, s["target_timerange"], y))
    return tr, raus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--muster")
    ap.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()

    ziel_dir = ROOT / a.draft
    if not ziel_dir.is_dir():
        # CapCut ersetzt "|" im Ordnernamen
        alt = ROOT / a.draft.replace(" | ", " - ")
        if alt.is_dir():
            ziel_dir = alt
        else:
            sys.exit(f"Draft nicht gefunden: {ziel_dir}")
    ziel = ziel_dir / "draft_info.json"
    geoeffnet = [x for x in ("template-2.tmp", "attachment_editing.json", "draft.extra",
                             "Resources", ".locked") if (ziel_dir / x).exists()]
    if geoeffnet == ["template-2.tmp"] and (ziel_dir / "draft_info.json.vor-entkopplung").exists():
        # Eigene Sidecar-Kopie (Sidecar-Regel unten), keine Oeffnungs-Spur — sonst warnte jedes --pruefen
        # nach der Entkopplung "LOESCHEN und neu bauen" (Endlos-Schleife). Geeicht 25.09.2026 an allen 45
        # Drafts dieses Macs: 28 von 28 von CapCut geoeffneten tragen zusaetzlich draft.extra/Resources/
        # attachment_editing.json; nur template-2.tmp + .vor-entkopplung = frisch entkoppelt (5 von 5).
        print("Hinweis: template-2.tmp stammt aus der eigenen Entkopplung — keine Oeffnungs-Spur.")
        geoeffnet = []
    if geoeffnet:
        print("WARNUNG: CapCut hat diesen Draft schon geoeffnet — Spuren:", ", ".join(geoeffnet))
        print("  Die Lernkartei (NACHTRAG CapCut 185) sagt: einen migrierten Draft NICHT flicken,\n"
              "  sondern LOESCHEN und jungfraeulich neu bauen, ALLE Patches VOR dem ersten Start.\n"
              "  Ein Patch hier wird beim naechsten Start aus template-2.tmp zurueckgerollt.")
    d = lade(ziel)
    an_t, an_tt = bindung(d)
    print(f"Draft „{ziel_dir.name}“: {an_t} Segmente an echtem Text, {an_tt} an Textvorlage")
    if an_tt == 0:
        print("Bereits bearbeitbar — nichts zu tun.")
        return
    if a.pruefen:
        print("NUR GEPRUEFT (--pruefen), nichts geschrieben.")
        return

    # WAECHTER: -f -i, NICHT -x. Gemessen am 22.09.2026 auf diesem Mac: bei laufendem
    # CapCut sieht "pgrep -f -i capcut" ACHT Prozesse (Hauptprozess, drei Renderer-,
    # zwei weitere Helfer, GPU-Helfer, parfait_crash_handler), "pgrep -x CapCut" nur
    # EINEN. Die Helfer halten Dateien weiter — wer nur -x prueft, schreibt in einen
    # belegten Draft. pgrep nimmt nur SICH selbst aus — jeden ANDEREN Prozess, dessen
    # Kommandozeile das Wort traegt, trifft -f mit. Gemessen am 25.09.2026 (VIS 016 EL):
    # ein Warte-Skript "capcut_draft016.sh" liess dieses Werkzeug mit 0 echten
    # App-Prozessen abbrechen. Darum zaehlen nur Treffer, deren Programm in
    # /Applications/…CapCut.app liegt — dieselbe Filterung wie untertitel_spur.py;
    # alle 8 echten Prozesse (auch parfait_crash_handler) liegen dort.
    if capcut_prozesse():
        sys.exit("CapCut laeuft (oder seine Helfer haengen nach) — es ueberschreibt Drafts.\n"
                 "Erst BEENDEN, dann WARTEN bis 'pgrep -f -i capcut' leer ist; die Helfer\n"
                 "brauchen nach dem Quit noch Sekunden. Notausgang: killall CapCut, dann\n"
                 "erneut pruefen.")
    if (ziel_dir / ".locked").exists():
        sys.exit(f"{ziel_dir}/.locked liegt noch da — CapCut hat den Draft belegt. Erst CapCut\n"
                 "beenden, dann die Datei entfernen, dann erneut.")

    muster_dir = (ROOT / a.muster) if a.muster else None
    if muster_dir is None:
        muster_dir, n = muster_finden(ziel_dir.name)
        print(f"Muster automatisch gewaehlt: „{muster_dir.name}“ ({n} bearbeitbare Untertitel)")
    m = lade(muster_dir / "draft_info.json")
    if bindung(m)[1]:
        sys.exit(f"Muster „{muster_dir.name}“ traegt selbst Textvorlagen — untauglich.")

    mtxt = m["materials"]["texts"][0]
    mtr = next(x for x in m["tracks"] if x.get("type") == "text")
    mseg = mtr["segments"][0]
    mids = {x["id"]: k for k, v in m["materials"].items() if isinstance(v, list)
            for x in v if isinstance(x, dict) and "id" in x}
    manim = None
    for ref in mseg.get("extra_material_refs", []):
        if mids.get(ref) == "material_animations":
            manim = next(x for x in m["materials"]["material_animations"] if x["id"] == ref)

    tr, posten = text_und_zeiten(d)
    shutil.copy(ziel, str(ziel) + ".vor-entkopplung")

    neue_t, neue_s, neue_a = [], [], []
    for i, (wortlaut, zr, y) in enumerate(posten):
        t = copy.deepcopy(mtxt)
        t["id"] = str(uuid.uuid4()).upper()
        c = json.loads(mtxt["content"])
        c["text"] = wortlaut
        for st in c.get("styles", []):
            st["range"] = [0, len(wortlaut)]
        t["content"] = json.dumps(c, ensure_ascii=False)
        t["base_content"] = wortlaut
        for k in ("recognize_text", "ssml_content"):
            if isinstance(t.get(k), str):
                t[k] = wortlaut
        if isinstance(t.get("words"), dict):
            t["words"] = {"end_time": [], "start_time": [], "text": []}
        # 185-Farbfix (Lernkartei, Quelle awms-09): 6-Hex parst CapCut 185 als
        # TRANSPARENT — die Untertitel waeren unsichtbar statt weiss.
        for feld, wert in (("text_color", "#ffffffff"), ("check_flag", 47),
                           ("use_effect_default_color", True)):
            t[feld] = wert
        if isinstance(t.get("shadow_color"), str) and len(t["shadow_color"]) == 7:
            t["shadow_color"] = t["shadow_color"] + "ff"
        t["subtitle_keywords_config"] = None   # Schablonen-Fox ist Stil-Preview-Futter
        t["subtitle_keywords"] = None
        neue_t.append(t)

        s = copy.deepcopy(mseg)
        s["id"] = str(uuid.uuid4()).upper()
        s["material_id"] = t["id"]
        s["target_timerange"] = zr
        s["render_index"] = 14000 + i
        s["clip"] = copy.deepcopy(mseg["clip"])
        s["clip"]["transform"] = {"x": 0.0, "y": y}
        refs = []
        if manim:
            an = copy.deepcopy(manim)
            an["id"] = str(uuid.uuid4()).upper()
            neue_a.append(an)
            refs.append(an["id"])
        s["extra_material_refs"] = refs
        neue_s.append(s)

    alt_refs = {r for s in tr["segments"] for r in s.get("extra_material_refs", [])}
    d["materials"]["texts"] = neue_t
    d["materials"]["text_templates"] = []
    ma = d["materials"].get("material_animations", [])
    d["materials"]["material_animations"] = [x for x in ma if x.get("id") not in alt_refs] + neue_a
    tr["segments"] = neue_s
    inhalt = json.dumps(d, ensure_ascii=False)
    # DIE SIDECAR-REGEL — der Grund, warum der erste Versuch im Lauf VIS 010 EL kippte:
    # CapCut haelt je Draft DREI Dateien mit demselben Inhalt (draft_info.json,
    # draft_info.json.bak, template-2.tmp). Wer nur die erste umstellt, laesst die
    # Vorlagen in den anderen beiden stehen — CapCut stellt beim naechsten Start daraus
    # wieder her, byte-genau auf den alten Stand. In den Drafts, die nachweislich
    # editierbar GEBLIEBEN sind (VIS 004/005/006 EL), steht die Entkopplung in allen
    # drei Dateien. Gemessen und gemeldet von den Schwester-Sessions levert-awms-b1
    # und levert-awms-ce, 21.09.2026.
    for name in ("draft_info.json", "draft_info.json.bak"):
        (ziel_dir / name).write_text(inhalt, encoding="utf-8")
    tmps = list(ziel_dir.glob("template-*.tmp"))
    for tmp in tmps:
        tmp.write_text(inhalt, encoding="utf-8")
    if not tmps:
        (ziel_dir / "template-2.tmp").write_text(inhalt, encoding="utf-8")

    # --- Gegenprobe: schreibt nur, was es auch belegen kann ---
    p = lade(ziel)
    an_t2, an_tt2 = bindung(p)
    texte = {x["id"]: x for x in p["materials"]["texts"]}
    tr2 = next(x for x in p["tracks"] if x.get("type") == "text")
    ab_zeit = sum(1 for s, (_, zr, _) in zip(tr2["segments"], posten)
                  if s["target_timerange"] != zr)
    ab_text = sum(1 for s, (w, _, _) in zip(tr2["segments"], posten)
                  if json.loads(texte[s["material_id"]]["content"])["text"] != w)
    fehlt = 0
    for x in texte.values():
        for st in json.loads(x["content"]).get("styles", []):
            pth = (st.get("font") or {}).get("path")
            if pth and not os.path.exists(pth):
                fehlt += 1
    print(f"umgestellt: {an_t2} Segmente an echtem Text, {an_tt2} an Textvorlage")
    print(f"Gegenprobe: Zeit-Abweichungen {ab_zeit} · Wortlaut-Abweichungen {ab_text} · "
          f"fehlende Schriften {fehlt}")
    if an_tt2 or ab_zeit or ab_text or fehlt:
        for name in ("draft_info.json", "draft_info.json.bak", "template-2.tmp"):
            shutil.copy(str(ziel) + ".vor-entkopplung", ziel_dir / name)
        sys.exit("ROT — alle drei Dateien auf .vor-entkopplung zurueckgerollt.")
    print("GRUEN in allen drei Dateien. Sicherung:", str(ziel) + ".vor-entkopplung")
    print("PFLICHT: nach dem CapCut-Neustart ERNEUT mit --pruefen gegenpruefen —\n"
          "genau dort ist der erste Versuch im Lauf VIS 010 EL gekippt.")
    print("Der Stil kommt jetzt aus dem Muster (Farbe/Look setzt Viktor in CapCut).")
    print("CapCut NEU STARTEN — es liest Drafts nur beim Start.")


if __name__ == "__main__":
    main()
