# Voraussetzungen — was da sein muss, bevor der erste Lauf startet

**Dieses Paket enthält KEINE Schlüssel.** Alle Konten unten sind eigene Konten des
Empfängers; die Schlüssel wohnen in einer eigenen `.env`-Datei außerhalb jedes Repos
(z. B. `~/.config/<projekt>/.env`) und werden nie committet.

---

## 1. Umgebung

| Was | Wofür | Prüfen mit |
|---|---|---|
| KI-Agent mit Datei- + Terminal-Zugriff (z. B. Claude Code) | führt die Kette aus | — |
| Linux- oder macOS-Rechner mit Platz (VSL-Videos sind groß) | Arbeitsort | `df -h` |
| `ffmpeg` + `ffprobe` | Messen, Zerlegen, Schneiden, Rendern | `ffmpeg -version` |
| Python 3.10+ (venv empfohlen) | Werkzeug-Skripte | `python3 --version` |
| `zip`/`rsync` | Übergabe-Pakete | `rsync --version` |
| CapCut auf dem Rechner des MENSCHEN | End-Montage + Sichtung | — |

## 2. Konten & Schlüssel

| Dienst | Wofür in dieser Kette | Pflicht? |
|---|---|---|
| **ElevenLabs** | Scribe-Transkript der Quelle · Sprechspur (Text-zu-Stimme, liefert Wort-Zeitstempel mit) · Stimm-Casting (Voice Design) | **Ja — das Herz der Linie** |
| **kie.ai** | Maschinen-Ohr (Gemini) für Prüfer/Abnahme · Vocal-Removal fürs Musikbett (Weg A) · optional Suno fürs Musikbett (Weg B) · Kling für Custom Clips | **Ja** |
| **Vmake** | eingebrannte Quell-Captions entfernen | Nur wenn die Quelle eingebrannte Captions hat (meist ja) |
| **Meta Marketing API** | Upload der fertigen Ad (immer pausiert) | Nur fürs letzte Glied — ohne endet der Lauf mit der fertigen MP4 |

Guthaben-Hinweis: Ein Longform-Lauf ruft ElevenLabs (Minuten an Audio, mehrere Takes je
Absatz), das Maschinen-Ohr (viele kurze Urteile) und ggf. Kling (Custom Clips) — vor dem
ersten Lauf Kontostände prüfen, statt mittendrin trocken zu laufen.

## 3. Ablage, die der erste Lauf anlegt (oder du vorher)

| Ordner | Zweck |
|---|---|
| `inbox/` | Einwurf: Quellvideo + finale Copy |
| `datenbanken/projekte/` | ein Ordner je Projekt — Karte mit Quell-Hash (Doppel-Rip-Schutz), Transkript, Übersetzung, Befund, finale Copy. Naming-Vorlage: `referenz/projekte-datenbank.DATENBANK.md` |
| `datenbanken/stimmen/` | das Stimmen-Register: je Brand die gewählte Stimme (voice_id, Design-Prompt, Einstellungen, Aussprache-Lexikon, gemessene Sprech-Rate) — **Geist, entsteht beim Casting** |
| `datenbanken/brand-<kürzel>/` | Brand-Wissen: Produkt-Fakten als Maßstab, Referenzbilder des eigenen Produkts (`Product Reference/`) für die Custom-Clip-Strecke, Lokalisierungs-Log |
| `brands/<KÜRZEL> - <Name>/<NNN SP>/` | Arbeitsordner je Ad (Pipeline, Song/Sprechspur, Renders, Übergabe-Paket) |
| `tools/sp/` | die Werkzeug-Skripte der Linie — **Geist, wächst im Use-and-Break** |

## 4. Was ausdrücklich NICHT im Paket ist

- **Schlüssel** — nie im Repo, siehe oben.
- **Meta-Adressbuch** (`ziele.json` mit Werbekonto/Seite/Pixel/Kampagne) — das sind
  Konto-Daten des Betreibers; der Skill `ad-upload` beschreibt das Format, angelegt
  wird es beim Einrichten mit eigenen IDs.
- **Datenbank-Inhalte** (Projekte, Brand-Wissen, Stimmen) — die entstehen aus eigener
  Arbeit; mitgegeben sind nur die Vertragskarten/Vorlagen.
- **Ripping Sheet** (die Browser-Software am Kettenanfang) — sie ist an den
  Ursprungs-Server gebunden. Der Hand-Weg funktioniert überall: MP4 in `inbox/` werfen
  und den Lauf im Chat starten; genau dafür hat die Kette den zweiten Trigger.
