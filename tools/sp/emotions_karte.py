#!/usr/bin/env python3
"""Emotions-Karte: die Delivery der ORIGINAL-Stimme je Copy-Zeile reverse-engineeren.

Warum: ElevenLabs v3 ohne Vorgabe wiederholt oder würfelt Emotionen. Also wird
zuerst gemessen, WIE das Original jede Zeile spricht (Emotion, Ton, Tempo,
betonte Wörter, Pausen), und daraus je Zeile ein v3-Audio-Tag-Vorschlag gebaut.
Ohr ist gemini-2.5-PRO via kie.ai, Audio im Kanal `image_url` (Belegt am
Transkriptions-Test mit bekanntem Wortlaut, RYZ 002 EL 16.09.2026). Die tote
Route input_audio (bekommt KEIN Audio durchgereicht, erfindet ein Urteil) ist
seit 19.09.2026 KOMPLETT raus — auch als Notnagel (Viktors Ohr-Gesetz). Jede
Antwort ist WORDS-gebunden: das Modell transkribiert zuerst blind (der Soll-Text
steht NICHT im Prompt), der Abgleich gegen die bekannte EN-Zeile läuft lokal;
verfehlt er, zählt die Zeile als KEIN URTEIL (fehler), nie als Messwert.
Schnipsel mono/48k gegen die 180-s-Timeouts.

CWD = Pipeline-Ordner. Aufruf:
  python3 emotions_karte.py --bloecke <bloecke.json>
bloecke.json: [{"t0":0.08,"t1":8.48,"en":"Your kidneys ..."} , ...]
Ausgabe: _pipeline/emotions_karte.json (je Zeile Analyse + v3_tags).
Exit 1, wenn eine Zeile kein gültiges JSON liefert (Rest wird trotzdem gespeichert).
"""
import argparse, base64, json, os, subprocess, sys, time
from pathlib import Path

BASIS = os.getcwd()
TAGS =["whispers","sighs","excited","angry","stern","serious","warm","reassuring",
        "urgent","sarcastic","curious","confident","calm","dramatic","emphatic"]

def key():
    for z in (Path.home()/".config"/"awms"/".env").read_text().splitlines():
        if z.startswith("KIE_API_KEY="): return z.split("=",1)[1].strip()
    sys.exit("KIE_API_KEY fehlt in ~/.config/awms/.env")

# WORDS-BINDUNG (Viktors Ohr-Gesetz, 19.09.2026): Der Soll-Text steht NICHT mehr im
# Prompt — ein taubes Modell koennte ihn sonst als "Transkription" zurueckkopieren.
# Das Modell transkribiert blind (words), der Abgleich gegen die bekannte EN-Zeile
# laeuft LOKAL (_gehoert). Verfehlt die Bindung, ist das Urteil derselben Antwort
# wertlos -> KEIN URTEIL, nie als Messwert verwenden.
PROMPT = ("You hear one short snippet from an English direct-response health ad "
 "(the narrator speaks one line). FIRST transcribe exactly what you hear. THEN judge "
 "ONLY the vocal delivery (not the content). Most ad narration is professionally "
 "NEUTRAL — flag emotion only when the delivery clearly departs from neutral "
 "narration. If you cannot hear any audio, answer exactly: NO_AUDIO. Otherwise "
 "answer STRICT JSON, nothing else: "
 '{{"words":"<verbatim transcription of what you hear>",'
 '"emotion":"<primary emotion, 1-3 words>","ton":"<tone of voice, 1-3 words>",'
 '"emotionsstaerke":"neutral/leicht/stark",'
 '"tempo":"slow/medium/fast","betonte_woerter":["<words the voice stresses>"],'
 '"pausen":"<none or where the voice pauses, max 8 words>",'
 '"v3_tags":[<tags ONLY if emotionsstaerke is stark, max 1, from: {tags}; else empty>],'
 '"note":"<max 12 words>"}}')

def _gehoert(words, en):
    """Lokale WORDS-Bindung: normierte Aehnlichkeit Transkription vs. bekannte Zeile."""
    import difflib, re as _re
    n = lambda s: _re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).split()
    if not words or not en: return 0.0
    return difflib.SequenceMatcher(None, n(words), n(en)).ratio()

# ROUTEN, in dieser Reihenfolge probiert. Belegt am Transkriptions-Test mit bekanntem
# Wortlaut (RYZ 002 EL, 16.09.2026): gemini-2.5-pro ueber `image_url` hoert das Audio
# wirklich. Die tote Sprosse ("gemini-2.5-flash", "input_audio") wurde am 19.09.2026
# auf Viktors Ohr-Gesetz ENTFERNT: input_audio traegt bei kie.ai KEIN Audio durch,
# das Modell halluziniert souveraen ("Hello, how are you?" auf eine Werbezeile) —
# ein Ausfall darf nie wie eine Antwort aussehen. NIE wieder als Fallback einbauen.
ROUTEN = [("gemini-2.5-pro",   "image_url"),
          ("gemini-2.5-flash", "image_url"),
          # 25.09.2026 (VIS 019 EL): 2.5-pro 500 "server is currently being maintained",
          # 2.5-flash + 3-flash 422 "channel is not supported"; gemini-3-pro bestand
          # Nur-Text ("OK") UND Transkriptions-Test mit bekanntem Wortlaut (Bindung 1,0).
          # Dritte Sprosse, greift nur, wenn die geltende Route ausfaellt; WORDS-Bindung
          # gilt unveraendert je Aufruf.
          ("gemini-3-pro",     "image_url")]

