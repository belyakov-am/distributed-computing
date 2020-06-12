from django.urls import path

from .views import Register, Authorize, CustomTokenVerifyView, confirm_registration
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register', Register.as_view()),
    path('confirm-registration', confirm_registration),
    path('authorize', Authorize.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('validate', CustomTokenVerifyView.as_view()),
]
