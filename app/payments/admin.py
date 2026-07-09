from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'amount', 'payment_month', 'method', 'status', 'created_at']
    list_filter = ['status', 'method', 'payment_month', 'group']
    search_fields = ['student__username', 'student__first_name']
