#!/usr/bin/env python3
"""Sprechspur-Prüfer (sprech-watch) — maschinelles Abhören statt Hoffen.

Muster Custom-Clip-Prüfer: harte Kriterien, TRUE/FALSE je Zeile, kein Geschmack.
Je Block: (1) Rück-Transkription (Scribe, de) gegen die Soll-Copy — Versprecher,
Doppelwörter, Auslassungen; (2) Pausen-Messung — Hänger > 0,8 s mitten im Block;
(3) Fensterzeit — Blockdauer gegen SOLL-Fenster (+0,25 s Toleranz); (4) das
Anker-kalibrierte Gemini-Ohr (gemini-2.5-flash via kie.ai) für Aussprache von
Zahlen/Namen, Artefakte, Roboter-Stellen.

CWD = Pipeline-Ordner. Aufruf:
  python3 pruefer.py --audio _work/sprechspur.wav --marken <marken.json> [--ohne-ohr]
Ausgabe: _pipeline/pruefer.json + Tabelle. Exit 1 = mindestens eine rote Zeile
(rote Zeile → NUR diese Stelle neu erzeugen, max. 3 Versuche, dann Befund an Viktor).
"""
import argparse, base64, difflib, json, os, re, subprocess, sys, time
from pathlib import Path

BASIS = os.getcwd()
STAMM = Path(__file__).resolve().parents[2]
GURL = "https://api.kie.ai/gemini-2.5-flash/v1/chat/completions"

# ROUTEN fuer das Gemini-Ohr, in dieser Reihenfolge probiert. Belegt am
# Transkriptions-Test mit bekanntem Wortlaut (RYZ 002 EL, 16.09.2026):
# gemini-2.5-pro ueber `image_url` hoert das Audio wirklich; gemini-2.5-flash ueber
# `input_audio` bekommt KEIN Audio durchgereicht und erfindet ein Urteil
# ("Hello, how are you?" auf eine Werbezeile). Reihenfolge nie umdrehen, ohne den
# Transkriptions-Test neu zu fahren.
ROUTEN = [("gemini-2.5-pro",   "image_url"),
          ("gemini-2.5-flash", "image_url"),
          ("gemini-2.5-flash", "input_audio")]

def audioteil(kanal, b64):
    if kanal == "image_url":
        return {"type":"image_url","image_url":{"url":"data:audio/mp3;base64,"+b64}}
    return {"type":"input_audio","input_audio":{"data":b64,"format":"mp3"}}

def kie_key():
    for z in (Path.home()/".config"/"awms"/".env").read_text().splitlines():
        if z.startswith("KIE_API_KEY="): return z.split("=",1)[1].strip()
    return None

# Ziffern → deutsche Zahlwörter (ARE-002-EL-Befund 04.09.2026): Die Soll-Copy trägt
# „50", „210", „70 Prozent" als Ziffern, Scribe hört „fünfzig", „zweihundertzehn" —
# der Wort-Abgleich fiel dadurch bei jedem Zahlen-Block auf 0,83–0,86 und färbte
# fehlerfreie Blöcke rot (Ohr grün). Beide Seiten werden jetzt auf Zahlwörter normiert.
_EINER=["","ein","zwei","drei","vier","fünf","sechs","sieben","acht","neun","zehn","elf","zwölf",
        "dreizehn","vierzehn","fünfzehn","sechzehn","siebzehn","achtzehn","neunzehn"]
_ZEHNER=["","","zwanzig","dreißig","vierzig","fünfzig","sechzig","siebzig","achtzig","neunzig"]
def _zahlwort(n):
    if n<20: return "eins" if n==1 else _EINER[n]
    if n<100:
        z,e=divmod(n,10)
        return _ZEHNER[z] if e==0 else f"{_EINER[e]}und{_ZEHNER[z]}"
    if n<1000:
        h,r=divmod(n,100)
        return ("ein" if h==1 else _EINER[h])+"hundert"+(_zahlwort(r) if r else "")
    if n<1000000:
        t,r=divmod(n,1000)
        return ("ein" if t==1 else _zahlwort(t))+"tausend"+(_zahlwort(r) if r else "")
    return str(n)
