# views.py (Yangilangan varianti)
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import User, Parents, UserRole
from .serializers import UserSerializer, ParentsSerializer
from .permissions import IsAdminOrSuperAdmin


class UserViewSet(viewsets.ModelViewSet): 
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
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
        """
        Siz aytgan mantiq: Adminni o'chirmoqchi bo'lgan odam Superadmin bo'lishi shart.
        """
        instance = self.get_object()
        current_user = request.user

        if instance.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            if current_user.role != UserRole.SUPERADMIN:
                raise PermissionDenied(
                    "Siz Admin yoki Superadmin foydalanuvchini oʻchira olmaysiz! Bunga faqat Superadmin haqli."
                )

        # 4. Agar shartlardan muvaffaqiyatli o'tsa, odatdagidek o'chirib yuboramiz
        self.perform_destroy(instance)
        return Response(
            {"detail": "Foydalanuvchi muvaffaqiyatli oʻchirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )
    

class ParentsViewSet(viewsets.ModelViewSet):
    """
    Ota-onalarni boshqarish uchun ViewSet.
    Buni ham faqat Admin va Superadmin boshqara oladi.
    """
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    permission_classes = [IsAdminOrSuperAdmin]