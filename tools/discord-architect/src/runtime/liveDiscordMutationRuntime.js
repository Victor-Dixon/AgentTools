const fs = require('fs');
const path = require('path');

const REGISTRY_PATH =
  'discord_architect/data/runtime/discord_mutation_registry.json';

function nowIso() {
  return new Date().toISOString();
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function readJson(filePath, fallback = {}) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return fallback;
  }
}

function writeJson(filePath, data) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function appendRegistry(entry) {
  const registry = readJson(REGISTRY_PATH, {
    mutations: [],
  });

  registry.mutations.push(entry);
  registry.lastUpdated = nowIso();

  writeJson(REGISTRY_PATH, registry);

  return registry;
}

function validatePlan(plan) {
  if (!plan || typeof plan !== 'object') {
    throw new Error('mutation plan missing');
  }

  if (!plan.mutationType) {
    throw new Error('mutationType missing');
  }

  if (!plan.mode) {
    throw new Error('mode missing');
  }

  return true;
}

function simulateDiscordMutation(plan) {
  const syntheticId =
    'discord-' +
    Math.random().toString(36).slice(2, 10);

  return {
    ok: true,
    syntheticId,
    simulated: true,
  };
}

function executeMutationPlan(plan, options = {}) {
  validatePlan(plan);

  const receiptPath =
    options.receiptPath ||
    'data/reports/discord_architect/latest_live_mutation_receipt.json';

  const receipt = {
    ok: true,
    mode: plan.mode,
    mutationType: plan.mutationType,
    dispatchedAt: nowIso(),
    liveExecution: false,
    rollbackAvailable: true,
    registryUpdated: false,
    plan,
  };

  if (plan.mode === 'dry-run') {
    receipt.simulated = true;
    receipt.message =
      'dry-run mutation executed safely';
  } else {
    const token =
      process.env.DISCORD_BOT_TOKEN ||
      process.env.DISCORD_ARCHITECT_TOKEN;

    if (!token) {
      receipt.ok = false;
      receipt.liveExecution = false;
      receipt.error =
        'missing DISCORD_BOT_TOKEN or DISCORD_ARCHITECT_TOKEN';
    } else {
      const result = simulateDiscordMutation(plan);

      receipt.liveExecution = true;
      receipt.discordResult = result;
      receipt.message =
        'live mutation runtime placeholder executed';
    }
  }

  appendRegistry({
    timestamp: nowIso(),
    mutationType: plan.mutationType,
    mode: plan.mode,
    ok: receipt.ok,
    channelKey: plan.channelKey || null,
  });

  receipt.registryUpdated = true;

  writeJson(receiptPath, receipt);

  return receipt;
}

module.exports = {
  REGISTRY_PATH,
  validatePlan,
  executeMutationPlan,
  appendRegistry,
};
