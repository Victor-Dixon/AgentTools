#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import json
import os
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

ROOT = Path.cwd()
SECRETS_DIR = ROOT / "runtime" / "secrets"
REPORT_DIR = ROOT / "data" / "reports" / "security" / "secret_broker"
TEMPLATE = SECRETS_DIR / "secrets.template.env"
LOCAL = SECRETS_DIR / "secrets.local.env"
INVENTORY = SECRETS_DIR / "secrets.inventory.json"

DEFAULT_TEMPLATE_KEYS = [
    "DISCORD_BOT_TOKEN",
    "DISCORD_APPLICATION_ID",
    "DISCORD_GUILD_ID",
    "DISCORD_TRADING_CHANNEL_ID",
    "DISCORD_TRADING_WEBHOOK_URL",
    "GEMINI_API_KEY",
    "GITHUB_PAT",
    "PYPI_API_TOKEN",
]


@dataclass(frozen=True)
class SecretWrite:
    key: str
    env_name: str
    file: str


def ensure_dirs() -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_gitignore() -> None:
    gitignore = ROOT / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    lines = existing.splitlines()
    required = ["runtime/secrets/*.env", "!runtime/secrets/*.template.env"]
    changed = False
    for line in required:
        if line not in lines:
            lines.append(line)
            changed = True
    if changed:
        gitignore.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def ensure_template() -> None:
    ensure_dirs()
    if not TEMPLATE.exists():
        TEMPLATE.write_text(
            "\n".join(f"export {key}=''" for key in DEFAULT_TEMPLATE_KEYS) + "\n",
            encoding="utf-8",
        )


def parse_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def write_env_file(path: Path, values: Dict[str, str]) -> None:
    ensure_dirs()
    text = "".join(f"export {key}='{value}'\n" for key, value in sorted(values.items()))
    path.write_text(text, encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def set_secret(key: str, value: str, env_file: Path = LOCAL) -> SecretWrite:
    if not key or not key.replace("_", "").replace(".", "").isalnum():
        raise ValueError(f"invalid secret key: {key!r}")
    env_name = key.upper().replace(".", "_")
    values = parse_env_file(env_file)
    values[env_name] = value
    write_env_file(env_file, values)
    update_inventory(env_name, env_file)
    return SecretWrite(key=key, env_name=env_name, file=str(env_file))


def update_inventory(env_name: str, env_file: Path) -> None:
    ensure_dirs()
    inv = {"secrets": {}}  # type: ignore[var-annotated]
    if INVENTORY.exists():
        try:
            inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            inv = {"secrets": {}}
    inv.setdefault("secrets", {})
    inv["secrets"][env_name] = {
        "env_file": str(env_file),
        "value_stored": True,
        "value_redacted": True,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }
    INVENTORY.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")


def init() -> None:
    ensure_dirs()
    ensure_gitignore()
    ensure_template()
    report = {
        "status": "PASS",
        "template": str(TEMPLATE),
        "local_env": str(LOCAL),
        "inventory": str(INVENTORY),
        "gitignore_guard": True,
        "secrets_redacted": True,
    }
    (REPORT_DIR / "latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("DREAM_SECRETS_INIT=PASS")
    print(f"TEMPLATE={TEMPLATE}")
    print(f"LOCAL_ENV={LOCAL}")
    print("SECRETS_REDACTED=TRUE")


def cmd_set(args: argparse.Namespace) -> None:
    value = args.value
    if value is None:
        value = getpass.getpass(f"{args.key}: ")
    result = set_secret(args.key, value)
    print("DREAM_SECRET_SET=PASS")
    print(f"KEY={result.env_name}")
    print(f"FILE={result.file}")
    print("VALUE_REDACTED=TRUE")


def cmd_export(args: argparse.Namespace) -> None:
    values = parse_env_file(Path(args.env_file))
    for key in sorted(values):
        print(f"export {key}='{values[key]}'")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dream.OS local env broker — loads secrets from gitignored runtime/secrets/*.env"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    p_set = sub.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("--value")

    p_export = sub.add_parser("export")
    p_export.add_argument("--env-file", default=str(LOCAL))

    args = parser.parse_args()
    if args.cmd == "init":
        init()
    elif args.cmd == "set":
        cmd_set(args)
    elif args.cmd == "export":
        cmd_export(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
