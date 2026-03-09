from rest_framework import serializers
from events.models import Event, EventGallery
from tickets.models import Ticket
from rsvp.models import RSVP
from accounts.models import User
from attendance.models import Attendance
from notifications.models import Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "is_organizer"]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user profile serializer"""
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "registration_number",
            "role",
            "profile_picture",
            "phone_number",
            "bio",
            "department",
            "batch_year",
            "is_organizer",
            "created_at",
        ]
        read_only_fields = ["id", "role", "created_at"]


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


class EventDetailSerializer(serializers.ModelSerializer):
    """Detailed event serializer with all fields"""
    organizer = UserSerializer(read_only=True)
    remaining_seats = serializers.ReadOnlyField()
    confirmed_count = serializers.ReadOnlyField()
    waitlist_count = serializers.ReadOnlyField()
    attendance_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "category",
            "banner",
            "event_date",
            "end_date",
            "venue",
            "venue_details",
            "max_attendees",
            "rsvp_deadline",
            "organizer",
            "ticket_price",
            "is_free",
            "status",
            "is_featured",
            "tags",
            "remaining_seats",
            "confirmed_count",
            "waitlist_count",
            "attendance_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events"""
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "category",
            "banner",
            "event_date",
            "end_date",
            "venue",
            "venue_details",
            "max_attendees",
            "rsvp_deadline",
            "ticket_price",
            "is_free",
            "status",
            "is_featured",
            "tags",
        ]


class RSVPSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ["id", "event", "user", "status", "additional_info", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "ticket_id",
            "event",
            "user",
            "status",
            "qr_code",
            "pdf_ticket",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["ticket_id", "created_at", "updated_at"]


class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    ticket = TicketSerializer(read_only=True)
    checked_in_by_user = UserSerializer(source='checked_in_by', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "user",
            "event",
            "ticket",
            "status",
            "checked_in_at",
            "checked_out_at",
            "checked_in_by_user",
        ]
        read_only_fields = ["id", "checked_in_at", "checked_out_at", "checked_in_by_user"]


class AttendeeListSerializer(serializers.ModelSerializer):
    """Simplified attendee serializer for list views"""
    rsvp_status = serializers.SerializerMethodField()
    attendance_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "registration_number",
            "department",
            "rsvp_status",
            "attendance_status",
        ]

    def get_rsvp_status(self, obj):
        event = self.context.get('event')
        if not event:
            return None
        rsvp = RSVP.objects.filter(user=obj, event=event).first()
        return rsvp.status if rsvp else None

    def get_attendance_status(self, obj):
        event = self.context.get('event')
        if not event:
            return None
        attendance = Attendance.objects.filter(user=obj, event=event).first()
        return attendance.status if attendance else None


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "link",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EventGallerySerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = EventGallery
        fields = [
            "id",
            "event",
            "image",
            "caption",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_by", "uploaded_at"]
