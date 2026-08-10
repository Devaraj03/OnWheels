from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Car

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # remember me logic
            if not remember:
                request.session.set_expiry(0)  # expires on browser close

            return redirect("wheels:home")
        else:
            messages.error(request, "Invalid username or password")

    return redirect("wheels:home")

def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("wheels:home")


#####################################################################

@login_required
def profile_view(request):
    user = request.user

    context = {
        "user_obj": user,
    }

    return render(request, "wheels/acc_profile.html", context)

@login_required
def my_reviews(request):
    reviews = request.user.reviews.select_related('car', 'car__brand').all()

    context = {

        "reviews": reviews,
        "review_count": reviews.count(),
    }

    return render(request, "wheels/my_reviews.html", context)

from django.db.models import Q

def get_filtered_cars(request):
    qs = Car.objects.select_related('brand', 'category')\
                    .prefetch_related('images')
    
    sort = request.GET.get('sort')

    # Search by name
    query = request.GET.get('q', '').strip()
    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(brand__name__icontains=query)
        )

    # Filter by fuel
    fuel = request.GET.get('fuel')
    if fuel and fuel != "Fuel":
        qs = qs.filter(fuel_type=fuel)

    # Filter by transmission
    transmission = request.GET.get('transmission')
    if transmission and transmission != "Transmission":
        qs = qs.filter(transmission=transmission)

    #sorting
    if sort == "price_low":
            qs = qs.order_by('price')
    elif sort == "price_high":
        qs = qs.order_by('-price')

    return qs

# @login_required
def home_page(request):
    cars = get_filtered_cars(request)
    return render(request, "wheels/home_page.html", {"cars": cars})


def car_detail(request, id):

    car = get_object_or_404(
        Car.objects.select_related(
            'brand',
            'category'
        ).prefetch_related(
            'images',
            'reviews__user'
        ),
        id=id
    )

    similar_cars = (
        Car.objects
        .filter(category=car.category)
        .exclude(id=car.id)[:3]
    )

    context = {
        "car": car,
        "similar_cars": similar_cars,
    }

    return render(
        request,
        "wheels/car_detail.html",
        context
    )

from .models import Car, Review
from django.contrib import messages

