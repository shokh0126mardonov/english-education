# app/serializers.py
from rest_framework import serializers
from .models import User, Parents

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Parolni hashlash uchun create_user ishlatamiz
        return User.objects.create_user(**validated_data)

    def validate(self, attrs):
        request_user = self.context['request'].user
        role_to_create = attrs.get('role', 'student')

        # Yaratish (POST) vaqtidagi tekshiruvlar
        if not self.instance:
            if role_to_create == 'admin':
                raise serializers.ValidationError("Admin rolida foydalanuvchi yaratish taqiqlangan.")
            
            if role_to_create == 'manager' and request_user.role != 'admin':
                raise serializers.ValidationError("Managerlarni faqat Admin yarata oladi.")
                
            if role_to_create in ['teacher', 'student'] and request_user.role not in ['admin', 'manager']:
                raise serializers.ValidationError("Teacher yoki Student yaratish uchun huquqingiz yetarli emas.")
        
        # Yangilash (PUT/PATCH) vaqtidagi tekshiruvlar
        else:
            new_role = attrs.get('role')
            if new_role and new_role != self.instance.role:
                # O'zining rolini hech kim o'zgartira olmaydi (hatto admin ham o'zinikini)
                if request_user == self.instance:
                    raise serializers.ValidationError("O'z rolingizni o'zgartira olmaysiz.")
                
                # Admin hammaning rolini o'zgartira oladi (o'zinikidan tashqari)
                if request_user.role == 'admin':
                    pass
                # Manager faqat student va teacherni rolini o'zgartira oladi
                elif request_user.role == 'manager' and self.instance.role in ['teacher', 'student'] and new_role in ['teacher', 'student']:
                    pass
                else:
                    raise serializers.ValidationError("Ushbu foydalanuvchi rolini o'zgartirishga ruxsatingiz yo'q.")

        return attrs


class ParentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parents
        fields = ['id', 'user', 'full_name', 'phone', 'telegram_id', 'telegram_username']
        # telegram_id ni CRUD qilib (tashqaridan yuborib) bo'lmaydi, faqat o'qish mumkin
        read_only_fields = ['telegram_id']

    def validate(self, attrs):
        request_user = self.context['request'].user
        
        # Parentsni studentdan tashqari hamma yarata oladi
        if not self.instance and request_user.role == 'student':
            raise serializers.ValidationError("Studentlar ota-ona ma'lumotini yarata olmaydi.")
        
        return attrs

    def update(self, instance, validated_data):
        new_phone = validated_data.get('phone')
        
        # Agar telefon raqam yangilansa va u eskisiga teng bo'lmasa, telegram_id o'chib ketadi
        if new_phone and new_phone != instance.phone:
            instance.telegram_id = None
            
        return super().update(instance, validated_data)


# app/serializers.py ichiga qo'shing:
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Foydalanuvchi login (username/password) tekshiriladi
        data = super().validate(attrs)
        
        # Tokenlarga qo'shimcha ravishda foydalanuvchining rolini qaytaramiz
        data['role'] = self.user.role
        
        return data