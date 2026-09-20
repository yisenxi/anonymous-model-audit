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

## Update — 2026-09-18 (later): mode-resolved re-measurement on the successor endpoint

The paragraph above reports what a single reading per probe shows. Two further runs were made on the successor endpoint with the decision rules fixed in advance (written to a local file and committed before each run; rules restated below).

**Design.** Fifteen probes: the five original probes, six new short probes, and a four-step length series built by padding one base sentence with a fixed filler. Six repeats per probe on `unbiased/pareto`; reference arms `qwen/qwen3.8-max`, `qwen/qwen3.8-flash`, `qwen/qwen3.7-max` and `z-ai/glm-5.3-flash` re-measured in the same window. Rules fixed before the run: (1) a probe whose six repeats contain two or more distinct values counts as multi-mode; (2) a delta counts as constant only if it is identical across every probe of the same length class; (3) a mode counts as family evidence only if it holds against two same-family reference arms at once, with that family's internal 51-token gap closing the arithmetic.

**Result.**

| Layer | Measurement | What a single reading would have concluded |
|---|---|---|
| Single readings | delta vs the Qwen 3.8 line spans 7 tokens across nine short probes; the length series is non-monotonic (32 → 44 → 41 → 116) | "text path not attributable", plus a contradictory length response |
| Mode-resolved (k = 6 per probe) | minority readings (6 of 90 reads, ≈7%) give delta **exactly −55** against qwen3.8-max and **exactly −4** against qwen3.7-max, across six dissimilar probes, 0 deviation | "text path = Qwen-family tokenizer with a fixed wrapper offset" |
| Family-closure check | the qwen3.7-to-qwen3.8 counting gap is a constant 51 tokens; −55 + 51 = **−4** | both reference arms close at once, which rules out a single-arm coincidence |
| Image path (control) | delta vs GLM-5.3-Flash constant **−10**; the 64×64 → 512×512 response is +345 on both endpoints | image path reproduces across the deployment change |
| Cross-deployment shift | text −62 → −55 and image −17 → −10, i.e. **both shift by +7** | the change sits in the wrapper (system prompt), not in the tokenizer |

**Reading.** The text-path call holds on the successor deployment in a minority mode; the majority mode belongs to a different counting basis, whose delta varies with content (span 50). Single readings are not decisive on this endpoint, which is precisely the failure mode the protocol's repeat-read gate exists for. The non-monotonic length response is a mode-mixing artifact: in the majority mode the series is strictly monotonic (32 → 44 → 68 → 116).

**What is superseded.** The statement in the previous update that the text-path call "does not carry over to the successor deployment" applies to single readings only, and is superseded by the mode-resolved result above. Everything else in that update stands, including the one-token overnight drift of the reference arms and the point that a differential baseline belongs to a deployment period.

`evidence/pareto-diagnostic-20260918-195248.jsonl` holds both runs (95 + 55 records; transport failures retried).

## Update — 2026-09-18 (audit batch): the offsets are invariant, the occurrence rate is not

A third batch was run with its decision rules fixed in advance (local file committed before the run, `ddbacfa`; restated below), to close two gaps: the earlier evidence stored only `prompt_tokens`, so a different upstream engine and a different reporting path were indistinguishable; and the family attribution rested on two same-family arms, all of them OpenRouter endpoints.

Across the three measurement windows there are now **9 minority readings in 309 text reads (2.9%), and every one sits at the same offset**: −55 against qwen3.8-max, −4 against qwen3.7-max, and −46 against qwen3.8-27b (measured on four of them). The third arm was predicted before the run as −55 + g, where g is the same-window qwen3.8-max-to-27b gap; g measured 9 on all four probes, and the reading matched.

**The occurrence rate is not stationary**: 0/23 (0%) in the first window, 6/90 (6.7%) in the second, 3/196 (1.5%) in the third. A single reading, or a handful, is very likely to miss the mode entirely, which is what happened in the first post-reveal run (23 reads, conclusion "not attributable").

**Rules fixed before this batch.** (1) Forty consecutive reads each of two probes with the full raw response body and response headers stored, to test whether minority readings carry a distinguishable signature (provider, response id, usage fields, headers); (2) targeted replication on four probes with a third same-family arm; (3) deep samples of twenty reads on three probes.

