#!/usr/bin/env python3
"""vmake_client.py — Vmake-Labs-API: eingebrannte Captions aus Video entfernen.

Selbst geschrieben am 20.08.2026, weil der Original-Client dem Buendel nicht beilag.
Signaturverfahren und Ablauf sind aus dem offiziellen Python-SDK v1.3.0 abgelesen
und live gegen den Server geprueft.

DREI FALLEN, ueber die man ohne Vorlage stolpert:
  1. Der Authorization-Header ist NICHT der Klartext-String, sondern dessen
     base64-Kodierung mit vorangestelltem "Bearer ".
  2. Der kanonische Pfad bekommt einen ANGEHAENGTEN Schraegstrich
     (/skill/config.json -> /skill/config.json/), sonst stimmt die Signatur nie.
  3. Der Body wird mit json.dumps in DEFAULT-Separatoren serialisiert (mit
     Leerzeichen). Kompaktes JSON ergibt einen anderen Hash und damit 401.
Signiert werden GENAU die Header, die im dict stehen — beim WAPI sind das
content-type/user-agent/x-sdk-date, beim Strategy-Host host/user-agent/x-sdk-date.

HOST: wapi-skill.vmake.ai. Das frueher im Skill genannte api.vmake.ai ist eine
Altlast mit abgelaufenem Zertifikat — nicht nutzen.

Keys: MT_AK / MT_SK in ~/.config/leichtkraut/.env (VMAKE_AK/VMAKE_SK als Alt-Namen).
Braucht: python3 -m pip install --user alibabacloud-oss-v2

Aufruf:
    vmake_client.py preflight
    vmake_client.py config
    vmake_client.py remove <datei|url> [--out <ziel.mp4>]
    vmake_client.py poll <task_id>
"""
import argparse, base64, hashlib, hmac, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

WAPI = "wapi-skill.vmake.ai"
ALGORITHM = "SDK-HMAC-SHA256"
USER_AGENT = "action-web-skill-v1.3.0"
ENV_DATEI = Path.home() / ".config" / "leichtkraut" / ".env"
GID_CACHE = Path.home() / ".cache" / "vmake" / "gid_cache.json"


def _env(*namen):
    for name in namen:
        wert = os.environ.get(name)
        if wert and wert.strip():
            return wert.strip()
    if ENV_DATEI.exists():
        for zeile in ENV_DATEI.read_text(encoding="utf-8").splitlines():
            zeile = zeile.strip()
            if zeile.startswith("#") or "=" not in zeile:
                continue
            k, _, v = zeile.partition("=")
            if k.strip() in namen and v.strip():
                return v.strip().strip("'\"")
    return None


AK = _env("MT_AK", "VMAKE_AK")
SK = _env("MT_SK", "VMAKE_SK")


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _log(text):
    print(f"[vmake] {text}", flush=True)


def signed(method, url, header, body_str=""):
    """Signiert nach SDK-HMAC-SHA256 und schickt ab. Gibt geparstes JSON zurueck."""
    if not AK or not SK:
        raise SystemExit(f"MT_AK/MT_SK fehlen (Umgebung oder {ENV_DATEI}). Viktor fragen.")
    from urllib.parse import urlparse
    teile = urlparse(url)
    stempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    header = dict(header)
    header["X-Sdk-Date"] = stempel

    namen = sorted(h.lower() for h in header)
    klein = {k.lower(): str(v).strip() for k, v in header.items()}
    kanon_header = "\n".join(f"{k}:{klein[k]}" for k in namen)
    pfad = teile.path if teile.path.endswith("/") else teile.path + "/"
    kanon = f"{method}\n{pfad}\n{teile.query}\n{kanon_header}\n{';'.join(namen)}\n{_sha(body_str)}"

    zu_signieren = f"{ALGORITHM}\n{stempel}\n{_sha(kanon)}"
    signatur = hmac.new(SK.encode(), zu_signieren.encode(), hashlib.sha256).hexdigest()
    klartext = f"{ALGORITHM} Access={AK}, SignedHeaders={';'.join(namen)}, Signature={signatur}"
    header["Authorization"] = "Bearer " + base64.b64encode(klartext.encode()).decode()

    daten = body_str.encode() if body_str else None
    anfrage = urllib.request.Request(url, data=daten, method=method, headers=header)
    try:
        with urllib.request.urlopen(anfrage, timeout=180) as antwort:
            return json.loads(antwort.read().decode())
    except urllib.error.HTTPError as f:
        raise SystemExit(f"HTTP {f.code} bei {method} {url}: {f.read().decode()[:300]}")


