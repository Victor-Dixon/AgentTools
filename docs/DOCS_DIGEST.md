# AgentTools Docs Digest

Generated from current repository docs after legacy archive extraction.

## Documents Reviewed

- `README.md`
- `PRODUCTION_READINESS.md`
- `PROJECT_REVIEW.md`
- `NEXT_UP.md`
- `TOOLBELT_UNIFICATION_PLAN.md`
- `TOOLS_CONSOLIDATION_PLAN.md`
- `TOOLS_FLATTENING_PLAN.md`
- `TOOLS_RANKING_REPORT.md`
- `docs/root/TOOLS_USAGE_GUIDE.md`
- `docs/TOOL_SURFACES_AND_OVERLAP.md`
- `docs/CODEBASE_RECON_AND_EXECUTION_PLAN.md`
- `docs/MCP_TOOLS_ROADMAP.md`
- `docs/architecture/CODE_INVENTORY.md`
- `docs/architecture/DOMAIN_MODEL_DISCOVERY.md`
- `docs/architecture/adr/0001-production-architecture.md`

## Heading Inventory

### `README.md`

- # 🐺 WE ARE SWARM
- ## What Is This?
- ## 🚀 Quick Start
- # Coordinate your swarm
- # Check who's available
- # Assign work
- # Learn which agent is best at what
- # Make collective decisions
- ## 📦 What's Included
- ### Core Modules
- ### IP-Level Modules (The Goldmines 💎)
- ## 🗳️ ConsensusEngine - Collective Decision Making
- # Create a proposal
- # Agents vote with reasoning
- # Check the result
- # {"passed": True, "reason": "3/4 approved (>66% required)"}
- ## 🚫 ConflictDetector - No Duplicate Work
- # Agent-1 declares what they're working on
- # Later, Agent-2 wants to work on the same area
- # When done, free up the area
- ## 🧬 AgentDNA - Learn Agent Strengths
- # Record completed work
- # Over time, patterns emerge...
- # Find the best agent for a new task
- # "Best agent: agent-1 (confidence: 92%)"
- # Get an agent's full profile
- # ["debugging", "auth", "python"]
- # Estimate how long a task will take
- # Get leaderboard
- # [("agent-1", 0.95, 12), ("agent-3", 0.88, 8), ...]
- ## ✅ WorkProofSystem - Verifiable Completion
- # BEFORE work: Commit to the task
- # Snapshots file hashes, timestamps, etc.
- # ... agent does the work ...
- # AFTER work: Generate proof
- # Anyone can verify the proof
- ## 📊 PatternMiner - Learn What Works
- # Record events as they happen
- # Over time, patterns emerge automatically...
- # Get suggestions for a new situation

### `PRODUCTION_READINESS.md`

- ## Current Security Audit Exception

### `PROJECT_REVIEW.md`

- # 🐺 COMPREHENSIVE PROJECT REVIEW - WE ARE SWARM
- ## 📊 EXECUTIVE SUMMARY
- ### Project Status: **ACTIVE DEVELOPMENT - PRE-LAUNCH**
- ## 📈 PROJECT METRICS
- ### Codebase Statistics
- ### Repository Health
- ### Directory Structure Analysis
- ## 🏗️ ARCHITECTURE ANALYSIS
- ### Core Components
- #### 1. **Swarm MCP Core** (`swarm_mcp/`) - ✅ **STRONG**
- #### 2. **MCP Servers** - ✅ **FUNCTIONAL**
- #### 3. **Tools Ecosystem** - ⚠️ **NEEDS CONSOLIDATION**
- ## 📚 DOCUMENTATION REVIEW
- ### Documentation Quality: **8/10** ✅
- ## 🧪 TESTING ANALYSIS
- ### Test Coverage: **6/10** ⚠️
- ## 🚀 DEPLOYMENT READINESS
- ### Pre-Launch Checklist: **5/10** ⚠️
- #### ✅ **COMPLETE:**
- #### ⚠️ **BLOCKERS (P0):**
- #### 📋 **RECOMMENDED (P1):**
- ## 🎯 STRENGTHS
- ### 1. **Strong Architectural Foundation**
- ### 2. **Comprehensive Tool Ecosystem**
- ### 3. **Excellent Documentation**
- ### 4. **Active Development**
- ### 5. **Innovative Features**
- ## ⚠️ WEAKNESSES & RISKS
- ### 1. **Tools Consolidation Incomplete** (CRITICAL)
- ### 2. **Test Coverage Insufficient** (HIGH)
- ### 3. **Pre-Launch Tasks Pending** (CRITICAL)
- ### 4. **No Version Tags** (MEDIUM)
- ### 5. **CI/CD Not Configured** (MEDIUM)
- ## 📋 PRIORITY RECOMMENDATIONS
- ### 🔴 **IMMEDIATE (This Week - P0)**
- ### 🟡 **SHORT TERM (Next Week - P1)**
- ### 🟢 **MEDIUM TERM (Next Month - P2)**
- ## 🎓 LESSONS LEARNED
- ### What's Working Well
- ### Areas for Improvement

