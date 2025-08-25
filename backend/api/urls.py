from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('chat/', views.chat_view, name='chat'),
    path('chat-stream/', views.chat_stream_view, name='chat-stream'),
]
