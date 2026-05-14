---
name: scan-tech-debt
description: Scan a GitHub Python repository for technical debt — long functions, high cyclomatic complexity, and low maintainability. Outputs a structured debt_report.json for downstream refactoring.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [python, github, refactor, tech-debt, devops]
    category: devops
    requires_toolsets: [terminal]

required_environment_variables:
  - name: GITHUB_TOKEN
    prompt: GitHub personal access token
    help: "Create at https://github.com/settings/tokens — needs 'repo' scope"
    required_for: fetching repository files
  - name: GITHUB_REPO
    prompt: Target repository (owner/repo)
    help: "e.g. octocat/hello-world"
    required_for: knowing which repo to scan
---

# scan-tech-debt

Scans a GitHub Python repository for technical debt and produces a prioritized
`/tmp/debt_report.json`. This is Step 1 of the refactor pipeline.

## When to Use

- User says "scan for tech debt", "find technical debt", "analyze code quality"
- Before running `/generate-refactor-pr`
- On a Hermes cron schedule for automated daily/weekly scans

## Procedure

1. **Confirm environment** — check GITHUB_TOKEN and GITHUB_REPO are in `~/.hermes/.env`.

2. **Install dependencies if missing**:
```bash
pip install PyGithub radon python-dotenv
```

3. **Save and run the scanner**:

Save the script at `skills/devops/scan-tech-debt/scripts/scan_tech_debt.py  # 安装后位于 ~/.hermes/skills/devops/scan-tech-debt/scripts/scan_tech_debt.py`, then run:
```bash
python "$(hermes skill-path scan-tech-debt)/scripts/scan_tech_debt.py"
```

The scanner will:
- Fetch all `.py` files from the repo via GitHub API
- Detect: long functions (>50 lines), high cyclomatic complexity (>10), low maintainability index (<20)
- Sort by severity (critical → high → medium)
- Save top 5 debts to `/tmp/debt_report.json`

4. **Report to user**:
   - How many files were scanned
   - How many debts were found
   - Top debts: file, function, severity, reason
   - Confirm the report path

5. **Suggest next step**: "Run `/generate-refactor-pr` to create GitHub PRs for these debts."

## Setting up Cron (Automated Weekly Scan)

Tell Hermes in natural language:
```
every Monday at 9am, run /scan-tech-debt and send me a summary
```

Hermes will register this as a cron job and deliver the summary via whatever
messaging platform you're using (Telegram, Slack, Feishu, etc.).

## Pitfalls

- If GITHUB_TOKEN lacks `repo` scope, fetch returns 0 files silently — check token permissions first
- Repos with >500 Python files may hit GitHub rate limits — set `MAX_DEBTS_PER_RUN=3` and run during off-peak hours
- Binary or non-UTF-8 files are silently skipped (expected)
- `migrations/` and `tests/` directories are ignored by default

## Verification

```bash
cat /tmp/debt_report.json | python -m json.tool | head -40
```

Should show `debts` array with at least one item containing `file_path`, `severity`, `debt_type`.
