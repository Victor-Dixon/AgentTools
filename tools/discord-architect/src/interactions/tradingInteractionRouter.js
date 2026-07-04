async function handleTradingInteraction(interaction) {
  const action = interaction.customId;

  switch (action) {
    case "trading.refresh":
      return {
        status: "refresh_requested"
      };

    case "trading.watch":
      return {
        status: "watch_registered"
      };

    case "trading.escalate":
      return {
        status: "escalation_created"
      };

    case "trading.closeout":
      return {
        status: "closeout_created"
      };

    default:
      return {
        status: "unknown_action"
      };
  }
}

module.exports = {
  handleTradingInteraction
};
