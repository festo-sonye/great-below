from .models import Category


def cart_context(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    return {'cart_count': cart_count}


def categories_context(request):
    categories = Category.objects.all()
    return {'all_categories': categories}


def notifications_context(request):
    """Add user notifications to template context"""
    if request.user.is_authenticated:
        notifications = request.user.notifications.all().order_by('-created_at')[:10]
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {
            'user_notifications': notifications,
            'unread_notifications_count': unread_count,
        }
    return {
        'user_notifications': [],
        'unread_notifications_count': 0,
    }
