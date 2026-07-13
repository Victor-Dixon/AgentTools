#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

try:
    import yaml
except Exception as exc:
    raise SystemExit(f"Missing PyYAML: {exc}")

CONTRACT = Path("runtime/contracts/capabilities/capability_unlock_intelligence.v1.yaml")
OUT_JSON = Path("data/reports/capabilities/latest_capability_unlocks.json")
OUT_MD = Path("data/reports/capabilities/latest_capability_unlocks.md")
DISCORD_MD = Path("data/reports/discord/capability_unlocks/latest_capability_unlock_card.md")


def git_log(limit: int = 12) -> list[str]:
    out = subprocess.check_output(
        ["git", "log", "--oneline", f"-{limit}"],
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def classify(commit_line: str, domains: dict) -> list[str]:
    lower = commit_line.lower()
    hits = []
    for domain, cfg in domains.items():
        if any(k.lower() in lower for k in cfg.get("keywords", [])):
            hits.append(domain)
    return hits or ["general"]


def capability_text(domain: str) -> str:
    return {
        "planner": "Planner can make stronger next-lane decisions with runtime proof awareness.",
        "authority": "Dream.OS can reduce duplicate truths and choose canonical operational sources.",
        "context": "Agents can receive compressed, authority-filtered operational context.",
        "agents": "Dream.OS can route work to external agents with safer delegation packets.",
        "trading": "Trading workflows gained stronger journaling, replay, or cockpit support.",
        "governance": "Runtime governance can classify, suppress, or decay operational entropy.",
        "general": "System capability increased through committed runtime changes.",
    }.get(domain, "System capability increased.")


def build_payload() -> dict:
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    commits = git_log()

    unlocks = []
    seen = set()

    for line in commits:
        domains = classify(line, contract["capability_domains"])
        for domain in domains:
            key = (domain, line)
            if key in seen:
                continue
            seen.add(key)
            unlocks.append(
                {
                    "domain": domain,
                    "commit": line,
                    "capability": capability_text(domain),
                }
            )

    return {
        "commit_count": len(commits),
        "unlock_count": len(unlocks),
        "unlocks": unlocks,
    }


def render_md(payload: dict) -> str:
    lines = [
        "# Capability Unlock Intelligence",
        "",
        f"commit_count: {payload['commit_count']}",
        f"unlock_count: {payload['unlock_count']}",
        "",
    ]

    for item in payload["unlocks"]:
        lines += [
            f"## {item['domain']}",
            f"- commit: `{item['commit']}`",
            f"- unlock: {item['capability']}",
            "",
        ]

    return "\n".join(lines)


def render_discord(payload: dict) -> str:
    top = payload["unlocks"][:8]

    lines = [
        "🧠 DREAM.OS CAPABILITY UNLOCKS",
        "",
        f"Commits reviewed: {payload['commit_count']}",
        f"Unlocks detected: {payload['unlock_count']}",
        "",
        "Unlocked:",
    ]

    for item in top:
        lines.append(f"- **{item['domain']}** — {item['capability']}")

    lines += [
        "",
        "Operator meaning:",
        "Dream.OS is learning to convert commits into capability state, not just file changes.",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_payload()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DISCORD_MD.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    DISCORD_MD.write_text(render_discord(payload), encoding="utf-8")

    print("CAPABILITY_UNLOCK_INTELLIGENCE=PASS")
    print(f"COMMITS={payload['commit_count']}")
    print(f"UNLOCKS={payload['unlock_count']}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"DISCORD={DISCORD_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
