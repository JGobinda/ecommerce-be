from ecommerce.cart.constants import PENDING
from ecommerce.cart.models import Order
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.shipping.models import ShippingDetail, ShippingOrder


class ShippingDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ShippingDetail
        fields = '__all__'

    def get_fields(self):
        fields = super(ShippingDetailSerializer, self).get_fields()
        request = self.context.get('request')
        if request and request.method.lower() in ['post', 'put', 'patch']:
            fields.pop('user')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        instance = super(ShippingDetailSerializer, self).create(validated_data)
        shipping_order_list = [ShippingOrder(shipping_detail=instance, order=order) for order in
                               Order.objects.filter(user=request.user, status=PENDING)]
        ShippingOrder.objects.bulk_create(shipping_order_list)
        return instance
