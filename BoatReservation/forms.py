from django.core.exceptions import ValidationError

__author__ = 'dbannon'

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Reservation

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time', 'boat']

    start_time = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'])
    end_time = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'])

    def clean(self):
        overlappingReservations = Reservation.objects.exclude(end_time__lte=self.cleaned_data.get('start_time')).exclude(start_time__gte=self.cleaned_data.get('end_time'))
        for r in overlappingReservations:
            if(r.boat == self.cleaned_data.get('boat')):
                raise ValidationError( 'This boat is already reserved for this time slot', code="alreadyReserved")
        return self.cleaned_data