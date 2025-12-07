from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()


class Conversation(models.Model):
    """Represents a conversation between a customer and a seller"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_conversations')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_conversations')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('customer', 'seller', 'order')

    def __str__(self):
        return f"Chat: {self.customer.email} <-> {self.seller.email}"

    def get_last_message(self):
        return self.messages.first()


class Message(models.Model):
    """Individual messages within a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"
