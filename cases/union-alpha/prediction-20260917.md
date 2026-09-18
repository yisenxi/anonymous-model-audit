# Union Alpha 前瞻预测卡（2026-09-17，四阶段协议完整执行）

目标：`stealth/union-alpha`（OpenRouter 免费 stealth，2026-09-16 上线，单一 provider 直转）
状态：真实前瞻记录（预测产生于揭晓前；截至 2026-09-17 无官方认领）

---

## Stage 0：时间一致性基线

- 归档快照：Internet Archive `20260916154548`（2026-09-16 15:45:48 UTC，上线当天），HTTP 200，CDX digest `LNDOWIONBTPWW5CD2D5OVTUIK3FQ6EM6`
- 上线配置：ctx 262,144 / max_out 131,072 / Free / text+image→text / Released Sep 16, 2026
- 关键声明："This model is hosted by one provider. OpenRouter forwards every request to it directly, with no routing decisions to make."
  → 排除路由切换导致的差分失真
- 漂移检查：9/16 快照 vs 9/17 实时，四项配置全一致（无漂移）

## Stage 1：配置指纹（未缩池）

| 模型 | ctx | max_out | tokenizer 字段 | modality |
|---|---|---|---|---|
| union-alpha | 262,144 | 131,072 | "Other" | text+image |
| qwen3.8-max | 1,000,000 | 131,072 | Qwen | text+image+video |
| mistral-large-2512 | 262,144 | 209,715 | Mistral | text+image+file |
| glm-5.3-flash | 1,310,720 | 131,072 | Other | text+image+video |

判定：混合特征（ctx 像 Mistral，max_out 像 Qwen/GLM，tokenizer 未标注）→ 配置层不缩池。

ctx 声明值可靠性说明：OpenRouter 的 `context_length` 是平台声明值，非实测值，且配置属 "deployment property"（可定制/可虚标，协议 §3.1 原话）。
因此 "ctx=262144 像 Mistral" 仅作参考，不作家族判据（尤其 union 的 ctx 与其他字段互相矛盾时）。
实测 ctx 需发超长 prompt（成本高，本次未做）。

## Stage 2：Tokenizer 差分 （核心证据）

### 跨家族（7 家族 × 5 探针）
| 家族 | 差分 | 判定 |
|---|---|---|
| Qwen（6 个模型） | 全部恒定（−62 / −53 / −11）| 命中 |
| GLM 系（4 个）| 变化 [−14,−13,−14,−13,−11] | 排除 |
| Mistral（3 个）| 变化（跨度 17）|| 排除 |
| Kimi K3 / MiniMax M3 / DeepSeek V4-Pro | 变化 | 排除 |

### 扩展字符集验证（code / emoji / 日文 / 数字）
| 差分 | code | emoji | japanese | numbers |
|---|---|---|---|---|
| union − qwen3.8-max | −62 | −62 | −62 | −62 |
| union − qwen3.7-max | −11 | −11 | −11 | −11 |

跨字符集完全恒定 → 非短提示碰撞（满足协议的跨长度/跨类型守卫）。

### Qwen 家族内自洽性
| 模型对 | 差分 |
|---|---|
| qwen3.8-max − qwen3.8-flash | 恒定 0 |
| qwen3.7-max − qwen3.6-flash | 恒定 0 |
| 3.8 系 − 3.7/3.6 系 | 恒定 51 |

验算自洽：union = qwen3.8 − 62 = qwen3.7 − 11，62 − 11 = 51
→ union 与 Qwen 3.6/3.7/3.8 三代共享同一 tokenizer（仅 system prompt 长度不同）。

### 稳定性（3 轮 + 10 轮复查）
- 4/5 基础探针 3 轮全一致（11/15/22/19）
- `cutoff` 探针：3 轮 [9,30,9]；6 轮 [9,9,9,30,9,9]；10 轮复查 [9,9,9,None,9,None,9,9,9,9]
- 修正解读：10 轮中 8 次稳定=9、2 次请求失败(None)、未再现 30
  → 该抖动源于请求失败/重试路径，而非模型 tokenizer 抖动（30 为异常值，非稳定态）
  → Stage 2 分析纪律：过滤失败请求；异常值单列，不并入差分计算

## Stage 3：行为探针（发现差异）

| 探针 | union | qwen3.8-max | qwen3.7-max |
|---|---|---|---|
| self_insist | 脚本化否认；rtok=0 | "我是 Qwen（通义千问）…"；rtok=133 | "我是通义千问…"；rtok=62 |
| reasoning_style | rtok=0 | rtok=85 | rtok=269 |
| code_cap | rtok=0 | rtok=62 | rtok=300 |

判定：union 无显式推理（rtok 恒 0），Qwen max 系均为 reasoning 模型 → 行为层与已知 Qwen max 变体不同。

