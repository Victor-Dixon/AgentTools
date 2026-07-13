#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HEALTH = Path(
    "data/reports/projectscanner/repo_health/latest.json"
)

PROMOTION = Path(
    "data/reports/projectscanner/promotion_recommendations/latest.json"
)

AUTHORITY = Path(
    "data/reports/projectscanner/cloud_authority_graph/latest.json"
)

OUT_MD = Path(
    "data/reports/discord/projectscanner/latest_projectscanner_intelligence_cards.md"
)

OUT_JSON = Path(
    "data/reports/discord/projectscanner/latest_projectscanner_intelligence_cards.json"
)

def load(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8")
    )

def main() -> int:
    health = load(HEALTH)
    promotion = load(PROMOTION)
    authority = load(AUTHORITY)

    top_health = sorted(
        health.get("scored_repos", []),
        key=lambda x: x["score"],
        reverse=True,
    )[:5]

    promo = promotion.get(
        "recommendations",
        []
    )[:5]

    authority_domains = authority.get(
        "authority_domains",
        {}
    )

    cards = {
        "top_health": top_health,
        "promotion": promo,
        "authority_domains": authority_domains,
    }

    OUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUT_JSON.write_text(
        json.dumps(cards, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# ProjectScanner Intelligence Cards",
        "",
        "## Repo Health Leaders",
        "",
    ]

    for repo in top_health:
        lines += [
            f"### {repo['repo']}",
            f"- score: {repo['score']}",
            f"- duplicate_pressure: {repo['duplicate_pressure']}",
            f"- language: {repo['language']}",
            "",
        ]

    lines += [
        "## Promotion Recommendations",
        "",
    ]

    for repo in promo:
        lines += [
            f"### {repo['repo']}",
            f"- recommendation: {repo['recommendation']}",
            f"- authority: {repo['authority']}",
            f"- score: {repo['score']}",
            "",
        ]

    lines += [
        "## Authority Domains",
        "",
    ]

    for domain, repos in sorted(
        authority_domains.items()
    ):
        lines.append(f"### {domain}")

        for repo in repos[:5]:
            lines.append(
                f"- {repo['repo']} "
                f"(score={repo['score']})"
            )

        lines.append("")

    OUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        "PROJECTSCANNER_DISCORD_INTELLIGENCE_CARDS=PASS"
    )
    print(f"CARDS={len(top_health)}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
