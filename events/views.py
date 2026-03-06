from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Event, EventGallery
from .forms import EventForm, EventGalleryForm, BulkEventGalleryForm, EventSearchForm
from rsvp.models import RSVP


def home(request):
    featured_events = Event.objects.filter(is_featured=True, status='upcoming').order_by('event_date')[:3]
    upcoming_events = Event.objects.filter(status='upcoming').order_by('event_date')[:6]
    ongoing_events = Event.objects.filter(status='ongoing').order_by('event_date')[:3]
    past_events = Event.objects.filter(status='completed').order_by('-event_date')[:4]
    total_events = Event.objects.count()
    total_members = 0
    try:
        from accounts.models import User
        total_members = User.objects.filter(role='student').count()
    except:
        pass
    return render(request, 'events/home.html', {
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
        'past_events': past_events,
        'total_events': total_events,
        'total_members': total_members,
    })


def event_list(request):
    events = Event.objects.exclude(status='draft')
    form = EventSearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        sort = form.cleaned_data.get('sort')
        if q:
            events = events.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q))
        if category:
            events = events.filter(category=category)
        if status:
            events = events.filter(status=status)
        if sort == 'popularity':
            events = events.annotate(rsvp_count=Count('rsvps')).order_by('-rsvp_count')
        elif sort == 'newest':
            events = events.order_by('-created_at')
        else:
            events = events.order_by('event_date')

    paginator = Paginator(events, 9)
    page = request.GET.get('page', 1)
    events_page = paginator.get_page(page)

    return render(request, 'events/event_list.html', {
        'events': events_page,
        'form': form,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    gallery = event.gallery_images.all()[:12]
    user_rsvp = None
    user_ticket = None
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
        if user_rsvp:
            from tickets.models import Ticket
            user_ticket = Ticket.objects.filter(user=request.user, event=event).first()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'gallery': gallery,
        'user_rsvp': user_rsvp,
        'user_ticket': user_ticket,
        'now': timezone.now(),
    })


@login_required
def create_event(request):
    if not request.user.is_organizer:
        messages.error(request, 'You do not have permission to create events.')
        return redirect('event_list')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', slug=event.slug)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


@login_required
def edit_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if not request.user.is_admin and event.organizer != request.user:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('event_detail', slug=slug)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            # Notify registered users about event update
            from notifications.utils import notify_event_update
            notify_event_update(event)
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', slug=slug)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Edit', 'event': event})


@login_required
def delete_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if not request.user.is_admin and event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('event_detail', slug=slug)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
        return redirect('event_list')
    return render(request, 'events/confirm_delete.html', {'event': event})


@login_required
def add_gallery(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if not request.user.is_admin and event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('event_detail', slug=slug)
    
    # Check if event has ended
    if timezone.now() < event.event_date:
        messages.error(request, 'Photos can only be uploaded after the event date. Please try again after ' + event.event_date.strftime('%B %d, %Y'))
        return redirect('event_detail', slug=slug)
    
    if request.method == 'POST':
        form = BulkEventGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            caption = form.cleaned_data.get('caption', '')
            
            if not images:
                messages.error(request, 'Please select at least one image.')
                return redirect('add_gallery', slug=slug)
            
            uploaded_count = 0
            for image in images:
                try:
                    gallery_item = EventGallery(
                        event=event,
                        image=image,
                        caption=caption,
                        uploaded_by=request.user
                    )
                    gallery_item.save()
                    uploaded_count += 1
                except Exception as e:
                    messages.warning(request, f'Failed to upload {image.name}: {str(e)}')
                    pass
            
            if uploaded_count > 0:
                messages.success(request, f'Successfully uploaded {uploaded_count} photo(s) to gallery!')
            return redirect('event_gallery', slug=slug)
    else:
        form = BulkEventGalleryForm()
    
    return render(request, 'events/add_gallery.html', {
        'form': form,
        'event': event,
        'is_bulk_upload': True
    })


def event_gallery(request, slug):
    """Display full gallery for an event - public view"""
    event = get_object_or_404(Event, slug=slug)
    gallery_images = event.gallery_images.all().order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(gallery_images, 12)  # 12 images per page
    page = request.GET.get('page', 1)
    images_page = paginator.get_page(page)
    
    # Check if user is organizer
    is_organizer = request.user.is_authenticated and (request.user == event.organizer or request.user.is_admin)
    
    return render(request, 'events/event_gallery.html', {
        'event': event,
        'images': images_page,
        'is_organizer': is_organizer,
        'total_images': gallery_images.count(),
    })


@login_required
def delete_gallery_image(request, image_id):
    """Delete a gallery image - organizers only"""
    image = get_object_or_404(EventGallery, id=image_id)
    event = image.event
    
    # Check permission
    if not request.user.is_admin and event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('event_gallery', slug=event.slug)
    
    if request.method == 'POST':
        try:
            # Delete the image file from storage
            if image.image:
                from django.core.files.storage import default_storage
                if default_storage.exists(str(image.image)):
                    default_storage.delete(str(image.image))
            
            image.delete()
            messages.success(request, 'Photo deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting photo: {str(e)}')
    
    return redirect('event_gallery', slug=event.slug)


@login_required
def event_attendees(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if not request.user.is_admin and event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('event_detail', slug=slug)
    confirmed_rsvps = event.rsvps.filter(status='confirmed').select_related('user')
    waitlisted_rsvps = event.rsvps.filter(status='waitlisted').select_related('user')
    checked_in = event.attendances.filter(status='checked_in').select_related('user')
    return render(request, 'events/attendees.html', {
        'event': event,
        'confirmed_rsvps': confirmed_rsvps,
        'waitlisted_rsvps': waitlisted_rsvps,
        'checked_in': checked_in,
    })
