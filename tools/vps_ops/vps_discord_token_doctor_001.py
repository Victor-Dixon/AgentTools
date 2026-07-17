from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

SECRET_ROOT = Path(os.environ.get("DREAMOS_SECRETS_DIR", str(Path.home() / "secrets")))
TARGET = SECRET_ROOT / os.environ.get("DISCORD_FLEET_ENV_FILE", "discord-fleet.env")

TOKEN_HINTS = {
    "DISCORD_BOT_TOKEN",
    "DREAMOSARCHITECT_BOT_TOKEN",
    "DREAMOS_ARCHITECT_BOT_TOKEN",
    "ARCHITECT_BOT_TOKEN",
    "DISCORD_ARCHITECT_BOT_TOKEN",
    "COMMANDER_BOT_TOKEN",
    "DISCORD_COMMANDER_BOT_TOKEN",
    "DREAMOS_COMMANDER_BOT_TOKEN",
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return values

    for raw in text.splitlines():
        line = raw.strip().rstrip("\r")

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip().strip("\"'")

        if value:
            values[key.strip()] = value

    return values


def verify(token: str) -> tuple[int, dict]:
    request = urllib.request.Request(
        "https://discord.com/api/v10/users/@me",
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DreamOS-Discord-Token-Doctor/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = json.loads(
                response.read().decode("utf-8", errors="ignore")
            )
            return response.status, body if isinstance(body, dict) else {}
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except Exception:
        return 0, {}


candidates: list[tuple[Path, str, str]] = []
seen: set[str] = set()

# Include active files and archived backups while recovering credentials.
for path in sorted(SECRET_ROOT.rglob("*")):
    if not path.is_file():
        continue

    for key, value in load_env(path).items():
        upper = key.upper()

        token_like = (
            key in TOKEN_HINTS
            or ("DISCORD" in upper and "TOKEN" in upper)
            or ("ARCHITECT" in upper and "TOKEN" in upper)
            or ("COMMANDER" in upper and "TOKEN" in upper)
        )

        if token_like and value not in seen:
            seen.add(value)
            candidates.append((path, key, value))

print("VPS_DISCORD_TOKEN_VALIDITY_AUDIT")
print(f"CANDIDATES={len(candidates)}")

valid: list[tuple[Path, str, str, dict]] = []

for path, key, token in candidates:
    status, identity = verify(token)

    print(f"FILE={path.relative_to(SECRET_ROOT)}")
    print(f"KEY={key}")
    print(f"HTTP={status}")
    print(f"VALID={'true' if status == 200 else 'false'}")

    if status == 200:
        valid.append((path, key, token, identity))

print(f"VALID_TOKENS={len(valid)}")
print("SECRETS_PRINTED=0")

if not valid:
    raise SystemExit("STATUS=BLOCKED_NO_VALID_DISCORD_TOKEN")

architect = next(
    (item for item in valid if "ARCHITECT" in item[1].upper()),
    valid[0],
)

commander = next(
    (
        item
        for item in valid
        if "COMMANDER" in item[1].upper()
        or item[1] == "DISCORD_BOT_TOKEN"
    ),
    architect,
)

current = load_env(TARGET)
guild_id = current.get(
    "DISCORD_GUILD_ID",
    "1375298054357254257",
)

managed = {
    "DISCORD_GUILD_ID",
    "DISCORD_BOT_TOKEN",
    "DREAMOSARCHITECT_BOT_TOKEN",
}

preserved: list[str] = []

if TARGET.exists():
    for raw in TARGET.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).splitlines():
        stripped = raw.strip()

        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()

            if key in managed:
                continue

        preserved.append(raw.rstrip("\r"))

while preserved and not preserved[-1]:
    preserved.pop()

if preserved:
    preserved.append("")

preserved.extend(
    [
        f"DISCORD_GUILD_ID={guild_id}",
        f"DISCORD_BOT_TOKEN={commander[2]}",
        f"DREAMOSARCHITECT_BOT_TOKEN={architect[2]}",
    ]
)

TARGET.write_text(
    "\n".join(preserved) + "\n",
    encoding="utf-8",
)
os.chmod(TARGET, 0o600)

print("STATUS=PASS_VALID_DISCORD_TOKENS_CANONICALIZED")
print(f"ARCHITECT_SOURCE={architect[0].relative_to(SECRET_ROOT)}:{architect[1]}")
print(f"COMMANDER_SOURCE={commander[0].relative_to(SECRET_ROOT)}:{commander[1]}")
print("SECRETS_PRINTED=0")
