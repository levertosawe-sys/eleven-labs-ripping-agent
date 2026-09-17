#!/usr/bin/env python3
"""Stimm-Casting: Bibliothek filtern, Finalisten mit der Testzeile erzeugen, Variation messen.

Setzt die Filterkette und die Messung der SKILL.md um. CWD = Pipeline-Ordner.
  kandidaten --gender male --age middle_aged            → _work/cast_kandidaten.json (Top 10)
  messen --text "<Testzeile>" [--fenster 8.4]           → Takes je Finalist + F0-Variation
Winner wird NICHT automatisch ins Register geschrieben — die Session prüft die
Tabelle gegen das Band (25–35 %) und schreibt die Register-Zeile selbst.
"""
import argparse, json, os, subprocess, sys, urllib.request
from pathlib import Path
import numpy as np

def key():
    for pfad in (Path.home()/".config"/"awms"/".env", Path.home()/".config"/"leichtkraut"/".env"):
        if pfad.exists():
            for z in pfad.read_text().splitlines():
                if z.startswith("ELEVENLABS_API_KEY="): return z.split("=",1)[1].strip()
    sys.exit("ELEVENLABS_API_KEY fehlt")

GUT_DESK = {"confident","pleasant","casual","crisp","upbeat","friendly","warm","professional","deep","intense"}
BOESE_NAME = ("meditation","asmr","sleep","schlaf")

def cmd_kandidaten(a):
    k=key(); alle=[]; seite=0
    while True:
        url=(f"https://api.elevenlabs.io/v1/shared-voices?page_size=100&language=de"
             f"&gender={a.gender}&page={seite}")
        d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"xi-api-key":k}),timeout=60))
        alle+=d.get("voices",[])
        if not d.get("has_more") or seite>=6: break
        seite+=1
    n0=len(alle)
    alter={a.age,"middle-aged" if a.age=="middle_aged" else a.age}
    alle=[v for v in alle if v.get("age") in alter]
    n1=len(alle)
    alle=[v for v in alle if not any(b in v.get("name","").lower() for b in BOESE_NAME)]
    alle=[v for v in alle if v.get("descriptive") not in ("calm","chill","gentle","meditative","soothing")]
    n2=len(alle)
    def rang(v):
        uc={"advertisement":0,"social_media":1,"conversational":2,"informative_educational":3}.get(v.get("use_case"),9)
        dk=0 if v.get("descriptive") in GUT_DESK else 1
        return (uc, dk, -(v.get("cloned_by_count") or 0))
    alle.sort(key=rang)
    top=alle[:10]
    json.dump([{ "voice_id":v["voice_id"],"name":v["name"],"age":v.get("age"),
                 "use_case":v.get("use_case"),"descriptive":v.get("descriptive"),
                 "accent":v.get("accent"),"cloned_by":v.get("cloned_by_count")} for v in top],
              open("_work/cast_kandidaten.json","w"), ensure_ascii=False, indent=1)
    print(f"{n0} Stimmen → {n1} nach Alter → {n2} nach Ausschluss → Top {len(top)} nach Register:")
    for v in top: print(f"  {v['name']:28s} {v.get('use_case','?'):22s} {v.get('descriptive','?'):12s} {v['voice_id']}")

def f0_variation(wav):
    raw=subprocess.run(["ffmpeg","-v","error","-i",wav,"-ac","1","-ar","16000","-f","f32le","-"],
                       capture_output=True).stdout
    x=np.frombuffer(raw,dtype=np.float32); sr=16000
    fen=int(0.040*sr); f0s=[]
    for a0 in range(0,len(x)-fen,fen):
        w=x[a0:a0+fen]
        if float(np.sqrt((w**2).mean()))<0.01: continue   # Stille überspringen
        w=w-w.mean(); c=np.correlate(w,w,mode="full")[fen-1:]
        lo,hi=int(sr/300),int(sr/70)
        if hi>=len(c): continue
        lag=lo+int(np.argmax(c[lo:hi]))
        if c[lag]>0.3*c[0]: f0s.append(sr/lag)
    if len(f0s)<10: return None,0
    f0s=np.array(f0s)
    return float(f0s.std()/f0s.mean()*100), len(f0s)

def cmd_messen(a):
    k=key(); kand=json.load(open("_work/cast_kandidaten.json"))
    os.makedirs("_work/cast",exist_ok=True)
    erg=[]
    for v in kand:
        mp3=f"_work/cast/{v['voice_id']}.mp3"
        if not os.path.exists(mp3):
            body={"text":a.text,"model_id":a.modell,"voice_settings":{"stability":0.5}}
            req=urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}?output_format=mp3_44100_128",
                data=json.dumps(body).encode(),method="POST",
                headers={"xi-api-key":k,"Content-Type":"application/json"})
            try:
                Path(mp3).write_bytes(urllib.request.urlopen(req,timeout=180).read())
            except Exception as e:
                erg.append({**v,"fehler":str(e)[:120]}); print(f"  {v['name']}: FEHLER {str(e)[:80]}"); continue
        var,nf=f0_variation(mp3)
        dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",mp3],
                                 capture_output=True,text=True).stdout.strip() or 0)
        rate=len(a.text.split())/dur if dur else 0
        erg.append({**v,"variation":round(var,1) if var else None,"dauer":round(dur,2),
                    "wps":round(rate,2),"im_band":bool(var and 25<=var<=35),
                    "passt_fenster":dur<=a.fenster*1.15})
        print(f"  {v['name']:28s} Var {var and round(var,1)} % · {dur:.1f}s · {rate:.2f} W/s")
    erg.sort(key=lambda e:(not e.get("im_band",False), -(e.get("variation") or 0)))
    json.dump(erg,open("_work/cast_messung.json","w"),ensure_ascii=False,indent=1)
    print("→ _work/cast_messung.json (sortiert: Band zuerst, dann Variation)")

ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
c=sub.add_parser("kandidaten"); c.add_argument("--gender",required=True); c.add_argument("--age",default="middle_aged")
m=sub.add_parser("messen"); m.add_argument("--text",required=True); m.add_argument("--fenster",type=float,default=8.4); m.add_argument("--modell",default="eleven_v3")
a=ap.parse_args()
{"kandidaten":cmd_kandidaten,"messen":cmd_messen}[a.cmd](a)
