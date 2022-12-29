from rest_framework.routers import DefaultRouter

from ecommerce.contact.api.v1.views.contact import ContactViewSet

ROUTER = DefaultRouter()
ROUTER.register('ok/', ContactViewSet, basename='contact')
urlpatterns = [] + ROUTER.urls
