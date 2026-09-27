"""Default-Caption-Stil auf ein exportiertes CapCut-Draft anwenden.

Warum es dieses Skript gibt: `draft_bauen` erbt seine Text-Optik von der
Schablone (neuestes echtes CapCut-Projekt). Nach einem CapCut-Update kann
deren Text-Template auf eine Store-Ressource zeigen, die es nicht mehr gibt
(Platzhalter-Pfad, fehlender Cache-Ordner) — dann trägt jeder Caption-Clip
ein rotes Nachlade-Icon und CapCut rendert den Demo-Text der Vorlage.
Dieses Skript ersetzt darum nach dem Export die Stil-Referenzen aller
Captions durch den eingefrorenen Default aus
`../assets/caption-stil-default.json` (ein von Viktor abgenommener Stil,
dessen Ressourcen real in CapCut existieren).

Chirurgische Regel (der eine Fehler, den dieses Skript nie machen darf):
`id`, `text_info_resources` und `aigc_config` eines text_templates-Eintrags
sind die PRO-CAPTION-VERDRAHTUNG (welches Template zeigt welchen Text).
Wer sie überschreibt, bekommt 220× den Demo-Text („Flexible editing …").
Ersetzt werden NUR die Ressourcen-/Stil-Felder.

Aufruf (CapCut vorher beenden — es überschreibt Drafts beim Beenden):
    python3 caption_stil.py "<Draft-Name>"        # z.B. "Singing VSL 009"
Erfolg = Ausgabe endet mit "OK: … Templates + … Texte umgestellt" je Datei
und einer Kontrollzeile "Bindungen individuell ✅".
"""
import copy, json, os, re, sys, glob, shutil

ROOT = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
DONOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "caption-stil-default.json")
KEEP = {"id", "text_info_resources", "aigc_config"}   # pro-Caption-Verdrahtung — nie anfassen


def apply(path, donor):
    d = json.load(open(path))
    mats = d.get("materials", {})
    tpls, txts = mats.get("text_templates", []), mats.get("texts", [])
    if not tpls and not txts:
        print(f"  {path}: keine Caption-Materialien — übersprungen")
        return
    shutil.copy(path, path + ".bak-stilfix")
    for t in tpls:
        for k, v in donor["template_felder"].items():
            if k in KEEP:
                continue
            t[k] = copy.deepcopy(v)
    for x in txts:
        c = json.loads(x["content"]) if isinstance(x.get("content"), str) else (x.get("content") or {})
        text = c.get("text", "")
        st = copy.deepcopy(donor["text_stil"])
        st["range"] = [0, len(text)]
        x["content"] = json.dumps({"styles": [st], "text": text}, ensure_ascii=False)
        for k, v in donor["texts_material_felder"].items():
            if k in x:
                x[k] = v
    s = json.dumps(d, ensure_ascii=False)
    json.loads(s)                      # Validierung VOR dem Schreiben
    open(path, "w").write(s)
    # Kontrolle: Verdrahtung noch individuell? (identische Bindungen = der Demo-Text-Fehler)
    if len(tpls) >= 2:
        same = json.dumps(tpls[0].get("text_info_resources")) == json.dumps(tpls[1].get("text_info_resources"))
        if same:
            shutil.copy(path + ".bak-stilfix", path)
            sys.exit(f"FEHLER: Bindungen wären identisch geworden — {path} aus Backup wiederhergestellt.")
    print(f"  OK: {len(tpls)} Templates + {len(txts)} Texte umgestellt — {path}")


def main():
    if len(sys.argv) != 2:
        sys.exit('Aufruf: python3 caption_stil.py "<Draft-Name>"')
    name = sys.argv[1]
    draft = os.path.join(ROOT, name)
    if not os.path.isdir(draft):
        # Der Draft-Ordner trägt den bereinigten Namen (capcut_export.sicherer_name:
        # „|" → „-"); der Aufruf darf den CapCut-Projektnamen nennen.
        alt_name = re.sub(r'[/\\:*?"<>|]', "-", name).strip()[:60]   # = capcut_export.sicherer_name
        if os.path.isdir(os.path.join(ROOT, alt_name)):
            draft = os.path.join(ROOT, alt_name)
        else:
            sys.exit(f"FEHLER: Draft nicht gefunden: {draft}")
    if os.popen("pgrep -x CapCut").read().strip():
        sys.exit("FEHLER: CapCut läuft — erst beenden (es überschreibt Drafts beim Beenden).")
    donor = json.load(open(DONOR))
    targets = [os.path.join(draft, "draft_info.json")] + \
              sorted(glob.glob(os.path.join(draft, "Timelines", "*", "draft_info.json")))
    found = [p for p in targets if os.path.isfile(p)]
    if not found:
        sys.exit(f"FEHLER: keine draft_info.json unter {draft}")
    for p in found:
        apply(p, donor)
    print("Bindungen individuell ✅ · Stil:", donor["template_felder"].get("name"),
          donor["template_felder"].get("resource_id"))


if __name__ == "__main__":
    main()
