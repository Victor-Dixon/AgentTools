const fs = require("fs");

function mapGuild(guild) {
  const schema = {
    schema: "dreamos.discord_architect.server.v1",
    server: guild.name,
    guild_id: guild.id || null,
    categories: [],
    roles: [],
    protected: ["rules", "announcements", "general"]
  };

  const channels = Array.from(guild.channels.cache.values());

  const categories = channels.filter((channel) => channel.type === 4);

  for (const category of categories) {
    const children = channels
      .filter((channel) => channel.parentId === category.id)
      .map((channel) => ({
        id: channel.id,
        name: channel.name,
        type: channel.type,
        parent_id: channel.parentId || null
      }));

    schema.categories.push({
      id: category.id,
      name: category.name,
      channels: children
    });
  }

  if (guild.roles && guild.roles.cache) {
    schema.roles = Array.from(guild.roles.cache.values()).map((role) => ({
      id: role.id,
      name: role.name,
      position: role.position,
      managed: role.managed,
      permissions: role.permissions ? role.permissions.bitfield.toString() : null
    }));
  }

  return schema;
}

function writeSchema(schema, outputPath) {
  fs.writeFileSync(outputPath, JSON.stringify(schema, null, 2));
  return outputPath;
}

module.exports = { mapGuild, writeSchema };
