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
