from rest_framework.routers import DefaultRouter
from .views.accounts import ListView
from django.urls import path
ROUTER = DefaultRouter()
# ROUTER.register('list/', ListView.as_view(), basename='list')

urlpatterns = [
    path('list/', ListView.as_view(), name='list')
] + ROUTER.urls