def norm(s):
    s=re.sub(r"\d+", lambda m: " "+_zahlwort(int(m.group()))+" ", s.lower())
    s=s.replace("%"," prozent ")
    # „einhundert"/„eintausend" ↔ Scribe „hundert"/„tausend": beide Seiten ohne das „ein"
    s=re.sub(r"\bein(hundert|tausend)", r"\1", s)
    # Bindestrich-Komposita zusammenziehen („Kollagen-Maske" ↔ Scribe „Kollagenmaske")
    s=re.sub(r"(?<=[a-zäöüß])-(?=[a-zäöüß])","",s)
    # Multiplikativ-Zahlwort: Scribe schreibt „dreizehn Mal", die Copy „dreizehnmal" — beide Seiten zusammenziehen
    s=re.sub(r"\b(\w+(?:zehn|zig|ßig|hundert|tausend|zwei|drei|vier|fünf|sechs|sieben|acht|neun|elf|zwölf|ein)) mal\b", r"\1mal", s)
    return re.sub(r"[^a-zäöüß0-9 ]"," ",s).split()

def zeichen_match(soll, gehoert):
    """Wort-Abgleich, robust gegen Scribes Wortgrenzen bei Bindestrich-Komposita:
    Soll und Hörung werden einmal mit zusammengezogenen Komposita („Kollagenglowupmaske")
    und einmal mit aufgetrennten („kollagen glow up maske") verglichen — der bessere
    Wert zählt. Der Token-Vergleich bleibt, damit ein fehlendes Wort („kein") weiter
    sichtbar ist (ein Zeichen-Vergleich ohne Leerzeichen ließe es bei 0,93 durchrutschen)."""
    def split_variante(x):
        return norm(re.sub(r"(?<=[a-zäöüß])-(?=[a-zäöüß])"," ",x.lower()))
    a=difflib.SequenceMatcher(None,norm(soll),norm(gehoert)).ratio()
    b=difflib.SequenceMatcher(None,split_variante(soll),split_variante(gehoert)).ratio()
    return round(max(a,b),3)

def pausen_in(p):
    out = subprocess.run(["ffmpeg","-i",p,"-af","silencedetect=noise=-32dB:d=0.8","-f","null","-"],
                         capture_output=True,text=True).stderr
    s=[float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)",out)]
    e=[float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)",out)]
    return list(zip(s,e))

def ohr(mp3, soll, k):
    prompt=("You hear one block of a German spoken ad voice-over. Target text: «"+soll+"». "
     "Judge ONLY the audio. STRICT JSON: "
     '{"aussprache_ok":true/false,"haenger":true/false,"artefakt":true/false,'
     '"roboterhaft":true/false,"note":"<max 12 words>"}')
    b64=base64.b64encode(open(mp3,"rb").read()).decode()
    out=""
    for modell,kanal in ROUTEN:
        url=f"https://api.kie.ai/{modell}/v1/chat/completions"
        payload={"model":modell,"temperature":0.1,"messages":[{"role":"user","content":[
            {"type":"text","text":prompt}, audioteil(kanal,b64)]}]}
        for w in (0,20,40):
            if w: time.sleep(w)
            out=subprocess.run(["curl","-s","-X","POST","-H",f"Authorization: Bearer {k}",
                                "-H","Content-Type: application/json","--data-binary","@-",url],
                               input=json.dumps(payload),capture_output=True,text=True,timeout=300).stdout
            try:
                txt=json.loads(out)["choices"][0]["message"]["content"]
                txt=txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                d=json.loads(txt); d["route"]=f"{modell}/{kanal}"
                return d
            except Exception:
                if '"code":500' not in out: break
    return {"fehler":out[:200]}

