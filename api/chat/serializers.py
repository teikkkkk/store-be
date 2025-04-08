from rest_framework import serializers
from .models import RoomChat, Chat
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'room', 'sender', 'content', 'timestamp']

class RoomChatSerializer(serializers.ModelSerializer):
    messages = ChatSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = RoomChat
        fields = ['id', 'user', 'username', 'room_id', 'created_at', 'messages']