from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-xl focus:ring-2 focus:ring-[#2EC4B6] focus:border-[#0E6A6A] bg-blue-50/30 placeholder-gray-400',
            'placeholder': 'Your email address'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add styling to all form fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-xl focus:ring-2 focus:ring-[#2EC4B6] focus:border-[#0E6A6A] bg-blue-50/30 placeholder-gray-400',
            'placeholder': 'Your username'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-xl focus:ring-2 focus:ring-[#2EC4B6] focus:border-[#0E6A6A] bg-blue-50/30 placeholder-gray-400',
            'placeholder': '••••••••'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-xl focus:ring-2 focus:ring-[#2EC4B6] focus:border-[#0E6A6A] bg-blue-50/30 placeholder-gray-400',
            'placeholder': '••••••••'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
