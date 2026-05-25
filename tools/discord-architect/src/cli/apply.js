#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const REQUIRED_SIGNATURE = "I AUTHORIZE DISCORD ARCHITECT APPLY";

function parseArgs(argv) {
  const args = {
    manifest: "../data/reports/discord_architect/apply_manifest.json",
    dryRun: false,
    signature: "",
    report: "../data/reports/discord_architect/apply_report.json",
    markdown: "../data/reports/discord_architect/apply_report.md"
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];

    if (arg === "--manifest") {
      args.manifest = next;
      i++;
    } else if (arg === "--signature") {
      args.signature = next;
      i++;
    } else if (arg === "--report") {
      args.report = next;
      i++;
    } else if (arg === "--markdown") {
      args.markdown = next;
      i++;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    }
  }

  return args;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function latestBackupExists() {
  const backupDir = path.join(process.cwd(), "schemas", "backups");
  if (!fs.existsSync(backupDir)) return false;
  return fs.readdirSync(backupDir).some((name) => name.endsWith(".json"));
}

function validateManifest(manifest, args) {
  const operations = manifest.operations || [];
  const blocked = [];
  const allowed = [];

  for (const op of operations) {
    if (op.action === "create_channel" && !op.destructive) {
      allowed.push(op);
    } else {
      blocked.push({
        ...op,
        block_reason: op.destructive
          ? "destructive_operation_blocked"
          : "operation_not_allowed_in_phase_1"
      });
    }
  }

  const signatureOk = args.signature === REQUIRED_SIGNATURE;
  const backupOk = latestBackupExists();

  const canExecute = signatureOk && backupOk && blocked.length === 0 && allowed.length > 0;

  return {
    schema: "dreamos.discord_architect.apply_report.v1",
    generated_at: new Date().toISOString(),
    mode: args.dryRun ? "dry_run" : "execute_requested",
    manifest_path: args.manifest,
    signature_ok: signatureOk,
    backup_ok: backupOk,
    discord_mutation_allowed: false,
    execute_blocked: true,
    execute_block_reason: args.dryRun
      ? "dry_run"
      : (!signatureOk
        ? "missing_or_invalid_signature"
        : (!backupOk
          ? "missing_backup"
          : (blocked.length > 0
            ? "blocked_operations_present"
            : "discord_api_apply_not_enabled_yet"))),
    allowed_operations: allowed,
    blocked_operations: blocked,
    operation_count: operations.length,
    allowed_count: allowed.length,
    blocked_count: blocked.length,
    phase_policy: {
      allowed_operations: ["create_channel"],
      blocked_operations: ["archive_channel", "delete_channel", "update_channel", "update_permissions"],
      destructive_delete: false
    },
    would_execute: canExecute && !args.dryRun
  };
}

function renderMarkdown(report) {
  const lines = [
    "# Discord Architect Apply Report",
    "",
    `Mode: \`${report.mode}\``,
    `Signature OK: ${report.signature_ok}`,
    `Backup OK: ${report.backup_ok}`,
    `Discord mutation allowed: ${report.discord_mutation_allowed}`,
    `Execute blocked: ${report.execute_blocked}`,
    `Reason: \`${report.execute_block_reason}\``,
    "",
    "## Allowed Operations",
    "",
    "| Action | Name | Category |",
    "|---|---|---|"
  ];

  for (const op of report.allowed_operations) {
    lines.push(`| ${op.action} | \`${op.name || ""}\` | ${op.category || ""} |`);
  }

  lines.push("", "## Blocked Operations", "", "| Action | Name | Reason |", "|---|---|---|");

  for (const op of report.blocked_operations) {
    lines.push(`| ${op.action} | \`${op.name || ""}\` | ${op.block_reason} |`);
  }

  return lines.join("\n") + "\n";
}

function writeApplyReport(args) {
  const manifest = readJson(args.manifest);
  const report = validateManifest(manifest, args);

  fs.mkdirSync(path.dirname(args.report), { recursive: true });
  fs.mkdirSync(path.dirname(args.markdown), { recursive: true });

  fs.writeFileSync(args.report, JSON.stringify(report, null, 2) + "\n");
  fs.writeFileSync(args.markdown, renderMarkdown(report));

  return report;
}

function main() {
  const args = parseArgs(process.argv);
  const report = writeApplyReport(args);

  console.log(`APPLY_MODE=${report.mode}`);
  console.log(`SIGNATURE_OK=${report.signature_ok}`);
  console.log(`BACKUP_OK=${report.backup_ok}`);
  console.log(`ALLOWED_COUNT=${report.allowed_count}`);
  console.log(`BLOCKED_COUNT=${report.blocked_count}`);
  console.log(`MUTATION_ALLOWED=${report.discord_mutation_allowed}`);
  console.log(`EXECUTE_BLOCKED=${report.execute_blocked}`);
  console.log(`REASON=${report.execute_block_reason}`);
  console.log(`REPORT_JSON=${args.report}`);
  console.log(`REPORT_MD=${args.markdown}`);
}

if (require.main === module) {
  main();
}

module.exports = {
  REQUIRED_SIGNATURE,
  parseArgs,
  latestBackupExists,
  validateManifest,
  renderMarkdown,
  writeApplyReport
};
