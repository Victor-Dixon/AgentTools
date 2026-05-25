function flattenChannels(schema) {
  const channels = new Map();

  for (const category of schema.categories || []) {
    for (const channel of category.channels || []) {
      channels.set(channel.name, {
        ...channel,
        category: category.name
      });
    }
  }

  return channels;
}

function diffSchemas(current, desired) {
  const operations = [];
  const protectedNames = new Set([
    ...(current.protected || []),
    ...(desired.protected || [])
  ]);

  const currentChannels = flattenChannels(current);
  const desiredChannels = flattenChannels(desired);

  for (const [name, desiredChannel] of desiredChannels.entries()) {
    if (!currentChannels.has(name)) {
      operations.push({
        action: "create_channel",
        name,
        channel_type: desiredChannel.type,
        category: desiredChannel.category,
        destructive: false
      });
      continue;
    }

    const currentChannel = currentChannels.get(name);
    if (
      currentChannel.type !== desiredChannel.type ||
      currentChannel.category !== desiredChannel.category
    ) {
      operations.push({
        action: "update_channel",
        name,
        from: {
          channel_type: currentChannel.type,
          category: currentChannel.category
        },
        to: {
          channel_type: desiredChannel.type,
          category: desiredChannel.category
        },
        destructive: false
      });
    }
  }

  for (const [name, currentChannel] of currentChannels.entries()) {
    if (!desiredChannels.has(name)) {
      operations.push({
        action: protectedNames.has(name) ? "skip_protected_channel" : "archive_channel",
        name,
        category: currentChannel.category,
        destructive: !protectedNames.has(name),
        protected: protectedNames.has(name)
      });
    }
  }

  return {
    schema: "dreamos.discord_architect.diff.v1",
    operation_count: operations.length,
    destructive_count: operations.filter((op) => op.destructive).length,
    operations
  };
}

module.exports = { diffSchemas, flattenChannels };
