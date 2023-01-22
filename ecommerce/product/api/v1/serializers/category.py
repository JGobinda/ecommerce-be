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
        return obj.category_products.all().count()
