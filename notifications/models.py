from django.db import models
from accounts.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('rsvp_confirmed', 'RSVP Confirmed'),
        ('ticket_generated', 'Ticket Generated'),
        ('event_reminder', 'Event Reminder'),
        ('event_updated', 'Event Updated'),
        ('waitlist_promoted', 'Promoted from Waitlist'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
