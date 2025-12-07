from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('confirmation/<str:order_code>/', views.order_confirmation, name='order_confirmation'),
    path('track/', views.track_order, name='track_order'),
    path('track/<str:order_code>/', views.order_status, name='order_status'),
    path('payment/mpesa/<str:order_code>/', views.initiate_mpesa_payment, name='initiate_mpesa_payment'),
    path('payment/mpesa/callback/', views.mpesa_payment_callback, name='mpesa_payment_callback'),
    path('api/check-payment-status/<str:order_code>/', views.check_payment_status_api, name='check_payment_status_api'),
    path('<str:order_code>/confirm-delivery/', views.confirm_delivery, name='confirm_delivery'),
    path('<str:order_code>/review/', views.leave_review, name='leave_review'),
]
