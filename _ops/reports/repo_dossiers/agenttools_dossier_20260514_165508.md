# AgentTools Repository Dossier

Generated: 2026-05-14T16:55:08-05:00

## Repository Identity

- Repo: AgentTools
- Role: Dream.OS toolbelt and operator surface layer

## Verified Top-Level Structure

```text
.cursor
.env.example
.git
.github
.gitignore
.pytest_cache
AGENTS.md
BRANCH_CLEANUP_STATUS.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
MASTER_TASK_LIST.md
MASTER_TASK_LOG.md
MISSION_BRIEF_FIRST_CONTACT.md
NEXT_UP.md
PHASE_0A_ORGANIZATION_PLAN.md
PRD.md
PRODUCTION_READINESS.md
PROJECT_STRUCTURE_TREE.md
QUICK_START_PHASE0A.md
README.md
ROADMAP.md
__pycache__
_ops
apps
check_v2_compliance.py
dependencies.json
docker-compose.yml
docs
dreamvault_closeout_bridge.py
examples
find_exact_dupes.py
generate_tools_report.py
integration
mcp_servers
node_modules
pack_messages
package-lock.json
package.json
packages
passdown.json
pyproject.toml
pytest.ini
scripts
src
start_swarm.py
swarm_brain
swarm_mcp
tests
tools
tools_inventory.json
tools_v2
tsconfig.base.json
```

## Tooling Signals

