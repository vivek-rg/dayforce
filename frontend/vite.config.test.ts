import { readFile } from "node:fs/promises";
import { expect, it, vi } from "vitest";
import { resolveConfig, transformWithEsbuild } from "vite";

it.each(["serve", "build"] as const)(
  "%s never sends the configured demo password to the browser",
  async (command) => {
    const password = "synthetic-browser-exposure-canary";
    vi.stubEnv("DEMO_PASSWORD", password);
    try {
      const config = await resolveConfig({}, command);
      expect(config.define ?? {}).not.toHaveProperty("__DEMO_PASSWORD__");
      const file = "src/features/auth/Login.tsx";
      const source = await readFile(file, "utf8");
      const result = await transformWithEsbuild(source, file, {
        define: config.define,
      });
      expect(result.code).not.toContain(password);
      expect(result.code).not.toContain("__DEMO_PASSWORD__");
    } finally {
      vi.unstubAllEnvs();
    }
  },
);
