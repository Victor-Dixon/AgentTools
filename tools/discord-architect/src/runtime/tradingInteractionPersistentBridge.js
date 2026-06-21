const sessionRegistry = require("./persistentSessionRegistry");
const mutationRuntime = require("../interactions/liveInteractionMutationRuntime");

function normalizeTradingAction(customId) {
  const suffix = String(customId || "").split(".").pop();

  if (suffix === "refresh") return "refresh";
  if (suffix === "watch" || suffix === "mark_watched") return "watch";
  if (suffix === "escalate") return "escalate";
  if (suffix === "closeout") return "closeout";

  return "unknown";
}

function inferTicker(interaction, fallback = "TSLA") {
  return interaction.ticker || fallback;
}

function ensureSessionForInteraction(interaction, options = {}) {
  const ticker = inferTicker(interaction, options.ticker || "TSLA");
  const messageId = interaction.message?.id || options.message_id || "unknown-message";
  const threadId = interaction.channel?.isThread?.() ? interaction.channel.id : options.thread_id || null;

  return sessionRegistry.upsertSession({
    domain: "trading",
    ticker,
    channel: options.channel || "market-live",
    message_id: messageId,
    thread_id: threadId,
    verdict: options.verdict || "unknown",
  });
}

function bridgeInteractionToPersistentSession(interaction, options = {}) {
  const ticker = inferTicker(interaction, options.ticker || "TSLA");
  const action = normalizeTradingAction(interaction.customId);
  const session = ensureSessionForInteraction(interaction, options);

  const event = mutationRuntime.buildInteractionEvent({
    ticker,
    action,
    message_id: session.message_id,
    thread_id: session.thread_id,
    operator: options.operator || interaction.user?.id || "operator",
  });

  const updated = sessionRegistry.appendSessionEvent("trading", ticker, event);

  return {
    status: "persistent_event_appended",
    ticker,
    action,
    session: updated,
    event,
  };
}

module.exports = {
  normalizeTradingAction,
  ensureSessionForInteraction,
  bridgeInteractionToPersistentSession,
};
