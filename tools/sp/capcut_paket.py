#!/usr/bin/env python3
"""SP — CapCut-Übergabepaket der Speaking-Kette (Ableger von tools/sa/capcut_paket.py).

Schnürt final.mp4 + Mitlese-Häppchen + fette Gestaltungs-Captions + gevendorte
CapCut-Skripte in EINEN Ordner und druckt den fertigen Ein-Prompt fürs Mac-Fenster.

Usage:
  python3 tools/sp/capcut_paket.py --projekt "001 EL" --brand "ARE - Areum" \
      --name "ARE 001 EL | 02.09.2026" --ip <server-ip>
"""
import argparse, json, os, re, shutil, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL = f"{BASE}/.claude/skills/sa-captions-capcut"
MAC_ZIEL_BASIS = '$HOME/Desktop/CapCut-Pakete'
WERKSTATT = "/root/AWMS/Longform-Singing-VSL-Agent"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projekt", required=True); ap.add_argument("--brand", required=True)
    ap.add_argument("--name", required=True); ap.add_argument("--ip", required=True, help="IP des Rechen-Servers, auf dem das Projekt liegt")
    a = ap.parse_args()
    nr = a.projekt.split()[0]
    P = f"{BASE}/brands/{a.brand}/{a.projekt}"; OUT = f"{P}/_capcut-paket"
    mp4 = f"{P}/_work/final.mp4"
    hae = f"{P}/_pipeline/captions{nr}_haeppchen.json"
    fett = f"{P}/_pipeline/fette_captions.json"
    for p, was in ((mp4,"_work/final.mp4"),(hae,f"captions{nr}_haeppchen.json"),
                   (fett,"fette_captions.json"),(f"{P}/_work/vmake_cleaned.mp4","Vmake-Beleg")):
        if not os.path.exists(p): sys.exit(f"ABBRUCH: {was} fehlt")
    if os.path.getmtime(mp4) < os.path.getmtime(f"{P}/_work/vmake_cleaned.mp4"):
        sys.exit("ABBRUCH (Vmake-Gate): final.mp4 älter als vmake_cleaned.mp4")
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(f"{OUT}/assets", exist_ok=True)
    shutil.copy(mp4, OUT); shutil.copy(hae, OUT); shutil.copy(fett, OUT)
    shutil.copytree(f"{SKILL}/scripts", f"{OUT}/scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/draft_feinschliff.py", f"{OUT}/scripts/")
    shutil.copy(f"{SKILL}/assets/caption-stil-default.json", f"{OUT}/assets/")
    dauer = round(float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",mp4],capture_output=True,text=True).stdout.strip()),3)
    h=json.load(open(hae)); f=json.load(open(fett))
    json.dump({"video_dauer_s":dauer,"haeppchen":len(h),"fette_captions":len(f),
               "mp4":"final.mp4","capcut_projektname":a.name,
               "ton":"final.mp4 traegt den FERTIGEN Mix (Sprechspur + Original-Instrumental) — KEINE Musik-Spur hinzufuegen"},
              open(f"{OUT}/fakten.json","w"), indent=1)
    vorlage=f"{os.path.dirname(os.path.abspath(__file__))}/capcut_anleitung_vorlage.md"
    txt=open(vorlage,encoding="utf-8").read()
    for k,v in {"{NAME}":a.name,"{DAUER}":str(dauer),"{NHAE}":str(len(h)),"{NFETT}":str(len(f)),"{NR}":nr}.items():
        txt=txt.replace(k,v)
    open(f"{OUT}/ANLEITUNG-FUER-DIE-KI.md","w",encoding="utf-8").write(txt)
    OUT_MAC=f"{WERKSTATT}/brands/{a.brand}/{a.projekt}/_capcut-paket"
    slug=re.sub(r"-{2,}","-",re.sub(r"[^a-z0-9.]+","-",a.name.lower())).strip("-")
    prompt=f"""Hol dir das fertige CapCut-Paket vom AWMS-Server und pushe die Speaking-Ad in CapCut.

1) Paket holen:
   mkdir -p "{MAC_ZIEL_BASIS}"
   rsync -az --partial "root@{a.ip}:{OUT_MAC}/" "{MAC_ZIEL_BASIS}/capcut-{slug}/"

2) Dort ANLEITUNG-FUER-DIE-KI.md lesen und abarbeiten. Video, Ton und alle
   Caption-Timings sind fertig und maschinell abgenommen — NICHTS neu rechnen,
   NICHTS transkribieren. Du baust nur den CapCut-Draft (Anleitung Schritt 1-4).
   WICHTIG: final.mp4 trägt den fertigen Ton-Mix — keine Musik-Spur dazulegen.

3) CapCut-Projektname exakt: "{a.name}"
   Ad-Datei im Paket: final.mp4 ({dauer}s, {len(h)} Mitlese-Häppchen + {len(f)} fette Caption(s))

4) Wenn alles in CapCut liegt, den Marker auf dem Server setzen:
   ssh root@{a.ip} 'touch "{OUT_MAC}/CAPCUT-GEPUSHT"'
"""
    open(f"{OUT}/PROMPT-FUER-MAC.txt","w",encoding="utf-8").write(prompt)
    open(f"{P}/PROMPT-FUER-MAC.txt","w",encoding="utf-8").write(prompt)
    print(f"✅ Paket: {OUT} ({len(h)} Häppchen · {len(f)} fette · Video {dauer}s)")
    print(f"✅ Prompt-Datei: {P}/PROMPT-FUER-MAC.txt")
    print("\n"+"="*70+"\nEIN-PROMPT fürs Mac-Fenster:\n"+"="*70+"\n\n"+prompt+"="*70)

if __name__ == "__main__": main()
