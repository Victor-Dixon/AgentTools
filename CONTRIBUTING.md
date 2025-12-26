# Contributing to the Swarm

**🐺 WE ARE SWARM**

Thank you for your interest in contributing to the Swarm ecosystem. We are building a unified, autonomous development system.

## 🌟 The Mission

Our goal is to create a self-improving, multi-agent system where every tool is accessible via a standardized interface (MCP) and organized by domain.

## 🛠️ Getting Started

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/your-org/swarm-mcp.git
    cd swarm-mcp
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -e ".[dev]"
    ```

3.  **Run the Toolbelt**:
    ```bash
    python tools/cli.py --list
    ```

## 🏗️ Architecture

*   **`swarm_mcp/`**: Core logic (Consensus, Memory, DNA) and MCP Servers.
*   **`tools/`**: Domain-specific CLI tools (Monitoring, Security, etc.).
*   **`examples/`**: Runnable examples.

## 📝 Pull Request Standards

1.  **Use the Toolbelt**: Before submitting, run:
    ```bash
    # Security Scan
    python tools/cli.py --security-scan
    
    # Import Validation
    python tools/cli.py --audit-imports
    ```

2.  **Tests**: Ensure all tests pass.
    ```bash
    pytest
    ```

3.  **Commit Messages**: Use semantic commits (e.g., `feat: Add new agent`, `fix: Resolve queue deadlock`).

## 🤝 Adding New Tools

1.  Create your script in the appropriate `tools/<category>/` directory.
2.  Register it in `tools/toolbelt_registry.py`.
3.  Add it to `swarm_mcp/servers/tools.py` if it should be exposed to AI agents.

## 💬 Community

Join the pack. Discussion happens on GitHub Issues and Discord.

---
**"The strength of the wolf is the pack."**
