from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


def send_notification_email(notification):
    """
    Send email notification to user based on notification type
    """
    user = notification.user
    
    if not user.email:
        return False
    
    # Email subject and templates based on notification type
    email_templates = {
        'order_placed': {
            'subject': '✅ Order Placed Successfully',
            'template': 'emails/order_placed.html',
        },
        'order_confirmed': {
            'subject': '📦 Your Order Has Been Confirmed',
            'template': 'emails/order_confirmed.html',
        },
        'order_shipped': {
            'subject': '🚚 Your Order is On The Way',
            'template': 'emails/order_shipped.html',
        },
        'order_delivered': {
            'subject': '📬 Your Order Has Been Delivered',
            'template': 'emails/order_delivered.html',
        },
        'delivery_pending': {
            'subject': '✋ Customer Confirmed Delivery',
            'template': 'emails/delivery_confirmed.html',
        },
        'review_request': {
            'subject': '⭐ You Received a New Review',
            'template': 'emails/review_received.html',
        },
        'message': {
            'subject': '💬 New Message From a Customer',
            'template': 'emails/new_message.html',
        },
        'system': {
            'subject': '📢 Important Notification',
            'template': 'emails/system_notification.html',
        },
    }
    
    email_info = email_templates.get(notification.notification_type)
    if not email_info:
        return False
    
    try:
        # Prepare context for email template
        context = {
            'user': user,
            'notification': notification,
            'order': notification.order,
            'order_link': f"{settings.SITE_URL}/orders/{notification.order.order_code}/status/" if notification.order else None,
        }
        
        # Render HTML email
        html_message = render_to_string(email_info['template'], context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=email_info['subject'],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending email to {user.email}: {str(e)}")
        return False


def send_seller_review_notification_email(seller, review):
    """
    Send email to seller when they receive a review
    """
    if not seller.email:
        return False
    
    try:
        subject = f'⭐ New {review.rating}-Star Review from {review.customer.first_name}'
        
        context = {
            'seller': seller,
            'review': review,
            'customer_name': review.customer.first_name,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'seller_profile_link': f"{settings.SITE_URL}/seller/{seller.id}/",
        }
        
        html_message = render_to_string('emails/seller_review.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seller.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending review email to {seller.email}: {str(e)}")
        return False


def send_delivery_confirmation_email(seller, order, customer):
    """
    Send email to seller when customer confirms delivery
    """
    if not seller.email:
        return False
    
    try:
        subject = f'✅ Delivery Confirmed for Order {order.order_code}'
        
        context = {
            'seller': seller,
            'order': order,
            'customer_name': customer.first_name,
            'order_link': f"{settings.SITE_URL}/orders/{order.order_code}/status/",
        }
        
        html_message = render_to_string('emails/delivery_confirmed_seller.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seller.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending delivery confirmation email to {seller.email}: {str(e)}")
        return False
