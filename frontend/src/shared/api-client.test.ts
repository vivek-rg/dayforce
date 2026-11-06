import { afterEach, describe, expect, it, vi } from "vitest";
import {
  ApiError,
  api,
  request,
  setAccessToken,
  setUnauthorizedHandler,
  sourcesOfCategory,
} from "./api";
import type { SourceRecord } from "./api-types";

afterEach(() => {
  vi.unstubAllGlobals();
  setAccessToken(null);
  setUnauthorizedHandler(null);
});

function stubFetch(response: Response) {
  const fetcher = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetcher);
  return fetcher;
}

const headersOf = (fetcher: ReturnType<typeof vi.fn>) =>
  new Headers((fetcher.mock.calls[0][1] as RequestInit).headers);

describe("API client auth header", () => {
  it("sends no Authorization header without a token", async () => {
    const fetcher = stubFetch(Response.json({ items: [] }));
    await api.hires();
    expect(headersOf(fetcher).has("Authorization")).toBe(false);
  });

  it("adds the bearer token once one is set", async () => {
    const fetcher = stubFetch(Response.json({ items: [] }));
    setAccessToken("secret-token");
    await api.hires();
    expect(headersOf(fetcher).get("Authorization")).toBe("Bearer secret-token");
  });

  it("keeps the JSON content type alongside the token", async () => {
    const fetcher = stubFetch(Response.json({}));
    setAccessToken("secret-token");
    await api.startTask("T1", 3);
    const init = fetcher.mock.calls[0][1] as RequestInit;
    expect(fetcher.mock.calls[0][0]).toBe("/api/tasks/T1/start");
    expect(headersOf(fetcher).get("Content-Type")).toBe("application/json");
    expect(init.body).toBe(JSON.stringify({ expected_version: 3 }));
  });

  it("lets the browser set the multipart boundary for uploads", async () => {
    const fetcher = stubFetch(Response.json({}, { status: 201 }));
    setAccessToken("secret-token");
    await api.uploadHireDocument(
      "H1",
      "tax",
      new File(["x"], "tax.txt", { type: "text/plain" }),
    );
    const init = fetcher.mock.calls[0][1] as RequestInit;
    expect(init.body).toBeInstanceOf(FormData);
    expect((init.body as FormData).get("category")).toBe("tax");
    expect(headersOf(fetcher).has("Content-Type")).toBe(false);
  });
});

describe("API client errors", () => {
  it("exposes status, code, details and the server message", async () => {
    stubFetch(
      Response.json(
        {
          error: {
            code: "STALE_VERSION",
            message: "This record changed. Reload and try again.",
            details: [{ field: "expected_version", message: "old" }],
          },
        },
        { status: 409 },
      ),
    );
    const error: unknown = await request("/x").catch(
      (reason: unknown) => reason,
    );
    expect(error).toBeInstanceOf(ApiError);
    const apiError = error as ApiError;
    expect(apiError.message).toBe("This record changed. Reload and try again.");
    expect(apiError.status).toBe(409);
    expect(apiError.code).toBe("STALE_VERSION");
    expect(apiError.details).toHaveLength(1);
  });

  it("falls back to an HTTP code when the body is not JSON", async () => {
    stubFetch(new Response("bad gateway", { status: 502 }));
    await expect(request("/x")).rejects.toMatchObject({
      status: 502,
      code: "HTTP_502",
    });
  });

  it("signs out on 401 only when a token was in use", async () => {
    const handler = vi.fn();
    setUnauthorizedHandler(handler);
    const expired = () =>
      Response.json(
        { error: { code: "UNAUTHENTICATED", message: "Sign in." } },
        { status: 401 },
      );
    stubFetch(expired());
    await expect(request("/sessions")).rejects.toBeInstanceOf(ApiError);
    expect(handler).not.toHaveBeenCalled();
    setAccessToken("token");
    stubFetch(expired());
    await expect(request("/me")).rejects.toBeInstanceOf(ApiError);
    expect(handler).toHaveBeenCalledOnce();
  });

  it("treats a missing extraction as none, and other failures as errors", async () => {
    stubFetch(
      Response.json(
        { error: { code: "NOT_FOUND", message: "No" } },
        { status: 404 },
      ),
    );
    await expect(api.latestExtraction("D1")).resolves.toBeNull();
    stubFetch(
      Response.json(
        { error: { code: "FORBIDDEN", message: "No" } },
        { status: 403 },
      ),
    );
    await expect(api.latestExtraction("D1")).rejects.toMatchObject({
      status: 403,
    });
  });
});

describe("sourcesOfCategory", () => {
  it("keeps only the requested category", () => {
    const base = {
      hire_id: "H1",
      version: 1,
      observed_at: "2026-01-01T00:00:00Z",
    };
    const items: SourceRecord[] = [
      {
        ...base,
        id: "a",
        payload: { category: "training", course_id: "C", state: "ASSIGNED" },
      },
      { ...base, id: "b", payload: { category: "benefits", state: "INVITED" } },
    ];
    expect(sourcesOfCategory(items, "benefits").map((item) => item.id)).toEqual(
      ["b"],
    );
  });
});
