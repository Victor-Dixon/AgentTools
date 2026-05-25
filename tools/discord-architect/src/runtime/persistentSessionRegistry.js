const fs = require("fs");
const path = require("path");

const ROOT = "/data/data/com.termux/files/home/projects/DreamVault";
const STATE_DIR = path.join(ROOT, "runtime", "state", "discord_architect");
const STATE_FILE = path.join(STATE_DIR, "persistent_sessions.json");

function ensureStateDir() {
  fs.mkdirSync(STATE_DIR, { recursive: true });
}

function loadSessions() {
  ensureStateDir();

  if (!fs.existsSync(STATE_FILE)) {
    return {};
  }

  return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
}

function saveSessions(sessions) {
  ensureStateDir();
  fs.writeFileSync(STATE_FILE, JSON.stringify(sessions, null, 2), "utf8");
}

function sessionKey(domain, ticker) {
  return `${domain}:${ticker}`;
}

function upsertSession(session) {
  const sessions = loadSessions();
  const key = sessionKey(session.domain, session.ticker);

  sessions[key] = {
    ...sessions[key],
    ...session,
    updated_at: new Date().toISOString(),
  };

  saveSessions(sessions);

  return sessions[key];
}

function getSession(domain, ticker) {
  const sessions = loadSessions();
  return sessions[sessionKey(domain, ticker)] || null;
}

function appendSessionEvent(domain, ticker, event) {
  const session = getSession(domain, ticker);

  if (!session) {
    throw new Error(`missing session: ${domain}:${ticker}`);
  }

  const events = session.events || [];

  events.push({
    ...event,
    timestamp: new Date().toISOString(),
  });

  return upsertSession({
    ...session,
    events,
  });
}

function replaySession(domain, ticker) {
  const session = getSession(domain, ticker);
  if (!session) return [];

  return session.events || [];
}

module.exports = {
  STATE_FILE,
  loadSessions,
  saveSessions,
  sessionKey,
  upsertSession,
  getSession,
  appendSessionEvent,
  replaySession,
};
