---
name: "Background Music via Suno V5"
description: "Purpose: Generate brand-matched custom instrumental BGM for an ad and mix it under the existing voice-over track. Use when the user wants BGM but the existing royalty-free option doesn't fit the brand tonality (e.g. an 'Inspiring Triumphant Trailer' track is too bombastic for a warm/empathic"
---
# Skill — Background Music via Suno V5 (kie.ai)

> **Purpose:** Generate brand-matched custom instrumental BGM for an ad and mix
> it under the existing voice-over track. Use when the user wants BGM but the
> existing royalty-free option doesn't fit the brand tonality (e.g. an
> "Inspiring Triumphant Trailer" track is too bombastic for a warm/empathic
> brand voice).
>
> **When to use:** Step 6 of `full-ad-production-workflow.md` — only when user
> explicitly requests BGM. Default for LEI projects is **VO-only** (per user
> preference confirmed 2026-06-10).

---

## Suno V5 Custom Mode (Instrumental Only)

### Dispatch

**Endpoint:** `POST https://api.kie.ai/api/v1/generate`

```bash
source ~/.config/[brand]/.env

curl -sS -X POST "https://api.kie.ai/api/v1/generate" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "",
    "style": "<style brief — long descriptor>",
    "title": "<track name>",
    "negativeTags": "<comma-separated styles to AVOID>",
    "customMode": true,
    "instrumental": true,
    "model": "V5",
    "callBackUrl": "https://example.com/cb"
  }'
# → {"code":200,"data":{"taskId":"<hex32>"}}
```

**Supported models:** `V4`, `V4_5`, `V4_5PLUS`, `V4_5ALL`, `V5`, `V5_5`
(use V5 for best balance of quality + speed)

### Poll

**Endpoint:** `GET https://api.kie.ai/api/v1/generate/record-info?taskId=<ID>`

(Note: this is NOT the `/jobs/recordInfo` endpoint used for Kling — different
namespace.)

```bash
curl -sS "https://api.kie.ai/api/v1/generate/record-info?taskId=$TID" \
  -H "Authorization: Bearer $KIE_API_KEY"
```

**Response shape:**
```json
{
  "code": 200,
  "data": {
    "status": "SUCCESS" | "PENDING" | "FAILED",
    "response": {
      "sunoData": [
        {"id": "<uuid>", "audioUrl": "https://tempfile.aiquickdraw.com/..."},
        {"id": "<uuid>", "audioUrl": "..."}
      ]
    }
  }
}
```

Suno always returns **2 variations per task** — download both, let user pick.

**Render time:** typically 60-180s for instrumental tracks. Output is 3-5 min.

---

## Style Prompt Engineering for Brand-Matched BGM

The `style` field accepts long descriptive prose. Cover:

1. **Instrument list** — what plays (acoustic guitar, piano, strings, etc.)
2. **Arc** — quiet→build→peak, or steady, or fade-in
3. **Mood** — emotional reference points (warm, intimate, hopeful, contemplative)
4. **Vibe references** — "documentary feel", "Pixar emotional moment", "Sunday morning warmth"
5. **Anti-references** — what it's NOT (no trailer drums, no EDM, no aggressive)

**Always also set `negativeTags`** — comma-separated genres/elements to avoid:
- `"trailer drum hits, bombastic, electronic synth, edm, dubstep, aggressive, dark, horror, distortion, harsh metallic, sad-only, depressing"`

### LEI brand validated style brief (warm Heilpraktikerin / Klostermedizin)

```
Warm acoustic cinematic instrumental, soft fingerpicked acoustic guitar and
gentle piano in foreground, warm cello and viola strings entering in second
half, light handpan and marimba accents, hopeful healing compassionate tone,
intimate documentary feel, traditional herbal medicine and monastery garden
atmosphere, golden hour warmth, building from quiet reflection to soft uplift
over 3 minutes, organic natural breathable, Pixar emotional moment soundtrack vibe
```

Negative tags:
```
trailer drum hits, bombastic, electronic synth, edm, dubstep, aggressive,
dark, horror, distortion, harsh metallic, sad-only, depressing
```

This produced a 4:20 BGM track for LEI 003 CC V14 — user later opted to ship
without BGM (VO-only preferred for this brand), but the recipe is locked for
future use.

---

## Mixing BGM Under Existing Ad

The existing finished ad MP4 (e.g. `LEI_003_CC_HookA_FINAL_V13.mp4`) already
has the narrator audio at full level. Mix BGM in via ffmpeg complex filter.

**Canonical BGM volume:** `0.08` (volume factor) = **−22 dB** below VO.

This level:
- Keeps the narrator clearly intelligible
- BGM is sensed emotionally but not foreground
- Phone speakers + headphones both work

```bash
ffmpeg -y -i final/<ad>_V<N>.mp4 -i bgm/<bgm>.mp3 \
  -filter_complex "
    [1:a]volume=0.08,
         afade=in:st=0:d=2,
         afade=out:st=<ad_len-3>:d=3,
         atrim=0:<ad_len>,
         asetpts=PTS-STARTPTS[bgm];
    [0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mix]
  " \
  -map 0:v -map "[mix]" -c:v copy -c:a aac -b:a 192k -movflags +faststart \
  final/<ad>_V<N+1>.mp4
```

Where `<ad_len>` = the original ad duration in seconds (e.g. 195.1 for LEI 003
CC V13). Fade-out starts 3s before end so it doesn't pop.

**Critical filter flags:**
- `normalize=0` on the amix — prevents the mixer from auto-attenuating both
  streams to prevent clip (which would lower the VO)
