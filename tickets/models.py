from django.db import models
import uuid
from accounts.models import User
from events.models import Event
from rsvp.models import RSVP


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    rsvp = models.OneToOneField(RSVP, on_delete=models.CASCADE, related_name='ticket', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    qr_code = models.ImageField(upload_to='tickets/qr_codes/', blank=True, null=True)
    pdf_ticket = models.FileField(upload_to='tickets/pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{str(self.ticket_id)[:8]} - {self.user.full_name} - {self.event.title}"

    @property
    def ticket_number(self):
        return str(self.ticket_id).upper()[:8]

    class Meta:
        ordering = ['-created_at']
