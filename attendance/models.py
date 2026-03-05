from django.db import models
from django.utils import timezone
from accounts.models import User
from events.models import Event
from tickets.models import Ticket


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='attendance', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_in')
    checked_in_at = models.DateTimeField(auto_now_add=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='check_ins_done')

    class Meta:
        unique_together = ['user', 'event']
        ordering = ['-checked_in_at']

    def __str__(self):
        return f"{self.user.full_name} checked in to {self.event.title}"
