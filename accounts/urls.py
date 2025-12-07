from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),
    path('seller/setup/', views.seller_profile_setup, name='seller_profile_setup'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/sellers/', views.admin_sellers, name='admin_sellers'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),
]
