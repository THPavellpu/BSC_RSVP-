from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import RSVP
from events.models import Event
from tickets.utils import generate_ticket
from notifications.utils import notify_rsvp_confirmed


@login_required
def rsvp_event(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if not event.is_rsvp_open:
        messages.error(request, 'RSVP is closed for this event.')
        return redirect('event_detail', slug=slug)

    existing_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
    if existing_rsvp:
        messages.warning(request, f'You have already registered for this event. Status: {existing_rsvp.get_status_display()}')
        return redirect('event_detail', slug=slug)

    if request.method == 'POST':
        additional_info = request.POST.get('additional_info', '')
        status = 'confirmed' if not event.is_full else 'waitlisted'

        rsvp = RSVP.objects.create(
            user=request.user,
            event=event,
            status=status,
            additional_info=additional_info,
        )

        if status == 'confirmed':
            # Generate ticket
            try:
                ticket = generate_ticket(request.user, event, rsvp)
                notify_rsvp_confirmed(request.user, event, ticket)
                messages.success(request, f'🎉 RSVP confirmed! Your ticket has been generated. Check your profile.')
            except Exception as e:
                print(f"Ticket/notification error: {e}")
                messages.success(request, f'🎉 RSVP confirmed! Your ticket is being processed.')
        else:
            messages.info(request, f'You have been added to the waiting list for "{event.title}".')

        return redirect('event_detail', slug=slug)

    return render(request, 'rsvp/rsvp_form.html', {'event': event})


@login_required
def cancel_rsvp(request, rsvp_id):
    rsvp = get_object_or_404(RSVP, id=rsvp_id, user=request.user)
    event = rsvp.event

    if request.method == 'POST':
        # Cancel associated ticket
        from tickets.models import Ticket
        Ticket.objects.filter(user=request.user, event=event).update(status='cancelled')

        # Promote first person on waitlist
        waitlisted = RSVP.objects.filter(event=event, status='waitlisted').order_by('created_at').first()
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
        messages.success(request, f'Your registration for "{event.title}" has been cancelled.')
        return redirect('profile')

    return render(request, 'rsvp/cancel_rsvp.html', {'rsvp': rsvp})
