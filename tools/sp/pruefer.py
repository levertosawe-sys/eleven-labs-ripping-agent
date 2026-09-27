#!/usr/bin/env python3
"""Sprechspur-Prüfer (sprech-watch) — maschinelles Abhören statt Hoffen.

Muster Custom-Clip-Prüfer: harte Kriterien, TRUE/FALSE je Zeile, kein Geschmack.
Je Block: (1) Rück-Transkription (Scribe, de) gegen die Soll-Copy — Versprecher,
Doppelwörter, Auslassungen; (2) Pausen-Messung — Hänger > 0,8 s mitten im Block;
(3) Fensterzeit — Blockdauer gegen SOLL-Fenster (+0,25 s Toleranz); (4) das
Anker-kalibrierte Gemini-Ohr (gemini-2.5-pro, Kanal image_url via kie.ai — die
tote input_audio-Route ist seit 19.09.2026 komplett raus) für Aussprache von
Zahlen/Namen, Artefakte, Roboter-Stellen. Jedes Ohr-Urteil ist WORDS-gebunden
(Modell transkribiert zuerst blind, Abgleich läuft lokal); Ausfall oder
Bindungs-Verfehlung = KEIN URTEIL — zählt nie als grün, nie als rot, wird
sichtbar gebucht (Viktors Ohr-Gesetz 19.09.2026).

CWD = Pipeline-Ordner. Aufruf:
  python3 pruefer.py --audio _work/sprechspur.wav --marken <marken.json> [--ohne-ohr]
Ausgabe: _pipeline/pruefer.json + Tabelle. Exit 1 = mindestens eine rote Zeile
(rote Zeile → NUR diese Stelle neu erzeugen, max. 3 Versuche, dann Befund an Viktor).
"""
import argparse, base64, difflib, json, os, re, subprocess, sys, time
from pathlib import Path

BASIS = os.getcwd()
STAMM = Path(__file__).resolve().parents[2]

# ROUTEN fuer das Gemini-Ohr, in dieser Reihenfolge probiert. Belegt am
# Transkriptions-Test mit bekanntem Wortlaut (RYZ 002 EL, 16.09.2026):
# gemini-2.5-pro ueber `image_url` hoert das Audio wirklich. Die tote Sprosse
# ("gemini-2.5-flash", "input_audio") wurde am 19.09.2026 auf Viktors Ohr-Gesetz
# ENTFERNT: input_audio traegt bei kie.ai KEIN Audio durch, das Modell erfindet
# souveraene Urteile ("Hello, how are you?" auf eine Werbezeile). Ein Ausfall
# darf nie wie eine Antwort aussehen — NIE wieder als Fallback einbauen.
ROUTEN = [("gemini-2.5-pro",   "image_url"),
          ("gemini-2.5-flash", "image_url"),
          # 25.09.2026 (VIS 019 EL): 2.5-pro 500 "server is currently being maintained",
          # 2.5-flash + 3-flash 422 "channel is not supported"; gemini-3-pro bestand
          # Nur-Text ("OK") UND Transkriptions-Test mit bekanntem Wortlaut (Bindung 1,0).
          # Dritte Sprosse, greift nur, wenn die geltende Route ausfaellt; WORDS-Bindung
          # gilt unveraendert je Aufruf.
          ("gemini-3-pro",     "image_url")]

# SICHERUNGSSCHALTER (25.09.2026, VIS 021 EL — wie emotions_karte.py): zwei Aufrufe in Folge
# nur HTTP 500 (je drei Versuche) = Route ausgefallen → fuer den Rest DIESES Laufs uebersprungen,
# sichtbar gemeldet. Jede echte Antwort setzt den Zaehler zurueck.
_NUR500 = {}

def _route_buchen(modell, fuenfhundert):
    if fuenfhundert == 3:
        _NUR500[modell] = _NUR500.get(modell, 0) + 1
        if _NUR500[modell] == 2:
            print(f"[ohr] {modell}: zwei Aufrufe in Folge nur HTTP 500 — Route fuer den Rest des Laufs "
                  f"uebersprungen (Ausfall, kein Urteil)", flush=True)
    else:
        _NUR500[modell] = 0

