import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AssistantPage,
  type AssistantTurn,
} from "./features/assistant/Assistant";
import { AuditPage } from "./features/audit/Audit";
import { LoginPage } from "./features/auth/Login";
import { DocumentQueuePage } from "./features/documents/DocumentQueue";
import { GuidePage } from "./features/guide/Guide";
import { InsightsPage } from "./features/insights/Insights";
import { ItEquipmentPage } from "./features/it/ItEquipment";
import { KnowledgePage } from "./features/knowledge/KnowledgeBase";
import { ManagerPage } from "./features/manager/ManagerDashboard";
import { MyWorkPage } from "./features/my-work/MyWork";
import { NotificationsPage } from "./features/notifications/Notifications";
import { OverviewPage } from "./features/overview/Overview";
import { BenefitsPage } from "./features/payroll/Benefits";
import { PayrollPage } from "./features/payroll/Payroll";
import { TrainingPage } from "./features/payroll/Training";
import { PortalPage } from "./features/portal/Portal";
import { ReviewInboxPage } from "./features/review/ReviewInbox";
import { SettingsPage } from "./features/settings/Settings";
import { CreateHirePage } from "./features/workspace/CreateHire";
import { DirectoryPage } from "./features/workspace/Directory";
import { HireWorkspacePage } from "./features/workspace/HireWorkspace";
import { api } from "./shared/api";
import type { AiHealth } from "./shared/api-types";
import { useHash, useInterval, useRoute } from "./shared/hooks";
import { Icon, MenuIcon } from "./shared/icons";
import { type Route, canOpen, homeHref, navFor } from "./shared/routes";
import { SessionProvider } from "./shared/session";
import { ShellContext, useSession, useUser } from "./shared/session-context";
import { DeniedState, EmptyState } from "./shared/ui";

export default function App() {
  return (
    <SessionProvider>
      <Root />
    </SessionProvider>
  );
}

function Root() {
  const { user, restoring } = useSession();
  const route = useRoute();
  if (restoring) return null;
  if (!user && (route.name === "how-it-works" || route.name === "role-guide")) {
    return <GuidePage page={route.name} />;
  }
  // Keyed by user, so no screen state survives a change of account.
  return user ? (
    <>
      <div className="demo-strip">Synthetic demo data</div>
      <Shell key={user.id} />
    </>
  ) : (
    <LoginPage />
  );
}

function AiBanner({ health }: { health: AiHealth | null }) {
  if (!health) return null;
  if (health.is_stub) {
    return (
      <div className="ai-banner" data-tone="warn" role="status">
        Offline rules are active. This is not a real AI model.
      </div>
    );
  }
  if (!health.available) {
    return (
      <div className="ai-banner" data-tone="info" role="status">
        AI is off. All manual work continues.
      </div>
    );
  }
  return null;
}

