from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('accounts/', include('accounts.urls')),
    path('rsvp/', include('rsvp.urls')),
    path('tickets/', include('tickets.urls')),
    path('attendance/', include('attendance.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('accounts.dashboard_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
