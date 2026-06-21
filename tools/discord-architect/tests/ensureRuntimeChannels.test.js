const assert = require("assert");

const {
  REQUIRED_CHANNELS,
} = require("../src/runtime/ensureRuntimeChannels");

assert.equal(REQUIRED_CHANNELS.length, 4);

const names = REQUIRED_CHANNELS.map((c) => c.name);

assert(names.includes("master-task-log"));
assert(names.includes("lane-closeouts"));
assert(names.includes("verification-results"));
assert(names.includes("blocked-lanes"));

console.log("ensureRuntimeChannels.test.js PASS");