function Shell() {
  const user = useUser();
  const { logout } = useSession();
  const route = useRoute();
  const hash = useHash();
  const [menuFor, setMenuFor] = useState<string | null>(null);
  const [drawerFor, setDrawerFor] = useState<string | null>(null);
  const [unread, setUnread] = useState(0);
  const [aiHealth, setAiHealth] = useState<AiHealth | null>(null);
  const [turns, setTurns] = useState<AssistantTurn[]>([]);
  const menuOpen = menuFor === hash;
  const drawerOpen = drawerFor === hash;

  const refreshUnread = useCallback(() => {
    api
      .notifications()
      .then((list) => setUnread(list.unread))
      .catch(() => {
        // The count is a convenience. The notifications page reports real errors.
      });
  }, []);

  const refreshHealth = useCallback(() => {
    api
      .aiHealth()
      .then(setAiHealth)
      .catch(() => setAiHealth(null));
  }, []);

  useEffect(() => {
    refreshUnread();
  }, [hash, refreshUnread]);
  useEffect(() => {
    refreshHealth();
  }, [refreshHealth]);
  useInterval(() => {
    refreshUnread();
    refreshHealth();
  }, 30_000);

  useEffect(() => {
    if (!menuOpen && !drawerOpen) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuFor(null);
        setDrawerFor(null);
      }
    }
    function onPointer(event: PointerEvent) {
      if (!(event.target as Element).closest(".user-menu")) setMenuFor(null);
    }
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onPointer);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onPointer);
    };
  }, [menuOpen, drawerOpen]);

  const shell = useMemo(
    () => ({ aiHealth, unread, refreshUnread }),
    [aiHealth, unread, refreshUnread],
  );

  const home = homeHref(user.role);
  const currentHref = route.name === "home" ? home : hash;
  const pageLabel =
    navFor(user.role)
      .flatMap((group) => group.items)
      .find((item) => item.href === currentHref)?.label ?? "Workspace";

  return (
    <ShellContext.Provider value={shell}>
      <div className="app">
        <a className="skip-link" href={hash || "#/"} onClick={focusMain}>
          Skip to content
        </a>
        <aside className="sidebar" data-open={drawerOpen || undefined}>
          <a className="brand" href={home}>
            OnboardIQ
          </a>
          <nav aria-label="Main">
            {navFor(user.role).map((group) => (
              <div key={group.label} className="nav-group">
                <p className="nav-label">{group.label}</p>
                <ul>
                  {group.items.map((item) => {
                    const active =
                      currentHref === item.href ||
                      (item.page === "directory" &&
                        (route.name === "hire" || route.name === "new-hire"));
                    return (
                      <li key={item.href}>
                        <a
                          className="nav-item"
                          href={item.href}
                          aria-current={active ? "page" : undefined}
                        >
                          <Icon name={item.icon} />
                          {item.label}
                          {item.page === "notifications" && unread > 0 && (
                            <span className="nav-count num">{unread}</span>
                          )}
                        </a>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </nav>
        </aside>
        {drawerOpen && (
          <button
            type="button"
            className="scrim"
            aria-label="Close navigation"
            onClick={() => setDrawerFor(null)}
          />
        )}
        <div className="workspace">
          <header className="topbar">
            <button
              type="button"
              className="btn btn-icon menu-button"
              aria-label="Open navigation"
              aria-expanded={drawerOpen}
              onClick={() => setDrawerFor(drawerOpen ? null : hash)}
            >
              <MenuIcon />
            </button>
            <span className="topbar-brand">OnboardIQ</span>
            <span className="topbar-location">{pageLabel}</span>
            <div className="topbar-right">
              <a
                className="bell"
                href="#/notifications"
                aria-label={`Notifications, ${unread} unread`}
              >
                <Icon name="bell" />
                <span className="num">{unread}</span>
              </a>
              <div className="user-menu">
                <button
                  type="button"
                  className="user-button"
                  aria-expanded={menuOpen}
                  aria-haspopup="true"
                  onClick={() => setMenuFor(menuOpen ? null : hash)}
                >
                  <span className="user-name">{user.display_name}</span>
                  <span className="user-role">{user.role}</span>
                </button>
                {menuOpen && (
                  <div className="user-panel">
                    <p className="user-panel-name">{user.display_name}</p>
                    <p className="muted small mono">{user.id}</p>
                    <button
                      type="button"
                      className="btn btn-sm"
                      onClick={() => void logout()}
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </header>
          <AiBanner health={aiHealth} />
          <main id="main" className="content" tabIndex={-1}>
            <RouteView route={route} turns={turns} setTurns={setTurns} />
          </main>
        </div>
      </div>
    </ShellContext.Provider>
  );
}

function focusMain(event: React.MouseEvent) {
  event.preventDefault();
  document.getElementById("main")?.focus();
}

function RouteView({
  route,
  turns,
  setTurns,
}: {
  route: Route;
  turns: AssistantTurn[];
  setTurns: React.Dispatch<React.SetStateAction<AssistantTurn[]>>;
}) {
  const user = useUser();
  useEffect(() => {
    if (route.name === "home") window.location.replace(homeHref(user.role));
  }, [route.name, user.role]);

  if (!canOpen(user.role, route)) {
    return <DeniedState message="This screen is not part of your role." />;
  }
  switch (route.name) {
    case "home":
      return null;
    case "not-found":
      return (
        <EmptyState
          action={<a href={homeHref(user.role)}>Go to your home page</a>}
        >
          This page does not exist.
        </EmptyState>
      );
    case "how-it-works":
    case "role-guide":
      return <GuidePage page={route.name} embedded />;
    case "dashboard":
      return <OverviewPage />;
    case "directory":
      return <DirectoryPage />;
    case "new-hire":
      return <CreateHirePage />;
    case "hire":
      return (
        <HireWorkspacePage
          key={route.hireId}
          hireId={route.hireId}
          tab={route.tab}
        />
      );
    case "tasks":
      return <MyWorkPage />;
    case "documents":
      return <DocumentQueuePage />;
    case "it":
      return <ItEquipmentPage />;
    case "review":
      return <ReviewInboxPage />;
    case "payroll":
      return <PayrollPage />;
    case "benefits":
      return <BenefitsPage />;
    case "training":
      return <TrainingPage />;
    case "manager":
      return <ManagerPage />;
    case "portal":
      return <PortalPage />;
    case "assistant":
      return <AssistantPage turns={turns} setTurns={setTurns} />;
    case "insights":
      return <InsightsPage />;
    case "knowledge":
      return <KnowledgePage />;
    case "notifications":
      return <NotificationsPage />;
    case "audit":
      return <AuditPage />;
    case "settings":
      return <SettingsPage />;
  }
}
