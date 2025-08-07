from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from accounts.forms import CustomUserRegistrationForm
from Booking.email_utils import send_welcome_email
from Booking.profile_models import Profile
from Booking.profile_forms import ProfilePictureForm
from django.contrib.auth.models import User

from Booking.models import Booking

@login_required(login_url='/login/')
def DashboardView(request):
    user = request.user
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=user)
    
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
        'profile': profile,
    })

@login_required  
def about(request):
    return render(request, 'about.html')

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Save the user
                user = form.save()
                
                # Log the user in automatically with the default backend
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Send welcome email
                email_sent = send_welcome_email(user)
                
                if email_sent:
                    messages.success(request, f'Welcome {user.username}! Your account has been created successfully. A welcome email has been sent to {user.email}.')
                else:
                    messages.warning(request, f'Welcome {user.username}! Your account has been created successfully, but we could not send the welcome email.')
                
                # Redirect to dashboard
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
                print(f"Registration error: {e}")  # Debug print
                
        else:
            # Form has validation errors
            messages.error(request, 'Please correct the errors below.')
            
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    """View user profile"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get booking statistics
    user_bookings = request.user.booking_set.all()
    approved_bookings_count = user_bookings.filter(status='approved').count()
    pending_bookings_count = user_bookings.filter(status='pending').count()
    total_bookings_count = user_bookings.count()
    
    # Get recent bookings (latest 5)
    recent_bookings = user_bookings.order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'approved_bookings_count': approved_bookings_count,
        'pending_bookings_count': pending_bookings_count,
        'total_bookings_count': total_bookings_count,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'profile/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile information"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile picture upload
        profile_form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        
        # Handle user information update
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        if profile_form.is_valid():
            profile_form.save()
            
            # Update user information
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfilePictureForm(instance=profile)
    
    return render(request, 'profile/edit_profile.html', {
        'profile_form': profile_form,
        'profile': profile
    })