```text
./.cursor/mcp.json
./__pycache__/dreamvault_closeout_bridge.cpython-313.pyc
./_ops/decisions/0001-agenttools-boundary.md
./apps/api/package.json
./apps/api/tsconfig.json
./docs/LEGACY_TOOL_MIGRATION_MATRIX.json
./docs/LEGACY_TOOL_MIGRATION_MATRIX.md
./docs/MCP_TOOLS_ROADMAP.md
./docs/TOOLBELT_SURFACE_AUDIT.json
./docs/TOOLBELT_SURFACE_AUDIT.md
./docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md
./docs/TOOL_SURFACES_AND_OVERLAP.md
./docs/root/DUPLICATE_TOOLS_REPORT.md
./docs/root/TOOLBELT_UNIFICATION_PLAN.md
./docs/root/TOOLS_CONSOLIDATION_PLAN.md
./docs/root/TOOLS_FLATTENING_PLAN.md
./docs/root/TOOLS_RANKING_REPORT.md
./docs/root/TOOLS_USAGE_GUIDE.md
./dreamvault_closeout_bridge.py
./examples/verify_all_tools.py
./generate_tools_report.py
./integration/swarm_mcp_server.py
./mcp_servers/GIT_OPERATIONS_README.md
./mcp_servers/MCP_TOOLS_ANALYSIS.md
./mcp_servers/README.md
./mcp_servers/SWARM_BRAIN_README.md
./mcp_servers/TASK_MANAGER_README.md
./mcp_servers/V2_COMPLIANCE_README.md
./mcp_servers/WEBSITE_MANAGER_README.md
./mcp_servers/__init__.py
./mcp_servers/all_mcp_servers.json
./mcp_servers/backup_automation_server.py
./mcp_servers/cicd_helper_server.py
./mcp_servers/code_quality_server.py
./mcp_servers/database_operations_server.py
./mcp_servers/dependency_management_server.py
./mcp_servers/discord_integration_server.py
./mcp_servers/documentation_generator_server.py
./mcp_servers/environment_setup_server.py
./mcp_servers/git_operations_server.py
./mcp_servers/issue_todo_tracker_server.py
./mcp_servers/memory_safety_server.py
./mcp_servers/messaging_server.py
./mcp_servers/mission_control_server.py
./mcp_servers/mod_deployment_server.py
./mcp_servers/observability_server.py
./mcp_servers/performance_profiler_server.py
./mcp_servers/player_analytics_server.py
./mcp_servers/refactoring_server.py
./mcp_servers/release_management_server.py
./mcp_servers/security_scanner_server.py
./mcp_servers/server_monitoring_server.py
./mcp_servers/swarm_brain_server.py
./mcp_servers/task_manager_server.py
./mcp_servers/testing_server.py
./mcp_servers/v2_compliance_server.py
./mcp_servers/website_audit_server.py
./mcp_servers/website_manager_server.py
./node_modules/next/server.d.ts
./node_modules/next/server.js
./node_modules/postcss-selector-parser/API.md
./node_modules/react-dom/client.react-server.js
./node_modules/react-dom/profiling.react-server.js
./node_modules/react-dom/react-dom.react-server.js
./node_modules/react-dom/server.browser.js
./node_modules/react-dom/server.bun.js
./node_modules/react-dom/server.edge.js
./node_modules/react-dom/server.js
./node_modules/react-dom/server.node.js
./node_modules/react-dom/server.react-server.js
./node_modules/react-dom/static.react-server.js
./node_modules/react/jsx-dev-runtime.react-server.js
./node_modules/react/jsx-runtime.react-server.js
./node_modules/react/react.react-server.js
./node_modules/socket.io-adapter/LICENSE
./node_modules/socket.io-adapter/Readme.md
./node_modules/socket.io-adapter/package.json
./node_modules/undici-types/api.d.ts
./scripts/audit_toolbelt_surfaces.py
./scripts/build_legacy_tool_migration_matrix.py
./scripts/quarantine_broken_tools_v2_registry_entries.py
./swarm_mcp/__init__.py
./swarm_mcp/__pycache__/__init__.cpython-313.pyc
./swarm_mcp/cli.py
./swarm_mcp/core/__init__.py
./swarm_mcp/core/agent_dna.py
./swarm_mcp/core/brain.py
./swarm_mcp/core/conflict.py
./swarm_mcp/core/consensus.py
./swarm_mcp/core/coordinator.py
./swarm_mcp/core/memory.py
./swarm_mcp/core/messaging.py
./swarm_mcp/core/messaging_templates.py
./swarm_mcp/core/pattern_miner.py
./swarm_mcp/core/recovery.py
./swarm_mcp/core/task_scoring.py
./swarm_mcp/core/verification.py
./swarm_mcp/core/work_proof.py
./swarm_mcp/servers/__init__.py
./swarm_mcp/servers/control.py
./swarm_mcp/servers/memory.py
./swarm_mcp/servers/messaging.py
./swarm_mcp/servers/tasks.py
./swarm_mcp/servers/tools.py
./swarm_mcp/tools/__init__.py
./tests/__pycache__/test_dreamvault_closeout_bridge.cpython-313-pytest-9.0.3.pyc
./tests/__pycache__/test_legacy_tool_migration_matrix.cpython-313-pytest-9.0.3.pyc
./tests/__pycache__/test_mcp_servers.cpython-313-pytest-9.0.3.pyc
./tests/__pycache__/test_toolbelt.cpython-313-pytest-9.0.3.pyc
./tests/__pycache__/test_toolbelt_surface_audit.cpython-313-pytest-9.0.3.pyc
./tests/__pycache__/test_tools_v2_registry_contract.cpython-313-pytest-9.0.3.pyc
./tests/__pycache__/test_tools_v2_safe_execution_contract.cpython-313-pytest-9.0.3.pyc
./tests/compat/test_agenttools_bus_message_adapter_contract.py
./tests/compat/test_agenttools_tool_adapter_characterization.py
./tests/test_legacy_tool_migration_matrix.py
./tests/test_mcp_servers.py
./tests/test_toolbelt.py
./tests/test_toolbelt_surface_audit.py
./tests/test_tools_v2_registry_contract.py
./tests/test_tools_v2_safe_execution_contract.py
```

## Runtime / App Signals

