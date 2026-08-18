# Happy Path Use Case: Enter Name, Create, Publish, Book

## Preconditions

- The application is running and the owner name chosen below is not already in use. Seed data only declares reserved demo names, so `alex` and `sam` are free on a freshly started app.
- All dates and times are expressed in UTC.

## Enter Name

1. An anonymous user opens the root page in a browser tab.
2. The application shows the name entry form, because no name is remembered yet.
3. The user enters a name, for example `Alex`, and submits it.
4. The application normalizes the name to `alex`. The name is unknown, so it is registered; had it been known, the same step would have signed the user in.
5. The application remembers `alex` and sends it as the user name on every later API request.

## Create Calendar

1. The user has no calendar yet, so the root page mounts the owner module, which shows the create-calendar form.
2. The user confirms creation; the calendar is named after the user, `alex`.
3. The application creates the calendar at `/cal/alex` and makes it public.
4. The application redirects the user to `/cal/alex`.
5. Because the entered name `alex` matches the calendar name, the owner component is displayed.

## Publish Availability

1. The owner adds a one-off availability range within the next four weeks that starts and ends on 30-minute boundaries, for example 10:00-11:00 UTC.
2. The application publishes the range as two available 30-minute slots: 10:00-10:30 UTC and 10:30-11:00 UTC.
3. The owner can view both available slots and share the public URL `/cal/alex`.

## Book a Meeting

1. Another user opens `/cal/alex` in a separate browser tab and is asked to enter a name first, because the name is remembered per tab.
2. The user enters `Sam`, which normalizes to `sam` and is registered.
3. Because `sam` does not match the calendar name `alex`, the visitor component is displayed with the published available slots.
4. The visitor selects the 10:00-10:30 UTC slot and confirms the booking; no extra name is needed, since the booking is made under the entered name.
5. The application reserves the slot for `sam` and displays the booking to the visitor.
6. The 10:00-10:30 UTC slot is no longer available to other visitors; the 10:30-11:00 UTC slot remains available.
7. The owner refreshes `/cal/alex` and sees the upcoming 10:00-10:30 UTC booking with the visitor's name `sam`.

## Result

- The calendar remains public at `/cal/alex` and is owned by the user `alex`.
- The user `alex` has one calendar; the user `sam` has none.
- The single booking is associated with the user `sam`.
- The 10:00-10:30 UTC slot is no longer available to other visitors; the 10:30-11:00 UTC slot remains available.
- The visitor sees their booking in the calendar whenever they are entered as `sam`.
