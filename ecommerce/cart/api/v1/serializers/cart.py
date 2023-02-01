from django.db.models import Sum, F
from rest_framework import serializers

from ecommerce.accounts.api.v1.serializers.accounts import UserSerializer
from ecommerce.cart.constants import PENDING, IN_PROCESS, ON_THE_WAY
from ecommerce.cart.models import Order
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.api.v1.serializers.product import ProductSerializer
from ecommerce.product.models import Product
from rest_framework.status import HTTP_400_BAD_REQUEST

from ecommerce.shipping.models import ShippingOrder, ShippingDetail


class OrderSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'product', 'quantity', 'status', 'total_price', 'updated_at']

    def get_fields(self):
        fields = super(OrderSerializer, self).get_fields()
        request = self.context.get('request')
        view = self.context.get('view')
        if request and request.method.lower() in ['get'] or view and view.action in ['recent_orders']:
            fields['product'] = ProductSerializer(context={
                view: view
            })
            fields['user'] = UserSerializer(context={'request': request})
            fields['total_price'] = serializers.SerializerMethodField()
            fields['has_previous_shipping_details'] = serializers.SerializerMethodField()
            fields['updated_at'] = serializers.SerializerMethodField()
        if request and request.method.lower() in ['post']:
            fields.pop('status')
            fields['product'] = serializers.SlugRelatedField(slug_field='uuid', queryset=Product.objects.all())
        if request and request.method.lower() in ['patch', 'put']:
            fields.pop('product')
            fields.pop('status')
        if view and view.action.lower() in ['payment_verification']:
            fields.clear()
            fields['total_price'] = serializers.IntegerField()
            fields['token'] = serializers.CharField(max_length=100)
        if view and view.action.lower() in ['remove_order']:
            fields.clear()
        return fields

    def validate(self, attrs):
        product = attrs.get('product')
        requested_quantity = attrs.get('quantity')
        request = self.context.get('request')
        view = self.context.get('view')
        # if request and request.method.lower() in ['post']:
        #     if Order.objects.filter(user=request.user, product=product, status=PENDING).exists():
        #         raise serializers.ValidationError("Order Already exists")
        if request and request.method.lower() in ['patch']:
            order = self.context.get("object")
            ordered_product = order.product
            if (ordered_product.quantity + order.quantity) < requested_quantity:
                raise serializers.ValidationError("stock quantity less than available quantity")
            ordered_product.save()
        if view and view.action.lower() in ['payment_verification']:
            # total = \
            #     Order.objects.filter(user=request.user, status__in=[ON_THE_WAY], is_paid=False).aggregate(
            #         total=Sum(F('total_price') * F('quantity')))[
            #         'total']
            # total_price = attrs.get('total_price')
            # if total_price != total:
            #     raise serializers.ValidationError({
            #         'error': 'Invalid price'
            #     })
            return attrs
        if request and request.method.lower() in ['post']:
            if Order.objects.filter(user=request.user, product=attrs.get('product'),
                                    status__in=[PENDING, IN_PROCESS]).exists():
                raise serializers.ValidationError({
                    'error': 'Order with this product already exists.'
                }, code=HTTP_400_BAD_REQUEST)
            if product.quantity < requested_quantity:
                raise serializers.ValidationError({
                    'error': 'Requested quantity beyond available quantity.'
                }, code=HTTP_400_BAD_REQUEST)
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        quantity = validated_data.get('quantity')
        product = validated_data.get('product')
        total_price = quantity * (product.base_price - product.discount_price)
        instance = Order.objects.create(user=request.user, product=product,
                                        quantity=quantity, status=PENDING, total_price=total_price)
        product.quantity -= quantity
        if product.quantity == 0:
            product.in_stock = False
        product.save()
        return instance

    def get_total_price(self, obj):
        request = self.context.get('request')
        return \
            Order.objects.filter(user=request.user, status__in=[PENDING, IN_PROCESS], is_paid=False).aggregate(
                total=Sum('total_price'))[
                'total']

    def get_has_previous_shipping_details(self, obj):
        request = self.context.get('request')
        return ShippingDetail.objects.filter(user=request.user).exists()

    def get_updated_at(self, obj):
        return obj.updated_at.date()

    def update(self, instance, validated_data):
        prev_quantity = instance.quantity
        instance = super(OrderSerializer, self).update(instance=instance, validated_data=validated_data)
        quantity = validated_data.get('quantity')
        product = instance.product
        base_price = product.base_price
        discount_price = product.discount_price if not None else 0
        instance.total_price = quantity * (base_price - discount_price)
        product.quantity += (prev_quantity - instance.quantity)
        product.save()
        instance.save()
        return instance