**Results.** (a) The 80 consecutive reads produced no minority reading at all, so the signature question stays **open** — from the evidence held, a different upstream engine and a different reporting path remain indistinguishable, and no claim is made either way. (b) The targeted replication caught one minority reading, and it matched all three arms exactly. (c) A direct Alibaba DashScope endpoint returns counts identical to the OpenRouter Qwen endpoints (11 of 11 comparable probes, difference 0), so the family reference does not depend on OpenRouter's plumbing. (d) The deep samples did not split the majority mode into additional values.

`evidence/pareto-audit-20260918-201638.jsonl` holds the batch (196 Pareto text reads plus reference arms and the DashScope calls).

## Update — 2026-09-20 (second time window: no minority reading, and what the new signature fields show)

A fourth batch was run on the same panel, with its decision rules fixed in advance (local file committed before the run, `5566b29`; restated below). It re-ran the fifteen-probe panel at six repeats per probe on `unbiased/pareto` (90 reads) with four reference arms measured in the same window, and it stores for **every** call what the previous update flagged as missing: the full raw response body, the response headers, and the provider / response-id / usage fields.

**Design and rules, fixed before the run.** (1) The minority mode counts as reproduced if it appears at least once in the 90 reads; (2) every minority reading must sit at exactly −55 against `qwen3.8-max`; (3) at exactly −4 against `qwen3.7-max` and −46 against `qwen3.8-27b`; (4) the majority delta against `qwen3.8-max` must still span at least 5 tokens across the nine short probes; (5) the occurrence rate in this window is predicted below 7%, and the window rates are reported separately, never pooled; (6) all fifteen majority readings must be unchanged from the previous window.

**Result.** The minority mode did **not** appear: 0 reads of 90, all fifteen probes single-mode. Rule 1 fails; rules 2 and 3 have no sample; rules 4, 5 and 6 hold. Every majority reading is **identical item by item** to the 9/18 window (44 / 39 / 36 / 175 / 134 / 36 / 36 / 38 / 32 / 44 / 34 / 32 / 44 / 68 / 116), which is also a check that the probe texts are byte-identical to that run: had any of them changed, fifteen identical counts would not be possible.

The occurrence rate across the four windows is now **0/23 (0%), 6/90 (6.7%), 3/196 (1.5%), 0/90 (0%)** — 9 minority readings in 399 text reads. Two-sided Fisher exact tests put the 9/18 diagnostic window against this one at p = 0.029, and the two 9/18 windows combined (9/180) against this one at p = 0.032. The rate is a per-window quantity, not a probability, and a window with no hit is not evidence that the mode is gone: the 95% upper bound on this window is 4.1%.

**The signature question stays open.** All 90 reads from the composite endpoint in this window were served by the same provider (`Unbiased`), and the minority reading recorded on 9/18 also came from that provider, so the field does not separate the two kinds of reading. From the evidence held, a different upstream and a different reporting path remain indistinguishable, and no claim is made either way.

**What the new fields did surface, in the reference arms.** The platform reports which upstream served each request. The three closed arms (`qwen3.8-max`, `qwen3.8-flash`, `qwen3.7-max`) were served by one upstream each across all forty-five calls, and their counts were constant. The open-weight arm `qwen/qwen3.8-27b` was served by **ten different upstreams across fifteen calls**. On the probe `n3_en_math` that arm read **136** in this batch (one upstream) against **68** on 9/18 (a different upstream) — the same model id, the same probe text, twice the count; on the other thirteen probes it kept a fixed −9 relation to the closed arm. Each of those two readings was taken once and neither has been repeated, so this is an observation, not yet a measured property.

**Reading.** A reference arm's count is not a function of the model id and the prompt alone; the serving upstream is part of it. Differential attribution therefore needs the arm's provider recorded and its readings checked for homogeneity before a delta is used, and an open-weight arm routed across many upstreams is a weaker reference than a closed single-upstream one. This layer was invisible until the provider and raw-body fields were stored — the same gap the previous update flagged, which is why those fields are now recorded on every call.

**Discipline and limitations.** The rules were fixed before the run; the negative result is published as such; per the pre-run rule the batch is final and no further probes were tried. The window is a single night-time run, four windows fall inside two days, and the reason the mode appears or does not is unknown and is not speculated on here.

`evidence/pareto-window3-20260920-015406.jsonl` holds the batch (150 records: 90 Pareto reads plus four reference arms, each record carrying the raw response body and headers); `evidence/pareto-window3-20260920-015406-analysis.md` is the mechanical verdict, `evidence/pareto-window3-20260920-015406-analysis-final.md` the cross-window analysis, and `evidence/pareto-window3-20260920-stats.txt` the recomputed window rates and tests.

