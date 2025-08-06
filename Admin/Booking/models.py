from django.db import models
from django.contrib.auth.models import User

# Only one classroom, so no need for a Classroom model or ForeignKey

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class Booking(models.Model):
    """
    Represents a booking for the single smart classroom.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.CharField(max_length=100)
    attendees = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} | {self.purpose} | {self.start_time:%Y-%m-%d %I:%M %p} - {self.end_time:%I:%M %p}"