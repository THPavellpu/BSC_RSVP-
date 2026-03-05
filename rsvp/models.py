from django.db import models
from django.utils import timezone
from accounts.models import User
from events.models import Event


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    additional_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'event']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.event.title} ({self.status})"
