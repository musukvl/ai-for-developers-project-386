# Happy Path Use Case: Choose Event Type, Book a Generated Slot

## Preconditions

- The application is running with the default seed: the predefined owner profile and the default event types `15m call` (15 minutes) and `30m call` (30 minutes).
- There is no start-page name and no remembered identity. The guest types a name only when confirming a slot.
- The owner does not publish availability. The backend generates free slots for 14 UTC calendar days starting from the current UTC date (today through today+13).
- For `30m call`, each of those days is filled with consecutive 30-minute slots from `00:00` UTC to `23:30` UTC. Slots whose start has already passed are not offered.
- All dates and times are expressed in UTC.

## Choose an Event Type

1. A guest opens `/` with no account and no login.
2. The application shows the event-types catalog. Each type shows its title, description, and duration.
3. The guest selects `30m call` and the app navigates to `/book/thirty-minute-call`.

## Book a Meeting

1. The application shows the calendar for `30m call` and the generated free slots in the next 14 days.
2. The guest selects tomorrow `10:00–10:30` UTC, types the name `Sam` on the confirmation form, and confirms. That name is for this booking only and is not remembered.
3. The application reserves that clock interval and shows a confirmation for `Sam` on `30m call`.
4. Tomorrow `10:00–10:30` UTC is no longer free for any event type, including `15m call`. The neighbouring generated slots (`09:30–10:00` and `10:30–11:00` for `30m call`) remain free.
5. The owner opens `/owner` (no sign-in) and sees the upcoming meeting: tomorrow `10:00`, guest `Sam`, event type `30m call`.

## Result

- The guest booked a system-generated slot without the owner setting availability and without logging in.
- The booking stores guest name `Sam` so the owner can see who is coming.
- The booking occupies `10:00–10:30` UTC tomorrow for every event type.
- The owner's upcoming list shows that booking together with bookings of any other event type.
- Cancelling the booking on `/owner` would offer `10:00–10:30` UTC again, because the slot grid is regenerated on each request.
