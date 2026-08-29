import type { ApiErrorCode } from "./types";

const ERROR_CODES: ReadonlySet<string> = new Set([
  "validation_error",
  "not_found",
  "conflict",
  "slot_occupied",
  "slot_outside_window",
  "slot_mismatch",
  "future_bookings_exist",
]);

export class ApiError extends Error {
  readonly code: ApiErrorCode;

  constructor(code: ApiErrorCode, message: string) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

function isApiErrorCode(value: unknown): value is ApiErrorCode {
  return typeof value === "string" && ERROR_CODES.has(value);
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...init, headers });
  } catch {
    throw new ApiError("validation_error", "Could not reach the server. Please try again.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const body: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const errorBody = body as { error?: { code?: unknown; message?: unknown } } | null;
    const code = errorBody?.error?.code;
    const message = errorBody?.error?.message;
    throw new ApiError(
      isApiErrorCode(code) ? code : "validation_error",
      typeof message === "string" ? message : "Something went wrong. Please try again."
    );
  }

  return body as T;
}

export const apiClient = {
  get: <T>(path: string): Promise<T> => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown): Promise<T> =>
    request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  del: <T = void>(path: string): Promise<T> => request<T>(path, { method: "DELETE" }),
};
