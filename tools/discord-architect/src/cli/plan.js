#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { diffSchemas } = require("../diff");

function parseArgs(argv) {
  const args = {
    current: "schemas/current.json",
    desired: "schemas/desired.json",
    out: "../data/reports/discord_architect/diff_plan.json",
    markdown: "../data/reports/discord_architect/diff_plan.md"
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];

    if (arg === "--current") {
      args.current = next;
      i++;
    } else if (arg === "--desired") {
      args.desired = next;
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

function renderMarkdown(plan, currentPath, desiredPath) {
  const lines = [
    "# Discord Architect Diff Plan",
    "",
    `Current: \`${currentPath}\``,
    `Desired: \`${desiredPath}\``,
    "",
    `Operations: ${plan.operation_count}`,
    `Destructive operations: ${plan.destructive_count}`,
    "",
    "| Action | Name | Category | Destructive |",
    "|---|---|---|---:|"
  ];

  for (const op of plan.operations) {
    lines.push(
      `| ${op.action} | \`${op.name || ""}\` | ${op.category || ""} | ${Boolean(op.destructive)} |`
    );
  }

  return lines.join("\n") + "\n";
}

function writePlan(args) {
  const current = readJson(args.current);
  const desired = readJson(args.desired);
  const plan = diffSchemas(current, desired);

  plan.current_schema = args.current;
  plan.desired_schema = args.desired;
  plan.generated_at = new Date().toISOString();
  plan.mode = "plan_only";

  fs.mkdirSync(path.dirname(args.out), { recursive: true });
  fs.mkdirSync(path.dirname(args.markdown), { recursive: true });

  fs.writeFileSync(args.out, JSON.stringify(plan, null, 2) + "\n");
  fs.writeFileSync(args.markdown, renderMarkdown(plan, args.current, args.desired));

  return plan;
}

function main() {
  const args = parseArgs(process.argv);
  const plan = writePlan(args);

  console.log(`PLAN_OPERATIONS=${plan.operation_count}`);
  console.log(`PLAN_DESTRUCTIVE=${plan.destructive_count}`);
  console.log(`PLAN_JSON=${args.out}`);
  console.log(`PLAN_MD=${args.markdown}`);
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  renderMarkdown,
  writePlan
};
