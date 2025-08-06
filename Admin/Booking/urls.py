from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.booking_view, name='booking'),
    path('create/', views.create_booking, name='create_booking'),
]