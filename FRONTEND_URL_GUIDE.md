# Frontend URL Guide - Remove `/api/` Prefix

## ✅ Frontend URLs (Return HTML)
Use these URLs in your web app navigation:

### Events
- Homepage: `/` 
- Event List: `/events/`
- Event Detail: `/events/<event-slug>/`
- Create Event: `/events/create/`
- Edit Event: `/events/<event-slug>/edit/`

### Accounts
- Register: `/accounts/register/`
- Login: `/accounts/login/`
- Logout: `/accounts/logout/`
- Profile: `/accounts/profile/`
- Edit Profile: `/accounts/profile/edit/`

### Tickets
- My Tickets: `/tickets/`
- Ticket Detail: `/tickets/<ticket-id>/`

### Dashboard
- Student Dashboard: `/dashboard/`
- Organizer Dashboard: `/dashboard/` (redirects automatically)

### RSVP
- RSVP Event: `/rsvp/event/<slug>/`
- Cancel RSVP: `/rsvp/cancel/<rsvp-id>/`

### Attendance
- Scan QR: `/attendance/scan/<event-slug>/`
- Attendance List: `/attendance/<event-slug>/`

### Notifications
- View Notifications: `/notifications/`

---

## ❌ API URLs (Return JSON - For Backend/Mobile Apps)
These are for API calls ONLY:

- `/api/events/` - GET list or create
- `/api/events/<slug>/` - GET event details
- `/api/tickets/` - GET user tickets
- `/api/user/profile/` - GET/PATCH user profile
- `/api/notifications/` - GET notifications
- etc.

---

## 🔧 What Was Wrong?

You were accessing paths like:
```
/api/events/iftar-party-2026-ramadan-80f861be/
```

These URLs are for API consumption (returning JSON).

**Replace with:**
```
/events/iftar-party-2026-ramadan-80f861be/
```

This will show the HTML frontend page instead.

---

## 📍 Full URL Examples

### ❌ Wrong (API - JSON)
- `/api/events/`
- `/api/tickets/`
- `/api/user/profile/`

### ✅ Correct (Frontend - HTML)
- `/events/`
- `/tickets/`
- `/accounts/profile/`

