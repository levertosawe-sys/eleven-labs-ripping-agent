#!/usr/bin/env python3
"""Lip-Sync-Aufträge abarbeiten und die Einbau-Liste schreiben. Im Pipeline-Ordner des Projekts ausführen.

  python3 lipsync_lauf.py --basis <Bildbasis> [--nur name1,name2] [--parallel 0] [--trotzdem]
                          [--auftraege _pipeline/lipsync_auftraege.json] [--einbau _pipeline/lipsync_einbau.json]
                          [--workflow "Eleven Labs Ripping Agent"]

Je Auftrag aus lipsync_auftraege.json ({"name","f0","f1","dauer","audio"}):
  - vorhanden: _work/lipsync/<name>_lipsync.mp4 hat f1 − f0 Frames UND _work/lipsync/<name>.auftrag.json nennt dieselben
    f0/f1 (fehlt die Datei, zählt nur die Frame-Zahl) → übersprungen, kostet nichts.
  - offene taskId: liegt _work/lipsync/<name>_lipsync.mp4.task ohne Ausgabe → erst abholen (der Auftrag ist schon bezahlt).
  - sonst Ausschnitt (lipsync_schnitt.py) → kie (lipsync_kie.py): „server busy" bis 5× im Abstand von 60 s, „Credits
    insufficient" bis 3× im Abstand von 120 s (Reservierungen paralleler Aufträge laufen aus). Keine Antwort in 1500 s →
    FEHLER mit Abhol-Befehl, nie neu einreichen (doppelt bezahlt).
Budget-Stopp: Übersteigen die Kosten der offenen Aufträge (8 kie-Credits je volle Sekunde, lite) den Kontostand oder ist der
Kontostand nicht lesbar, endet das Skript mit Exit 6, ohne etwas zu starten — außer mit --trotzdem.
--parallel 0 = automatisch: 3 gleichzeitig, wenn der Kontostand ≥ 2 × offene Kosten ist, sonst 1.
Verbrauch je erfolgreichem Auftrag → <AWMS>/.usage/direkt.jsonl (AWMS = erster Ordner nach oben mit workflows/). Fehlt er:
WARNUNG, dann aus _work/lipsync/<name>_lipsync.mp4.job.json (Feld creditsConsumed) von Hand nachbuchen.
Einbau-Liste = alle Aufträge mit gültiger Ausgabe; ein Neu-Lauf „<name>b" (auch c, d …) ersetzt dort seinen Erstlauf „<name>".
Ausgabe: je Auftrag „ok"/„vorhanden"/„FEHLER <Grund>", Schlusszeile „Einbau: N Einträge". Exit 1, sobald ein FEHLER dabei war.
"""
import argparse, datetime, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HIER = Path(__file__).resolve().parent; PY = sys.executable

def frames(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return int(r.stdout.strip())
    except ValueError: return -1

def usage_datei():
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / "workflows").is_dir(): return p / ".usage" / "direkt.jsonl"
    return None

def kontostand():
    r = subprocess.run([PY, str(HIER / "lipsync_kie.py"), "--pruefen"], capture_output=True, text=True)
    try: return float(r.stdout.rsplit(":", 1)[1].strip())
    except (IndexError, ValueError): return None

def gueltig(x):
    out = f"_work/lipsync/{x['name']}_lipsync.mp4"; meta = f"_work/lipsync/{x['name']}.auftrag.json"
    if not os.path.exists(out) or frames(out) != x["f1"] - x["f0"]: return False
    if os.path.exists(meta):
        m = json.load(open(meta))
        return m.get("f0") == x["f0"] and m.get("f1") == x["f1"]
    return True

def ersetzte(namen):
    return {n[:-1] for n in namen if len(n) > 1 and n[-1] in "bcdefgh" and n[:-1] in namen}

