# API Quick Reference Guide

## 📍 All Available Endpoints

### Authentication (2 endpoints)
- `POST /auth/login/` - Get JWT token
- `POST /auth/refresh/` - Refresh JWT token

### Events Management (6 endpoints)
- `GET /events/` - List all events
- `GET /events/<slug>/` - Get event details
- `POST /events/create/` ⭐ NEW
- `PATCH /events/<slug>/update/` ⭐ NEW
- `DELETE /events/<slug>/delete/` ⭐ NEW
- `GET /events/<slug>/analytics/` ⭐ NEW

### Attendees Management (2 endpoints) ⭐ NEW
- `GET /events/<slug>/attendees/` - List attendees
- `GET /events/<slug>/attendees/stats/` - Attendees statistics

### Attendance (Check-In/Check-Out) (4 endpoints) ⭐ NEW
- `POST /attendance/check-in/` - Check-in attendee
- `POST /attendance/check-out/` - Check-out attendee
- `GET /events/<slug>/attendance/` - Event attendance records
- `GET /attendance/my-attendance/` - My attendance history

### RSVP Management (5 endpoints)
- `POST /events/<slug>/register/` - Register for event (existing)
- `GET /rsvp/` - My RSVPs ⭐ NEW
- `GET /rsvp/<rsvp_id>/` - RSVP details ⭐ NEW
- `DELETE /rsvp/<rsvp_id>/cancel/` - Cancel RSVP ⭐ NEW
- `PATCH /rsvp/<rsvp_id>/update/` - Update RSVP ⭐ NEW

### Tickets (2 endpoints)
- `GET /tickets/` - My tickets
- `GET /tickets/<ticket_id>/` - Ticket details

### User Profile (4 endpoints) ⭐ NEW
- `GET /user/profile/` - My profile
- `PATCH /user/profile/update/` - Update profile
- `GET /user/<user_id>/profile/` - Other user's profile
- `GET /organizers/` - List all organizers

### Notifications (4 endpoints) ⭐ NEW
- `GET /notifications/` - Get notifications
- `PATCH /notifications/<notification_id>/read/` - Mark as read
- `DELETE /notifications/<notification_id>/delete/` - Delete notification
- `GET /notifications/unread-count/` - Unread count

### Event Gallery (3 endpoints) ⭐ NEW
- `GET /events/<slug>/gallery/` - Get gallery images
- `POST /events/<slug>/gallery/upload/` - Upload image
- `DELETE /events/<slug>/gallery/<image_id>/delete/` - Delete image

---

## 🎯 Total Endpoints: 43 (26 ⭐ NEW)

---

## 📊 Endpoint Summary by Feature

| Feature | Endpoints | Status |
|---------|-----------|--------|
| Authentication | 2 | ✅ Existing |
| Events | 6 | ✅ Enhanced |
| Attendees | 2 | ⭐ NEW |
| Attendance (Check-In) | 4 | ⭐ NEW |
| RSVP | 5 | ✅ Enhanced |
| Tickets | 2 | ✅ Existing |
| User Profiles | 4 | ⭐ NEW |
| Notifications | 4 | ⭐ NEW |
| Event Gallery | 3 | ⭐ NEW |
| **TOTAL** | **32** | **26 New** |

---

## 🔐 Authentication Required
**All endpoints EXCEPT:**
- `GET /events/` - List events (public)
- `GET /events/<slug>/` - Event details (public)
- `GET /user/<user_id>/profile/` - User profile (public)
- `GET /organizers/` - Organizers list (public)
- `GET /events/<slug>/gallery/` - Gallery (public)
- `POST /auth/login/` - Login (no auth needed)
- `POST /auth/refresh/` - Refresh token (no auth needed)

---

## 👤 Permission Levels

### Public Access (No Login)
- Browse events
- View event details & gallery
- View organizer list
- View user profiles

### User/Student (Authenticated)
- Browse events
- Register for events
- View my tickets
- Check-in to events
- Manage my profile
- View notifications

### Organizer (Event Owner)
- Create events
- Edit own events
- Delete own events
- View attendees list
- View attendance records
- Check-in attendees
- Upload gallery images
- View event analytics

