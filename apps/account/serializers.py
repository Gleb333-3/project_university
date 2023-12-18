from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings


User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(max_length=200, required=True)
    password = serializers.CharField(max_length=128, required=True)
    password_confirm = serializers.CharField(max_length=128, required=True)

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Этот ник уже занят, выберите другой.'
            )
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Данный почтовый адрес уже занят, используйте другой.'
            )
        return email

    def validate(self, attrs: dict):
        password = attrs.get('password')
        password_confirmation = attrs.pop('password_confirm')
        if password != password_confirmation:
            raise serializers.ValidationError(
                'Пароли не совпадают.'
            )
        return attrs

    def create(self, validated_data: dict):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        user.send_activation_code()
        return user


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(min_length=1, max_length=10, required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            return email
        raise serializers.ValidationError('Пользователь не найден.')

    def validate_code(self,code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Неверный код.')
        return code

    def validate(self, attrs: dict):
        email = attrs.get('email')
        code = attrs.get('code')
        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('Пользователь не найден.')
        return attrs

    def activate_account(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=128)

    def validate_username(self, username):
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователя с указанным ником не существует.'
            )
        return username

    def validate(self, attrs: dict):
        request = self.context.get('request')
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = authenticate(
                username=username,
                password=password,
                request=request
            )
            if not user:
                raise serializers.ValidationError('Неправильное имя пользователя или пароль.')
        else:
            raise serializers.ValidationError('Заполните все поля.')
        attrs['user'] = user
        return attrs