from rest_framework import serializers
from .models import User, Parents, UserRole

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role', 'phone']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# serializers.py
from rest_framework import serializers
from .models import Parents

class ParentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parents
        exclude = ['telegram_id'] 
        
    def update(self, instance, validated_data):
        new_phone = validated_data.get('phone')

        if new_phone and instance.phone != new_phone:
            instance.telegram_id = None
        return super().update(instance, validated_data)