def wapi(pfad, body):
    body_str = json.dumps(body) if body else ""
    antwort = signed("POST", f"https://{WAPI}{pfad}",
                     {"User-Agent": USER_AGENT, "Content-Type": "application/json"}, body_str)
    meta = antwort.get("meta", {})
    if meta.get("code") != 0:
        raise SystemExit(f"Vmake meldet Fehler {meta.get('code')}: {meta.get('msg')}")
    return antwort.get("response", {})


def gid_holen(conf):
    """gid einmal holen und cachen — der Server vergibt sie im config-Aufruf."""
    if GID_CACHE.exists():
        try:
            g = json.loads(GID_CACHE.read_text()).get("gid")
            if g:
                return g
        except (json.JSONDecodeError, OSError):
            pass
    g = conf.get("gid", "")
    if g:
        GID_CACHE.parent.mkdir(parents=True, exist_ok=True)
        GID_CACHE.write_text(json.dumps({"gid": g}))
    return g


def config():
    return wapi("/skill/config.json", {"gid": "", "version": "v1.0.0"})


def strategie(conf, art):
    """art: 'upload' oder 'api' — holt die Token-Policy vom Region-Host."""
    regionen = (conf.get("algorithm") or {}).get("regions") or {}
    host = regionen.get("cn-north-4") or next(iter(regionen.values()), None)
    if not host:
        raise SystemExit("Keine Region in der Server-Konfiguration.")
    typ = (conf.get("algorithm") or {}).get("token_policy_type", "mtai")
    antwort = signed("GET", f"https://{host}/ai/token_policy?type={typ}",
                     {"Host": host, "User-Agent": USER_AGENT})
    daten = antwort["data"]["mtai"][art]
    return daten[daten["order"][0]]


def hochladen(policy, datei):
    import alibabacloud_oss_v2 as oss
    from urllib.parse import urlparse
    c = policy["credentials"]
    cfg = oss.config.load_default()
    cfg.credentials_provider = oss.credentials.StaticCredentialsProvider(
        c["access_key"], c["secret_key"], c.get("session_token"))
    endpunkt = policy["url"]
    wirt = urlparse(endpunkt if "//" in endpunkt else "https://" + endpunkt).netloc or endpunkt
    if wirt.startswith(policy["bucket"] + "."):
        wirt = wirt[len(policy["bucket"]) + 1:]
    cfg.endpoint = "https://" + wirt
    cfg.region = policy.get("region") or wirt.split(".")[0].replace("oss-", "")
    klient = oss.Client(cfg)
    groesse = os.path.getsize(datei)
    _log(f"Upload nach OSS: {os.path.basename(datei)} ({groesse/1048576:.1f} MB)")
    ergebnis = klient.put_object_from_file(
        oss.PutObjectRequest(bucket=policy["bucket"], key=policy["key"]), datei)
    if ergebnis.status_code != 200:
        raise SystemExit(f"OSS-Upload fehlgeschlagen: HTTP {ergebnis.status_code}")
    _log("Upload fertig.")
    return policy["data"]


def entfernen(datei, ziel):
    conf = config()
    voreinstellung = (conf.get("algorithm") or {}).get("invoke", {}).get("videoscreenclear")
    if not voreinstellung:
        raise SystemExit("Task 'videoscreenclear' steht in der Server-Konfiguration nicht zur Verfuegung.")
    gid = gid_holen(conf)

    medien_url = hochladen(strategie(conf, "upload"), datei)

    _log("Kontingent pruefen (consume) …")
    consume = wapi("/skill/consume.json",
                   {"url": medien_url, "task": "videoscreenclear", "gid": gid})
    context = consume.get("context", "")

    ai = strategie(conf, "api")
    body = {
        "params": json.dumps(voreinstellung.get("params") or {}),
        "context": context,
        "task": voreinstellung["task"],
        "task_type": "mtlab",
        "sync_timeout": ai["sync_timeout"],
        "init_images": [{"url": medien_url}],
    }
    url = ai["url"].rstrip("/") + "/" + ai["push_path"].lstrip("/")
    wirt = url.split("//", 1)[-1].split("/", 1)[0]
    _log(f"Task starten: {voreinstellung['task']}")
    antwort = signed("POST", url, {"Host": wirt, "User-Agent": USER_AGENT}, json.dumps(body))

    daten = antwort.get("data", {})
    if daten.get("status") == 9:
        task_id = str(daten["result"]["id"]).strip()
        _log(f"Asynchron angenommen, task_id={task_id}")
        antwort = pollen(task_id, ai)
    return abliefern(antwort, ziel)


