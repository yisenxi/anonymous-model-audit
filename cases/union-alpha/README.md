# Union Alpha: tokenizer fingerprint, before the reveal

Published as a thread on X on 2026-09-17, before any official confirmation: https://x.com/yisenxi2026/status/2100493581048013227

Model: `stealth/union-alpha`, a free stealth listing on OpenRouter from 2026-09-16 (also served on OpenCode Go as `union-alpha`).
Method: the four-stage protocol from *Auditing Anonymous AI Models* (arXiv:2608.31142).
Prediction written 2026-09-17, before any official confirmation.
Call: the tokenizer family is Qwen (Alibaba), not the community's leading guesses of Mistral or Zhipu.

## What each stage found

| Stage | Test | Result |
|---|---|---|
| 0 | Internet Archive snapshot of the listing page (captured 2026-09-16 15:45 UTC, listing day), plus a drift check against the live page a day later | Snapshot captured. No drift in context, max output, price, or modality. The page states the model is hosted by one provider and that OpenRouter forwards requests directly with no routing decisions, which rules out provider switching as an explanation for the differential. |
| 1 | Field-level comparison of context length, max output, modality, and the catalog's tokenizer tag | Inconclusive. Mixed signals: the context length matches Mistral's 262,144, max output matches the Qwen and GLM lines at 131,072, and the tokenizer tag reads "Other". Stage 1 eliminated nothing. |
| 2 | Prompt-token counts across five probe types plus code, emoji, Japanese, and digit-heavy text | Constant offset against the whole Qwen 3.6/3.7/3.8 line (six models). The offset varies against GLM, Mistral, Kimi, MiniMax, and DeepSeek. |
| 3 | Identity, knowledge-edge, reasoning-style, and code probes | union returns no reasoning tokens and its platform parameter list has no `reasoning` entry. The Qwen Max models all reason. So union is not a straight Qwen-Max deployment. |

The Qwen family is internally consistent in the same measurement: same-generation pairs offset by 0, cross-generation pairs by 51, and union sits at qwen3.8 minus 62 and qwen3.7 minus 11. Since 62 minus 11 equals 51, the arithmetic closes.

## Call

Tokenizer family: Qwen (Alibaba), high confidence. Six Qwen models across nine probes give a constant offset, including the character-set probes; every other candidate family varies.

Specific variant: not asserted. union runs a smaller context window than Qwen3.8-Max or Flash (262,144 measured against at least 500,067) and does no explicit reasoning, so it is a different deployment from those two.

## Caveats

A constant offset identifies a tokenizer lineage, not weights. Integer counts from the same endpoint on the same day can rule tokenizer sharing in or out; they cannot show that two endpoints serve identical checkpoints.

union and Qwen may share an operator. Stage 0 shows the listing has one provider, not that the provider is Alibaba.

A one-token gap appeared between the two platforms for the same probe (15 on OpenRouter, 16 on OpenCode Go). OpenRouter's own Anthropic-format endpoint also returns 15, so the format is not the cause. The gap is at the deployment level: the same model id does not imply the same deployment, and audit baselines belong to a specific platform, endpoint, and date.

The competing Xiaomi MiMo-V3 hypothesis could not be tested. Only MiMo V2 and V2.5 are served anywhere I checked, and MiMo V3 is not public. MiMo V2.5 does not share union's offset with GLM (234/234/236, varying), and its own two models offset by a constant 4.

## How this gets scored

If the reveal names Qwen or Alibaba, the tokenizer-family call was correct. If it names Mistral, Zhipu, or anyone else, that is a Stage 2 failure under a single-provider-forwarded listing, and it goes in the record as a scope limit rather than an anomaly.

## Files

`prediction-20260917.md` is the original working record. `prediction-20260917-en.md` is the English version. `evidence/` holds the raw measurement files, one per run, each carrying the timestamp of the run that produced it.

## Update — 2026-09-17 (evening): class-dependent token accounting

Two further measurement runs, archived in `evidence/`, were made after this case was published.

**Image-bearing requests** (`image-expand-20260917-181131.jsonl`). The same prompt with an image attached gives a constant offset of −17 against GLM-5.3-Flash on all four image probes (64×64, 256×256 gradient, 256×256 noise, 512×512). The two endpoints also move identically with image size: union 21 → 366, GLM-5.3-Flash 38 → 383, both +345. Against the Qwen 3.8 line the image offsets are not constant: −76, +8, +77. The Qwen 3.8 Max and Flash lines do not scale the same way (97 → 289 and 122 → 314).

