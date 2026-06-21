const assert = require('assert');
const fs = require('fs');

const {
  SupervisorDaemon
} = require('../src/runtime/supervisorDaemon');

const registryPath =
  'discord_architect/data/runtime/test_supervisor_registry.json';

const healthPath =
  'data/reports/discord_architect/runtime_health/test_runtime_health_snapshot.json';

const eventLog =
  'data/reports/discord_architect/runtime_health/test_runtime_events.jsonl';

fs.mkdirSync(
  'discord_architect/data/runtime',
  { recursive: true }
);

fs.writeFileSync(
  registryPath,
  JSON.stringify({
    version: 1,
    supervisor: 'discord_architect',
    plugins: [
      {
        id: 'capability_feed',
        type: 'discord_feed',
        status: 'enabled',
        entrypoint: 'discord_architect/src/runtime/liveCapabilityEventDispatcher.js',
        outputs: ['discord:master-task-log'],
        loadPolicy: 'manifest_only'
      }
    ]
  }, null, 2)
);

const daemon = new SupervisorDaemon({
  registryPath,
  healthPath,
  eventLog,
  intervalMs: 1000,
});

const start = daemon.start();

assert.strictEqual(start.ok, true);
assert.ok(fs.existsSync(healthPath));
assert.ok(fs.existsSync(eventLog));

const snapshot = JSON.parse(
  fs.readFileSync(healthPath, 'utf8')
);

assert.strictEqual(snapshot.health.pluginCount, 1);
assert.strictEqual(snapshot.boot.loadedCount, 1);

const stop = daemon.stop();

assert.strictEqual(stop.ok, true);

console.log('supervisorDaemon.test.js PASS');
