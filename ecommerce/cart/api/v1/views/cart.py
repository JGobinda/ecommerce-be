from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ecommerce.cart.api.v1.serializers.cart import OrderSerializer
from ecommerce.cart.constants import PENDING
from ecommerce.cart.models import Order


class OrderViewSet(ModelViewSet):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = Order.objects.filter(status=PENDING)
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request and self.request.method.lower() in ['get']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get', ], url_path='clear-order', url_name='clear-order')
    def clear_order(self, request, *args, **kwargs):
        Order.objects.filter(user=self.request.user).delete()
        return Response({
            'detail': 'Order Cleared'
        })