@login_required
def add_review(request, id):

    car = get_object_or_404(Car, id=id)

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.update_or_create(
            user=request.user,
            car=car,
            defaults={
                "rating": rating,
                "comment": comment,
            }
        )

        messages.success(
            request,
            "Review submitted successfully."
        )

    return redirect(
        "wheels:car_detail",
        id=car.id
    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Review


from django.contrib import messages
from django.contrib.auth.models import User

@login_required
def update_profile(request):

    if request.method == "POST":

        username = request.POST.get("username")

        # Check if username already exists
        if User.objects.exclude(id=request.user.id).filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("wheels:profile")

        request.user.username = username

        request.user.first_name = request.POST.get(
            "first_name"
        )

        request.user.last_name = request.POST.get(
            "last_name"
        )

        request.user.email = request.POST.get(
            "email"
        )

        request.user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

    return redirect("wheels:profile")

@login_required
def edit_review(request, id):

    review = get_object_or_404(
        Review,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        review.rating = request.POST.get("rating")

        review.comment = request.POST.get(
            "comment"
        )

        review.save()

    return redirect("wheels:my_reviews")


@login_required
def delete_review(request, id):

    review = get_object_or_404(
        Review,
        id=id,
        user=request.user
    )

    review.delete()

    return redirect("wheels:my_reviews")


from django.contrib.auth.models import User
from django.contrib import messages
import re

def signup_view(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Username exists
        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("wheels:home")

        # Email exists
        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("wheels:home")

        # Password validation
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"

        if not re.match(pattern, password):

            messages.error(
                request,
                "Password must be at least 8 characters and contain uppercase, lowercase, number and special character."
            )

            return redirect("wheels:home")

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(
            request,
            f"Welcome {first_name}!"
        )

        return redirect("wheels:home")

    return redirect("wheels:home")

from django.contrib.admin.views.decorators import user_passes_test
from .models import Car, Brand, Category

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def manage_cars(request):

    context = {
        "cars": Car.objects.select_related(
            "brand",
            "category"
        ),
        "brands": Brand.objects.all(),
        "categories": Category.objects.all(),
    }

    return render(
        request,
        "wheels/manage_cars.html",
        context
    )

from decimal import Decimal, InvalidOperation

def validate_car(request, image_required=True):

    name = request.POST.get("name", "").strip()
    brand = request.POST.get("brand", "").strip()
    category = request.POST.get("category", "").strip()
    price = request.POST.get("price", "").strip()
    fuel_type = request.POST.get("fuel_type", "").strip()
    transmission = request.POST.get("transmission", "").strip()
    engine = request.POST.get("engine", "").strip()
    mileage = request.POST.get("mileage", "").strip()
    seating_capacity = request.POST.get("seating_capacity", "").strip()
    launch_year = request.POST.get("launch_year", "").strip()
    description = request.POST.get("description", "").strip()
    image = request.FILES.get("image")

    # Required validations
    if not name:
        return "Car name is required."

    if not brand:
        return "Please select a brand."

    if not category:
        return "Please select a category."

    if not price:
        return "Price is required."

    if not fuel_type:
        return "Please select fuel type."

    if not transmission:
        return "Please select transmission."

    if not engine:
        return "Engine is required."

    if not mileage:
        return "Mileage is required."

    if not seating_capacity:
        return "Seating capacity is required."

    if not launch_year:
        return "Launch year is required."

    if not description:
        return "Description is required."

    if image_required and not image:
        return "Please upload a car image."

    # Decimal validation
    try:
        Decimal(price)
    except InvalidOperation:
        return "Price must be a valid decimal number."

    try:
        Decimal(mileage)
    except InvalidOperation:
        return "Mileage must be a valid decimal number."

    # Integer validation
    try:
        int(seating_capacity)
    except ValueError:
        return "Seating capacity must be an integer."

    try:
        int(launch_year)
    except ValueError:
        return "Launch year must be an integer."

    return None

from .models import Car, CarImage

@user_passes_test(is_superuser)
def add_car(request):

    if request.method == "POST":
        
        error = validate_car(request, image_required=True)

        if error:
            messages.error(request, error)
            return redirect("wheels:manage_cars")

        car = Car.objects.create(
            name=request.POST.get("name"),
            brand_id=request.POST.get("brand"),
            category_id=request.POST.get("category"),
            price=request.POST.get("price"),
            fuel_type=request.POST.get("fuel_type"),
            transmission=request.POST.get("transmission"),
            engine=request.POST.get("engine"),
            mileage=request.POST.get("mileage"),
            seating_capacity=request.POST.get("seating_capacity"),
            launch_year=request.POST.get("launch_year"),
            description=request.POST.get("description"),
        )

        image = request.FILES.get("image")

        if image:
            CarImage.objects.create(
                car=car,
                image=image,
                is_thumbnail=True
            )

        messages.success(request, "Car added successfully.")

    return redirect("wheels:manage_cars")

@user_passes_test(is_superuser)
def edit_car(request, id):

    car = get_object_or_404(
        Car,
        id=id
    )

    if request.method == "POST":

        error = validate_car(request, image_required=False)

        if error:
            messages.error(request, error)
            return redirect("wheels:manage_cars")

        car.name = request.POST.get("name")
        car.brand_id = request.POST.get("brand")
        car.category_id = request.POST.get("category")
        car.price = request.POST.get("price")
        car.fuel_type = request.POST.get("fuel_type")
        car.transmission = request.POST.get("transmission")
        car.engine = request.POST.get("engine")
        car.mileage = request.POST.get("mileage")
        car.seating_capacity = request.POST.get("seating_capacity")
        car.launch_year = request.POST.get("launch_year")
        car.description = request.POST.get("description")

        image = request.FILES.get("image")

        if image:
            thumb = car.images.filter(is_thumbnail=True).first()

            if thumb:
                thumb.image = image
                thumb.save()
            else:
                CarImage.objects.create(
                    car=car,
                    image=image,
                    is_thumbnail=True
                )

        car.save()
        messages.success(request, "Car updated successfully.")


    return redirect("wheels:manage_cars")


@user_passes_test(is_superuser)
def delete_car(request, id):

    car = get_object_or_404(
        Car,
        id=id
    )

    car.delete()

    return redirect("wheels:manage_cars")

