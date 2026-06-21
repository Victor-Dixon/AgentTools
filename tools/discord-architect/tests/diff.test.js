const assert = require("assert");
const { diffSchemas } = require("../src/diff");

const current = {
  protected: ["general"],
  categories: [
    {
      name: "COMMUNITY",
      channels: [
        { name: "general", type: "text" },
        { name: "old-chat", type: "text" }
      ]
    }
  ]
};

const desired = {
  protected: ["general"],
  categories: [
    {
      name: "COMMUNITY",
      channels: [
        { name: "general", type: "text" },
        { name: "options-flow", type: "text" }
      ]
    }
  ]
};

const plan = diffSchemas(current, desired);

assert.equal(plan.schema, "dreamos.discord_architect.diff.v1");
assert.equal(plan.operation_count, 2);
assert.equal(plan.destructive_count, 1);
assert(plan.operations.some((op) => op.action === "create_channel" && op.name === "options-flow"));
assert(plan.operations.some((op) => op.action === "archive_channel" && op.name === "old-chat"));

console.log("diff.test.js PASS");
