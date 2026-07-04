const assert = require('assert');
const fs = require('fs');
const { dispatchCapabilityEvent } = require('../src/runtime/liveCapabilityEventDispatcher');

(async () => {
  const receiptPath = 'data/reports/discord/capability_evolution_feed/latest_dispatch_receipt.json';

  const receipt = await dispatchCapabilityEvent({
    receiptPath,
    mode: 'dry-run',
  });

  assert.strictEqual(receipt.ok, true);
  assert.strictEqual(receipt.mode, 'dry-run');
  assert.strictEqual(receipt.channelKey, 'master-task-log');
  assert.strictEqual(receipt.eventType, 'capability_evolution_closeout');
  assert.strictEqual(receipt.liveSendAttempted, false);
  assert.ok(receipt.contentPreview.includes('Capability Unlocked'));
  assert.ok(fs.existsSync(receiptPath));

  const liveReceipt = await dispatchCapabilityEvent({
    receiptPath: 'data/reports/discord/capability_evolution_feed/live_dispatch_blocked_receipt.json',
    mode: 'live',
  });

  assert.strictEqual(liveReceipt.ok, false);
  assert.strictEqual(liveReceipt.liveSendAttempted, true);
  assert.ok(liveReceipt.senderReceipt);
  assert.strictEqual(liveReceipt.senderReceipt.error, 'missing_or_invalid_webhook');

  console.log('liveCapabilityEventDispatcher.test.js PASS');
})();
