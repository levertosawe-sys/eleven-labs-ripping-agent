#!/usr/bin/env python3
"""Sprechspur-Bau — HIER wird ElevenLabs generiert (v3 + Audio-Tags).

Gesetz (gemessen): Eine Copy ist EIN Sprechakt — ganzer Take, dann an den
GEMESSENEN Pausen schneiden und per adelay auf die Zeitmarken legen. Blockweise
Erzeugung klingt roboterhaft (Schlussmelodie in jedem Block). v3 kann kein
previous_text — der Ein-Take-Weg ersetzt es.

CWD = Pipeline-Ordner. Subkommandos:
  stimme <KÜRZEL>                          → Register-Zeile zeigen (Fehler, wenn leer → Casting)
  take --text <take.txt> --kuerzel ROV [--out _work/take.mp3]
        take.txt = die Copy MIT v3-Tags in eckigen Klammern, Blöcke durch Leerzeile
  montage --take _work/take.mp3 --marken <marken.json> [--out _work/sprechspur.wav]
        marken.json = [{"start":0.08,"ende":8.48,"text":"..."}, ...] (SOLL-Fenster je Block)
        --nur-messen: Sprechdauer je Block (nach Tempo + Pausen-Quetsche) als JSON, keine Montage —
        damit werden die Marken nach GEMESSENER Dauer verteilt statt nach Wortzahl (v3 würfelt
        die Pace je Take um ±10 %)
  woerter --audio _work/sprechspur.wav     → _pipeline/sprech_words.json (Scribe, de)
Tempo-Gesetz der Montage: --tempo hebt den GANZEN Take gleichmäßig an (Default = Obergrenze 1,12 — v3 spricht Werbe-Copy zu gemächlich, ein gleichmäßiger Lift hält die
Prosodie, blockweise Sprünge klingen nach Schnitt); --atem (Default 0,45 s) ist die
Luft, die jeder Block VOR der nächsten Marke frei lässt — ohne sie kleben die Sätze
aneinander (gemessen: 0,02–0,07 s Stille an drei von fünf Kanten). Je Block dann:
Überlänge ≤10 % → atempo; 10–15 % nur bei ruhigen Blöcken; darüber Abbruch mit
Kürzungs-Auftrag — nie schneller als 1,15.
"""
import argparse, csv, json, os, re, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

BASIS = os.getcwd()
STAMM = Path(__file__).resolve().parents[2]
REGISTER = STAMM / "datenbanken" / "stimmen" / "daten.csv"

def key():
    for pfad in (Path.home()/".config"/"awms"/".env", Path.home()/".config"/"leichtkraut"/".env"):
        if pfad.exists():
            for z in pfad.read_text().splitlines():
                if z.startswith("ELEVENLABS_API_KEY="): return z.split("=",1)[1].strip()
    sys.exit("ELEVENLABS_API_KEY fehlt — Viktor fragen, nie auf andere Keys ausweichen.")

def stimme(kuerzel):
    with open(REGISTER, encoding="utf-8") as f:
        treffer = [r for r in csv.DictReader(f) if r["marke"].strip().upper() == kuerzel.upper()]
    if len(treffer) > 1:
        sys.exit(f"Stimmen-Register hat {len(treffer)} Zeilen für {kuerzel} — eine Marke, eine "
                 f"Stimme. Erst aufräumen (die ERSTE Casting-Zeile gilt), dann weiter.")
    if treffer: return treffer[0]
    sys.exit(f"Stimmen-Register hat keine Zeile für {kuerzel} — erst Stimm-Casting "
             f"(speaking-vsl-stimm-casting) oder Viktors Stimme eintragen.")

def cmd_take(a):
    if a.voice_id:
        # Experiment-Weg (z. B. Voice-Design-Test): Stimme direkt, Register unangetastet
        r = {"voice_id": a.voice_id, "name": a.voice_name or a.voice_id,
             "modell": "eleven_v3", "stability": "0.5", "similarity_boost": "0.75", "style": "0.0"}
    else:
        r = stimme(a.kuerzel)
    text = Path(a.text).read_text(encoding="utf-8").strip()
    einst = {"stability": a.stability if a.stability is not None else float(r["stability"] or 0.5)}
    if a.similarity is not None: einst["similarity_boost"] = a.similarity
    elif r.get("similarity_boost"): einst["similarity_boost"] = float(r["similarity_boost"])
    if r.get("style"): einst["style"] = float(r["style"])
    body = {"text": text, "model_id": r["modell"] or "eleven_v3", "voice_settings": einst}
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{r['voice_id']}?output_format=mp3_44100_192",
        data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": key(), "Content-Type": "application/json"})
    for versuch in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as antwort:
                Path(a.out).write_bytes(antwort.read()); break
        except urllib.error.HTTPError as e:
            fehler = e.read().decode()[:400]
            if versuch == 2: sys.exit(f"ElevenLabs {e.code}: {fehler}")
    d = dauer(a.out)
    print(f"Take OK → {a.out} · {d:.2f}s · Stimme {r['name']} ({r['voice_id']}) · {body['model_id']}")

