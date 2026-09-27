#!/usr/bin/env python3
"""untertitel_regel.py — prueft eine Speaking-VSL-SRT gegen die Skill-Regel und
schneidet zu lange Einblendungen an Wortgrenzen nach.

WARUM DIESES WERKZEUG EXISTIERT
-------------------------------
`.claude/skills/speaking-vsl-captions/SKILL.md` schreibt die Regel:

    "je Einblendung 1,5-3 s, und ein Szenenwechsel ist immer auch ein
     Textwechsel, wenn der Satz es hergibt"
    "Hoechstens zwei Zeilen je Einblendung"
    "Zeilenlaenge hoechstens ~34 Zeichen"

Der Skill lieferte aber nur die SKILL.md, kein Skript. Die Cue-Bildung wurde
damit je Lauf von Hand nachgebaut — und im Lauf VIS 006 EL (19.09.2026) rutschte
die Obergrenze durch: 10 von 44 Einblendungen standen laenger als 3,0 s, die
laengste 3,98 s. Zeilen- und Zeichenregel waren eingehalten, nur die Standzeit
nicht. Gefunden wurde das nicht am Bild, sondern durch Nachmessen der SRT.

Seitdem prueft und repariert dieses Werkzeug die Regel, statt sie dem Gedaechtnis
zu ueberlassen.

WAS ES NICHT TUT
----------------
Es baut keine SRT und formuliert nichts um. Der Wortlaut bleibt Zeichen fuer
Zeichen stehen — es setzt nur andere Grenzen zwischen die Woerter. Die
Wort-Reihenfolge wird am Ende hart gegengeprueft; weicht sie ab, bricht das
Werkzeug ab und schreibt nichts.

WOHER DIE WORTZEITEN KOMMEN
---------------------------
Aus den Caption-Haeppchen (`captions<NNN>_haeppchen.json`, absolut = t + start).
Deren Wortfolge weicht von der SRT geregelt ab: Zahlwoerter stehen dort als
Ziffern, Bindestrich-Komposita sind zerlegt. Darum wird per difflib abgeglichen
und eine n:m-Stelle als EIN Zeitfenster uebernommen. Ohne Haeppchen wird
innerhalb der Einblendung proportional zur Zeichenlaenge geteilt — derselbe
Notweg, den der Captions-Skill fuer Woerter ohne Treffer nennt. Welcher Weg je
Schnitt gegriffen hat, steht im Protokoll.

BEISPIEL
--------
    # nur messen (Exit 1 bei Befund)
    python3 tools/sp/untertitel_regel.py --srt _work/captions.srt \
        --haeppchen _capcut-paket/captions006_haeppchen.json

    # nachschneiden, Szenenschnitte bevorzugen
    python3 tools/sp/untertitel_regel.py --srt _work/captions.srt \
        --haeppchen _capcut-paket/captions006_haeppchen.json \
        --kanten _pipeline/clip_karte.json \
        -o _work/captions.srt --protokoll _pipeline/untertitel_regel.json
"""

import argparse, json, os, re, sys, unicodedata, difflib

SATZENDE = ('.', '!', '?', '…', ':', ';')


# ---------------------------------------------------------------- SRT lesen/schreiben

def zeit_lesen(s):
    h, m, rest = s.strip().split(':')
    sek, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(sek) + int(ms) / 1000.0


def zeit_schreiben(t):
    if t < 0:
        t = 0.0
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def srt_lesen(pfad):
    rohe = [b for b in re.split(r'\n\s*\n', open(pfad, encoding='utf-8').read().strip()) if b.strip()]
    cues = []
    for b in rohe:
        L = [x for x in b.split('\n') if x.strip() != '']
        # Index-Zeile ist optional
        i = 1 if L and L[0].strip().isdigit() else 0
        a, e = L[i].split('-->')
        cues.append({'t0': zeit_lesen(a), 't1': zeit_lesen(e),
                     'woerter': ' '.join(L[i + 1:]).split()})
    return cues


