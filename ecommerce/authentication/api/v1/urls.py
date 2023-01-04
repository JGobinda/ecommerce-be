from django.urls import path
from rest_framework.routers import DefaultRouter
from ecommerce.authentication.api.v1.views.token import ObtainAuthTokenView

ROUTER = DefaultRouter()

urlpatterns = [
                  path('auth/obtain/', ObtainAuthTokenView.as_view(), name='obtain'),
              ] + ROUTER.urls