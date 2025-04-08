from django.db import models
from django.contrib.auth.models import User

class RoomChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    room_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    temp_field = models.CharField(max_length=10, default='temp')   

    def __str__(self):
        return f"RoomChat {self.room_id} for {self.user.username}"

    class Meta:
        db_table = 'room_chat'

class Chat(models.Model):
    room = models.ForeignKey(RoomChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.room.room_id} by {self.sender.username}"

    class Meta:
        db_table = 'chat'