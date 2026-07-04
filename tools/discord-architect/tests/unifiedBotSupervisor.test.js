const assert = require('assert');
const fs = require('fs');

const {
  ensureRegistry,
  emitSupervisorEvent,
  buildPublicWebsiteSnapshot
} = require('../src/runtime/unifiedBotSupervisor');

const registryPath = 'discord_architect/data/runtime/test_bot_plugin_registry.json';
const eventLog = 'data/reports/discord_architect/unified_event_bus/test_events.jsonl';
const websiteOut = 'data/public/events/test_latest.json';

const registry = ensureRegistry(registryPath);
assert.strictEqual(registry.supervisor, 'discord_architect');
assert.strictEqual(registry.policy.one_control_plane, true);
assert.ok(registry.plugins.length >= 3);

const event = emitSupervisorEvent({
  type: 'capability_unlocked',
  visibility: 'public',
  discordTargets: ['master-task-log'],
  websiteTargets: ['weareswarm'],
  payload: {
    title: 'Unified Bot Supervisor',
    summary: 'Discord Architect now supervises plugins instead of requiring many terminals.'
  }
}, { eventLog });

assert.strictEqual(event.type, 'capability_unlocked');
assert.ok(fs.existsSync(eventLog));

const snapshot = buildPublicWebsiteSnapshot({
  eventLog,
  outPath: websiteOut
});

assert.strictEqual(snapshot.event_count, 1);
assert.ok(fs.existsSync(websiteOut));

console.log('unifiedBotSupervisor.test.js PASS');
