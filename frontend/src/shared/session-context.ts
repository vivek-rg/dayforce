import { createContext, useContext } from "react";
import type { AiHealth, User } from "./api-types";

export type SessionValue = {
  user: User | null;
  expired: boolean;
  login: (userId: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const SessionContext = createContext<SessionValue | null>(null);

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession needs a SessionProvider.");
  return value;
}

/** For screens inside the signed-in shell, where a user always exists. */
export function useUser(): User {
  const { user } = useSession();
  if (!user) throw new Error("useUser needs a signed-in user.");
  return user;
}

export type ShellValue = {
  aiHealth: AiHealth | null;
  unread: number;
  refreshUnread: () => void;
};

export const ShellContext = createContext<ShellValue>({
  aiHealth: null,
  unread: 0,
  refreshUnread: () => {},
});

export function useShell(): ShellValue {
  return useContext(ShellContext);
}
