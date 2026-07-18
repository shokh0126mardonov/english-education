from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Parents

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'avatar')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']

    def has_module_permission(self, request):
        # Asosiy (public) sxemada Users qismi umuman ko'rinmasligi uchun:
        if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
            return False
        return super().has_module_permission(request)

from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
            return False
        return super().has_module_permission(request)


admin.site.register(Parents)
    