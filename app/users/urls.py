# app/urls.py
# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ParentsViewSet, check_student_parent_telegram, LoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'parents', ParentsViewSet, basename='parent')

urlpatterns = [
    path('', include(router.urls)),
    path('students/<int:student_id>/check-telegram/', check_student_parent_telegram, name='check-telegram'),
    
    # LOGIN API MANZILI
    path('auth/login/', LoginView.as_view(), name='login'),
]