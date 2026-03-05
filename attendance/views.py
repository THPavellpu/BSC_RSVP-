from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Attendance
from tickets.models import Ticket
from events.models import Event
import uuid


@login_required
def scan_qr(request, slug):
    """Page for organizers to scan QR codes."""
    if not request.user.is_organizer:
        messages.error(request, 'Access denied.')
        return redirect('home')
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'attendance/scan_qr.html', {'event': event})


@login_required
def verify_ticket(request):
    """API endpoint to verify a ticket from QR scan."""
    if not request.user.is_organizer:
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    ticket_data = request.GET.get('ticket_data', '')
    event_id = request.GET.get('event_id', '')

    if not ticket_data or not event_id:
        return JsonResponse({'success': False, 'message': 'Invalid request.'})

    # Parse QR data: LPUBSC-TICKET:<uuid>
    if not ticket_data.startswith('LPUBSC-TICKET:'):
        return JsonResponse({'success': False, 'message': 'Invalid QR code format.'})

    ticket_uuid_str = ticket_data.replace('LPUBSC-TICKET:', '').strip()

    try:
        ticket_uuid = uuid.UUID(ticket_uuid_str)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid ticket ID.'})

    try:
        ticket = Ticket.objects.select_related('user', 'event').get(ticket_id=ticket_uuid)
    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ticket not found.'})

    # Verify event match
    if str(ticket.event.id) != str(event_id):
        return JsonResponse({'success': False, 'message': f'Ticket is for a different event: {ticket.event.title}'})

    if ticket.status == 'cancelled':
        return JsonResponse({'success': False, 'message': 'This ticket has been cancelled.'})

    if ticket.status == 'used':
        try:
            att = Attendance.objects.get(ticket=ticket)
            return JsonResponse({
                'success': False,
                'message': f'Ticket already used! {ticket.user.full_name} checked in at {att.checked_in_at.strftime("%H:%M")}'
            })
        except Attendance.DoesNotExist:
            pass

    # Check if already checked in
    existing_attendance = Attendance.objects.filter(user=ticket.user, event=ticket.event).first()
    if existing_attendance:
        return JsonResponse({
            'success': False,
            'message': f'Already checked in! {ticket.user.full_name} at {existing_attendance.checked_in_at.strftime("%H:%M")}'
        })

    # Check in the user
    attendance = Attendance.objects.create(
        user=ticket.user,
        event=ticket.event,
        ticket=ticket,
        status='checked_in',
        checked_in_by=request.user,
    )

    # Update ticket status
    ticket.status = 'used'
    ticket.save()

    return JsonResponse({
        'success': True,
        'message': f'✅ Checked in successfully!',
        'user_name': ticket.user.full_name,
        'ticket_number': ticket.ticket_number,
        'check_in_time': attendance.checked_in_at.strftime('%H:%M:%S'),
    })


@login_required
def manual_checkin(request, slug):
    """Manual check-in by ticket number."""
    if not request.user.is_organizer:
        messages.error(request, 'Access denied.')
        return redirect('home')
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id', '').strip()
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id, event=event)
            if Attendance.objects.filter(user=ticket.user, event=event).exists():
                messages.warning(request, f'{ticket.user.full_name} is already checked in.')
            else:
                Attendance.objects.create(
                    user=ticket.user,
                    event=event,
                    ticket=ticket,
                    status='checked_in',
                    checked_in_by=request.user,
                )
                ticket.status = 'used'
                ticket.save()
                messages.success(request, f'✅ {ticket.user.full_name} checked in successfully!')
        except Ticket.DoesNotExist:
            messages.error(request, 'Ticket not found for this event.')
    return redirect('scan_qr', slug=slug)


@login_required
def attendance_list(request, slug):
    """View attendance list for an event."""
    event = get_object_or_404(Event, slug=slug)
    if not request.user.is_admin and event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('event_detail', slug=slug)
    attendances = Attendance.objects.filter(event=event).select_related('user').order_by('-checked_in_at')
    return render(request, 'attendance/attendance_list.html', {
        'event': event,
        'attendances': attendances,
        'total': attendances.count(),
    })
