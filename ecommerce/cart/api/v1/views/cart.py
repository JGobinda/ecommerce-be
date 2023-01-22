from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from config.settings import KHALTI_VERIFICATION_URL, KHALTI_TEST_SECRET_KEY, KHALTI_TEST_PUBLIC_KEY
from ecommerce.cart.api.v1.serializers.cart import OrderSerializer
from ecommerce.cart.constants import PENDING, CANCELLED, IN_PROCESS
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
        Order.objects.filter(user=self.request.user).update(status=CANCELLED)
        return Response({
            'detail': 'Order Cleared'
        })

    @action(detail=False, methods=['get', ], url_path='payment-method', url_name='payment-method')
    def update_payment(self, request, *args, **kwargs):
        """
        method--query_param
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        payment_method = self.request.query_params.get('method')
        if payment_method == 'KHALTI':
            Order.objects.filter(user=request.user, status=PENDING).update(payment_method='KHALTI')
        if payment_method == 'CASH_ON_DELIVERY':
            Order.objects.filter(user=request.user, status=PENDING).update(payment_method='CASH_ON_DELIVERY')
        Order.objects.filter(user=request.user, status=PENDING).update(status=IN_PROCESS)
        return Response({
            'detail': "Payment method updated"
        })

    @action(detail=False, methods=['post'], url_path='payment-verification', url_name='payment-verification')
    def payment_verification(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        total_price = serializer.validated_data.get('total_price') * 100
        token = serializer.validated_data.get('token')
        headers = {
            "Authorization": f"Key {KHALTI_TEST_SECRET_KEY}"
        }
        import requests
        response = requests.post(KHALTI_VERIFICATION_URL, {"token": token, "amount": total_price}, headers=headers)
        if response.status_code != 200:
            return Response(response.json()['amount'])
        Order.objects.filter(user=self.request.user, is_paid=False).exclude(
            Q(status='CANCELLED') | Q(status='DELIVERED')).update(is_paid=True)
        return Response(
            {
                'detail': 'payment successful'
            }
        )

    @action(detail=False, methods=['get'], url_path='recent-orders', url_name='recent-orders',
            serializer_class=OrderSerializer)
    def recent_orders(self, request, *args, **kwargs):
        recent_order_queryset = Order.objects.filter(user=self.request.user)
        serializer = self.get_serializer(recent_order_queryset, many=True)
        return Response(serializer.data)

