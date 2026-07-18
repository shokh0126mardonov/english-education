# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser
# pyrefly: ignore [missing-import]
from django.core.validators import RegexValidator
from app.common.models import BaseModel

class User(AbstractUser, BaseModel):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    phone_regex = RegexValidator(
        regex=r'^\+?998?\d{9}$',
        message="Phone number must be entered in the format: '+998901234567'."
    )

    role = models.CharField('Role', max_length=20, choices=RoleChoices.choices, default=RoleChoices.STUDENT)
    phone_number = models.CharField('Phone number', validators=[phone_regex], max_length=17, blank=True, null=True)
    avatar = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Parents(BaseModel):
    user = models.ForeignKey(User,limit_choices_to={'role': User.RoleChoices.STUDENT}, on_delete=models.CASCADE, related_name='parent') 
    full_name = models.CharField(max_length=100, verbose_name="To'liq ismi")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami", unique=True)
    telegram_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telegram ID")
    telegram_username = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telegram username")

    class Meta:
        verbose_name = "Ota-ona"
        verbose_name_plural = "Ota-onalar"

    def __str__(self):
        return f"{self.full_name} - {self.user.username}"
