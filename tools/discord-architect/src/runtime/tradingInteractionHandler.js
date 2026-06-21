const fs = require("fs");
const path = require("path");
const {
  Client,
  GatewayIntentBits,
  Events,
} = require("discord.js");

function envToken() {
  return process.env.DISCORD_BOT_TOKEN ||
    process.env.DISCORD_TOKEN ||
    process.env.FREERIDEINVESTOR_DISCORD_BOT_TOKEN ||
    "";
}

function writeInteractionReport(event) {
  const root = path.join(__dirname, "..", "..", "..");
  const outdir = path.join(root, "data", "reports", "trading", "interactions");
  fs.mkdirSync(outdir, { recursive: true });

  const file = path.join(outdir, "latest_trading_button_interaction.json");
  fs.writeFileSync(file, JSON.stringify(event, null, 2));
  return file;
}

function resolveAction(customId) {
  if (customId === "trading_cognition.refresh") {
    return {
      title: "Refresh queued",
      response: "Refresh request captured. Next lane should rerun cognition engines and edit the card.",
      status: "refresh_requested",
    };
  }

  if (customId === "trading_cognition.mark_watched") {
    return {
      title: "Marked watched",
      response: "Marked this trading cognition card as watched.",
      status: "watched",
    };
  }

  if (customId === "trading_cognition.escalate") {
    return {
      title: "Escalated",
      response: "Escalated this card for operator review.",
      status: "escalated",
    };
  }

  if (customId === "trading_cognition.closeout") {
    return {
      title: "Closeout requested",
      response: "Closeout request captured. Next lane should generate a trading closeout artifact.",
      status: "closeout_requested",
    };
  }

  return {
    title: "Unknown action",
    response: `Unknown trading action: ${customId}`,
    status: "unknown",
  };
}

async function main() {
  const token = envToken();
  if (!token) {
    console.error("DISCORD_TOKEN_MISSING=FAIL");
    process.exit(2);
  }

  const client = new Client({
    intents: [GatewayIntentBits.Guilds],
  });

  client.once(Events.ClientReady, () => {
    console.log("TRADING_INTERACTION_HANDLER_READY=PASS");
    console.log(`BOT=${client.user.tag}`);
  });

  client.on(Events.InteractionCreate, async (interaction) => {
    if (!interaction.isButton()) return;
    if (!interaction.customId.startsWith("trading_cognition.")) return;

    const action = resolveAction(interaction.customId);

    const event = {
      generated_at: new Date().toISOString(),
      custom_id: interaction.customId,
      status: action.status,
      guild_id: interaction.guildId || null,
      channel_id: interaction.channelId || null,
      message_id: interaction.message ? interaction.message.id : null,
      user_id: interaction.user ? interaction.user.id : null,
    };

    const reportPath = writeInteractionReport(event);

    await interaction.reply({
      content: `${action.title}: ${action.response}`,
      ephemeral: true,
    });

    console.log("TRADING_BUTTON_INTERACTION=PASS");
    console.log(`ACTION=${action.status}`);
    console.log(`REPORT=${reportPath}`);
  });

  await client.login(token);
}

main().catch((error) => {
  console.error("TRADING_INTERACTION_HANDLER=FAIL");
  console.error(error);
  process.exit(1);
});
