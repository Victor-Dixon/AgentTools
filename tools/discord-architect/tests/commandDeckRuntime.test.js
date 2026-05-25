const assert = require("assert");

const {
  buildTradingCommandDeckRow,
} = require("../src/views/TradingCommandDeckView");

const {
  registerPersistentView,
  getPersistentView,
  getPersistentViewCount,
} = require("../src/runtime/persistentViewRegistry");

const {
  handleTradingInteraction,
} = require("../src/interactions/tradingInteractionRouter");

const mutationRuntime = require("../src/interactions/liveInteractionMutationRuntime");

function fakeInteraction(customId = "trading.refresh") {
  return {
    customId,
    message: {
      id: "msg-test-1",
    },
  };
}

async function main() {
  const row = buildTradingCommandDeckRow();
  assert(row, "command deck row missing");
  assert.equal(row.components.length, 4);

  const customIds = row.components.map((component) => component.data.custom_id);
  assert.deepEqual(customIds, [
    "trading.refresh",
    "trading.watch",
    "trading.escalate",
    "trading.closeout",
  ]);

  registerPersistentView("msg-test-1", {
    ticker: "TSLA",
    channel: "market-live",
  });

  assert.equal(getPersistentView("msg-test-1").ticker, "TSLA");
  assert(getPersistentViewCount() >= 1);

  assert.equal(
    (await handleTradingInteraction(fakeInteraction("trading.refresh"))).status,
    "refresh_requested"
  );

  assert.equal(
    (await handleTradingInteraction(fakeInteraction("trading.watch"))).status,
    "watch_registered"
  );

  assert.equal(
    (await handleTradingInteraction(fakeInteraction("trading.escalate"))).status,
    "escalation_created"
  );

  assert.equal(
    (await handleTradingInteraction(fakeInteraction("trading.closeout"))).status,
    "closeout_created"
  );

  const event = mutationRuntime.buildInteractionEvent({
    ticker: "TSLA",
    action: "refresh",
    message_id: "msg-test-1",
    operator: "tester",
  });

  assert.equal(event.ticker, "TSLA");
  assert.equal(event.action, "refresh");
  assert.equal(event.status, "recorded");

  const persisted = mutationRuntime.persistInteractionEvent({
    ticker: "TSLA",
    action: "watch",
    message_id: "msg-test-1",
    operator: "tester",
  });

  assert.equal(persisted.status, "persisted");
  assert(persisted.outfile.includes("data/reports/trading/interactions"));

  console.log("commandDeckRuntime.test.js PASS");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
