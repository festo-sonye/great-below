from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.views.decorators.http import require_POST
from .models import Product, Category, SellerReview
from orders.models import Order, OrderItem, OrderStatusHistory, Payment
from decimal import Decimal


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
    
    # Get seller rating and review count
    seller_reviews = SellerReview.objects.filter(seller=product.seller)
    avg_rating = seller_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    review_count = seller_reviews.count()
    
    context = {
        'product': product,
        'related_products': related_products,
        'seller_rating': avg_rating,
        'review_count': review_count,
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


@login_required(login_url='accounts:login')
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
        payment_method = request.POST.get('payment_method', 'mpesa')
        customer_latitude = request.POST.get('customer_latitude')
        customer_longitude = request.POST.get('customer_longitude')
        
        if not all([customer_name, customer_phone, customer_address]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'shop/checkout.html', {
                'cart_items': cart_items,
                'total': total,
            })
        
        order = Order.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
            total_amount=Decimal(str(total)),
            customer_latitude=customer_latitude if customer_latitude else None,
            customer_longitude=customer_longitude if customer_longitude else None,
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
        
        # Create Payment record with 20% deposit
        deposit_amount = Decimal(str(total)) * Decimal('0.20')
        balance_amount = Decimal(str(total)) * Decimal('0.80')
        
        payment = Payment.objects.create(
            order=order,
            deposit_amount=deposit_amount,
            balance_amount=balance_amount,
            deposit_payment_method=payment_method,
            status='pending',
        )
        
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            note=f'Order placed successfully. 20% deposit (KES {deposit_amount}) required.'
        )
        
        request.session['cart'] = {}
        request.session.modified = True
        
        # Store order code in session to show payment details
        request.session['last_order_code'] = order.order_code
        
        # For now, all payments go to order confirmation page
        # M-PESA integration will be added back when credentials are available
        messages.success(request, f'Order placed! Please pay the 20% deposit of KES {deposit_amount} to confirm your order.')
        return redirect('orders:order_confirmation', order_code=order.order_code)
    
    # Pre-fill user info if logged in
    initial_data = {
        'customer_name': request.user.get_full_name() if request.user.is_authenticated else '',
        'customer_phone': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
        'customer_email': request.user.email if request.user.is_authenticated else '',
    }
    
    total_decimal = Decimal(str(total))
    deposit_amount = total_decimal * Decimal('0.20')
    balance_amount = total_decimal * Decimal('0.80')
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'deposit_amount': deposit_amount,
        'balance_amount': balance_amount,
        'initial_data': initial_data,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def add_product(request):
    """Allow sellers to add new products"""
    if request.user.user_type != 'seller':
        messages.error(request, 'Only sellers can add products.')
        return redirect('shop:home')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        colors = request.POST.get('colors', '')
        sizes = request.POST.get('sizes', '')
        image = request.FILES.get('image')
        
        if not all([name, description, category_id, price, stock, image]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'shop/add_product.html', {'categories': categories})
        
        # Generate slug from product name
        from django.utils.text import slugify
        slug = slugify(name)
        
        # Check if slug already exists
        counter = 1
        original_slug = slug
        while Product.objects.filter(slug=slug).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        
        try:
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=description,
                category_id=category_id,
                price=Decimal(price),
                stock=int(stock),
                colors=colors,
                sizes=sizes,
                image=image,
                seller=request.user,
                available=True,
            )
            
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('accounts:seller_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            return render(request, 'shop/add_product.html', {'categories': categories})
    
    context = {
        'categories': categories,
    }
    return render(request, 'shop/add_product.html', context)


@login_required
def edit_product(request, product_id):
    """Allow sellers to edit their products"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user is the product seller
    if product.seller != request.user:
        messages.error(request, 'You can only edit your own products.')
        return redirect('accounts:seller_dashboard')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        colors = request.POST.get('colors', '')
        sizes = request.POST.get('sizes', '')
        image = request.FILES.get('image')
        
        if not all([name, description, category_id, price, stock]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'shop/edit_product.html', {
                'product': product,
                'categories': categories,
            })
        
        try:
            product.name = name
            product.description = description
            product.category_id = category_id
            product.price = Decimal(price)
            product.stock = int(stock)
            product.colors = colors
            product.sizes = sizes
            
            if image:
                product.image = image
            
            product.save()
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('accounts:seller_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return render(request, 'shop/edit_product.html', {
                'product': product,
                'categories': categories,
            })
    
    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'shop/edit_product.html', context)


@login_required
def delete_product(request, product_id):
    """Allow sellers to delete their products"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user is the product seller
    if product.seller != request.user:
        messages.error(request, 'You can only delete your own products.')
        return redirect('accounts:seller_dashboard')
    
    product_name = product.name
    product.delete()
    
    messages.success(request, f'Product "{product_name}" has been deleted successfully!')
    return redirect('accounts:seller_dashboard')
