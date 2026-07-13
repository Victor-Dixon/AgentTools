from __future__ import annotations

from datetime import datetime
from pathlib import Path

root = Path("data/reports/projectscanner_library")
rows = []

for d in sorted(root.iterdir()) if root.exists() else []:
    if not d.is_dir():
        continue
    stdout = d / "projectscanner_stdout.txt"
    report = d / "projects_report.md"
    rows.append(
        {
            "repo": d.name,
            "stdout_exists": stdout.exists(),
            "report_exists": report.exists(),
            "stdout_lines": len(stdout.read_text(errors="ignore").splitlines())
            if stdout.exists()
            else 0,
            "report_lines": len(report.read_text(errors="ignore").splitlines())
            if report.exists()
            else 0,
        }
    )

lines = [
    "# Projectscanner Library Index",
    "",
    "generated={}".format(datetime.now().isoformat(timespec="seconds")),
    "",
    "| repo | stdout | report | stdout lines | report lines |",
    "|---|---|---|---:|---:|",
]
for row in rows:
    lines.append(
        "| `{repo}` | {stdout} | {report} | {stdout_lines} | {report_lines} |".format(
            repo=row["repo"],
            stdout=row["stdout_exists"],
            report=row["report_exists"],
            stdout_lines=row["stdout_lines"],
            report_lines=row["report_lines"],
        )
    )

Path("data/reports/projectscanner_library_index.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
print("SCANNED={}".format(len(rows)))
