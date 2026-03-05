from django.urls import path
from . import views

urlpatterns = [
    path('scan/<slug:slug>/', views.scan_qr, name='scan_qr'),
    path('verify/', views.verify_ticket, name='verify_ticket'),
    path('manual-checkin/<slug:slug>/', views.manual_checkin, name='manual_checkin'),
    path('list/<slug:slug>/', views.attendance_list, name='attendance_list'),
]
