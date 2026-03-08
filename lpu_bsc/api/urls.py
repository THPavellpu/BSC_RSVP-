from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),

    path("events/", views.events_list),
    path("events/<slug:slug>/", views.event_detail),

    path("events/<slug:slug>/register/", views.register_event),

    path("tickets/", views.my_tickets),
    path("tickets/<uuid:ticket_id>/", views.ticket_detail),
]
