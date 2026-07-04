#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = {
    source: "schemas/current.json",
    outdir: "schemas/backups"
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];

    if (arg === "--source") {
      args.source = next;
      i++;
    } else if (arg === "--outdir") {
      args.outdir = next;
      i++;
    }
  }

  return args;
}

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function backupSchema(source, outdir) {
  const raw = fs.readFileSync(source, "utf8");
  const parsed = JSON.parse(raw);

  fs.mkdirSync(outdir, { recursive: true });

  const filename = `discord_schema_backup_${timestamp()}.json`;
  const backupPath = path.join(outdir, filename);

  const payload = {
    schema: "dreamos.discord_architect.backup.v1",
    generated_at: new Date().toISOString(),
    source_schema: source,
    protected: parsed.protected || [],
    snapshot: parsed
  };

  fs.writeFileSync(
    backupPath,
    JSON.stringify(payload, null, 2) + "\n"
  );

  return {
    backup_path: backupPath,
    protected_count: payload.protected.length
  };
}

function main() {
  const args = parseArgs(process.argv);
  const result = backupSchema(args.source, args.outdir);

  console.log(`BACKUP_PATH=${result.backup_path}`);
  console.log(`PROTECTED_COUNT=${result.protected_count}`);
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  backupSchema
};
