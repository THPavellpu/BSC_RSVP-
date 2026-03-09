from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ===== Authentication =====
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ===== Events =====
    path('events/', views.events_list, name='events_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('events/<slug:slug>/update/', views.update_event, name='update_event'),
    path('events/<slug:slug>/delete/', views.delete_event, name='delete_event'),
    path('events/<slug:slug>/analytics/', views.event_analytics, name='event_analytics'),

    # ===== Attendees =====
    path('events/<slug:slug>/attendees/', views.event_attendees, name='event_attendees'),
    path('events/<slug:slug>/attendees/stats/', views.attendees_stats, name='attendees_stats'),

    # ===== Attendance =====
    path('attendance/check-in/', views.check_in_attendee, name='check_in'),
    path('attendance/check-out/', views.check_out_attendee, name='check_out'),
    path('events/<slug:slug>/attendance/', views.event_attendance_records, name='event_attendance'),
    path('attendance/my-attendance/', views.my_attendance, name='my_attendance'),

    # ===== RSVP =====
    path('events/<slug:slug>/register/', views.register_event, name='register_event'),
    path('rsvp/', views.my_rsvps, name='my_rsvps'),
    path('rsvp/<int:rsvp_id>/', views.rsvp_detail, name='rsvp_detail'),
    path('rsvp/<int:rsvp_id>/cancel/', views.cancel_rsvp, name='cancel_rsvp'),
    path('rsvp/<int:rsvp_id>/update/', views.update_rsvp, name='update_rsvp'),

    # ===== Tickets =====
    path('tickets/', views.my_tickets, name='my_tickets'),
    path('tickets/<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # ===== User Profile =====
    path('user/profile/', views.my_profile, name='my_profile'),
    path('user/profile/update/', views.update_profile, name='update_profile'),
    path('user/<int:user_id>/profile/', views.user_profile, name='user_profile'),
    path('organizers/', views.organizers_list, name='organizers_list'),

    # ===== Notifications =====
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/unread-count/', views.unread_notifications_count, name='unread_count'),

    # ===== Event Gallery =====
    path('events/<slug:slug>/gallery/', views.event_gallery, name='event_gallery'),
    path('events/<slug:slug>/gallery/upload/', views.upload_gallery_image, name='upload_gallery_image'),
    path('events/<slug:slug>/gallery/<int:image_id>/delete/', views.delete_gallery_image, name='delete_gallery_image'),
]
