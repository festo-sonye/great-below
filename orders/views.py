from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order


def order_confirmation(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    context = {
        'order': order,
    }
    return render(request, 'orders/order_confirmation.html', context)


def track_order(request):
    if request.method == 'POST':
        order_code = request.POST.get('order_code', '').strip().upper()
        if order_code:
            try:
                order = Order.objects.get(order_code=order_code)
                return redirect('orders:order_status', order_code=order.order_code)
            except Order.DoesNotExist:
                messages.error(request, 'Order not found. Please check your order code.')
    
    return render(request, 'orders/track_order.html')


def order_status(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    status_history = order.status_history.all()
    
    context = {
        'order': order,
        'status_history': status_history,
    }
    return render(request, 'orders/order_status.html', context)
