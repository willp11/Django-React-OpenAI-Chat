from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('chat-messages/<str:chat_id>/', views.get_chat_messages, name='get-chat-messages'),
    path('create-chat/', views.create_chat, name='create-chat'),
    path('chat-stream/<str:chat_id>/', views.chat_stream, name='chat-stream'),
]
