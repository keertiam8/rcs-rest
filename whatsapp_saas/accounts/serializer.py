

from rest_framework import routers, serializers, viewsets
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','password','is_verified']
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)   # 🔐 HASHING HERE
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class LoginVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    otp = serializers.CharField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()



