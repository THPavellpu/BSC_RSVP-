import qrcode
import os
import io
import logging
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


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

    # Save QR code to in-memory fil
    filename = f"ticket_{ticket.ticket_id}.png"

    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    # Save through ImageField (important for Cloudinary)
    ticket.qr_code.save(filename, ContentFile(img_io.getvalue()), save=True)

    return ticket.qr_code.name

def generate_pdf_ticket(ticket):
    """Generate a PDF ticket using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # Generate PDF to bytes
        pdf_io = io.BytesIO()
        doc = SimpleDocTemplate(pdf_io, pagesize=A4)
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

        # QR Code - include in PDF if available
        if ticket.qr_code:
            try:
                # Try to get path for local storage
                qr_path = default_storage.path(str(ticket.qr_code))
                if os.path.exists(qr_path):
                    qr_img = Image(qr_path, width=5*cm, height=5*cm)
                    story.append(qr_img)
            except (AttributeError, NotImplementedError):
                # For cloud storage like Cloudinary, fallback to QR code text
                pass

        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Present this ticket at the event entrance.", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)))

        doc.build(story)
        pdf_io.seek(0)
        
        # Save PDF using Django storage API
        filename = f"ticket_{ticket.ticket_id}.pdf"
        filepath = f"tickets/pdfs/{filename}"
        default_storage.save(filepath, ContentFile(pdf_io.getvalue()))
        return filepath
    except ImportError:
        return None


def generate_ticket(user, event, rsvp=None):
    """Generate a complete ticket with QR code and PDF."""
    from .models import Ticket

    # Check if ticket already exists
    existing = Ticket.objects.filter(user=user, event=event).first()
    if existing:
        logger.info(f"Ticket already exists for user {user.id} and event {event.id}")
        return existing

    ticket = Ticket.objects.create(
        user=user,
        event=event,
        rsvp=rsvp,
        status='active',
    )
    logger.info(f"Created ticket {ticket.ticket_id} for user {user.id} and event {event.id}")

    # Generate QR code
    try:
        generate_qr_code(ticket)
        logger.info(f"Successfully generated QR code for ticket {ticket.ticket_id}")
    except Exception as e:
        logger.error(f"QR code generation error for ticket {ticket.ticket_id}: {str(e)}", exc_info=True)

    # Generate PDF
    try:
        pdf_path = generate_pdf_ticket(ticket)
        if pdf_path:
            ticket.pdf_ticket = pdf_path
            ticket.save()
            logger.info(f"Successfully generated PDF for ticket {ticket.ticket_id}: {pdf_path}")
        else:
            logger.warning(f"PDF generation returned None for ticket {ticket.ticket_id}")
    except Exception as e:
        logger.error(f"PDF generation error for ticket {ticket.ticket_id}: {str(e)}", exc_info=True)

    return ticket