# SICHERUNGSSCHALTER (25.09.2026, VIS 021 EL): Liefert eine Route bei ZWEI Aufrufen in Folge
# nur HTTP 500 (je drei Versuche mit 20/40 s Pause), ist sie ausgefallen, nicht wackelig — sie
# wird fuer den Rest DIESES Laufs uebersprungen (sichtbar gemeldet). Ohne Schalter kostete die
# Wartung von 2.5-pro jede Zeile ~60 s Warten: 28 Zeilen = ~35 min statt ~10. Jede echte Antwort
# der Route (auch NO_AUDIO/Bindung verfehlt) setzt den Zaehler zurueck.
_NUR500 = {}

def _teil(kanal, b64):
    # nur noch image_url — input_audio ist die tote Route (s. ROUTEN-Kommentar)
    return {"type":"image_url","image_url":{"url":"data:audio/mp3;base64,"+b64}}

def ask(mp3, en, k):
    b64 = base64.b64encode(open(mp3,"rb").read()).decode()
    letzte = ""
    for modell, kanal in ROUTEN:
        if _NUR500.get(modell, 0) >= 2:
            letzte = f"{modell}/{kanal}: in diesem Lauf uebersprungen (2 Aufrufe in Folge nur HTTP 500)"; continue
        url = f"https://api.kie.ai/{modell}/v1/chat/completions"
        payload = {"model":modell,"temperature":0.1,"messages":[{"role":"user","content":[
            {"type":"text","text":PROMPT.format(en=en, tags=", ".join(TAGS))},
            _teil(kanal, b64)]}]}
        fuenfhundert = 0
        for w in (0, 20, 40):
            if w: time.sleep(w)
            try:
                out = subprocess.run(["curl","-s","-X","POST","-H",f"Authorization: Bearer {k}",
                                      "-H","Content-Type: application/json","--data-binary","@-",url],
                                     input=json.dumps(payload), capture_output=True, text=True, timeout=300).stdout
            except subprocess.TimeoutExpired:
                # 25.09.2026 (VIS 018 EL): ein 300-s-Timeout warf bisher eine unbehandelte Ausnahme —
                # der ganze Lauf brach bei Zeile 12 von 23 ab und ALLE Urteile gingen verloren.
                # Timeout = Ausfall (Ohr-Gesetz Punkt 3): sichtbar buchen, naechste Route.
                letzte = f"{modell}/{kanal}: Timeout 300 s (Ausfall, kein Urteil)"; break
            letzte = out[:300]
            try:
                txt = json.loads(out)["choices"][0]["message"]["content"]
                txt = txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                if txt.upper().startswith("NO_AUDIO"):
                    letzte = f"{modell}/{kanal}: NO_AUDIO (Modell hoert nichts)"; break
                d = json.loads(txt)
                bind = _gehoert(d.get("words",""), en)
                if bind < 0.6:
                    # nicht ans Audio gebunden -> naechste Route; nie als Urteil werten
                    letzte = f"{modell}/{kanal}: WORDS-Bindung verfehlt ({bind:.2f}): {str(d.get('words',''))[:80]}"; break
                d["v3_tags"] = [t for t in d.get("v3_tags",[]) if t in TAGS]
                d["route"] = f"{modell}/{kanal}"
                d["words_match"] = round(bind, 3)
                _NUR500[modell] = 0
                return d
            except Exception:
                if '"code":500' not in out: break   # echter Fehler -> naechste Route
                fuenfhundert += 1
        if fuenfhundert == 3:
            _NUR500[modell] = _NUR500.get(modell, 0) + 1
            if _NUR500[modell] == 2:
                print(f"[ohr] {modell}: zwei Aufrufe in Folge nur HTTP 500 — Route fuer den Rest des Laufs "
                      f"uebersprungen (Ausfall, kein Urteil)", file=sys.stderr, flush=True)
        else:
            _NUR500[modell] = 0
    return {"fehler": letzte}

ap = argparse.ArgumentParser(); ap.add_argument("--bloecke", required=True)
a = ap.parse_args()
bloecke = json.load(open(a.bloecke))
SRC = f"{BASIS}/_work/source_original.mp4"
if not os.path.exists(SRC): SRC = f"{BASIS}/_work/source.mp4"
k = key(); rows = []; kaputt = 0
for i, b in enumerate(bloecke):
    snip = f"{BASIS}/_work/emo_{i:02d}.mp3"
    # mono + 48k: grosse Nutzlasten laufen bei kie in den 180-s-Timeout (Ohr-Gesetz 19.09.2026)
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{b['t0']:.2f}","-to",f"{b['t1']:.2f}",
                    "-i",SRC,"-vn","-ac","1","-c:a","libmp3lame","-b:a","48k",snip], check=True)
    r = ask(snip, b["en"], k)
    os.remove(snip)
    rows.append({"zeile": i, "t0": b["t0"], "t1": b["t1"], "en": b["en"], **r})
    if "fehler" in r: kaputt += 1
    print(f"Zeile {i}: {r.get('emotion','KEIN URTEIL')} · Ton {r.get('ton','—')} · Tags {r.get('v3_tags','—')}")
    # Zwischenstand nach JEDER Zeile sichern (ein Abbruch kostet sonst alle bisherigen Urteile)
    json.dump(rows, open(f"{BASIS}/_pipeline/emotions_karte.json","w"), ensure_ascii=False, indent=1)
json.dump(rows, open(f"{BASIS}/_pipeline/emotions_karte.json","w"), ensure_ascii=False, indent=1)
print(f"emotions_karte.json: {len(rows)} Zeilen, {kaputt} ohne Urteil (Ausfall/WORDS-Bindung — nie als grün oder rot werten)")
sys.exit(1 if kaputt else 0)
