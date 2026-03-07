from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
import logging
from django.conf import settings
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

