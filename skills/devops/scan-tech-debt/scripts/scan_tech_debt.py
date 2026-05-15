#!/usr/bin/env python3
"""
Tech Debt Scanner — called by Hermes /scan-tech-debt skill
Install: pip install PyGithub radon python-dotenv
Place at: ~/.hermes/scripts/scan_tech_debt.py
"""

import ast
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

from dotenv import load_dotenv
from github import Github
from radon.complexity import cc_visit
from radon.metrics import mi_visit

load_dotenv(Path.home() / ".hermes" / ".env")

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO  = os.environ["GITHUB_REPO"]
MAX_DEBTS    = int(os.environ.get("MAX_DEBTS_PER_RUN", "5"))
OUTPUT_PATH  = Path(os.environ.get("DEBT_REPORT_PATH", "/tmp/debt_report.json"))

THRESHOLDS = {
    "max_function_lines":        50,
    "max_cyclomatic_complexity": 10,
    "min_maintainability_index": 20,
}
IGNORE_PATTERNS = [
    "*/migrations/*", "*/tests/*", "*/vendor/*",
    "*/__pycache__/*", "setup.py",
]

@dataclass
class DebtItem:
    file_path: str
    function_name: str
    debt_type: str
    severity: str
    detail: str
    line_start: int
    line_end: int
    current_value: float
    threshold: float

def should_ignore(path):
    return any(fnmatch(path, p) for p in IGNORE_PATTERNS)

def fetch_python_files():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    results = []
    def walk(path=""):
        for item in repo.get_contents(path):
            if item.type == "dir":
                walk(item.path)
            elif item.name.endswith(".py") and not should_ignore(item.path):
                try:
                    results.append((item.path, item.decoded_content.decode("utf-8")))
                except Exception:
                    pass
    walk()
    return results

def analyze(file_path, content):
    debts = []
    t = THRESHOLDS
    try:
        for block in cc_visit(content):
            if block.complexity > t["max_cyclomatic_complexity"]:
                sev = "critical" if block.complexity > t["max_cyclomatic_complexity"] * 1.5 else "high"
                debts.append(DebtItem(
                    file_path=file_path, function_name=block.name,
                    debt_type="high_complexity", severity=sev,
                    detail=f"Cyclomatic complexity {block.complexity}, threshold {t['max_cyclomatic_complexity']}.",
                    line_start=block.lineno, line_end=block.endline,
                    current_value=block.complexity, threshold=t["max_cyclomatic_complexity"],
                ))
    except Exception:
        pass
    try:
        for node in ast.walk(ast.parse(content)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = getattr(node, "end_lineno", node.lineno) - node.lineno + 1
                if length > t["max_function_lines"]:
                    sev = "critical" if length > t["max_function_lines"] * 2 else "high"
                    debts.append(DebtItem(
                        file_path=file_path, function_name=node.name,
                        debt_type="long_function", severity=sev,
                        detail=f"Function is {length} lines, threshold {t['max_function_lines']}.",
                        line_start=node.lineno, line_end=getattr(node, "end_lineno", node.lineno),
                        current_value=length, threshold=t["max_function_lines"],
                    ))
    except SyntaxError:
        pass
    try:
        mi = mi_visit(content, multi=True)
        if isinstance(mi, (int, float)) and mi < t["min_maintainability_index"]:
            debts.append(DebtItem(
                file_path=file_path, function_name="<module>",
                debt_type="low_maintainability", severity="medium",
                detail=f"Maintainability index {mi:.1f}, threshold {t['min_maintainability_index']}.",
                line_start=1, line_end=len(content.splitlines()),
                current_value=round(mi, 2), threshold=t["min_maintainability_index"],
            ))
    except Exception:
        pass
    return debts

print(f"[scan] Fetching from {GITHUB_REPO} ...")
files = fetch_python_files()
print(f"[scan] Analyzing {len(files)} files ...")
all_debts = []
for path, content in files:
    all_debts.extend(analyze(path, content))

severity_order = {"critical": 0, "high": 1, "medium": 2}
all_debts.sort(key=lambda d: (severity_order.get(d.severity, 9), -d.current_value))
top = all_debts[:MAX_DEBTS]

report = {
    "repo": GITHUB_REPO,
    "scanned_at": datetime.utcnow().isoformat(),
    "total_files": len(files),
    "total_debts_found": len(all_debts),
    "debts_to_process": len(top),
    "summary": {"by_type": {}, "by_severity": {}},
    "debts": [asdict(d) for d in top],
}
for d in all_debts:
    report["summary"]["by_type"][d.debt_type] = report["summary"]["by_type"].get(d.debt_type, 0) + 1
    report["summary"]["by_severity"][d.severity] = report["summary"]["by_severity"].get(d.severity, 0) + 1

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(f"[scan] Done. {len(all_debts)} debts found, top {len(top)} saved → {OUTPUT_PATH}")
print(json.dumps(report["summary"], indent=2))
