# -*- coding: utf-8 -*-
"""client.py — OpenAI-compatible chat/completions client (records usage fields)

stdlib only (urllib); API keys are read from the environment and never logged.
"""
import json
import ssl
import time
import urllib.error
import urllib.request

TIMEOUT = 180
MAX_RETRIES = 3
_CTX = ssl._create_unverified_context()


class LLMClient:
    """OpenAI 兼容 chat/completions 客户端，返回 content/reasoning/usage 全字段。"""

    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def chat(self, model, prompt, max_tokens=1000):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "stream": False,
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"},
            method="POST")
        t0 = time.time()
        for attempt in range(MAX_RETRIES + 1):
            if attempt > 0:
                time.sleep(2 * attempt)
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX) as r:
                    body = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    detail = e.read().decode("utf-8", errors="replace")[:200]
                    raise RuntimeError(f"HTTP {e.code}: {detail}")
                if attempt == MAX_RETRIES:
                    raise
            except Exception:
                if attempt == MAX_RETRIES:
                    raise
        msg = body["choices"][0]["message"]
        usage = body.get("usage") or {}
        return {
            "content": msg.get("content") or "",
            "reasoning": (msg.get("reasoning") or "")[:500],
            "reasoning_details": msg.get("reasoning_details"),
            "model_echo": body.get("model"),
            "usage": {k: usage.get(k) for k in
                      ["prompt_tokens", "completion_tokens", "total_tokens",
                       "reasoning_tokens", "cached_tokens"]},
            "latency_s": round(time.time() - t0, 2),
        }


# 模型注册表（别名 -> base_url, key 环境变量, model_id）
# 使用方可用 register() 增补自己的模型/端点。
MODELS = {
    "ox":     ("https://openrouter.ai/api/v1",    "OPENROUTER_API_KEY", "stealth/ox-alpha"),
    "glm53":  ("https://open.bigmodel.cn/api/paas/v4", "ZHIPU_API_KEY", "glm-5.3"),
    "glm52":  ("https://open.bigmodel.cn/api/paas/v4", "ZHIPU_API_KEY", "glm-5.2"),
    "mimo":   ("https://api.xiaomimimo.com/v1",   "MIMO_API_KEY", "mimo-v2.5-pro"),
    "kimi":   ("https://api.moonshot.cn/v1",      "MOONSHOT_API_KEY", "kimi-k3"),
    "qwen":   ("https://dashscope.aliyuncs.com/compatible-mode/v1", "ALI_API_KEY", "qwen3.8-max"),
    "hy3":    ("https://tokenhub.tencentmaas.cn/v1", "TENCENT_API_KEY", "hy3"),
    "ernie":  ("https://qianfan.baidubce.com/v2", "BAIDU_API_KEY", "ernie-5.1"),
    "step":   ("https://api.stepfun.com/v1",      "STEP_API_KEY", "step-3.7-flash"),
}


def register(alias, base_url, key_env, model_id):
    MODELS[alias] = (base_url, key_env, model_id)
