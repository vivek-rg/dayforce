import assert from "node:assert/strict";

const base = process.env.SMOKE_BASE_URL || "http://127.0.0.1:5173";
const health = await fetch(`${base}/api/health`, {
  signal: AbortSignal.timeout(5000),
});
assert.equal(health.status, 200);
assert.deepEqual(await health.json(), {
  status: "ok",
  database: "ok",
  schema_version: 1,
});
const bootstrap = await fetch(`${base}/api/bootstrap`, {
  signal: AbortSignal.timeout(5000),
});
assert.equal(bootstrap.status, 200);
const data = await bootstrap.json();
assert.equal(data.project_name, "DayOne Proof");
assert.equal(data.foundation_only, true);
const page = await fetch(base, { signal: AbortSignal.timeout(5000) });
assert.equal(page.status, 200);
assert.match(await page.text(), /DayOne Proof/);
console.log(
  "PASS: frontend origin -> API proxy/server -> SQLite health and stored project name; HTML served.",
);
