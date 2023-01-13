from rest_framework import serializers

from ecommerce.accounts.api.v1.serializers.accounts import UserSerializer
from ecommerce.cart.constants import PENDING
from ecommerce.cart.models import Order
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.api.v1.serializers.product import ProductSerializer
from ecommerce.product.models import Product
from rest_framework.status import HTTP_400_BAD_REQUEST


class OrderSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Order
        fields = ['uuid', 'product', 'quantity', 'status']

    def get_fields(self):
        fields = super(OrderSerializer, self).get_fields()
        request = self.context.get('request')
        if request and request.method.lower() in ['get']:
            fields['product'] = ProductSerializer()
            fields['user'] = UserSerializer(context={'request': request})
        if request and request.method.lower() in ['post']:
            fields.pop('status')
            fields['product'] = serializers.SlugRelatedField(slug_field='uuid', queryset=Product.objects.all())
        if request and request.method.lower() in ['patch', 'put']:
            fields.pop('product')
            fields.pop('status')
        return fields

    def validate(self, attrs):
        product = attrs.get('product')
        requested_quantity = attrs.get('quantity')
        request = self.context.get('request')
        if request and request.method.lower() in ['post']:
            if Order.objects.filter(user=request.user, product=attrs.get('product')).exists():
                raise serializers.ValidationError({
                    'error': 'Order with this product already exists.'
                }, code=HTTP_400_BAD_REQUEST)
            if product.quantity <= requested_quantity:
                raise serializers.ValidationError({
                    'error': 'Requested quantity beyond available quantity.'
                }, code=HTTP_400_BAD_REQUEST)

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        quantity = validated_data.get('quantity')
        product = validated_data.get('product')
        instance = Order.objects.create(user=request.user, product=product,
                                        quantity=quantity, status=PENDING)
        product.quantity -= quantity
        product.save()
        return instance
