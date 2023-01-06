from rest_framework import serializers

from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.api.v1.serializers.product import ProductSerializer
from ecommerce.product.models import Product
from ecommerce.wishlist.models import WishList


class WishListSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = WishList
        fields = ['uuid', 'product']

    def get_fields(self):
        fields = super(WishListSerializer, self).get_fields()
        request = self.context.get('request')
        if request and request.method.lower() in ['get']:
            fields['product'] = ProductSerializer(fields=['uuid', 'name'])
        if request and request.method.lower() in ['put', 'patch', 'post']:
            fields['product'] = serializers.SlugRelatedField(slug_field='uuid', queryset=Product.objects.all())
        return fields

    def validate(self, attrs):
        request = self.context.get('request')
        product = attrs.get('product')
        if WishList.objects.filter(user=request.user, product=product):
            raise serializers.ValidationError(
                {
                    'error': 'This product is already in wishlist'
                }
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        product = validated_data.get('product')
        instance = WishList.objects.create(user=request.user, product=product)
        return instance

