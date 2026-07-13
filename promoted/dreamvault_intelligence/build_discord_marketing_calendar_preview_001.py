from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

IN_JSON = Path("data/reports/marketing/launch_calendar_14_days.json")
OUT_JSON = Path("data/reports/marketing/discord_calendar/marketing_calendar_discord_payloads.json")
OUT_MD = Path("data/reports/marketing/discord_calendar/marketing_calendar_discord_preview.md")

MAX_FIELDS_PER_EMBED = 10


def load_calendar() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"calendar missing: {IN_JSON}")
    return json.loads(IN_JSON.read_text(encoding="utf-8"))


def build_payloads(calendar: dict) -> list[dict]:
    by_day: dict[int, list[dict]] = defaultdict(list)
    for post in calendar["posts"]:
        by_day[int(post["day"])].append(post)

    payloads = []
    for day in sorted(by_day):
        posts = by_day[day]
        date = posts[0]["date"]

        fields = []
        for post in posts[:MAX_FIELDS_PER_EMBED]:
            fields.append({
                "name": f"{post['platform']} · {post['type']}",
                "value": (
                    f"**{post['title']}**\n"
                    f"Hook: {post['hook']}\n"
                    f"Status: `{post['status']}`"
                )[:1024],
                "inline": False,
            })

        overflow = max(0, len(posts) - MAX_FIELDS_PER_EMBED)
        if overflow:
            fields.append({
                "name": "More",
                "value": f"{overflow} additional posts omitted from this card.",
                "inline": False,
            })

        payloads.append({
            "channel_hint": "marketing-calendar",
            "content": "",
            "embeds": [
                {
                    "title": f"DreamOS.ai / freerideinvestor · Launch Calendar · Day {day}",
                    "description": (
                        f"Date: `{date}`\n"
                        f"Policy: manual approval before live posting. No fake engagement. No mass DMs."
                    ),
                    "fields": fields,
                    "footer": {
                        "text": "Generated from posting_calendar_001 · preview only"
                    },
                }
            ],
        })

    return payloads


def render_md(calendar: dict, payloads: list[dict]) -> str:
    lines = [
        "# Discord Marketing Calendar Preview",
        "",
        f"STATUS={calendar['status']}",
        f"BRAND_ACCOUNT={calendar['brand_account']}",
        f"SHOW_NAME={calendar['show_name']}",
        f"DURATION_DAYS={calendar['duration_days']}",
        f"POST_COUNT={calendar['post_count']}",
        f"DISCORD_CARD_COUNT={len(payloads)}",
        "",
        "## Suggested Discord Channel",
        "",
        "`#marketing-calendar`",
        "",
        "## Cards",
        "",
    ]

    for payload in payloads:
        embed = payload["embeds"][0]
        lines.append(f"### {embed['title']}")
        lines.append("")
        lines.append(embed["description"])
        lines.append("")
        for field in embed["fields"]:
            lines.append(f"- **{field['name']}** — {field['value'].replace(chr(10), ' / ')}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    calendar = load_calendar()
    payloads = build_payloads(calendar)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "status": "READY",
        "source": str(IN_JSON),
        "channel_hint": "marketing-calendar",
        "payload_count": len(payloads),
        "payloads": payloads,
    }, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(calendar, payloads), encoding="utf-8")

    print("DISCORD_MARKETING_CALENDAR=READY")
    print("CHANNEL_HINT=marketing-calendar")
    print(f"PAYLOAD_COUNT={len(payloads)}")


if __name__ == "__main__":
    main()
