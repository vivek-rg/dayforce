import type {
  AcceptedWork,
  AiHealth,
  AiRunList,
  AssistantAnswer,
  AuditEventList,
  Bootstrap,
  Case,
  CaseList,
  Category,
  DecisionRequest,
  DecisionResult,
  Document,
  DocumentExtraction,
  DocumentList,
  DocumentReviewRequest,
  ErrorDetail,
  ErrorResponse,
  Escalation,
  EscalationList,
  Hire,
  HireCreate,
  HireList,
  InsightMetrics,
  InsightSummary,
  KnowledgeDocument,
  KnowledgeDocumentList,
  Metrics,
  NotificationList,
  Overview,
  Plan,
  PreviewRequest,
  Proposal,
  ProposalList,
  QuestionList,
  Reference,
  Session,
  SourceRecord,
  SourceRecordList,
  SourceWrite,
  SweepResult,
  Task,
  TaskList,
  User,
} from "./api-types";

// The token lives in this module only. A refresh signs the user out, by design.
let accessToken: string | null = null;
let onUnauthorized: (() => void) | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function setUnauthorizedHandler(handler: (() => void) | null) {
  onUnauthorized = handler;
}

/** A server error. `message` is the server's own text, safe to show as-is. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: ErrorDetail[];

  constructor(
    status: number,
    code: string,
    message: string,
    details: ErrorDetail[] = [],
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function withAuth(init?: RequestInit): RequestInit | undefined {
  if (!accessToken) return init;
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${accessToken}`);
  return { ...init, headers };
}

async function toApiError(response: Response): Promise<ApiError> {
  let code = `HTTP_${response.status}`;
  let message = `Request failed (${response.status}).`;
  let details: ErrorDetail[] = [];
  try {
    const body = (await response.json()) as ErrorResponse;
    code = body.error?.code ?? code;
    message = body.error?.message ?? message;
    details = body.error?.details ?? [];
  } catch {
    // A proxy/transport error need not contain JSON.
  }
  if (response.status === 401 && accessToken) onUnauthorized?.();
  return new ApiError(response.status, code, message, details);
}

// Relative URLs keep browser traffic on the same origin; never put model keys here.
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, withAuth(init));
  if (!response.ok) throw await toApiError(response);
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function fetchBootstrap(signal?: AbortSignal) {
  return request<Bootstrap>("/bootstrap", { signal });
}

function get<T>(path: string, signal?: AbortSignal) {
  return request<T>(path, { signal });
}

function send<T>(method: "POST" | "PUT", path: string, body?: unknown) {
  return request<T>(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
}

// No Content-Type here: the browser must set the multipart boundary itself.
function upload<T>(path: string, form: FormData) {
  return request<T>(path, { method: "POST", body: form });
}

const id = encodeURIComponent;

type Payload = SourceRecord["payload"];
export type SourceOf<C extends Category> = Omit<SourceRecord, "payload"> & {
  payload: Extract<Payload, { category: C }>;
};

/** Narrows a mixed source list to one category's payload type. */
export function sourcesOfCategory<C extends Category>(
  items: SourceRecord[],
  category: C,
): SourceOf<C>[] {
  return items.filter(
    (item) => item.payload.category === category,
  ) as SourceOf<C>[];
}

