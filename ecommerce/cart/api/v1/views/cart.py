from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from config.settings import KHALTI_VERIFICATION_URL, KHALTI_TEST_SECRET_KEY, KHALTI_TEST_PUBLIC_KEY
from ecommerce.cart.api.v1.serializers.cart import OrderSerializer
from ecommerce.cart.constants import PENDING, CANCELLED, IN_PROCESS, ON_THE_WAY, KHALTI, CASH_ON_DELIVERY
from ecommerce.cart.models import Order
from ecommerce.cart.utils import send_order_placed_mail, send_payment_completed_mail
from ecommerce.shipping.models import ShippingDetail


class OrderViewSet(ModelViewSet):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = Order.objects.filter(status__in=[PENDING, IN_PROCESS]).exclude(status__in=[ON_THE_WAY])
    serializer_class = OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_rating_lookup_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.action in ['update', 'partial_update']:
            if product_rating_lookup_kwarg in self.kwargs:
                context['object'] = self.get_object()
        return context

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
        for order in Order.objects.filter(user=self.request.user, status="CANCELLED"):
            product = order.product
            product.quantity += order.quantity
            product.save()
        return Response({
            'detail': 'Order Cleared'
        })

    @action(detail=True, methods=['post', ], url_path='remove-order', url_name='remove-order')
    def remove_order(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = CANCELLED
        product = obj.product
        product.quantity += obj.quantity
        obj.save()
        product.save()
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
            Order.objects.filter(user=request.user, status=PENDING).update(status=ON_THE_WAY)
        if payment_method == 'CASH_ON_DELIVERY':
            Order.objects.filter(user=request.user, status=PENDING).update(payment_method='CASH_ON_DELIVERY')
            Order.objects.filter(user=request.user, status=PENDING).update(status=ON_THE_WAY)
        if ShippingDetail.objects.filter(user=request.user):
            shipping_mail = ShippingDetail.objects.filter(user=request.user).latest('created_at', 'updated_at').email
            send_order_placed_mail(request.user, shipping_mail)
        send_order_placed_mail(request.user)
        return Response({
            'detail': "Payment method updated"
        })

    @action(detail=False, methods=['post'], url_path='payment-verification', url_name='payment-verification')
    def payment_verification(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        total_price = int(serializer.validated_data.get('total_price') * 100)
        token = serializer.validated_data.get('token')
        headers = {
            "Authorization": f"Key {KHALTI_TEST_SECRET_KEY}"
        }
        print(total_price)
        import requests
        response = requests.post(KHALTI_VERIFICATION_URL, {"token": token, "amount": total_price}, headers=headers)
        if response.status_code != 200:
            return Response(response.json()['amount'])
        Order.objects.filter(user=self.request.user, is_paid=False).exclude(
            Q(status='CANCELLED') | Q(status='DELIVERED')).update(is_paid=True, status=ON_THE_WAY)
        if ShippingDetail.objects.filter(user=request.user):
            shipping_mail = ShippingDetail.objects.filter(user=request.user).latest('created_at', 'updated_at').email
            send_payment_completed_mail(request.user, shipping_mail)
        send_payment_completed_mail(request.user)
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

    @action(detail=False, methods=['get'], url_path='order-completion', url_name='order-completion')
    def order_completion(self, request, *args, **kwargs):
        order_queryset = Order.objects.filter(user=self.request.user, status__in=[ON_THE_WAY, IN_PROCESS])
        if order_queryset:
            payment_type = order_queryset.latest('created_at', 'updated_at').payment_method
            # print("HERE: ", payment_type)
            if payment_type == "KHALTI":
                return Response({
                    'type': KHALTI
                })
            else:
                return Response({
                    'type': CASH_ON_DELIVERY
                })
        else:
            return Response({
                'type': False
            })
