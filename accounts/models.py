from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"

    @property
    def is_customer(self):
        return self.user_type == 'customer'

    @property
    def is_seller(self):
        return self.user_type == 'seller'

    @property
    def is_admin_user(self):
        return self.user_type == 'admin' or self.is_staff


class SellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller_profile')
    shop_name = models.CharField(max_length=200)
    shop_description = models.TextField(blank=True)
    shop_image = models.ImageField(upload_to='shop_images/', blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    shop_address = models.TextField()
    bank_account = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    mpesa_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Seller Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return self.shop_name
