from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seeds the database with sample data for development'

    def handle(self, *args, **options):
        from accounts.models import User
        from events.models import Event
        from django.utils.text import slugify
        import uuid

        self.stdout.write('Seeding database...')

        # Create organizer
        if not User.objects.filter(email='organizer@lpu.in').exists():
            organizer = User.objects.create_user(
                username='organizer',
                email='organizer@lpu.in',
                password='password123',
                full_name='Community Organizer',
                role='organizer',
                registration_number='ORG001',
            )
        else:
            organizer = User.objects.get(email='organizer@lpu.in')
        self.stdout.write('  Created organizer: organizer@lpu.in / password123')

        # Create students
        for i in range(1, 6):
            email = f'student{i}@lpu.in'
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    username=f'student{i}',
                    email=email,
                    password='password123',
                    full_name=f'Bangladeshi Student {i}',
                    role='student',
                    registration_number=f'12{i:04d}',
                    department='Computer Science',
                    batch_year='2023',
                )
        self.stdout.write('  Created 5 students: student1–5@lpu.in / password123')

        # Note: Event creation removed to preserve existing organizer-created events in production
        # Only organizer-created events are retained. To add new events, create them manually in the admin panel.

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded! Run: python manage.py runserver'))
