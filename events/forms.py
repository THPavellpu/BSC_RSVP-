from django import forms
from .models import Event, EventGallery
from django.utils import timezone


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'banner',
            'event_date', 'end_date', 'venue', 'venue_details',
            'max_attendees', 'rsvp_deadline', 'ticket_price',
            'is_free', 'status', 'is_featured', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'venue_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional venue details...'}),
            'max_attendees': forms.NumberInput(attrs={'class': 'form-control'}),
            'rsvp_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag1, tag2, tag3'}),
        }


class EventGalleryForm(forms.ModelForm):
    class Meta:
        model = EventGallery
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (optional)'}),
        }


class EventSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search events...'})
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Event.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status'), ('upcoming', 'Upcoming'), ('ongoing', 'Ongoing'), ('completed', 'Past')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[('date', 'By Date'), ('popularity', 'By Popularity'), ('newest', 'Newest First')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
