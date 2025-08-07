from django.urls import path, include
from django.contrib import admin    
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Define URL patterns for the Django project
urlpatterns = [
    # Django admin interface with custom styling
    path('admin/', admin.site.urls),

    # Home page (requires user to be logged in, see views.py)
    path('', views.DashboardView, name='Dashboard'),
    path('dashboard/', views.DashboardView, name='dashboard'),

    # About page (requires user to be logged in, see views.py)
    path('about/', views.about, name='about'),

    # Django built-in authentication URLs (login, logout, password reset, etc.)
    path('', include('django.contrib.auth.urls')),

    # Registration URL for user registration (see views.py)
    path('register/', views.register, name='register'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Include URLs from the Booking app
    path('booking/', include('Booking.urls')),
    
]

# Customize admin site
admin.site.site_header = "🏫 Smart Classroom Admin Panel"
admin.site.site_title = "Smart Classroom Admin"
admin.site.index_title = "Smart Classroom Administration Dashboard"

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
