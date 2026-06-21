"""
Characterization tests for AgentTools domain/application import boundaries.

These tests protect the current production spine while the architecture is
restored. They should pass before any structural refactor.
"""

import importlib


DOMAIN_MODULES = [
    "swarm_mcp.core.agent_dna",
    "swarm_mcp.core.conflict",
    "swarm_mcp.core.consensus",
    "swarm_mcp.core.messaging",
    "swarm_mcp.core.messaging_templates",
    "swarm_mcp.core.task_scoring",
    "swarm_mcp.core.verification",
    "swarm_mcp.core.work_proof",
]

APPLICATION_MODULES = [
    "swarm_mcp.core.brain",
    "swarm_mcp.core.coordinator",
    "swarm_mcp.core.memory",
    "swarm_mcp.core.pattern_miner",
    "swarm_mcp.core.recovery",
]

ADAPTER_MODULES = [
    "swarm_mcp.servers.control",
    "swarm_mcp.servers.memory",
    "swarm_mcp.servers.messaging",
    "swarm_mcp.servers.tasks",
    "swarm_mcp.servers.tools",
]


def test_domain_modules_import_cleanly():
    for module_name in DOMAIN_MODULES:
        assert importlib.import_module(module_name)


def test_application_modules_import_cleanly():
    for module_name in APPLICATION_MODULES:
        assert importlib.import_module(module_name)


def test_adapter_modules_import_cleanly():
    for module_name in ADAPTER_MODULES:
        assert importlib.import_module(module_name)
