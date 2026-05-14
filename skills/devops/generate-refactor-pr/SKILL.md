---
name: generate-refactor-pr
description: Read debt_report.json from scan-tech-debt, use an LLM to generate refactored Python code for each debt item, and automatically create a GitHub Pull Request with the changes.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [python, github, refactor, pull-request, llm]
    category: devops
    requires_toolsets: [terminal]

required_environment_variables:
  - name: GITHUB_TOKEN
    prompt: GitHub personal access token
    help: "Needs 'repo' scope to create branches and PRs"
    required_for: creating branches and pull requests
  - name: GITHUB_REPO
    prompt: Target repository (owner/repo)
    required_for: knowing which repo to open PRs against
  - name: ANTHROPIC_API_KEY
    prompt: Anthropic API key
    help: "Get from https://console.anthropic.com"
    required_for: generating refactored code with Claude
---

# generate-refactor-pr

Reads `/tmp/debt_report.json` (produced by `/scan-tech-debt`), calls Claude to
generate refactored code for each debt item, then opens a **draft Pull Request**
on GitHub. This is Step 2 of the refactor pipeline.

## When to Use

- After `/scan-tech-debt` has produced a report
- User says "create refactor PR", "fix the tech debt", "generate PRs"

## Procedure

1. **Confirm prerequisites**:
   - `/tmp/debt_report.json` exists (run `/scan-tech-debt` first if not)
   - GITHUB_TOKEN, GITHUB_REPO, ANTHROPIC_API_KEY are set in `~/.hermes/.env`

2. **Install dependencies if missing**:
```bash
pip install PyGithub anthropic python-dotenv
```

3. **Save and run the PR generator**:

Save the script at `skills/devops/generate-refactor-pr/scripts/generate_refactor_pr.py  # 安装后位于 ~/.hermes/skills/devops/generate-refactor-pr/scripts/generate_refactor_pr.py`, then run:
```bash
python "$(hermes skill-path generate-refactor-pr)/scripts/generate_refactor_pr.py"
```

The script will for each debt item:
- Fetch the current file content from GitHub
- Extract the target function (line_start → line_end)
- Send to Claude with a refactor prompt
- Create a new branch: `refactor/auto-{debt_type}-{timestamp}`
- Commit only the changed file
- Open a **draft PR** titled `[Auto Refactor] {function_name} in {file_path}`
- Add labels: `auto-refactor`, `tech-debt`

4. **Report to user**:
   - List of PRs created with URLs
   - Any items skipped (e.g. parse errors)
   - Remind user: "These are draft PRs — review before marking ready."

5. **Suggest next step**: "Run `/run-test-validation` to check if tests still pass."

## PR Design Decisions

- **Draft PRs only** — prevents accidental merge; human must review and approve
- **One PR per debt item** — keeps diffs small and reviewable
- **Branch naming**: `refactor/auto-{type}-{yyyymmdd-hhmmss}`
- **Base branch**: `main` (configurable via `REFACTOR_BASE_BRANCH` env var)

## Pitfalls

- If the function spans multiple classes or has complex imports, Claude may miss context — the prompt includes ±20 lines of surrounding code as context window
- GitHub API allows max 1000 files per commit via contents API; for larger changes use git CLI instead
- Rate limit: GitHub allows 5000 API calls/hour per token — fine for typical runs

## Verification

After running, check:
```bash
# List recently created branches
gh pr list --label auto-refactor --state open
```

Each PR should have a clear description of what was refactored and why.
