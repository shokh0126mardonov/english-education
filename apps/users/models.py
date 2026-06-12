from django.db import models

from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class UserRole(models.TextChoices):
    SUPERADMIN = 'SUPERADMIN','Superadmin'
    ADMIN = 'ADMIN','Admin'
    TEACHER = 'TEACHER','Teacher'
    STUDENT = 'STUDENT','Student'


class User(AbstractUser):
    role = models.CharField(
        choices=UserRole.choices,default=UserRole.STUDENT
    )
    
    phone = PhoneNumberField(
        unique=True,region="UZ",
    )