import type {
  Case,
  CheckResult,
  DisplayStatus,
  Document,
  Hire,
} from "./api-types";

export type Tone = "ok" | "warn" | "bad" | "info" | "muted";

/** "RESERVED_COLLECTION_PENDING" becomes "Reserved collection pending". */
export function humanize(code: string): string {
  const words = code.replace(/[_-]+/g, " ").trim().toLowerCase();
  return words ? words[0].toUpperCase() + words.slice(1) : "";
}

const REASONS: Record<string, string> = {
  DOCUMENT_NOT_SUBMITTED: "No document has been submitted yet.",
  HUMAN_VERIFIED: "A person reviewed and verified the document.",
  DOCUMENT_REJECTED: "A person rejected the document.",
  DOCUMENT_RESUBMISSION_REQUESTED: "A person asked for the document again.",
  AWAITING_HUMAN_REVIEW: "Submitted, and waiting for a person to review it.",
  NO_EMPLOYMENT_DOCUMENT: "No signed employment document to compare against.",
  LOCATION_NOT_FOUND_IN_DOCUMENT:
    "No work location could be read from the employment document.",
  PROFILE_DOCUMENT_LOCATION_CONFLICT:
    "The profile location and the employment document disagree.",
  LOCATION_MATCHES: "The profile location matches the employment document.",
  NO_EQUIPMENT_RECORD: "No equipment record exists for this hire.",
  DEVICE_LOCATION_MISMATCH:
    "The device is at a different location from the hire.",
  HANDOVER_RECORDED: "A device handover is recorded.",
  RESERVED_COLLECTION_PENDING:
    "No handover is recorded. A reservation is not a delivery.",
  NO_ACCESS_RECORDS: "No access request records exist.",
  ACCESS_PENDING: "Some access requests are still waiting.",
  ACCESS_PROVISIONED_SIMULATED:
    "All access requests are marked provisioned (simulated).",
  NO_PAYROLL_RECORD: "No payroll record exists.",
  PAYROLL_CONFIRMED: "Payroll confirmed the setup.",
  PAYROLL_NOT_CONFIRMED: "Payroll has not confirmed the setup.",
  NO_BENEFITS_RECORD: "No benefits record exists.",
  BENEFITS_ENROLLED: "The benefits owner recorded enrolment.",
  BENEFITS_DECLINED: "A benefits decline is recorded.",
  BENEFITS_PENDING: "Benefits enrolment is not resolved yet.",
  NO_TRAINING_RECORDS: "No training records exist.",
  TRAINING_INCOMPLETE: "Some assigned training is not recorded as complete.",
  TRAINING_RECORDED_COMPLETE: "All assigned training is recorded as complete.",
  NO_MANAGER_PLAN: "No buddy or first-week plan is recorded.",
  BUDDY_AND_PLAN_RECORDED: "A buddy and first-week plan are recorded.",
};

export function reasonText(code: string): string {
  return REASONS[code] ?? humanize(code);
}

const CHECKS: Record<string, string> = {
  identity_document_verified: "Identity document verified",
  employment_document_verified: "Employment document verified",
  profile_location_confirmed: "Profile location confirmed",
  device_handover_recorded: "Device handover recorded",
  it_access_provisioned: "IT access provisioned",
  payroll_setup_confirmed: "Payroll setup confirmed",
  benefits_resolved: "Benefits resolved",
  training_completed: "Training completed",
  manager_plan_recorded: "Manager plan recorded",
};

export function checkLabel(checkType: string): string {
  return CHECKS[checkType] ?? humanize(checkType);
}

export const DOCUMENT_CATEGORIES: {
  id: Document["category"];
  label: string;
}[] = [
  { id: "government_id", label: "Government ID" },
  { id: "address_proof", label: "Address proof" },
  { id: "education", label: "Education" },
  { id: "previous_employment", label: "Previous employment" },
  { id: "bank_details", label: "Bank details" },
  { id: "tax", label: "Tax" },
  { id: "signed_employment", label: "Signed employment" },
];

export function documentCategoryLabel(category: string): string {
  return (
    DOCUMENT_CATEGORIES.find((item) => item.id === category)?.label ??
    humanize(category)
  );
}

const CATEGORY_LABELS: Record<string, string> = {
  documents: "Documents",
  equipment: "Equipment",
  it_access: "IT access",
  payroll: "Payroll",
  benefits: "Benefits",
  training: "Training",
  manager: "Manager",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? humanize(category);
}

const LOCATIONS: Record<string, string> = {
  "HYD-DEMO": "Hyderabad",
  "BLR-DEMO": "Bengaluru",
};

export function locationLabel(location: string): string {
  return LOCATIONS[location] ?? location;
}

export function hireRoleLabel(role: Hire["role"]): string {
  return humanize(role);
}

function parseDateOnly(value: string): Date | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (!match) return null;
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

const DATE = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});
const DATE_TIME = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

/** Date-only strings are calendar days; never shift them through a time zone. */
export function formatDate(value: string): string {
  const parsed = parseDateOnly(value);
  return parsed ? DATE.format(parsed) : value;
}

export function formatDateTime(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : DATE_TIME.format(parsed);
}

export function formatBytes(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function factValue(value: string | number | boolean | null): string {
  if (value === null) return "None";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

export function displayStatusTone(status: DisplayStatus): Tone {
  switch (status) {
    case "COMPLETED":
      return "ok";
    case "BLOCKED":
    case "OVERDUE":
      return "bad";
    case "PENDING_APPROVAL":
    case "IN_PROGRESS":
      return "warn";
    case "CANCELLED":
      return "muted";
    default:
      return "info";
  }
}

export function evidenceTone(result: CheckResult | null | undefined): Tone {
  switch (result) {
    case "VERIFIED":
      return "ok";
    case "BLOCKED":
      return "bad";
    case "UNKNOWN":
      return "warn";
    default:
      return "muted";
  }
}

export function onboardingTone(status: Hire["onboarding_status"]): Tone {
  if (status === "COMPLETED") return "ok";
  if (status === "BLOCKED") return "bad";
  if (status === "IN_PROGRESS") return "warn";
  return "info";
}

export function documentTone(state: Document["state"]): Tone {
  if (state === "VERIFIED") return "ok";
  if (state === "REJECTED" || state === "RESUBMISSION_REQUESTED") return "bad";
  if (state === "SUPERSEDED") return "muted";
  return "warn";
}

export function caseTone(state: Case["state"]): Tone {
  if (state === "RESOLVED") return "ok";
  if (state === "ESCALATED") return "bad";
  if (state === "WAITING_HUMAN" || state === "WAITING_APPROVAL") return "warn";
  return "info";
}

const ACCESS_ITEMS: Record<string, string> = {
  CORPORATE_EMAIL: "Corporate email",
  VPN: "VPN",
  APPLICATION_ACCESS: "Application access",
  REQUIRED_SOFTWARE: "Required software",
};

export function accessItemLabel(item: string): string {
  return ACCESS_ITEMS[item] ?? humanize(item);
}
