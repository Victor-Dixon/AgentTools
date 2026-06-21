const fs = require('fs');
const path = require('path');

const DEFAULT_REGISTRY =
  'discord_architect/data/runtime/bot_plugin_registry.json';

function nowIso() {
  return new Date().toISOString();
}

function readJson(filePath, fallback = null) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return fallback;
  }
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function normalizePlugin(plugin) {
  return {
    id: plugin.id,
    type: plugin.type || 'unknown',
    status: plugin.status || 'disabled',
    entrypoint: plugin.entrypoint || null,
    outputs: plugin.outputs || [],
    loadPolicy: plugin.loadPolicy || 'manifest_only',
  };
}

function loadRegistry(registryPath = DEFAULT_REGISTRY) {
  const registry = readJson(registryPath, {
    version: 1,
    supervisor: 'discord_architect',
    plugins: [],
  });

  return {
    ...registry,
    plugins: (registry.plugins || []).map(normalizePlugin),
  };
}

function evaluatePlugin(plugin) {
  const enabled = plugin.status === 'enabled';
  const hasEntrypoint = Boolean(plugin.entrypoint);

  return {
    id: plugin.id,
    type: plugin.type,
    status: plugin.status,
    enabled,
    hasEntrypoint,
    outputs: plugin.outputs,
    loadable: enabled && hasEntrypoint,
    loaded: false,
    error: null,
  };
}

function bootPlugins(options = {}) {
  const registryPath = options.registryPath || DEFAULT_REGISTRY;
  const reportPath =
    options.reportPath ||
    'data/reports/discord_architect/plugin_loader_runtime/plugin_boot_report.json';

  const registry = loadRegistry(registryPath);

  const plugins = registry.plugins.map((plugin) => {
    const result = evaluatePlugin(plugin);

    if (!result.loadable) {
      return result;
    }

    if (plugin.loadPolicy === 'manifest_only') {
      result.loaded = true;
      result.mode = 'manifest_only';
      return result;
    }

    try {
      require(path.resolve(plugin.entrypoint));
      result.loaded = true;
      result.mode = 'require';
    } catch (err) {
      result.loaded = false;
      result.error = String(err);
    }

    return result;
  });

  const report = {
    bootedAt: nowIso(),
    supervisor: registry.supervisor || 'discord_architect',
    pluginCount: plugins.length,
    enabledCount: plugins.filter((p) => p.enabled).length,
    loadedCount: plugins.filter((p) => p.loaded).length,
    failedCount: plugins.filter((p) => p.error).length,
    plugins,
  };

  writeJson(reportPath, report);
  return report;
}

function setPluginStatus(pluginId, status, options = {}) {
  const registryPath = options.registryPath || DEFAULT_REGISTRY;
  const registry = loadRegistry(registryPath);

  let found = false;

  registry.plugins = registry.plugins.map((plugin) => {
    if (plugin.id === pluginId) {
      found = true;
      return { ...plugin, status };
    }
    return plugin;
  });

  if (!found) {
    throw new Error(`plugin not found: ${pluginId}`);
  }

  writeJson(registryPath, registry);
  return registry;
}

module.exports = {
  DEFAULT_REGISTRY,
  loadRegistry,
  bootPlugins,
  setPluginStatus,
  evaluatePlugin,
};