### `NEXT_UP.md`

- # NEXT UP — SWARM MCP EXECUTION DASHBOARD
- ## What this project even is
- ## Where we are now (accurate status)
- ## Inventory proof snapshot (evidence as of 2026-03-23)
- ### Reproducibility note
- ## What we should focus on next (strict order)
- ## Definition of done for this transition
- ## Operator handoff note (2026-03-24)
- ## Tooling stream update (mirrors SSOT, 2026-03-24 UTC)
- ### Completed now
- ### Commands run (2026-03-24 UTC)
- ### Active blocker
- # Production Restoration Backlog
- ## Objective
- ## Current Architecture Decision
- ## Active Product Spine
- ## TDD Rule
- ## Next Workstream
- ### 1. Agent domain
- ### 2. Message domain
- ### 3. Task domain
- ### 4. Work proof / verification
- ### 5. MCP adapter consolidation
- ## Exit Criteria

### `TOOLBELT_UNIFICATION_PLAN.md`

- # 🛠️ Toolbelt Unification & V2 Migration Plan
- ## 🎯 Objective
- ## Phase 1: Registry Mapping & Gap Analysis
- ## Phase 2: V2 Adapter Implementation
- ## Phase 3: CLI & MCP Entry Point Migration
- ## Phase 4: Verification & Cleanup
- ## 📋 Execution Checklist
- ## 🚀 Benefits

### `TOOLS_CONSOLIDATION_PLAN.md`

- # 🗂️ Tools & Tools_v2 Consolidation Plan
- ## 📊 Current State Analysis
- ### `tools/` Directory
- ### `tools_v2/` Directory
- ### Key Differences
- ## 🎯 Consolidation Strategy
- ### Phase 0A: Organization & Planning (P0) - **START HERE**
- ### Phase 1: Analysis & Mapping (P0)
- ### Phase 2: Unified Tools Migration (P0)
- ### Phase 3: Domain Tools Migration (P1)
- ### Phase 4: Adapter Pattern Conversion (P1)
- ### Phase 5: Registry Unification (P1)
- ### Phase 6: Duplicate Removal (P1)
- ### Phase 7: Testing & Validation (P1)
- ### Phase 8: Documentation & Cleanup (P2)
- ## 📋 Detailed Migration Checklist
- ### Unified Tools (Priority: P0)
- #### 1. Unified Monitor
- #### 2. Unified Validator
- #### 3. Unified Analyzer
- #### 4. Unified Security Scanner
- #### 5. Unified Debugger
- #### 6. Unified Environment
- ### Domain Tools (Priority: P1)
- #### GitHub Tools
- #### WordPress Tools
- #### Discord Tools
- ## 🔄 Registry Unification Strategy
- ### Current State
- ### Unified Registry Design
- # Unified registry that supports both patterns
- ### Backward Compatibility
- ## 📊 Success Metrics
- ### Quantitative
- ### Qualitative
- ## 🚨 Risks & Mitigation
- ### Risk 1: Breaking Changes
- ### Risk 2: Lost Functionality
- ### Risk 3: Registry Conflicts
- ### Risk 4: V2 Compliance Violations

### `TOOLS_FLATTENING_PLAN.md`

- # 🗂️ Tools Flattening & Organization Plan
- ## 📊 Current State Analysis
- ### Directory Statistics
- ### Current Structure
- ## 🎯 Flattening Strategy
- ### Phase 1: Pre-Flattening Analysis (P0)
- #### 1.1 Dependency Mapping
- #### 1.2 Conflict Detection
- #### 1.3 Registry Analysis
- #### 1.4 Architecture Analysis
- ### Phase 2: Target Organization Structure (P0)
- #### 2.1 Proposed Structure
- #### 2.2 Organization Principles
- ### Phase 3: Flattening Execution (P0)
- #### 3.1 Create Target Structure
- #### 3.2 Move Core Infrastructure
- #### 3.3 Move Category Tools
- #### 3.4 Move Unified Tools
- #### 3.5 Move Domain Tools
- #### 3.6 Move Deprecated Tools
- #### 3.7 Move Tests and Examples
- #### 3.8 Clean Up Empty Directories
- ### Phase 4: Import Path Updates (P0)
- #### 4.1 Update Internal Imports
- #### 4.2 Update External Imports
- #### 4.3 Update Registry References
- ### Phase 5: Registry Unification (P0)
- #### 5.1 Design Unified Registry
- #### 5.2 Merge Registry Data
- #### 5.3 Create Unified Registry Implementation
- #### 5.4 Update Registry Consumers
- ### Phase 6: Adapter Pattern Migration (P1)
- #### 6.1 Identify Migration Candidates
- #### 6.2 Create Legacy Adapter
- #### 6.3 Migrate Tools to Adapters
- ### Phase 7: Testing & Validation (P0)
- #### 7.1 Import Testing
- #### 7.2 Registry Testing
- #### 7.3 Integration Testing
- #### 7.4 Smoke Testing

