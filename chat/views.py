from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Conversation, Message
from orders.models import Order, Notification
from shop.models import Product

User = get_user_model()


@login_required
def conversations_list(request):
    """Display all conversations for the logged-in user"""
    if request.user.is_customer:
        conversations = Conversation.objects.filter(customer=request.user)
    else:  # seller
        conversations = Conversation.objects.filter(seller=request.user)
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'chat/conversations_list.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """Display detailed conversation with chat interface"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.customer, conversation.seller]:
        return redirect('messages:conversations_list')
    
    # Mark messages as read for current user
    unread_messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True)
    
    messages = conversation.messages.all().order_by('created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.save()  # Update 'updated_at'
            
            # Create notification for the other user
            other_user = conversation.seller if request.user.is_customer else conversation.customer
            Notification.objects.create(
                user=other_user,
                notification_type='message',
                title=f'New message from {request.user.first_name}',
                message=f'{request.user.first_name}: {content[:100]}',
                order=conversation.order
            )
            
            return redirect('chat:conversation_detail', conversation_id=conversation.id)
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'other_user': conversation.seller if request.user.is_customer else conversation.customer,
    }
    return render(request, 'chat/conversation_detail.html', context)


@login_required
def start_conversation(request, order_id):
    """Start a new conversation for an order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Find the seller of the order (first product's seller)
    seller = order.items.first().product.seller if order.items.exists() else None
    if not seller:
        return redirect('chat:conversations_list')
    
    # Determine customer based on user role
    if request.user.is_customer:
        customer = request.user
    elif request.user.is_seller:
        # If order has customer link, use it; otherwise try to match by email
        customer = order.customer if order.customer else None
        if not customer:
            # Try to find customer by email
            try:
                customer = User.objects.get(email=order.customer_email, user_type='customer')
            except User.DoesNotExist:
                # Create or find customer
                pass
        if not customer:
            return redirect('chat:conversations_list')
        seller = request.user
    else:
        return redirect('chat:conversations_list')
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        customer=customer,
        seller=seller,
        order=order,
    )
    
    return redirect('chat:conversation_detail', conversation_id=conversation.id)


@login_required
@require_POST
def send_message_ajax(request, conversation_id):
    """AJAX endpoint to send a message"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.customer, conversation.seller]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    conversation.save()
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'sender': message.sender.email,
            'content': message.content,
            'created_at': message.created_at.strftime('%b %d, %Y %I:%M %p'),
        }
    })


@login_required
def get_unread_count(request):
    """Get unread message count for current user"""
    if request.user.is_customer:
        conversations = Conversation.objects.filter(customer=request.user)
    else:
        conversations = Conversation.objects.filter(seller=request.user)
    
    unread_count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': unread_count})
