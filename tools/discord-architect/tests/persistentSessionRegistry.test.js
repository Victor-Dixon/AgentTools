const assert = require("assert");
const fs = require("fs");

const registry = require("../src/runtime/persistentSessionRegistry");

if (fs.existsSync(registry.STATE_FILE)) {
  fs.unlinkSync(registry.STATE_FILE);
}

const session = registry.upsertSession({
  domain: "trading",
  ticker: "TSLA",
  channel: "market-live",
  message_id: "msg-persist-1",
  thread_id: "thread-persist-1",
  verdict: "mixed_consolidation",
});

assert.equal(session.ticker, "TSLA");
assert.equal(session.message_id, "msg-persist-1");

const loaded = registry.getSession("trading", "TSLA");
assert.equal(loaded.thread_id, "thread-persist-1");

registry.appendSessionEvent("trading", "TSLA", {
  action: "refresh",
  status: "requested",
});

registry.appendSessionEvent("trading", "TSLA", {
  action: "watch",
  status: "registered",
});

const replay = registry.replaySession("trading", "TSLA");
assert.equal(replay.length, 2);
assert.equal(replay[0].action, "refresh");
assert.equal(replay[1].action, "watch");

const reloaded = registry.loadSessions();
assert(reloaded["trading:TSLA"]);
assert.equal(reloaded["trading:TSLA"].events.length, 2);

console.log("persistentSessionRegistry.test.js PASS");
