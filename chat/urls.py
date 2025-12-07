from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversations_list, name='conversations_list'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:order_id>/', views.start_conversation, name='start_conversation'),
    path('<int:conversation_id>/send/', views.send_message_ajax, name='send_message_ajax'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
]
