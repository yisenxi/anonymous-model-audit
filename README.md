# anonymous-model-audit

Four-stage black-box identity verification for anonymous AI models released under codenames on developer platforms.

**Paper:** [Auditing Anonymous AI Models: A Four-Stage Protocol for Black-Box Identity Verification](https://arxiv.org/abs/2608.31142) (arXiv:2608.31142) · **Data:** [Zenodo](https://doi.org/10.5281/zenodo.22210928)

Tokenizer fingerprints have been used for model-family attribution in community practice; this tool implements the staged, validated protocol of the paper above — a four-stage forensic procedure that reconstructs identity from deployment properties the model cannot fake.

## Protocol mapping

| Stage | Tool component | What it does |
|---|---|---|
| Stage 0 — launch-time configuration forensics | *(process stage, no crawler)* | Recovers launch-time declarations from platform record pages and archived snapshots (Internet Archive); exposes preview→production drift. Performed by the auditor prior to tool use. |
| Stage 1 — configuration fingerprinting | `scripts/audit.py fingerprint --match <target> --save` | Pulls the platform's full model catalog (public `/models` endpoint, no key needed) and computes layered candidate-pool shrinkage: context → +max-output → +reasoning profile → +modality |
| Stage 2 — tokenizer differential | `scripts/audit.py run --target <alias> --candidates a,b` | Runs identical prompts against target and candidates; computes per-probe prompt-token differentials; enforces the mandatory multi-length condition (built-in: 3 short + 2 long across two languages) |
| Stage 3 — behavioral corroboration | same `run` command (`--hard` / `--format`) | Knowledge-cutoff, reasoning-control, modality, and self-identification probes (evidence ranking: configuration > tokenizer > knowledge boundary) |
| Confidence grading | integrated in output | family / version-line / variant / exact-checkpoint grading; *cannot attribute* as a first-class output |

## Requirements

Pure Python standard library (`urllib`/`json`) — **no third-party packages**. Python ≥ 3.10.

## Quick start

```bash
# Stage 1: catalog-wide configuration scan (public API, no key)
python scripts/audit.py fingerprint --match stealth/ox-alpha --save

# Stages 2-3: tokenizer differential + behavioral probes (keys from environment; never written to disk)
export OPENROUTER_API_KEY=...
python scripts/audit.py run --target ox --candidates glm53,glm52,step --save
```

## Data handling

- API keys are read from environment variables only; they are never logged, cached, or written to any file.
- Query logs (responses + usage metadata) are written to local JSONL files supplied via `--save`; strip credentials before sharing.
- The tool queries public model-catalog endpoints and the API endpoints you configure; it performs no scraping of non-public pages.

## Evidence provenance (flagship case)

The prospective flagship case in the paper was analyzed **before** the official reveal:

- 2026-08-23 16:11 — catalog snapshot (`models-snapshot-20260823-161058.json`)
- 2026-08-23 22:01 — configuration fingerprint database (`fingerprint-db-ox-v2-20260823-220158.json`)
- 2026-08-23 22:57 — ox-full probe JSONL (`audit-oxfull-20260823-225759.jsonl`), source of Fig. 2 and the collision ablation
- 2026-08-26 — official reveal: ZAI GLM-5.3-Flash
- 2026-08-31 — paper posted to arXiv

All artifacts carry the original `ts`/`timestamp` fields from the moment of collection. Deployment variant was **not** pre-asserted; the family and version-line inferences were confirmed by the reveal.

All of the above files — catalog snapshot, fingerprint database, probe JSONL, and the S1–S4 supplementary documents — are archived unchanged at [Zenodo (DOI: 10.5281/zenodo.22210928)](https://doi.org/10.5281/zenodo.22210928), where the file timestamps and contents can be verified independently.

## Case files

Pre-reveal measurement records, one directory per model. Each record is written before the official reveal and scored against it after.

`cases/union-alpha/` covers Union Alpha, listed on OpenRouter and OpenCode Go on 2026-09-16. The call is Qwen for the tokenizer family, against the leading community guesses of Mistral and Zhipu; the record was written 2026-09-17, with no official confirmation available at the time. It also documents a one-token cross-platform gap for the same model id, a context-length control showing that the platform's admission check estimates tokens from character count rather than the real tokenizer, and the boundary that the competing MiMo V3 hypothesis cannot be tested until V3 is public.

## Methodological notes

- The mandatory **cross-length condition** (paper §3.3) is enforced by the `run` component: it refuses to emit a same-tokenizer verdict from short-prompt probes alone (short-prompt collisions are documented as false positives under a short-only rule).
- The **probe-stability rule** (§3.3) discards a probe if the *target* endpoint returns inconsistent prompt-token counts across repeated identical rounds, before constancy is computed. One probe (`style_en`) was discarded in the flagship run for target-side instability.
- Stage 0 depends on externally archived snapshots (Internet Archive); snapshot absence, incompleteness, or tampering narrows the evidence — the protocol reports *cannot attribute* rather than guessing.

## Related community work

- Shrey (2026) — community forensics campaign (600+ requests) on the flagship case
- ItsKaiwenDu — Ox Alpha stylometry study
- iSimplifyMe — tokenizer-fingerprint white paper

## License

MIT
