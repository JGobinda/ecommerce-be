from django.db.models import Sum, F, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# from ecommerce.cart.constants import DELIVERED
from ecommerce.cart.constants import PENDING, IN_PROCESS, ON_THE_WAY
from ecommerce.cart.models import Order
from ecommerce.commons.mixins.viewsets import ListRetrieveViewSetMixin, CreateUpdateViewSetMixin, \
    ListCreateUpdateRetrieveViewSetMixin
from ecommerce.product.api.v1.serializers.category import CategorySerializer
from ecommerce.product.api.v1.serializers.product import ProductSerializer, ProductRatingSerializer
from ecommerce.product.models import Product, ProductRating, Category
from ecommerce.wishlist.models import WishList


class ProductViewSet(ListRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category__title', 'name']
    ordering_fields = ['name', 'quantity', 'base_price']
    search_fields = ['name', 'category__title']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.action in ['featured_products']:
                return Product.objects.filter(in_stock=True, featured=True).exclude(
                    uuid__in=Order.objects.filter(user=self.request.user,
                                                  status__in=[PENDING, IN_PROCESS]).values_list(
                        'product__uuid', flat=True))[:15]

            if self.action in ['latest_products']:
                return Product.objects.filter(in_stock=True).exclude(
                    Q(featured=True) | Q(uuid__in=Order.objects.filter(user=self.request.user,
                                                                       status__in=[PENDING, IN_PROCESS
                                                                                ]).values_list(
                        'product__uuid',
                        flat=True))
                ).order_by(
                    '-created_at', '-updated_at')[:12]
            if self.action in ['trending_products']:
                return Product.objects.filter(in_stock=True, uuid__in=Order.objects.all().values_list(
                    'product__uuid',
                    flat=True)).exclude(uuid__in=Order.objects.filter(user=self.request.user).values_list(
                    'product__uuid',
                    flat=True)).annotate(
                    purchases=Count('product_carts')).order_by('-purchases')[:8]
            return Product.objects.filter(in_stock=True).exclude(
                uuid__in=Order.objects.filter(user=self.request.user,
                                              status__in=[PENDING, IN_PROCESS]).values_list(
                    'product__uuid', flat=True))
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
                           'trending_products', 'top_categories', 'related_products', 'get_product_ratings']:
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
        trending_product_queryset = self.get_queryset()
        page = self.paginate_queryset(trending_product_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(trending_product_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_name='top-discount-products', url_path='top-discount-products')
    def top_discount_products(self, request, *args, **kwargs):
        top_discount_products_queryset = self.get_queryset()[:5]
        serializer = self.get_serializer(top_discount_products_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_name='top-categories', url_path='top-categories',
            serializer_class=CategorySerializer)
    def top_categories(self, request, *args, **kwargs):
        top_categories_uuid = Product.objects.filter(in_stock=True).annotate(
            purchases=Count('product_carts')).order_by('-purchases').values_list('category__uuid', flat=True).distinct()
        top_categories_queryset = set([Category.objects.get(uuid=uuid) for uuid in top_categories_uuid])
        serializer = self.get_serializer(top_categories_queryset, many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_name='related-products', url_path='related-products',
            serializer_class=ProductSerializer)
    def related_products(self, request, *args, **kwargs):
        product = self.get_object()
        related_products_queryset = Product.objects.filter(in_stock=True,
                                                           category__uuid__in=product.category.all().values_list('uuid',
                                                                                                                 flat=True))[
                                    :4]
        serializer = self.get_serializer(list(set(related_products_queryset)), many=True,
                                         context={
                                             'view': self,
                                             'request': self.request
                                         }
                                         )
        return Response(serializer.data)

    @action(methods=['get', ], detail=True, url_name='product-ratings', url_path='product-ratings',
            serializer_class=ProductSerializer)
    def get_product_ratings(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, context={'product': product, 'view': self})
        return Response(serializer.data)

    @action(methods=['get', ], detail=False, url_name='wished-products', url_path='wished-products',
            serializer_class=ProductSerializer)
    def get_wished_products(self, request, *args, **kwargs):
        product_queryset = Product.objects.filter(
            uuid__in=WishList.objects.filter(user=request.user).values_list('product__uuid', flat=True)).exclude(
            uuid__in=Order.objects.filter(user=self.request.user, status__in=[PENDING, IN_PROCESS]).values_list(
                'product__uuid', flat=True)
        )
        serializer = self.get_serializer(product_queryset, many=True)
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
