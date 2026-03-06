#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lpu_bsc.settings')
sys.path.insert(0, '/d/Desktop/lpu_bsc')
django.setup()

from django.test import Client

client = Client()

# Test events list
try:
    response = client.get('/events/')
    print(f"Events list status: {response.status_code}")
except Exception as e:
    print(f"Events list error: {str(e)}")
    import traceback
    traceback.print_exc()

# Test event detail
try:
    response = client.get('/events/event-name/')
    print(f"Event detail status: {response.status_code}")
except Exception as e:
    print(f"Event detail error: {str(e)}")
    import traceback
    traceback.print_exc()
