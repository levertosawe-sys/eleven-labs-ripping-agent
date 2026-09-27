#!/usr/bin/env python3
"""Clip-Karte der Speaking-Kette (Verallgemeinerung der Projekt-Ports 006/007).

CWD = Pipeline-Ordner des Projekts (brands/<Brand>/<NNN> EL/; Laeufe vor dem 02.09.2026: <NNN> SP).
  bau                 → Szenen zerlegen (scene>0,30), EN-Wörter zuordnen, 2 Frames je Clip
  merge <besch.json>  → Augen-Beschreibungen anheften → _pipeline/clip_karte.json
Die Beschreibung macht die KI mit EIGENEN Augen (Kontakt-Sheets) — kein Gemini fürs Bild.
"""
import json, os, re, subprocess, sys

BASIS = os.getcwd()
# Reihenfolge nach INHALT, nicht nach Namen: bild_basis.mp4 ist die reparierte Bildbasis
# (Original + Vmake nur im Untertitel-Band). Wo sie existiert, ist sie die Wahrheit —
# vmake_cleaned.mp4 kann Schaden ausserhalb des Bands tragen (VIS 001 EL, 18.09.2026).
for _k in ("_work/bild_basis.mp4", "_work/vmake_cleaned.mp4", "_work/source.mp4"):
    SRC = f"{BASIS}/{_k}"
    if os.path.exists(SRC): break
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
szenen_treffer = len(ts) - 1

# Zwei weitere Erkenner, beide auf 90x160 Grau (sp-learnings 9 und 21):
#  (a) Nachbar-Frame-Differenz > 18  -> HARTE Schnitte, die scene>0,30 auf einfarbigen
#      Ads verschluckt (durchgehend rotes 3D, rosa Studio -> 40-Sekunden-"Clips").
#  (b) Differenz ueber 15 Frame (0,5 s) > 18 -> WEICHE Blenden. Eine Blende verteilt die
#      Aenderung auf 10-20 Frames; je Nachbarpaar bleiben 5-8 Punkte, also unter jeder
#      Sprung-Schwelle, ueber den halben Sekundenabstand sind es 20-60.
import numpy as np
GRAU = f"{BASIS}/_work/clips/grau.npy"
if os.path.exists(GRAU):
    F = np.load(GRAU)
else:
    BW, BH = 90, 160
    roh = subprocess.run(["ffmpeg","-v","error","-i",SRC,"-vf",f"scale={BW}:{BH}",
                          "-pix_fmt","gray","-f","rawvideo","-"], capture_output=True).stdout
    nf = len(roh) // (BW*BH)
    F = np.frombuffer(roh[:nf*BW*BH], np.uint8).reshape(nf, BH, BW).astype(np.int16)
    np.save(GRAU, F)
# FPS aus dem VIDEO-Strom, nie aus DUR: DUR ist die Container-Dauer (ffprobe format), und die
# richtet sich nach der laengeren Spur — bei Quellen, deren Ton das Bild ueberragt, wurden die
# Schnitte sonst um DUR/Bilddauer zu spaet gesetzt (VIS 021 EL, 25.09.2026: Ton 65,734 s gegen
# 1968 Frames = 65,600 s → +0,13 s bei 64 s; das Ankleben < 0,8 s uebernahm jeweils die FALSCHE,
# spaetere Grenze).
_rf = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
                      "stream=r_frame_rate","-of","csv=p=0",SRC], capture_output=True, text=True).stdout.strip()
_z, _, _n = _rf.partition("/")
FPS = float(_z) / float(_n or 1) if _z else len(F) / DUR
VDUR = len(F) / FPS
SPAN = 15

def grenzen(d, schwelle, versatz, mindestabstand):
    raus = []; letzt = -10**9
    for i in np.where(d > schwelle)[0]:
        if i - letzt > mindestabstand: raus.append(round((i + versatz) / FPS, 2))
        letzt = i
    return raus

