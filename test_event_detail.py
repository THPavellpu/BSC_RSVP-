#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lpu_bsc.settings')
django.setup()

from events.models import Event
from rsvp.models import RSVP
from tickets.models import Ticket
from django.contrib.auth.models import AnonymousUser

# Test the view directly
from django.test import RequestFactory
from events.views import event_detail

factory = RequestFactory()
event = Event.objects.first()

try:
    request = factory.get(f'/events/{event.slug}/')
    request.user = AnonymousUser()  # Anonymous user
    response = event_detail(request, slug=event.slug)
    print(f"Response status: {response.status_code}")
    print("Success!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
