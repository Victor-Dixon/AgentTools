const fs = require('fs');
const path = require('path');

const {
  bootPlugins,
  loadRegistry,
} = require('./pluginLoaderRuntime');

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function writeJson(filePath, data) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function nowIso() {
  return new Date().toISOString();
}

class SupervisorDaemon {
  constructor(options = {}) {
    this.registryPath =
      options.registryPath ||
      'discord_architect/data/runtime/bot_plugin_registry.json';

    this.healthPath =
      options.healthPath ||
      'data/reports/discord_architect/runtime_health/runtime_health_snapshot.json';

    this.eventLog =
      options.eventLog ||
      'data/reports/discord_architect/runtime_health/runtime_events.jsonl';

    this.intervalMs = options.intervalMs || 30000;

    this.running = false;
    this.loopHandle = null;
    this.cycles = 0;
  }

  emitEvent(event) {
    ensureDir(this.eventLog);

    fs.appendFileSync(
      this.eventLog,
      JSON.stringify({
        ts: nowIso(),
        ...event,
      }) + '\n'
    );
  }

  collectHealth() {
    const registry = loadRegistry(this.registryPath);

    const pluginSummary = registry.plugins.map((plugin) => ({
      id: plugin.id,
      status: plugin.status,
      type: plugin.type,
      outputs: plugin.outputs || [],
    }));

    return {
      generatedAt: nowIso(),
      supervisor: 'discord_architect',
      pluginCount: pluginSummary.length,
      enabledCount: pluginSummary.filter(
        (p) => p.status === 'enabled'
      ).length,
      plugins: pluginSummary,
    };
  }

  runCycle() {
    const boot = bootPlugins({
      registryPath: this.registryPath,
    });

    const health = this.collectHealth();

    const snapshot = {
      cycle: this.cycles + 1,
      daemonRunning: this.running,
      boot,
      health,
    };

    writeJson(this.healthPath, snapshot);

    this.emitEvent({
      type: 'supervisor_cycle',
      pluginCount: health.pluginCount,
      enabledCount: health.enabledCount,
      loadedCount: boot.loadedCount,
      failedCount: boot.failedCount,
    });

    this.cycles += 1;

    return snapshot;
  }

  start() {
    if (this.running) {
      return {
        ok: false,
        error: 'already_running',
      };
    }

    this.running = true;

    const first = this.runCycle();

    this.loopHandle = setInterval(() => {
      try {
        this.runCycle();
      } catch (err) {
        this.emitEvent({
          type: 'daemon_error',
          error: String(err),
        });
      }
    }, this.intervalMs);

    return {
      ok: true,
      startedAt: nowIso(),
      firstCycle: first,
    };
  }

  stop() {
    if (this.loopHandle) {
      clearInterval(this.loopHandle);
    }

    this.running = false;

    this.emitEvent({
      type: 'daemon_stopped',
    });

    return {
      ok: true,
      stoppedAt: nowIso(),
      cycles: this.cycles,
    };
  }
}

module.exports = {
  SupervisorDaemon,
};
