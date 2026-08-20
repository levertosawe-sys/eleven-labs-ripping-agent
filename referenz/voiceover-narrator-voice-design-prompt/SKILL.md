---
name: "VOICEOVER NARRATOR VOICE DESIGN PROMPT"
description: "Produce a ready-to-paste voice-design prompt for the single narrator voice that carries the entire ad — for ElevenLabs Voice Design. Chat output only — no files."
---
# SKILL — VOICEOVER NARRATOR VOICE DESIGN PROMPT

Produce a ready-to-paste voice-design prompt for the single narrator voice that carries the entire ad — for ElevenLabs Voice Design. Chat output only — no files.

Used by formats with a single narrator voice (e.g. TS). Not for character dialogue — that is `character-voice-design-prompt.md`. Not for mixed narrator + characters — that is `mn-voice-design-prompts.md`.

## Inputs

- `script.md` — strict source of truth for spoken content and any explicit voice direction.
- Active format file — defines the narrator's structural role (spine vs. accent vs. interlocutor) and therefore the register the voice must hold.
- Active style file — informs tonal register (claymation = warm/tactile/handmade; photorealism = grounded/material).
- Brand `CLAUDE.md` and project `iteration-log.md` — for any prior framing or brand-level voice convention.

## Procedure

1. Re-read `script.md`.
2. Read or recall the active format and style files — the voice has to fit the ad it lives inside, not just the surface adjectives of the script.
3. Note any explicit voice direction in the script (e.g. *"ruhige männliche Stimme"*) — treat as authoritative.
4. Analyze the emotional arc as a whole — where the voice opens (hook), how it carries diagnostic / explanatory / proof / CTA passages, where it lands.
5. **Think around corners on register.** Surface adjectives ("warm", "calm", "intimate") are rarely the whole brief. Reconcile them against:
    - **What the format needs the voice to do.** A TS ad makes claims through visuals + voice alone — the narrator usually has to carry credibility, meaning warm-and-quietly-authoritative, not warm alone.
    - **What the product is asking the listener to believe.** Health, science, money, time → authority underneath warmth. Lifestyle, joy, taste → warmth alone.
    - **What the listener is being asked to do.** A reflective ad asks them to feel; a CTA-heavy ad asks them to act. The voice baseline tilts accordingly.

    The output should encode the *resolved* register, not the surface adjectives.
6. Decide language explicitly (match the script's spoken language).
7. Write one prompt covering the full voiceover. One voice — register shifts live inside it as involuntary texture, not as separate voices.
8. Output one VOICE DESIGN code block.

## Content rules

Cover the following in compressed, precise language:

- **Physical voice qualities** — age, gender, vocal depth and texture.
- **Spoken language** — name it explicitly (e.g. *natural German*).
- **Pace and rhythm** — tied to the ad's emotional logic.
- **Authority / warmth balance** — the resolved register from step 5. If both must coexist (warm-and-authoritative, intimate-and-credible), name it.
- **Emotional arc texture** — what stays constant across the ad, and what surfaces under diagnostic / scientific / proof / CTA passages — never as performance, always as involuntary texture.
- **One final sentence** capturing the *feeling of being spoken to* by this narrator — not their biography.

Every word must do specific work. The reader should be able to *hear* the voice before generating. No generic descriptors.

## Hard constraints

- **Length.** Prompt body must stay **under 900 characters**. The platform rejects over 1000.
- **No minor-age keywords.** Terms like *teen*, *child*, *kid*, *young girl* trigger the platform's safety filter. For a youthful read use *light*, *bright*, *lifted*, *bouncy*, *high-pitched*.
- **No slow-pacing keywords.** Ads need fast-paced delivery. Avoid words like *unhurried*, *slow*, *measured*, *deliberate*, *leisurely*, *takes time*, *paced out*, *drawn out* — they produce sluggish voice generations that don't hold attention in a social feed. When characterising pace, prefer terms that imply controlled but brisk delivery: *crisp*, *fluid*, *natural*, *even-paced*, *brisk*, *tight*, *confident*. The only exception is a specific reflective beat genuinely justified by the narrator's role — but the default for ad-voice design is fast-paced.

## Output format

Print directly in chat.

```
VOICE DESIGN — Narrator
` ` `
<voice-design prompt, ≤900 chars>
` ` `
```

(Use real triple backticks in actual output.)

After the block, add a closing line: *"Generate this in ElevenLabs and tell me what you'd like adjusted — texture, register, pace, or specific moments — and I'll revise the prompt."*

## Revisions — handled inside this skill

Don't route voice-prompt revisions through `iterate-and-revise.md`.

Targeted feedback ("too breathy", "make him older", "more authority under the mechanism passage") → revise and reprint the full block. Preserve everything not flagged. Wholesale rethink → regenerate.

## Promotion

After the run, append to `iteration-log.md`:

- The final narrator voice prompt.
- Any framing that worked unusually well or unusually badly.

Brand-generalizable observations get promoted to the brand `CLAUDE.md` at session end.
