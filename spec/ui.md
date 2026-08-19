# Calls Calendar UI Requirements

## General

- The application is an English-language SPA with two routes: `/` and `/cal/:ownerId`.
- The name-entry form is shown before a user can access either route in a browser tab.
- The normalized name is stored in tab-scoped `sessionStorage`; it is sent with every API request as `X-User-Name`.
- The shell chooses the role from the entered name and URL: the calendar owner sees the owner UI when their name equals `ownerId`; all other users see the visitor UI.
- User names and API errors are displayed in the UI without exposing implementation details or HTTP status codes.
- Every page must provide loading, empty, and error feedback appropriate to its action.
- Use a responsive layout that remains usable in a narrow in-editor browser and on mobile-sized viewports.

## Date and time conventions

- Store, exchange, and calculate all dates and times in UTC.
- Do not show the `UTC` suffix to users in slot and booking lists.
- Display times in 24-hour format: `HH:mm`, for example `05:30` or `18:00`.
- Display booked-meeting date/time values as `YYYY.MM.DD HH:mm`, for example `2026.08.27 05:30`.
- Calendar month labels and selected-day labels are rendered in UTC.
- The calendar begins its week on Monday and shows weekday headings `Mon` through `Sun`.
- Availability and booking slots are fixed at 30 minutes. Owner time controls must offer only `HH:00` and `HH:30` values; seconds must not be displayed or requested.

## Shared calendar and slot-picker component

Both roles use the same monthly calendar layout:

- Show a month grid with previous/next month controls and a separate **Available times** panel.
- Each date tile shows its day number. Days with available slots also show the number of slots.
- Selecting a date updates the Available times panel to show only slots on that date.
- Each slot is displayed as `HH:mm–HH:mm` with the relevant role action.
- Dates before the current UTC date are disabled and visually muted for both roles.
- For visitors, dates without available slots are disabled; visitors cannot select or book them.
- For owners, future dates with no slots remain selectable so availability can be added.
- If the selected date has no available slots, show a clear empty-state message.
- If a calendar contains no available slots, still render the owner calendar picker; the visitor sees the appropriate no-availability state.

## Calendar directory control

Both the owner and visitor calendar pages show a control listing every existing calendar, so users can jump between calendars without knowing owner names in advance:

- Label the control **Other calendars** and render it as a list of links, one per existing calendar owner, each pointing to `/cal/{ownerId}`.
- Sort the list alphabetically by owner name.
- Exclude the calendar currently being viewed from the list.
- Show a clear empty-state message when no other calendars exist.
- Give the control its own loading and error feedback, independent of the calendar picker above it, so a failure to load the directory never blocks viewing or managing the current calendar.

## Name entry page

- Show the application title, a concise explanation, a required name input, and a **Continue** action.
- On submit, normalize/register the name through the Users API and remember the returned normalized name for the current tab.
- Show a validation or API error inline and preserve the submitted value for correction.

## Root page (`/`)

For an entered name:

- Show the owner create-calendar flow when the user has no calendar.
- Show the **Other calendars** directory control alongside the create-calendar flow,
  including when the entered user does not yet own a calendar.
- The create form has a single clear action to create the calendar named after the user.
- After successful creation, navigate to `/cal/{normalizedName}`.
- When the user already owns a calendar, provide a direct route to that calendar instead of offering a second creation action.

## Owner calendar page (`/cal/:ownerId`)

The owner page is shown only when the entered name matches `ownerId`.

- Display the calendar owner name and the public share path `/cal/{ownerId}`.
- Show the **Other calendars** directory control described above.
- Use the shared monthly calendar picker for availability management.
- Allow the owner to select any non-past day in the calendar.
- Below the calendar, show an **Add a time frame** form for the currently selected date.
  - Do not ask the owner for a date in this form.
  - Provide separate start-time and end-time dropdowns.
  - Both dropdowns contain 30-minute values only, from `00:00` through `23:30`.
  - Send the selected day and two chosen times as UTC availability bounds.
  - Show inline validation errors such as end time not being after start time or a range outside the four-week horizon.
- In the Available times panel, label the slot action **Remove**.
- Removing a free slot refreshes the calendar. A booked slot cannot be removed until its booking is cancelled.
- Show a **Booked meetings** section. Each item displays:
  - `YYYY.MM.DD HH:mm`
  - visitor name
  - **Cancel** action
- Cancelling a booking refreshes availability so the freed slot appears again.

## Visitor calendar page (`/cal/:ownerId`)

The visitor page is shown when the entered name differs from `ownerId`.

- Display the owner name and use the shared monthly calendar picker.
- Show the **Other calendars** directory control described above.
- Only dates with open slots may be selected.
- In the Available times panel, label the slot action **Book**.
- Selecting **Book** creates a booking for the currently entered name without asking for a second name.
- If booking returns a conflict because the view is stale, refetch the calendar and explain that the selected slot was just taken.
- Show a **My bookings** section containing only bookings made by the current visitor.
- Each booking displays `YYYY.MM.DD HH:mm` and a **Cancel** action.
- Cancelling refreshes the calendar and returns the slot to the available list.
- For a missing calendar, show a **Calendar not found** page with a link back to the root page.

## Visual and interaction requirements

- Use clear visual distinction for available, selected, disabled/past, and outside-month calendar dates.
- Use accessible button labels for month navigation and calendar days, including available-slot counts when applicable.
- Use semantic labels for all owner time controls.
- Disable controls when an action cannot be performed, rather than letting users submit an invalid date or slot selection.
- Ensure action buttons clearly state the outcome: **Continue**, **Create calendar**, **Publish availability**, **Book**, **Remove**, and **Cancel**.
