from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from .models import Category, Company, Car, CarRating, Booking
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def home(request):
    categories = Category.objects.all()
    featured_cars = Car.objects.filter(is_available=True)[:6]
    return render(request, 'carapp/home.html', {
        'categories': categories,
        'featured_cars': featured_cars
    })

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'carapp/category_list.html', {
        'categories': categories
    })

def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    cars = Car.objects.filter(category=category, is_available=True)
    return render(request, 'carapp/category_detail.html', {
        'category': category,
        'cars': cars
    })

def company_list(request):
    companies = Company.objects.all()
    return render(request, 'carapp/company_list.html', {
        'companies': companies
    })

def company_detail(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    cars = Car.objects.filter(company=company, is_available=True)
    return render(request, 'carapp/company_detail.html', {
        'company': company,
        'cars': cars
    })

@login_required
def rate_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            try:
                # Update existing rating or create new one
                car_rating, created = CarRating.objects.update_or_create(
                    car=car,
                    user=request.user,
                    defaults={'rating': rating, 'comment': comment}
                )
                messages.success(request, 'Thank you for your rating!')
            except ValueError:
                messages.error(request, 'Invalid rating value')
        else:
            messages.error(request, 'Rating is required')
            
    return redirect('carapp:car_detail', car_id=car_id)

def car_detail(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = CarRating.objects.filter(car=car, user=request.user).first()
    ratings = car.carrating_set.all().order_by('-created_at')
    
    return render(request, 'carapp/car_detail.html', {
        'car': car,
        'user_rating': user_rating,
        'ratings': ratings
    })

def car_list(request):
    """View for displaying all available cars"""
    cars = Car.objects.filter(is_available=True).order_by('-average_rating')
    return render(request, 'carapp/car_list.html', {
        'cars': cars
    })

def search_cars(request):
    """View for searching cars"""
    query = request.GET.get('q', '')
    cars = []
    
    if query:
        cars = Car.objects.filter(
            Q(name__icontains=query) |
            Q(company__name__icontains=query) |
            Q(category__name__icontains=query)
        ).filter(is_available=True)
    
    return render(request, 'carapp/search_results.html', {
        'cars': cars,
        'query': query
    })

@login_required
def book_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    
    if request.method == 'POST':
        rental_type = request.POST.get('rental_type')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration')
        
        try:
            # Combine date and time
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            
            # Calculate end time based on rental type and duration
            if rental_type == 'HOURLY':
                end_datetime = start_datetime + timezone.timedelta(hours=int(duration))
            elif rental_type == 'DAILY':
                end_datetime = start_datetime + timezone.timedelta(days=int(duration))
            else:  # MONTHLY
                end_datetime = start_datetime + timezone.timedelta(days=int(duration) * 30)
            
            # Check if car is available for the selected period
            conflicting_bookings = Booking.objects.filter(
                car=car,
                status__in=['PENDING', 'CONFIRMED'],
                start_time__lt=end_datetime,
                end_time__gt=start_datetime
            )
            
            if conflicting_bookings.exists():
                messages.error(request, 'Car is not available for the selected time period')
                return redirect('carapp:car_detail', car_id=car.id)
            
            # Create booking
            booking = Booking(
                car=car,
                user=request.user,
                rental_type=rental_type,
                start_time=start_datetime,
                end_time=end_datetime
            )
            booking.save()
            
            messages.success(request, 'Booking request submitted successfully!')
            return redirect('carapp:booking_detail', booking_id=booking.id)
            
        except ValueError as e:
            messages.error(request, 'Invalid date or time format')
            return redirect('carapp:car_detail', car_id=car.id)
    
    return render(request, 'carapp/book_car.html', {
        'car': car
    })

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'carapp/booking_detail.html', {
        'booking': booking
    })

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'carapp/my_bookings.html', {
        'bookings': bookings
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def about(request):
    return render(request, 'carapp/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you can add code to send email or save to database
        
        messages.success(request, 'Thank you for your message. We will get back to you soon!')
        return redirect('carapp:contact')
        
    return render(request, 'carapp/contact.html')
