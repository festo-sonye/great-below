from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'color', 'size', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 1
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'customer_name', 'customer_phone', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_code', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['order_code', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_code', 'status', 'total_amount', 'delivery_notes')
        }),
        ('Customer Info', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'customer_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                note=f'Status updated to {obj.get_status_display()}'
            )
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_price', 'quantity']
    list_filter = ['order']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_at']
    list_filter = ['status', 'created_at']
