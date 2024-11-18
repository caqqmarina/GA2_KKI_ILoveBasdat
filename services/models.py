from django.db import models
from main.models import User, Worker

# Category and Subcategory Models
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    category = models.ForeignKey(ServiceCategory, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# Testimonial Model
class Testimonial(models.Model):
    subcategory = models.ForeignKey(Subcategory, related_name='testimonials', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField()  # Add a rating field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.user.username} for {self.subcategory.name}"

# Service Session Model
class ServiceSession(models.Model):
    subcategory = models.ForeignKey(Subcategory, related_name='sessions', on_delete=models.CASCADE)
    session = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.session} - Rp {self.price}"

# Booking Model
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(ServiceSession, on_delete=models.CASCADE)
    date_booked = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    status = models.CharField(max_length=20, default='Pending')  # Status field for booking

    def __str__(self):
        return f"Booking by {self.user.username} for {self.session.session}"

# Worker Service Model
class WorkerService(models.Model):
    worker = models.ForeignKey(Worker, related_name='services', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='workers', on_delete=models.CASCADE)
    is_joined = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.worker.name} in {self.subcategory.name}"