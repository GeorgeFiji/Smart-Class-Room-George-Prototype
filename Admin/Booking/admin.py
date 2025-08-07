
from django.contrib import admin
from django.contrib import messages
from .models import Booking
from .email_utils import send_booking_status_email

def approve_bookings(modeladmin, request, queryset):
    """Custom admin action to approve bookings and send notification emails"""
    updated = 0
    for booking in queryset:
        if booking.status != 'approved':
            booking.status = 'approved'
            booking.save()
            
            # Send status update email
            if booking.user.email:
                send_booking_status_email(booking)
            
            updated += 1
    
    if updated:
        messages.success(request, f'{updated} booking(s) approved and notification emails sent.')
    else:
        messages.info(request, 'No bookings were updated.')

def reject_bookings(modeladmin, request, queryset):
    """Custom admin action to reject bookings and send notification emails"""
    updated = 0
    for booking in queryset:
        if booking.status != 'rejected':
            booking.status = 'rejected'
            booking.save()
            
            # Send status update email
            if booking.user.email:
                send_booking_status_email(booking)
            
            updated += 1
    
    if updated:
        messages.success(request, f'{updated} booking(s) rejected and notification emails sent.')
    else:
        messages.info(request, 'No bookings were updated.')

approve_bookings.short_description = "✅ Approve selected bookings"
reject_bookings.short_description = "❌ Reject selected bookings"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "start_time", "end_time", "status", "receipt", "created_at")
    list_filter = ("status", "start_time", "user", "created_at")
    search_fields = ("user__username", "user__email", "purpose", "description")
    list_editable = ("status",)
    actions = [approve_bookings, reject_bookings]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'purpose', 'description')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'attendees')
        }),
        ('Status & Receipt', {
            'fields': ('status', 'receipt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        """Override save to send status email when status changes"""
        if change:  # Only for existing objects
            # Get the original object to compare status
            original = Booking.objects.get(pk=obj.pk)
            status_changed = original.status != obj.status
        else:
            status_changed = False
        
        super().save_model(request, obj, form, change)
        
        # Send email if status changed
        if status_changed and obj.user.email:
            email_sent = send_booking_status_email(obj)
            if email_sent:
                messages.success(request, f'Status updated and notification email sent to {obj.user.email}')
            else:
                messages.warning(request, 'Status updated but email notification failed to send')



