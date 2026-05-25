const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");

const { backupSchema } = require("../src/cli/backup");

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "discord-backup-"));

const source = path.join(tmp, "current.json");
const outdir = path.join(tmp, "backups");

fs.writeFileSync(
  source,
  JSON.stringify({
    protected: ["general", "rules"],
    categories: [
      {
        name: "COMMUNITY",
        channels: [
          { name: "general", type: "text" }
        ]
      }
    ]
  })
);

const result = backupSchema(source, outdir);

assert(fs.existsSync(result.backup_path));

const payload = JSON.parse(fs.readFileSync(result.backup_path, "utf8"));

assert.equal(payload.schema, "dreamos.discord_architect.backup.v1");
assert.equal(payload.protected.length, 2);

console.log("backup.test.js PASS");
