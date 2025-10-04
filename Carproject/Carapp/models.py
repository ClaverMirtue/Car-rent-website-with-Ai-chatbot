from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"

class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('AUTO', 'Automatic'),
        ('MANUAL', 'Manual'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    model_year = models.IntegerField()
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    seats = models.IntegerField()
    
    # Charges
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Images
    image1 = models.ImageField(upload_to='car_images/')
    image2 = models.ImageField(upload_to='car_images/', blank=True)
    image3 = models.ImageField(upload_to='car_images/', blank=True)
    
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    
    # Add average rating field
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_ratings = models.IntegerField(default=0)
    
    def update_rating(self):
        ratings = self.carrating_set.all()
        if ratings:
            self.average_rating = sum(rating.rating for rating in ratings) / len(ratings)
            self.total_ratings = len(ratings)
        else:
            self.average_rating = 0
            self.total_ratings = 0
        self.save()
    
    def __str__(self):
        return f"{self.company.name} {self.name} ({self.model_year})"

class CarRating(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('car', 'user')  # One rating per user per car
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.car.update_rating()

class Booking(models.Model):
    BOOKING_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    RENTAL_TYPE = [
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('MONTHLY', 'Monthly'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_type = models.CharField(max_length=10, choices=RENTAL_TYPE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=BOOKING_STATUS, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.car.name} ({self.start_time.date()})"
    
    def calculate_total_amount(self):
        duration = self.end_time - self.start_time
        
        if self.rental_type == 'HOURLY':
            hours = duration.total_seconds() / 3600
            return self.car.hourly_rate * hours
        elif self.rental_type == 'DAILY':
            days = duration.days + (duration.seconds > 0)
            return self.car.daily_rate * days
        else:  # MONTHLY
            months = (duration.days // 30) + (duration.days % 30 > 0)
            return self.car.monthly_rate * months
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)
