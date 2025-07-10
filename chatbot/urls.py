from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot_view'),
    path('send-message/', views.send_message, name='send_message'),
    path('history/', views.chat_history, name='chat_history'),
    path('new-chat/', views.start_new_chat, name='start_new_chat'),
    path('load-session/<int:session_id>/', views.load_chat_session, name='load_chat_session'),
] 