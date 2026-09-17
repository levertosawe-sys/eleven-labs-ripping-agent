#!/usr/bin/env python3
"""Video-zu-Video-Lip-Sync über kie.ai (Modell volcengine/video-to-video-lip-sync). Eigenständig, nur curl + Python.

  python3 lipsync_kie.py <video.mp4> <audio.wav> <out.mp4> [lite]   → out.mp4 + out.mp4.job.json (enthält creditsConsumed)
  python3 lipsync_kie.py --pruefen                                  → Schlüssel + Kontostand, ohne Upload und ohne Kosten
  python3 lipsync_kie.py --abholen <taskId> <out.mp4> <video.mp4>   → Ergebnis eines schon bezahlten Auftrags holen
  python3 lipsync_kie.py --kennzeichnen <out.mp4> <video.mp4>       → Farbkennzeichnung des Eingangs auf eine vorhandene Ausgabe

Schlüssel: Umgebungsvariable KIE_API_KEY; sonst die erste .env mit KIE_API_KEY= auf dem Weg vom Arbeitsordner nach oben;
sonst ~/.config/leichtkraut/.env. Der Schlüssel wird nie ausgegeben.
Ablauf: beide Dateien hochladen (kie nimmt nur URLs; Links leben 24 h) → createTask (taskId steht in der Ausgabe) →
recordInfo alle 10 s, höchstens 1500 s (beobachtet 37–933 s) → Ergebnis laden → Farbkennzeichnung übertragen.

Farbkennzeichnung: kie reicht die YUV-Werte des Eingangs durch (Abweichung U/V < 0,1, Luma ~1 Stufe dunkler), schreibt aber
KEINE Farbkennzeichnung. Ein bt709-Eingang wird dann beim Dekodieren mit der bt601-Standardmatrix gelesen → Hauttöne verschieben
sich (Farbstich Ø 3,6 statt 1,0). Darum wird die Kennzeichnung des Eingangs per h264_metadata in den Bitstrom geschrieben —
ohne Neu-Encode, YUV bleibt bitgleich.

Exit-Codes: 0 ok · 2 „server busy" (0 Credits, später wiederholen) · 3 „Credits insufficient" (402; auch bei genug Guthaben,
wenn parallele Aufträge reservieren → einzeln wiederholen) · 4 keine Antwort in 1500 s (Auftrag läuft bei kie weiter und ist
bezahlt → NICHT neu starten, sondern --abholen mit der taskId) · 1 alles andere (Meldung lesen).
"""
import json, os, subprocess, sys, time
from pathlib import Path

API = "https://api.kie.ai/api/v1/jobs/createTask"
STATUS = "https://api.kie.ai/api/v1/jobs/recordInfo?taskId="
UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
KONTO = "https://api.kie.ai/api/v1/chat/credit"
VUI = {"primaries": {"bt709": 1, "bt470m": 4, "bt470bg": 5, "smpte170m": 6, "smpte240m": 7, "bt2020": 9},
       "transfer": {"bt709": 1, "gamma22": 4, "gamma28": 5, "smpte170m": 6, "smpte240m": 7, "iec61966-2-1": 13, "bt2020-10": 14},
       "matrix": {"bt709": 1, "fcc": 4, "bt470bg": 5, "smpte170m": 6, "smpte240m": 7, "bt2020nc": 9}}

def schluessel():
    if os.environ.get("KIE_API_KEY"): return os.environ["KIE_API_KEY"].strip()
    orte = [p / ".env" for p in [Path.cwd(), *Path.cwd().parents]] + [Path.home() / ".config" / "leichtkraut" / ".env"]
    for env in orte:
        if env.is_file():
            for zeile in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                if zeile.startswith("KIE_API_KEY="): return zeile.split("=", 1)[1].strip().strip('"').strip("'")
    print("FEHLER: KIE_API_KEY fehlt (Umgebung oder .env) — ohne Schlüssel wird nichts gerufen.", file=sys.stderr); sys.exit(1)

def curl_json(args, timeout=600):
    p = subprocess.run(["curl", "-s"] + args, capture_output=True, text=True, timeout=timeout)
    try: return json.loads(p.stdout)
    except Exception: return {"_roh": (p.stdout or p.stderr)[:400]}

def kontostand(key):
    d = curl_json(["-H", f"Authorization: Bearer {key}", KONTO], timeout=60)
    return d.get("data") if isinstance(d.get("data"), (int, float)) else None

def hochladen(pfad, key):
    typ = "video/mp4" if str(pfad).endswith(".mp4") else "audio/wav"
    d = curl_json(["-X", "POST", UPLOAD, "-H", f"Authorization: Bearer {key}", "-F", "uploadPath=awms/lipsync",
                   "-F", f"fileName={Path(pfad).name}", "-F", f"file=@{pfad};type={typ}"])
    url = (d.get("data") or {}).get("fileUrl") or (d.get("data") or {}).get("downloadUrl")
    if not url: print(f"FEHLER: Upload ohne URL für {pfad}: {json.dumps(d)[:300]}", file=sys.stderr); sys.exit(1)
    return url

