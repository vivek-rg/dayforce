import type { Bootstrap, ErrorResponse } from "./api-types";

// Relative URLs keep browser traffic on the same origin; never put model keys here.
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init);
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const body = (await response.json()) as ErrorResponse;
      message = body.error?.message ?? message;
    } catch {
      // A proxy/transport error need not contain JSON.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function fetchBootstrap(signal?: AbortSignal) {
  return request<Bootstrap>("/bootstrap", { signal });
}
