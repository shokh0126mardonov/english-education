from rest_framework import permissions
from .models import UserRole

class IsSuperAdmin(permissions.BasePermission):
    """Faqat Superadmin kirishi uchun"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.SUPERADMIN


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """Admin yoki Superadmin kirishi uchun"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [UserRole.SUPERADMIN, UserRole.ADMIN]


class IsTeacher(permissions.BasePermission):
    """Faqat Oʻqituvchilar uchun"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.TEACHER


class IsStudent(permissions.BasePermission):
    """Faqat Talabalar uchun"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.STUDENT