```text
./node_modules/abstract-logging/package.json
./node_modules/accepts/package.json
./node_modules/ajv-formats/package.json
./node_modules/ajv/package.json
./node_modules/any-promise/package.json
./node_modules/anymatch/package.json
./node_modules/arg/package.json
./node_modules/assertion-error/package.json
./node_modules/atomic-sleep/package.json
./node_modules/autoprefixer/package.json
./node_modules/avvio/package.json
./node_modules/base64id/package.json
./node_modules/baseline-browser-mapping/package.json
./node_modules/binary-extensions/package.json
./node_modules/braces/package.json
./node_modules/browserslist/package.json
./node_modules/camelcase-css/package.json
./node_modules/caniuse-lite/package.json
./node_modules/chai/package.json
./node_modules/client-only/package.json
./node_modules/commander/package.json
./node_modules/convert-source-map/package.json
./node_modules/cookie/package.json
./node_modules/cssesc/package.json
./node_modules/csstype/package.json
./node_modules/debug/package.json
./node_modules/dequal/package.json
./node_modules/detect-libc/package.json
./node_modules/didyoumean/package.json
./node_modules/dlv/package.json
./node_modules/dotenv/package.json
./node_modules/electron-to-chromium/package.json
./node_modules/engine.io-parser/package.json
./node_modules/es-module-lexer/package.json
./node_modules/esbuild/package.json
./node_modules/escalade/package.json
./node_modules/estree-walker/package.json
./node_modules/expect-type/package.json
./node_modules/fast-decode-uri-component/package.json
./node_modules/fast-deep-equal/package.json
./node_modules/fast-json-stringify/package.json
./node_modules/fast-querystring/package.json
./node_modules/fast-uri/package.json
./node_modules/fastify-plugin/package.json
./node_modules/fastify/package.json
./node_modules/fastq/package.json
./node_modules/fill-range/package.json
./node_modules/find-my-way/package.json
./node_modules/fraction.js/package.json
./node_modules/function-bind/package.json
./node_modules/get-tsconfig/package.json
./node_modules/glob-parent/package.json
./node_modules/hasown/package.json
./node_modules/ipaddr.js/package.json
./node_modules/is-binary-path/package.json
./node_modules/is-core-module/package.json
./node_modules/is-extglob/package.json
./node_modules/is-glob/package.json
./node_modules/is-number/package.json
./node_modules/jiti/package.json
./node_modules/json-schema-ref-resolver/package.json
./node_modules/json-schema-traverse/package.json
./node_modules/lightningcss-android-arm64/package.json
./node_modules/lightningcss/package.json
./node_modules/lilconfig/package.json
./node_modules/lines-and-columns/package.json
./node_modules/magic-string/package.json
./node_modules/merge2/package.json
./node_modules/micromatch/package.json
./node_modules/mime-db/package.json
./node_modules/mime-types/package.json
./node_modules/mnemonist/package.json
./node_modules/ms/package.json
./node_modules/mz/package.json
./node_modules/nanoid/package.json
./node_modules/negotiator/package.json
./node_modules/node-releases/package.json
./node_modules/normalize-path/package.json
./node_modules/object-assign/package.json
./node_modules/object-hash/package.json
./node_modules/obliterator/package.json
./node_modules/obug/package.json
./node_modules/on-exit-leak-free/package.json
./node_modules/path-parse/package.json
./node_modules/pathe/package.json
./node_modules/pg-cloudflare/package.json
./node_modules/pg-connection-string/package.json
./node_modules/pg-int8/package.json
./node_modules/pg-pool/package.json
./node_modules/pg-protocol/package.json
./node_modules/pg-types/package.json
./node_modules/pg/package.json
./node_modules/pgpass/package.json
./node_modules/picocolors/package.json
./node_modules/picomatch/package.json
./node_modules/pify/package.json
./node_modules/pino-abstract-transport/package.json
./node_modules/pino-std-serializers/package.json
./node_modules/pino/package.json
./node_modules/pirates/package.json
./node_modules/postcss-import/package.json
./node_modules/postcss-js/package.json
./node_modules/postcss-load-config/package.json
./node_modules/postcss-nested/package.json
./node_modules/postcss-selector-parser/package.json
./node_modules/postcss-value-parser/package.json
./node_modules/postcss/package.json
./node_modules/postgres-array/package.json
./node_modules/postgres-bytea/package.json
./node_modules/postgres-date/package.json
./node_modules/postgres-interval/package.json
./node_modules/process-warning/package.json
./node_modules/queue-microtask/package.json
./node_modules/quick-format-unescaped/package.json
./node_modules/react-dom/package.json
./node_modules/react/package.json
./node_modules/read-cache/package.json
./node_modules/readdirp/package.json
./node_modules/real-require/package.json
./node_modules/require-from-string/package.json
```

