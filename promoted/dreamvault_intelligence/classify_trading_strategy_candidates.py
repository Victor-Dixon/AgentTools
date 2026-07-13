#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path.home() / "projects"
OUT_JSON = Path("runtime/trading/strategies/strategy_candidates.json")
OUT_MD = Path("data/reports/trading/strategy_candidates.md")

repo_keywords = re.compile(r"(trading|trade|stock|market|invest|robot|pine|pinescript|macd|strategy)", re.I)
file_keywords = re.compile(r"(//@version|strategy\s*\(|indicator\s*\(|macd|rsi|bollinger|buy|sell|long|short|entry|exit)", re.I)

candidates = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(part in {".git", "node_modules", ".venv", "__pycache__"} for part in path.parts):
        continue
    if path.suffix.lower() not in {".pine", ".pinescript", ".txt", ".md", ".py", ".js", ".ts", ".json"}:
        continue

    repo_name = path.relative_to(ROOT).parts[0] if path.is_relative_to(ROOT) else ""
    if not repo_keywords.search(str(path)):
        continue

    try:
        text = path.read_text(errors="ignore")
    except Exception:
        continue

    hits = file_keywords.findall(text)
    if not hits:
        continue

    score = 0
    score += 10 if path.suffix.lower() in {".pine", ".pinescript"} else 0
    score += 8 if "strategy(" in text.lower() else 0
    score += 6 if "indicator(" in text.lower() else 0
    score += 4 if "macd" in text.lower() else 0
    score += 3 if "buy" in text.lower() and "sell" in text.lower() else 0
    score += 2 if repo_keywords.search(repo_name) else 0

    lines = []
    for i, line in enumerate(text.splitlines(), start=1):
        if file_keywords.search(line):
            lines.append({"line": i, "text": line.strip()[:220]})
        if len(lines) >= 12:
            break

    candidates.append({
        "repo": repo_name,
        "path": str(path),
        "score": score,
        "suffix": path.suffix.lower(),
        "matches": lines,
    })

candidates.sort(key=lambda x: (-x["score"], x["path"]))

OUT_JSON.write_text(json.dumps({"candidates": candidates}, indent=2))

md = ["# Trading Strategy Candidates", "", f"TOTAL={len(candidates)}", ""]
for c in candidates[:80]:
    md.append(f"## score={c['score']} `{c['repo']}`")
    md.append(f"- path: `{c['path']}`")
    for m in c["matches"][:6]:
        md.append(f"  - L{m['line']}: {m['text']}")
    md.append("")

OUT_MD.write_text("\n".join(md))

print(f"CANDIDATES={len(candidates)}")
print(f"JSON={OUT_JSON}")
print(f"MD={OUT_MD}")
