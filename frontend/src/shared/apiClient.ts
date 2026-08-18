export type ErrorCode = 'validation_error' | 'name_mismatch' | 'not_found' | 'conflict'

export class ApiError extends Error {
  constructor(public readonly code: ErrorCode, message: string) {
    super(message)
  }
}

export type Slot = { start: string; end: string }
export type Booking = { id: string; start: string; end: string; visitorName: string }
export type OwnerCalendar = { ownerId: string; availableSlots: Slot[]; bookings: Booking[] }
export type VisitorCalendar = { ownerId: string; availableSlots: Slot[]; myBookings: Booking[] }

let userName = ''

export function setApiUserName(name: string): void {
  userName = name
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (userName) headers.set('X-User-Name', userName)
  if (options.body) headers.set('Content-Type', 'application/json')
  const response = await fetch(`/api${path}`, { ...options, headers })
  if (response.status === 204) return undefined as T
  const body = await response.json()
  if (!response.ok) throw new ApiError(body.error.code as ErrorCode, body.error.message)
  return body as T
}
