# serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Parents

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role', 'phone']

    def create(self, validated_data):
        # Parolni shifrlab bazaga yozish
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Foydalanuvchi o'z profilini qisman o'zgartirishi uchun xavfsiz serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone']


class ChangePasswordSerializer(serializers.Serializer):
    """Parolni o'zgartirish uchun maxsus validatsiya serializeri"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol notoʻgʻri kiritildi!")
        return value


class ParentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parents
        exclude = ['telegram_id'] 
        
    def update(self, instance, validated_data):
        new_phone = validated_data.get('phone')

        # Telefon raqami o'zgarganda telegram_id ni tozalash
        if new_phone and instance.phone != new_phone:
            instance.telegram_id = None

        return super().update(instance, validated_data)
    

from rest_framework import serializers
from apps.users.models import Parents

class ParentTelegramStatusSerializer(serializers.ModelSerializer):
    # Telegram ulanganini True/False ko'rinishida hisoblab beradigan maydon
    is_telegram_connected = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Parents
        fields = ['id', 'parent_name', 'telegram_id', 'is_telegram_connected']

    def get_is_telegram_connected(self, obj):
        return obj.telegram_id is not None

    def get_parent_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return "Ismsiz Ota-ona"