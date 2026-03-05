"""
Management command to seed the database with sample data for development.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seeds the database with sample data for development'

    def handle(self, *args, **options):
        from accounts.models import User
        from events.models import Event

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
            self.stdout.write(f'  Created organizer: organizer@lpu.in / password123')
        else:
            organizer = User.objects.get(email='organizer@lpu.in')

        # Create sample students
        students = []
        for i in range(1, 6):
            email = f'student{i}@lpu.in'
            if not User.objects.filter(email=email).exists():
                s = User.objects.create_user(
                    username=f'student{i}',
                    email=email,
                    password='password123',
                    full_name=f'Bangladeshi Student {i}',
                    role='student',
                    registration_number=f'12{i:04d}',
                    department='Computer Science',
                    batch_year='2023',
                )
                students.append(s)
        self.stdout.write(f'  Created 5 sample students (password: password123)')

        # Create sample events
        categories = ['cultural', 'sports', 'seminar', 'meetup', 'workshop']
        event_titles = [
            'Eid Celebration 2024',
            'Bangladeshi Cultural Night',
            'Cricket Tournament',
            'Career Guidance Seminar',
            'Community Meetup – Spring 2024',
            'Tech Workshop: App Development',
        ]

        for i, title in enumerate(event_titles):
            from django.utils.text import slugify
            import uuid
            slug = slugify(title) + '-' + str(uuid.uuid4())[:6]
            event_date = timezone.now() + timedelta(days=random.randint(5, 60))
            if not Event.objects.filter(title=title).exists():
                Event.objects.create(
                    title=title,
                    slug=slug,
                    description=f"Join us for {title}! This is a wonderful opportunity for all Bangladeshi students at LPU to come together, celebrate, and connect with each other.\n\nDon't miss this event — register now!",
                    category=categories[i % len(categories)],
                    event_date=event_date,
                    end_date=event_date + timedelta(hours=3),
                    venue='Uni Block 34, LPU Campus',
                    max_attendees=random.randint(50, 200),
                    rsvp_deadline=event_date - timedelta(days=2),
                    organizer=organizer,
                    is_free=random.choice([True, True, False]),
                    ticket_price=random.choice([0, 50, 100, 200]),
                    status='upcoming',
                    is_featured=(i < 2),
                    tags=f'lpu bsc bangladesh community',
                )

        self.stdout.write(self.style.SUCCESS(f'  Created {len(event_titles)} sample events'))
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Organizer: organizer@lpu.in / password123')
        self.stdout.write('  Students:  student1@lpu.in – student5@lpu.in / password123')
