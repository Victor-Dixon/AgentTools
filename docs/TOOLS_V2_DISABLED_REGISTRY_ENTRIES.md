# tools_v2 Disabled Registry Entries

These entries were removed from the active `tools_v2` registry because the registry contract test proved they do not instantiate cleanly.

Active registry policy:

- `ToolRegistry.list_tools()` must return only loadable tools.
- `ToolRegistry.get_tool()` must instantiate the adapter.
- Each active adapter must expose a valid `ToolSpec`.
- Broken or incomplete adapters stay in `disabled_tools` until fixed.

## Disabled Entries

- `agent.points` — Missing class: tools_v2.categories.session_tools.PointsCalculatorTool
- `brain.get` — Abstract adapter missing get_spec/validate
- `brain.note` — Abstract adapter missing get_spec/validate
- `brain.search` — Abstract adapter missing get_spec/validate
- `brain.session` — Abstract adapter missing get_spec/validate
- `brain.share` — Abstract adapter missing get_spec/validate
- `discord.health` — Abstract adapter missing get_spec/validate
- `discord.start` — Abstract adapter missing get_spec/validate
- `discord.test` — Abstract adapter missing get_spec/validate
- `infra.roi_calc` — Missing class: tools_v2.categories.infrastructure_tools.ROICalculatorTool
- `mem.imports` — Missing class: tools_v2.categories.memory_safety_adapters.ImportValidatorTool
- `msgtask.fingerprint` — Abstract adapter missing get_spec/validate
- `msgtask.ingest` — Abstract adapter missing get_spec/validate
- `msgtask.parse` — Abstract adapter missing get_spec/validate
- `obs.get` — Abstract adapter missing get_spec/validate
- `obs.health` — Abstract adapter missing get_spec/validate
- `obs.metrics` — Abstract adapter missing get_spec/validate
- `obs.slo` — Abstract adapter missing get_spec/validate
