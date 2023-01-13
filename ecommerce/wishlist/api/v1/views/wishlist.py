from rest_framework.response import Response

from ecommerce.commons.mixins.viewsets import ListCreateDestroyViewSetMixin
from ecommerce.wishlist.api.v1.serializers.wishlist import WishListSerializer
from ecommerce.wishlist.models import WishList


class WishListViewSet(ListCreateDestroyViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data
        )
