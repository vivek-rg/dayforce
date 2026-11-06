import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import { type Route, parseHash } from "./routes";

export function asError(reason: unknown): Error {
  return reason instanceof Error ? reason : new Error("Something went wrong.");
}

export type Resource<T> = {
  data: T | undefined;
  error: Error | undefined;
  loading: boolean;
  refreshing: boolean;
  reload: () => void;
};

type Settled<T> = {
  key: string;
  nonce: number;
  data: T | undefined;
  error: Error | undefined;
};

/**
 * Loads data for a key and aborts stale requests. A null key loads nothing.
 * Reloads keep the last good data on screen, so polling never flashes a skeleton.
 */
export function useResource<T>(
  key: string | null,
  load: (signal: AbortSignal) => Promise<T>,
): Resource<T> {
  const loadRef = useRef(load);
  useEffect(() => {
    loadRef.current = load;
  });
  const [nonce, setNonce] = useState(0);
  const [settled, setSettled] = useState<Settled<T> | null>(null);

  useEffect(() => {
    if (key === null) return;
    const controller = new AbortController();
    loadRef.current(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) {
          setSettled({ key, nonce, data, error: undefined });
        }
      },
      (reason: unknown) => {
        if (!controller.signal.aborted) {
          setSettled((previous) => ({
            key,
            nonce,
            data: previous?.key === key ? previous.data : undefined,
            error: asError(reason),
          }));
        }
      },
    );
    return () => controller.abort();
  }, [key, nonce]);

  const reload = useCallback(() => setNonce((value) => value + 1), []);
  const current = settled?.key === key ? settled : null;
  return {
    data: current?.data,
    error: current?.error,
    loading: key !== null && current === null,
    refreshing: current !== null && current.nonce !== nonce,
    reload,
  };
}

export function useInterval(callback: () => void, delay: number | null) {
  const latest = useRef(callback);
  useEffect(() => {
    latest.current = callback;
  });
  useEffect(() => {
    if (delay === null) return;
    const timer = window.setInterval(() => latest.current(), delay);
    return () => window.clearInterval(timer);
  }, [delay]);
}

export type ActionResult<T> = { ok: true; value: T } | { ok: false };

/** One user-triggered mutation: pending flag, error text, and never an automatic retry. */
export function useAction() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const run = useCallback(
    async <T>(action: () => Promise<T>): Promise<ActionResult<T>> => {
      setPending(true);
      setError(null);
      try {
        return { ok: true, value: await action() };
      } catch (reason) {
        setError(asError(reason));
        return { ok: false };
      } finally {
        setPending(false);
      }
    },
    [],
  );
  const clear = useCallback(() => setError(null), []);
  return { pending, error, run, clear };
}

function subscribeToHash(listener: () => void) {
  window.addEventListener("hashchange", listener);
  return () => window.removeEventListener("hashchange", listener);
}

export function useHash(): string {
  return useSyncExternalStore(subscribeToHash, () => window.location.hash);
}

export function useRoute(): Route {
  const hash = useHash();
  return useMemo(() => parseHash(hash), [hash]);
}
