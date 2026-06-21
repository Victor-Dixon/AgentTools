const fs = require("fs");
const path = require("path");
const {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  Client,
  EmbedBuilder,
  GatewayIntentBits,
} = require("discord.js");

function envToken() {
  return process.env.DISCORD_BOT_TOKEN ||
    process.env.DISCORD_TOKEN ||
    process.env.FREERIDEINVESTOR_DISCORD_BOT_TOKEN ||
    "";
}

function findTextChannelByName(guild, name) {
  return guild.channels.cache.find((channel) => {
    return channel && channel.name === name && typeof channel.send === "function";
  });
}

function buildRows() {
  return [
    new ActionRowBuilder().addComponents(
      new ButtonBuilder().setCustomId("trading_cognition.refresh").setLabel("Refresh Read").setStyle(ButtonStyle.Primary),
      new ButtonBuilder().setCustomId("trading_cognition.mark_watched").setLabel("Mark Watched").setStyle(ButtonStyle.Secondary),
      new ButtonBuilder().setCustomId("trading_cognition.escalate").setLabel("Escalate").setStyle(ButtonStyle.Danger),
      new ButtonBuilder().setCustomId("trading_cognition.closeout").setLabel("Create Closeout").setStyle(ButtonStyle.Success)
    ),
  ];
}

async function main() {
  const token = envToken();
  if (!token) {
    console.error("DISCORD_TOKEN_MISSING=FAIL");
    process.exit(2);
  }

  const root = path.join(__dirname, "..", "..", "..");
  const payloadPath = path.join(root, "data", "reports", "trading", "live_cards", "latest_live_market_card_payload.json");
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  const rawEmbed = payload.embeds[0];

  const client = new Client({ intents: [GatewayIntentBits.Guilds] });

  client.once("clientReady", async () => {
    try {
      const guild = client.guilds.cache.first();
      if (!guild) throw new Error("No visible guilds");

      await guild.channels.fetch();

      const channel = findTextChannelByName(guild, "market-live");
      if (!channel) throw new Error("market-live channel not found or not sendable");

      const embed = new EmbedBuilder()
        .setTitle(rawEmbed.title)
        .setDescription(rawEmbed.description);

      for (const field of rawEmbed.fields || []) {
        embed.addFields({
          name: field.name,
          value: field.value || "none",
          inline: Boolean(field.inline),
        });
      }

      const message = await channel.send({
        embeds: [embed],
        components: buildRows(),
      });

      const report = {
        status: "pass",
        guild: guild.name,
        channel: channel.name,
        message_id: message.id,
        components: [
          "trading_cognition.refresh",
          "trading_cognition.mark_watched",
          "trading_cognition.escalate",
          "trading_cognition.closeout"
        ],
      };

      const outdir = path.join(root, "data", "reports", "trading", "live_cards");
      fs.mkdirSync(outdir, { recursive: true });
      fs.writeFileSync(path.join(outdir, "latest_interactive_market_card_post.json"), JSON.stringify(report, null, 2));

      console.log("INTERACTIVE_MARKET_CARD_POST=PASS");
      console.log(`GUILD=${guild.name}`);
      console.log(`CHANNEL=${channel.name}`);
      console.log(`MESSAGE_ID=${message.id}`);
    } catch (error) {
      console.error("INTERACTIVE_MARKET_CARD_POST=FAIL");
      console.error(error);
      process.exitCode = 1;
    } finally {
      await client.destroy();
    }
  });

  await client.login(token);
}

main().catch((error) => {
  console.error("INTERACTIVE_MARKET_CARD_POST=FAIL");
  console.error(error);
  process.exit(1);
});
