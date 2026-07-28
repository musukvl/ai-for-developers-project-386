# Happy Path Use Case: Create, Publish, Book

## Preconditions

- The application is running and the owner name/ID chosen below is not already in use.
- All dates and times are expressed in UTC.

## User Registration

1. An anonymous user opens the root page in a browser tab.
2. The application starts a tab session and assigns it an ID.
3. The session ID identifies calendars owned by this user, or bookings made by this user.

## Create Calendar

1. The owner sees the create-calendar form on the root page.
2. The owner enters a unique calendar name/ID, for example `alex`.
3. The owner clicks to the **Create** button.
4. The application creates the calendar at `/cal/alex` and makes it public.
5. The application redirects the owner to `/cal/alex`, where the calendar component is displayed.

## Publish Availability

1. The owner adds a one-off availability range within the next four weeks that starts and ends on 30-minute boundaries, for example 10:00-11:00 UTC.
2. The application publishes the range as two available 30-minute slots: 10:00-10:30 UTC and 10:30-11:00 UTC.
3. The owner can view both available slots and share the public URL `/cal/alex`.

## Book a Meeting

1. A visitor opens `/cal/alex`.
2. The application starts a tab session for the visitor and displays the published available slots.
3. The visitor selects the 10:00-10:30 UTC slot, enters their name, and confirms the booking.
4. The application reserves the slot for the visitor's current tab session and displays the booking to the visitor.
5. The 10:00-10:30 UTC slot is no longer available to other visitors; the 10:30-11:00 UTC slot remains available.
6. The owner refreshes `/cal/alex` and sees the upcoming 10:00-10:30 UTC booking with the visitor's name.

## Result

- The calendar remains public at `/cal/alex`.
- The owner has one calendar associated with their current tab session.
- The single booking is associated with the visitor's current tab session.
- The 10:00-10:30 UTC slot is no longer available to other visitors; the 10:30-11:00 UTC slot remains available.
- The visitor sees their booking in the calendar.
