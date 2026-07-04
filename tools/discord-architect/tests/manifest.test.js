const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");

const {
  REQUIRED_SIGNATURE,
  writeManifest
} = require("../src/cli/manifest");

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "discord-manifest-"));

const planPath = path.join(tmp, "plan.json");
const outPath = path.join(tmp, "manifest.json");
const mdPath = path.join(tmp, "manifest.md");

fs.writeFileSync(
  planPath,
  JSON.stringify({
    operations: [
      { action: "create_channel", name: "options-flow", destructive: false },
      { action: "archive_channel", name: "old-chat", destructive: true }
    ]
  })
);

const manifest = writeManifest({
  plan: planPath,
  out: outPath,
  markdown: mdPath
});

assert.equal(manifest.schema, "dreamos.discord_architect.apply_manifest.v1");
assert.equal(manifest.required_signature, REQUIRED_SIGNATURE);
assert.equal(manifest.discord_mutation_allowed, false);
assert.equal(manifest.operation_count, 2);
assert.equal(manifest.destructive_count, 1);
assert(fs.existsSync(outPath));
assert(fs.existsSync(mdPath));

console.log("manifest.test.js PASS");