def pollen(task_id, ai=None):
    if ai is None:
        ai = strategie(config(), "api")
    wirt = ai["url"].split("//", 1)[-1].split("/", 1)[0]
    url = ai["url"].rstrip("/") + "/" + ai["status_query"]["path"].lstrip("/") + f"?task_id={task_id}"
    pausen = [int(p.strip()) / 1000 for p in str(ai["status_query"]["durations"]).split(",") if p.strip()]
    pausen += [10.0] * 90  # Videos brauchen laut Skill deutlich laenger als gemeldet
    start = time.monotonic()
    for i, pause in enumerate(pausen, 1):
        time.sleep(pause)
        antwort = signed("GET", url, {"Host": wirt, "User-Agent": USER_AGENT})
        daten = antwort.get("data") or {}
        status, fortschritt = daten.get("status"), daten.get("progress")
        # ZWEI FALLEN, beide teuer bezahlt:
        #  a) status 0 heisst NICHT fertig — der Task laeuft dann noch. FERTIG ist status 10.
        #  b) Das Ergebnis steht in result.urls (bzw. result.data.media_info_list),
        #     NICHT in result.mtlab_res.media_info_list — das bleibt immer null.
        # Auch progress==1 ist kein Fertig-Signal: es steht dort minutenlang, waehrend der
        # Task noch in der Warteschlange haengt (waiting_time war hier 13,6 Minuten bei
        # nur 92 s echter Rechenzeit). Nur status 10 zaehlt.
        if status == 10 or (daten.get("result") or {}).get("urls"):
            _log(f"FERTIG nach {time.monotonic()-start:.0f}s ({i} Abfragen)")
            return antwort
        if status == 3:
            raise SystemExit(f"FEHLGESCHLAGEN: {json.dumps(antwort)[:400]}")
        if i == 1 or i % 6 == 0:
            rest = daten.get("predict_elapsed")
            hinweis = f" · geschaetzt {int(rest)/1000:.0f}s gesamt" if rest else ""
            _log(f"laeuft … {time.monotonic()-start:.0f}s (fortschritt {fortschritt}{hinweis})")
    raise SystemExit(f"Zeitueberschreitung. Spaeter fortsetzen: vmake_client.py poll {task_id}")


def _urls_finden(objekt):
    """Ergebnis-URLs. Zuerst result.urls — dort liegen sie wirklich."""
    if isinstance(objekt, dict):
        direkt = (objekt.get("result") or {}).get("urls")
        if direkt:
            return list(direkt)
    treffer = []
    if isinstance(objekt, dict):
        for k, v in objekt.items():
            if isinstance(v, str) and v.startswith("http") and k in ("url", "media_url", "image_url"):
                treffer.append(v)
            else:
                treffer += _urls_finden(v)
    elif isinstance(objekt, list):
        for v in objekt:
            treffer += _urls_finden(v)
    return treffer


def abliefern(antwort, ziel):
    urls = _urls_finden(antwort.get("data", antwort))
    if not urls:
        print(json.dumps(antwort, ensure_ascii=False)[:800])
        raise SystemExit("Keine Ergebnis-URL in der Antwort gefunden.")
    url = urls[0]
    _log(f"Ergebnis: {url[:90]}…")
    if ziel:
        Path(ziel).parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=600) as q, open(ziel, "wb") as z:
            while True:
                brocken = q.read(1 << 20)
                if not brocken:
                    break
                z.write(brocken)
        _log(f"Geladen nach {ziel} ({os.path.getsize(ziel)/1048576:.1f} MB)")
    return url


def main():
    p = argparse.ArgumentParser(description="Vmake — Captions aus Video entfernen")
    p.add_argument("befehl", choices=["preflight", "config", "remove", "poll"])
    p.add_argument("wert", nargs="?")
    p.add_argument("--out", default=None, help="Zieldatei fuer das bereinigte Video")
    a = p.parse_args()

    if a.befehl == "preflight":
        tasks = list((config().get("algorithm") or {}).get("invoke", {}))
        print("ok")
        print(f"  Tasks: {', '.join(tasks)}")
        print(f"  videoscreenclear: {'ja' if 'videoscreenclear' in tasks else 'NEIN'}")
    elif a.befehl == "config":
        print(json.dumps(config(), indent=2, ensure_ascii=False))
    elif a.befehl == "remove":
        if not a.wert:
            raise SystemExit("Aufruf: remove <datei> [--out ziel.mp4]")
        entfernen(a.wert, a.out)
    elif a.befehl == "poll":
        if not a.wert:
            raise SystemExit("Aufruf: poll <task_id>")
        abliefern(pollen(a.wert), a.out)


if __name__ == "__main__":
    main()