def srt_schreiben(pfad, cues, zeilen_max, zeichen_max):
    aus = []
    for n, c in enumerate(cues, 1):
        _, zl = umbrechen(c['woerter'], zeilen_max, zeichen_max)
        aus.append('%d\n%s --> %s\n%s\n' % (n, zeit_schreiben(c['t0']), zeit_schreiben(c['t1']), '\n'.join(zl)))
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write('\n'.join(aus))


# ---------------------------------------------------------------- Zeilenumbruch

def umbrechen(woerter, k, zeichen):
    """Teilt in hoechstens k Zeilen so, dass die LAENGSTE Zeile minimal wird.
    Gibt (laengste Zeile, Zeilen) zurueck. DP, weil greedy die letzte Zeile
    verhungern laesst ('Meso-Zeaxanthin' allein unter einer vollen Zeile)."""
    n = len(woerter)
    if n == 0:
        return 0, ['']
    laenge = lambda i, j: sum(len(w) for w in woerter[i:j]) + (j - i - 1)
    INF = float('inf')
    dp = [[INF] * (n + 1) for _ in range(k + 1)]
    wahl = [[None] * (n + 1) for _ in range(k + 1)]
    for r in range(k + 1):
        dp[r][n] = 0
    for r in range(1, k + 1):
        for i in range(n - 1, -1, -1):
            best, bj = INF, None
            for j in range(i + 1, n + 1):
                c = max(laenge(i, j), dp[r - 1][j])
                if c < best:
                    best, bj = c, j
            dp[r][i], wahl[r][i] = best, bj
    zl, i, r = [], 0, k
    while i < n and r > 0:
        j = wahl[r][i]
        zl.append(' '.join(woerter[i:j]))
        i, r = j, r - 1
    return dp[k][0], zl


def passt(woerter, k, zeichen):
    return umbrechen(woerter, k, zeichen)[0] <= zeichen


# ---------------------------------------------------------------- Wortzeiten

def norm(s):
    s = unicodedata.normalize('NFC', s).lower()
    return re.sub(r'[^0-9a-zäöüß]', '', s)


def wortzeiten(haeppchen_pfad, srt_woerter):
    """Ordnet jedem SRT-Wort (start, end) zu. Gibt (zeiten, bericht) zurueck;
    zeiten[i] ist None, wo der Abgleich nichts hergab."""
    h = json.load(open(haeppchen_pfad, encoding='utf-8'))
    H = []
    for c in h:
        for w in c['woerter']:
            H.append((w['text'], c['t'] + w['start'], c['t'] + w['end']))
    a = [norm(x[0]) for x in H]
    b = [norm(x) for x in srt_woerter]
    zeiten = [None] * len(srt_woerter)
    bericht = {'haeppchen_woerter': len(H), 'srt_woerter': len(srt_woerter),
               'gleich': 0, 'zusammengefasst': 0, 'ohne_treffer': 0, 'stellen': []}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                zeiten[j1 + k] = (H[i1 + k][1], H[i1 + k][2])
            bericht['gleich'] += i2 - i1
        elif tag == 'replace' and i2 > i1 and j2 > j1:
            # n:m-Stelle (Ziffer <-> Zahlwort, zerlegtes Kompositum):
            # das ganze H-Fenster deckt das ganze S-Fenster ab, proportional geteilt
            t0, t1 = H[i1][1], H[i2 - 1][2]
            teil = srt_woerter[j1:j2]
            ges = sum(len(w) for w in teil) or 1
            lauf = t0
            for k, w in enumerate(teil):
                d = (t1 - t0) * len(w) / ges
                zeiten[j1 + k] = (lauf, lauf + d)
                lauf += d
            bericht['zusammengefasst'] += j2 - j1
            bericht['stellen'].append({'haeppchen': [H[k][0] for k in range(i1, i2)],
                                       'srt': teil, 't0': round(t0, 3), 't1': round(t1, 3)})
        else:
            bericht['ohne_treffer'] += max(0, j2 - j1)
            bericht['stellen'].append({'tag': tag, 'srt': srt_woerter[j1:j2]})
    return zeiten, bericht