def audioteil(kanal, b64):
    # nur noch image_url — input_audio ist die tote Route (s. ROUTEN-Kommentar)
    return {"type":"image_url","image_url":{"url":"data:audio/mp3;base64,"+b64}}

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
    # Leerzeichen-Komposita (VIS 021 EL, 25.09.2026): Die Copy schreibt „Sleep Guard Pro",
    # Scribe hört „Sleepguard Pro" — ohne Bindestrich griff keine Variante, der Block wurde
    # mit 0,8 rot, obwohl jedes Wort gesprochen war. Zusammengezogen wird NUR ein Wortpaar,
    # dessen Verbindung auf der anderen Seite als EIN Wort steht — ein fehlendes Wort bleibt
    # damit sichtbar (kein Zeichen-Vergleich ohne Leerzeichen).
    def paare(toks, gegen):
        g=set(gegen); aus=[]; i=0
        while i<len(toks):
            if i+1<len(toks) and toks[i]+toks[i+1] in g: aus.append(toks[i]+toks[i+1]); i+=2
            else: aus.append(toks[i]); i+=1
        return aus
    ns, ng = norm(soll), norm(gehoert)
    a=difflib.SequenceMatcher(None,ns,ng).ratio()
    b=difflib.SequenceMatcher(None,split_variante(soll),split_variante(gehoert)).ratio()
    c=difflib.SequenceMatcher(None,paare(ns,ng),paare(ng,ns)).ratio()
    return round(max(a,b,c),3)

def pausen_in(p):
    out = subprocess.run(["ffmpeg","-i",p,"-af","silencedetect=noise=-32dB:d=0.8","-f","null","-"],
                         capture_output=True,text=True).stderr
    s=[float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)",out)]
    e=[float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)",out)]
    return list(zip(s,e))

