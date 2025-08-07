from django.contrib.auth.models import User
from Booking.models import Booking
from datetime import date

def admin_dashboard_stats(request):
    """
    Context processor to provide dashboard statistics for the admin panel.
    """
    if request.path.startswith('/admin/'):
        try:
            total_bookings = Booking.objects.count()
            pending_bookings = Booking.objects.filter(status='Pending').count()
            total_users = User.objects.count()
            todays_bookings = Booking.objects.filter(date=date.today()).count()
            
            return {
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'total_users': total_users,
                'todays_bookings': todays_bookings,
            }
        except Exception:
            # Return default values if there's any error
            return {
                'total_bookings': 0,
                'pending_bookings': 0,
                'total_users': 0,
                'todays_bookings': 0,
            }
    return {}
