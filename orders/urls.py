from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('confirmation/<str:order_code>/', views.order_confirmation, name='order_confirmation'),
    path('track/', views.track_order, name='track_order'),
    path('track/<str:order_code>/', views.order_status, name='order_status'),
]
