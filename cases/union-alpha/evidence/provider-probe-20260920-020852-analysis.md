# 参照臂读数与上游 provider 的关系 — 分析（20260920-020852）

> 事前声明：`evidence/pre-specified-provider-20260920.md`（跑前落盘并提交，跑后不改）
> 证据：`evidence/provider-probe-20260920-020852.jsonl`（204 条，含每条的原始响应体 + 响应头）


各上游的 tag / 量化：
`Darkbloom`=darkbloom/fp4/fp4 `DeepInfra`=deepinfra/bf16/bf16 `Phala`=phala/unknown `DekaLLM`=dekallm/unknown `Mancer 2`=mancer/fp8/fp8 `Reka`=reka/fp8/fp8 `Parasail`=parasail/fp8/fp8 `Chutes`=chutes/fp8/fp8 `AkashML`=akashml/fp8/fp8 `Ionstream`=ionstream/fp8/fp8 `Io Net`=io-net/fp8/fp8 `CoreWeave`=coreweave/fp8/fp8 `Novita`=novita/unknown `Alibaba`=alibaba/unknown `Cloudflare`=cloudflare/unknown `Venice`=venice/fp8/fp8

## 定向组：每家上游 × 每个探针（k=3）

| 探针 | Darkbloom | DeepInfra | Phala | DekaLLM | Mancer 2 | Reka | Parasail | Chutes | AkashML | Ionstream | Io Net | CoreWeave | Novita | Alibaba | Cloudflare | Venice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n3_en_math | [68, 68, 68] | [68, 68, 68] | [136, 136, 136] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [68, 68, 68] | [64, 64, 64] | [64, 64, 64] | [68, 68, 68] | [105, 105, 105] |
| n5_zh_code | [70, 70, 70] | [70, 70, 70] | [138, 138, 138] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [70, 70, 70] | [66, 66, 66] | [66, 66, 66] | [70, 70, 70] | [107, 107, 107] |
| L0_base | [57, 57, 57] | [57, 57, 57] | [125, 125, 125] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [57, 57, 57] | [53, 53, 53] | [53, 53, 53] | [57, 57, 57] | [94, 94, 94] |
| identity_en | [67, 67, 67] | [67, 67, 67] | [135, 135, 135] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [67, 67, 67] | [63, 63, 63] | [63, 63, 63] | [67, 67, 67] | [104, 104, 104] |

## 默认组（不钉 provider）

| 探针 | 读数（含上游） |
|---|---|
| n3_en_math | 68(DekaLLM), 68(DekaLLM), 68(DekaLLM) |
| n5_zh_code | 70(Ionstream), 70(Ionstream), 70(Ionstream) |
| L0_base | 125(Phala), 125(Phala), 125(Phala) |
| identity_en | 67(Ionstream), 67(Ionstream), 67(Ionstream) |

## 事前预测判定

- **P1 上游内稳定 + 上游间有差**：上游内稳定=✅；出现跨上游差异的探针 ['n3_en_math', 'n5_zh_code', 'L0_base', 'identity_en'] → ✅ 成立
- **P2a n3_en_math 钉 Phala = 136**：[136, 136, 136] → ✅ 成立
- **P2b n3_en_math 钉 Reka = 68**：[68, 68, 68] → ✅ 成立
- **P3a L0_base 钉 Venice = 94**：[94, 94, 94] → ✅ 成立
- **P3b n5_zh_code 钉 Novita = 66**：[66, 66, 66] → ✅ 成立
- **P4 对照探针 identity_en 全上游同值**：[63, 67, 104, 135] → ❌ 失败
- **P5 默认组跨上游读数 ≥2 个**：{'n3_en_math': [68], 'n5_zh_code': [70], 'L0_base': [125], 'identity_en': [67]} → ❌ 失败

- PIN 未被遵守的单元：**0** / 定向组 192

## 结论（按事前规则机械套用）

1. **参照臂的 prompt_tokens 由上游 provider 决定**：任何 Δ 归因须记录 provider 并按 provider 分层；开放权重的多上游臂不能直接当参照臂。
2. 单次观测（136 / 94 / 66）的可复现性见上表；未复现者记为瞬态，不写作属性。
3. 本批为终局；机制层面（各家上游为何不同）不作推测。