def ohr(mp3, soll, k):
    # WORDS-BINDUNG (Viktors Ohr-Gesetz 19.09.2026): Der Soll-Text steht NICHT im
    # Prompt — ein taubes Modell koennte ihn sonst als "Transkription" zurueckkopieren.
    # Erst words, dann Urteil; der Abgleich laeuft lokal ueber zeichen_match. Verfehlt
    # die Bindung, ist die Antwort KEIN URTEIL (fehler) — nie gruen, nie rot.
    prompt=("You hear one block of a German spoken ad voice-over. FIRST transcribe the "
     "German words you hear, verbatim. THEN judge ONLY the audio delivery. If you cannot "
     "hear any audio, answer exactly: NO_AUDIO. Otherwise STRICT JSON, nothing else: "
     '{"words":"<German words you hear>","aussprache_ok":true/false,"haenger":true/false,'
     '"artefakt":true/false,"roboterhaft":true/false,"note":"<max 12 words>"}')
    b64=base64.b64encode(open(mp3,"rb").read()).decode()
    out=""
    for modell,kanal in ROUTEN:
        if _NUR500.get(modell,0) >= 2:
            out=f"{modell}/{kanal}: in diesem Lauf uebersprungen (2 Aufrufe in Folge nur HTTP 500)"; continue
        url=f"https://api.kie.ai/{modell}/v1/chat/completions"
        payload={"model":modell,"temperature":0.1,"messages":[{"role":"user","content":[
            {"type":"text","text":prompt}, audioteil(kanal,b64)]}]}
        fuenfhundert=0
        for w in (0,20,40):
            if w: time.sleep(w)
            try:
                out=subprocess.run(["curl","-s","-X","POST","-H",f"Authorization: Bearer {k}",
                                    "-H","Content-Type: application/json","--data-binary","@-",url],
                                   input=json.dumps(payload),capture_output=True,text=True,timeout=300).stdout
            except subprocess.TimeoutExpired:
                # 25.09.2026 (VIS 020 EL): unbehandelter Timeout brach den ganzen Lauf ab und
                # druckte den Schluessel im Traceback — Timeout = Ausfall dieses Versuchs.
                out=f"{modell}/{kanal}: Timeout 300 s"; continue
            try:
                txt=json.loads(out)["choices"][0]["message"]["content"]
                txt=txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                if txt.upper().startswith("NO_AUDIO"):
                    out=f"{modell}/{kanal}: NO_AUDIO (Modell hoert nichts)"; break
                d=json.loads(txt)
                bind=zeichen_match(soll, str(d.get("words","")))
                if bind < 0.6:
                    out=f"{modell}/{kanal}: WORDS-Bindung verfehlt ({bind}): {str(d.get('words',''))[:80]}"; break
                d["route"]=f"{modell}/{kanal}"; d["words_match"]=bind
                _NUR500[modell]=0
                return d
            except Exception:
                if '"code":500' not in out: break
                fuenfhundert+=1
        _route_buchen(modell, fuenfhundert)
    return {"fehler":str(out)[:200]}

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
    # KORREKTUR 19.09.2026 (Befund VIS 005 EL): Die Montage legt den Block MIT seinem
    # --vorlauf an die Marke — die Sprache setzt also erst bei t+vorlauf ein, nicht bei t.
    # Das alte feste Fenster [t-0,45 ; t+0,05] verfehlte die Stille dadurch systematisch und
    # meldete "kleben", obwohl die Pause da war (gemessen: 7 Fehlalarme bei EINER echt engen
    # Kante). Jetzt wird der echte Sprech-Einsatz ab der Marke gesucht und die Stille DAVOR
    # geprüft; das Suchfenster deckt Vorläufe bis 0,45 s ab.
    for m in marken[1:]:
        t=m["start"]
        einsatz=next((b0 for a0,b0 in zip(s2,e2) if b0 >= t-0.10 and b0 <= t+0.45), None)
        if einsatz is not None:
            continue                      # Stille endet genau am Sprech-Einsatz -> Pause vorhanden
        if not any(a0 <= t+0.45 and b0 >= t-0.45 for a0,b0 in zip(s2,e2)):
            befunde.append(f"Blöcke kleben an Marke {t:.2f}s (keine Stille ≥0,25 s davor)")
    identitaet={}
    if k:
        mp3="_work/pruef_spur.mp3"
        # mono + 48k: grosse Nutzlasten laufen bei kie in den 180-s-Timeout (Ohr-Gesetz 19.09.2026)
        subprocess.run(["ffmpeg","-y","-v","error","-i",audio,"-ac","1","-c:a","libmp3lame","-b:a","48k",mp3],check=True)
        prompt=("You hear one continuous German ad voice-over. FIRST transcribe the first ten "
         "German words you hear. THEN judge ONLY voice identity. If you cannot hear any audio, "
         "answer exactly: NO_AUDIO. Otherwise STRICT JSON, nothing else: "
         '{"words_start":"<first ten German words you hear>",'
         '"same_speaker":true/false,"wechsel_bei_sekunde":<number or null>,'
         '"note":"<max 12 words>"}')
        b64=base64.b64encode(open(mp3,"rb").read()).decode()
        for modell,kanal in ROUTEN:
            if _NUR500.get(modell,0) >= 2: continue   # Sicherungsschalter (s. oben)
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
                    if txt.upper().startswith("NO_AUDIO"): break   # Kanal taub -> naechste Route
                    kand=json.loads(txt)
                    # WORDS-Bindung gegen den Anfang der ersten Soll-Zeile (lokal)
                    bind=zeichen_match(" ".join(str(marken[0]["text"]).split()[:12]), str(kand.get("words_start","")))
                    if bind < 0.5: break   # nicht ans Audio gebunden -> naechste Route
                    identitaet=kand; identitaet["route"]=f"{modell}/{kanal}"; identitaet["words_match"]=bind; break
                except Exception:
                    if '"code":500' not in out2: break
            if identitaet: break
        os.remove(mp3)
        if not identitaet:
            print("SPUR-OHR: KEIN URTEIL (Ausfall oder WORDS-Bindung verfehlt) — Stimm-Identitaet unbewertet")
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
rows=[]; rot=0; ohne_urteil=0; ohr_ausfall=0
spur_befunde, spur_ident = spur_checks(a.audio, marken, k)
for b in spur_befunde: print(f"SPUR ROT: {b}")
if spur_ident.get("same_speaker") is True: print(f"SPUR: eine Stimme durchgehend ({spur_ident.get('note','')})")
# Volltext-Rücktranskription EINMAL für die ganze Spur. Sie ist der Gegencheck gegen
# falsche Rote: Der Block-Schnipsel gibt Scribe keinen Kontext — an den Schnittkanten
# zerlegt es Komposita („Autofahren" -> „Auto fahren") und vergarbelt Eigennamen
# („Visiovance" -> „VisioWands"). Belegt VIS 006 EL 19.09.2026: zwei von 16 Blöcken
# waren allein dadurch rot, der Volltext derselben Spur war Wort für Wort sauber.
# Jede falsche Rote kostet einen Take — darum der Gegencheck, bevor ein Block rot bleibt.
_ganz = []
try:
    _gz = f"{BASIS}/_work/pruef_ganz.json"
    _r = subprocess.run([sys.executable, str(STAMM/".claude/skills/singing-vsl-transkription/scripts/transcribe.py"),
                         a.audio, "--out", _gz, "--sprache", "de"], capture_output=True, text=True)
    if _r.returncode == 0:
        _ganz = json.loads(open(_gz).read())["woerter"]
        os.remove(_gz)
except Exception:
    _ganz = []

def _ganz_match(soll, t0, t1, rand=1.5):
    """Bester Treffer der Soll-Zeile in der Volltext-Hörung rund um das Fenster.

    Ein FESTES Fenster taugt nicht: Die Marken liegen nicht auf Wortgrenzen, und schon
    ein halbes Nachbarwort drückt den Wert unter die Schwelle (gemessen VIS 006 EL:
    festes Fenster 0,857 — obwohl die Volltext-Hörung derselben Stelle wortgenau ist).
    Darum wird im Kandidaten-Bereich das best passende zusammenhängende Wortfenster
    gesucht, mit der Wortzahl der Soll-Zeile als Länge."""
    if not _ganz: return None
    z = lambda w: w.get("start", w.get("s", 0))
    kand = [w["text"] for w in _ganz if t0 - rand <= z(w) < t1 + rand]
    n = len(norm(soll))
    if not kand or n == 0: return None
    best = 0.0
    for laenge in (n, n + 1, n + 2, max(1, n - 1)):
        for i in range(0, max(1, len(kand) - laenge + 1)):
            best = max(best, zeichen_match(soll, " ".join(kand[i:i + laenge])))
    return round(best, 3)

