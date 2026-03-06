# Ticket Generation System - Visual Flow & Architecture

## 🔄 Ticket Generation Flow

```
User RSVPs for Event
        ↓
RSVP Created & Confirmed
        ↓
views.py: generate_ticket() called
        ↓
Ticket Model: New ticket created
        ↓
★ Signal: post_save triggered
        ↓
signals.py: ensure_ticket_files()
        ↓
        ├─→ generate_qr_code(ticket)
        │   ├─ Generate QR image (PIL)
        │   ├─ Convert to PNG bytes
        │   ├─ Save to storage (Cloudinary/Local)
        │   └─ Update ticket.qr_code field
        │
        └─→ generate_pdf_ticket(ticket)
            ├─ Create ReportLab PDF container
            ├─ Read QR from storage (BytesIO)
            ├─ Embed QR in PDF
            ├─ Save PDF to storage
            └─ Update ticket.pdf_ticket field
        ↓
Ticket Complete ✓
        ↓
User can view & download
```

## 🏗️ Architecture

```
tickets/
├── models.py
│   └── Ticket
│       ├── qr_code: ImageField
│       └── pdf_ticket: FileField
│
├── utils.py (GENERATION LOGIC)
│   ├── generate_qr_code(ticket)
│   ├── generate_pdf_ticket(ticket)
│   └── generate_ticket(user, event)
│
├── signals.py (AUTO-GENERATION)
│   └── ensure_ticket_files(signal)
│
├── views.py (DISPLAY & DOWNLOAD)
│   ├── my_tickets()
│   ├── ticket_detail()
│   └── download_ticket()
│
├── admin.py (DEBUG & MANUAL OPERATIONS)
│   ├── Status indicators
│   ├── QR preview
│   └── Bulk regeneration
│
└── management/commands/
    └── regenerate_tickets.py (CLI TOOL)
```

## 📊 Data Flow

```
CREATION PATH:
┌─────────────────────────────────────┐
│      User RSVP Registration         │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  rsvp/views.py                      │
│  generate_ticket(user, event)       │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  tickets/models.py                  │
│  Ticket.objects.create()            │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Django Signal: post_save           │
│  (automatic trigger)                │
└────────────┬────────────────────────┘
             │
             ├─────────────────────────────┐
             ↓                             ↓
┌────────────────────────┐   ┌───────────────────────┐
│  QR CODE GENERATION    │   │  PDF GENERATION       │
├────────────────────────┤   ├───────────────────────┤
│ 1. Create QR data      │   │ 1. Create PDF canvas  │
│ 2. Generate image      │   │ 2. Add event details  │
│ 3. Convert to PNG      │   │ 3. Read QR from file  │
│ 4. Upload to storage   │   │ 4. Embed QR in PDF    │
│ 5. Save path to DB     │   │ 5. Upload to storage  │
│ ↓ .qr_code field       │   │ 6. Save path to DB    │
│                        │   │ ↓ .pdf_ticket field   │
└────────────────────────┘   └───────────────────────┘
             │                             │
             └─────────────┬───────────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  Ticket Complete ✓   │
                │ Ready to display     │
                └──────────────────────┘

ACCESS PATH:
User Views Ticket
        ↓
ticket_detail.html: displays ticket.qr_code.url
        ↓
QR CODE VISIBLE ✓

User Downloads PDF
        ↓
download_ticket view
        ↓
Reads ticket.pdf_ticket from storage
        ↓
Returns HTTP response with PDF
        ↓
PDF DOWNLOADED ✓
```

## 🔌 Integration Points

```
PostgreSQL (database)
        ↓
        ├─→ stores Ticket model
        ├─→ stores file paths/references
        └─→ tracks statuses
        
Cloudinary (media storage)
        ↓
        ├─→ stores QR code images
        ├─→ stores PDF files
        └─→ provides public URLs
        
Django ORM
        ↓
        ├─→ creates Ticket records
        ├─→ triggers post_save signals
        └─→ updates file field references
        
Storage API (django.core.files.storage)
        ↓
        ├─→ abstract storage layer
        ├─→ handles Cloudinary or local filesystem
        └─→ returns consistent file paths
```

## 🔧 Component Responsibilities

### tickets/utils.py
- **Input**: Ticket instance
- **Process**: Generate QR code and PDF
- **Output**: File paths stored in ticket
- **Storage**: Saves to Cloudinary/Local via storage API
- **Errors**: Logged with full traceback