def dauer(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                 "-of","csv=p=0",p],capture_output=True,text=True).stdout.strip())

def pausen(p, noise="-32dB", mind=0.18):
    out = subprocess.run(["ffmpeg","-i",p,"-af",f"silencedetect=noise={noise}:d={mind}","-f","null","-"],
                         capture_output=True, text=True).stderr
    starts = [float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)", out)]
    enden  = [float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)", out)]
    return [( s, e ) for s, e in zip(starts, enden)]

def _take_woerter(take):
    """Scribe-Wortzeiten des Takes (de) — die exakte Schnitt-Grundlage."""
    import tempfile
    roh = tempfile.mktemp(suffix=".json")
    script = STAMM/".claude"/"skills"/"singing-vsl-transkription"/"scripts"/"transcribe.py"
    r = subprocess.run([sys.executable,str(script),take,"--out",roh,"--sprache","de"],
                       capture_output=True,text=True)
    if r.returncode != 0: return None
    d = json.loads(Path(roh).read_text()); os.remove(roh)
    return [{"w":w["text"],"s":w["start"],"e":w["end"]} for w in d["woerter"]]

# Zahlwoerter fuer das Alignment (YUR-003-EL-Befund 08.09.2026): Die Copy traegt "142.000",
# der Take spricht "Hundertzweiundvierzigtausend" — ein gehoertes Token gegen zwei geschriebene.
# difflib findet keinen Match, die Blockgrenze landet MITTEN im Zahlwort, und der Schnitt macht
# aus "142.000" ein "42.000". Ein Faktenfehler, den kein Ohr-Urteil meldet, weil die Aussprache
# sauber ist. Deshalb: Ziffern zu Zahlwoertern normieren UND an den Fugen zerlegen, weil
# "einhundert…" (aus Ziffern erzeugt) und "hundert…" (so gesprochen) sonst wieder auseinanderlaufen.
_EINER=["","ein","zwei","drei","vier","fuenf","sechs","sieben","acht","neun","zehn","elf","zwoelf",
        "dreizehn","vierzehn","fuenfzehn","sechzehn","siebzehn","achtzehn","neunzehn"]
_ZEHNER=["","","zwanzig","dreissig","vierzig","fuenfzig","sechzig","siebzig","achtzig","neunzig"]
def _zahlwort(n):
    if n<20: return "eins" if n==1 else _EINER[n]
    if n<100:
        z,e=divmod(n,10); return _ZEHNER[z] if e==0 else f"{_EINER[e]}und{_ZEHNER[z]}"
    if n<1000:
        h,r=divmod(n,100); return ("ein" if h==1 else _EINER[h])+"hundert"+(_zahlwort(r) if r else "")
    if n<1000000:
        t,r=divmod(n,1000); return ("ein" if t==1 else _zahlwort(t))+"tausend"+(_zahlwort(r) if r else "")
    return str(n)
def _norm_w(s):
    s=s.lower().replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    s=re.sub(r"(?<=\d)\.(?=\d{3})","",s)                                  # 142.000 -> 142000
    s=re.sub(r"\d+", lambda m: " "+_zahlwort(int(m.group()))+" ", s)
    s=s.replace("%"," prozent ")
    s=re.sub(r"(?<=[a-z])-(?=[a-z])","",s)                                  # Collagen-Botox -> collagenbotox
    s=re.sub(r"[^a-z0-9 ]"," ",s)
    s=re.sub(r"(hundert|tausend|millionen?)", r" \1 ", s)                   # Fugen zerlegen
    return [w for w in s.split() if w]

