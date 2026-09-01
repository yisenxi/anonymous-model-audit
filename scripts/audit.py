# -*- coding: utf-8 -*-
"""audit.py — audit-tool CLI 入口

用法:
  python scripts/audit.py fingerprint [--base-url URL] [--models-path PATH] [--match ID] [--out DIR]
  python scripts/audit.py run --target ox --candidates glm53,kimi [--hard] [--format] [--rounds 1] [--out DIR] [--tag NAME]

示例:
  python scripts/audit.py fingerprint --match stealth/ox-alpha
  python scripts/audit.py run --target ox --candidates glm53,kimi --hard --format
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from audit import fingerprint, runner  # noqa: E402

DEFAULT_OUT = os.path.join(os.path.dirname(__file__), "..", "data")


def cmd_fingerprint(args):
    key = os.environ.get("OPENROUTER_API_KEY", "")
    db = fingerprint.scan(args.base_url, args.models_path, key=key)
    print(f"[INFO] {args.base_url} 共 {len(db)} 模型")
    n, dup = fingerprint.uniqueness(db)
    print(f"指纹组合总数: {n}，重复组: {len(dup)}")
    for members in dup.values():
        print(f"  组({len(members)}): {members}")
    if args.match:
        exact, same = fingerprint.match(db, args.match)
        if exact is None:
            print(f"[WARN] {args.match} 不在库中")
        else:
            print(f"\n=== 与 {args.match} 指纹完全一致的模型 ===")
            for m in exact:
                print(f"  {m}")
            if same:
                print(f"\n=== reasoning 结构相同的模型 ===")
                for m, diffs in same:
                    print(f"  {m}  (差异: {','.join(diffs) or '无'})")
    if args.save:
        path = fingerprint.save(db, args.out, tag=args.tag)
        print(f"[SAVE] {path}")


def cmd_run(args):
    names = [args.target] + [c.strip() for c in args.candidates.split(",")]
    unknown = [n for n in names if n not in runner.MODELS]
    if unknown:
        print(f"[ERR] 未知模型: {unknown}")
        sys.exit(1)
    recs, diffs, summary = runner.audit(
        args.target, names[1:], hard=args.hard, fmt=args.format,
        rounds=args.rounds, out_dir=args.out, tag=args.tag)
    print(runner.render_summary(summary, args.target, names[1:]))
    if recs:
        path = runner.save(recs, args.out, tag=args.tag)
        print(f"\n[SAVE] {path}")


def main():
    ap = argparse.ArgumentParser(description="audit-tool: anonymous-model forensic audit")
    sub = ap.add_subparsers(dest="cmd", required=True)

    fp = sub.add_parser("fingerprint", help="阶段一：配置层全库指纹扫描")
    fp.add_argument("--base-url", default="https://openrouter.ai")
    fp.add_argument("--models-path", default="/api/v1/models")
    fp.add_argument("--match", default=None, help="目标模型 ID，输出唯一匹配")
    fp.add_argument("--out", default=DEFAULT_OUT)
    fp.add_argument("--tag", default="scan")
    fp.add_argument("--save", action="store_true")
    fp.set_defaults(func=cmd_fingerprint)

    rn = sub.add_parser("run", help="阶段二三：行为矩阵 + 差值恒定检测")
    rn.add_argument("--target", required=True, help="目标模型别名（MODELS 注册表）")
    rn.add_argument("--candidates", required=True, help="候选池，逗号分隔")
    rn.add_argument("--hard", action="store_true", help="跑能力题")
    rn.add_argument("--format", action="store_true", help="跑格式题")
    rn.add_argument("--rounds", type=int, default=1)
    rn.add_argument("--out", default=DEFAULT_OUT)
    rn.add_argument("--tag", default="audit")
    rn.set_defaults(func=cmd_run)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
