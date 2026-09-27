"""Caption-Engine: aus Ad-Ton + Skript lesbare Caption-Häppchen mit exakten Wortzeiten.

Die REGELN (wie eine Caption auszusehen hat) stehen in skills/captions.md — hier steht
nur die Mechanik, die sie ausführt. Ändern sich die Regeln, ändert sich beides.

Zwei Schritte:
  1. wortzeiten()  — ElevenLabs Forced Alignment: Ton + Skript -> exakte Zeit je Wort.
     Der Text bleibt Viktors Skript (nie verhört), die Zeit kommt aus dem echten Ton.
  2. haeppchen()   — die Wörter zu kurzen Gruppen schneiden (Regeln aus skills/captions.md).
"""
from __future__ import annotations

import json
import re
import urllib.request
import uuid
from pathlib import Path

FA_URL = "https://api.elevenlabs.io/v1/forced-alignment"

# Satzzeichen, die wegfallen. Der Apostroph fehlt bewusst: er steckt IN Wörtern
# („it's", „geht's") und ist kein Satzzeichen.
RAND_ZEICHEN = r'[.,;:!?…"„“”»«()\[\]\-–—]'
NACHHALL = 0.15   # Sekunden, die ein Häppchen nach dem letzten Wort stehen bleibt:
                  # Das Auge braucht den Rest eines Lidschlags, sonst blitzt es nur.


def skript_bauen(stuecke: list[str]) -> str:
    """Die Skript-Stücke zu einem Skript verbinden und Wort-Dopplungen an den Grenzen
    entfernen.

    Warum nötig: Die Stücke kommen aus dem Voice Trimmer, der den Segment-Text
    proportional zur Zeit aufteilt und dabei an Wortgrenzen NACH AUSSEN rundet —
    zwei Nachbar-Stücke können deshalb dasselbe Wort greifen. Das ist erwartetes
    Verhalten der Quelle, kein Defekt: Wer hier abbricht, bekommt nie Captions.
    Doppeltes Wort raus, weiter.
    """
    raus: list[str] = []
    for stueck in [s.strip() for s in stuecke if s and s.strip()]:
        w = stueck.split()
        if raus and w and raus[-1].strip('.,!?;:').lower() == w[0].strip('.,!?;:').lower():
            w = w[1:]  # Grenz-Dopplung: das Wort steht schon da
        raus.extend(w)
    return " ".join(raus)


def wortzeiten(audio_pfad: Path, skript: str, key: str, timeout: int = 180) -> list[dict]:
    """Exakte Wortzeiten via ElevenLabs Forced Alignment.

    Gibt [{text, start, end, loss}] zurück (Zeiten in Sekunden, relativ zum Audio).
    Leerzeichen-Einträge der API werden verworfen — wir arbeiten auf Wörtern.
    Wirft RuntimeError mit sprechender Meldung, wenn die API nicht mitspielt.
    """
    audio = Path(audio_pfad).read_bytes()
    b = uuid.uuid4().hex
    teile = [
        f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{Path(audio_pfad).name}"\r\n'
        f'Content-Type: audio/mpeg\r\n\r\n'.encode() + audio + b"\r\n",
        f'--{b}\r\nContent-Disposition: form-data; name="text"\r\n\r\n{skript}\r\n'.encode(),
        f"--{b}--\r\n".encode(),
    ]
    req = urllib.request.Request(
        FA_URL, data=b"".join(teile), method="POST",
        headers={"xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Forced Alignment {e.code}: {e.read().decode('utf-8', 'replace')[:200]}")
    except Exception as e:
        raise RuntimeError(f"Forced Alignment nicht erreichbar: {e}")
    roh = d.get("words") or []
    if not roh:
        raise RuntimeError("Forced Alignment lieferte keine Wörter.")
    # loss kann fehlen -> None durchreichen, nicht 0: eine 0 würde jede Güte-Prüfung
    # klaglos bestehen lassen und damit still das Gegenteil ihres Zwecks tun.
    return [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"]),
             "loss": (float(w["loss"]) if w.get("loss") is not None else None)}
            for w in roh if str(w.get("text", "")).strip()]


