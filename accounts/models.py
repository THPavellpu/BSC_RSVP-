from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('student', 'Student'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    department = models.CharField(max_length=200, blank=True)
    batch_year = models.CharField(max_length=10, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def get_full_name(self):
        return self.full_name

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_organizer(self):
        return self.role in ('admin', 'organizer') or self.is_superuser

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
