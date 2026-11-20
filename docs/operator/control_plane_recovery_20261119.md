# Deferred Dream.OS Control Plane recovery

Status: DEFERRED / NOT RESTORED. Victor requested a draft and a return to branch retirement.

## Observed evidence
- Connected Dream.OS Control Plane health call returned USER_NOT_LOGGED_IN: connector is not connected. This is a connection/authentication failure, not proof that the Python server itself is broken.
- Historical operator readback found no listener on port 59134. That receipt is historical; current host listener state is UNVERIFIED.
- Existing source: mcp_servers/dreamos_control_plane_server.py, SERVER_VERSION 0.5.0, stdio transport intended for Secure MCP Tunnel. GitHub Architect and Discord functionality are delegated, not a reason to build a second executor.
- Source has platform-specific fallback paths. Active deployment env, process ownership, transport and OAuth issuer configuration require direct verification; do not infer them from defaults.
- Working fallback: DreamVault fixed-operation maintenance bridge and GitHub Architect's existing request queue/VPS executor. Five DreamVault branch retirements have durable receipts, documented at https://github.com/Victor-Dixon/DreamVault/issues/267#issuecomment-7012465766.

## Smallest future repair sequence
1. Establish the actual installed source, service/process, bind address and transport using already-authorized read-only tools. Distinguish connection absence, tunnel reachability, OAuth rejection and server failure. Never collect token values.
2. Reuse the existing tunnel and stdio server; repair only the proven failing layer. Require a user-facing reachable authorization endpoint. Do not publish a localhost URL as if it were reachable remotely, disable TLS verification, expose raw shell, or broaden network binds/scopes to make login work.
3. Complete normal operator OAuth connection using minimal read scope first. No invented authentication acknowledgment or untrusted human_approved flag.
4. Verify discovery, health and one read-only inspection; check redaction and deny missing/wrong-scope/expired authorization.
5. Independently read back the resulting receipt. Keep all destructive and outbound operations disabled until their existing boundaries are separately verified.

## Exact acceptance gate
- Existing connector successfully connects through its intended operator flow.
- Health and tool discovery return through that connection, not a local substitute.
- One authorized read-only inspection returns a bounded, redacted result tied to installed source identity.
- Unauthorized requests fail closed; credentials are absent from output/log artifacts.
- No branch deletion, Discord send, arbitrary shell, production deployment or scope expansion used as a smoke test.
- Record source revision, transport, observed results and remaining limits in docs/root/MASTER_TASK_LOG.md.

This PR records recovery work only. No service restart, install, tunnel, OAuth scope, credential or runtime permission was changed.
