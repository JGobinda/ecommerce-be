from rest_framework.response import Response

from ecommerce.cart.constants import PENDING, IN_PROCESS
from ecommerce.cart.models import Order
from ecommerce.commons.mixins.viewsets import ListCreateDestroyViewSetMixin
from ecommerce.wishlist.api.v1.serializers.wishlist import WishListSerializer
from ecommerce.wishlist.models import WishList


class WishListViewSet(ListCreateDestroyViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    serializer_class = WishListSerializer

    def get_queryset(self):
        return WishList.objects.filter(user=self.request.user).exclude(
            product__uuid__in=Order.objects.filter(user=self.request.user, status__in=[PENDING, IN_PROCESS]).values_list('product__uuid', flat=True))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data
        )
