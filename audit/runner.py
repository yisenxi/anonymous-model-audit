# -*- coding: utf-8 -*-
"""runner.py — Stages 2–3: behavioral matrix + cross-length tokenizer differentials

Short prompts alone can collide across tokenizers; the differential check must
span short / medium / long (and language) probes.

Usage:
  from audit import runner
  result = runner.audit(target="ox", candidates=["glm53", "kimi"], hard=True, format=True)
"""
import json
import os
import time

from .client import LLMClient, MODELS
from .probes import IDENTITY_PROBES, LONG_PROBES, HARD_QUESTIONS, FORMAT_PROBES


def _probe_plan(hard, fmt):
    plan = []
    for p in IDENTITY_PROBES:
        plan.append(("identity", p["id"], p["prompt"], None, 1500))
    for p in LONG_PROBES:
        plan.append(("long", p["id"], p["prompt"], None, 5))  # 只要 usage
    if hard:
        for q in HARD_QUESTIONS:
            plan.append(("hard", q["id"], q["prompt"],
                         {"type": q["type"], "math": q.get("math"), "checkers": q.get("checkers")}, 1500))
    if fmt:
        for q in FORMAT_PROBES:
            plan.append(("format", q["id"], q["prompt"], {"selfjust": q.get("selfjust")}, 1500))
    return plan


def audit(target, candidates, hard=False, fmt=False, rounds=1,
          out_dir=None, tag=None, on_record=None):
    """执行审计：返回 (records, diffs, summary)

    records: 全量探针记录（含 usage/reasoning 全字段）
    diffs:   tokenizer 差值表（target vs 每候选，跨长度）
    summary: 每模型统计（身份/能力/格式/差值恒定判定）
    """
    names = [target] + list(candidates)
    clients, recs = {}, []

    for n in names:
        if n not in MODELS:
            print(f"[SKIP] 未知模型 {n}")
            continue
        base, key_env, mid = MODELS[n]
        key = os.environ.get(key_env, "")
        if not key:
            print(f"[SKIP] 环境变量 {key_env} 未设置，跳过 {n}")
            continue
        clients[n] = LLMClient(base, key)

    plan = _probe_plan(hard, fmt)
    for n, cli in clients.items():
        mid = MODELS[n][2]
        for kind, pid, prompt, meta, mt in plan:
            for r in range(rounds):
                try:
                    res = cli.chat(mid, prompt, max_tokens=mt)
                    rec = {"ts": time.strftime("%Y%m%d-%H%M%S"), "probe": pid, "kind": kind,
                           "round": r, "meta": meta, "content": res["content"],
                           "reasoning": res["reasoning"],
                           "reasoning_details": res["reasoning_details"],
                           "usage": res["usage"], "model_echo": res["model_echo"],
                           "latency_s": res["latency_s"]}
                except Exception as e:
                    rec = {"ts": time.strftime("%Y%m%d-%H%M%S"), "probe": pid, "kind": kind,
                           "round": r, "error": str(e)[:200]}
                recs.append(rec)
                if on_record:
                    on_record(rec)

    # 阶段三：差值恒定检测（跨长度）
    diffs = []
    if target in clients:
        tmid = MODELS[target][2]
        for c, cli in clients.items():
            if c == target:
                continue
            cmid = MODELS[c][2]
            for p in IDENTITY_PROBES + LONG_PROBES:
                rt = [r for r in recs if r.get("probe") == p["id"] and r.get("model_echo") == tmid]
                rc = [r for r in recs if r.get("probe") == p["id"] and r.get("model_echo") == cmid]
                if rt and rc and rt[0].get("usage") and rc[0].get("usage"):
                    pt_t = rt[0]["usage"].get("prompt_tokens")
                    pt_c = rc[0]["usage"].get("prompt_tokens")
                    if pt_t is not None and pt_c is not None:
                        diffs.append({"cand": c, "probe": p["id"],
                                      "target": pt_t, "cand_pt": pt_c, "diff": pt_t - pt_c})

    return recs, diffs, summarize(recs, diffs, target, candidates)


def summarize(recs, diffs, target, candidates):
    """生成每模型摘要 + 差值恒定判定（跨长度恒定 = 同 tokenizer 信号）"""
    summary = {}
    id_of = {MODELS[n][2]: n for n in [target] + list(candidates) if n in MODELS}
    for mid, name in id_of.items():
        mrecs = [r for r in recs if r.get("model_echo") == mid]
        summary[name] = {
            "calls": len(mrecs),
            "identity": {r["probe"]: (r.get("content") or "")[:60].replace("\n", " ")
                         for r in mrecs if r.get("kind") == "identity"},
            "reasoning_tokens": {r["probe"]: (r.get("usage") or {}).get("reasoning_tokens")
                                 for r in mrecs if r.get("kind") == "identity"},
            "hard_output": sum(1 for r in mrecs if r.get("kind") == "hard" and r.get("content")),
            "hard_total": sum(1 for r in mrecs if r.get("kind") == "hard"),
            "format_output": sum(1 for r in mrecs if r.get("kind") == "format" and r.get("content")),
            "format_total": sum(1 for r in mrecs if r.get("kind") == "format"),
        }

    # 差值恒定判定：跨长度（identity×3 + long×2）全恒定 = 同 tokenizer 信号
    by_cand = {}
    for d in diffs:
        by_cand.setdefault(d["cand"], []).append(d["diff"])
    for cand, vals in by_cand.items():
        summary.setdefault(cand, {})["diff_constant"] = \
            (len(set(vals)) == 1 and len(vals) >= 2, vals)
    return summary


def render_summary(summary, target, candidates):
    """控制台渲染摘要"""
    lines = [f"===== 审计汇总 目标={target} 候选={','.join(candidates)} ====="]
    for n in [target] + list(candidates):
        s = summary.get(n)
        if not s:
            lines.append(f"\n[{n}] 无数据")
            continue
        lines.append(f"\n[{n}] 调用 {s.get('calls', 0)} 次")
        for pid, text in (s.get("identity") or {}).items():
            lines.append(f"  {pid}: {text}")
        if "hard_total" in s:
            lines.append(f"  能力题: {s['hard_output']}/{s['hard_total']} 有输出")
        if "format_total" in s:
            lines.append(f"  格式题: {s['format_output']}/{s['format_total']} 有输出")
        if "diff_constant" in s:
            const, vals = s["diff_constant"]
            verdict = "跨长度恒定 = 同 tokenizer 信号" if const else "不恒定（不同 tokenizer）"
            lines.append(f"  差值({n} vs 目标): {vals} → {verdict}")
    return "\n".join(lines)


def save(recs, out_dir, tag="audit"):
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(out_dir, f"audit-{tag}-{ts}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return path
