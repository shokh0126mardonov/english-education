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
    


class Parents(models.Model):
    user = models.OneToOneField(User,limit_choices_to={'role':'STUDENT'},related_name="parents",on_delete=models.CASCADE)
    full_name = models.CharField(max_length=128,null=True)

    telegram_id = models.PositiveBigIntegerField(
        unique=True,null=True,blank=True
    )
    phone = PhoneNumberField(
        unique=True,region="UZ",
    )