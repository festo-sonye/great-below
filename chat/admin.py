from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'seller', 'order', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer__email', 'seller__email', 'order__order_code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'conversation__customer__email', 'conversation__seller__email', 'content')
    readonly_fields = ('created_at',)