### reasoning 开关验证（排除"未开开关"解释）
- 平台参数表：union `supported_parameters` = `max_tokens, response_format, temperature, tool_choice, tools, top_p`，不含 `reasoning`；qwen3.8/3.7-max 均含 `reasoning / reasoning_effort / include_reasoning`
- 显式传参实测（union）：默认 / `{enabled:true}` / `{effort:"high"}` / `{max_tokens:500}` → rtok 全部为 0
- 结论：union 平台层面不支持 reasoning，rtok=0 是部署特性而非调用方式问题 → 行为差异可靠

### 关推理对照（qwen3.8-flash, 2026-09-17 追加）
| 配置 | rtok | 与 union 差分 |
|---|---|---|
| qwen3.8-flash 默认（推理开）| 49–83 | −62（恒定）|
| qwen3.8-flash `reasoning:{enabled:false}` | 0 | −26（恒定）|

方法论发现：关推理会改变 ptok（本次 −36），平台在不同 reasoning 配置下注入不同 system prompt。
两种配置各自与 union 的差分仍恒定（同 tokenizer），但 −26 < −62，即 union 与"关推理配置"的 system prompt 更接近。

推论（支持性证据）：union ≈ Qwen 3.8 系的 non-reasoning 部署（rtok=0 一致；system prompt 仅差 26 token；tokenizer 同源）。

注意：ptok 差分含 system prompt 分量，差分恒定反映"同 tokenizer + 稳定 sys 差"，而非"sys 完全相同"（对协议 Stage 2 的解读纪律）。

### ctx 声明实测（2026-09-17 追加）
阶梯长 prompt 实测：64K/256K/512K/800K/1,000K 字符档全部成功（ptok 10,673→166,669）；
1,048,600 字符档被拒，错误消息："This endpoint's maximum context length is 262144 tokens"。
→ union 的 262,144 声明属实（不虚标）。

附带发现：平台拒绝时的估算口径为 字符数 ÷ 4（1,048,600 → 报 262,151），
而实测 ptok 比例为 1/6 字符 → 平台 ctx 准入检查用粗估，非真实 tokenizer 计数。

对照实验（qwen3.8-max，声称 1,000,000）：无法实测，免费/低额度账号对该付费模型的 prompt 上限为 4,633 token
（HTTP402: "Prompt tokens limit exceeded: 275007 > 4633"），远低于模型 ctx。
→ 审计注意事项：账号级 prompt 限制会掩盖模型真实 ctx，审计前须确认账号额度不构成瓶颈
（union 因是免费模型无此限制，故其 262,144 可实测）。
→ 该对照同时再次确认平台估算口径 = 字符数 ÷ 4（1,100,024 → 报 275,007）。

### ctx 对照实验（充值后重测, 2026-09-17 追加）

| 模型 | 声明 ctx | 实测 | 判定 |
|---|---|---|---|
| union-alpha | 262,144 | 262,144（错误消息确认）| 属实 |
| qwen3.8-max | 1,000,000 | ≥500,067（3.0M 字符档成功；3.8M 档请求超时未完成）| 至少 500K |

结论：两方声明均未证伪。union 与 qwen3.8-max 的 ctx 不同（262K vs ≥500K）→ 非同配置部署。

附带：
- qwen3.8-max 的 ptok/字符比（≈1/6）与 union 完全一致 → 再次支持同 tokenizer
- provider 溯源（endpoints API）：qwen3.8-max = Alibaba；union = "Stealth"（OpenRouter 匿名标签，不暴露厂商）；
  glm-5.3-flash = 6 个 provider（DeepInfra/InferenceNet/Relace/Morph/Wafer/GMICloud）

→ 综合定位更新：union = Qwen tokenizer 家族的独立/降配部署（262K ctx + 无 reasoning；非 qwen3.8-max/flash 的直接同配置）。

### 跨平台验证（OpenCode Go vs OpenRouter, 2026-09-17）

Go 端点（`zen/go/v1/messages`, Anthropic 格式）对照同一批探针：

| 项 | OpenCode Go | OpenRouter | 判定 |
|---|---|---|---|
| qwen3.8-flash / max 的 ptok | [73,77,71,84,81] | [73,77,71,84,81] | 逐点完全相同 |
| union-alpha 的 ptok | [_, 16, _, _, _]（端点不稳）| [11, 15, 9, 22, 19] | 近似（差 1）|
| union − qwen | −61（1 点）| −62 | ≈ 一致 |

结论：
1. Qwen 的 token 计数跨平台完全一致（provider 均为 Alibaba）→ 计数与平台网关无关
2. union − qwen 差分跨平台一致（−61 vs −62）→ tokenizer 结论不是平台 artifact（verification 通过）
3. 观测备注：union-alpha 在 OpenCode Go 端点路由不稳定（HTTP503 "Endpoint is unavailable" 与 HTTP401 "Missing API key" 交替出现；同端点 qwen3.8-flash/max 正常），记录为平台侧状态，不影响 OpenRouter 侧结论

### 那 1 个 token 的差异溯源（2026-09-17）

| 端点 | union ptok（identity_en）|
|---|---|
| OpenRouter `chat/completions` | 15 |
| OpenRouter `messages` | 15 |
| OpenCode Go `messages` | 16 |

