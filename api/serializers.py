from rest_framework import serializers
from events.models import Event
from tickets.models import Ticket
from rsvp.models import RSVP
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "is_organizer"]


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    remaining_seats = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "banner",
            "event_date",
            "venue",
            "remaining_seats",
            "organizer",
        ]


class RSVPSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ["id", "event", "status", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "ticket_id",
            "event",
            "status",
            "qr_code",
            "created_at",
        ]