def eins(x, a, usage):
    n = x["name"]; out = f"_work/lipsync/{n}_lipsync.mp4"; soll = x["f1"] - x["f0"]; video = f"_work/lipsync/{n}_video.mp4"
    if gueltig(x): return n, "vorhanden", None
    task = out + ".task"
    if os.path.exists(task) and not os.path.exists(out):
        r = subprocess.run([PY, str(HIER / "lipsync_kie.py"), "--abholen", open(task).read().strip(), out, video], capture_output=True, text=True)
        with open(f"_work/lipsync/{n}.log", "a") as log: log.write(r.stdout + r.stderr)
        if r.returncode != 0: return n, "FEHLER", f"offene taskId nicht abholbar (Exit {r.returncode}): " + (r.stdout + r.stderr)[-200:]
    else:
        r = subprocess.run([PY, str(HIER / "lipsync_schnitt.py"), n, str(x["f0"]), str(x["f1"]), x.get("audio", "_work/sprechspur.wav"),
                            "--basis", a.basis], capture_output=True, text=True)
        if r.returncode != 0: return n, "FEHLER", "Ausschnitt: " + (r.stdout + r.stderr)[-300:]
        busy = knapp = 0
        while True:
            r = subprocess.run([PY, str(HIER / "lipsync_kie.py"), video, f"_work/lipsync/{n}_audio.wav", out, "lite"], capture_output=True, text=True)
            with open(f"_work/lipsync/{n}.log", "a") as log: log.write(r.stdout + r.stderr)
            if r.returncode == 0 and os.path.exists(out): break
            if r.returncode == 2 and busy < 5: busy += 1; time.sleep(60); continue
            if r.returncode == 3 and knapp < 3: knapp += 1; time.sleep(120); continue
            if r.returncode == 4: return n, "FEHLER", "keine Antwort in 1500 s — NICHT neu starten; nächster Aufruf holt die taskId ab"
            return n, "FEHLER", (r.stdout + r.stderr)[-300:]
    if os.path.exists(task): os.remove(task)
    cr = json.load(open(out + ".job.json")).get("creditsConsumed") if os.path.exists(out + ".job.json") else None
    if usage:
        usage.parent.mkdir(parents=True, exist_ok=True)
        with open(usage, "a") as f:
            f.write(json.dumps({"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "workflow": a.workflow,
                                "anbieter": "kie", "menge": cr, "notiz": f"{Path.cwd().name} Lip-Sync {n} ({x.get('dauer')} s, volcengine lite)"}) + "\n")
    fr = frames(out)
    if fr != soll: return n, "FEHLER", f"Ausgabe hat {fr} Frames statt {soll} — Audio-Länge von _work/lipsync/{n}_audio.wav prüfen"
    json.dump({"f0": x["f0"], "f1": x["f1"], "audio": x.get("audio")}, open(f"_work/lipsync/{n}.auftrag.json", "w"))
    return n, f"ok {fr}/{soll} Frames · {cr} Credits", None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nur", default=""); ap.add_argument("--parallel", type=int, default=0); ap.add_argument("--trotzdem", action="store_true")
    ap.add_argument("--basis", default="_work/bildbasis.mp4"); ap.add_argument("--auftraege", default="_pipeline/lipsync_auftraege.json")
    ap.add_argument("--einbau", default="_pipeline/lipsync_einbau.json"); ap.add_argument("--workflow", default="Eleven Labs Ripping Agent")
    a = ap.parse_args()
    if not os.path.exists(a.auftraege): sys.exit(f"FEHLER: {a.auftraege} fehlt — erst lipsync_bereiche.py laufen lassen")
    if not os.path.exists(a.basis): sys.exit(f"FEHLER: Bildbasis fehlt: {a.basis} (--basis angeben)")
    os.makedirs("_work/lipsync", exist_ok=True)
    auftr = json.load(open(a.auftraege)); nur = {s for s in a.nur.split(",") if s}
    offen = [x for x in auftr if (not nur or x["name"] in nur)]
    usage = usage_datei()
    if not usage: print("WARNUNG: kein AWMS-Ordner (workflows/) oberhalb gefunden — Verbrauch danach aus *.job.json nachbuchen")
    zu_bezahlen = [x for x in offen if not gueltig(x) and not os.path.exists(f"_work/lipsync/{x['name']}_lipsync.mp4.task")]
    kosten = sum(8 * int(x["dauer"]) for x in zu_bezahlen)
    k = kontostand() if zu_bezahlen else None
    if zu_bezahlen and not a.trotzdem and (k is None or kosten > k):
        print(f"BUDGET-STOPP: offene Kosten ≈ {kosten} Credits für {len(zu_bezahlen)} Aufträge · Kontostand {k if k is not None else 'unbekannt'}. "
              "Nichts gestartet — Entscheid des Nutzers (aufladen / Auswahl per --nur / ohne Lip-Sync).")
        sys.exit(6)
    par = a.parallel if a.parallel > 0 else (3 if (k is not None and k >= 2 * kosten) else 1)
    print(f"Offene Kosten ≈ {kosten} Credits · Kontostand {k} → parallel {par}", flush=True)
    fehler = 0
    with ThreadPoolExecutor(max_workers=par) as ex:
        for n, status, grund in ex.map(lambda x: eins(x, a, usage), offen):
            print(n, status, grund or "", flush=True); fehler += status == "FEHLER"
    einbau = [{"f0": x["f0"], "f1": x["f1"], "datei": f"_work/lipsync/{x['name']}_lipsync.mp4", "name": x["name"]} for x in auftr if gueltig(x)]
    weg = ersetzte({e["name"] for e in einbau})
    einbau = sorted([e for e in einbau if e["name"] not in weg], key=lambda e: e["f0"])
    json.dump(einbau, open(a.einbau, "w"), indent=1)
    print(f"Einbau: {len(einbau)} Einträge → {a.einbau}" + (f" · {fehler} FEHLER" if fehler else ""))
    if fehler: sys.exit(1)

if __name__ == "__main__": main()