## Update — 2026-09-20 (later): the reference arm's count is set by the serving upstream

A fifth batch, with its rules fixed in advance (local file committed before the run, `a353f96`), tested the observation from the previous update directly: the same model id, the same prompt text, pinned to each upstream the platform currently lists for it, three repeats each.

**Design.** `qwen/qwen3.8-27b` is an open-weight model, and the platform lists sixteen upstreams for it. Four probes (`n3_en_math`, `n5_zh_code`, `L0_base` and the control `identity_en`) × sixteen upstreams × three repeats, with the upstream pinned in the request (`provider.order` plus `allow_fallbacks: false`); the platform honoured the pin in **192 of 192** calls. Twelve further calls were made with no pin.

**Result.** The sixteen upstreams fall into four counting groups, and each group's difference holds on every probe:

| Probe | 12 upstreams | Alibaba, Novita | Venice | Phala |
|---|---|---|---|---|
| n3_en_math | 68 | 64 (−4) | 105 (+37) | **136 (+68)** |
| n5_zh_code | 70 | 66 (−4) | 107 (+37) | **138 (+68)** |
| L0_base | 57 | 53 (−4) | 94 (+37) | **125 (+68)** |
| identity_en | 67 | 63 (−4) | 104 (+37) | **135 (+68)** |

The twelve: AkashML, Chutes, Cloudflare, CoreWeave, Darkbloom, DeepInfra, DekaLLM, Io Net, Ionstream, Mancer 2, Parasail, Reka. All sixty-four (probe × upstream) cells are identical across their three repeats, so the arm is deterministic within an upstream. The offsets are constant per upstream across all four probes (+68, +37, −4, 0): the same tokenizer with a different fixed wrapper per upstream, not different tokenizers. Quantization does not line up with the groups — the twelve include fp4, bf16 and fp8 hardware, and the deviating groups include fp8 and unlabelled.

**Two predictions failed, and both are reported as failed.** I had predicted that the control probe `identity_en` would read the same on every upstream, i.e. that the deviant readings were content-specific. It does not: all four probes split by upstream, so the earlier phrasing stands corrected — the upstream difference holds for every request to this arm, not for some content. I had also predicted that unpinned calls would land across at least two upstreams; three consecutive unpinned calls landed on a single one each time. That is a weakness of the design, but it produced the sharper illustration: unpinned, `L0_base` read **125** on Phala while twelve of the sixteen upstreams read **57**, so one unpinned reading came out **2.19×** the modal value.

**The three deviant cells in the previous update are now closed.** `n3_en_math` read 136 on Phala, `n5_zh_code` read 66 on Novita and `L0_base` read 94 on Venice; each of those readings reproduces exactly when that upstream is pinned. The arm was not unstable — the router had simply sent those three calls to three different upstreams.

**Reading.** A reference arm's count is a function of (model id, serving upstream, content), and this layer is invisible unless the provider field is recorded; this batch is the second time the fields added in the previous update have paid off, the first being the deviant cells themselves. The wider point concerns what a constant delta can establish: constancy says "same tokenizer, a fixed difference" and nothing about *which layer* that fixed difference belongs to. Three layers have now produced constants of exactly that shape in this case — **+7** across the deployment change, **51** between two model generations of the same family, and **−4 / +37 / +68** across upstreams. A delta rule therefore has to be bound to a controlled layer (same endpoint, same upstream, same window), or a constant will be booked to the wrong layer.

**Honest limitation this batch adds.** The family-closure argument used a third arm that is an open-weight, multi-upstream model. Had the router sent that call to Phala, the third arm's arithmetic would have been off by 68 and would have looked like a failed family closure. The call on 9/18 happened to land on Reka, whose count satisfies that prediction, so the third-arm leg of the closure rests partly on routing luck. The two primary arms are closed models served by a single upstream each (30 of 30 calls on Alibaba), so the main closure is unaffected.

`evidence/provider-probe-20260920-020852.jsonl` holds the batch (204 records, raw response bodies and headers included), the mechanical verdict is in `evidence/provider-probe-20260920-020852-analysis.md`, the analysis in `evidence/provider-probe-20260920-020852-analysis-final.md`, and the recomputed statistics in `evidence/provider-probe-20260920-stats.txt`.

