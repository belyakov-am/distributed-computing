from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.exceptions import TokenError

from .models import Profile
from .serializers import RegisterSerializer, ConfirmRegistrationSerializer
from .util import get_notification_queue, make_confirmation_message, message_queue_provider


@api_view(["GET"])
def confirm_registration(request):
    serializer = ConfirmRegistrationSerializer(data=request.query_params)
    serializer.is_valid()
    
    token = request.query_params.get('token')
    user_id = request.query_params.get('id')

    try:
        _ = RefreshToken(token=token)
    except TokenError:
        return Response(data={'message': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()

    return Response(data={'message': 'Email is verified, registration completed.'}, status=status.HTTP_200_OK)


def register_user(request, email, password):
    email = BaseUserManager.normalize_email(email)
    email = email.lower()

    exists = User.objects.filter(email=email).exists()
    if exists:
        return Response({'error', 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

    user = User()
    user.username = email
    user.email = email
    user.set_password(password)
    user.is_active = False

    try:
        with transaction.atomic():
            user.save()
            profile = Profile()
            profile.user = user
            profile.save()
    except Exception as ex:
        raise ex

    queue = get_notification_queue("email")
    body = make_confirmation_message(confirm_registration, RefreshToken.for_user(user), user.id)

    message_queue_provider.send_confirmation(queue, email, "Registration confirmation", body)

    return Response({'user_id': user.id, 'email': email, "msg": "Check email"}, status=status.HTTP_200_OK)


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

        if not user.is_active:
            return Response(
                {'error': 'Your account is not verified yet. Check your email.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

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
