from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User as DjangoUser
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import UserRegistrationForm, LoginForm, UserProfileForm, PasswordResetEmailForm, CustomPasswordSetForm
from .models import User
from events.models import Event
from rsvp.models import RSVP
from tickets.models import Ticket
from attendance.models import Attendance
from notifications.models import Notification


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to LPU BSC, {user.full_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            messages.success(request, f'Welcome back, {user.full_name}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    user = request.user
    rsvps = RSVP.objects.filter(user=user).select_related('event').order_by('-created_at')
    tickets = Ticket.objects.filter(user=user).select_related('event').order_by('-created_at')
    attendances = Attendance.objects.filter(user=user).select_related('event').order_by('-checked_in_at')
    return render(request, 'accounts/profile.html', {
        'user': user,
        'rsvps': rsvps,
        'tickets': tickets,
        'attendances': attendances,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    if user.is_organizer:
        return redirect('organizer_dashboard')
    # Student dashboard
    rsvps = RSVP.objects.filter(user=user).select_related('event').order_by('-created_at')[:5]
    tickets = Ticket.objects.filter(user=user).select_related('event').order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(status='upcoming').order_by('event_date')[:6]
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
    total_events_attended = Attendance.objects.filter(user=user).count()
    return render(request, 'accounts/dashboard.html', {
        'rsvps': rsvps,
        'tickets': tickets,
        'upcoming_events': upcoming_events,
        'notifications': notifications,
        'total_events_attended': total_events_attended,
    })


@login_required
def organizer_dashboard(request):
    if not request.user.is_organizer:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    user = request.user
    if user.is_admin:
        events = Event.objects.all().order_by('-created_at')
    else:
        events = Event.objects.filter(organizer=user).order_by('-created_at')

    total_users = User.objects.filter(role='student').count()
    total_events = events.count()
    total_rsvps = RSVP.objects.filter(event__in=events).count()
    total_attendances = Attendance.objects.filter(event__in=events).count()

    events_data = []
    for event in events[:10]:
        rsvp_count = RSVP.objects.filter(event=event).count()
        attendance_count = Attendance.objects.filter(event=event).count()
        events_data.append({
            'event': event,
            'rsvp_count': rsvp_count,
            'attendance_count': attendance_count,
            'remaining_seats': max(0, event.max_attendees - rsvp_count),
        })

    return render(request, 'accounts/organizer_dashboard.html', {
        'events_data': events_data,
        'total_users': total_users,
        'total_events': total_events,
        'total_rsvps': total_rsvps,
        'total_attendances': total_attendances,
        'all_events': events,
    })


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetEmailForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    html_email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password-reset-done')
    
    def form_valid(self, form):
        messages.info(self, 'If an account with that email exists, you will receive a password reset link shortly.')
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordSetForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password-reset-complete')
    
    def form_valid(self, form):
        messages.success(self, 'Your password has been reset successfully! You can now log in with your new password.')
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
