from django import forms
from .models import Booking
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    # Create a list of available time slots (one-hour slots)
    TIME_SLOT_CHOICES = [
        ('08:00', '8:00 AM - 9:00 AM'),
        ('09:00', '9:00 AM - 10:00 AM'),
        ('10:00', '10:00 AM - 11:00 AM'),
        ('11:00', '11:00 AM - 12:00 PM'),
        ('12:00', '12:00 PM - 1:00 PM'),
        ('13:00', '1:00 PM - 2:00 PM'),
        ('14:00', '2:00 PM - 3:00 PM'),
        ('15:00', '3:00 PM - 4:00 PM'),
        ('16:00', '4:00 PM - 5:00 PM'),
        ('17:00', '5:00 PM - 6:00 PM'),
    ]
    
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]'
        }),
        label='Booking Date'
    )
    
    time_slot = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]'
        }),
        label='Time Slot (1 Hour Duration)'
    )

    class Meta:
        model = Booking
        fields = ['booking_date', 'time_slot', 'purpose', 'attendees', 'description']
        widgets = {
            'purpose': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]',
                'placeholder': 'e.g., Team Meeting, Workshop, Presentation'
            }),
            'attendees': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]',
                'min': '1',
                'max': '50'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]',
                'rows': '3',
                'placeholder': 'Additional details about your booking...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        time_slot = cleaned_data.get('time_slot')
        
        if booking_date and time_slot:
            # Convert date and time slot into datetime objects
            start_hour = int(time_slot.split(':')[0])
            start_time = datetime.combine(booking_date, datetime.min.time().replace(hour=start_hour))
            end_time = start_time + timedelta(hours=1)
            
            # Check if booking is in the past
            if start_time < datetime.now():
                raise forms.ValidationError("You cannot book a time slot in the past.")
            
            # Store the calculated datetime fields
            cleaned_data['start_time'] = start_time
            cleaned_data['end_time'] = end_time
            
            # Check for conflicts with existing bookings
            existing_bookings = Booking.objects.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=['pending', 'approved']
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_bookings.exists():
                raise forms.ValidationError(
                    f"This time slot is already booked. Please choose a different time."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the start_time and end_time from cleaned data
        if hasattr(self, 'cleaned_data'):
            instance.start_time = self.cleaned_data.get('start_time')
            instance.end_time = self.cleaned_data.get('end_time')
        
        if commit:
            instance.save()
        return instance
