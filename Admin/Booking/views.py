from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Booking
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .email_utils import send_booking_confirmation_email, send_admin_notification_email
from django.contrib import messages

def booking_view(request):
    # Show all bookings for the week in the calendar
    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    day_dates = [( (start + timedelta(days=i)).strftime('%A'), (start + timedelta(days=i)).strftime('%Y-%m-%d') ) for i in range(7)]
    hours = list(range(7, 23))  # 7AM to 10PM
    # Only show bookings for this week
    week_start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    bookings = Booking.objects.filter(start_time__gte=week_start, start_time__lt=week_end)
    # Define a color palette
    color_palette = [
        "from-green-400/95 to-green-600/95",
        "from-blue-400/95 to-blue-600/95",
        "from-cyan-400/95 to-cyan-600/95",
        "from-teal-400/95 to-teal-600/95",
        "from-indigo-400/95 to-indigo-600/95",
        "from-pink-400/95 to-pink-600/95",
        "from-yellow-400/95 to-yellow-500/95",
        "from-purple-400/95 to-purple-600/95",
        "from-rose-400/95 to-rose-600/95",
        "from-orange-400/95 to-orange-600/95",
    ]
    # Assign a color to each user
    user_ids = list(User.objects.values_list('id', flat=True).order_by('id'))
    user_color_map = {}
    for idx, user_id in enumerate(user_ids):
        user_color_map[user_id] = color_palette[idx % len(color_palette)]
    # Pass user_color_map to template
    return render(request, 'booking.html', {
        'bookings': bookings,
        'hours': hours,
        'day_dates': day_dates,
        'user_color_map': user_color_map,
    })


@login_required
def create_booking(request):
    # Pre-fill form if slot info is passed
    initial = {}
    day = request.GET.get('day')
    date = request.GET.get('date')
    hour = request.GET.get('hour')
    if date and hour:
        # Try to build a start_time from date and hour
        try:
            start_time = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H")
            end_time = start_time.replace(hour=start_time.hour+1)
            initial['start_time'] = start_time
            initial['end_time'] = end_time
        except Exception:
            pass
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = 'pending'
            
            # Handle receipt upload
            if 'receipt' in request.FILES:
                booking.receipt = request.FILES['receipt']
            
            booking.save()
            
            # Send confirmation email to user
            if request.user.email:
                email_sent = send_booking_confirmation_email(booking)
                if email_sent:
                    messages.success(request, 'Booking created successfully! A confirmation email has been sent.')
                else:
                    messages.success(request, 'Booking created successfully!')
                    messages.warning(request, 'Confirmation email could not be sent.')
            else:
                messages.success(request, 'Booking created successfully!')
                messages.info(request, 'Add your email address to receive booking notifications.')
            
            # Send notification email to admins
            send_admin_notification_email(booking)
            
            return redirect('booking')
    else:
        form = BookingForm(initial=initial)
    return render(request, 'create_booking.html', {'form': form})