### `TOOLS_RANKING_REPORT.md`

- # 🛠️ Inventory of Tools Ranked by Value (LOC)
- ## 📊 Category Summary
- ## 📂 misc (244 tools)
- ## 📂 reporting_tools (89 tools)
- ## 📂 github_tools (69 tools)
- ## 📂 testing_tools (87 tools)
- ## 📂 swarm_tools (47 tools)
- ## 📂 web_tools (37 tools)
- ## 📂 communication_tools (27 tools)
- ## 📂 thea (23 tools)
- ## 📂 fixes (19 tools)
- ## 📂 cli (3 tools)
- ## 📂 captain (13 tools)
- ## 📂 automation (8 tools)
- ## 📂 communication (9 tools)
- ## 📂 cleanup (9 tools)
- ## 📂 agent_ops (7 tools)
- ## 📂 cloud_tools (6 tools)
- ## 📂 deployment (5 tools)
- ## 📂 toolbelt (11 tools)
- ## 📂 analysis (5 tools)
- ## 📂 debug (5 tools)
- ## 📂 intelligent_mission_advisor (1 tools)
- ## 📂 discovery (5 tools)
- ## 📂 github_consolidation_tools (1 tools)
- ## 📂 autonomous_workflow_tools (1 tools)
- ## 📂 coordination_tools (1 tools)
- ## 📂 import_fix_tools (1 tools)
- ## 📂 discord_webhook_tools (1 tools)
- ## 📂 ssot_validation_tools (1 tools)
- ## 📂 memory_safety_tools (1 tools)
- ## 📂 setup (2 tools)
- ## 📂 swarm_mission_control (1 tools)
- ## 📂 swarm_consciousness (1 tools)
- ## 📂 generators (2 tools)
- ## 📂 integration_tools (1 tools)
- ## 📂 deprecated (4 tools)
- ## 📂 validation_tools (1 tools)
- ## 📂 proposal_tools (1 tools)
- ## 📂 consolidation (2 tools)

### `docs/root/TOOLS_USAGE_GUIDE.md`

- # 🛠️ Tools Usage Guide - Phase 0A Support
- ## 📦 Installation
- ### 1. Install Project Dependencies
- # Install in development mode (recommended)
- # Or install with dev dependencies
- # Or install with full dependencies
- ### 2. Verify Installation
- # Check Python version (needs 3.10+)
- # Verify project structure
- ## 🚀 Using the Tools
- ### Method 1: Direct Tool Execution (Recommended)
- # Unified Analyzer
- # Unified Validator
- # Unified Monitor
- ### Method 2: Using Python Module Syntax
- # Run as Python modules
- ### Alternative: CLI Dispatcher
- # Use unified dispatcher
- # Example: Run a registered command
- ## 🎯 Tools for Phase 0A Tasks
- ### 1. Tool Inventory System
- #### Use Unified Analyzer for Tool Discovery
- # Analyze repository structure
- # Analyze project structure
- # Detect consolidation opportunities
- # Find overlap between tools
- # Run all analysis categories
- #### Use Consolidation Analyzer (Diamond Tool)
- # Analyze consolidation opportunities
- # Or directly
- #### Use Source Analyzer (Diamond Tool)
- # Get source code statistics
- # Or directly
- ### 2. Dependency Mapping
- #### Use Unified Validator for Import Analysis
- # Validate all imports
- # Audit imports (Gold Tool)
- # Or directly
- #### Use Import Chain Validator
- # Validate import chains

### `docs/TOOL_SURFACES_AND_OVERLAP.md`

- # Tool Surfaces & Overlap Map
- ## Tool surfaces in this repo
- ## MCP servers (external tool surface)
- ### `git-operations`
- ### `swarm-brain`
- ### `swarm-messaging`
- ### `task-manager`
- ### `v2-compliance`
- ### `website-manager`
- ## Family Focus Board (runtime surface)
- ## Toolbelt V2 registry (internal adapter tool surface)
- ### Registry health (known failing entries)
- ### `agent_ops`
- ### `analysis`
- ### `business_intelligence`
- ### `captain`
- ### `compliance`
- ### `config`
- ### `consciousness`
- ### `coordination`
- ### `docs`
- ### `health`
- ### `infrastructure`
- ### `integration`
- ### `intelligent_advisor`
- ### `memory_safety`
- ### `messaging`
- ### `onboarding`
- ### `oss`
- ### `session`
- ### `testing`
- ### `v2`
- ### `validation`
- ### `vector`
- ### `workflow`
- ## Legacy CLI toolbelt registry
- ### `analysis`
- ### `compliance`
- ### `coordination`
- ### `git/github`

