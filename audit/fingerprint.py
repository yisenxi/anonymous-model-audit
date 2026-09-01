# -*- coding: utf-8 -*-
"""fingerprint.py — Stage 1: catalog-wide configuration fingerprinting

Pull platform model metadata, extract fingerprint fields (reasoning / params /
context / max output / tokenizer), run uniqueness checks and --match.

Usage:
  from audit import fingerprint
  db = fingerprint.scan("https://openrouter.ai", "/api/v1/models")
  fingerprint.match(db, "stealth/ox-alpha")
"""
import json
import os
import ssl
import time
import urllib.request
from collections import Counter

_CTX = ssl._create_unverified_context()

# 默认字段映射（OpenRouter /api/v1/models 结构；其他平台用 field_map 覆盖）
DEFAULT_FIELDS = {
    "context": "context_length",
    "max_out": "top_provider.max_completion_tokens",
    "tokenizer": "architecture.tokenizer",
    "modality": "architecture.modality",
    "reasoning": "reasoning",
    "supported_parameters": "supported_parameters",
    "default_parameters": "default_parameters",
    "pricing": "pricing",
    "created": "created",
    "expiration_date": "expiration_date",
}
COMP_FIELDS = ["reasoning", "supported_parameters", "context", "max_out"]


def _deep_get(obj, path):
    cur = obj
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def extract(m, fields):
    fp = {}
    for key, path in fields.items():
        v = _deep_get(m, path)
        if key == "supported_parameters" and isinstance(v, list):
            v = sorted(v)
        fp[key] = v
    return fp


def identity_key(fp, comp_fields=None):
    comp = comp_fields or COMP_FIELDS
    return json.dumps({k: fp[k] for k in comp if k in fp}, sort_keys=True, ensure_ascii=False)


def fetch_models(base_url, models_path, key=""):
    url = base_url.rstrip("/") + "/" + models_path.lstrip("/")
    h = {"User-Agent": "Mozilla/5.0 audit-tool/0.1"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=60, context=_CTX) as r:
        d = json.loads(r.read().decode())
    return d.get("data", d) if isinstance(d, dict) else d


def scan(base_url="https://openrouter.ai", models_path="/api/v1/models",
         field_map=None, key=""):
    """全库扫描：返回 {model_id: fingerprint}"""
    fields = field_map or DEFAULT_FIELDS
    models = fetch_models(base_url, models_path, key)
    return {m.get("id", f"idx-{i}"): extract(m, fields) for i, m in enumerate(models)}


def uniqueness(db, comp_fields=None):
    """指纹唯一性检测：返回 (总组合数, 重复组 {key: [成员]})"""
    c = Counter(identity_key(fp, comp_fields) for fp in db.values())
    dup = {k: [mid for mid, fp in db.items() if identity_key(fp, comp_fields) == k]
           for k, v in c.items() if v > 1}
    return len(c), dup


def match(db, target, comp_fields=None):
    """匹配模式：返回 (完全一致组, reasoning 结构相同组[带差异标注])"""
    if target not in db:
        return None, None
    tkey = identity_key(db[target], comp_fields)
    exact = [mid for mid, fp in db.items() if identity_key(fp, comp_fields) == tkey]
    t_reason = db[target].get("reasoning")
    same_reason = []
    for mid, fp in db.items():
        if mid != target and fp.get("reasoning") == t_reason:
            diffs = [k for k in (comp_fields or COMP_FIELDS)
                     if k != "reasoning" and fp.get(k) != db[target].get(k)]
            same_reason.append((mid, diffs))
    return exact, same_reason


def save(db, out_dir, tag="scan"):
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(out_dir, f"fingerprint-db-{tag}-{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ts": ts, "total": len(db), "db": db}, f, ensure_ascii=False, indent=1)
    return path
