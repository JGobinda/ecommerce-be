from knox.serializers import UserSerializer
from rest_framework import serializers

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
            fields['product'] = ProductSerializer(fields=['uuid', 'name'])
            fields['user'] = UserSerializer()
        if request and request.method.lower() in ['post']:
            fields.pop('status')
            fields['product'] = serializers.SlugRelatedField(slug_field='uuid', queryset=Product.objects.all())
        if request and request.method.lower() in ['patch', 'put']:
            fields.pop('product')
            fields.pop('status')
        return fields

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method.lower() in ['post']:
            if Order.objects.filter(user=request.user, product=attrs.get('product')).exists():
                raise serializers.ValidationError({
                    'error': 'Order with this product already exists'
                }, code=HTTP_400_BAD_REQUEST)

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        instance = Order.objects.create(user=request.user, product=validated_data.get('product'),
                                        quantity=validated_data.get('quantity'), status=PENDING)
        return instance
