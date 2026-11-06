import type { Role } from "./api-types";

export const HIRE_TABS = [
  "plan",
  "timeline",
  "evidence",
  "documents",
  "investigation",
  "history",
] as const;
export type HireTab = (typeof HIRE_TABS)[number];

export type PageName =
  | "dashboard"
  | "directory"
  | "new-hire"
  | "tasks"
  | "documents"
  | "it"
  | "review"
  | "payroll"
  | "benefits"
  | "training"
  | "manager"
  | "portal"
  | "assistant"
  | "insights"
  | "knowledge"
  | "notifications"
  | "audit"
  | "settings";

export type Route =
  | { name: "home" }
  | { name: "not-found" }
  | { name: "hire"; hireId: string; tab: HireTab }
  | { name: PageName };

const SIMPLE_PATHS: Record<string, PageName> = {
  dashboard: "dashboard",
  hires: "directory",
  "hires/new": "new-hire",
  tasks: "tasks",
  documents: "documents",
  it: "it",
  review: "review",
  payroll: "payroll",
  benefits: "benefits",
  training: "training",
  manager: "manager",
  portal: "portal",
  assistant: "assistant",
  insights: "insights",
  knowledge: "knowledge",
  notifications: "notifications",
  audit: "audit",
  settings: "settings",
};

export function parseHash(hash: string): Route {
  const path = hash.replace(/^#\/?/, "").replace(/\/+$/, "");
  if (!path) return { name: "home" };
  if (Object.hasOwn(SIMPLE_PATHS, path)) return { name: SIMPLE_PATHS[path] };
  const match = /^hires\/([^/]+)(?:\/([a-z]+))?$/.exec(path);
  if (match) {
    const tab = match[2] ?? "plan";
    if ((HIRE_TABS as readonly string[]).includes(tab)) {
      return {
        name: "hire",
        hireId: decodeURIComponent(match[1]),
        tab: tab as HireTab,
      };
    }
  }
  return { name: "not-found" };
}

export function hireHref(hireId: string, tab?: HireTab): string {
  const base = `#/hires/${encodeURIComponent(hireId)}`;
  return tab ? `${base}/${tab}` : base;
}

const ALL: Role[] = [
  "HR",
  "IT",
  "PAYROLL",
  "BENEFITS",
  "TRAINING",
  "MANAGER",
  "EMPLOYEE",
];
const STAFF = ALL.filter((role) => role !== "EMPLOYEE");

// Convenience only. The server enforces every one of these again.
const PAGE_ROLES: Record<PageName, Role[]> = {
  dashboard: ["HR"],
  directory: STAFF,
  "new-hire": ["HR"],
  tasks: ALL,
  documents: ["HR"],
  it: ["IT", "HR"],
  review: ["HR", "IT"],
  payroll: ["PAYROLL", "HR"],
  benefits: ["BENEFITS", "HR"],
  training: ["TRAINING", "HR"],
  manager: ["MANAGER"],
  portal: ["EMPLOYEE"],
  assistant: ALL,
  insights: ["HR"],
  knowledge: ["HR"],
  notifications: ALL,
  audit: ["HR"],
  settings: ["HR"],
};

export function canOpen(role: Role, route: Route): boolean {
  if (route.name === "home" || route.name === "not-found") return true;
  if (route.name === "hire") return true;
  return PAGE_ROLES[route.name].includes(role);
}

const HOME: Record<Role, string> = {
  HR: "#/dashboard",
  IT: "#/it",
  PAYROLL: "#/payroll",
  BENEFITS: "#/benefits",
  TRAINING: "#/training",
  MANAGER: "#/manager",
  EMPLOYEE: "#/portal",
};

export function homeHref(role: Role): string {
  return HOME[role];
}

export type NavIcon =
  | "dashboard"
  | "people"
  | "tasks"
  | "document"
  | "device"
  | "inbox"
  | "payroll"
  | "benefits"
  | "training"
  | "team"
  | "home"
  | "assistant"
  | "insights"
  | "book"
  | "bell"
  | "audit"
  | "settings";

export type NavItem = {
  href: string;
  label: string;
  icon: NavIcon;
  page: PageName;
};
export type NavGroup = { label: string; items: NavItem[] };

const ITEMS: Record<string, NavItem> = {
  dashboard: {
    href: "#/dashboard",
    label: "Overview",
    icon: "dashboard",
    page: "dashboard",
  },
  directory: {
    href: "#/hires",
    label: "Employees",
    icon: "people",
    page: "directory",
  },
  tasks: { href: "#/tasks", label: "Tasks", icon: "tasks", page: "tasks" },
  documents: {
    href: "#/documents",
    label: "Document verification",
    icon: "document",
    page: "documents",
  },
  it: { href: "#/it", label: "IT and equipment", icon: "device", page: "it" },
  review: {
    href: "#/review",
    label: "Review inbox",
    icon: "inbox",
    page: "review",
  },
  payroll: {
    href: "#/payroll",
    label: "Payroll",
    icon: "payroll",
    page: "payroll",
  },
  benefits: {
    href: "#/benefits",
    label: "Benefits",
    icon: "benefits",
    page: "benefits",
  },
  training: {
    href: "#/training",
    label: "Training",
    icon: "training",
    page: "training",
  },
  manager: {
    href: "#/manager",
    label: "My team",
    icon: "team",
    page: "manager",
  },
  portal: {
    href: "#/portal",
    label: "My onboarding",
    icon: "home",
    page: "portal",
  },
  assistant: {
    href: "#/assistant",
    label: "Knowledge assistant",
    icon: "assistant",
    page: "assistant",
  },
  insights: {
    href: "#/insights",
    label: "AI insights",
    icon: "insights",
    page: "insights",
  },
  knowledge: {
    href: "#/knowledge",
    label: "Knowledge base",
    icon: "book",
    page: "knowledge",
  },
  notifications: {
    href: "#/notifications",
    label: "Notifications",
    icon: "bell",
    page: "notifications",
  },
  audit: {
    href: "#/audit",
    label: "Audit and reliability",
    icon: "audit",
    page: "audit",
  },
  settings: {
    href: "#/settings",
    label: "Settings",
    icon: "settings",
    page: "settings",
  },
};

const pick = (...keys: string[]) => keys.map((key) => ITEMS[key]);

export function navFor(role: Role): NavGroup[] {
  const help: NavGroup = {
    label: "Help",
    items: pick("assistant", "notifications"),
  };
  switch (role) {
    case "HR":
      return [
        { label: "Onboarding", items: pick("dashboard", "directory", "tasks") },
        { label: "Verification", items: pick("documents", "review") },
        {
          label: "Systems",
          items: pick("it", "payroll", "benefits", "training"),
        },
        {
          label: "Knowledge",
          items: pick("assistant", "knowledge", "insights"),
        },
        { label: "Admin", items: pick("notifications", "audit", "settings") },
      ];
    case "IT":
      return [
        { label: "Work", items: pick("it", "review", "tasks", "directory") },
        help,
      ];
    case "PAYROLL":
      return [
        { label: "Work", items: pick("payroll", "tasks", "directory") },
        help,
      ];
    case "BENEFITS":
      return [
        { label: "Work", items: pick("benefits", "tasks", "directory") },
        help,
      ];
    case "TRAINING":
      return [
        { label: "Work", items: pick("training", "tasks", "directory") },
        help,
      ];
    case "MANAGER":
      return [
        { label: "Work", items: pick("manager", "tasks", "directory") },
        help,
      ];
    case "EMPLOYEE":
      return [{ label: "Onboarding", items: pick("portal", "tasks") }, help];
  }
}
