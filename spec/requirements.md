# Calls calendar app: Functional Requirements

## Overview
The project is a simple educational project to demonstrate the backend and frontend application example. This document describes external behaviour only: supported scenarios, data that is shown or stored, and booking constraints. Stack, internals, and project structure are chosen separately.

## Roles
- Calendar Owner: A single predefined profile. The owner creates event types and views upcoming meetings. This profile is used by default in the admin part of the application.
- Guest: Anyone browsing the public calendar. The guest views event types, picks a type, and books a free slot. The guest does not create an account and does not log in to browse or book.

There is no registration and no authentication. There are no passwords.

## User Identity
- Do not ask for a name on a start page, and do not remember a name per tab. That would be login. Guests browse and book without signing in.
- The owner is a single predefined profile used by the admin pages. There is no sign-in and no password.
- Do ask for the guest's name when they confirm a slot. That booking name is stored on that booking only so the owner's upcoming-meetings list can show who is coming. It is not an account, it does not log the guest in, and using the same name later does not restore a session.

## Event Types
- The calendar has event types that a guest picks before booking. An event type has an id, a title, a description, and a duration in minutes.
- The calendar has two default event types: `15m call` (15 minutes) and `30m call` (30 minutes).
- The calendar owner can create additional custom event types and set each type's id, title, description, and duration in minutes.
- The owner's upcoming-meetings list shows bookings of every event type together in one list.
- Occupancy is by clock time, not by event type: two bookings cannot overlap, even when they are different event types.

## Slot generation
- The owner does not set, edit, or remove available slots. The backend generates them.
- Available slots are formed for 14 UTC calendar days starting from the current UTC date: today through today+13.
- For the selected event type, each of those days is filled with consecutive slots of that type's duration in minutes, starting at `00:00` UTC. A slot must start and end on the same UTC date.
- A slot whose start has already passed is not offered.
- A guest can book only a free generated slot from that window.
- A booking occupies its clock interval for every event type: any generated slot that overlaps a booking is not free.
- Cancelling a booking frees that interval. The slot is offered again because the grid is regenerated, not because stored availability was restored.

## Core Features
- There is a single public calendar with a predefined owner.
- Guests open the public calendar, view its event types, choose a type, and book a free slot of that type inside the 14-day window.
- The owner views a list of upcoming booked meetings across all event types.
- Prevent double-booking of the same time, including across different event types.
- Cancelling a booking returns that interval to the generated free-slot list.
- No notifications — users refresh the page to see changes.

## Calendar Owner Capabilities
- The owner is a single predefined profile with no sign-in required.
- Create custom event types (id, title, description, duration in minutes) in addition to the default `15m call` and `30m call`.
- Delete custom event types, but only if no upcoming bookings reference that type. Default event types cannot be deleted while they have future bookings.
- View a page of upcoming meetings that lists bookings of every event type in one list, showing the guest name given at booking time and the event type.
- Share a public link to the calendar for guests to view.
- Cancel booked meetings.

## Guest Capabilities
- Open the public calendar with no account and no login.
- View a page of event types showing title, description, and duration.
- Select an event type, open the calendar, and pick a free slot in the next 14 days.
- Confirm a booking on the selected slot by entering a guest name. The booking stores the chosen event type and that name. That guest name is not a login and is not remembered.

## Constraints & Scope
- No registration, no passwords, and no authentication.
- No personal account dashboards, no guest sessions, and no start-page name remembered per tab.
- No integration with external calendar services.
- No persistent storage of event types or bookings (in-memory storage only). Slots are not stored; they are generated on each request.
- The calendar is publicly accessible by URL.
- Single timezone support: UTC only.
- No email or in-app notifications.
- No owner-published availability and no recurring availability schedules.
- Maximum booking horizon: 14 days from the current date.
- Server restart clears event types and bookings; nothing survives a restart except the declared seed data, which is loaded again on every start.
- Seeded demo data recreates the predefined owner profile, the default event types (`15m call`, `30m call`), and any declared demo bookings.
