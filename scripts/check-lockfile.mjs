import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const { packages } = JSON.parse(
  readFileSync(new URL("../package-lock.json", import.meta.url), "utf8"),
);

for (const name of ["rollup", "esbuild"]) {
  const dependencies = packages[`node_modules/${name}`]?.optionalDependencies;
  assert.ok(dependencies, `Missing ${name} optional dependencies in lockfile.`);
  for (const [platform, version] of Object.entries(dependencies)) {
    if (!platform.startsWith(`@${name}/`)) continue;
    assert.equal(
      packages[`node_modules/${platform}`]?.version,
      version,
      `Lockfile is missing ${platform}@${version}; regenerate without node_modules present.`,
    );
  }
}

console.log("PASS: Rollup and esbuild platform packages are fully locked.");
