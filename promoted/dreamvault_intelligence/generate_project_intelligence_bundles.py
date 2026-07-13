#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SCAN_JSON = Path("data/reports/projectscanner/ecosystem_scan_001/projects_scan.json")
OUT_ROOT = Path("data/intelligence/repos")
REPORT = Path("data/reports/projectscanner/ecosystem_scan_001/intelligence_bundle_report.md")

DOC_KEYS = ["readme", "prd", "roadmap", "master_task_list", "next_up"]

ROLE_HINTS = {
    "DreamOS": "canonical runtime",
    "DreamVault": "governance memory and reporting spine",
    "AgentTools": "toolbelt adapters and operator surfaces",
    "projectscanner": "repo intelligence scanner",
    "DreamTradeData": "raw market data capture repo",
    "FreerideinvestorWebsite": "FreeRideInvestor web/theme consolidation source",
    "FreeRideInvestor": "product/business repo",
}

SPECIAL_NOTES = {
    "Dream.os-Core": "Mirror of DreamOS at same HEAD during inventory pass. Treat as duplicate/mirror, not salvage source unless new divergence appears.",
    "FreerideinvestorWebsite": "Contains substantial variant-only website/theme assets. Do not delete. Requires promotion manifest into FreeRideInvestor.",
    "DreamTradeData": "Git exists but HEAD unavailable during inventory. Raw untracked data repo; needs data governance before docs work.",
}

def safe_name(name: str) -> str:
    return name.replace("/", "_")

def missing_docs(markers: dict) -> list[str]:
    return [k for k in DOC_KEYS if not markers.get(k)]

def docs_score(markers: dict) -> int:
    present = sum(1 for k in DOC_KEYS if markers.get(k))
    return round((present / len(DOC_KEYS)) * 100)

def recommendation(project: dict) -> dict:
    name = project["name"]
    markers = project.get("markers", {})
    missing = missing_docs(markers)
    dirty = bool(project.get("git_status_short"))

    actions = []
    risk = "low"

    if missing:
        actions.append("docs_refresh")
    if "prd" in missing or "roadmap" in missing:
        actions.append("prd_roadmap_alignment")
    if "master_task_list" in missing or "next_up" in missing:
        actions.append("operator_governance_docs")
    if dirty:
        actions.append("dirty_state_review")
        risk = "medium"
    if name in SPECIAL_NOTES:
        actions.append("special_handling")
        risk = "medium"

    if name == "DreamTradeData":
        risk = "high"
        actions.append("data_repo_governance")

    return {
        "repo": name,
        "risk": risk,
        "recommended_next_classes": actions or ["no_docs_gap_detected"],
        "missing_docs": missing,
        "notes": SPECIAL_NOTES.get(name, ""),
    }

def main() -> int:
    scan = json.loads(SCAN_JSON.read_text())
    projects = scan["projects"]
    generated = datetime.now(timezone.utc).isoformat()

    rows = []

    for project in projects:
        name = project["name"]
        out_dir = OUT_ROOT / safe_name(name)
        out_dir.mkdir(parents=True, exist_ok=True)

        markers = project.get("markers", {})
        rec = recommendation(project)

        analysis = {
            "generated": generated,
            "repo": name,
            "role_hint": ROLE_HINTS.get(name, "unclassified project"),
            "path": project.get("path"),
            "is_git": project.get("is_git"),
            "branch": project.get("branch"),
            "head": project.get("head"),
            "dirty": bool(project.get("git_status_short")),
            "git_status_short": project.get("git_status_short", []),
            "file_count": project.get("file_count"),
            "dir_count": project.get("dir_count"),
            "top_level": project.get("top_level", []),
            "docs_markers": markers,
            "docs_score": docs_score(markers),
            "missing_docs": missing_docs(markers),
            "cleanup_registry": project.get("cleanup_registry", {}),
            "special_note": SPECIAL_NOTES.get(name, ""),
        }

        chatgpt_context = {
            "repo": name,
            "role_hint": analysis["role_hint"],
            "current_state": {
                "branch": analysis["branch"],
                "head": analysis["head"],
                "dirty": analysis["dirty"],
                "file_count": analysis["file_count"],
                "docs_score": analysis["docs_score"],
                "missing_docs": analysis["missing_docs"],
            },
            "operator_guidance": {
                "safe_next_action": rec["recommended_next_classes"][0],
                "guardrails": [
                    "Do not perform destructive cleanup without a promotion manifest.",
                    "Do not repeat completed inventory cleanup classes.",
                    "Use repo-local tests or file existence checks as verification gates.",
                    "Commit only scoped artifacts per lane.",
                ],
            },
            "special_note": analysis["special_note"],
            "source_artifacts": {
                "ecosystem_scan": str(SCAN_JSON),
                "cleanup_registry": "data/registry/cleanup_progress.json",
                "campaign_status": "data/reports/cleanup/CAMPAIGN_STATUS.md",
            },
        }

        docs_gap_lines = [
            f"# {name} Docs Gap Report",
            "",
            f"- Generated: {generated}",
            f"- Docs score: {analysis['docs_score']}",
            "",
            "## Present Docs",
            "",
        ]
        for key in DOC_KEYS:
            docs_gap_lines.append(f"- {key}: {'yes' if markers.get(key) else 'no'}")
        docs_gap_lines.extend(["", "## Missing Docs", ""])
        if analysis["missing_docs"]:
            docs_gap_lines.extend(f"- {x}" for x in analysis["missing_docs"])
        else:
            docs_gap_lines.append("- none")
        docs_gap_lines.extend(["", "DOCS_GAP_REPORT=PASS", ""])

        (out_dir / "repo_analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
        (out_dir / "chatgpt_context.json").write_text(json.dumps(chatgpt_context, indent=2, sort_keys=True) + "\n")
        (out_dir / "cleanup_recommendations.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        (out_dir / "docs_gap_report.md").write_text("\n".join(docs_gap_lines))

        rows.append((name, analysis["docs_score"], len(analysis["missing_docs"]), rec["risk"], ", ".join(rec["recommended_next_classes"])))

    lines = [
        "# Project Intelligence Bundle Report",
        "",
        f"- Generated: {generated}",
        f"- Projects: {len(projects)}",
        f"- Output root: `{OUT_ROOT}`",
        "",
        "| Repo | Docs Score | Missing Docs | Risk | Recommended Classes |",
        "|---|---:|---:|---|---|",
    ]

    for name, score, missing_count, risk, actions in rows:
        lines.append(f"| {name} | {score} | {missing_count} | {risk} | {actions} |")

    lines.extend(["", "PROJECT_INTELLIGENCE_BUNDLES=PASS", ""])
    REPORT.write_text("\n".join(lines))

    print("PROJECT_INTELLIGENCE_BUNDLES=PASS")
    print(f"PROJECTS={len(projects)}")
    print(f"OUT_ROOT={OUT_ROOT}")
    print(f"REPORT={REPORT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
