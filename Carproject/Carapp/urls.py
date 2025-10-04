from django.urls import path, include
from . import views

app_name = 'carapp'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    
    # Company URLs
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    
    # Car URLs
    path('cars/', views.car_list, name='car_list'),  # New view for all cars
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/<int:car_id>/rate/', views.rate_car, name='rate_car'),
    path('cars/<int:car_id>/book/', views.book_car, name='book_car'),
    
    # Search
    path('search/', views.search_cars, name='search_cars'),  # New view for search
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
] 