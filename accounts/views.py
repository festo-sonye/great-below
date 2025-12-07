from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q, Avg
from datetime import timedelta
from django.utils import timezone
from .models import CustomUser, SellerProfile
from .forms import CustomUserCreationForm, CustomUserLoginForm, SellerProfileForm, CustomUserProfileForm
from orders.models import Order, Payment
from shop.models import Product, SellerReview


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in with explicit backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome {user.first_name}! Account created successfully.')
            
            # If seller, redirect to seller profile setup
            if user.user_type == 'seller':
                return redirect('accounts:seller_profile_setup')
            return redirect('shop:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        # If user is authenticated and is seller, redirect to dashboard
        if request.user.is_seller:
            return redirect('accounts:seller_dashboard')
        elif request.user.is_admin_user:
            return redirect('admin:index')
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Redirect based on user type
            if user.is_admin_user:
                return redirect('admin:index')
            elif user.is_seller:
                return redirect('accounts:seller_dashboard')
            return redirect('shop:home')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomUserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:home')


@login_required(login_url='accounts:login')
def profile(request):
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = CustomUserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required(login_url='accounts:login')
def seller_profile_setup(request):
    if not request.user.is_seller:
        messages.error(request, 'Only sellers can access this page.')
        return redirect('shop:home')
    
    # Get or create seller profile
    seller_profile, created = SellerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=seller_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shop profile updated successfully!')
            return redirect('accounts:seller_dashboard')
    else:
        form = SellerProfileForm(instance=seller_profile)
    
    return render(request, 'accounts/seller_profile_setup.html', {'form': form})


@login_required(login_url='accounts:login')
def seller_dashboard(request):
    if not request.user.is_seller:
        messages.error(request, 'Only sellers can access this page.')
        return redirect('shop:home')
    
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return redirect('accounts:seller_profile_setup')
    
    # Get seller's products
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # Get seller's orders (from products sold)
    from orders.models import OrderItem
    seller_order_items = OrderItem.objects.filter(product__seller=request.user).select_related('order').order_by('-order__created_at')
    
    # Get unique orders
    seller_orders = Order.objects.filter(items__product__seller=request.user).distinct().order_by('-created_at')
    
    # Get seller's reviews
    reviews = SellerReview.objects.filter(seller=request.user)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'seller_profile': seller_profile,
        'products': products,
        'product_count': products.count(),
        'seller_orders': seller_orders,
        'seller_order_items': seller_order_items,
        'orders_count': seller_orders.count(),
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
    }
    return render(request, 'accounts/seller_dashboard.html', context)


def seller_profile(request, seller_id):
    """Public seller profile view with reviews and ratings"""
    try:
        seller = CustomUser.objects.get(id=seller_id, user_type='seller', is_active=True)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Seller not found.')
        return redirect('shop:home')
    
    try:
        seller_profile = seller.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, 'Seller profile not found.')
        return redirect('shop:home')
    
    # Get seller's products (published only)
    products = Product.objects.filter(seller=seller, available=True).order_by('-created_at')
    
    # Get seller's reviews
    reviews = SellerReview.objects.filter(seller=seller).order_by('-created_at')
    
    # Calculate ratings
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    # Count reviews by rating
    star_counts = {}
    for rating in range(5, 0, -1):
        star_counts[rating] = reviews.filter(rating=rating).count()
    
    context = {
        'seller': seller,
        'seller_profile': seller_profile,
        'products': products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'star_counts': star_counts,
    }
    
    return render(request, 'accounts/seller_profile.html', context)


@login_required(login_url='accounts:login')
def customer_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your orders.')
        return redirect('accounts:login')
    
    # Get user's orders (works for both customers and sellers who make purchases)
    from orders.models import Order
    orders = Order.objects.filter(customer_email=request.user.email).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required(login_url='accounts:login')
def admin_dashboard(request):
    """Admin dashboard for Festo - custom theme matching the app"""
    # Check if user is admin
    if request.user.user_type != 'admin':
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('shop:home')
    
    # Get statistics
    total_users = CustomUser.objects.filter(is_active=True).count()
    total_sellers = CustomUser.objects.filter(user_type='seller', is_active=True).count()
    total_customers = CustomUser.objects.filter(user_type='customer', is_active=True).count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Get recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Get low stock products
    low_stock_products = Product.objects.filter(stock__lt=5).order_by('stock')[:8]
    
    # Get recent reviews
    recent_reviews = SellerReview.objects.all().order_by('-created_at')[:5]
    
    # Calculate average rating for each seller
    sellers = CustomUser.objects.filter(user_type='seller').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating')[:5]
    
    context = {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_customers': total_customers,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'recent_reviews': recent_reviews,
        'top_sellers': sellers,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required(login_url='accounts:login')
def admin_orders(request):
    """Admin view for managing all orders"""
    if request.user.user_type != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('shop:home')
    
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'statuses': Order._meta.get_field('status').choices,
        'selected_status': status,
    }
    
    return render(request, 'accounts/admin_orders.html', context)


@login_required(login_url='accounts:login')
def admin_sellers(request):
    """Admin view for managing sellers"""
    if request.user.user_type != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('shop:home')
    
    sellers = CustomUser.objects.filter(user_type='seller').annotate(
        product_count=Count('products'),
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews'),
        total_orders=Count('products__orderitem')
    ).order_by('-avg_rating')
    
    context = {
        'sellers': sellers,
    }
    
    return render(request, 'accounts/admin_sellers.html', context)


@login_required(login_url='accounts:login')
def admin_products(request):
    """Admin view for managing products"""
    if request.user.user_type != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('shop:home')
    
    products = Product.objects.all().order_by('-created_at')
    
    # Filter by seller if provided
    seller_id = request.GET.get('seller')
    if seller_id:
        products = products.filter(seller_id=seller_id)
    
    # Filter by low stock
    low_stock = request.GET.get('low_stock')
    if low_stock:
        products = products.filter(stock__lt=5)
    
    sellers = CustomUser.objects.filter(user_type='seller')
    
    context = {
        'products': products,
        'sellers': sellers,
        'selected_seller': seller_id,
        'low_stock': low_stock,
    }
    
    return render(request, 'accounts/admin_products.html', context)


@login_required(login_url='accounts:login')
def admin_reviews(request):
    """Admin view for managing seller reviews"""
    if request.user.user_type != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('shop:home')
    
    reviews = SellerReview.objects.all().order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    
    return render(request, 'accounts/admin_reviews.html', context)
