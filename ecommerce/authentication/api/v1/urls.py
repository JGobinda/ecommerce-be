from django.urls import path
from rest_framework.routers import DefaultRouter

from ecommerce.authentication.api.v1.views.registration import UserAccountRegistrationView
from ecommerce.authentication.api.v1.views.reset_password import PasswordResetView, PasswordResetConfirmView
from ecommerce.authentication.api.v1.views.token import ObtainAuthTokenView
from ecommerce.authentication.api.v1.views.user_activation import UserAccountActivationWithOTPView

ROUTER = DefaultRouter()
ROUTER.register('register', UserAccountRegistrationView, basename='register')

urlpatterns = [
                  path('auth/obtain/', ObtainAuthTokenView.as_view(), name='obtain'),
                  path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
                  path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
                       name='password-reset-confirm'),
                  path('otp-activate/', UserAccountActivationWithOTPView.as_view(), name='otp_activate'),
              ] + ROUTER.urls
