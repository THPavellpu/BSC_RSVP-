# Quick Reference - Ticket QR & PDF System

## ✅ Quick Fix Commands

### Regenerate All Missing Tickets
```bash
python manage.py regenerate_tickets
```

### Regenerate Specific User's Tickets
```bash
python manage.py regenerate_tickets --user=john@example.com
```

### Force Regenerate ALL Tickets
```bash
python manage.py regenerate_tickets --force
```

### Run Diagnostic Test
```bash
python manage.py shell < test_ticket_system.py
```

## 🔍 Debugging in Django Shell

```bash
python manage.py shell
```

### Check Ticket Status
```python
from tickets.models import Ticket

# Get a ticket
ticket = Ticket.objects.first()

# Check files
print(f"QR Code: {ticket.qr_code}")      # Should show file path
print(f"PDF: {ticket.pdf_ticket}")        # Should show file path

# Check if QR/PDF exist
from django.core.files.storage import default_storage
if ticket.qr_code and default_storage.exists(str(ticket.qr_code)):
    print("✓ QR file exists in storage")
else:
    print("✗ QR file missing")
```

### Manually Generate QR for One Ticket
```python
from tickets.models import Ticket
from tickets.utils import generate_qr_code

ticket = Ticket.objects.first()
generate_qr_code(ticket)
print(f"Generated: {ticket.qr_code}")
```

### Manually Generate PDF for One Ticket
```python
from tickets.models import Ticket
from tickets.utils import generate_pdf_ticket

ticket = Ticket.objects.first()
pdf_path = generate_pdf_ticket(ticket)
ticket.pdf_ticket = pdf_path
ticket.save()
print(f"Generated: {pdf_path}")
```

## 📊 Environment Variables Checklist

### For Cloudinary (Production)
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### For PostgreSQL (Production)
```bash
DB_NAME=lpu_bsc_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost_or_server
DB_PORT=5432
```

### Verify Environment Variables
```bash
# Windows PowerShell
Get-Item Env:CLOUDINARY_CLOUD_NAME
Get-Item Env:DB_NAME

# Linux/Mac
env | grep CLOUDINARY
env | grep DB_
```

## 🛠️ Admin Interface Quick Actions

1. **View Tickets**: `/admin/tickets/ticket/`

2. **Check QR/PDF Status**:
   - Green ✓ = Generated
   - Red ✗ = Missing

3. **Preview QR Code**: Click on ticket → see QR image preview

4. **Bulk Regenerate**:
   - Select tickets
   - Choose action: "🔄 Regenerate QR codes and PDFs"
   - Click "Go"

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| QR not showing | `regenerate_tickets` or check admin |
| PDF download fails | Check if `pdf_ticket` field is empty in admin |
| Cloudinary 404 | Verify env variables are set correctly |
| "Database connection error" | Check PostgreSQL is running and credentials |
| "ReportLab not found" | `pip install reportlab` |

## 📝 Important Files

| File | Purpose |
|------|---------|
| `tickets/utils.py` | QR & PDF generation logic |
| `tickets/signals.py` | Auto-generation when ticket created |
| `tickets/views.py` | Display & download endpoints |
| `tickets/admin.py` | Admin interface with debug info |
| `TICKET_SETUP.md` | Detailed setup guide |
| `test_ticket_system.py` | Diagnostic test script |

## 🚀 Deployment Checklist

- [ ] PostgreSQL configured in settings
- [ ] PostgreSQL running and accessible
- [ ] Cloudinary env variables set
- [ ] `python manage.py migrate` run
- [ ] ReportLab installed: `pip list | grep reportlab`
- [ ] Test regeneration: `python manage.py regenerate_tickets`
- [ ] Check admin: `/admin/tickets/ticket/` shows QR & PDF status
- [ ] Try creating new RSVP and check ticket generation

## 📞 Support Info

**For logs**, check:
- Django console/stdout for immediate output
- Settings for `LOGGING` configuration
- `/admin/tickets/ticket/` for file status details

**For detailed tracking**, add logging to settings.py:
```python
LOGGING = {
    'loggers': {
        'tickets': {
            'level': 'DEBUG',
        }
    }
}
```
