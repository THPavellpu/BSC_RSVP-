from django.contrib import admin
from .models import RSVP


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'created_at']
    list_filter = ['status', 'event']
    search_fields = ['user__full_name', 'user__email', 'event__title']
    readonly_fields = ['created_at']
