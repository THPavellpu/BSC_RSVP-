import qrcode
import os
import io
import logging
import requests
from PIL import Image as PILImage
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def generate_qr_code(ticket):
    """
    Generate QR code for a ticket and save it to storage (local or Cloudinary).
    Returns the saved file path/reference.
    """
    try:
        qr_data = f"LPUBSC-TICKET:{ticket.ticket_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image with PIL
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to RGB if necessary (for PNG compatibility)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert PIL image to bytes
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        # Create filename and save to storage
        filename = f"ticket_{ticket.ticket_id}.png"
        filepath = f"tickets/qr_codes/{filename}"
        
        # Save file using Django storage (handles both local and Cloudinary)
        saved_path = default_storage.save(filepath, ContentFile(img_io.getvalue()))
        
        # Update ticket with the saved file path
        ticket.qr_code = saved_path
        ticket.save(update_fields=['qr_code', 'updated_at'])
        
        logger.info(f"✓ QR code generated for ticket {ticket.ticket_id}")
        return saved_path
        
    except Exception as e:
        logger.error(f"✗ QR code generation failed for ticket {ticket.ticket_id}: {str(e)}", exc_info=True)
        raise


def generate_pdf_ticket(ticket):
    """
    Generate a professional PDF ticket with embedded QR code.
    Returns the saved file path/reference.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        # Create PDF in memory
        pdf_io = io.BytesIO()
        doc = SimpleDocTemplate(pdf_io, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=colors.HexColor('#1a472a'),
            alignment=TA_CENTER,
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#27ae60'),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=8
        )
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=4
        )
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#999999'),
            spaceAfter=4
        )
        
        # Header
        story.append(Paragraph("LPU BANGLADESH", title_style))
        story.append(Paragraph("STUDENTS COMMUNITY", title_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("EVENT ADMISSION TICKET", subtitle_style))
        story.append(Spacer(1, 0.4*cm))
        
        # Event Information
        story.append(Paragraph(f"<b>EVENT:</b> {ticket.event.title}", body_style))
        story.append(Spacer(1, 0.2*cm))
        
        story.append(Paragraph(f"<b>ATTENDEE:</b> {ticket.user.full_name}", body_style))
        story.append(Spacer(1, 0.2*cm))
        
        event_date = ticket.event.event_date.strftime('%d %B %Y at %I:%M %p')
        story.append(Paragraph(f"<b>DATE & TIME:</b> {event_date}", body_style))
        story.append(Spacer(1, 0.2*cm))
        
        story.append(Paragraph(f"<b>VENUE:</b> {ticket.event.venue}", body_style))
        story.append(Spacer(1, 0.2*cm))
        
        ticket_status = ticket.get_status_display()
        status_color = '#27ae60' if ticket.status == 'active' else '#e74c3c'
        story.append(Paragraph(f"<b>STATUS:</b> <font color='{status_color}'>{ticket_status}</font>", body_style))
        story.append(Spacer(1, 0.5*cm))
        
        # QR Code Section
        story.append(Paragraph("ADMISSION QR CODE", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        
        qr_img = None
        if ticket.qr_code:
            try:
                # Try to get QR code from storage
                qr_io = io.BytesIO()
                qr_file = default_storage.open(str(ticket.qr_code), 'rb')
                qr_io.write(qr_file.read())
                qr_file.close()
                qr_io.seek(0)
                
                # Add QR image to PDF
                qr_img = RLImage(qr_io, width=5*cm, height=5*cm)
                story.append(qr_img)
                story.append(Spacer(1, 0.3*cm))
            except Exception as e:
                logger.warning(f"Could not embed QR code in PDF for ticket {ticket.ticket_id}: {str(e)}")
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"<b>TICKET ID:</b> {ticket.ticket_number}", footer_style))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("Please present this ticket at the event entrance.", footer_style))
        story.append(Paragraph("Keep this ticket safe for entry verification.", footer_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Generated: " + timezone.now().strftime('%d %b %Y %H:%M'), footer_style))
        
        # Build PDF
        doc.build(story)
        pdf_io.seek(0)
        
        # Save PDF to storage
        filename = f"ticket_{ticket.ticket_id}.pdf"
        filepath = f"tickets/pdfs/{filename}"
        saved_path = default_storage.save(filepath, ContentFile(pdf_io.getvalue()))
        
        logger.info(f"✓ PDF generated for ticket {ticket.ticket_id}")
        return saved_path
        
    except ImportError as e:
        logger.error(f"✗ ReportLab not installed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"✗ PDF generation failed for ticket {ticket.ticket_id}: {str(e)}", exc_info=True)
        raise


def generate_ticket(user, event, rsvp=None):
    """
    Generate a complete ticket with QR code and PDF.
    - Checks if ticket already exists for user+event
    - Generates QR code and saves to Cloudinary/local storage
    - Generates PDF with embedded QR code
    - Works with PostgreSQL database
    """
    from .models import Ticket
    
    try:
        # Check if ticket already exists
        existing = Ticket.objects.filter(user=user, event=event).first()
        if existing:
            logger.info(f"⚠ Ticket already exists for user {user.id} and event {event.id}")
            return existing
        
        # Create new ticket
        ticket = Ticket.objects.create(
            user=user,
            event=event,
            rsvp=rsvp,
            status='active',
        )
        logger.info(f"✓ New ticket created: {ticket.ticket_id}")
        
        # Generate QR code (must be first, so it exists for PDF embedding)
        try:
            qr_path = generate_qr_code(ticket)
            logger.info(f"✓ QR code saved: {qr_path}")
        except Exception as e:
            logger.error(f"✗ QR code generation failed: {str(e)}")
            raise
        
        # Generate PDF with embedded QR code
        try:
            pdf_path = generate_pdf_ticket(ticket)
            if pdf_path:
                ticket.pdf_ticket = pdf_path
                ticket.save(update_fields=['pdf_ticket', 'updated_at'])
                logger.info(f"✓ PDF saved: {pdf_path}")
            else:
                logger.warning(f"⚠ PDF generation returned None")
        except Exception as e:
            logger.error(f"✗ PDF generation failed: {str(e)}")
            raise
        
        logger.info(f"✓ Ticket complete: {ticket.ticket_id} (QR + PDF ready)")
        return ticket
        
    except Exception as e:
        logger.error(f"✗ Ticket generation failed: {str(e)}", exc_info=True)
        raise