hart = grenzen(np.abs(np.diff(F, axis=0)).mean(axis=(1,2)), 18, 1, 3)
weich = grenzen(np.abs(F[SPAN:] - F[:-SPAN]).mean(axis=(1,2)), 18, SPAN/2, int(0.6*FPS))
ts += hart + weich
print(f"Schnitte: {szenen_treffer} aus scene>0,30 · {len(hart)} harte (Nachbar-Diff>18) · "
      f"{len(weich)} weiche Blenden ({SPAN}-Frame-Diff>18)")

# Selbstpruefung der Zeitachse: harte Schnitte (Frame-Index / FPS) und ffmpeg-Szenenschnitte
# (pts_time) messen dieselben Kanten — liegen sie mehr als 1,5 Frames auseinander, stimmt die
# Zeitachse nicht, und jede Clip-Grenze waere verschoben. Dann abbrechen statt still weiterbauen.
# Je HARTEM Schnitt der naechste Szenenschnitt (nicht umgekehrt: zwei echte Szenenschnitte
# 3 Frames auseinander — Blitz — behalten beim harten Erkenner nur den ersten, VIS 021 EL 6,83/6,93 s).
_szene = ts[1:szenen_treffer + 1]
# Gemessen wird die SYSTEMATISCHE Drift (Median), nicht der Ausreisser: echte harte Spruenge ohne
# ffmpeg-Szenenschnitt gibt es (VIS 021 EL 18,33 s, Nachbar-Diff 21) — die sind kein Achsenfehler.
_abw = [min(abs(h - s) for s in _szene) for h in hart if _szene and min(abs(h - s) for s in _szene) < 0.2]
_med = float(np.median(_abw)) if _abw else 0.0
if len(_abw) >= 3 and _med > 1.0 / FPS:
    sys.exit(f"ABBRUCH Zeitachse: harte Schnitte liegen im Median {_med:.3f} s neben den Szenenschnitten "
             f"(FPS {FPS:.3f}, Bild {VDUR:.2f} s, Container {DUR:.2f} s) — FPS-/Dauer-Quelle pruefen.")
print(f"Zeitachse ok: FPS {FPS:.3f} · Bild {VDUR:.2f} s · Abweichung hart↔Szene Median "
      f"{_med*1000:.0f} ms ({len(_abw)} Paare)")
ts.append(VDUR); ts = sorted(set(t for t in ts if t <= VDUR))
clips = []
for a, b in zip(ts, ts[1:]):
    if clips and b - a < 0.8: clips[-1][1] = b   # Blitz-Fehltrigger und Doppel-Treffer ankleben
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
# Beschriftung per PIL statt ffmpeg-drawtext: drawtext braucht Fontconfig und scheitert auf
# diesem Mac STILL ("Cannot load default config file") — die Frames kamen dann ohne Clip-Nummer
# heraus, und wer 88 Clips beschreibt, verzaehlt sich ohne Beschriftung (VIS 001 EL, 18.09.2026).
try:
    from PIL import Image, ImageDraw
    PIL_DA = True
except ImportError:
    PIL_DA = False
    print("HINWEIS: PIL fehlt — Frames bleiben unbeschriftet")
for k in karte:
    for tag, t in (("a", k["t0"] + min(0.3, k["dauer"] * 0.2)), ("b", (k["t0"] + k["t1"]) / 2)):
        ziel = f"{BASIS}/_work/clips/frames/c{k['clip']:03d}{tag}.jpg"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{t:.2f}","-i",SRC,"-frames:v","1",
                        "-vf","scale=200:-2","-q:v","5",ziel], check=True)
        if PIL_DA:
            lbl = f"C{k['clip']} {int(k['t0'])//60}:{int(k['t0'])%60:02d}-{int(k['t1'])//60}:{int(k['t1'])%60:02d}"
            im = Image.open(ziel).convert("RGB"); d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 4 + 6 * len(lbl), 16], fill=(0, 0, 0))
            d.text((3, 3), lbl, fill=(255, 255, 255))
            im.save(ziel, quality=85)
print("Frames fertig:", len(os.listdir(f"{BASIS}/_work/clips/frames")))
