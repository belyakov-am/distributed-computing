from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenVerifyView

from users.models import Profile
from users.serializers import RegisterSerializer


def register_user(request, email, password):
    email = BaseUserManager.normalize_email(email)
    email = email.lower()

    exists = User.objects.filter(email=email).exists()
    if exists:
        return Response({'error', 'user already registered'}, email)

    user = User()
    user.username = email
    user.email = email
    user.set_password(password)

    try:
        with transaction.atomic():
            user.save()
            profile = Profile()
            profile.user = user
            profile.save()
    except Exception as ex:
        raise ex

    return Response({'user_id': user.id, 'email': email}, status=status.HTTP_200_OK)


class Register(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        return register_user(request, email, password)


class Authorize(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        user = User.objects.get(email=email)

        refresh_token = RefreshToken.for_user(user)
        return Response({'access': str(refresh_token.access_token), 'refresh': str(refresh_token)})


class CustomTokenVerifyView(TokenVerifyView):
    def get(self, request, *args, **kwargs):
        response = super().post(request)
        if response.status_code == status.HTTP_200_OK:
            response.data["message"] = "Token is valid."
        return response

    def post(self, *args, **kwargs):
        return Response(data={"detail": "Method 'POST' not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
