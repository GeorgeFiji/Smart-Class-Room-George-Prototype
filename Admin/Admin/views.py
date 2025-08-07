from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from Booking.profile_forms import ProfilePictureForm
from Booking.profile_models import Profile
from django.contrib.auth.decorators import login_required
from Booking.email_utils import send_welcome_email
from django.contrib import messages
from accounts.forms import CustomUserRegistrationForm

# Home page view
# Only accessible to logged-in users (redirects to /login/ if not authenticated)

from Booking.models import Booking

@login_required(login_url='/login/')
def DashboardView(request):
    user = request.user
    # Booking status counts for donut chart
    pending_count = Booking.objects.filter(user=user, status='pending').count()
    approved_count = Booking.objects.filter(user=user, status='approved').count()
    rejected_count = Booking.objects.filter(user=user, status='rejected').count()
    total_count = Booking.objects.filter(user=user).count()
    return render(request, 'Dashboard.html', {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
        'user': user,
    })

# About page view
# Only accessible to logged-in users (redirects to /login/ if not authenticated)
@login_required(login_url='/login/')
def about(request):
    # Render the about.html template
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email
            if user.email:  # Only send if user has email
                email_sent = send_welcome_email(user)
                if email_sent:
                    messages.success(request, 'Account created successfully! A welcome email has been sent to your email address.')
                else:
                    messages.success(request, 'Account created successfully!')
                    messages.warning(request, 'Welcome email could not be sent. Please check your email address.')
            else:
                messages.success(request, 'Account created successfully!')
                messages.info(request, 'Please add your email address to receive notifications.')
            
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
