#!/usr/bin/env python3
"""Abnahme der Speaking-Kette — Zahlen statt Gefühl, vor jedem „fertig".

Prüft: (1) Frame-Zahl Quelle vs. Final (Copy-Zweig: Gleichstand, ±1 Endframe durch
-shortest), (2) Dauer, (3) je Block die Startmarke: Kreuzkorrelation der
Sprechspur-Blöcke gegen die Final-Tonspur, Offset ≤ 0,25 s, (4) Loudness des
Finals im Band -17..-15 LUFS.

CWD = Pipeline-Ordner. Aufruf:
  python3 abnahme.py --marken <marken.json> [--final _work/final.mp4]
Exit 1 = eine Zahl steht nicht. Ergebnis: _pipeline/abnahme.json.
"""
import argparse, json, os, subprocess, sys
import numpy as np

BASIS = os.getcwd()
def wav(p, t0=None, t1=None, sr=16000):
    cmd=["ffmpeg","-v","error"]
    if t0 is not None: cmd+=["-ss",f"{t0:.2f}"]
    if t1 is not None: cmd+=["-to",f"{t1:.2f}"]
    cmd+=["-i",p,"-ac","1","-ar",str(sr),"-f","f32le","-"]
    raw=subprocess.run(cmd,capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32), sr

ap=argparse.ArgumentParser()
ap.add_argument("--marken",required=True)
ap.add_argument("--final",default="_work/final.mp4")
ap.add_argument("--sprechspur",default="_work/sprechspur.wav")
ap.add_argument("--quelle",default="_work/source.mp4")
a=ap.parse_args()
marken=json.load(open(a.marken))
befund={"checks":[]}; rot=0
def check(name, ok, wert):
    global rot
    befund["checks"].append({"check":name,"ok":bool(ok),"wert":wert})
    print(f"{'OK ' if ok else 'ROT'} {name}: {wert}")
    if not ok: rot+=1

def frames(p):
    return int(subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v:0",
        "-show_entries","stream=nb_read_frames","-of","csv=p=0",p],capture_output=True,text=True).stdout.strip() or 0)
fq,ff=frames(a.quelle),frames(a.final)
check("Frame-Zahl (Quelle vs Final, ±1)", abs(fq-ff)<=1, f"{fq} / {ff}")
def dauer(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",p],capture_output=True,text=True).stdout.strip())
check("Dauer (±0,2 s)", abs(dauer(a.quelle)-dauer(a.final))<=0.2, f"{dauer(a.quelle):.2f} / {dauer(a.final):.2f}")
fin,_=wav(a.final)
for i,m in enumerate(marken):
    t0,t1=m["start"],m["ende"]
    blk,sr=wav(a.sprechspur,t0,min(t1,t0+3))
    fen,_ = wav(a.final,max(0,t0-0.5),min(t1,t0+3)+0.5)
    if not len(blk) or not len(fen): check(f"Block {i} Startmarke", False, "kein Audio"); continue
    n=min(len(blk),len(fen))
    c=np.correlate(fen,blk[:n],mode="valid")
    off=(np.argmax(np.abs(c))/sr)-(0.5 if t0>=0.5 else t0)
    check(f"Block {i} Startmarke (±0,25 s)", abs(off)<=0.25, f"Offset {off*1000:.0f} ms")
out=subprocess.run(["ffmpeg","-i",a.final,"-af","loudnorm=print_format=json","-f","null","-"],
                   capture_output=True,text=True).stderr
try:
    lj=json.loads(out[out.rindex("{"):out.rindex("}")+1]); lufs=float(lj["input_i"])
    check("Loudness -17..-15 LUFS", -17<=lufs<=-15, f"{lufs:.1f} LUFS")
except Exception:
    check("Loudness messbar", False, "loudnorm-JSON nicht lesbar")
json.dump(befund,open(f"{BASIS}/_pipeline/abnahme.json","w"),ensure_ascii=False,indent=1)
print(f"abnahme.json: {len(befund['checks'])} Checks, {rot} rot")
sys.exit(1 if rot else 0)
