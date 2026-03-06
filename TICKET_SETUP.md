# Ticket Generation System - Setup & Troubleshooting Guide

## Overview
This system generates QR codes and PDF tickets for event attendees. It supports:
- **PostgreSQL** database (as required)
- **Cloudinary** cloud storage for media files
- **Local filesystem** storage for development

## Configuration

### 1. PostgreSQL Setup

Edit `lpu_bsc/settings.py` and use PostgreSQL instead of SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'lpu_bsc_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Set environment variables:
```bash
# .env or system environment
DB_NAME=lpu_bsc_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Cloudinary Setup

**Environment Variables Required:**
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

When these variables are set, Django will automatically use Cloudinary for file storage.

**For Development (Local Storage):**
If Cloudinary environment variables are NOT set, the system falls back to local filesystem storage in `media/` directory.

### 3. Database Migrations

Apply migrations to create Ticket model:

```bash
python manage.py migrate tickets
```

## File Structure

```
tickets/
├── migrations/           # Database migrations
├── management/
│   └── commands/
│       └── regenerate_tickets.py  # Manual regeneration command
├── models.py            # Ticket model
├── utils.py             # QR & PDF generation functions
├── views.py             # Ticket views
├── admin.py             # Django admin interface
├── signals.py           # Auto-generation on ticket creation
├── apps.py              # Signal registration
└── urls.py              # URL routes
```

## Usage

### Automatic Ticket Generation

When a user registers for an event and gets a confirmed RSVP:

1. `rsvp/views.py` calls `generate_ticket(user, event, rsvp)`
2. A new Ticket is created
3. Signal handler automatically generates:
   - QR code (PNG image)
   - PDF file with embedded QR code

### Manual Ticket Regeneration

**Command line:**
```bash
# Regenerate missing QR/PDF files
python manage.py regenerate_tickets

# Force regenerate all tickets
python manage.py regenerate_tickets --force

# For specific user
python manage.py regenerate_tickets --user=john@example.com

# For specific event
python manage.py regenerate_tickets --event=1

# For specific ticket
python manage.py regenerate_tickets --ticket-id=abc-def-ghi
```

**Django Admin:**
1. Go to `admin/tickets/ticket/`
2. Select tickets from the list
3. Choose "🔄 Regenerate QR codes and PDFs for selected tickets" from actions
4. Click "Go"

### Manual API (Python/Django Shell)

```python
from tickets.models import Ticket
from tickets.utils import generate_qr_code, generate_pdf_ticket

# Get a ticket
ticket = Ticket.objects.first()

# Generate/Regenerate QR
generate_qr_code(ticket)

# Generate/Regenerate PDF
pdf_path = generate_pdf_ticket(ticket)
ticket.pdf_ticket = pdf_path
ticket.save()
```

## Troubleshooting

### Issue: QR codes not displaying in templates

**Symptoms:**
- Template shows empty QR space
- No `qr_code` in ticket object

**Solutions:**
1. Check if QR code was generated:
   ```bash
   python manage.py shell
   >>> from tickets.models import Ticket
   >>> t = Ticket.objects.first()
   >>> print(t.qr_code)  # Should show file path, not empty
   ```

2. Regenerate missing QR codes:
   ```bash
   python manage.py regenerate_tickets
   ```

3. Check file storage configuration:
   - For Cloudinary: Ensure environment variables are set
   - For local storage: Ensure `media/tickets/qr_codes/` directory exists

### Issue: PDFs not downloading

**Symptoms:**
- Download button shows 404 error
- PDF file field is empty

**Solutions:**
1. Generate missing PDFs:
   ```bash
   python manage.py regenerate_tickets
   ```

2. Check PDF storage:
   ```bash
   python manage.py shell
   >>> from tickets.models import Ticket
   >>> t = Ticket.objects.first()
   >>> print(t.pdf_ticket)  # Should show file path
   ```

3. Verify ReportLab is installed:
   ```bash
   pip install reportlab
   ```

### Issue: Cloudinary uploads failing

**Symptoms:**
- Management command shows errors saving to Cloudinary
- Files appear to save but then 404 when accessed

**Solutions:**
1. Verify Cloudinary credentials:
   ```bash
   python manage.py shell
   >>> import cloudinary
   >>> cloudinary.config(verbose=True)  # Check configuration
   ```

2. Check environment variables:
   ```bash
   # On Windows PowerShell
   Get-Item Env:CLOUDINARY_CLOUD_NAME
   Get-Item Env:CLOUDINARY_API_KEY
   
   # Or in Python
   import os
   print(os.environ.get('CLOUDINARY_CLOUD_NAME'))
   ```

3. Test Cloudinary upload directly:
   ```bash
   python manage.py shell
   >>> from django.core.files.storage import default_storage
   >>> from django.core.files.base import ContentFile
   >>> from PIL import Image
   >>> import io
   >>> 
   >>> # Create test image
   >>> img = Image.new('RGB', (100, 100), color='red')
   >>> img_io = io.BytesIO()
   >>> img.save(img_io, format='PNG')
   >>> img_io.seek(0)
   >>> 
   >>> # Try to save
   >>> path = default_storage.save('test.png', ContentFile(img_io.getvalue()))
   >>> print(path)  # Should show saved path
   ```

### Issue: PostgreSQL connection errors

**Symptoms:**
- `django.db.utils.OperationalError: could not connect to server`

**Solutions:**
1. Verify PostgreSQL is running:
   ```bash
   # Windows
   Services > PostgreSQL Database Server
   
   # Or via command
   pg_isready -h localhost -p 5432
   ```

2. Check connection parameters:
   ```bash
   # Verify environment variables
   echo $DB_NAME
   echo $DB_USER
   echo $DB_HOST
   echo $DB_PORT
   ```

3. Test connection manually:
   ```bash
   psql -h localhost -U postgres -d lpu_bsc_db
   ```

## Admin Interface Features

### Ticket List View
- **QR Status**: Shows ✓ or ✗ with color coding
- **PDF Status**: Shows ✓ or ✗ with color coding
- **Quick Regenerate**: One-click regeneration for individual tickets

### Ticket Detail View
- **QR Preview**: Shows actual QR code image
- **File Status**: Detailed info about stored files
- **Regenerate Action**: Bulk action for multiple tickets

## Logging

All ticket operations are logged to `logs/tickets.log` (or to Django logging):

```python
import logging
logger = logging.getLogger('tickets')

# Configure in settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/tickets.log',
        },
    },
    'loggers': {
        'tickets': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Performance Considerations

- QR generation: ~50-100ms per ticket
- PDF generation: ~200-500ms per ticket
- Cloudinary upload: ~500-2000ms depending on network

For bulk operations, consider:
- Running `regenerate_tickets` during off-hours
- Using Django Celery for async generation
- Batch processing in the management command

## Testing

```python
# Test ticket generation
python manage.py shell
>>> from accounts.models import User
>>> from events.models import Event
>>> from tickets.utils import generate_ticket
>>> 
>>> user = User.objects.first()
>>> event = Event.objects.first()
>>> ticket = generate_ticket(user, event)
>>> print(f"Ticket: {ticket.ticket_id}")
>>> print(f"QR: {ticket.qr_code}")
>>> print(f"PDF: {ticket.pdf_ticket}")
```

## Notes

⚠️ **Important Reminders:**

- Always use PostgreSQL in production
- Set Cloudinary environment variables for production
- Keep ReportLab installed for PDF generation
- Verify QR codes generate before embedding in PDFs
- Check logs for detailed error messages
- Use Django admin to debug ticket generation
