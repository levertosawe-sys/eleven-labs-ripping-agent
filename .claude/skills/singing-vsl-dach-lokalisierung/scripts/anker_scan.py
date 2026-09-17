#!/usr/bin/env python3
"""Fremde Alltags-Anker in einer übersetzten Copy finden — Vorlauf zum Lokalisierungs-Befund.

Findet die Anker-Arten, die sich zuverlässig an Wortformen erkennen lassen: Laden- und
Ketten-Namen, Herkunfts-Bauteile ("US", "amerikanisch"), Währung und Maßeinheiten fremder
Systeme, dazu US-Bundesstaaten und große US-Städte. Personen- und Ortsnamen der Story kann
das Skript NICHT abschließend prüfen — dafür bleibt die Prüf-Dimension Figuren-Namen
zuständig; das Skript sagt am Ende selbst, was es nicht abdeckt.

Aufruf (ausführen, nicht lesen):
  python3 scripts/anker_scan.py <pfad zur uebersetzung-datei.md>

Ausgabe: je Fund eine Zeile `<Zeilennummer> · <Klasse> · "<Treffer>" · <Kontext>`, danach
eine Zählung je Klasse. Exit 0 = keine Funde, Exit 1 = Funde vorhanden (jeder Fund gehört
als Anpassung in den Befund), Exit 2 = Aufruf- oder Datei-Fehler.

Abhängigkeiten: nur die Standardbibliothek.
"""
import os
import re
import sys
from collections import Counter

# Ketten, die im DACH-Alltag nicht vorkommen. Nicht abschliessend — der Test ist
# "kommt dieser Laden im Alltag der Avatarin vor?", nicht die Liste.
KETTEN = [
    "Walmart", "Wal-Mart", "Target", "Costco", "Kroger", "Safeway", "Publix",
    "Whole Foods", "Trader Joe", "Dollar General", "Dollar Tree", "7-Eleven",
    "CVS", "Walgreens", "Rite Aid", "GNC", "Vitamin Shoppe", "Sam's Club",
    "Sprouts", "Wegmans", "Albertsons", "Duane Reade",
]
# Herkunfts-Bauteile. "US" case-sensitive mit Wortgrenze, damit "aus"/"Haus" nicht treffen.
HERKUNFT = [
    (r"\bUS\b", "US"), (r"\bU\.S\.\b", "U.S."), (r"\bUSA\b", "USA"),
    (r"\bamerikanisch\w*\b", "amerikanisch"), (r"\bAmerican\b", "American"),
    (r"\bStates\b", "States"),
]
WAEHRUNG = [(r"\$", "$"), (r"\bDollar\w*\b", "Dollar"), (r"\bUSD\b", "USD"),
            (r"\bCents?\b", "Cent (im Dollar-Kontext prüfen)")]
MASSE = [(r"\bMeilen?\b", "Meile"), (r"\bZoll\b", "Zoll"), (r"\bInch(es)?\b", "Inch"),
         (r"\bGallone[nr]?\b", "Gallone"), (r"\bFahrenheit\b", "Fahrenheit"),
         (r"\bUnzen?\b", "Unze"), (r"\bYards?\b", "Yard"), (r"\bFu(ss|ß)\b", "Fuß")]
US_ORTE = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "Kalifornien", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
    "Los Angeles", "San Francisco", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Diego", "Dallas", "Miami", "Atlanta", "Boston", "Seattle", "Denver",
    "Las Vegas", "Beverly Hills", "Brooklyn", "Manhattan", "Bronx", "Queens",
]

if len(sys.argv) < 2:
    print("FEHLER: Pfad zur Copy-Datei fehlt.\n"
          "  python3 scripts/anker_scan.py <projekte-db>/<projekt>/<slug>-uebersetzung-<JJJJ-MM-TT>.md",
          file=sys.stderr)
    raise SystemExit(2)
pfad = sys.argv[1]
if not os.path.isfile(pfad):
    print(f"FEHLER: Datei nicht gefunden: {pfad}\n"
          "  Der Pfad ist die Übersetzungs-Datei aus dem Abschnitt Eingabe dieses Skills.",
          file=sys.stderr)
    raise SystemExit(2)
try:
    zeilen = open(pfad, encoding="utf-8").read().splitlines()
except UnicodeDecodeError:
    print(f"FEHLER: {pfad} ist nicht UTF-8 — bitte als UTF-8 speichern.", file=sys.stderr)
    raise SystemExit(2)

muster = []
muster += [(re.compile(re.escape(k), re.I), "laden", k) for k in KETTEN]
muster += [(re.compile(p), "herkunft", name) for p, name in HERKUNFT]
muster += [(re.compile(p, re.I), "waehrung", name) for p, name in WAEHRUNG]
muster += [(re.compile(p, re.I), "mass", name) for p, name in MASSE]
muster += [(re.compile(re.escape(o), re.I), "ort", o) for o in US_ORTE]

funde = []
for nr, zeile in enumerate(zeilen, 1):
    for rx, klasse, name in muster:
        m = rx.search(zeile)
        if m:
            kontext = zeile.strip()
            if len(kontext) > 90:
                s = max(0, m.start() - 40)
                kontext = ("…" if s else "") + kontext[s:s + 90] + "…"
            funde.append((nr, klasse, name, kontext))

if funde:
    print(f"{len(funde)} Fund(e) in {pfad}:\n")
    for nr, klasse, name, kontext in funde:
        print(f"  Zeile {nr:4d} · {klasse:9s} · \"{name}\" · {kontext}")
    print("\nZählung je Klasse:", dict(Counter(k for _, k, _, _ in funde)))
    print("Jeder Fund gehört als Anpassung in den Befund — Alltags-Anker haben kein "
          "\"Original lassen\".")
else:
    print(f"Keine Laden-, Herkunfts-, Währungs- oder Maß-Funde in {pfad}.")

print("\nNICHT abgedeckt (von Hand prüfen): Personen- und Ortsnamen der Story, die nicht "
      "aus den USA stammen (z. B. spanische oder italienische Namen einer fremdsprachigen "
      "Quelle) — dafür die Prüf-Dimensionen Figuren-Namen und Kulturelle Anker.")
raise SystemExit(1 if funde else 0)
