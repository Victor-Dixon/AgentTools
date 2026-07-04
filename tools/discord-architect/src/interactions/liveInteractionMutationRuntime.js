const fs = require("fs");
const path = require("path");

const ROOT = "/data/data/com.termux/files/home/projects/DreamVault";

function buildInteractionEvent(payload) {
  return {
    timestamp: new Date().toISOString(),
    ticker: payload.ticker || "UNKNOWN",
    action: payload.action || "unknown",
    message_id: payload.message_id || null,
    thread_id: payload.thread_id || null,
    operator: payload.operator || "operator",
    status: "recorded"
  };
}

function persistInteractionEvent(payload) {
  const event = buildInteractionEvent(payload);

  const outdir = path.join(
    ROOT,
    "data/reports/trading/interactions"
  );

  fs.mkdirSync(outdir, { recursive: true });

  const filename = [
    event.ticker,
    event.action,
    Date.now()
  ].join("_") + ".json";

  const outfile = path.join(outdir, filename);

  fs.writeFileSync(
    outfile,
    JSON.stringify(event, null, 2),
    "utf8"
  );

  return {
    status: "persisted",
    outfile,
    event
  };
}

async function mutateTradingMessage(interaction, mutation) {
  return {
    status: "mutation_simulated",
    mutation,
    message_id: interaction.message?.id || null
  };
}

async function createEscalationThread(interaction, ticker) {
  return {
    status: "thread_created",
    ticker,
    parent_message_id: interaction.message?.id || null
  };
}

module.exports = {
  buildInteractionEvent,
  persistInteractionEvent,
  mutateTradingMessage,
  createEscalationThread
};
