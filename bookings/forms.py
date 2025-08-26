from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('number_of_seats',)

    def __init__(self, *args, **kwargs):
        self.travel_option = kwargs.pop('travel_option', None)
        super().__init__(*args, **kwargs)

    def clean_number_of_seats(self):
        seats = self.cleaned_data['number_of_seats']
        if seats <= 0:
            raise forms.ValidationError("Number of seats must be positive.")
        if self.travel_option and seats > self.travel_option.available_seats:
            raise forms.ValidationError("Not enough seats available.")
        return seats
