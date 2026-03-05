from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
import os
from django.conf import settings
from .models import Ticket


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('event').order_by('-created_at')
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def download_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    if ticket.pdf_ticket:
        pdf_path = os.path.join(settings.MEDIA_ROOT, str(ticket.pdf_ticket))
        if os.path.exists(pdf_path):
            return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf',
                                as_attachment=True, filename=f'ticket_{ticket.ticket_number}.pdf')
    messages.error(request, 'PDF ticket not available. Please try again.')
    return redirect('ticket_detail', ticket_id=ticket_id)