def zeiten_ergaenzen(cue, zeiten_slice):
    """Fuellt fehlende Wortzeiten innerhalb einer Einblendung proportional zur
    Zeichenlaenge — der Notweg des Captions-Skills."""
    w = cue['woerter']
    if all(z is not None for z in zeiten_slice):
        return list(zeiten_slice), False
    ges = sum(len(x) for x in w) or 1
    lauf, aus = cue['t0'], []
    for x in w:
        d = (cue['t1'] - cue['t0']) * len(x) / ges
        aus.append((lauf, lauf + d))
        lauf += d
    return aus, True


# ---------------------------------------------------------------- Schnitte

def kanten_lesen(pfad):
    d = json.load(open(pfad, encoding='utf-8'))
    ks = set()
    if isinstance(d, list) and d and isinstance(d[0], dict):
        for c in d:
            for f in ('t0', 't1'):
                if f in c:
                    ks.add(round(float(c[f]), 3))
    elif isinstance(d, list):
        ks = {round(float(x), 3) for x in d}
    elif isinstance(d, dict):
        for f in ('kanten', 'schnitte', 'cuts'):
            if f in d:
                ks = {round(float(x), 3) for x in d[f]}
    return sorted(ks)


def kante_im_spalt(kanten, t_von, t_bis):
    for k in kanten:
        if t_von - 1e-9 <= k <= t_bis + 1e-9:
            return k
    return None


# ---------------------------------------------------------------- Nachschnitt

def teilen(cue, zeiten, kanten, a):
    """Teilt eine zu lange Einblendung rekursiv. Gibt eine Liste Einblendungen
    zurueck (jede mit 'grund' = warum HIER geschnitten wurde)."""
    dauer = cue['t1'] - cue['t0']
    w = cue['woerter']
    if dauer <= a.max + 1e-6 or len(w) < 2:
        return [cue]

    best = None
    for i in range(1, len(w)):                       # Schnitt VOR Wort i
        links, rechts = w[:i], w[i:]
        if not passt(links, a.zeilen, a.zeichen) or not passt(rechts, a.zeilen, a.zeichen):
            continue
        spalt_a, spalt_b = zeiten[i - 1][1], zeiten[i][0]
        grenze = (spalt_a + spalt_b) / 2.0
        d_l, d_r = grenze - cue['t0'], cue['t1'] - grenze
        if d_l <= 0 or d_r <= 0:
            continue
        # Punkte: hoeher ist besser
        p = 0.0
        grund = 'wortgrenze'
        k = kante_im_spalt(kanten, spalt_a, spalt_b)
        if k is not None:
            p += 100.0                                # Szenenwechsel = Textwechsel
            grenze = k
            d_l, d_r = grenze - cue['t0'], cue['t1'] - grenze
            grund = 'szenenschnitt'
            if d_l <= 0 or d_r <= 0:
                continue
        if w[i - 1].rstrip('")“”\'').endswith(SATZENDE):
            p += 60.0
            grund = 'satzende' if grund == 'wortgrenze' else grund + '+satzende'
        # HARTE Boeden. Sie stehen VOR den Punkten, damit kein Bonus sie ueberstimmt.
        # Gemessen im Lauf VIS 006 EL: der Szenenschnitt-Bonus (100) hat die weiche
        # Kurz-Strafe (12) ueberrannt und "Vielleicht" 0,26 s lang aufblitzen lassen —
        # 38,5 Zeichen/s. Eine zu lange Einblendung gegen ein Blitzen zu tauschen ist
        # kein Fortschritt, darum sind Boden und Lesetempo Ausschluss, nicht Abzug.
        if min(d_l, d_r) < a.boden:
            continue
        eltern_cps = sum(len(x) for x in w) / max(dauer, 1e-6)
        deckel_cps = max(a.cps, eltern_cps)           # nie schlechter als vorher
        if (sum(len(x) for x in links) / d_l > deckel_cps or
                sum(len(x) for x in rechts) / d_r > deckel_cps):
            continue
        p += 12.0 * max(0.0, spalt_b - spalt_a)       # echte Sprechpause
        p -= 8.0 * abs(d_l - d_r)                     # ausgewogen
        for d in (d_l, d_r):
            if d > a.max:
                p -= 40.0                             # bleibt zu lang
            if d < a.min:
                p -= 10.0 * (a.min - d)               # unter dem Sollband, aber lesbar
        if best is None or p > best[0]:
            best = (p, i, grenze, grund)

    if best is None:                                  # kein zulaessiger Schnitt
        cue = dict(cue); cue['grund'] = 'unteilbar'
        return [cue]

    _, i, grenze, grund = best
    links = {'t0': cue['t0'], 't1': grenze - a.lucke, 'woerter': w[:i], 'grund': grund}
    rechts = {'t0': grenze, 't1': cue['t1'], 'woerter': w[i:], 'grund': cue.get('grund', 'quelle')}
    return (teilen(links, zeiten[:i], kanten, a) +
            teilen(rechts, zeiten[i:], kanten, a))


