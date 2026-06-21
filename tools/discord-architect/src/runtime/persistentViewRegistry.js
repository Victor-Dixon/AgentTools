const registry = new Map();

function registerPersistentView(messageId, payload) {
  registry.set(messageId, payload);
}

function getPersistentView(messageId) {
  return registry.get(messageId);
}

function getPersistentViewCount() {
  return registry.size;
}

module.exports = {
  registerPersistentView,
  getPersistentView,
  getPersistentViewCount
};
