/**
 * The one module that talks to the backend: attaches `X-User-Name` and maps
 * error bodies to the four documented error codes, so components handle
 * `name_mismatch`, `not_found`, and `conflict` explicitly instead of
 * inspecting HTTP status codes.
 */

export const USER_NAME_STORAGE_KEY = "callsCalendarUserName";

export type ApiErrorCode = "validation_error" | "name_mismatch" | "not_found" | "conflict";

export class ApiError extends Error {
  readonly code: ApiErrorCode;

  constructor(code: ApiErrorCode, message: string) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

function currentUserName(): string | null {
  return sessionStorage.getItem(USER_NAME_STORAGE_KEY);
}

function isApiErrorCode(value: unknown): value is ApiErrorCode {
  return (
    value === "validation_error" ||
    value === "name_mismatch" ||
    value === "not_found" ||
    value === "conflict"
  );
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const userName = currentUserName();
  if (userName) {
    headers.set("X-User-Name", userName);
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