for i,m in enumerate(marken):
    t0,t1=m["start"],m["ende"]
    blk=f"{BASIS}/_work/pruef_{i:02d}.mp3"
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{t0:.2f}","-to",f"{t1:.2f}",
                    "-i",a.audio,"-c:a","libmp3lame","-b:a","160k",blk],check=True)
    # Ohr-Kopie klein und mono (48k, Ohr-Gesetz 19.09.2026) — Scribe behaelt die 160k-Fassung
    ohrblk=f"{BASIS}/_work/pruef_{i:02d}_ohr.mp3"
    subprocess.run(["ffmpeg","-y","-v","error","-i",blk,"-ac","1","-c:a","libmp3lame","-b:a","48k",ohrblk],check=True)
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
    # 3) Ohr — Ausfall/Bindungs-Verfehlung ist KEIN URTEIL: der Ohr-Anteil bleibt
    # unbewertet (Standardwerte greifen), wird aber sichtbar gezaehlt und gemeldet
    urteil={} if a.ohne_ohr or not k else ohr(ohrblk,m["text"],k)
    if "fehler" in urteil: ohr_ausfall += 1
    sauber = not doppel and not p_in and urteil.get("aussprache_ok",True) \
             and not urteil.get("haenger",False) and not urteil.get("artefakt",False) \
             and not urteil.get("roboterhaft",False)
    # Gegencheck gegen den Volltext: NUR wenn der Block allein am match scheitert.
    # Doppelwörter, Hänger und Ohr-Befunde werden davon nie überstimmt.
    match_ganz = None; befund = None
    if sauber and match < 0.92 and _ganz:
        match_ganz = _ganz_match(m["text"], t0, t1)
        if match_ganz >= 0.92:
            befund = (f"Block-Schnipsel falsch-rot (match {match}) — die Volltext-Hörung "
                      f"derselben Stelle trifft {match_ganz}. Scribe verliert am Schnitt den Kontext.")
    # DRITTE KLASSE „kein Urteil" (VIS 001 EL, 19.09.2026): Eine LEERE Scribe-Antwort ist kein
    # Fehler des Takes, sondern ein Ausfall der Messung — zwei Bloecke lieferten erst nichts und
    # beim naechsten Lauf den vollen Text (das Audio trug nachweislich 82 % Sprache). Als ROT
    # gezaehlt schickt das den Loop auf eine Reparatur, die es nicht braucht.
    if not gehoert.strip():
        gruen = None; ohne_urteil += 1
    else:
        gruen = sauber and (match>=0.92 or (match_ganz is not None and match_ganz>=0.92))
        if not gruen: rot+=1
    rows.append({"block":i,"fenster":[t0,t1],"match":match,"match_ganz":match_ganz,
                 "befund":befund,"doppel":doppel,
                 "haenger_innen":p_in,"gehoert":gehoert,"ohr":urteil,"gruen":gruen})
    for f in (blk,roh,ohrblk):
        if os.path.exists(f): os.remove(f)
    if befund: print(f"   ↳ Block {i}: {befund}")
    print(f"Block {i}: match {match}{f' (Volltext {match_ganz})' if match_ganz is not None else ''} · Doppel {doppel or '—'} · Hänger {p_in or '—'} · "
          f"Ohr {('KEIN URTEIL' if 'fehler' in urteil else urteil.get('note','—')) if urteil else 'aus'} → {'KEIN URTEIL (Scribe leer)' if gruen is None else ('GRÜN' if gruen else 'ROT')}")
rot += len(spur_befunde)
json.dump({"spur":{"befunde":spur_befunde,"identitaet":spur_ident},"bloecke":rows},
          open(f"{BASIS}/_pipeline/pruefer.json","w"),ensure_ascii=False,indent=1)
print(f"pruefer.json: {len(rows)} Blöcke + Spur-Ebene, {rot} rot"
      + (f", {ohne_urteil} ohne Urteil (Scribe leer — erneut fahren)" if ohne_urteil else "")
      + (f", Ohr: {ohr_ausfall}x KEIN URTEIL (Ausfall/WORDS-Bindung — Ohr-Anteil unbewertet)" if ohr_ausfall else ""))
sys.exit(1 if rot else 0)
