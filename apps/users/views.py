# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import User, Parents, UserRole
from .serializers import UserSerializer, ParentsSerializer
from .permissions import IsSuperAdmin, IsAdminOrSuperAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    Foydalanuvchilarni (Admin, Teacher, Student) boshqarish uchun ViewSet.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Rollar bo'yicha umumiy endpointga kirish huquqini belgilash.
        Faqat Admin va Superadmin foydalanuvchilar ro'yxatini ko'ra oladi va o'zgartira oladi.
        """
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Siz aytgan asosiy mantiq shu yerda:
        Admin yaratishni faqat Superadmin-ga ruxsat beramiz.
        """
        requested_role = self.request.data.get('role')
        current_user = self.request.user

        # Agar yangi foydalanuvchi ADMIN yoki SUPERADMIN roly boti bilan yaratilayotgan bo'lsa
        if requested_role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            # Unda so'rov yuborayotgan odam albatta SUPERADMIN bo'lishi shart
            if current_user.role != UserRole.SUPERADMIN:
                raise PermissionDenied("Siz Admin yoki Superadmin yarata olmaysiz! Bunga faqat Superadmin haqli.")

        serializer.save()

    def perform_update(self, serializer):
        """
        Mavjud foydalanuvchini o'zgartirayotganda ham rolni tekshirish
        """
        requested_role = self.request.data.get('role')
        current_user = self.request.user

        if requested_role and requested_role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            if current_user.role != UserRole.SUPERADMIN:
                raise PermissionDenied("Foydalanuvchi rolini Admin-ga o'zgartirish faqat Superadmin uchun.")

        serializer.save()


class ParentsViewSet(viewsets.ModelViewSet):
    """
    Ota-onalarni boshqarish uchun ViewSet.
    Buni ham faqat Admin va Superadmin boshqara oladi.
    """
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    permission_classes = [IsAdminOrSuperAdmin]