__author__ = 'dbannon'

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime

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
        if(len(self.errors) == 0):  #skip form validation if field validation found errors
            self.validateEndTimeAfterStartTime()
            self.validateInFuture()
            self.validateAcceptableLength()
            self.validateInAcceptableDateRange()
            self.validateNotOverlapping()
        return self.cleaned_data

    def validateNotOverlapping(self):
        '''
        This reservation can't conflict with a previously created reservation
        times can overlap, as long as the reserved boat isn't also the same
        returns nothing, raises ValidationError if it overlaps
        :return:
        '''
        overlappingReservations = Reservation.objects.exclude(end_time__lte=self.cleaned_data.get('start_time')).exclude(start_time__gte=self.cleaned_data.get('end_time'))
        for r in overlappingReservations:
            if(r.boat == self.cleaned_data.get('boat')):
                raise ValidationError( 'This boat is already reserved for this time slot', code="alreadyReserved")

    def validateInAcceptableDateRange(self):
        '''
        Reservations can't start before 9:00 am and can't end after 6:00pm
        raises ValidationError if the start or end time is outside the acceptable range.
        TODO: this should be field-level validation rather than form-level (shouldn't affect functionality)
        :return:
        '''
        if self.cleaned_data.get("start_time").hour < 9:
            raise ValidationError("Your reservation cannot start before 9:00 AM")
        end_time = self.cleaned_data.get("end_time")
        if ((end_time.hour == 18 and end_time.minute > 0) or end_time.hour > 18):
            #this condition is "good enough", not perfect. Should really compare to another datetime, but that's complicated
            raise ValidationError("Your reservation cannot end after 6:00 PM")

    def validateAcceptableLength(self):
        '''
        Raises ValidationError if the reservation is less than 30 min long or more than 4 hours
        :return:
        '''
        length = self.cleaned_data.get("end_time") - self.cleaned_data.get("start_time")
        if(length < timedelta(0, 60*30)):
            raise ValidationError('Reservations cannot be less than 30 minutes long', code="tooShort")
        elif (length > timedelta(0, 60*60*4)):
            raise ValidationError('Reservations cannot be more than 4 hours long', code="tooLong")

    def validateEndTimeAfterStartTime(self):
        '''
        Raises ValidationError if the reservation end time is before the start time
        I think this is done in the front-end but it's best to do it back here too
        :return:
        '''
        if(self.cleaned_data.get("end_time") < self.cleaned_data.get("start_time")):
            raise ValidationError('Reservations cannot end before they start', code="wrongDirection")

    def validateInFuture(self):
        '''
        Raises ValidationError if the reservation start time is before datetime.now()
        This is done in the front-end but it's best to do it back here too
        TODO: this should be field-level validation rather than form-level (shouldn't affect functionality)
        :return:
        '''
        if(self.cleaned_data.get("start_time") < timezone.now()):
            raise ValidationError('Reservations cannot start in the past', code="spaceTimeContinuum")