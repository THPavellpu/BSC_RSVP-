from django.db import models
from django.utils import timezone
from django.urls import reverse
from accounts.models import User


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('seminar', 'Seminar'),
        ('meetup', 'Meetup'),
        ('workshop', 'Workshop'),
        ('competition', 'Competition'),
        ('social', 'Social'),
        ('academic', 'Academic'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    event_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=300)
    venue_details = models.TextField(blank=True)
    max_attendees = models.PositiveIntegerField(default=100)
    rsvp_deadline = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_featured = models.BooleanField(default=False)
    tags = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})

    @property
    def is_rsvp_open(self):
        return timezone.now() <= self.rsvp_deadline and self.status == 'upcoming'

    @property
    def registered_count(self):
        return self.rsvps.filter(status__in=['confirmed', 'waitlisted']).count()

    @property
    def confirmed_count(self):
        return self.rsvps.filter(status='confirmed').count()

    @property
    def waitlist_count(self):
        return self.rsvps.filter(status='waitlisted').count()

    @property
    def remaining_seats(self):
        return max(0, self.max_attendees - self.confirmed_count)

    @property
    def is_full(self):
        return self.confirmed_count >= self.max_attendees

    @property
    def attendance_percentage(self):
        if self.confirmed_count == 0:
            return 0
        checked_in = self.attendances.filter(status='checked_in').count()
        return round((checked_in / self.confirmed_count) * 100, 1)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = slugify(self.title) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-event_date']


class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='event_gallery/')
    caption = models.CharField(max_length=300, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.title} - Gallery Image"

    class Meta:
        verbose_name_plural = 'Event Gallery Images'
        ordering = ['-uploaded_at']
