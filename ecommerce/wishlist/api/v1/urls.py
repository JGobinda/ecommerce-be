from rest_framework.routers import DefaultRouter

from ecommerce.wishlist.api.v1.views.wishlist import WishListViewSet

ROUTER = DefaultRouter()
ROUTER.register('', WishListViewSet, basename='wish_list')
urlpatterns = ROUTER.urls
