from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.Login.as_view(), name='login'),
    path('auth/logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),

    path('travel-options/', views.travel_options, name='travel-options'),
    path('travel-options/<int:pk>/book/', views.book_option, name='book-option'),

    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel-booking'),
]
