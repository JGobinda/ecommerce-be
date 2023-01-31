from rest_framework.routers import DefaultRouter

from ecommerce.contact.api.v1.views.contact import ContactViewSet, FAQViewSet

ROUTER = DefaultRouter()
ROUTER.register(f'FAQ', FAQViewSet, basename='faq')
ROUTER.register('', ContactViewSet, basename='contact')
urlpatterns = ROUTER.urls
