from django.urls import path
from .views import login_view, logout_view, chat_room, chat_messages_api

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('chat/', chat_room, name='chat_room'),
    path('chat/messages/<str:room_name>/', chat_messages_api, name='chat_messages_api'),
]
