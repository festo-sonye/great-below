from django.db import models
from django.utils import timezone
from shop.models import Product
import random
import string


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('on_the_way', 'On the Way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_code = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    customer_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_code}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self.generate_order_code()
        super().save(*args, **kwargs)

    def generate_order_code(self):
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"CR-{year}-{random_part}"

    def get_status_progress(self):
        status_order = ['pending', 'processing', 'packed', 'on_the_way', 'delivered']
        if self.status == 'cancelled':
            return 0
        try:
            return (status_order.index(self.status) + 1) * 20
        except ValueError:
            return 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        return self.product_price * self.quantity


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order status histories'

    def __str__(self):
        return f"{self.order.order_code} - {self.status}"
