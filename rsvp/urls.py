from django.urls import path
from . import views

app_name = "rsvp"
urlpatterns = [
    path('event/<slug:slug>/', views.rsvp_event, name='rsvp_event'),
    path('cancel/<int:rsvp_id>/', views.cancel_rsvp, name='cancel_rsvp'),

    # Success pages
    path('success/ticket/<uuid:ticket_id>/', views.registration_success, name='registration_success_ticket'),
    path('success/rsvp/<int:rsvp_id>/', views.registration_success, name='registration_success_rsvp'),
]