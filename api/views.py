from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from events.models import Event, EventGallery
from rsvp.models import RSVP
from tickets.models import Ticket
from tickets.utils import generate_ticket
from attendance.models import Attendance
from accounts.models import User
from notifications.models import Notification

from .serializers import (
    EventSerializer, 
    EventDetailSerializer,
    EventCreateUpdateSerializer,
    TicketSerializer, 
    RSVPSerializer,
    AttendanceSerializer,
    AttendeeListSerializer,
    UserDetailSerializer,
    NotificationSerializer,
    EventGallerySerializer,
)


# ============= EVENTS ENDPOINTS =============

@api_view(["GET"])
@permission_classes([AllowAny])
def events_list(request):
    """List all upcoming events with optional filtering"""
    events = Event.objects.filter(status="upcoming")
    
    # Filter by category
    category = request.query_params.get('category')
    if category:
        events = events.filter(category=category)
    
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def event_detail(request, slug):
    """Get detailed event information"""
    event = get_object_or_404(Event, slug=slug)
    serializer = EventDetailSerializer(event)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_event(request):
    """Create new event (organizer only)"""
    if not request.user.is_organizer:
        return Response(
            {"error": "Only organizers can create events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = EventCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save(organizer=request.user)
        return Response(
            EventDetailSerializer(event).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_event(request, slug):
    """Update event (organizer only)"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only update your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = EventCreateUpdateSerializer(
        event, 
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    if serializer.is_valid():
        event = serializer.save()
        return Response(EventDetailSerializer(event).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_event(request, slug):
    """Delete event (organizer only)"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only delete your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    event.delete()
    return Response(
        {"message": "Event deleted successfully"}, 
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_analytics(request, slug):
    """Get event analytics (organizer only)"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only view analytics for your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    data = {
        "event_title": event.title,
        "total_capacity": event.max_attendees,
        "confirmed_registrations": event.confirmed_count,
        "waitlisted": event.waitlist_count,
        "total_registrations": event.registered_count,
        "checked_in": event.attendances.filter(status='checked_in').count(),
        "attendance_percentage": event.attendance_percentage,
        "remaining_seats": event.remaining_seats,
        "event_status": event.status,
    }
    return Response(data)


# ============= ATTENDEES ENDPOINTS =============

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_attendees(request, slug):
    """Get list of attendees for an event"""
    event = get_object_or_404(Event, slug=slug)
    
    # Only organizer can view attendees list
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only view attendees for your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filter by status
    status_filter = request.query_params.get('status')  # confirmed, waitlisted, all
    
    if status_filter == 'confirmed':
        rsvps = event.rsvps.filter(status='confirmed')
    elif status_filter == 'waitlisted':
        rsvps = event.rsvps.filter(status='waitlisted')
    else:
        rsvps = event.rsvps.all()
    
    users = User.objects.filter(rsvps__in=rsvps)
    serializer = AttendeeListSerializer(
        users, 
        many=True, 
        context={'event': event}
    )
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def attendees_stats(request, slug):
    """Get attendance statistics for an event"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only view stats for your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = {
        "event_title": event.title,
        "total_capacity": event.max_attendees,
        "confirmed_count": event.confirmed_count,
        "waitlisted_count": event.waitlist_count,
        "total_registered": event.registered_count,
        "checked_in_count": event.attendances.filter(status='checked_in').count(),
        "not_checked_in": event.confirmed_count - event.attendances.filter(status='checked_in').count(),
        "attendance_rate": f"{event.attendance_percentage}%",
        "available_seats": event.remaining_seats,
        "is_full": event.is_full,
    }
    return Response(stats)


# ============= ATTENDANCE ENDPOINTS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_in_attendee(request):
    """
    Check-in an attendee
    Required: ticket_id or event_slug + user_id
    """
    ticket_id = request.data.get('ticket_id')
    event_slug = request.data.get('event_slug')
    user_id = request.data.get('user_id')
    
    if ticket_id:
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        event = ticket.event
        user = ticket.user
    elif event_slug and user_id:
        event = get_object_or_404(Event, slug=event_slug)
        user = get_object_or_404(User, id=user_id)
    else:
        return Response(
            {"error": "Provide either ticket_id or (event_slug + user_id)"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user is organizer or admin
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "Only event organizer can check-in attendees"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if already checked in
    attendance = Attendance.objects.filter(user=user, event=event).first()
    if attendance and attendance.status == 'checked_in':
        return Response(
            {"error": "User already checked in"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create or update attendance
    if attendance:
        attendance.status = 'checked_in'
        attendance.checked_in_at = timezone.now()
        attendance.checked_in_by = request.user
        attendance.save()
    else:
        attendance = Attendance.objects.create(
            user=user,
            event=event,
            status='checked_in',
            checked_in_by=request.user,
            ticket=ticket if ticket_id else None
        )
    
    serializer = AttendanceSerializer(attendance)
    return Response(
        {
            "message": "User checked in successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_out_attendee(request):
    """Check-out an attendee"""
    ticket_id = request.data.get('ticket_id')
    event_slug = request.data.get('event_slug')
    user_id = request.data.get('user_id')
    
    if ticket_id:
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        event = ticket.event
        user = ticket.user
    elif event_slug and user_id:
        event = get_object_or_404(Event, slug=event_slug)
        user = get_object_or_404(User, id=user_id)
    else:
        return Response(
            {"error": "Provide either ticket_id or (event_slug + user_id)"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "Only event organizer can check-out attendees"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    attendance = get_object_or_404(Attendance, user=user, event=event)
    
    attendance.status = 'checked_out'
    attendance.checked_out_at = timezone.now()
    attendance.save()
    
    serializer = AttendanceSerializer(attendance)
    return Response(
        {
            "message": "User checked out successfully",
            "data": serializer.data
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_attendance_records(request, slug):
    """Get all attendance records for an event"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only view attendance for your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filter by status
    status_filter = request.query_params.get('status')  # checked_in, checked_out, all
    
    attendances = event.attendances.all()
    if status_filter and status_filter != 'all':
        attendances = attendances.filter(status=status_filter)
    
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_attendance(request):
    """Get current user's attendance history"""
    attendances = Attendance.objects.filter(user=request.user)
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)


# ============= RSVP ENDPOINTS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_event(request, slug):
    """Register for an event"""
    event = get_object_or_404(Event, slug=slug)

    existing = RSVP.objects.filter(user=request.user, event=event).first()
    if existing:
        return Response({"message": "Already registered"}, status=400)

    status_choice = "confirmed" if not event.is_full else "waitlisted"

    rsvp = RSVP.objects.create(
        user=request.user,
        event=event,
        status=status_choice,
        additional_info=request.data.get('additional_info', '')
    )

    ticket = None

    if status_choice == "confirmed":
        ticket = generate_ticket(request.user, event, rsvp)

    return Response({
        "status": status_choice,
        "ticket_id": str(ticket.ticket_id) if ticket else None,
        "rsvp_id": rsvp.id
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_rsvps(request):
    """Get current user's RSVPs"""
    rsvps = RSVP.objects.filter(user=request.user)
    serializer = RSVPSerializer(rsvps, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def rsvp_detail(request, rsvp_id):
    """Get RSVP details"""
    rsvp = get_object_or_404(RSVP, id=rsvp_id, user=request.user)
    serializer = RSVPSerializer(rsvp)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_rsvp(request, rsvp_id):
    """Cancel RSVP"""
    rsvp = get_object_or_404(RSVP, id=rsvp_id, user=request.user)
    event = rsvp.event
    
    rsvp.status = 'cancelled'
    rsvp.save()
    
    # If there's a ticket, cancel it too
    if hasattr(rsvp, 'ticket'):
        rsvp.ticket.status = 'cancelled'
        rsvp.ticket.save()
    
    return Response({"message": "RSVP cancelled successfully"})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_rsvp(request, rsvp_id):
    """Update RSVP"""
    rsvp = get_object_or_404(RSVP, id=rsvp_id, user=request.user)
    
    serializer = RSVPSerializer(rsvp, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============= TICKETS ENDPOINTS =============

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_tickets(request):
    """Get current user's tickets"""
    tickets = Ticket.objects.filter(user=request.user)
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ticket_detail(request, ticket_id):
    """Get ticket details"""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)


# ============= USER PROFILE ENDPOINTS =============

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """Get current user's profile"""
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update current user's profile"""
    serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_profile(request, user_id):
    """Get public user profile"""
    user = get_object_or_404(User, id=user_id)
    serializer = UserDetailSerializer(user)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def organizers_list(request):
    """Get all organizers"""
    organizers = User.objects.filter(Q(role='organizer') | Q(is_superuser=True)).distinct()
    serializer = UserDetailSerializer(organizers, many=True)
    return Response(serializer.data)


# ============= NOTIFICATIONS ENDPOINTS =============

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """Get user notifications with pagination"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read status
    unread_only = request.query_params.get('unread') == 'true'
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return Response({"message": "Notification deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_notifications_count(request):
    """Get unread notifications count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({"unread_count": count})


# ============= EVENT GALLERY ENDPOINTS =============

@api_view(["GET"])
@permission_classes([AllowAny])
def event_gallery(request, slug):
    """Get event gallery images"""
    event = get_object_or_404(Event, slug=slug)
    gallery_images = event.gallery_images.all()
    serializer = EventGallerySerializer(gallery_images, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_gallery_image(request, slug):
    """Upload image to event gallery"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only upload images for your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = EventGallerySerializer(data=request.data)
    if serializer.is_valid():
        gallery_image = serializer.save(event=event, uploaded_by=request.user)
        return Response(
            EventGallerySerializer(gallery_image).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_gallery_image(request, slug, image_id):
    """Delete gallery image"""
    event = get_object_or_404(Event, slug=slug)
    
    if event.organizer != request.user and not request.user.is_superuser:
        return Response(
            {"error": "You can only delete images from your own events"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    gallery_image = get_object_or_404(EventGallery, id=image_id, event=event)
    gallery_image.delete()
    return Response({"message": "Image deleted"}, status=status.HTTP_204_NO_CONTENT)
