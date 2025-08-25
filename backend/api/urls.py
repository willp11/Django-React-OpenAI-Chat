from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('create-chat/', views.create_chat, name='create-chat'),
    path('chat-stream/', views.chat_stream, name='chat-stream'),
]
