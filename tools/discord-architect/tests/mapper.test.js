const assert = require("assert");
const { mapGuild } = require("../src/mapper");

function cache(values) {
  return { values: () => values };
}

const guild = {
  id: "guild-1",
  name: "Test Guild",
  channels: {
    cache: cache([
      { id: "cat-1", name: "COMMUNITY", type: 4 },
      { id: "chan-1", name: "general", type: 0, parentId: "cat-1" },
      { id: "voice-1", name: "voice-lounge", type: 2, parentId: "cat-1" }
    ])
  },
  roles: {
    cache: cache([
      { id: "role-1", name: "@everyone", position: 0, managed: false, permissions: { bitfield: 0n } }
    ])
  }
};

const schema = mapGuild(guild);

assert.equal(schema.schema, "dreamos.discord_architect.server.v1");
assert.equal(schema.server, "Test Guild");
assert.equal(schema.categories.length, 1);
assert.equal(schema.categories[0].channels.length, 2);
assert.equal(schema.roles.length, 1);

console.log("mapper.test.js PASS");
