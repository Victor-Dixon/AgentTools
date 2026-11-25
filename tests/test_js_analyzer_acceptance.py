"""Real installed analyzer acceptance, explicitly enabled by dedicated CI."""
import os
import subprocess
import json

import pytest

from mcp_servers.code_quality_server import find_dead_code

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENTTOOLS_JS_ANALYZER_ACCEPTANCE") != "1",
    reason="requires pinned npm analyzer dependencies",
)


@pytest.mark.parametrize("tool,version", [("ts-prune", "0.10.3"), ("knip", "5.46.0")])
def test_real_analyzer(tmp_path, tool, version):
    (tmp_path / "package.json").write_text(json.dumps({"name": "analyzer-fixture", "version": "1.0.0", "private": True}))
    (tmp_path / "tsconfig.json").write_text(json.dumps({"compilerOptions": {"target": "ES2020", "module": "commonjs"}, "include": ["src/**/*.ts"]}))
    src = tmp_path / "src"
    src.mkdir()
    (src / "index.ts").write_text("import { used } from './lib';\nconsole.log(used());\n")
    (src / "lib.ts").write_text("export function used() { return 1; }\nexport function unused() { return 2; }\n")
    (tmp_path / "knip.json").write_text(json.dumps({"entry": ["src/index.ts"], "project": ["src/**/*.ts"]}))
    subprocess.run(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund", "--save-dev", f"{tool}@{version}", "typescript@5.7.3"], cwd=tmp_path, check=True, timeout=180)
    result = find_dead_code(str(tmp_path), language="typescript")
    assert result["success"], result
    assert result["tool"] == tool, result
    names = [entry.get("export") or (entry.get("item", {}).get("name") if isinstance(entry.get("item"), dict) else None) for entry in result["dead_code"]]
    assert "unused" in names, result
    assert "used" not in names, result
    print(f"REAL_ANALYZER_PASS={tool} findings={result['total']}")