export const api = {
  login: (user_id: string, password: string) =>
    send<Session>("POST", "/sessions", { user_id, password }),
  logout: () => request<void>("/sessions/current", { method: "DELETE" }),
  me: (signal?: AbortSignal) => get<User>("/me", signal),
  reference: (signal?: AbortSignal) => get<Reference>("/reference", signal),
  aiHealth: (signal?: AbortSignal) => get<AiHealth>("/health/ai", signal),

  hires: (signal?: AbortSignal) => get<HireList>("/hires", signal),
  hire: (hireId: string, signal?: AbortSignal) =>
    get<Hire>(`/hires/${id(hireId)}`, signal),
  createHire: (body: HireCreate) => send<Hire>("POST", "/hires", body),
  plan: (hireId: string, signal?: AbortSignal) =>
    get<Plan>(`/hires/${id(hireId)}/plan`, signal),
  history: (hireId: string, signal?: AbortSignal) =>
    get<AuditEventList>(`/hires/${id(hireId)}/history`, signal),

  myWork: (signal?: AbortSignal) => get<TaskList>("/my-work", signal),
  startTask: (taskId: string, expected_version: number) =>
    send<Task>("POST", `/tasks/${id(taskId)}/start`, { expected_version }),
  completeTask: (taskId: string, expected_version: number) =>
    send<Task>("POST", `/tasks/${id(taskId)}/complete`, { expected_version }),
  reassignTask: (
    taskId: string,
    expected_version: number,
    owner_user_id: string,
  ) =>
    send<Task>("POST", `/tasks/${id(taskId)}/reassign`, {
      expected_version,
      owner_user_id,
    }),

  sources: async <C extends Category>(category: C, signal?: AbortSignal) => {
    const list = await get<SourceRecordList>(
      `/sources?category=${id(category)}`,
      signal,
    );
    return sourcesOfCategory(list.items, category);
  },
  writeSource: (hireId: string, sourceId: string, body: SourceWrite) =>
    send<SourceRecord>(
      "PUT",
      `/hires/${id(hireId)}/sources/${id(sourceId)}`,
      body,
    ),

  hireDocuments: (hireId: string, signal?: AbortSignal) =>
    get<DocumentList>(`/hires/${id(hireId)}/documents`, signal),
  uploadHireDocument: (
    hireId: string,
    category: Document["category"],
    file: File,
  ) => {
    const form = new FormData();
    form.append("category", category);
    form.append("file", file);
    return upload<Document>(`/hires/${id(hireId)}/documents`, form);
  },
  documentQueue: (signal?: AbortSignal) =>
    get<DocumentList>("/documents/queue", signal),
  runExtraction: (documentId: string) =>
    send<DocumentExtraction>(
      "POST",
      `/documents/${id(documentId)}/extractions`,
    ),
  /** A 404 means no extraction has run yet, which is not an error. */
  latestExtraction: async (documentId: string, signal?: AbortSignal) => {
    try {
      return await get<DocumentExtraction>(
        `/documents/${id(documentId)}/extractions/latest`,
        signal,
      );
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 404) return null;
      throw reason;
    }
  },
  reviewDocument: (documentId: string, body: DocumentReviewRequest) =>
    send<Document>("POST", `/documents/${id(documentId)}/reviews`, body),

  openCase: (hireId: string, message: string) =>
    send<AcceptedWork>("POST", `/hires/${id(hireId)}/cases`, { message }),
  hireCases: (hireId: string, signal?: AbortSignal) =>
    get<CaseList>(`/hires/${id(hireId)}/cases`, signal),
  getCase: (caseId: string, signal?: AbortSignal) =>
    get<Case>(`/cases/${id(caseId)}`, signal),
  questions: (signal?: AbortSignal) => get<QuestionList>("/questions", signal),
  answerQuestion: (questionId: string, answer: string) =>
    send<AcceptedWork>("POST", `/questions/${id(questionId)}/responses`, {
      answer,
    }),

  reviewInbox: (signal?: AbortSignal) =>
    get<ProposalList>("/review-inbox", signal),
  proposal: (proposalId: string, signal?: AbortSignal) =>
    get<Proposal>(`/proposals/${id(proposalId)}`, signal),
  changePreview: (hireId: string, body: PreviewRequest) =>
    send<Proposal>("POST", `/hires/${id(hireId)}/change-previews`, body),
  equipmentRequest: (hireId: string, equipment_record_id: string) =>
    send<Proposal>("POST", `/hires/${id(hireId)}/equipment-requests`, {
      equipment_record_id,
    }),
  decide: (proposalId: string, body: DecisionRequest) =>
    send<DecisionResult>(
      "POST",
      `/proposals/${id(proposalId)}/decisions`,
      body,
    ),

  ask: (question: string) =>
    send<AssistantAnswer>("POST", "/assistant/questions", { question }),
  escalate: (question: string, ai_run_id: string | null) =>
    send<Escalation>("POST", "/assistant/escalations", { question, ai_run_id }),
  escalations: (signal?: AbortSignal) =>
    get<EscalationList>("/assistant/escalations", signal),
  myEscalations: (signal?: AbortSignal) =>
    get<EscalationList>("/assistant/escalations/mine", signal),
  answerEscalation: (escalationId: string, answer: string) =>
    send<Escalation>(
      "POST",
      `/assistant/escalations/${id(escalationId)}/answers`,
      { answer },
    ),

  knowledgeDocuments: (signal?: AbortSignal) =>
    get<KnowledgeDocumentList>("/knowledge/documents", signal),
  uploadKnowledge: (
    title: string,
    access_level: KnowledgeDocument["access_level"],
    file: File,
  ) => {
    const form = new FormData();
    form.append("title", title);
    form.append("access_level", access_level);
    form.append("file", file);
    return upload<KnowledgeDocument>("/knowledge/documents", form);
  },
  approveKnowledge: (documentId: string, version: number) =>
    send<KnowledgeDocument>(
      "POST",
      `/knowledge/documents/${id(documentId)}/approve`,
      { version },
    ),

  notifications: (signal?: AbortSignal) =>
    get<NotificationList>("/notifications", signal),
  markRead: (notificationId: string) =>
    request<void>(`/notifications/${id(notificationId)}/read`, {
      method: "POST",
    }),
  sweep: () => send<SweepResult>("POST", "/notifications/sweep"),

  overview: (signal?: AbortSignal) =>
    get<Overview>("/analytics/overview", signal),
  insightMetrics: (signal?: AbortSignal) =>
    get<InsightMetrics>("/insights/metrics", signal),
  insightSummary: () => send<InsightSummary>("POST", "/insights/summaries"),
  auditEvents: (signal?: AbortSignal) =>
    get<AuditEventList>("/audit-events", signal),
  aiRuns: (signal?: AbortSignal) => get<AiRunList>("/ai-runs", signal),
  metrics: (signal?: AbortSignal) => get<Metrics>("/metrics", signal),
};

/** Fetches a private document with the auth header and hands it to the browser as a file. */
export async function downloadDocument(documentId: string, filename: string) {
  const response = await fetch(
    `/api/documents/${id(documentId)}/content`,
    withAuth(),
  );
  if (!response.ok) throw await toApiError(response);
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
