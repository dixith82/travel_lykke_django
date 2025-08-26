from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, ProfileForm, BookingForm
from .models import TravelOption, Booking

def home(request):
    return redirect('travel-options')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'bookings/register.html', {'form': form})

class Login(LoginView):
    template_name = 'bookings/login.html'

class Logout(LogoutView):
    pass

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'bookings/profile.html', {'form': form})

def travel_options(request):
    q = TravelOption.objects.all().order_by('departure_datetime')
    t = request.GET.get('type', '').upper()
    src = request.GET.get('source', '')
    dst = request.GET.get('destination', '')
    date = request.GET.get('date', '')

    if t in ['FLIGHT','TRAIN','BUS']:
        q = q.filter(type=t)
    if src:
        q = q.filter(source__icontains=src)
    if dst:
        q = q.filter(destination__icontains=dst)
    if date:
        from datetime import datetime
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            q = q.filter(departure_datetime__date=d)
        except ValueError:
            messages.warning(request, "Invalid date format. Use YYYY-MM-DD.")

    return render(request, 'bookings/travel_options_list.html', {'options': q})

@login_required
def book_option(request, pk):
    with transaction.atomic():
        travel = TravelOption.objects.select_for_update().get(pk=pk)
        if request.method == 'POST':
            form = BookingForm(request.POST, travel_option=travel)
            if form.is_valid():
                seats = form.cleaned_data['number_of_seats']
                if seats > travel.available_seats:
                    messages.error(request, "Not enough seats available.")
                    return redirect('travel-options')
                total = seats * float(travel.price)
                booking = Booking.objects.create(
                    user=request.user,
                    travel_option=travel,
                    number_of_seats=seats,
                    total_price=total,
                    status='CONFIRMED',
                )
                travel.available_seats -= seats
                travel.save()
                messages.success(request, f"Booking confirmed! ID: {booking.id}")
                return redirect('my-bookings')
        else:
            form = BookingForm(travel_option=travel)
        return render(request, 'bookings/booking_form.html', {'travel': travel, 'form': form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

@login_required
def cancel_booking(request, pk):
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update(), pk=pk, user=request.user)
        if booking.status == 'CONFIRMED':
            booking.status = 'CANCELLED'
            booking.save()
            travel = booking.travel_option
            travel.available_seats += booking.number_of_seats
            travel.save()
            messages.info(request, "Booking cancelled and seats released.")
        else:
            messages.warning(request, "Booking already cancelled.")
    return redirect('my-bookings')
