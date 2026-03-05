from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'user', 'event', 'status', 'created_at']
    list_filter = ['status', 'event']
    search_fields = ['user__full_name', 'user__email', 'event__title', 'ticket_id']
    readonly_fields = ['ticket_id', 'created_at']
