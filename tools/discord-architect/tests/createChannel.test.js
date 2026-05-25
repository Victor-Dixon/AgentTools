const assert = require("assert");
const { ChannelType } = require("discord.js");
const {
  normalizeChannelType,
  findCategory,
  createChannelFromOperation
} = require("../src/adapters/createChannel");

function cache(items) {
  return {
    find(fn) {
      return items.find(fn);
    }
  };
}

assert.equal(normalizeChannelType("text"), ChannelType.GuildText);
assert.equal(normalizeChannelType("voice"), ChannelType.GuildVoice);
assert.equal(normalizeChannelType("forum"), ChannelType.GuildForum);

const guild = {
  channels: {
    cache: cache([
      { id: "cat-1", name: "COMMUNITY", type: ChannelType.GuildCategory },
      { id: "chan-1", name: "general", type: ChannelType.GuildText }
    ]),
    async create(payload) {
      return {
        id: "created-1",
        name: payload.name,
        parentId: payload.parent || null
      };
    }
  }
};

assert.equal(findCategory(guild, "COMMUNITY").id, "cat-1");
assert.equal(findCategory(guild, "MISSING"), null);

(async () => {
  const dry = await createChannelFromOperation(guild, {
    action: "create_channel",
    name: "options-flow",
    category: "COMMUNITY",
    channel_type: "text",
    destructive: false
  }, { dryRun: true });

  assert.equal(dry.status, "dry_run");
  assert.equal(dry.payload.parent, "cat-1");

  const existing = await createChannelFromOperation(guild, {
    action: "create_channel",
    name: "general",
    category: "COMMUNITY",
    channel_type: "text",
    destructive: false
  }, { dryRun: false });

  assert.equal(existing.status, "skipped");

  const blocked = await createChannelFromOperation(guild, {
    action: "archive_channel",
    name: "old-chat",
    destructive: true
  }, { dryRun: false });

  assert.equal(blocked.status, "blocked");

  console.log("createChannel.test.js PASS");
})();
