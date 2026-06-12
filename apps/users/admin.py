from django.contrib import admin

from .models import User,Parents

admin.site.register(
    [
        User,Parents
    ]
)