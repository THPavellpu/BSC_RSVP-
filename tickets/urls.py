from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_tickets, name='my_tickets'),
    path('<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('<uuid:ticket_id>/download/', views.download_ticket, name='download_ticket'),
]