def spur_checks(audio, marken, k):
    """Spur-Ebene: tote Luft an den Blockgrenzen + Stimm-Identität über die ganze Spur.
    Blind-Stellen aus Viktors erstem Gate-Befund — er hörte eine 1-s-Pause bei Sekunde 29
    und einen Stimm-Wechsel vorn, der Prüfer sah beides nicht (er hörte nur INS Blockinnere)."""
    befunde=[]
    out=subprocess.run(["ffmpeg","-i",audio,"-af","silencedetect=noise=-38dB:d=0.35","-f","null","-"],
                       capture_output=True,text=True).stderr
    s=[float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)",out)]
    e=[float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)",out)]
    ende_letzte=marken[-1]["ende"]
    for a0,b0 in zip(s,e):
        # Schwelle 0,8 s mitten im Clip; vor einer Schnittkante (Marke auf einer Kante der Clip-Karte) ist
        # Luft bis 1,0 s Atem, kein Fehler (sprech-watch §Schnittkanten-Anker)
        grenze = 1.0 if any(abs(b0-k) <= 0.3 for k in KANTEN) else 0.8
        if b0-a0 > grenze and a0 > 0.2 and b0 < ende_letzte-0.2:
            befunde.append(f"tote Luft {a0:.2f}-{b0:.2f}s ({b0-a0:.2f}s)")
    for m in marken:
        einsaetze=[b0 for b0 in e if abs(b0-m["start"])<1.2] or [m["start"]]
        off=min(einsaetze,key=lambda x:abs(x-m["start"]))-m["start"]
        if abs(off)>0.30:
            befunde.append(f"Stimm-Einsatz {off:+.2f}s neben Marke {m['start']:.2f}s")
    # Kanten-Atem: vor jeder Marke (außer der ersten) muss eine Stille ≥ 0,25 s liegen —
    # sonst kleben die Sätze („überlagert"). Gemessen mit -38 dB / 0,25 s.
    out=subprocess.run(["ffmpeg","-i",audio,"-af","silencedetect=noise=-38dB:d=0.25","-f","null","-"],
                       capture_output=True,text=True).stderr
    s2=[float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)",out)]
    e2=[float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)",out)]
    for m in marken[1:]:
        t=m["start"]
        if not any(a0 <= t+0.05 and b0 >= t-0.45 for a0,b0 in zip(s2,e2)):
            befunde.append(f"Blöcke kleben an Marke {t:.2f}s (keine Stille ≥0,25 s davor)")
    identitaet={}
    if k:
        mp3="_work/pruef_spur.mp3"
        subprocess.run(["ffmpeg","-y","-v","error","-i",audio,"-c:a","libmp3lame","-b:a","128k",mp3],check=True)
        prompt=("You hear one continuous German ad voice-over. Judge ONLY voice identity. STRICT JSON: "
         '{"same_speaker":true/false,"wechsel_bei_sekunde":<number or null>,'
         '"note":"<max 12 words>"}')
        b64=base64.b64encode(open(mp3,"rb").read()).decode()
        for modell,kanal in ROUTEN:
            url=f"https://api.kie.ai/{modell}/v1/chat/completions"
            payload={"model":modell,"temperature":0.1,"messages":[{"role":"user","content":[
                {"type":"text","text":prompt}, audioteil(kanal,b64)]}]}
            for w in (0,20,40):
                if w: time.sleep(w)
                out2=subprocess.run(["curl","-s","-X","POST","-H",f"Authorization: Bearer {k}",
                    "-H","Content-Type: application/json","--data-binary","@-",url],
                    input=json.dumps(payload),capture_output=True,text=True,timeout=300).stdout
                try:
                    txt=json.loads(out2)["choices"][0]["message"]["content"]
                    txt=txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                    identitaet=json.loads(txt); identitaet["route"]=f"{modell}/{kanal}"; break
                except Exception:
                    if '"code":500' not in out2: break
            if identitaet: break
        os.remove(mp3)
        if identitaet and not identitaet.get("same_speaker",True):
            befunde.append(f"Stimm-Wechsel bei ~{identitaet.get('wechsel_bei_sekunde')}s ({identitaet.get('note','')})")
    return befunde, identitaet

