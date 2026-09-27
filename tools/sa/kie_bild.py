#!/usr/bin/env python3
"""kie_bild.py — Frame-Edit und Clip-Animation der Custom-Clip-Strecke über kie.ai.

Ersetzt die Higgsfield CLI. Beide Etappen laufen über denselben Anbieter, der in
dieser Kette ohnehin schon Suno und Gemini stellt — ein Konto, ein Schlüssel.

    edit      Frame umbranden  -> Modell nano-banana-2   (Nano Banana 2)
    animate   Clip animieren   -> Modell kling-3.0/video (Kling 3.0, nur Startbild)

Schlüssel: KIE_API_KEY aus der Umgebung, sonst ~/.config/leichtkraut/.env.
Nur Standardbibliothek — kein pip, läuft mit dem System-Python.

Aufrufe (aus der Projekt-Wurzel):

    python3 tools/sa/kie_bild.py edit \\
        --frame  _work/clips/c285_start.png \\
        --referenz "datenbanken/brand-solena/Product Reference/beutel.png" \\
        --prompt-datei _work/clips/c285_prompt.txt \\
        --out    _work/clips/c285_start_sol.png

    python3 tools/sa/kie_bild.py animate \\
        --startbild _work/clips/c285_start_sol.png \\
        --prompt-datei _work/clips/c285_kling.txt \\
        --sekunden 3 \\
        --out _work/clips/c285_roh.mp4

Beide geben am Ende den lokalen Pfad aus und schreiben das Job-JSON daneben als
`<out>.job.json` — der Beleg, den der Lauf-Bericht zitiert.
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

API = "https://api.kie.ai/api/v1/jobs/createTask"
STATUS = "https://api.kie.ai/api/v1/jobs/recordInfo?taskId="
UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
ENV_DATEI = Path.home() / ".config" / "leichtkraut" / ".env"

MODELL_EDIT = "nano-banana-2"
MODELL_VIDEO = "kling-3.0/video"


def schluessel():
    """KIE_API_KEY — Umgebung zuerst, sonst die .env. Kein Rückgriff auf andere Keys."""
    wert = os.environ.get("KIE_API_KEY")
    if wert:
        return wert.strip()
    if ENV_DATEI.exists():
        for zeile in ENV_DATEI.read_text(encoding="utf-8").splitlines():
            if zeile.startswith("KIE_API_KEY="):
                return zeile.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(
        "KIE_API_KEY fehlt (Umgebung oder %s). Ohne Schlüssel wird nichts gerufen." % ENV_DATEI
    )


def _post(url, daten, kopf, timeout=180):
    """POST über curl. Grund (gemessen 23.08.2026, SOL 002): urllib wird von der
    Cloudflare-Front von kie.ai mit HTTP 403 / error 1010 abgewiesen (TLS-/UA-
    Fingerprint), curl kommt durch — dieselbe Route, die suno<NNN>_lib.py ohnehin nutzt."""
    import subprocess as _sp, tempfile as _tf, os as _os
    kopf_args = []
    for k, v in kopf.items():
        if k.lower() in ("content-length",):
            continue
        kopf_args += ["-H", "%s: %s" % (k, v)]
    with _tf.NamedTemporaryFile(delete=False) as f:
        f.write(daten if isinstance(daten, bytes) else daten.encode("utf-8"))
        tmp = f.name
    try:
        p = _sp.run(["curl", "-s", "-X", "POST", url] + kopf_args +
                    ["--data-binary", "@" + tmp], capture_output=True, text=True, timeout=timeout)
    finally:
        _os.unlink(tmp)
    try:
        return json.loads(p.stdout)
    except Exception:
        raise SystemExit("kie.ai Antwort unlesbar auf %s\n%s" % (url, (p.stdout or p.stderr)[:600]))


def hochladen(pfad, key):
    """Lokale Datei -> öffentliche URL. kie.ai nimmt nur URLs, keine Uploads im Job.

    Die Datei liegt dort 24 Stunden; danach ist der Link tot. Für einen Lauf reicht
    das, für ein Archiv nicht — das Original bleibt lokal die Wahrheit.
    """
    pfad = Path(pfad)
    if not pfad.exists():
        raise SystemExit("Datei fehlt: %s" % pfad)
    typ = mimetypes.guess_type(pfad.name)[0] or "application/octet-stream"
    grenze = "----awms%s" % uuid.uuid4().hex
    teile = []
    for feld, wert in (("uploadPath", "images/awms"), ("fileName", pfad.name)):
        teile.append(
            ('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (grenze, feld, wert)).encode()
        )
    teile.append(
        (
            '--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
            "Content-Type: %s\r\n\r\n" % (grenze, pfad.name, typ)
        ).encode()
    )
    teile.append(pfad.read_bytes())
    teile.append(("\r\n--%s--\r\n" % grenze).encode())
    koerper = b"".join(teile)
    import subprocess as _sp
    p = _sp.run(["curl", "-s", "-X", "POST", UPLOAD,
                 "-H", "Authorization: Bearer %s" % key,
                 "-F", "uploadPath=images/awms",
                 "-F", "fileName=%s" % pfad.name,
                 "-F", "file=@%s;type=%s" % (pfad, typ)],
                capture_output=True, text=True, timeout=600)
    try:
        antwort = json.loads(p.stdout)
    except Exception:
        raise SystemExit("Upload-Antwort unlesbar: %s" % ((p.stdout or p.stderr)[:400]))
    url = (antwort.get("data") or {}).get("fileUrl") or (antwort.get("data") or {}).get("downloadUrl")
    if not url:
        raise SystemExit("Upload ohne fileUrl: %s" % json.dumps(antwort)[:400])
    return url


def job(modell, eingabe, key, warte_max=1800):
    """Job anlegen und bis zum Ergebnis pollen. Läuft im Vordergrund, mit Deckel."""
    antwort = _post(
        API,
        json.dumps({"model": modell, "input": eingabe}).encode("utf-8"),
        {"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
    )
    task = (antwort.get("data") or {}).get("taskId")
    if not task:
        raise SystemExit("kie.ai gab keine taskId: %s" % json.dumps(antwort)[:400])
    print("  Job %s (%s) …" % (task, modell), flush=True)

    begonnen = time.time()
    while True:
        if time.time() - begonnen > warte_max:
            raise SystemExit(
                "Job %s nach %d s nicht fertig — abgebrochen. Im Chat melden, nicht "
                "blind neu würfeln (der Job kann trotzdem noch abrechnen)." % (task, warte_max)
            )
        time.sleep(6)
        # Status-Poll über curl (siehe _post-Kommentar: urllib wird von Cloudflare geblockt)
        import subprocess as _sp
        _p = _sp.run(["curl", "-s", STATUS + task,
                      "-H", "Authorization: Bearer %s" % key],
                     capture_output=True, text=True, timeout=60)
        try:
            stand = json.loads(_p.stdout)
        except Exception:
            continue  # Netz-Zucker: weiter pollen, der Job läuft ja
        daten = stand.get("data") or {}
        zustand = str(daten.get("state") or daten.get("status") or "").lower()
        if zustand in ("success", "succeeded", "completed"):
            roh = daten.get("resultJson")
            ergebnis = json.loads(roh) if isinstance(roh, str) else (roh or {})
            urls = ergebnis.get("resultUrls") or []
            if not urls:
                raise SystemExit("Job fertig, aber ohne resultUrls: %s" % json.dumps(daten)[:400])
            return urls[0], daten
        if zustand in ("fail", "failed", "error"):
            raise SystemExit(
                "Job %s fehlgeschlagen: %s" % (task, daten.get("failMsg") or json.dumps(daten)[:400])
            )


def herunterladen(url, ziel):
    """Ergebnis holen — über curl (urllib bekommt von der Cloudflare-Front 403)."""
    import subprocess as _sp
    Path(ziel).parent.mkdir(parents=True, exist_ok=True)
    p = _sp.run(["curl", "-sL", "--fail", "-o", str(ziel), url], capture_output=True, text=True, timeout=600)
    if p.returncode != 0 or not Path(ziel).exists() or Path(ziel).stat().st_size == 0:
        raise SystemExit("Download fehlgeschlagen (%s): %s" % (url, (p.stderr or "")[:300]))
    return Path(ziel)
def prompt_lesen(args):
    if args.prompt_datei:
        return Path(args.prompt_datei).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt.strip()
    raise SystemExit("Kein Prompt: --prompt-datei oder --prompt angeben.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    unter = ap.add_subparsers(dest="befehl", required=True)

    e = unter.add_parser("edit", help="Frame umbranden (Nano Banana 2)")
    e.add_argument("--frame", required=True, help="Original-Frame = Referenz (1)")
    e.add_argument("--referenz", required=True, help="Tier-1-Produktreferenz = Referenz (2)")
    e.add_argument("--prompt-datei")
    e.add_argument("--prompt")
    e.add_argument("--out", required=True)
    e.add_argument("--aspect", default="9:16")
    e.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])

    a = unter.add_parser("animate", help="Clip animieren (Kling 3.0, nur Startbild)")
    a.add_argument("--startbild", required=True)
    a.add_argument("--endbild", default=None, help="optional: Ziel-Frame als zweites Bild (Start+Ende) — nur wenn der Start-Frame das Produkt nicht vollständig zeigt")
    a.add_argument("--prompt-datei")
    a.add_argument("--prompt")
    a.add_argument("--sekunden", type=int, required=True, help="ganze Sekunden, 3-15")
    a.add_argument("--out", required=True)
    a.add_argument("--aspect", default="9:16")
    a.add_argument("--mode", default="std", choices=["std", "pro", "4K"])

    args = ap.parse_args()
    key = schluessel()
    text = prompt_lesen(args)

    if args.befehl == "edit":
        print("Upload Frame + Referenz …", flush=True)
        bilder = [hochladen(args.frame, key), hochladen(args.referenz, key)]
        url, roh = job(
            MODELL_EDIT,
            {
                "prompt": text,
                "image_input": bilder,
                "aspect_ratio": args.aspect,
                "resolution": args.resolution,
                "output_format": "png",
            },
            key,
        )
    else:
        if not 3 <= args.sekunden <= 15:
            raise SystemExit("--sekunden muss 3-15 sein (API-Minimum ist 3).")
        print("Upload Startbild …", flush=True)
        url, roh = job(
            MODELL_VIDEO,
            {
                # Schema-Stand 23.08.2026 (gemessen, SOL 002): "duration" ist ein STRING-Enum
                # und "multi_shots" ist PFLICHT — fehlt es, antwortet die API mit
                # HTTP 422 "multi_shots cannot be empty". aspect_ratio entfällt, weil das
                # Modell es aus dem Startbild ableitet (9:16 bleibt damit erhalten).
                "prompt": text,
                "image_urls": [hochladen(args.startbild, key)] + ([hochladen(args.endbild, key)] if args.endbild else []),
                "duration": str(int(args.sekunden)),
                "mode": args.mode,
                "sound": False,
                "multi_shots": False,
            },
            key,
        )

    ziel = herunterladen(url, args.out)
    Path(str(args.out) + ".job.json").write_text(
        json.dumps(roh, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("✅ %s (%.1f MB) · Beleg: %s.job.json" % (ziel, ziel.stat().st_size / 1e6, args.out))


if __name__ == "__main__":
    main()
