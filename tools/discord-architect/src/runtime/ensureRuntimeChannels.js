const {
  ChannelType,
  PermissionsBitField,
} = require("discord.js");

const REQUIRED_CHANNELS = [
  {
    name: "master-task-log",
    topic: "Canonical Dream.OS task lifecycle stream.",
  },
  {
    name: "lane-closeouts",
    topic: "Governed runtime closeouts and completion packets.",
  },
  {
    name: "verification-results",
    topic: "Verification gates, CPC pass/fail, and test evidence.",
  },
  {
    name: "blocked-lanes",
    topic: "Blocked execution lanes and failure investigations.",
  },
];

async function ensureRuntimeChannels(client, guildId) {
  const guild = await client.guilds.fetch(guildId);

  const existing = guild.channels.cache;

  const results = [];

  for (const spec of REQUIRED_CHANNELS) {
    let channel = existing.find(
      (c) => c.name === spec.name,
    );

    if (!channel) {
      channel = await guild.channels.create({
        name: spec.name,
        type: ChannelType.GuildText,
        topic: spec.topic,
        permissionOverwrites: [
          {
            id: guild.roles.everyone.id,
            allow: [
              PermissionsBitField.Flags.ViewChannel,
            ],
          },
        ],
      });

      results.push({
        channel: spec.name,
        status: "created",
        id: channel.id,
      });
    } else {
      results.push({
        channel: spec.name,
        status: "exists",
        id: channel.id,
      });
    }
  }

  return results;
}

module.exports = {
  REQUIRED_CHANNELS,
  ensureRuntimeChannels,
};
