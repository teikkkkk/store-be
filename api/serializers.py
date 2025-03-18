from rest_framework import serializers
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password','is_staff']

    def validate(self, data):
        
        if data['password']:
            if len(data['password']) < 8:
                raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']