# from django.db import models
# from main.models import User, Worker

# # Category and Subcategory Models
# class ServiceCategory(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()

#     def __str__(self):
#         return self.name

# class Subcategory(models.Model):
#     category = models.ForeignKey(ServiceCategory, related_name='subcategories', on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     description = models.TextField()

#     def __str__(self):
#         return self.name

# # Testimonial Model
# class Testimonial(models.Model):
#     subcategory = models.ForeignKey(Subcategory, related_name='testimonials', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     rating = models.PositiveSmallIntegerField(default=5)  # Add a default value for rating
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Testimonial by {self.user.username} for {self.subcategory.name}"

# # Service Session Model
# class ServiceSession(models.Model):
#     subcategory = models.ForeignKey(Subcategory, related_name='sessions', on_delete=models.CASCADE)
#     session = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.session} - Rp {self.price}"

# # Booking Model
# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     session = models.ForeignKey(ServiceSession, on_delete=models.CASCADE)
#     date_booked = models.DateTimeField(auto_now_add=True)
#     details = models.TextField()
#     status = models.CharField(max_length=20, default='Pending')  # Status field for booking

#     def __str__(self):
#         return f"Booking by {self.user.username} for {self.session.session}"

# # Worker Service Model
# class WorkerService(models.Model):
#     worker = models.ForeignKey(Worker, related_name='services', on_delete=models.CASCADE)
#     subcategory = models.ForeignKey(Subcategory, related_name='workers', on_delete=models.CASCADE)
#     is_joined = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.worker.name} in {self.subcategory.name}"

# class ServiceOrder(models.Model):
#     STATUS_CHOICES = [
#         ('waiting_for_departure', 'Waiting for Worker to Depart'),
#         ('arrived_at_location', 'Worker Arrived at Location'),
#         ('service_in_progress', 'Service in Progress'),
#         ('order_completed', 'Order Completed'),
#         ('order_canceled', 'Order Canceled'),
#     ]

#     order_name = models.CharField(max_length=100)
#     status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='waiting_for_departure')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.order_name

# class WorkerServiceOrder(models.Model):
#     STATUS_CHOICES = [
#         ('looking_for_worker', 'Looking for Nearby Worker'),
#         ('worker_assigned', 'Waiting for Worker'),
#         ('in_progress', 'Service in Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled')
#     ]

#     subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
#     session = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='looking_for_worker')
#     workers = models.ManyToManyField(Worker, related_name='available_orders')
#     assigned_worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def get_status_display(self):
#         return dict(self.STATUS_CHOICES)[self.status]

#     def __str__(self):
#         return f"Order #{self.id} - {self.subcategory.name} - {self.get_status_display()}"