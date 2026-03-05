import qrcode
import os
import io
from django.conf import settings
from django.utils import timezone


def generate_qr_code(ticket):
    """Generate QR code for a ticket and save it."""
    qr_data = f"LPUBSC-TICKET:{ticket.ticket_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'tickets', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    filename = f"ticket_{ticket.ticket_id}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)
    return f"tickets/qr_codes/{filename}"


def generate_pdf_ticket(ticket):
    """Generate a PDF ticket using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'tickets', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        filename = f"ticket_{ticket.ticket_id}.pdf"
        filepath = os.path.join(pdf_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#1a472a'), alignment=TA_CENTER)
        story.append(Paragraph("LPU Bangladesh Students Community", title_style))
        story.append(Paragraph("EVENT TICKET", title_style))
        story.append(Spacer(1, 0.5*cm))

        # Event details
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=12)
        story.append(Paragraph(f"<b>Event:</b> {ticket.event.title}", body_style))
        story.append(Paragraph(f"<b>Name:</b> {ticket.user.full_name}", body_style))
        story.append(Paragraph(f"<b>Ticket ID:</b> {ticket.ticket_id}", body_style))
        story.append(Paragraph(f"<b>Date:</b> {ticket.event.event_date.strftime('%B %d, %Y at %I:%M %p')}", body_style))
        story.append(Paragraph(f"<b>Venue:</b> {ticket.event.venue}", body_style))
        story.append(Paragraph(f"<b>Status:</b> {ticket.get_status_display()}", body_style))
        story.append(Spacer(1, 1*cm))

        # QR Code
        if ticket.qr_code:
            qr_path = os.path.join(settings.MEDIA_ROOT, str(ticket.qr_code))
            if os.path.exists(qr_path):
                qr_img = Image(qr_path, width=5*cm, height=5*cm)
                story.append(qr_img)

        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Present this ticket at the event entrance.", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)))

        doc.build(story)
        return f"tickets/pdfs/{filename}"
    except ImportError:
        return None


def generate_ticket(user, event, rsvp=None):
    """Generate a complete ticket with QR code and PDF."""
    from .models import Ticket

    # Check if ticket already exists
    existing = Ticket.objects.filter(user=user, event=event).first()
    if existing:
        return existing

    ticket = Ticket.objects.create(
        user=user,
        event=event,
        rsvp=rsvp,
        status='active',
    )

    # Generate QR code
    try:
        qr_path = generate_qr_code(ticket)
        ticket.qr_code = qr_path
        ticket.save()
    except Exception as e:
        print(f"QR code generation error: {e}")

    # Generate PDF
    try:
        pdf_path = generate_pdf_ticket(ticket)
        if pdf_path:
            ticket.pdf_ticket = pdf_path
            ticket.save()
    except Exception as e:
        print(f"PDF generation error: {e}")

    return ticket
