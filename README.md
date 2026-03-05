# 🇧🇩 LPU Bangladesh Students Community — Event Management Platform

A full-featured Django web application for managing events, RSVPs, and QR-based check-ins for the Bangladesh Students Community at Lovely Professional University.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Registration, login, role-based access (Admin / Organizer / Student) |
| 📅 Event Management | Create, edit, delete events with banner, category, venue, capacity |
| ✅ RSVP System | Register for events with waitlist support and duplicate prevention |
| 🎫 Ticket Generation | Digital tickets with unique UUID + QR code auto-generated on RSVP |
| 📄 PDF Tickets | Download ticket as PDF (via ReportLab) |
| 📷 QR Check-in | Camera-based QR scanner for organizers to check in attendees |
| 📊 Dashboard | Stats, event management, attendance analytics for organizers |
| 🔔 Notifications | In-app + email notifications for RSVP, ticket, event updates |
| 🖼️ Event Gallery | Upload photos after events; public gallery on event page |
| 🔍 Search & Filter | Search by title, filter by category/status, sort by date/popularity |
| 📱 Responsive | Mobile-first Bootstrap 5 design, optimized for smartphones |

---

## 🛠️ Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (dev) / PostgreSQL (production)  
- **Frontend**: HTML5 + Bootstrap 5 + custom CSS
- **QR Code**: `qrcode` Python library
- **PDF**: ReportLab
- **Fonts**: Playfair Display + DM Sans (Google Fonts)
- **Icons**: Bootstrap Icons

---

## 🚀 Quick Start

### 1. Clone and set up environment

```bash
git clone <repo>
cd lpu_bsc

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment (optional for dev)

```bash
# For development, default settings use SQLite and console email
# For production, set these environment variables:
export DB_NAME=lpu_bsc_db
export DB_USER=postgres
export DB_PASSWORD=yourpassword
export EMAIL_HOST_USER=your@gmail.com
export EMAIL_HOST_PASSWORD=apppassword
```

### 3. Run migrations

```bash
python manage.py makemigrations accounts events rsvp tickets attendance notifications
python manage.py migrate
```

### 4. Create admin account

```bash
python manage.py createsuperuser
```

### 5. Load sample data (optional)

```bash
python manage.py seed_data
```
This creates:
- Organizer: `organizer@lpu.in` / `password123`
- Students: `student1@lpu.in` – `student5@lpu.in` / `password123`
- 6 sample upcoming events

### 6. Run the server

```bash
python manage.py runserver
```

Visit → **http://127.0.0.1:8000**  
Admin → **http://127.0.0.1:8000/admin**

---

## 📁 Project Structure

```
lpu_bsc/
├── lpu_bsc/              # Project settings & URLs
│   ├── settings.py
│   └── urls.py
├── accounts/             # User auth, profiles, dashboards
├── events/               # Event CRUD, gallery, search
├── rsvp/                 # RSVP registration & cancellation
├── tickets/              # Ticket generation, QR codes, PDF
├── attendance/           # QR scanning, check-in, attendance logs
├── notifications/        # In-app + email notifications
├── templates/            # All HTML templates
│   ├── base.html
│   ├── events/
│   ├── accounts/
│   ├── tickets/
│   ├── attendance/
│   ├── rsvp/
│   └── notifications/
├── static/               # CSS, JS, images
├── media/                # Uploaded files
├── requirements.txt
├── manage.py
└── setup.sh
```

---

## 👥 User Roles

| Role | Permissions |
|---|---|
| **Student** | Browse events, RSVP, view/download tickets, profile |
| **Organizer** | All student permissions + create/edit events, manage attendees, QR check-in |
| **Admin** | Full access to all events and users |

To promote a user to Organizer or Admin:
1. Go to `/admin/`
2. Find the user under Accounts → Users
3. Change their `role` field

---

## 🎫 Ticket & QR Code Flow

1. Student RSVPs → Ticket automatically generated
2. Ticket includes unique UUID and QR code image
3. Student views ticket at `/tickets/<uuid>/`
4. Student downloads PDF ticket
5. At event: Organizer opens `/attendance/scan/<event-slug>/`
6. Camera scans QR → API validates → Attendee marked checked-in
7. Duplicate scan detection prevents double check-ins

---

## 📧 Email Configuration

For Gmail:
1. Enable 2FA on your Gmail account
2. Create an App Password at myaccount.google.com/apppasswords
3. Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` env variables

For development, switch to console backend in settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## ☁️ Deployment (Render)

1. Create a PostgreSQL database on Render
2. Create a new Web Service pointing to this repo
3. Build command: `pip install -r requirements.txt && python manage.py migrate`
4. Start command: `gunicorn lpu_bsc.wsgi`
5. Set environment variables in Render dashboard

---

## 🔮 Future Features

- [ ] Online payment gateway (Stripe/Razorpay)
- [ ] Event feedback & ratings
- [ ] Participation certificates (PDF)
- [ ] Push notifications
- [ ] REST API for mobile app
- [ ] Multi-community support

---

**Built with ❤️ for the Bangladesh Students Community at LPU**
