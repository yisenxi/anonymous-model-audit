# -*- coding: utf-8 -*-
"""probes.py — synthetic audit probe bank (no production or personal data)

- IDENTITY_PROBES: self-report / knowledge-cutoff probes
- LONG_PROBES:     multi-length text for cross-length differentials
- HARD_QUESTIONS:  capability ceiling probes
- FORMAT_PROBES:   format-constraint probes + self-justification patterns

All prompts are synthetic; do not add real business or personal content.
"""
import json
import re

# ------------------------------------------------------------------ 身份自报
IDENTITY_PROBES = [
    {"id": "identity_zh", "prompt": "你是哪个公司或组织开发的模型？请如实回答你的真实身份。"},
    {"id": "identity_en", "prompt": "Which company or organization developed you? Answer truthfully about your real identity."},
    {"id": "cutoff", "prompt": "你的知识截止日期是什么时候？只回答日期。"},
]

# ------------------------------------------------------------------ 多长度（阶段三差值恒定检测）
LONG_PROBES = [
    {"id": "long_zh", "prompt": "请用中文详细解释什么是量子计算。请从量子比特的基本概念讲起，介绍叠加态和纠缠态，然后讨论量子纠错、量子退相干、以及当前主流的量子计算硬件平台（包括超导、离子阱、光量子、中性原子等路线）的优缺点，最后谈谈量子计算在密码学、化学模拟、优化问题和大规模机器学习中的潜在应用，以及未来十年可能面临的工程挑战。请给出全面而深入的分析，字数不限，但请务必覆盖上述所有方面。"},
    {"id": "long_en", "prompt": "The quick brown fox jumps over the lazy dog. The history of computing is a fascinating journey from mechanical calculators through vacuum tubes and transistors to integrated circuits and modern microprocessors. Today we are witnessing the rise of neural networks, large language models, and artificial intelligence systems that can write code, generate images, and reason about complex problems. This essay explores how we got here and where we might be going, covering topics such as Moore's Law, the von Neumann architecture, parallel computing, cloud infrastructure, and the social implications of automation."},
]

# ------------------------------------------------------------------ 硬判分能力题
HARD_QUESTIONS = [
    {"id": "H1", "type": "math", "prompt": "计算 2024 的 2024 次方除以 7 的余数。只输出数字。",
     "math": r"^\s*1\s*$"},
    {"id": "H2", "type": "math", "prompt": "第 100 个质数是多少？只输出数字。",
     "math": r"^\s*541\s*$"},
    {"id": "H3", "type": "math", "prompt": "计算 1 的平方加 2 的平方一直加到 100 的平方（即 Σk², k=1..100）。只输出数字。",
     "math": r"^\s*338350\s*$"},
    {"id": "H4", "type": "math", "prompt": "计算定积分 ∫₀¹ (3x² + 2x) dx 的值。只输出数字。",
     "math": r"^\s*2\s*$"},
    {"id": "H5", "type": "logic", "prompt": "骑士永远说真话，骗子永远说假话。A 说：\"B 是骗子\"。B 说：\"A 和我是同一种人\"。请回答：A 和 B 分别是什么身份？只回答格式如：A=骑士，B=骗子。",
     "checkers": [["A=骑士", "A是骑士", "A 是骑士", "A 骑士"], ["B=骗子", "B是骗子", "B 是骗子", "B 骗子"]]},
    {"id": "H6", "type": "math", "prompt": "数列 2, 6, 12, 20, 30, ? 的下一个数是多少？只输出数字。",
     "math": r"^\s*42\s*$"},
    {"id": "H7", "type": "code", "prompt": "用 Python 计算 1 到 100 之间所有 3 的倍数的和。只输出最终数字结果。",
     "math": r"^\s*1683\s*$"},
    {"id": "H8", "type": "code", "prompt": "对有序数组 [1, 3, 5, 7, 9, 11, 13] 用二分查找定位元素 7，返回其索引（从 0 开始）。只输出索引数字。",
     "math": r"^\s*3\s*$"},
    {"id": "H9", "type": "instruct", "prompt": "写一句 10 个字以内的话。要求：必须包含\"天空\"二字；不能包含\"的\"字；不要解释为什么。只输出那句话。",
     "checkers": [["天空"]]},
    {"id": "H10", "type": "math", "prompt": "1! + 2! + 3! + 4! 等于多少？只输出数字。",
     "math": r"^\s*33\s*$"},
]

# ------------------------------------------------------------------ 格式纪律题 + 自证检测
SELFJUST_PAT = re.compile(
    r"(共\s*\d+\s*字|已\s*(满足|符合|遵守)|注[:：]|（[^）]{0,10}(字|要求|约束)|不含|无[“\"']?的[\"']?字)")

FORMAT_PROBES = [
    {"id": "F1", "type": "json", "prompt": "输出一个 JSON 对象，包含字段 name（值 test）和 value（值 42）。只输出 JSON，不要任何其他文字。",
     "check": lambda c: json.loads(c.strip()) == {"name": "test", "value": 42}},
    {"id": "F2", "type": "upper", "prompt": "把短语 \"hello world\" 翻译成英文大写形式（全部大写字母，只有空格分隔）。只输出结果。",
     "check": lambda c: re.fullmatch(r"[A-Z ]+", c.strip()) is not None and "HELLO" in c.upper()},
    {"id": "F3", "type": "exactlen", "prompt": "用恰好 15 个字（不含标点）介绍你自己。只输出那 15 个字。",
     "check": lambda c: len(re.sub(r"[，。！？、,.!?；;:：\"'\"'\s]", "", c.strip())) == 15},
    {"id": "F4", "type": "template", "prompt": "用以下模板回答：以 [BEGIN] 开头，中间写\"格式测试\"四个字，以 [END] 结尾。不要输出其他内容。",
     "check": lambda c: c.strip().startswith("[BEGIN]") and c.strip().endswith("[END]")},
    {"id": "F5", "type": "selfjust", "prompt": "用一句话介绍你自己。要求：必须包含“助手”二字；不能包含“的”字；总字数在 12 到 25 之间（含标点）。",
     "check": lambda c: ("助手" in c) and ("的" not in c) and (12 <= len(c.strip()) <= 25),
     "selfjust": True},
    {"id": "F6", "type": "order", "prompt": "列出喜欢编程的 3 个理由，编号顺序必须为：3、1、2（第一条写编号3，第二条写编号1，第三条写编号2）。",
     "check": lambda c: c.find("3.") < c.find("1.") < c.find("2.")},
    {"id": "F7", "type": "nopunct", "prompt": "写一句 8 个字的话形容大海。要求：不能使用任何标点符号。只输出那句话。",
     "check": lambda c: len(re.sub(r"[，。！？、,.!?；;:：\"'\"'\s]", "", c.strip())) == 8
                        and not re.search(r"[，。！？、,.!?；;:：]", c)},
    {"id": "F8", "type": "nestedjson", "prompt": "输出嵌套 JSON：外层字段 ok 值 true，内层 data 包含字段 a=1。只输出 JSON。",
     "check": lambda c: json.loads(c.strip()) == {"ok": True, "data": {"a": 1}}},
    {"id": "F9", "type": "numonly", "prompt": "1 加 2 乘 3 等于多少？只输出数字，不要任何文字。",
     "check": lambda c: re.fullmatch(r"\s*7\s*", c) is not None},
    {"id": "F10", "type": "oneliner", "prompt": "用一行不超过 50 个字符的英文句子解释什么是递归。",
     "check": lambda c: len(c.strip()) <= 50 and "recurs" in c.lower()},
]
