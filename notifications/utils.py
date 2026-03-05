from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def create_notification(user, notification_type, title, message, link=''):
    from .models import Notification
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )


def notify_rsvp_confirmed(user, event, ticket=None):
    title = f"RSVP Confirmed: {event.title}"
    message = f"Your registration for {event.title} on {event.event_date.strftime('%B %d, %Y')} has been confirmed!"
    link = f"/tickets/"
    
    notification = None
    try:
        notification = create_notification(user, 'rsvp_confirmed', title, message, link)
    except Exception as e:
        print(f"Notification creation error: {e}")

    # Send email
    try:
        send_mail(
            subject=f"[LPU BSC] RSVP Confirmed - {event.title}",
            message=f"Hi {user.full_name},\n\n{message}\n\nVenue: {event.venue}\n\nSee you there!\n\nLPU Bangladesh Students Community",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email sending error: {e}")

    return notification


def notify_event_update(event):
    from rsvp.models import RSVP
    rsvps = RSVP.objects.filter(event=event, status='confirmed').select_related('user')
    for rsvp in rsvps:
        create_notification(
            rsvp.user,
            'event_updated',
            f"Event Updated: {event.title}",
            f"The event '{event.title}' has been updated. Please check the latest details.",
            link=f"/events/{event.slug}/",
        )
        try:
            send_mail(
                subject=f"[LPU BSC] Event Updated - {event.title}",
                message=f"Hi {rsvp.user.full_name},\n\nThe event '{event.title}' has been updated.\n\nPlease check the event page for the latest details.\n\nLPU Bangladesh Students Community",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[rsvp.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