# ---------------------------------------------------------------- Messung

def messen(cues, a):
    lang, kurz, breit, viele, hetze = [], [], [], [], []
    for n, c in enumerate(cues, 1):
        d = c['t1'] - c['t0']
        tempo = sum(len(x) for x in c['woerter']) / max(d, 1e-6)
        if tempo > a.cps:
            hetze.append((n, round(tempo, 1), round(d, 2), ' '.join(c['woerter'])))
        _, zl = umbrechen(c['woerter'], a.zeilen, a.zeichen)
        if d > a.max + 1e-6:
            lang.append((n, round(d, 2), ' / '.join(zl)))
        if d < a.min - 1e-6:
            kurz.append((n, round(d, 2), ' / '.join(zl)))
        if len(zl) > a.zeilen:
            viele.append((n, len(zl)))
        for z in zl:
            if len(z) > a.zeichen:
                breit.append((n, len(z), z))
    return {'lang': lang, 'kurz': kurz, 'breit': breit, 'viele': viele, 'hetze': hetze}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--srt', required=True)
    p.add_argument('--haeppchen')
    p.add_argument('--kanten')
    p.add_argument('--min', type=float, default=1.5)
    p.add_argument('--max', type=float, default=3.0)
    p.add_argument('--zeilen', type=int, default=2)
    p.add_argument('--zeichen', type=int, default=34)
    p.add_argument('--lucke', type=float, default=0.08, help='Luft zwischen zwei Einblendungen')
    p.add_argument('--boden', type=float, default=0.80,
                   help='harte Untergrenze je Einblendung: darunter wird nicht geschnitten')
    p.add_argument('--cps', type=float, default=20.0,
                   help='Lesetempo-Deckel (Zeichen/s); ein Schnitt darf ihn nie ueberschreiten '
                        'und das Tempo der Ausgangs-Einblendung nie verschlechtern')
    p.add_argument('-o', '--aus')
    p.add_argument('--protokoll')
    a = p.parse_args()

    # Pfade zuerst pruefen: im Messmodus wird --haeppchen nicht gelesen, ein Tippfehler
    # im Pfad fiele dort sonst erst beim spaeteren Nachschnitt auf.
    for feld, pfad in (('--srt', a.srt), ('--haeppchen', a.haeppchen), ('--kanten', a.kanten)):
        if pfad and not os.path.exists(pfad):
            print('FEHLER: %s zeigt auf eine Datei, die es nicht gibt: %s' % (feld, pfad), file=sys.stderr)
            sys.exit(3)

    cues = srt_lesen(a.srt)
    woerter_vorher = [w for c in cues for w in c['woerter']]
    vor = messen(cues, a)
    print('SRT %s — %d Einblendungen, %d Woerter' % (os.path.basename(a.srt), len(cues), len(woerter_vorher)))
    print('  Regel: %.1f-%.1f s, max %d Zeilen a %d Zeichen' % (a.min, a.max, a.zeilen, a.zeichen))
    print('  UEBER %.1f s: %d   unter %.1f s: %d   zu breit: %d   zu viele Zeilen: %d   ueber %.0f Zeichen/s: %d'
          % (a.max, len(vor['lang']), a.min, len(vor['kurz']), len(vor['breit']), len(vor['viele']),
             a.cps, len(vor['hetze'])))
    for n, d, t in vor['lang']:
        print('    #%-3d %.2f s  %s' % (n, d, t))

    if not a.aus:
        sys.exit(1 if (vor['lang'] or vor['breit'] or vor['viele']) else 0)

    # ---- nachschneiden
    kanten = kanten_lesen(a.kanten) if a.kanten else []
    zeiten_alle, abgleich = ([], None)
    if a.haeppchen:
        zeiten_alle, abgleich = wortzeiten(a.haeppchen, woerter_vorher)
    else:
        zeiten_alle = [None] * len(woerter_vorher)

    neu, notweg, i = [], 0, 0
    for c in cues:
        n = len(c['woerter'])
        z, ersatz = zeiten_ergaenzen(c, zeiten_alle[i:i + n])
        i += n
        if ersatz and c['t1'] - c['t0'] > a.max:
            notweg += 1
        neu.extend(teilen(c, z, kanten, a))

    # ---- Waechter: der Wortlaut muss Zeichen fuer Zeichen derselbe sein
    woerter_nachher = [w for c in neu for w in c['woerter']]
    if woerter_nachher != woerter_vorher:
        print('ABBRUCH: Wortfolge veraendert (%d -> %d). Nichts geschrieben.'
              % (len(woerter_vorher), len(woerter_nachher)), file=sys.stderr)
        sys.exit(2)
    for x, y in zip(neu, neu[1:]):
        if y['t0'] < x['t1'] - 1e-6:
            print('ABBRUCH: Einblendungen ueberlappen bei %.3f s. Nichts geschrieben.' % y['t0'], file=sys.stderr)
            sys.exit(2)

    nach = messen(neu, a)
    srt_schreiben(a.aus, neu, a.zeilen, a.zeichen)
    print('\ngeschrieben: %s — %d Einblendungen (vorher %d)' % (a.aus, len(neu), len(cues)))
    print('  UEBER %.1f s: %d (vorher %d)   unter %.1f s: %d (vorher %d)   ueber %.0f Zeichen/s: %d (vorher %d)'
          % (a.max, len(nach['lang']), len(vor['lang']), a.min, len(nach['kurz']), len(vor['kurz']),
             a.cps, len(nach['hetze']), len(vor['hetze'])))
    gruende = {}
    for c in neu:
        gruende[c.get('grund', 'quelle')] = gruende.get(c.get('grund', 'quelle'), 0) + 1
    print('  Schnittgruende: ' + ', '.join('%s=%d' % kv for kv in sorted(gruende.items())))
    if notweg:
        print('  HINWEIS: %d Einblendung(en) ohne Wortzeiten proportional geteilt' % notweg)
    for n, d, t in nach['lang']:
        print('  BLEIBT LANG #%-3d %.2f s  %s' % (n, d, t))

    if a.protokoll:
        with open(a.protokoll, 'w', encoding='utf-8') as f:
            json.dump({'srt': a.srt, 'aus': a.aus,
                       'regel': {'min': a.min, 'max': a.max, 'zeilen': a.zeilen, 'zeichen': a.zeichen},
                       'kanten': len(kanten), 'abgleich': abgleich,
                       'vorher': {'cues': len(cues), **{k: len(v) for k, v in vor.items()}},
                       'nachher': {'cues': len(neu), **{k: len(v) for k, v in nach.items()}},
                       'gruende': gruende, 'proportional_geteilt': notweg,
                       'bleibt_lang': nach['lang']}, f, ensure_ascii=False, indent=1)
        print('  Protokoll: %s' % a.protokoll)
    sys.exit(0)


if __name__ == '__main__':
    main()
