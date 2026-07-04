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

function normalizeChannelName(name) {
  return String(name || '')
    .trim()
    .toLowerCase()
    .replace(/^#/, '')
    .replace(/[^a-z0-9-_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function buildChannelMutationPlan(input = {}) {
  const channelName = normalizeChannelName(input.name || input.channelName);
  if (!channelName) {
    throw new Error('channel name is required');
  }

  return {
    mutationType: 'channel.ensure',
    mode: input.mode || 'dry-run',
    guildId: input.guildId || process.env.DISCORD_GUILD_ID || null,
    channelKey: input.channelKey || channelName,
    channelName,
    channelType: input.channelType || 'GUILD_TEXT',
    parentKey: input.parentKey || null,
    topic: input.topic || '',
    reason: input.reason || 'Dream.OS governed channel ensure',
    createdAt: nowIso(),
  };
}

function buildWebhookMutationPlan(input = {}) {
  const channelId = input.channelId || process.env.DISCORD_CHANNEL_ID || null;
  const channelKey = input.channelKey || null;
  const webhookName = input.webhookName || input.name || 'Dream.OS Capability Feed';

  if (!channelId && !channelKey) {
    throw new Error('channelId or channelKey is required');
  }

  return {
    mutationType: 'webhook.ensure',
    mode: input.mode || 'dry-run',
    guildId: input.guildId || process.env.DISCORD_GUILD_ID || null,
    channelId,
    channelKey,
    webhookName,
    reason: input.reason || 'Dream.OS governed webhook ensure',
    createdAt: nowIso(),
  };
}

function dispatchMutationPlan(plan, options = {}) {
  const receiptPath =
    options.receiptPath ||
    'data/reports/discord_architect/channel_webhook_manager/latest_mutation_receipt.json';

  const receipt = {
    ok: true,
    mode: plan.mode || 'dry-run',
    mutationType: plan.mutationType,
    liveMutationAttempted: false,
    liveMutationSupported: false,
    plan,
    dispatchedAt: nowIso(),
  };

  if (plan.mode === 'live') {
    receipt.ok = false;
    receipt.liveMutationAttempted = true;
    receipt.error = 'live Discord mutation sender not configured in this lane';
  }

  writeJson(receiptPath, receipt);
  return receipt;
}

function ensureChannel(input = {}, options = {}) {
  const plan = buildChannelMutationPlan(input);
  return dispatchMutationPlan(plan, options);
}

function ensureWebhook(input = {}, options = {}) {
  const plan = buildWebhookMutationPlan(input);
  return dispatchMutationPlan(plan, options);
}

module.exports = {
  normalizeChannelName,
  buildChannelMutationPlan,
  buildWebhookMutationPlan,
  dispatchMutationPlan,
  ensureChannel,
  ensureWebhook,
};