def saeubern(wort: str) -> list[str]:
    """Ein Wort caption-tauglich machen: Satzzeichen an den Rändern weg, innere
    Bindestriche zu Wortgrenzen. Gibt eine LISTE zurück, weil „money-back" zu zwei
    Wörtern wird. Leere Liste, wenn nur ein Satzzeichen übrig war.

    Kommas/Punkte INNERHALB von Zahlen bleiben („50,000", „3.5") — dort trennen sie
    nicht Sätze, sondern gehören zur Zahl.
    """
    w = str(wort).strip()
    if not w:
        return []
    # Bindestrich zwischen Buchstaben/Ziffern = Wortgrenze
    w = re.sub(r"(?<=[\w])[-–—](?=[\w])", " ", w)
    raus = []
    for teil in w.split():
        # Zahl mit Trennzeichen (50,000 / 3.5) unangetastet lassen
        if re.fullmatch(r"\d[\d.,]*\d|\d", teil):
            raus.append(teil)
            continue
        teil = re.sub(f"^{RAND_ZEICHEN}+|{RAND_ZEICHEN}+$", "", teil)
        if teil:
            raus.append(teil)
    return raus


def _satzende(wort: str) -> bool:
    """Endete das ORIGINAL-Wort einen Satz/Teilsatz? Das ist die beste natürliche
    Bruchstelle — auch wenn das Zeichen selbst nie in der Caption landet."""
    return bool(re.search(r"""[.!?,;:…]["»«')\]]*$""", str(wort).strip()))


def _passt(gruppe: list[dict], max_woerter: int, max_zeichen: int) -> bool:
    return (len(gruppe) <= max_woerter
            and len(" ".join(x["text"] for x in gruppe)) <= max_zeichen)


ZIEL_WOERTER = 3      # Referenz-Ads: meist 3-4 Wörter je Häppchen
NAHT_BONUS = 8.0      # Gewicht der Sprechpause gegen die Größen-Abweichung


def _teilen(gruppe: list[dict], max_woerter: int, max_zeichen: int) -> list[list[dict]]:
    """Eine zu lange Gruppe in Häppchen teilen — ALLE Schnitte gemeinsam optimiert.

    Warum nicht Schnitt für Schnitt: Jede Naht einzeln auf „die größte Lücke" zu
    setzen, klingt vernünftig, erzeugt aber Waisen und Überlängen — zwei unabhängig
    gewählte Schnitte können nebeneinander rutschen („ich" allein) oder weit
    auseinander („stundenlang auf Beute herum", 27 Zeichen). Deshalb sucht eine
    Dynamische Programmierung die beste GESAMT-Aufteilung: Häppchen nahe der
    Zielgröße, Schnitte möglichst auf Sprechpausen, Grenzen als harte Bedingung.
    """
    n = len(gruppe)
    if _passt(gruppe, max_woerter, max_zeichen) or n < 2:
        return [gruppe]

    def zeichen(j, i):
        return len(" ".join(x["text"] for x in gruppe[j:i]))

    def luecke_vor(j):
        return 0.0 if j == 0 else max(0.0, gruppe[j]["start"] - gruppe[j - 1]["end"])

    unendlich = float("inf")
    kosten = [unendlich] * (n + 1)
    herkunft = [0] * (n + 1)
    kosten[0] = 0.0
    for i in range(1, n + 1):
        for j in range(max(0, i - max_woerter), i):
            if kosten[j] == unendlich or zeichen(j, i) > max_zeichen:
                continue
            # Abweichung von der Zielgröße quadratisch, echte Naht am Schnitt belohnt
            wert = kosten[j] + (i - j - ZIEL_WOERTER) ** 2 - NAHT_BONUS * luecke_vor(j)
            if wert < kosten[i]:
                kosten[i], herkunft[i] = wert, j
    if kosten[n] == unendlich:  # kein Weg (z.B. ein Wort länger als max_zeichen)
        return [gruppe[i:i + max_woerter] for i in range(0, n, max_woerter)]
    schnitte, i = [], n
    while i > 0:
        schnitte.append((herkunft[i], i))
        i = herkunft[i]
    return [gruppe[a:b] for a, b in reversed(schnitte)]