**Paired text/image requests** (`mode-census-20260917-182900.jsonl`). The same carrier sent with and without an attached 64×64 image: union 9 → 23, GLM-5.3-Flash 22 → 40, so the class offset moves from −13 on text to −17 on image while staying constant inside each class. The image contributes 14 tokens on union and 18 on GLM-5.3-Flash. At 512×512 both endpoints gained 345 tokens over their own 64×64 reading, so the image tokens scale identically and the four-token gap is a fixed difference on the image path. The reference arms are stable to the token across repeated reads (77, 77, 41, 28).

**Repeat reads of identical text requests** (`drift-recheck-20260917-174937.jsonl`, `mode-census-20260917-182900.jsonl`). The endpoint returns two distinct prompt-token values for the same request. In ten consecutive identical reads the values came in stretches: 15, 15, 33, 33, 15, 15, 15, 33, 33, 15, with six readings at the low value and four at the high one. The high value sits 18 tokens above the low one and does not match the Qwen-family offset. Text-path constants reproduce exactly at the low value: Qwen3.8 line −62, Qwen3.8-Flash with reasoning off −26, Qwen3.7-Max −11.

**Reading.** The reported prompt-token count is not a single function of the input. Text-path counting is consistent with the Qwen family; image-path counting is consistent with GLM-5.3-Flash. The call above is unchanged and stays scoped to the text-path measurement, which reproduced on the day it was published, four hours after the thread went up.

**Coverage correction.** The character-set probes were run on two of the six Qwen models, not all six. Every measured pair still held a constant offset; the scope of that sentence was wider than the measurement.

## Update — 2026-09-18 (reveal, and a re-measurement on the successor endpoint)

The stealth period ended. `stealth/union-alpha` now returns HTTP 404: "Thank you for participating in the Stealth Union Alpha testing period. This model was Unbiased's Pareto." OpenRouter's listing page states the model was "revealed to be Pareto by Unbiased", and the vendor describes Pareto 26.9 as "one model, several engines" and "not a router". The successor endpoint is `unbiased/pareto`, with the same 262,144-token context and 131,072 maximum output as the stealth listing; the raw 404 body is archived at `evidence/reveal-404-union-alpha-20260918.json`.

**Re-measurement after the reveal** (`evidence/pareto-successor-20260918-193329.jsonl`, 78 records; every reference arm re-measured in the same run, failed transports retried)

| Path | Before the reveal (`stealth/union-alpha`) | After the reveal (`unbiased/pareto`) |
|---|---|---|
| Image path, vs GLM-5.3-Flash | constant −17 (4/4 image probes) | constant **−10** (4/4 image probes) |
| Image path, 64×64 → 512×512 response | both endpoints +345 | both endpoints **+345** |
| Image path, vs the Qwen 3.8 line | not constant (−76, +8, +77) | not constant (−92, −8, −8, +61) |
| Text path, vs the Qwen 3.8 line | constant −62 (5/5 probes) | **not constant** (−32, −37, −34, +11, −37) |
| Text path, vs Qwen3.7-Max | constant −11 (5/5 probes) | not constant (+19, +14, +17, +62, +14) |
| Text path, vs GLM-5.3-Flash | drifting (−14 to −11) | not constant (+12 to +52) |
| Ten repeats of one text request | two values (15 / 33, offset +18) | one value (10/10 identical) |

**What holds and what does not.** The image-path finding reproduces across the deployment change: the offset against GLM-5.3-Flash is constant again, and the two endpoints still move identically with image size (+345 each, 31 → 376 on Pareto and 41 → 386 on GLM-5.3-Flash). The text-path call does not reproduce on the production deployment: no tested reference arm yields a constant offset there, and the ten-repeat reading showed no second mode. The text-path call therefore stays scoped to the platform, endpoint and deployment period it was measured on. It reproduced on that deployment four hours after the thread went up; it does not carry over to the successor deployment.

**A note on baselines.** The reference arms themselves moved by one token between the two days (GLM-5.3-Flash identity_en 28 → 27, Qwen3.8-Max and Qwen3.8-Flash 77 → 76, Qwen3.8-Flash with reasoning off 41 → 40), which is exactly why the same-day control arms are what make the comparison above meaningful. A differential baseline belongs to a deployment period, and the reveal is an observable deployment boundary.

**Limitation.** The vendor describes Pareto as a composite of several models but does not name them, so the component identities behind either path remain unconfirmed; the two counting paths remain an observation, not a mechanism claim. The long-probe texts used in the 2026-09-17 run could not be recovered (the scripts are gone and the archived evidence stores counts only), so the cross-day comparison above uses the three short probes; every conclusion drawn here comes from same-run comparisons.
