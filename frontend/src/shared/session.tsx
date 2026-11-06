import {
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api, setAccessToken, setUnauthorizedHandler } from "./api";
import type { User } from "./api-types";
import { SessionContext } from "./session-context";

function goHome() {
  window.location.hash = "";
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [expired, setExpired] = useState(false);

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
    () => ({ user, expired, login, logout }),
    [user, expired, login, logout],
  );
  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
}
