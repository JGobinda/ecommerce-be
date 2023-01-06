from django.urls import path
from rest_framework.routers import DefaultRouter

from ecommerce.product.api.v1.views import ProductViewSet

ROUTER = DefaultRouter()
ROUTER.register('', ProductViewSet, basename='product_view')
urlpatterns = [
              ] + ROUTER.urls
