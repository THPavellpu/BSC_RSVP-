from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from events.models import Event
from rsvp.models import RSVP
from tickets.models import Ticket
from tickets.utils import generate_ticket

from .serializers import EventSerializer, TicketSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def events_list(request):
    events = Event.objects.filter(status="upcoming")
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    serializer = EventSerializer(event)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_event(request, slug):
    event = get_object_or_404(Event, slug=slug)

    existing = RSVP.objects.filter(user=request.user, event=event).first()
    if existing:
        return Response({"message": "Already registered"}, status=400)

    status = "confirmed" if not event.is_full else "waitlisted"

    rsvp = RSVP.objects.create(
        user=request.user,
        event=event,
        status=status
    )

    ticket = None

    if status == "confirmed":
        ticket = generate_ticket(request.user, event, rsvp)

    return Response({
        "status": status,
        "ticket_id": str(ticket.ticket_id) if ticket else None
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)
