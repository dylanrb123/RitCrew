from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail

from BoatReservation.forms import UserCreateForm, ReservationForm
from .models import Reservation, Boat



def create_user(request):
    return redirect('home')

def home(request):
    template = 'home.html'
    create_account_form = UserCreateForm()
    login_form = AuthenticationForm()
    reservation_form = ReservationForm()
    if request.POST:
        if 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('home')
            else:
                request.session['js_inject'] = "$('#login-modal').modal('show');"
        elif 'create_account' in request.POST:
            create_account_form = UserCreateForm(request.POST)
            if create_account_form.is_valid():
                user = create_account_form.save()
                user.save()
                new_user = authenticate(username=request.POST['username'], password=request.POST['password1'])
                login(request, new_user)
                return redirect('home')
            else:
                request.session['js_inject'] = "$('#create-account-modal').modal('show');"
        elif 'logout' in request.POST:
            logout(request)
        elif 'reservation' in request.POST:
            reservation_form = ReservationForm(request.POST)
            if reservation_form.is_valid():
                user = request.user
                if user.is_authenticated():
                    reservation = reservation_form.save(commit=False)
                    reservation.user = request.user
                    reservation.save()
                    boat = Boat.objects.get(name=request.POST['boat'])
                    message = 'Reservation Details:\n'
                    message += 'Start time: ' + request.POST['start_time'] + '\n'
                    message += 'End time: ' + request.POST['end_time'] + '\n'
                    message += 'Boat reserved: ' + str(boat) + '\n'
                    send_mail('Boat Reservation Confirmation', message, 'dylan@dylanbannon.com', [request.user.email, 'dylan@dylanbannon.com'])
                    return redirect('home')
                else:
                    messages.error(request, "You must be logged in to make a reservation.")
            else:
                request.session['js_inject'] = "$('#reservation-modal').modal('show');"
    js_inject = request.session.pop('js_inject') if 'js_inject' in request.session else ''
    reservations = Reservation.objects.all()
    context = {'login_form': login_form, 'create_account_form': create_account_form, 'reservation_form': reservation_form, 'js_inject': js_inject,
               'reservations': reservations}
    return render(request, template, context)

def index(request):
    return render(request, 'index.html')
