#!/usr/bin/env python3
"""Zahlwörter → Ziffern für Caption-Wortlisten (FA-Schema [{text,start,end,…}]).

Warum: Captions sind Lese-Text im Sekundentakt — „37" liest sich, „siebenunddreißig"
nicht. Konvertiert wird NUR, was eindeutig Kardinalzahl ist; die Artikel/Pronomen
ein/eine/einen/einem/einer/eines werden NIE angefasst (die „eine Katze → 1 Katze"-
Falle), Ordinale (erste, zweiten …) bleiben Wörter, „eins" bleibt Wort (im Zweifel
Wort — eine falsche Ziffer ist schlimmer als ein langsames Zahlwort).

Aufruf:
  ziffern.py <fa_words.json> <out.json>   # konvertiert, merged Mehr-Wort-Zahlen
  ziffern.py --test                       # Selbst-Test (muss „ALLE TESTS OK" drucken)

Mehr-Wort-Zahlen („siebenunddreißig Komma fünf") werden zu EINEM Token gemerged:
start = erstes Wort, end = letztes Wort. Tausender-Punkt ab 4 Stellen (5.000).
"""
import json
import re
import sys

EINER = {"null": 0, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6,
         "sieben": 7, "acht": 8, "neun": 9, "zehn": 10, "elf": 11, "zwölf": 12,
         "dreizehn": 13, "vierzehn": 14, "fünfzehn": 15, "sechzehn": 16,
         "siebzehn": 17, "achtzehn": 18, "neunzehn": 19}
