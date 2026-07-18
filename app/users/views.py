# app/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Parents
from .serializers import UserSerializer, ParentsSerializer
from .permissions import UserAccessPermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserAccessPermission]

    def destroy(self, request, *args, **kwargs):
        # Faqat admin va manager foydalanuvchini o'chira oladi (permission qisman buni yopgan, bu yerda aniq qilamiz)
        if request.user.role not in ['admin', 'manager']:
            return Response({"detail": "O'chirishga ruxsat yo'q."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ParentsViewSet(viewsets.ModelViewSet):
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    # Ota-onalarni ham hamma (studentdan tashqari) boshqarishi uchun IsAuthenticated ishlatamiz, serializerda cheklaymiz
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user.role == 'student':
            raise serializers.ValidationError("Student ota-onani o'chira olmaydi.")
        instance.delete()


# 4-ETAP: Student ID kelganda Telegram ID borligini tekshiradigan API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_student_parent_telegram(request, student_id):
    try:
        # Avval kelgan ID rostdan ham student ekanligini tekshiramiz
        student = User.objects.get(id=student_id, role='student')
    except User.DoesNotExist:
        return Response({"detail": "Student topilmadi."}, status=status.HTTP_404_NOT_FOUND)

    # Studentga bog'langan ota-onalarni qidiramiz
    parent = Parents.objects.filter(user=student).first()
    
    if parent and parent.telegram_id is not None:
        return Response({
            "status": "success", 
            "telegram_id": parent.telegram_id
        }, status=status.HTTP_200_OK)
        
    return Response({
        "status": "error", 
        "detail": "Telegram ID mavjud emas."
    }, status=status.HTTP_400_BAD_REQUEST)


# app/views.py ichiga qo'shing:
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer