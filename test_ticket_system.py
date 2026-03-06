"""
Test script to verify ticket QR and PDF generation.
Run this from Django shell: python manage.py shell < test_ticket_system.py
"""

import os
from django.conf import settings
from django.core.files.storage import default_storage
from tickets.models import Ticket
from tickets.utils import generate_qr_code, generate_pdf_ticket

print("\n" + "="*60)
print("TICKET SYSTEM DIAGNOSTIC TEST")
print("="*60)

# Check 1: Storage Configuration
print("\n[1] Checking Storage Configuration...")
if os.environ.get("CLOUDINARY_CLOUD_NAME"):
    print("✓ Using Cloudinary storage")
    print(f"  Cloud: {os.environ.get('CLOUDINARY_CLOUD_NAME')}")
else:
    print("✓ Using Local filesystem storage")
    print(f"  Media Root: {settings.MEDIA_ROOT}")

# Check 2: Database Configuration
print("\n[2] Checking Database Configuration...")
db_engine = settings.DATABASES['default']['ENGINE']
if 'postgresql' in db_engine:
    print(f"✓ PostgreSQL configured")
    print(f"  Host: {settings.DATABASES['default'].get('HOST', 'localhost')}")
    print(f"  Database: {settings.DATABASES['default'].get('NAME', '')}")
elif 'sqlite' in db_engine:
    print(f"⚠ SQLite detected (use PostgreSQL in production)")
else:
    print(f"? Database: {db_engine}")

# Check 3: Check Existing Tickets
print("\n[3] Checking Existing Tickets...")
total_tickets = Ticket.objects.count()
print(f"Total tickets: {total_tickets}")

if total_tickets > 0:
    # Sample ticket
    sample = Ticket.objects.first()
    print(f"\nSample Ticket: {sample.ticket_number}")
    print(f"  User: {sample.user.full_name}")
    print(f"  Event: {sample.event.title}")
    print(f"  Status: {sample.get_status_display()}")
    print(f"  QR Code: {'✓' if sample.qr_code else '✗ MISSING'}")
    print(f"  PDF: {'✓' if sample.pdf_ticket else '✗ MISSING'}")
    
    # Check for missing files
    missing_qr = Ticket.objects.filter(qr_code='').count()
    missing_pdf = Ticket.objects.filter(pdf_ticket='').count()
    
    if missing_qr > 0:
        print(f"\n⚠ {missing_qr} ticket(s) missing QR codes")
    if missing_pdf > 0:
        print(f"⚠ {missing_pdf} ticket(s) missing PDF files")
    
    if missing_qr == 0 and missing_pdf == 0:
        print("\n✓ All tickets have QR codes and PDFs")
else:
    print("No tickets found. Create some RSVP registrations first.")

# Check 4: Test File Storage Access
print("\n[4] Testing File Storage Access...")
try:
    # Try to save a test file
    test_content = b"test content"
    test_path = "test/test.txt"
    saved_path = default_storage.save(test_path, test_content)
    print(f"✓ Storage write OK: {saved_path}")
    
    # Try to read it back
    with default_storage.open(saved_path, 'rb') as f:
        content = f.read()
    print(f"✓ Storage read OK ({len(content)} bytes)")
    
    # Clean up
    default_storage.delete(saved_path)
    print(f"✓ Storage delete OK")
except Exception as e:
    print(f"✗ Storage error: {str(e)}")

# Check 5: Test QR Generation
print("\n[5] Testing QR Code Generation...")
if total_tickets > 0:
    sample = Ticket.objects.first()
    try:
        # Regenerate QR
        qr_path = generate_qr_code(sample)
        if qr_path:
            print(f"✓ QR generated successfully")
            print(f"  Path: {qr_path}")
            
            # Try to access it
            try:
                with default_storage.open(str(sample.qr_code), 'rb') as f:
                    qr_data = f.read()
                print(f"✓ QR accessible ({len(qr_data)} bytes)")
            except Exception as e:
                print(f"✗ QR read error: {str(e)}")
        else:
            print("✗ QR generation returned None")
    except Exception as e:
        print(f"✗ QR generation error: {str(e)}")
else:
    print("⚠ No tickets to test")

# Check 6: Test PDF Generation
print("\n[6] Testing PDF Generation...")
if total_tickets > 0:
    sample = Ticket.objects.first()
    try:
        # Regenerate PDF
        pdf_path = generate_pdf_ticket(sample)
        if pdf_path:
            print(f"✓ PDF generated successfully")
            print(f"  Path: {pdf_path}")
            
            # Try to access it
            try:
                with default_storage.open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                print(f"✓ PDF accessible ({len(pdf_data)} bytes)")
                
                # Check if it's a valid PDF (starts with %PDF)
                if pdf_data.startswith(b'%PDF'):
                    print(f"✓ PDF format valid")
                else:
                    print(f"⚠ PDF format might be invalid")
            except Exception as e:
                print(f"✗ PDF read error: {str(e)}")
        else:
            print("✗ PDF generation returned None")
    except Exception as e:
        print(f"✗ PDF generation error: {str(e)}")
else:
    print("⚠ No tickets to test")

print("\n" + "="*60)
print("DIAGNOSTIC TEST COMPLETE")
print("="*60)
print("\nNext Steps:")
print("1. If QR or PDF are missing, run:")
print("   python manage.py regenerate_tickets")
print("2. Check Django admin at /admin/tickets/ticket/")
print("3. Review TICKET_SETUP.md for detailed troubleshooting")
print("\n")