→ 端点格式被排除（OR 两种格式同为 15）→ 差异来自平台/后端部署本身。

判定：同名 stealth 模型（`union-alpha`）在 OpenRouter（provider 标签 "Stealth"）与 OpenCode Go（provider "Console Go"）
并非同一逐字节部署（system prompt 或计数包装差 1 token）。

协议启示（新增纪律）：
> "相同 model id" ≠ "相同部署"，审计基准必须绑定到具体的（平台 × 端点 × 时间）三元组；
> 跨平台不可复用差分基准值。
> 但固定偏移不影响家族判据（两平台的 union−qwen 差分均恒定：−61 / −62）。

### ctx 三方对照补测（qwen3.8-flash, 2026-09-17）

| 模型 | 声明 ctx | 实测 | provider |
|---|---|---|---|
| union-alpha | 262,144 | 262,144（上限确认）| Stealth（匿名标签）|
| qwen3.8-flash | 1,000,000 | ≥500,067 | Alibaba |
| qwen3.8-max | 1,000,000 | ≥500,067 | Alibaba |
| qwen3.8-27b | 1,000,000（目录）| 未测 | provider 仅 262,144（声明不一致）|

要点：
1. flash 与 max 的 ptok 逐档完全相同（133,402/233,402/333,402/500,067）→ 同 tokenizer + 同配置（与 Δ0 一致）
2. union（262K）显著低于 flash/max（≥500K） → union 为降配部署，定位更明确
3. 发现声明不一致实例：qwen3.8-27b 目录标 1,000,000 但 provider 端 `context_length` 仅 262,144
   → 平台目录声明不可全信（支持"ctx 声明需实测"的方法论主张）

---

## 预测（分级）

| 层 | 结论 | 置信度 | 依据 |
|---|---|---|---|
| tokenizer 家族 | Qwen（阿里）系 | high | 6 个 Qwen 模型 × 9 探针（含跨字符集）全部恒定；家族内自洽；排除 GLM/Mistral/Kimi/MiniMax/DeepSeek |
| 具体变体/版本 | not pre-asserted | 未断言 | union 无 reasoning，与已知 Qwen max(reasoning) 系不同；可能是未发布的 non-reasoning 变体，或基于 Qwen tokenizer 的第三方模型 |
| system prompt 长度 | 比 qwen3.7 短 11 token、比 qwen3.8 短 62 token | medium | 差分分解 |

### 与社区假说的分歧（本预测的独立价值）
- 社区主流猜测：Mistral（ctx=256K 契合）或 Zhipu（沿用 Ox/Omen 系列模式）
- 本协议输出：Qwen（tokenizer 层），与社区共识相左
- 若揭晓为 Qwen：协议前瞻命中（且是"反共识"命中）
- 若揭晓为 Mistral/Zhipu：Stage 2 判据在"单一 provider 直转"场景下出现新的失败模式（需记录）

### 保留的替代解释（诚实边界）
1. 共享 tokenizer ≠ 同一模型（协议 §3.3 既有边界）
2. union 与 Qwen 可能由同一托管方服务（Stage 0 只证明"单一 provider"，未证明该 provider 就是 Qwen 官方）
3. `cutoff` 探针的偶发 ptok 抖动提示 union 侧存在轻度计数不稳定

## 揭晓评分标准
- 揭晓 Qwen/阿里：tokenizer 家族层预测正确
- 揭晓 Mistral/Zhipu/其他：预测错误，记录为"单一 provider 直转场景下 Stage 2 的失败案例"
- 长期不揭晓：按协议归为 *cannot attribute 的持续性观察*（tokenizer 层结论仍独立成立）

## 证据文件

`evidence/` 下 20 个文件，每个以产生它的运行时间戳命名：

- `probe-union-*`（基准 5 探针）
- `catalog-union-*`、`catalog2-union-*`（候选批次）
- `stability-union-*`（稳定性 3 轮）
- `charset-union-*`（扩展字符集）
- `qwen-cross-*`（Qwen 家族内交叉）
- `cutoff-recheck*`（cutoff 复查 6 轮与 10 轮）
- `stage3-union-*`（行为探针）
- `reasoning-switch-*`（reasoning 开关验证）
- `qwen38flash-noreason-*`、`qwen38max-noreason-*`（关推理对照）
- `ctx-sweep-*`（ctx 阶梯：union、qwen3.8-flash、qwen3.8-max）
- `xplat-go-*`（跨平台验证与重试）
- `stage0-stage1-20260917.md`（Stage 0/1 记录）

---

**更新（2026-09-17 晚）**：补充测量显示本端点的 prompt-token 计数**按探针类别走不同口径**（文本路径与 Qwen 系一致、图像路径与 GLM-5.3-Flash 一致，后者在 4 张图上恒定 −17 且随图像尺寸的增量逐点相同），且**同一文本请求会返回两个读数**（相差 +18~+21，成串出现而非逐次交替）。详见 `README.md` 的 Update 段。以上预测本体不变，仍限于文本路径的测量结论。

Post-reveal re-measurement (2026-09-18): see README, Update — 2026-09-18.
