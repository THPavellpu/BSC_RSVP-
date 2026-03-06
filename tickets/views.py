from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
import os
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Ticket

logger = logging.getLogger(__name__)


@login_required
def my_tickets(request):
    """Display all tickets for the current user."""
    tickets = Ticket.objects.filter(user=request.user).select_related('event').order_by('-created_at')
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})


@login_required
def ticket_detail(request, ticket_id):
    """Display detailed ticket information with QR code."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    # Log ticket view
    logger.info(f"User {request.user.id} viewed ticket {ticket.ticket_id}")
    
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def download_ticket(request, ticket_id):
    """
    Download ticket PDF.
    Generates PDF on-the-fly if not available.
    """
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    try:
        # Check if PDF exists
        if not ticket.pdf_ticket:
            logger.warning(f"PDF not found for ticket {ticket.ticket_id}, attempting to generate...")
            from tickets.utils import generate_pdf_ticket
            
            # Ensure QR code exists first
            if not ticket.qr_code:
                from tickets.utils import generate_qr_code
                generate_qr_code(ticket)
            
            # Generate PDF
            pdf_path = generate_pdf_ticket(ticket)
            if pdf_path:
                ticket.pdf_ticket = pdf_path
                ticket.save(update_fields=['pdf_ticket', 'updated_at'])
                logger.info(f"PDF generated on-the-fly for ticket {ticket.ticket_id}")
            else:
                raise Exception("PDF generation returned None")
        
        # Open and serve PDF file
        pdf_file = default_storage.open(str(ticket.pdf_ticket), 'rb')
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.ticket_number}.pdf"'
        pdf_file.close()
        
        logger.info(f"PDF downloaded for ticket {ticket.ticket_id}")
        return response
        
    except FileNotFoundError:
        logger.error(f"PDF file not found for ticket {ticket.ticket_id}")
        messages.error(request, 'PDF file not found. Our team has been notified.')
        return redirect('ticket_detail', ticket_id=ticket_id)
        
    except Exception as e:
        logger.error(f"Error downloading PDF for ticket {ticket.ticket_id}: {str(e)}", exc_info=True)
        messages.error(request, f'Error downloading PDF: {str(e)}')
        return redirect('ticket_detail', ticket_id=ticket_id)

