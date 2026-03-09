# Complete API Endpoints Documentation

## Base URL
```
http://localhost:8000/api
```

---

## 🔐 Authentication Endpoints

### 1. Login (Get JWT Token)
**POST** `/auth/login/`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "access": "eyj...",
  "refresh": "eyj..."
}
```

### 2. Refresh Token
**POST** `/auth/refresh/`
```json
{
  "refresh": "eyj..."
}
```

---

## 🎉 Events Endpoints

### 1. List All Events
**GET** `/events/`
- Query Parameters: `category=cultural|sports|seminar|workshop|etc`
- Authorization: Not required

**Response:**
```json
[
  {
    "id": 1,
    "title": "Tech Summit 2026",
    "slug": "tech-summit-2026-ab12cd34",
    "description": "...",
    "event_date": "2026-03-20T10:00:00Z",
    "venue": "Main Auditorium",
    "remaining_seats": 50,
    "organizer": {
      "id": 1,
      "full_name": "John Organizer",
      "email": "john@example.com",
      "is_organizer": true
    }
  }
]
```

### 2. Get Event Details
**GET** `/events/<slug>/`
- Authorization: Not required

**Response:**
```json
{
  "id": 1,
  "title": "Tech Summit 2026",
  "slug": "tech-summit-2026-ab12cd34",
  "description": "...",
  "category": "seminar",
  "event_date": "2026-03-20T10:00:00Z",
  "end_date": "2026-03-20T17:00:00Z",
  "venue": "Main Auditorium",
  "venue_details": "Building A, Room 101",
  "max_attendees": 100,
  "rsvp_deadline": "2026-03-18T00:00:00Z",
  "ticket_price": "0.00",
  "is_free": true,
  "status": "upcoming",
  "confirmed_count": 45,
  "waitlist_count": 10,
  "attendance_percentage": 30.5,
  "remaining_seats": 55,
  "organizer": {...}
}
```

### 3. Create Event
**POST** `/events/create/`
- Authorization: Required (organizer only)

```json
{
  "title": "New Workshop",
  "description": "Workshop description",
  "category": "workshop",
  "event_date": "2026-04-01T10:00:00Z",
  "end_date": "2026-04-01T16:00:00Z",
  "venue": "Lab Building",
  "venue_details": "Room 205",
  "max_attendees": 50,
  "rsvp_deadline": "2026-03-30T00:00:00Z",
  "ticket_price": "0.00",
  "is_free": true,
  "status": "upcoming",
  "is_featured": false,
  "tags": "workshop,python,coding"
}
```

### 4. Update Event
**PATCH** `/events/<slug>/update/`
- Authorization: Required (event organizer only)
- Same fields as create endpoint

### 5. Delete Event
**DELETE** `/events/<slug>/delete/`
- Authorization: Required (event organizer only)

### 6. Get Event Analytics
**GET** `/events/<slug>/analytics/`
- Authorization: Required (event organizer only)

**Response:**
```json
{
  "event_title": "Tech Summit 2026",
  "total_capacity": 100,
  "confirmed_registrations": 45,
  "waitlisted": 10,
  "total_registrations": 55,
  "checked_in": 35,
  "attendance_percentage": 70.0,
  "remaining_seats": 55,
  "event_status": "ongoing"
}
```

---

## 👥 Attendees Endpoints

### 1. Get Event Attendees List
**GET** `/events/<slug>/attendees/`
- Query Parameters: `status=confirmed|waitlisted|all`
- Authorization: Required (event organizer only)

**Response:**
```json
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
  },
  {
    "id": 6,
    "full_name": "Jane Student",
    "email": "jane@student.com",
    "phone_number": "+91-9876543211",
    "registration_number": "2024002",
    "department": "CSE",
    "rsvp_status": "waitlisted",
    "attendance_status": null
  }
]
```

### 2. Get Attendees Statistics
**GET** `/events/<slug>/attendees/stats/`
- Authorization: Required (event organizer only)

**Response:**
```json
{
  "event_title": "Tech Summit 2026",
  "total_capacity": 100,
  "confirmed_count": 45,
  "waitlisted_count": 10,
  "total_registered": 55,
  "checked_in_count": 35,
  "not_checked_in": 10,
  "attendance_rate": "77.8%",
  "available_seats": 55,
  "is_full": false
}
```

---

## ✅ Attendance (Check-In/Check-Out) Endpoints

### 1. Check-In Attendee
**POST** `/attendance/check-in/`
- Authorization: Required (event organizer only)

**Option 1: Using Ticket ID**
```json
{
  "ticket_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Option 2: Using Event Slug + User ID**
```json
{
  "event_slug": "tech-summit-2026-ab12cd34",
  "user_id": 5
}
```

**Response:**
```json
{
  "message": "User checked in successfully",
  "data": {
    "id": 1,
    "user": {...},
    "event": {...},
    "status": "checked_in",
    "checked_in_at": "2026-03-20T10:30:00Z",
    "checked_out_at": null,
    "checked_in_by_user": {...}
  }
}
```

### 2. Check-Out Attendee
**POST** `/attendance/check-out/`
- Authorization: Required (event organizer only)

**Same request format as check-in**

### 3. Get Event Attendance Records
**GET** `/events/<slug>/attendance/`
- Query Parameters: `status=checked_in|checked_out|all`
- Authorization: Required (event organizer only)

**Response:**
```json
[
  {
    "id": 1,
    "user": {...},
    "event": {...},
    "ticket": {...},
    "status": "checked_in",
    "checked_in_at": "2026-03-20T10:30:00Z",
    "checked_out_at": null,
    "checked_in_by_user": {...}
  }
]
```

### 4. Get My Attendance History
**GET** `/attendance/my-attendance/`
- Authorization: Required

**Response:** Same as above but for current user

---

## 🎫 RSVP Endpoints

### 1. Register for Event
**POST** `/events/<slug>/register/`
- Authorization: Required

```json
{
  "additional_info": "I have any dietary restrictions"
}
```

**Response:**
```json
{
  "status": "confirmed",
  "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
  "rsvp_id": 1
}
```

### 2. Get My RSVPs
**GET** `/rsvp/`
- Authorization: Required

**Response:**
```json
[
  {
    "id": 1,
    "event": {...},
    "user": {...},
    "status": "confirmed",
    "additional_info": "...",
    "created_at": "2026-03-15T10:00:00Z",
    "updated_at": "2026-03-15T10:00:00Z"
  }
]
```

### 3. Get RSVP Details
**GET** `/rsvp/<rsvp_id>/`
- Authorization: Required (only own RSVP)

### 4. Cancel RSVP
**DELETE** `/rsvp/<rsvp_id>/cancel/`
- Authorization: Required (only own RSVP)

### 5. Update RSVP
**PATCH** `/rsvp/<rsvp_id>/update/`
- Authorization: Required (only own RSVP)

```json
{
  "status": "cancelled",
  "additional_info": "Updated info"
}
```

---

## 🎟️ Tickets Endpoints

### 1. Get My Tickets
**GET** `/tickets/`
- Authorization: Required

**Response:**
```json
[
  {
    "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
    "event": {...},
    "user": {...},
    "status": "active",
    "qr_code": "http://media/tickets/qr_codes/...",
    "pdf_ticket": "http://media/tickets/pdfs/...",
    "created_at": "2026-03-15T10:00:00Z",
    "updated_at": "2026-03-15T10:00:00Z"
  }
]
```

### 2. Get Ticket Details
**GET** `/tickets/<ticket_id>/`
- Authorization: Required (only own ticket)

---

## 👤 User Profile Endpoints

### 1. Get My Profile
**GET** `/user/profile/`
- Authorization: Required

**Response:**
```json
{
  "id": 5,
  "full_name": "John Student",
  "email": "john@student.com",
  "registration_number": "2024001",
  "role": "student",
  "profile_picture": "http://media/profile_pics/...",
  "phone_number": "+91-9876543210",
  "bio": "I love attending tech events",
  "department": "IT",
  "batch_year": "2024",
  "is_organizer": false,
  "created_at": "2026-01-15T10:00:00Z"
}
```

### 2. Update My Profile
**PATCH** `/user/profile/update/`
- Authorization: Required

```json
{
  "full_name": "John Updated",
  "phone_number": "+91-9876543210",
  "bio": "Updated bio",
  "profile_picture": "file"
}
```

### 3. Get Other User's Profile
**GET** `/user/<user_id>/profile/`
- Authorization: Not required (public profile)

### 4. Get All Organizers
**GET** `/organizers/`
- Authorization: Not required

**Response:**
```json
[
  {
    "id": 1,
    "full_name": "John Organizer",
    "email": "john@example.com",
    "role": "organizer",
    "is_organizer": true
  }
]
```

---

## 🔔 Notifications Endpoints

### 1. Get Notifications
**GET** `/notifications/`
- Query Parameters: `unread=true|false`
- Authorization: Required

**Response:**
```json
[
  {
    "id": 1,
    "notification_type": "rsvp_confirmed",
    "title": "Registration Confirmed",
    "message": "You've been registered for Tech Summit 2026",
    "is_read": false,
    "link": "/events/tech-summit-2026/",
    "created_at": "2026-03-15T10:00:00Z"
  }
]
```

### 2. Mark Notification as Read
**PATCH** `/notifications/<notification_id>/read/`
- Authorization: Required

### 3. Delete Notification
**DELETE** `/notifications/<notification_id>/delete/`
- Authorization: Required

### 4. Get Unread Notifications Count
**GET** `/notifications/unread-count/`
- Authorization: Required

**Response:**
```json
{
  "unread_count": 3
}
```

---

## 🖼️ Event Gallery Endpoints

### 1. Get Event Gallery
**GET** `/events/<slug>/gallery/`
- Authorization: Not required

**Response:**
```json
[
  {
    "id": 1,
    "event": 1,
    "image": "http://media/event_gallery/...",
    "caption": "Opening ceremony",
    "uploaded_by": {...},
    "uploaded_at": "2026-03-20T15:00:00Z"
  }
]
```

### 2. Upload Gallery Image
**POST** `/events/<slug>/gallery/upload/`
- Authorization: Required (event organizer only)
- Content-Type: multipart/form-data

```json
{
  "image": "file",
  "caption": "Event opening ceremony"
}
```

### 3. Delete Gallery Image
**DELETE** `/events/<slug>/gallery/<image_id>/delete/`
- Authorization: Required (event organizer only)

---

## 📋 Quick Reference - Most Used Endpoints

### For Students/Attendees:
```
GET    /events/                          - Browse events
GET    /events/<slug>/                   - View event details
POST   /events/<slug>/register/          - Register for event
GET    /rsvp/                            - View my registrations
GET    /tickets/                         - View my tickets
POST   /attendance/check-in/             - Check-in to event
GET    /notifications/                   - View notifications
PATCH  /user/profile/update/             - Update profile
```

### For Organizers:
```
POST   /events/create/                   - Create new event
PATCH  /events/<slug>/update/            - Update event
GET    /events/<slug>/attendees/         - View attendees list
GET    /events/<slug>/attendees/stats/   - View attendance stats
POST   /attendance/check-in/             - Check-in attendees
GET    /events/<slug>/analytics/         - View event analytics
POST   /events/<slug>/gallery/upload/    - Upload gallery images
```

---

## 🔑 Headers Required

All authenticated endpoints require:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## 💡 Usage Examples

### Example 1: Complete Attendee Flow
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Response: {"access":"token123","refresh":"token456"}

# 2. Browse Events
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer token123"

# 3. View Event Details
curl -X GET http://localhost:8000/api/events/tech-summit-2026-ab12cd34/ \
  -H "Authorization: Bearer token123"

# 4. Register for Event
curl -X POST http://localhost:8000/api/events/tech-summit-2026-ab12cd34/register/ \
  -H "Authorization: Bearer token123" \
  -H "Content-Type: application/json" \
  -d '{"additional_info":"No dietary restrictions"}'

# Response: {"status":"confirmed","ticket_id":"550e...","rsvp_id":1}

# 5. Get My Tickets
curl -X GET http://localhost:8000/api/tickets/ \
  -H "Authorization: Bearer token123"

# 6. Check-In to Event
curl -X POST http://localhost:8000/api/attendance/check-in/ \
  -H "Authorization: Bearer token123" \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"550e8400-e29b-41d4-a716-446655440000"}'
```

### Example 2: Event Organizer Flow
```bash
# 1. Create Event
curl -X POST http://localhost:8000/api/events/create/ \
  -H "Authorization: Bearer token123" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Python Workshop",
    "description":"Learn Python basics",
    "category":"workshop",
    "event_date":"2026-04-01T10:00:00Z",
    "venue":"Lab A",
    "max_attendees":30,
    "rsvp_deadline":"2026-03-30T00:00:00Z"
  }'

# 2. View Attendees
curl -X GET http://localhost:8000/api/events/python-workshop-abc/attendees/ \
  -H "Authorization: Bearer token123"

# 3. Check-In Attendee
curl -X POST http://localhost:8000/api/attendance/check-in/ \
  -H "Authorization: Bearer token123" \
  -H "Content-Type: application/json" \
  -d '{"event_slug":"python-workshop-abc","user_id":5}'

# 4. View Analytics
curl -X GET http://localhost:8000/api/events/python-workshop-abc/analytics/ \
  -H "Authorization: Bearer token123"
```

---

## 🚀 Status Codes Guide

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Successful deletion
- **400 Bad Request** - Invalid data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Access denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error
