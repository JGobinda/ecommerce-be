from rest_framework.permissions import AllowAny

from ecommerce.commons.mixins.viewsets import ListRetrieveViewSetMixin
from ecommerce.product.api.v1.serializers.product import ProductSerializer
from ecommerce.product.models import Product


class ProductViewSet(ListRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = None

    def get_permissions(self):
        return [AllowAny()]
