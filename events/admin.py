from django.contrib import admin
from .models import Event, EventGallery


class EventGalleryInline(admin.TabularInline):
    model = EventGallery
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'event_date', 'max_attendees', 'confirmed_count', 'organizer']
    list_filter = ['status', 'category', 'is_featured']
    search_fields = ['title', 'venue', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EventGalleryInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EventGallery)
class EventGalleryAdmin(admin.ModelAdmin):
    list_display = ['event', 'caption', 'uploaded_by', 'uploaded_at']
    list_filter = ['event']
