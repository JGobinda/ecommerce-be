from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from ecommerce.commons.mixins.viewsets import ListRetrieveViewSetMixin
from ecommerce.product.api.v1.serializers.product import ProductSerializer
from ecommerce.product.models import Product


class ProductViewSet(ListRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = Product.objects.filter(in_stock=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category__title', 'name']
    ordering_fields = ['name']
    search_fields = ['name', 'category__title']

    @action(detail=False, methods=['get'], url_path='featured-products', url_name='featured-products')
    def featured_products(self, request, *args, **kwargs):
        featured_product_queryset = Product.objects.filter(in_stock=True, featured=True)[:15]
        serializer = self.get_serializer(featured_product_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_name='latest-products', url_path='latest-products')
    def latest_products(self, request, *args, **kwargs):
        latest_products_queryset = Product.objects.filter(in_stock=True).order_by('-created_at', '-updated_at')[:15]
        serializer = self.get_serializer(latest_products_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)
