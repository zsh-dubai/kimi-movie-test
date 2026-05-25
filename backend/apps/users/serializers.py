from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'gender', 'birthday', 'bio']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'nickname']

    def create(self, validated_data):
        validated_data.pop('email', None)
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        nickname = validated_data.pop('nickname', '')
        user = User.objects.create_user(
            username=username,
            password=password,
            nickname=nickname
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
