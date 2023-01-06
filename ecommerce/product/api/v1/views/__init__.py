from ecommerce.commons.mixins.viewsets import ListRetrieveViewSetMixin
from ecommerce.product.api.v1.serializers.product import ProductSerializer
from ecommerce.product.models import Product


class ProductViewSet(ListRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

