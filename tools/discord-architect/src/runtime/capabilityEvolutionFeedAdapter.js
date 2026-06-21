const fs = require('fs');

function readCapabilityPayload(payloadPath) {
  const raw = fs.readFileSync(payloadPath, 'utf8');
  return JSON.parse(raw);
}

function renderCapabilityMessage(payload) {
  const unlocks = Array.isArray(payload.capability_unlocks)
    ? payload.capability_unlocks.map((item) => `- ${item}`).join('\n')
    : '- none listed';

  const next = Array.isArray(payload.unlocks_following_tasks)
    ? payload.unlocks_following_tasks.map((item) => `- ${item}`).join('\n')
    : '- none listed';

  return [
    '🧠 **Capability Unlocked**',
    '',
    `**${payload.title || payload.source_task || 'Dream.OS capability evolution'}**`,
    '',
    '**Why this matters**',
    payload.why_this_matters || 'No strategic rationale provided.',
    '',
    '**Unlocked capabilities**',
    unlocks,
    '',
    '**Unlocks next**',
    next,
    '',
    `Route: \`${payload.channel_key || 'master-task-log'}\``,
    `Source task: \`${payload.source_task || 'unknown'}\``,
    payload.commit ? `Commit: \`${payload.commit.slice(0, 8)}\`` : null,
  ].filter(Boolean).join('\n');
}

function buildMasterTaskLogEvent(payloadPath) {
  const payload = readCapabilityPayload(payloadPath);
  return {
    channelKey: payload.channel_key || 'master-task-log',
    eventType: payload.event_type || 'capability_evolution_closeout',
    content: renderCapabilityMessage(payload),
    sourceTask: payload.source_task || null,
  };
}

module.exports = {
  readCapabilityPayload,
  renderCapabilityMessage,
  buildMasterTaskLogEvent,
};
