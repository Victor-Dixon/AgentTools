const assert = require('assert');
const fs = require('fs');

const {
  REGISTRY_PATH,
  executeMutationPlan,
} = require('../src/runtime/liveDiscordMutationRuntime');

const dryReceipt = executeMutationPlan(
  {
    mutationType: 'channel.ensure',
    mode: 'dry-run',
    channelKey: 'master-task-log',
  },
  {
    receiptPath:
      'data/reports/discord_architect/test_dry_receipt.json',
  }
);

assert.strictEqual(dryReceipt.ok, true);
assert.strictEqual(dryReceipt.simulated, true);
assert.strictEqual(dryReceipt.registryUpdated, true);

const liveBlocked = executeMutationPlan(
  {
    mutationType: 'webhook.ensure',
    mode: 'live',
    channelKey: 'master-task-log',
  },
  {
    receiptPath:
      'data/reports/discord_architect/test_live_blocked_receipt.json',
  }
);

assert.strictEqual(liveBlocked.ok, false);
assert.ok(
  String(liveBlocked.error).includes('missing DISCORD_BOT_TOKEN')
);

assert.ok(fs.existsSync(REGISTRY_PATH));

const registry = JSON.parse(
  fs.readFileSync(REGISTRY_PATH, 'utf8')
);

assert.ok(Array.isArray(registry.mutations));
assert.ok(registry.mutations.length >= 2);

console.log('liveDiscordMutationRuntime.test.js PASS');
