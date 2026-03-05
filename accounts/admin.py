from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'registration_number', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'full_name', 'registration_number']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('full_name', 'registration_number', 'role', 'profile_picture', 'phone_number', 'bio', 'department', 'batch_year')}),
    )
