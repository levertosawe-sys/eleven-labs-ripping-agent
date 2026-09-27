"""CapCut-Export: aus den Bausteinen des Musik-Finders ein BEARBEITBARES CapCut-Projekt.

Kein offizielles Format, keine API — deshalb SCHABLONEN-CHIRURGIE: Wir nehmen ein echtes
Projekt von Viktors Platte als Spender (gleiche CapCut-Version, gleiche Feld-Sätze),
leeren die Spuren und setzen unsere Segmente hinein. Nach einem CapCut-Update wird einfach
ein frisches echtes Projekt zum Spender — dafür `spender_finden()`.

Was gebaut wird (alles als EIGENE, in CapCut editierbare Spuren):
  Video   — die einzelnen Clips (Grenzen kommen exakt aus dem B-Roll-Sourcer)
  Audio 1 — die gemischte Musik (mit Wechsel-Geometrie, Fades, Lautstärken)
  Audio 2 — die platzierten Sound-Effekte
  Text    — Captions als native CapCut-Vorlagen-Segmente (mit Wort-Timings)

Fallen, die Blut gekostet haben — nicht „aufräumen":
  · Mac-CapCut nutzt draft_info.json (NICHT draft_content.json wie Windows/JianYing)
  · Zeiten in MIKROSEKUNDEN
  · Jedes Segment braucht EIGENE extra_material_refs (Speed/Canvas/… frisch klonen)
  · root_meta_info.json muss den Eintrag kennen, sonst taucht das Projekt nie auf
  · Das Projekt erscheint erst nach einem CAPCUT-NEUSTART
  · Segment-Dauer = EXAKTE Schnitt-Dauer, nicht die Datei-Länge (AAC-Padding schiebt
    sonst je Clip ~40 ms auf -> Captions sind hinten ~1 s daneben)
"""
from __future__ import annotations

import copy
import json
import math
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"
# ffprobe maschinen-unabhängig auflösen: PATH zuerst, dann die üblichen Homebrew-Orte
FFPROBE = (shutil.which("ffprobe")
           or next((p for p in ("/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe")
                    if Path(p).exists()), "ffprobe"))


# ---------------------------------------------------------------- kleine Helfer

def neue_id() -> str:
    return str(uuid.uuid4()).upper()


def _probe(pfad: Path, felder: str) -> str:
    p = subprocess.run([FFPROBE, "-v", "error", "-show_entries", felder,
                        "-of", "csv=p=0", str(pfad)], capture_output=True, text=True)
    return p.stdout.strip()


def dauer_us(pfad: Path) -> int:
    try:
        return int(float(_probe(pfad, "format=duration")) * 1_000_000)
    except (ValueError, IndexError):
        return 1_000_000


def clip_dims(pfad: Path):
    try:
        w, h = _probe(pfad, "stream=width,height").split("\n")[0].split(",")[:2]
        return int(w), int(h)
    except (ValueError, IndexError):
        return 1080, 1920


def sicherer_name(name: str) -> str:
    name = re.sub(r'[/\\:*?"<>|]', "-", str(name or "Projekt")).strip()
    return (name or "Projekt")[:60]


def draft_pfad(name: str) -> Path:
    return ROOT / sicherer_name(name)


def media_pfad(name: str) -> Path:
    """Die Medien müssen INNERHALB des CapCut-Projektordners liegen!
    CapCut ist eine Sandbox-App: Dateien woanders (z.B. in AWMS) quittiert es beim
    Öffnen mit „Kein Zugriff auf die Datei möglich" und will sie neu verknüpfen."""
    return draft_pfad(name) / "awms_media"


def draft_token() -> str | None:
    """Das Platzhalter-Kürzel, mit dem CapCut Pfade INNERHALB eines Projektordners schreibt.

    Es ist pro Installation gleich (kein Projekt-Schlüssel) und wird deshalb aus einem
    vorhandenen Projekt gelesen, statt geraten. Ein selbst geschriebener absoluter Pfad
    öffnet nicht zuverlässig — geschrieben wird die Form, die CapCut selbst benutzt."""
    for ordner in sorted(ROOT.glob("*/draft_info.json"), key=lambda p: -p.stat().st_mtime)[:20]:
        treffer = re.search(r"##_draftpath_placeholder_[0-9A-Fa-f-]+_##", ordner.read_text(errors="ignore")[:400000])
        if treffer:
            return treffer.group(0)
    return None