def kennzeichnen(out, eingang):
    """Farbkennzeichnung des Eingangs auf die Ausgabe übertragen (Bitstrom, kein Neu-Encode). Rückgabe: Beschreibung."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=color_primaries,color_transfer,color_space,color_range", "-of", "json", eingang], capture_output=True, text=True)
    try: s = json.loads(r.stdout)["streams"][0]
    except Exception: return "Eingang nicht lesbar — Kennzeichnung übersprungen"
    teile = []
    if s.get("color_primaries") in VUI["primaries"]: teile.append(f"colour_primaries={VUI['primaries'][s['color_primaries']]}")
    if s.get("color_transfer") in VUI["transfer"]: teile.append(f"transfer_characteristics={VUI['transfer'][s['color_transfer']]}")
    if s.get("color_space") in VUI["matrix"]: teile.append(f"matrix_coefficients={VUI['matrix'][s['color_space']]}")
    if s.get("color_range") in ("tv", "pc"): teile.append(f"video_full_range_flag={1 if s['color_range'] == 'pc' else 0}")
    if not teile: return "Eingang ohne Farbkennzeichnung — nichts zu übertragen"
    tmp = out + ".tag.mp4"
    p = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c", "copy", "-bsf:v", "h264_metadata=" + ":".join(teile), tmp],
                       capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(tmp):
        print(f"FEHLER: Kennzeichnung fehlgeschlagen: {p.stderr[:300]}", file=sys.stderr); sys.exit(1)
    os.replace(tmp, out)
    return "Farbkennzeichnung übertragen: " + ", ".join(teile)

def warten_und_laden(task, key, out, video):
    t0 = time.time(); rec = None
    while time.time() - t0 < 1500:
        time.sleep(10)
        s = curl_json(["-H", f"Authorization: Bearer {key}", STATUS + task], timeout=60)
        rec = s.get("data") if isinstance(s.get("data"), dict) else None
        if rec and rec.get("state") in ("success", "fail"): break
    if not rec or rec.get("state") not in ("success", "fail"):
        print(f"Keine Antwort in 1500 s — Auftrag läuft bei kie weiter. Später abholen: lipsync_kie.py --abholen {task} {out} {video}", file=sys.stderr)
        sys.exit(4)
    if rec.get("state") != "success":
        print(f"Job nicht erfolgreich: {json.dumps(rec)[:400]}", file=sys.stderr)
        sys.exit(2 if "busy" in str(rec.get("failMsg", "")).lower() else 1)
    json.dump(rec, open(out + ".job.json", "w"), indent=1)
    urls = json.loads(rec.get("resultJson") or "{}").get("resultUrls") or []
    if not urls: print("FEHLER: Job ohne resultUrls", file=sys.stderr); sys.exit(1)
    subprocess.run(["curl", "-sL", urls[0], "-o", out], check=True)
    if not os.path.exists(out) or os.path.getsize(out) < 1000: print("FEHLER: Ergebnis-Download leer", file=sys.stderr); sys.exit(1)
    print(kennzeichnen(out, video))
    print("->", out, os.path.getsize(out), "bytes ·", rec.get("creditsConsumed"), "Credits")

def main():
    if len(sys.argv) > 3 and sys.argv[1] == "--kennzeichnen":
        print(sys.argv[2], "·", kennzeichnen(sys.argv[2], sys.argv[3])); return
    key = schluessel()
    if len(sys.argv) > 1 and sys.argv[1] == "--pruefen":
        k = kontostand(key)
        print("kie-Schlüssel ok · Kontostand:", k if k is not None else "unbekannt (Antwort unlesbar)"); return
    if len(sys.argv) > 4 and sys.argv[1] == "--abholen":
        return warten_und_laden(sys.argv[2], key, sys.argv[3], sys.argv[4])
    if len(sys.argv) < 4: print(__doc__); sys.exit(1)
    video, audio, out = sys.argv[1], sys.argv[2], sys.argv[3]; mode = sys.argv[4] if len(sys.argv) > 4 else "lite"
    for p in (video, audio):
        if not os.path.exists(p): print(f"FEHLER: Datei fehlt: {p}", file=sys.stderr); sys.exit(1)
    vurl, aurl = hochladen(video, key), hochladen(audio, key)
    body = {"model": "volcengine/video-to-video-lip-sync",
            "input": {"mode": mode, "video_url": vurl, "audio_url": aurl, "separate_vocal": False, "open_scenedet": False,
                      "align_audio": True, "align_audio_reverse": False, "templ_start_seconds": 0}}
    d = curl_json(["-X", "POST", API, "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json", "--data-binary", json.dumps(body)])
    task = (d.get("data") or {}).get("taskId") if isinstance(d.get("data"), dict) else None
    if not task:
        print(f"createTask fehlgeschlagen: {json.dumps(d)[:300]}", file=sys.stderr)
        sys.exit(3 if d.get("code") == 402 else 1)
    print("taskId:", task, flush=True)
    open(out + ".task", "w").write(task)
    warten_und_laden(task, key, out, video)

if __name__ == "__main__": main()
