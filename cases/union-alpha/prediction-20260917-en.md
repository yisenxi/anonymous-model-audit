# Union Alpha, measurement record

Target: `stealth/union-alpha`
Platforms: OpenRouter (`stealth/union-alpha`, free) and OpenCode Go (`union-alpha`, free, unlimited requests)
Listed 2026-09-16. All measurements below taken 2026-09-17.
Protocol: four stages, arXiv:2608.31142.

## Stage 0, archived baseline

Internet Archive captured the listing page at `20260916154548`, which is 2026-09-16 15:45:48 UTC, the day it went up. CDX digest `LNDOWIONBTPWW5CD2D5OVTUIK3FQ6EM6`, HTTP 200.

The snapshot records context 262,144, max output 131,072, price free, modality text and image in, text out, released Sep 16 2026. Comparing it to the live page a day later showed no change in any of those four fields.

The snapshot also carries a line worth keeping: "This model is hosted by one provider. OpenRouter forwards every request to it directly, no routing decisions to make." That matters because it removes provider switching from the list of things that could produce a stable offset.

## Stage 1, configuration fingerprint

Context length 262,144 lines up with mistral-large-2512; max output 131,072 lines up with qwen3.8-max and glm-5.3-flash; the catalog's tokenizer tag for union reads "Other". Modality is text and image, where qwen3.8-max adds video and mistral-large adds file input.

Three fields, three different neighbors. Nothing got eliminated, which is how Stage 1 is supposed to behave when the listing is vague on purpose. One caveat about the field itself: these are platform declarations, not measurements, and the catalog is demonstrably not always right. qwen3.8-27b carries a catalog context length of 1,000,000 while its provider entry says 262,144.

## Stage 2, tokenizer differential

Against the candidate families, five probes each:

| Candidate family | Offset from union | Result |
|---|---|---|
| Qwen (six models) | constant, at 62, 53, or 11 depending on generation | aligns |
| GLM (four models) | varies, values -14 through -11 | no |
| Mistral (three models) | varies, spread of 17 | no |
| Kimi K3, MiniMax M3, DeepSeek V4-Pro | varies | no |

Character-set probes, to guard against the short-prompt collision case:

| Offset | code | emoji | Japanese | digits |
|---|---|---|---|---|
| union minus qwen3.8-max | -62 | -62 | -62 | -62 |
| union minus qwen3.7-max | -11 | -11 | -11 | -11 |

Inside the Qwen line: qwen3.8-max against qwen3.8-flash gives a constant 0, qwen3.7-max against qwen3.6-flash gives a constant 0, and the 3.8 series against the 3.7/3.6 series gives a constant 51. Since union sits at qwen3.8 minus 62 and qwen3.7 minus 11, and 62 minus 11 is 51, union shares the tokenizer of the 3.6/3.7/3.8 line.

Stability: four of five base probes gave identical counts across three rounds (11, 15, 22, 19). The cutoff probe gave 9, 30, 9 across three rounds, 9,9,9,30,9,9 across six, and 9,9,9,fail,9,fail,9,9,9,9 across ten. The outlier tracks failed requests rather than tokenizer jitter, so failures get filtered and outliers listed separately.

## Stage 3, behaviour

union answers with a scripted denial ("I'm Union Alpha, and my developer is currently anonymous") and returns zero reasoning tokens on every probe. qwen3.8-max and qwen3.7-max both return reasoning tokens in the 60 to 300 range on the same prompts.

Checking whether that is a calling-method artifact: union's supported-parameter list contains no `reasoning` entry, while both Qwen Max models expose `reasoning`, `reasoning_effort`, and `include_reasoning`. Passing `{enabled: true}` or `{effort: "high"}` to union changes nothing, and passing `{enabled: false}` to qwen3.8-max returns HTTP 400, "Reasoning is mandatory for this endpoint and cannot be disabled." The absence of reasoning on union is a property of the deployment.

One control run explains where part of the offset comes from. Turning reasoning off on qwen3.8-flash moves its prompt-token count by 36, which shifts union minus qwen3.8-flash from -62 to -26. Both values are constant. So the differential carries a system-prompt component, and a constant offset means the same tokenizer plus a stable system-prompt difference, not identical system prompts.

## Context lengths

union rejects requests past 262,144, and the rejection message states that number, so the declared figure holds. qwen3.8-flash and qwen3.8-max both accepted inputs measured at 500,067 tokens and above, so their 1,000,000 declarations were not falsified within what could be sent.

Two things surfaced along the way. The platform's admission check uses a rough estimate of characters divided by four rather than the real token count, so a request whose true token count is well under the cap can still be turned away. And account-level prompt limits can mask a model's real context: on a low-balance account, requests to qwen3.8-max were capped at 4,633 tokens until credits were added.

## Cross-platform check

Same probes, OpenCode Go's Anthropic-format endpoint against OpenRouter:

| Item | OpenCode Go | OpenRouter |
|---|---|---|
| qwen3.8-flash and max counts | 73, 77, 71, 84, 81 | 73, 77, 71, 84, 81 |
| union counts | partial run, 16 on the one probe that returned | 11, 15, 9, 22, 19 |
| union minus qwen | -61 | -62 |

Qwen's counts are identical across platforms. union differs by one token. The format was ruled out, since OpenRouter's own Anthropic-format endpoint also returns 15. That leaves a deployment-level difference. The gap does not disturb the family call, since both platforms give a constant offset, but it does mean the same model id on two platforms is not the same deployment, and baselines should not be carried across.

## Call

Tokenizer family is Qwen (Alibaba) at high confidence. Six Qwen models across nine probes, including character-set probes, give a constant offset, the family is internally consistent, and GLM, Mistral, Kimi, MiniMax, and DeepSeek all vary.

The specific variant is not asserted. union has no reasoning where the Qwen Max line does, and a smaller context window than the 3.8 models.

Three things could still change the picture. A constant offset shows shared tokenizer lineage, not shared weights. The Qwen serving and the union serving could have the same operator, which Stage 0 cannot rule out. And the MiMo V3 hypothesis is untestable until V3 is public; MiMo V2.5 does not align with union in the meantime.

## Scoring

Revealed as Qwen or Alibaba, the call was right. Revealed as anything else, the case gets logged as a Stage 2 failure mode for single-provider-forwarded listings and folded into the protocol's stated scope.

## Evidence

One file per run, named for the run: `probe-union-*` (baseline probes), `catalog-union-*` and `catalog2-union-*` (candidate batches), `stability-union-*` (three rounds), `charset-union-*` (character sets), `qwen-cross-*` (family internals), `cutoff-recheck*`, `stage3-union-*` (behaviour), `reasoning-switch-*`, `qwen38flash-noreason-*` and `qwen38max-noreason-*` (controls), `ctx-sweep-*` (context), `xplat-go-*` (cross-platform), plus `stage0-stage1-20260917.md`.

**Update (2026-09-17, evening).** Further measurement showed the endpoint reports class-dependent token counts (text path consistent with the Qwen family, image path consistent with GLM-5.3-Flash) and returns two distinct readings for identical text requests. See the update section in `README.md`. The call above is unchanged.

Post-reveal re-measurement (2026-09-18): see README, Update — 2026-09-18.
