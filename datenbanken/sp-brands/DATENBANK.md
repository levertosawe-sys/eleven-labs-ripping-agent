---
name: sp-brands
typ: CSV (Tabelle)
zweck: Brand-Adressbuch der Speaking-Kette — je Ziel-Brand eine Zeile; löst Kürzel → brands/-Ordner, Sprache, Brand-Wissensdatenbank (AWMS-Hauptordner) und den customClips-Schalter auf. Ersetzt für diese Kette die Linien-Registry der Singing-Kette (Viktors Entscheid: komplett getrennt).
schreibt: die Session beim Anlegen einer neuen Ziel-Brand (mit Viktor) · die Audio-Prüfung (bett_offset_db nach Viktors Wahl an der Pegel-Leiter)
liest: das Ripping Sheet (Agent-Dialog + Auftrags-Bau, Spalte quell_brands) · der Trigger (Brand bestimmen) · singing-vsl-dach-lokalisierung (Brand-DB-Pfad) · speaking-vsl-uebersetzung (Brand-DB-Pfad für die Kundensprache) · custom-clips (Schalter) · tools/sp/bett_pegel.py (bett_offset_db)
format: daten.csv mit Kopfzeile; je Brand eine Zeile
---
# Brand-Adressbuch — Speaking

Spalten: `kuerzel` (Text, z. B. ROV) · `brand_ordner` (Ordnername unter `brands/`)
· `sprache` (de/fr/…) · `brand_db` (Pfad der Wissensdatenbank im AWMS-Hauptordner)
· `custom_clips` (true/false) · `quell_brands` (Semikolon-Liste der Sheet-Bibliotheken,
aus denen in diese Brand gerippt werden darf, z. B. `quasi;brand-searcher`; leer = jede
Quell-Brand) · `angelegt` (JJJJ-MM-TT) · `produkte` (Semikolon-Liste der Produkte dieser
Brand, benannt wie im `produkt-steckbrief.md`; seit 07.09.2026 — der Rip-Dialog bietet sie
zur Wahl, der Auftrag nennt das Ziel-Produkt, der Knoten produkt-abgleich hält die Quelle
dagegen; leer = kein Abgleich. Kein Komma im Produktnamen, die Datei ist kommagetrennt) · `bett_offset_db`
(Zahl in dB, Default 0: Viktors Ohr-Regler fürs Musikbett dieser Brand — 0 = exakt das gemessene
Original-Verhältnis Stimme→Bett, negativ = Bett leiser; liest `tools/sp/bett_pegel.py`, setzt die
Audio-Prüfung nach Viktors Wahl an der Pegel-Leiter).
Neue Brand = neue Zeile (mit Viktor abgestimmt) — kein Code, kein Deploy.

**Ripping Sheet (seit 02.09.2026, Viktors Entscheid):** Das Sheet liest diese Datei bei
jedem Zugriff und bietet die Brands hier im Rip-Dialog unter dem Agenten „🎙 Eleven Labs"
an (Schlüssel `SP:<KÜRZEL>`); der Auftragstext nennt Projektname, Inbox-Pfad und diese
Zeile. `brand_db` muss auf einen EXISTIERENDEN Ordner zeigen — Areum-Steckbrief und
Referenzbilder liegen in `brand-quasi/Product Reference/`, Orelias in `brand-resilia/`
(Stand 02.09.2026; eigene Ordner brand-areum/brand-orelia gibt es noch nicht).
Die Brand-Stimme wohnt NICHT hier, sondern im Stimmen-Register (datenbanken/stimmen).