def haeppchen(woerter: list[dict], max_woerter: int = 4, max_zeichen: int = 26,
              pause: float = 0.28, luecke_zu: float = 0.6) -> list[dict]:
    """Wörter zu Caption-Häppchen gruppieren.

    Zwei Durchgänge, damit Sinngrenzen vor der Zählung kommen (Regel aus
    skills/captions.md): erst an Satzzeichen-Stellen und Sprechpausen trennen, dann
    zu lange Reste an ihrer besten inneren Naht teilen.

    max_woerter=4 / max_zeichen=26: Die Referenz-Ads zeigen 2-5 Wörter je Häppchen;
      deutsche Wörter sind länger, deshalb zusätzlich eine Zeichen-Grenze.
    pause=0.28: Sprechpausen ab ~0,3 s sind hörbare Phrasengrenzen — dort bricht auch
      ein Mensch um.
    luecke_zu=0.6: Kurze Lücken zwischen Häppchen werden zugezogen (Caption steht
      durchgehend); bei echten Pausen ab 0,6 s verschwindet sie stattdessen.

    Gibt [{text, t, dauer, woerter:[{text,start,end}]}] zurück — start/end der Wörter
    sind RELATIV zum Häppchen-Anfang (so will es CapCut).
    """
    # Durchgang 1: nur an Sinngrenzen trennen (Satzzeichen im Skript, Sprechpausen)
    roh: list[list[dict]] = []
    aktuell: list[dict] = []
    for w in woerter:
        teile = saeubern(w["text"])
        if not teile:
            continue
        if aktuell and (w["start"] - aktuell[-1]["end"] >= pause or aktuell[-1]["bruch"]):
            roh.append(aktuell)
            aktuell = []
        # Ein Original-Wort kann zu mehreren werden (money-back): Zeit gleichmäßig teilen
        spanne = max(0.01, w["end"] - w["start"]) / len(teile)
        for k, t in enumerate(teile):
            aktuell.append({"text": t, "start": w["start"] + k * spanne,
                            "end": w["start"] + (k + 1) * spanne, "bruch": False})
        aktuell[-1]["bruch"] = _satzende(w["text"])
    if aktuell:
        roh.append(aktuell)

    # Durchgang 2: zu lange Gruppen an ihrer besten Naht teilen
    gruppen: list[list[dict]] = []
    for g in roh:
        gruppen.extend(_teilen(g, max_woerter, max_zeichen))

    # Durchgang 2.5: zu KURZ stehende Häppchen mit einem Nachbarn verschmelzen.
    # Steht ein Häppchen kürzer als MIN_STAND (unten definiert), wurde es zu klein
    # geschnitten — eine schnell gesprochene Phrase, dicht gefolgt vom nächsten. Statt
    # es aufblitzen zu lassen (oder den Export daran scheitern zu lassen), mit dem
    # Nachbarn verbinden, der die Größengrenze noch hält; der kleinere Nachbar zuerst,
    # damit die Zielgröße gewahrt bleibt. Geht kein Merge (beide Nachbarn schon voll),
    # bleibt es kurz — pruefen() meldet es, der Export duldet es. Für saubere Ads ohne
    # zu kurze Häppchen läuft diese Schleife leer: die Ausgabe ändert sich nicht.
    def _stand(gi):
        t1 = gruppen[gi][-1]["end"]
        if gi + 1 < len(gruppen):
            nx = gruppen[gi + 1][0]["start"]
            t1 = nx if (nx - t1) < luecke_zu else t1 + NACHHALL
        else:
            t1 += NACHHALL
        return t1 - gruppen[gi][0]["start"]

    i = 0
    while len(gruppen) > 1 and i < len(gruppen):
        if _stand(i) >= MIN_STAND:
            i += 1
            continue
        nach_ok = i + 1 < len(gruppen) and _passt(gruppen[i] + gruppen[i + 1], max_woerter, max_zeichen)
        vor_ok = i > 0 and _passt(gruppen[i - 1] + gruppen[i], max_woerter, max_zeichen)
        if nach_ok and (not vor_ok or len(gruppen[i + 1]) <= len(gruppen[i - 1])):
            gruppen[i] += gruppen[i + 1]
            del gruppen[i + 1]          # dieselbe Stelle nochmal prüfen (i bleibt)
        elif vor_ok:
            gruppen[i - 1] += gruppen[i]
            del gruppen[i]
            i -= 1
        else:
            i += 1                      # kein Merge möglich — kurz lassen

    raus = []
    for gi, g in enumerate(gruppen):
        t0, t1 = g[0]["start"], g[-1]["end"]
        # Lücke zum nächsten Häppchen zuziehen, wenn sie klein ist
        if gi + 1 < len(gruppen):
            naechster = gruppen[gi + 1][0]["start"]
            t1 = naechster if (naechster - t1) < luecke_zu else t1 + NACHHALL
        else:
            t1 += NACHHALL
        raus.append({
            "text": " ".join(x["text"] for x in g),
            "t": round(t0, 3),
            "dauer": round(t1 - t0, 3),
            "woerter": [{"text": x["text"], "start": round(x["start"] - t0, 3),
                         "end": round(x["end"] - t0, 3)} for x in g],
        })
    return raus


