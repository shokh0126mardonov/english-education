from django.db import models
from django.contrib.auth.models import AbstractUser
from app.common.models import BaseModel

class User(AbstractUser, BaseModel):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.STUDENT)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
