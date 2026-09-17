#!/usr/bin/env python3
"""Clip-Karte der Speaking-Kette (Verallgemeinerung der Projekt-Ports 006/007).

CWD = Pipeline-Ordner des Projekts (brands/<Brand>/<NNN> EL/; Laeufe vor dem 02.09.2026: <NNN> SP).
  bau                 → Szenen zerlegen (scene>0,30), EN-Wörter zuordnen, 2 Frames je Clip
  merge <besch.json>  → Augen-Beschreibungen anheften → _pipeline/clip_karte.json
Die Beschreibung macht die KI mit EIGENEN Augen (Kontakt-Sheets) — kein Gemini fürs Bild.
"""
import json, os, re, subprocess, sys

BASIS = os.getcwd()
SRC = f"{BASIS}/_work/vmake_cleaned.mp4"
if not os.path.exists(SRC): SRC = f"{BASIS}/_work/source.mp4"
GRENZEN = f"{BASIS}/_work/clips/szenen_030.txt"

if len(sys.argv) > 2 and sys.argv[1] == "merge":
    karte = json.load(open(f"{BASIS}/_pipeline/clip_karte_roh.json"))
    b = {int(k): v for k, v in json.load(open(sys.argv[2])).items()}
    fehlen = [k["clip"] for k in karte if k["clip"] not in b]
    assert not fehlen, f"Beschreibungen fehlen für Clips {fehlen[:10]} — JEDER Clip braucht Augen"
    for k in karte:
        e = b[k["clip"]]
        k["bild"], k["typ"], k["uebergang"] = e["bild"], e.get("typ", "R"), bool(e.get("uebergang", False))
    json.dump(karte, open(f"{BASIS}/_pipeline/clip_karte.json", "w"), ensure_ascii=False, indent=1)
    print(f"clip_karte.json: {len(karte)} Clips mit Augen-Beschreibung"); sys.exit(0)

DUR = json.load(open(f"{BASIS}/_pipeline/sp_config.json"))["dur"]
os.makedirs(f"{BASIS}/_work/clips", exist_ok=True)
if not os.path.exists(GRENZEN):
    with open(GRENZEN, "w") as g:
        subprocess.run(["ffmpeg","-hide_banner","-i",SRC,"-vf","select='gt(scene,0.30)',showinfo","-f","null","-"],
                       stderr=g, check=True)
ts = [0.0]
for line in open(GRENZEN):
    m = re.search(r"pts_time:([\d.]+)", line)
    if m: ts.append(float(m.group(1)))
ts.append(DUR); ts = sorted(set(ts))
clips = []
for a, b in zip(ts, ts[1:]):
    if clips and b - a < 0.5: clips[-1][1] = b   # Blitz-Fehltrigger ankleben
    else: clips.append([a, b])
words = json.load(open(f"{BASIS}/_pipeline/source_words.json"))["words"]
karte = []
for i, (a, b) in enumerate(clips):
    ww = [w for w in words if a <= (w["s"] + w["e"]) / 2 < b]
    karte.append({"clip": i, "t0": round(a, 2), "t1": round(b, 2), "dauer": round(b - a, 2),
                  "en": " ".join(w["w"] for w in ww), "woerter": len(ww),
                  "endet_mit_satzende": bool(ww) and bool(re.search(r"[.!?]$", ww[-1]["w"]))})
json.dump(karte, open(f"{BASIS}/_pipeline/clip_karte_roh.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(karte)} Clips · Ø {DUR/len(karte):.1f}s · {sum(1 for k in karte if not k['en'])} ohne Text")
os.makedirs(f"{BASIS}/_work/clips/frames", exist_ok=True)
for k in karte:
    for tag, t in (("a", k["t0"] + min(0.3, k["dauer"] * 0.2)), ("b", (k["t0"] + k["t1"]) / 2)):
        lbl = f"C{k['clip']} {int(k['t0'])//60}\\:{int(k['t0'])%60:02d}-{int(k['t1'])//60}\\:{int(k['t1'])%60:02d}"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{t:.2f}","-i",SRC,"-frames:v","1",
                        "-vf",f"scale=200:-2,drawtext=text='{lbl}':x=4:y=4:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.7",
                        "-q:v","5",f"{BASIS}/_work/clips/frames/c{k['clip']:03d}{tag}.jpg"], check=True)
print("Frames fertig:", len(os.listdir(f"{BASIS}/_work/clips/frames")))
