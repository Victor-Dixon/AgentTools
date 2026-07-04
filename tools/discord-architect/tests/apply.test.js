const assert = require("assert");
const { validateManifest, REQUIRED_SIGNATURE } = require("../src/cli/apply");

const manifest = {
  operations: [
    { action: "create_channel", name: "voice-lounge", category: "COMMUNITY", destructive: false },
    { action: "archive_channel", name: "old-chat", category: "COMMUNITY", destructive: true }
  ]
};

const report = validateManifest(manifest, {
  dryRun: true,
  signature: REQUIRED_SIGNATURE,
  manifest: "manifest.json"
});

assert.equal(report.schema, "dreamos.discord_architect.apply_report.v1");
assert.equal(report.allowed_count, 1);
assert.equal(report.blocked_count, 1);
assert.equal(report.discord_mutation_allowed, false);
assert.equal(report.execute_blocked, true);

console.log("apply.test.js PASS");
