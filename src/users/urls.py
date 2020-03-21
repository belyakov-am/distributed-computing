from django.urls import path

from users.views import Register, Authorize, CustomTokenVerifyView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register', Register.as_view()),
    path('authorize', Authorize.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('validate', CustomTokenVerifyView.as_view()),
]