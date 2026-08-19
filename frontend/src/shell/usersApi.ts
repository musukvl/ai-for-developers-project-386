/** Users API: the only call the shell makes directly (name entry belongs to the shell). */

import { apiClient } from "../api/client";
import type { EnterNameResult } from "../api/types";

export function enterName(rawName: string): Promise<EnterNameResult> {
  return apiClient.post<EnterNameResult>("/users", { name: rawName });
}
