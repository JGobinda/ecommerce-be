from rest_framework.routers import DefaultRouter

from ecommerce.shipping.api.v1.views.shipping import ShippingDetailViewSet

ROUTER = DefaultRouter()
ROUTER.register('', ShippingDetailViewSet, basename='shipping-detail')
urlpatterns = [] + ROUTER.urls
