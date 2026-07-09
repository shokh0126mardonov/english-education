from django.db import models
from app.common.models import BaseModel
from app.users.models import User

class Payment(BaseModel):
    class MethodChoices(models.TextChoices):
        CASH = 'cash', 'Cash'
        CARD = 'card', 'Card'
        PAYME = 'payme', 'Payme'
        CLICK = 'click', 'Click'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=MethodChoices.choices, default=MethodChoices.CASH)

    def __str__(self):
        return f"{self.student.username} - {self.amount} via {self.get_method_display()}"
