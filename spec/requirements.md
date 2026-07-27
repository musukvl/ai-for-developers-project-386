# Calls calendar app

The project is a simple educational project to demonstrate the backend and frontend application example.

## Functional Requirements

### Core Features
- Each user can create and publish a calendar with available meeting times
- Available time slots are displayed as 30-minute intervals
- Other users can view published calendars and book available time slots
- Calendar owners can view a list of upcoming booked meetings
- Prevent double-booking of the same time slot

### Calendar Owner Capabilities
- Create a personal calendar
- Define time periods for availability
- Time periods must be multiples of 30 minutes
- View all available time slots for their calendar
- View list of booked meetings with visitor information
- Share a public link to their calendar for others to view
- Cancel booked meetings

### Calendar Visitor Capabilities  
- Browse available public calendars
- View available time slots in a calendar format
- View their own bookings in calendar
- Cancel their bookings

### Constraints & Scope
- No user authentication or login system
- No personal account dashboards
- No integration with external calendar services
- No persistent storage of user data or bookings (in-memory storage only)
- All calendars are publicly accessible by URL/ID
- Single timezone support (UTC or configurable)
