const { ChannelType } = require("discord.js");

function normalizeChannelType(type) {
  if (type === undefined || type === null || type === "text") return ChannelType.GuildText;
  if (type === "voice") return ChannelType.GuildVoice;
  if (type === "forum") return ChannelType.GuildForum;
  if (type === "category") return ChannelType.GuildCategory;
  if (typeof type === "number") return type;
  throw new Error(`unsupported channel type: ${type}`);
}

function findCategory(guild, name) {
  const wanted = String(name || "").toLowerCase();
  const cache = guild && guild.channels && guild.channels.cache;

  if (!cache) return null;

  const matchesCategory = (channel) =>
    channel &&
    String(channel.name || "").toLowerCase() === wanted &&
    channel.type === ChannelType.GuildCategory;

  if (typeof cache.find === "function") {
    return cache.find(matchesCategory) || null;
  }

  const channels =
    typeof cache.values === "function"
      ? Array.from(cache.values())
      : Array.isArray(cache)
        ? cache
        : Object.values(cache);

  return channels.find(matchesCategory) || null;
}

function findExistingChannel(guild, name) {
  const wanted = String(name || "").toLowerCase();
  const cache = guild && guild.channels && guild.channels.cache;

  if (!cache) return null;

  const matchesName = (channel) =>
    channel && String(channel.name || "").toLowerCase() === wanted;

  if (typeof cache.find === "function") {
    return cache.find(matchesName) || null;
  }

  const channels =
    typeof cache.values === "function"
      ? Array.from(cache.values())
      : Array.isArray(cache)
        ? cache
        : Object.values(cache);

  return channels.find(matchesName) || null;
}

async function createChannelFromOperation(guild, operation, options = {}) {
  if (!operation || operation.action !== "create_channel") {
    return { status: operation && operation.destructive ? "blocked" : "ignored" };
  }

  if (operation.destructive) {
    return { status: "blocked" };
  }

  const existing = findExistingChannel(guild, operation.name);
  if (existing) {
    return { status: "skipped", channel: existing };
  }

  const category = operation.category ? findCategory(guild, operation.category) : null;

  const payload = {
    name: operation.name,
    type: normalizeChannelType(operation.channel_type || operation.type || "text"),
  };

  if (category) payload.parent = category.id;

  if (options.dryRun) {
    return { status: "dry_run", payload };
  }

  const channel = await guild.channels.create(payload);
  return { status: "created", channel, payload };
}

module.exports = {
  normalizeChannelType,
  findCategory,
  findExistingChannel,
  createChannelFromOperation,
};
