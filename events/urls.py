from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('events/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('events/<slug:slug>/delete/', views.delete_event, name='delete_event'),
    path('events/<slug:slug>/gallery/add/', views.add_gallery, name='add_gallery'),
    path('events/<slug:slug>/attendees/', views.event_attendees, name='event_attendees'),
]
