#!/usr/bin/env python3
"""etikett_wort.py — EIN Wort auf einem Etikett im Bild austauschen, deterministisch.

Der Fall (VIS 006 EL, 19.09.2026): Die Quell-Ad bewirbt eine FREMDE Marke, deren Produkt
optisch identisch mit dem eigenen ist — gleiches Etikett-Layout, gleiche Wirkstoff-Zeilen,
nur ein anderer Name im Kopf. Dann muss NICHT das Produkt neu erzeugt werden (Kling), es
muss ein WORT getauscht werden. Das ist deterministisch machbar und kostet 0 Credits.

Verfahren je Frame:
  1. Wortband aus den OCR-Boxen der Quelle interpolieren (fps des OCR ist gröber als das Video).
  2. Im Band die dunklen Pixel finden = die Buchstaben. Daraus Grundlinie, Oberlinie,
     linke und rechte Kante messen (Neigung per Regression, nicht geschätzt).
  3. Löschen: Jede Spalte des Wortes wird zwischen Ober- und Unterkante linear aus den
     Etikett-Pixeln direkt darüber und darunter interpoliert. Auf einem gleichmäßig hellen
     Etikett ist das nahtlos — kein Inpaint-Modell nötig, keine zerrissene Struktur
     (Memory „Retusche kostet Bild").
  4. Neues Wort in der gemessenen Versalhöhe und der gemessenen Schriftfarbe setzen,
     auf die gemessene Neigung drehen, auf die gemessene Breite ziehen, einsetzen.

Aufruf (CWD = Pipeline-Ordner):
  python3 tools/sp/etikett_wort.py --video _work/bild_basis.mp4 --ziel _work/bild_marke.mp4 \
      --ocr _pipeline/ocr_orig_voll.jsonl --alt NEUROBELLA --neu VISIOVANCE \
      --font tools/sp/fonts/Poppins-Bold.ttf [--nur-frames 2280,2370 --probe _work/probe]
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True)
ap.add_argument("--ziel")
ap.add_argument("--ocr", required=True)
ap.add_argument("--alt", required=True, help="Wort, das im Bild steht (OCR-Schreibung)")
ap.add_argument("--neu", required=True, help="Wort, das hin soll")
ap.add_argument("--font", required=True)
ap.add_argument("--max-y", type=int, default=880, help="Textboxen darunter ignorieren (Caption-Band)")
ap.add_argument("--pad", type=int, default=14)
ap.add_argument("--kanten", help="clip_karte.json: Erben von Massen darf keine Schnittkante "
                "ueberschreiten. Hinter einem Schnitt steht das Wort in anderer Groesse und "
                "Neigung; geerbte Masse decken es dann nicht (belegt VIS 006 EL: Winkel sprang "
                "bei Frame 3211 von -1,39 auf +1,92, die geerbten 280 px deckten ein deutlich "
                "groesseres NEUROBELLA nicht ab).")
ap.add_argument("--rand", type=float, default=0.6,
                help="Sekunden, um die jedes Fenster ueber die OCR-Stuetzstellen hinaus "
                     "verlaengert wird. Noetig, weil das OCR groeber abtastet als das Video: "
                     "bei fps=4 liegt die Fensterkante bis zu 7 Frames daneben, und dort blitzt "
                     "die alte Marke wieder auf (belegt VIS 006 EL: Frames 2443-2445 getauscht, "
                     "ab 2446 stand NEUROBELLA wieder da). Im Rand entscheidet die MESSUNG je "
                     "Frame — ist keine Schrift da, greift die Mindest-Pixelzahl und es passiert "
                     "nichts; ist welche da, erbt der Frame die Masse der Nachbarn.")  # grosszuegig: bei geneigtem Wort darf es den Box-Rand nicht beruehren
ap.add_argument("--probe", help="Ordner: je getauschtem Frame ein PNG vorher/nachher")
ap.add_argument("--nur-frames", help="a,b — nur diesen Frame-Bereich rechnen (Probe)")
a = ap.parse_args()

pr = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
      "stream=width,height,r_frame_rate","-of","json",a.video],capture_output=True,text=True).stdout)["streams"][0]
W, H = int(pr["width"]), int(pr["height"])
num, den = pr["r_frame_rate"].split("/"); FPS = int(num)/int(den)

# --- OCR-Boxen des Wortes einlesen -------------------------------------------------
schl = a.alt.lower().replace(" ", "")
boxen = []
for z in open(a.ocr):
    d = json.loads(z)
    for x in d["texte"]:
        if schl in x["text"].lower().replace(" ", "") and x["y"]*H < a.max_y:
            boxen.append((float(d["t"]), x["x"]*W, x["y"]*H, x["w"]*W, x["h"]*H))
if not boxen:
    sys.exit(f"Wort {a.alt!r} in {a.ocr} nicht gefunden (ueber y={a.max_y}).")
boxen.sort()
ts = np.array([b[0] for b in boxen])
print(f"[wort] {len(boxen)} OCR-Treffer fuer {a.alt!r}, {ts.min():.2f}-{ts.max():.2f} s")

# Zusammenhängende Fenster (Lücke > 1,5 s trennt)
fenster = []
lauf = [boxen[0]]
for b in boxen[1:]:
    if b[0] - lauf[-1][0] > 1.5: fenster.append(lauf); lauf = [b]
    else: lauf.append(b)
fenster.append(lauf)
print(f"[wort] {len(fenster)} Fenster: " + " · ".join(f"{f[0][0]:.2f}-{f[-1][0]:.2f}s" for f in fenster))

def fenster_index(t):
    for i, f in enumerate(fenster):
        if f[0][0] - a.rand <= t <= f[-1][0] + a.rand: return i
    return None

def im_kern(t):
    """True, wenn t zwischen den OCR-Stuetzstellen liegt (dort ist das Wort sicher da).
    Im RAND (ausserhalb) ist es unsicher — dort darf nur eine plausible Messung handeln,
    sonst setzt das Werkzeug das neue Wort auf eine Stelle, an der gar keins steht."""
    for f in fenster:
        if f[0][0] <= t <= f[-1][0]: return True
    return False

def box_bei(t):
    """Box linear zwischen den OCR-Stützstellen interpolieren (nur INNERHALB eines Fensters)."""
    for f in fenster:
        # KEINE Extrapolation ueber die OCR-Stuetzstellen hinaus. Mit 0,30 s Zugabe
        # geriet die Box in Frames, in denen das Wort noch gar nicht (oder nicht mehr)
        # da ist — die Messung entgleiste dort auf 146 px Versalhoehe statt 48
        # (belegt VIS 006 EL, Frames 2256-2264).
        if f[0][0] - a.rand <= t <= f[-1][0] + a.rand:
            tt = np.array([x[0] for x in f])
            if len(f) == 1: return f[0][1:]
            return tuple(np.interp(t, tt, [x[i] for x in f]) for i in range(1, 5))
    return None

FONT = a.font
def wort_bild(text, hoehe_px, farbe, breite_px):
    """Das neue Wort als RGBA, Versalhöhe = hoehe_px, danach auf breite_px gezogen."""
    gross = max(20, int(hoehe_px * 4))
    f = ImageFont.truetype(FONT, gross)
    d = ImageDraw.Draw(Image.new("L", (10, 10)))
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    im = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), text, font=f, fill=tuple(int(c) for c in farbe) + (255,))
    # auf die gemessene Versalhöhe bringen
    alpha = np.array(im)[:, :, 3]
    ys = np.where(alpha.max(axis=1) > 40)[0]
    if len(ys) < 2: return None
    ist = ys.max() - ys.min() + 1
    sk = hoehe_px / ist
    im = im.resize((max(1, int(im.width * sk)), max(1, int(im.height * sk))), Image.LANCZOS)
    # auf die gemessene Wortbreite ziehen
    alpha = np.array(im)[:, :, 3]
    xs = np.where(alpha.max(axis=0) > 40)[0]
    if len(xs) < 2: return None
    ist_b = xs.max() - xs.min() + 1
    if ist_b > 0 and abs(breite_px - ist_b) > 2:
        sk2 = breite_px / ist_b
        im = im.resize((max(1, int(im.width * sk2)), im.height), Image.LANCZOS)
    return im

lese = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",a.video,"-f","rawvideo","-pix_fmt","rgb24","-"],
                        stdout=subprocess.PIPE)
schreib = None
if a.ziel:
    schreib = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24",
        "-s",f"{W}x{H}","-r",f"{FPS}","-i","-","-i",a.video,"-map","0:v","-map","1:a?",
        "-c:v","libx264","-crf","18","-preset","slow","-pix_fmt","yuv420p","-c:a","copy",a.ziel],
        stdin=subprocess.PIPE)
if a.probe: os.makedirs(a.probe, exist_ok=True)
nur = tuple(int(x) for x in a.nur_frames.split(",")) if a.nur_frames else None

GROESSE = W*H*3
n = getauscht = 0
protokoll = []
KANTEN = sorted(c["t0"] for c in json.load(open(a.kanten))) if a.kanten else []
def clip_von(t):
    i = 0
    for k, kt in enumerate(KANTEN):
        if t >= kt: i = k
    return i
akt_clip = None
letzte_hoehen = []          # Plausibilitaets-Waechter, JE FENSTER zurueckgesetzt
letzte_masse = None         # (Breite, Winkel) der letzten plausiblen Messung
breite_erbe = winkel_erbe = None
akt_fenster = None
uebersprungen = 0
while True:
    roh = lese.stdout.read(GROESSE)
    if len(roh) < GROESSE: break
    f = np.frombuffer(roh, np.uint8).reshape(H, W, 3).copy()
    t = n / FPS
    bx = box_bei(t)
    fi = fenster_index(t)
    ci = clip_von(t) if KANTEN else None
    if ci != akt_clip:
        # Schnittkante: Erb-Gedaechtnis loeschen.
        letzte_hoehen = []; letzte_masse = None
        akt_clip = ci
    if fi != akt_fenster:
        # Neues Fenster: Waechter zuruecksetzen. Die Fenster haben echt verschiedene
        # Schriftgroessen (VIS 006 EL: 45 px im Packshot-Fenster A, 23 px in Fenster B) —
        # ein gemeinsamer Referenzwert verwirft ein ganzes Fenster (270 von 285 Frames).
        letzte_hoehen = []; letzte_masse = None
        akt_fenster = fi
    if bx and (nur is None or nur[0] <= n <= nur[1]):
        BX, BY, BW, BH = [int(round(v)) for v in bx]
        p = a.pad
        x0, y0 = max(0, BX-p), max(0, BY-p)
        x1, y1 = min(W, BX+BW+p), min(H, BY+BH+p)
        sub = f[y0:y1, x0:x1].astype(np.int16)
        if sub.size:
            g = sub.mean(axis=2)
            # Schwelle ADAPTIV nach Otsu statt fest. Eine feste Schwelle
            # (Perzentil-75 minus 70) faengt bei Bewegungsunschaerfe nur die
            # Buchstaben-KERNE; ihr weicher Saum bleibt stehen und scheint als Geist
            # hinter dem neuen Wort durch (belegt VIS 006 EL, Frame 2280 — „OBELLA"
            # war nach dem Tausch noch lesbar). Otsu trennt Etikett und Schrift dort,
            # wo die beiden Verteilungen sich wirklich scheiden.
            hist, kanten = np.histogram(g, bins=64, range=(0, 255))
            gesamt = hist.sum()
            if gesamt > 0:
                w0 = np.cumsum(hist); w1 = gesamt - w0
                mitte = (kanten[:-1] + kanten[1:]) / 2
                m0 = np.cumsum(hist * mitte) / np.maximum(w0, 1)
                m1 = (np.cumsum((hist * mitte)[::-1])[::-1] - hist * mitte + hist * mitte) 
                m1 = (hist * mitte).sum() - np.cumsum(hist * mitte)
                m1 = m1 / np.maximum(w1, 1)
                var = w0 * w1 * (m0 - m1) ** 2
                schwelle = float(mitte[int(np.argmax(var))])
            else:
                schwelle = np.percentile(g, 75) - 70
            # Saum grosszuegig mitnehmen: 35 % ueber die Otsu-Grenze. Gemessen an der
            # unschaerfsten Stelle (VIS 006 EL, Frame 2280): Otsu = 133, die Buchstaben-Kerne
            # liegen darunter, ihr Saum aber zwischen 149 und 180 — mit nur 12 % Zuschlag
            # blieb er als Geist stehen. Ab 200 kippt die Erkennung ins Etikett (48 % statt
            # 25 % der Box). 35 % trifft den Saum und laesst das Etikett stehen.
            # ZWEI Masken, bewusst getrennt:
            #  - kern (Otsu pur) MISST die Geometrie: Versalhoehe, Breite, Neigung.
            #    Eine weite Maske blaeht diese Werte auf und das neue Wort wird zu gross
            #    (gemessen VIS 006 EL: Versalhoehe sprang von 39-49 auf 40-91 px).
            #  - dunkel (Otsu x 1,35) LOESCHT: sie muss auch den weichen Saum fassen,
            #    sonst bleibt bei Bewegungsunschaerfe ein Geist stehen.
            kern = g < schwelle
            dunkel = g < schwelle * 1.35
            ys, xs = np.where(kern)
            if len(xs) > 60:
                # Grund- und Oberlinie messen
                cx, cb, ct = [], [], []
                for c in range(xs.min(), xs.max()+1):
                    sp = np.where(kern[:, c])[0]
                    if len(sp): cx.append(c); cb.append(sp.max()); ct.append(sp.min())
                cx = np.array(cx); cb = np.array(cb); ct = np.array(ct)
                if len(cx) > 20:
                    mb, bb = np.polyfit(cx, cb, 1)
                    mt, bt = np.polyfit(cx, ct, 1)
                    hoehe = float(np.median(cb - ct))
                    breite = int(xs.max() - xs.min() + 1)
                    farbe = sub[kern].mean(axis=0)
                    # Plausibilitaets-Waechter: Die Schrifthoehe aendert sich von Frame zu
                    # Frame nur langsam. Ein Sprung um mehr als 35 % heisst, die Messung hat
                    # etwas anderes gefasst (Siegel, Etikettrand, halb sichtbares Wort) —
                    # dann lieber NICHTS tun als ein falsch grosses Wort setzen.
                    # Der Waechter greift erst, wenn er genug gesehen hat, und misst gegen
                    # den MEDIAN ALLER bisherigen Messungen — nicht gegen die letzten zehn.
                    # Sonst vergiftet ein einziger kaputter erster Frame den ganzen Lauf
                    # (belegt VIS 006 EL: 1 statt 488 getauschte Frames, weil Frame 2264 mit
                    # 146 px Referenz wurde).
                    # Bei unplausibler Messung wird NICHT uebersprungen — ein ausgelassener
                    # Frame zeigt die FREMDMARKE, und 3-5 Frames reichen zum sichtbaren
                    # Aufblitzen (belegt VIS 006 EL: 4 Luecken von 0,10-0,17 s). Stattdessen
                    # erbt der Frame Hoehe, Breite und Winkel von den Nachbarn; die POSITION
                    # kommt weiter aus diesem Frame, denn die stimmt auch dann.
                    geerbt = False
                    if len(letzte_hoehen) >= 15:
                        ref = float(np.median(letzte_hoehen))
                        if ref > 0 and (hoehe > ref*1.35 or hoehe < ref*0.65):
                            if not im_kern(t):
                                # Im RAND: unplausibel heisst hier wahrscheinlich „kein Wort da".
                                # Nichts tun ist richtig — ein geerbtes Wort waere ein
                                # Fremdkoerper an einer Stelle ohne Schriftzug.
                                if schreib: schreib.stdin.write(f.tobytes())
                                n += 1; continue
                            hoehe = ref
                            if letzte_masse:
                                breite_erbe, winkel_erbe = letzte_masse
                            geerbt = True
                            uebersprungen += 1
                    if not geerbt:
                        letzte_hoehen.append(hoehe)
                    # 1) Wort löschen: je Spalte zwischen Ober- und Unterkante interpolieren
                    # Loeschen entlang der GEFITTETEN Linien, nicht entlang der
                    # Spalten-Extreme. Extreme je Spalte erzeugen eine gezackte Unterkante —
                    # sichtbar als senkrechte Schlieren unter dem Wort (belegt VIS 006 EL).
                    # Die gefitteten Linien laufen glatt mit der Neigung mit.
                    # --- Abdecken + Neusatz als EINE Karte -------------------------
                    # Sechs Versuche davor (VIS 006 EL 19.09.2026) sind gemessen gescheitert:
                    # fuenf Loesch-Verfahren, die pro Spalte rechnen und am Etikettrand keine
                    # Stuetze finden, und eine Variante, bei der Abdeck-Platte und neues Wort
                    # getrennt verankert wurden — dann driften sie auseinander.
                    # Was traegt: EINE Karte (gemessene Etikettfarbe + neues Wort darauf),
                    # EINMAL gedreht, an EINEM Anker gesetzt. Plattenfarbe und Schriftfarbe
                    # sind beide aus diesem Frame gemessen, nichts geraten.
                    # Plattenfarbe ist KEIN flacher Wert: Das Etikett sitzt auf einem
                    # Zylinder und ist zu den Raendern hin abgeschattet. Eine flache Platte
                    # steht darum als heller Kasten im Bild (belegt VIS 006 EL). Darum wird
                    # der Untergrund REKONSTRUIERT: die Buchstaben-Pixel werden iterativ aus
                    # ihrer hellen Nachbarschaft aufgefuellt, danach weich geglaettet — die
                    # Woelbung bleibt erhalten, die Schrift verschwindet.
                    # Untergrund ZEILENWEISE rekonstruieren. Die iterative
                    # Nachbarschafts-Fuellung schafft dicke Buchstabenkerne nicht — sie
                    # hinterlaesst ein graues Abbild der alten Schrift, das hinter dem neuen
                    # Wort als Geist durchscheint (belegt VIS 006 EL, Frame 2280: „OBELLA"
                    # blieb lesbar). Das Etikett ist in jeder Zeile gleichmaessig hell, also
                    # ist der Median der HELLEN Pixel derselben Zeile die richtige Farbe —
                    # ein Durchgang, kein Rest, und die Woelbung von oben nach unten bleibt.
                    fuell = sub.astype(np.float32).copy()
                    for r in range(sub.shape[0]):
                        frei = ~dunkel[r]
                        if frei.sum() >= 6:
                            med = np.median(sub[r][frei], axis=0)
                        else:
                            nah = [rr for rr in range(max(0,r-6), min(sub.shape[0], r+7))
                                   if (~dunkel[rr]).sum() >= 6]
                            if not nah: continue
                            med = np.median(np.concatenate([sub[rr][~dunkel[rr]] for rr in nah]), axis=0)
                        fuell[r][dunkel[r]] = med
                    untergrund = np.array(Image.fromarray(
                        np.clip(fuell,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)))
                    # Die Rekonstruktion wird NUR dort eingesetzt, wo Buchstaben standen —
                    # nicht als Platte. Eine Platte hat immer eine Kante; eine maskierte
                    # Ersetzung hat keine. Die Maske wird geweitet und weich gemacht, damit
                    # die Anti-Aliasing-Raender der alten Schrift mitgehen.
                    m = dunkel.astype(np.float32)
                    for _ in range(4):
                        m = np.maximum.reduce([m, np.roll(m,1,0), np.roll(m,-1,0),
                                                  np.roll(m,1,1), np.roll(m,-1,1)])
                    m = np.array(Image.fromarray((m*255).astype(np.uint8)).filter(
                        ImageFilter.GaussianBlur(2)), dtype=np.float32)/255.0
                    sub = (untergrund*m[:,:,None] + sub*(1-m[:,:,None])).astype(np.int16)
                    f[y0:y1, x0:x1] = np.clip(sub, 0, 255).astype(np.uint8)
                    bw_ = int(xs.max() - xs.min() + 1)
                    bh_ = int(ys.max() - ys.min() + 1)
                    if geerbt and breite_erbe: bw_ = breite_erbe
                    wb = wort_bild(a.neu, hoehe, farbe, bw_)
                    if wb is not None:
                        winkel = winkel_erbe if (geerbt and winkel_erbe is not None) \
                                 else -math.degrees(math.atan(mb))
                        if not geerbt: letzte_masse = (bw_, winkel)
                        karte = wb.rotate(winkel, expand=True, resample=Image.BICUBIC)
                        # EIN Anker: die Mitte der alten Buchstaben-Huelle. Das neue Wort
                        # wird auf dieselbe Mitte gesetzt — gleiche Hoehe, gleiche Breite,
                        # gleiche Neigung, also deckt es genau die alte Flaeche ab.
                        ax = x0 + (xs.min() + xs.max())/2.0
                        ay = y0 + (ys.min() + ys.max())/2.0
                        ka = np.array(karte)[:, :, 3]
                        kyy = np.where(ka.max(axis=1) > 40)[0]; kxx = np.where(ka.max(axis=0) > 40)[0]
                        ox = int(round(ax - (kxx.min()+kxx.max())/2)) if len(kxx) else int(round(ax - karte.width/2))
                        oy = int(round(ay - (kyy.min()+kyy.max())/2)) if len(kyy) else int(round(ay - karte.height/2))
                        basis = Image.fromarray(f)
                        tmp = Image.new("RGBA", (W, H), (0,0,0,0))
                        tmp.paste(karte, (ox, oy), karte)
                        f = np.array(Image.alpha_composite(basis.convert("RGBA"), tmp).convert("RGB"))
                        getauscht += 1
                        protokoll.append({"frame": n, "t": round(t,3), "hoehe": round(hoehe,1),
                                          "breite": bw_, "winkel": round(winkel,2),
                                          "farbe": [int(v) for v in farbe]})
                        if a.probe and getauscht % 15 == 1:
                            Image.fromarray(f).save(f"{a.probe}/f{n:05d}.png")
    if schreib: schreib.stdin.write(f.tobytes())
    n += 1

if schreib:
    schreib.stdin.close(); schreib.wait()
lese.wait()
if protokoll:
    json.dump(protokoll, open("_pipeline/etikett_wort.json", "w"), indent=1)
print(f"[wort] {n} Frames gelesen · {getauscht} Frames getauscht"
      + (f" · {uebersprungen} uebersprungen (Messung unplausibel)" if uebersprungen else "") + (f" → {a.ziel}" if a.ziel else ""))
if protokoll:
    h = [p["hoehe"] for p in protokoll]; wkl = [p["winkel"] for p in protokoll]
    print(f"[wort] Versalhöhe {min(h):.0f}–{max(h):.0f} px · Neigung {min(wkl):+.1f}–{max(wkl):+.1f}°")
