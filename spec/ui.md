# Calls Calendar UI Requirements

## General

- The application is an English-language SPA. Routes:
  - `/` — guest event-type catalog (public calendar)
  - `/book/:eventTypeId` — generated slots for that type and booking confirmation
  - `/owner` — admin: create event types and upcoming meetings
- There is no name-entry page and no name stored in `sessionStorage`. Guests browse without an account. The guest types a name only on the booking confirmation form.
- Owner pages use the predefined owner profile with no sign-in.
- API errors are displayed in the UI without exposing implementation details or HTTP status codes.
- Every page must provide loading, empty, and error feedback appropriate to its action.
- Use a responsive layout that remains usable in a narrow in-editor browser and on mobile-sized viewports.

## Date and time conventions

- Store, exchange, and calculate all dates and times in UTC.
- Do not show the `UTC` suffix to users in slot and booking lists.
- Display times in 24-hour format: `HH:mm`, for example `05:30` or `18:00`.
- Display booked-meeting date/time values as `YYYY.MM.DD HH:mm`, for example `2026.08.27 05:30`.
- Calendar month labels and selected-day labels are rendered in UTC.
- The calendar begins its week on Monday and shows weekday headings `Mon` through `Sun`.
- Booking slots use the selected event type's duration, not a fixed 30 minutes. Seconds must not be displayed or requested.

## Shared calendar and slot-picker component

The guest booking calendar uses a monthly layout. Slots are system-generated for the selected event type; the owner does not add or remove them.

- Show a month grid with previous/next month controls and a separate **Available times** panel.
- Each date tile shows its day number. Days with available slots also show the number of slots.
- Selecting a date updates the Available times panel to show only slots on that date.
- Each slot is displayed as `HH:mm–HH:mm` with a **Book** action.
- Dates before the current UTC date are disabled and visually muted.
- Dates after the 14-day window (today through today+13 UTC) are disabled.
- Dates without available slots are disabled; guests cannot select or book them.
- If the selected date has no available slots, show a clear empty-state message.

## Guest event-types page (`/`)

- This is the public calendar. No login and no name field.
- List event types with title, description, and duration.
- Selecting a type navigates to `/book/{eventTypeId}`.
- Show an empty state when no event types exist.

## Guest booking page (`/book/:eventTypeId`)

- Show the selected event type's title, description, and duration.
- Use the shared monthly calendar picker for that type's generated slots.
- Only dates with open generated slots in the 14-day window may be selected.
- Choosing **Book** on a slot opens a confirmation that requires a guest name. Submitting sends `eventTypeId`, `slotStart`, and `guestName` in `POST /api/bookings`. Do not reuse or remember that name on later visits.
- Handle booking errors with user-friendly messages based on error code:
  - `slot_occupied` — "This slot was just taken. Please choose another time." Then refetch slots.
  - `slot_outside_window` — "This time is no longer available. Please select a different slot."
  - `slot_mismatch` — "Invalid time selected. Please choose from the available slots."
- After a successful booking, show confirmation with the time, event type, and the name just entered.
- If `{eventTypeId}` is unknown, show a not-found state with a link back to `/`.

## Owner page (`/owner`)

- No sign-in. This page is the admin part and uses the predefined owner profile by default.
- Provide a form to create an event type: id, title, description, and duration in minutes, in addition to the default `15m call` and `30m call`.
- Show an **Event types** section listing all event types. Each item displays title, description, duration, and a **Delete** action.
  - Deleting an event type prompts for confirmation.
  - If deletion fails with `future_bookings_exist`, show a message: "Cannot delete — cancel all upcoming bookings for this event type first."
  - After successful deletion, refresh the event types list.
- Show a **Booked meetings** section listing upcoming bookings of every event type in one list. Each item displays:
  - `YYYY.MM.DD HH:mm`
  - event type title
  - guest name given at booking time
  - **Cancel** action
- Cancelling a booking refreshes the list. The freed interval appears again as a generated slot on the guest calendar.
- Show a public link guests can open (the catalog at `/`).

## Visual and interaction requirements

- Use clear visual distinction for available, selected, disabled/past, and outside-month calendar dates.
- Use accessible button labels for month navigation and calendar days, including available-slot counts when applicable.
- Use semantic labels for slot times, the guest-name field, and booking actions.
- Disable controls when an action cannot be performed, rather than letting users submit an invalid date or slot selection.
- Ensure action buttons clearly state the outcome: **Book**, **Confirm booking**, **Create event type**, and **Cancel**.
