
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Booking
from .profile_models import Profile
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
        messages.success(request, f'✅ {updated} booking(s) approved and notification emails sent.')
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
        messages.success(request, f'❌ {updated} booking(s) rejected and notification emails sent.')
    else:
        messages.info(request, 'No bookings were updated.')

approve_bookings.short_description = "✅ Approve selected bookings"
reject_bookings.short_description = "❌ Reject selected bookings"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("colored_user", "purpose", "formatted_schedule", "colored_status", "attendees_count", "receipt_status", "created_at")
    list_filter = ("status", "start_time", "user", "created_at")
    search_fields = ("user__username", "user__email", "purpose", "description")
    actions = [approve_bookings, reject_bookings]
    date_hierarchy = 'start_time'
    list_per_page = 20
    
    fieldsets = (
        ('📋 Booking Information', {
            'fields': ('user', 'purpose', 'description'),
            'classes': ('wide',)
        }),
        ('⏰ Schedule Details', {
            'fields': ('start_time', 'end_time', 'attendees'),
            'classes': ('wide',)
        }),
        ('📄 Status & Documentation', {
            'fields': ('status', 'receipt'),
            'classes': ('wide',)
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def colored_user(self, obj):
        """Display user with colored badge"""
        return format_html(
            '<span style="background: linear-gradient(135deg, #0E6A6A, #2EC4B6); color: white; padding: 6px 12px; border-radius: 15px; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">{}</span>',
            obj.user.get_full_name() or obj.user.username
        )
    colored_user.short_description = "👤 User"
    colored_user.admin_order_field = 'user__username'
    
    def formatted_schedule(self, obj):
        """Display formatted schedule with icons"""
        return format_html(
            '<div style="font-size: 13px; line-height: 1.4;"><strong style="color: #0E6A6A;">📅 {}</strong><br><span style="color: #666;">🕒 {} - {}</span></div>',
            obj.start_time.strftime("%B %d, %Y"),
            obj.start_time.strftime("%I:%M %p"),
            obj.end_time.strftime("%I:%M %p")
        )
    formatted_schedule.short_description = "📅 Schedule"
    formatted_schedule.admin_order_field = 'start_time'
    
    def colored_status(self, obj):
        """Display status with colored badges"""
        colors = {
            'pending': '#f59e0b',
            'approved': '#10b981',
            'rejected': '#ef4444'
        }
        icons = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 15px; border-radius: 20px; font-weight: bold; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">{} {}</span>',
            colors.get(obj.status, '#6b7280'),
            icons.get(obj.status, '❓'),
            obj.get_status_display()
        )
    colored_status.short_description = "📊 Status"
    colored_status.admin_order_field = 'status'
    
    def attendees_count(self, obj):
        """Display attendees with icon"""
        return format_html(
            '<span style="background: linear-gradient(135deg, #e0f2fe, #b3e5fc); color: #0277bd; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; border: 1px solid #81d4fa;">👥 {}</span>',
            obj.attendees
        )
    attendees_count.short_description = "👥 Attendees"
    attendees_count.admin_order_field = 'attendees'
    
    def receipt_status(self, obj):
        """Display receipt status with icons"""
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank" style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 4px 10px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 11px; text-transform: uppercase; box-shadow: 0 2px 4px rgba(16,185,129,0.3); transition: all 0.3s ease;">📄 View Receipt</a>',
                obj.receipt.url
            )
        else:
            return format_html(
                '<span style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px; text-transform: uppercase; box-shadow: 0 2px 4px rgba(239,68,68,0.3);">❌ No Receipt</span>'
            )
    receipt_status.short_description = "📄 Receipt"
    
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
                messages.success(request, f'✅ Status updated and notification email sent to {obj.user.email}')
            else:
                messages.warning(request, '⚠️ Status updated but email notification failed to send')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'profile_picture_preview', 'user_email', 'date_joined')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('user__date_joined', 'user__is_active')
    readonly_fields = ('profile_picture_preview',)
    
    fieldsets = (
        ('👤 User Information', {
            'fields': ('user',),
            'classes': ('wide',)
        }),
        ('📸 Profile Picture', {
            'fields': ('profile_picture', 'profile_picture_preview'),
            'classes': ('wide',)
        }),
    )
    
    def user_info(self, obj):
        """Display user info with styling"""
        full_name = obj.user.get_full_name()
        username = obj.user.username
        display_name = full_name if full_name else username
        
        return format_html(
            '<div style="line-height: 1.4;"><strong style="color: #0E6A6A; font-size: 14px;">{}</strong><br><small style="color: #666; font-size: 12px;">@{}</small></div>',
            display_name,
            username
        )
    user_info.short_description = "👤 User"
    user_info.admin_order_field = 'user__username'
    
    def profile_picture_preview(self, obj):
        """Display profile picture preview"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 3px solid #0E6A6A; box-shadow: 0 3px 10px rgba(14,106,106,0.3);" />',
                obj.profile_picture.url
            )
        else:
            return format_html(
                '<div style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #0E6A6A, #2EC4B6); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px; box-shadow: 0 3px 10px rgba(14,106,106,0.3);">{}</div>',
                obj.user.get_full_name().split()[0][0].upper() if obj.user.get_full_name() else obj.user.username[0].upper()
            )
    profile_picture_preview.short_description = "📸 Preview"
    
    def user_email(self, obj):
        """Display user email with styling"""
        return format_html(
            '<span style="color: #0E6A6A; font-weight: 500;">{}</span>',
            obj.user.email
        )
    user_email.short_description = "📧 Email"
    user_email.admin_order_field = 'user__email'
    
    def date_joined(self, obj):
        """Display join date with styling"""
        return format_html(
            '<span style="background: linear-gradient(135deg, #e0f2fe, #b3e5fc); color: #0277bd; padding: 4px 8px; border-radius: 10px; font-size: 12px; font-weight: 500;">{}</span>',
            obj.user.date_joined.strftime("%B %d, %Y")
        )
    date_joined.short_description = "📅 Joined"
    date_joined.admin_order_field = 'user__date_joined'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }



