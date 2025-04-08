from django.urls import path
from .views import CreateRoomChat, GetRoomChats, AdminRoomChats, GetFirebaseToken

urlpatterns = [
    path('create-chat/', CreateRoomChat.as_view(), name='create-chat'),
    path('get-room/', GetRoomChats.as_view(), name='get-room'),
    path('chat-rooms/', AdminRoomChats.as_view(), name='admin-chat-rooms'),
    path('token/', GetFirebaseToken.as_view(), name='get-firebase-token'),
]