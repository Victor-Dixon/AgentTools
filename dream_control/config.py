"""Filesystem layout, operator config, and environment discovery."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_HOME = Path.home() / ".dreamos" / "control"

# Canonical VPS runtime node (see docs/DREAM_CONTROL_V1.md).
DEFAULT_VPS = {
    "host": "2.25.64.233",
    "user": "dreamos",
    "identity_file": "~/.ssh/hostinger_galaxy_ed25519",
    "runner_name": "dreamvault-vps-01",
    "runner_dir": "/home/dreamos/runners/dreamvault",
    "runner_labels": ["self-hosted", "Linux", "X64", "dreamvault-vps"],
    "brain_url": "",
}

# Repositories in the Dream.OS portfolio and the pillar each one owns.
DEFAULT_REPOS = {
    "DreamVault": {"owner": "Victor-Dixon", "pillar": "authority"},
    "projectscanner": {"owner": "Victor-Dixon", "pillar": "discovery"},
    "AgentTools": {"owner": "Victor-Dixon", "pillar": "execution"},
    "dreamos-brain": {"owner": "Victor-Dixon", "pillar": "control_plane"},
    "Dream.os-Core": {"owner": "Victor-Dixon", "pillar": "runtime"},
    "dream-data-vault": {"owner": "Victor-Dixon", "pillar": "data"},
}


def control_home() -> Path:
    """Root of the control-plane filesystem projection."""
    env = os.environ.get("DREAMOS_CONTROL_HOME")
    return Path(env).expanduser().resolve() if env else DEFAULT_HOME


@dataclass(frozen=True)
class Paths:
    home: Path

    @property
    def config(self) -> Path:
        return self.home / "config"

    @property
    def state(self) -> Path:
        return self.home / "state"

    @property
    def events(self) -> Path:
        return self.home / "events"

    @property
    def cache(self) -> Path:
        return self.home / "cache"

    @property
    def handoff(self) -> Path:
        return self.home / "handoff"

    @property
    def event_log(self) -> Path:
        return self.events / "events.jsonl"

    @property
    def operator_file(self) -> Path:
        return self.config / "operator.json"

    @property
    def environments_file(self) -> Path:
        return self.config / "environments.json"

    @property
    def policies_file(self) -> Path:
        return self.config / "policies.json"

    def ensure(self) -> Paths:
        for directory in (self.config, self.state, self.events, self.cache, self.handoff):
            directory.mkdir(parents=True, exist_ok=True)
        return self


def paths() -> Paths:
    return Paths(control_home())


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {} if default is None else default


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def detect_environment() -> str:
    """Best-effort identification of the machine the agent is running on."""
    if os.environ.get("DREAMOS_ENVIRONMENT"):
        return os.environ["DREAMOS_ENVIRONMENT"]
    prefix = os.environ.get("PREFIX", "")
    if "com.termux" in prefix or Path("/data/data/com.termux").exists():
        return "android_termux"
    if os.name == "nt":
        return "windows_desktop"
    if Path("/home/dreamos").exists() and os.environ.get("USER") == "dreamos":
        return "dreamos_vps"
    if os.environ.get("CLAUDE_CODE_SESSION") or os.environ.get("CLAUDECODE"):
        return "claude"
    return "linux"


def default_agent_id(environment: str | None = None) -> str:
    if os.environ.get("DREAMOS_AGENT_ID"):
        return os.environ["DREAMOS_AGENT_ID"]
    return f"{(environment or detect_environment())}_agent_001"


@dataclass
class OperatorConfig:
    """Durable operator contract: who is driving, and from where."""

    operator: str = "Victor"
    clipboard_command: str = "$HOME/bin/cliprun"
    projects_root: str = str(Path.home() / "projects")
    repos: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_REPOS))
    vps: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_VPS))
    notes: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, p: Paths | None = None) -> OperatorConfig:
        p = p or paths()
        data = read_json(p.operator_file, {})
        base = cls()
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(base, key) and value is not None:
                    setattr(base, key, value)
        # Never let a partial config drop the canonical VPS fields.
        merged_vps = dict(DEFAULT_VPS)
        merged_vps.update(base.vps or {})
        base.vps = merged_vps
        return base

    def save(self, p: Paths | None = None) -> Path:
        p = (p or paths()).ensure()
        return write_json(p.operator_file, self.__dict__)


def project_root_for(repo: str, config: OperatorConfig | None = None) -> Path | None:
    """Locate a portfolio repository checkout on this machine."""
    config = config or OperatorConfig.load()
    env_key = f"DREAMOS_REPO_{repo.upper().replace('-', '_').replace('.', '_')}"
    candidates = []
    if os.environ.get(env_key):
        candidates.append(Path(os.environ[env_key]))
    candidates += [
        Path(config.projects_root).expanduser() / repo,
        Path.home() / repo,
        Path.cwd() / repo,
    ]
    for candidate in candidates:
        try:
            if (candidate / ".git").exists():
                return candidate.resolve()
        except OSError:
            continue
    return None


def tool_available(name: str) -> bool:
    return shutil.which(name) is not None
