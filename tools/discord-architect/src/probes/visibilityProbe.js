const fs = require("fs");
const path = require("path");
const { Client, GatewayIntentBits, Partials } = require("discord.js");

function envToken() {
  return process.env.DISCORD_BOT_TOKEN || process.env.DISCORD_TOKEN || process.env.FREERIDEINVESTOR_DISCORD_BOT_TOKEN || "";
}

function safeMessage(message) {
  return {
    id: message.id,
    author_id: message.author ? message.author.id : null,
    author_bot: message.author ? message.author.bot : null,
    created_timestamp: message.createdTimestamp || null,
    content_preview: message.content ? message.content.slice(0, 160) : "",
    has_content: Boolean(message.content),
    attachments: message.attachments ? message.attachments.size : 0,
    embeds: message.embeds ? message.embeds.length : 0,
  };
}

async function probe() {
  const token = envToken();
  if (!token) {
    console.error("DISCORD_TOKEN_MISSING=FAIL");
    process.exit(2);
  }

  const client = new Client({
    intents: [
      GatewayIntentBits.Guilds,
      // Message content is privileged. Channel-only probe avoids disallowed intents.
      GatewayIntentBits.GuildMessages,
    ],
    partials: [Partials.Channel],
  });

  const report = {
    generated_at: new Date().toISOString(),
    bot_user: null,
    guilds: [],
  };

  client.once("ready", async () => {
    report.bot_user = {
      id: client.user.id,
      tag: client.user.tag,
    };

    for (const guild of client.guilds.cache.values()) {
      const guildEntry = {
        id: guild.id,
        name: guild.name,
        owner_id: guild.ownerId || null,
        channels: [],
      };

      let channels;
      try {
        channels = await guild.channels.fetch();
      } catch (error) {
        guildEntry.channel_fetch_error = String(error.message || error);
        report.guilds.push(guildEntry);
        continue;
      }

      for (const channel of channels.values()) {
        if (!channel) continue;

        const channelEntry = {
          id: channel.id,
          name: channel.name || null,
          type: channel.type,
          parent_id: channel.parentId || null,
          message_probe: {
            attempted: false,
            status: "not_text_or_not_fetchable",
            messages: [],
          },
        };

        if (typeof channel.messages?.fetch === "function") {
          channelEntry.message_probe.attempted = true;
          try {
            const messages = await channel.messages.fetch({ limit: 5 });
            channelEntry.message_probe.status = "pass";
            channelEntry.message_probe.messages = Array.from(messages.values()).map(safeMessage);
          } catch (error) {
            channelEntry.message_probe.status = "fail";
            channelEntry.message_probe.error = String(error.message || error);
          }
        }

        guildEntry.channels.push(channelEntry);
      }

      report.guilds.push(guildEntry);
    }

    const outdir = path.join("..", "data", "reports", "discord_architect");
    fs.mkdirSync(outdir, { recursive: true });

    const jsonPath = path.join(outdir, "discord_visibility_probe.json");
    const mdPath = path.join(outdir, "discord_visibility_probe.md");

    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));

    const lines = [
      "# Discord Visibility Probe",
      "",
      `Generated: ${report.generated_at}`,
      `Bot: ${report.bot_user ? report.bot_user.tag : "unknown"}`,
      "",
    ];

    for (const guild of report.guilds) {
      lines.push(`## ${guild.name}`);
      lines.push("");
      lines.push(`Guild ID: \`${guild.id}\``);
      lines.push("");
      lines.push("| Channel | Type | Message probe | Recent readable messages |");
      lines.push("|---|---:|---|---:|");

      for (const channel of guild.channels) {
        lines.push(
          `| #${channel.name || channel.id} | ${channel.type} | ${channel.message_probe.status} | ${channel.message_probe.messages.length} |`
        );
      }

      lines.push("");
    }

    fs.writeFileSync(mdPath, lines.join("\n") + "\n");

    console.log("DISCORD_VISIBILITY_PROBE=PASS");
    console.log(`GUILDS=${report.guilds.length}`);
    console.log(`JSON=${jsonPath}`);
    console.log(`MD=${mdPath}`);

    await client.destroy();
  });

  await client.login(token);
}

probe().catch((error) => {
  console.error("DISCORD_VISIBILITY_PROBE=FAIL");
  console.error(error);
  process.exit(1);
});
