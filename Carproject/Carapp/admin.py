from django.contrib import admin
from .models import Category, Company, Car, CarRating, Booking

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'category', 'model_year', 'hourly_rate', 'is_available', 'average_rating']
    list_filter = ['company', 'category', 'is_available']
    search_fields = ['name', 'company__name', 'category__name']
    readonly_fields = ['average_rating', 'total_ratings']

@admin.register(CarRating)
class CarRatingAdmin(admin.ModelAdmin):
    list_display = ['car', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['car__name', 'user__username']
    readonly_fields = ['created_at']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['car', 'user', 'rental_type', 'start_time', 'end_time', 'status', 'total_amount']
    list_filter = ['status', 'rental_type', 'booking_date']
    search_fields = ['car__name', 'user__username']
    readonly_fields = ['booking_date', 'total_amount']
