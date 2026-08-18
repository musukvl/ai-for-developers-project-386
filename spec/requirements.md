# Calls calendar app: Functional Requirements

## Overview
The project is a simple educational project to demonstrate the backend and frontend application example.

## Roles
- User: Anyone using the app, identified by the name entered on the start page. The same name always means the same user.
- Calendar Owner: A user whose name matches the calendar name/ID in the URL. Creates and manages that calendar's available meeting times.
- Calendar Visitor: A user whose name does not match the calendar name/ID in the URL. Views available slots and books meetings.

## User Identity
- The user enters a name on the start page before viewing or using any calendar
- The name is trimmed and normalized to lowercase; the normalized name is the user ID used in storage, in the API, and in URLs
- Entering an existing name logs the user in as that user; entering a new name registers it. There are no passwords and no verification step
- The application remembers the entered name so it does not have to be retyped on every page
- The role is derived per calendar: entering `sam` and opening `/cal/sam` shows the owner view, while entering `sam` and opening `/cal/vasya` shows the visitor view

## Core Features
- Each user can create a calendar with available meeting times, and the calendar becomes public immediately after creation
- A calendar's name/ID is always the owner's user name
- Available time slots are displayed as fixed 30-minute intervals
- Other users can view published calendars and book available time slots
- Calendar owners can view a list of upcoming booked meetings
- Prevent double-booking of the same time slot
- One calendar per owner; a second create attempt by the same user is rejected
- Opening `/cal/{name}` for a calendar that does not exist offers creation when `{name}` is the entered name, and otherwise shows a "calendar not found" page
- Availability can be published up to 4 weeks (rolling) into the future
- A slot is either free or booked and always stays in the calendar; a booked slot cannot be removed while the booking exists, and removing neighbouring slots never affects it
- To free a booked time the owner cancels the booking first and then removes the slot
- Cancelling a booking returns its slot to the available list, whether the owner or the visitor cancelled it
- No notifications — users refresh the page to see changes

## Calendar Owner Capabilities
- Create a personal calendar named after the owner's user name
- Define specific date/time ranges for availability (one-off blocks, not recurring)
- Time periods must be multiples of 30 minutes
- View all available time slots for their calendar
- View list of booked meetings with visitor name information
- Share a public link to their calendar for others to view
- Cancel booked meetings
- Access own calendar at `/cal/{name}` while entered under that name

## Calendar Visitor Capabilities  
- Open a public calendar directly by URL/ID after entering a name
- View available time slots in a calendar format
- Book a 30-minute time slot; the booking is tied to the visitor's entered name
- View their own bookings in calendar while entered under the same name
- Cancel their bookings

## Constraints & Scope
- No passwords and no authentication: entering a name is enough to act as that user
- No personal account dashboards
- No integration with external calendar services
- No persistent storage of users, calendars or bookings (in-memory storage only)
- All calendars are publicly accessible by URL/ID
- Single timezone support: UTC only
- No email or in-app notifications
- No recurring availability schedules
- Maximum booking horizon: 4 weeks from current date
- Server restart clears all users, calendars, availability, and bookings; nothing survives a restart except the declared seed data, which is loaded again on every start
- Seeded demo data uses reserved names (`demo-owner`, `demo-visitor`), so names used in the use cases are free on a freshly started app
- The entered name is remembered per browser tab, so owner and visitor can be simulated by entering different names in separate tabs. Opening a new tab asks for the name again.
