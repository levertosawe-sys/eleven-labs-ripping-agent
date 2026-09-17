#!/usr/bin/env python3
"""Quellvideo/-audio → Transkript-Rohmaterial über ElevenLabs Scribe (JSON).

Warum Scribe statt eines Sprachmodells: Scribe misst Wort-Zeitstempel direkt
an der Tonspur — kein Zeitachsen-Drift über lange Videos, kein Stückeln, ein
Call fürs ganze Video. (Engine-Vergleich mit Messwerten: DECISIONS.md.)

Bekannte Macke: Scribe kann vereinzelt eine kurze Passage auslassen. Darum
listet das Script alle Wort-Lücken > 5 s als Prüfauftrag — die SKILL.md sagt,
wie ein Lücken-Fenster nachgeprüft wird (--start/--dauer).

Key kommt aus ELEVENLABS_API_KEY — Umgebung zuerst, sonst
~/.config/leichtkraut/.env. Kein Rückgriff auf andere Keys im System.

Aufruf:
  python3 transcribe.py <video-oder-audio> --out <roh.json> [--bloecke <transkript.md>]
  python3 transcribe.py <video> --out <fenster.json> --start 350 --dauer 12
Erfolg: Exit 0, die --out-Datei existiert, Meldung "… Wörter"; Lücken > 5 s
werden auf stderr gelistet (kein Fehler — ein Prüfauftrag).
Verbrauch wird nach .usage/elevenlabs.jsonl der AWMS-Wurzel mitgeschrieben (best effort).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

API_URL = "https://api.elevenlabs.io/v1/speech-to-text"
ENV_DATEI = Path.home() / ".config" / "leichtkraut" / ".env"
MODELL = "scribe_v1"
# Lücken über dieser Schwelle sind verdächtig: echte Erzähl-Pausen in Ads sind
# kürzer, ausgelassene Passagen (beobachtete Scribe-Macke) länger.
LUECKE_SEK = 5.0


def _env_wert(name: str) -> str | None:
    wert = os.environ.get(name)
    if wert and wert.strip():
        return wert.strip()
    if ENV_DATEI.exists():
        for zeile in ENV_DATEI.read_text(encoding="utf-8").splitlines():
            zeile = zeile.strip()
            if zeile.startswith("#") or "=" not in zeile:
                continue
            k, _, v = zeile.partition("=")
            if k.strip() == name and v.strip():
                return v.strip().strip("'\"")
    return None


def _ffmpeg(*args: str) -> None:
    lauf = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                          capture_output=True, text=True)
    if lauf.returncode != 0:
        raise SystemExit(f"ffmpeg fehlgeschlagen: {lauf.stderr.strip()[:300]}")


def _dauer(pfad: Path) -> float:
    lauf = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(pfad)],
        capture_output=True, text=True)
    try:
        return float(lauf.stdout.strip())
    except ValueError:
        raise SystemExit(f"ffprobe konnte die Dauer von {pfad} nicht lesen: {lauf.stderr.strip()[:200]}")


def _log_usage(audio_s: float) -> None:
    try:
        wurzel = next((p for p in Path(__file__).resolve().parents
                       if (p / "app" / "server.mjs").exists()), None)
        if wurzel is None:
            return
        import datetime
        eintrag = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "quelle": "singing-vsl-transkription",
            "modell": MODELL,
            "audio_s": round(audio_s, 1),
        }
        (wurzel / ".usage").mkdir(exist_ok=True)
        with open(wurzel / ".usage" / "elevenlabs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _scribe(key: str, clip: Path, sprache: str = "en") -> dict:
    """Ein Scribe-Call, Multipart über die Standardbibliothek.
    3 Versuche mit Backoff bei 429/5xx/Netz; andere 4xx = harter Fehler."""
    grenze = uuid.uuid4().hex
    felder = {"model_id": MODELL, "language_code": sprache,
              "timestamps_granularity": "word", "tag_audio_events": "false"}
    teile = []
    for k, v in felder.items():
        teile.append(f"--{grenze}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    teile.append(
        f"--{grenze}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"{clip.name}\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode()
        + clip.read_bytes() + b"\r\n")
    teile.append(f"--{grenze}--\r\n".encode())
    body = b"".join(teile)
    kontext = ssl.create_default_context()
    letzter: Exception | None = None
    for versuch in range(3):
        try:
            anfrage = Request(API_URL, data=body, method="POST", headers={
                "xi-api-key": key,
                "Content-Type": f"multipart/form-data; boundary={grenze}"})
            # Timeout 600 s: Upload + Verarbeitung liegen normal unter 2 min,
            # der Rest ist Luft für lange Videos und lahme Verbindungen.
            with urlopen(anfrage, timeout=600, context=kontext) as antwort:
                return json.loads(antwort.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            korper = ""
            try:
                korper = exc.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                pass
            if 400 <= exc.code < 500 and exc.code != 429:
                raise SystemExit(f"Scribe-Fehler {exc.code} (kein Retry sinnvoll): {korper}")
            letzter = exc
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            letzter = exc
        if versuch < 2:
            wartezeit = 3.0 * (2 ** versuch)
            print(f"[transkription] Fehler, neuer Versuch in {wartezeit:.0f}s "
                  f"({versuch + 2}/3): {letzter}", file=sys.stderr)
            time.sleep(wartezeit)
    raise SystemExit(f"Scribe nach 3 Versuchen gescheitert: {letzter}")


def _woerter(antwort: dict, versatz: float) -> list[dict]:
    raus = []
    for w in antwort.get("words", []):
        if w.get("type") != "word":
            continue
        raus.append({"text": str(w.get("text", "")),
                     "start": round(float(w["start"]) + versatz, 2),
                     "end": round(float(w["end"]) + versatz, 2)})
    return raus


def _luecken(woerter: list[dict]) -> list[tuple[float, float]]:
    raus = []
    for a, b in zip(woerter, woerter[1:]):
        if b["start"] - a["end"] > LUECKE_SEK:
            raus.append((a["end"], b["start"]))
    return raus


def _bloecke_bauen(woerter: list[dict], ziel: Path) -> int:
    """Wörter → Blöcke von ~4–10 s an Satzgrenzen, je Block eine (M:SS)-Zeile.
    Satzgrenzen werden nie gebrochen; ein überlanger Satz bleibt ein eigener Block."""
    saetze, akt = [], []
    for w in woerter:
        akt.append(w)
        if re.search(r"[.!?][\"']?$", w["text"]):
            saetze.append(akt)
            akt = []
    if akt:
        saetze.append(akt)

    ZIEL, MAX = 7.0, 10.0
    bloecke, akt = [], []
    for satz in saetze:
        if not akt:
            akt = list(satz)
            continue
        dauer_mit = satz[-1]["end"] - akt[0]["start"]
        dauer_ohne = akt[-1]["end"] - akt[0]["start"]
        if dauer_mit <= MAX and (dauer_ohne < ZIEL or dauer_mit <= ZIEL + 1.5):
            akt += satz
        else:
            bloecke.append(akt)
            akt = list(satz)
    if akt:
        bloecke.append(akt)

    zeilen = []
    for b in bloecke:
        text = re.sub(r"\s+", " ", " ".join(w["text"] for w in b)).strip()
        s = b[0]["start"]
        zeilen.append(f"({int(s // 60)}:{int(s % 60):02d}) {text}")
    ziel.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    return len(bloecke)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Video- oder Audiodatei")
    parser.add_argument("--out", required=True, help="Zieldatei fuer das Roh-JSON")
    parser.add_argument("--bloecke", help="optional: Transkript-Bloecke als Markdown hierhin")
    parser.add_argument("--start", type=float, help="Fenster-Modus: Startsekunde")
    parser.add_argument("--dauer", type=float, help="Fenster-Modus: Laenge in Sekunden")
    parser.add_argument("--sprache", default="en", help="Sprachcode fuer Scribe (Default en; de fuer den Wort-Cache der Sprechspur)")
    args = parser.parse_args()

    key = _env_wert("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit(f"ELEVENLABS_API_KEY fehlt (Umgebung oder {ENV_DATEI}). "
                         "Kein Ausweichen auf andere Keys — Viktor fragen.")
    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"Datei nicht gefunden: {video}")
    if (args.start is None) != (args.dauer is None):
        raise SystemExit("--start und --dauer nur zusammen (Fenster-Modus).")

    with tempfile.TemporaryDirectory(prefix="svsl-scribe-") as tmp:
        clip = Path(tmp) / "audio.mp3"
        schnitt = []
        if args.start is not None:
            schnitt = ["-ss", str(args.start), "-t", str(args.dauer)]
        # immer re-encodieren: -c-copy-Schnitte haben sich als unzuverlässiger
        # API-Input erwiesen, und 16 kHz mono reicht für Sprache
        _ffmpeg(*schnitt, "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                "-b:a", "64k", str(clip))
        audio_s = _dauer(clip)
        print(f"[transkription] Scribe-Call ({audio_s:.0f}s Audio)…", file=sys.stderr)
        antwort = _scribe(key, clip, args.sprache)

    versatz = args.start or 0.0
    woerter = _woerter(antwort, versatz)
    _log_usage(audio_s)

    ergebnis = {
        "quelle": str(video), "modell": MODELL,
        "audio_dauer_s": round(audio_s, 2), "versatz_s": versatz,
        "woerter_anzahl": len(woerter), "woerter": woerter,
        "antwort_roh": antwort,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2), encoding="utf-8")

    if not woerter:
        # Im Fenster-Modus ist Leere ein gültiger Befund (echte Pause/Musik) —
        # im Volllauf ist sie ein Fehler (falsche Datei? nur Musik?).
        if args.start is not None:
            print(f"[transkription] Fenster leer — Beleg für Pause/Musik → {out}", file=sys.stderr)
            return
        raise SystemExit("Kein einziges Wort — Audio prüfen (nur Musik? falsche Datei?).")

    for von, bis in _luecken(woerter):
        print(f"[transkription] LÜCKE {von:.1f}s–{bis:.1f}s ({bis - von:.1f}s) — "
              f"per Fenster nachprüfen (SKILL.md, Schritt 2)", file=sys.stderr)

    if args.bloecke:
        n = _bloecke_bauen(woerter, Path(args.bloecke))
        print(f"[transkription] {n} Blöcke → {args.bloecke}", file=sys.stderr)
    print(f"[transkription] {len(woerter)} Wörter, Sprache bis "
          f"{woerter[-1]['end']:.1f}s → {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
