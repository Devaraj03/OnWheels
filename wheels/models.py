from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
# BRAND MODEL

class Brand(models.Model):
    name = models.CharField(max_length=100,unique=True)
    logo = models.ImageField(upload_to='brands/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name

# Car Model
class Car(models.Model):
    FUEL_CHOICES =[
        ('Petrol','Petrol'),
        ('Diesel','Diesel'),
        ('Electric','Electric'),
    ]

    TRANSMISSION_CHOICES =[
        ('Manual','Manual'),
        ('Automatic','Automatic'),
    ]

    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='cars')
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='cars')
    price = models.DecimalField(max_digits=10,decimal_places=2)
    fuel_type = models.CharField(max_length=20,choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20,choices=TRANSMISSION_CHOICES)
    engine = models.CharField(max_length=50)
    mileage = models.DecimalField(max_digits=5, decimal_places=2)
    seating_capacity = models.IntegerField()
    launch_year = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['brand']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['fuel_type']),
        ]

    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    def thumbnail(self):
        thumb = self.images.filter(is_thumbnail=True).first()
        return thumb or self.images.first()
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/')
    is_thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.car.name} Image"

# Review Model

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    car = models.ForeignKey(Car,on_delete=models.CASCADE,related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'car'], name='unique_user_car_review')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.car.name}"