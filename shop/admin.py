from django.contrib import admin
from .models import Category, Product, ProductImage, SellerReview


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'category', 'price', 'stock', 'available', 'featured', 'created_at']
    list_filter = ['available', 'featured', 'category', 'seller', 'created_at']
    list_editable = ['price', 'stock', 'available', 'featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'order']
    list_filter = ['product']


@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ['seller', 'customer', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at', 'seller']
    search_fields = ['seller__first_name', 'customer__first_name', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
