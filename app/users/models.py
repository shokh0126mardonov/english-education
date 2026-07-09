from django.db import models
from django.contrib.auth.models import AbstractUser
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