## Frontend / Dashboard Signals

```text
./node_modules/@alloc/quick-lru/index.d.ts
./node_modules/@alloc/quick-lru/index.js
./node_modules/@alloc/quick-lru/license
./node_modules/@alloc/quick-lru/package.json
./node_modules/@alloc/quick-lru/readme.md
./node_modules/@esbuild/android-arm64/README.md
./node_modules/@esbuild/android-arm64/package.json
./node_modules/@next/env/README.md
./node_modules/@next/env/package.json
./node_modules/@types/react-dom/LICENSE
./node_modules/@types/react-dom/README.md
./node_modules/@types/react-dom/canary.d.ts
./node_modules/@types/react-dom/client.d.ts
./node_modules/@types/react-dom/experimental.d.ts
./node_modules/@types/react-dom/index.d.ts
./node_modules/@types/react-dom/package.json
./node_modules/@types/react-dom/server.browser.d.ts
./node_modules/@types/react-dom/server.bun.d.ts
./node_modules/@types/react-dom/server.d.ts
./node_modules/@types/react-dom/server.edge.d.ts
./node_modules/@types/react-dom/server.node.d.ts
./node_modules/@types/react-dom/static.browser.d.ts
./node_modules/@types/react-dom/static.d.ts
./node_modules/@types/react-dom/static.edge.d.ts
./node_modules/@types/react-dom/static.node.d.ts
./node_modules/@types/react/LICENSE
./node_modules/@types/react/README.md
./node_modules/@types/react/canary.d.ts
./node_modules/@types/react/compiler-runtime.d.ts
./node_modules/@types/react/experimental.d.ts
./node_modules/@types/react/global.d.ts
./node_modules/@types/react/index.d.ts
./node_modules/@types/react/jsx-dev-runtime.d.ts
./node_modules/@types/react/jsx-runtime.d.ts
./node_modules/@types/react/package.json
./node_modules/@vitest/expect/LICENSE
./node_modules/@vitest/expect/README.md
./node_modules/@vitest/expect/package.json
./node_modules/@vitest/mocker/LICENSE
./node_modules/@vitest/mocker/README.md
./node_modules/@vitest/mocker/package.json
./node_modules/@vitest/pretty-format/LICENSE
./node_modules/@vitest/pretty-format/README.md
./node_modules/@vitest/pretty-format/package.json
./node_modules/@vitest/runner/LICENSE
./node_modules/@vitest/runner/README.md
./node_modules/@vitest/runner/package.json
./node_modules/@vitest/runner/types.d.ts
./node_modules/@vitest/runner/utils.d.ts
./node_modules/@vitest/snapshot/LICENSE
./node_modules/@vitest/snapshot/README.md
./node_modules/@vitest/snapshot/environment.d.ts
./node_modules/@vitest/snapshot/manager.d.ts
./node_modules/@vitest/snapshot/package.json
./node_modules/@vitest/spy/LICENSE
./node_modules/@vitest/spy/README.md
./node_modules/@vitest/spy/optional-types.d.ts
./node_modules/@vitest/spy/package.json
./node_modules/@vitest/utils/LICENSE
./node_modules/@vitest/utils/README.md
./node_modules/@vitest/utils/diff.d.ts
./node_modules/@vitest/utils/error.d.ts
./node_modules/@vitest/utils/helpers.d.ts
./node_modules/@vitest/utils/package.json
./node_modules/camelcase-css/README.md
./node_modules/camelcase-css/index-es5.js
./node_modules/camelcase-css/index.js
./node_modules/camelcase-css/license
./node_modules/camelcase-css/package.json
./node_modules/cssesc/LICENSE-MIT.txt
./node_modules/cssesc/README.md
./node_modules/cssesc/bin/cssesc
./node_modules/cssesc/cssesc.js
./node_modules/cssesc/man/cssesc.1
./node_modules/cssesc/package.json
./node_modules/csstype/LICENSE
./node_modules/csstype/README.md
./node_modules/csstype/index.d.ts
./node_modules/csstype/index.js.flow
./node_modules/csstype/package.json
./node_modules/esbuild/LICENSE.md
./node_modules/esbuild/README.md
./node_modules/esbuild/bin/esbuild
./node_modules/esbuild/install.js
./node_modules/esbuild/lib/main.d.ts
./node_modules/esbuild/lib/main.js
./node_modules/esbuild/package.json
./node_modules/fast-deep-equal/es6/react.d.ts
./node_modules/fast-deep-equal/es6/react.js
./node_modules/fast-deep-equal/react.d.ts
./node_modules/fast-deep-equal/react.js
./node_modules/fast-json-stringify/build/build-schema-validator.js
./node_modules/fast-json-stringify/test/required.test.js
./node_modules/fast-json-stringify/test/requiresAjv.test.js
./node_modules/fastify/build/build-error-serializer.js
./node_modules/fastify/build/build-validation.js
./node_modules/fastify/build/sync-version.js
./node_modules/fastify/test/build-certificate.js
./node_modules/lightningcss-android-arm64/LICENSE
./node_modules/lightningcss-android-arm64/README.md
./node_modules/lightningcss-android-arm64/lightningcss.android-arm64.node
./node_modules/lightningcss-android-arm64/package.json
./node_modules/lightningcss/LICENSE
./node_modules/lightningcss/README.md
./node_modules/lightningcss/node/ast.d.ts
./node_modules/lightningcss/node/ast.js.flow
./node_modules/lightningcss/node/browserslistToTargets.js
./node_modules/lightningcss/node/composeVisitors.js
./node_modules/lightningcss/node/flags.js
./node_modules/lightningcss/node/index.d.ts
./node_modules/lightningcss/node/index.js
./node_modules/lightningcss/node/index.js.flow
./node_modules/lightningcss/node/index.mjs
./node_modules/lightningcss/node/targets.d.ts
./node_modules/lightningcss/node/targets.js.flow
./node_modules/lightningcss/package.json
./node_modules/lines-and-columns/build/index.d.ts
./node_modules/lines-and-columns/build/index.js
./node_modules/mnemonist/sort/quick.js
./scripts/build_legacy_tool_migration_matrix.py
```

