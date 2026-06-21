const fs = require("fs");
const path = require("path");
const { Client, GatewayIntentBits, EmbedBuilder } = require("discord.js");

function envToken() {
  return process.env.DISCORD_BOT_TOKEN ||
    process.env.DISCORD_TOKEN ||
    process.env.FREERIDEINVESTOR_DISCORD_BOT_TOKEN ||
    "";
}

function findTextChannelByName(guild, name) {
  return guild.channels.cache.find((channel) => {
    return channel &&
      channel.name === name &&
      typeof channel.send === "function";
  });
}

async function main() {
  const token = envToken();
  if (!token) {
    console.error("DISCORD_TOKEN_MISSING=FAIL");
    process.exit(2);
  }

  const root = path.join(__dirname, "..", "..", "..");
  const payloadPath = path.join(
    root,
    "data",
    "reports",
    "trading",
    "live_cards",
    "latest_live_market_card_payload.json"
  );

  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  const rawEmbed = payload.embeds[0];

  const client = new Client({
    intents: [GatewayIntentBits.Guilds],
  });

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
        username: payload.username,
        embeds: [embed],
      });

      console.log("BOT_MARKET_CARD_POST=PASS");
      console.log(`GUILD=${guild.name}`);
      console.log(`CHANNEL=${channel.name}`);
      console.log(`MESSAGE_ID=${message.id}`);
    } catch (error) {
      console.error("BOT_MARKET_CARD_POST=FAIL");
      console.error(error);
      process.exitCode = 1;
    } finally {
      await client.destroy();
    }
  });

  await client.login(token);
}

main().catch((error) => {
  console.error("BOT_MARKET_CARD_POST=FAIL");
  console.error(error);
  process.exit(1);
});
