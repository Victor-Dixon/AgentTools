const assert = require('assert');

const {
  validateWebhookUrl,
  sendWebhookMessage,
} = require('../src/runtime/liveDiscordRestSender');

assert.strictEqual(
  validateWebhookUrl(
    'DISCORD_WEBHOOK_URL_PLACEHOLDER_DO_NOT_USE'
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
    webhookUrl: 'DISCORD_WEBHOOK_URL_PLACEHOLDER_DO_NOT_USE',
  });

  assert.strictEqual(dry.ok, true);
  assert.strictEqual(dry.simulated, true);
  assert.strictEqual(dry.webhookConfigured, true);

  console.log('liveDiscordRestSender.test.js PASS');
})();