- `asetpts=PTS-STARTPTS` after atrim — resets timestamps to start at 0
- `duration=first` on amix — output length = first input (VO) length

---

## Volume Adjustment Recipe

If user feedback is "BGM too loud":
- Drop to `0.05` (≈ −26 dB) or even `0.03` for very subtle background

If "BGM too quiet":
- Raise to `0.12` (≈ −18 dB) — still under VO but noticeable

If "Want BGM swell at CTA only":
- Replace single volume with `volume='if(gt(t,180),0.18,0.05)':eval=frame`
  (ramps from 0.05 to 0.18 starting at t=180s)

---

## Reuse Across Hook Variants

Once a BGM is chosen for a project, persist as
`<project>/bgm/<project>_bgm_master.mp3`. Apply the SAME track to all hook
variants (A, B, C) so the brand audio identity stays consistent. Each variant
just re-runs the ffmpeg mix step against its own V<N>.mp4 base.

---

## Cost

- Suno V5 instrumental generation: ~30 credits on kie.ai ≈ **$0.15** per task
  (2 variations included)
- Mixing: $0 (local ffmpeg)
- Total per project: <$0.50 even with 2-3 prompt iterations

---

## When NOT to use this skill

- Brand explicitly prefers VO-only (default for LEI — confirmed by user 2026-06-10)
- Brand has a licensed track they want to use (use that directly with the
  same ffmpeg mix recipe, just skip Suno)
- Existing BGM is good enough — A/B test it before regenerating
- Music must use specific real-world melody (Suno can't reproduce
  copyrighted melodies — would need licensed track)

---

## See Also

- `full-ad-production-workflow.md` Step 6 — where BGM mixing fits in pipeline
- `kie-ai-kling-integration.md` — same kie.ai auth + polling pattern

---

## Addendum (validated LEI 014 VM, 2026-07-01)

### ElevenLabs Music API — fallback when kie.ai/Suno is out of credits
When kie.ai returns `402 Credits insufficient` and Higgsfield can't do music (`generate_audio`
is speech-only), generate the track directly on the **ElevenLabs Music API** using the same
`ELEVENLABS_API_KEY`:
```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $KEY" -H "Content-Type: application/json" \
  -o bgm.mp3 -d '{"prompt":"<full instrumental style brief, say NO vocals>","music_length_ms":225000}'
```
Returns the MP3 directly (no polling). `music_length_ms` ≈ ad length (it honors it — 225s here).
Same mixing recipe (volume 0.08–0.10, afade in/out, `normalize=0`) as above.

### Per-variant BGM for A/B/C hook variants
Each hook variant gets its **own distinct** BGM track (user request on 014 VM) — keep the same
overall arc (e.g. sneaky → tension → triumphant → warm for a villain ad) but shift the flavor
per hook tone (bold/confrontational vs. sneaky/waltzy). Generate one Suno task per variant
(each returns 2 variations — pick the longer/fuller one).

### Seamless self-loop when the track is shorter than the ad
Suno tracks (~100–150s) are often shorter than a 3–4 min ad. Loop **seamlessly** with a
crossfaded self-join, then use as the master (trim happens at mix time):
```bash
ffmpeg -y -i t.mp3 -i t.mp3 -filter_complex "[0:a][1:a]acrossfade=d=4:c1=tri:c2=tri[o]" -map "[o]" master.mp3
```
One crossfaded loop point covers up to ~2× the track length — enough for a single ad. Avoids
the hard "restart" pop of a plain `-stream_loop`.

### Villain/comedy ad style brief (locked)
"Playful cinematic Pixar comedy orchestral, strong dynamic arc: mischievous sneaky pizzicato +
staccato bassoon + cheeky walking bass (smug villain) → rising tension low brass/tremolo → big
heroic triumphant orchestral burst (soaring strings, brass fanfare, uplifting percussion) →
warm hopeful piano+strings resolution. Characterful animated-movie score, energetic, full of
personality." Negatives: `vocals, lyrics, lo-fi, edm, dubstep, harsh distortion, horror,
dark-only, sad-only, ambient drone, trap, hip hop, aggressive metal`.

## Loud BGM that stays copy-timed → SIDECHAIN DUCKING (LEI 017 TVC)
When the user wants the music LOUD *and* "perfectly timed to the copy/visuals": don't just lower the music — **duck it under the VO with sidechaincompress**. The music plays loud in the gaps between phrases and automatically dips when the character speaks → it *feels* edited to the copy without any manual hit-syncing.
```
ffmpeg -i ad.mp4 -i music.mp3 -filter_complex "\
[0:a]aformat=channel_layouts=stereo,asplit=2[voc][sc];\
[1:a]atrim=0:LEN,afade=in:st=0:d=1,afade=out:st=OUT:d=2,volume=0.95[m];\
[m][sc]sidechaincompress=threshold=0.03:ratio=12:attack=4:release=260[duck];\
[voc][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.98[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac ...
```
Music `volume=0.95`, `ratio=12`, `release=260ms`, final `alimiter` prevents clip. Verify `volumedetect` max < 0 dB.

## Decouple ad-speed from music-speed
To make the ad "faster to fit the music" while keeping the music at its own tempo: speed the CLEAN ad (video+VO together, `setpts=PTS/F` + `atempo=F`) FIRST, THEN re-mix the (unchanged-speed) music under the faster ad. Never speed the music with the visuals.

## Testing several tracks
Suno returns 2 variations/task; run 1-2 tasks with the SAME style prompt to get 3+ takes that "sound alike" for A/B music testing. Mixing is free ffmpeg — produce one output per (hook × track) combo the user wants.
