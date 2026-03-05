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

        # Create events
        categories = ['cultural', 'sports', 'seminar', 'meetup', 'workshop']
        titles = [
            'Eid Celebration 2024',
            'Bangladeshi Cultural Night',
            'Cricket Tournament',
            'Career Guidance Seminar',
            'Community Meetup – Spring 2024',
            'Tech Workshop: App Development',
        ]
        for i, title in enumerate(titles):
            if not Event.objects.filter(title=title).exists():
                event_date = timezone.now() + timedelta(days=random.randint(7, 60))
                Event.objects.create(
                    title=title,
                    slug=slugify(title) + '-' + str(uuid.uuid4())[:6],
                    description=f"Join us for {title}! A wonderful opportunity for Bangladeshi students at LPU to connect and celebrate.\n\nRegister now and secure your spot!",
                    category=categories[i % len(categories)],
                    event_date=event_date,
                    end_date=event_date + timedelta(hours=3),
                    venue='Uni Block 34 Auditorium, LPU Campus',
                    max_attendees=random.choice([50, 100, 150, 200]),
                    rsvp_deadline=event_date - timedelta(days=2),
                    organizer=organizer,
                    is_free=i % 3 != 0,
                    ticket_price=0 if i % 3 != 0 else 100,
                    status='upcoming',
                    is_featured=(i < 2),
                    tags='lpu bsc bangladesh community',
                )
        self.stdout.write(f'  Created {len(titles)} sample events')
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded! Run: python manage.py runserver'))
