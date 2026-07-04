const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { writePlan } = require("../src/cli/plan");

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "discord-plan-"));

const currentPath = path.join(tmp, "current.json");
const desiredPath = path.join(tmp, "desired.json");
const outPath = path.join(tmp, "plan.json");
const mdPath = path.join(tmp, "plan.md");

fs.writeFileSync(currentPath, JSON.stringify({
  protected: ["general"],
  categories: [
    { name: "COMMUNITY", channels: [{ name: "general", type: "text" }] }
  ]
}));

fs.writeFileSync(desiredPath, JSON.stringify({
  protected: ["general"],
  categories: [
    { name: "COMMUNITY", channels: [
      { name: "general", type: "text" },
      { name: "options-flow", type: "text" }
    ] }
  ]
}));

const plan = writePlan({
  current: currentPath,
  desired: desiredPath,
  out: outPath,
  markdown: mdPath
});

assert.equal(plan.mode, "plan_only");
assert.equal(plan.operation_count, 1);
assert(fs.existsSync(outPath));
assert(fs.existsSync(mdPath));

console.log("plan.test.js PASS");
