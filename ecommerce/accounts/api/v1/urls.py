from rest_framework.routers import DefaultRouter
from .views.accounts import UserViewSet
ROUTER = DefaultRouter()
ROUTER.register('', UserViewSet, basename='user')

urlpatterns = [
] + ROUTER.urls

