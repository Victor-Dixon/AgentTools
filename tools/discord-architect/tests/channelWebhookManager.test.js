const assert = require('assert');
const fs = require('fs');

const {
  normalizeChannelName,
  buildChannelMutationPlan,
  buildWebhookMutationPlan,
  ensureChannel,
  ensureWebhook,
} = require('../src/runtime/channelWebhookManager');

assert.strictEqual(normalizeChannelName('#Master Task Log!!'), 'master-task-log');

const channelPlan = buildChannelMutationPlan({
  name: '#Master Task Log',
  channelKey: 'master-task-log',
  topic: 'Dream.OS governed closeouts and capability unlocks',
});

assert.strictEqual(channelPlan.mutationType, 'channel.ensure');
assert.strictEqual(channelPlan.channelName, 'master-task-log');
assert.strictEqual(channelPlan.channelKey, 'master-task-log');
assert.strictEqual(channelPlan.channelType, 'GUILD_TEXT');

const webhookPlan = buildWebhookMutationPlan({
  channelKey: 'master-task-log',
  webhookName: 'Dream.OS Capability Feed',
});

assert.strictEqual(webhookPlan.mutationType, 'webhook.ensure');
assert.strictEqual(webhookPlan.channelKey, 'master-task-log');
assert.strictEqual(webhookPlan.webhookName, 'Dream.OS Capability Feed');

const channelReceiptPath = 'data/reports/discord_architect/channel_webhook_manager/test_channel_receipt.json';
const channelReceipt = ensureChannel(
  {
    name: '#Master Task Log',
    channelKey: 'master-task-log',
    mode: 'dry-run',
  },
  { receiptPath: channelReceiptPath }
);

assert.strictEqual(channelReceipt.ok, true);
assert.strictEqual(channelReceipt.mode, 'dry-run');
assert.strictEqual(channelReceipt.liveMutationAttempted, false);
assert.ok(fs.existsSync(channelReceiptPath));

const webhookReceiptPath = 'data/reports/discord_architect/channel_webhook_manager/test_webhook_receipt.json';
const webhookReceipt = ensureWebhook(
  {
    channelKey: 'master-task-log',
    webhookName: 'Dream.OS Capability Feed',
    mode: 'dry-run',
  },
  { receiptPath: webhookReceiptPath }
);

assert.strictEqual(webhookReceipt.ok, true);
assert.strictEqual(webhookReceipt.mode, 'dry-run');
assert.strictEqual(webhookReceipt.liveMutationAttempted, false);
assert.ok(fs.existsSync(webhookReceiptPath));

const liveReceipt = ensureWebhook(
  {
    channelKey: 'master-task-log',
    webhookName: 'Dream.OS Capability Feed',
    mode: 'live',
  },
  { receiptPath: 'data/reports/discord_architect/channel_webhook_manager/test_live_blocked_receipt.json' }
);

assert.strictEqual(liveReceipt.ok, false);
assert.strictEqual(liveReceipt.liveMutationAttempted, true);
assert.ok(liveReceipt.error.includes('not configured'));

console.log('channelWebhookManager.test.js PASS');
