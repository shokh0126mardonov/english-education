from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from app.users.models import User
from app.users.serializers import RegisterSerializer, LoginSerializer, UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage User resources (Teachers, Students, Admins).
    Supports filtering by role, e.g., GET /api/users/?role=teacher
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class RegisterView(APIView):
    """
    API View to handle user registration. Returns JWT credentials and profile
    upon successful creation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens to immediately authenticate the newly registered user
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    API View to handle user login. Authenticates credentials and returns JWT
    tokens alongside user profile details.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user_serializer = UserSerializer(validated_data['user'])

        return Response({
            'refresh': validated_data['refresh'],
            'access': validated_data['access'],
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)