### `docs/CODEBASE_RECON_AND_EXECUTION_PLAN.md`

- # Codebase Recon & Closure-First Execution Plan
- ## Executive Summary
- ## Codebase Map
- ## Real Architecture
- ## Critical Findings
- ## Shipping Blockers
- ## What To Kill / Freeze / Defer
- ## What To Build Next
- ### Primary Lane: **Make Family Focus Board (`apps/api` + `apps/web` + `packages/shared`) the single shipping lane, with swarm/tooling treated as platform support**
- ## 30-Day Execution Plan
- ### Week 1 — Contract & Gate Closure
- ### Week 2 — Backend Reliability Closure
- ### Week 3 — MVP Usability Closure
- ### Week 4 — Drift Reduction Closure
- ## Evidence Appendix

### `docs/MCP_TOOLS_ROADMAP.md`

- # 🛠️ MCP Tools Roadmap - Game Server & Automation
- ## 🎮 Tier 1: Game Server Ecosystem (Immediate Value)
- ### 1. **Server Performance Monitor**
- # MCP Tools:
- ### 2. **Player Analytics & Moderation**
- # MCP Tools:
- ### 3. **Game Server Orchestration**
- # MCP Tools:
- ### 4. **Backup & Disaster Recovery**
- # MCP Tools:
- ## 💬 Tier 2: Community Management
- ### 5. **Discord Bot Integration**
- # MCP Tools:
- ### 6. **Content Creator Tools**
- # MCP Tools:
- ## 🔧 Tier 3: DevOps & Infrastructure
- ### 7. **Container Orchestration for Games**
- # MCP Tools:
- ### 8. **Log Analysis & Debugging**
- # MCP Tools:
- ## 💰 Tier 4: Business Operations
- ### 9. **Subscription & Payment Management**
- # MCP Tools:
- ### 10. **Website & Landing Page Generator**
- # MCP Tools:
- ## 🎯 Priority Matrix
- ## 🚀 Recommended Build Order
- ### Phase 1: Core Value (Weeks 1-2)
- ### Phase 2: Community Growth (Weeks 3-4)
- ### Phase 3: Scale (Weeks 5-8)
- ## 💡 Cross-Selling Strategy
- ## 🎮 Game-Specific Expansions
- ### Minecraft
- ### Rust
- ### ARK/Conan
- ### Palworld

### `docs/architecture/CODE_INVENTORY.md`

- # AgentTools Code Inventory
- ## `swarm_mcp/__init__.py`
- ## `swarm_mcp/cli.py`
- ### Functions
- ## `swarm_mcp/core/__init__.py`
- ## `swarm_mcp/core/agent_dna.py`
- ### Classes
- ## `swarm_mcp/core/brain.py`
- ### Classes
- ## `swarm_mcp/core/conflict.py`
- ### Classes
- ## `swarm_mcp/core/consensus.py`
- ### Classes
- ## `swarm_mcp/core/coordinator.py`
- ### Classes
- ## `swarm_mcp/core/memory.py`
- ### Classes
- ## `swarm_mcp/core/messaging.py`
- ### Classes
- ### Functions
- ## `swarm_mcp/core/messaging_templates.py`
- ### Classes
- ### Functions
- ## `swarm_mcp/core/pattern_miner.py`
- ### Classes
- ## `swarm_mcp/core/recovery.py`
- ### Classes
- ## `swarm_mcp/core/task_scoring.py`
- ### Classes
- ## `swarm_mcp/core/verification.py`
- ### Classes
- ## `swarm_mcp/core/work_proof.py`
- ### Classes
- ## `swarm_mcp/servers/__init__.py`
- ## `swarm_mcp/servers/control.py`
- ### Functions
- ## `swarm_mcp/servers/memory.py`
- ### Functions
- ## `swarm_mcp/servers/messaging.py`
- ### Functions

### `docs/architecture/DOMAIN_MODEL_DISCOVERY.md`

- # AgentTools Domain Model Discovery
- ## Product Thesis
- ## Candidate Domains
- ## Architecture Principle
- ## Refactor Policy

### `docs/architecture/adr/0001-production-architecture.md`

- # ADR-0001: AgentTools Production Architecture
- ## Status
- ## Context
- ## Decision
- ## Current Boundary Mapping
- ## Testing Strategy
- ## Refactor Constraint
- ## Consequences

