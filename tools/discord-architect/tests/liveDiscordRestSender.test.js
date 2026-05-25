const assert = require('assert');

const {
  validateWebhookUrl,
  sendWebhookMessage,
} = require('../src/runtime/liveDiscordRestSender');

assert.strictEqual(
  validateWebhookUrl(
    'https://discord.com/api/webhooks/123/test'
  ),
  true
);

assert.strictEqual(
  validateWebhookUrl('https://example.com/nope'),
  false
);

(async () => {
  const invalid = await sendWebhookMessage({
    content: 'hello',
    mode: 'dry-run',
    webhookUrl: '',
  });

  assert.strictEqual(invalid.ok, false);
  assert.strictEqual(invalid.error, 'missing_or_invalid_webhook');

  const dry = await sendWebhookMessage({
    content: 'Dream.OS capability evolution event',
    mode: 'dry-run',
    webhookUrl: 'https://discord.com/api/webhooks/123/test',
  });

  assert.strictEqual(dry.ok, true);
  assert.strictEqual(dry.simulated, true);
  assert.strictEqual(dry.webhookConfigured, true);

  console.log('liveDiscordRestSender.test.js PASS');
})();