def im_draft(pfad: Path, name: str) -> str:
    """Pfad für draft_info.json: innerhalb des Projektordners als CapCut-Platzhalter, sonst absolut."""
    token = draft_token()
    d = str(draft_pfad(name))
    s = str(pfad)
    return token + s[len(d):] if token and s.startswith(d) else s


def platz_machen(name: str) -> Path:
    """Den Projektordner LEER hinterlassen — CapCut schreibt beim Öffnen eigenen Zustand
    hinein (Timelines/, subdraft/, draft_virtual_store.json …). Bleibt der beim
    Neu-Export liegen, zeigt CapCut zwei Zeitleisten und einen toten Player.

    SCHUTZ: Nur Ordner anfassen, die von UNS stammen (erkennbar an awms_media) —
    ein echtes CapCut-Projekt mit gleichem Namen wird NIE gelöscht."""
    draft = draft_pfad(name)
    if draft.exists():
        if not (draft / "awms_media").exists() and (draft / "draft_info.json").exists():
            raise RuntimeError(
                f"In CapCut gibt es schon ein eigenes Projekt namens {draft.name} - "
                "ich fasse es nicht an. Bitte das Musik-Finder-Projekt umbenennen.")
        shutil.rmtree(draft, ignore_errors=True)
    draft.mkdir(parents=True)
    return draft


# ---------------------------------------------------------------- Spender

def spender_finden(bevorzugt: str | None = None) -> Path:
    """Ein echtes Projekt als Schablone: braucht Video- + Audio- + Text-Segmente und
    text_templates (nur die geben Captions den „Vorlagen"-Tab). Neuestes zuerst —
    nach einem CapCut-Update ist das automatisch eins im neuen Format."""
    kandidaten = []
    for p in (ROOT.iterdir() if ROOT.exists() else []):
        f = p / "draft_info.json"
        if not f.is_file():
            continue
        # Eigene Exporte überspringen (erkennbar an awms_media). Sonst wird die Kopie
        # zur Schablone der nächsten Kopie — Fehler würden sich einbrennen und
        # weitervererben. Schablone ist immer ein von Hand gebautes Viktor-Projekt.
        if (p / "awms_media").exists():
            continue
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        spuren = {t.get("type") for t in d.get("tracks", []) if t.get("segments")}
        if not {"video", "audio", "text"} <= spuren:
            continue
        if not d.get("materials", {}).get("text_templates"):
            continue
        kandidaten.append((f.stat().st_mtime, p))
    if not kandidaten:
        raise RuntimeError("Kein CapCut-Projekt als Schablone gefunden. Bitte einmal ein "
                           "echtes Projekt in CapCut anlegen (Clips + Musik + Untertitel).")
    if bevorzugt:
        for _, p in kandidaten:
            if p.name == bevorzugt:
                return p
    return max(kandidaten)[1]


def wort_zeiten(text: str, dauer_ms: int, woerter: list[dict] | None = None) -> dict:
    """Wort-Timings im CapCut-Format: Millisekunden relativ zum Segment, Leerzeichen
    als eigene Null-Dauer-Einträge (so erwartet CapCut es für die Karaoke-Hervorhebung).

    Mit `woerter` (aus captions.haeppchen(), Zeiten in Sekunden relativ zum Häppchen)
    sind es die ECHTEN Zeiten aus dem Ton. Ohne — nur als Notnagel, wenn keine
    Ausrichtung vorliegt — gleichmäßig nach Wortlänge geschätzt.
    """
    tokens, starts, enden = [], [], []
    if woerter:
        for i, w in enumerate(woerter):
            if i:
                # Leerzeichen füllt die Lücke zwischen zwei Wörtern
                tokens.append(" ")
                starts.append(int(enden[-1]))
                enden.append(int(round(w["start"] * 1000)))
            tokens.append(w["text"])
            starts.append(int(round(w["start"] * 1000)))
            enden.append(int(round(w["end"] * 1000)))
        return {"start_time": starts, "end_time": enden, "text": tokens}
    for i, w in enumerate(str(text).split(" ")):
        if i:
            tokens.append(" ")
        tokens.append(w)
    gewichte = [len(t) if t != " " else 0 for t in tokens]
    summe = sum(gewichte) or 1
    nutz = int(dauer_ms * 0.92)
    cursor = 0
    for g in gewichte:
        anteil = int(nutz * g / summe)
        starts.append(cursor)
        enden.append(cursor + anteil if anteil else cursor)
        cursor += anteil
    return {"start_time": starts, "end_time": enden, "text": tokens}


