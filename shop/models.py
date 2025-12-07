from django.db import models
from django.urls import reverse
from accounts.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products', null=True, blank=True, limit_choices_to={'user_type': 'seller'})
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/')
    colors = models.CharField(max_length=200, blank=True, help_text='Comma-separated colors')
    sizes = models.CharField(max_length=200, blank=True, help_text='Comma-separated sizes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def in_stock(self):
        return self.stock > 0

    def get_colors_list(self):
        if self.colors:
            return [c.strip() for c in self.colors.split(',')]
        return []

    def get_sizes_list(self):
        if self.sizes:
            return [s.strip() for s in self.sizes.split(',')]
        return []


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Image for {self.product.name}'


class SellerReview(models.Model):
    RATING_CHOICES = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews', limit_choices_to={'user_type': 'seller'})
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='seller_reviews_given', limit_choices_to={'user_type': 'customer'})
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('seller', 'customer', 'order')

    def __str__(self):
        return f'{self.get_rating_display()} - {self.seller.get_full_name()}'

    @property
    def rating_stars(self):
        return '⭐' * self.rating

        return f"Image for {self.product.name}"
