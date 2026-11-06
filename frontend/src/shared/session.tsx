import {
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  api,
  hasStoredSession,
  setAccessToken,
  setUnauthorizedHandler,
} from "./api";
import type { User } from "./api-types";
import { SessionContext } from "./session-context";

function goHome() {
  window.location.hash = "";
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [expired, setExpired] = useState(false);
  const [restoring, setRestoring] = useState(hasStoredSession);

  // After a refresh, the saved session is checked against the server before use.
  useEffect(() => {
    if (!restoring) return;
    const controller = new AbortController();
    api
      .me(controller.signal)
      .then(setUser)
      .catch(() => undefined)
      .finally(() => {
        if (!controller.signal.aborted) setRestoring(false);
      });
    return () => controller.abort();
    // Runs once, on first load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setAccessToken(null);
      setUser(null);
      setExpired(true);
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (userId: string, password: string) => {
    const session = await api.login(userId, password);
    setAccessToken(session.access_token);
    setExpired(false);
    goHome();
    setUser(session.user);
  }, []);

  const signUp = useCallback(
    async (name: string, email: string, password: string) => {
      const session = await api.createAccount(name, email, password);
      setAccessToken(session.access_token);
      setExpired(false);
      goHome();
      setUser(session.user);
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } finally {
      setAccessToken(null);
      setUser(null);
      goHome();
    }
  }, []);

  const value = useMemo(
    () => ({ user, expired, restoring, login, signUp, logout }),
    [user, expired, restoring, login, signUp, logout],
  );
  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
}
