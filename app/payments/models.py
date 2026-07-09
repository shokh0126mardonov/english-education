from django.db import models
from app.common.models import BaseModel
from app.users.models import User
from app.lessons.models import Group

class Payment(BaseModel):
    class MethodChoices(models.TextChoices):
        CASH = 'cash', 'Cash'
        CARD = 'card', 'Card'
        PAYME = 'payme', 'Payme'
        CLICK = 'click', 'Click'

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payments', 
        limit_choices_to={'role': User.RoleChoices.STUDENT},
        verbose_name='Student'
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payments',
        verbose_name='Group'
    )
    amount = models.DecimalField('Amount', max_digits=10, decimal_places=2)
    payment_month = models.DateField('Payment month', null=True, blank=True, help_text="The month this payment belongs to")
    method = models.CharField('Method', max_length=20, choices=MethodChoices.choices, default=MethodChoices.CASH)
    status = models.CharField('Status', max_length=20, choices=StatusChoices.choices, default=StatusChoices.COMPLETED)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_month']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.amount} via {self.get_method_display()} ({self.get_status_display()})"
