import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import net from "node:net";

const root = fileURLToPath(new URL("../", import.meta.url));
const python = path.join(
  root,
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const built = process.argv.includes("--built");
const children = [];
let stopping = false;

// Refuse occupied ports so a smoke test cannot accidentally hit someone else's app.
for (const port of built ? [8000] : [8000, 5173]) {
  await new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", () =>
      reject(new Error(`Port ${port} is occupied. Stop the other app first.`)),
    );
    server.listen(port, "127.0.0.1", () => server.close(resolve));
  }).catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}
if (!existsSync(python) || !existsSync(path.join(root, "node_modules"))) {
  console.error(
    "Dependencies missing. Follow README installation steps first.",
  );
  process.exit(1);
}
if (built && !existsSync(path.join(root, "frontend/dist/index.html"))) {
  console.error("Run npm run build before npm start.");
  process.exit(1);
}

function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (process.platform === "win32" && child.pid) {
      // The Windows venv launcher can spawn a second Python process; stop only our tree.
      spawnSync("taskkill", ["/PID", String(child.pid), "/T", "/F"], {
        stdio: "ignore",
      });
    } else {
      child.kill("SIGTERM");
    }
  }
  process.exitCode = code;
}
function run(command, args, cwd) {
  const child = spawn(command, args, {
    cwd,
    stdio: "inherit",
    env: process.env,
  });
  children.push(child);
  child.on("error", (error) => {
    console.error(error.message);
    stop(1);
  });
  child.on("exit", (code) => {
    if (!stopping) stop(code || 1);
  });
}
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
run(
  python,
  [
    "-m",
    "uvicorn",
    "app.main:app",
    "--app-dir",
    "backend",
    "--host",
    "127.0.0.1",
    "--port",
    "8000",
  ],
  root,
);
if (!built) {
  run(
    process.execPath,
    [
      path.join(root, "node_modules/vite/bin/vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5173",
      "--strictPort",
    ],
    path.join(root, "frontend"),
  );
}
console.log(
  `DayOne Proof: http://127.0.0.1:${built ? "8000" : "5173"} (Ctrl+C stops all services)`,
);
