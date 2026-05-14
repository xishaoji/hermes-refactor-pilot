---
name: refactor-pipeline
description: Run the full automated refactor pipeline end-to-end — scan tech debt, generate PRs, and validate tests — in a single command.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [python, github, refactor, pipeline, devops]
    category: devops
    requires_toolsets: [terminal]
---

# refactor-pipeline

Orchestrates the full three-step refactor pipeline in one shot:

```
/scan-tech-debt  →  /generate-refactor-pr  →  /run-test-validation
```

## When to Use

- User says "run the full refactor pipeline", "do a complete refactor run"
- Scheduled cron job for automated weekly refactoring

## Procedure

1. Run `/scan-tech-debt` — wait for debt_report.json
2. If 0 debts found → report "No tech debt found, skipping." and stop
3. Run `/generate-refactor-pr` — collect list of created PR URLs
4. For each PR branch, run `/run-test-validation`
5. Summarize results:
   - N files scanned
   - M debts found
   - K PRs created (with URLs)
   - Test results per PR (pass / fail / inconclusive)

## Cron Setup (Automated Weekly Run)

Tell Hermes:
```
每周一早上9点运行 /refactor-pipeline，把结果发到飞书
```

Hermes 会注册一个 cron job，每周自动执行完整流程并推送摘要。

## Output Format

```
📊 重构周报 — 2026-05-12

扫描：42 个文件，发现 8 个技术债
本次处理：5 个（按严重程度排序）

PR 状态：
  ✅ big_function in service/user.py → https://github.com/.../pull/42 (测试通过)
  ✅ parse_config in utils/config.py  → https://github.com/.../pull/43 (测试通过)
  ❌ process_data in jobs/etl.py     → https://github.com/.../pull/44 (2个测试失败)

待处理：3 个技术债留到下次
```
