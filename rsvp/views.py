from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import RSVP
from events.models import Event
from tickets.utils import generate_ticket
from tickets.models import Ticket
from notifications.utils import notify_rsvp_confirmed


@login_required
def rsvp_event(request, slug):
    event = get_object_or_404(Event, slug=slug)

    # Check RSVP availability
    if not event.is_rsvp_open:
        messages.error(request, 'RSVP is closed for this event.')
        return redirect('event_detail', slug=slug)

    # Prevent duplicate registration
    existing_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
    if existing_rsvp:
        messages.warning(
            request,
            f'You have already registered for this event. Status: {existing_rsvp.get_status_display()}'
        )
        return redirect('event_detail', slug=slug)

    if request.method == 'POST':
        additional_info = request.POST.get('additional_info', '')

        # Determine RSVP status
        status = 'confirmed' if not event.is_full else 'waitlisted'

        # Create RSVP
        rsvp = RSVP.objects.create(
            user=request.user,
            event=event,
            status=status,
            additional_info=additional_info,
        )

        # Ensure DB save completed
        rsvp.refresh_from_db()

        # If confirmed → generate ticket
        if status == 'confirmed':
            try:
                ticket = generate_ticket(request.user, event, rsvp)

                # Send notification
                try:
                    notify_rsvp_confirmed(request.user, event, ticket)
                except Exception as e:
                    print(f"Notification error: {e}")

                return redirect('registration_success', ticket_id=ticket.ticket_id)

            except Exception as e:
                print(f"Ticket generation error: {e}")
                return redirect('registration_success_rsvp', rsvp_id=rsvp.id)

        # If waitlisted
        return redirect('registration_success_rsvp', rsvp_id=rsvp.id)

    return render(request, 'rsvp/rsvp_form.html', {'event': event})


@login_required
def registration_success(request, ticket_id=None, rsvp_id=None):
    """Display registration confirmation."""

    ticket = None
    rsvp = None

    # Case 1: Ticket exists
    if ticket_id:
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
        rsvp = ticket.rsvp

    # Case 2: RSVP exists but maybe waitlisted
    if rsvp_id and not rsvp:
        rsvp = get_object_or_404(RSVP, id=rsvp_id, user=request.user)

        if rsvp.status == 'confirmed':
            ticket = Ticket.objects.filter(user=request.user, event=rsvp.event).first()

    if not rsvp:
        messages.error(request, 'Registration not found.')
        return redirect('event_list')

    return render(request, 'rsvp/registration_success.html', {
        'ticket': ticket,
        'rsvp': rsvp,
    })


@login_required
def cancel_rsvp(request, rsvp_id):
    rsvp = get_object_or_404(RSVP, id=rsvp_id, user=request.user)
    event = rsvp.event

    if request.method == 'POST':

        # Cancel ticket
        Ticket.objects.filter(user=request.user, event=event).update(status='cancelled')

        # Promote waitlisted attendee
        waitlisted = RSVP.objects.filter(
            event=event,
            status='waitlisted'
        ).order_by('created_at').first()

        if waitlisted:
            waitlisted.status = 'confirmed'
            waitlisted.save()

            try:
                ticket = generate_ticket(waitlisted.user, event, waitlisted)
                notify_rsvp_confirmed(waitlisted.user, event, ticket)
            except Exception as e:
                print(f"Waitlist promotion error: {e}")

        rsvp.status = 'cancelled'
        rsvp.save()

        messages.success(
            request,
            f'Your registration for "{event.title}" has been cancelled.'
        )

        return redirect('profile')

    return render(request, 'rsvp/cancel_rsvp.html', {'rsvp': rsvp})