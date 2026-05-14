---
name: run-test-validation
description: Clone the refactor branch from a GitHub PR, run pytest, and report pass/fail results with logs. Provides automated quality gate for auto-generated refactor PRs.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [python, pytest, testing, ci, refactor, validation]
    category: devops
    requires_toolsets: [terminal]

required_environment_variables:
  - name: GITHUB_TOKEN
    prompt: GitHub personal access token
    help: "Needs 'repo' scope to read PR branches"
    required_for: cloning the PR branch
  - name: GITHUB_REPO
    prompt: Target repository (owner/repo)
    required_for: knowing which repo to test
---

# run-test-validation

Checks out a refactor PR branch, runs `pytest`, parses the results, and reports
back with a clear pass/fail + actionable log. This is Step 3 of the refactor
pipeline — the automated quality gate.

## When to Use

- After `/generate-refactor-pr` has created one or more PRs
- User says "run tests", "validate the refactor", "check if tests pass"
- On a cron trigger after PRs are opened

## Procedure

1. **Get the PR branch name** — either from the user or by reading `/tmp/debt_report.json`
   for the most recent refactor run.

2. **Install dependencies if missing**:
```bash
pip install PyGithub python-dotenv pytest
```

3. **Clone and test in an isolated temp directory**:

```bash
# Done automatically by the validation script
git clone --depth=1 --branch {branch_name} https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git /tmp/refactor-test
cd /tmp/refactor-test
pip install -e ".[dev]" 2>/dev/null || pip install -r requirements.txt 2>/dev/null || true
python -m pytest --tb=short --json-report --json-report-file=/tmp/test_result.json -q
```

4. **Parse and summarize results** from `/tmp/test_result.json`:
   - Total tests, passed, failed, errors
   - If **PASS**: recommend marking the PR as ready for review
   - If **FAIL**: show the failing test names and tracebacks, suggest the PR needs manual fix

5. **Report to user** with:
   - ✅ or ❌ status
   - Summary line: "42 passed, 0 failed in 8.3s"
   - On failure: paste the first 3 failing test names and their short tracebacks

6. **Cleanup** the temp clone:
```bash
rm -rf /tmp/refactor-test
```

## Decision Logic

| Test result   | Action                                              |
|---------------|-----------------------------------------------------|
| All pass      | Notify user, suggest marking PR ready for review    |
| Some fail     | Show failures, suggest manual inspection of the PR  |
| Import errors | Likely missing dependency — check requirements.txt  |
| Timeout >5min | Kill process, report as inconclusive                |

## Pitfalls

- If the repo has no tests, pytest will exit 5 (no tests collected) — treat this as "inconclusive, not failure"
- Some repos require secrets/env vars to run tests — check for a `.env.test` or `pytest.ini`
- The clone uses GITHUB_TOKEN for auth; make sure it has read access to the branch

## Verification

```bash
cat /tmp/test_result.json | python -m json.tool | grep -E '"outcome"|"nodeid"' | head -20
```
