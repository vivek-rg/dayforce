import { fileURLToPath } from "node:url";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const repoRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig(({ command, mode }) => {
  // Demo-account autofill is a dev-server convenience only; builds never embed the password.
  const demoPassword =
    command === "serve"
      ? (loadEnv(mode, repoRoot, "DEMO_").DEMO_PASSWORD ?? "")
      : "";
  return {
    plugins: [react()],
    define: { __DEMO_PASSWORD__: JSON.stringify(demoPassword) },
    server: {
      proxy: { "/api": "http://127.0.0.1:8000" },
    },
  };
});