### tickets/signals.py  
- **Trigger**: post_save signal on Ticket creation
- **Purpose**: Auto-generate missing files
- **Safety**: Ensures no ticket lacks files
- **Monitoring**: Logs all operations

### tickets/views.py
- **Function 1**: Display tickets (`my_tickets`, `ticket_detail`)
- **Function 2**: Download PDFs (`download_ticket`)
- **Fallback**: Generate PDF on-the-fly if missing
- **Error Handling**: Graceful fallback with user messaging

### tickets/admin.py
- **Display**: Status indicators for QR & PDF
- **Preview**: Shows QR code image
- **Action**: Bulk regeneration button
- **Debug**: File status information panel

### Management Command
- **CLI Tool**: `regenerate_tickets`
- **Filters**: User, event, specific ticket
- **Force**: Option to regenerate all
- **Status**: Progress reporting and summary

## 📈 Storage Backend Selection

```
At Django Startup (lpu_bsc/settings.py):

if os.environ.get("CLOUDINARY_CLOUD_NAME"):
    ↓
    Use Cloudinary Storage
    ├─ Upload to Cloudinary
    ├─ Get public URLs
    └─ Serve from CDN
else
    ↓
    Use Local FileSystem Storage
    ├─ Save to media/
    ├─ Serve locally
    └─ Good for development
```

## 🎯 Quality Assurance Checks

```
✓ QR Code Generation
  ├─ PIL creates image (100px × 100px)
  ├─ Converts to PNG format
  ├─ Uploads to storage
  └─ Field updated with path

✓ PDF Generation
  ├─ ReportLab creates document
  ├─ Reads QR from storage (BytesIO)
  ├─ Embeds QR at correct size
  ├─ Uploads to storage
  └─ Field updated with path

✓ Storage Access
  ├─ File can be written
  ├─ File can be read back
  ├─ File returns correct bytes
  └─ URLs are valid and accessible

✓ Database
  ├─ Paths stored correctly
  ├─ Fields can be queried
  ├─ Relationships intact
  └─ Signal handlers fire
```

## 🧪 Testing Pyramid

```
                    ▲
                   / \
                 /User Tests\
               /  (Manual)   \
             /________________\
                     / \
                    /   \
               Integration Tests
              (Admin Operations)
          /________________________\
               / \
              /   \
         Unit Tests
     (Function Logic)
    /________________\
```

### Test Levels:

1. **Unit Tests** (utils functions)
   - QR generation
   - PDF generation
   - Storage operations

2. **Integration Tests** (Signal + Model)
   - Ticket creation triggers generation
   - Files saved to correct locations
   - Fields updated properly

3. **End-to-End Tests** (Views + Display)
   - QR displays on page
   - PDF downloads successfully
   - Admin shows statuses

## 🚦 Status Indicators

```
Admin List View:
┌────────────┬──────────────┐
│ Ticket     │ QR  │ PDF    │
├────────────┼─────┼────────┤
│ #abc1      │ ✓  │ ✓      │  Green = Generated
│ #abc2      │ ✗  │ ✗      │  Red = Missing
│ #abc3      │ ✓  │ ✗      │  Mixed = Partial
└────────────┴─────┴────────┘
```

## 📊 Performance Metrics

```
Operation          Typical Time    With Cloudinary
─────────────────────────────────────────────────
QR Generation      50-100ms        +500-2000ms upload
PDF Generation     200-500ms       +500-2000ms upload
Total (both)       ~300-600ms      ~1-4s total

Batch Operation (100 tickets):
30-60 seconds (local) or 2-4 minutes (Cloudinary)
```

## 🔐 Security Considerations

```
✓ File Permissions
  └─ Tickets only accessible to ticket owner

✓ Storage Security  
  └─ Cloudinary API keys in env variables

✓ Database Access
  └─ PostgreSQL with credentials

✓ URL Generation
  └─ Signed URLs if using Cloudinary

✓ Error Messages
  └─ No sensitive data exposed to users
```

---

## Summary

The system is designed with:
- **Automatic generation** (no manual intervention)
- **Multiple regeneration methods** (CLI, Admin, Views)
- **Comprehensive logging** (all operations tracked)
- **Error resilience** (graceful fallbacks)
- **Storage agnostic** (Cloudinary or local)
- **Database agnostic** (PostgreSQL or SQLite)
