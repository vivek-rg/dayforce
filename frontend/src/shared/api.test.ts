import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchBootstrap, request } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("shared HTTP boundary", () => {
  it("reads the database-backed bootstrap through the API prefix", async () => {
    const payload = {
      project_name: "DayOne Proof",
      message: "Connected",
      foundation_only: true,
    };
    const fetcher = vi.fn().mockResolvedValue(Response.json(payload));
    vi.stubGlobal("fetch", fetcher);
    await expect(fetchBootstrap()).resolves.toEqual(payload);
    expect(fetcher).toHaveBeenCalledWith("/api/bootstrap", {
      signal: undefined,
    });
  });

  it("surfaces the server error rather than reporting success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            error: {
              code: "FEATURE_NOT_IMPLEMENTED",
              message: "Not implemented",
              details: [],
            },
          },
          { status: 501 },
        ),
      ),
    );
    await expect(request("/hires")).rejects.toThrow("Not implemented");
  });

  it("handles a non-JSON upstream failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("unavailable", { status: 503 })),
    );
    await expect(fetchBootstrap()).rejects.toThrow("503");
  });
});
