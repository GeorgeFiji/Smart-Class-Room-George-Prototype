from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address to receive notifications.',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply custom CSS classes to all fields
        for field_name in self.fields:
            if field_name not in ['email', 'first_name', 'last_name']:  # These already have custom widgets
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0E6A6A] focus:border-[#0E6A6A]'
                })
        
        # Custom placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
