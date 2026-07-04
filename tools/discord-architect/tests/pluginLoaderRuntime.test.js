const assert = require('assert');
const fs = require('fs');

const {
  loadRegistry,
  bootPlugins,
  setPluginStatus,
  evaluatePlugin,
} = require('../src/runtime/pluginLoaderRuntime');

const registryPath = 'discord_architect/data/runtime/test_plugin_loader_registry.json';
const reportPath = 'data/reports/discord_architect/plugin_loader_runtime/test_plugin_boot_report.json';

fs.mkdirSync('discord_architect/data/runtime', { recursive: true });

fs.writeFileSync(registryPath, JSON.stringify({
  version: 1,
  supervisor: 'discord_architect',
  plugins: [
    {
      id: 'capability_evolution_feed',
      type: 'discord_feed',
      status: 'enabled',
      entrypoint: 'discord_architect/src/runtime/liveCapabilityEventDispatcher.js',
      outputs: ['discord:master-task-log'],
      loadPolicy: 'manifest_only'
    },
    {
      id: 'trading_tool',
      type: 'project_bot_plugin',
      status: 'planned',
      entrypoint: 'runtime/scripts/trading',
      outputs: ['discord:trading']
    }
  ]
}, null, 2));

const registry = loadRegistry(registryPath);
assert.strictEqual(registry.plugins.length, 2);

const evalResult = evaluatePlugin(registry.plugins[0]);
assert.strictEqual(evalResult.loadable, true);

const report = bootPlugins({ registryPath, reportPath });
assert.strictEqual(report.pluginCount, 2);
assert.strictEqual(report.enabledCount, 1);
assert.strictEqual(report.loadedCount, 1);
assert.strictEqual(report.failedCount, 0);
assert.ok(fs.existsSync(reportPath));

setPluginStatus('trading_tool', 'enabled', { registryPath });
const updated = loadRegistry(registryPath);
assert.strictEqual(
  updated.plugins.find((p) => p.id === 'trading_tool').status,
  'enabled'
);

console.log('pluginLoaderRuntime.test.js PASS');
