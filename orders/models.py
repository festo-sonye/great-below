from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from shop.models import Product
import random
import string

User = get_user_model()


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
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    customer_address = models.TextField()
    customer_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    customer_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-PESA'),
        ('cash', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    
    # Deposit (20%)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_paid = models.BooleanField(default=False)
    deposit_payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    deposit_paid_date = models.DateTimeField(null=True, blank=True)
    deposit_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Remaining balance (80%)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_paid = models.BooleanField(default=False)
    balance_payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    balance_paid_date = models.DateTimeField(null=True, blank=True)
    balance_transaction_id = models.CharField(max_length=100, blank=True)
    
    # M-PESA fields
    checkout_request_id = models.CharField(max_length=100, blank=True)
    
    # Payment status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for {self.order.order_code}"

    def save(self, *args, **kwargs):
        # Auto-calculate deposit (20%) and balance (80%) based on order total
        if not self.deposit_amount:
            self.deposit_amount = self.order.total_amount * 0.20
        if not self.balance_amount:
            self.balance_amount = self.order.total_amount * 0.80
        super().save(*args, **kwargs)

    @property
    def total_paid(self):
        """Get total amount paid so far"""
        total = 0
        if self.deposit_paid:
            total += self.deposit_amount
        if self.balance_paid:
            total += self.balance_amount
        return total

    @property
    def is_fully_paid(self):
        """Check if order is fully paid"""
        return self.deposit_paid and self.balance_paid

    @property
    def remaining_balance(self):
        """Get remaining amount to be paid"""
        return self.order.total_amount - self.total_paid


class DeliveryConfirmation(models.Model):
    """Track delivery confirmation by customer"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_confirmation')
    customer_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmation_note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-confirmed_at']
    
    def __str__(self):
        return f"Delivery Confirmation - {self.order.order_code}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('delivery_pending', 'Delivery Pending Confirmation'),
        ('review_request', 'Review Request'),
        ('message', 'New Message'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
