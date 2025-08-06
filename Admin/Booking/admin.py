
from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "start_time", "end_time", "status", "receipt")
    list_filter = ("status", "start_time", "user")
    search_fields = ("user__username", "purpose", "description")