### Admin (Superuser)
- All organizer permissions
- Access any event
- Manage any resource

---

## 🚀 Most Important New Endpoints

### For Students:
```
🎫 Register & Get Tickets
POST /events/<slug>/register/
GET /tickets/

✅ Check-In/Check-Out
POST /attendance/check-in/
POST /attendance/check-out/

📋 View My Events
GET /rsvp/
GET /notifications/

👤 Profile Management
GET /user/profile/
PATCH /user/profile/update/
```

### For Organizers:
```
📅 Event Management
POST /events/create/
PATCH /events/<slug>/update/
DELETE /events/<slug>/delete/

👥 Attendee Management
GET /events/<slug>/attendees/
GET /events/<slug>/attendees/stats/

✅ Attendance & Analytics
POST /attendance/check-in/
GET /events/<slug>/attendance/
GET /events/<slug>/analytics/

🖼️ Media Management
POST /events/<slug>/gallery/upload/
GET /events/<slug>/gallery/
DELETE /events/<slug>/gallery/<id>/delete/
```

---

## 💡 Data Models Covered

✅ **User** - Profile management
✅ **Event** - Full CRUD with analytics
✅ **RSVP** - Registration management
✅ **Ticket** - Ticket viewing
✅ **Attendance** - Check-in/check-out tracking
✅ **Notification** - Notification management
✅ **EventGallery** - Gallery image management

---

## 🔗 Key Features Overview

### 1. **Event Discovery**
- Browse upcoming events by category
- View complete event details
- See attendee information

### 2. **Event Registration**
- Register for events
- Get instant tickets (if confirmed)
- Join waitlist (if full)
- Cancel RSVP

### 3. **Attendance Tracking**
- Check-in via ticket or user ID
- Check-out tracking
- Real-time attendance statistics
- Attendance percentage calculation

### 4. **User Management**
- Complete profile management
- View other users
- Browse organizers

### 5. **Notifications**
- Real-time notifications
- Mark as read
- Delete notifications
- Unread count tracking

### 6. **Event Analytics**
- Confirmed count
- Waitlist tracking
- Attendance percentage
- Available seats

### 7. **Event Gallery**
- Photo gallery for events
- Organizer can upload photos
- Public can view photos

---

## 📝 Request/Response Examples

### ✅ Check-In Attendee Example
```bash
curl -X POST http://localhost:8000/api/attendance/check-in/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"550e8400-e29b-41d4-a716-446655440000"}'

# Response:
{
  "message": "User checked in successfully",
  "data": {
    "id": 1,
    "user": {...},
    "event": {...},
    "status": "checked_in",
    "checked_in_at": "2026-03-20T10:30:00Z"
  }
}
```

### 👥 Get Attendees Example
```bash
curl -X GET "http://localhost:8000/api/events/tech-summit-2026/attendees/?status=confirmed" \
  -H "Authorization: Bearer TOKEN"

# Response:
[
  {
    "id": 5,
    "full_name": "John Student",
    "email": "john@student.com",
    "phone_number": "+91-9876543210",
    "registration_number": "2024001",
    "department": "IT",
    "rsvp_status": "confirmed",
    "attendance_status": "checked_in"
  }
]
```

### 📊 Analytics Example
```bash
curl -X GET http://localhost:8000/api/events/tech-summit-2026/analytics/ \
  -H "Authorization: Bearer TOKEN"

# Response:
{
  "event_title": "Tech Summit 2026",
  "total_capacity": 100,
  "confirmed_registrations": 45,
  "checked_in": 35,
  "attendance_percentage": 77.8,
  "remaining_seats": 55
}
```

---

## ⚡ Quick Integration Guide

### Step 1: Install Package
```bash
pip install -r requirements.txt
```

### Step 2: Makemigrations & Migrate
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Start Server
```bash
python manage.py runserver
```

### Step 4: Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### Step 5: Use Token in Requests
```bash
curl -X GET http://localhost:8000/api/tickets/ \
  -H "Authorization: Bearer <token>"
```

---

## 📚 Full Documentation
See `API_ENDPOINTS.md` for complete endpoint documentation with all parameters and examples.