## Testing Signals

```text
tests/__pycache__/test_agent_dna.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_conflict.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_consensus.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_docs_contract.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_domain_import_boundaries.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_dreamvault_closeout_bridge.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_legacy_tool_migration_matrix.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_mcp_servers.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_pattern_miner.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_project_artifact_contract.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_remaining_python_imports.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_stage4_features.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_toolbelt.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_toolbelt_surface_audit.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_tools_v2_registry_contract.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_tools_v2_safe_execution_contract.cpython-313-pytest-9.0.3.pyc
tests/__pycache__/test_work_proof.cpython-313-pytest-9.0.3.pyc
tests/compat/__pycache__/test_agenttools_bus_message_adapter_contract.cpython-313-pytest-9.0.3.pyc
tests/compat/__pycache__/test_agenttools_tool_adapter_characterization.cpython-313-pytest-9.0.3.pyc
tests/compat/__pycache__/test_dreamos_message_contract_boundary.cpython-313-pytest-9.0.3.pyc
tests/compat/test_agenttools_bus_message_adapter_contract.py
tests/compat/test_agenttools_tool_adapter_characterization.py
tests/compat/test_dreamos_message_contract_boundary.py
tests/test_agent_dna.py
tests/test_conflict.py
tests/test_consensus.py
tests/test_docs_contract.py
tests/test_domain_import_boundaries.py
tests/test_dreamvault_closeout_bridge.py
tests/test_legacy_tool_migration_matrix.py
tests/test_mcp_servers.py
tests/test_pattern_miner.py
tests/test_project_artifact_contract.py
tests/test_remaining_python_imports.py
tests/test_stage4_features.py
tests/test_toolbelt.py
tests/test_toolbelt_surface_audit.py
tests/test_tools_v2_registry_contract.py
tests/test_tools_v2_safe_execution_contract.py
tests/test_work_proof.py
```

