#!/usr/bin/env python3
"""Gestaltungs-Overlays 1:1 nachbauen — statische Text-Elemente über Real-Footage
(Titelbox, Kopfzeile, Preis-Störer), übersetzt, in Größe/Position/Farbe/Schrift des
Originals, als EINE PNG-Ebene für den Render (render.py --overlay).

Warum ein eigenes Werkzeug: CapCut-Captions an dieser Stelle sehen aus wie
Fremdkörper (falsche Farbe, falsche Größe, verrutscht) — das Original hat die
Elemente exakt gesetzt, also werden sie gemessen und deterministisch nachgebaut.

CWD = Pipeline-Ordner. Aufruf:
  python3 overlays.py --spec _pipeline/overlays.json [--out _work/overlays.png] [--vorschau _work/sicht/overlays_vorschau.png --frame _work/source_original.mp4:1.0]
overlays.json = Liste von Elementen (Pixel der Quell-Größe 720x1280):
  {"art":"boxzeilen","zeilen":["Wir haben zu viele","Kollagen-Masken gemacht"],"mitte_x":360,
   "zeilen_y":[[194,245],[250,298]],"schrift":"Inter-Variable.ttf","gewicht":"SemiBold",
   "schriftgroesse":34,"box_farbe":"#FFFFFF","text_farbe":"#0B0A0A","radius":8,"polster":14,
   "emoji":{"quelle":"_work/source_original.mp4:1.0","box":[534,248,571,283],"nach_zeile":1}}
  {"art":"textzeilen","zeilen":["BITTE HILF UNS,","UNSER LAGER ZU LEEREN"],"mitte_x":360,
   "zeilen_y":[[323,350],[363,390]],"schrift":"Inter-Variable.ttf","gewicht":"Bold",
   "schriftgroesse":36,"text_farbe":"#FFFFFF","schatten_farbe":"#1F1813","schatten":[2,2],"max_breite":600}
  {"art":"blase","box":[38,264,436,421],"radius":18,"box_farbe":"#FFFFFF","schwanz":[44,431,22],"zeit":[0,5.4],
   "avatar":{"box":[58,306,100,348]},"schrift":"Inter-Variable.ttf",
   "zeilen":[{"text":"Antwort auf den Kommentar von username","links_x":118,"zeilen_y":[289,303],"schriftgroesse":19,"gewicht":"Regular","text_farbe":"#7A7A7A"},
             {"text":"Woran erkennt man, dass","links_x":118,"zeilen_y":[319,346],"schriftgroesse":31,"gewicht":"SemiBold","text_farbe":"#161616"}]}
  {"art":"kreis","zeilen":["Kaufe 3 + 3 GRATIS","bis zu 65 % RABATT"],"box":[30,434,262,667],
   "fuellung":"#D20000","rand_farbe":"#CF9E67","rand":4,"schrift":"Inter-Variable.ttf","gewicht":"Bold",
   "schriftgroessen":[26,21],"text_farbe":"#FFFFFF","zeilen_y":[[524,545],[557,574]]}
"zeit":[t0,t1] (optional, Sekunden) begrenzt ein Element auf sein Original-Zeitfenster (Kommentar-Blase
nur im Hook, Badge nur in seiner Szene) — dann schreibt das Werkzeug je Fenster eine eigene Ebene
und render.py bekommt sie als --overlay <out-stamm>_zeiten.json (alle Ebenen in EINEM Encode). Ohne "zeit" gilt die ganze Ad.
Gesetz: Zeilen werden so groß gesetzt, wie zeilen_y es vorgibt (Versalhöhe des
Originals), Text wird auf mitte_x zentriert; wird eine Zeile breiter als max_breite,
schrumpft nur diese Zeile. Nichts wird geraten: jede Zahl kommt aus der Messung
(_work/gestaltungs-text.md / overlay_boxen.json).
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HIER = os.path.dirname(os.path.abspath(__file__)); FONTS = os.path.join(HIER, "fonts")
W, H = 720, 1280

def schrift(name, gewicht, groesse):
    f = ImageFont.truetype(os.path.join(FONTS, name), groesse)
    # Gewicht über die Achsen setzen (Inter: opsz + wght) — Namen wie "Bold" greifen bei
    # Variable-Fonts nicht zuverlässig, die Zahl (600 = SemiBold, 700 = Bold, 800 = ExtraBold) schon.
    wght = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700, "ExtraBold": 800, "Black": 900}.get(gewicht, gewicht)
    try:
        achsen = f.get_variation_axes()
        werte = [ax["default"] for ax in achsen]
        for i, ax in enumerate(achsen):
            n = ax.get("name", b""); n = n.decode() if isinstance(n, bytes) else str(n)
            if n.lower().startswith("weight") or n.lower() == "wght": werte[i] = float(wght)
            if n.lower().startswith("optical"): werte[i] = min(max(groesse, ax["minimum"]), ax["maximum"])
        f.set_variation_by_axes(werte)
    except Exception:
        pass
    return f

def frame(quelle):
    pfad, t = quelle.rsplit(":", 1)
    raw = subprocess.run(["ffmpeg","-nostdin","-v","error","-ss",t,"-i",pfad,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return Image.frombytes("RGB", (W, H), raw)

def passend(text, name, gewicht, groesse, max_breite):
    f = schrift(name, gewicht, groesse)
    while max_breite and f.getlength(text) > max_breite and groesse > 8:
        groesse -= 1; f = schrift(name, gewicht, groesse)
    return f

def zeile_setzen(draw, text, f, mitte_x, y0, y1, farbe, schatten=None, schatten_farbe=None):
    # Versalhöhe an zeilen_y ausrichten: Text-Bbox messen, vertikal in [y0,y1] mittig
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    x = mitte_x - (r - l) / 2 - l; y = y0 + ((y1 - y0) - (b - t)) / 2 - t
    if schatten: draw.text((x + schatten[0], y + schatten[1]), text, font=f, fill=schatten_farbe)
    draw.text((x, y), text, font=f, fill=farbe)
    return (x + l, y + t, x + r, y + b)

def zeichnen(img, d, e):
    """Ein Element auf die Ebene img (Draw d) setzen."""
    art = e["art"]
    if art == "boxzeilen":
        f = schrift(e["schrift"], e.get("gewicht", "Bold"), e["schriftgroesse"]); p = e.get("polster", 14)
        emo = None
        if e.get("emoji"):
            q = e["emoji"]; src = frame(q["quelle"]); emo = src.crop(tuple(q["box"]))
        for i, (txt, (y0, y1)) in enumerate(zip(e["zeilen"], e["zeilen_y"])):
            fz = passend(txt, e["schrift"], e.get("gewicht", "Bold"), e["schriftgroesse"], e.get("max_breite", 660) - (emo.width + 10 if emo and i == e["emoji"].get("nach_zeile", 1) else 0))
            l, t, r, b = d.textbbox((0, 0), txt, font=fz); tb = r - l
            extra = (emo.width + 10) if (emo is not None and i == e["emoji"].get("nach_zeile", 1)) else 0
            x0 = e["mitte_x"] - (tb + extra) / 2 - p; x1 = e["mitte_x"] + (tb + extra) / 2 + p
            d.rounded_rectangle((x0, y0, x1, y1), radius=e.get("radius", 8), fill=e["box_farbe"])
            bb = zeile_setzen(d, txt, fz, e["mitte_x"] - extra / 2, y0, y1, e["text_farbe"])
            if extra:
                ey = int((y0 + y1) / 2 - emo.height / 2); img.paste(emo, (int(bb[2] + 10), ey))
    elif art == "textzeilen":
        for txt, (y0, y1) in zip(e["zeilen"], e["zeilen_y"]):
            fz = passend(txt, e["schrift"], e.get("gewicht", "Bold"), e["schriftgroesse"], e.get("max_breite", 660))
            zeile_setzen(d, txt, fz, e["mitte_x"], y0, y1, e["text_farbe"], e.get("schatten"), e.get("schatten_farbe"))
    elif art == "kreis":
        x0, y0, x1, y1 = e["box"]; r = e.get("rand", 4)
        d.ellipse((x0, y0, x1, y1), fill=e["rand_farbe"]); d.ellipse((x0 + r, y0 + r, x1 - r, y1 - r), fill=e["fuellung"])
        mx = (x0 + x1) / 2; maxb = (x1 - x0) - 2 * e.get("polster", 24)
        for txt, g, (ly0, ly1) in zip(e["zeilen"], e["schriftgroessen"], e["zeilen_y"]):
            fz = passend(txt, e["schrift"], e.get("gewicht", "Bold"), g, maxb)
            zeile_setzen(d, txt, fz, mx, ly0, ly1, e["text_farbe"])
    elif art == "blase":
        # EINE abgerundete Box mit mehreren Zeilen (je Zeile eigene Größe/Farbe/Gewicht, zentriert oder
        # linksbündig), optional Avatar-Kreis und Sprechblasen-Schwanz — Kommentar-Blasen, Siegel, Badges.
        x0, y0, x1, y1 = e["box"]; d.rounded_rectangle((x0, y0, x1, y1), radius=e.get("radius", 14), fill=e["box_farbe"])
        if e.get("schwanz"):   # [x_spitze, y_spitze, breite]: Dreieck unter der Box, Spitze (x,y) links unten
            sx, sy, sb = e["schwanz"]; d.polygon([(sx, sy), (sx, y1 - 1), (sx + sb, y1 - 1)], fill=e["box_farbe"])
        if e.get("avatar"):    # {"box":[x0,y0,x1,y1]}: grauer Kreis mit heller Kopf-Schulter-Silhouette
            ax0, ay0, ax1, ay1 = e["avatar"]["box"]; d.ellipse((ax0, ay0, ax1, ay1), fill=e["avatar"].get("farbe", "#D9D9D9"))
            cx, cy, r = (ax0 + ax1) / 2, (ay0 + ay1) / 2, (ax1 - ax0) / 2; sil = e["avatar"].get("silhouette", "#F4F4F4")
            d.ellipse((cx - r * 0.28, cy - r * 0.6, cx + r * 0.28, cy - r * 0.04), fill=sil)
            d.pieslice((cx - r * 0.6, cy + r * 0.02, cx + r * 0.6, cy + r * 1.1), 180, 360, fill=sil)
        for z in e["zeilen"]:
            fz = passend(z["text"], e["schrift"], z.get("gewicht", e.get("gewicht", "Bold")), z["schriftgroesse"], z.get("max_breite", x1 - x0 - 2 * e.get("polster", 14)))
            ly0, ly1 = z["zeilen_y"]; farbe = z.get("text_farbe", e.get("text_farbe", "#111111"))
            if "links_x" in z:
                l, t, r, b = d.textbbox((0, 0), z["text"], font=fz)
                d.text((z["links_x"] - l, ly0 + ((ly1 - ly0) - (b - t)) / 2 - t), z["text"], font=fz, fill=farbe)
            else:
                zeile_setzen(d, z["text"], fz, z.get("mitte_x", (x0 + x1) / 2), ly0, ly1, farbe)
    else: sys.exit(f"unbekannte art: {art}")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--spec", required=True); ap.add_argument("--out", default="_work/overlays.png")
    ap.add_argument("--vorschau"); ap.add_argument("--frame")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for e in spec: zeichnen(img, d, e)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); img.save(a.out)
    print(f"Overlay-Ebene → {a.out} ({len(spec)} Elemente)")
    # Zeitfenster: Trägt ein Element "zeit": [t0, t1], entsteht je Fenster eine eigene Ebene
    # <out-stamm>_<n>.png plus die Liste <out-stamm>_zeiten.json (png/t0/t1) — render.py --overlay
    # nimmt diese JSON und legt alle Ebenen in EINEM Encode. Elemente ohne "zeit" liegen über der ganzen Ad.
    fenster = {}
    for e in spec: fenster.setdefault(tuple(e.get("zeit", [])), []).append(e)
    if any(k for k in fenster):
        stamm = a.out.rsplit(".", 1)[0]; liste = []
        for n, (k, elems) in enumerate(fenster.items()):
            teil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(teil)
            for e in elems: zeichnen(teil, dd, e)
            pf = f"{stamm}_{n}.png"; teil.save(pf); liste.append({"png": pf, "t0": k[0] if k else None, "t1": k[1] if k else None})
        json.dump(liste, open(f"{stamm}_zeiten.json", "w"), indent=1); print(f"Zeitfenster-Ebenen: {len(liste)} → {stamm}_zeiten.json")
    if a.vorschau and a.frame:
        base = frame(a.frame).convert("RGBA"); base.alpha_composite(img); base.convert("RGB").save(a.vorschau); print(f"Vorschau → {a.vorschau}")

if __name__ == "__main__": main()
