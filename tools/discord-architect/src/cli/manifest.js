#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const REQUIRED_SIGNATURE = "I AUTHORIZE DISCORD ARCHITECT APPLY";

function parseArgs(argv) {
  const args = {
    plan: "../data/reports/discord_architect/diff_plan.json",
    out: "../data/reports/discord_architect/apply_manifest.json",
    markdown: "../data/reports/discord_architect/apply_manifest.md"
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];

    if (arg === "--plan") {
      args.plan = next;
      i++;
    } else if (arg === "--out") {
      args.out = next;
      i++;
    } else if (arg === "--markdown") {
      args.markdown = next;
      i++;
    }
  }

  return args;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function buildManifest(plan, planPath) {
  const operations = plan.operations || [];
  const destructive = operations.filter((op) => op.destructive);

  return {
    schema: "dreamos.discord_architect.apply_manifest.v1",
    generated_at: new Date().toISOString(),
    mode: "manifest_only",
    plan_path: planPath,
    required_signature: REQUIRED_SIGNATURE,
    signed: false,
    discord_mutation_allowed: false,
    operation_count: operations.length,
    destructive_count: destructive.length,
    gates: {
      plan_present: true,
      backup_required: true,
      operator_signature_required: true,
      destructive_ops_blocked_without_signature: destructive.length > 0,
      direct_ai_mutation_blocked: true
    },
    operations
  };
}

function renderMarkdown(manifest) {
  const lines = [
    "# Discord Architect Apply Manifest",
    "",
    `Mode: \`${manifest.mode}\``,
    `Operations: ${manifest.operation_count}`,
    `Destructive operations: ${manifest.destructive_count}`,
    `Discord mutation allowed: ${manifest.discord_mutation_allowed}`,
    "",
    "## Required Signature",
    "",
    `\`${manifest.required_signature}\``,
    "",
    "## Gates",
    "",
    "| Gate | Value |",
    "|---|---|"
  ];

  for (const [key, value] of Object.entries(manifest.gates)) {
    lines.push(`| ${key} | ${value} |`);
  }

  lines.push("", "## Operations", "", "| Action | Name | Destructive |", "|---|---|---:|");

  for (const op of manifest.operations) {
    lines.push(`| ${op.action} | \`${op.name || ""}\` | ${Boolean(op.destructive)} |`);
  }

  return lines.join("\n") + "\n";
}

function writeManifest(args) {
  const plan = readJson(args.plan);
  const manifest = buildManifest(plan, args.plan);

  fs.mkdirSync(path.dirname(args.out), { recursive: true });
  fs.mkdirSync(path.dirname(args.markdown), { recursive: true });

  fs.writeFileSync(args.out, JSON.stringify(manifest, null, 2) + "\n");
  fs.writeFileSync(args.markdown, renderMarkdown(manifest));

  return manifest;
}

function main() {
  const args = parseArgs(process.argv);
  const manifest = writeManifest(args);

  console.log(`MANIFEST_OPERATIONS=${manifest.operation_count}`);
  console.log(`MANIFEST_DESTRUCTIVE=${manifest.destructive_count}`);
  console.log(`MUTATION_ALLOWED=${manifest.discord_mutation_allowed}`);
  console.log(`REQUIRED_SIGNATURE=${manifest.required_signature}`);
  console.log(`MANIFEST_JSON=${args.out}`);
  console.log(`MANIFEST_MD=${args.markdown}`);
}

if (require.main === module) {
  main();
}

module.exports = {
  REQUIRED_SIGNATURE,
  parseArgs,
  buildManifest,
  renderMarkdown,
  writeManifest
};
