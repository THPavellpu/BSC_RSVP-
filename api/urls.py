from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ===== Authentication =====
    path('auth/login/', TokenObtainPairView.as_view(), name='api_token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),

    # ===== Events =====
    path('events/', views.events_list, name='api_events_list'),
    path('events/create/', views.create_event, name='api_create_event'),
    path('events/<slug:slug>/', views.event_detail, name='api_event_detail'),
    path('events/<slug:slug>/update/', views.update_event, name='api_update_event'),
    path('events/<slug:slug>/delete/', views.delete_event, name='api_delete_event'),
    path('events/<slug:slug>/analytics/', views.event_analytics, name='api_event_analytics'),

    # ===== Attendees =====
    path('events/<slug:slug>/attendees/', views.event_attendees, name='api_event_attendees'),
    path('events/<slug:slug>/attendees/stats/', views.attendees_stats, name='api_attendees_stats'),

    # ===== Attendance =====
    path('attendance/check-in/', views.check_in_attendee, name='api_check_in'),
    path('attendance/check-out/', views.check_out_attendee, name='api_check_out'),
    path('events/<slug:slug>/attendance/', views.event_attendance_records, name='api_event_attendance'),
    path('attendance/my-attendance/', views.my_attendance, name='api_my_attendance'),

    # ===== RSVP =====
    path('events/<slug:slug>/register/', views.register_event, name='api_register_event'),
    path('rsvp/', views.my_rsvps, name='api_my_rsvps'),
    path('rsvp/<int:rsvp_id>/', views.rsvp_detail, name='api_rsvp_detail'),
    path('rsvp/<int:rsvp_id>/cancel/', views.cancel_rsvp, name='api_cancel_rsvp'),
    path('rsvp/<int:rsvp_id>/update/', views.update_rsvp, name='api_update_rsvp'),

    # ===== Tickets =====
    path('tickets/', views.my_tickets, name='api_my_tickets'),
    path('tickets/<uuid:ticket_id>/', views.ticket_detail, name='api_ticket_detail'),

    # ===== User Profile =====
    path('user/profile/', views.my_profile, name='api_my_profile'),
    path('user/profile/update/', views.update_profile, name='api_update_profile'),
    path('user/<int:user_id>/profile/', views.user_profile, name='api_user_profile'),
    path('organizers/', views.organizers_list, name='api_organizers_list'),

    # ===== Notifications =====
    path('notifications/', views.notifications_list, name='api_notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='api_mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='api_delete_notification'),
    path('notifications/unread-count/', views.unread_notifications_count, name='api_unread_count'),

    # ===== Event Gallery =====
    path('events/<slug:slug>/gallery/', views.event_gallery, name='api_event_gallery'),
    path('events/<slug:slug>/gallery/upload/', views.upload_gallery_image, name='api_upload_gallery_image'),
    path('events/<slug:slug>/gallery/<int:image_id>/delete/', views.delete_gallery_image, name='api_delete_gallery_image'),
]
