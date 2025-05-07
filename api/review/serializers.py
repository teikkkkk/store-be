from rest_framework import serializers
from .models import Review
from django.contrib.auth import get_user_model

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at','user_id']

    def get_username(self, obj):
        return obj.user.username