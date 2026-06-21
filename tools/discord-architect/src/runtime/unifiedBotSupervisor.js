const fs = require('fs');
const path = require('path');

const DEFAULT_REGISTRY = 'discord_architect/data/runtime/bot_plugin_registry.json';
const DEFAULT_EVENT_LOG = 'data/reports/discord_architect/unified_event_bus/events.jsonl';

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function readJson(filePath, fallback) {
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

function appendJsonl(filePath, row) {
  ensureDir(filePath);
  fs.appendFileSync(filePath, JSON.stringify(row) + '\n');
}

function defaultRegistry() {
  return {
    version: 1,
    supervisor: 'discord_architect',
    policy: {
      one_control_plane: true,
      plugins_not_terminals: true,
      discord_and_websites_share_event_bus: true
    },
    plugins: [
      {
        id: 'capability_evolution_feed',
        type: 'discord_feed',
        status: 'enabled',
        entrypoint: 'discord_architect/src/runtime/liveCapabilityEventDispatcher.js',
        outputs: ['discord:master-task-log']
      },
      {
        id: 'trading_tool',
        type: 'project_bot_plugin',
        status: 'planned',
        entrypoint: 'runtime/scripts/trading',
        outputs: ['discord:trading', 'website:trading']
      },
      {
        id: 'public_website_event_bridge',
        type: 'website_bridge',
        status: 'planned',
        entrypoint: 'data/public/events/latest.json',
        outputs: ['website:weareswarm', 'website:dadudekc']
      }
    ]
  };
}

function ensureRegistry(registryPath = DEFAULT_REGISTRY) {
  const existing = readJson(registryPath, null);
  if (existing) return existing;

  const registry = defaultRegistry();
  writeJson(registryPath, registry);
  return registry;
}

function emitSupervisorEvent(event, options = {}) {
  const eventLog = options.eventLog || DEFAULT_EVENT_LOG;
  const row = {
    ts: new Date().toISOString(),
    source: event.source || 'discord_architect',
    type: event.type || 'runtime_event',
    visibility: event.visibility || 'internal',
    discordTargets: event.discordTargets || [],
    websiteTargets: event.websiteTargets || [],
    payload: event.payload || {}
  };

  appendJsonl(eventLog, row);
  return row;
}

function buildPublicWebsiteSnapshot(options = {}) {
  const eventLog = options.eventLog || DEFAULT_EVENT_LOG;
  const outPath = options.outPath || 'data/public/events/latest.json';

  const lines = fs.existsSync(eventLog)
    ? fs.readFileSync(eventLog, 'utf8').trim().split('\n').filter(Boolean)
    : [];

  const events = lines.slice(-25).map((line) => JSON.parse(line));

  const snapshot = {
    generated_at: new Date().toISOString(),
    event_count: events.length,
    events
  };

  writeJson(outPath, snapshot);
  return snapshot;
}

module.exports = {
  DEFAULT_REGISTRY,
  DEFAULT_EVENT_LOG,
  ensureRegistry,
  emitSupervisorEvent,
  buildPublicWebsiteSnapshot
};
