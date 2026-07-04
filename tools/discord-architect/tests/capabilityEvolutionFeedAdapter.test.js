const assert = require('assert');
const {
  buildMasterTaskLogEvent,
  renderCapabilityMessage,
} = require('../src/runtime/capabilityEvolutionFeedAdapter');

const payloadPath = 'data/reports/discord/capability_evolution_feed/latest_capability_evolution_event.json';

const event = buildMasterTaskLogEvent(payloadPath);

assert.strictEqual(event.channelKey, 'master-task-log');
assert.strictEqual(event.eventType, 'capability_evolution_closeout');
assert.ok(event.content.includes('Capability Unlocked'));
assert.ok(event.content.includes('Why this matters'));
assert.ok(event.content.includes('Unlocked capabilities'));
assert.ok(event.content.includes('Unlocks next'));

const rendered = renderCapabilityMessage({
  title: 'Test Capability',
  source_task: 'test_task_001',
  channel_key: 'master-task-log',
  capability_unlocks: ['test_unlock'],
  unlocks_following_tasks: ['next_task'],
  why_this_matters: 'It proves rendering works.',
  commit: '1234567890abcdef'
});

assert.ok(rendered.includes('Test Capability'));
assert.ok(rendered.includes('test_unlock'));
assert.ok(rendered.includes('next_task'));
assert.ok(rendered.includes('12345678'));

console.log('capabilityEvolutionFeedAdapter.test.js PASS');
