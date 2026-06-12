# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

from .models import User, Parents, UserRole
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    ChangePasswordSerializer, 
    ParentsSerializer
)
from .permissions import IsAdminOrSuperAdmin,IsTeacher


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Action turiga qarab serializerlarni dinamik almashtirish"""
        if self.action == 'me':
            return UserProfileSerializer
        if self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer

    def get_permissions(self):
        """Faqat 'me' va 'change_password' oddiy foydalanuvchilarga ochiq, qolganlar Admin/Superadmin uchun"""
        if self.action in ['me', 'change_password']:
            return [IsAuthenticated()]
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Admin yoki Superadmin yaratishni faqat Superadmin-ga ruxsat berish"""
        requested_role = self.request.data.get('role')
        current_user = self.request.user

        if requested_role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            if current_user.role != UserRole.SUPERADMIN:
                raise PermissionDenied("Siz Admin yoki Superadmin yarata olmaysiz! Bunga faqat Superadmin haqli.")

        serializer.save()

    def perform_update(self, serializer):
        """Foydalanuvchi rolini Admin-ga o'zgartirishni cheklash"""
        requested_role = self.request.data.get('role')
        current_user = self.request.user

        if requested_role and requested_role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            if current_user.role != UserRole.SUPERADMIN:
                raise PermissionDenied("Foydalanuvchi rolini Admin-ga o'zgartirish faqat Superadmin uchun.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Adminlarni faqat Superadmin o'chira olishi mantiqi"""
        instance = self.get_object()
        current_user = request.user

        if instance.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            if current_user.role != UserRole.SUPERADMIN:
                raise PermissionDenied(
                    "Siz Admin yoki Superadmin foydalanuvchini oʻchira olmaysiz! Bunga faqat Superadmin haqli."
                )

        self.perform_destroy(instance)
        return Response(
            {"detail": "Foydalanuvchi muvaffaqiyatli oʻchirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )

    # 👇 1. PROFIL ENDPOINTI (GET, PUT, PATCH)
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """/api/v1/users/me/"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # 👇 2. PAROLNI O'ZGARTIRISH ENDPOINTI (POST)
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """/api/v1/users/change-password/"""
        user = request.user
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid(raise_exception=True):
            # Yangi parolni o'rnatish va shifrlash
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {"detail": "Parol muvaffaqiyatli oʻzgartirildi."}, 
                status=status.HTTP_200_OK
            )


class ParentsViewSet(viewsets.ModelViewSet):
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    permission_classes = [IsAdminOrSuperAdmin]

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema


class ParentTelegramConnection(APIView):
    permission_classes = [IsTeacher | IsAdminOrSuperAdmin]

    @extend_schema(
        summary="Ota-ona telegram botdan o'tganini status kod orqali tekshirish",
        responses={
            200: None,  
            404: None   
        }
    )

    def get(self, request: Request, pk=None) -> Response:
        user = get_object_or_404(User, pk=pk)

        if hasattr(user, 'parents') and user.parents.telegram_id:
            return Response(
                status=status.HTTP_200_OK
            )
            
        return Response(
            status=status.HTTP_404_NOT_FOUND
        )