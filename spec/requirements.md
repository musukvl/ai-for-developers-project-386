# Calls calendar app: Functional Requirements

## Overview
The project is a simple educational project to demonstrate the backend and frontend application example.

## Roles
- Calendar Owner: A user who creates and manages a calendar with available meeting times. Identified by a name/ID in the URL.
- Calendar Visitor: A user who opens a public calendar link and books meetings. Identified by the current browser tab.

## Core Features
- Each user can create a calendar with available meeting times, and the calendar becomes public immediately after creation
- Available time slots are displayed as fixed 30-minute intervals
- Other users can view published calendars and book available time slots
- Calendar owners can view a list of upcoming booked meetings
- Prevent double-booking of the same time slot
- One calendar per owner
- Availability can be published up to 4 weeks (rolling) into the future
- Creating a calendar with an existing owner name/ID is rejected
- Existing bookings remain valid even if the owner later removes the surrounding availability
- No notifications — users refresh the page to see changes

## Calendar Owner Capabilities
- Create a personal calendar with a unique name/ID
- Define specific date/time ranges for availability (one-off blocks, not recurring)
- Time periods must be multiples of 30 minutes
- View all available time slots for their calendar
- View list of booked meetings with visitor name information
- Share a public link to their calendar for others to view
- Cancel booked meetings
- Access own calendar via owner name/ID in URL

## Calendar Visitor Capabilities  
- Open a public calendar directly by URL/ID
- View available time slots in a calendar format
- Book a 30-minute time slot by providing a visitor name (booking tied to the current browser tab)
- View their own bookings in calendar while using the same browser tab
- Cancel their bookings

## Constraints & Scope
- No user authentication or login system
- No personal account dashboards
- No integration with external calendar services
- No persistent storage of user data or bookings (in-memory storage only)
- All calendars are publicly accessible by URL/ID
- Single timezone support: UTC only
- No email or in-app notifications
- No recurring availability schedules
- Maximum booking horizon: 4 weeks from current date
- Server restart clears all calendars, availability, and bookings
- App could be started in tab-based session mode for testing purposes, or in browser-based session mode for production use. In tab-based session mode, the owner and visitor can be simulated in separate browser tabs. In browser-based session mode, the owner and visitor are identified by the current browser session.
