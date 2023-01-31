from ecommerce.cart.constants import PENDING, IN_PROCESS
from ecommerce.cart.models import Order
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.models import Category
from rest_framework import serializers


class CategorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'description']

    def get_fields(self):
        fields = super(CategorySerializer, self).get_fields()
        request = self.context.get('request')
        if request and request.method.lower() in ['get']:
            fields['products_count'] = serializers.SerializerMethodField()
        return fields

    def get_products_count(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.category_products.exclude(
                uuid__in=Order.objects.filter(user=self.request.user, status__in=[PENDING, IN_PROCESS]).values_list(
                    'product__uuid', flat=True)).count()
        return obj.category_products.all().count()
