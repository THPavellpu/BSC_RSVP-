from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'checked_in_at', 'checked_in_by']
    list_filter = ['status', 'event']
    search_fields = ['user__full_name', 'user__email', 'event__title']
    readonly_fields = ['checked_in_at']
