const {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle
} = require("discord.js");

function buildTradingCommandDeckRow() {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId("trading.refresh")
      .setLabel("Refresh")
      .setStyle(ButtonStyle.Primary),

    new ButtonBuilder()
      .setCustomId("trading.watch")
      .setLabel("Watch")
      .setStyle(ButtonStyle.Secondary),

    new ButtonBuilder()
      .setCustomId("trading.escalate")
      .setLabel("Escalate")
      .setStyle(ButtonStyle.Danger),

    new ButtonBuilder()
      .setCustomId("trading.closeout")
      .setLabel("Closeout")
      .setStyle(ButtonStyle.Success)
  );
}

module.exports = {
  buildTradingCommandDeckRow
};