## Update — 2026-09-20 (later still): the upstream offset does not move with length

A sixth batch, with its rules fixed in advance (local file committed before the run, `412d0d0`), tested how the previous batch's four counting groups should be read. A difference between two *tokenizers* grows with length; a fixed difference does not. The fifteen-probe panel, whose baseline readings run from 57 to 162 tokens, was therefore pinned to one upstream from each group — Phala (+68), Venice (+37), Alibaba (−4) and DeepInfra as the baseline — three repeats each.

**Result: the offset does not move.** On all fifteen probes, and on every step of the length series, the differences are exactly **+68, +37 and −4**, with zero deviation. All sixty (probe × upstream) cells are identical across their three repeats, and the pin was honoured in **180 of 180** calls. Selected rows, with the baseline reading in brackets:

| Probe | Phala | Venice | Alibaba | baseline |
|---|---|---|---|---|
| identity_zh (67) | 135 | 104 | 63 | 67 |
| cutoff (61) | 129 | 98 | 57 | 61 |
| long_zh (155) | 223 | 192 | 151 | 155 |
| long_en (162) | 230 | 199 | 158 | 162 |
| n3_en_math (68) | 136 | 105 | 64 | 68 |
| L0_base (57) | 125 | 94 | 53 | 57 |
| L1_pad2 (67) | 135 | 104 | 63 | 67 |
| L2_pad6 (87) | 155 | 124 | 83 | 87 |
| L3_pad14 (127) | 195 | 164 | 123 | 127 |

**Reading.** The difference between upstreams is a fixed block, independent of length and of content: the same tokenizer with a different fixed wrapper per upstream, not different tokenizers. The prediction I wrote in advance — that the offset would grow with length, which would have meant a tokenizer difference and would have obliged me to reword the previous update — did not occur, and is reported here as not occurring.

**The wider point, now with three layers.** A constant delta says "same tokenizer, a fixed difference" and nothing about *which layer* that difference belongs to. In this case constants of exactly that shape now appear at three layers: **+7** across the deployment change, **51** between two generations of one family, and **−4 / +37 / +68** across upstreams. It also validates on an independent layer the reasoning that carries the text-path call on the composite endpoint: the −55 offset was read as "same tokenizer with a fixed difference" precisely because it held across content-diverse probes, and here the same structure reproduces at the upstream layer across a 2.8× length span.

**What changes and what does not.** The two primary reference arms are closed models, served by a single upstream each (30 of 30 calls on Alibaba), so the main family-closure result is unaffected. The third arm is the open-weight, multi-upstream model, and its reading on 9/18 happened to land on an upstream whose offset is zero; that leg of the closure therefore rests partly on routing luck, which the previous update flagged and this one quantifies. The four reference-arm requirements this batch adds: record the provider on every call, check that a reference arm has a single reading per probe before using it, prefer a closed single-upstream arm, and never attribute a change in an open-weight arm's count to the endpoint under test.

`evidence/provider-length-20260920-022101.jsonl` holds the batch (180 records, raw bodies and headers included), with the mechanical verdict in `evidence/provider-length-20260920-022101-analysis.md` and the analysis in `evidence/provider-length-20260920-022101-analysis-final.md`.

## Update — 2026-09-20 (second window, about 7.5 hours later): the upstream offsets are unchanged

A seventh batch re-pinned the four upstreams — one from each counting group — over three probes (`identity_en`, `L0_base`, `long_zh`) at 09:53, about 7.5 hours after the batch at 02:21, with its rules fixed in advance (`1bbf285`).

**Result: nothing moved.** The offsets are **+68 / +37 / −4** on all three probes; the baseline readings are **67 / 57 / 155**, exactly as in the first window; all twelve (probe × upstream) cells are identical across their repeats; and 36 of 36 calls were served by the upstream that was requested.

One process note, because it belongs in the record: the first attempt at this batch was cut off at 28 of 36 calls by a tooling timeout — an infrastructure event, not a measurement outcome. The eight missing cells were measured later in the same window under the same rules, and the batch is reported with that fact attached rather than quietly completed.

**Reading.** The per-upstream offsets are stable across two windows about 7.5 hours apart on the same day. Cross-day stability remains untested, so the previous update's limitation is narrowed rather than withdrawn.

`evidence/provider-window2-20260920-095344.jsonl` holds the batch (36 records, raw bodies and headers included) with the verdict in `evidence/provider-window2-20260920-095344-analysis.md`.
