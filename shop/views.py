from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Product, Category
from orders.models import Order, OrderItem, OrderStatusHistory


def home(request):
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    new_arrivals = Product.objects.filter(available=True).order_by('-created_at')[:8]
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)


def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    availability = request.GET.get('availability')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if availability == 'in_stock':
        products = products.filter(stock__gt=0)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'shop/category.html', context)


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'shop/search.html', context)


def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def cart(request):
    cart = get_cart(request)
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'color': item.get('color', ''),
                'size': item.get('size', ''),
                'subtotal': subtotal,
            })
            total += subtotal
        except Product.DoesNotExist:
            pass
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    color = request.POST.get('color', '')
    size = request.POST.get('size', '')
    
    product_key = str(product_id)
    
    if product_key in cart:
        cart[product_key]['quantity'] += quantity
    else:
        cart[product_key] = {
            'quantity': quantity,
            'color': color,
            'size': size,
        }
    
    save_cart(request, cart)
    messages.success(request, f'{product.name} added to cart!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values())
        })
    
    return redirect('shop:cart')


@require_POST
def update_cart(request, product_id):
    cart = get_cart(request)
    product_key = str(product_id)
    
    if product_key in cart:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[product_key]['quantity'] = quantity
        else:
            del cart[product_key]
        save_cart(request, cart)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('shop:cart')


@require_POST
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    product_key = str(product_id)
    
    if product_key in cart:
        del cart[product_key]
        save_cart(request, cart)
        messages.success(request, 'Item removed from cart.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('shop:cart')


def checkout(request):
    cart = get_cart(request)
    
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop:cart')
    
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'color': item.get('color', ''),
                'size': item.get('size', ''),
                'subtotal': subtotal,
            })
            total += subtotal
        except Product.DoesNotExist:
            pass
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email', '')
        customer_address = request.POST.get('customer_address')
        
        if not all([customer_name, customer_phone, customer_address]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'shop/checkout.html', {
                'cart_items': cart_items,
                'total': total,
            })
        
        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
            total_amount=total,
        )
        
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=item['quantity'],
                    color=item.get('color', ''),
                    size=item.get('size', ''),
                )
                product.stock -= item['quantity']
                product.save()
            except Product.DoesNotExist:
                pass
        
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            note='Order placed successfully.'
        )
        
        request.session['cart'] = {}
        request.session.modified = True
        
        return redirect('orders:order_confirmation', order_code=order.order_code)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)
