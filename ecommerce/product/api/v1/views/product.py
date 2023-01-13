from django.db.models import Sum, F, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ecommerce.cart.models import Order
from ecommerce.commons.mixins.viewsets import ListRetrieveViewSetMixin, CreateUpdateViewSetMixin, \
    ListCreateUpdateRetrieveViewSetMixin
from ecommerce.product.api.v1.serializers.product import ProductSerializer, ProductRatingSerializer
from ecommerce.product.models import Product, ProductRating


class ProductViewSet(ListRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category__title', 'name']
    ordering_fields = ['name']
    search_fields = ['name', 'category__title']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.action in ['featured_products']:
                return Product.objects.filter(in_stock=True, featured=True).exclude(
                    uuid__in=Order.objects.filter(user=self.request.user).values_list('product__uuid', flat=True))[:15]
            if self.action in ['latest_products']:
                return Product.objects.filter(in_stock=True).exclude(
                    uuid__in=Order.objects.filter(user=self.request.user).values_list('product__uuid',
                                                                                      flat=True)).order_by(
                    '-created_at', '-updated_at')[:15]
            if self.action in ['trending_products']:
                return Product.objects.filter(in_stock=True).annotate(
                    purchases=Count('product_carts')).order_by(
                    '-purchases').exclude(
                    uuid__in=Order.objects.filter(user=self.request.user).values_list('product__uuid', flat=True))[:15]
            return Product.objects.filter(in_stock=True).exclude(
                uuid__in=Order.objects.filter(user=self.request.user).values_list('uuid', flat=True))
        if self.action in ['top_discount_products']:
            return Product.objects.filter(in_stock=True).annotate(discount_per=Sum(
                F('discount_price') * 100 / F('base_price')
            )).filter(discount_per__gte=5).order_by('-discount_per')[:5]
        if self.action in ['trending_products']:
            return Product.objects.filter(in_stock=True).annotate(
                purchases=Count('product_carts')).order_by(
                '-purchases')[:15]
        return Product.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured_products', 'latest_products', 'top_discount_products',
                           'trending_products']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='featured-products', url_name='featured-products')
    def featured_products(self, request, *args, **kwargs):
        featured_product_queryset = self.get_queryset()
        serializer = self.get_serializer(featured_product_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_name='latest-products', url_path='latest-products')
    def latest_products(self, request, *args, **kwargs):
        latest_products_queryset = self.get_queryset()
        serializer = self.get_serializer(latest_products_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_name='trending-products', url_path='trending-products')
    def trending_products(self, request, *args, **kwargs):
        latest_products_queryset = self.get_queryset()
        page = self.paginate_queryset(latest_products_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(latest_products_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    # @action(detail=True, methods=['patch'], url_path='ratings', url_name='ratings')
    # def update_product_rating(self, request, *args, **kwargs):
    #     """
    #     flag true up, flag false down
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     product = self.get_object()
    #     serializer = self.get_serializer(data=request.data,
    #                                      context={'view': self, 'request': self.request, 'object': product})
    #     serializer.is_valid(raise_exception=True)
    #     flag = serializer.validated_data.get('flag')
    #     if flag:
    #         product.ratings += 1
    #     else:
    #         product.ratings -= 1
    #     product.save()
    #     return Response({
    #         'rating': product.ratings
    #     })

    @action(methods=['get'], detail=False, url_name='top-discount-products', url_path='top-discount-products')
    def top_discount_products(self, request, *args, **kwargs):
        top_discount_products_queryset = self.get_queryset()
        serializer = self.get_serializer(top_discount_products_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)


class ProductRatingViewSet(ListCreateUpdateRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = ProductRating.objects.all()
    serializer_class = ProductRatingSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_rating_lookup_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.action in ['update', 'partial_update']:
            if product_rating_lookup_kwarg in self.kwargs:
                context['object'] = self.get_object()
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    # def update(self, request, *args, **kwargs):
    # serializer = self.get_serializer(data=request.data)
    # serializer.is_valid(raise_exception=True)
    # self.perform_update(serializer)
    # return Response(serializer.data)