MIN_STAND = 0.25  # Sekunden: kürzer als ein Lidschlag ist nicht lesbar, nur ein Blitzen


def pruefen(haeppchen_liste: list[dict], max_woerter: int = 4, max_zeichen: int = 26,
            min_stand: float = MIN_STAND) -> list[str]:
    """Die Häppchen gegen die Regeln aus skills/captions.md prüfen. Gibt Befunde als
    Liste zurück (leer = sauber). Zählen überlässt man besser dem Rechner als dem Auge.

    min_stand=0 schaltet die Standzeit-Prüfung ab — dann bleiben nur die STRUKTUR-Regeln
    (Wortzahl, Zeichenzahl, Satzzeichen), die auf einen echten Fehler in haeppchen()
    deuten. Der Export nutzt das: eine minimal zu kurze Standzeit (schnelles Sprechtempo,
    nahtloser Übergang) ist ein Grenzfall, kein Grund, das ganze Projekt zu blockieren."""
    befunde = []
    for h in haeppchen_liste:
        n = len(h["text"].split())
        if n > max_woerter:
            befunde.append(f"{h['text']!r}: {n} Wörter (max {max_woerter})")
        if len(h["text"]) > max_zeichen:
            befunde.append(f"{h['text']!r}: {len(h['text'])} Zeichen (max {max_zeichen})")
        # Satzzeichen irgendwo im Wort — auch innen (money-back). Zahlen ausgenommen,
        # dort gehören Punkt/Komma zur Zahl (50,000 · 1.100 · 3.5).
        for wort in h["text"].split():
            if re.fullmatch(r"\d[\d.,]*\d|\d", wort):
                continue
            if re.search(RAND_ZEICHEN, wort):
                befunde.append(f"{h['text']!r}: Satzzeichen an {wort!r}")
        if min_stand and h["dauer"] < min_stand:
            befunde.append(f"{h['text']!r}: steht nur {h['dauer']}s (min {min_stand}s)")
    return befunde
