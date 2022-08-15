from rest_framework import serializers
from .models import User
from .public_id_generator import GeneratorId


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        print({**validated_data})
        user = User.objects.create_user(**validated_data)
        user.public_key = str(user.id) + str(GeneratorId.public_id())
        user.save()
        return user