ZEHNER = {"zwanzig": 20, "dreißig": 30, "dreissig": 30, "vierzig": 40,
          "fünfzig": 50, "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90}
# NIE konvertieren — Artikel/Pronomen-Homonyme und bewusst Konservatives:
SPERRE = {"ein", "eine", "einen", "einem", "einer", "eines", "eins"}


def _kardinal(w: str):
    """Ein einzelnes Wort als Kardinalzahl parsen — None, wenn keins (oder gesperrt)."""
    t = w.lower()
    if t in SPERRE:
        return None
    if t in EINER: return EINER[t]
    if t in ZEHNER: return ZEHNER[t]
    m = re.fullmatch(r"(?:(ein|zwei|drei|vier|fünf|sechs|sieben|acht|neun)und)?"
                     r"(zwanzig|dreißig|dreissig|vierzig|fünfzig|sechzig|siebzig|achtzig|neunzig)", t)
    if m:
        e = {"ein": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6,
             "sieben": 7, "acht": 8, "neun": 9}.get(m.group(1), 0)
        return e + ZEHNER[m.group(2)]
    m = re.fullmatch(r"(?:(ein|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf"
                     r"|zwanzig|dreißig|vierzig|fünfzig|sechzig|siebzig|achtzig|neunzig"
                     r"|(?:\w+und)?(?:zwanzig|dreißig|vierzig|fünfzig|sechzig|siebzig|achtzig|neunzig))?)"
                     r"(hundert|tausend)(\w*)", t)
    if m:
        basis = _kardinal(m.group(1)) if m.group(1) else 1
        if m.group(1) == "ein": basis = 1
        if basis is None: return None
        wert = basis * (100 if m.group(2) == "hundert" else 1000)
        rest = m.group(3)
        if not rest:                      # glatte hundert/tausend („fünftausend", „hundert")
            return wert
        # ZUSAMMENGESETZTE Hunderter/Tausender (Ergaenzung 25.09.2026, Lauf VIS 004):
        # „hundertneunundzwanzig" = 129, „zweihundertzweiundsechzig" = 262. Ohne das blieb
        # ausgerechnet die PREIS-Zeile jedes Offers als Wortungetuem in den Captions stehen.
        # Der Rest muss selbst eine gueltige Kardinalzahl UNTERHALB der Stufe sein; alles
        # andere (hundertprozentig, tausendfach, hunderteins — „eins" steht in der SPERRE)
        # faellt weiter durch und bleibt Wort.
        r = _kardinal(rest)
        stufe = 100 if m.group(2) == "hundert" else 1000
        if r is None or r >= stufe:
            return None
        return wert + r
    return None


def _fmt(n) -> str:
    if isinstance(n, float):
        return f"{n:.10g}".replace(".", ",")
    s = str(n)
    return f"{s[:-3]}.{s[-3:]}" if len(s) >= 4 else s


def _strip(w: str):
    m = re.match(r"^([\"'„»(]*)(.*?)([\"'“«).,!?;:]*)$", w)
    return m.group(1), m.group(2), m.group(3)


def konvertieren(words: list) -> list:
    konvertieren.n_conv = 0
    out, i = [], 0
    while i < len(words):
        pre, kern, post = _strip(words[i]["text"])
        n = _kardinal(kern)
        if n is None:
            out.append(dict(words[i]))
            i += 1
            continue
        # Dezimal-Fenster: „<zahl> Komma <einer> [<einer> …]"
        if (not post and i + 2 < len(words)
                and words[i + 1]["text"].lower().strip(".,!?") == "komma"):
            dez, j = "", i + 2
            while j < len(words):
                _, k2, p2 = _strip(words[j]["text"])
                d = _kardinal(k2)
                if d is None or d > 9: break
                dez += str(d)
                j += 1
                if p2: break
            if dez:
                _, _, post_l = _strip(words[j - 1]["text"])
                out.append({**words[i], "text": f"{pre}{_fmt(n)},{dez}{post_l}",
                            "end": words[j - 1]["end"]})
                konvertieren.n_conv += 1
                i = j
                continue
        out.append({**words[i], "text": f"{pre}{_fmt(n)}{post}"})
        konvertieren.n_conv += 1
        i += 1
    return out


def _test():
    def w(*texte):
        return [{"text": t, "start": k * 1.0, "end": k + 0.5} for k, t in enumerate(texte)]
    faelle = [
        (w("eine", "Katze"), ["eine", "Katze"]),                      # Artikel-Sperre
        (w("ein", "Geheimnis"), ["ein", "Geheimnis"]),
        (w("siebenunddreißig,"), ["37,"]),
        (w("zweiundfünfzig."), ["52."]),
        (w("siebenunddreißig", "Komma", "fünf", "Grad"), ["37,5", "Grad"]),
        (w("Fünftausend-Euro-Facial"), ["Fünftausend-Euro-Facial"]),  # Kompositum: kein Solo-Zahlwort
        (w("fünftausend"), ["5.000"]),
        (w("zwanzigtausend", "Euro"), ["20.000", "Euro"]),
        (w("genau", "zwei", "Stunden"), ["genau", "2", "Stunden"]),
        (w("achtzig"), ["80"]),
        (w("dreißig", "Tage"), ["30", "Tage"]),
        (w("ersten", "Woche"), ["ersten", "Woche"]),                  # Ordinale bleiben
        (w("eins"), ["eins"]),                                        # konservativ
        (w("„Achtzig", "Euro"), ["„80", "Euro"]),
    ]
    ok = True
    for eingabe, soll in faelle:
        ist = [x["text"] for x in konvertieren(eingabe)]
        if ist != soll:
            ok = False
            print(f"FEHLER: {[x['text'] for x in eingabe]} → {ist} (soll {soll})")
    merged = konvertieren(w("siebenunddreißig", "Komma", "fünf"))
    if not (len(merged) == 1 and merged[0]["start"] == 0.0 and merged[0]["end"] == 2.5):
        ok = False
        print(f"FEHLER Timing-Merge: {merged}")
    print("ALLE TESTS OK" if ok else "TESTS FEHLGESCHLAGEN")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if sys.argv[1] == "--test":
        _test()
    words = json.load(open(sys.argv[1]))
    out = konvertieren(words)
    json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    print(f"{len(words)} Wörter → {len(out)} Tokens · Zahlen konvertiert: {konvertieren.n_conv}")
