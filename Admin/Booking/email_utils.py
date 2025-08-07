from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_welcome_email(user):
    """Send welcome email to newly registered user"""
    subject = 'Welcome to Smart Classroom Booking System!'
    
    # Render HTML email template
    html_message = render_to_string('emails/welcome_email.html', {
        'user': user,
        'site_name': 'Smart Classroom Booking System'
    })
    
    # Create plain text version
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False

def send_booking_confirmation_email(booking):
    """Send booking confirmation email to user"""
    subject = f'Booking Confirmation - {booking.purpose}'
    
    html_message = render_to_string('emails/booking_confirmation.html', {
        'booking': booking,
        'user': booking.user,
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending booking confirmation email: {e}")
        return False

def send_booking_status_email(booking):
    """Send email when booking status changes"""
    status_messages = {
        'approved': 'Your booking has been approved!',
        'rejected': 'Your booking has been rejected.',
        'pending': 'Your booking is under review.'
    }
    
    subject = f'Booking {booking.status.title()} - {booking.purpose}'
    
    html_message = render_to_string('emails/booking_status.html', {
        'booking': booking,
        'user': booking.user,
        'status_message': status_messages.get(booking.status, 'Your booking status has been updated.'),
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending booking status email: {e}")
        return False

def send_admin_notification_email(booking):
    """Send notification to admin when new booking is created"""
    subject = f'New Booking Request - {booking.purpose}'
    
    # Get admin users
    from django.contrib.auth.models import User
    admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
    
    if not admin_emails:
        return False
    
    html_message = render_to_string('emails/admin_notification.html', {
        'booking': booking,
        'user': booking.user,
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(admin_emails),
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending admin notification email: {e}")
        return False
