const fs = require('fs');
const path = require('path');

function nowIso() {
  return new Date().toISOString();
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function writeJson(filePath, data) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function validateWebhookUrl(url) {
  return typeof url === 'string'
    && url.startsWith('https://discord.com/api/webhooks/');
}

async function sendWebhookMessage(input = {}) {
  const mode = input.mode || process.env.DISCORD_DISPATCH_MODE || 'dry-run';

  const receipt = {
    ok: true,
    mode,
    sentAt: nowIso(),
    webhookConfigured: false,
    liveSendAttempted: false,
    messageLength: String(input.content || '').length,
    route: input.route || 'master-task-log',
  };

  const routeKey = String(input.route || 'master-task-log').replace(/-/g, '_');
  const routeEnv = `DISCORD_${routeKey.toUpperCase()}_WEBHOOK`;
  let receiptWebhook = null;

  try {
    const receiptPath = `data/reports/discord_architect/webhooks/${routeKey}_webhook_receipt.json`;
    receiptWebhook = JSON.parse(fs.readFileSync(receiptPath, 'utf8')).webhookUrl;
  } catch {}

  if (!receiptWebhook && input.route === 'master-task-log') {
    try {
      receiptWebhook = JSON.parse(
        fs.readFileSync('data/reports/discord_architect/live_master_task_log_webhook.json', 'utf8')
      ).url;
    } catch {}
  }

  const webhookUrl =
    input.webhookUrl ||
    process.env[routeEnv] ||
    receiptWebhook ||
    process.env.DISCORD_MASTER_TASK_LOG_WEBHOOK ||
    process.env.DISCORD_WEBHOOK_URL;

  if (!validateWebhookUrl(webhookUrl || '')) {
    receipt.ok = false;
    receipt.error = 'missing_or_invalid_webhook';
    return receipt;
  }

  receipt.webhookConfigured = true;

  if (mode === 'dry-run') {
    receipt.simulated = true;
    receipt.preview = String(input.content || '').slice(0, 300);

    writeJson(
      'data/reports/discord_architect/latest_webhook_dispatch_receipt.json',
      receipt
    );

    return receipt;
  }

  receipt.liveSendAttempted = true;

  const body = {
    content: String(input.content || ''),
  };

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    receipt.httpStatus = response.status;
    receipt.ok = response.ok;

    if (!response.ok) {
      receipt.error = await response.text();
    }

  } catch (err) {
    receipt.ok = false;
    receipt.error = String(err);
  }

  writeJson(
    'data/reports/discord_architect/latest_webhook_dispatch_receipt.json',
    receipt
  );

  return receipt;
}

module.exports = {
  validateWebhookUrl,
  sendWebhookMessage,
};
