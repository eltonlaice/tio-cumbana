---
name: diagnose-mildew
description: Diagnose cucurbit downy mildew (Pseudoperonospora cubensis) and related early-stage foliar diseases on cucumber, melon, watermelon, and pumpkin. Use when the farmer sends a photo of a leaf with yellowing, angular blotches, or grey mould on the underside, OR when overnight humidity and temperature data match the infection envelope. Returns a severity score (0-3), a stage classification, and a concrete treatment plan with dosages and local supplier references.
---

# Diagnose Mildew

This skill is the diagnostic core that Tio Cumbana invokes every time the farmer asks "is my cucumber OK?" or the vigilance loop sees a humidity spike. It's separated from the conversational system prompt so the same logic powers reactive replies, proactive triggers, and any future Claude Desktop / Claude Code integration the project picks up.

## When to use

- Farmer-supplied photo of a cucurbit leaf with any of: yellow mottling between veins, angular brown lesions bounded by veinlets, grey/violet down on the underside, water-soaked patches, sudden wilt.
- Vigilance trigger: overnight relative humidity > 85% for 3+ consecutive hours combined with leaf-canopy temperature 15–22 °C (the canonical *Pseudoperonospora cubensis* infection window). The `tio-cumbana-weather` MCP server emits this as `mildew_risk: true`.
- Phenological-stage trigger: cucumber between week 4 and week 8 from planting (when canopy density is highest and downy mildew historically takes hold).

## Inputs expected

The agent should provide whichever of the following are available:

- `image`: leaf photo (front and/or back of the leaf is best; back is diagnostic).
- `crop`: the cultivar — cucumber (Epsilon F1), pepper (Indra F1), tomato, etc. Default: cucumber.
- `phenological_week`: weeks since planting.
- `weather`: dict from the weather MCP — current temp, RH, recent precipitation, mildew_risk flag.
- `farmer_history`: short notes on past interventions ("treated with copper 6 days ago", "rejected Mancozeb").

If only the photo is provided, proceed with conservative dosages and explicitly ask the farmer (in Tio Cumbana's voice) for the missing context in the response.

## Identification criteria

Visually distinguish downy mildew from look-alikes:

| Sign | Downy mildew | Powdery mildew | Bacterial spot | Nutrient deficiency |
|---|---|---|---|---|
| Top of leaf | Pale yellow angular blotches bounded by veins | White powder | Small dark dots, water-halo | Diffuse yellowing, no angular pattern |
| Back of leaf | Grey-violet down (sporangia) — diagnostic | Same powder | Clear/oily spots | Clean |
| Pattern | Starts on lower-shaded leaves | Often upper canopy | Anywhere, often after rain | Older leaves first |
| Severity progression | Days, dramatic | Weeks, slower | Days, lesion-bound | Weeks, gradual |

If you cannot see the back of the leaf, ask for a follow-up photo. **Never diagnose downy mildew from a top-only photo at high confidence.**

## Severity scoring

- **0 — Suspect:** suggestive symptoms, no sporulation visible. Action: monitor + curative spray on next dawn if weather window matches.
- **1 — Early:** angular blotches on 1-3 lower leaves, sporulation faint or absent. Action: curative spray now, repeat in 7 days.
- **2 — Established:** sporulation clear on multiple leaves, plant still vigorous. Action: curative spray now, sanitation (remove worst leaves), recheck in 3 days.
- **3 — Heavy:** sporulation on >30% of canopy, leaf collapse in patches. Action: aggressive curative spray, prune severely, expect partial yield loss; brief the farmer plainly.

## Treatment plan template

See `references/treatments.md` for the full table (active ingredients, brand names available at AQI Machava, dosages, REI/PHI, rotation rules, organic alternatives). The default for cucumber in Maluana, severity 1-2, is mancozeb 80 WP at 25 g per 10 L of water, applied at dawn before bee activity, **unless** the farmer's preferences (Memory) say otherwise — Dona Maria does not use Mancozeb; for her, fall back to copper hydroxide 53.8 WG at 20 g / 10 L.

## Output format

Return a single JSON object:

```json
{
  "stage": "downy_mildew | powdery_mildew | bacterial_spot | deficiency | unknown",
  "severity": 0,
  "confidence": 0.0,
  "diagnostic_notes": "<one sentence — what you saw and didn't see>",
  "ask_followup": "<question for the farmer if confidence < 0.7, else null>",
  "treatment": {
    "product": "<active ingredient and brand if available>",
    "dose": "<amount per 10 L>",
    "timing": "<when to apply>",
    "supplier": "<AQI Machava unless Memory says otherwise>",
    "alternatives_if_unavailable": ["..."]
  },
  "narration": "<the Tio Cumbana voice — what the farmer hears, in PT with Changana code-switch where natural. 2-4 sentences max.>"
}
```

The `narration` field is what the conversational layer feeds to ElevenLabs. Keep it conversational, concrete, and short — voice-note length, not memo length.

## Constraints

- Never recommend a product that the farmer's Memory marks as rejected.
- Never give a dosage range — pick one number with a reason.
- If `confidence < 0.4`, do not draft a treatment; instead populate `ask_followup` only.
- If the photo shows no foliar issue at all, return `stage: "unknown"` with severity 0 and a friendly check-in narration ("Tudo bem aqui, continua assim...").
