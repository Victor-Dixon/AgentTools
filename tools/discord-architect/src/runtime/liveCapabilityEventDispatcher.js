const fs = require('fs');
const path = require('path');
const { buildMasterTaskLogEvent } = require('./capabilityEvolutionFeedAdapter');
const { sendWebhookMessage } = require('./liveDiscordRestSender');

function nowIso() {
  return new Date().toISOString();
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function dispatchCapabilityEvent(options = {}) {
  const payloadPath = options.payloadPath || 'data/reports/discord/capability_evolution_feed/latest_capability_evolution_event.json';
  const receiptPath = options.receiptPath || 'data/reports/discord/capability_evolution_feed/latest_dispatch_receipt.json';
  const mode = options.mode || process.env.DISCORD_DISPATCH_MODE || 'dry-run';

  const event = options.event || buildMasterTaskLogEvent(payloadPath);

  const receipt = {
    ok: true,
    mode,
    dispatched_at: nowIso(),
    channelKey: event.channelKey || event.target_channel || 'master-task-log',
    eventType: event.eventType || event.event_type || 'generic_event',
    sourceTask: event.sourceTask || event.source || 'unknown',
    contentPreview: String(
      event.content ||
      event.summary ||
      JSON.stringify(event).slice(0, 500)
    ).slice(0, 500),
    liveSendAttempted: false,
    liveSendSupported: false,
  };

  if (mode === 'live') {
    receipt.liveSendAttempted = true;
    const content =
      event.content ||
      event.summary ||
      (event.title ? `📡 **${event.title}**\n${event.summary || ''}` : JSON.stringify(event));

    return sendWebhookMessage({
      content,
      mode: 'live',
      route: event.channelKey || event.target_channel || 'master-task-log',
    }).then((sendReceipt) => {
      receipt.ok = sendReceipt.ok;
      receipt.senderReceipt = sendReceipt;
      if (!sendReceipt.ok) {
        receipt.error = sendReceipt.error;
      }
      writeJson(receiptPath, receipt);
      return receipt;
    });
  }

  writeJson(receiptPath, receipt);
  return receipt;
}

if (require.main === module) {
  const receipt = dispatchCapabilityEvent();
  console.log(JSON.stringify(receipt, null, 2));
}

module.exports = {
  dispatchCapabilityEvent,
};