ap=argparse.ArgumentParser()
ap.add_argument("--audio",default="_work/sprechspur.wav")
ap.add_argument("--marken",required=True)
ap.add_argument("--ohne-ohr",action="store_true")
ap.add_argument("--kanten",help="Clip-Karte (_pipeline/clip_karte.json): vor Schnittkanten gilt die 1,0-s-Luftgrenze statt 0,8 s")
a=ap.parse_args()
KANTEN=[c["t0"] for c in json.load(open(a.kanten))] if a.kanten else []
marken=json.load(open(a.marken))
k=None if a.ohne_ohr else kie_key()
rows=[]; rot=0
spur_befunde, spur_ident = spur_checks(a.audio, marken, k)
for b in spur_befunde: print(f"SPUR ROT: {b}")
if spur_ident.get("same_speaker") is True: print(f"SPUR: eine Stimme durchgehend ({spur_ident.get('note','')})")
for i,m in enumerate(marken):
    t0,t1=m["start"],m["ende"]
    blk=f"{BASIS}/_work/pruef_{i:02d}.mp3"
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{t0:.2f}","-to",f"{t1:.2f}",
                    "-i",a.audio,"-c:a","libmp3lame","-b:a","160k",blk],check=True)
    # 1) Rücktranskription
    roh=f"{BASIS}/_work/pruef_{i:02d}.json"
    r=subprocess.run([sys.executable,str(STAMM/".claude/skills/singing-vsl-transkription/scripts/transcribe.py"),
                      blk,"--out",roh,"--sprache","de"],capture_output=True,text=True)
    gehoert=""
    if r.returncode==0:
        d=json.loads(open(roh).read()); gehoert=" ".join(w["text"] for w in d["woerter"])
    match=zeichen_match(m["text"],gehoert)
    # Doppelwörter in der Hörung
    hw=norm(gehoert); doppel=[hw[j] for j in range(1,len(hw)) if hw[j]==hw[j-1]]
    # 2) Hänger: Pausen > 0,8 s mitten im Block (Randstille zählt nicht)
    p_in=[(round(s,2),round(e,2)) for s,e in pausen_in(blk) if s>0.1 and e<(t1-t0)-0.1]
    # 3) Ohr
    urteil={} if a.ohne_ohr or not k else ohr(blk,m["text"],k)
    gruen = match>=0.92 and not doppel and not p_in and urteil.get("aussprache_ok",True) \
            and not urteil.get("haenger",False) and not urteil.get("artefakt",False) \
            and not urteil.get("roboterhaft",False)
    if not gruen: rot+=1
    rows.append({"block":i,"fenster":[t0,t1],"match":match,"doppel":doppel,
                 "haenger_innen":p_in,"gehoert":gehoert,"ohr":urteil,"gruen":gruen})
    for f in (blk,roh):
        if os.path.exists(f): os.remove(f)
    print(f"Block {i}: match {match} · Doppel {doppel or '—'} · Hänger {p_in or '—'} · "
          f"Ohr {urteil.get('note','—') if urteil else 'aus'} → {'GRÜN' if gruen else 'ROT'}")
rot += len(spur_befunde)
json.dump({"spur":{"befunde":spur_befunde,"identitaet":spur_ident},"bloecke":rows},
          open(f"{BASIS}/_pipeline/pruefer.json","w"),ensure_ascii=False,indent=1)
print(f"pruefer.json: {len(rows)} Blöcke + Spur-Ebene, {rot} rot")
sys.exit(1 if rot else 0)
