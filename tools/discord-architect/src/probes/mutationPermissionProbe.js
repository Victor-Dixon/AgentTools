const fs = require("fs");
const path = require("path");
const {
  ChannelType,
  Client,
  GatewayIntentBits,
  PermissionsBitField,
} = require("discord.js");

function envToken() {
  return process.env.DISCORD_BOT_TOKEN ||
    process.env.DISCORD_TOKEN ||
    process.env.FREERIDEINVESTOR_DISCORD_BOT_TOKEN ||
    "";
}

function has(perms, flag) {
  return perms && perms.has(flag);
}

async function main() {
  const token = envToken();
  if (!token) {
    console.error("DISCORD_TOKEN_MISSING=FAIL");
    process.exit(2);
  }

  const client = new Client({ intents: [GatewayIntentBits.Guilds] });

  client.once("clientReady", async () => {
    const report = {
      generated_at: new Date().toISOString(),
      bot: client.user.tag,
      guilds: [],
    };

    for (const guild of client.guilds.cache.values()) {
      await guild.channels.fetch();

      const me = await guild.members.fetchMe();
      const basePerms = me.permissions;

      const textChannels = guild.channels.cache.filter((c) => {
        return c && c.type === ChannelType.GuildText;
      });

      const channelRows = [];

      for (const channel of textChannels.values()) {
        const perms = channel.permissionsFor(me);

        channelRows.push({
          id: channel.id,
          name: channel.name,
          view_channel: has(perms, PermissionsBitField.Flags.ViewChannel),
          send_messages: has(perms, PermissionsBitField.Flags.SendMessages),
          manage_channels: has(perms, PermissionsBitField.Flags.ManageChannels),
          manage_webhooks: has(perms, PermissionsBitField.Flags.ManageWebhooks),
          create_public_threads: has(perms, PermissionsBitField.Flags.CreatePublicThreads),
          send_messages_in_threads: has(perms, PermissionsBitField.Flags.SendMessagesInThreads),
        });
      }

      report.guilds.push({
        id: guild.id,
        name: guild.name,
        guild_permissions: {
          manage_channels: has(basePerms, PermissionsBitField.Flags.ManageChannels),
          manage_webhooks: has(basePerms, PermissionsBitField.Flags.ManageWebhooks),
          create_public_threads: has(basePerms, PermissionsBitField.Flags.CreatePublicThreads),
          send_messages_in_threads: has(basePerms, PermissionsBitField.Flags.SendMessagesInThreads),
        },
        channels: channelRows,
      });
    }

    const root = path.join(__dirname, "..", "..", "..");
    const outdir = path.join(root, "data", "reports", "discord_architect");
    fs.mkdirSync(outdir, { recursive: true });

    const jsonPath = path.join(outdir, "discord_mutation_permission_probe.json");
    const mdPath = path.join(outdir, "discord_mutation_permission_probe.md");

    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));

    const lines = [
      "# Discord Mutation Permission Probe",
      "",
      `Generated: ${report.generated_at}`,
      `Bot: ${report.bot}`,
      "",
    ];

    for (const guild of report.guilds) {
      lines.push(`## ${guild.name}`);
      lines.push("");
      lines.push("### Guild Permissions");
      lines.push("");
      for (const [key, value] of Object.entries(guild.guild_permissions)) {
        lines.push(`- ${key}: ${value ? "PASS" : "FAIL"}`);
      }
      lines.push("");
      lines.push("| Channel | Send | Manage Channels | Webhooks | Public Threads | Thread Send |");
      lines.push("|---|---|---|---|---|---|");
      for (const c of guild.channels) {
        lines.push(
          `| #${c.name} | ${c.send_messages ? "PASS" : "FAIL"} | ${c.manage_channels ? "PASS" : "FAIL"} | ${c.manage_webhooks ? "PASS" : "FAIL"} | ${c.create_public_threads ? "PASS" : "FAIL"} | ${c.send_messages_in_threads ? "PASS" : "FAIL"} |`
        );
      }
      lines.push("");
    }

    fs.writeFileSync(mdPath, lines.join("\n") + "\n");

    console.log("DISCORD_MUTATION_PERMISSION_PROBE=PASS");
    console.log(`JSON=${jsonPath}`);
    console.log(`MD=${mdPath}`);

    await client.destroy();
  });

  await client.login(token);
}

main().catch((error) => {
  console.error("DISCORD_MUTATION_PERMISSION_PROBE=FAIL");
  console.error(error);
  process.exit(1);
});
