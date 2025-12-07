from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, SellerProfile

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'profile_image')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop_name', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('shop_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
