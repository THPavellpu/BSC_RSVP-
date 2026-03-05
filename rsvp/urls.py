from django.urls import path
from . import views

urlpatterns = [
    path('event/<slug:slug>/', views.rsvp_event, name='rsvp_event'),
    path('cancel/<int:rsvp_id>/', views.cancel_rsvp, name='cancel_rsvp'),
    path('success/<uuid:ticket_id>/', views.registration_success, name='registration_success'),
    path('success/rsvp/<int:rsvp_id>/', views.registration_success, name='registration_success_rsvp'),
]