def cmd_montage(a):
    marken = json.load(open(a.marken))
    ersatz = {int(k): v for k, v in (json.load(open(a.ersatz)) if getattr(a, 'ersatz', None) else {}).items()}
    if a.tempo > 1.12 or a.tempo < 0.95:
        sys.exit(f"--tempo {a.tempo} liegt außerhalb 0,95–1,12 — darüber klingt die Stimme gehetzt, darunter zäh.")
    tw = _take_woerter(a.take)
    if abs(a.tempo - 1.0) > 0.001:
        # Gleichmäßiger Lift des ganzen Takes VOR dem Schneiden: Wortzeiten skalieren mit,
        # Scribe muss nicht erneut hören.
        getempt = f"{BASIS}/_work/take_tempo.wav"
        subprocess.run(["ffmpeg","-y","-v","error","-i",a.take,"-af",f"atempo={a.tempo:.4f}",
                        "-ar","44100","-ac","2",getempt], check=True)
        a.take = getempt
        if tw:
            for w in tw: w["s"] /= a.tempo; w["e"] /= a.tempo
    take_d = dauer(a.take)
    paus = pausen(a.take)
    grenzen = None
    if tw:
        # Präziser Weg: Soll-Wortstrom gegen gehörten Wortstrom alignen (difflib),
        # Blockgrenze = Mitte zwischen letztem Wort des Blocks und erstem des nächsten.
        import difflib
        soll_woerter, soll_grenzidx = [], []
        for m in marken:
            soll_woerter += _norm_w(m["text"]); soll_grenzidx.append(len(soll_woerter))
        hoer = [x for w in tw for x in _norm_w(w["w"])]
        hoer_map = []   # Index im hoer-Strom → tw-Index
        for i,w in enumerate(tw): hoer_map += [i]*len(_norm_w(w["w"]))
        sm = difflib.SequenceMatcher(None, soll_woerter, hoer)
        abb = {}
        for b in sm.get_matching_blocks():
            for k in range(b.size): abb[b.a+k] = b.b+k
        grenzen = [0.0]
        # Wortzeiten je Block (erstes Wort / letztes Wort) — die Blockkanten werden
        # daran geschnitten, nicht an Stille-Schwellen (die kappen den Atem-Anlauf).
        wort_s = [tw[0]["s"]]; wort_e = []
        for gi in soll_grenzidx[:-1]:
            links = max((v for s,v in abb.items() if s < gi), default=None)
            rechts = min((v for s,v in abb.items() if s >= gi), default=None)
            if links is None or rechts is None: grenzen = None; break
            t_l = tw[hoer_map[links]]["e"]; t_r = tw[hoer_map[rechts]]["s"]
            grenzen.append((t_l + t_r) / 2); wort_e.append(t_l); wort_s.append(t_r)
        if grenzen: grenzen.append(take_d); wort_e.append(tw[-1]["e"])
        else: wort_s = None
    if not grenzen:
        # Ausweichweg: Pause, die dem Zeichenanteil am nächsten liegt
        ges_zeichen = sum(len(m["text"]) for m in marken)
        grenzen = [0.0]; acc = 0
        for m in marken[:-1]:
            acc += len(m["text"])
            soll = take_d * acc / ges_zeichen
            if not paus: sys.exit("Keine Sprechpausen gemessen — Take prüfen (durchgehend Ton?).")
            beste = min(paus, key=lambda p: abs((p[0]+p[1])/2 - soll))
            grenzen.append((beste[0]+beste[1])/2)
        grenzen.append(take_d)
        print("Hinweis: Scribe-Alignment nicht möglich — Zeichen-Anteils-Schnitt benutzt.", file=sys.stderr)
    if not tw: wort_s = None
    teile = []
    protokoll = []
    messung = []
    VORLAUF, NACHLAUF = a.vorlauf, a.nachlauf
    for i, m in enumerate(marken):
        t0, t1 = grenzen[i], grenzen[i+1]
        # Atem-Reserve: der Block muss VOR der nächsten Marke enden, sonst kleben die Sätze.
        letzter = (i == len(marken) - 1)
        fenster = m["ende"] - m["start"] - (0.0 if letzter else a.atem)
        teil = f"{BASIS}/_work/block_{i:02d}.wav"
        vorlauf = 0.0
        if wort_s:
            # Kante = erstes Wort − 150 ms (Atem bleibt) … letztes Wort + 150 ms, innerhalb der Pausen-Mitten
            t0n, t1n = max(t0, wort_s[i] - VORLAUF), min(t1, wort_e[i] + NACHLAUF)
            if t1n > t0n + 0.2: t0, t1 = t0n, t1n
            vorlauf = max(0.0, wort_s[i] - t0)
        # Rand-Stille wegtrimmen (der Schnitt liegt in Pausen-MITTEN — ohne Trim beginnt
        # jeder Block mit halber Take-Pause und die Marke verfehlt den Stimm-Einsatz)
        # Schwelle -58 dB statt -40: Bei -40 fiel der weiche Stimm-Einsatz (200 ms Anlauf
        # von -75 auf -47 dB) mit weg — die Blockkante wurde ein Klick (Viktors Befund
        # ARE 001 EL: "Bruch bei Sekunde 13 und 36"). Rest-Stille bleibt kurz stehen.
        trim=("silenceremove=start_periods=1:start_threshold=-58dB:start_silence=0.06,"
              "areverse,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.10,areverse")
        if wort_s: trim = "anull"   # Wortzeiten-Kanten: kein Schwellen-Trim
        if i in ersatz:
            # Block kommt aus einer eigenen Datei (Wuerfel/anderer Take). Dort gibt es keine
            # Take-Wortzeiten, also Rand-Stille per Schwelle weg — sonst traegt der Block die
            # volle Anlauf-Stille seiner eigenen Aufnahme.
            subprocess.run(["ffmpeg","-y","-v","error","-i",ersatz[i],"-af",
                            "silenceremove=start_periods=1:start_threshold=-58dB:start_silence=0.06,"
                            "areverse,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.10,areverse",
                            "-ar","44100","-ac","2",teil], check=True)
            if a.tempo != 1.0:
                subprocess.run(["ffmpeg","-y","-v","error","-i",teil,"-af",f"atempo={a.tempo:.4f}",
                                f"{teil}.t.wav"], check=True)
                os.replace(f"{teil}.t.wav", teil)
            vorlauf = 0.0
            protokoll.append(f"Block {i}: Ersatz {os.path.basename(ersatz[i])}")
            blockdauer = dauer(teil)
        else:
            subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{t0:.3f}","-to",f"{t1:.3f}",
                            "-i",a.take,"-af",trim,"-ar","44100","-ac","2",teil], check=True)
            blockdauer = dauer(teil)
        # Vor-/Nachlauf (Atem) zählen nicht zur Sprechzeit: Der Vorlauf liegt VOR der Marke,
        # der Nachlauf überlappt den Atem des Folgeblocks — nur die Wörter müssen ins Fenster.
        if wort_s and i not in ersatz: blockdauer -= (vorlauf + max(0.0, t1 - wort_e[i]))
        # Innen-Pausen IMMER quetschen, nicht erst bei Überlänge: Satz-Tags ([warm], [emphatic])
        # legen mitten im Block 0,8–1,0 s Stille — der Prüfer meldet sie als Hänger, das Ohr als
        # Loch. Jede Stille ≥ 0,6 s wird per Segment-Schnitt auf 0,40 s gekürzt (0,20 s bleiben an
        # jeder Seite), der Sprechrhythmus bleibt. (ffmpeg silenceremove entfernte gemessen nur
        # 0,17 s von 1,15 s — darum der eigene Schnitt.)
        d_vor = dauer(teil)
        lang = [(s0, e0) for s0, e0 in pausen(teil, noise="-30dB", mind=0.6) if e0 - s0 >= 0.6]
        if lang:
            segs = []; pos = 0.0
            for s0, e0 in lang:
                segs.append((pos, s0 + 0.20)); pos = e0 - 0.20
            segs.append((pos, d_vor))
            filt = ";".join(f"[0]atrim=start={x0:.3f}:end={x1:.3f},asetpts=N/SR/TB[s{k}]" for k, (x0, x1) in enumerate(segs))
            filt += ";" + "".join(f"[s{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[out]"
            gequetscht = f"{BASIS}/_work/block_{i:02d}_iq.wav"
            subprocess.run(["ffmpeg","-y","-v","error","-i",teil,"-filter_complex",filt,"-map","[out]",gequetscht], check=True)
            neu_d = dauer(gequetscht)
            if neu_d < d_vor - 0.05:
                os.replace(gequetscht, teil)
                protokoll.append(f"Block {i}: Innen-Pausen {d_vor:.2f}→{neu_d:.2f}s ({len(lang)}×)")
                blockdauer -= (d_vor - neu_d)
            else:
                os.remove(gequetscht)
        # Eskalations-Leiter bei Überlänge: (1) Pausen quetschen — v3 legt mit Tags
        # theatralische Pausen, die Wörter bleiben unberührt; (2) atempo bis 1,10;
        # (3) darüber ist die Copy zu lang → kürzen, nie hetzen.
        if blockdauer > fenster:
            gequetscht = f"{BASIS}/_work/block_{i:02d}_sq.wav"
            subprocess.run(["ffmpeg","-y","-v","error","-i",teil,"-af",
                "silenceremove=stop_periods=-1:stop_duration=0.40:stop_threshold=-35dB:stop_silence=0.32",
                gequetscht], check=True)
            neu_d = dauer(gequetscht)
            if neu_d < blockdauer - 0.05:
                os.replace(gequetscht, teil)
                protokoll.append(f"Block {i}: Pausen {blockdauer:.2f}→{neu_d:.2f}s")
                blockdauer = neu_d
            else:
                os.remove(gequetscht)
        if a.nur_messen:
            # Mess-Modus: nur die gequetschte Sprechdauer je Block melden (für die Marken-Planung),
            # keine Leiter, keine Montage.
            # Datei-Dauer inkl. Vor-/Nachlauf melden: der Planer setzt daraus die Marken — meldet man nur die
            # Wortzeit, kleben die Blöcke (Nachlauf + Vorlauf des Folgeblocks fressen den Atem auf).
            messung.append({"block": i, "sprechdauer": round(dauer(teil), 2), "fenster": round(fenster, 2)})
            os.remove(teil); continue
        if blockdauer > fenster:
            faktor = blockdauer / fenster
            if faktor > 1.15:
                sys.exit(f"Block {i} ist {blockdauer:.2f}s für ein {fenster:.2f}s-Fenster "
                         f"(x{faktor:.2f}, nach Pausen-Quetsche) — Copy kürzen und neu erzeugen.")
            getempt = f"{BASIS}/_work/block_{i:02d}_at.wav"
            subprocess.run(["ffmpeg","-y","-v","error","-i",teil,"-af",
                            f"atempo={min(faktor,1.15):.4f}",getempt], check=True)
            os.replace(getempt, teil)
            protokoll.append(f"Block {i}: atempo {faktor:.3f}")
        elif a.dehnen and i < len(marken)-1 and blockdauer < fenster - 0.6:
            # UNTER-Länge: tote Luft > 0,6 s vor der nächsten Marke — sanft dehnen
            # (Gesetz der Werkstatt: nie beschleunigen, leicht verlangsamen erlaubt),
            # Untergrenze 0,94; der Rest bleibt als natürlicher Absatz-Atem stehen.
            ziel = fenster - 0.5
            faktor = max(blockdauer / ziel, 0.94)
            if faktor < 0.999:
                getempt = f"{BASIS}/_work/block_{i:02d}_at.wav"
                subprocess.run(["ffmpeg","-y","-v","error","-i",teil,"-af",
                                f"atempo={faktor:.4f}",getempt], check=True)
                os.replace(getempt, teil)
                protokoll.append(f"Block {i}: gedehnt {faktor:.3f} (Luft {fenster-blockdauer:.2f}s)")
        # Das ERSTE WORT landet auf der Marke — der Vorlauf (Atem) liegt davor.
        teile.append((teil, max(0.0, m["start"] - vorlauf)))
    if a.nur_messen:
        ges = sum(x["sprechdauer"] for x in messung) + a.atem * (len(messung) - 1)
        out = json.dumps({"tempo": a.tempo, "atem": a.atem, "bloecke": messung,
                          "bedarf_s": round(ges, 2), "video_s": round(marken[-1]["ende"], 2)}, ensure_ascii=False)
        if a.messung: Path(a.messung).write_text(out, encoding="utf-8")
        print(out)
        return
    ein = []; filt = []
    for i,(teil, start) in enumerate(teile):
        ein += ["-i", teil]
        bd = dauer(teil)
        # Ein-/Ausblende je Block (15 / 60 ms): kein Sample-Sprung an der Kante.
        # Blenden so lang wie der Vor-/Nachlauf erlaubt: der Atem kommt weich, nicht als Schnipsel.
        fin, fout = min(0.08, VORLAUF/2), min(0.10, NACHLAUF/2)
        filt.append(f"[{i}]afade=t=in:d={fin:.3f},afade=t=out:st={max(bd-fout,0):.3f}:d={fout:.3f},"
                    f"adelay={int(start*1000)}|{int(start*1000)}[d{i}]")
    # Grundrauschen auf Take-Niveau (~ -84 dB) über die ganze Spur: Zwischen den Blöcken
    # stand vorher digitale Null (-180 dB) — das Ohr hört das Vakuum als Bruch.
    gesamt = marken[-1]["ende"] + 0.5
    filt.append(f"anoisesrc=color=pink:amplitude={a.rauschen}:duration={gesamt:.2f}:sample_rate=44100,"
                f"aformat=channel_layouts=stereo[rt]")
    filt.append("".join(f"[d{i}]" for i in range(len(teile))) + "[rt]" +
                f"amix=inputs={len(teile)+1}:normalize=0,loudnorm=I=-16:TP=-1.5[out]")
    subprocess.run(["ffmpeg","-y","-v","error"]+ein+["-filter_complex",";".join(filt),
                    "-map","[out]","-ar","44100",a.out], check=True)
    for t,_ in teile: os.remove(t)
    print(f"Montage OK → {a.out} · {dauer(a.out):.2f}s · Tempo {a.tempo:.3f} · Atem {a.atem:.2f}s · Schnitte {[round(g,2) for g in grenzen[1:-1]]}"
          + (" · " + " · ".join(protokoll) if protokoll else ""))

def cmd_woerter(a):
    script = STAMM/".claude"/"skills"/"singing-vsl-transkription"/"scripts"/"transcribe.py"
    r = subprocess.run([sys.executable, str(script), a.audio, "--out",
                        f"{BASIS}/_pipeline/sprech_words_roh.json", "--sprache","de"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Scribe-Wortcache scheiterte:\n{r.stderr[-400:]}")
    d = json.loads(open(f"{BASIS}/_pipeline/sprech_words_roh.json").read())
    words=[{"w":w["text"],"s":round(w["start"],2),"e":round(w["end"],2)} for w in d["woerter"]]
    json.dump({"language":"de","words":words}, open(f"{BASIS}/_pipeline/sprech_words.json","w"),
              ensure_ascii=False)
    print(f"Wort-Cache: {len(words)} Wörter → _pipeline/sprech_words.json")

ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("stimme"); s.add_argument("kuerzel")
t = sub.add_parser("take"); t.add_argument("--text",required=True); t.add_argument("--kuerzel",required=True); t.add_argument("--out",default="_work/take.mp3"); t.add_argument("--voice-id"); t.add_argument("--voice-name")
# Lebendigkeits-Regler (v3): stability 0.0 = kreativ/ausdrucksstark, 0.5 = neutral, 1.0 = robust/flach.
# Ohne Angabe gilt die Register-Zeile (bzw. 0.5 im Experiment-Weg).
t.add_argument("--stability", type=float); t.add_argument("--similarity", type=float)
m = sub.add_parser("montage"); m.add_argument("--tempo",type=float,default=1.12); m.add_argument("--nur-messen",action="store_true"); m.add_argument("--messung",help="Datei für die Mess-Ausgabe (JSON)"); m.add_argument("--atem",type=float,default=0.45); m.add_argument("--ersatz",help='JSON {"<block>": "<audio>"}: einzelne Bloecke aus einer anderen Datei statt aus dem Take schneiden — noetig, wenn die Marken auf Bildschnittkanten verankert sind und ein Take nicht fuer jeden Block die passende Laenge liefert (Take-Streuung +-10 %)'); m.add_argument("--dehnen",action="store_true",help="Unterlaengen dehnen (atempo<1). AUS per Default: an verankerten Schnittkanten frisst das Dehnen genau den Atem, den marken_planen.py eingeplant hat, und klingt nach Slow-Motion (YUR-003-EL-Befund 08.09.2026)"); m.add_argument("--vorlauf",type=float,default=0.30); m.add_argument("--nachlauf",type=float,default=0.20); m.add_argument("--rauschen",type=float,default=0.0004); m.add_argument("--take",default="_work/take.mp3"); m.add_argument("--marken",required=True); m.add_argument("--out",default="_work/sprechspur.wav")
w = sub.add_parser("woerter"); w.add_argument("--audio",default="_work/sprechspur.wav")
a = ap.parse_args()
if a.cmd=="stimme": print(json.dumps(stimme(a.kuerzel), ensure_ascii=False, indent=1))
elif a.cmd=="take": cmd_take(a)
elif a.cmd=="montage": cmd_montage(a)
elif a.cmd=="woerter": cmd_woerter(a)
