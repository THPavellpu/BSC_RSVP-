"""
Signal handlers for ticket generation and maintenance.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Ticket
from .utils import generate_qr_code, generate_pdf_ticket
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Ticket)
def ensure_ticket_files(sender, instance, created, **kwargs):
    """
    Ensure QR code and PDF exist for all tickets.
    This signal fires after a Ticket is saved.
    """
    try:
        # Generate QR code if missing
        if not instance.qr_code:
            try:
                logger.info(f"Generating QR code for ticket {instance.ticket_id}...")
                generate_qr_code(instance)
                logger.info(f"✓ QR code generated: {instance.ticket_id}")
            except Exception as e:
                logger.error(f"✗ QR code generation failed for {instance.ticket_id}: {str(e)}", exc_info=True)
        
        # Generate PDF if missing
        if not instance.pdf_ticket:
            try:
                logger.info(f"Generating PDF for ticket {instance.ticket_id}...")
                pdf_path = generate_pdf_ticket(instance)
                if pdf_path:
                    instance.pdf_ticket = pdf_path
                    instance.save(update_fields=['pdf_ticket', 'updated_at'])
                    logger.info(f"✓ PDF generated: {instance.ticket_id}")
                else:
                    logger.warning(f"⚠ PDF generation returned None for {instance.ticket_id}")
            except Exception as e:
                logger.error(f"✗ PDF generation failed for {instance.ticket_id}: {str(e)}", exc_info=True)
                
    except Exception as e:
        logger.error(f"✗ Signal handler error for ticket {instance.ticket_id}: {str(e)}", exc_info=True)
