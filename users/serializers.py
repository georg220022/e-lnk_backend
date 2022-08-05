from dataclasses import field
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken



class ChangePasswordSerializer(serializers.Serializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user