## Current README Head

```markdown
# 🐺 WE ARE SWARM

**Multi-Agent AI Coordination Framework** with Model Context Protocol (MCP) support.

*A pack of wolves, not bees.*

*"Alone we are strong. Together we are unstoppable."*

---

## What Is This?

A framework that enables **multiple AI agents** (Claude, GPT, Gemini, etc.) to work together autonomously - coordinating tasks, sharing knowledge, making collective decisions, and learning from each other.

Think of it as the **nervous system for an AI swarm**.

```
┌─────────────────────────────────────────────────────────────┐
│                     WE ARE SWARM 🐺                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐      messages      ┌─────────┐               │
│   │ Agent-1 │◄──────────────────►│ Agent-2 │               │
│   │ Claude  │                    │  GPT-4  │               │
│   └────┬────┘                    └────┬────┘               │
│        │       shared memory          │                     │
│        │     conflict detection       │                     │
│        │       consensus voting       │                     │
│        └──────────┬───────────────────┘                     │
│                   ▼                                         │
│   ┌─────────────────────────────────────────┐              │
│   │           SWARM MCP TOOLBELT            │              │
│   │                                         │              │
│   │  Core:        IP-Level:                 │              │
│   │  • Messaging  • Consensus Engine        │              │
│   │  • Tasks      • Conflict Detector       │              │
│   │  • Memory     • Agent DNA               │              │
│   │               • Work Proof              │              │
│   │               • Pattern Miner           │              │
│   └─────────────────────────────────────────┘              │
│                   ▲                                         │
│        ┌──────────┴───────────────────┐                     │
│        │                              │                     │
│   ┌─────────┐                    ┌─────────┐               │
│   │ Agent-3 │                    │ Agent-4 │               │
│   │ Claude  │                    │ Gemini  │               │
│   └─────────┘                    └─────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
pip install swarm-mcp
```

```python
from swarm_mcp import PackCoordinator, AgentDNA, ConsensusEngine

# Coordinate your swarm
pack = PackCoordinator(wolves=["agent-1", "agent-2", "agent-3"])

# Check who's available
ready = pack.get_ready_wolves()

# Assign work
pack.assign_hunt("agent-1", "Fix the authentication bug")

# Learn which agent is best at what
dna = AgentDNA()
best_agent, confidence = dna.find_best_agent(category="debugging")

# Make collective decisions
consensus = ConsensusEngine()
proposal = consensus.propose("agent-1", "Use PostgreSQL", "Need ACID transactions...")
```

```

## Proven Capabilities

- Agent tooling and orchestration helpers
- MCP/API integration surfaces
- Dashboard/operator UX components
- Runtime adapters and bridges
- Repo-level tests and validation
- Multi-language toolchain support
- Automation utility scaffolding

## Unverified / Avoid Claiming

- Autonomous AGI
- Fully autonomous swarm intelligence
- Guaranteed autonomous execution
- Production-ready claims without verification

## Recommended GitHub Description

> Dream.OS toolbelt for MCP/API adapters, dashboards, operator surfaces, runtime bridges, and automation utilities.

## README Rewrite Direction

- Position AgentTools as the operator tooling layer
- Clarify separation from DreamOS canonical runtime
- Highlight adapters, dashboards, and MCP surfaces
- Include verified tooling/runtime evidence only
- Add architecture map later

## Ecosystem Role

| Repo | Relationship |
|---|---|
| DreamOS | canonical runtime/orchestration/contracts layer |
| DreamVault | governance, reports, operational memory |
| AgentTools | adapters, dashboards, MCP/API surfaces, tooling |
| projectscanner | repo intelligence and inventory feeds |

## Confidence

- Confidence: HIGH
- Evidence density: HIGH
- README rewrite readiness: READY

AGENTTOOLS_DOSSIER=PASS
