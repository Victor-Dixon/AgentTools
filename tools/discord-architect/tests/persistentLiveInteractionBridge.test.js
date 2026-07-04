const assert = require("assert");
const fs = require("fs");

const sessionRegistry = require("../src/runtime/persistentSessionRegistry");
const bridge = require("../src/runtime/tradingInteractionPersistentBridge");

if (fs.existsSync(sessionRegistry.STATE_FILE)) {
  fs.unlinkSync(sessionRegistry.STATE_FILE);
}

const interaction = {
  customId: "trading_cognition.refresh",
  message: { id: "msg-live-bridge-1" },
  user: { id: "operator-1" },
};

const result = bridge.bridgeInteractionToPersistentSession(interaction, {
  ticker: "TSLA",
  channel: "market-live",
  verdict: "mixed_consolidation",
});

assert.equal(result.status, "persistent_event_appended");
assert.equal(result.action, "refresh");
assert.equal(result.ticker, "TSLA");

const session = sessionRegistry.getSession("trading", "TSLA");
assert(session);
assert.equal(session.message_id, "msg-live-bridge-1");
assert.equal(session.events.length, 1);
assert.equal(session.events[0].action, "refresh");

assert.equal(bridge.normalizeTradingAction("trading_cognition.mark_watched"), "watch");
assert.equal(bridge.normalizeTradingAction("trading.closeout"), "closeout");

console.log("persistentLiveInteractionBridge.test.js PASS");
