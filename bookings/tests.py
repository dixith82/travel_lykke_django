from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import TravelOption, Booking

class BookingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'a@example.com', 'pass12345')
        self.trip = TravelOption.objects.create(
            type='BUS',
            source='City A',
            destination='City B',
            departure_datetime=timezone.now() + timezone.timedelta(days=1),
            price=200.00,
            available_seats=10
        )

    def test_create_booking_and_reduce_seats(self):
        self.client.login(username='alice', password='pass12345')
        resp = self.client.post(f'/travel-options/{self.trip.id}/book/', {'number_of_seats': 3})
        self.assertEqual(resp.status_code, 302)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 7)
        b = Booking.objects.get(user=self.user)
        self.assertEqual(float(b.total_price), 600.0)

    def test_cancel_booking_restores_seats(self):
        self.client.login(username='alice', password='pass12345')
        self.client.post(f'/travel-options/{self.trip.id}/book/', {'number_of_seats': 2})
        b = Booking.objects.get(user=self.user)
        self.client.post(f'/bookings/{b.id}/cancel/')
        self.trip.refresh_from_db()
        b.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 10)
        self.assertEqual(b.status, 'CANCELLED')
