# app/permissions.py
from rest_framework import permissions

class UserAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Safe metodlar (GET, HEAD, OPTIONS) hamma autentifikatsiyadan o'tganlar uchun ochiq
        if request.method in permissions.SAFE_METHODS:
            return True

        # Yaratish (POST) va O'chirish/Yangilash mantiqlari serializer/viewset ichida batafsil tekshiriladi
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin o'zidan tashqari hamma narsani (o'chirish, o'zgartirish) qila oladi
        if user.role == 'admin':
            return True
            
        # Manager faqat teacher va studentlarni o'zgartira oladi (yoki o'chiradi)
        if user.role == 'manager' and obj.role in ['teacher', 'student']:
            return True

        # Har bir foydalanuvchi faqat o'zini yangilay oladi (o'chira olmaydi, agar u admin/manager bo'lmasa)
        if request.method in ['PUT', 'PATCH'] and obj == user:
            return True

        return False