import { useEffect, useState } from "react";
import { fetchBootstrap } from "./shared/api";
import type { Bootstrap } from "./shared/api-types";

export default function App() {
  const [data, setData] = useState<Bootstrap | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    fetchBootstrap(controller.signal)
      .then(setData)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(
            reason instanceof Error ? reason.message : "Backend unavailable.",
          );
        }
      });
    return () => controller.abort();
  }, [attempt]);

  function retry() {
    setError("");
    setData(null);
    setAttempt((value) => value + 1);
  }

  return (
    <main>
      <h1>{data?.project_name ?? "DayOne Proof"}</h1>
      <p>Repository foundation · local development only</p>
      <section aria-labelledby="connection-title">
        <h2 id="connection-title">Connection check</h2>
        {!data && !error && <p role="status">Checking backend and SQLite…</p>}
        {data && <p role="status">{data.message}</p>}
        {error && (
          <div role="alert">
            <p>{error} Confirm the backend is running, then retry.</p>
          </div>
        )}
        <button onClick={retry} disabled={!data && !error}>
          Check connection again
        </button>
      </section>
      <section aria-labelledby="scope-title">
        <h2 id="scope-title">What is ready?</h2>
        <ul>
          <li>React → FastAPI → local SQLite connectivity.</li>
          <li>Shared contracts and separate module folders.</li>
          <li>
            Business workflows are not implemented. Reserved endpoints return
            501.
          </li>
        </ul>
        <p>Start with AGENTS.md, PHASES.md and CHANGES.md in the repository.</p>
      </section>
      <a href="http://127.0.0.1:8000/docs">Inspect backend API contracts</a>
    </main>
  );
}
