from rest_framework.routers import DefaultRouter

from ecommerce.cart.api.v1.views.cart import OrderViewSet

ROUTER = DefaultRouter()
ROUTER.register('', OrderViewSet, basename='order')
urlpatterns = ROUTER.urls