# ---------------------------------------------------------------- Draft bauen

def draft_bauen(name, clips, musik=None, sfx=None, captions=None, cover=None,
                spender=None, log=None, uebergaenge=None):
    """Baut den CapCut-Projektordner und meldet ihn an. Gibt (pfad, infos) zurück.

    clips:      [{pfad, dauer}]          — Dauer in SEKUNDEN (die exakte Schnitt-Dauer!)
    musik:      {pfad} | None            — eine fertige Musik-Spur
    sfx:        [{pfad, t, gain?, fade_in?, fade_out?, quelle_ab?, dauer?}] — Sekunden/dB
    captions:   [{text, t, dauer}] | None
    uebergaenge: [{nach_clip, material}] — CapCut-Übergänge, geerntet aus einem echten
                Projekt (draft_lesen): material ist der verbatim-Klon aus dessen
                materials.transitions, nach_clip der 0-basierte Clip, an dessen ENDE
                der Übergang sitzt. Braucht den lokalen CapCut-Effekt-Cache — gegeben,
                solange auf demselben Mac geerntet wurde.
    """
    def _log(s):
        if log:
            log(s)

    donor_p = spender_finden(spender)
    donor = json.loads((donor_p / "draft_info.json").read_text())
    _log(f"Schablone: {donor_p.name}")

    mats = donor["materials"]
    video_track = next(t for t in donor["tracks"] if t["type"] == "video" and t.get("segments"))
    audio_track = next(t for t in donor["tracks"] if t["type"] == "audio" and t.get("segments"))
    text_track = next(t for t in donor["tracks"] if t["type"] == "text" and t.get("segments"))
    proto_vseg = copy.deepcopy(video_track["segments"][0])
    proto_aseg = copy.deepcopy(audio_track["segments"][0])
    proto_cseg = copy.deepcopy(text_track["segments"][0])
    proto_vmat = copy.deepcopy(next(m for m in mats["videos"] if m["id"] == proto_vseg["material_id"]))
    proto_amat = copy.deepcopy(next(m for m in mats["audios"] if m["id"] == proto_aseg["material_id"]))

    index = {}
    for art, liste in mats.items():
        if isinstance(liste, list):
            for m in liste:
                if isinstance(m, dict) and "id" in m:
                    index[m["id"]] = (art, m)

    def refs_von(seg):
        return [(index[r][0], copy.deepcopy(index[r][1]))
                for r in seg.get("extra_material_refs", []) if r in index]

    proto_vrefs = refs_von(proto_vseg)
    # ⛔ audio_fades NICHT mitklonen: das Spender-Segment bringt seine eigene
    # Ausblende-Kurve mit (z.B. 7,3 s fade_out) — geerbt läge sie auf JEDER Musik- und
    # SFX-Spur und würgt z.B. einen Riser genau vor seinem Höhepunkt ab (Viktors
    # „schwarze Balken"). Fades schreiben wir nur noch BEWUSST, je Segment (unten).
    proto_arefs = [(art, obj) for art, obj in refs_von(proto_aseg) if art != "audio_fades"]
    proto_crefs = refs_von(proto_cseg)
    # Fade-Schema des Spenders als Vorlage fürs bewusste Schreiben; hat der Spender
    # keins, reicht das minimale bekannte Schema (Zeiten in Mikrosekunden).
    proto_fade = copy.deepcopy(next(iter(mats.get("audio_fades") or []), None)) or {
        "id": "", "type": "audio_fade", "fade_type": 0,
        "fade_in_duration": 0, "fade_out_duration": 0}

    # Caption-Vorlage (text_template_subtitle) + inneres Text-Material
    proto_tpl = copy.deepcopy(next(m for m in mats["text_templates"] if m["id"] == proto_cseg["material_id"]))
    texts_idx = {x["id"]: x for x in mats.get("texts", [])}
    innen_id = proto_tpl["text_info_resources"][0]["text_material_id"]
    proto_inner = copy.deepcopy(texts_idx[innen_id])
    proto_inhalt = json.loads(proto_inner["content"])
    proto_tir_refs = [(index[r][0], copy.deepcopy(index[r][1]))
                      for r in proto_tpl["text_info_resources"][0].get("extra_material_refs", []) if r in index]

    neu = copy.deepcopy(donor)
    neu["id"] = neue_id()
    for art in neu["materials"]:
        if isinstance(neu["materials"][art], list):
            neu["materials"][art] = []

    def material_rein(art, obj):
        obj = copy.deepcopy(obj)
        obj["id"] = neue_id()
        neu["materials"].setdefault(art, []).append(obj)
        return obj["id"]

    def segment_bauen(proto, refs, mat_id, start_us, dauer, quelle=True):
        seg = copy.deepcopy(proto)
        seg["id"] = neue_id()
        seg["material_id"] = mat_id
        seg["target_timerange"] = {"start": int(start_us), "duration": int(dauer)}
        seg["source_timerange"] = {"start": 0, "duration": int(dauer)} if quelle else None
        seg["extra_material_refs"] = [material_rein(art, obj) for art, obj in refs]
        return seg

    def spur_bauen(vorbild, typ, segmente):
        spur = copy.deepcopy(vorbild)
        spur["id"] = neue_id()
        spur["type"] = typ
        spur["segments"] = segmente
        return spur

    # ---- Video-Spur ----
    vsegs, kum = [], 0
    for c in clips:
        pfad = Path(c["pfad"])
        datei_us = dauer_us(pfad)
        d_us = min(int(round(float(c["dauer"]) * 1_000_000)), datei_us)
        w, h = clip_dims(pfad)
        m = copy.deepcopy(proto_vmat)
        m.update({"path": im_draft(pfad, name), "material_name": pfad.name, "duration": datei_us,
                  "width": w, "height": h})
        vsegs.append(segment_bauen(proto_vseg, proto_vrefs, material_rein("videos", m), kum, d_us))
        kum += d_us
    gesamt_us = kum
    _log(f"{len(vsegs)} Clips · {gesamt_us / 1e6:.2f}s")

    # Geerntete CapCut-Übergänge an die Nähte hängen (Referenz sitzt am Clip DAVOR —
    # dasselbe Muster wie in Viktors echten Projekten).
    n_ueber = 0
    for u in (uebergaenge or []):
        try:
            i = int(u.get("nach_clip", -1))
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(vsegs) - 1 and isinstance(u.get("material"), dict):
            vsegs[i]["extra_material_refs"].append(material_rein("transitions", u["material"]))
            n_ueber += 1
            _log(f"Übergang {u['material'].get('name', '?')} nach Clip {i + 1}")

    spuren = [spur_bauen(video_track, "video", vsegs)]

    # ---- Captions (native Vorlagen-Segmente) ----
    csegs = []
    for c in (captions or []):
        text = str(c.get("text") or "").strip()
        if not text:
            continue
        d_us = int(round(float(c["dauer"]) * 1_000_000))
        start = int(round(float(c["t"]) * 1_000_000))
        inner = copy.deepcopy(proto_inner)
        inner["id"] = neue_id()
        inhalt = copy.deepcopy(proto_inhalt)
        inhalt["text"] = text
        for st in inhalt.get("styles", []):
            st["range"] = [0, len(text)]
        inner["content"] = json.dumps(inhalt, ensure_ascii=False)
        inner["words"] = wort_zeiten(text, d_us // 1000, c.get("woerter"))
        neu["materials"]["texts"].append(inner)
        tpl = copy.deepcopy(proto_tpl)
        tpl["id"] = neue_id()
        tir = tpl["text_info_resources"][0]
        tir["id"] = neue_id()
        tir["text_material_id"] = inner["id"]
        tir["attach_info"]["duration"] = d_us
        tir["extra_material_refs"] = [material_rein(art, obj) for art, obj in proto_tir_refs]
        neu["materials"]["text_templates"].append(tpl)
        csegs.append(segment_bauen(proto_cseg, proto_crefs, tpl["id"], start, d_us, quelle=False))
    if csegs:
        spuren.append(spur_bauen(text_track, "text", csegs))
        _log(f"{len(csegs)} Captions")

    # ---- Audio: Musik + SFX ----
    def audio_segment(pfad, start_us, max_dauer=None, gain_db=0.0,
                      fade_in=0.0, fade_out=0.0, quelle_ab=0.0):
        """Ein Audio-Segment mit BEWUSSTEN Eigenschaften: Lautstärke in dB, Ein-/
        Ausblende in Sekunden, quelle_ab = Startpunkt in der Datei (getrimmter Kopf).
        Fades entstehen als frisches Material — nie geerbt (siehe proto_arefs)."""
        pfad = Path(pfad)
        d_us = dauer_us(pfad)
        ab_us = int(round(max(0.0, float(quelle_ab)) * 1_000_000))
        nutz = max(1, d_us - ab_us)
        if max_dauer:
            nutz = min(nutz, int(max_dauer))
        seg = segment_bauen(proto_aseg, proto_arefs, material_rein("audios", copy.deepcopy(proto_amat) | {
            "path": im_draft(pfad, name), "name": pfad.stem, "material_name": pfad.name,
            "duration": d_us}), start_us, nutz)
        seg["source_timerange"] = {"start": ab_us, "duration": int(nutz)}
        vol = round(10 ** (max(-36.0, min(9.0, float(gain_db))) / 20), 6)
        seg["volume"] = vol
        if "last_nonzero_volume" in seg:
            seg["last_nonzero_volume"] = vol
        if fade_in or fade_out:
            f = copy.deepcopy(proto_fade)
            f["fade_in_duration"] = int(round(max(0.0, float(fade_in)) * 1_000_000))
            f["fade_out_duration"] = int(round(max(0.0, float(fade_out)) * 1_000_000))
            seg["extra_material_refs"].append(material_rein("audio_fades", f))
        return seg

    if musik and Path(musik["pfad"]).exists():
        spuren.append(spur_bauen(audio_track, "audio",
                                 [audio_segment(musik["pfad"], 0, max_dauer=gesamt_us)]))
        _log("Musik-Spur")
    if sfx:
        segs = []
        for s in sfx:
            if not Path(s["pfad"]).exists():
                continue
            wunsch = int(round(float(s["dauer"]) * 1_000_000)) if s.get("dauer") else None
            segs.append(audio_segment(
                s["pfad"], int(round(float(s["t"]) * 1_000_000)), max_dauer=wunsch,
                gain_db=float(s.get("gain") or 0.0),
                fade_in=float(s.get("fade_in") or 0.0), fade_out=float(s.get("fade_out") or 0.0),
                quelle_ab=float(s.get("quelle_ab") or 0.0)))
        if segs:
            spuren.append(spur_bauen(audio_track, "audio", segs))
            _log(f"{len(segs)} Sound-Effekte")

    neu["tracks"] = spuren
    neu["duration"] = gesamt_us

    # ---- Schreiben + bei CapCut anmelden ----
    draft = ROOT / sicherer_name(name)
    draft.mkdir(parents=True, exist_ok=True)
    (draft / "draft_info.json").write_text(json.dumps(neu, ensure_ascii=False))
    if cover and Path(cover).exists():
        shutil.copy2(cover, draft / "draft_cover.jpg")

    meta = json.loads((donor_p / "draft_meta_info.json").read_text())
    jetzt_us = int(time.time() * 1_000_000)
    meta.update({"draft_id": neu["id"], "draft_name": draft.name,
                 "draft_fold_path": str(draft), "draft_root_path": str(ROOT),
                 "draft_json_file": str(draft / "draft_info.json"),
                 "draft_cover": "draft_cover.jpg", "tm_draft_create": jetzt_us,
                 "tm_draft_modified": jetzt_us, "tm_duration": gesamt_us})
    if isinstance(meta.get("draft_materials"), list):
        meta["draft_materials"] = [{**b, "value": []} if isinstance(b, dict) else b
                                   for b in meta["draft_materials"]]
    (draft / "draft_meta_info.json").write_text(json.dumps(meta, ensure_ascii=False))

    root_pfad = ROOT / "root_meta_info.json"
    backup = ROOT / "root_meta_info.json.awms-backup"
    if not backup.exists() and root_pfad.exists():
        backup.write_bytes(root_pfad.read_bytes())
    root = json.loads(root_pfad.read_text())
    eintraege = [e for e in root.get("all_draft_store", []) if e.get("draft_name") != draft.name]
    if not eintraege:
        raise RuntimeError("root_meta_info.json hat keine Vorlage für den Eintrag.")
    vorbild = copy.deepcopy(eintraege[0])
    vorbild.update({"draft_id": neu["id"], "draft_name": draft.name,
                    "draft_fold_path": str(draft), "draft_root_path": str(ROOT),
                    "draft_json_file": str(draft / "draft_info.json"),
                    "draft_cover": str(draft / "draft_cover.jpg"),
                    "draft_new_version": donor.get("new_version", "")})
    root["all_draft_store"] = [vorbild] + eintraege
    if isinstance(root.get("draft_ids"), list) and neu["id"] not in root["draft_ids"]:
        root["draft_ids"] = [neu["id"]] + root["draft_ids"]
    root_pfad.write_text(json.dumps(root, ensure_ascii=False))

    return draft, {"clips": len(vsegs), "captions": len(csegs), "spuren": len(spuren),
                   "uebergaenge": n_ueber,
                   "dauer_s": round(gesamt_us / 1e6, 2), "schablone": donor_p.name}


# ---------------------------------------------------------------- Draft zurücklesen
# Die Rück-Ernte: Viktor perfektioniert ein exportiertes Projekt IN CapCut (verschiebt
# SFX, legt Übergänge, holt neue Sounds dazu) — draft_lesen() liest diesen Stand zurück,
# damit die Kombi ihn ernten kann. Das Draft ist dann die Wahrheit, nicht unser job.json.

def draft_lesen(name: str) -> dict:
    """Ein CapCut-Projekt (draft_info.json) zurücklesen.

    Gibt {uebergaenge, audios, naehte, dauer}:
      uebergaenge: [{nach_clip, zeit, material}] — material = verbatim-Klon fürs
                   spätere Wieder-Einsetzen über draft_bauen(uebergaenge=…)
      audios:      [{datei, pfad, eigene, t, dauer, quelle_ab, gain, fade_in, fade_out}]
                   eigene=True = stammt aus unserem Export (liegt in awms_media)
      naehte:      absolute Zeiten der Clip-Grenzen (Sekunden)
    CapCut schreibt Pfade im Draft-Ordner als ##_draftpath_placeholder_…## — die werden
    auf den echten Ordner aufgelöst."""
    draft = draft_pfad(name)
    d = json.loads((draft / "draft_info.json").read_text())
    mats = d.get("materials") or {}
    fades = {m["id"]: m for m in mats.get("audio_fades") or [] if isinstance(m, dict)}
    trans = {m["id"]: m for m in mats.get("transitions") or [] if isinstance(m, dict)}
    audio_mat = {m["id"]: m for m in mats.get("audios") or [] if isinstance(m, dict)}
    us = 1_000_000

    uebergaenge, naehte = [], []
    vtrack = next((t for t in d.get("tracks", []) if t.get("type") == "video" and t.get("segments")), None)
    if vtrack:
        segs = vtrack["segments"]
        for i, sg in enumerate(segs):
            tt = sg.get("target_timerange") or {}
            ende = round((tt.get("start", 0) + tt.get("duration", 0)) / us, 3)
            if i < len(segs) - 1:
                naehte.append(ende)
            for r in sg.get("extra_material_refs") or []:
                if r in trans:
                    uebergaenge.append({"nach_clip": i, "zeit": ende,
                                        "material": copy.deepcopy(trans[r])})

    audios = []
    for t in d.get("tracks", []):
        if t.get("type") != "audio":
            continue
        for sg in t.get("segments") or []:
            m = audio_mat.get(sg.get("material_id")) or {}
            roh = str(m.get("path") or "")
            pfad = re.sub(r"##_draftpath_placeholder_[0-9A-Fa-f-]+_##", str(draft), roh)
            tt = sg.get("target_timerange") or {}
            st = sg.get("source_timerange") or {}
            fade = next((fades[r] for r in sg.get("extra_material_refs") or [] if r in fades), None) or {}
            try:
                vol = float(sg.get("volume", 1.0))
            except (TypeError, ValueError):
                vol = 1.0
            audios.append({
                "datei": Path(pfad).name,
                "pfad": pfad,
                "eigene": "awms_media" in roh,
                "t": round(tt.get("start", 0) / us, 3),
                "dauer": round(tt.get("duration", 0) / us, 3),
                "quelle_ab": round(st.get("start", 0) / us, 3) if st else 0.0,
                "gain": round(20 * math.log10(vol), 1) if vol > 0 else -36.0,
                "fade_in": round(fade.get("fade_in_duration", 0) / us, 2),
                "fade_out": round(fade.get("fade_out_duration", 0) / us, 2),
            })
    return {"uebergaenge": uebergaenge, "audios": audios, "naehte": naehte,
            "dauer": round((d.get("duration") or 0) / us, 3)}
