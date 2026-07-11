from __future__ import annotations

from pathlib import Path

from agent_tools.discord_commander.commands.prompt_library_commands import (
    list_prompt_domains,
    prompt_next_steps,
    prompt_search,
    show_prompt,
)


def _write_dreamvault_fixture(root: Path) -> None:
    prompts = root / "runtime" / "prompts"
    for domain in ("closeout", "discord", "swarm"):
        (prompts / domain).mkdir(parents=True, exist_ok=True)
    (prompts / "closeout" / "default.md").write_text(
        "# Closeout\nGenerated {generated}\n",
        encoding="utf-8",
    )
    (prompts / "discord" / "default.md").write_text(
        "# Discord\nNext {next_target}\n",
        encoding="utf-8",
    )
    (prompts / "swarm" / "default.md").write_text(
        "# Swarm\nRoute to closeout\n",
        encoding="utf-8",
    )
    (prompts / "token_registry.yaml").write_text("version: 1\ntokens: {}\n", encoding="utf-8")
    (prompts / "workflow_graph.yaml").write_text(
        "version: 1\nnodes:\n  closeout:\n    next: [discord]\n  discord:\n    next: [swarm]\n  swarm:\n    next: [closeout]\n",
        encoding="utf-8",
    )
    (root / "NEXT_UP.md").write_text("next lane here\n", encoding="utf-8")
    package_root = root / "src" / "dreamvault" / "prompts"
    package_root.mkdir(parents=True, exist_ok=True)
    (root / "src" / "dreamvault" / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "token_resolver.py").write_text(
        """
from pathlib import Path


class PromptRenderResult:
    def __init__(self, domain, source_path, rendered, tokens, unavailable_tokens):
        self.domain = domain
        self.source_path = source_path
        self.rendered = rendered
        self.tokens = tokens
        self.unavailable_tokens = unavailable_tokens


class PromptTokenResolver:
    def __init__(self, dreamvault_root):
        self.dreamvault_root = Path(dreamvault_root)

    def prompt_roots(self):
        return [self.dreamvault_root / "runtime" / "prompts"]

    def list_domains(self):
        return sorted(path.name for path in self.prompt_roots()[0].iterdir() if path.is_dir())

    def prompt_source(self, domain, filename="default.md"):
        path = self.prompt_roots()[0] / domain / filename
        return {"domain": domain, "filename": filename, "source_root": "DreamVault", "path": str(path)}

    def load_prompt(self, domain, filename="default.md"):
        return (self.prompt_roots()[0] / domain / filename).read_text(encoding="utf-8")

    def render_prompt(self, domain, filename="default.md"):
        body = self.load_prompt(domain, filename).replace("{next_target}", "next lane here").replace("{generated}", "2026-07-03T20:00:00+00:00")
        return PromptRenderResult(domain, self.prompt_roots()[0] / domain / filename, body, {}, [])

    def next_domains(self, domain):
        mapping = {"closeout": ["discord"], "discord": ["swarm"], "swarm": ["closeout"]}
        return mapping.get(domain, [])

    def search(self, query):
        query = query.lower()
        rows = []
        for domain in self.list_domains():
            body = self.load_prompt(domain).lower()
            if query in domain.lower() or query in body:
                rows.append(
                    {
                        "domain": domain,
                        "title": domain.title(),
                        "source_root": "DreamVault",
                        "path": str(self.prompt_roots()[0] / domain / "default.md"),
                    }
                )
        return rows
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_list_prompt_domains_reads_governed_roots(tmp_path):
    _write_dreamvault_fixture(tmp_path)

    payload = list_prompt_domains(tmp_path)

    assert payload["dreamvault_root"] == str(tmp_path)
    assert payload["domains"] == ["closeout", "discord", "swarm"]


def test_show_prompt_render_resolves_tokens(tmp_path):
    _write_dreamvault_fixture(tmp_path)

    payload = show_prompt("discord", rendered=True, root=tmp_path)

    assert payload["domain"] == "discord"
    assert "next lane here" in payload["body"]
    assert payload["unavailable_tokens"] == []


def test_prompt_search_matches_domain_and_content(tmp_path):
    _write_dreamvault_fixture(tmp_path)

    rows = prompt_search("closeout", tmp_path)

    assert rows
    assert rows[0]["domain"] == "closeout"


def test_prompt_next_steps_reads_workflow_graph(tmp_path):
    _write_dreamvault_fixture(tmp_path)

    payload = prompt_next_steps("closeout", tmp_path)

    assert payload["next"] == ["discord"]
