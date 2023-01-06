from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.models import Category


class CategorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
