from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ParentsViewSet,ParentTelegramConnection

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'parents', ParentsViewSet, basename='parent')


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', include(router.urls)),
    path('telegram-check/<int:pk>/',ParentTelegramConnection.as_view())
]
