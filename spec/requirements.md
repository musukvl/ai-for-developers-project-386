# Calls Calendar App: Functional Requirements

## Overview

A simple educational project demonstrating a backend and frontend application. This document describes external behaviour only: supported scenarios, data shown or stored, and booking constraints. Stack, internals, and project structure are in `implementation.md`.

## Roles

- **Calendar Owner**: A single predefined profile used by the admin pages. Creates event types and views upcoming meetings. No sign-in and no password.
- **Guest**: Anyone browsing the public calendar. Views event types, picks a type, and books a free slot. No account, no login, no registration.

## User Identity

- Do not ask for a name on a start page, and do not remember a name per tab.
- Ask for the guest's name only when they confirm a slot. That name is stored on that booking only so the owner can see who is coming. It is not an account and is not remembered.

## Event Types

- The unit a guest picks before booking is an **event type**, not an owner calendar. There is a single public calendar.
- An event type has: id, title, description, and duration in minutes.
- A booking stores `eventTypeId`, `eventTypeTitle`, the slot times, and `guestName`. Time and guest name alone are not enough.
- The public catalog lists event types. It must not list owner calendars or a calendar directory.
- Default event types: `15m call` (15 min) and `30m call` (30 min).
- The owner can create additional event types and delete them if no upcoming bookings reference that type.

## Slot Generation and the 14-Day Window

- The backend generates available slots. The owner does not publish, edit, or remove availability.
- **Window**: 14 UTC calendar days from the current UTC date: today through today+13. A slot on today+14 (the 15th calendar day) is outside the window.
- For the selected event type, each day is filled with consecutive slots of that type's duration starting at `00:00` UTC. A slot must start and end on the same UTC date.
- Slots whose start has already passed are not offered.

## Occupancy

- Occupancy is by clock time, not by event type: two bookings cannot overlap, even when they are different event types.
- Example: a booking of `30m call` at 10:00–10:30 occupies that interval for `15m call` as well.
- Cancelling a booking frees that interval. The slot reappears because the grid is regenerated, not because stored availability is restored.

## Owner Capabilities

- Create and delete event types.
- View upcoming meetings across all event types in one list, showing event type title and guest name.
- Cancel booked meetings.
- Share the public link to the calendar.

## Guest Capabilities

- Open the public calendar with no account.
- View event types (title, description, duration).
- Select a type, pick a free slot in the 14-day window, and confirm by entering a guest name.

## Constraints & Scope

- No persistent storage; in-memory only. Slots are generated on each request.
- Single timezone: UTC only.
- No email or in-app notifications.
- Server restart reloads seed data; nothing else survives.
