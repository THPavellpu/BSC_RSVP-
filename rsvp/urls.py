from django.urls import path
from . import views

urlpatterns = [
    path('event/<slug:slug>/', views.rsvp_event, name='rsvp_event'),
    path('cancel/<int:rsvp_id>/', views.cancel_rsvp, name='cancel_rsvp'),
]
